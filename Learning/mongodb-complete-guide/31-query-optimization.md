# Chapter 31: Query Optimization

## Table of Contents
- [Understanding Query Optimization](#understanding-query-optimization)
- [Query Execution Plans](#query-execution-plans)
- [Explain Fundamentals](#explain-fundamentals)
- [Reading Explain Output](#reading-explain-output)
- [Query Patterns and Performance](#query-patterns-and-performance)
- [Index Selection](#index-selection)
- [Query Planner Cache](#query-planner-cache)
- [Optimization Techniques](#optimization-techniques)
- [Summary](#summary)

---

## Understanding Query Optimization

Query optimization is the process of selecting the most efficient execution plan for a query. MongoDB's query planner evaluates available indexes and chooses the best strategy.

### Query Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Query Execution Lifecycle                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Parse Query                                                    │
│     └── Parse query document and options                           │
│                                                                     │
│  2. Plan Generation                                                │
│     └── Generate candidate execution plans                         │
│                                                                     │
│  3. Plan Selection                                                 │
│     ├── Run trial execution for each plan                          │
│     └── Select plan that returns results fastest                   │
│                                                                     │
│  4. Plan Execution                                                 │
│     └── Execute selected plan                                      │
│                                                                     │
│  5. Result Return                                                  │
│     └── Return documents to client                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Create test collection with indexes
db.users.drop()

// Insert sample data
const users = []
const cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]
const statuses = ["active", "inactive", "pending"]

for (let i = 0; i < 10000; i++) {
  users.push({
    userId: i + 1,
    name: `User ${i + 1}`,
    email: `user${i + 1}@example.com`,
    age: Math.floor(Math.random() * 60) + 18,
    city: cities[Math.floor(Math.random() * cities.length)],
    status: statuses[Math.floor(Math.random() * statuses.length)],
    score: Math.floor(Math.random() * 1000),
    createdAt: new Date(Date.now() - Math.random() * 365 * 24 * 60 * 60 * 1000),
    tags: ["user", i % 2 === 0 ? "premium" : "standard"]
  })
}
db.users.insertMany(users)

// Create indexes
db.users.createIndex({ email: 1 }, { unique: true })
db.users.createIndex({ status: 1 })
db.users.createIndex({ city: 1 })
db.users.createIndex({ age: 1 })
db.users.createIndex({ status: 1, city: 1 })
db.users.createIndex({ status: 1, age: 1 })
db.users.createIndex({ city: 1, status: 1, age: 1 })
```

---

## Query Execution Plans

### Plan Types

| Plan Type | Description | Performance |
|-----------|-------------|-------------|
| **COLLSCAN** | Full collection scan | Slowest |
| **IXSCAN** | Index scan | Fast |
| **FETCH** | Retrieve full document | Adds overhead |
| **SORT** | In-memory sort | Memory intensive |
| **LIMIT** | Limit results | Optimization |
| **PROJECTION_COVERED** | Index-only query | Fastest |

### Plan Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Query Plan Structure                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Query: { status: "active", city: "Chicago", age: { $gt: 30 } }    │
│                                                                     │
│  Plan Tree:                                                        │
│  ┌──────────┐                                                      │
│  │  LIMIT   │  ← Limit results                                     │
│  └────┬─────┘                                                      │
│       │                                                            │
│  ┌────▼─────┐                                                      │
│  │  FETCH   │  ← Fetch full documents                              │
│  └────┬─────┘                                                      │
│       │                                                            │
│  ┌────▼─────┐                                                      │
│  │  IXSCAN  │  ← Scan index { city: 1, status: 1, age: 1 }        │
│  └──────────┘                                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Explain Fundamentals

### Explain Verbosity Modes

```javascript
// queryPlanner - shows winning plan only
db.users.find({ status: "active" }).explain()
db.users.find({ status: "active" }).explain("queryPlanner")

// executionStats - includes execution statistics
db.users.find({ status: "active" }).explain("executionStats")

// allPlansExecution - shows all candidate plans
db.users.find({ status: "active" }).explain("allPlansExecution")
```

### Basic Explain Usage

```javascript
// Explain a find query
db.users.find({ status: "active", city: "Chicago" }).explain("executionStats")

// Explain with sort and limit
db.users.find({ status: "active" })
  .sort({ age: -1 })
  .limit(10)
  .explain("executionStats")

// Explain count
db.users.countDocuments({ status: "active" }, { explain: true })

// Explain aggregate
db.users.aggregate([
  { $match: { status: "active" } },
  { $group: { _id: "$city", count: { $sum: 1 } } }
]).explain("executionStats")
```

---

## Reading Explain Output

### Key Fields in Explain Output

```javascript
const explain = db.users.find({ status: "active", city: "Chicago" }).explain("executionStats")

// Key sections:
// 1. queryPlanner - plan selection info
// 2. winningPlan - chosen execution plan
// 3. executionStats - actual execution metrics

// Important metrics:
print("=== Query Execution Analysis ===")
print("nReturned:", explain.executionStats.nReturned)
print("executionTimeMillis:", explain.executionStats.executionTimeMillis)
print("totalKeysExamined:", explain.executionStats.totalKeysExamined)
print("totalDocsExamined:", explain.executionStats.totalDocsExamined)
```

### Understanding the Winning Plan

```javascript
const explain = db.users.find({ status: "active" }).explain("executionStats")

// Navigate winning plan
const winningPlan = explain.queryPlanner.winningPlan

print("=== Winning Plan ===")
print("Stage:", winningPlan.stage)

if (winningPlan.inputStage) {
  print("Input Stage:", winningPlan.inputStage.stage)
  if (winningPlan.inputStage.indexName) {
    print("Index Used:", winningPlan.inputStage.indexName)
  }
}
```

### Execution Statistics Analysis

```javascript
function analyzeQuery(query, options = {}) {
  const cursor = db.users.find(query)
  if (options.sort) cursor.sort(options.sort)
  if (options.limit) cursor.limit(options.limit)
  
  const explain = cursor.explain("executionStats")
  const stats = explain.executionStats
  const plan = explain.queryPlanner.winningPlan
  
  print("=== Query Analysis ===")
  print("Query:", JSON.stringify(query))
  
  // Execution metrics
  print("\n--- Execution Metrics ---")
  print("Documents Returned:", stats.nReturned)
  print("Execution Time:", stats.executionTimeMillis, "ms")
  print("Keys Examined:", stats.totalKeysExamined)
  print("Documents Examined:", stats.totalDocsExamined)
  
  // Efficiency
  print("\n--- Efficiency ---")
  const docsRatio = stats.totalDocsExamined > 0 
    ? (stats.nReturned / stats.totalDocsExamined * 100).toFixed(2) 
    : 100
  print("Docs Efficiency:", docsRatio + "%")
  
  const keysRatio = stats.totalKeysExamined > 0
    ? (stats.nReturned / stats.totalKeysExamined * 100).toFixed(2)
    : 100
  print("Keys Efficiency:", keysRatio + "%")
  
  // Plan info
  print("\n--- Plan Info ---")
  print("Plan Type:", plan.stage)
  
  // Check for COLLSCAN
  function hasCollscan(stage) {
    if (stage.stage === "COLLSCAN") return true
    if (stage.inputStage) return hasCollscan(stage.inputStage)
    if (stage.inputStages) return stage.inputStages.some(hasCollscan)
    return false
  }
  
  if (hasCollscan(plan)) {
    print("⚠️  WARNING: Collection scan detected!")
  }
  
  // Index usage
  function getIndexName(stage) {
    if (stage.indexName) return stage.indexName
    if (stage.inputStage) return getIndexName(stage.inputStage)
    return null
  }
  
  const indexUsed = getIndexName(plan)
  print("Index Used:", indexUsed || "None")
  
  return explain
}

// Test various queries
analyzeQuery({ status: "active" })
analyzeQuery({ status: "active", city: "Chicago" })
analyzeQuery({ age: { $gt: 30 } })
analyzeQuery({ name: /^User 1/ })  // No index on name
```

---

## Query Patterns and Performance

### Equality vs Range Queries

```javascript
// Equality - more selective
analyzeQuery({ status: "active" })  // Uses index efficiently

// Range - less selective
analyzeQuery({ age: { $gt: 30 } })  // May examine more documents

// Combined
analyzeQuery({ status: "active", age: { $gt: 30 } })
```

### Compound Index Usage

```javascript
// Index: { status: 1, city: 1 }

// ✓ Uses both fields - efficient
analyzeQuery({ status: "active", city: "Chicago" })

// ✓ Uses prefix - efficient
analyzeQuery({ status: "active" })

// ⚠️ Can only use index partially
analyzeQuery({ city: "Chicago" })  // status prefix not used
```

### Index Prefix Rule

```javascript
// Index: { city: 1, status: 1, age: 1 }

// ✓ Full prefix match
analyzeQuery({ city: "Chicago", status: "active", age: 30 })

// ✓ Prefix matches
analyzeQuery({ city: "Chicago", status: "active" })
analyzeQuery({ city: "Chicago" })

// ⚠️ Skips prefix - cannot use index
analyzeQuery({ status: "active" })          // Skips city
analyzeQuery({ age: 30 })                   // Skips city, status
analyzeQuery({ status: "active", age: 30 }) // Skips city
```

### Sort Optimization

```javascript
// Create index for sort
db.users.createIndex({ score: -1 })

// ✓ Sort uses index - no in-memory sort
db.users.find({}).sort({ score: -1 }).limit(10).explain("executionStats")
// Check for SORT stage - should not appear

// ⚠️ Sort doesn't match index direction
db.users.find({}).sort({ score: 1 }).limit(10).explain("executionStats")
// May need in-memory sort

// ✓ Compound index covers sort
// Index: { status: 1, age: 1 }
db.users.find({ status: "active" }).sort({ age: 1 }).explain("executionStats")
```

---

## Index Selection

### How MongoDB Chooses Indexes

```javascript
// Multiple indexes available
db.users.getIndexes().forEach(idx => print(idx.name + ":", JSON.stringify(idx.key)))

// MongoDB evaluates candidate indexes
const explain = db.users.find({ status: "active", city: "Chicago" })
  .explain("allPlansExecution")

// View rejected plans
if (explain.queryPlanner.rejectedPlans.length > 0) {
  print("\n=== Rejected Plans ===")
  explain.queryPlanner.rejectedPlans.forEach((plan, i) => {
    print(`Plan ${i + 1}:`, JSON.stringify(plan))
  })
}
```

### Forcing Index Hints

```javascript
// Let MongoDB choose (usually best)
db.users.find({ status: "active", city: "Chicago" }).explain("executionStats")

// Force specific index
db.users.find({ status: "active", city: "Chicago" })
  .hint({ status: 1 })
  .explain("executionStats")

// Force collection scan (for testing)
db.users.find({ status: "active" })
  .hint({ $natural: 1 })
  .explain("executionStats")

// Compare index performance
function compareIndexes(query) {
  const indexes = db.users.getIndexes()
    .filter(idx => idx.name !== "_id_")
    .map(idx => idx.name)
  
  print("=== Index Comparison for:", JSON.stringify(query), "===\n")
  
  // No hint (MongoDB's choice)
  const noHint = db.users.find(query).explain("executionStats")
  print("MongoDB Choice:")
  print("  Index:", noHint.queryPlanner.winningPlan.inputStage?.indexName || "COLLSCAN")
  print("  Time:", noHint.executionStats.executionTimeMillis, "ms")
  print("  Docs Examined:", noHint.executionStats.totalDocsExamined)
  
  // Try each index
  indexes.forEach(indexName => {
    try {
      const hinted = db.users.find(query).hint(indexName).explain("executionStats")
      print(`\n${indexName}:`)
      print("  Time:", hinted.executionStats.executionTimeMillis, "ms")
      print("  Docs Examined:", hinted.executionStats.totalDocsExamined)
    } catch (e) {
      print(`\n${indexName}: Not applicable`)
    }
  })
}

compareIndexes({ status: "active", city: "Chicago" })
```

---

## Query Planner Cache

### Understanding Plan Cache

```javascript
// View plan cache stats
db.users.getPlanCache().list()

// Clear plan cache
db.users.getPlanCache().clear()

// View specific cached plans
db.users.getPlanCache().list().forEach(entry => {
  print("Query Hash:", entry.queryHash)
  print("Plan Cache Key:", entry.planCacheKey)
  print("Is Active:", entry.isActive)
  if (entry.cachedPlan) {
    print("Cached Plan Stage:", entry.cachedPlan.stage)
  }
  print("---")
})
```

### Plan Cache Eviction

```javascript
// Plans are evicted when:
// 1. Index created/dropped
// 2. Collection dropped
// 3. Server restart
// 4. Manual clear
// 5. Plan becomes inefficient

// Force re-evaluation by clearing cache
db.users.getPlanCache().clear()

// Run query to cache new plan
db.users.find({ status: "active", city: "Chicago" }).explain()

// Check cache again
print("Cached plans:", db.users.getPlanCache().list().length)
```

---

## Optimization Techniques

### 1. Covered Queries

```javascript
// Create index that covers query
db.users.createIndex({ email: 1, name: 1, status: 1 })

// Query returns only indexed fields
const explain = db.users.find(
  { email: "user1@example.com" },
  { _id: 0, email: 1, name: 1, status: 1 }  // Only indexed fields
).explain("executionStats")

// Check for PROJECTION_COVERED or no FETCH stage
print("Stage:", explain.queryPlanner.winningPlan.stage)
// If no FETCH, it's a covered query
```

### 2. Projection Optimization

```javascript
// ✗ Fetching all fields
db.users.find({ status: "active" }).explain("executionStats")

// ✓ Project only needed fields
db.users.find(
  { status: "active" },
  { userId: 1, name: 1, email: 1 }
).explain("executionStats")
// Still needs FETCH, but transfers less data
```

### 3. Limit Early

```javascript
// ✓ Limit reduces work
db.users.find({ status: "active" }).limit(10).explain("executionStats")
// nReturned: 10, stops early

// ✗ Without limit
db.users.find({ status: "active" }).explain("executionStats")
// nReturned: all matching documents
```

### 4. Avoid Negation

```javascript
// ⚠️ $ne cannot use index efficiently
analyzeQuery({ status: { $ne: "inactive" } })

// ⚠️ $nin cannot use index efficiently
analyzeQuery({ status: { $nin: ["inactive", "pending"] } })

// ✓ Use $in instead when possible
analyzeQuery({ status: { $in: ["active"] } })
```

### 5. Avoid Regex with Leading Wildcards

```javascript
// ✓ Prefix regex can use index
analyzeQuery({ email: /^user1/ })

// ⚠️ Non-prefix regex requires scan
analyzeQuery({ email: /example.com$/ })
analyzeQuery({ email: /user/ })  // Contains
```

### 6. Optimize OR Queries

```javascript
// Create indexes for OR branches
db.users.createIndex({ status: 1 })
db.users.createIndex({ score: 1 })

// MongoDB can use index merge for $or
const explain = db.users.find({
  $or: [
    { status: "active" },
    { score: { $gt: 900 } }
  ]
}).explain("executionStats")

// Look for OR stage with IXSCAN children
printjson(explain.queryPlanner.winningPlan)
```

### 7. Use Appropriate Data Types

```javascript
// String comparison
db.users.find({ userId: "1" })  // String

// Numeric comparison (faster if field is numeric)
db.users.find({ userId: 1 })    // Number

// Ensure types match for index usage
```

---

## Summary

### Query Optimization Checklist

| Item | Action |
|------|--------|
| **Use explain** | Always analyze slow queries |
| **Check index usage** | Verify IXSCAN vs COLLSCAN |
| **Examine ratios** | nReturned vs totalDocsExamined |
| **Avoid SORT stage** | Create indexes for sort fields |
| **Use covered queries** | Project only indexed fields |
| **Limit results** | Reduce work with limit() |

### Explain Verbosity Comparison

| Mode | Use Case | Information |
|------|----------|-------------|
| `queryPlanner` | Plan overview | Winning plan only |
| `executionStats` | Performance analysis | Actual metrics |
| `allPlansExecution` | Index comparison | All candidate plans |

### Performance Indicators

| Indicator | Good | Bad |
|-----------|------|-----|
| **Stage** | IXSCAN | COLLSCAN |
| **nReturned/totalDocsExamined** | Close to 1 | Much less than 1 |
| **SORT stage** | Absent | Present |
| **Execution time** | Low | High |

### What's Next?

In the next chapter, we'll explore Array Query Operators in detail.

---

## Practice Questions

1. What are the three explain verbosity modes?
2. What does totalDocsExamined tell you?
3. Why is COLLSCAN usually bad?
4. How does the index prefix rule work?
5. What is a covered query?
6. Why should you avoid negation operators?
7. How does MongoDB choose between multiple indexes?
8. What causes plan cache eviction?

---

## Hands-On Exercises

### Exercise 1: Explain Analysis

```javascript
// Analyze these queries and explain the differences

// Query 1: Single field with index
const q1 = db.users.find({ status: "active" }).explain("executionStats")
print("Query 1 - Single indexed field:")
print("  Index:", q1.queryPlanner.winningPlan.inputStage?.indexName)
print("  Docs Examined:", q1.executionStats.totalDocsExamined)
print("  Time:", q1.executionStats.executionTimeMillis, "ms")

// Query 2: Compound query matching index
const q2 = db.users.find({ status: "active", city: "Chicago" }).explain("executionStats")
print("\nQuery 2 - Compound indexed fields:")
print("  Index:", q2.queryPlanner.winningPlan.inputStage?.indexName)
print("  Docs Examined:", q2.executionStats.totalDocsExamined)
print("  Time:", q2.executionStats.executionTimeMillis, "ms")

// Query 3: Field without index
const q3 = db.users.find({ name: "User 1" }).explain("executionStats")
print("\nQuery 3 - Non-indexed field:")
print("  Stage:", q3.queryPlanner.winningPlan.stage)
print("  Docs Examined:", q3.executionStats.totalDocsExamined)
print("  Time:", q3.executionStats.executionTimeMillis, "ms")

// Analysis: Which query is most efficient? Why?
```

### Exercise 2: Index Prefix Usage

```javascript
// Test index prefix rule with { city: 1, status: 1, age: 1 }

const testCases = [
  { city: "Chicago" },                           // Uses prefix
  { city: "Chicago", status: "active" },         // Uses prefix
  { city: "Chicago", status: "active", age: 30 },// Full index
  { status: "active" },                          // Skips city
  { age: 30 },                                   // Skips city, status
  { status: "active", age: 30 },                 // Skips city
  { city: "Chicago", age: 30 }                   // Skips status
]

print("=== Index Prefix Rule Test ===")
print("Index: { city: 1, status: 1, age: 1 }\n")

testCases.forEach((query, i) => {
  const explain = db.users.find(query).explain("executionStats")
  const plan = explain.queryPlanner.winningPlan
  
  // Find index stage
  function findIndex(stage) {
    if (stage.indexName) return stage.indexName
    if (stage.inputStage) return findIndex(stage.inputStage)
    return null
  }
  
  const indexUsed = findIndex(plan)
  const usesCompound = indexUsed === "city_1_status_1_age_1"
  
  print(`Test ${i + 1}: ${JSON.stringify(query)}`)
  print(`  Index: ${indexUsed || "COLLSCAN"}`)
  print(`  Uses compound: ${usesCompound ? "✓" : "✗"}`)
  print(`  Docs examined: ${explain.executionStats.totalDocsExamined}`)
  print("")
})
```

### Exercise 3: Covered Query

```javascript
// Create and test covered query

// Ensure index exists
db.users.createIndex({ status: 1, city: 1, score: 1 })

// Non-covered query (includes _id or non-indexed field)
const nonCovered = db.users.find(
  { status: "active", city: "Chicago" },
  { status: 1, city: 1, name: 1 }  // name not in index
).explain("executionStats")

// Covered query (only indexed fields, exclude _id)
const covered = db.users.find(
  { status: "active", city: "Chicago" },
  { _id: 0, status: 1, city: 1, score: 1 }
).explain("executionStats")

print("=== Covered Query Test ===\n")

print("Non-covered query:")
print("  Projection includes: status, city, name (name not indexed)")
print("  Has FETCH:", JSON.stringify(nonCovered.queryPlanner.winningPlan).includes("FETCH"))
print("")

print("Covered query:")
print("  Projection includes: status, city, score (all indexed)")
print("  Has FETCH:", JSON.stringify(covered.queryPlanner.winningPlan).includes("FETCH"))

// Note: Covered queries don't need FETCH stage
```

### Exercise 4: Sort Optimization

```javascript
// Test sort with and without index support

// Without index on sort field
db.users.dropIndex("createdAt_-1") // Remove if exists

const noIndexSort = db.users.find({ status: "active" })
  .sort({ createdAt: -1 })
  .limit(10)
  .explain("executionStats")

print("=== Sort Optimization ===\n")

print("Sort WITHOUT index:")
print("  Has SORT stage:", JSON.stringify(noIndexSort.queryPlanner.winningPlan).includes("SORT"))
print("  Time:", noIndexSort.executionStats.executionTimeMillis, "ms")

// Create index for sort
db.users.createIndex({ status: 1, createdAt: -1 })

const withIndexSort = db.users.find({ status: "active" })
  .sort({ createdAt: -1 })
  .limit(10)
  .explain("executionStats")

print("\nSort WITH index:")
print("  Has SORT stage:", JSON.stringify(withIndexSort.queryPlanner.winningPlan).includes("SORT"))
print("  Time:", withIndexSort.executionStats.executionTimeMillis, "ms")
print("  Index:", withIndexSort.queryPlanner.winningPlan.inputStage?.indexName)
```

### Exercise 5: Query Comparison Tool

```javascript
// Build a query comparison tool

function compareQueries(queries) {
  const results = []
  
  queries.forEach((queryDef, i) => {
    const { name, query, projection, sort, limit } = queryDef
    
    let cursor = db.users.find(query, projection || {})
    if (sort) cursor = cursor.sort(sort)
    if (limit) cursor = cursor.limit(limit)
    
    const explain = cursor.explain("executionStats")
    const stats = explain.executionStats
    const plan = explain.queryPlanner.winningPlan
    
    // Find scan type and index
    function getScanInfo(stage) {
      if (stage.stage === "COLLSCAN") return { type: "COLLSCAN", index: null }
      if (stage.stage === "IXSCAN") return { type: "IXSCAN", index: stage.indexName }
      if (stage.inputStage) return getScanInfo(stage.inputStage)
      return { type: stage.stage, index: null }
    }
    
    const scanInfo = getScanInfo(plan)
    
    results.push({
      name,
      scanType: scanInfo.type,
      index: scanInfo.index,
      nReturned: stats.nReturned,
      docsExamined: stats.totalDocsExamined,
      keysExamined: stats.totalKeysExamined,
      timeMs: stats.executionTimeMillis,
      efficiency: stats.totalDocsExamined > 0 
        ? (stats.nReturned / stats.totalDocsExamined * 100).toFixed(1) + "%"
        : "100%"
    })
  })
  
  // Display results
  print("=== Query Comparison Results ===\n")
  print("| Name | Scan | Index | Returned | Docs | Keys | Time | Efficiency |")
  print("|------|------|-------|----------|------|------|------|------------|")
  
  results.forEach(r => {
    print(`| ${r.name} | ${r.scanType} | ${r.index || 'N/A'} | ${r.nReturned} | ${r.docsExamined} | ${r.keysExamined} | ${r.timeMs}ms | ${r.efficiency} |`)
  })
  
  // Find winner
  const winner = results.reduce((best, curr) => 
    curr.timeMs < best.timeMs ? curr : best
  )
  print(`\nFastest: ${winner.name} (${winner.timeMs}ms)`)
  
  return results
}

// Compare different approaches
compareQueries([
  { 
    name: "Basic",
    query: { status: "active" }
  },
  {
    name: "Limited",
    query: { status: "active" },
    limit: 100
  },
  {
    name: "Projected",
    query: { status: "active" },
    projection: { userId: 1, name: 1 },
    limit: 100
  },
  {
    name: "Compound",
    query: { status: "active", city: "Chicago" },
    limit: 100
  },
  {
    name: "NoIndex",
    query: { name: /^User 1/ },
    limit: 100
  }
])
```

---

[← Previous: Output Operations](30-output-operations.md) | [Next: Array Query Operators →](32-array-query-operators.md)
