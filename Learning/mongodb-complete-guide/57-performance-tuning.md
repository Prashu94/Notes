# Chapter 57: Performance Tuning

## Table of Contents
- [Performance Tuning Overview](#performance-tuning-overview)
- [Query Optimization](#query-optimization)
- [Index Optimization](#index-optimization)
- [Schema Optimization](#schema-optimization)
- [Hardware Considerations](#hardware-considerations)
- [Configuration Tuning](#configuration-tuning)
- [Summary](#summary)

---

## Performance Tuning Overview

### Performance Tuning Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Performance Tuning Workflow                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  1. MEASURE │───►│ 2. ANALYZE  │───►│ 3. OPTIMIZE │             │
│  └─────────────┘    └─────────────┘    └─────────────┘             │
│        │                                      │                     │
│        │                                      │                     │
│        └──────────────────────────────────────┘                     │
│                    4. REPEAT                                        │
│                                                                     │
│  Measure:                                                          │
│  • Query execution times                                           │
│  • Resource utilization                                            │
│  • Throughput metrics                                              │
│                                                                     │
│  Analyze:                                                          │
│  • Identify bottlenecks                                            │
│  • Review query plans                                              │
│  • Profile slow operations                                         │
│                                                                     │
│  Optimize:                                                         │
│  • Add/modify indexes                                              │
│  • Rewrite queries                                                 │
│  • Adjust configuration                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Performance Metrics

| Metric | Target | Warning | Critical |
|--------|--------|---------|----------|
| Query latency (p95) | < 50ms | > 100ms | > 500ms |
| Scan to return ratio | < 1.5 | > 5 | > 10 |
| Index hit ratio | > 99% | < 95% | < 90% |
| Page faults/sec | < 10 | > 50 | > 100 |
| Lock % | < 5% | > 20% | > 50% |

---

## Query Optimization

### Using explain()

```javascript
// Basic explain
db.orders.find({ status: "pending" }).explain()

// Execution stats (recommended)
db.orders.find({ status: "pending" }).explain("executionStats")

// All plans considered
db.orders.find({ status: "pending" }).explain("allPlansExecution")
```

### Understanding Explain Output

```javascript
// Key fields to analyze
{
  "queryPlanner": {
    "winningPlan": {
      "stage": "FETCH",           // Final stage
      "inputStage": {
        "stage": "IXSCAN",        // Good: Using index
        "keyPattern": { "status": 1 },
        "indexName": "status_1"
      }
    }
  },
  "executionStats": {
    "executionSuccess": true,
    "nReturned": 100,             // Documents returned
    "executionTimeMillis": 5,     // Total time
    "totalKeysExamined": 100,     // Index keys scanned
    "totalDocsExamined": 100      // Documents scanned
  }
}

// Efficiency ratio
// totalDocsExamined / nReturned should be close to 1
// If >> 1, index is not selective enough
```

### Query Plan Stages

| Stage | Description | Performance |
|-------|-------------|-------------|
| COLLSCAN | Full collection scan | Poor |
| IXSCAN | Index scan | Good |
| FETCH | Retrieve documents | Depends |
| SORT | In-memory sort | Can be slow |
| SORT_KEY_GENERATOR | Generate sort keys | Moderate |
| PROJECTION | Apply projection | Fast |
| LIMIT | Limit results | Fast |
| SKIP | Skip results | Moderate |

### Optimizing Slow Queries

```javascript
// Bad: Collection scan
db.orders.find({
  customerId: "C123",
  status: "shipped",
  orderDate: { $gte: ISODate("2024-01-01") }
})
// Plan: COLLSCAN

// Better: Add compound index
db.orders.createIndex({ 
  customerId: 1, 
  status: 1, 
  orderDate: -1 
})
// Plan: IXSCAN

// Even better: Covered query (include projection fields in index)
db.orders.createIndex({ 
  customerId: 1, 
  status: 1, 
  orderDate: -1,
  total: 1
})

db.orders.find(
  { customerId: "C123", status: "shipped" },
  { _id: 0, orderDate: 1, total: 1 }  // All fields in index
)
// Plan: IXSCAN (covered - no FETCH needed)
```

### Query Anti-Patterns

```javascript
// Anti-pattern 1: $regex without anchor
// Bad
db.users.find({ email: /gmail/ })
// Better
db.users.find({ email: /^.*gmail\.com$/ })
// Best (if possible)
db.users.find({ emailDomain: "gmail.com" })

// Anti-pattern 2: $ne and $nin (can't use index efficiently)
// Bad
db.products.find({ status: { $ne: "deleted" } })
// Better
db.products.find({ status: { $in: ["active", "pending", "sold"] } })

// Anti-pattern 3: $where (executes JavaScript)
// Bad
db.orders.find({ $where: "this.total > this.discount * 2" })
// Better
db.orders.find({ 
  $expr: { $gt: ["$total", { $multiply: ["$discount", 2] }] }
})

// Anti-pattern 4: Large skip values
// Bad
db.products.find().skip(100000).limit(20)
// Better: Use range-based pagination
db.products.find({ _id: { $gt: lastId } }).limit(20)
```

---

## Index Optimization

### Index Analysis

```javascript
// List all indexes
db.collection.getIndexes()

// Index statistics
db.collection.aggregate([{ $indexStats: {} }])

// Find unused indexes
db.collection.aggregate([
  { $indexStats: {} },
  { $match: { "accesses.ops": 0 } }
])

// Find duplicate indexes
function findDuplicateIndexes(collName) {
  const indexes = db.getCollection(collName).getIndexes()
  const duplicates = []
  
  for (let i = 0; i < indexes.length; i++) {
    for (let j = i + 1; j < indexes.length; j++) {
      const keys1 = Object.keys(indexes[i].key)
      const keys2 = Object.keys(indexes[j].key)
      
      // Check if one is prefix of another
      let isPrefix = true
      const minLen = Math.min(keys1.length, keys2.length)
      
      for (let k = 0; k < minLen; k++) {
        if (keys1[k] !== keys2[k] || 
            indexes[i].key[keys1[k]] !== indexes[j].key[keys2[k]]) {
          isPrefix = false
          break
        }
      }
      
      if (isPrefix) {
        duplicates.push({
          index1: indexes[i].name,
          index2: indexes[j].name,
          reason: "One is prefix of another"
        })
      }
    }
  }
  
  return duplicates
}
```

### Index Size Management

```javascript
// Check index sizes
db.collection.stats().indexSizes

// Total index size
db.collection.totalIndexSize()

// Index should fit in RAM
// Check with:
const stats = db.serverStatus()
const cacheSize = stats.wiredTiger.cache["maximum bytes configured"]
const indexSize = db.collection.totalIndexSize()

if (indexSize > cacheSize * 0.5) {
  print("Warning: Index size exceeds 50% of cache")
}
```

### Optimal Index Design

```javascript
// ESR Rule: Equality, Sort, Range
// Order index fields as: Equality → Sort → Range

// Query pattern
db.orders.find({
  status: "shipped",           // Equality
  customerId: "C123"           // Equality
}).sort({ 
  orderDate: -1                // Sort
}).limit(10)

// Optimal index
db.orders.createIndex({
  status: 1,                   // E
  customerId: 1,               // E
  orderDate: -1                // S
})

// For queries with range conditions
db.orders.find({
  status: "shipped",           // Equality
  orderDate: { $gte: date }    // Range
}).sort({ 
  total: -1                    // Sort
})

// Index: Equality → Sort → Range
db.orders.createIndex({
  status: 1,                   // E
  total: -1,                   // S
  orderDate: -1                // R
})
```

### Partial Indexes

```javascript
// Index only active documents
db.users.createIndex(
  { email: 1 },
  { 
    partialFilterExpression: { status: "active" },
    name: "email_active"
  }
)

// Smaller index, faster updates
// Only use for queries that match the filter

// Query must include filter condition
db.users.find({ 
  email: "user@example.com", 
  status: "active"  // Must include this!
})
```

---

## Schema Optimization

### Document Size Optimization

```javascript
// Check average document size
db.collection.stats().avgObjSize

// Use shorter field names for high-volume collections
// Instead of:
{
  "customerFirstName": "John",
  "customerLastName": "Doe",
  "customerEmailAddress": "john@example.com"
}

// Use:
{
  "fn": "John",
  "ln": "Doe",
  "em": "john@example.com"
}
// Savings: ~30 bytes per document

// For millions of documents, this adds up!
```

### Embedding vs Referencing

```javascript
// Embed when:
// - Data is accessed together
// - One-to-few relationship
// - Data doesn't change often

// Embedded (good for blog posts with comments)
{
  _id: ObjectId("..."),
  title: "My Post",
  comments: [
    { user: "Alice", text: "Great post!" },
    { user: "Bob", text: "Thanks!" }
  ]
}

// Reference when:
// - Data is accessed independently
// - One-to-many or many-to-many
// - Data changes frequently

// Referenced (good for orders with many items)
// Order document
{ _id: "ORD123", customerId: "C1", total: 500 }

// Order items (separate collection)
{ orderId: "ORD123", productId: "P1", qty: 2 }
{ orderId: "ORD123", productId: "P2", qty: 1 }
```

### Bucket Pattern

```javascript
// Instead of one document per measurement
// (millions of small documents)
{
  _id: ObjectId("..."),
  sensorId: "S1",
  timestamp: ISODate("2024-01-15T10:30:00Z"),
  value: 23.5
}

// Use bucket pattern (fewer, larger documents)
{
  _id: ObjectId("..."),
  sensorId: "S1",
  startTime: ISODate("2024-01-15T10:00:00Z"),
  endTime: ISODate("2024-01-15T11:00:00Z"),
  count: 60,
  measurements: [
    { t: ISODate("2024-01-15T10:00:00Z"), v: 23.1 },
    { t: ISODate("2024-01-15T10:01:00Z"), v: 23.2 },
    // ... up to 60 measurements per hour
  ],
  stats: {
    min: 22.8,
    max: 24.1,
    avg: 23.5
  }
}

// Benefits:
// - Fewer documents = smaller index
// - Better read performance
// - Pre-computed statistics
```

### Computed Pattern

```javascript
// Store computed values instead of calculating
// Bad: Calculate on every read
db.orders.aggregate([
  { $match: { customerId: "C123" } },
  { $group: { 
    _id: "$customerId", 
    totalOrders: { $sum: 1 },
    totalSpent: { $sum: "$total" }
  }}
])

// Better: Pre-compute and store
// Customer document
{
  _id: "C123",
  name: "John Doe",
  stats: {
    totalOrders: 150,
    totalSpent: 25000,
    lastOrderDate: ISODate("2024-01-15")
  }
}

// Update stats when order is placed
db.customers.updateOne(
  { _id: "C123" },
  {
    $inc: { 
      "stats.totalOrders": 1, 
      "stats.totalSpent": orderTotal 
    },
    $set: { "stats.lastOrderDate": new Date() }
  }
)
```

---

## Hardware Considerations

### Memory Sizing

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Memory Recommendations                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Working Set = Frequently accessed data + indexes                  │
│                                                                     │
│  Ideal: Working Set fits in RAM                                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        Total RAM                            │   │
│  │  ┌─────────────────────────────────────────────────────┐   │   │
│  │  │              WiredTiger Cache (50%)                 │   │   │
│  │  │  ┌───────────────────────────────────────────────┐ │   │   │
│  │  │  │    Indexes + Hot Data                         │ │   │   │
│  │  │  └───────────────────────────────────────────────┘ │   │   │
│  │  └─────────────────────────────────────────────────────┘   │   │
│  │  ┌───────────────────┐  ┌───────────────────────────┐     │   │
│  │  │ OS + Other (25%)  │  │ Connections + Ops (25%)   │     │   │
│  │  └───────────────────┘  └───────────────────────────┘     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Formula:                                                          │
│  Required RAM = (Total Index Size + Hot Data) / 0.5                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Storage Optimization

```yaml
# Use SSDs for best performance
# RAID 10 for production

# mongod.conf storage settings
storage:
  dbPath: /data/db
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # Adjust based on RAM
    collectionConfig:
      blockCompressor: snappy  # or zlib, zstd
    indexConfig:
      prefixCompression: true
```

### CPU Considerations

```javascript
// MongoDB is multi-threaded
// More cores = better concurrency

// Check current thread usage
db.serverStatus().wiredTiger.concurrentTransactions

// Read tickets (default 128)
// Write tickets (default 128)

// If seeing ticket exhaustion, consider:
// - More CPU cores
// - Reduce long-running operations
// - Optimize queries
```

---

## Configuration Tuning

### WiredTiger Cache

```yaml
# mongod.conf
storage:
  wiredTiger:
    engineConfig:
      # Default: 50% of (RAM - 1GB) or 256MB, whichever is larger
      cacheSizeGB: 8
```

```javascript
// Monitor cache usage
const cache = db.serverStatus().wiredTiger.cache
const used = cache["bytes currently in the cache"]
const max = cache["maximum bytes configured"]
const pct = (used / max * 100).toFixed(1)

print(`Cache usage: ${pct}%`)

// If consistently > 95%, increase cache size
// If < 50%, may be able to reduce
```

### Connection Pool

```yaml
# mongod.conf
net:
  maxIncomingConnections: 65536  # Default
```

```javascript
// Application connection pool settings (Node.js example)
const client = new MongoClient(uri, {
  maxPoolSize: 100,      // Max connections per host
  minPoolSize: 10,       // Min connections to maintain
  maxIdleTimeMS: 30000,  // Close idle connections after 30s
  waitQueueTimeoutMS: 5000  // Fail if can't get connection in 5s
})
```

### Read/Write Concerns

```javascript
// Balance consistency vs performance

// Write concern
db.collection.insertOne(
  { doc: "data" },
  { 
    writeConcern: { 
      w: 1,           // Acknowledge after primary
      // w: "majority" // Acknowledge after majority (slower, safer)
      j: false        // Don't wait for journal (faster, less durable)
    }
  }
)

// Read concern
db.collection.find().readConcern("local")      // Fastest
db.collection.find().readConcern("majority")   // Consistent
db.collection.find().readConcern("linearizable") // Strongest (slowest)

// Read preference
db.collection.find().readPref("secondaryPreferred") // Distribute load
```

---

## Summary

### Optimization Priority

| Priority | Area | Impact |
|----------|------|--------|
| 1 | Query optimization | Highest |
| 2 | Index design | High |
| 3 | Schema design | High |
| 4 | Hardware | Medium |
| 5 | Configuration | Medium |

### Key Tuning Parameters

| Parameter | Default | Tuning Guidance |
|-----------|---------|-----------------|
| WiredTiger cache | 50% RAM | Adjust based on working set |
| Read concern | local | Use majority for consistency |
| Write concern | 1 | Use majority for durability |
| Connection pool | varies | Match expected concurrency |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Profile before optimizing | Target real bottlenecks |
| Test changes in staging | Avoid production issues |
| Monitor after changes | Verify improvement |
| Document optimizations | Future reference |

### What's Next?

In the next chapter, we'll explore Memory Management.

---

## Practice Questions

1. What does COLLSCAN in explain output indicate?
2. What is the ESR rule for index design?
3. When should you use partial indexes?
4. How do you identify unused indexes?
5. What is the bucket pattern?
6. How much RAM should WiredTiger cache use?
7. What are the trade-offs of different write concerns?
8. How do you optimize range queries with sorting?

---

## Hands-On Exercises

### Exercise 1: Query Performance Analyzer

```javascript
// Analyze query performance

function analyzeQueryPerformance(query, collection) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           QUERY PERFORMANCE ANALYZER                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const coll = db.getCollection(collection)
  
  // Run explain
  const explain = coll.find(query).explain("executionStats")
  const stats = explain.executionStats
  const plan = explain.queryPlanner.winningPlan
  
  print("Query:")
  print(JSON.stringify(query, null, 2))
  print()
  
  // Performance metrics
  print("┌─ PERFORMANCE METRICS ─────────────────────────────────────┐")
  print(`│  Execution Time: ${stats.executionTimeMillis}ms`.padEnd(60) + "│")
  print(`│  Documents Returned: ${stats.nReturned}`.padEnd(60) + "│")
  print(`│  Documents Examined: ${stats.totalDocsExamined}`.padEnd(60) + "│")
  print(`│  Keys Examined: ${stats.totalKeysExamined}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Efficiency analysis
  print("┌─ EFFICIENCY ANALYSIS ─────────────────────────────────────┐")
  
  const docEfficiency = stats.nReturned > 0 
    ? (stats.nReturned / stats.totalDocsExamined * 100).toFixed(1)
    : 0
  const keyEfficiency = stats.nReturned > 0 && stats.totalKeysExamined > 0
    ? (stats.nReturned / stats.totalKeysExamined * 100).toFixed(1)
    : 100
  
  print(`│  Document Efficiency: ${docEfficiency}%`.padEnd(60) + "│")
  print(`│  Key Efficiency: ${keyEfficiency}%`.padEnd(60) + "│")
  
  // Get plan stages
  function getStages(plan, depth = 0) {
    const stages = []
    stages.push({ stage: plan.stage, depth })
    if (plan.inputStage) {
      stages.push(...getStages(plan.inputStage, depth + 1))
    }
    if (plan.inputStages) {
      plan.inputStages.forEach(s => stages.push(...getStages(s, depth + 1)))
    }
    return stages
  }
  
  const stages = getStages(plan)
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Query plan
  print("┌─ QUERY PLAN ──────────────────────────────────────────────┐")
  stages.forEach(s => {
    const indent = "  ".repeat(s.depth)
    print(`│  ${indent}${s.stage}`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recommendations
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  const recommendations = []
  
  if (stages.some(s => s.stage === 'COLLSCAN')) {
    recommendations.push("⚠ COLLSCAN detected - Add index for query fields")
  }
  
  if (stages.some(s => s.stage === 'SORT') && !stages.some(s => s.stage === 'SORT_MERGE')) {
    recommendations.push("⚠ In-memory SORT - Consider index for sort fields")
  }
  
  if (parseFloat(docEfficiency) < 50) {
    recommendations.push("⚠ Low efficiency - Index may not be selective")
  }
  
  if (stats.executionTimeMillis > 100) {
    recommendations.push("⚠ Slow query (>100ms) - Needs optimization")
  }
  
  if (recommendations.length === 0) {
    print("│  ✓ Query appears well-optimized".padEnd(60) + "│")
  } else {
    recommendations.forEach(r => {
      print(`│  ${r}`.padEnd(60) + "│")
    })
  }
  
  print("└────────────────────────────────────────────────────────────┘")
  
  return { stats, plan, recommendations }
}

// Example usage
// analyzeQueryPerformance({ status: "active" }, "users")
```

### Exercise 2: Index Optimizer

```javascript
// Suggest index improvements

function indexOptimizer(collectionName) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           INDEX OPTIMIZER                                   ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const coll = db.getCollection(collectionName)
  
  // Get current indexes
  const indexes = coll.getIndexes()
  print(`Collection: ${collectionName}`)
  print(`Current Indexes: ${indexes.length}\n`)
  
  // Get index usage stats
  const indexStats = coll.aggregate([{ $indexStats: {} }]).toArray()
  
  print("┌─ INDEX USAGE ─────────────────────────────────────────────┐")
  print("│  Index Name                      Operations    Since      │")
  print("├────────────────────────────────────────────────────────────┤")
  
  const unusedIndexes = []
  
  indexStats.forEach(stat => {
    const name = stat.name.substring(0, 30).padEnd(32)
    const ops = String(stat.accesses.ops).padEnd(12)
    const since = stat.accesses.since?.toISOString().split('T')[0] || 'N/A'
    
    print(`│  ${name} ${ops} ${since}  │`)
    
    if (stat.accesses.ops === 0 && stat.name !== '_id_') {
      unusedIndexes.push(stat.name)
    }
  })
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Check for unused indexes
  if (unusedIndexes.length > 0) {
    print("┌─ UNUSED INDEXES (consider dropping) ─────────────────────┐")
    unusedIndexes.forEach(idx => {
      print(`│  • ${idx}`.padEnd(60) + "│")
    })
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Check for duplicate/redundant indexes
  print("┌─ REDUNDANCY CHECK ────────────────────────────────────────┐")
  
  let foundRedundant = false
  for (let i = 0; i < indexes.length; i++) {
    for (let j = i + 1; j < indexes.length; j++) {
      const keys1 = Object.keys(indexes[i].key)
      const keys2 = Object.keys(indexes[j].key)
      
      // Check if one is prefix of another
      const minLen = Math.min(keys1.length, keys2.length)
      let isPrefix = true
      
      for (let k = 0; k < minLen; k++) {
        if (keys1[k] !== keys2[k]) {
          isPrefix = false
          break
        }
      }
      
      if (isPrefix && keys1.length !== keys2.length) {
        foundRedundant = true
        const shorter = keys1.length < keys2.length ? indexes[i].name : indexes[j].name
        const longer = keys1.length < keys2.length ? indexes[j].name : indexes[i].name
        print(`│  ${shorter} is prefix of ${longer}`.padEnd(60) + "│")
      }
    }
  }
  
  if (!foundRedundant) {
    print("│  ✓ No redundant indexes found".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Index size analysis
  print("┌─ INDEX SIZE ANALYSIS ─────────────────────────────────────┐")
  
  const stats = coll.stats()
  const totalIndexSize = stats.totalIndexSize
  const dataSize = stats.size
  const indexRatio = (totalIndexSize / dataSize * 100).toFixed(1)
  
  print(`│  Data Size: ${(dataSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Total Index Size: ${(totalIndexSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Index to Data Ratio: ${indexRatio}%`.padEnd(60) + "│")
  
  if (parseFloat(indexRatio) > 100) {
    print("│  ⚠ Indexes larger than data - review index necessity".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

// Usage
// indexOptimizer("orders")
```

### Exercise 3: Schema Performance Review

```javascript
// Review schema for performance issues

function schemaPerformanceReview(collectionName, sampleSize = 100) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           SCHEMA PERFORMANCE REVIEW                         ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const coll = db.getCollection(collectionName)
  
  // Sample documents
  const sample = coll.aggregate([{ $sample: { size: sampleSize } }]).toArray()
  
  if (sample.length === 0) {
    print("Collection is empty")
    return
  }
  
  // Analyze document structure
  const fieldStats = {}
  let totalSize = 0
  let maxSize = 0
  let arrayFields = new Set()
  let deepNesting = []
  
  function analyzeDocument(doc, prefix = '', depth = 0) {
    for (const [key, value] of Object.entries(doc)) {
      const fullKey = prefix ? `${prefix}.${key}` : key
      
      if (!fieldStats[fullKey]) {
        fieldStats[fullKey] = { count: 0, types: new Set(), sizes: [] }
      }
      
      fieldStats[fullKey].count++
      fieldStats[fullKey].types.add(typeof value)
      
      if (Array.isArray(value)) {
        arrayFields.add(fullKey)
        fieldStats[fullKey].sizes.push(value.length)
      }
      
      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        if (depth > 3) {
          deepNesting.push(fullKey)
        }
        analyzeDocument(value, fullKey, depth + 1)
      }
    }
  }
  
  sample.forEach(doc => {
    const size = Object.bsonsize(doc)
    totalSize += size
    maxSize = Math.max(maxSize, size)
    analyzeDocument(doc)
  })
  
  // Document size analysis
  print("┌─ DOCUMENT SIZE ANALYSIS ──────────────────────────────────┐")
  print(`│  Average Size: ${(totalSize / sample.length / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  print(`│  Max Size: ${(maxSize / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  
  if (maxSize > 1024 * 1024) {
    print("│  ⚠ Documents approaching 16MB limit".padEnd(60) + "│")
  } else if (totalSize / sample.length > 100 * 1024) {
    print("│  ⚠ Large average document size - consider optimization".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Array analysis
  if (arrayFields.size > 0) {
    print("┌─ ARRAY FIELDS ────────────────────────────────────────────┐")
    
    arrayFields.forEach(field => {
      const sizes = fieldStats[field].sizes
      const avgSize = sizes.reduce((a, b) => a + b, 0) / sizes.length
      const maxArraySize = Math.max(...sizes)
      
      print(`│  ${field}`.padEnd(60) + "│")
      print(`│    Avg length: ${avgSize.toFixed(1)}, Max: ${maxArraySize}`.padEnd(60) + "│")
      
      if (maxArraySize > 100) {
        print("│    ⚠ Large array - consider bucketing".padEnd(60) + "│")
      }
    })
    
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Deep nesting
  if (deepNesting.length > 0) {
    print("┌─ DEEP NESTING (>3 levels) ────────────────────────────────┐")
    [...new Set(deepNesting)].slice(0, 5).forEach(field => {
      print(`│  • ${field}`.padEnd(60) + "│")
    })
    print("│  ⚠ Deep nesting can impact query performance".padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Field name length analysis
  const longFieldNames = Object.keys(fieldStats).filter(f => f.length > 20)
  if (longFieldNames.length > 5) {
    print("┌─ LONG FIELD NAMES ────────────────────────────────────────┐")
    print(`│  ${longFieldNames.length} fields with names > 20 chars`.padEnd(60) + "│")
    print("│  Consider shorter names for high-volume collections".padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
  }
}

// Usage
// schemaPerformanceReview("orders")
```

### Exercise 4: Performance Benchmark

```javascript
// Run performance benchmarks

function runBenchmark(options = {}) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           PERFORMANCE BENCHMARK                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const {
    collection = 'benchmark_test',
    iterations = 1000,
    documentSize = 'small'
  } = options
  
  const coll = db.getCollection(collection)
  
  // Generate test document
  function generateDoc(size) {
    const base = {
      timestamp: new Date(),
      counter: 0,
      status: "active"
    }
    
    if (size === 'medium') {
      base.data = "x".repeat(1000)
      base.tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
    } else if (size === 'large') {
      base.data = "x".repeat(10000)
      base.tags = Array(50).fill(0).map((_, i) => `tag${i}`)
      base.nested = { a: { b: { c: { d: "deep" } } } }
    }
    
    return base
  }
  
  // Setup
  coll.drop()
  coll.createIndex({ status: 1 })
  coll.createIndex({ timestamp: -1 })
  
  print(`Document size: ${documentSize}`)
  print(`Iterations: ${iterations}\n`)
  
  const results = {}
  
  // Insert benchmark
  print("Running INSERT benchmark...")
  let start = Date.now()
  for (let i = 0; i < iterations; i++) {
    const doc = generateDoc(documentSize)
    doc.counter = i
    coll.insertOne(doc)
  }
  results.insert = Date.now() - start
  
  // Find by _id benchmark
  print("Running FIND by _id benchmark...")
  const ids = coll.find({}, { _id: 1 }).limit(iterations).toArray().map(d => d._id)
  start = Date.now()
  for (const id of ids) {
    coll.findOne({ _id: id })
  }
  results.findById = Date.now() - start
  
  // Find by index benchmark
  print("Running FIND by index benchmark...")
  start = Date.now()
  for (let i = 0; i < iterations; i++) {
    coll.findOne({ status: "active", counter: i })
  }
  results.findByIndex = Date.now() - start
  
  // Update benchmark
  print("Running UPDATE benchmark...")
  start = Date.now()
  for (let i = 0; i < iterations; i++) {
    coll.updateOne(
      { counter: i },
      { $set: { updated: true } }
    )
  }
  results.update = Date.now() - start
  
  // Aggregation benchmark
  print("Running AGGREGATION benchmark...")
  start = Date.now()
  for (let i = 0; i < 100; i++) {  // Fewer iterations for aggregation
    coll.aggregate([
      { $match: { status: "active" } },
      { $group: { _id: "$status", count: { $sum: 1 } } }
    ]).toArray()
  }
  results.aggregation = Date.now() - start
  
  // Results
  print("\n┌─ BENCHMARK RESULTS ────────────────────────────────────────┐")
  print(`│  INSERT (${iterations}): ${results.insert}ms (${(iterations / results.insert * 1000).toFixed(0)} ops/sec)`.padEnd(60) + "│")
  print(`│  FIND by _id (${iterations}): ${results.findById}ms (${(iterations / results.findById * 1000).toFixed(0)} ops/sec)`.padEnd(60) + "│")
  print(`│  FIND by index (${iterations}): ${results.findByIndex}ms (${(iterations / results.findByIndex * 1000).toFixed(0)} ops/sec)`.padEnd(60) + "│")
  print(`│  UPDATE (${iterations}): ${results.update}ms (${(iterations / results.update * 1000).toFixed(0)} ops/sec)`.padEnd(60) + "│")
  print(`│  AGGREGATION (100): ${results.aggregation}ms (${(100 / results.aggregation * 1000).toFixed(0)} ops/sec)`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  // Cleanup
  coll.drop()
  
  return results
}

// Usage
// runBenchmark({ iterations: 1000, documentSize: 'small' })
```

### Exercise 5: Performance Tuning Checklist

```javascript
// Generate performance tuning checklist

function performanceTuningChecklist() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         PERFORMANCE TUNING CHECKLIST                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const serverStatus = db.serverStatus()
  const checks = []
  
  // Check 1: Cache utilization
  if (serverStatus.wiredTiger) {
    const cache = serverStatus.wiredTiger.cache
    const used = cache["bytes currently in the cache"]
    const max = cache["maximum bytes configured"]
    const pct = (used / max * 100).toFixed(1)
    
    checks.push({
      category: "Memory",
      item: "WiredTiger cache utilization",
      value: `${pct}%`,
      status: parseFloat(pct) < 95 ? "✓" : "⚠",
      recommendation: parseFloat(pct) >= 95 ? "Consider increasing cache size" : null
    })
  }
  
  // Check 2: Connection utilization
  const conn = serverStatus.connections
  const connPct = (conn.current / (conn.current + conn.available) * 100).toFixed(1)
  
  checks.push({
    category: "Connections",
    item: "Connection utilization",
    value: `${connPct}%`,
    status: parseFloat(connPct) < 80 ? "✓" : "⚠",
    recommendation: parseFloat(connPct) >= 80 ? "Review connection pooling" : null
  })
  
  // Check 3: Page faults
  const pageFaults = serverStatus.extra_info?.page_faults || 0
  checks.push({
    category: "Memory",
    item: "Page faults",
    value: pageFaults.toString(),
    status: pageFaults < 100 ? "✓" : "⚠",
    recommendation: pageFaults >= 100 ? "Working set may exceed RAM" : null
  })
  
  // Check 4: Ticket availability
  if (serverStatus.wiredTiger?.concurrentTransactions) {
    const read = serverStatus.wiredTiger.concurrentTransactions.read
    const write = serverStatus.wiredTiger.concurrentTransactions.write
    
    const readPct = ((read.totalTickets - read.available) / read.totalTickets * 100).toFixed(1)
    const writePct = ((write.totalTickets - write.available) / write.totalTickets * 100).toFixed(1)
    
    checks.push({
      category: "Concurrency",
      item: "Read ticket usage",
      value: `${readPct}%`,
      status: parseFloat(readPct) < 80 ? "✓" : "⚠",
      recommendation: parseFloat(readPct) >= 80 ? "Queries may be blocking" : null
    })
    
    checks.push({
      category: "Concurrency",
      item: "Write ticket usage",
      value: `${writePct}%`,
      status: parseFloat(writePct) < 80 ? "✓" : "⚠",
      recommendation: parseFloat(writePct) >= 80 ? "Writes may be blocking" : null
    })
  }
  
  // Check 5: Profiling enabled
  const profStatus = db.getProfilingStatus()
  checks.push({
    category: "Diagnostics",
    item: "Query profiling",
    value: profStatus.was > 0 ? "Enabled" : "Disabled",
    status: profStatus.was > 0 ? "✓" : "!",
    recommendation: profStatus.was === 0 ? "Enable for slow query detection" : null
  })
  
  // Print checklist
  let currentCategory = ""
  
  checks.forEach(check => {
    if (check.category !== currentCategory) {
      currentCategory = check.category
      print(`\n┌─ ${currentCategory.toUpperCase()} ${"─".repeat(55 - currentCategory.length)}┐`)
    }
    
    print(`│  ${check.status} ${check.item}: ${check.value}`.padEnd(60) + "│")
    
    if (check.recommendation) {
      print(`│    → ${check.recommendation}`.padEnd(60) + "│")
    }
  })
  
  print("└────────────────────────────────────────────────────────────┘")
  
  // Summary
  const issues = checks.filter(c => c.status === "⚠").length
  const warnings = checks.filter(c => c.status === "!").length
  
  print(`\nSummary: ${checks.length - issues - warnings} OK, ${warnings} warnings, ${issues} issues`)
}

performanceTuningChecklist()
```

---

[← Previous: Monitoring](56-monitoring.md) | [Next: Memory Management →](58-memory-management.md)
