# Chapter 18: Compound Indexes

## Table of Contents
- [Introduction to Compound Indexes](#introduction-to-compound-indexes)
- [Creating Compound Indexes](#creating-compound-indexes)
- [Index Prefixes](#index-prefixes)
- [Sort Order in Compound Indexes](#sort-order-in-compound-indexes)
- [The ESR Rule](#the-esr-rule)
- [Compound Index Strategies](#compound-index-strategies)
- [Covered Queries](#covered-queries)
- [Common Patterns](#common-patterns)
- [Summary](#summary)

---

## Introduction to Compound Indexes

A compound index is an index on multiple fields. The order of fields in a compound index is critical.

### Compound Index Structure

```
┌─────────────────────────────────────────────────────────────────────┐
│            Compound Index: { category: 1, price: 1 }                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Index Entry Structure (sorted by category, then price):            │
│                                                                     │
│  ┌─────────────────┬─────────┬─────────────────────────┐           │
│  │   category      │  price  │   Document Pointer      │           │
│  ├─────────────────┼─────────┼─────────────────────────┤           │
│  │  Books          │  9.99   │  → doc_id_1            │           │
│  │  Books          │  14.99  │  → doc_id_2            │           │
│  │  Books          │  29.99  │  → doc_id_3            │           │
│  │  Electronics    │  49.99  │  → doc_id_4            │           │
│  │  Electronics    │  99.99  │  → doc_id_5            │           │
│  │  Electronics    │  199.99 │  → doc_id_6            │           │
│  │  Home           │  19.99  │  → doc_id_7            │           │
│  │  Home           │  39.99  │  → doc_id_8            │           │
│  └─────────────────┴─────────┴─────────────────────────┘           │
│                                                                     │
│  • First sorted by category (alphabetically)                       │
│  • Within each category, sorted by price (ascending)               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Field Order Matters

```javascript
// Index: { category: 1, price: 1 }

// Query 1: Uses index efficiently
db.products.find({ category: "Electronics" })
// Can use index - category is prefix

// Query 2: Uses index efficiently
db.products.find({ category: "Electronics", price: { $lt: 100 } })
// Can use index - both fields in order

// Query 3: Cannot use index efficiently
db.products.find({ price: { $lt: 100 } })
// Cannot use index - price is not prefix
// Must scan entire index or collection
```

---

## Creating Compound Indexes

### Basic Creation

```javascript
// Two-field compound index
db.products.createIndex({ category: 1, price: 1 })

// Three-field compound index
db.orders.createIndex({ customerId: 1, status: 1, createdAt: -1 })

// With options
db.products.createIndex(
  { category: 1, sku: 1 },
  {
    unique: true,
    name: "category_sku_unique"
  }
)
```

### Maximum Fields

```javascript
// MongoDB supports up to 32 fields in compound index
// But in practice, 3-5 fields is typical

// Example: E-commerce product search
db.products.createIndex({
  category: 1,
  brand: 1,
  price: 1,
  rating: -1
})
```

---

## Index Prefixes

A compound index supports queries on any prefix of the indexed fields.

### Prefix Concept

```javascript
// Index: { a: 1, b: 1, c: 1, d: 1 }

// Supported prefixes:
// { a: 1 }
// { a: 1, b: 1 }
// { a: 1, b: 1, c: 1 }
// { a: 1, b: 1, c: 1, d: 1 }

// NOT a valid prefix (skips b):
// { a: 1, c: 1 }
```

### Practical Example

```javascript
// Create compound index
db.orders.createIndex({ customerId: 1, status: 1, createdAt: -1 })

// Query 1: Uses index (prefix: customerId)
db.orders.find({ customerId: "cust-001" })

// Query 2: Uses index (prefix: customerId, status)
db.orders.find({ customerId: "cust-001", status: "pending" })

// Query 3: Uses index (full index)
db.orders.find({ 
  customerId: "cust-001", 
  status: "pending",
  createdAt: { $gte: new Date("2024-01-01") }
})

// Query 4: CANNOT use index efficiently (no customerId)
db.orders.find({ status: "pending" })

// Query 5: PARTIAL use (only customerId prefix)
db.orders.find({ customerId: "cust-001", createdAt: { $gte: new Date() } })
// Uses index for customerId, but not optimally for createdAt
```

---

## Sort Order in Compound Indexes

### Direction Matters for Multi-Field Sort

```javascript
// Index: { category: 1, price: 1 }

// Supported sorts:
db.products.find().sort({ category: 1 })                    // ✓
db.products.find().sort({ category: -1 })                   // ✓ (reverse scan)
db.products.find().sort({ category: 1, price: 1 })          // ✓
db.products.find().sort({ category: -1, price: -1 })        // ✓ (reverse scan)

// NOT supported (requires in-memory sort):
db.products.find().sort({ category: 1, price: -1 })         // ✗
db.products.find().sort({ category: -1, price: 1 })         // ✗
db.products.find().sort({ price: 1 })                       // ✗ (not prefix)
```

### Creating Index for Mixed Sort

```javascript
// For sort: { category: 1, price: -1 }
// Create index with matching directions
db.products.createIndex({ category: 1, price: -1 })

// Now supports:
db.products.find().sort({ category: 1, price: -1 })   // ✓ Forward
db.products.find().sort({ category: -1, price: 1 })   // ✓ Reverse
```

### Sort Direction Table

```
┌────────────────────────────────────────────────────────────────────┐
│           Index: { a: 1, b: -1, c: 1 }                             │
├────────────────────────────────────────────────────────────────────┤
│  Sort                          │  Uses Index?                      │
│  ──────────────────────────────┼────────────────────────────────── │
│  { a: 1 }                      │  ✓ Yes                           │
│  { a: -1 }                     │  ✓ Yes (reverse)                 │
│  { a: 1, b: -1 }               │  ✓ Yes                           │
│  { a: -1, b: 1 }               │  ✓ Yes (reverse)                 │
│  { a: 1, b: -1, c: 1 }         │  ✓ Yes                           │
│  { a: -1, b: 1, c: -1 }        │  ✓ Yes (reverse)                 │
│  { a: 1, b: 1 }                │  ✗ No (b direction mismatch)     │
│  { b: -1 }                     │  ✗ No (not prefix)               │
│  { a: 1, c: 1 }                │  ✗ No (skips b)                  │
└────────────────────────────────────────────────────────────────────┘
```

---

## The ESR Rule

**E**quality, **S**ort, **R**ange - the optimal order for compound index fields.

### Rule Explanation

```javascript
// Query pattern:
db.orders.find({
  customerId: "cust-001",           // Equality
  status: { $in: ["pending", "processing"] },  // Range (treated as range)
  createdAt: { $gte: startDate }    // Range
}).sort({ amount: -1 })             // Sort

// ESR optimal index:
db.orders.createIndex({
  customerId: 1,   // E - Equality first
  amount: -1,      // S - Sort second
  status: 1,       // R - Range last
  createdAt: 1     // R - Range last
})
```

### Why ESR Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ESR Rule Explained                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. EQUALITY First                                                  │
│     • Narrows results to exact matches                             │
│     • Most selective filtering                                     │
│     • Creates contiguous index range                               │
│                                                                     │
│  2. SORT Second                                                     │
│     • After equality, remaining entries are in sort order          │
│     • Avoids in-memory sort                                        │
│     • Streaming results possible                                   │
│                                                                     │
│  3. RANGE Last                                                      │
│     • Range conditions scan multiple index entries                 │
│     • After equality+sort, range filters remaining entries         │
│     • Range on early field breaks sort optimization                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### ESR Examples

```javascript
// Example 1: User orders query
// Query: Find user's orders in date range, sorted by amount
db.orders.find({
  userId: "user-001",              // E
  createdAt: { $gte: start, $lte: end }  // R
}).sort({ amount: -1 })            // S

// Optimal index: E, S, R
db.orders.createIndex({ userId: 1, amount: -1, createdAt: 1 })


// Example 2: Product search
// Query: Category + price range + sorted by rating
db.products.find({
  category: "Electronics",         // E
  price: { $gte: 100, $lte: 500 }  // R
}).sort({ rating: -1 })            // S

// Optimal index
db.products.createIndex({ category: 1, rating: -1, price: 1 })


// Example 3: Multiple equalities
// Query: Store + status + date range, sorted by priority
db.tasks.find({
  storeId: "store-001",            // E
  status: "pending",               // E
  dueDate: { $lte: new Date() }    // R
}).sort({ priority: -1 })          // S

// Optimal index
db.tasks.createIndex({ 
  storeId: 1, 
  status: 1, 
  priority: -1, 
  dueDate: 1 
})
```

---

## Compound Index Strategies

### Strategy 1: Cover Common Query Patterns

```javascript
// Analyze query patterns first
// Pattern 1: Find by user and status
db.orders.find({ userId: "u1", status: "pending" })

// Pattern 2: Find by user, sorted by date
db.orders.find({ userId: "u1" }).sort({ createdAt: -1 })

// Pattern 3: Find by user, status, date range
db.orders.find({ 
  userId: "u1", 
  status: "completed",
  createdAt: { $gte: start }
})

// One index covers all patterns
db.orders.createIndex({ userId: 1, status: 1, createdAt: -1 })
```

### Strategy 2: Balance Read vs Write

```javascript
// More indexes = slower writes
// Choose indexes that cover multiple queries

// Instead of:
db.products.createIndex({ category: 1 })
db.products.createIndex({ category: 1, brand: 1 })
db.products.createIndex({ category: 1, brand: 1, price: 1 })

// Use single compound index:
db.products.createIndex({ category: 1, brand: 1, price: 1 })
// Supports all three query patterns via prefixes
```

### Strategy 3: Consider Selectivity

```javascript
// Put more selective fields first
// (when not constrained by ESR)

// Example: Logging collection
// userId: high selectivity (many users)
// level: low selectivity (only: info, warn, error)

// Better order:
db.logs.createIndex({ userId: 1, level: 1, timestamp: -1 })

// Rather than:
db.logs.createIndex({ level: 1, userId: 1, timestamp: -1 })
```

---

## Covered Queries

A covered query is satisfied entirely by the index without reading documents.

### Creating Covered Queries

```javascript
// Index
db.users.createIndex({ email: 1, name: 1, status: 1 })

// Covered query - all fields in index
db.users.find(
  { email: "john@example.com" },
  { email: 1, name: 1, status: 1, _id: 0 }  // Must exclude _id
)

// Check with explain
const plan = db.users.find(
  { email: "john@example.com" },
  { email: 1, name: 1, status: 1, _id: 0 }
).explain("executionStats")

// For covered query:
// totalDocsExamined: 0 (no document fetched)
```

### Covered Query Requirements

```javascript
// Requirements for covered query:
// 1. All query fields are in the index
// 2. All projection fields are in the index
// 3. _id is excluded from projection (or also indexed)
// 4. No array fields (multikey index)

// Example setup
db.users.createIndex({ 
  email: 1, 
  name: 1, 
  age: 1, 
  status: 1 
})

// Covered:
db.users.find(
  { email: "test@example.com" },
  { name: 1, age: 1, _id: 0 }
)

// NOT covered (includes non-indexed field):
db.users.find(
  { email: "test@example.com" },
  { name: 1, age: 1, address: 1, _id: 0 }  // address not in index
)

// NOT covered (_id included):
db.users.find(
  { email: "test@example.com" },
  { name: 1, age: 1 }  // _id included by default
)
```

---

## Common Patterns

### Pattern 1: Customer Orders

```javascript
// Common queries:
// - Get customer's orders
// - Get customer's orders by status
// - Get customer's recent orders

db.orders.createIndex({ 
  customerId: 1, 
  status: 1, 
  createdAt: -1 
})

// All queries work efficiently:
db.orders.find({ customerId: "c1" })
db.orders.find({ customerId: "c1", status: "pending" })
db.orders.find({ customerId: "c1" }).sort({ createdAt: -1 }).limit(10)
```

### Pattern 2: E-commerce Product Catalog

```javascript
// Common queries:
// - Browse by category
// - Filter by category and price range
// - Sort by rating, price, or date

// Index for category browsing with price filter
db.products.createIndex({ 
  category: 1, 
  isActive: 1,
  price: 1 
})

// Index for sorting by rating
db.products.createIndex({ 
  category: 1, 
  isActive: 1,
  rating: -1 
})

// Queries:
db.products.find({ category: "Electronics", isActive: true })
  .sort({ rating: -1 })
  .limit(20)

db.products.find({ 
  category: "Electronics", 
  isActive: true,
  price: { $gte: 100, $lte: 500 }
})
```

### Pattern 3: Time-Series Data

```javascript
// Sensor readings by device and time
db.readings.createIndex({ 
  deviceId: 1, 
  timestamp: -1 
})

// Get latest readings for device
db.readings.find({ deviceId: "sensor-001" })
  .sort({ timestamp: -1 })
  .limit(100)

// Get readings in time range
db.readings.find({
  deviceId: "sensor-001",
  timestamp: { 
    $gte: ISODate("2024-01-01"),
    $lt: ISODate("2024-01-02")
  }
})
```

### Pattern 4: Multi-Tenant Application

```javascript
// Always filter by tenant first
db.documents.createIndex({
  tenantId: 1,
  type: 1,
  createdAt: -1
})

// All queries include tenantId
db.documents.find({ 
  tenantId: "tenant-001",
  type: "invoice"
}).sort({ createdAt: -1 })
```

---

## Summary

### Compound Index Key Points

| Concept | Description |
|---------|-------------|
| **Field Order** | Critical - determines query support |
| **Prefixes** | Index supports queries on any prefix |
| **Sort Direction** | Must match or be exact reverse |
| **ESR Rule** | Equality → Sort → Range |
| **Covered Query** | No document fetch needed |

### Design Guidelines

| Guideline | Description |
|-----------|-------------|
| **Analyze Queries** | Design indexes for actual query patterns |
| **Use Prefixes** | One index can serve multiple queries |
| **Consider Selectivity** | More selective fields earlier |
| **Test with explain()** | Verify index usage |

### What's Next?

In the next chapter, we'll explore Multikey Indexes for array fields.

---

## Practice Questions

1. Why does field order matter in compound indexes?
2. What is an index prefix and how does it help?
3. When does sort direction matter in compound indexes?
4. Explain the ESR rule with an example.
5. What are the requirements for a covered query?
6. How do you choose which fields to include in a compound index?
7. Can one compound index replace multiple single field indexes?
8. How does selectivity affect compound index design?

---

## Hands-On Exercises

### Exercise 1: Index Prefix Behavior

```javascript
// Setup
db.compound_test.drop()
for (let i = 0; i < 1000; i++) {
  db.compound_test.insertOne({
    a: `value_${i % 10}`,
    b: `value_${i % 20}`,
    c: `value_${i % 50}`,
    d: i
  })
}

// Create compound index
db.compound_test.createIndex({ a: 1, b: 1, c: 1 })

// Test prefix queries
const queries = [
  { a: "value_1" },                           // Uses prefix { a }
  { a: "value_1", b: "value_5" },             // Uses prefix { a, b }
  { a: "value_1", b: "value_5", c: "value_10" }, // Uses full index
  { b: "value_5" },                           // No prefix match
  { a: "value_1", c: "value_10" }             // Uses { a } only
]

queries.forEach((query, i) => {
  const plan = db.compound_test.find(query).explain()
  const stage = plan.queryPlanner.winningPlan.inputStage?.stage || 
                plan.queryPlanner.winningPlan.stage
  print(`Query ${i + 1}: ${JSON.stringify(query)}`)
  print(`  Stage: ${stage}`)
})
```

### Exercise 2: Sort Direction

```javascript
// Create index with specific directions
db.sort_test.drop()
db.sort_test.insertMany([
  { category: "A", price: 100, rating: 4.5 },
  { category: "A", price: 200, rating: 4.0 },
  { category: "B", price: 150, rating: 4.8 },
  { category: "B", price: 250, rating: 3.5 }
])

db.sort_test.createIndex({ category: 1, price: -1 })

// Test sorts
const sorts = [
  { category: 1 },
  { category: -1 },
  { category: 1, price: -1 },
  { category: -1, price: 1 },
  { category: 1, price: 1 },   // Should need in-memory sort
  { price: -1 }                // Not prefix
]

sorts.forEach((sort, i) => {
  const plan = db.sort_test.find().sort(sort).explain()
  const stages = JSON.stringify(plan.queryPlanner.winningPlan)
  const usesSort = stages.includes('"stage":"SORT"')
  print(`Sort ${i + 1}: ${JSON.stringify(sort)}`)
  print(`  In-memory sort needed: ${usesSort}`)
})
```

### Exercise 3: ESR Rule Application

```javascript
// Setup
db.esr_orders.drop()
for (let i = 0; i < 1000; i++) {
  db.esr_orders.insertOne({
    customerId: `cust-${i % 50}`,
    status: ["pending", "processing", "shipped", "delivered"][i % 4],
    amount: Math.random() * 1000,
    createdAt: new Date(Date.now() - Math.random() * 86400000 * 30)
  })
}

// Query pattern: customer's pending orders, sorted by amount
const query = { customerId: "cust-10", status: "pending" }
const sort = { amount: -1 }

// Test different index orders
const indexOrders = [
  { customerId: 1, status: 1, amount: -1 },         // E, E, S - Good
  { customerId: 1, amount: -1, status: 1 },         // E, S, R - Best (ESR)
  { amount: -1, customerId: 1, status: 1 },         // S, E, E - Poor
  { status: 1, customerId: 1, amount: -1 }          // E, E, S - Depends on selectivity
]

indexOrders.forEach((idx, i) => {
  // Drop existing indexes
  db.esr_orders.dropIndexes()
  
  // Create new index
  const idxName = `test_idx_${i}`
  db.esr_orders.createIndex(idx, { name: idxName })
  
  // Test query
  const plan = db.esr_orders.find(query).sort(sort).explain("executionStats")
  
  print(`\nIndex ${i + 1}: ${JSON.stringify(idx)}`)
  print(`  Keys examined: ${plan.executionStats.totalKeysExamined}`)
  print(`  Docs examined: ${plan.executionStats.totalDocsExamined}`)
  print(`  Execution time: ${plan.executionStats.executionTimeMillis}ms`)
})
```

### Exercise 4: Covered Query

```javascript
// Setup
db.covered_test.drop()
db.covered_test.insertMany([
  { email: "a@test.com", name: "Alice", age: 30, city: "NYC" },
  { email: "b@test.com", name: "Bob", age: 25, city: "LA" },
  { email: "c@test.com", name: "Charlie", age: 35, city: "Chicago" }
])

// Create index for covered query
db.covered_test.createIndex({ email: 1, name: 1, age: 1 })

// Test covered vs non-covered
print("Covered query (email, name, age without _id):")
let plan = db.covered_test.find(
  { email: "a@test.com" },
  { email: 1, name: 1, age: 1, _id: 0 }
).explain("executionStats")
print(`  Docs examined: ${plan.executionStats.totalDocsExamined}`)

print("\nNon-covered query (includes city):")
plan = db.covered_test.find(
  { email: "a@test.com" },
  { email: 1, name: 1, age: 1, city: 1, _id: 0 }
).explain("executionStats")
print(`  Docs examined: ${plan.executionStats.totalDocsExamined}`)

print("\nNon-covered query (includes _id):")
plan = db.covered_test.find(
  { email: "a@test.com" },
  { email: 1, name: 1, age: 1 }
).explain("executionStats")
print(`  Docs examined: ${plan.executionStats.totalDocsExamined}`)
```

---

[← Previous: Single Field Indexes](17-single-field-indexes.md) | [Next: Multikey Indexes →](19-multikey-indexes.md)
