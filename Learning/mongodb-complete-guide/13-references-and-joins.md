# Chapter 13: References and Joins

## Table of Contents
- [References Overview](#references-overview)
- [Manual References](#manual-references)
- [DBRef (Database References)](#dbref-database-references)
- [The $lookup Aggregation Stage](#the-lookup-aggregation-stage)
- [Advanced $lookup Operations](#advanced-lookup-operations)
- [Joining Multiple Collections](#joining-multiple-collections)
- [Performance Considerations](#performance-considerations)
- [Application-Level Joins](#application-level-joins)
- [Summary](#summary)

---

## References Overview

References allow you to normalize your data by storing related information in separate collections and connecting them through identifiers.

### Reference Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MongoDB Reference Types                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Manual References                                               │
│     • Store related document's _id                                  │
│     • Simple and flexible                                           │
│     • Most common approach                                          │
│                                                                     │
│  2. DBRefs                                                          │
│     • Formal reference format with collection name                  │
│     • Less common, more verbose                                     │
│     • Useful for cross-collection or cross-database references     │
│                                                                     │
│  3. $lookup (Server-side Join)                                      │
│     • Join collections in aggregation pipeline                      │
│     • Similar to SQL LEFT OUTER JOIN                                │
│     • Available since MongoDB 3.2                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Manual References

### Basic Manual Reference

```javascript
// User document
{
  _id: ObjectId("user001"),
  name: "John Doe",
  email: "john@example.com"
}

// Order document with manual reference
{
  _id: ObjectId("order001"),
  orderNumber: "ORD-2024-001",
  userId: ObjectId("user001"),  // Manual reference to user
  items: [
    { productId: ObjectId("prod001"), qty: 2 }
  ],
  total: 199.98,
  createdAt: new Date()
}

// Product document
{
  _id: ObjectId("prod001"),
  name: "Widget",
  price: 99.99
}
```

### Resolving Manual References

```javascript
// Application code to resolve reference
const order = db.orders.findOne({ _id: ObjectId("order001") })
const user = db.users.findOne({ _id: order.userId })
const products = db.products.find({
  _id: { $in: order.items.map(item => item.productId) }
}).toArray()

// Using $lookup in aggregation
db.orders.aggregate([
  { $match: { _id: ObjectId("order001") } },
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" }
])
```

### Reference Arrays

```javascript
// User with array of references
{
  _id: ObjectId("user001"),
  name: "John Doe",
  favoriteProductIds: [
    ObjectId("prod001"),
    ObjectId("prod002"),
    ObjectId("prod003")
  ]
}

// Resolve array of references
db.users.aggregate([
  { $match: { _id: ObjectId("user001") } },
  {
    $lookup: {
      from: "products",
      localField: "favoriteProductIds",
      foreignField: "_id",
      as: "favoriteProducts"
    }
  }
])
```

---

## DBRef (Database References)

### DBRef Structure

```javascript
// DBRef format
{
  $ref: "collection_name",
  $id: ObjectId("..."),
  $db: "database_name"  // Optional
}

// Document with DBRef
{
  _id: ObjectId("order001"),
  orderNumber: "ORD-2024-001",
  customer: {
    $ref: "users",
    $id: ObjectId("user001")
  }
}
```

### When to Use DBRef

```javascript
// DBRef is useful when:
// 1. References span multiple collections dynamically
{
  _id: ObjectId("comment001"),
  text: "Great!",
  target: {
    $ref: "posts",      // Could be "posts", "products", "articles"
    $id: ObjectId("...")
  }
}

// 2. Cross-database references
{
  _id: ObjectId("..."),
  relatedDoc: {
    $ref: "items",
    $id: ObjectId("..."),
    $db: "other_database"
  }
}

// Generally, manual references are preferred
// DBRefs add overhead without built-in resolution
```

---

## The $lookup Aggregation Stage

### Basic $lookup Syntax

```javascript
{
  $lookup: {
    from: "foreign_collection",     // Collection to join
    localField: "local_field",      // Field from input documents
    foreignField: "foreign_field",  // Field from foreign collection
    as: "output_array"             // Output array field name
  }
}
```

### Simple Join Example

```javascript
// Collections
// users: { _id, name, email }
// orders: { _id, userId, total, items }

// Join orders with users
db.orders.aggregate([
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "customer"
    }
  }
])

// Result:
{
  _id: ObjectId("order001"),
  userId: ObjectId("user001"),
  total: 199.98,
  items: [...],
  customer: [  // Array of matching documents
    {
      _id: ObjectId("user001"),
      name: "John Doe",
      email: "john@example.com"
    }
  ]
}
```

### $unwind After $lookup

```javascript
// Convert array to single document
db.orders.aggregate([
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" }  // Flatten the array
])

// Result:
{
  _id: ObjectId("order001"),
  userId: ObjectId("user001"),
  total: 199.98,
  customer: {  // Now an object, not array
    _id: ObjectId("user001"),
    name: "John Doe",
    email: "john@example.com"
  }
}

// Preserve documents without matches
db.orders.aggregate([
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "customer"
    }
  },
  {
    $unwind: {
      path: "$customer",
      preserveNullAndEmptyArrays: true  // Keep orders without users
    }
  }
])
```

---

## Advanced $lookup Operations

### Pipeline Lookup (MongoDB 3.6+)

```javascript
// Use pipeline for complex joins
db.orders.aggregate([
  {
    $lookup: {
      from: "users",
      let: { userId: "$userId" },  // Define variables
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$userId"] } } },
        { $project: { name: 1, email: 1, _id: 0 } }  // Select fields
      ],
      as: "customer"
    }
  }
])

// Join with conditions
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { orderDate: "$createdAt" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$category", "Electronics"] },
                { $lte: ["$createdAt", "$$orderDate"] }
              ]
            }
          }
        },
        { $limit: 5 }
      ],
      as: "relatedProducts"
    }
  }
])
```

### Correlated Subqueries

```javascript
// Get orders with items expanded
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { productIds: "$items.productId" },
      pipeline: [
        { $match: { $expr: { $in: ["$_id", "$$productIds"] } } }
      ],
      as: "productDetails"
    }
  }
])

// Calculate order total with product prices
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { items: "$items" },
      pipeline: [
        {
          $match: {
            $expr: {
              $in: ["$_id", { $map: { input: "$$items", as: "i", in: "$$i.productId" } }]
            }
          }
        }
      ],
      as: "products"
    }
  },
  {
    $addFields: {
      calculatedTotal: {
        $reduce: {
          input: "$items",
          initialValue: 0,
          in: {
            $add: [
              "$$value",
              {
                $multiply: [
                  "$$this.qty",
                  {
                    $let: {
                      vars: {
                        product: {
                          $arrayElemAt: [
                            {
                              $filter: {
                                input: "$products",
                                cond: { $eq: ["$$this.productId", "$$product._id"] }
                              }
                            },
                            0
                          ]
                        }
                      },
                      in: "$$product.price"
                    }
                  }
                ]
              }
            ]
          }
        }
      }
    }
  }
])
```

### Uncorrelated Subquery

```javascript
// Join without matching fields (all combinations)
db.orders.aggregate([
  {
    $lookup: {
      from: "promotions",
      pipeline: [
        { $match: { active: true } },
        { $match: { $expr: { $gt: ["$endDate", "$$NOW"] } } }
      ],
      as: "activePromotions"
    }
  }
])
```

---

## Joining Multiple Collections

### Chained $lookup

```javascript
// Join orders -> users -> addresses
db.orders.aggregate([
  // First lookup: orders -> users
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  },
  { $unwind: "$user" },
  
  // Second lookup: users -> addresses
  {
    $lookup: {
      from: "addresses",
      localField: "user.addressIds",
      foreignField: "_id",
      as: "user.addresses"
    }
  },
  
  // Third lookup: orders -> products
  {
    $lookup: {
      from: "products",
      localField: "items.productId",
      foreignField: "_id",
      as: "products"
    }
  }
])
```

### Nested $lookup

```javascript
// Lookup within lookup pipeline
db.orders.aggregate([
  {
    $lookup: {
      from: "users",
      let: { userId: "$userId" },
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$userId"] } } },
        // Nested lookup for user's orders history
        {
          $lookup: {
            from: "orders",
            localField: "_id",
            foreignField: "userId",
            as: "orderHistory"
          }
        },
        {
          $addFields: {
            totalOrders: { $size: "$orderHistory" },
            totalSpent: { $sum: "$orderHistory.total" }
          }
        },
        { $project: { orderHistory: 0 } }
      ],
      as: "customer"
    }
  }
])
```

### Complete E-commerce Query

```javascript
// Get order with all related data
db.orders.aggregate([
  { $match: { _id: ObjectId("order001") } },
  
  // Join customer
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  
  // Join shipping address
  {
    $lookup: {
      from: "addresses",
      localField: "shippingAddressId",
      foreignField: "_id",
      as: "shippingAddress"
    }
  },
  { $unwind: "$shippingAddress" },
  
  // Join products for each item
  {
    $lookup: {
      from: "products",
      localField: "items.productId",
      foreignField: "_id",
      as: "productDetails"
    }
  },
  
  // Merge product details into items
  {
    $addFields: {
      items: {
        $map: {
          input: "$items",
          as: "item",
          in: {
            $mergeObjects: [
              "$$item",
              {
                product: {
                  $arrayElemAt: [
                    {
                      $filter: {
                        input: "$productDetails",
                        cond: { $eq: ["$$this._id", "$$item.productId"] }
                      }
                    },
                    0
                  ]
                }
              }
            ]
          }
        }
      }
    }
  },
  
  // Clean up
  { $project: { productDetails: 0 } }
])
```

---

## Performance Considerations

### Index for $lookup

```javascript
// Always index the foreign field
db.orders.createIndex({ userId: 1 })
db.users.createIndex({ _id: 1 })  // Usually exists by default

// For pipeline lookups, index the match conditions
db.products.createIndex({ category: 1, createdAt: 1 })
```

### $lookup Performance Tips

```
┌─────────────────────────────────────────────────────────────────────┐
│                 $lookup Performance Optimization                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Filter Early                                                    │
│     • Use $match before $lookup to reduce documents                │
│     • Filter the foreign collection in pipeline                    │
│                                                                     │
│  2. Index Properly                                                  │
│     • Index localField in source collection                        │
│     • Index foreignField in joined collection                      │
│     • Index any fields used in pipeline $match                     │
│                                                                     │
│  3. Limit Results                                                   │
│     • Use $limit in pipeline to cap results                        │
│     • Use $project to return only needed fields                    │
│                                                                     │
│  4. Consider Data Model                                            │
│     • If $lookup is frequent, consider embedding                   │
│     • Use denormalization for read-heavy workloads                 │
│                                                                     │
│  5. Monitor Performance                                            │
│     • Use explain() to analyze query plans                         │
│     • Check for COLLSCAN (table scans)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Comparing Approaches

```javascript
// Approach 1: $lookup (server-side join)
// Pros: Single query, atomic view
// Cons: Can be slow for large datasets

db.orders.aggregate([
  { $match: { status: "pending" } },  // Filter first
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  },
  { $limit: 100 }  // Limit results
])

// Approach 2: Application-level join
// Pros: More control, can use caching
// Cons: Multiple round trips

const orders = db.orders.find({ status: "pending" }).limit(100).toArray()
const userIds = [...new Set(orders.map(o => o.userId))]
const users = db.users.find({ _id: { $in: userIds } }).toArray()
const userMap = new Map(users.map(u => [u._id.toString(), u]))

const enrichedOrders = orders.map(order => ({
  ...order,
  user: userMap.get(order.userId.toString())
}))
```

### Explain $lookup

```javascript
// Check query plan
db.orders.aggregate([
  { $match: { status: "pending" } },
  {
    $lookup: {
      from: "users",
      localField: "userId",
      foreignField: "_id",
      as: "user"
    }
  }
]).explain("executionStats")

// Look for:
// - IXSCAN vs COLLSCAN
// - executionTimeMillis
// - totalDocsExamined
```

---

## Application-Level Joins

### Manual Join Pattern

```javascript
// Node.js example
async function getOrderWithDetails(orderId) {
  // Step 1: Get order
  const order = await db.collection('orders').findOne({ _id: orderId })
  
  if (!order) return null
  
  // Step 2: Get related data in parallel
  const [user, products] = await Promise.all([
    db.collection('users').findOne({ _id: order.userId }),
    db.collection('products').find({
      _id: { $in: order.items.map(i => i.productId) }
    }).toArray()
  ])
  
  // Step 3: Combine data
  const productMap = new Map(products.map(p => [p._id.toString(), p]))
  
  return {
    ...order,
    user,
    items: order.items.map(item => ({
      ...item,
      product: productMap.get(item.productId.toString())
    }))
  }
}
```

### Cached Reference Pattern

```javascript
// Cache frequently accessed references
class ReferenceCache {
  constructor(db, ttlMs = 60000) {
    this.db = db
    this.cache = new Map()
    this.ttlMs = ttlMs
  }
  
  async getUser(userId) {
    const key = `user:${userId}`
    const cached = this.cache.get(key)
    
    if (cached && Date.now() - cached.timestamp < this.ttlMs) {
      return cached.data
    }
    
    const user = await this.db.collection('users').findOne({ _id: userId })
    this.cache.set(key, { data: user, timestamp: Date.now() })
    return user
  }
  
  async resolveUsers(userIds) {
    const unique = [...new Set(userIds.map(id => id.toString()))]
    const results = await Promise.all(
      unique.map(id => this.getUser(new ObjectId(id)))
    )
    return new Map(results.map((user, i) => [unique[i], user]))
  }
}
```

### Batch Loading Pattern

```javascript
// DataLoader pattern for efficient batching
const DataLoader = require('dataloader')

const userLoader = new DataLoader(async (userIds) => {
  const users = await db.collection('users').find({
    _id: { $in: userIds }
  }).toArray()
  
  const userMap = new Map(users.map(u => [u._id.toString(), u]))
  return userIds.map(id => userMap.get(id.toString()))
})

// Usage - requests are automatically batched
async function resolveOrder(order) {
  const user = await userLoader.load(order.userId)
  return { ...order, user }
}
```

---

## Summary

### Reference Methods Comparison

| Method | Use Case | Pros | Cons |
|--------|----------|------|------|
| **Manual Reference** | Most scenarios | Simple, flexible | Requires join logic |
| **DBRef** | Cross-collection dynamic refs | Structured format | Verbose, no auto-resolve |
| **$lookup** | Server-side joins | Single query | Performance at scale |
| **Application Join** | Complex scenarios | Full control | Multiple queries |

### $lookup Variants

| Syntax | Use Case |
|--------|----------|
| Basic (localField/foreignField) | Simple equality joins |
| Pipeline | Complex conditions, transformations |
| Nested $lookup | Multiple levels of joins |
| Uncorrelated | All combinations |

### Best Practices

1. **Index foreign fields** for $lookup performance
2. **Filter early** with $match before $lookup
3. **Limit results** when possible
4. **Consider embedding** for frequently joined data
5. **Use application joins** for complex caching needs

### What's Next?

In the next chapter, we'll explore Schema Validation for data integrity.

---

## Practice Questions

1. What's the difference between manual references and DBRefs?
2. How does $lookup perform a join operation?
3. When should you use pipeline $lookup vs basic $lookup?
4. How do you optimize $lookup performance?
5. What's the purpose of $unwind after $lookup?
6. How do you join more than two collections?
7. When should you use application-level joins vs $lookup?
8. How do you handle missing references in joins?

---

## Hands-On Exercises

### Exercise 1: Basic $lookup

```javascript
// Setup collections
db.authors.insertMany([
  { _id: 1, name: "Jane Austen", country: "UK" },
  { _id: 2, name: "Mark Twain", country: "USA" },
  { _id: 3, name: "Leo Tolstoy", country: "Russia" }
])

db.books.insertMany([
  { _id: 101, title: "Pride and Prejudice", authorId: 1, year: 1813 },
  { _id: 102, title: "Emma", authorId: 1, year: 1815 },
  { _id: 103, title: "Tom Sawyer", authorId: 2, year: 1876 },
  { _id: 104, title: "War and Peace", authorId: 3, year: 1869 },
  { _id: 105, title: "Unknown Book", authorId: 99, year: 2000 }  // No matching author
])

// 1. Join books with authors
db.books.aggregate([
  {
    $lookup: {
      from: "authors",
      localField: "authorId",
      foreignField: "_id",
      as: "author"
    }
  },
  { $unwind: { path: "$author", preserveNullAndEmptyArrays: true } }
])

// 2. Get authors with their books
db.authors.aggregate([
  {
    $lookup: {
      from: "books",
      localField: "_id",
      foreignField: "authorId",
      as: "books"
    }
  },
  {
    $addFields: {
      bookCount: { $size: "$books" }
    }
  }
])
```

### Exercise 2: Pipeline $lookup

```javascript
// Setup
db.customers.insertMany([
  { _id: 1, name: "Alice", tier: "gold" },
  { _id: 2, name: "Bob", tier: "silver" },
  { _id: 3, name: "Charlie", tier: "bronze" }
])

db.orderHistory.insertMany([
  { _id: 1, customerId: 1, amount: 100, date: new Date("2024-01-15") },
  { _id: 2, customerId: 1, amount: 200, date: new Date("2024-02-15") },
  { _id: 3, customerId: 2, amount: 50, date: new Date("2024-01-20") },
  { _id: 4, customerId: 1, amount: 300, date: new Date("2023-12-15") }
])

// Get customers with orders from 2024 only
db.customers.aggregate([
  {
    $lookup: {
      from: "orderHistory",
      let: { custId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$customerId", "$$custId"] },
            date: { $gte: new Date("2024-01-01") }
          }
        },
        { $sort: { date: -1 } }
      ],
      as: "recentOrders"
    }
  },
  {
    $addFields: {
      totalSpent2024: { $sum: "$recentOrders.amount" }
    }
  }
])
```

### Exercise 3: Multiple Joins

```javascript
// Setup e-commerce data
db.categories.insertMany([
  { _id: 1, name: "Electronics" },
  { _id: 2, name: "Books" }
])

db.products.insertMany([
  { _id: 101, name: "Laptop", categoryId: 1, price: 999 },
  { _id: 102, name: "Phone", categoryId: 1, price: 699 },
  { _id: 103, name: "Novel", categoryId: 2, price: 15 }
])

db.reviews.insertMany([
  { productId: 101, rating: 5, comment: "Great laptop!" },
  { productId: 101, rating: 4, comment: "Good value" },
  { productId: 102, rating: 3, comment: "Average phone" }
])

// Get products with category and reviews
db.products.aggregate([
  // Join category
  {
    $lookup: {
      from: "categories",
      localField: "categoryId",
      foreignField: "_id",
      as: "category"
    }
  },
  { $unwind: "$category" },
  
  // Join reviews
  {
    $lookup: {
      from: "reviews",
      localField: "_id",
      foreignField: "productId",
      as: "reviews"
    }
  },
  
  // Calculate average rating
  {
    $addFields: {
      reviewCount: { $size: "$reviews" },
      avgRating: { $avg: "$reviews.rating" }
    }
  },
  
  // Project final shape
  {
    $project: {
      name: 1,
      price: 1,
      category: "$category.name",
      reviewCount: 1,
      avgRating: { $round: ["$avgRating", 1] }
    }
  }
])
```

### Exercise 4: Self-Join (Hierarchical Data)

```javascript
// Employees with managers
db.employees.insertMany([
  { _id: 1, name: "CEO", managerId: null },
  { _id: 2, name: "CTO", managerId: 1 },
  { _id: 3, name: "CFO", managerId: 1 },
  { _id: 4, name: "Developer", managerId: 2 },
  { _id: 5, name: "Designer", managerId: 2 },
  { _id: 6, name: "Accountant", managerId: 3 }
])

// Get employees with their manager info
db.employees.aggregate([
  {
    $lookup: {
      from: "employees",
      localField: "managerId",
      foreignField: "_id",
      as: "manager"
    }
  },
  {
    $unwind: {
      path: "$manager",
      preserveNullAndEmptyArrays: true
    }
  },
  {
    $project: {
      name: 1,
      managerName: { $ifNull: ["$manager.name", "No Manager"] }
    }
  }
])

// Get managers with their direct reports
db.employees.aggregate([
  {
    $lookup: {
      from: "employees",
      localField: "_id",
      foreignField: "managerId",
      as: "directReports"
    }
  },
  {
    $match: {
      "directReports.0": { $exists: true }  // Only managers
    }
  },
  {
    $project: {
      name: 1,
      directReports: "$directReports.name",
      reportCount: { $size: "$directReports" }
    }
  }
])
```

---

[← Previous: Embedded Documents](12-embedded-documents.md) | [Next: Schema Validation →](14-schema-validation.md)
