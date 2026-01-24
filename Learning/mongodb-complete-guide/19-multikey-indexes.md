# Chapter 19: Multikey Indexes

## Table of Contents
- [Introduction to Multikey Indexes](#introduction-to-multikey-indexes)
- [How Multikey Indexes Work](#how-multikey-indexes-work)
- [Creating Multikey Indexes](#creating-multikey-indexes)
- [Querying with Multikey Indexes](#querying-with-multikey-indexes)
- [Compound Multikey Indexes](#compound-multikey-indexes)
- [Multikey Index Limitations](#multikey-index-limitations)
- [Performance Considerations](#performance-considerations)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Introduction to Multikey Indexes

Multikey indexes are automatically created when you index a field that contains an array. MongoDB creates an index entry for each element in the array.

### Multikey Index Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Multikey Index Structure                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Document:                                                          │
│  {                                                                  │
│    _id: 1,                                                          │
│    name: "Product A",                                               │
│    tags: ["electronics", "sale", "featured"]                        │
│  }                                                                  │
│                                                                     │
│  Index on { tags: 1 } creates entries:                             │
│                                                                     │
│  ┌─────────────┬─────────────────┐                                 │
│  │  Key        │  Document       │                                 │
│  ├─────────────┼─────────────────┤                                 │
│  │ electronics │  → document 1   │                                 │
│  │ featured    │  → document 1   │                                 │
│  │ sale        │  → document 1   │                                 │
│  └─────────────┴─────────────────┘                                 │
│                                                                     │
│  One document → Multiple index entries                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## How Multikey Indexes Work

### Automatic Creation

```javascript
// Insert document with array
db.products.insertOne({
  name: "Laptop",
  tags: ["electronics", "computers", "sale"]
})

// Create index on array field
db.products.createIndex({ tags: 1 })

// MongoDB automatically creates multikey index
// Check with explain
db.products.find({ tags: "electronics" }).explain()
// Shows: "isMultiKey": true
```

### Index Entry Generation

```javascript
// Document
{
  _id: 1,
  title: "Blog Post",
  tags: ["mongodb", "database", "tutorial"]
}

// Multikey index creates 3 entries for this document:
// ("database", _id: 1)
// ("mongodb", _id: 1)
// ("tutorial", _id: 1)

// Multiple documents with overlapping values
{
  _id: 2,
  title: "Another Post",
  tags: ["mongodb", "javascript"]
}

// Total index now has:
// ("database", _id: 1)
// ("javascript", _id: 2)
// ("mongodb", _id: 1)
// ("mongodb", _id: 2)  // Same key, different documents
// ("tutorial", _id: 1)
```

---

## Creating Multikey Indexes

### Basic Array Index

```javascript
// Simple array of values
db.articles.insertMany([
  {
    title: "MongoDB Basics",
    tags: ["mongodb", "database", "nosql"]
  },
  {
    title: "Node.js Guide",
    tags: ["javascript", "nodejs", "backend"]
  }
])

// Create multikey index
db.articles.createIndex({ tags: 1 })
```

### Array of Embedded Documents

```javascript
// Documents with array of objects
db.products.insertOne({
  name: "Smartphone",
  reviews: [
    { user: "john", rating: 5, text: "Excellent!" },
    { user: "jane", rating: 4, text: "Very good" },
    { user: "bob", rating: 3, text: "Decent" }
  ]
})

// Index on embedded field within array
db.products.createIndex({ "reviews.rating": 1 })

// Index on multiple embedded fields
db.products.createIndex({ "reviews.user": 1 })
```

### Nested Arrays

```javascript
// Document with nested structure
db.inventory.insertOne({
  item: "ABC",
  stock: [
    {
      warehouse: "A",
      locations: [
        { shelf: "A1", qty: 10 },
        { shelf: "A2", qty: 20 }
      ]
    },
    {
      warehouse: "B",
      locations: [
        { shelf: "B1", qty: 15 }
      ]
    }
  ]
})

// Index on nested array field
db.inventory.createIndex({ "stock.locations.shelf": 1 })
```

---

## Querying with Multikey Indexes

### Basic Queries

```javascript
// Setup
db.products.insertMany([
  { name: "Product A", tags: ["electronics", "sale", "new"] },
  { name: "Product B", tags: ["clothing", "sale"] },
  { name: "Product C", tags: ["electronics", "clearance"] }
])

db.products.createIndex({ tags: 1 })

// Query single value
db.products.find({ tags: "electronics" })
// Returns: Product A, Product C

// Query with $in
db.products.find({ tags: { $in: ["sale", "clearance"] } })
// Returns: Product A, Product B, Product C

// Query with $all (AND condition)
db.products.find({ tags: { $all: ["electronics", "sale"] } })
// Returns: Product A only
```

### Array Query Operators

```javascript
// $elemMatch for complex conditions
db.products.insertMany([
  {
    name: "Widget",
    variants: [
      { color: "red", size: "S", qty: 10 },
      { color: "blue", size: "M", qty: 20 }
    ]
  },
  {
    name: "Gadget",
    variants: [
      { color: "red", size: "M", qty: 5 },
      { color: "green", size: "L", qty: 15 }
    ]
  }
])

db.products.createIndex({ "variants.color": 1, "variants.size": 1 })

// Find products with red color AND size M in SAME variant
db.products.find({
  variants: {
    $elemMatch: { color: "red", size: "M" }
  }
})
// Returns: Gadget only

// Without $elemMatch - matches across different elements
db.products.find({
  "variants.color": "red",
  "variants.size": "M"
})
// Returns: Widget AND Gadget
// (Widget has red in one element, M in another)
```

### Array Size Queries

```javascript
// Create index on tags
db.articles.createIndex({ tags: 1 })

// Query by array size (doesn't use multikey index)
db.articles.find({ tags: { $size: 3 } })

// For size queries, consider adding a size field
db.articles.updateMany(
  {},
  [{ $set: { tagCount: { $size: "$tags" } } }]
)
db.articles.createIndex({ tagCount: 1 })
```

---

## Compound Multikey Indexes

### Single Array Field

```javascript
// Compound index with one array field
db.orders.insertMany([
  {
    orderId: "O001",
    customer: "John",
    items: ["apple", "banana", "orange"]
  },
  {
    orderId: "O002",
    customer: "Jane",
    items: ["apple", "grape"]
  }
])

// Valid: One array field + scalar fields
db.orders.createIndex({ customer: 1, items: 1 })

// Query uses compound index
db.orders.find({ customer: "John", items: "apple" })
```

### Embedded Documents in Arrays

```javascript
// Product with reviews
db.products.insertMany([
  {
    sku: "SKU001",
    name: "Laptop",
    reviews: [
      { rating: 5, verified: true },
      { rating: 4, verified: true }
    ]
  },
  {
    sku: "SKU002",
    name: "Phone",
    reviews: [
      { rating: 3, verified: false }
    ]
  }
])

// Compound index on embedded array fields
db.products.createIndex({ "reviews.rating": 1, "reviews.verified": 1 })

// Query with both fields
db.products.find({
  "reviews.rating": { $gte: 4 },
  "reviews.verified": true
})
```

---

## Multikey Index Limitations

### Parallel Arrays Restriction

```javascript
// Cannot index two parallel arrays in compound index
db.data.insertOne({
  arr1: [1, 2, 3],
  arr2: ["a", "b", "c"]
})

// This FAILS
db.data.createIndex({ arr1: 1, arr2: 1 })
// Error: cannot index parallel arrays

// Reason: Would create n×m index entries
// arr1 has 3 elements, arr2 has 3 elements
// Would need 9 entries per document (Cartesian product)
```

### Valid Compound Multikey Scenarios

```javascript
// One array, one scalar - OK
db.collection.createIndex({ arrayField: 1, scalarField: 1 })

// Array of embedded documents - OK
db.collection.createIndex({ "arr.field1": 1, "arr.field2": 1 })
// Both fields from same array

// Nested arrays - depends on structure
db.collection.insertOne({
  outer: [
    { inner: [1, 2] },
    { inner: [3, 4] }
  ]
})
// Index on outer.inner creates multikey entries
```

### Shard Key Restriction

```javascript
// Cannot use multikey index as shard key
sh.shardCollection("db.collection", { tags: 1 })
// Error: shard key cannot be a multikey index

// Solution: Use hashed index on different field
sh.shardCollection("db.collection", { _id: "hashed" })
```

### Covered Query Limitation

```javascript
// Multikey indexes cannot cover queries
db.products.createIndex({ tags: 1, name: 1 })

// This query is NOT covered (even with projection)
db.products.find(
  { tags: "electronics" },
  { tags: 1, name: 1, _id: 0 }
)
// Will still fetch documents
```

---

## Performance Considerations

### Index Size

```javascript
// Multikey indexes are larger
// More index entries = more storage and memory

// Check index size
db.products.stats().indexSizes

// Example:
// Regular index on 1M docs with 1M entries
// Multikey index on 1M docs with avg 5 elements = 5M entries
```

### Write Performance

```javascript
// Updates to arrays affect index
db.products.updateOne(
  { _id: 1 },
  { $push: { tags: "new-tag" } }
)
// Must add new index entry

db.products.updateOne(
  { _id: 1 },
  { $pull: { tags: "old-tag" } }
)
// Must remove index entry

// Bulk array modifications are expensive
db.products.updateOne(
  { _id: 1 },
  { $set: { tags: ["completely", "new", "array", "of", "tags"] } }
)
// Remove old entries, add new entries
```

### Query Optimization

```javascript
// Use $elemMatch for precise array element matching
// More efficient than separate field queries

// Good: Single index scan
db.products.find({
  variants: {
    $elemMatch: {
      color: "red",
      size: "M",
      qty: { $gte: 5 }
    }
  }
})

// Less optimal: May scan more entries
db.products.find({
  "variants.color": "red",
  "variants.size": "M",
  "variants.qty": { $gte: 5 }
})
```

---

## Best Practices

### 1. Limit Array Size

```javascript
// Large arrays = many index entries
// Consider bucket pattern for large arrays

// Instead of:
{
  userId: 1,
  activities: [/* 10,000 activity entries */]
}

// Use separate collection or bucket:
{
  userId: 1,
  date: "2024-01-15",
  activities: [/* 100 entries */]
}
```

### 2. Index Selective Fields

```javascript
// Index fields used in queries, not all array fields

// If you only search by tags
db.products.createIndex({ tags: 1 })

// Don't also index images array if not queried
// db.products.createIndex({ images: 1 })  // Skip if not needed
```

### 3. Use Compound Indexes Wisely

```javascript
// Combine with high-selectivity scalar fields
db.orders.createIndex({ customerId: 1, items: 1 })

// Query efficiently filters by customer first
db.orders.find({ customerId: "c001", items: "product-x" })
```

### 4. Consider Denormalization

```javascript
// If array searches are complex, consider restructuring

// Instead of querying nested arrays:
{
  orderId: 1,
  items: [
    { productId: "p1", options: [{ size: "M" }] }
  ]
}

// Flatten for simpler queries:
{
  orderId: 1,
  items: [
    { productId: "p1", size: "M" }
  ]
}
```

### 5. Monitor Index Usage

```javascript
// Check if multikey index is being used
db.products.aggregate([{ $indexStats: {} }])

// Review query patterns
db.products.find({ tags: "sale" }).explain("executionStats")

// Look for:
// - "isMultiKey": true
// - Reasonable keysExamined vs docsReturned ratio
```

---

## Summary

### Multikey Index Features

| Feature | Description |
|---------|-------------|
| **Automatic** | Created when indexing array field |
| **Multiple Entries** | One entry per array element |
| **Embedded Support** | Index fields within array of objects |
| **Query Support** | Efficiently query array contents |

### Limitations

| Limitation | Description |
|------------|-------------|
| **Parallel Arrays** | Cannot compound two array fields |
| **Covered Queries** | Cannot cover queries |
| **Shard Key** | Cannot be shard key |
| **Index Size** | Larger than regular indexes |

### What's Next?

In the next chapter, we'll explore Text Indexes for full-text search.

---

## Practice Questions

1. How does MongoDB automatically create multikey indexes?
2. What happens when you update an array in a document with a multikey index?
3. Why can't you create a compound index on two array fields?
4. How does $elemMatch differ from querying individual array element fields?
5. Why can't multikey indexes cover queries?
6. What's the performance impact of large arrays on multikey indexes?
7. How do you index a field within an array of embedded documents?
8. When should you avoid multikey indexes?

---

## Hands-On Exercises

### Exercise 1: Basic Multikey Index

```javascript
// Setup
db.multikey_articles.drop()
db.multikey_articles.insertMany([
  {
    title: "MongoDB Tutorial",
    tags: ["mongodb", "database", "nosql", "tutorial"],
    author: "John"
  },
  {
    title: "Node.js Basics",
    tags: ["javascript", "nodejs", "backend", "tutorial"],
    author: "Jane"
  },
  {
    title: "React Guide",
    tags: ["javascript", "react", "frontend"],
    author: "Bob"
  },
  {
    title: "Full Stack Development",
    tags: ["javascript", "nodejs", "mongodb", "react"],
    author: "Alice"
  }
])

// Create multikey index
db.multikey_articles.createIndex({ tags: 1 })

// Test queries
print("Articles with 'javascript' tag:")
db.multikey_articles.find({ tags: "javascript" }).forEach(doc => print("  -", doc.title))

print("\nArticles with 'mongodb' OR 'react' tag:")
db.multikey_articles.find({ tags: { $in: ["mongodb", "react"] } })
  .forEach(doc => print("  -", doc.title))

print("\nArticles with BOTH 'javascript' AND 'tutorial' tags:")
db.multikey_articles.find({ tags: { $all: ["javascript", "tutorial"] } })
  .forEach(doc => print("  -", doc.title))

// Check index is multikey
const plan = db.multikey_articles.find({ tags: "javascript" }).explain()
print("\nIs Multikey:", plan.queryPlanner.winningPlan.inputStage.isMultiKey)
```

### Exercise 2: Array of Embedded Documents

```javascript
// Setup
db.multikey_products.drop()
db.multikey_products.insertMany([
  {
    name: "Laptop",
    reviews: [
      { user: "john", rating: 5, verified: true },
      { user: "jane", rating: 4, verified: true },
      { user: "guest1", rating: 3, verified: false }
    ]
  },
  {
    name: "Phone",
    reviews: [
      { user: "bob", rating: 5, verified: true },
      { user: "guest2", rating: 2, verified: false }
    ]
  },
  {
    name: "Tablet",
    reviews: [
      { user: "alice", rating: 4, verified: true }
    ]
  }
])

// Create multikey index on embedded fields
db.multikey_products.createIndex({ "reviews.rating": 1 })
db.multikey_products.createIndex({ "reviews.verified": 1 })

// Find products with any 5-star review
print("Products with 5-star reviews:")
db.multikey_products.find({ "reviews.rating": 5 })
  .forEach(doc => print("  -", doc.name))

// Find products with verified reviews rating 4+
print("\nProducts with verified 4+ star reviews:")
db.multikey_products.find({
  reviews: {
    $elemMatch: { rating: { $gte: 4 }, verified: true }
  }
}).forEach(doc => print("  -", doc.name))
```

### Exercise 3: Compound Multikey Index

```javascript
// Setup
db.multikey_orders.drop()
db.multikey_orders.insertMany([
  {
    customer: "cust-001",
    status: "completed",
    items: ["apple", "banana", "orange"]
  },
  {
    customer: "cust-001",
    status: "pending",
    items: ["grape", "apple"]
  },
  {
    customer: "cust-002",
    status: "completed",
    items: ["banana", "kiwi"]
  }
])

// Compound index: scalar + array
db.multikey_orders.createIndex({ customer: 1, items: 1 })

// Query using compound index
print("Customer cust-001 orders with apple:")
db.multikey_orders.find({ customer: "cust-001", items: "apple" })
  .forEach(doc => print("  - Status:", doc.status, "Items:", doc.items.join(", ")))

// Verify index usage
const plan = db.multikey_orders.find({ customer: "cust-001", items: "apple" })
  .explain()
print("\nIndex used:", plan.queryPlanner.winningPlan.inputStage.indexName)
```

### Exercise 4: Parallel Arrays (Demonstrating Limitation)

```javascript
// Setup
db.parallel_test.drop()
db.parallel_test.insertOne({
  arr1: [1, 2, 3],
  arr2: ["a", "b", "c"],
  scalar: "test"
})

// Try to create compound index on parallel arrays
try {
  db.parallel_test.createIndex({ arr1: 1, arr2: 1 })
  print("Index created successfully")
} catch (e) {
  print("Error (expected):", e.message)
}

// Valid: One array with scalar
db.parallel_test.createIndex({ arr1: 1, scalar: 1 })
print("\nIndex with one array + scalar: SUCCESS")

// Valid: Single array
db.parallel_test.createIndex({ arr2: 1 })
print("Index on single array: SUCCESS")

// Show indexes
print("\nCreated indexes:")
db.parallel_test.getIndexes().forEach(idx => {
  if (idx.name !== "_id_") {
    print("  -", idx.name, ":", JSON.stringify(idx.key))
  }
})
```

### Exercise 5: Performance Analysis

```javascript
// Setup with larger dataset
db.perf_products.drop()
const categories = ["electronics", "clothing", "home", "sports", "books"]
const tags = ["sale", "new", "featured", "clearance", "bestseller", "limited"]

for (let i = 0; i < 1000; i++) {
  const numTags = Math.floor(Math.random() * 5) + 1
  const productTags = []
  for (let j = 0; j < numTags; j++) {
    productTags.push(tags[Math.floor(Math.random() * tags.length)])
  }
  
  db.perf_products.insertOne({
    name: `Product ${i}`,
    category: categories[Math.floor(Math.random() * categories.length)],
    tags: [...new Set(productTags)]  // Unique tags
  })
}

// Without index
print("Query without index:")
let start = new Date()
db.perf_products.find({ tags: "sale" }).toArray()
print("  Time:", new Date() - start, "ms")

// Create multikey index
db.perf_products.createIndex({ tags: 1 })

// With index
print("\nQuery with multikey index:")
start = new Date()
db.perf_products.find({ tags: "sale" }).toArray()
print("  Time:", new Date() - start, "ms")

// Check index stats
const plan = db.perf_products.find({ tags: "sale" }).explain("executionStats")
print("\nIndex scan stats:")
print("  Keys examined:", plan.executionStats.totalKeysExamined)
print("  Docs examined:", plan.executionStats.totalDocsExamined)
print("  Docs returned:", plan.executionStats.nReturned)
```

---

[← Previous: Compound Indexes](18-compound-indexes.md) | [Next: Text Indexes →](20-text-indexes.md)
