# Chapter 16: Index Fundamentals

## Table of Contents
- [Introduction to Indexes](#introduction-to-indexes)
- [How Indexes Work](#how-indexes-work)
- [Index Types Overview](#index-types-overview)
- [Default _id Index](#default-_id-index)
- [Creating Indexes](#creating-indexes)
- [Index Properties](#index-properties)
- [Query Plans and EXPLAIN](#query-plans-and-explain)
- [Index Selection](#index-selection)
- [Index Usage Patterns](#index-usage-patterns)
- [Summary](#summary)

---

## Introduction to Indexes

Indexes are data structures that improve the speed of data retrieval operations. Without indexes, MongoDB must scan every document in a collection to find matching documents.

### Why Indexes Matter

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Collection Scan vs Index Scan                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Collection Scan (No Index):                                        │
│  ┌───┬───┬───┬───┬───┬───┬───┬───┬───┬───┐                        │
│  │ 1 │ 2 │ 3 │ 4 │ 5 │ 6 │ 7 │ 8 │ 9 │10 │  ← Scan ALL documents  │
│  └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┘                        │
│                                                                     │
│  Documents Examined: 1,000,000 (all)                               │
│  Time: O(n) - Linear                                               │
│                                                                     │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                     │
│  Index Scan (With Index):                                          │
│                                                                     │
│           ┌───┐                                                    │
│           │ D │  ← B-tree root                                     │
│        ┌──┴───┴──┐                                                 │
│      ┌─┴─┐   ┌───┴───┐                                             │
│      │ B │   │   F   │                                             │
│     ┌┴─┬─┴┐ ┌┴──┬──┬─┴┐                                            │
│     │A│ │C│ │E│ │G│ │H│  ← Direct lookup                           │
│     └─┘ └─┘ └─┘ └─┘ └─┘                                            │
│                                                                     │
│  Documents Examined: 3-4 (log n)                                   │
│  Time: O(log n) - Logarithmic                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Index Performance Impact

| Collection Size | Collection Scan | Index Scan | Improvement |
|----------------|-----------------|------------|-------------|
| 1,000 docs | 1,000 reads | ~10 reads | 100x |
| 100,000 docs | 100,000 reads | ~17 reads | 6,000x |
| 1,000,000 docs | 1,000,000 reads | ~20 reads | 50,000x |
| 100,000,000 docs | 100M reads | ~27 reads | 3.7M x |

---

## How Indexes Work

MongoDB indexes use B-tree data structures (B+ trees for WiredTiger).

### B-Tree Structure

```javascript
// Index on { age: 1 }
// B-tree conceptual structure:

/*
                    [25, 50, 75]
                   /     |      \
                  /      |       \
    [10,15,20]     [30,40,45]    [60,70]    [80,90,95]
       |   |   |       |   |   |     |   |      |   |   |
      docs docs docs  docs docs docs docs docs  docs docs docs
*/

// Searching for age: 40
// 1. Start at root [25, 50, 75]
// 2. 40 is between 25 and 50, go to middle child
// 3. Navigate to [30, 40, 45]
// 4. Find 40, follow pointer to document
```

### Index Entry Structure

```javascript
// Document
{
  _id: ObjectId("507f1f77bcf86cd799439011"),
  name: "John",
  age: 30,
  email: "john@example.com"
}

// Index entry on { age: 1 }
{
  key: 30,
  location: "507f1f77bcf86cd799439011"  // Pointer to document
}

// Compound index { name: 1, age: 1 }
{
  key: ["John", 30],
  location: "507f1f77bcf86cd799439011"
}
```

### Index Storage

```javascript
// Check index sizes
db.collection.stats()

// Output includes:
{
  "indexSizes": {
    "_id_": 4096000,
    "name_1": 2048000,
    "email_1": 3072000
  },
  "totalIndexSize": 9216000
}
```

---

## Index Types Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MongoDB Index Types                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Single Field Index                                                │
│  └── { fieldName: 1 }                                              │
│                                                                     │
│  Compound Index                                                    │
│  └── { field1: 1, field2: -1 }                                     │
│                                                                     │
│  Multikey Index                                                    │
│  └── Index on array fields                                         │
│                                                                     │
│  Text Index                                                        │
│  └── { field: "text" }                                             │
│                                                                     │
│  Geospatial Index                                                  │
│  ├── 2dsphere (GeoJSON)                                            │
│  └── 2d (legacy coordinate pairs)                                  │
│                                                                     │
│  Hashed Index                                                      │
│  └── { field: "hashed" }                                           │
│                                                                     │
│  Wildcard Index                                                    │
│  └── { "$**": 1 }                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Default _id Index

Every MongoDB collection has a unique index on the `_id` field.

```javascript
// _id index is created automatically
db.createCollection("newCollection")

// View indexes
db.newCollection.getIndexes()
// Output: [{ "v": 2, "key": { "_id": 1 }, "name": "_id_" }]

// Cannot drop _id index on regular collections
db.newCollection.dropIndex("_id_")
// Error: cannot drop _id index

// _id is always unique
db.newCollection.insertMany([
  { _id: 1, name: "First" },
  { _id: 1, name: "Duplicate" }  // Error: duplicate key
])
```

### _id Field Best Practices

```javascript
// Default ObjectId (recommended)
db.collection.insertOne({ name: "Auto ID" })
// _id: ObjectId("...")

// Custom _id (when needed)
db.collection.insertOne({ _id: "custom-id-001", name: "Custom" })

// Compound _id (for specific use cases)
db.collection.insertOne({
  _id: { date: "2024-01-15", userId: "user-001" },
  data: "..."
})
```

---

## Creating Indexes

### Basic Index Creation

```javascript
// Create ascending index
db.users.createIndex({ email: 1 })

// Create descending index
db.users.createIndex({ createdAt: -1 })

// Create with options
db.users.createIndex(
  { email: 1 },
  {
    name: "email_unique_idx",
    unique: true,
    background: true
  }
)

// Check operation status
db.currentOp({ "command.createIndexes": { $exists: true } })
```

### createIndexes() - Multiple Indexes

```javascript
// Create multiple indexes at once
db.products.createIndexes([
  { key: { sku: 1 }, name: "sku_idx", unique: true },
  { key: { category: 1 }, name: "category_idx" },
  { key: { price: 1 }, name: "price_idx" }
])
```

### Build Options

```javascript
// Background build (deprecated in 4.2+, use default)
db.collection.createIndex(
  { field: 1 },
  { background: true }  // Pre-4.2
)

// MongoDB 4.2+: Indexes build in background by default
// Use commitQuorum for replica sets
db.collection.createIndex(
  { field: 1 },
  { commitQuorum: "votingMembers" }
)
```

---

## Index Properties

### Unique Index

```javascript
// Unique constraint
db.users.createIndex(
  { email: 1 },
  { unique: true }
)

// Insert succeeds
db.users.insertOne({ email: "john@example.com" })

// Duplicate fails
db.users.insertOne({ email: "john@example.com" })
// Error: E11000 duplicate key error

// Unique compound index
db.orders.createIndex(
  { customerId: 1, orderNumber: 1 },
  { unique: true }
)
```

### Sparse Index

```javascript
// Only index documents that have the field
db.contacts.createIndex(
  { phone: 1 },
  { sparse: true }
)

// Documents without phone field not in index
db.contacts.insertMany([
  { name: "John", phone: "123-456-7890" },  // Indexed
  { name: "Jane" },                          // NOT indexed
  { name: "Bob", phone: null }               // Indexed (null value)
])

// Note: Sparse indexes can miss documents in queries
db.contacts.find().sort({ phone: 1 })  // May not use sparse index
```

### Partial Index

```javascript
// Index only documents matching filter
db.orders.createIndex(
  { createdAt: 1 },
  {
    partialFilterExpression: {
      status: "active"
    }
  }
)

// Only active orders are indexed
// Query must include filter to use partial index
db.orders.find({ status: "active" }).sort({ createdAt: 1 })  // Uses index
db.orders.find().sort({ createdAt: 1 })  // May not use index

// Partial unique index
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: {
      email: { $exists: true }
    }
  }
)
// Allows multiple documents without email field
```

### TTL (Time-To-Live) Index

```javascript
// Auto-delete documents after time period
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 3600 }  // Delete after 1 hour
)

// Document structure
db.sessions.insertOne({
  sessionId: "abc123",
  userId: "user-001",
  createdAt: new Date()  // TTL based on this field
})

// Modify TTL
db.runCommand({
  collMod: "sessions",
  index: {
    keyPattern: { createdAt: 1 },
    expireAfterSeconds: 7200  // Change to 2 hours
  }
})
```

### Hidden Index

```javascript
// Hide index without dropping (MongoDB 4.4+)
db.collection.hideIndex("index_name")

// Unhide
db.collection.unhideIndex("index_name")

// Create as hidden
db.collection.createIndex(
  { field: 1 },
  { hidden: true }
)

// Test query performance without index
// (without actually dropping it)
```

---

## Query Plans and EXPLAIN

### Using explain()

```javascript
// Basic explain
db.users.find({ email: "john@example.com" }).explain()

// Execution stats
db.users.find({ email: "john@example.com" }).explain("executionStats")

// All plans
db.users.find({ email: "john@example.com" }).explain("allPlansExecution")
```

### Reading explain() Output

```javascript
// Example output
{
  "queryPlanner": {
    "winningPlan": {
      "stage": "FETCH",
      "inputStage": {
        "stage": "IXSCAN",
        "keyPattern": { "email": 1 },
        "indexName": "email_1",
        "direction": "forward"
      }
    }
  },
  "executionStats": {
    "executionSuccess": true,
    "nReturned": 1,
    "executionTimeMillis": 0,
    "totalKeysExamined": 1,
    "totalDocsExamined": 1
  }
}
```

### Query Stages

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Common Query Stages                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  COLLSCAN    │ Collection scan (no index used)                     │
│  IXSCAN      │ Index scan                                          │
│  FETCH       │ Retrieve documents from collection                  │
│  SORT        │ In-memory sort (not covered by index)               │
│  PROJECTION  │ Select specific fields                              │
│  LIMIT       │ Limit results                                       │
│  SKIP        │ Skip documents                                      │
│  SHARD_MERGE │ Merge results from shards                          │
│  COUNT_SCAN  │ Count using index                                   │
│  AND_SORTED  │ AND with sorted inputs                              │
│  OR          │ OR of multiple plans                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Identify Index Problems

```javascript
// Bad: Collection scan
{
  "stage": "COLLSCAN"  // No index used!
}

// Bad: In-memory sort
{
  "stage": "SORT",
  "memUsage": 33554432,  // 32MB limit
  "memLimit": 33554432
}

// Good: Covered query
{
  "totalDocsExamined": 0  // No document fetch needed
}

// Good: Efficient index use
{
  "nReturned": 10,
  "totalKeysExamined": 10,  // Same as returned
  "totalDocsExamined": 10   // Same as returned
}
```

---

## Index Selection

MongoDB's query planner selects the best index.

### Query Planner Process

```javascript
// 1. Generate candidate plans (one per relevant index)
// 2. Execute plans in parallel (race)
// 3. Select winning plan (fewest work units)
// 4. Cache winning plan for similar queries

// View cached plans
db.collection.getPlanCache().list()

// Clear plan cache
db.collection.getPlanCache().clear()
```

### Hint to Force Index

```javascript
// Force specific index
db.users.find({ name: "John", age: 30 })
  .hint({ name: 1 })  // Force name index

// Force index by name
db.users.find({ name: "John" })
  .hint("name_1")

// Force collection scan (for testing)
db.users.find({ name: "John" })
  .hint({ $natural: 1 })
```

---

## Index Usage Patterns

### Equality, Sort, Range (ESR) Rule

```javascript
// For compound indexes, order fields:
// 1. Equality conditions first
// 2. Sort fields second
// 3. Range conditions last

// Query pattern
db.orders.find({
  customerId: "cust-001",     // Equality
  status: "active",            // Equality
  createdAt: { $gte: startDate }  // Range
}).sort({ amount: -1 })        // Sort

// Optimal index
db.orders.createIndex({
  customerId: 1,   // E: Equality
  status: 1,       // E: Equality
  amount: -1,      // S: Sort
  createdAt: 1     // R: Range
})
```

### Index Intersection

```javascript
// MongoDB can combine multiple indexes
db.users.createIndex({ name: 1 })
db.users.createIndex({ age: 1 })

// Query might use both
db.users.find({ name: "John", age: 30 })

// Usually compound index is better
db.users.createIndex({ name: 1, age: 1 })
```

### Covering Queries

```javascript
// Index covers query when all fields are in index
db.users.createIndex({ email: 1, name: 1, age: 1 })

// Covered query (no FETCH stage)
db.users.find(
  { email: "john@example.com" },
  { name: 1, age: 1, _id: 0 }  // Only indexed fields
)

// explain shows totalDocsExamined: 0
```

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| **B-tree** | Index data structure |
| **IXSCAN** | Index scan (efficient) |
| **COLLSCAN** | Collection scan (avoid) |
| **Covered Query** | Query satisfied entirely by index |
| **ESR Rule** | Equality, Sort, Range ordering |

### Index Properties

| Property | Description |
|----------|-------------|
| **unique** | Enforce uniqueness |
| **sparse** | Only index existing fields |
| **partial** | Index subset of documents |
| **TTL** | Auto-expire documents |
| **hidden** | Hide without dropping |

### What's Next?

In the next chapter, we'll deep dive into Single Field Indexes.

---

## Practice Questions

1. What's the time complexity of a B-tree lookup?
2. When would you use a sparse index vs partial index?
3. How do you identify a collection scan in explain output?
4. What is a covered query and why is it efficient?
5. How does the query planner select an index?
6. What is the ESR rule for compound indexes?
7. When should you use index hints?
8. How does TTL index work?

---

## Hands-On Exercises

### Exercise 1: Create and Analyze Indexes

```javascript
// Setup
db.test_users.drop()
for (let i = 0; i < 10000; i++) {
  db.test_users.insertOne({
    name: `User${i}`,
    email: `user${i}@example.com`,
    age: Math.floor(Math.random() * 80) + 18,
    status: i % 2 === 0 ? "active" : "inactive",
    createdAt: new Date(Date.now() - Math.random() * 86400000 * 365)
  })
}

// Query without index
const noIndexPlan = db.test_users.find({ email: "user5000@example.com" })
  .explain("executionStats")
print("Without index:")
print("  Stage:", noIndexPlan.queryPlanner.winningPlan.stage)
print("  Docs examined:", noIndexPlan.executionStats.totalDocsExamined)
print("  Time:", noIndexPlan.executionStats.executionTimeMillis, "ms")

// Create index
db.test_users.createIndex({ email: 1 })

// Query with index
const withIndexPlan = db.test_users.find({ email: "user5000@example.com" })
  .explain("executionStats")
print("\nWith index:")
print("  Stage:", withIndexPlan.queryPlanner.winningPlan.inputStage.stage)
print("  Keys examined:", withIndexPlan.executionStats.totalKeysExamined)
print("  Docs examined:", withIndexPlan.executionStats.totalDocsExamined)
print("  Time:", withIndexPlan.executionStats.executionTimeMillis, "ms")
```

### Exercise 2: Partial Index

```javascript
// Create partial index for active users only
db.test_users.createIndex(
  { name: 1 },
  {
    partialFilterExpression: { status: "active" },
    name: "active_users_name"
  }
)

// Query that uses partial index
const activePlan = db.test_users.find({ status: "active", name: "User100" })
  .explain()
print("Active users query uses:", activePlan.queryPlanner.winningPlan.inputStage?.indexName)

// Query that doesn't use partial index
const allPlan = db.test_users.find({ name: "User100" })
  .explain()
print("All users query uses:", allPlan.queryPlanner.winningPlan.inputStage?.indexName || "COLLSCAN")
```

### Exercise 3: TTL Index

```javascript
// Create sessions collection
db.test_sessions.drop()

// Create TTL index (expire after 60 seconds)
db.test_sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 60 }
)

// Insert session
db.test_sessions.insertOne({
  sessionId: "session-001",
  userId: "user-001",
  createdAt: new Date()
})

// Check count
print("Initial count:", db.test_sessions.countDocuments())

// Wait and check again (TTL background task runs every 60 seconds)
print("Document will be deleted after TTL expires")
```

### Exercise 4: Covered Query

```javascript
// Create compound index
db.test_users.createIndex({ status: 1, email: 1, name: 1 })

// Covered query (only request indexed fields, exclude _id)
const coveredPlan = db.test_users.find(
  { status: "active" },
  { email: 1, name: 1, _id: 0 }
).explain("executionStats")

print("Covered query:")
print("  Total keys examined:", coveredPlan.executionStats.totalKeysExamined)
print("  Total docs examined:", coveredPlan.executionStats.totalDocsExamined)
// totalDocsExamined should be 0 for covered query

// Non-covered query (includes non-indexed field)
const nonCoveredPlan = db.test_users.find(
  { status: "active" },
  { email: 1, name: 1, age: 1, _id: 0 }  // age not in index
).explain("executionStats")

print("\nNon-covered query:")
print("  Total keys examined:", nonCoveredPlan.executionStats.totalKeysExamined)
print("  Total docs examined:", nonCoveredPlan.executionStats.totalDocsExamined)
```

---

[← Previous: Schema Design Patterns](15-schema-design-patterns.md) | [Next: Single Field Indexes →](17-single-field-indexes.md)
