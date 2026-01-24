# Chapter 17: Single Field Indexes

## Table of Contents
- [Introduction to Single Field Indexes](#introduction-to-single-field-indexes)
- [Creating Single Field Indexes](#creating-single-field-indexes)
- [Sort Order](#sort-order)
- [Indexing Embedded Documents](#indexing-embedded-documents)
- [Index on Array Fields](#index-on-array-fields)
- [Null Values in Indexes](#null-values-in-indexes)
- [Single Field Index Strategies](#single-field-index-strategies)
- [Performance Considerations](#performance-considerations)
- [Summary](#summary)

---

## Introduction to Single Field Indexes

A single field index is the simplest index type, created on one field of a document.

### When to Use Single Field Indexes

```
┌─────────────────────────────────────────────────────────────────────┐
│              Single Field Index Use Cases                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ✓ Good Use Cases:                                                 │
│  • Unique identifiers (email, username, sku)                       │
│  • Frequently queried fields                                       │
│  • Sort operations on single field                                 │
│  • Simple equality queries                                         │
│                                                                     │
│  ✗ Consider Compound Index Instead:                                │
│  • Queries always filter on multiple fields                        │
│  • Need covered queries with multiple fields                       │
│  • Sort combined with filter on different field                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Creating Single Field Indexes

### Basic Creation

```javascript
// Ascending index
db.users.createIndex({ email: 1 })

// Descending index
db.users.createIndex({ createdAt: -1 })

// With custom name
db.users.createIndex(
  { email: 1 },
  { name: "email_idx" }
)

// View all indexes
db.users.getIndexes()
/*
[
  { "v": 2, "key": { "_id": 1 }, "name": "_id_" },
  { "v": 2, "key": { "email": 1 }, "name": "email_idx" }
]
*/
```

### Index Options

```javascript
// Unique index
db.users.createIndex(
  { email: 1 },
  { unique: true }
)

// Sparse index (only index documents with field)
db.users.createIndex(
  { phone: 1 },
  { sparse: true }
)

// Partial index (filter condition)
db.users.createIndex(
  { lastLogin: 1 },
  {
    partialFilterExpression: {
      status: "active"
    }
  }
)

// TTL index (auto-expire)
db.sessions.createIndex(
  { expiresAt: 1 },
  { expireAfterSeconds: 0 }  // Expire at expiresAt time
)

// Background (pre-4.2)
db.users.createIndex(
  { field: 1 },
  { background: true }
)
```

---

## Sort Order

For single field indexes, sort order doesn't matter for the index itself, but impacts range queries.

### Sort Direction

```javascript
// Create index
db.products.createIndex({ price: 1 })

// Both queries use the index
db.products.find().sort({ price: 1 })   // Ascending - forward scan
db.products.find().sort({ price: -1 })  // Descending - backward scan

// Range query direction
db.products.find({ price: { $gt: 100 } }).sort({ price: 1 })   // Efficient
db.products.find({ price: { $gt: 100 } }).sort({ price: -1 })  // Also uses index
```

### explain() for Sort

```javascript
// Check sort uses index
const plan = db.products.find().sort({ price: 1 }).explain()

// Good: Index provides sort
{
  "stage": "FETCH",
  "inputStage": {
    "stage": "IXSCAN",
    "direction": "forward"
  }
}

// Bad: In-memory sort
{
  "stage": "SORT",
  "inputStage": {
    "stage": "COLLSCAN"
  }
}
```

---

## Indexing Embedded Documents

### Index on Embedded Field

```javascript
// Document structure
{
  _id: 1,
  name: "John",
  address: {
    city: "New York",
    zipCode: "10001",
    country: "USA"
  }
}

// Index on embedded field using dot notation
db.users.createIndex({ "address.city": 1 })

// Query uses index
db.users.find({ "address.city": "New York" })

// Multiple embedded field indexes
db.users.createIndex({ "address.zipCode": 1 })
db.users.createIndex({ "address.country": 1 })
```

### Index on Entire Embedded Document

```javascript
// Index on entire subdocument
db.users.createIndex({ address: 1 })

// Query must match ENTIRE subdocument EXACTLY
db.users.find({
  address: {
    city: "New York",
    zipCode: "10001",
    country: "USA"
  }
})  // Uses index

// This does NOT use the subdocument index
db.users.find({ "address.city": "New York" })

// Field order matters for subdocument match
db.users.find({
  address: {
    country: "USA",  // Different order
    city: "New York",
    zipCode: "10001"
  }
})  // Does NOT match!
```

### Best Practice: Use Dot Notation

```javascript
// Recommended: Index specific fields
db.users.createIndex({ "address.city": 1 })
db.users.createIndex({ "address.country": 1 })

// More flexible queries
db.users.find({ "address.city": "New York" })
db.users.find({ "address.country": "USA" })
db.users.find({ 
  "address.city": "New York",
  "address.country": "USA"
})
```

---

## Index on Array Fields

Single field indexes on arrays create multikey indexes.

### Multikey Index Basics

```javascript
// Document with array
{
  _id: 1,
  name: "Product A",
  tags: ["electronics", "sale", "featured"]
}

// Create index on array field
db.products.createIndex({ tags: 1 })
// Automatically becomes multikey index

// Index entry created for EACH array element
// Conceptually:
// "electronics" -> document 1
// "sale" -> document 1
// "featured" -> document 1

// Query any element
db.products.find({ tags: "sale" })  // Uses index
```

### Array of Embedded Documents

```javascript
// Document structure
{
  _id: 1,
  name: "Book",
  reviews: [
    { user: "john", rating: 5, text: "Great!" },
    { user: "jane", rating: 4, text: "Good" }
  ]
}

// Index on embedded field within array
db.products.createIndex({ "reviews.rating": 1 })

// Queries that use index
db.products.find({ "reviews.rating": 5 })
db.products.find({ "reviews.rating": { $gte: 4 } })
```

### Multikey Index Limitations

```javascript
// Cannot have multiple multikey fields in compound index
db.collection.insertOne({
  tags: ["a", "b"],
  categories: ["x", "y"]
})

// This fails if both are arrays
db.collection.createIndex({ tags: 1, categories: 1 })
// Error: cannot index parallel arrays

// OK if only one field is array
db.collection.createIndex({ tags: 1, name: 1 })  // Works
```

---

## Null Values in Indexes

### Null Handling

```javascript
// Documents
db.users.insertMany([
  { name: "John", email: "john@example.com" },
  { name: "Jane", email: null },
  { name: "Bob" }  // No email field
])

// Index on email
db.users.createIndex({ email: 1 })

// Query for null
db.users.find({ email: null })
// Returns both: { email: null } AND { email: { $exists: false } }

// Query for existing null
db.users.find({ email: { $type: "null" } })
// Only returns { email: null }
```

### Unique Index with Nulls

```javascript
// Problem: Unique index allows only one null
db.users.createIndex({ email: 1 }, { unique: true })

db.users.insertOne({ name: "User1" })  // OK (null email)
db.users.insertOne({ name: "User2" })  // Error! Duplicate null

// Solution: Partial unique index
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: {
      email: { $exists: true }
    }
  }
)

// Now multiple documents without email are allowed
db.users.insertOne({ name: "User1" })  // OK
db.users.insertOne({ name: "User2" })  // OK
db.users.insertOne({ email: "test@example.com" })  // OK
db.users.insertOne({ email: "test@example.com" })  // Error! Duplicate
```

### Sparse Index for Null Handling

```javascript
// Sparse index excludes documents without the field
db.users.createIndex(
  { email: 1 },
  { sparse: true }
)

// Only documents WITH email field are indexed
// Note: email: null IS indexed, only missing field is excluded

// Comparison with partial
db.users.createIndex(
  { email: 1 },
  {
    partialFilterExpression: {
      email: { $exists: true, $ne: null }
    }
  }
)
// Excludes both missing field AND null values
```

---

## Single Field Index Strategies

### Strategy 1: High Cardinality Fields

```javascript
// Good: High cardinality (many unique values)
db.users.createIndex({ email: 1 })    // Unique per user
db.users.createIndex({ phone: 1 })    // Unique per user

// Poor: Low cardinality (few unique values)
db.users.createIndex({ status: 1 })   // Only: active, inactive, pending
db.users.createIndex({ gender: 1 })   // Only: M, F, Other

// Low cardinality indexes scan many documents
db.users.find({ status: "active" })   // 80% of documents match
```

### Strategy 2: Selective Queries

```javascript
// Index for selective queries (few results)
db.orders.createIndex({ orderNumber: 1 })  // Returns 1 document

// Combined with filter for less selective
db.orders.createIndex(
  { createdAt: 1 },
  {
    partialFilterExpression: {
      status: { $in: ["pending", "processing"] }
    }
  }
)
```

### Strategy 3: Write vs Read Trade-off

```javascript
// Each index adds write overhead
// Insert: Must update ALL indexes
// Update: Must update AFFECTED indexes
// Delete: Must update ALL indexes

// Monitor index usage
db.collection.aggregate([
  { $indexStats: {} }
])
/*
[
  {
    "name": "email_1",
    "accesses": {
      "ops": 15234,
      "since": ISODate("...")
    }
  }
]
*/

// Remove unused indexes
db.collection.dropIndex("unused_index_name")
```

---

## Performance Considerations

### Index Size

```javascript
// Check index size
db.collection.stats().indexSizes
/*
{
  "_id_": 2031616,
  "email_1": 1523712,
  "name_1": 1234567
}
*/

// Larger field values = larger index
// String indexes larger than numeric
// Consider field size when indexing
```

### Index Selectivity

```javascript
// Selectivity = unique values / total documents
// Higher is better

// High selectivity (good)
db.users.createIndex({ email: 1 })  // ~1.0 selectivity

// Low selectivity (poor)
db.users.createIndex({ country: 1 })  // ~0.001 if 1000 countries, 1M users

// Check cardinality
db.users.distinct("country").length  // Number of unique values
db.users.countDocuments()  // Total documents
```

### Monitoring Index Usage

```javascript
// Index statistics
db.collection.aggregate([{ $indexStats: {} }])

// Profile slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Check system.profile
db.system.profile.find({ millis: { $gt: 100 } })
  .sort({ ts: -1 })
  .limit(10)
```

### Index Intersection

```javascript
// MongoDB can combine single field indexes
db.products.createIndex({ category: 1 })
db.products.createIndex({ price: 1 })

// Query might use both indexes
db.products.find({
  category: "Electronics",
  price: { $lt: 100 }
}).explain()

// Usually compound index is more efficient
db.products.createIndex({ category: 1, price: 1 })
```

---

## Summary

### Single Field Index Features

| Feature | Description |
|---------|-------------|
| **Basic** | Index on one field |
| **Multikey** | Automatic for arrays |
| **Embedded** | Dot notation for nested fields |
| **Direction** | 1 (ascending) or -1 (descending) |

### Index Options

| Option | Description |
|--------|-------------|
| **unique** | Enforce uniqueness |
| **sparse** | Exclude missing fields |
| **partial** | Filter indexed documents |
| **TTL** | Auto-expire documents |

### What's Next?

In the next chapter, we'll explore Compound Indexes for multi-field queries.

---

## Practice Questions

1. When would you index an entire embedded document vs a field within it?
2. What is a multikey index and when is it created?
3. How do sparse and partial indexes differ?
4. Why does index selectivity matter?
5. How do you handle unique indexes when some documents lack the field?
6. What's the overhead of adding an index?
7. How can you monitor index usage?
8. When would index intersection occur?

---

## Hands-On Exercises

### Exercise 1: Basic Single Field Index

```javascript
// Setup
db.idx_products.drop()
db.idx_products.insertMany([
  { sku: "PRD001", name: "Widget", price: 29.99, category: "Tools" },
  { sku: "PRD002", name: "Gadget", price: 49.99, category: "Electronics" },
  { sku: "PRD003", name: "Gizmo", price: 19.99, category: "Tools" },
  { sku: "PRD004", name: "Thingamajig", price: 99.99, category: "Electronics" }
])

// Create unique index on SKU
db.idx_products.createIndex({ sku: 1 }, { unique: true })

// Verify
db.idx_products.getIndexes()

// Test uniqueness
try {
  db.idx_products.insertOne({ sku: "PRD001", name: "Duplicate" })
} catch (e) {
  print("Correctly rejected duplicate:", e.message)
}

// Query using index
db.idx_products.find({ sku: "PRD002" }).explain("executionStats")
```

### Exercise 2: Embedded Field Index

```javascript
// Setup
db.idx_users.drop()
db.idx_users.insertMany([
  {
    name: "John",
    address: { city: "New York", state: "NY", zip: "10001" }
  },
  {
    name: "Jane",
    address: { city: "Los Angeles", state: "CA", zip: "90001" }
  },
  {
    name: "Bob",
    address: { city: "New York", state: "NY", zip: "10002" }
  }
])

// Index on embedded field
db.idx_users.createIndex({ "address.city": 1 })

// Query using embedded field index
const plan = db.idx_users.find({ "address.city": "New York" })
  .explain("executionStats")

print("Index used:", plan.queryPlanner.winningPlan.inputStage.indexName)
print("Docs returned:", plan.executionStats.nReturned)
```

### Exercise 3: Multikey Index

```javascript
// Setup
db.idx_articles.drop()
db.idx_articles.insertMany([
  {
    title: "MongoDB Basics",
    tags: ["mongodb", "database", "nosql", "tutorial"]
  },
  {
    title: "Advanced Queries",
    tags: ["mongodb", "queries", "aggregation"]
  },
  {
    title: "Indexing Guide",
    tags: ["mongodb", "performance", "indexing"]
  }
])

// Create index on array field
db.idx_articles.createIndex({ tags: 1 })

// Query single tag
print("Articles with 'mongodb' tag:")
db.idx_articles.find({ tags: "mongodb" }).forEach(doc => print("  -", doc.title))

// Query with $in
print("\nArticles with 'performance' or 'tutorial':")
db.idx_articles.find({ tags: { $in: ["performance", "tutorial"] } })
  .forEach(doc => print("  -", doc.title))

// Verify index is multikey
const stats = db.idx_articles.aggregate([{ $indexStats: {} }]).toArray()
print("\nIndex stats:", JSON.stringify(stats.find(s => s.name === "tags_1"), null, 2))
```

### Exercise 4: Partial Unique Index

```javascript
// Setup
db.idx_accounts.drop()

// Create partial unique index
db.idx_accounts.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: {
      email: { $exists: true, $ne: null }
    }
  }
)

// Insert documents without email (should all succeed)
db.idx_accounts.insertOne({ name: "Guest1" })
db.idx_accounts.insertOne({ name: "Guest2" })
db.idx_accounts.insertOne({ name: "Guest3", email: null })

print("Documents without valid email:", db.idx_accounts.countDocuments({
  $or: [
    { email: { $exists: false } },
    { email: null }
  ]
}))

// Insert documents with email
db.idx_accounts.insertOne({ name: "User1", email: "user1@example.com" })

// Try duplicate email
try {
  db.idx_accounts.insertOne({ name: "User2", email: "user1@example.com" })
} catch (e) {
  print("\nCorrectly rejected duplicate email")
}

// Different email succeeds
db.idx_accounts.insertOne({ name: "User2", email: "user2@example.com" })
print("Total documents:", db.idx_accounts.countDocuments())
```

---

[← Previous: Index Fundamentals](16-index-fundamentals.md) | [Next: Compound Indexes →](18-compound-indexes.md)
