# Chapter 29: Aggregation Performance

## Table of Contents
- [Understanding Aggregation Performance](#understanding-aggregation-performance)
- [Pipeline Optimization Rules](#pipeline-optimization-rules)
- [Using Indexes in Aggregation](#using-indexes-in-aggregation)
- [Explain for Aggregation](#explain-for-aggregation)
- [Memory Considerations](#memory-considerations)
- [Pipeline Stage Performance](#pipeline-stage-performance)
- [Optimization Strategies](#optimization-strategies)
- [Monitoring and Profiling](#monitoring-and-profiling)
- [Summary](#summary)

---

## Understanding Aggregation Performance

Aggregation pipeline performance depends on efficient stage ordering, proper index usage, and memory management.

### Performance Factors

```
┌─────────────────────────────────────────────────────────────────────┐
│                Aggregation Performance Factors                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Index Usage                                                    │
│     ├── $match can use indexes                                     │
│     ├── $sort can use indexes                                      │
│     └── $geoNear requires geospatial index                        │
│                                                                     │
│  2. Pipeline Order                                                 │
│     ├── Filter early ($match)                                      │
│     ├── Reduce documents before expensive operations               │
│     └── Project only needed fields                                 │
│                                                                     │
│  3. Memory Limits                                                  │
│     ├── 100MB per pipeline stage                                   │
│     ├── allowDiskUse for larger operations                         │
│     └── 16MB document limit for output                             │
│                                                                     │
│  4. Stage Complexity                                               │
│     ├── $lookup can be expensive                                   │
│     ├── $unwind multiplies documents                               │
│     └── $group memory depends on cardinality                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Create sample data for testing
db.orders.drop()

// Insert 10,000 orders for performance testing
const customers = ["customer1", "customer2", "customer3", "customer4", "customer5"]
const products = ["Widget", "Gadget", "Gizmo", "Tool", "Device"]
const statuses = ["pending", "completed", "shipped", "cancelled"]
const regions = ["East", "West", "North", "South"]

const orders = []
for (let i = 0; i < 10000; i++) {
  orders.push({
    orderId: i + 1,
    customer: customers[Math.floor(Math.random() * customers.length)],
    product: products[Math.floor(Math.random() * products.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    region: regions[Math.floor(Math.random() * regions.length)],
    quantity: Math.floor(Math.random() * 100) + 1,
    price: Math.floor(Math.random() * 1000) + 10,
    date: new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1)
  })
}
db.orders.insertMany(orders)
```

---

## Pipeline Optimization Rules

### Automatic Optimizations

MongoDB automatically applies several pipeline optimizations:

```javascript
// MongoDB combines adjacent $match stages
// Original:
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $match: { region: "East" } }
])

// Optimized internally to:
// { $match: { status: "completed", region: "East" } }
```

### $match Movement

```javascript
// MongoDB moves $match before $project when possible
// Original:
db.orders.aggregate([
  { $project: { status: 1, total: { $multiply: ["$quantity", "$price"] } } },
  { $match: { status: "completed" } }
])

// Optimized internally: $match { status } moved before $project
```

### $sort + $limit Coalescing

```javascript
// MongoDB optimizes $sort + $limit
// Original:
db.orders.aggregate([
  { $sort: { price: -1 } },
  { $limit: 10 }
])

// Internally optimized to a top-k sort (only tracks top 10)
```

### $skip + $limit Coalescing

```javascript
// $skip and $limit are combined
// Original:
db.orders.aggregate([
  { $sort: { date: -1 } },
  { $skip: 100 },
  { $limit: 10 }
])

// Optimized: only processes skip + limit documents
```

---

## Using Indexes in Aggregation

### Indexable Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Stages That Can Use Indexes                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $match (at pipeline start)                                        │
│  ├── Uses indexes for query predicates                             │
│  └── Must be first stage (or after $geoNear)                       │
│                                                                     │
│  $sort (at pipeline start)                                         │
│  ├── Uses indexes if immediately follows $match                    │
│  └── Or if first stage                                             │
│                                                                     │
│  $geoNear                                                          │
│  ├── Must be first stage                                           │
│  └── Requires geospatial index                                     │
│                                                                     │
│  $lookup                                                           │
│  └── Uses index on foreignField                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Index-Optimized Pipeline

```javascript
// Create appropriate indexes
db.orders.createIndex({ status: 1 })
db.orders.createIndex({ status: 1, date: -1 })
db.orders.createIndex({ region: 1, status: 1, price: -1 })

// ✓ Good: $match at start uses index
db.orders.aggregate([
  { $match: { status: "completed" } },  // Uses index
  { $sort: { date: -1 } },
  { $limit: 100 }
])

// ✓ Good: Compound index covers $match and $sort
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { date: -1 } },              // Covered by compound index
  { $limit: 100 }
])
```

### Non-Indexed Pipeline

```javascript
// ✗ Bad: $match after $project cannot use index
db.orders.aggregate([
  { $project: { status: 1, price: 1 } },
  { $match: { status: "completed" } }   // Cannot use index
])

// ✗ Bad: $sort after $group cannot use index
db.orders.aggregate([
  { $group: { _id: "$product", total: { $sum: "$price" } } },
  { $sort: { total: -1 } }              // In-memory sort
])
```

### Check Index Usage

```javascript
// Verify index usage with explain
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { date: -1 } },
  { $limit: 10 }
]).explain("executionStats")
```

---

## Explain for Aggregation

### Explain Modes

```javascript
// queryPlanner - default, shows query plan
db.orders.aggregate([
  { $match: { status: "completed" } }
]).explain()

// executionStats - includes execution statistics
db.orders.aggregate([
  { $match: { status: "completed" } }
]).explain("executionStats")

// allPlansExecution - shows all candidate plans
db.orders.aggregate([
  { $match: { status: "completed" } }
]).explain("allPlansExecution")
```

### Reading Explain Output

```javascript
const explain = db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$region", count: { $sum: 1 } } }
]).explain("executionStats")

// Key fields to examine:
// explain.stages[0].$cursor.queryPlanner.winningPlan
// explain.stages[0].$cursor.executionStats.executionTimeMillis
// explain.stages[0].$cursor.executionStats.totalDocsExamined
// explain.stages[0].$cursor.executionStats.totalKeysExamined
```

### Explain Analysis Example

```javascript
// Analyze pipeline performance
function analyzeAggregation(pipeline) {
  const explain = db.orders.aggregate(pipeline).explain("executionStats")
  
  // Extract key metrics
  const cursorStage = explain.stages.find(s => s.$cursor)
  
  if (cursorStage) {
    const stats = cursorStage.$cursor.executionStats
    const plan = cursorStage.$cursor.queryPlanner.winningPlan
    
    print("=== Pipeline Analysis ===")
    print("Execution Time:", stats.executionTimeMillis, "ms")
    print("Documents Examined:", stats.totalDocsExamined)
    print("Keys Examined:", stats.totalKeysExamined)
    print("Documents Returned:", stats.nReturned)
    print("Index Used:", plan.inputStage?.indexName || "COLLSCAN")
    
    // Efficiency ratio
    if (stats.totalDocsExamined > 0) {
      const efficiency = (stats.nReturned / stats.totalDocsExamined * 100).toFixed(2)
      print("Efficiency:", efficiency + "%")
    }
  }
  
  return explain
}

// Test
analyzeAggregation([
  { $match: { status: "completed" } },
  { $group: { _id: "$region", count: { $sum: 1 } } }
])
```

---

## Memory Considerations

### Stage Memory Limits

```javascript
// Default: 100MB per pipeline stage
// If exceeded without allowDiskUse: error

// Large $group may exceed memory
db.orders.aggregate([
  { $group: { _id: "$customer", orders: { $push: "$$ROOT" } } }
])
// Can fail with high cardinality or large documents
```

### allowDiskUse

```javascript
// Enable disk use for memory-intensive operations
db.orders.aggregate(
  [
    { $sort: { price: -1 } },  // Large sort
    { $group: { _id: "$region", orders: { $push: "$$ROOT" } } }  // Large group
  ],
  { allowDiskUse: true }
)
```

### Memory-Efficient Alternatives

```javascript
// ✗ Memory-intensive: pushing all documents
db.orders.aggregate([
  {
    $group: {
      _id: "$customer",
      allOrders: { $push: "$$ROOT" }  // Stores all documents in memory
    }
  }
])

// ✓ Memory-efficient: aggregate values
db.orders.aggregate([
  {
    $group: {
      _id: "$customer",
      orderCount: { $sum: 1 },
      totalValue: { $sum: { $multiply: ["$quantity", "$price"] } },
      avgOrderValue: { $avg: { $multiply: ["$quantity", "$price"] } }
    }
  }
])
```

### Reducing Memory Usage

```javascript
// 1. Project early to reduce document size
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $project: { customer: 1, price: 1, quantity: 1 } },  // Reduce size
  { $group: { _id: "$customer", total: { $sum: { $multiply: ["$price", "$quantity"] } } } }
])

// 2. Use $limit before expensive operations
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { date: -1 } },
  { $limit: 1000 },  // Limit before group
  { $group: { _id: "$region", count: { $sum: 1 } } }
])

// 3. Avoid $push with large datasets
// Instead of collecting all, use separate queries
```

---

## Pipeline Stage Performance

### Stage Performance Comparison

| Stage | Relative Cost | Index Usage | Memory Impact |
|-------|---------------|-------------|---------------|
| `$match` | Low | Yes (at start) | Low |
| `$project` | Low | No | Low |
| `$addFields` | Low | No | Medium |
| `$sort` | Medium-High | Yes (at start) | High |
| `$limit` | Low | Combined with sort | Low |
| `$skip` | Low | Combined with sort | Low |
| `$group` | Medium-High | No | High |
| `$unwind` | Medium | No | Medium |
| `$lookup` | High | Yes (foreignField) | High |
| `$facet` | High | Per sub-pipeline | Very High |

### Expensive Stage Patterns

```javascript
// ✗ Expensive: $unwind creating many documents
db.orders.aggregate([
  { $unwind: "$items" },  // If items is large array, document explosion
  { $group: { _id: "$product", count: { $sum: 1 } } }
])

// ✓ Better: Use array operators when possible
db.orders.aggregate([
  {
    $project: {
      product: 1,
      itemCount: { $size: "$items" }
    }
  }
])
```

### $lookup Performance

```javascript
// Create index on foreign field
db.products.createIndex({ productId: 1 })

// ✓ Good: Index on foreign field
db.orders.aggregate([
  { $match: { status: "completed" } },  // Filter first
  { $limit: 100 },                       // Limit lookups
  {
    $lookup: {
      from: "products",
      localField: "product",
      foreignField: "productId",        // Indexed field
      as: "productDetails"
    }
  }
])

// ✓ Better: Use pipeline lookup with filtering
db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $lookup: {
      from: "products",
      let: { productName: "$product" },
      pipeline: [
        { $match: { $expr: { $eq: ["$productId", "$$productName"] } } },
        { $project: { name: 1, price: 1 } }  // Only needed fields
      ],
      as: "productDetails"
    }
  }
])
```

---

## Optimization Strategies

### Strategy 1: Filter Early

```javascript
// ✓ Optimal: Filter → Sort → Limit → Project
db.orders.aggregate([
  { $match: { status: "completed", region: "East" } },
  { $sort: { date: -1 } },
  { $limit: 100 },
  { $project: { customer: 1, product: 1, total: { $multiply: ["$quantity", "$price"] } } }
])

// ✗ Suboptimal: Project → Filter (loses index)
db.orders.aggregate([
  { $project: { status: 1, region: 1, total: { $multiply: ["$quantity", "$price"] } } },
  { $match: { status: "completed", region: "East" } },
  { $sort: { total: -1 } },
  { $limit: 100 }
])
```

### Strategy 2: Limit Before Expensive Operations

```javascript
// ✓ Good: Limit before $lookup
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { date: -1 } },
  { $limit: 100 },  // Limit BEFORE lookup
  { $lookup: { from: "customers", localField: "customer", foreignField: "_id", as: "customerInfo" } }
])

// ✗ Bad: $lookup on all documents
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $lookup: { from: "customers", localField: "customer", foreignField: "_id", as: "customerInfo" } },
  { $sort: { date: -1 } },
  { $limit: 100 }
])
```

### Strategy 3: Use Covered Queries

```javascript
// Create covering index
db.orders.createIndex({ status: 1, region: 1, quantity: 1, price: 1 })

// Covered query - only uses index
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $project: { _id: 0, region: 1, quantity: 1, price: 1 } }  // All fields in index
])
```

### Strategy 4: Avoid Unnecessary Stages

```javascript
// ✗ Unnecessary stages
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $project: { customer: 1, product: 1, price: 1 } },
  { $match: { price: { $gt: 100 } } },  // Could be combined
  { $project: { customer: 1, product: 1 } }  // Redundant project
])

// ✓ Simplified
db.orders.aggregate([
  { $match: { status: "completed", price: { $gt: 100 } } },
  { $project: { customer: 1, product: 1 } }
])
```

### Strategy 5: Optimize $group

```javascript
// ✗ High cardinality grouping
db.orders.aggregate([
  {
    $group: {
      _id: { customer: "$customer", product: "$product", date: "$date" },
      // Many unique combinations = high memory
    }
  }
])

// ✓ Reduce cardinality with date truncation
db.orders.aggregate([
  {
    $group: {
      _id: {
        customer: "$customer",
        product: "$product",
        month: { $dateToString: { format: "%Y-%m", date: "$date" } }
      },
      total: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  }
])
```

---

## Monitoring and Profiling

### Enable Profiling

```javascript
// Enable profiling for slow operations (> 100ms)
db.setProfilingLevel(1, { slowms: 100 })

// Profile all operations
db.setProfilingLevel(2)

// Check current level
db.getProfilingStatus()

// View profile data
db.system.profile.find().sort({ ts: -1 }).limit(10)
```

### Find Slow Aggregations

```javascript
// Find slow aggregation operations
db.system.profile.find({
  op: "command",
  "command.aggregate": { $exists: true },
  millis: { $gt: 100 }
}).sort({ millis: -1 }).limit(10)
```

### Aggregation Metrics

```javascript
// Get server status for aggregation metrics
db.serverStatus().metrics.aggStageCounters
// Shows count of each stage type executed

// Current operations
db.currentOp({
  "command.aggregate": { $exists: true }
})
```

### Performance Benchmarking

```javascript
// Benchmark pipeline performance
function benchmarkPipeline(pipeline, iterations = 10) {
  const times = []
  
  for (let i = 0; i < iterations; i++) {
    const start = new Date()
    db.orders.aggregate(pipeline).toArray()
    const elapsed = new Date() - start
    times.push(elapsed)
  }
  
  const avg = times.reduce((a, b) => a + b, 0) / times.length
  const min = Math.min(...times)
  const max = Math.max(...times)
  
  print("=== Benchmark Results ===")
  print("Iterations:", iterations)
  print("Average:", avg.toFixed(2), "ms")
  print("Min:", min, "ms")
  print("Max:", max, "ms")
  
  return { avg, min, max, times }
}

// Test
benchmarkPipeline([
  { $match: { status: "completed" } },
  { $group: { _id: "$region", total: { $sum: 1 } } }
])
```

---

## Summary

### Optimization Checklist

| Item | Action |
|------|--------|
| **$match position** | Place at start of pipeline |
| **Index coverage** | Create indexes for $match/$sort |
| **$limit placement** | Before expensive operations |
| **$project timing** | Early to reduce document size |
| **$lookup optimization** | Index foreign field, limit before lookup |
| **Memory usage** | Use allowDiskUse for large operations |
| **Stage count** | Minimize unnecessary stages |

### Performance Rules

| Rule | Description |
|------|-------------|
| **Filter early** | $match as first stage |
| **Sort efficiently** | Use indexes, combine with $limit |
| **Limit before lookup** | Reduce join operations |
| **Project minimally** | Only include needed fields |
| **Group smartly** | Reduce cardinality |
| **Monitor performance** | Use explain and profiling |

### What's Next?

In the next chapter, we'll explore Output Operations including $out and $merge.

---

## Practice Questions

1. Which stages can use indexes?
2. What's the default memory limit per pipeline stage?
3. How does MongoDB optimize $sort + $limit?
4. When should you use allowDiskUse?
5. What makes $lookup expensive?
6. How do you verify index usage in aggregation?
7. What's a covered query in aggregation?
8. How do you profile slow aggregations?

---

## Hands-On Exercises

### Exercise 1: Index Optimization

```javascript
// Create indexes
db.orders.createIndex({ status: 1 })
db.orders.createIndex({ status: 1, date: -1 })
db.orders.createIndex({ region: 1, status: 1 })

// Compare with and without index
function compareWithIndex(withIndex, withoutIndex) {
  print("=== With Index ===")
  const explain1 = db.orders.aggregate(withIndex).explain("executionStats")
  const cursor1 = explain1.stages.find(s => s.$cursor)
  if (cursor1) {
    print("Execution time:", cursor1.$cursor.executionStats.executionTimeMillis, "ms")
    print("Docs examined:", cursor1.$cursor.executionStats.totalDocsExamined)
    print("Index:", cursor1.$cursor.queryPlanner.winningPlan.inputStage?.indexName || "COLLSCAN")
  }
  
  print("\n=== Without Index ===")
  const explain2 = db.orders.aggregate(withoutIndex).explain("executionStats")
  const cursor2 = explain2.stages.find(s => s.$cursor)
  if (cursor2) {
    print("Execution time:", cursor2.$cursor.executionStats.executionTimeMillis, "ms")
    print("Docs examined:", cursor2.$cursor.executionStats.totalDocsExamined)
    print("Index:", cursor2.$cursor.queryPlanner.winningPlan.inputStage?.indexName || "COLLSCAN")
  }
}

// Test 1: $match optimization
compareWithIndex(
  // With index
  [
    { $match: { status: "completed" } },
    { $group: { _id: "$region", count: { $sum: 1 } } }
  ],
  // Without index (forces collection scan by adding unindexed field)
  [
    { $match: { status: "completed", nonExistentField: { $exists: false } } },
    { $group: { _id: "$region", count: { $sum: 1 } } }
  ]
)
```

### Exercise 2: Pipeline Optimization

```javascript
// Optimize this pipeline

// Original (suboptimal)
const suboptimal = [
  { $project: { customer: 1, status: 1, total: { $multiply: ["$quantity", "$price"] } } },
  { $match: { status: "completed" } },
  { $sort: { total: -1 } },
  { $group: { _id: "$customer", maxOrder: { $max: "$total" } } },
  { $sort: { maxOrder: -1 } },
  { $limit: 10 }
]

// Optimized version
const optimized = [
  { $match: { status: "completed" } },  // Filter FIRST (uses index)
  { $sort: { customer: 1 } },            // Sort for grouping efficiency
  {
    $group: {
      _id: "$customer",
      maxOrder: { $max: { $multiply: ["$quantity", "$price"] } }
    }
  },
  { $sort: { maxOrder: -1 } },
  { $limit: 10 }
]

// Compare
print("=== Suboptimal ===")
const start1 = new Date()
db.orders.aggregate(suboptimal).toArray()
print("Time:", new Date() - start1, "ms")

print("\n=== Optimized ===")
const start2 = new Date()
db.orders.aggregate(optimized).toArray()
print("Time:", new Date() - start2, "ms")
```

### Exercise 3: Memory-Efficient Aggregation

```javascript
// Compare memory-intensive vs memory-efficient

// Memory-intensive (collects all documents)
print("=== Memory Intensive ===")
try {
  const result1 = db.orders.aggregate([
    { $match: { status: "completed" } },
    {
      $group: {
        _id: "$customer",
        orders: { $push: "$$ROOT" }  // Stores all documents
      }
    }
  ]).toArray()
  print("Success, groups:", result1.length)
} catch (e) {
  print("Error:", e.message)
}

// Memory-efficient (aggregates values)
print("\n=== Memory Efficient ===")
const result2 = db.orders.aggregate([
  { $match: { status: "completed" } },
  {
    $group: {
      _id: "$customer",
      orderCount: { $sum: 1 },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      avgOrderValue: { $avg: { $multiply: ["$quantity", "$price"] } },
      lastOrder: { $max: "$date" }
    }
  }
]).toArray()
print("Success, groups:", result2.length)
```

### Exercise 4: Profiling Aggregations

```javascript
// Set up profiling
db.setProfilingLevel(1, { slowms: 0 })  // Profile all for testing

// Run some aggregations
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $group: { _id: "$region", count: { $sum: 1 } } }
]).toArray()

db.orders.aggregate([
  { $sort: { date: -1 } },
  { $limit: 100 }
]).toArray()

db.orders.aggregate([
  { $match: { region: "East" } },
  { $group: { _id: "$customer", total: { $sum: { $multiply: ["$quantity", "$price"] } } } },
  { $sort: { total: -1 } }
]).toArray()

// Analyze profile data
print("=== Recent Aggregations ===")
db.system.profile.find({
  "command.aggregate": "orders"
}).sort({ ts: -1 }).limit(5).forEach(doc => {
  print("\nTime:", doc.millis, "ms")
  print("Pipeline stages:", doc.command.pipeline?.length || 0)
  if (doc.command.pipeline) {
    doc.command.pipeline.forEach((stage, i) => {
      print("  Stage", i + 1, ":", Object.keys(stage)[0])
    })
  }
})

// Reset profiling
db.setProfilingLevel(0)
```

### Exercise 5: Benchmark Comparisons

```javascript
// Comprehensive benchmark

function fullBenchmark() {
  const pipelines = {
    "Simple match + group": [
      { $match: { status: "completed" } },
      { $group: { _id: "$region", count: { $sum: 1 } } }
    ],
    
    "Match + sort + limit": [
      { $match: { status: "completed" } },
      { $sort: { date: -1 } },
      { $limit: 100 }
    ],
    
    "Complex grouping": [
      { $match: { status: "completed" } },
      {
        $group: {
          _id: { customer: "$customer", region: "$region" },
          total: { $sum: { $multiply: ["$quantity", "$price"] } },
          count: { $sum: 1 },
          avgPrice: { $avg: "$price" }
        }
      },
      { $sort: { total: -1 } }
    ],
    
    "Faceted analysis": [
      { $match: { status: "completed" } },
      {
        $facet: {
          "byRegion": [
            { $group: { _id: "$region", count: { $sum: 1 } } }
          ],
          "byProduct": [
            { $group: { _id: "$product", count: { $sum: 1 } } }
          ],
          "stats": [
            {
              $group: {
                _id: null,
                total: { $sum: { $multiply: ["$quantity", "$price"] } },
                avg: { $avg: { $multiply: ["$quantity", "$price"] } }
              }
            }
          ]
        }
      }
    ]
  }
  
  const results = {}
  
  for (const [name, pipeline] of Object.entries(pipelines)) {
    const times = []
    for (let i = 0; i < 5; i++) {
      const start = new Date()
      db.orders.aggregate(pipeline).toArray()
      times.push(new Date() - start)
    }
    results[name] = {
      avg: (times.reduce((a, b) => a + b, 0) / times.length).toFixed(2),
      min: Math.min(...times),
      max: Math.max(...times)
    }
  }
  
  print("=== Benchmark Results ===")
  for (const [name, stats] of Object.entries(results)) {
    print(`\n${name}:`)
    print(`  Avg: ${stats.avg}ms, Min: ${stats.min}ms, Max: ${stats.max}ms`)
  }
  
  return results
}

fullBenchmark()
```

---

[← Previous: Window Functions](28-window-functions.md) | [Next: Output Operations →](30-output-operations.md)
