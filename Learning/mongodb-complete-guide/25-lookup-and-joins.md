# Chapter 25: $lookup and Joins

## Table of Contents
- [Introduction to $lookup](#introduction-to-lookup)
- [Basic $lookup](#basic-lookup)
- [Uncorrelated Subqueries](#uncorrelated-subqueries)
- [Correlated Subqueries](#correlated-subqueries)
- [Multiple Joins](#multiple-joins)
- [Join Performance](#join-performance)
- [$graphLookup for Recursive Queries](#graphlookup-for-recursive-queries)
- [Common Join Patterns](#common-join-patterns)
- [Summary](#summary)

---

## Introduction to $lookup

The `$lookup` stage performs a left outer join between documents in the pipeline and documents in another collection.

### $lookup Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                        $lookup Operation                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  orders collection:                 products collection:            │
│  ┌──────────────────┐              ┌──────────────────┐            │
│  │ _id: 1           │              │ _id: "prod1"     │            │
│  │ productId: "prod1"│──────┐      │ name: "Widget"   │            │
│  │ quantity: 5      │      │      │ price: 25        │            │
│  └──────────────────┘      │      └──────────────────┘            │
│                            │                                       │
│                            ▼                                       │
│  Result:                                                           │
│  ┌──────────────────────────────────────────┐                      │
│  │ _id: 1                                    │                      │
│  │ productId: "prod1"                        │                      │
│  │ quantity: 5                               │                      │
│  │ productDetails: [                         │                      │
│  │   { _id: "prod1", name: "Widget", ... }   │                      │
│  │ ]                                         │                      │
│  └──────────────────────────────────────────┘                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Products collection
db.products.drop()
db.products.insertMany([
  { _id: "prod1", name: "Widget", category: "Electronics", price: 25 },
  { _id: "prod2", name: "Gadget", category: "Electronics", price: 50 },
  { _id: "prod3", name: "Book", category: "Media", price: 15 },
  { _id: "prod4", name: "DVD", category: "Media", price: 10 }
])

// Orders collection
db.orders.drop()
db.orders.insertMany([
  { _id: 1, customerId: "cust1", productId: "prod1", quantity: 5, date: ISODate("2024-01-15") },
  { _id: 2, customerId: "cust1", productId: "prod2", quantity: 2, date: ISODate("2024-01-15") },
  { _id: 3, customerId: "cust2", productId: "prod1", quantity: 10, date: ISODate("2024-01-16") },
  { _id: 4, customerId: "cust2", productId: "prod3", quantity: 3, date: ISODate("2024-01-17") },
  { _id: 5, customerId: "cust3", productId: "prod5", quantity: 1, date: ISODate("2024-01-18") } // Non-existent product
])

// Customers collection
db.customers.drop()
db.customers.insertMany([
  { _id: "cust1", name: "John", email: "john@example.com", tier: "gold" },
  { _id: "cust2", name: "Jane", email: "jane@example.com", tier: "silver" },
  { _id: "cust3", name: "Bob", email: "bob@example.com", tier: "bronze" }
])

// Categories collection
db.categories.drop()
db.categories.insertMany([
  { _id: "Electronics", description: "Electronic devices", tax: 0.10 },
  { _id: "Media", description: "Books and entertainment", tax: 0.05 }
])
```

---

## Basic $lookup

### Simple Join Syntax

```javascript
{
  $lookup: {
    from: "collection",        // Collection to join
    localField: "field",       // Field from input documents
    foreignField: "field",     // Field from joined documents
    as: "outputField"          // Output array field
  }
}
```

### Basic Example

```javascript
// Join orders with products
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  }
])

// Output:
// {
//   _id: 1,
//   customerId: "cust1",
//   productId: "prod1",
//   quantity: 5,
//   date: ...,
//   product: [
//     { _id: "prod1", name: "Widget", category: "Electronics", price: 25 }
//   ]
// }
```

### Unwind Single Match

```javascript
// Flatten single-match arrays
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: "$product" },
  {
    $project: {
      orderId: "$_id",
      productName: "$product.name",
      quantity: 1,
      unitPrice: "$product.price",
      total: { $multiply: ["$quantity", "$product.price"] }
    }
  }
])
```

### Preserve Non-Matches

```javascript
// Keep documents without matches (left outer join)
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  {
    $unwind: {
      path: "$product",
      preserveNullAndEmptyArrays: true
    }
  },
  {
    $project: {
      orderId: "$_id",
      productName: { $ifNull: ["$product.name", "Unknown Product"] },
      quantity: 1,
      hasProduct: { $gt: [{ $size: { $ifNull: [["$product"], []] } }, 0] }
    }
  }
])
```

---

## Uncorrelated Subqueries

### Pipeline Lookup

```javascript
// Advanced lookup with pipeline
{
  $lookup: {
    from: "collection",
    let: { localVar: "$localField" },
    pipeline: [
      // Stages executed in foreign collection
    ],
    as: "outputField"
  }
}
```

### Filtered Join

```javascript
// Only join products in specific category
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { productId: "$productId" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$_id", "$$productId"] },
                { $eq: ["$category", "Electronics"] }
              ]
            }
          }
        }
      ],
      as: "electronicProduct"
    }
  },
  {
    $match: { electronicProduct: { $ne: [] } }
  }
])
```

### Join with Projection

```javascript
// Join only specific fields
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { productId: "$productId" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$_id", "$$productId"] }
          }
        },
        {
          $project: {
            name: 1,
            price: 1,
            _id: 0
          }
        }
      ],
      as: "productInfo"
    }
  },
  { $unwind: "$productInfo" }
])
```

### Join with Aggregation

```javascript
// Get customer with total orders
db.customers.aggregate([
  {
    $lookup: {
      from: "orders",
      let: { customerId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$customerId", "$$customerId"] }
          }
        },
        {
          $group: {
            _id: null,
            orderCount: { $sum: 1 },
            totalQuantity: { $sum: "$quantity" }
          }
        }
      ],
      as: "orderStats"
    }
  },
  {
    $project: {
      name: 1,
      email: 1,
      orderCount: { $ifNull: [{ $arrayElemAt: ["$orderStats.orderCount", 0] }, 0] },
      totalQuantity: { $ifNull: [{ $arrayElemAt: ["$orderStats.totalQuantity", 0] }, 0] }
    }
  }
])
```

---

## Correlated Subqueries

### Range-Based Join

```javascript
// Find orders with products in similar price range
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      let: { orderedProduct: "$productId" },
      pipeline: [
        // First get the ordered product's price
        {
          $match: {
            $expr: { $eq: ["$_id", "$$orderedProduct"] }
          }
        }
      ],
      as: "orderedProductInfo"
    }
  },
  { $unwind: "$orderedProductInfo" },
  {
    $lookup: {
      from: "products",
      let: { 
        productPrice: "$orderedProductInfo.price",
        productId: "$orderedProductInfo._id"
      },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $ne: ["$_id", "$$productId"] },
                { $gte: ["$price", { $multiply: ["$$productPrice", 0.8] }] },
                { $lte: ["$price", { $multiply: ["$$productPrice", 1.2] }] }
              ]
            }
          }
        },
        { $project: { name: 1, price: 1 } }
      ],
      as: "similarProducts"
    }
  },
  {
    $project: {
      orderId: "$_id",
      product: "$orderedProductInfo.name",
      similarProducts: 1
    }
  }
])
```

### Date-Based Join

```javascript
// Get orders with products ordered within same week
db.orders.aggregate([
  {
    $lookup: {
      from: "orders",
      let: { 
        orderDate: "$date",
        orderId: "$_id"
      },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $ne: ["$_id", "$$orderId"] },
                { $gte: ["$date", { $dateSubtract: { startDate: "$$orderDate", unit: "week", amount: 1 } }] },
                { $lte: ["$date", { $dateAdd: { startDate: "$$orderDate", unit: "week", amount: 1 } }] }
              ]
            }
          }
        },
        { $project: { productId: 1, date: 1 } }
      ],
      as: "nearbyOrders"
    }
  }
])
```

---

## Multiple Joins

### Chain Multiple $lookups

```javascript
// Orders with product and customer details
db.orders.aggregate([
  // Join products
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: { path: "$product", preserveNullAndEmptyArrays: true } },
  
  // Join customers
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: { path: "$customer", preserveNullAndEmptyArrays: true } },
  
  // Join categories
  {
    $lookup: {
      from: "categories",
      localField: "product.category",
      foreignField: "_id",
      as: "category"
    }
  },
  { $unwind: { path: "$category", preserveNullAndEmptyArrays: true } },
  
  // Final projection
  {
    $project: {
      orderId: "$_id",
      customerName: "$customer.name",
      customerTier: "$customer.tier",
      productName: "$product.name",
      categoryName: "$product.category",
      quantity: 1,
      unitPrice: "$product.price",
      subtotal: { $multiply: ["$quantity", { $ifNull: ["$product.price", 0] }] },
      tax: {
        $multiply: [
          { $multiply: ["$quantity", { $ifNull: ["$product.price", 0] }] },
          { $ifNull: ["$category.tax", 0] }
        ]
      }
    }
  }
])
```

### Nested Lookups

```javascript
// Products with their orders and order customers
db.products.aggregate([
  {
    $lookup: {
      from: "orders",
      let: { productId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: { $eq: ["$productId", "$$productId"] }
          }
        },
        // Nested lookup for customer info
        {
          $lookup: {
            from: "customers",
            localField: "customerId",
            foreignField: "_id",
            as: "customer"
          }
        },
        { $unwind: "$customer" },
        {
          $project: {
            orderId: "$_id",
            customerName: "$customer.name",
            quantity: 1,
            date: 1
          }
        }
      ],
      as: "orders"
    }
  },
  {
    $project: {
      name: 1,
      category: 1,
      price: 1,
      totalOrders: { $size: "$orders" },
      totalQuantitySold: { $sum: "$orders.quantity" },
      customers: { $setUnion: "$orders.customerName" }
    }
  }
])
```

---

## Join Performance

### Index Requirements

```javascript
// Create indexes on foreign fields
db.products.createIndex({ _id: 1 })  // Usually exists by default
db.orders.createIndex({ productId: 1 })
db.orders.createIndex({ customerId: 1 })

// Compound index for filtered lookups
db.products.createIndex({ category: 1, _id: 1 })
```

### Performance Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                   $lookup Performance Tips                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Index the foreign field                                        │
│     • foreignField should have an index                            │
│     • Dramatically improves join performance                       │
│                                                                     │
│  2. Filter before joining                                          │
│     • Use $match before $lookup                                    │
│     • Reduces documents to join                                    │
│                                                                     │
│  3. Project before joining                                         │
│     • Remove unnecessary fields                                    │
│     • Reduces memory usage                                         │
│                                                                     │
│  4. Consider denormalization                                       │
│     • Frequent joins suggest schema redesign                       │
│     • Embed frequently accessed data                               │
│                                                                     │
│  5. Use allowDiskUse for large joins                               │
│     • Prevents out-of-memory errors                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Optimized Pipeline

```javascript
// ✓ Good: Filter, project, then join
db.orders.aggregate([
  // 1. Filter early
  { $match: { date: { $gte: ISODate("2024-01-16") } } },
  
  // 2. Project only needed fields
  { $project: { productId: 1, quantity: 1 } },
  
  // 3. Join
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  }
])

// ✗ Bad: Join all, then filter
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $match: { date: { $gte: ISODate("2024-01-16") } } }
])
```

### Using allowDiskUse

```javascript
// For large joins
db.orders.aggregate(
  [
    {
      $lookup: {
        from: "products",
        localField: "productId",
        foreignField: "_id",
        as: "product"
      }
    }
  ],
  { allowDiskUse: true }
)
```

---

## $graphLookup for Recursive Queries

### $graphLookup Syntax

```javascript
{
  $graphLookup: {
    from: "collection",
    startWith: "$field",
    connectFromField: "field",
    connectToField: "field",
    as: "outputArray",
    maxDepth: <number>,           // Optional
    depthField: "depthFieldName"  // Optional
  }
}
```

### Hierarchical Data Setup

```javascript
// Employees with manager hierarchy
db.employees.drop()
db.employees.insertMany([
  { _id: 1, name: "CEO", managerId: null, title: "Chief Executive Officer" },
  { _id: 2, name: "CTO", managerId: 1, title: "Chief Technology Officer" },
  { _id: 3, name: "CFO", managerId: 1, title: "Chief Financial Officer" },
  { _id: 4, name: "Dev Lead", managerId: 2, title: "Development Lead" },
  { _id: 5, name: "QA Lead", managerId: 2, title: "QA Lead" },
  { _id: 6, name: "Developer 1", managerId: 4, title: "Senior Developer" },
  { _id: 7, name: "Developer 2", managerId: 4, title: "Junior Developer" },
  { _id: 8, name: "QA Engineer", managerId: 5, title: "QA Engineer" }
])
```

### Find All Subordinates

```javascript
// Find all employees under CTO
db.employees.aggregate([
  { $match: { name: "CTO" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "managerId",
      as: "allReports",
      depthField: "level"
    }
  },
  {
    $project: {
      manager: "$name",
      reports: {
        $map: {
          input: { $sortArray: { input: "$allReports", sortBy: { level: 1 } } },
          in: {
            name: "$$this.name",
            title: "$$this.title",
            level: "$$this.level"
          }
        }
      }
    }
  }
])

// Output:
// {
//   manager: "CTO",
//   reports: [
//     { name: "Dev Lead", title: "Development Lead", level: 0 },
//     { name: "QA Lead", title: "QA Lead", level: 0 },
//     { name: "Developer 1", title: "Senior Developer", level: 1 },
//     { name: "Developer 2", title: "Junior Developer", level: 1 },
//     { name: "QA Engineer", title: "QA Engineer", level: 1 }
//   ]
// }
```

### Find Management Chain

```javascript
// Find all managers above an employee
db.employees.aggregate([
  { $match: { name: "Developer 1" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$managerId",
      connectFromField: "managerId",
      connectToField: "_id",
      as: "managementChain",
      depthField: "level"
    }
  },
  {
    $project: {
      employee: "$name",
      managers: {
        $map: {
          input: { $sortArray: { input: "$managementChain", sortBy: { level: 1 } } },
          in: { name: "$$this.name", title: "$$this.title" }
        }
      }
    }
  }
])
```

### Limited Depth

```javascript
// Only direct reports (1 level)
db.employees.aggregate([
  { $match: { name: "CEO" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "managerId",
      as: "directReports",
      maxDepth: 0  // Only direct reports
    }
  }
])

// 2 levels deep
db.employees.aggregate([
  { $match: { name: "CEO" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "managerId",
      as: "reports",
      maxDepth: 1  // Direct + 1 level down
    }
  }
])
```

---

## Common Join Patterns

### One-to-One

```javascript
// User with profile
db.users.aggregate([
  {
    $lookup: {
      from: "profiles",
      localField: "_id",
      foreignField: "userId",
      as: "profile"
    }
  },
  { $unwind: "$profile" }  // Flatten single document
])
```

### One-to-Many

```javascript
// Customer with orders
db.customers.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "customerId",
      as: "orders"
    }
  }
])  // Keep as array
```

### Many-to-Many

```javascript
// Setup: Students and Courses with enrollment
db.enrollments.drop()
db.enrollments.insertMany([
  { studentId: "s1", courseId: "c1" },
  { studentId: "s1", courseId: "c2" },
  { studentId: "s2", courseId: "c1" }
])

db.students.drop()
db.students.insertMany([
  { _id: "s1", name: "Alice" },
  { _id: "s2", name: "Bob" }
])

db.courses.drop()
db.courses.insertMany([
  { _id: "c1", name: "Math" },
  { _id: "c2", name: "Science" }
])

// Student with enrolled courses
db.students.aggregate([
  {
    $lookup: {
      from: "enrollments",
      localField: "_id",
      foreignField: "studentId",
      as: "enrollments"
    }
  },
  { $unwind: "$enrollments" },
  {
    $lookup: {
      from: "courses",
      localField: "enrollments.courseId",
      foreignField: "_id",
      as: "course"
    }
  },
  { $unwind: "$course" },
  {
    $group: {
      _id: "$_id",
      name: { $first: "$name" },
      courses: { $push: "$course.name" }
    }
  }
])
```

### Self-Join

```javascript
// Products with same category
db.products.aggregate([
  {
    $lookup: {
      from: "products",
      let: { category: "$category", productId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$category", "$$category"] },
                { $ne: ["$_id", "$$productId"] }
              ]
            }
          }
        },
        { $project: { name: 1, price: 1 } }
      ],
      as: "relatedProducts"
    }
  }
])
```

---

## Summary

### $lookup Reference

| Pattern | Syntax |
|---------|--------|
| **Basic** | `{ from, localField, foreignField, as }` |
| **Pipeline** | `{ from, let, pipeline, as }` |
| **Filtered** | Use `$match` in pipeline |
| **Projected** | Use `$project` in pipeline |

### $graphLookup Reference

| Parameter | Description |
|-----------|-------------|
| **from** | Collection to traverse |
| **startWith** | Starting point |
| **connectFromField** | Field containing next values |
| **connectToField** | Field to match against |
| **maxDepth** | Maximum recursion depth |
| **depthField** | Field to store depth |

### Performance Tips

| Tip | Description |
|-----|-------------|
| **Index foreign fields** | Essential for performance |
| **Filter before join** | Reduce documents |
| **Project before join** | Reduce data size |
| **Use allowDiskUse** | For large joins |
| **Consider embedding** | Frequent joins → denormalize |

### What's Next?

In the next chapter, we'll explore $unwind and Array Processing.

---

## Practice Questions

1. What's the difference between basic $lookup and pipeline $lookup?
2. How do you preserve documents without matches in a join?
3. What's the purpose of `let` in pipeline lookups?
4. How does $graphLookup differ from regular $lookup?
5. What indexes should you create for efficient joins?
6. How do you join multiple collections in one pipeline?
7. What is maxDepth in $graphLookup?
8. When should you consider embedding instead of joining?

---

## Hands-On Exercises

### Exercise 1: Basic Joins

```javascript
// Using the sample data:

// 1. Get all orders with product details
db.orders.aggregate([
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: { path: "$product", preserveNullAndEmptyArrays: true } },
  {
    $project: {
      orderId: "$_id",
      productName: { $ifNull: ["$product.name", "Unknown"] },
      quantity: 1,
      unitPrice: "$product.price",
      total: { $multiply: ["$quantity", { $ifNull: ["$product.price", 0] }] }
    }
  }
])

// 2. Get customers with their order count
db.customers.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "customerId",
      as: "orders"
    }
  },
  {
    $project: {
      name: 1,
      email: 1,
      tier: 1,
      orderCount: { $size: "$orders" }
    }
  }
])
```

### Exercise 2: Complex Joins

```javascript
// Full order details with customer, product, and category

db.orders.aggregate([
  // Join products
  {
    $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }
  },
  { $unwind: { path: "$product", preserveNullAndEmptyArrays: true } },
  
  // Join customers
  {
    $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: { path: "$customer", preserveNullAndEmptyArrays: true } },
  
  // Join categories
  {
    $lookup: {
      from: "categories",
      localField: "product.category",
      foreignField: "_id",
      as: "category"
    }
  },
  { $unwind: { path: "$category", preserveNullAndEmptyArrays: true } },
  
  // Calculate totals
  {
    $project: {
      orderId: "$_id",
      customer: {
        name: "$customer.name",
        tier: "$customer.tier"
      },
      product: {
        name: "$product.name",
        category: "$product.category"
      },
      quantity: 1,
      subtotal: { $multiply: ["$quantity", { $ifNull: ["$product.price", 0] }] },
      tax: {
        $multiply: [
          { $multiply: ["$quantity", { $ifNull: ["$product.price", 0] }] },
          { $ifNull: ["$category.tax", 0] }
        ]
      },
      date: 1
    }
  },
  {
    $addFields: {
      total: { $add: ["$subtotal", "$tax"] }
    }
  }
])
```

### Exercise 3: Pipeline Lookup

```javascript
// Get products with their recent orders (last 3 days)

db.products.aggregate([
  {
    $lookup: {
      from: "orders",
      let: { productId: "$_id" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$productId", "$$productId"] },
                { $gte: ["$date", ISODate("2024-01-16")] }
              ]
            }
          }
        },
        { $sort: { date: -1 } },
        { $limit: 5 },
        {
          $lookup: {
            from: "customers",
            localField: "customerId",
            foreignField: "_id",
            as: "customer"
          }
        },
        { $unwind: "$customer" },
        {
          $project: {
            orderId: "$_id",
            customerName: "$customer.name",
            quantity: 1,
            date: 1
          }
        }
      ],
      as: "recentOrders"
    }
  },
  {
    $project: {
      name: 1,
      category: 1,
      price: 1,
      recentOrderCount: { $size: "$recentOrders" },
      recentQuantitySold: { $sum: "$recentOrders.quantity" },
      recentOrders: 1
    }
  }
])
```

### Exercise 4: $graphLookup

```javascript
// Using employees collection:

// 1. Get organization tree from CEO
db.employees.aggregate([
  { $match: { name: "CEO" } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$_id",
      connectFromField: "_id",
      connectToField: "managerId",
      as: "allEmployees",
      depthField: "level"
    }
  },
  {
    $project: {
      ceo: "$name",
      totalEmployees: { $size: "$allEmployees" },
      byLevel: {
        $map: {
          input: { $range: [0, 3] },
          as: "lvl",
          in: {
            level: "$$lvl",
            count: {
              $size: {
                $filter: {
                  input: "$allEmployees",
                  cond: { $eq: ["$$this.level", "$$lvl"] }
                }
              }
            }
          }
        }
      }
    }
  }
])

// 2. Get management chain for each employee
db.employees.aggregate([
  { $match: { managerId: { $ne: null } } },
  {
    $graphLookup: {
      from: "employees",
      startWith: "$managerId",
      connectFromField: "managerId",
      connectToField: "_id",
      as: "managers",
      depthField: "level"
    }
  },
  {
    $project: {
      employee: "$name",
      title: 1,
      managementChain: {
        $map: {
          input: { $sortArray: { input: "$managers", sortBy: { level: 1 } } },
          in: "$$this.name"
        }
      },
      levelsToTop: { $add: [{ $size: "$managers" }, 1] }
    }
  },
  { $sort: { levelsToTop: -1 } }
])
```

### Exercise 5: Performance Optimization

```javascript
// Create indexes for joins
db.products.createIndex({ _id: 1 })
db.orders.createIndex({ productId: 1 })
db.orders.createIndex({ customerId: 1 })
db.orders.createIndex({ date: -1 })

// Optimized query: Electronics orders in January
db.orders.aggregate([
  // Filter by date first
  {
    $match: {
      date: { $gte: ISODate("2024-01-01"), $lt: ISODate("2024-02-01") }
    }
  },
  // Project only needed fields
  { $project: { productId: 1, quantity: 1 } },
  // Join products
  {
    $lookup: {
      from: "products",
      let: { productId: "$productId" },
      pipeline: [
        {
          $match: {
            $expr: {
              $and: [
                { $eq: ["$_id", "$$productId"] },
                { $eq: ["$category", "Electronics"] }
              ]
            }
          }
        },
        { $project: { name: 1, price: 1 } }
      ],
      as: "product"
    }
  },
  // Filter only matched
  { $match: { product: { $ne: [] } } },
  { $unwind: "$product" },
  // Calculate
  {
    $project: {
      product: "$product.name",
      quantity: 1,
      revenue: { $multiply: ["$quantity", "$product.price"] }
    }
  }
])
```

---

[← Previous: $group and Accumulators](24-group-and-accumulators.md) | [Next: $unwind and Array Processing →](26-unwind-and-array-processing.md)
