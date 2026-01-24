# Chapter 15: Schema Design Patterns

## Table of Contents
- [Introduction to Schema Patterns](#introduction-to-schema-patterns)
- [Polymorphic Pattern](#polymorphic-pattern)
- [Attribute Pattern](#attribute-pattern)
- [Bucket Pattern](#bucket-pattern)
- [Outlier Pattern](#outlier-pattern)
- [Computed Pattern](#computed-pattern)
- [Subset Pattern](#subset-pattern)
- [Extended Reference Pattern](#extended-reference-pattern)
- [Approximation Pattern](#approximation-pattern)
- [Tree Patterns](#tree-patterns)
- [Document Versioning Pattern](#document-versioning-pattern)
- [Schema Versioning Pattern](#schema-versioning-pattern)
- [Summary](#summary)

---

## Introduction to Schema Patterns

Schema design patterns are proven solutions to common data modeling challenges in MongoDB. They help optimize for specific use cases while maintaining flexibility.

### Pattern Selection Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Schema Pattern Selection                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Problem                          │ Pattern                        │
│  ─────────────────────────────────┼─────────────────────────────── │
│  Multiple document types          │ Polymorphic                    │
│  Variable/sparse attributes       │ Attribute                      │
│  High-volume time-series data     │ Bucket                         │
│  Few documents with many items    │ Outlier                        │
│  Expensive aggregations           │ Computed                       │
│  Large documents, partial access  │ Subset                         │
│  Frequent joins for same data     │ Extended Reference             │
│  Approximate counts/stats OK      │ Approximation                  │
│  Hierarchical data                │ Tree (various)                 │
│  Document change history          │ Document Versioning            │
│  Schema evolution                 │ Schema Versioning              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Polymorphic Pattern

Store different types of documents in the same collection with a type indicator.

### Problem
You have similar but not identical document types that need to be queried together.

### Solution

```javascript
// Single products collection with different product types
db.products.insertMany([
  // Book
  {
    _id: 1,
    type: "book",
    name: "MongoDB: The Definitive Guide",
    price: 49.99,
    // Book-specific fields
    author: "Shannon Bradshaw",
    isbn: "978-1491954461",
    pages: 514
  },
  
  // Electronics
  {
    _id: 2,
    type: "electronics",
    name: "Wireless Mouse",
    price: 29.99,
    // Electronics-specific fields
    brand: "Logitech",
    warranty: "2 years",
    voltage: "3V"
  },
  
  // Clothing
  {
    _id: 3,
    type: "clothing",
    name: "Cotton T-Shirt",
    price: 19.99,
    // Clothing-specific fields
    size: "M",
    color: "Blue",
    material: "100% Cotton"
  }
])

// Query all products
db.products.find({ price: { $lt: 50 } })

// Query specific type
db.products.find({ type: "book", author: "Shannon Bradshaw" })

// Aggregation across types
db.products.aggregate([
  { $group: { _id: "$type", avgPrice: { $avg: "$price" } } }
])
```

### Use Cases
- E-commerce product catalogs
- CMS with different content types
- User activities/events logging
- Multi-tenant applications

---

## Attribute Pattern

Convert fields with similar access patterns into an array of key-value pairs.

### Problem
Documents have many similar fields that are queried the same way, or fields vary significantly between documents.

### Solution

```javascript
// Without pattern - many optional fields
{
  name: "Movie",
  release_USA: "2024-01-15",
  release_UK: "2024-01-20",
  release_France: "2024-02-01",
  release_Germany: "2024-02-15",
  // ... many more countries
}

// With Attribute Pattern
{
  name: "Movie",
  releases: [
    { country: "USA", date: ISODate("2024-01-15") },
    { country: "UK", date: ISODate("2024-01-20") },
    { country: "France", date: ISODate("2024-02-01") },
    { country: "Germany", date: ISODate("2024-02-15") }
  ]
}

// Better example: Product specifications
db.products.insertOne({
  name: "Gaming Laptop",
  sku: "LAP-001",
  price: 1499.99,
  specs: [
    { k: "cpu", v: "Intel i9-13900H" },
    { k: "ram", v: "32GB DDR5" },
    { k: "storage", v: "1TB NVMe SSD" },
    { k: "gpu", v: "RTX 4080" },
    { k: "display", v: "17.3 inch 4K" },
    { k: "battery", v: "99Wh" },
    { k: "weight", v: "2.5 kg" }
  ]
})

// Single compound index covers all specs
db.products.createIndex({ "specs.k": 1, "specs.v": 1 })

// Query any specification
db.products.find({ specs: { $elemMatch: { k: "cpu", v: /Intel i9/ } } })
db.products.find({ specs: { $elemMatch: { k: "ram", v: "32GB DDR5" } } })
```

### Use Cases
- Product specifications
- Movie release dates by country
- Multilingual content
- Custom/variable attributes

---

## Bucket Pattern

Group related data into buckets (batches) to reduce document count and improve query efficiency.

### Problem
Time-series or event data creates too many small documents.

### Solution

```javascript
// Without pattern - one document per reading
// Millions of documents per day!
{
  sensorId: "temp-001",
  timestamp: ISODate("2024-01-15T10:00:00Z"),
  value: 22.5
}

// With Bucket Pattern - one document per hour
{
  sensorId: "temp-001",
  date: ISODate("2024-01-15"),
  hour: 10,
  
  // Pre-computed stats for the bucket
  count: 60,
  sum: 1350,
  avg: 22.5,
  min: 21.8,
  max: 23.2,
  
  // Individual readings
  readings: [
    { minute: 0, value: 22.5 },
    { minute: 1, value: 22.6 },
    { minute: 2, value: 22.4 },
    // ... 60 readings per document
  ]
}

// Insert/update with bucket
function addReading(sensorId, timestamp, value) {
  const date = new Date(timestamp)
  date.setMinutes(0, 0, 0)
  const hour = timestamp.getHours()
  const minute = timestamp.getMinutes()
  
  return db.sensor_readings.updateOne(
    {
      sensorId: sensorId,
      date: new Date(date.toISOString().split('T')[0]),
      hour: hour,
      count: { $lt: 60 }  // Bucket not full
    },
    {
      $push: {
        readings: { minute: minute, value: value }
      },
      $inc: { count: 1, sum: value },
      $min: { min: value },
      $max: { max: value }
    },
    { upsert: true }
  )
}

// Query efficiency: 24 documents/day vs 86,400
db.sensor_readings.find({
  sensorId: "temp-001",
  date: ISODate("2024-01-15")
})
```

### Bucket Sizes

```javascript
// Bucket by time period
// Hourly buckets (60-3600 entries)
{ period: "hour", maxEntries: 3600 }

// Daily buckets (for lower frequency data)
{ period: "day", maxEntries: 1440 }

// Fixed size buckets
{ maxEntries: 100 }  // Start new document after 100 entries
```

### Use Cases
- IoT sensor data
- Stock prices
- User activity logs
- Server metrics

---

## Outlier Pattern

Handle documents that don't fit the normal pattern separately.

### Problem
Most documents are small, but some have unusually large arrays or data.

### Solution

```javascript
// Book with normal number of reviews (embedded)
{
  _id: "book-001",
  title: "Regular Book",
  reviews: [
    { user: "user1", rating: 5, text: "Great!" },
    { user: "user2", rating: 4, text: "Good" },
    // 20-50 reviews embedded
  ],
  reviewCount: 25,
  hasExtraReviews: false
}

// Book with massive reviews (outlier)
{
  _id: "book-002",
  title: "Bestseller Book",
  reviews: [
    // Only keep top 50 reviews
    { user: "user1", rating: 5, text: "Amazing!" },
    // ...
  ],
  reviewCount: 15000,
  hasExtraReviews: true  // Flag indicating overflow
}

// Overflow collection for outliers
// reviews_overflow collection
{
  bookId: "book-002",
  reviews: [
    // Additional reviews stored separately
  ]
}

// Query pattern
function getBookReviews(bookId, page = 1, limit = 20) {
  const book = db.books.findOne({ _id: bookId })
  
  if (!book.hasExtraReviews || page === 1) {
    // Return embedded reviews for first page
    return book.reviews.slice(0, limit)
  }
  
  // Query overflow collection for subsequent pages
  return db.reviews_overflow.find({ bookId: bookId })
    .skip((page - 1) * limit)
    .limit(limit)
    .toArray()
}
```

### Use Cases
- Social media posts with viral engagement
- Products with extreme review counts
- Users with exceptional activity
- Popular items in recommendation systems

---

## Computed Pattern

Pre-compute frequently needed calculations to avoid repeated computation.

### Problem
Expensive aggregations are performed repeatedly on unchanged data.

### Solution

```javascript
// Instead of calculating on every read:
db.movies.aggregate([
  { $match: { _id: movieId } },
  { $unwind: "$ratings" },
  { $group: { _id: null, avgRating: { $avg: "$ratings" } } }
])

// Store computed values in document
{
  _id: "movie-001",
  title: "Great Movie",
  
  // Computed fields (updated on writes)
  stats: {
    ratingCount: 15234,
    ratingSum: 68553,
    avgRating: 4.5,
    ratingDistribution: {
      "5": 8000,
      "4": 4000,
      "3": 2000,
      "2": 800,
      "1": 434
    }
  },
  
  lastRatingAt: ISODate("2024-01-15T10:30:00Z")
}

// Update computed fields atomically
db.movies.updateOne(
  { _id: "movie-001" },
  [
    {
      $set: {
        "stats.ratingCount": { $add: ["$stats.ratingCount", 1] },
        "stats.ratingSum": { $add: ["$stats.ratingSum", newRating] },
        "stats.avgRating": {
          $divide: [
            { $add: ["$stats.ratingSum", newRating] },
            { $add: ["$stats.ratingCount", 1] }
          ]
        },
        [`stats.ratingDistribution.${newRating}`]: {
          $add: [{ $ifNull: [`$stats.ratingDistribution.${newRating}`, 0] }, 1]
        },
        lastRatingAt: "$$NOW"
      }
    }
  ]
)
```

### Other Computed Examples

```javascript
// E-commerce order totals
{
  _id: "order-001",
  items: [...],
  
  // Computed
  itemCount: 5,
  subtotal: 249.95,
  tax: 22.50,
  shipping: 9.99,
  total: 282.44
}

// User statistics
{
  _id: "user-001",
  
  // Computed
  stats: {
    postsCount: 142,
    followersCount: 5432,
    followingCount: 234,
    likesReceived: 89234
  }
}

// Leaderboard
{
  gameId: "game-001",
  
  // Computed top 100
  leaderboard: [
    { rank: 1, playerId: "p001", score: 99500, name: "Champion" },
    { rank: 2, playerId: "p002", score: 98200, name: "RunnerUp" },
    // ...
  ],
  lastUpdated: ISODate("...")
}
```

### Use Cases
- Rating averages
- Order totals
- User statistics
- Leaderboards
- Inventory counts

---

## Subset Pattern

Embed only the most relevant subset of data in the main document.

### Problem
Documents are too large because of embedded arrays, but most queries only need a small portion.

### Solution

```javascript
// Product with subset of reviews
{
  _id: "product-001",
  name: "Popular Product",
  price: 99.99,
  
  // Only most recent/helpful reviews embedded
  topReviews: [
    { 
      userId: "u001",
      userName: "Happy Customer",
      rating: 5,
      text: "Best purchase ever!",
      helpful: 234,
      date: ISODate("2024-01-10")
    },
    // ... 5-10 top reviews
  ],
  
  // Statistics
  reviewStats: {
    count: 2456,
    avgRating: 4.7
  }
}

// Full reviews in separate collection
db.reviews.find({ productId: "product-001" })

// Update subset when new review is added
function addReview(productId, review) {
  // Insert into reviews collection
  db.reviews.insertOne({
    productId: productId,
    ...review,
    helpful: 0,
    date: new Date()
  })
  
  // Update product stats
  db.products.updateOne(
    { _id: productId },
    {
      $inc: {
        "reviewStats.count": 1
      }
      // Recalculate avgRating...
    }
  )
  
  // Periodically update topReviews (async job)
  // Or update if new review qualifies
}
```

### Use Cases
- Product reviews
- User's recent orders
- Blog post comments
- Activity feeds

---

## Extended Reference Pattern

Duplicate frequently accessed fields from referenced documents.

### Problem
Frequent lookups to get the same few fields from related documents.

### Solution

```javascript
// Without pattern - always need lookup
{
  _id: "order-001",
  customerId: ObjectId("cust-001"),
  items: [...]
}
// Need $lookup to get customer name for every order display

// With Extended Reference
{
  _id: "order-001",
  customer: {
    // Extended reference - commonly needed fields
    _id: ObjectId("cust-001"),
    name: "John Doe",
    email: "john@example.com"
    // Full customer data still in customers collection
  },
  items: [
    {
      productId: ObjectId("prod-001"),
      // Extended reference for product
      name: "Widget",
      sku: "WID-001",
      price: 29.99,  // Price at time of order
      quantity: 2
    }
  ],
  total: 59.98,
  createdAt: ISODate("...")
}

// Most queries don't need $lookup
db.orders.find({ "customer.name": "John Doe" })

// Only use $lookup when full details needed
db.orders.aggregate([
  { $match: { _id: "order-001" } },
  {
    $lookup: {
      from: "customers",
      localField: "customer._id",
      foreignField: "_id",
      as: "fullCustomer"
    }
  }
])
```

### Handling Updates

```javascript
// When customer updates their name
db.customers.updateOne(
  { _id: customerId },
  { $set: { name: "John Smith" } }
)

// Option 1: Update all orders (if few documents)
db.orders.updateMany(
  { "customer._id": customerId },
  { $set: { "customer.name": "John Smith" } }
)

// Option 2: Accept stale data (often OK for historical records)
// Orders keep the name at time of order

// Option 3: Lazy update on next access
```

### Use Cases
- Order with customer info
- Post with author info
- Comment with user info
- Invoice with product info

---

## Approximation Pattern

Accept approximate values when exact precision isn't required.

### Problem
Exact counts require scanning all documents or maintaining precise counters under high write load.

### Solution

```javascript
// Page view counter with approximation
{
  pageId: "home",
  viewCount: 1523456,  // Approximate
  lastUpdated: ISODate("...")
}

// Only update occasionally (every Nth view)
function incrementPageView(pageId) {
  // Random probability update (1 in 10)
  if (Math.random() < 0.1) {
    db.pageViews.updateOne(
      { pageId: pageId },
      { 
        $inc: { viewCount: 10 },  // Increment by inverse of probability
        $set: { lastUpdated: new Date() }
      },
      { upsert: true }
    )
  }
}

// More sophisticated: Probabilistic counter
{
  pageId: "home",
  counts: {
    hourly: 1234,      // More accurate
    daily: 45678,      // Less updates
    monthly: 1234567   // Even fewer updates
  }
}

// User count approximation
function getApproximateUserCount() {
  // Instead of db.users.countDocuments()
  // Use cached/sampled count
  const stats = db.stats.findOne({ type: "userStats" })
  return stats.approximateCount
}

// Update periodically (cron job)
function updateUserCount() {
  const count = db.users.estimatedDocumentCount()  // Fast estimate
  db.stats.updateOne(
    { type: "userStats" },
    { $set: { approximateCount: count, updatedAt: new Date() } },
    { upsert: true }
  )
}
```

### Use Cases
- Page view counts
- Like counts
- Follower counts
- Analytics counters
- Real-time dashboards

---

## Tree Patterns

Several patterns for storing hierarchical data.

### Parent Reference

```javascript
// Each node stores its parent
{
  _id: "category-1",
  name: "Electronics",
  parent: null  // Root node
}
{
  _id: "category-2",
  name: "Phones",
  parent: "category-1"
}
{
  _id: "category-3",
  name: "Smartphones",
  parent: "category-2"
}

// Find children
db.categories.find({ parent: "category-1" })

// Find ancestors (requires multiple queries or $graphLookup)
db.categories.aggregate([
  { $match: { _id: "category-3" } },
  {
    $graphLookup: {
      from: "categories",
      startWith: "$parent",
      connectFromField: "parent",
      connectToField: "_id",
      as: "ancestors"
    }
  }
])
```

### Child Reference

```javascript
// Each node stores its children
{
  _id: "category-1",
  name: "Electronics",
  children: ["category-2", "category-4"]
}
{
  _id: "category-2",
  name: "Phones",
  children: ["category-3"]
}

// Find children (embedded)
const node = db.categories.findOne({ _id: "category-1" })
// children are node.children

// Find all descendants (recursive)
function getDescendants(nodeId) {
  const node = db.categories.findOne({ _id: nodeId })
  if (!node || !node.children.length) return []
  
  let descendants = [...node.children]
  for (const childId of node.children) {
    descendants = descendants.concat(getDescendants(childId))
  }
  return descendants
}
```

### Materialized Path

```javascript
// Store full path in each node
{
  _id: "category-3",
  name: "Smartphones",
  path: ",category-1,category-2,category-3,",
  depth: 2
}

// Find all descendants of category-1
db.categories.find({
  path: /^,category-1,/
})

// Find ancestors
db.categories.find({
  _id: { $in: ["category-1", "category-2"] }  // Parse from path
})

// Find direct children
db.categories.find({
  path: /^,category-1,[^,]+,$/
})
```

### Nested Sets

```javascript
// Store left/right boundaries
{
  _id: "category-1",
  name: "Electronics",
  left: 1,
  right: 10
}
{
  _id: "category-2",
  name: "Phones",
  left: 2,
  right: 7
}
{
  _id: "category-3",
  name: "Smartphones",
  left: 3,
  right: 4
}

// Find all descendants
db.categories.find({
  left: { $gt: 1 },
  right: { $lt: 10 }
})

// Note: Updates are expensive (recalculate boundaries)
```

### Tree Pattern Comparison

| Pattern | Find Children | Find Descendants | Find Ancestors | Insert/Move |
|---------|--------------|------------------|----------------|-------------|
| Parent Reference | Query | Multiple queries/$graphLookup | Multiple queries | Easy |
| Child Reference | Embedded | Recursive | Query | Medium |
| Materialized Path | Regex | Regex | Parse path | Medium |
| Nested Sets | Range | Range | Range | Expensive |

---

## Document Versioning Pattern

Maintain history of document changes.

### Solution

```javascript
// Current document collection
{
  _id: "doc-001",
  title: "My Document",
  content: "Current content...",
  version: 5,
  updatedAt: ISODate("2024-01-15"),
  updatedBy: "user-001"
}

// History collection
{
  _id: ObjectId("..."),
  documentId: "doc-001",
  version: 4,
  title: "My Document",
  content: "Previous content...",
  updatedAt: ISODate("2024-01-14"),
  updatedBy: "user-002",
  changeType: "edit"
}

// Save version before update
function updateDocument(docId, updates, userId) {
  // Get current document
  const current = db.documents.findOne({ _id: docId })
  
  // Save to history
  db.document_history.insertOne({
    documentId: docId,
    version: current.version,
    ...current,
    _id: undefined  // Remove _id
  })
  
  // Update document
  return db.documents.updateOne(
    { _id: docId },
    {
      $set: {
        ...updates,
        updatedAt: new Date(),
        updatedBy: userId
      },
      $inc: { version: 1 }
    }
  )
}

// Get document at specific version
function getDocumentVersion(docId, version) {
  const current = db.documents.findOne({ _id: docId })
  if (current.version === version) return current
  
  return db.document_history.findOne({
    documentId: docId,
    version: version
  })
}

// Get version history
function getVersionHistory(docId, limit = 10) {
  return db.document_history.find({ documentId: docId })
    .sort({ version: -1 })
    .limit(limit)
    .toArray()
}
```

---

## Schema Versioning Pattern

Handle schema evolution across document versions.

### Solution

```javascript
// Add schema version to all documents
{
  _id: "user-001",
  schemaVersion: 2,
  name: "John Doe",
  email: "john@example.com",
  // v2 fields
  profile: {
    firstName: "John",
    lastName: "Doe"
  }
}

// Old document (v1)
{
  _id: "user-002",
  schemaVersion: 1,
  firstName: "Jane",
  lastName: "Doe",
  email: "jane@example.com"
}

// Migration function
function migrateUserToV2(user) {
  if (user.schemaVersion >= 2) return user
  
  return {
    ...user,
    schemaVersion: 2,
    name: `${user.firstName} ${user.lastName}`,
    profile: {
      firstName: user.firstName,
      lastName: user.lastName
    },
    firstName: undefined,
    lastName: undefined
  }
}

// Read with migration
function getUser(userId) {
  const user = db.users.findOne({ _id: userId })
  if (!user) return null
  
  // Migrate on read
  const migrated = migrateUserToV2(user)
  
  // Optionally save migrated version
  if (migrated.schemaVersion > user.schemaVersion) {
    db.users.replaceOne({ _id: userId }, migrated)
  }
  
  return migrated
}

// Batch migration
function migrateAllUsers() {
  const cursor = db.users.find({ schemaVersion: { $lt: 2 } })
  let count = 0
  
  while (cursor.hasNext()) {
    const user = cursor.next()
    const migrated = migrateUserToV2(user)
    db.users.replaceOne({ _id: user._id }, migrated)
    count++
  }
  
  return count
}
```

---

## Summary

### Pattern Quick Reference

| Pattern | Use When |
|---------|----------|
| **Polymorphic** | Different document types in same collection |
| **Attribute** | Variable/sparse fields with similar queries |
| **Bucket** | High-volume time-series data |
| **Outlier** | Some documents have exceptional data sizes |
| **Computed** | Repeated expensive calculations |
| **Subset** | Only need portion of large embedded arrays |
| **Extended Reference** | Frequently access same fields from references |
| **Approximation** | Exact counts not required |
| **Tree** | Hierarchical data structures |
| **Document Versioning** | Need change history |
| **Schema Versioning** | Schema evolves over time |

### What's Next?

In the next chapter, we'll explore Index Fundamentals for query optimization.

---

## Practice Questions

1. When should you use the Polymorphic Pattern?
2. How does the Bucket Pattern improve performance?
3. What's the trade-off of the Extended Reference Pattern?
4. When is approximate counting acceptable?
5. Which tree pattern is best for frequent hierarchy queries?
6. How do you handle schema evolution with versioning?
7. What's the difference between Document and Schema Versioning?
8. When would you combine multiple patterns?

---

## Hands-On Exercises

### Exercise 1: Implement Bucket Pattern

```javascript
// Create sensor data with bucket pattern
function recordSensorData(sensorId, value) {
  const now = new Date()
  const hourStart = new Date(now)
  hourStart.setMinutes(0, 0, 0)
  
  return db.sensor_buckets.updateOne(
    {
      sensorId: sensorId,
      hour: hourStart,
      count: { $lt: 60 }
    },
    {
      $push: {
        readings: {
          minute: now.getMinutes(),
          value: value,
          timestamp: now
        }
      },
      $inc: { count: 1, sum: value },
      $min: { min: value },
      $max: { max: value },
      $setOnInsert: {
        sensorId: sensorId,
        hour: hourStart
      }
    },
    { upsert: true }
  )
}

// Test it
for (let i = 0; i < 10; i++) {
  recordSensorData("temp-001", 20 + Math.random() * 10)
}

// Query buckets
db.sensor_buckets.find({ sensorId: "temp-001" })
```

### Exercise 2: Implement Computed Pattern

```javascript
// Product with computed reviews
db.computed_products.insertOne({
  _id: "prod-001",
  name: "Test Product",
  stats: {
    reviewCount: 0,
    ratingSum: 0,
    avgRating: 0,
    ratings: { "1": 0, "2": 0, "3": 0, "4": 0, "5": 0 }
  }
})

// Add review and update computed fields
function addReview(productId, rating) {
  const ratingKey = `stats.ratings.${rating}`
  
  return db.computed_products.findOneAndUpdate(
    { _id: productId },
    [
      {
        $set: {
          "stats.reviewCount": { $add: ["$stats.reviewCount", 1] },
          "stats.ratingSum": { $add: ["$stats.ratingSum", rating] },
          "stats.avgRating": {
            $round: [{
              $divide: [
                { $add: ["$stats.ratingSum", rating] },
                { $add: ["$stats.reviewCount", 1] }
              ]
            }, 2]
          },
          [ratingKey]: { $add: [{ $ifNull: [`$${ratingKey}`, 0] }, 1] }
        }
      }
    ],
    { returnDocument: "after" }
  )
}

// Add some reviews
addReview("prod-001", 5)
addReview("prod-001", 4)
addReview("prod-001", 5)
addReview("prod-001", 3)

// Check result
db.computed_products.findOne({ _id: "prod-001" })
```

---

[← Previous: Schema Validation](14-schema-validation.md) | [Next: Index Fundamentals →](16-index-fundamentals.md)
