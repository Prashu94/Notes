# Chapter 76: Performance Case Studies

## Table of Contents
- [Case Study 1: E-Commerce Platform Optimization](#case-study-1-e-commerce-platform-optimization)
- [Case Study 2: Social Media Feed Performance](#case-study-2-social-media-feed-performance)
- [Case Study 3: IoT Data Pipeline](#case-study-3-iot-data-pipeline)
- [Case Study 4: Real-Time Analytics Dashboard](#case-study-4-real-time-analytics-dashboard)
- [Case Study 5: Multi-Tenant SaaS Application](#case-study-5-multi-tenant-saas-application)
- [Performance Analysis Framework](#performance-analysis-framework)
- [Summary](#summary)

---

## Case Study 1: E-Commerce Platform Optimization

### Problem Statement

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Initial Performance Issues                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Symptoms:                                                          │
│  • Product search taking 3-5 seconds                                │
│  • Category pages timing out during peak hours                      │
│  • Cart operations causing database locks                           │
│  • Order placement failing under load                               │
│                                                                     │
│  Metrics Before Optimization:                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Average Query Time:      2,500ms                           │   │
│  │  P99 Query Time:          8,000ms                           │   │
│  │  Peak CPU Usage:          95%                               │   │
│  │  Collection Scans/min:    15,000                            │   │
│  │  Index Hit Ratio:         45%                               │   │
│  │  Failed Transactions:     5%                                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Scale:                                                             │
│  • 2M products                                                      │
│  • 500K daily active users                                          │
│  • 50K orders per day                                               │
│  • 5M page views per day                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Analysis Phase

```javascript
// Step 1: Identify slow queries using profiler
db.setProfilingLevel(1, { slowms: 100 })

// Review slow query log
db.system.profile.find({
  ns: /ecommerce\.(products|orders|carts)/,
  millis: { $gt: 100 }
}).sort({ ts: -1 }).limit(50)

// Common slow queries identified:
const slowQueries = [
  // 1. Product search without text index
  {
    query: { name: /laptop/i, category: "electronics" },
    avgTime: "2.5s",
    issue: "Regex scan on 2M documents"
  },
  
  // 2. Category listing with multiple sorts
  {
    query: { category: "electronics" },
    sort: { price: 1, rating: -1 },
    avgTime: "3.2s",
    issue: "In-memory sort, no compound index"
  },
  
  // 3. Cart with populated product details
  {
    aggregate: [
      { $match: { userId: "..." } },
      { $lookup: { from: "products", ... } }
    ],
    avgTime: "1.8s",
    issue: "N+1 lookups for each cart item"
  },
  
  // 4. Order history with date range
  {
    query: { userId: "...", createdAt: { $gte: "...", $lte: "..." } },
    avgTime: "1.5s",
    issue: "Index on userId only, not compound"
  }
]

// Step 2: Analyze index usage
db.products.aggregate([
  { $indexStats: {} }
]).forEach(stat => {
  print(`Index: ${stat.name}, Accesses: ${stat.accesses.ops}`)
})

// Identified missing/underused indexes:
// - Text index for search: NOT EXISTS
// - Compound index for sort: NOT EXISTS
// - Products have 15 indexes, many unused
```

### Solution Implementation

```javascript
// Solution 1: Implement text search with facets
db.products.createIndex(
  {
    name: "text",
    description: "text",
    "category.name": "text",
    brand: "text"
  },
  {
    weights: { name: 10, brand: 5, "category.name": 3, description: 1 },
    name: "product_search_text"
  }
)

// Optimized search query
async function searchProducts(query, filters, options) {
  const pipeline = [
    // Text search stage
    {
      $match: {
        $text: { $search: query },
        status: "active"
      }
    },
    
    // Apply filters
    ...(filters.category ? [{ $match: { "category.path": new RegExp(`^${filters.category}`) } }] : []),
    ...(filters.priceRange ? [{ 
      $match: { 
        "pricing.salePrice": { 
          $gte: filters.priceRange.min, 
          $lte: filters.priceRange.max 
        } 
      } 
    }] : []),
    
    // Add relevance score
    { $addFields: { score: { $meta: "textScore" } } },
    
    // Facets for filters
    {
      $facet: {
        results: [
          { $sort: { score: -1, "reviews.averageRating": -1 } },
          { $skip: options.skip || 0 },
          { $limit: options.limit || 20 },
          { $project: { name: 1, slug: 1, pricing: 1, "media.primaryImage": 1, reviews: 1 } }
        ],
        categories: [
          { $group: { _id: "$category.name", count: { $sum: 1 } } },
          { $sort: { count: -1 } },
          { $limit: 10 }
        ],
        priceRanges: [
          {
            $bucket: {
              groupBy: "$pricing.salePrice",
              boundaries: [0, 50, 100, 250, 500, 1000, Infinity],
              default: "Other",
              output: { count: { $sum: 1 } }
            }
          }
        ],
        totalCount: [{ $count: "count" }]
      }
    }
  ]
  
  return await db.products.aggregate(pipeline).toArray()
}

// Result: Search time reduced from 2.5s to 45ms

// Solution 2: Compound indexes for category listings
db.products.createIndex(
  { "category.path": 1, "pricing.salePrice": 1 },
  { name: "category_price_idx" }
)

db.products.createIndex(
  { "category.path": 1, "reviews.averageRating": -1 },
  { name: "category_rating_idx" }
)

db.products.createIndex(
  { "category.path": 1, createdAt: -1 },
  { name: "category_new_idx" }
)

// Optimized category listing with sort selection
async function getCategoryProducts(categoryPath, sortBy, options) {
  const sortOptions = {
    'price_asc': { "pricing.salePrice": 1 },
    'price_desc': { "pricing.salePrice": -1 },
    'rating': { "reviews.averageRating": -1 },
    'newest': { createdAt: -1 }
  }
  
  // Use hint to ensure correct index
  const hint = {
    'price_asc': 'category_price_idx',
    'price_desc': 'category_price_idx',
    'rating': 'category_rating_idx',
    'newest': 'category_new_idx'
  }
  
  return await db.products
    .find({ "category.path": new RegExp(`^${categoryPath}`), status: "active" })
    .sort(sortOptions[sortBy] || sortOptions['rating'])
    .hint(hint[sortBy] || hint['rating'])
    .skip(options.skip || 0)
    .limit(options.limit || 24)
    .toArray()
}

// Result: Category listing reduced from 3.2s to 35ms

// Solution 3: Denormalize cart data
// Before: Cart stored only product IDs, required lookups
const oldCartSchema = {
  items: [{ productId: ObjectId(), quantity: 1 }]
}

// After: Cart stores product snapshot
const newCartSchema = {
  items: [{
    productId: ObjectId(),
    sku: "LAPTOP-001",
    name: "Pro Laptop",
    image: "/images/laptop.jpg",
    price: 999.99,
    quantity: 1
  }]
}

// Result: Cart load reduced from 1.8s to 15ms

// Solution 4: Compound index for orders
db.orders.createIndex(
  { "customer._id": 1, createdAt: -1 },
  { name: "customer_orders_idx" }
)

// Result: Order history reduced from 1.5s to 25ms
```

### Results After Optimization

```
┌─────────────────────────────────────────────────────────────────────┐
│                    After Optimization                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Metrics After Optimization:                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Average Query Time:      45ms (98% improvement)            │   │
│  │  P99 Query Time:          150ms (98% improvement)           │   │
│  │  Peak CPU Usage:          35% (63% improvement)             │   │
│  │  Collection Scans/min:    50 (99.7% improvement)            │   │
│  │  Index Hit Ratio:         99.5% (121% improvement)          │   │
│  │  Failed Transactions:     0.01% (99.8% improvement)         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Before          After                                              │
│  ───────         ─────                                              │
│  Search:    2,500ms  →   45ms                                       │
│  Category:  3,200ms  →   35ms                                       │
│  Cart:      1,800ms  →   15ms                                       │
│  Orders:    1,500ms  →   25ms                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Case Study 2: Social Media Feed Performance

### Problem Statement

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Social Media Feed Issues                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Symptoms:                                                          │
│  • Feed loading takes 5-10 seconds                                  │
│  • Feed becomes stale during high-follow scenarios                  │
│  • Popular users cause fan-out storms                               │
│  • Memory usage spikes during feed generation                       │
│                                                                     │
│  Scale:                                                             │
│  • 10M users                                                        │
│  • 500M follow relationships                                        │
│  • 100M posts                                                       │
│  • Average user follows 200 accounts                                │
│  • Celebrity users have 5M+ followers                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Analysis: Fan-out Strategies

```javascript
// Strategy Analysis
const strategies = {
  // Fan-out on Write: Push posts to all followers' feeds
  fanOutOnWrite: {
    pros: [
      "Fast feed reads (O(1) lookup)",
      "Simple feed retrieval query"
    ],
    cons: [
      "Celebrity problem: 5M writes per post",
      "Storage explosion",
      "Write latency for popular users"
    ],
    bestFor: "Users with < 10K followers"
  },
  
  // Fan-out on Read: Pull posts from followed users at read time
  fanOutOnRead: {
    pros: [
      "No write amplification",
      "Storage efficient"
    ],
    cons: [
      "Slow feed reads for users following many accounts",
      "Complex aggregation queries"
    ],
    bestFor: "Celebrity posts"
  },
  
  // Hybrid: Combine both based on follower count
  hybrid: {
    pros: [
      "Balanced write/read load",
      "Handles celebrity problem"
    ],
    cons: [
      "Complex implementation",
      "Need to merge feeds"
    ],
    bestFor: "Large-scale social platforms"
  }
}
```

### Hybrid Feed Implementation

```javascript
// User classification
const CELEBRITY_THRESHOLD = 50000  // followers

class HybridFeedService {
  constructor(db) {
    this.posts = db.collection('posts')
    this.feeds = db.collection('feeds')
    this.follows = db.collection('follows')
    this.users = db.collection('users')
  }
  
  async createPost(authorId, content) {
    const author = await this.users.findOne({ _id: authorId })
    const followerCount = author.stats.followers
    
    // Create post
    const post = {
      authorId,
      content,
      createdAt: new Date(),
      stats: { likes: 0, comments: 0 }
    }
    const result = await this.posts.insertOne(post)
    post._id = result.insertedId
    
    // Decide fan-out strategy
    if (followerCount < CELEBRITY_THRESHOLD) {
      // Fan-out on write for regular users
      await this.fanOutToFollowers(post)
    }
    // Celebrities: no fan-out, pulled at read time
    
    return post
  }
  
  async fanOutToFollowers(post) {
    const BATCH_SIZE = 10000
    let lastId = null
    
    while (true) {
      const query = { followingId: post.authorId }
      if (lastId) query._id = { $gt: lastId }
      
      const followers = await this.follows
        .find(query)
        .sort({ _id: 1 })
        .limit(BATCH_SIZE)
        .toArray()
      
      if (followers.length === 0) break
      
      const feedEntries = followers.map(f => ({
        userId: f.followerId,
        postId: post._id,
        authorId: post.authorId,
        createdAt: post.createdAt,
        score: post.createdAt.getTime()
      }))
      
      await this.feeds.insertMany(feedEntries, { ordered: false })
      
      lastId = followers[followers.length - 1]._id
      
      if (followers.length < BATCH_SIZE) break
    }
  }
  
  async getFeed(userId, options = {}) {
    const { before, limit = 20 } = options
    
    // Get users this person follows
    const following = await this.follows
      .find({ followerId: userId })
      .project({ followingId: 1 })
      .toArray()
    
    const followingIds = following.map(f => f.followingId)
    
    // Separate celebrities from regular users
    const users = await this.users
      .find({ _id: { $in: followingIds } })
      .project({ _id: 1, 'stats.followers': 1 })
      .toArray()
    
    const celebrityIds = users
      .filter(u => u.stats.followers >= CELEBRITY_THRESHOLD)
      .map(u => u._id)
    
    const regularUserIds = users
      .filter(u => u.stats.followers < CELEBRITY_THRESHOLD)
      .map(u => u._id)
    
    // Parallel fetch: pre-computed feed + celebrity posts
    const scoreThreshold = before || Date.now()
    
    const [precomputedFeed, celebrityPosts] = await Promise.all([
      // Pre-computed feed entries
      this.feeds
        .find({
          userId,
          score: { $lt: scoreThreshold }
        })
        .sort({ score: -1 })
        .limit(limit * 2)  // Fetch extra for merging
        .toArray(),
      
      // Direct fetch celebrity posts
      celebrityIds.length > 0 ? this.posts
        .find({
          authorId: { $in: celebrityIds },
          createdAt: { $lt: new Date(scoreThreshold) }
        })
        .sort({ createdAt: -1 })
        .limit(limit * 2)
        .toArray() : []
    ])
    
    // Merge and sort
    const allItems = [
      ...precomputedFeed.map(f => ({ postId: f.postId, score: f.score })),
      ...celebrityPosts.map(p => ({ postId: p._id, score: p.createdAt.getTime() }))
    ]
    
    // Sort by score descending and dedupe
    const seen = new Set()
    const sortedItems = allItems
      .sort((a, b) => b.score - a.score)
      .filter(item => {
        const key = item.postId.toString()
        if (seen.has(key)) return false
        seen.add(key)
        return true
      })
      .slice(0, limit)
    
    // Fetch full post details
    const postIds = sortedItems.map(i => i.postId)
    
    return await this.posts.aggregate([
      { $match: { _id: { $in: postIds } } },
      {
        $lookup: {
          from: 'users',
          localField: 'authorId',
          foreignField: '_id',
          pipeline: [
            { $project: { username: 1, 'profile.displayName': 1, 'profile.avatar': 1, verified: 1 } }
          ],
          as: 'author'
        }
      },
      { $unwind: '$author' },
      {
        $addFields: {
          sortOrder: { $indexOfArray: [postIds, '$_id'] }
        }
      },
      { $sort: { sortOrder: 1 } }
    ]).toArray()
  }
}
```

### Feed Caching Strategy

```javascript
// Redis caching layer for feeds
class CachedFeedService {
  constructor(db, redis) {
    this.feedService = new HybridFeedService(db)
    this.redis = redis
    this.CACHE_TTL = 300  // 5 minutes
    this.CACHE_SIZE = 200 // Cache top 200 posts
  }
  
  async getFeed(userId, options = {}) {
    const { before, limit = 20, skipCache = false } = options
    
    // Check cache first
    if (!skipCache && !before) {
      const cached = await this.getCachedFeed(userId, limit)
      if (cached) return cached
    }
    
    // Fetch from database
    const feed = await this.feedService.getFeed(userId, options)
    
    // Cache if fetching first page
    if (!before && feed.length > 0) {
      await this.cacheFeed(userId, feed)
    }
    
    return feed
  }
  
  async getCachedFeed(userId, limit) {
    const key = `feed:${userId}`
    const cached = await this.redis.lrange(key, 0, limit - 1)
    
    if (cached.length > 0) {
      return cached.map(JSON.parse)
    }
    return null
  }
  
  async cacheFeed(userId, posts) {
    const key = `feed:${userId}`
    const pipeline = this.redis.pipeline()
    
    // Clear existing
    pipeline.del(key)
    
    // Add new posts
    for (const post of posts.slice(0, this.CACHE_SIZE)) {
      pipeline.rpush(key, JSON.stringify(post))
    }
    
    // Set TTL
    pipeline.expire(key, this.CACHE_TTL)
    
    await pipeline.exec()
  }
  
  async invalidateFeed(userId) {
    await this.redis.del(`feed:${userId}`)
  }
  
  // Warm cache for active users
  async warmCaches(activeUserIds) {
    const BATCH_SIZE = 100
    
    for (let i = 0; i < activeUserIds.length; i += BATCH_SIZE) {
      const batch = activeUserIds.slice(i, i + BATCH_SIZE)
      
      await Promise.all(batch.map(async userId => {
        const feed = await this.feedService.getFeed(userId, { limit: 50 })
        await this.cacheFeed(userId, feed)
      }))
    }
  }
}
```

### Results

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Feed Performance Results                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Before (Fan-out on Write only):                                    │
│  • Feed load: 5-10s for users following celebrities                 │
│  • Celebrity post: 30s+ to fan-out to 5M followers                  │
│  • Storage: 500GB feed collection                                   │
│                                                                     │
│  After (Hybrid + Caching):                                          │
│  • Feed load: 50ms average (cache hit)                              │
│  • Feed load: 200ms average (cache miss)                            │
│  • Celebrity post: 10ms (no fan-out)                                │
│  • Storage: 150GB feed collection (70% reduction)                   │
│                                                                     │
│  Improvement:                                                       │
│  • 99% reduction in feed load time                                  │
│  • 99.9% reduction in celebrity post time                           │
│  • 70% storage reduction                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Case Study 3: IoT Data Pipeline

### Problem Statement

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IoT Data Pipeline Issues                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Symptoms:                                                          │
│  • Data ingestion falling behind (lag growing)                      │
│  • Dashboard queries timing out                                     │
│  • Storage growing 50GB/day                                         │
│  • Aggregation queries taking minutes                               │
│                                                                     │
│  Scale:                                                             │
│  • 100,000 IoT devices                                              │
│  • 1 reading per second per device                                  │
│  • 8.6B readings per day                                            │
│  • 90-day retention requirement                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Solution: Time Series with Bucketing

```javascript
// Before: Individual documents
const oldSchema = {
  deviceId: "sensor-001",
  timestamp: ISODate("2024-11-20T10:30:00.000Z"),
  temperature: 23.5,
  humidity: 45.2
}
// Problem: 8.6B documents/day, massive index overhead

// After: Bucketed documents (1-hour buckets)
db.createCollection("sensor_data_bucketed", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "minutes"
  }
})

// Bucketed schema
const bucketedSchema = {
  metadata: {
    deviceId: "sensor-001",
    deviceType: "temperature_humidity",
    location: { building: "A", floor: 2 }
  },
  timestamp: ISODate("2024-11-20T10:00:00.000Z"),  // Bucket start
  measurements: [
    { t: 0, temp: 23.5, hum: 45.2 },    // offset in seconds
    { t: 1, temp: 23.5, hum: 45.1 },
    { t: 2, temp: 23.6, hum: 45.0 },
    // ... up to 3600 readings per bucket
  ],
  summary: {
    count: 3600,
    temp: { min: 22.1, max: 24.5, avg: 23.4, sum: 84240 },
    hum: { min: 44.0, max: 46.5, avg: 45.2, sum: 162720 }
  }
}

// Ingestion service with batching
class IoTIngestionService {
  constructor(db) {
    this.collection = db.collection('sensor_data_bucketed')
    this.buffer = new Map()  // deviceId -> readings[]
    this.BATCH_SIZE = 100
    this.FLUSH_INTERVAL = 1000  // 1 second
  }
  
  start() {
    setInterval(() => this.flush(), this.FLUSH_INTERVAL)
  }
  
  async ingest(reading) {
    const key = `${reading.deviceId}:${this.getBucketTime(reading.timestamp)}`
    
    if (!this.buffer.has(key)) {
      this.buffer.set(key, [])
    }
    
    this.buffer.get(key).push(reading)
    
    if (this.buffer.get(key).length >= this.BATCH_SIZE) {
      await this.flushKey(key)
    }
  }
  
  getBucketTime(timestamp) {
    const date = new Date(timestamp)
    date.setMinutes(0, 0, 0)
    return date.toISOString()
  }
  
  async flush() {
    const keys = [...this.buffer.keys()]
    
    await Promise.all(keys.map(key => this.flushKey(key)))
  }
  
  async flushKey(key) {
    const readings = this.buffer.get(key)
    if (!readings || readings.length === 0) return
    
    this.buffer.delete(key)
    
    const [deviceId, bucketTime] = key.split(':')
    const bucketStart = new Date(bucketTime)
    
    // Calculate offsets and prepare measurements
    const measurements = readings.map(r => ({
      t: Math.floor((new Date(r.timestamp) - bucketStart) / 1000),
      temp: r.temperature,
      hum: r.humidity
    }))
    
    // Calculate summary stats
    const temps = readings.map(r => r.temperature)
    const hums = readings.map(r => r.humidity)
    
    const summaryUpdate = {
      'summary.count': readings.length,
      'summary.temp.sum': temps.reduce((a, b) => a + b, 0),
      'summary.hum.sum': hums.reduce((a, b) => a + b, 0)
    }
    
    // Upsert bucket document
    await this.collection.updateOne(
      {
        'metadata.deviceId': deviceId,
        timestamp: bucketStart
      },
      {
        $setOnInsert: {
          metadata: readings[0].metadata || { deviceId },
          timestamp: bucketStart
        },
        $push: {
          measurements: { $each: measurements }
        },
        $inc: summaryUpdate,
        $min: {
          'summary.temp.min': Math.min(...temps),
          'summary.hum.min': Math.min(...hums)
        },
        $max: {
          'summary.temp.max': Math.max(...temps),
          'summary.hum.max': Math.max(...hums)
        }
      },
      { upsert: true }
    )
  }
}
```

### Optimized Query Patterns

```javascript
// Dashboard queries optimized for time series

class IoTQueryService {
  constructor(db) {
    this.collection = db.collection('sensor_data_bucketed')
  }
  
  // Get aggregated data for charts (uses pre-computed summaries)
  async getAggregatedData(deviceId, startTime, endTime, granularity = 'hour') {
    // For hourly data, just read summaries (no need to process measurements)
    if (granularity === 'hour') {
      return await this.collection.aggregate([
        {
          $match: {
            'metadata.deviceId': deviceId,
            timestamp: { $gte: startTime, $lte: endTime }
          }
        },
        {
          $project: {
            timestamp: 1,
            avgTemp: { $divide: ['$summary.temp.sum', '$summary.count'] },
            avgHum: { $divide: ['$summary.hum.sum', '$summary.count'] },
            minTemp: '$summary.temp.min',
            maxTemp: '$summary.temp.max'
          }
        },
        { $sort: { timestamp: 1 } }
      ]).toArray()
    }
    
    // For daily aggregation
    if (granularity === 'day') {
      return await this.collection.aggregate([
        {
          $match: {
            'metadata.deviceId': deviceId,
            timestamp: { $gte: startTime, $lte: endTime }
          }
        },
        {
          $group: {
            _id: { $dateToString: { format: '%Y-%m-%d', date: '$timestamp' } },
            totalCount: { $sum: '$summary.count' },
            tempSum: { $sum: '$summary.temp.sum' },
            humSum: { $sum: '$summary.hum.sum' },
            minTemp: { $min: '$summary.temp.min' },
            maxTemp: { $max: '$summary.temp.max' }
          }
        },
        {
          $project: {
            date: '$_id',
            avgTemp: { $divide: ['$tempSum', '$totalCount'] },
            avgHum: { $divide: ['$humSum', '$totalCount'] },
            minTemp: 1,
            maxTemp: 1
          }
        },
        { $sort: { date: 1 } }
      ]).toArray()
    }
    
    // For minute-level, need to unwind measurements
    return await this.collection.aggregate([
      {
        $match: {
          'metadata.deviceId': deviceId,
          timestamp: { $gte: startTime, $lte: endTime }
        }
      },
      { $unwind: '$measurements' },
      {
        $project: {
          timestamp: {
            $add: ['$timestamp', { $multiply: ['$measurements.t', 1000] }]
          },
          temp: '$measurements.temp',
          hum: '$measurements.hum'
        }
      },
      { $sort: { timestamp: 1 } }
    ]).toArray()
  }
  
  // Real-time device status (last reading)
  async getDeviceStatus(deviceId) {
    const result = await this.collection.aggregate([
      {
        $match: { 'metadata.deviceId': deviceId }
      },
      { $sort: { timestamp: -1 } },
      { $limit: 1 },
      {
        $project: {
          deviceId: '$metadata.deviceId',
          location: '$metadata.location',
          lastBucket: '$timestamp',
          latestReading: { $arrayElemAt: ['$measurements', -1] },
          hourlyAvg: {
            temp: { $divide: ['$summary.temp.sum', '$summary.count'] },
            hum: { $divide: ['$summary.hum.sum', '$summary.count'] }
          }
        }
      }
    ]).toArray()
    
    return result[0] || null
  }
  
  // Fleet overview with filtering
  async getFleetOverview(filter = {}) {
    const matchStage = {}
    if (filter.building) matchStage['metadata.location.building'] = filter.building
    if (filter.floor) matchStage['metadata.location.floor'] = filter.floor
    
    // Get latest hour's data for all matching devices
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
    
    return await this.collection.aggregate([
      {
        $match: {
          ...matchStage,
          timestamp: { $gte: oneHourAgo }
        }
      },
      {
        $group: {
          _id: '$metadata.deviceId',
          location: { $first: '$metadata.location' },
          avgTemp: { $avg: { $divide: ['$summary.temp.sum', '$summary.count'] } },
          avgHum: { $avg: { $divide: ['$summary.hum.sum', '$summary.count'] } },
          readingCount: { $sum: '$summary.count' }
        }
      },
      {
        $project: {
          deviceId: '$_id',
          location: 1,
          avgTemp: { $round: ['$avgTemp', 1] },
          avgHum: { $round: ['$avgHum', 1] },
          status: {
            $cond: {
              if: { $lt: ['$readingCount', 3000] },  // Less than 83% uptime
              then: 'degraded',
              else: 'healthy'
            }
          }
        }
      },
      { $sort: { deviceId: 1 } }
    ]).toArray()
  }
}
```

### Results

```
┌─────────────────────────────────────────────────────────────────────┐
│                    IoT Pipeline Results                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Storage Efficiency:                                                │
│  • Before: 50GB/day (individual docs)                               │
│  • After: 5GB/day (bucketed with compression)                       │
│  • 90% storage reduction                                            │
│                                                                     │
│  Ingestion Performance:                                             │
│  • Before: 50,000 writes/sec (individual)                           │
│  • After: 1,000 writes/sec (batched upserts)                        │
│  • 98% write reduction                                              │
│                                                                     │
│  Query Performance:                                                 │
│  • Hourly aggregation: 5s → 50ms                                    │
│  • Daily aggregation: 60s → 200ms                                   │
│  • Device status: 500ms → 10ms                                      │
│  • Fleet overview: timeout → 500ms                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Case Study 4: Real-Time Analytics Dashboard

### Problem Statement

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Analytics Dashboard Issues                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Symptoms:                                                          │
│  • Dashboard takes 30+ seconds to load                              │
│  • Real-time metrics are 5+ minutes stale                           │
│  • Multiple users cause database overload                           │
│  • Complex aggregations timeout                                     │
│                                                                     │
│  Requirements:                                                      │
│  • Sub-second dashboard refresh                                     │
│  • Real-time event counts (< 1 min lag)                             │
│  • Support 100 concurrent dashboard users                           │
│  • Historical comparisons (today vs yesterday)                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Solution: Materialized Views with Change Streams

```javascript
// Pre-aggregation collections
const collections = {
  // Real-time (1-minute buckets)
  realtime: 'analytics_realtime',
  // Hourly rollups
  hourly: 'analytics_hourly',
  // Daily rollups
  daily: 'analytics_daily'
}

// Real-time aggregation service
class RealTimeAnalyticsService {
  constructor(db) {
    this.db = db
    this.events = db.collection('events')
    this.realtime = db.collection('analytics_realtime')
    this.hourly = db.collection('analytics_hourly')
    this.daily = db.collection('analytics_daily')
  }
  
  // Process incoming event
  async processEvent(event) {
    const minuteBucket = this.getMinuteBucket(event.timestamp)
    const dimensions = this.extractDimensions(event)
    
    // Update real-time bucket
    await this.realtime.updateOne(
      {
        timestamp: minuteBucket,
        ...dimensions
      },
      {
        $inc: {
          count: 1,
          [`events.${event.type}`]: 1,
          revenue: event.revenue || 0
        },
        $setOnInsert: {
          timestamp: minuteBucket,
          ...dimensions
        }
      },
      { upsert: true }
    )
  }
  
  getMinuteBucket(timestamp) {
    const date = new Date(timestamp)
    date.setSeconds(0, 0)
    return date
  }
  
  extractDimensions(event) {
    return {
      platform: event.platform || 'unknown',
      country: event.country || 'unknown',
      channel: event.channel || 'direct'
    }
  }
  
  // Roll up to hourly (run every hour)
  async rollupToHourly() {
    const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000)
    const hourStart = new Date(oneHourAgo)
    hourStart.setMinutes(0, 0, 0)
    
    const hourEnd = new Date(hourStart.getTime() + 60 * 60 * 1000)
    
    const pipeline = [
      {
        $match: {
          timestamp: { $gte: hourStart, $lt: hourEnd }
        }
      },
      {
        $group: {
          _id: {
            platform: '$platform',
            country: '$country',
            channel: '$channel'
          },
          count: { $sum: '$count' },
          revenue: { $sum: '$revenue' },
          events: {
            $mergeObjects: '$events'
          }
        }
      },
      {
        $project: {
          timestamp: hourStart,
          platform: '$_id.platform',
          country: '$_id.country',
          channel: '$_id.channel',
          count: 1,
          revenue: 1,
          events: 1
        }
      },
      {
        $merge: {
          into: 'analytics_hourly',
          on: ['timestamp', 'platform', 'country', 'channel'],
          whenMatched: 'replace',
          whenNotMatched: 'insert'
        }
      }
    ]
    
    await this.realtime.aggregate(pipeline).toArray()
    
    // Clean up old real-time data
    await this.realtime.deleteMany({
      timestamp: { $lt: oneHourAgo }
    })
  }
  
  // Roll up to daily (run daily)
  async rollupToDaily() {
    const yesterday = new Date()
    yesterday.setDate(yesterday.getDate() - 1)
    yesterday.setHours(0, 0, 0, 0)
    
    const today = new Date(yesterday.getTime() + 24 * 60 * 60 * 1000)
    
    const pipeline = [
      {
        $match: {
          timestamp: { $gte: yesterday, $lt: today }
        }
      },
      {
        $group: {
          _id: {
            platform: '$platform',
            country: '$country',
            channel: '$channel'
          },
          count: { $sum: '$count' },
          revenue: { $sum: '$revenue' },
          hourlyBreakdown: {
            $push: {
              hour: { $hour: '$timestamp' },
              count: '$count',
              revenue: '$revenue'
            }
          }
        }
      },
      {
        $project: {
          date: yesterday,
          platform: '$_id.platform',
          country: '$_id.country',
          channel: '$_id.channel',
          count: 1,
          revenue: 1,
          hourlyBreakdown: 1
        }
      },
      {
        $merge: {
          into: 'analytics_daily',
          on: ['date', 'platform', 'country', 'channel'],
          whenMatched: 'replace',
          whenNotMatched: 'insert'
        }
      }
    ]
    
    await this.hourly.aggregate(pipeline).toArray()
  }
}

// Dashboard query service
class DashboardQueryService {
  constructor(db, redis) {
    this.realtime = db.collection('analytics_realtime')
    this.hourly = db.collection('analytics_hourly')
    this.daily = db.collection('analytics_daily')
    this.redis = redis
  }
  
  // Real-time metrics (last 60 minutes)
  async getRealTimeMetrics(filters = {}) {
    const cacheKey = `dashboard:realtime:${JSON.stringify(filters)}`
    
    // Check cache (10-second TTL for real-time)
    const cached = await this.redis.get(cacheKey)
    if (cached) return JSON.parse(cached)
    
    const sixtyMinutesAgo = new Date(Date.now() - 60 * 60 * 1000)
    
    const matchStage = { timestamp: { $gte: sixtyMinutesAgo } }
    if (filters.platform) matchStage.platform = filters.platform
    if (filters.country) matchStage.country = filters.country
    
    const result = await this.realtime.aggregate([
      { $match: matchStage },
      {
        $group: {
          _id: null,
          totalCount: { $sum: '$count' },
          totalRevenue: { $sum: '$revenue' },
          byMinute: {
            $push: {
              timestamp: '$timestamp',
              count: '$count',
              revenue: '$revenue'
            }
          }
        }
      },
      {
        $project: {
          totalCount: 1,
          totalRevenue: { $round: ['$totalRevenue', 2] },
          trend: { $slice: [{ $sortArray: { input: '$byMinute', sortBy: { timestamp: 1 } } }, -60] }
        }
      }
    ]).toArray()
    
    const metrics = result[0] || { totalCount: 0, totalRevenue: 0, trend: [] }
    
    // Cache for 10 seconds
    await this.redis.setex(cacheKey, 10, JSON.stringify(metrics))
    
    return metrics
  }
  
  // Today vs yesterday comparison
  async getTodayVsYesterday(filters = {}) {
    const cacheKey = `dashboard:comparison:${JSON.stringify(filters)}`
    
    const cached = await this.redis.get(cacheKey)
    if (cached) return JSON.parse(cached)
    
    const now = new Date()
    const todayStart = new Date(now)
    todayStart.setHours(0, 0, 0, 0)
    
    const yesterdayStart = new Date(todayStart.getTime() - 24 * 60 * 60 * 1000)
    
    // Current hour for fair comparison
    const currentHour = now.getHours()
    
    const matchStage = {}
    if (filters.platform) matchStage.platform = filters.platform
    
    const [todayData, yesterdayData] = await Promise.all([
      // Today's data (from hourly + real-time for current hour)
      this.hourly.aggregate([
        {
          $match: {
            ...matchStage,
            timestamp: { $gte: todayStart, $lt: now }
          }
        },
        {
          $group: {
            _id: null,
            count: { $sum: '$count' },
            revenue: { $sum: '$revenue' }
          }
        }
      ]).toArray(),
      
      // Yesterday's data (up to same hour for fair comparison)
      this.hourly.aggregate([
        {
          $match: {
            ...matchStage,
            timestamp: {
              $gte: yesterdayStart,
              $lt: new Date(yesterdayStart.getTime() + currentHour * 60 * 60 * 1000)
            }
          }
        },
        {
          $group: {
            _id: null,
            count: { $sum: '$count' },
            revenue: { $sum: '$revenue' }
          }
        }
      ]).toArray()
    ])
    
    const today = todayData[0] || { count: 0, revenue: 0 }
    const yesterday = yesterdayData[0] || { count: 0, revenue: 0 }
    
    const result = {
      today,
      yesterday,
      change: {
        count: yesterday.count > 0 
          ? ((today.count - yesterday.count) / yesterday.count * 100).toFixed(1)
          : 0,
        revenue: yesterday.revenue > 0
          ? ((today.revenue - yesterday.revenue) / yesterday.revenue * 100).toFixed(1)
          : 0
      }
    }
    
    // Cache for 1 minute
    await this.redis.setex(cacheKey, 60, JSON.stringify(result))
    
    return result
  }
  
  // Top dimensions
  async getTopDimensions(dimension, limit = 10, filters = {}) {
    const cacheKey = `dashboard:top:${dimension}:${limit}:${JSON.stringify(filters)}`
    
    const cached = await this.redis.get(cacheKey)
    if (cached) return JSON.parse(cached)
    
    const todayStart = new Date()
    todayStart.setHours(0, 0, 0, 0)
    
    const result = await this.hourly.aggregate([
      {
        $match: {
          timestamp: { $gte: todayStart },
          ...filters
        }
      },
      {
        $group: {
          _id: `$${dimension}`,
          count: { $sum: '$count' },
          revenue: { $sum: '$revenue' }
        }
      },
      { $sort: { count: -1 } },
      { $limit: limit },
      {
        $project: {
          name: '$_id',
          count: 1,
          revenue: { $round: ['$revenue', 2] }
        }
      }
    ]).toArray()
    
    // Cache for 5 minutes
    await this.redis.setex(cacheKey, 300, JSON.stringify(result))
    
    return result
  }
}

// Indexes
db.analytics_realtime.createIndex({ timestamp: 1 })
db.analytics_realtime.createIndex({ timestamp: 1, platform: 1, country: 1, channel: 1 }, { unique: true })

db.analytics_hourly.createIndex({ timestamp: 1 })
db.analytics_hourly.createIndex({ timestamp: 1, platform: 1, country: 1, channel: 1 }, { unique: true })

db.analytics_daily.createIndex({ date: 1 })
db.analytics_daily.createIndex({ date: 1, platform: 1, country: 1, channel: 1 }, { unique: true })
```

### Results

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Dashboard Performance Results                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Query Performance:                                                 │
│  • Real-time metrics: 30s → 50ms (600x faster)                      │
│  • Today vs Yesterday: 45s → 100ms (450x faster)                    │
│  • Top dimensions: 20s → 80ms (250x faster)                         │
│                                                                     │
│  Data Freshness:                                                    │
│  • Before: 5+ minute lag                                            │
│  • After: < 10 second lag                                           │
│                                                                     │
│  Concurrency:                                                       │
│  • Before: 10 users caused timeouts                                 │
│  • After: 100+ users with sub-second response                       │
│                                                                     │
│  Resource Usage:                                                    │
│  • Query load on primary: 90% → 5%                                  │
│  • Cache hit rate: N/A → 95%                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Case Study 5: Multi-Tenant SaaS Application

### Problem Statement

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Multi-Tenant Issues                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Symptoms:                                                          │
│  • Large tenants affecting small tenant performance                 │
│  • Noisy neighbor problem                                           │
│  • Uneven data distribution                                         │
│  • Backup and restore complexity                                    │
│                                                                     │
│  Scale:                                                             │
│  • 5,000 tenants                                                    │
│  • 80% of data from top 100 tenants                                 │
│  • Data isolation requirements                                      │
│  • Per-tenant SLAs                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Solution: Tenant-Aware Sharding

```javascript
// Tenant isolation strategy
const tenantStrategies = {
  // Small tenants: Shared collections with tenant field
  shared: {
    collections: ['tasks', 'documents', 'comments'],
    shardKey: { tenantId: 'hashed' }
  },
  
  // Large tenants: Dedicated collections
  dedicated: {
    threshold: 1000000,  // documents
    collections: ['tasks', 'documents', 'comments']
  },
  
  // Enterprise: Dedicated database
  enterprise: {
    separateDatabase: true
  }
}

// Tenant-aware data access layer
class TenantDataService {
  constructor(client) {
    this.client = client
    this.defaultDb = client.db('saas_shared')
  }
  
  async getCollection(tenantId, collectionName) {
    const tenant = await this.getTenantConfig(tenantId)
    
    switch (tenant.tier) {
      case 'enterprise':
        return this.client.db(`tenant_${tenantId}`).collection(collectionName)
      
      case 'dedicated':
        return this.defaultDb.collection(`${collectionName}_${tenantId}`)
      
      default:
        return this.defaultDb.collection(collectionName)
    }
  }
  
  async getTenantConfig(tenantId) {
    // Cache tenant configs
    if (!this.tenantCache) {
      this.tenantCache = new Map()
    }
    
    if (this.tenantCache.has(tenantId)) {
      return this.tenantCache.get(tenantId)
    }
    
    const config = await this.defaultDb.collection('tenants').findOne({ _id: tenantId })
    this.tenantCache.set(tenantId, config)
    
    return config
  }
  
  // Generic CRUD with tenant isolation
  async find(tenantId, collectionName, query, options = {}) {
    const collection = await this.getCollection(tenantId, collectionName)
    const tenant = await this.getTenantConfig(tenantId)
    
    // Add tenant filter for shared collections
    const fullQuery = tenant.tier === 'shared' 
      ? { ...query, tenantId }
      : query
    
    return await collection.find(fullQuery, options).toArray()
  }
  
  async insertOne(tenantId, collectionName, document) {
    const collection = await this.getCollection(tenantId, collectionName)
    const tenant = await this.getTenantConfig(tenantId)
    
    const fullDocument = tenant.tier === 'shared'
      ? { ...document, tenantId }
      : document
    
    return await collection.insertOne(fullDocument)
  }
  
  async updateOne(tenantId, collectionName, filter, update) {
    const collection = await this.getCollection(tenantId, collectionName)
    const tenant = await this.getTenantConfig(tenantId)
    
    const fullFilter = tenant.tier === 'shared'
      ? { ...filter, tenantId }
      : filter
    
    return await collection.updateOne(fullFilter, update)
  }
  
  async deleteOne(tenantId, collectionName, filter) {
    const collection = await this.getCollection(tenantId, collectionName)
    const tenant = await this.getTenantConfig(tenantId)
    
    const fullFilter = tenant.tier === 'shared'
      ? { ...filter, tenantId }
      : filter
    
    return await collection.deleteOne(fullFilter)
  }
}

// Tenant resource limits
class TenantLimitsService {
  constructor(db, redis) {
    this.db = db
    this.redis = redis
  }
  
  async checkLimits(tenantId, operation) {
    const tenant = await this.db.collection('tenants').findOne({ _id: tenantId })
    const limits = tenant.limits || this.getDefaultLimits(tenant.tier)
    
    // Check request rate
    const rateKey = `rate:${tenantId}`
    const currentRate = await this.redis.incr(rateKey)
    
    if (currentRate === 1) {
      await this.redis.expire(rateKey, 60)  // 1-minute window
    }
    
    if (currentRate > limits.requestsPerMinute) {
      throw new Error('Rate limit exceeded')
    }
    
    // Check storage (for writes)
    if (['insert', 'update'].includes(operation)) {
      const usage = await this.getStorageUsage(tenantId)
      
      if (usage > limits.storageBytes) {
        throw new Error('Storage limit exceeded')
      }
    }
    
    return true
  }
  
  async getStorageUsage(tenantId) {
    const cacheKey = `storage:${tenantId}`
    const cached = await this.redis.get(cacheKey)
    
    if (cached) return parseInt(cached)
    
    // Calculate actual usage
    const tenant = await this.db.collection('tenants').findOne({ _id: tenantId })
    let totalSize = 0
    
    if (tenant.tier === 'enterprise') {
      const stats = await this.db.getSiblingDB(`tenant_${tenantId}`).stats()
      totalSize = stats.dataSize
    } else if (tenant.tier === 'dedicated') {
      for (const coll of ['tasks', 'documents', 'comments']) {
        const stats = await this.db.collection(`${coll}_${tenantId}`).stats()
        totalSize += stats.size
      }
    } else {
      // Estimate for shared (more expensive query)
      const pipeline = [
        { $match: { tenantId } },
        { $group: { _id: null, size: { $sum: { $bsonSize: '$$ROOT' } } } }
      ]
      
      for (const coll of ['tasks', 'documents', 'comments']) {
        const result = await this.db.collection(coll).aggregate(pipeline).toArray()
        totalSize += result[0]?.size || 0
      }
    }
    
    // Cache for 5 minutes
    await this.redis.setex(cacheKey, 300, totalSize.toString())
    
    return totalSize
  }
  
  getDefaultLimits(tier) {
    const limits = {
      free: {
        requestsPerMinute: 60,
        storageBytes: 100 * 1024 * 1024,  // 100MB
        documentsPerCollection: 10000
      },
      starter: {
        requestsPerMinute: 300,
        storageBytes: 1 * 1024 * 1024 * 1024,  // 1GB
        documentsPerCollection: 100000
      },
      professional: {
        requestsPerMinute: 1000,
        storageBytes: 10 * 1024 * 1024 * 1024,  // 10GB
        documentsPerCollection: 1000000
      },
      enterprise: {
        requestsPerMinute: 10000,
        storageBytes: 100 * 1024 * 1024 * 1024,  // 100GB
        documentsPerCollection: Infinity
      }
    }
    
    return limits[tier] || limits.free
  }
}

// Tenant migration (upgrade tier)
class TenantMigrationService {
  constructor(client) {
    this.client = client
    this.db = client.db('saas_shared')
  }
  
  async migrateToDedicated(tenantId) {
    const session = this.client.startSession()
    
    try {
      await session.withTransaction(async () => {
        // Migrate each collection
        for (const collName of ['tasks', 'documents', 'comments']) {
          const sourceCollection = this.db.collection(collName)
          const targetCollection = this.db.collection(`${collName}_${tenantId}`)
          
          // Copy documents in batches
          const batchSize = 10000
          let lastId = null
          
          while (true) {
            const query = { tenantId }
            if (lastId) query._id = { $gt: lastId }
            
            const docs = await sourceCollection
              .find(query, { session })
              .sort({ _id: 1 })
              .limit(batchSize)
              .toArray()
            
            if (docs.length === 0) break
            
            // Remove tenantId field for dedicated collection
            const cleanDocs = docs.map(({ tenantId, ...rest }) => rest)
            
            await targetCollection.insertMany(cleanDocs, { session })
            
            lastId = docs[docs.length - 1]._id
          }
          
          // Delete from shared collection
          await sourceCollection.deleteMany({ tenantId }, { session })
        }
        
        // Update tenant tier
        await this.db.collection('tenants').updateOne(
          { _id: tenantId },
          { $set: { tier: 'dedicated', migratedAt: new Date() } },
          { session }
        )
      })
    } finally {
      await session.endSession()
    }
  }
}

// Indexes for multi-tenant
db.tasks.createIndex({ tenantId: 1, createdAt: -1 })
db.tasks.createIndex({ tenantId: 1, status: 1 })
db.documents.createIndex({ tenantId: 1, folderId: 1 })
db.comments.createIndex({ tenantId: 1, documentId: 1 })
```

---

## Performance Analysis Framework

### Systematic Performance Review

```javascript
// Performance analysis toolkit
class PerformanceAnalyzer {
  constructor(db) {
    this.db = db
  }
  
  async runFullAnalysis() {
    const report = {
      timestamp: new Date(),
      
      // Index analysis
      indexes: await this.analyzeIndexes(),
      
      // Query analysis
      slowQueries: await this.analyzeSlowQueries(),
      
      // Collection stats
      collections: await this.analyzeCollections(),
      
      // Resource usage
      resources: await this.analyzeResources(),
      
      // Recommendations
      recommendations: []
    }
    
    // Generate recommendations
    report.recommendations = this.generateRecommendations(report)
    
    return report
  }
  
  async analyzeIndexes() {
    const collections = await this.db.listCollections().toArray()
    const analysis = []
    
    for (const coll of collections) {
      const indexes = await this.db.collection(coll.name).indexes()
      const stats = await this.db.collection(coll.name).aggregate([
        { $indexStats: {} }
      ]).toArray()
      
      const indexAnalysis = indexes.map(idx => {
        const stat = stats.find(s => s.name === idx.name)
        return {
          name: idx.name,
          keys: idx.key,
          accesses: stat?.accesses?.ops || 0,
          since: stat?.accesses?.since,
          size: null  // Would need collStats
        }
      })
      
      // Find unused indexes (0 accesses in last 7 days)
      const unused = indexAnalysis.filter(idx => 
        idx.name !== '_id_' && idx.accesses === 0
      )
      
      analysis.push({
        collection: coll.name,
        indexes: indexAnalysis,
        unusedIndexes: unused,
        indexCount: indexes.length
      })
    }
    
    return analysis
  }
  
  async analyzeSlowQueries() {
    // Get from profiler
    const slowQueries = await this.db.collection('system.profile')
      .find({ millis: { $gt: 100 } })
      .sort({ ts: -1 })
      .limit(100)
      .toArray()
    
    // Group by query pattern
    const patterns = {}
    
    for (const query of slowQueries) {
      const pattern = this.getQueryPattern(query)
      
      if (!patterns[pattern]) {
        patterns[pattern] = {
          pattern,
          count: 0,
          totalMs: 0,
          maxMs: 0,
          examples: []
        }
      }
      
      patterns[pattern].count++
      patterns[pattern].totalMs += query.millis
      patterns[pattern].maxMs = Math.max(patterns[pattern].maxMs, query.millis)
      
      if (patterns[pattern].examples.length < 3) {
        patterns[pattern].examples.push(query)
      }
    }
    
    return Object.values(patterns)
      .sort((a, b) => b.totalMs - a.totalMs)
      .slice(0, 20)
  }
  
  getQueryPattern(query) {
    // Normalize query to pattern
    const ns = query.ns
    const op = query.op
    const keys = query.command?.filter 
      ? Object.keys(query.command.filter).sort().join(',')
      : 'unknown'
    
    return `${ns}:${op}:${keys}`
  }
  
  async analyzeCollections() {
    const collections = await this.db.listCollections().toArray()
    const analysis = []
    
    for (const coll of collections) {
      if (coll.name.startsWith('system.')) continue
      
      const stats = await this.db.runCommand({ collStats: coll.name })
      
      analysis.push({
        name: coll.name,
        count: stats.count,
        size: stats.size,
        avgObjSize: stats.avgObjSize,
        storageSize: stats.storageSize,
        totalIndexSize: stats.totalIndexSize,
        indexCount: stats.nindexes,
        indexToDataRatio: stats.totalIndexSize / stats.size
      })
    }
    
    return analysis.sort((a, b) => b.size - a.size)
  }
  
  async analyzeResources() {
    const serverStatus = await this.db.admin().command({ serverStatus: 1 })
    
    return {
      connections: {
        current: serverStatus.connections.current,
        available: serverStatus.connections.available,
        utilization: serverStatus.connections.current / 
          (serverStatus.connections.current + serverStatus.connections.available)
      },
      memory: {
        resident: serverStatus.mem.resident,
        virtual: serverStatus.mem.virtual
      },
      opcounters: serverStatus.opcounters,
      network: {
        bytesIn: serverStatus.network.bytesIn,
        bytesOut: serverStatus.network.bytesOut,
        numRequests: serverStatus.network.numRequests
      }
    }
  }
  
  generateRecommendations(report) {
    const recommendations = []
    
    // Check for unused indexes
    for (const coll of report.indexes) {
      if (coll.unusedIndexes.length > 0) {
        recommendations.push({
          severity: 'medium',
          category: 'indexes',
          collection: coll.collection,
          message: `Found ${coll.unusedIndexes.length} unused indexes`,
          action: `Consider dropping: ${coll.unusedIndexes.map(i => i.name).join(', ')}`
        })
      }
      
      // Check for too many indexes
      if (coll.indexCount > 10) {
        recommendations.push({
          severity: 'low',
          category: 'indexes',
          collection: coll.collection,
          message: `Collection has ${coll.indexCount} indexes`,
          action: 'Review index necessity, each index adds write overhead'
        })
      }
    }
    
    // Check slow queries
    for (const pattern of report.slowQueries) {
      if (pattern.count > 10) {
        recommendations.push({
          severity: 'high',
          category: 'queries',
          pattern: pattern.pattern,
          message: `Slow query pattern executed ${pattern.count} times, avg ${Math.round(pattern.totalMs/pattern.count)}ms`,
          action: 'Add appropriate index or optimize query'
        })
      }
    }
    
    // Check collection sizes
    for (const coll of report.collections) {
      if (coll.indexToDataRatio > 0.5) {
        recommendations.push({
          severity: 'medium',
          category: 'storage',
          collection: coll.name,
          message: `Index size is ${Math.round(coll.indexToDataRatio * 100)}% of data size`,
          action: 'Review indexes for potential consolidation'
        })
      }
    }
    
    // Check connection usage
    if (report.resources.connections.utilization > 0.8) {
      recommendations.push({
        severity: 'high',
        category: 'resources',
        message: `Connection utilization at ${Math.round(report.resources.connections.utilization * 100)}%`,
        action: 'Review connection pooling settings or scale cluster'
      })
    }
    
    return recommendations.sort((a, b) => {
      const severityOrder = { high: 0, medium: 1, low: 2 }
      return severityOrder[a.severity] - severityOrder[b.severity]
    })
  }
}
```

---

## Summary

### Case Study Comparison

| Case Study | Main Issue | Solution | Improvement |
|------------|------------|----------|-------------|
| E-Commerce | Slow queries | Text search + compound indexes | 98% faster |
| Social Feed | Fan-out storm | Hybrid strategy + caching | 99% faster |
| IoT Pipeline | Volume overload | Time series bucketing | 90% storage reduction |
| Analytics | Stale dashboards | Materialized views | Real-time refresh |
| Multi-tenant | Noisy neighbor | Tenant isolation tiers | SLA compliance |

### Key Performance Patterns

| Pattern | When to Use | Benefit |
|---------|-------------|---------|
| Compound indexes | Multi-field queries | Covered queries |
| Text indexes | Full-text search | Fast search |
| Bucketing | Time series data | Storage + query efficiency |
| Fan-out hybrid | Social feeds | Balanced load |
| Materialized views | Dashboard queries | Pre-computed results |
| Tenant isolation | Multi-tenant SaaS | Resource fairness |

### Performance Checklist

```markdown
## Pre-Production Performance Review

### Indexing
- [ ] All query patterns have supporting indexes
- [ ] Compound indexes match query field order
- [ ] No unused indexes
- [ ] Index size is reasonable (<50% of data)

### Query Patterns
- [ ] No collection scans for common queries
- [ ] Aggregations use $match early
- [ ] Projections limit returned fields
- [ ] Pagination uses range queries

### Data Model
- [ ] Frequently accessed data is embedded
- [ ] Document size is < 16MB
- [ ] Arrays have bounded growth
- [ ] Schema supports query patterns

### Scaling
- [ ] Shard key chosen for workload
- [ ] Data is evenly distributed
- [ ] Hot spots are mitigated
- [ ] Connection pooling is configured

### Monitoring
- [ ] Slow query logging enabled
- [ ] Alerts configured for key metrics
- [ ] Performance baseline established
- [ ] Regular index review scheduled
```

---

## Practice Questions

1. When should you use fan-out on write vs fan-out on read?
2. How does bucketing improve time series performance?
3. What are the benefits of materialized views for dashboards?
4. How do you handle the noisy neighbor problem in multi-tenant apps?
5. What metrics indicate index efficiency issues?
6. How do you optimize compound indexes for sort operations?
7. What caching strategies work best with MongoDB?
8. How do you perform a systematic performance analysis?

---

[← Previous: Real-World Patterns](75-real-world-patterns.md) | [Next: Migration Strategies →](77-migration-strategies.md)
