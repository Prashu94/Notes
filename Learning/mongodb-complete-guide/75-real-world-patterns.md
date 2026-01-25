# Chapter 75: Real-World Patterns

## Table of Contents
- [E-Commerce Patterns](#e-commerce-patterns)
- [Social Media Patterns](#social-media-patterns)
- [Content Management Patterns](#content-management-patterns)
- [IoT and Time Series Patterns](#iot-and-time-series-patterns)
- [Gaming Patterns](#gaming-patterns)
- [Financial Services Patterns](#financial-services-patterns)
- [Summary](#summary)

---

## E-Commerce Patterns

### Product Catalog Schema

```javascript
// Product document with variants
const productSchema = {
  _id: ObjectId(),
  sku: "LAPTOP-PRO-15",
  name: "Pro Laptop 15-inch",
  slug: "pro-laptop-15-inch",
  
  // Category hierarchy using materialized path
  category: {
    _id: ObjectId("cat123"),
    name: "Laptops",
    path: "/Electronics/Computers/Laptops",
    ancestors: [
      { _id: ObjectId("cat001"), name: "Electronics", slug: "electronics" },
      { _id: ObjectId("cat002"), name: "Computers", slug: "computers" }
    ]
  },
  
  // Brand reference
  brand: {
    _id: ObjectId("brand123"),
    name: "TechBrand",
    logo: "/images/brands/techbrand.png"
  },
  
  // Pricing with history
  pricing: {
    currency: "USD",
    listPrice: 1499.99,
    salePrice: 1299.99,
    costPrice: 900.00,  // Internal only
    discount: {
      type: "percentage",
      value: 13,
      validUntil: ISODate("2024-12-31")
    },
    priceHistory: [
      { price: 1499.99, date: ISODate("2024-01-01") },
      { price: 1399.99, date: ISODate("2024-06-01") },
      { price: 1299.99, date: ISODate("2024-11-01") }
    ]
  },
  
  // Product variants
  variants: [
    {
      sku: "LAPTOP-PRO-15-8GB-256",
      name: "8GB RAM / 256GB SSD",
      attributes: { ram: "8GB", storage: "256GB" },
      pricing: { listPrice: 1299.99, salePrice: 1099.99 },
      inventory: { quantity: 50, warehouse: "WH-001" }
    },
    {
      sku: "LAPTOP-PRO-15-16GB-512",
      name: "16GB RAM / 512GB SSD",
      attributes: { ram: "16GB", storage: "512GB" },
      pricing: { listPrice: 1499.99, salePrice: 1299.99 },
      inventory: { quantity: 30, warehouse: "WH-001" }
    },
    {
      sku: "LAPTOP-PRO-15-32GB-1TB",
      name: "32GB RAM / 1TB SSD",
      attributes: { ram: "32GB", storage: "1TB" },
      pricing: { listPrice: 1899.99, salePrice: 1699.99 },
      inventory: { quantity: 15, warehouse: "WH-002" }
    }
  ],
  
  // Specifications
  specifications: {
    display: { size: "15.6 inches", resolution: "2560x1440", type: "IPS" },
    processor: { brand: "Intel", model: "Core i7-12700H", cores: 14 },
    graphics: { brand: "NVIDIA", model: "RTX 3060", memory: "6GB" },
    battery: { capacity: "86Wh", life: "10 hours" },
    weight: { value: 2.1, unit: "kg" },
    dimensions: { width: 35.5, depth: 24.8, height: 1.8, unit: "cm" }
  },
  
  // SEO and marketing
  seo: {
    title: "Pro Laptop 15-inch - High Performance Computing",
    description: "Powerful 15-inch laptop with latest Intel processor...",
    keywords: ["laptop", "gaming", "professional", "high-performance"]
  },
  
  // Media
  media: {
    primaryImage: "/images/products/laptop-pro-15-main.jpg",
    images: [
      { url: "/images/products/laptop-pro-15-1.jpg", alt: "Front view" },
      { url: "/images/products/laptop-pro-15-2.jpg", alt: "Side view" },
      { url: "/images/products/laptop-pro-15-3.jpg", alt: "Keyboard" }
    ],
    videos: [
      { url: "/videos/laptop-pro-15-review.mp4", thumbnail: "..." }
    ]
  },
  
  // Inventory summary
  inventory: {
    totalQuantity: 95,
    reserved: 5,
    available: 90,
    lowStockThreshold: 20,
    status: "in_stock"
  },
  
  // Reviews summary (computed)
  reviews: {
    averageRating: 4.5,
    totalCount: 234,
    distribution: { "5": 150, "4": 50, "3": 20, "2": 10, "1": 4 }
  },
  
  // Flags and status
  status: "active",
  flags: {
    featured: true,
    newArrival: false,
    bestSeller: true,
    onSale: true
  },
  
  // Timestamps
  createdAt: ISODate("2024-01-15"),
  updatedAt: ISODate("2024-11-20"),
  publishedAt: ISODate("2024-01-20")
}

// Indexes for product catalog
db.products.createIndex({ "category.path": 1 })
db.products.createIndex({ "brand._id": 1 })
db.products.createIndex({ "pricing.salePrice": 1 })
db.products.createIndex({ "reviews.averageRating": -1 })
db.products.createIndex({ "variants.sku": 1 })
db.products.createIndex({ status: 1, "flags.featured": 1 })
db.products.createIndex(
  { name: "text", "seo.keywords": "text", "category.name": "text" },
  { weights: { name: 10, "seo.keywords": 5, "category.name": 2 } }
)
```

### Shopping Cart Pattern

```javascript
// Cart with expiration
const cartSchema = {
  _id: ObjectId(),
  
  // User reference (or session for guest)
  userId: ObjectId("user123"),
  sessionId: "sess_abc123",  // For guest carts
  
  // Cart items
  items: [
    {
      productId: ObjectId("prod123"),
      variantSku: "LAPTOP-PRO-15-16GB-512",
      name: "Pro Laptop 15-inch - 16GB/512GB",
      image: "/images/products/laptop-pro-15-main.jpg",
      quantity: 1,
      unitPrice: 1299.99,
      totalPrice: 1299.99,
      addedAt: ISODate("2024-11-20T10:30:00Z")
    },
    {
      productId: ObjectId("prod456"),
      variantSku: "MOUSE-WIRELESS-BLK",
      name: "Wireless Mouse - Black",
      image: "/images/products/mouse-wireless.jpg",
      quantity: 2,
      unitPrice: 49.99,
      totalPrice: 99.98,
      addedAt: ISODate("2024-11-20T10:35:00Z")
    }
  ],
  
  // Pricing summary
  summary: {
    subtotal: 1399.97,
    discount: 0,
    shipping: 0,
    tax: 0,
    total: 1399.97,
    itemCount: 3
  },
  
  // Applied coupons
  coupons: [],
  
  // Shipping address (if selected)
  shippingAddress: null,
  
  // Status and timestamps
  status: "active",
  createdAt: ISODate("2024-11-20T10:30:00Z"),
  updatedAt: ISODate("2024-11-20T10:35:00Z"),
  expiresAt: ISODate("2024-11-27T10:30:00Z")  // 7-day expiration
}

// Cart operations
class CartService {
  constructor(db) {
    this.carts = db.collection('carts')
    this.products = db.collection('products')
  }
  
  async addItem(cartId, productId, variantSku, quantity = 1) {
    // Get product details
    const product = await this.products.findOne(
      { _id: productId, "variants.sku": variantSku },
      { projection: { name: 1, "variants.$": 1, media: 1 } }
    )
    
    if (!product) throw new Error('Product not found')
    
    const variant = product.variants[0]
    const unitPrice = variant.pricing.salePrice || variant.pricing.listPrice
    
    // Check if item exists in cart
    const existingItem = await this.carts.findOne({
      _id: cartId,
      "items.variantSku": variantSku
    })
    
    if (existingItem) {
      // Update quantity
      await this.carts.updateOne(
        { _id: cartId, "items.variantSku": variantSku },
        {
          $inc: { "items.$.quantity": quantity },
          $set: { 
            "items.$.totalPrice": { $multiply: ["$items.$.unitPrice", { $add: ["$items.$.quantity", quantity] }] },
            updatedAt: new Date()
          }
        }
      )
    } else {
      // Add new item
      const item = {
        productId,
        variantSku,
        name: `${product.name} - ${variant.name}`,
        image: product.media.primaryImage,
        quantity,
        unitPrice,
        totalPrice: unitPrice * quantity,
        addedAt: new Date()
      }
      
      await this.carts.updateOne(
        { _id: cartId },
        {
          $push: { items: item },
          $set: { updatedAt: new Date() }
        }
      )
    }
    
    // Recalculate summary
    await this.recalculateSummary(cartId)
  }
  
  async recalculateSummary(cartId) {
    const result = await this.carts.aggregate([
      { $match: { _id: cartId } },
      { $unwind: "$items" },
      {
        $group: {
          _id: "$_id",
          subtotal: { $sum: "$items.totalPrice" },
          itemCount: { $sum: "$items.quantity" }
        }
      }
    ]).toArray()
    
    if (result.length > 0) {
      const { subtotal, itemCount } = result[0]
      
      await this.carts.updateOne(
        { _id: cartId },
        {
          $set: {
            "summary.subtotal": subtotal,
            "summary.itemCount": itemCount,
            "summary.total": subtotal,  // Add tax/shipping calculation
            updatedAt: new Date()
          }
        }
      )
    }
  }
  
  async applyCoupon(cartId, couponCode) {
    const coupon = await this.db.collection('coupons').findOne({
      code: couponCode,
      status: 'active',
      validFrom: { $lte: new Date() },
      validUntil: { $gte: new Date() }
    })
    
    if (!coupon) throw new Error('Invalid coupon')
    
    const cart = await this.carts.findOne({ _id: cartId })
    
    let discount = 0
    if (coupon.type === 'percentage') {
      discount = cart.summary.subtotal * (coupon.value / 100)
      if (coupon.maxDiscount) {
        discount = Math.min(discount, coupon.maxDiscount)
      }
    } else if (coupon.type === 'fixed') {
      discount = coupon.value
    }
    
    await this.carts.updateOne(
      { _id: cartId },
      {
        $push: { coupons: { code: couponCode, discount } },
        $set: {
          "summary.discount": discount,
          "summary.total": cart.summary.subtotal - discount,
          updatedAt: new Date()
        }
      }
    )
  }
}

// TTL index for cart expiration
db.carts.createIndex({ expiresAt: 1 }, { expireAfterSeconds: 0 })
db.carts.createIndex({ userId: 1, status: 1 })
db.carts.createIndex({ sessionId: 1, status: 1 })
```

### Order Management Pattern

```javascript
// Order document
const orderSchema = {
  _id: ObjectId(),
  orderNumber: "ORD-2024-000123",
  
  // Customer info
  customer: {
    _id: ObjectId("user123"),
    email: "customer@example.com",
    name: "John Doe",
    phone: "+1-555-123-4567"
  },
  
  // Order items (snapshot at time of order)
  items: [
    {
      productId: ObjectId("prod123"),
      sku: "LAPTOP-PRO-15-16GB-512",
      name: "Pro Laptop 15-inch - 16GB/512GB",
      image: "/images/products/laptop-pro-15-main.jpg",
      quantity: 1,
      unitPrice: 1299.99,
      totalPrice: 1299.99,
      status: "processing"
    }
  ],
  
  // Addresses
  shippingAddress: {
    name: "John Doe",
    street: "123 Main St",
    city: "San Francisco",
    state: "CA",
    postalCode: "94102",
    country: "US",
    phone: "+1-555-123-4567"
  },
  
  billingAddress: {
    name: "John Doe",
    street: "123 Main St",
    city: "San Francisco",
    state: "CA",
    postalCode: "94102",
    country: "US"
  },
  
  // Pricing
  pricing: {
    subtotal: 1299.99,
    discount: 100.00,
    shipping: 0,
    tax: 107.25,
    total: 1307.24,
    currency: "USD"
  },
  
  // Payment
  payment: {
    method: "credit_card",
    status: "captured",
    transactionId: "txn_abc123",
    paidAt: ISODate("2024-11-20T11:00:00Z"),
    cardLast4: "4242",
    cardBrand: "visa"
  },
  
  // Shipping
  shipping: {
    method: "standard",
    carrier: "FedEx",
    trackingNumber: "794644790132",
    estimatedDelivery: ISODate("2024-11-25"),
    shippedAt: null,
    deliveredAt: null
  },
  
  // Order status with history
  status: "processing",
  statusHistory: [
    { status: "pending", timestamp: ISODate("2024-11-20T10:55:00Z") },
    { status: "paid", timestamp: ISODate("2024-11-20T11:00:00Z") },
    { status: "processing", timestamp: ISODate("2024-11-20T11:05:00Z") }
  ],
  
  // Notes
  notes: {
    customer: "Please leave at door",
    internal: "Priority customer"
  },
  
  // Timestamps
  createdAt: ISODate("2024-11-20T10:55:00Z"),
  updatedAt: ISODate("2024-11-20T11:05:00Z")
}

// Order state machine
class OrderStateMachine {
  constructor() {
    this.transitions = {
      pending: ['paid', 'cancelled'],
      paid: ['processing', 'refunded'],
      processing: ['shipped', 'cancelled'],
      shipped: ['delivered', 'returned'],
      delivered: ['returned', 'completed'],
      completed: [],
      cancelled: [],
      refunded: [],
      returned: ['refunded']
    }
  }
  
  canTransition(fromStatus, toStatus) {
    return this.transitions[fromStatus]?.includes(toStatus) || false
  }
  
  async updateStatus(db, orderId, newStatus, note = '') {
    const order = await db.collection('orders').findOne({ _id: orderId })
    
    if (!order) throw new Error('Order not found')
    
    if (!this.canTransition(order.status, newStatus)) {
      throw new Error(`Cannot transition from ${order.status} to ${newStatus}`)
    }
    
    const result = await db.collection('orders').updateOne(
      { _id: orderId },
      {
        $set: { 
          status: newStatus,
          updatedAt: new Date()
        },
        $push: {
          statusHistory: {
            status: newStatus,
            timestamp: new Date(),
            note
          }
        }
      }
    )
    
    // Trigger side effects
    await this.handleStatusChange(db, order, newStatus)
    
    return result
  }
  
  async handleStatusChange(db, order, newStatus) {
    switch (newStatus) {
      case 'paid':
        await this.reserveInventory(db, order)
        break
      case 'shipped':
        await this.updateShipping(db, order)
        await this.sendShippingNotification(order)
        break
      case 'cancelled':
        await this.releaseInventory(db, order)
        await this.processRefund(order)
        break
      case 'delivered':
        await this.sendDeliveryNotification(order)
        break
    }
  }
  
  async reserveInventory(db, order) {
    for (const item of order.items) {
      await db.collection('products').updateOne(
        { _id: item.productId, "variants.sku": item.sku },
        {
          $inc: {
            "inventory.reserved": item.quantity,
            "inventory.available": -item.quantity
          }
        }
      )
    }
  }
  
  async releaseInventory(db, order) {
    for (const item of order.items) {
      await db.collection('products').updateOne(
        { _id: item.productId, "variants.sku": item.sku },
        {
          $inc: {
            "inventory.reserved": -item.quantity,
            "inventory.available": item.quantity
          }
        }
      )
    }
  }
}

// Order indexes
db.orders.createIndex({ orderNumber: 1 }, { unique: true })
db.orders.createIndex({ "customer._id": 1, createdAt: -1 })
db.orders.createIndex({ status: 1, createdAt: -1 })
db.orders.createIndex({ "payment.status": 1 })
db.orders.createIndex({ "shipping.trackingNumber": 1 })
```

---

## Social Media Patterns

### User Profile and Relationships

```javascript
// User profile with social features
const userProfileSchema = {
  _id: ObjectId(),
  username: "johndoe",
  email: "john@example.com",
  
  // Profile info
  profile: {
    displayName: "John Doe",
    bio: "Software developer and coffee enthusiast",
    avatar: "/images/avatars/johndoe.jpg",
    coverImage: "/images/covers/johndoe.jpg",
    location: "San Francisco, CA",
    website: "https://johndoe.com",
    birthDate: ISODate("1990-05-15"),
    joinedAt: ISODate("2020-01-15")
  },
  
  // Privacy settings
  privacy: {
    profileVisibility: "public",  // public, followers, private
    showEmail: false,
    showLocation: true,
    allowMessages: "followers"
  },
  
  // Social stats (denormalized for performance)
  stats: {
    posts: 234,
    followers: 1250,
    following: 450,
    likes: 5670
  },
  
  // Verification
  verified: true,
  verifiedAt: ISODate("2023-06-01"),
  
  // Account status
  status: "active",
  lastActiveAt: ISODate("2024-11-20T15:30:00Z")
}

// Following relationship (separate collection for scale)
const followSchema = {
  _id: ObjectId(),
  followerId: ObjectId("user123"),
  followingId: ObjectId("user456"),
  createdAt: ISODate("2024-11-01"),
  
  // Notifications preference for this follow
  notifications: {
    posts: true,
    stories: true,
    live: true
  }
}

// Indexes for social graph
db.follows.createIndex({ followerId: 1, followingId: 1 }, { unique: true })
db.follows.createIndex({ followerId: 1, createdAt: -1 })
db.follows.createIndex({ followingId: 1, createdAt: -1 })

// Social graph operations
class SocialGraphService {
  constructor(db) {
    this.users = db.collection('users')
    this.follows = db.collection('follows')
  }
  
  async follow(followerId, followingId) {
    const session = this.users.client.startSession()
    
    try {
      await session.withTransaction(async () => {
        // Create follow relationship
        await this.follows.insertOne({
          followerId,
          followingId,
          createdAt: new Date(),
          notifications: { posts: true, stories: true, live: true }
        }, { session })
        
        // Update stats
        await this.users.updateOne(
          { _id: followerId },
          { $inc: { "stats.following": 1 } },
          { session }
        )
        
        await this.users.updateOne(
          { _id: followingId },
          { $inc: { "stats.followers": 1 } },
          { session }
        )
      })
    } finally {
      await session.endSession()
    }
  }
  
  async unfollow(followerId, followingId) {
    const session = this.users.client.startSession()
    
    try {
      await session.withTransaction(async () => {
        const result = await this.follows.deleteOne(
          { followerId, followingId },
          { session }
        )
        
        if (result.deletedCount > 0) {
          await this.users.updateOne(
            { _id: followerId },
            { $inc: { "stats.following": -1 } },
            { session }
          )
          
          await this.users.updateOne(
            { _id: followingId },
            { $inc: { "stats.followers": -1 } },
            { session }
          )
        }
      })
    } finally {
      await session.endSession()
    }
  }
  
  async getFollowers(userId, options = {}) {
    const { skip = 0, limit = 20 } = options
    
    return await this.follows.aggregate([
      { $match: { followingId: userId } },
      { $sort: { createdAt: -1 } },
      { $skip: skip },
      { $limit: limit },
      {
        $lookup: {
          from: 'users',
          localField: 'followerId',
          foreignField: '_id',
          as: 'user'
        }
      },
      { $unwind: '$user' },
      {
        $project: {
          _id: '$user._id',
          username: '$user.username',
          displayName: '$user.profile.displayName',
          avatar: '$user.profile.avatar',
          verified: '$user.verified',
          followedAt: '$createdAt'
        }
      }
    ]).toArray()
  }
  
  async getMutualFollows(userId1, userId2) {
    const user1Following = await this.follows.distinct('followingId', { followerId: userId1 })
    const user2Following = await this.follows.distinct('followingId', { followerId: userId2 })
    
    return user1Following.filter(id => 
      user2Following.some(id2 => id.equals(id2))
    )
  }
}
```

### Post and Feed Pattern

```javascript
// Post document
const postSchema = {
  _id: ObjectId(),
  authorId: ObjectId("user123"),
  
  // Content
  content: {
    text: "Just launched my new project! 🚀 Check it out...",
    media: [
      {
        type: "image",
        url: "/media/posts/img123.jpg",
        thumbnail: "/media/posts/img123_thumb.jpg",
        dimensions: { width: 1200, height: 800 },
        alt: "Project screenshot"
      }
    ],
    links: [
      {
        url: "https://myproject.com",
        title: "My Project",
        description: "An awesome new project",
        image: "https://myproject.com/og-image.jpg"
      }
    ],
    mentions: [
      { userId: ObjectId("user456"), username: "janedoe", position: [45, 53] }
    ],
    hashtags: ["launch", "project", "coding"]
  },
  
  // Engagement stats (denormalized)
  stats: {
    likes: 156,
    comments: 23,
    shares: 12,
    views: 2340,
    saves: 45
  },
  
  // Visibility and settings
  visibility: "public",  // public, followers, mentioned, private
  allowComments: true,
  allowShares: true,
  
  // Location (optional)
  location: {
    type: "Point",
    coordinates: [-122.4194, 37.7749],
    name: "San Francisco, CA"
  },
  
  // Threading (for replies)
  replyTo: null,  // ObjectId of parent post
  threadId: null,  // ObjectId of thread root
  
  // Timestamps
  createdAt: ISODate("2024-11-20T10:00:00Z"),
  updatedAt: ISODate("2024-11-20T10:00:00Z"),
  
  // Moderation
  moderation: {
    status: "approved",
    reviewedAt: null,
    flags: []
  }
}

// Feed generation using fan-out on write
class FeedService {
  constructor(db) {
    this.posts = db.collection('posts')
    this.feeds = db.collection('feeds')
    this.follows = db.collection('follows')
  }
  
  async createPost(authorId, content, options = {}) {
    const post = {
      authorId,
      content,
      stats: { likes: 0, comments: 0, shares: 0, views: 0, saves: 0 },
      visibility: options.visibility || 'public',
      allowComments: options.allowComments !== false,
      allowShares: options.allowShares !== false,
      replyTo: options.replyTo || null,
      threadId: options.threadId || null,
      location: options.location || null,
      createdAt: new Date(),
      updatedAt: new Date(),
      moderation: { status: 'approved', reviewedAt: null, flags: [] }
    }
    
    const result = await this.posts.insertOne(post)
    post._id = result.insertedId
    
    // Fan-out to followers' feeds
    await this.fanOutPost(post)
    
    return post
  }
  
  async fanOutPost(post) {
    // Get followers
    const followers = await this.follows.find({
      followingId: post.authorId,
      "notifications.posts": true
    }).toArray()
    
    // Batch insert into feeds
    const feedEntries = followers.map(follow => ({
      userId: follow.followerId,
      postId: post._id,
      authorId: post.authorId,
      score: post.createdAt.getTime(),  // Use timestamp as initial score
      createdAt: post.createdAt
    }))
    
    // Add author's own feed entry
    feedEntries.push({
      userId: post.authorId,
      postId: post._id,
      authorId: post.authorId,
      score: post.createdAt.getTime(),
      createdAt: post.createdAt
    })
    
    if (feedEntries.length > 0) {
      await this.feeds.insertMany(feedEntries, { ordered: false })
    }
  }
  
  async getFeed(userId, options = {}) {
    const { before, limit = 20 } = options
    
    const query = { userId }
    if (before) {
      query.score = { $lt: before }
    }
    
    const feedEntries = await this.feeds
      .find(query)
      .sort({ score: -1 })
      .limit(limit)
      .toArray()
    
    // Get full post details
    const postIds = feedEntries.map(e => e.postId)
    
    const posts = await this.posts.aggregate([
      { $match: { _id: { $in: postIds } } },
      {
        $lookup: {
          from: 'users',
          localField: 'authorId',
          foreignField: '_id',
          as: 'author'
        }
      },
      { $unwind: '$author' },
      {
        $project: {
          content: 1,
          stats: 1,
          visibility: 1,
          createdAt: 1,
          author: {
            _id: '$author._id',
            username: '$author.username',
            displayName: '$author.profile.displayName',
            avatar: '$author.profile.avatar',
            verified: '$author.verified'
          }
        }
      }
    ]).toArray()
    
    // Maintain feed order
    const postMap = new Map(posts.map(p => [p._id.toString(), p]))
    return postIds.map(id => postMap.get(id.toString())).filter(Boolean)
  }
  
  // Clean up old feed entries
  async cleanupFeeds(daysOld = 7) {
    const cutoff = new Date()
    cutoff.setDate(cutoff.getDate() - daysOld)
    
    await this.feeds.deleteMany({
      createdAt: { $lt: cutoff }
    })
  }
}

// Indexes
db.posts.createIndex({ authorId: 1, createdAt: -1 })
db.posts.createIndex({ "content.hashtags": 1, createdAt: -1 })
db.posts.createIndex({ "content.mentions.userId": 1 })
db.posts.createIndex({ visibility: 1, createdAt: -1 })
db.posts.createIndex({ location: "2dsphere" })
db.posts.createIndex({ threadId: 1, createdAt: 1 })

db.feeds.createIndex({ userId: 1, score: -1 })
db.feeds.createIndex({ createdAt: 1 }, { expireAfterSeconds: 7 * 24 * 60 * 60 })
```

---

## Content Management Patterns

### Hierarchical Content Structure

```javascript
// CMS page with nested blocks
const pageSchema = {
  _id: ObjectId(),
  
  // URL and identification
  slug: "about-us",
  path: "/company/about-us",
  
  // Metadata
  meta: {
    title: "About Us - Company Name",
    description: "Learn about our company history and mission",
    keywords: ["about", "company", "team"],
    ogImage: "/images/og/about-us.jpg",
    canonical: "https://company.com/company/about-us"
  },
  
  // Page content using blocks
  content: {
    layout: "default",
    blocks: [
      {
        id: "hero-1",
        type: "hero",
        data: {
          title: "About Our Company",
          subtitle: "Building the future, one innovation at a time",
          backgroundImage: "/images/hero/about.jpg",
          cta: { text: "Learn More", link: "#story" }
        },
        settings: {
          fullWidth: true,
          height: "large",
          textAlign: "center"
        }
      },
      {
        id: "text-1",
        type: "richText",
        data: {
          content: "<p>Founded in 2010, our company has grown...</p>"
        },
        settings: {
          maxWidth: "800px",
          padding: "large"
        }
      },
      {
        id: "team-1",
        type: "teamGrid",
        data: {
          title: "Our Leadership Team",
          members: [
            {
              name: "Jane Smith",
              role: "CEO",
              image: "/images/team/jane.jpg",
              bio: "Jane has 20 years of experience...",
              social: {
                linkedin: "https://linkedin.com/in/janesmith",
                twitter: "https://twitter.com/janesmith"
              }
            }
            // ... more team members
          ]
        },
        settings: {
          columns: 3,
          showBio: true
        }
      },
      {
        id: "timeline-1",
        type: "timeline",
        data: {
          title: "Our Journey",
          events: [
            { year: 2010, title: "Founded", description: "Started in a garage..." },
            { year: 2015, title: "First Million", description: "Reached 1M users..." },
            { year: 2020, title: "Global Expansion", description: "Offices in 10 countries..." }
          ]
        }
      }
    ]
  },
  
  // Page hierarchy
  parent: ObjectId("page_company"),  // Parent page reference
  ancestors: [
    { _id: ObjectId("page_home"), slug: "home", title: "Home" },
    { _id: ObjectId("page_company"), slug: "company", title: "Company" }
  ],
  children: [],  // Populated dynamically
  order: 1,
  
  // Publishing
  status: "published",
  publishedAt: ISODate("2024-01-15"),
  
  // Versioning
  version: 5,
  
  // Access control
  access: {
    visibility: "public",
    requiredRoles: []
  },
  
  // Timestamps
  createdAt: ISODate("2024-01-10"),
  updatedAt: ISODate("2024-11-15"),
  createdBy: ObjectId("admin123"),
  updatedBy: ObjectId("admin456")
}

// Version history collection
const pageVersionSchema = {
  _id: ObjectId(),
  pageId: ObjectId("page123"),
  version: 4,
  content: { /* full content snapshot */ },
  meta: { /* meta snapshot */ },
  changedBy: ObjectId("admin123"),
  changeNote: "Updated team section",
  createdAt: ISODate("2024-11-01")
}

// CMS service
class CMSService {
  constructor(db) {
    this.pages = db.collection('pages')
    this.versions = db.collection('page_versions')
  }
  
  async updatePage(pageId, updates, userId, note = '') {
    const page = await this.pages.findOne({ _id: pageId })
    
    if (!page) throw new Error('Page not found')
    
    // Save current version
    await this.versions.insertOne({
      pageId,
      version: page.version,
      content: page.content,
      meta: page.meta,
      changedBy: userId,
      changeNote: note,
      createdAt: new Date()
    })
    
    // Update page
    await this.pages.updateOne(
      { _id: pageId },
      {
        $set: {
          ...updates,
          version: page.version + 1,
          updatedAt: new Date(),
          updatedBy: userId
        }
      }
    )
  }
  
  async revertToVersion(pageId, version, userId) {
    const versionDoc = await this.versions.findOne({ pageId, version })
    
    if (!versionDoc) throw new Error('Version not found')
    
    await this.updatePage(
      pageId,
      { content: versionDoc.content, meta: versionDoc.meta },
      userId,
      `Reverted to version ${version}`
    )
  }
  
  async getPageTree(rootSlug = null) {
    const matchStage = rootSlug 
      ? { $match: { parent: null } }
      : { $match: { slug: rootSlug } }
    
    return await this.pages.aggregate([
      matchStage,
      {
        $graphLookup: {
          from: 'pages',
          startWith: '$_id',
          connectFromField: '_id',
          connectToField: 'parent',
          as: 'descendants',
          maxDepth: 5,
          depthField: 'depth'
        }
      },
      {
        $project: {
          _id: 1,
          slug: 1,
          path: 1,
          title: '$meta.title',
          status: 1,
          children: {
            $filter: {
              input: '$descendants',
              cond: { $eq: ['$$this.depth', 0] }
            }
          }
        }
      }
    ]).toArray()
  }
  
  async buildNavigation(maxDepth = 2) {
    const pages = await this.pages.find({
      status: 'published',
      'access.visibility': 'public'
    }).sort({ order: 1 }).toArray()
    
    const buildTree = (parentId, depth = 0) => {
      if (depth >= maxDepth) return []
      
      return pages
        .filter(p => {
          const pParent = p.parent?.toString()
          const targetParent = parentId?.toString()
          return pParent === targetParent
        })
        .map(p => ({
          _id: p._id,
          title: p.meta.title,
          path: p.path,
          children: buildTree(p._id, depth + 1)
        }))
    }
    
    return buildTree(null)
  }
}

// Indexes
db.pages.createIndex({ slug: 1 }, { unique: true })
db.pages.createIndex({ path: 1 }, { unique: true })
db.pages.createIndex({ parent: 1, order: 1 })
db.pages.createIndex({ status: 1, "access.visibility": 1 })
db.pages.createIndex({ "content.blocks.type": 1 })

db.page_versions.createIndex({ pageId: 1, version: -1 })
db.page_versions.createIndex({ pageId: 1, createdAt: -1 })
```

---

## IoT and Time Series Patterns

### Sensor Data Pattern

```javascript
// Time series collection for sensor data
db.createCollection("sensor_readings", {
  timeseries: {
    timeField: "timestamp",
    metaField: "metadata",
    granularity: "seconds"
  },
  expireAfterSeconds: 86400 * 90  // 90 days retention
})

// Sensor reading document
const sensorReadingSchema = {
  timestamp: ISODate("2024-11-20T15:30:00.000Z"),
  
  metadata: {
    deviceId: "sensor-001",
    deviceType: "temperature_humidity",
    location: {
      building: "A",
      floor: 2,
      room: "201",
      coordinates: [-122.4194, 37.7749]
    },
    tags: ["production", "critical"]
  },
  
  readings: {
    temperature: 23.5,
    humidity: 45.2,
    pressure: 1013.25
  },
  
  quality: {
    signalStrength: -45,  // dBm
    batteryLevel: 85,     // percent
    dataQuality: "good"
  }
}

// IoT data service
class IoTDataService {
  constructor(db) {
    this.readings = db.collection('sensor_readings')
    this.devices = db.collection('devices')
    this.alerts = db.collection('alerts')
  }
  
  async insertReadings(readings) {
    // Batch insert with validation
    const validReadings = readings.filter(r => this.validateReading(r))
    
    if (validReadings.length > 0) {
      await this.readings.insertMany(validReadings, { ordered: false })
      
      // Check for alerts
      await this.checkAlertConditions(validReadings)
    }
    
    return {
      inserted: validReadings.length,
      rejected: readings.length - validReadings.length
    }
  }
  
  validateReading(reading) {
    // Basic validation
    if (!reading.timestamp || !reading.metadata?.deviceId) return false
    if (!reading.readings || Object.keys(reading.readings).length === 0) return false
    return true
  }
  
  async checkAlertConditions(readings) {
    // Get alert rules for devices
    const deviceIds = [...new Set(readings.map(r => r.metadata.deviceId))]
    
    const rules = await this.devices.aggregate([
      { $match: { deviceId: { $in: deviceIds } } },
      { $unwind: '$alertRules' },
      {
        $project: {
          deviceId: 1,
          rule: '$alertRules'
        }
      }
    ]).toArray()
    
    const alerts = []
    
    for (const reading of readings) {
      const deviceRules = rules.filter(r => r.deviceId === reading.metadata.deviceId)
      
      for (const { rule } of deviceRules) {
        const value = reading.readings[rule.metric]
        
        if (value !== undefined) {
          let triggered = false
          
          switch (rule.condition) {
            case 'gt': triggered = value > rule.threshold; break
            case 'lt': triggered = value < rule.threshold; break
            case 'gte': triggered = value >= rule.threshold; break
            case 'lte': triggered = value <= rule.threshold; break
          }
          
          if (triggered) {
            alerts.push({
              deviceId: reading.metadata.deviceId,
              ruleId: rule.ruleId,
              metric: rule.metric,
              value,
              threshold: rule.threshold,
              condition: rule.condition,
              severity: rule.severity,
              timestamp: reading.timestamp,
              acknowledged: false
            })
          }
        }
      }
    }
    
    if (alerts.length > 0) {
      await this.alerts.insertMany(alerts)
    }
  }
  
  async getAggregatedData(deviceId, options = {}) {
    const {
      startTime,
      endTime = new Date(),
      interval = 'hour',  // minute, hour, day
      metrics = ['temperature', 'humidity']
    } = options
    
    const dateFormat = {
      minute: { $dateToString: { format: '%Y-%m-%dT%H:%M', date: '$timestamp' } },
      hour: { $dateToString: { format: '%Y-%m-%dT%H:00', date: '$timestamp' } },
      day: { $dateToString: { format: '%Y-%m-%d', date: '$timestamp' } }
    }
    
    const groupFields = {
      _id: dateFormat[interval]
    }
    
    // Build aggregation fields for each metric
    for (const metric of metrics) {
      groupFields[`${metric}_avg`] = { $avg: `$readings.${metric}` }
      groupFields[`${metric}_min`] = { $min: `$readings.${metric}` }
      groupFields[`${metric}_max`] = { $max: `$readings.${metric}` }
    }
    groupFields.count = { $sum: 1 }
    
    return await this.readings.aggregate([
      {
        $match: {
          'metadata.deviceId': deviceId,
          timestamp: {
            $gte: startTime,
            $lte: endTime
          }
        }
      },
      { $group: groupFields },
      { $sort: { _id: 1 } }
    ]).toArray()
  }
  
  async getDeviceStatus(deviceId) {
    // Get latest reading
    const latest = await this.readings.findOne(
      { 'metadata.deviceId': deviceId },
      { sort: { timestamp: -1 } }
    )
    
    if (!latest) return null
    
    // Get stats for last 24 hours
    const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000)
    
    const stats = await this.readings.aggregate([
      {
        $match: {
          'metadata.deviceId': deviceId,
          timestamp: { $gte: dayAgo }
        }
      },
      {
        $group: {
          _id: null,
          avgTemp: { $avg: '$readings.temperature' },
          avgHumidity: { $avg: '$readings.humidity' },
          readingCount: { $sum: 1 },
          lastReading: { $max: '$timestamp' }
        }
      }
    ]).toArray()
    
    return {
      deviceId,
      current: latest.readings,
      metadata: latest.metadata,
      quality: latest.quality,
      stats24h: stats[0] || null,
      online: (Date.now() - latest.timestamp.getTime()) < 5 * 60 * 1000  // 5 min threshold
    }
  }
}

// Indexes
db.sensor_readings.createIndex({ 'metadata.deviceId': 1, timestamp: -1 })
db.sensor_readings.createIndex({ 'metadata.location.building': 1, timestamp: -1 })
db.sensor_readings.createIndex({ 'metadata.tags': 1 })
```

---

## Gaming Patterns

### Player Profile and Progress

```javascript
// Player profile with game state
const playerSchema = {
  _id: ObjectId(),
  
  // Account info
  account: {
    username: "ProGamer99",
    email: "player@example.com",
    platform: "steam",
    platformId: "steam_12345",
    createdAt: ISODate("2023-01-15"),
    lastLoginAt: ISODate("2024-11-20")
  },
  
  // Game progress
  progress: {
    level: 45,
    experience: 125000,
    experienceToNextLevel: 150000,
    totalPlayTime: 3600000,  // milliseconds
    
    // Campaign progress
    campaign: {
      currentChapter: 5,
      currentMission: 3,
      completedMissions: ["1-1", "1-2", "1-3", "2-1", "2-2", "2-3", "3-1", "3-2", "3-3", "4-1", "4-2", "4-3", "5-1", "5-2"],
      difficulty: "hard"
    },
    
    // Achievements
    achievements: [
      { id: "first_blood", unlockedAt: ISODate("2023-01-15"), progress: 1 },
      { id: "level_10", unlockedAt: ISODate("2023-02-01"), progress: 1 },
      { id: "collector", unlockedAt: null, progress: 45, target: 100 }
    ]
  },
  
  // Inventory
  inventory: {
    currency: {
      gold: 15000,
      gems: 250,
      tickets: 5
    },
    
    items: [
      {
        itemId: "sword_legendary_001",
        name: "Blade of Fury",
        type: "weapon",
        rarity: "legendary",
        level: 40,
        stats: { attack: 150, critRate: 15 },
        equipped: true,
        obtainedAt: ISODate("2024-10-15")
      },
      {
        itemId: "armor_epic_002",
        name: "Dragon Scale Armor",
        type: "armor",
        rarity: "epic",
        level: 38,
        stats: { defense: 120, health: 500 },
        equipped: true,
        obtainedAt: ISODate("2024-09-20")
      }
      // ... more items
    ],
    
    maxSlots: 100,
    usedSlots: 67
  },
  
  // Stats and records
  stats: {
    battles: {
      total: 1500,
      wins: 1050,
      losses: 450,
      winRate: 0.7
    },
    
    pvp: {
      rating: 2150,
      rank: "Diamond",
      seasonWins: 45,
      seasonLosses: 20,
      highestRating: 2300
    },
    
    records: {
      highestDamage: 150000,
      fastestBoss: 45.3,  // seconds
      longestStreak: 25
    }
  },
  
  // Social
  social: {
    guildId: ObjectId("guild123"),
    guildRole: "officer",
    friends: [ObjectId("player456"), ObjectId("player789")],
    blocked: []
  },
  
  // Settings
  settings: {
    notifications: { push: true, email: false },
    privacy: { showOnline: true, allowFriendRequests: true },
    graphics: { quality: "high", fps: 60 }
  }
}

// Game service
class GameService {
  constructor(db) {
    this.players = db.collection('players')
    this.leaderboards = db.collection('leaderboards')
    this.matches = db.collection('matches')
  }
  
  async addExperience(playerId, amount, source) {
    const player = await this.players.findOne({ _id: playerId })
    
    let newExp = player.progress.experience + amount
    let newLevel = player.progress.level
    let expToNext = player.progress.experienceToNextLevel
    
    // Level up logic
    while (newExp >= expToNext) {
      newExp -= expToNext
      newLevel++
      expToNext = this.calculateExpToNextLevel(newLevel)
      
      // Grant level-up rewards
      await this.grantLevelUpRewards(playerId, newLevel)
    }
    
    await this.players.updateOne(
      { _id: playerId },
      {
        $set: {
          'progress.level': newLevel,
          'progress.experience': newExp,
          'progress.experienceToNextLevel': expToNext
        },
        $push: {
          expLog: {
            amount,
            source,
            timestamp: new Date(),
            levelBefore: player.progress.level,
            levelAfter: newLevel
          }
        }
      }
    )
    
    return { newLevel, newExp, leveledUp: newLevel > player.progress.level }
  }
  
  calculateExpToNextLevel(level) {
    // Exponential scaling
    return Math.floor(1000 * Math.pow(1.1, level))
  }
  
  async updatePvPRating(winnerId, loserId) {
    const [winner, loser] = await Promise.all([
      this.players.findOne({ _id: winnerId }),
      this.players.findOne({ _id: loserId })
    ])
    
    // ELO calculation
    const K = 32
    const expectedWinner = 1 / (1 + Math.pow(10, (loser.stats.pvp.rating - winner.stats.pvp.rating) / 400))
    const expectedLoser = 1 - expectedWinner
    
    const winnerNewRating = Math.round(winner.stats.pvp.rating + K * (1 - expectedWinner))
    const loserNewRating = Math.round(loser.stats.pvp.rating + K * (0 - expectedLoser))
    
    await Promise.all([
      this.players.updateOne(
        { _id: winnerId },
        {
          $set: {
            'stats.pvp.rating': winnerNewRating,
            'stats.pvp.rank': this.getRankFromRating(winnerNewRating),
            'stats.pvp.highestRating': Math.max(winnerNewRating, winner.stats.pvp.highestRating)
          },
          $inc: {
            'stats.pvp.seasonWins': 1,
            'stats.battles.total': 1,
            'stats.battles.wins': 1
          }
        }
      ),
      this.players.updateOne(
        { _id: loserId },
        {
          $set: {
            'stats.pvp.rating': Math.max(0, loserNewRating),
            'stats.pvp.rank': this.getRankFromRating(Math.max(0, loserNewRating))
          },
          $inc: {
            'stats.pvp.seasonLosses': 1,
            'stats.battles.total': 1,
            'stats.battles.losses': 1
          }
        }
      )
    ])
    
    // Update leaderboard
    await this.updateLeaderboard(winnerId, winnerNewRating)
    await this.updateLeaderboard(loserId, loserNewRating)
  }
  
  getRankFromRating(rating) {
    if (rating >= 2500) return 'Master'
    if (rating >= 2000) return 'Diamond'
    if (rating >= 1500) return 'Platinum'
    if (rating >= 1000) return 'Gold'
    if (rating >= 500) return 'Silver'
    return 'Bronze'
  }
  
  async updateLeaderboard(playerId, rating) {
    const player = await this.players.findOne({ _id: playerId })
    
    await this.leaderboards.updateOne(
      { 
        type: 'pvp_season',
        season: this.getCurrentSeason(),
        playerId
      },
      {
        $set: {
          rating,
          rank: this.getRankFromRating(rating),
          username: player.account.username,
          updatedAt: new Date()
        },
        $setOnInsert: {
          createdAt: new Date()
        }
      },
      { upsert: true }
    )
  }
  
  async getLeaderboard(type, options = {}) {
    const { skip = 0, limit = 100 } = options
    
    return await this.leaderboards.find({
      type,
      season: this.getCurrentSeason()
    })
    .sort({ rating: -1 })
    .skip(skip)
    .limit(limit)
    .toArray()
  }
  
  getCurrentSeason() {
    const now = new Date()
    return `${now.getFullYear()}-S${Math.ceil((now.getMonth() + 1) / 3)}`
  }
}

// Indexes
db.players.createIndex({ 'account.username': 1 }, { unique: true })
db.players.createIndex({ 'account.platformId': 1 })
db.players.createIndex({ 'stats.pvp.rating': -1 })
db.players.createIndex({ 'social.guildId': 1 })

db.leaderboards.createIndex({ type: 1, season: 1, rating: -1 })
db.leaderboards.createIndex({ type: 1, season: 1, playerId: 1 }, { unique: true })
```

---

## Financial Services Patterns

### Transaction and Account Pattern

```javascript
// Account document
const accountSchema = {
  _id: ObjectId(),
  accountNumber: "ACC-2024-000123",
  
  // Account holder
  holder: {
    customerId: ObjectId("cust123"),
    name: "John Doe",
    type: "individual"  // individual, business
  },
  
  // Account details
  details: {
    type: "checking",  // checking, savings, investment
    currency: "USD",
    status: "active",
    openedAt: ISODate("2020-01-15")
  },
  
  // Balance (use Decimal128 for precision)
  balance: {
    available: NumberDecimal("15234.56"),
    pending: NumberDecimal("500.00"),
    total: NumberDecimal("15734.56")
  },
  
  // Limits
  limits: {
    dailyWithdrawal: NumberDecimal("5000.00"),
    dailyTransfer: NumberDecimal("10000.00"),
    monthlyLimit: NumberDecimal("50000.00")
  },
  
  // Usage tracking
  usage: {
    today: {
      date: ISODate("2024-11-20"),
      withdrawn: NumberDecimal("500.00"),
      transferred: NumberDecimal("1500.00")
    },
    thisMonth: {
      month: "2024-11",
      total: NumberDecimal("8500.00")
    }
  },
  
  // Metadata
  metadata: {
    branch: "SF-001",
    accountManager: ObjectId("emp123"),
    tags: ["premium", "high-value"]
  }
}

// Transaction document
const transactionSchema = {
  _id: ObjectId(),
  transactionId: "TXN-2024-11-20-000456",
  
  // Accounts involved
  source: {
    accountId: ObjectId("acc123"),
    accountNumber: "ACC-2024-000123"
  },
  destination: {
    accountId: ObjectId("acc456"),
    accountNumber: "ACC-2024-000456",
    external: false,
    bankCode: null
  },
  
  // Transaction details
  amount: NumberDecimal("1000.00"),
  currency: "USD",
  type: "transfer",  // deposit, withdrawal, transfer, payment, fee
  
  // Status tracking
  status: "completed",  // pending, processing, completed, failed, reversed
  statusHistory: [
    { status: "pending", timestamp: ISODate("2024-11-20T10:00:00Z") },
    { status: "processing", timestamp: ISODate("2024-11-20T10:00:01Z") },
    { status: "completed", timestamp: ISODate("2024-11-20T10:00:02Z") }
  ],
  
  // Balances at time of transaction
  balanceAfter: {
    source: NumberDecimal("14234.56"),
    destination: NumberDecimal("5500.00")
  },
  
  // Description and reference
  description: "Monthly rent payment",
  reference: "RENT-NOV-2024",
  memo: "November 2024 rent",
  
  // Timestamps
  initiatedAt: ISODate("2024-11-20T10:00:00Z"),
  completedAt: ISODate("2024-11-20T10:00:02Z"),
  
  // Audit trail
  audit: {
    initiatedBy: ObjectId("user123"),
    channel: "mobile_app",
    ipAddress: "192.168.1.100",
    deviceId: "device_abc123"
  }
}

// Financial service with ACID transactions
class FinancialService {
  constructor(client, dbName) {
    this.client = client
    this.db = client.db(dbName)
    this.accounts = this.db.collection('accounts')
    this.transactions = this.db.collection('transactions')
  }
  
  async transfer(sourceAccountId, destAccountId, amount, description, userId) {
    const session = this.client.startSession()
    
    try {
      let result
      
      await session.withTransaction(async () => {
        // Get accounts with lock (using findOneAndUpdate for atomic read)
        const sourceAccount = await this.accounts.findOne(
          { _id: sourceAccountId },
          { session }
        )
        
        const destAccount = await this.accounts.findOne(
          { _id: destAccountId },
          { session }
        )
        
        // Validations
        if (!sourceAccount || !destAccount) {
          throw new Error('Account not found')
        }
        
        if (sourceAccount.details.status !== 'active' || destAccount.details.status !== 'active') {
          throw new Error('Account not active')
        }
        
        const amountDecimal = NumberDecimal(amount.toString())
        
        if (sourceAccount.balance.available.lessThan(amountDecimal)) {
          throw new Error('Insufficient funds')
        }
        
        // Check daily limits
        await this.checkLimits(sourceAccount, amountDecimal)
        
        // Generate transaction ID
        const transactionId = this.generateTransactionId()
        
        // Create transaction record
        const transaction = {
          transactionId,
          source: {
            accountId: sourceAccountId,
            accountNumber: sourceAccount.accountNumber
          },
          destination: {
            accountId: destAccountId,
            accountNumber: destAccount.accountNumber,
            external: false
          },
          amount: amountDecimal,
          currency: sourceAccount.details.currency,
          type: 'transfer',
          status: 'processing',
          statusHistory: [
            { status: 'pending', timestamp: new Date() },
            { status: 'processing', timestamp: new Date() }
          ],
          description,
          initiatedAt: new Date(),
          audit: {
            initiatedBy: userId,
            channel: 'api'
          }
        }
        
        await this.transactions.insertOne(transaction, { session })
        
        // Update source account
        const newSourceBalance = sourceAccount.balance.available.subtract(amountDecimal)
        await this.accounts.updateOne(
          { _id: sourceAccountId },
          {
            $set: {
              'balance.available': newSourceBalance,
              'balance.total': sourceAccount.balance.total.subtract(amountDecimal)
            },
            $inc: {
              'usage.today.transferred': amountDecimal
            }
          },
          { session }
        )
        
        // Update destination account
        const newDestBalance = destAccount.balance.available.add(amountDecimal)
        await this.accounts.updateOne(
          { _id: destAccountId },
          {
            $set: {
              'balance.available': newDestBalance,
              'balance.total': destAccount.balance.total.add(amountDecimal)
            }
          },
          { session }
        )
        
        // Update transaction with final balances
        await this.transactions.updateOne(
          { transactionId },
          {
            $set: {
              status: 'completed',
              completedAt: new Date(),
              'balanceAfter.source': newSourceBalance,
              'balanceAfter.destination': newDestBalance
            },
            $push: {
              statusHistory: { status: 'completed', timestamp: new Date() }
            }
          },
          { session }
        )
        
        result = { transactionId, status: 'completed' }
      }, {
        readConcern: { level: 'snapshot' },
        writeConcern: { w: 'majority' }
      })
      
      return result
      
    } finally {
      await session.endSession()
    }
  }
  
  async checkLimits(account, amount) {
    const today = new Date()
    today.setHours(0, 0, 0, 0)
    
    // Reset daily usage if new day
    if (account.usage.today.date < today) {
      await this.accounts.updateOne(
        { _id: account._id },
        {
          $set: {
            'usage.today': {
              date: today,
              withdrawn: NumberDecimal('0'),
              transferred: NumberDecimal('0')
            }
          }
        }
      )
      account.usage.today.transferred = NumberDecimal('0')
    }
    
    const projectedDaily = account.usage.today.transferred.add(amount)
    
    if (projectedDaily.greaterThan(account.limits.dailyTransfer)) {
      throw new Error('Daily transfer limit exceeded')
    }
  }
  
  generateTransactionId() {
    const date = new Date()
    const dateStr = date.toISOString().slice(0, 10).replace(/-/g, '')
    const random = Math.floor(Math.random() * 1000000).toString().padStart(6, '0')
    return `TXN-${dateStr}-${random}`
  }
  
  async getAccountStatement(accountId, startDate, endDate, options = {}) {
    const { skip = 0, limit = 100 } = options
    
    const transactions = await this.transactions.find({
      $or: [
        { 'source.accountId': accountId },
        { 'destination.accountId': accountId }
      ],
      status: 'completed',
      completedAt: {
        $gte: startDate,
        $lte: endDate
      }
    })
    .sort({ completedAt: -1 })
    .skip(skip)
    .limit(limit)
    .toArray()
    
    // Format as statement
    return transactions.map(txn => {
      const isDebit = txn.source.accountId.equals(accountId)
      
      return {
        date: txn.completedAt,
        transactionId: txn.transactionId,
        description: txn.description,
        type: isDebit ? 'DEBIT' : 'CREDIT',
        amount: isDebit ? txn.amount.negate() : txn.amount,
        balance: isDebit ? txn.balanceAfter.source : txn.balanceAfter.destination
      }
    })
  }
}

// Indexes
db.accounts.createIndex({ accountNumber: 1 }, { unique: true })
db.accounts.createIndex({ 'holder.customerId': 1 })
db.accounts.createIndex({ 'details.status': 1 })

db.transactions.createIndex({ transactionId: 1 }, { unique: true })
db.transactions.createIndex({ 'source.accountId': 1, completedAt: -1 })
db.transactions.createIndex({ 'destination.accountId': 1, completedAt: -1 })
db.transactions.createIndex({ status: 1, initiatedAt: 1 })
```

---

## Summary

### Pattern Selection Guide

| Use Case | Recommended Pattern | Key Features |
|----------|---------------------|--------------|
| Product Catalog | Embedded variants | Single document queries |
| Shopping Cart | TTL + denormalization | Auto-expiration, fast access |
| Orders | State machine | Audit trail, status history |
| Social Graph | Separate collection | Scale follows separately |
| Feed | Fan-out on write | Fast read, eventual consistency |
| CMS | Block-based content | Flexible, versioned |
| IoT | Time series collection | Automatic bucketing |
| Gaming | Embedded progress | Single player document |
| Financial | ACID transactions | Consistency, audit |

### Design Principles

| Principle | Application |
|-----------|-------------|
| Data locality | Embed frequently accessed together |
| Query patterns | Design schema around queries |
| Write patterns | Consider update frequency |
| Scalability | Plan sharding early |
| Consistency | Use transactions where needed |
| Performance | Index based on access patterns |

---

## Practice Questions

1. When should you embed vs reference documents?
2. How does fan-out on write help with feed generation?
3. What is the bucket pattern for time series data?
4. How do you implement a state machine in MongoDB?
5. What are the benefits of denormalizing social stats?
6. How do you handle financial transactions atomically?
7. What indexes support e-commerce product search?
8. How do you implement versioning for CMS content?

---

[← Previous: Atlas Monitoring](74-atlas-monitoring.md) | [Next: Performance Case Studies →](76-performance-case-studies.md)
