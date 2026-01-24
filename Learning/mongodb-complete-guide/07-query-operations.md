# Chapter 7: Query Operations

## Table of Contents
- [Query Fundamentals](#query-fundamentals)
- [find() Method](#find-method)
- [Query Selectors](#query-selectors)
- [Comparison Operators](#comparison-operators)
- [Logical Operators](#logical-operators)
- [Element Operators](#element-operators)
- [Array Query Operators](#array-query-operators)
- [Query Projection](#query-projection)
- [Cursor Methods](#cursor-methods)
- [Summary](#summary)

---

## Query Fundamentals

### Query Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MongoDB Query Flow                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client Query                                                        │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Query Parser                                                 │   │
│  │ • Parse query document                                      │   │
│  │ • Validate operators                                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Query Planner                                                │   │
│  │ • Analyze available indexes                                 │   │
│  │ • Generate candidate plans                                  │   │
│  │ • Select optimal plan                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ Query Executor                                               │   │
│  │ • Execute chosen plan                                       │   │
│  │ • Fetch matching documents                                  │   │
│  │ • Apply projection                                          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  Cursor (Results)                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic Query Syntax

```javascript
db.collection.find(
  { query },      // Filter criteria
  { projection }  // Fields to include/exclude
)
```

---

## find() Method

### Finding All Documents

```javascript
// Find all documents in a collection
db.users.find()

// Find all with pretty formatting
db.users.find().pretty()

// Equivalent to SQL: SELECT * FROM users
```

### Finding with Criteria

```javascript
// Find documents where field equals value
db.users.find({ name: "John" })

// Multiple conditions (AND)
db.users.find({ 
  status: "active",
  age: 30 
})

// Equivalent to SQL: SELECT * FROM users WHERE status = 'active' AND age = 30
```

### findOne()

```javascript
// Return single document (or null)
db.users.findOne({ email: "john@example.com" })

// Returns the first matching document
// Useful when you expect only one result

// With projection
db.users.findOne(
  { email: "john@example.com" },
  { name: 1, email: 1, _id: 0 }
)
```

### Sample Data for Examples

```javascript
// Insert sample data
db.products.insertMany([
  { name: "Laptop", price: 999, category: "Electronics", stock: 50, tags: ["computer", "portable"], ratings: [4, 5, 4, 3, 5] },
  { name: "Phone", price: 599, category: "Electronics", stock: 100, tags: ["mobile", "portable"], ratings: [5, 4, 5, 5] },
  { name: "Tablet", price: 399, category: "Electronics", stock: 30, tags: ["computer", "portable", "touchscreen"], ratings: [4, 4, 3] },
  { name: "Headphones", price: 149, category: "Electronics", stock: 200, tags: ["audio", "portable"], ratings: [5, 5, 4, 5, 5] },
  { name: "Book", price: 29, category: "Books", stock: 500, tags: ["reading", "education"], ratings: [4, 3, 4] },
  { name: "Desk", price: 299, category: "Furniture", stock: 20, tags: ["office", "wood"], ratings: [4, 4, 5] },
  { name: "Chair", price: 199, category: "Furniture", stock: 0, tags: ["office", "ergonomic"], ratings: [3, 4, 3, 2] },
  { name: "Monitor", price: 449, category: "Electronics", stock: 45, tags: ["computer", "display"], ratings: [5, 4, 5] }
])
```

---

## Query Selectors

### Exact Match

```javascript
// String match
db.products.find({ name: "Laptop" })

// Number match
db.products.find({ price: 999 })

// Boolean match
db.users.find({ isActive: true })

// Null match (matches null or missing field)
db.products.find({ discount: null })
```

### Nested Document Match

```javascript
// Sample document with nested data
db.users.insertOne({
  name: "John",
  address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001"
  }
})

// Match exact embedded document (order matters!)
db.users.find({
  address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001"
  }
})

// Match specific nested field (preferred)
db.users.find({ "address.city": "New York" })

// Multiple nested conditions
db.users.find({
  "address.city": "New York",
  "address.state": "NY"
})
```

### Array Match

```javascript
// Match entire array (exact, order matters)
db.products.find({ tags: ["computer", "portable"] })

// Match if array contains element
db.products.find({ tags: "portable" })

// Match multiple array elements (all must exist)
db.products.find({ tags: { $all: ["portable", "computer"] } })
```

---

## Comparison Operators

### Operator Reference

| Operator | Description |
|----------|-------------|
| `$eq` | Equal to |
| `$ne` | Not equal to |
| `$gt` | Greater than |
| `$gte` | Greater than or equal |
| `$lt` | Less than |
| `$lte` | Less than or equal |
| `$in` | Match any value in array |
| `$nin` | Not match any value in array |

### $eq (Equal)

```javascript
// Explicit equality
db.products.find({ price: { $eq: 999 } })

// Same as
db.products.find({ price: 999 })

// With nested fields
db.users.find({ "address.city": { $eq: "New York" } })
```

### $ne (Not Equal)

```javascript
// Find products not in Electronics category
db.products.find({ category: { $ne: "Electronics" } })

// Find users without admin role
db.users.find({ role: { $ne: "admin" } })
```

### $gt, $gte, $lt, $lte (Range)

```javascript
// Greater than
db.products.find({ price: { $gt: 500 } })

// Greater than or equal
db.products.find({ price: { $gte: 500 } })

// Less than
db.products.find({ stock: { $lt: 50 } })

// Less than or equal
db.products.find({ stock: { $lte: 50 } })

// Range query (between)
db.products.find({
  price: { $gte: 100, $lte: 500 }
})
// SQL: WHERE price >= 100 AND price <= 500

// Date range
db.orders.find({
  orderDate: {
    $gte: ISODate("2024-01-01"),
    $lt: ISODate("2024-02-01")
  }
})
```

### $in (Match Any)

```javascript
// Match any value in list
db.products.find({
  category: { $in: ["Electronics", "Books"] }
})
// SQL: WHERE category IN ('Electronics', 'Books')

// With ObjectIds
db.orders.find({
  productId: { $in: [
    ObjectId("..."),
    ObjectId("..."),
    ObjectId("...")
  ]}
})

// With strings
db.users.find({
  status: { $in: ["active", "pending"] }
})
```

### $nin (Not In)

```javascript
// Not match any value in list
db.products.find({
  category: { $nin: ["Electronics", "Books"] }
})
// SQL: WHERE category NOT IN ('Electronics', 'Books')
```

---

## Logical Operators

### Operator Reference

| Operator | Description |
|----------|-------------|
| `$and` | Logical AND |
| `$or` | Logical OR |
| `$not` | Negates expression |
| `$nor` | Fails all conditions |

### $and (Logical AND)

```javascript
// Implicit AND (multiple conditions)
db.products.find({
  category: "Electronics",
  price: { $lt: 500 }
})

// Explicit $and
db.products.find({
  $and: [
    { category: "Electronics" },
    { price: { $lt: 500 } }
  ]
})

// Required when same field appears multiple times
db.products.find({
  $and: [
    { price: { $gt: 100 } },
    { price: { $lt: 500 } }
  ]
})

// Or combine in single object
db.products.find({
  price: { $gt: 100, $lt: 500 }
})
```

### $or (Logical OR)

```javascript
// Match any condition
db.products.find({
  $or: [
    { category: "Electronics" },
    { price: { $lt: 50 } }
  ]
})
// SQL: WHERE category = 'Electronics' OR price < 50

// Complex OR with AND
db.products.find({
  $or: [
    { category: "Electronics", price: { $lt: 500 } },
    { category: "Books" }
  ]
})
```

### $not (Negation)

```javascript
// Negate a condition
db.products.find({
  price: { $not: { $gt: 500 } }
})
// Matches: price <= 500 OR price does not exist

// With regex
db.products.find({
  name: { $not: /^Phone/ }
})
```

### $nor (Not OR)

```javascript
// Fail all conditions
db.products.find({
  $nor: [
    { category: "Electronics" },
    { price: { $gt: 500 } }
  ]
})
// Matches documents that are NOT Electronics AND price NOT > 500
```

### Complex Logical Combinations

```javascript
// (category = 'Electronics' AND price < 500) OR (category = 'Books' AND stock > 100)
db.products.find({
  $or: [
    {
      $and: [
        { category: "Electronics" },
        { price: { $lt: 500 } }
      ]
    },
    {
      $and: [
        { category: "Books" },
        { stock: { $gt: 100 } }
      ]
    }
  ]
})

// Simplified version
db.products.find({
  $or: [
    { category: "Electronics", price: { $lt: 500 } },
    { category: "Books", stock: { $gt: 100 } }
  ]
})
```

---

## Element Operators

### $exists

```javascript
// Field exists
db.products.find({ discount: { $exists: true } })

// Field does not exist
db.products.find({ discount: { $exists: false } })

// Field exists and is not null
db.products.find({
  discount: { $exists: true, $ne: null }
})
```

### $type

```javascript
// Match by BSON type
db.collection.find({ field: { $type: "string" } })
db.collection.find({ field: { $type: 2 } })  // Type number for string

// Multiple types
db.collection.find({
  field: { $type: ["string", "null"] }
})

// Common type values:
// "double" (1), "string" (2), "object" (3), "array" (4)
// "binData" (5), "objectId" (7), "bool" (8), "date" (9)
// "null" (10), "int" (16), "long" (18), "decimal" (19)

// Find documents where age is a number
db.users.find({
  age: { $type: "number" }  // Matches int, long, double, decimal
})
```

---

## Array Query Operators

### $all (Match All Elements)

```javascript
// Array must contain all specified elements
db.products.find({
  tags: { $all: ["portable", "computer"] }
})

// Order doesn't matter, extra elements allowed
// Matches: ["computer", "portable", "touchscreen"]
```

### $elemMatch (Match Array Element)

```javascript
// Sample data with array of objects
db.orders.insertOne({
  orderId: "ORD001",
  items: [
    { product: "Laptop", quantity: 1, price: 999 },
    { product: "Mouse", quantity: 2, price: 29 }
  ]
})

// Match document where at least one array element matches ALL criteria
db.orders.find({
  items: {
    $elemMatch: {
      product: "Laptop",
      quantity: { $gte: 1 }
    }
  }
})

// Without $elemMatch (matches if ANY element matches each condition)
db.orders.find({
  "items.product": "Laptop",
  "items.quantity": { $gte: 1 }
})
// This could match different elements!
```

```
┌─────────────────────────────────────────────────────────────────────┐
│              $elemMatch vs Dot Notation Queries                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Document:                                                          │
│  { items: [                                                        │
│    { name: "A", qty: 5, price: 10 },                              │
│    { name: "B", qty: 2, price: 50 }                               │
│  ]}                                                                 │
│                                                                     │
│  Query: name = "A" AND qty > 3                                     │
│                                                                     │
│  Using dot notation:                                                │
│  { "items.name": "A", "items.qty": { $gt: 3 } }                   │
│  ✓ Matches - name: "A" exists AND qty > 3 exists (different items) │
│                                                                     │
│  Using $elemMatch:                                                  │
│  { items: { $elemMatch: { name: "A", qty: { $gt: 3 } } } }        │
│  ✓ Matches - same item has name: "A" AND qty > 3                   │
│                                                                     │
│  Key difference: $elemMatch ensures same array element matches all  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### $size (Array Length)

```javascript
// Match exact array size
db.products.find({ tags: { $size: 2 } })

// Note: $size doesn't accept ranges
// For range queries, use aggregation or add a size field

// Workaround for size > N using $exists
db.products.find({ "tags.3": { $exists: true } })  // Size >= 4
```

### Array Index Queries

```javascript
// Query specific array index
db.products.find({ "tags.0": "computer" })  // First element

db.products.find({ "ratings.0": { $gte: 4 } })  // First rating >= 4

// Query nested array objects by index
db.orders.find({ "items.0.product": "Laptop" })
```

---

## Query Projection

### Basic Projection

```javascript
// Include specific fields (plus _id by default)
db.products.find(
  { category: "Electronics" },
  { name: 1, price: 1 }
)
// Returns: { _id: ..., name: ..., price: ... }

// Exclude _id
db.products.find(
  { category: "Electronics" },
  { name: 1, price: 1, _id: 0 }
)
// Returns: { name: ..., price: ... }

// Exclude specific fields
db.products.find(
  { category: "Electronics" },
  { ratings: 0, tags: 0 }
)
// Returns all fields except ratings and tags
```

### Projection Rules

```javascript
// Cannot mix inclusion and exclusion (except _id)

// ❌ Invalid
db.products.find({}, { name: 1, ratings: 0 })

// ✓ Valid - _id is special
db.products.find({}, { name: 1, price: 1, _id: 0 })

// ✓ Valid - all exclusion
db.products.find({}, { ratings: 0, tags: 0 })
```

### Array Projection Operators

```javascript
// $slice - limit array elements
db.products.find(
  { name: "Laptop" },
  { ratings: { $slice: 3 } }     // First 3 elements
)

db.products.find(
  { name: "Laptop" },
  { ratings: { $slice: -2 } }    // Last 2 elements
)

db.products.find(
  { name: "Laptop" },
  { ratings: { $slice: [1, 2] } } // Skip 1, take 2
)

// $ - first matched array element
db.products.find(
  { tags: "portable" },
  { "tags.$": 1 }  // Only the matched element
)

// $elemMatch in projection
db.orders.find(
  { orderId: "ORD001" },
  {
    items: {
      $elemMatch: { price: { $gt: 50 } }
    }
  }
)
```

### Projection with Expressions (MongoDB 4.4+)

```javascript
// Using aggregation expressions in projection
db.products.find(
  { category: "Electronics" },
  {
    name: 1,
    price: 1,
    inStock: { $gt: ["$stock", 0] },
    discountedPrice: { $multiply: ["$price", 0.9] }
  }
)
```

---

## Cursor Methods

### Common Cursor Methods

```javascript
// sort() - order results
db.products.find().sort({ price: 1 })   // Ascending
db.products.find().sort({ price: -1 })  // Descending

// Multiple sort fields
db.products.find().sort({ category: 1, price: -1 })

// limit() - restrict number of results
db.products.find().limit(5)

// skip() - skip documents (pagination)
db.products.find().skip(10).limit(5)  // Page 3, 5 per page

// count() / countDocuments()
db.products.countDocuments({ category: "Electronics" })

// distinct()
db.products.distinct("category")
// Returns: ["Electronics", "Books", "Furniture"]

// Method chaining
db.products
  .find({ category: "Electronics" })
  .sort({ price: -1 })
  .skip(0)
  .limit(10)
```

### Cursor Iteration

```javascript
// Iterate with forEach
db.products.find().forEach(doc => {
  print(doc.name + ": $" + doc.price)
})

// Convert to array
const results = db.products.find().toArray()

// Check if more results
const cursor = db.products.find()
while (cursor.hasNext()) {
  printjson(cursor.next())
}

// Get explanation
db.products.find({ category: "Electronics" }).explain("executionStats")
```

### Pagination Pattern

```javascript
// Offset-based pagination
function getPage(collection, query, page, pageSize) {
  const skip = (page - 1) * pageSize
  return collection.find(query)
    .sort({ _id: 1 })
    .skip(skip)
    .limit(pageSize)
    .toArray()
}

// Usage
const page1 = getPage(db.products, {}, 1, 10)
const page2 = getPage(db.products, {}, 2, 10)

// Cursor-based pagination (more efficient for large datasets)
function getNextPage(collection, lastId, pageSize) {
  const query = lastId ? { _id: { $gt: lastId } } : {}
  return collection.find(query)
    .sort({ _id: 1 })
    .limit(pageSize)
    .toArray()
}

// Usage
const firstPage = getNextPage(db.products, null, 10)
const lastId = firstPage[firstPage.length - 1]._id
const secondPage = getNextPage(db.products, lastId, 10)
```

---

## Evaluation Operators

### $regex (Regular Expression)

```javascript
// Case-sensitive match
db.products.find({ name: { $regex: "phone" } })

// Case-insensitive match
db.products.find({ name: { $regex: /phone/i } })
db.products.find({ name: { $regex: "phone", $options: "i" } })

// Starts with
db.products.find({ name: { $regex: "^Lap" } })

// Ends with
db.products.find({ name: { $regex: "top$" } })

// Contains
db.products.find({ name: { $regex: "apt" } })

// Multiple patterns
db.products.find({
  $or: [
    { name: { $regex: /laptop/i } },
    { name: { $regex: /phone/i } }
  ]
})
```

### $expr (Expression)

```javascript
// Compare two fields
db.products.find({
  $expr: { $gt: ["$stock", "$reorderLevel"] }
})

// Use aggregation operators
db.products.find({
  $expr: {
    $and: [
      { $gte: ["$price", 100] },
      { $lte: ["$price", 500] }
    ]
  }
})

// String comparison
db.users.find({
  $expr: { $eq: ["$firstName", "$username"] }
})
```

### $text (Text Search)

```javascript
// First, create text index
db.products.createIndex({ name: "text", description: "text" })

// Text search
db.products.find({ $text: { $search: "laptop computer" } })

// Phrase search
db.products.find({ $text: { $search: "\"gaming laptop\"" } })

// Exclude words
db.products.find({ $text: { $search: "laptop -gaming" } })

// With text score
db.products.find(
  { $text: { $search: "laptop" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })
```

### $where (JavaScript Expression)

```javascript
// Use JavaScript (slower, use sparingly)
db.products.find({
  $where: function() {
    return this.price > 100 && this.stock > 0
  }
})

// String form
db.products.find({
  $where: "this.price > 100 && this.stock > 0"
})

// Note: $where doesn't use indexes, prefer $expr when possible
```

---

## Summary

### Query Operators Reference

| Category | Operators |
|----------|-----------|
| **Comparison** | $eq, $ne, $gt, $gte, $lt, $lte, $in, $nin |
| **Logical** | $and, $or, $not, $nor |
| **Element** | $exists, $type |
| **Array** | $all, $elemMatch, $size |
| **Evaluation** | $regex, $expr, $text, $where |

### Query Performance Tips

1. **Use indexes** for frequently queried fields
2. **Prefer $in over $or** for same field queries
3. **Limit projection** to needed fields
4. **Use cursor methods** for pagination
5. **Avoid $where** when possible (no index support)

### What's Next?

In the next chapter, we'll explore Update Operations, learning how to modify documents in MongoDB.

---

## Practice Questions

1. What's the difference between find() and findOne()?
2. When would you use $elemMatch vs dot notation for array queries?
3. How do you perform a case-insensitive search in MongoDB?
4. What's the difference between $and and implicit AND?
5. How do you query for documents where a field doesn't exist?
6. What are the limitations of the $size operator?
7. How does projection work with inclusion vs exclusion?
8. What's the difference between offset-based and cursor-based pagination?

---

## Hands-On Exercises

### Exercise 1: Basic Queries

```javascript
// Using the products collection from earlier examples

// 1. Find all electronics
db.products.find({ category: "Electronics" })

// 2. Find products under $200
db.products.find({ price: { $lt: 200 } })

// 3. Find products with stock between 20 and 100
db.products.find({
  stock: { $gte: 20, $lte: 100 }
})

// 4. Find products in Electronics or Books
db.products.find({
  category: { $in: ["Electronics", "Books"] }
})
```

### Exercise 2: Complex Queries

```javascript
// 1. Electronics priced 100-500 OR Books with stock > 100
db.products.find({
  $or: [
    { category: "Electronics", price: { $gte: 100, $lte: 500 } },
    { category: "Books", stock: { $gt: 100 } }
  ]
})

// 2. Products with "portable" tag that are NOT Electronics
db.products.find({
  tags: "portable",
  category: { $ne: "Electronics" }
})

// 3. Products with at least 4 ratings, all >= 4
db.products.find({
  ratings: { $not: { $elemMatch: { $lt: 4 } } },
  "ratings.3": { $exists: true }
})
```

### Exercise 3: Array Queries

```javascript
// Insert sample orders
db.orders.insertMany([
  {
    orderId: "ORD001",
    customer: "Alice",
    items: [
      { product: "Laptop", qty: 1, price: 999 },
      { product: "Mouse", qty: 2, price: 25 }
    ],
    total: 1049
  },
  {
    orderId: "ORD002",
    customer: "Bob",
    items: [
      { product: "Phone", qty: 1, price: 599 },
      { product: "Case", qty: 3, price: 15 }
    ],
    total: 644
  }
])

// 1. Find orders containing Laptop
db.orders.find({ "items.product": "Laptop" })

// 2. Find orders with item quantity > 1 AND price > 20
db.orders.find({
  items: { $elemMatch: { qty: { $gt: 1 }, price: { $gt: 20 } } }
})

// 3. Find orders with exactly 2 items
db.orders.find({ items: { $size: 2 } })
```

### Exercise 4: Projection and Cursors

```javascript
// 1. Return only name and price, sorted by price descending
db.products.find({}, { name: 1, price: 1, _id: 0 }).sort({ price: -1 })

// 2. Get top 3 most expensive products
db.products.find().sort({ price: -1 }).limit(3)

// 3. Paginate: page 2, 3 items per page, sorted by name
db.products.find()
  .sort({ name: 1 })
  .skip(3)
  .limit(3)

// 4. Get first 2 ratings for each product
db.products.find({}, { name: 1, ratings: { $slice: 2 } })
```

---

[← Previous: Insert Operations](06-insert-operations.md) | [Next: Update Operations →](08-update-operations.md)
