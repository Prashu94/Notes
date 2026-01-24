# Chapter 11: Data Modeling Concepts

## Table of Contents
- [Data Modeling Overview](#data-modeling-overview)
- [Document Model vs Relational Model](#document-model-vs-relational-model)
- [Embedding vs Referencing](#embedding-vs-referencing)
- [Schema Design Patterns](#schema-design-patterns)
- [One-to-One Relationships](#one-to-one-relationships)
- [One-to-Many Relationships](#one-to-many-relationships)
- [Many-to-Many Relationships](#many-to-many-relationships)
- [Schema Design Best Practices](#schema-design-best-practices)
- [Summary](#summary)

---

## Data Modeling Overview

Data modeling in MongoDB involves designing document structures that efficiently support your application's queries and updates while maintaining data integrity.

### Key Principles

```
┌─────────────────────────────────────────────────────────────────────┐
│                 MongoDB Data Modeling Principles                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Model for your application's data access patterns              │
│  2. Pre-join data by embedding (denormalization)                   │
│  3. Consider document size limits (16MB max)                       │
│  4. Balance read and write performance                             │
│  5. Plan for growth and scalability                                │
│                                                                     │
│  Questions to ask:                                                 │
│  • How will data be queried?                                       │
│  • What is the read/write ratio?                                   │
│  • How will data grow over time?                                   │
│  • What relationships exist between entities?                      │
│  • What are the consistency requirements?                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Modeling Workflow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Understand    │────►│     Design      │────►│    Optimize     │
│   Requirements  │     │     Schema      │     │    & Iterate    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
       │                        │                        │
       ▼                        ▼                        ▼
  • Use cases              • Entities              • Index strategy
  • Query patterns         • Relationships         • Performance test
  • Data volumes           • Embed vs reference    • Refactor as needed
  • Growth projections     • Document structure
```

---

## Document Model vs Relational Model

### Relational Model (Normalized)

```sql
-- Traditional relational schema
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(100)
);

CREATE TABLE addresses (
  id INT PRIMARY KEY,
  user_id INT REFERENCES users(id),
  street VARCHAR(200),
  city VARCHAR(100),
  country VARCHAR(100)
);

CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_id INT REFERENCES users(id),
  order_date DATE,
  total DECIMAL(10,2)
);

CREATE TABLE order_items (
  id INT PRIMARY KEY,
  order_id INT REFERENCES orders(id),
  product_id INT,
  quantity INT,
  price DECIMAL(10,2)
);

-- Query requires multiple JOINs
SELECT u.name, a.city, o.order_date, oi.quantity, p.name
FROM users u
JOIN addresses a ON u.id = a.user_id
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE u.id = 123;
```

### Document Model (Denormalized)

```javascript
// MongoDB document-oriented approach
{
  _id: ObjectId("..."),
  name: "John Doe",
  email: "john@example.com",
  addresses: [
    {
      type: "home",
      street: "123 Main St",
      city: "New York",
      country: "USA"
    },
    {
      type: "work",
      street: "456 Office Blvd",
      city: "New York",
      country: "USA"
    }
  ],
  orders: [
    {
      orderId: "ORD001",
      orderDate: ISODate("2024-01-15"),
      total: 299.99,
      items: [
        { productId: "P001", name: "Laptop", quantity: 1, price: 299.99 }
      ]
    }
  ]
}

// Single query retrieves all data
db.users.findOne({ _id: ObjectId("...") })
```

### Comparison

| Aspect | Relational | Document |
|--------|-----------|----------|
| **Schema** | Fixed, predefined | Flexible, dynamic |
| **Relationships** | JOINs at query time | Embedded or referenced |
| **Normalization** | Highly normalized | Often denormalized |
| **Reads** | May need JOINs | Often single document |
| **Writes** | May need transactions | Often atomic |
| **Scaling** | Vertical primarily | Horizontal (sharding) |

---

## Embedding vs Referencing

### Embedding (Denormalization)

```javascript
// Embedded subdocuments
{
  _id: ObjectId("user123"),
  name: "John Doe",
  // Embedded address - stored within user document
  address: {
    street: "123 Main St",
    city: "New York",
    zipCode: "10001"
  },
  // Embedded array of phone numbers
  phones: [
    { type: "home", number: "555-1234" },
    { type: "mobile", number: "555-5678" }
  ]
}
```

**When to Embed:**
- Data is accessed together frequently
- Data has a "contains" relationship
- One-to-few relationships
- Data rarely changes independently
- Embedded data doesn't need independent access

### Referencing (Normalization)

```javascript
// User document with reference
{
  _id: ObjectId("user123"),
  name: "John Doe",
  email: "john@example.com",
  companyId: ObjectId("company456")  // Reference to company
}

// Company document (separate collection)
{
  _id: ObjectId("company456"),
  name: "Acme Corp",
  industry: "Technology",
  employees: 500
}

// Query with $lookup
db.users.aggregate([
  { $match: { _id: ObjectId("user123") } },
  {
    $lookup: {
      from: "companies",
      localField: "companyId",
      foreignField: "_id",
      as: "company"
    }
  }
])
```

**When to Reference:**
- Data is accessed independently
- One-to-many or many-to-many with large sets
- Data changes frequently
- Unbounded growth in related data
- Need to avoid document size limits

### Decision Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Embed vs Reference Decision                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                        EMBED when:                                  │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │ • One-to-One relationships                                │     │
│  │ • One-to-Few relationships (< 100 items)                  │     │
│  │ • Data always retrieved together                          │     │
│  │ • Parent-child with exclusive ownership                   │     │
│  │ • Subdocuments rarely change                              │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                     │
│                      REFERENCE when:                                │
│  ┌───────────────────────────────────────────────────────────┐     │
│  │ • One-to-Many with large/unbounded "many"                 │     │
│  │ • Many-to-Many relationships                              │     │
│  │ • Data needed independently                               │     │
│  │ • Frequent updates to related data                        │     │
│  │ • Document would exceed 16MB                              │     │
│  │ • Data shared across multiple documents                   │     │
│  └───────────────────────────────────────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Schema Design Patterns

### Pattern 1: Attribute Pattern

Use for varied attributes across documents.

```javascript
// Without pattern - sparse fields
{
  _id: 1,
  name: "T-Shirt",
  size_small_stock: 50,
  size_medium_stock: 30,
  size_large_stock: 25,
  color_red: true,
  color_blue: true
  // Many optional fields...
}

// With Attribute Pattern
{
  _id: 1,
  name: "T-Shirt",
  attributes: [
    { name: "size", value: "small", stock: 50 },
    { name: "size", value: "medium", stock: 30 },
    { name: "size", value: "large", stock: 25 },
    { name: "color", value: "red" },
    { name: "color", value: "blue" }
  ]
}

// Index for efficient queries
db.products.createIndex({ "attributes.name": 1, "attributes.value": 1 })

// Query any attribute
db.products.find({ 
  attributes: { $elemMatch: { name: "color", value: "red" } }
})
```

### Pattern 2: Bucket Pattern

Group related data into buckets for time-series or high-volume data.

```javascript
// Without pattern - one document per measurement
{
  sensorId: "temp-001",
  timestamp: ISODate("2024-01-15T10:00:00Z"),
  temperature: 22.5
}

// With Bucket Pattern - grouped measurements
{
  sensorId: "temp-001",
  date: ISODate("2024-01-15"),
  hour: 10,
  measurements: [
    { minute: 0, temperature: 22.5 },
    { minute: 1, temperature: 22.6 },
    { minute: 2, temperature: 22.4 },
    // ... up to 60 measurements per document
  ],
  count: 60,
  sum: 1350,
  avg: 22.5,
  min: 22.1,
  max: 22.9
}

// Benefits:
// - Fewer documents to manage
// - Pre-computed aggregates
// - Efficient for range queries
```

### Pattern 3: Extended Reference Pattern

Embed frequently-accessed fields from referenced documents.

```javascript
// Full reference (requires lookup)
{
  _id: "order001",
  customerId: ObjectId("cust123"),
  items: [...]
}

// Extended reference (embedded summary)
{
  _id: "order001",
  customer: {
    _id: ObjectId("cust123"),
    name: "John Doe",          // Frequently accessed
    email: "john@example.com"  // Frequently accessed
    // Full customer data still in customers collection
  },
  items: [...]
}

// Most queries don't need $lookup
// Can still reference full customer when needed
```

### Pattern 4: Subset Pattern

Embed only frequently-accessed subset of data.

```javascript
// Product with embedded top reviews only
{
  _id: "product001",
  name: "Wireless Headphones",
  price: 79.99,
  // Embed only top 10 reviews
  topReviews: [
    { user: "Alice", rating: 5, text: "Great sound!", date: ISODate("...") },
    { user: "Bob", rating: 5, text: "Love it!", date: ISODate("...") },
    // ... top 10 only
  ],
  reviewCount: 1523,
  avgRating: 4.5
}

// Full reviews in separate collection
db.reviews.find({ productId: "product001" })
```

### Pattern 5: Computed Pattern

Pre-compute frequently-needed calculations.

```javascript
// Without computed fields
{
  _id: "movie001",
  title: "The Matrix",
  ratings: [5, 4, 5, 3, 5, 4, 5, 4, 5, 5, ...]  // Thousands of ratings
}
// Query: Calculate average every time

// With Computed Pattern
{
  _id: "movie001",
  title: "The Matrix",
  ratingCount: 15234,
  ratingSum: 68553,
  avgRating: 4.5,  // Pre-computed
  lastRatingAt: ISODate("...")
}

// Update with new rating
db.movies.updateOne(
  { _id: "movie001" },
  {
    $inc: { ratingCount: 1, ratingSum: 5 },
    $set: { 
      avgRating: { $divide: [{ $add: ["$ratingSum", 5] }, { $add: ["$ratingCount", 1] }] },
      lastRatingAt: new Date()
    }
  }
)
```

---

## One-to-One Relationships

### Embedded One-to-One

```javascript
// User with embedded profile (preferred for 1:1)
{
  _id: ObjectId("user123"),
  username: "johndoe",
  email: "john@example.com",
  profile: {
    firstName: "John",
    lastName: "Doe",
    avatar: "https://...",
    bio: "Software developer",
    birthDate: ISODate("1990-05-15"),
    preferences: {
      theme: "dark",
      language: "en",
      notifications: true
    }
  }
}
```

### Referenced One-to-One

```javascript
// Useful when profile is large or accessed separately
// User document
{
  _id: ObjectId("user123"),
  username: "johndoe",
  email: "john@example.com"
}

// Separate profile document
{
  _id: ObjectId("profile123"),
  userId: ObjectId("user123"),
  firstName: "John",
  lastName: "Doe",
  // Large fields...
  resume: "...(large text)...",
  portfolio: [...],  // Many items
  workHistory: [...]
}

// Two-way reference for flexibility
{
  _id: ObjectId("user123"),
  username: "johndoe",
  profileId: ObjectId("profile123")
}
```

---

## One-to-Many Relationships

### Embedding Few (One-to-Few)

```javascript
// Order with embedded items (few items per order)
{
  _id: ObjectId("order001"),
  orderDate: ISODate("2024-01-15"),
  customer: {
    _id: ObjectId("cust123"),
    name: "John Doe"
  },
  items: [
    { productId: "P001", name: "Laptop", price: 999, qty: 1 },
    { productId: "P002", name: "Mouse", price: 29, qty: 2 },
    { productId: "P003", name: "Keyboard", price: 79, qty: 1 }
  ],
  total: 1136
}
```

### Referencing Many (One-to-Many)

```javascript
// Blog post - comments can grow unbounded
// Post document (parent)
{
  _id: ObjectId("post001"),
  title: "MongoDB Best Practices",
  content: "...",
  author: ObjectId("user123"),
  createdAt: ISODate("2024-01-15"),
  commentCount: 1523
}

// Comment documents (children)
{
  _id: ObjectId("comment001"),
  postId: ObjectId("post001"),  // Reference to parent
  author: {
    _id: ObjectId("user456"),
    name: "Jane"
  },
  text: "Great article!",
  createdAt: ISODate("2024-01-16")
}

// Query comments for a post
db.comments.find({ postId: ObjectId("post001") })
  .sort({ createdAt: -1 })
  .limit(20)
```

### Parent Reference vs Child Reference

```javascript
// Parent Reference (children know their parent)
// Categories can have many products
{
  _id: "category001",
  name: "Electronics",
  description: "..."
}

{
  _id: "product001",
  name: "Laptop",
  categoryId: "category001"  // Reference to parent
}

// Query products in category
db.products.find({ categoryId: "category001" })


// Child Reference (parent knows its children)
// User with list of order IDs (for smaller lists)
{
  _id: ObjectId("user123"),
  name: "John",
  orderIds: [
    ObjectId("order001"),
    ObjectId("order002"),
    ObjectId("order003")
  ]
}

// Query using $in
db.orders.find({ _id: { $in: user.orderIds } })
```

### Hybrid Approach

```javascript
// Product with embedded recent reviews + reference to all reviews
{
  _id: "product001",
  name: "Wireless Headphones",
  // Embedded: most recent 5 reviews
  recentReviews: [
    { userId: "u1", rating: 5, text: "Excellent!", date: ISODate("...") },
    { userId: "u2", rating: 4, text: "Good quality", date: ISODate("...") },
    // ... 5 most recent
  ],
  reviewStats: {
    count: 1523,
    avgRating: 4.5,
    distribution: { "5": 800, "4": 450, "3": 200, "2": 50, "1": 23 }
  }
}

// Full reviews in separate collection
{
  _id: ObjectId("review001"),
  productId: "product001",
  userId: ObjectId("user123"),
  rating: 5,
  text: "Excellent product!",
  helpful: 45,
  createdAt: ISODate("...")
}
```

---

## Many-to-Many Relationships

### Two-Way Embedding (Small Sets)

```javascript
// Authors and Books (small number on both sides)
// Author document
{
  _id: ObjectId("author001"),
  name: "Jane Author",
  books: [
    { _id: ObjectId("book001"), title: "First Book" },
    { _id: ObjectId("book002"), title: "Second Book" }
  ]
}

// Book document
{
  _id: ObjectId("book001"),
  title: "First Book",
  authors: [
    { _id: ObjectId("author001"), name: "Jane Author" },
    { _id: ObjectId("author002"), name: "John Writer" }
  ]
}

// Note: Requires updating both documents when relationship changes
```

### Reference with Array (Medium Sets)

```javascript
// Students and Courses
// Student document
{
  _id: ObjectId("student001"),
  name: "Alice",
  courseIds: [
    ObjectId("course001"),
    ObjectId("course002"),
    ObjectId("course003")
  ]
}

// Course document
{
  _id: ObjectId("course001"),
  title: "MongoDB 101",
  studentIds: [
    ObjectId("student001"),
    ObjectId("student002"),
    // ... up to reasonable limit
  ],
  studentCount: 45
}

// Query with $lookup
db.students.aggregate([
  { $match: { _id: ObjectId("student001") } },
  {
    $lookup: {
      from: "courses",
      localField: "courseIds",
      foreignField: "_id",
      as: "courses"
    }
  }
])
```

### Junction Collection (Large Sets)

```javascript
// Products and Categories (many products, many categories)
// Product document
{
  _id: ObjectId("product001"),
  name: "Laptop",
  price: 999
}

// Category document
{
  _id: ObjectId("category001"),
  name: "Electronics"
}

// Junction/Mapping collection
{
  _id: ObjectId("mapping001"),
  productId: ObjectId("product001"),
  categoryId: ObjectId("category001"),
  // Additional relationship attributes
  isPrimary: true,
  addedAt: ISODate("2024-01-15")
}

// Index for efficient lookups
db.productCategories.createIndex({ productId: 1 })
db.productCategories.createIndex({ categoryId: 1 })

// Find all products in a category
db.productCategories.aggregate([
  { $match: { categoryId: ObjectId("category001") } },
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: "$product" },
  { $replaceRoot: { newRoot: "$product" } }
])
```

---

## Schema Design Best Practices

### 1. Design for Queries

```javascript
// Identify your queries first
// Query 1: Get user with recent orders
// Query 2: Get all orders for a date range
// Query 3: Get top products by category

// Design schema to support these queries efficiently
{
  _id: ObjectId("user123"),
  name: "John",
  // Embed recent orders for Query 1
  recentOrders: [/* last 5 orders */],
  orderCount: 47
}

// Separate orders collection for Query 2
{
  _id: ObjectId("order001"),
  userId: ObjectId("user123"),
  orderDate: ISODate("2024-01-15"),  // Indexed for range queries
  items: [...]
}
```

### 2. Consider Document Growth

```javascript
// Bad: Unbounded array growth
{
  _id: ObjectId("user123"),
  activities: []  // Could grow forever!
}

// Good: Capped or separate collection
{
  _id: ObjectId("user123"),
  recentActivities: []  // Keep last 10 only
}
// OR use separate collection with TTL index
```

### 3. Balance Normalization

```javascript
// Over-normalized (too many lookups)
{
  _id: "order001",
  customerRef: ObjectId("c1"),
  shippingAddressRef: ObjectId("a1"),
  billingAddressRef: ObjectId("a2"),
  items: [{ productRef: ObjectId("p1"), qty: 1 }]
}

// Over-denormalized (too much duplication)
{
  _id: "order001",
  customer: { /* full customer object */ },
  shippingAddress: { /* full address */ },
  billingAddress: { /* full address */ },
  items: [{ product: { /* full product */ }, qty: 1 }]
}

// Balanced
{
  _id: "order001",
  customer: {
    _id: ObjectId("c1"),
    name: "John",  // Frequently needed
    email: "john@example.com"  // Frequently needed
  },
  shippingAddress: { /* embedded - specific to order */ },
  items: [{
    productId: ObjectId("p1"),
    name: "Product",  // Snapshot at order time
    price: 99.99,     // Snapshot at order time
    qty: 1
  }]
}
```

### 4. Plan for Atomicity

```javascript
// MongoDB guarantees atomic updates at document level
// Design to keep related data together when atomicity matters

// Single document update is atomic
db.accounts.updateOne(
  { _id: "account001" },
  { 
    $inc: { balance: -100 },
    $push: { 
      transactions: { 
        amount: -100, 
        date: new Date(),
        type: "withdrawal"
      }
    }
  }
)

// If data must be updated atomically, keep it in same document
// or use transactions for multi-document operations
```

### 5. Use Appropriate Types

```javascript
// Use correct BSON types
{
  // Dates - not strings
  createdAt: ISODate("2024-01-15T10:00:00Z"),  // Good
  createdAt: "2024-01-15",  // Bad
  
  // Numbers for calculations
  price: 99.99,      // Good - can use $inc, $mul
  price: "99.99",    // Bad - string
  
  // ObjectId for references
  userId: ObjectId("..."),  // Good
  userId: "user123",        // OK for business keys
  
  // Arrays for multiple values
  tags: ["electronics", "sale"],  // Good
  tag1: "electronics", tag2: "sale"  // Bad
}
```

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Embedding** | Store related data in same document |
| **Referencing** | Store related data in separate documents |
| **Denormalization** | Duplicate data for read performance |
| **Schema Patterns** | Proven solutions for common scenarios |

### Decision Checklist

- [ ] What queries will the application perform?
- [ ] What is the read/write ratio?
- [ ] Will arrays grow unbounded?
- [ ] Is data accessed together or independently?
- [ ] What are the consistency requirements?
- [ ] How will the data scale over time?

### What's Next?

In the next chapter, we'll explore Embedded Documents in more detail.

---

## Practice Questions

1. When should you embed vs reference documents?
2. What are the trade-offs of denormalization?
3. How do you model a one-to-many relationship with unbounded "many"?
4. What is the Bucket Pattern and when should you use it?
5. How do you handle many-to-many relationships in MongoDB?
6. What factors influence schema design decisions?
7. How does atomicity affect schema design?
8. What's the Extended Reference Pattern?

---

## Hands-On Exercises

### Exercise 1: E-commerce Schema Design

Design a schema for an e-commerce platform with:
- Users with addresses
- Products with categories
- Orders with items
- Reviews for products

```javascript
// Users collection
{
  _id: ObjectId("..."),
  email: "user@example.com",
  name: "John Doe",
  addresses: [
    {
      type: "shipping",
      street: "123 Main St",
      city: "New York",
      zipCode: "10001",
      isDefault: true
    }
  ],
  createdAt: ISODate("...")
}

// Products collection
{
  _id: ObjectId("..."),
  sku: "PROD001",
  name: "Wireless Headphones",
  price: 79.99,
  categories: [
    { _id: ObjectId("..."), name: "Electronics" },
    { _id: ObjectId("..."), name: "Audio" }
  ],
  reviewStats: {
    count: 156,
    avgRating: 4.5
  },
  topReviews: [/* embedded top 5 */]
}

// Orders collection
{
  _id: ObjectId("..."),
  orderNumber: "ORD-2024-001",
  customer: {
    _id: ObjectId("..."),
    name: "John Doe",
    email: "user@example.com"
  },
  shippingAddress: { /* snapshot */ },
  items: [
    {
      productId: ObjectId("..."),
      name: "Wireless Headphones",  // Snapshot
      price: 79.99,                 // Snapshot
      quantity: 2
    }
  ],
  status: "shipped",
  createdAt: ISODate("...")
}

// Reviews collection (separate for scalability)
{
  _id: ObjectId("..."),
  productId: ObjectId("..."),
  userId: ObjectId("..."),
  userName: "John",
  rating: 5,
  text: "Great product!",
  helpful: 12,
  createdAt: ISODate("...")
}
```

### Exercise 2: Social Media Schema

Design a schema for a social media platform:
- Users with followers/following
- Posts with likes and comments
- Direct messages

```javascript
// Solution approach:
// - Users: embedded profile, referenced followers (can be large)
// - Posts: embedded author summary, referenced comments
// - Messages: separate collection with participants

// Think about:
// - Feed generation queries
// - Notification patterns
// - Message threading
```

### Exercise 3: Choose Embedding vs Referencing

For each scenario, decide whether to embed or reference:

1. **Blog comments** - Reference (unbounded growth)
2. **User preferences** - Embed (always accessed with user)
3. **Order line items** - Embed (always accessed together, limited)
4. **Product images** - Depends (few=embed, many/large=reference)
5. **Employee department** - Reference (shared, changes)

---

[← Previous: Bulk Write Operations](10-bulk-write-operations.md) | [Next: Embedded Documents →](12-embedded-documents.md)
