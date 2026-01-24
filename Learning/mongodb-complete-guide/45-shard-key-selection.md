# Chapter 45: Shard Key Selection

## Table of Contents
- [Shard Key Importance](#shard-key-importance)
- [Shard Key Properties](#shard-key-properties)
- [Shard Key Strategies](#shard-key-strategies)
- [Common Patterns](#common-patterns)
- [Anti-Patterns](#anti-patterns)
- [Changing Shard Keys](#changing-shard-keys)
- [Summary](#summary)

---

## Shard Key Importance

The shard key is the most critical decision in sharding. It affects performance, scalability, and can be difficult to change later.

### Impact of Shard Key

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Shard Key Impact Areas                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  QUERY PERFORMANCE                                                 │
│  ├── Good key → Targeted queries (fast)                            │
│  └── Bad key → Scatter-gather queries (slow)                       │
│                                                                     │
│  WRITE DISTRIBUTION                                                │
│  ├── Good key → Even write distribution                            │
│  └── Bad key → Hot spots, single shard bottleneck                  │
│                                                                     │
│  DATA DISTRIBUTION                                                 │
│  ├── Good key → Even data across shards                            │
│  └── Bad key → Jumbo chunks, imbalanced shards                     │
│                                                                     │
│  SCALABILITY                                                       │
│  ├── Good key → Linear scaling as shards added                     │
│  └── Bad key → Diminishing returns, rearchitecture needed          │
│                                                                     │
│  OPERATIONAL COMPLEXITY                                            │
│  ├── Good key → Smooth operations                                  │
│  └── Bad key → Frequent rebalancing, manual intervention           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Shard Key Selection Checklist

```javascript
// Questions to answer before selecting a shard key

const shardKeyChecklist = {
  // 1. Query patterns
  queries: [
    "What are the most common query patterns?",
    "Which fields appear in WHERE clauses?",
    "Are there range queries? On which fields?"
  ],
  
  // 2. Write patterns
  writes: [
    "What's the insert rate?",
    "Are inserts random or sequential?",
    "Which documents are updated frequently?"
  ],
  
  // 3. Data characteristics
  data: [
    "What's the cardinality of candidate fields?",
    "Is data evenly distributed?",
    "Are there monotonically increasing values?"
  ],
  
  // 4. Growth expectations
  growth: [
    "How will data grow over time?",
    "Will query patterns change?",
    "How many shards will eventually be needed?"
  ]
}
```

---

## Shard Key Properties

### Four Key Properties

```
┌─────────────────────────────────────────────────────────────────────┐
│              Essential Shard Key Properties                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. CARDINALITY                                                    │
│     Number of unique values                                        │
│                                                                     │
│     LOW (Bad)              HIGH (Good)                             │
│     ├── status: ["active", "inactive"]                             │
│     │   Only 2 chunks possible                                     │
│     └── userId: "user_001" to "user_999999"                        │
│         Many chunks possible                                       │
│                                                                     │
│  2. FREQUENCY                                                      │
│     How often values repeat                                        │
│                                                                     │
│     SKEWED (Bad)           UNIFORM (Good)                          │
│     ├── 80% of docs have status: "active"                          │
│     │   Hot spot on one shard                                      │
│     └── userId evenly distributed                                  │
│         Balanced load                                              │
│                                                                     │
│  3. MONOTONICITY                                                   │
│     Values increase/decrease over time                             │
│                                                                     │
│     MONOTONIC (Bad for range) NON-MONOTONIC (Good)                │
│     ├── timestamp, auto-increment ID                               │
│     │   All inserts go to one shard                                │
│     └── Random, hashed values                                      │
│         Inserts spread across shards                               │
│                                                                     │
│  4. QUERY ISOLATION                                                │
│     Queries can target single shard                                │
│                                                                     │
│     SCATTER-GATHER (Bad)   TARGETED (Good)                        │
│     ├── Query doesn't include key                                  │
│     │   Must hit all shards                                        │
│     └── Query includes key                                         │
│         Single shard lookup                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Cardinality Analysis

```javascript
// Analyze cardinality of potential shard key fields

function analyzeCardinality(collection, field) {
  const coll = db[collection]
  const total = coll.countDocuments()
  
  // Get distinct count
  const distinctValues = coll.distinct(field).length
  
  // Calculate cardinality ratio
  const ratio = (distinctValues / total * 100).toFixed(2)
  
  // Assess
  let assessment
  if (ratio > 50) {
    assessment = "HIGH - Good shard key candidate"
  } else if (ratio > 10) {
    assessment = "MEDIUM - Consider compound key"
  } else if (ratio > 1) {
    assessment = "LOW - Poor shard key alone"
  } else {
    assessment = "VERY LOW - Not suitable"
  }
  
  return {
    field,
    totalDocuments: total,
    distinctValues,
    cardinalityRatio: ratio + "%",
    assessment
  }
}

// Example usage
// analyzeCardinality("orders", "customerId")
```

### Frequency Distribution

```javascript
// Analyze frequency distribution

function analyzeFrequency(collection, field) {
  const coll = db[collection]
  const total = coll.countDocuments()
  
  // Get value frequencies
  const distribution = coll.aggregate([
    { $group: { _id: `$${field}`, count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 10 }
  ]).toArray()
  
  // Calculate statistics
  const topValue = distribution[0]
  const topPercentage = (topValue.count / total * 100).toFixed(2)
  
  // Assess skewness
  let assessment
  if (topPercentage < 5) {
    assessment = "UNIFORM - Good distribution"
  } else if (topPercentage < 20) {
    assessment = "SLIGHTLY SKEWED - Acceptable"
  } else if (topPercentage < 50) {
    assessment = "SKEWED - May cause hot spots"
  } else {
    assessment = "HIGHLY SKEWED - Not recommended"
  }
  
  return {
    field,
    topValues: distribution.slice(0, 5).map(d => ({
      value: d._id,
      count: d.count,
      percentage: (d.count / total * 100).toFixed(2) + "%"
    })),
    assessment
  }
}
```

---

## Shard Key Strategies

### Strategy 1: Ranged Shard Key

```javascript
// Use for range queries on the shard key

// Good for:
// - Date-based queries (with compound key)
// - Sequential access patterns
// - Range scans

// Example: E-commerce orders by customer
sh.shardCollection("ecommerce.orders", { customerId: 1 })

// Queries that benefit:
db.orders.find({ customerId: "C123" })
db.orders.find({ customerId: { $gte: "C100", $lte: "C200" } })

// Considerations:
// - Avoid monotonic keys (like auto-increment)
// - Can create hot spots if inserts are sequential
```

### Strategy 2: Hashed Shard Key

```javascript
// Use for even distribution with random access

// Good for:
// - Insert-heavy workloads
// - Monotonically increasing source keys
// - When you don't need range queries on shard key

// Example: Users by hashed _id
sh.shardCollection("mydb.users", { _id: "hashed" })

// Or hash a specific field
sh.shardCollection("mydb.events", { timestamp: "hashed" })

// Benefits:
// - Even data distribution
// - Even write distribution
// - No hot spots

// Drawbacks:
// - Range queries hit all shards
// - No data locality
```

### Strategy 3: Compound Shard Key

```javascript
// Combine multiple fields for better properties

// Pattern: coarse_locality + fine_cardinality

// Example 1: Customer + Order
sh.shardCollection("ecommerce.orders", { customerId: 1, orderId: 1 })

// Query isolation for customer queries
db.orders.find({ customerId: "C123" })  // Targeted

// Example 2: Tenant + Timestamp
sh.shardCollection("saas.events", { tenantId: 1, timestamp: 1 })

// Benefits:
// - Query isolation (first field)
// - High cardinality (combination)
// - Range queries on second field within first field values

// Example 3: Region + Hashed ID
// Create index first
db.logs.createIndex({ region: 1, _id: "hashed" })
sh.shardCollection("mydb.logs", { region: 1, _id: "hashed" })

// Geographic locality with distributed writes
```

### Strategy 4: Zone Sharding

```javascript
// Associate shard key ranges with specific shards

// Use case: Geographic data locality
sh.addShardToZone("shard-us-east", "US")
sh.addShardToZone("shard-us-west", "US")
sh.addShardToZone("shard-eu", "EU")

// Define zones
sh.updateZoneKeyRange(
  "mydb.users",
  { region: "US", _id: MinKey },
  { region: "US", _id: MaxKey },
  "US"
)

sh.updateZoneKeyRange(
  "mydb.users",
  { region: "EU", _id: MinKey },
  { region: "EU", _id: MaxKey },
  "EU"
)

// Now US data stays on US shards
// EU data stays on EU shards
```

---

## Common Patterns

### Pattern 1: Multi-Tenant SaaS

```javascript
// Problem: Multiple tenants, isolation needed

// ❌ Bad: Random distribution
sh.shardCollection("saas.data", { _id: "hashed" })
// Tenant queries scatter across all shards

// ✓ Good: Tenant-based sharding
sh.shardCollection("saas.data", { tenantId: 1, documentId: 1 })

// Benefits:
// - Tenant queries are targeted
// - Easy tenant isolation
// - Can use zones for tenant placement

// Query pattern:
db.data.find({ tenantId: "tenant_123" })  // Single shard
db.data.find({ tenantId: "tenant_123", documentId: "doc_456" })  // Single shard
```

### Pattern 2: Time-Series Data

```javascript
// Problem: Huge volume of timestamped data

// ❌ Bad: Timestamp only (monotonic)
sh.shardCollection("metrics.data", { timestamp: 1 })
// All inserts go to one shard

// ❌ Bad: Hashed timestamp
sh.shardCollection("metrics.data", { timestamp: "hashed" })
// Range queries hit all shards

// ✓ Good: Compound with device/source
sh.shardCollection("metrics.data", { deviceId: 1, timestamp: 1 })

// Benefits:
// - Inserts distributed by device
// - Time range queries for single device are targeted
// - Device dashboard queries are efficient

// Alternative: Add randomizer
{
  deviceId: "device_123",
  timestamp: ISODate("2024-01-15T10:30:00Z"),
  bucket: Math.floor(Math.random() * 10)  // 0-9
}
sh.shardCollection("metrics.data", { bucket: 1, timestamp: 1 })
```

### Pattern 3: E-Commerce Orders

```javascript
// Problem: Orders with various query patterns

// Query patterns:
// 1. Find orders by customer
// 2. Find order by order ID
// 3. Find orders by date range

// ✓ Solution: Customer + Order compound key
sh.shardCollection("ecommerce.orders", { customerId: 1, orderId: 1 })

// Create secondary index for order lookup
db.orders.createIndex({ orderId: 1 })

// Query routing:
db.orders.find({ customerId: "C123" })           // Targeted
db.orders.find({ customerId: "C123", orderId: "O456" })  // Targeted
db.orders.find({ orderId: "O456" })              // Uses index, scatter-gather

// For date queries, add index:
db.orders.createIndex({ orderDate: 1 })
```

### Pattern 4: User Sessions

```javascript
// Problem: High-volume session data

// Requirements:
// - Fast session lookups by session ID
// - User can have multiple sessions
// - Sessions expire

// ✓ Solution: Hashed session ID
sh.shardCollection("app.sessions", { sessionId: "hashed" })

// Benefits:
// - Session lookups are targeted (exact match)
// - Even distribution of sessions
// - Write scaling for session creation

// Alternative: User-based for session history
sh.shardCollection("app.sessions", { userId: 1, sessionId: 1 })

// Now user's session history is on one shard
db.sessions.find({ userId: "U123" })  // Targeted
```

### Pattern 5: Social Media Posts

```javascript
// Problem: Posts with various access patterns

// Access patterns:
// 1. User's own posts (frequent)
// 2. Posts by hashtag
// 3. Posts by date

// ✓ Solution: Author-based sharding
sh.shardCollection("social.posts", { authorId: 1, createdAt: -1 })

// Secondary indexes for other patterns
db.posts.createIndex({ hashtags: 1 })
db.posts.createIndex({ createdAt: -1 })

// User timeline query (targeted)
db.posts.find({ authorId: "user_123" }).sort({ createdAt: -1 }).limit(20)

// Hashtag query (scatter-gather with index)
db.posts.find({ hashtags: "mongodb" }).sort({ createdAt: -1 }).limit(20)
```

---

## Anti-Patterns

### Anti-Pattern 1: Low Cardinality

```javascript
// ❌ Don't: Shard on status field
sh.shardCollection("orders", { status: 1 })

// Problem:
// Only values: "pending", "processing", "shipped", "delivered"
// Maximum 4 chunks - can't scale beyond 4 shards

// Result:
// ┌────────────────────────────────────────────┐
// │ Shard 1: status="pending" (30%)           │
// │ Shard 2: status="processing" (5%)         │
// │ Shard 3: status="shipped" (10%)           │
// │ Shard 4: status="delivered" (55%)         │
// └────────────────────────────────────────────┘
// Highly imbalanced, can't add more shards

// ✓ Instead: Use compound key
sh.shardCollection("orders", { status: 1, orderId: 1 })
// Or better, customer-based:
sh.shardCollection("orders", { customerId: 1, orderId: 1 })
```

### Anti-Pattern 2: Monotonically Increasing

```javascript
// ❌ Don't: Shard on timestamp alone
sh.shardCollection("logs", { timestamp: 1 })

// Problem:
// All new inserts go to the same shard (max range chunk)

// Visualization:
// Time →
// ┌─────────┐ ┌─────────┐ ┌─────────┐
// │ Shard 1 │ │ Shard 2 │ │ Shard 3 │ ← ALL inserts here
// │ Jan     │ │ Feb     │ │ March   │
// │ (idle)  │ │ (idle)  │ │ (HOT)   │
// └─────────┘ └─────────┘ └─────────┘

// ✓ Instead: Hash or compound key
sh.shardCollection("logs", { timestamp: "hashed" })
// Or
sh.shardCollection("logs", { source: 1, timestamp: 1 })
```

### Anti-Pattern 3: Highly Skewed Data

```javascript
// ❌ Don't: Shard on unevenly distributed field
sh.shardCollection("sales", { country: 1 })

// If 80% of sales are from USA:
// ┌────────────────────────────────────────────┐
// │ Shard 1: USA (80% of data) - OVERLOADED   │
// │ Shard 2: All other countries (20%)        │
// └────────────────────────────────────────────┘

// ✓ Instead: Add more granularity
sh.shardCollection("sales", { country: 1, region: 1, saleId: 1 })
// Or use zones to manually balance
```

### Anti-Pattern 4: Missing Index Before Sharding

```javascript
// ❌ Don't: Shard without existing index
sh.shardCollection("data", { field1: 1 })
// Error: Can't shard, no index

// ✓ Always: Create index first
db.data.createIndex({ field1: 1 })
sh.shardCollection("data", { field1: 1 })

// For hashed:
db.data.createIndex({ field1: "hashed" })
sh.shardCollection("data", { field1: "hashed" })
```

### Anti-Pattern 5: Array Shard Key

```javascript
// ❌ Don't: Use array field as shard key
// Arrays create multikey indexes - not allowed for sharding

// Document:
{
  _id: 1,
  tags: ["mongodb", "database", "nosql"]  // Can't shard on this
}

// ✓ Instead: Extract to separate field or collection
{
  _id: 1,
  primaryTag: "mongodb",  // Shard on this
  tags: ["mongodb", "database", "nosql"]
}
```

---

## Changing Shard Keys

### Before MongoDB 5.0

```javascript
// Changing shard key was NOT supported

// Options:
// 1. Create new collection with new shard key
// 2. Export, drop, re-shard, import
// 3. Add shard key suffix field (refine)

// Option 1: New collection approach
// 1. Create new sharded collection
sh.shardCollection("mydb.orders_new", { customerId: 1, orderId: 1 })

// 2. Copy data
db.orders.find().forEach(doc => {
  db.orders_new.insertOne(doc)
})

// 3. Rename collections
db.orders.renameCollection("orders_old")
db.orders_new.renameCollection("orders")
```

### MongoDB 5.0+: Refine Shard Key

```javascript
// Add suffix fields to existing shard key

// Current shard key:
{ customerId: 1 }

// Refine to:
{ customerId: 1, orderId: 1 }

// Command:
db.adminCommand({
  refineCollectionShardKey: "mydb.orders",
  key: { customerId: 1, orderId: 1 }
})

// Requirements:
// - Can only ADD fields (suffix)
// - Cannot remove or change existing fields
// - New fields must be in existing index
// - Documents must have the new field (or null)
```

### MongoDB 5.0+: Reshard Collection

```javascript
// Completely change shard key (with resharding)

// Current: { orderId: 1 }
// New: { customerId: 1 }

// Reshard command
db.adminCommand({
  reshardCollection: "mydb.orders",
  key: { customerId: 1 }
})

// Monitor progress
db.adminCommand({ currentOp: true, desc: "ReshardingCoordinator" })

// Notes:
// - Creates new chunks in background
// - Minimal impact on running operations
// - Can take significant time for large collections
// - Doubles storage temporarily
```

### Shard Key Change Decision

```
┌─────────────────────────────────────────────────────────────────────┐
│             Shard Key Change Decision Tree                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Need to change shard key?                                         │
│       │                                                            │
│       ├─── Want to ADD fields to key?                              │
│       │        │                                                   │
│       │        └─── YES → Use refineCollectionShardKey             │
│       │                   (MongoDB 5.0+)                           │
│       │                                                            │
│       ├─── Want DIFFERENT key entirely?                            │
│       │        │                                                   │
│       │        ├─── MongoDB 5.0+ → Use reshardCollection           │
│       │        │                                                   │
│       │        └─── Older version → Manual migration               │
│       │                                                            │
│       └─── Can tolerate downtime?                                  │
│                │                                                   │
│                ├─── YES → Export/Import approach                   │
│                │                                                   │
│                └─── NO → Live migration with dual-write            │
│                                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Shard Key Properties

| Property | Good | Bad |
|----------|------|-----|
| Cardinality | High (many values) | Low (few values) |
| Frequency | Uniform | Skewed |
| Monotonicity | Non-monotonic | Monotonic |
| Query Pattern | Matches key | Doesn't match |

### Shard Key Strategies

| Strategy | Best For | Trade-offs |
|----------|----------|------------|
| Ranged | Range queries | Can have hot spots |
| Hashed | Even distribution | No range queries |
| Compound | Multiple patterns | More complex |
| Zone | Geographic locality | Manual management |

### Common Mistakes

| Mistake | Impact | Solution |
|---------|--------|----------|
| Low cardinality | Limited shards | Use compound key |
| Monotonic key | Write hot spot | Hash or compound |
| Skewed distribution | Imbalanced shards | Better key selection |
| Ignoring query patterns | Scatter-gather | Match key to queries |

### What's Next?

In the next chapter, we'll cover setting up a Sharded Cluster.

---

## Practice Questions

1. What are the four properties of a good shard key?
2. Why is monotonically increasing bad for ranged shard keys?
3. When would you use a hashed shard key?
4. What is a compound shard key?
5. How does zone sharding help with geographic distribution?
6. What happens with a low cardinality shard key?
7. Can you change a shard key after creation?
8. What is the refineCollectionShardKey command?

---

## Hands-On Exercises

### Exercise 1: Shard Key Evaluator

```javascript
// Comprehensive shard key evaluation tool

function evaluateShardKey(collectionName, field, options = {}) {
  print(`=== Shard Key Evaluation: ${field} ===\n`)
  
  const coll = db[collectionName]
  const total = coll.countDocuments()
  const sampleSize = Math.min(10000, total)
  
  if (total === 0) {
    print("Collection is empty")
    return
  }
  
  // 1. Cardinality
  print("1. CARDINALITY")
  const distinctCount = coll.distinct(field).length
  const cardinalityRatio = (distinctCount / total * 100)
  
  let cardinalityScore
  if (cardinalityRatio > 50) {
    cardinalityScore = "Excellent"
  } else if (cardinalityRatio > 20) {
    cardinalityScore = "Good"
  } else if (cardinalityRatio > 5) {
    cardinalityScore = "Fair"
  } else {
    cardinalityScore = "Poor"
  }
  
  print(`   Unique values: ${distinctCount}`)
  print(`   Cardinality ratio: ${cardinalityRatio.toFixed(2)}%`)
  print(`   Assessment: ${cardinalityScore}`)
  print()
  
  // 2. Frequency Distribution
  print("2. FREQUENCY DISTRIBUTION")
  const distribution = coll.aggregate([
    { $group: { _id: `$${field}`, count: { $sum: 1 } } },
    { $sort: { count: -1 } },
    { $limit: 5 }
  ]).toArray()
  
  const topPct = (distribution[0]?.count / total * 100) || 0
  let frequencyScore
  if (topPct < 5) {
    frequencyScore = "Excellent"
  } else if (topPct < 15) {
    frequencyScore = "Good"
  } else if (topPct < 30) {
    frequencyScore = "Fair"
  } else {
    frequencyScore = "Poor"
  }
  
  print("   Top 5 values:")
  distribution.forEach(d => {
    const pct = (d.count / total * 100).toFixed(2)
    print(`     ${d._id}: ${d.count} (${pct}%)`)
  })
  print(`   Assessment: ${frequencyScore}`)
  print()
  
  // 3. Check for monotonicity (sample-based)
  print("3. MONOTONICITY CHECK")
  const sample = coll.find({}, { [field]: 1, _id: 1 })
    .sort({ _id: 1 })
    .limit(100)
    .toArray()
  
  let increasing = 0
  let decreasing = 0
  
  for (let i = 1; i < sample.length; i++) {
    const prev = sample[i-1][field]
    const curr = sample[i][field]
    
    if (curr > prev) increasing++
    else if (curr < prev) decreasing++
  }
  
  const monotonic = increasing > sample.length * 0.9 || 
                    decreasing > sample.length * 0.9
  
  let monotonicScore = monotonic ? "Poor (monotonic)" : "Good (non-monotonic)"
  print(`   Increasing trend: ${(increasing / sample.length * 100).toFixed(0)}%`)
  print(`   Assessment: ${monotonicScore}`)
  print()
  
  // 4. Overall recommendation
  print("4. OVERALL RECOMMENDATION")
  
  const scores = {
    cardinality: cardinalityRatio > 20 ? 1 : 0,
    frequency: topPct < 20 ? 1 : 0,
    monotonicity: !monotonic ? 1 : 0
  }
  
  const totalScore = Object.values(scores).reduce((a, b) => a + b, 0)
  
  if (totalScore === 3) {
    print("   ✓ RECOMMENDED as shard key")
  } else if (totalScore === 2) {
    print("   ! ACCEPTABLE - consider compound key for improvement")
  } else {
    print("   ✗ NOT RECOMMENDED - look for better alternatives")
  }
  
  print("\n   Scores:")
  Object.entries(scores).forEach(([k, v]) => {
    const icon = v ? "✓" : "✗"
    print(`     ${icon} ${k}`)
  })
  
  return { distinctCount, cardinalityRatio, topPct, monotonic, totalScore }
}

// Create test data
db.shardKeyEval.drop()
for (let i = 0; i < 1000; i++) {
  db.shardKeyEval.insertOne({
    customerId: `customer_${Math.floor(Math.random() * 200)}`,
    status: ["pending", "active", "completed"][Math.floor(Math.random() * 3)],
    orderId: `order_${i.toString().padStart(6, "0")}`,
    timestamp: new Date(Date.now() - Math.random() * 86400000 * 30)
  })
}

// Evaluate different fields
print("Evaluating customerId:")
evaluateShardKey("shardKeyEval", "customerId")

print("\n" + "=".repeat(60) + "\n")

print("Evaluating status:")
evaluateShardKey("shardKeyEval", "status")

print("\n" + "=".repeat(60) + "\n")

print("Evaluating orderId:")
evaluateShardKey("shardKeyEval", "orderId")
```

### Exercise 2: Compound Key Designer

```javascript
// Design optimal compound shard key

function designCompoundKey(collectionName, candidateFields, queryPatterns) {
  print("=== Compound Shard Key Designer ===\n")
  
  const coll = db[collectionName]
  const total = coll.countDocuments()
  
  // Analyze each field
  print("Field Analysis:")
  const fieldStats = {}
  
  candidateFields.forEach(field => {
    const distinct = coll.distinct(field).length
    const ratio = (distinct / total * 100).toFixed(2)
    fieldStats[field] = { distinct, ratio: parseFloat(ratio) }
    print(`  ${field}: ${distinct} unique (${ratio}%)`)
  })
  
  print()
  
  // Check query patterns
  print("Query Pattern Analysis:")
  queryPatterns.forEach((pattern, i) => {
    const matchingFields = candidateFields.filter(f => pattern.fields.includes(f))
    const coverage = (matchingFields.length / pattern.fields.length * 100).toFixed(0)
    print(`  Q${i + 1}: ${JSON.stringify(pattern.fields)}`)
    print(`      Frequency: ${pattern.frequency}, Coverage: ${coverage}%`)
  })
  
  print()
  
  // Generate compound key recommendations
  print("Compound Key Recommendations:\n")
  
  // Strategy: High frequency field + High cardinality field
  const sortedByCardinality = [...candidateFields]
    .sort((a, b) => fieldStats[b].ratio - fieldStats[a].ratio)
  
  // Find field that matches most query patterns
  const fieldQueryCoverage = {}
  candidateFields.forEach(field => {
    fieldQueryCoverage[field] = queryPatterns
      .filter(p => p.fields.includes(field))
      .reduce((sum, p) => sum + (p.frequency === "high" ? 3 : p.frequency === "medium" ? 2 : 1), 0)
  })
  
  const sortedByCoverage = [...candidateFields]
    .sort((a, b) => fieldQueryCoverage[b] - fieldQueryCoverage[a])
  
  // Recommendation 1: Query-optimized
  print("Option 1: Query-Optimized")
  print(`  Key: { ${sortedByCoverage[0]}: 1, ${sortedByCardinality[0]}: 1 }`)
  print(`  Rationale: Prioritizes query targeting`)
  print()
  
  // Recommendation 2: Distribution-optimized
  print("Option 2: Distribution-Optimized")
  print(`  Key: { ${sortedByCardinality[0]}: 1, ${sortedByCardinality[1] || sortedByCoverage[0]}: 1 }`)
  print(`  Rationale: Prioritizes even data distribution`)
  print()
  
  // Recommendation 3: Hashed option
  print("Option 3: Hashed Primary")
  print(`  Key: { ${sortedByCardinality[0]}: "hashed" }`)
  print(`  Rationale: Maximum write distribution, sacrifice range queries`)
  
  return { fieldStats, fieldQueryCoverage }
}

// Example: E-commerce orders
db.designTest.drop()
for (let i = 0; i < 500; i++) {
  db.designTest.insertOne({
    customerId: `C${Math.floor(Math.random() * 100).toString().padStart(3, "0")}`,
    region: ["US", "EU", "APAC"][Math.floor(Math.random() * 3)],
    status: ["pending", "shipped", "delivered"][Math.floor(Math.random() * 3)],
    orderId: `O${i.toString().padStart(6, "0")}`
  })
}

designCompoundKey(
  "designTest",
  ["customerId", "region", "status", "orderId"],
  [
    { fields: ["customerId"], frequency: "high" },
    { fields: ["customerId", "status"], frequency: "medium" },
    { fields: ["region"], frequency: "low" },
    { fields: ["orderId"], frequency: "medium" }
  ]
)
```

### Exercise 3: Shard Key Anti-Pattern Detector

```javascript
// Detect shard key anti-patterns

function detectAntiPatterns(collectionName, proposedKey) {
  print("=== Shard Key Anti-Pattern Detection ===\n")
  print(`Collection: ${collectionName}`)
  print(`Proposed Key: ${JSON.stringify(proposedKey)}`)
  print()
  
  const coll = db[collectionName]
  const total = coll.countDocuments()
  const issues = []
  const warnings = []
  
  const keyFields = Object.keys(proposedKey)
  
  // Check each field
  keyFields.forEach((field, index) => {
    const isHashed = proposedKey[field] === "hashed"
    
    // Anti-pattern 1: Array field
    const sampleWithArray = coll.findOne({ [field]: { $type: "array" } })
    if (sampleWithArray) {
      issues.push({
        pattern: "Array Shard Key",
        field,
        description: "Arrays cannot be used as shard keys",
        severity: "CRITICAL"
      })
    }
    
    // Anti-pattern 2: Low cardinality
    const distinct = coll.distinct(field).length
    const cardinalityRatio = distinct / total * 100
    
    if (cardinalityRatio < 1) {
      issues.push({
        pattern: "Very Low Cardinality",
        field,
        description: `Only ${distinct} unique values for ${total} documents`,
        severity: "HIGH"
      })
    } else if (cardinalityRatio < 10 && index === 0) {
      warnings.push({
        pattern: "Low Cardinality (first field)",
        field,
        description: `${distinct} unique values may limit scalability`,
        severity: "MEDIUM"
      })
    }
    
    // Anti-pattern 3: Highly skewed
    const topValue = coll.aggregate([
      { $group: { _id: `$${field}`, count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 1 }
    ]).toArray()[0]
    
    const topPct = topValue ? (topValue.count / total * 100) : 0
    
    if (topPct > 50) {
      issues.push({
        pattern: "Highly Skewed Distribution",
        field,
        description: `${topPct.toFixed(1)}% of data has value "${topValue._id}"`,
        severity: "HIGH"
      })
    } else if (topPct > 30) {
      warnings.push({
        pattern: "Skewed Distribution",
        field,
        description: `${topPct.toFixed(1)}% of data in single value`,
        severity: "MEDIUM"
      })
    }
    
    // Anti-pattern 4: Monotonic (check if it looks like ObjectId or timestamp)
    if (!isHashed && (field === "_id" || field.includes("timestamp") || field.includes("created"))) {
      warnings.push({
        pattern: "Potentially Monotonic",
        field,
        description: "Field may be monotonically increasing - consider hashing",
        severity: "MEDIUM"
      })
    }
  })
  
  // Display results
  print("ISSUES (Must Fix):")
  if (issues.length === 0) {
    print("  None detected ✓")
  } else {
    issues.forEach(i => {
      print(`  ✗ [${i.severity}] ${i.pattern}`)
      print(`    Field: ${i.field}`)
      print(`    ${i.description}`)
    })
  }
  print()
  
  print("WARNINGS (Review Recommended):")
  if (warnings.length === 0) {
    print("  None detected ✓")
  } else {
    warnings.forEach(w => {
      print(`  ! [${w.severity}] ${w.pattern}`)
      print(`    Field: ${w.field}`)
      print(`    ${w.description}`)
    })
  }
  print()
  
  // Final verdict
  print("VERDICT:")
  if (issues.length > 0) {
    print("  ✗ DO NOT USE this shard key - critical issues found")
  } else if (warnings.length > 0) {
    print("  ! REVIEW carefully before using")
  } else {
    print("  ✓ Shard key appears suitable")
  }
  
  return { issues, warnings }
}

// Create test data with anti-patterns
db.antiPatternTest.drop()
for (let i = 0; i < 1000; i++) {
  db.antiPatternTest.insertOne({
    status: i < 800 ? "active" : "inactive",  // Skewed
    category: "electronics",  // Very low cardinality
    tags: ["tag1", "tag2"],  // Array
    userId: `user_${Math.floor(Math.random() * 500)}`,  // Good
    createdAt: new Date()  // Monotonic
  })
}

// Test various proposed keys
print("Testing { status: 1 }:")
detectAntiPatterns("antiPatternTest", { status: 1 })

print("\n" + "=".repeat(60) + "\n")

print("Testing { tags: 1 }:")
detectAntiPatterns("antiPatternTest", { tags: 1 })

print("\n" + "=".repeat(60) + "\n")

print("Testing { userId: 1 }:")
detectAntiPatterns("antiPatternTest", { userId: 1 })
```

### Exercise 4: Query Routing Analyzer

```javascript
// Analyze how queries route with a given shard key

function analyzeQueryRouting(shardKey, queries) {
  print("=== Query Routing Analysis ===\n")
  print(`Shard Key: ${JSON.stringify(shardKey)}`)
  print()
  
  const keyFields = Object.keys(shardKey)
  const firstField = keyFields[0]
  
  print("Query Routing Results:\n")
  print("┌" + "─".repeat(58) + "┐")
  print("│ Query" + " ".repeat(32) + "│ Routing" + " ".repeat(8) + "│")
  print("├" + "─".repeat(58) + "┤")
  
  queries.forEach(query => {
    const queryFields = Object.keys(query.filter || query)
    
    // Determine routing type
    let routingType
    let icon
    
    // Check if query includes shard key prefix
    const hasKeyPrefix = queryFields.includes(firstField)
    const hasFullKey = keyFields.every(k => queryFields.includes(k))
    
    if (hasFullKey) {
      routingType = "TARGETED (full key)"
      icon = "✓✓"
    } else if (hasKeyPrefix) {
      routingType = "TARGETED (prefix)"
      icon = "✓"
    } else {
      routingType = "SCATTER-GATHER"
      icon = "✗"
    }
    
    const queryStr = JSON.stringify(query).substring(0, 35).padEnd(35)
    const routingStr = (icon + " " + routingType).padEnd(18)
    
    print(`│ ${queryStr} │ ${routingStr}│`)
  })
  
  print("└" + "─".repeat(58) + "┘")
  
  // Summary
  const targeted = queries.filter(q => {
    const fields = Object.keys(q.filter || q)
    return fields.includes(firstField)
  }).length
  
  print()
  print("Summary:")
  print(`  Targeted queries: ${targeted}/${queries.length}`)
  print(`  Scatter-gather queries: ${queries.length - targeted}/${queries.length}`)
  
  if (targeted < queries.length * 0.5) {
    print()
    print("  ⚠ Warning: Most queries don't target the shard key")
    print("    Consider changing the shard key to match query patterns")
  }
}

// Example: E-commerce with customerId: 1, orderId: 1 shard key
analyzeQueryRouting(
  { customerId: 1, orderId: 1 },
  [
    { customerId: "C123" },
    { customerId: "C123", orderId: "O456" },
    { orderId: "O789" },
    { status: "pending" },
    { customerId: "C123", status: "pending" },
    { createdAt: { $gte: "2024-01-01" } }
  ]
)
```

---

[← Previous: Sharding Concepts](44-sharding-concepts.md) | [Next: Sharded Cluster Setup →](46-sharded-cluster-setup.md)
