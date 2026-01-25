# Chapter 65: Views

## Table of Contents
- [Views Overview](#views-overview)
- [Creating Views](#creating-views)
- [View Operations](#view-operations)
- [Advanced View Patterns](#advanced-view-patterns)
- [Materialized Views](#materialized-views)
- [Summary](#summary)

---

## Views Overview

### What are MongoDB Views?

```
┌─────────────────────────────────────────────────────────────────────┐
│                       MongoDB Views Concept                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  A view is a queryable object defined by an aggregation pipeline   │
│  on a source collection. Views are computed dynamically at         │
│  query time - they don't store data themselves.                    │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                Source Collection: orders                     │   │
│  │  ┌─────────────────────────────────────────────────────────┐│   │
│  │  │ { _id: 1, customer: "A", status: "shipped", total: 100 }││   │
│  │  │ { _id: 2, customer: "B", status: "pending", total: 200 }││   │
│  │  │ { _id: 3, customer: "A", status: "shipped", total: 150 }││   │
│  │  └─────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                 View: shippedOrders                          │   │
│  │  Aggregation Pipeline:                                       │   │
│  │  [ { $match: { status: "shipped" } } ]                      │   │
│  │                                                              │   │
│  │  Result when queried:                                        │   │
│  │  ┌─────────────────────────────────────────────────────────┐│   │
│  │  │ { _id: 1, customer: "A", status: "shipped", total: 100 }││   │
│  │  │ { _id: 3, customer: "A", status: "shipped", total: 150 }││   │
│  │  └─────────────────────────────────────────────────────────┘│   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Key Characteristics:                                              │
│  • Read-only (no inserts/updates/deletes)                          │
│  • Computed on-demand at query time                                │
│  • Can be based on collections or other views                      │
│  • Inherits collation from source (if not specified)               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Benefits of Views

| Benefit | Description |
|---------|-------------|
| Data abstraction | Hide complex aggregations |
| Security | Expose only specific fields |
| Simplification | Present data in user-friendly format |
| Consistency | Standardize common queries |
| Maintenance | Change underlying logic without affecting clients |

### Views vs Collections

| Feature | View | Collection |
|---------|------|------------|
| Stores data | ❌ No | ✓ Yes |
| Insert/Update/Delete | ❌ No | ✓ Yes |
| Indexes (direct) | ❌ No | ✓ Yes |
| Computed at query | ✓ Yes | ❌ No |
| Can use aggregation | ✓ Yes (definition) | ✓ Yes (queries) |

---

## Creating Views

### Basic View Creation

```javascript
// Create a simple view
db.createView(
  "activeUsers",           // View name
  "users",                 // Source collection
  [                        // Aggregation pipeline
    { $match: { status: "active" } }
  ]
)

// Query the view like a collection
db.activeUsers.find()
db.activeUsers.find({ role: "admin" })
db.activeUsers.countDocuments()
```

### View with Multiple Pipeline Stages

```javascript
// Create view with projection and transformation
db.createView(
  "customerSummary",
  "customers",
  [
    // Filter active customers
    { $match: { status: "active" } },
    
    // Lookup orders
    { $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "customerId",
      as: "orders"
    }},
    
    // Calculate statistics
    { $project: {
      name: 1,
      email: 1,
      orderCount: { $size: "$orders" },
      totalSpent: { $sum: "$orders.total" },
      avgOrderValue: { $avg: "$orders.total" },
      lastOrderDate: { $max: "$orders.date" }
    }},
    
    // Sort by total spent
    { $sort: { totalSpent: -1 } }
  ]
)
```

### View with Collation

```javascript
// Create view with specific collation
db.createView(
  "sortedProducts",
  "products",
  [
    { $sort: { name: 1 } }
  ],
  {
    collation: { locale: "en", strength: 2 }  // Case-insensitive
  }
)

// Queries on this view use the specified collation
db.sortedProducts.find({ name: "apple" })  // Finds "Apple", "APPLE", etc.
```

### View on View (Nested Views)

```javascript
// Base collection
// users: { name, email, role, department, salary, status }

// First view: active employees
db.createView(
  "activeEmployees",
  "users",
  [
    { $match: { status: "active" } },
    { $project: { 
      name: 1, 
      email: 1, 
      role: 1, 
      department: 1 
    }}
  ]
)

// Second view: built on first view
db.createView(
  "engineeringTeam",
  "activeEmployees",  // Source is the view
  [
    { $match: { department: "engineering" } }
  ]
)

// Query nested view
db.engineeringTeam.find()
```

---

## View Operations

### Querying Views

```javascript
// Views support standard query operations

// Find with filter
db.activeUsers.find({ role: "admin" })

// Find with projection
db.activeUsers.find({}, { name: 1, email: 1 })

// Find with sort and limit
db.activeUsers.find().sort({ createdAt: -1 }).limit(10)

// Count documents
db.activeUsers.countDocuments()
db.activeUsers.countDocuments({ role: "admin" })

// Distinct values
db.activeUsers.distinct("department")

// Aggregation on view
db.activeUsers.aggregate([
  { $group: {
    _id: "$department",
    count: { $sum: 1 }
  }}
])
```

### Explain View Queries

```javascript
// Explain to see how view queries are executed
db.activeUsers.find().explain("executionStats")

// The explain output shows:
// - View pipeline is prepended to query
// - Indexes from source collection are used
// - Optimization by MongoDB query planner
```

### Listing Views

```javascript
// List all views in database
db.getCollectionInfos({ type: "view" })

// Get specific view definition
db.getCollectionInfos({ name: "activeUsers" })

// List views and collections
db.getCollectionNames()

// Check if something is a view
const info = db.getCollectionInfos({ name: "activeUsers" })[0]
if (info && info.type === "view") {
  print("This is a view")
  print("Pipeline:", JSON.stringify(info.options.pipeline))
  print("Source:", info.options.viewOn)
}
```

### Modifying Views

```javascript
// MongoDB doesn't have ALTER VIEW
// You must drop and recreate

// Option 1: Drop and recreate
db.activeUsers.drop()
db.createView("activeUsers", "users", [
  { $match: { status: "active", verified: true } }  // Updated condition
])

// Option 2: Use collMod (change properties but not pipeline)
db.runCommand({
  collMod: "activeUsers",
  viewOn: "users",
  pipeline: [
    { $match: { status: "active", verified: true } }
  ]
})
```

### Dropping Views

```javascript
// Drop a view
db.activeUsers.drop()

// Drop multiple views
["view1", "view2", "view3"].forEach(v => {
  db.getCollection(v).drop()
})
```

---

## Advanced View Patterns

### Security Views (Column-Level Security)

```javascript
// Hide sensitive fields from regular users
db.createView(
  "employeesPublic",
  "employees",
  [
    { $project: {
      name: 1,
      email: 1,
      department: 1,
      title: 1
      // Salary, SSN, personal info excluded
    }}
  ]
)

// Grant read access only to this view
// Users see limited data while collection has full data
```

### Row-Level Security Views

```javascript
// Create department-specific views
function createDepartmentView(department) {
  db.createView(
    `employees_${department.toLowerCase()}`,
    "employees",
    [
      { $match: { department: department } },
      { $project: {
        name: 1,
        email: 1,
        title: 1,
        salary: 1
      }}
    ]
  )
}

createDepartmentView("Engineering")
createDepartmentView("Sales")
createDepartmentView("Marketing")

// Department managers only have access to their view
```

### Denormalized Views

```javascript
// Create denormalized view from normalized collections
db.createView(
  "orderDetails",
  "orders",
  [
    // Lookup customer
    { $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }},
    { $unwind: "$customer" },
    
    // Lookup order items with product details
    { $lookup: {
      from: "orderItems",
      localField: "_id",
      foreignField: "orderId",
      as: "items"
    }},
    
    { $unwind: "$items" },
    
    { $lookup: {
      from: "products",
      localField: "items.productId",
      foreignField: "_id",
      as: "items.product"
    }},
    
    { $unwind: "$items.product" },
    
    // Regroup items
    { $group: {
      _id: "$_id",
      orderDate: { $first: "$orderDate" },
      status: { $first: "$status" },
      customer: { $first: {
        name: "$customer.name",
        email: "$customer.email"
      }},
      items: { $push: {
        productName: "$items.product.name",
        quantity: "$items.quantity",
        unitPrice: "$items.unitPrice",
        lineTotal: { $multiply: ["$items.quantity", "$items.unitPrice"] }
      }},
      total: { $sum: { $multiply: ["$items.quantity", "$items.unitPrice"] } }
    }},
    
    { $sort: { orderDate: -1 } }
  ]
)

// Query denormalized data easily
db.orderDetails.find({ "customer.name": "John Doe" })
```

### Reporting Views

```javascript
// Sales dashboard view
db.createView(
  "salesDashboard",
  "orders",
  [
    { $match: { status: "completed" } },
    
    { $group: {
      _id: {
        year: { $year: "$orderDate" },
        month: { $month: "$orderDate" }
      },
      totalRevenue: { $sum: "$total" },
      orderCount: { $sum: 1 },
      avgOrderValue: { $avg: "$total" },
      uniqueCustomers: { $addToSet: "$customerId" }
    }},
    
    { $project: {
      _id: 0,
      year: "$_id.year",
      month: "$_id.month",
      totalRevenue: { $round: ["$totalRevenue", 2] },
      orderCount: 1,
      avgOrderValue: { $round: ["$avgOrderValue", 2] },
      uniqueCustomerCount: { $size: "$uniqueCustomers" }
    }},
    
    { $sort: { year: -1, month: -1 } }
  ]
)

// Product performance view
db.createView(
  "productPerformance",
  "orderItems",
  [
    { $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }},
    { $unwind: "$product" },
    
    { $group: {
      _id: "$productId",
      productName: { $first: "$product.name" },
      category: { $first: "$product.category" },
      totalSold: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$unitPrice"] } },
      orderCount: { $sum: 1 }
    }},
    
    { $project: {
      productName: 1,
      category: 1,
      totalSold: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      orderCount: 1,
      avgUnitsPerOrder: { 
        $round: [{ $divide: ["$totalSold", "$orderCount"] }, 2] 
      }
    }},
    
    { $sort: { totalRevenue: -1 } }
  ]
)
```

### Union Views (Combining Collections)

```javascript
// Combine activity from multiple collections
db.createView(
  "allActivity",
  "userLogins",
  [
    // Start with logins
    { $project: {
      timestamp: "$loginTime",
      userId: 1,
      activityType: { $literal: "login" },
      details: { ip: "$ipAddress", device: "$deviceType" }
    }},
    
    // Union with purchases
    { $unionWith: {
      coll: "purchases",
      pipeline: [
        { $project: {
          timestamp: "$purchaseDate",
          userId: "$customerId",
          activityType: { $literal: "purchase" },
          details: { amount: "$total", items: "$itemCount" }
        }}
      ]
    }},
    
    // Union with page views
    { $unionWith: {
      coll: "pageViews",
      pipeline: [
        { $project: {
          timestamp: "$viewTime",
          userId: 1,
          activityType: { $literal: "pageView" },
          details: { page: "$pageUrl", duration: "$timeOnPage" }
        }}
      ]
    }},
    
    // Sort by timestamp
    { $sort: { timestamp: -1 } }
  ]
)

// Query unified activity
db.allActivity.find({ userId: "user123" }).limit(50)
```

---

## Materialized Views

### Understanding Materialized Views

```
┌─────────────────────────────────────────────────────────────────────┐
│            Regular View vs Materialized View                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Regular View (On-demand):                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Query → Pipeline executes → Results returned                │   │
│  │  (Computed every time)                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Materialized View (Pre-computed):                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Scheduled Job → Pipeline executes → Results stored          │   │
│  │  Query → Read from stored results → Fast response            │   │
│  │  (Pre-computed, refreshed periodically)                      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Trade-offs:                                                       │
│  • Regular: Always current, slower queries                         │
│  • Materialized: Fast queries, data may be stale                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Creating Materialized Views with $merge

```javascript
// Create materialized view using $merge
function refreshMaterializedView() {
  db.orders.aggregate([
    { $match: { status: "completed" } },
    
    { $group: {
      _id: {
        date: { $dateToString: { format: "%Y-%m-%d", date: "$orderDate" } },
        category: "$category"
      },
      totalSales: { $sum: "$total" },
      orderCount: { $sum: 1 },
      avgOrderValue: { $avg: "$total" }
    }},
    
    { $project: {
      _id: 0,
      date: "$_id.date",
      category: "$_id.category",
      totalSales: { $round: ["$totalSales", 2] },
      orderCount: 1,
      avgOrderValue: { $round: ["$avgOrderValue", 2] },
      lastUpdated: { $literal: new Date() }
    }},
    
    // Write results to materialized view collection
    { $merge: {
      into: "dailySalesSummary",
      on: ["date", "category"],
      whenMatched: "replace",
      whenNotMatched: "insert"
    }}
  ])
}

// Create index on materialized view
db.dailySalesSummary.createIndex({ date: -1 })
db.dailySalesSummary.createIndex({ category: 1 })

// Schedule refresh (run periodically)
refreshMaterializedView()

// Fast queries on materialized view
db.dailySalesSummary.find({
  date: { $gte: "2024-01-01", $lte: "2024-01-31" },
  category: "electronics"
}).sort({ date: -1 })
```

### Incremental Materialized Views

```javascript
// Track last refresh time
db.materializedViewMetadata.insertOne({
  viewName: "salesSummary",
  lastRefreshTime: new Date("2020-01-01")  // Initial
})

// Incremental refresh function
function incrementalRefresh(viewName, targetCollection) {
  // Get last refresh time
  const metadata = db.materializedViewMetadata.findOne({ viewName: viewName })
  const lastRefresh = metadata?.lastRefreshTime || new Date("2020-01-01")
  const now = new Date()
  
  // Only process new/updated records
  db.orders.aggregate([
    { $match: {
      $or: [
        { createdAt: { $gt: lastRefresh } },
        { updatedAt: { $gt: lastRefresh } }
      ]
    }},
    
    { $group: {
      _id: {
        date: { $dateToString: { format: "%Y-%m-%d", date: "$orderDate" } },
        productId: "$productId"
      },
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: "$total" }
    }},
    
    { $merge: {
      into: targetCollection,
      on: ["_id.date", "_id.productId"],
      whenMatched: [
        { $set: {
          totalQuantity: { $add: ["$totalQuantity", "$$new.totalQuantity"] },
          totalRevenue: { $add: ["$totalRevenue", "$$new.totalRevenue"] }
        }}
      ],
      whenNotMatched: "insert"
    }}
  ])
  
  // Update metadata
  db.materializedViewMetadata.updateOne(
    { viewName: viewName },
    { $set: { lastRefreshTime: now } },
    { upsert: true }
  )
  
  return { lastRefresh, processedUntil: now }
}

// Run incremental refresh
incrementalRefresh("salesSummary", "productSalesSummary")
```

### On-Demand Materialized View with $out

```javascript
// Complete replacement materialized view
function createSnapshot() {
  const timestamp = new Date().toISOString().split('T')[0]
  const collectionName = `inventory_snapshot_${timestamp.replace(/-/g, '')}`
  
  db.inventory.aggregate([
    { $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }},
    { $unwind: "$product" },
    
    { $lookup: {
      from: "warehouses",
      localField: "warehouseId",
      foreignField: "_id",
      as: "warehouse"
    }},
    { $unwind: "$warehouse" },
    
    { $project: {
      productName: "$product.name",
      category: "$product.category",
      warehouseName: "$warehouse.name",
      location: "$warehouse.location",
      quantity: 1,
      lastUpdated: 1,
      value: { $multiply: ["$quantity", "$product.unitCost"] },
      snapshotDate: { $literal: new Date() }
    }},
    
    // Write to new collection (replaces if exists)
    { $out: collectionName }
  ])
  
  return collectionName
}

// Create daily snapshot
const snapshotCollection = createSnapshot()
print(`Created snapshot: ${snapshotCollection}`)
```

---

## Summary

### View Types

| Type | Storage | Freshness | Performance |
|------|---------|-----------|-------------|
| Regular View | None | Always current | Query-time computation |
| Materialized ($merge) | Collection | Periodic refresh | Pre-computed, fast |
| Snapshot ($out) | Collection | Point-in-time | Pre-computed, fast |

### View Limitations

| Limitation | Description |
|------------|-------------|
| Read-only | Cannot insert, update, or delete |
| No direct indexes | Relies on source collection indexes |
| Pipeline restrictions | Some operators not allowed |
| Performance | Complex pipelines can be slow |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Use for data abstraction | Simpler client code |
| Security views | Column/row level security |
| Materialized for reports | Fast dashboard queries |
| Index source collections | Optimize view performance |
| Keep pipelines simple | Better query optimization |

---

## Practice Questions

1. What is the difference between a view and a collection?
2. Can you write to a MongoDB view?
3. How do you create a view on another view?
4. What is a materialized view and how is it different?
5. How do you update a view definition?
6. What are security views and how do they work?
7. When would you use $out vs $merge for materialized views?
8. How do indexes work with views?

---

## Hands-On Exercises

### Exercise 1: E-commerce View System

```javascript
// Setup sample data
db.products.insertMany([
  { _id: 1, name: "Laptop", category: "Electronics", price: 999, stock: 50, active: true },
  { _id: 2, name: "Phone", category: "Electronics", price: 699, stock: 100, active: true },
  { _id: 3, name: "Shirt", category: "Clothing", price: 29, stock: 200, active: true },
  { _id: 4, name: "Pants", category: "Clothing", price: 49, stock: 150, active: false }
])

db.orders.insertMany([
  { _id: 1, customerId: 101, productId: 1, quantity: 2, total: 1998, date: new Date("2024-01-15"), status: "completed" },
  { _id: 2, customerId: 102, productId: 2, quantity: 1, total: 699, date: new Date("2024-01-16"), status: "completed" },
  { _id: 3, customerId: 101, productId: 3, quantity: 3, total: 87, date: new Date("2024-01-17"), status: "pending" },
  { _id: 4, customerId: 103, productId: 1, quantity: 1, total: 999, date: new Date("2024-01-18"), status: "completed" }
])

db.customers.insertMany([
  { _id: 101, name: "Alice", email: "alice@example.com", tier: "gold" },
  { _id: 102, name: "Bob", email: "bob@example.com", tier: "silver" },
  { _id: 103, name: "Charlie", email: "charlie@example.com", tier: "bronze" }
])

// Create views

// 1. Active products view
db.createView(
  "activeProducts",
  "products",
  [
    { $match: { active: true, stock: { $gt: 0 } } },
    { $project: {
      name: 1,
      category: 1,
      price: 1,
      inStock: { $gt: ["$stock", 0] }
    }}
  ]
)

// 2. Order details view (denormalized)
db.createView(
  "orderDetails",
  "orders",
  [
    { $lookup: {
      from: "customers",
      localField: "customerId",
      foreignField: "_id",
      as: "customer"
    }},
    { $unwind: "$customer" },
    
    { $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }},
    { $unwind: "$product" },
    
    { $project: {
      orderDate: "$date",
      status: 1,
      customerName: "$customer.name",
      customerEmail: "$customer.email",
      customerTier: "$customer.tier",
      productName: "$product.name",
      productCategory: "$product.category",
      quantity: 1,
      unitPrice: "$product.price",
      total: 1
    }}
  ]
)

// 3. Customer summary view
db.createView(
  "customerSummary",
  "orders",
  [
    { $match: { status: "completed" } },
    { $group: {
      _id: "$customerId",
      orderCount: { $sum: 1 },
      totalSpent: { $sum: "$total" },
      lastOrderDate: { $max: "$date" }
    }},
    
    { $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "_id",
      as: "customer"
    }},
    { $unwind: "$customer" },
    
    { $project: {
      _id: 0,
      customerId: "$_id",
      name: "$customer.name",
      email: "$customer.email",
      tier: "$customer.tier",
      orderCount: 1,
      totalSpent: 1,
      avgOrderValue: { $round: [{ $divide: ["$totalSpent", "$orderCount"] }, 2] },
      lastOrderDate: 1
    }},
    
    { $sort: { totalSpent: -1 } }
  ]
)

// 4. Category performance view
db.createView(
  "categoryPerformance",
  "orders",
  [
    { $match: { status: "completed" } },
    
    { $lookup: {
      from: "products",
      localField: "productId",
      foreignField: "_id",
      as: "product"
    }},
    { $unwind: "$product" },
    
    { $group: {
      _id: "$product.category",
      totalRevenue: { $sum: "$total" },
      totalOrders: { $sum: 1 },
      totalUnits: { $sum: "$quantity" },
      uniqueProducts: { $addToSet: "$productId" }
    }},
    
    { $project: {
      _id: 0,
      category: "$_id",
      totalRevenue: 1,
      totalOrders: 1,
      totalUnits: 1,
      productCount: { $size: "$uniqueProducts" },
      avgRevenuePerOrder: { $round: [{ $divide: ["$totalRevenue", "$totalOrders"] }, 2] }
    }},
    
    { $sort: { totalRevenue: -1 } }
  ]
)

// Test views
print("\n=== Active Products ===")
printjson(db.activeProducts.find().toArray())

print("\n=== Order Details ===")
printjson(db.orderDetails.find().toArray())

print("\n=== Customer Summary ===")
printjson(db.customerSummary.find().toArray())

print("\n=== Category Performance ===")
printjson(db.categoryPerformance.find().toArray())
```

### Exercise 2: View Management Utility

```javascript
// View management functions

const ViewManager = {
  // List all views with details
  listViews() {
    const views = db.getCollectionInfos({ type: "view" })
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                   DATABASE VIEWS                            ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    if (views.length === 0) {
      print("No views found in this database.")
      return []
    }
    
    views.forEach(view => {
      print(`┌─ ${view.name} ───────────────────────────────────────────`)
      print(`│  Source: ${view.options.viewOn}`)
      print(`│  Pipeline stages: ${view.options.pipeline.length}`)
      
      view.options.pipeline.forEach((stage, i) => {
        const stageOp = Object.keys(stage)[0]
        print(`│    ${i + 1}. ${stageOp}`)
      })
      
      if (view.options.collation) {
        print(`│  Collation: ${JSON.stringify(view.options.collation)}`)
      }
      
      print("└────────────────────────────────────────────────────────────\n")
    })
    
    return views
  },
  
  // Get view definition
  getDefinition(viewName) {
    const views = db.getCollectionInfos({ name: viewName })
    if (views.length === 0 || views[0].type !== "view") {
      return null
    }
    return {
      name: viewName,
      source: views[0].options.viewOn,
      pipeline: views[0].options.pipeline,
      collation: views[0].options.collation
    }
  },
  
  // Validate view
  validateView(viewName) {
    const view = db.getCollection(viewName)
    
    try {
      // Try to query the view
      const result = view.findOne()
      
      // Get execution stats
      const explain = view.find().limit(100).explain("executionStats")
      
      return {
        valid: true,
        sampleDocument: result,
        executionTimeMs: explain.executionStats?.executionTimeMillis,
        documentsExamined: explain.executionStats?.totalDocsExamined
      }
    } catch (error) {
      return {
        valid: false,
        error: error.message
      }
    }
  },
  
  // Clone view with new name
  cloneView(sourceName, newName) {
    const def = this.getDefinition(sourceName)
    
    if (!def) {
      throw new Error(`View ${sourceName} not found`)
    }
    
    const options = {}
    if (def.collation) {
      options.collation = def.collation
    }
    
    db.createView(newName, def.source, def.pipeline, options)
    return true
  },
  
  // Export view definition as JSON
  exportDefinition(viewName) {
    const def = this.getDefinition(viewName)
    if (!def) {
      return null
    }
    
    return JSON.stringify({
      createView: viewName,
      viewOn: def.source,
      pipeline: def.pipeline,
      collation: def.collation
    }, null, 2)
  },
  
  // Import view from JSON definition
  importDefinition(jsonDef) {
    const def = typeof jsonDef === 'string' ? JSON.parse(jsonDef) : jsonDef
    
    const options = {}
    if (def.collation) {
      options.collation = def.collation
    }
    
    db.createView(def.createView, def.viewOn, def.pipeline, options)
    return true
  },
  
  // Dependency tree
  getDependencyTree(viewName) {
    const tree = {}
    const visited = new Set()
    
    function traverse(name, depth = 0) {
      if (visited.has(name)) return null
      visited.add(name)
      
      const info = db.getCollectionInfos({ name: name })[0]
      
      if (!info) {
        return { name, type: "missing", depth }
      }
      
      if (info.type === "view") {
        return {
          name,
          type: "view",
          depth,
          source: traverse(info.options.viewOn, depth + 1)
        }
      } else {
        return { name, type: "collection", depth }
      }
    }
    
    return traverse(viewName)
  }
}

// Test view manager
print("View List:")
ViewManager.listViews()

print("\nView Definition (orderDetails):")
printjson(ViewManager.getDefinition("orderDetails"))

print("\nView Validation (customerSummary):")
printjson(ViewManager.validateView("customerSummary"))

print("\nDependency Tree (orderDetails):")
printjson(ViewManager.getDependencyTree("orderDetails"))
```

### Exercise 3: Materialized View Refresh System

```javascript
// Materialized view management system

const MaterializedViewManager = {
  // Metadata collection
  metadataCollection: "mv_metadata",
  
  // Register a materialized view
  register(viewName, sourceCollection, pipeline, options = {}) {
    const {
      refreshInterval = 3600000,  // 1 hour default
      incrementalField = null,
      mergeOn = "_id"
    } = options
    
    db.getCollection(this.metadataCollection).updateOne(
      { viewName: viewName },
      {
        $set: {
          viewName: viewName,
          sourceCollection: sourceCollection,
          targetCollection: `mv_${viewName}`,
          pipeline: pipeline,
          mergeOn: mergeOn,
          incrementalField: incrementalField,
          refreshInterval: refreshInterval,
          createdAt: new Date(),
          lastRefresh: null,
          refreshCount: 0,
          status: "registered"
        }
      },
      { upsert: true }
    )
    
    print(`Registered materialized view: ${viewName}`)
    return true
  },
  
  // Full refresh
  fullRefresh(viewName) {
    const meta = db.getCollection(this.metadataCollection).findOne({ viewName: viewName })
    
    if (!meta) {
      throw new Error(`Materialized view ${viewName} not registered`)
    }
    
    const startTime = new Date()
    
    // Execute pipeline with $merge
    const pipeline = [
      ...meta.pipeline,
      {
        $merge: {
          into: meta.targetCollection,
          on: meta.mergeOn,
          whenMatched: "replace",
          whenNotMatched: "insert"
        }
      }
    ]
    
    db.getCollection(meta.sourceCollection).aggregate(pipeline)
    
    const endTime = new Date()
    const duration = endTime - startTime
    
    // Update metadata
    db.getCollection(this.metadataCollection).updateOne(
      { viewName: viewName },
      {
        $set: {
          lastRefresh: endTime,
          lastRefreshDuration: duration,
          status: "active"
        },
        $inc: { refreshCount: 1 }
      }
    )
    
    print(`Refreshed ${viewName} in ${duration}ms`)
    return { duration, timestamp: endTime }
  },
  
  // Incremental refresh
  incrementalRefresh(viewName) {
    const meta = db.getCollection(this.metadataCollection).findOne({ viewName: viewName })
    
    if (!meta) {
      throw new Error(`Materialized view ${viewName} not registered`)
    }
    
    if (!meta.incrementalField) {
      throw new Error(`No incremental field configured for ${viewName}`)
    }
    
    const lastRefresh = meta.lastRefresh || new Date(0)
    const startTime = new Date()
    
    // Add filter for incremental
    const pipeline = [
      { $match: { [meta.incrementalField]: { $gt: lastRefresh } } },
      ...meta.pipeline,
      {
        $merge: {
          into: meta.targetCollection,
          on: meta.mergeOn,
          whenMatched: "merge",
          whenNotMatched: "insert"
        }
      }
    ]
    
    db.getCollection(meta.sourceCollection).aggregate(pipeline)
    
    const endTime = new Date()
    
    db.getCollection(this.metadataCollection).updateOne(
      { viewName: viewName },
      {
        $set: {
          lastRefresh: endTime,
          lastRefreshDuration: endTime - startTime,
          status: "active"
        },
        $inc: { refreshCount: 1 }
      }
    )
    
    return { duration: endTime - startTime, timestamp: endTime }
  },
  
  // Get status of all materialized views
  status() {
    const views = db.getCollection(this.metadataCollection).find().toArray()
    
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           MATERIALIZED VIEWS STATUS                         ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    views.forEach(v => {
      const targetStats = db.getCollection(v.targetCollection).stats()
      const docCount = db.getCollection(v.targetCollection).countDocuments()
      const staleness = v.lastRefresh 
        ? Math.round((new Date() - v.lastRefresh) / 60000) 
        : "Never refreshed"
      
      print(`┌─ ${v.viewName} ───────────────────────────────────────────`)
      print(`│  Target: ${v.targetCollection}`)
      print(`│  Status: ${v.status}`)
      print(`│  Documents: ${docCount}`)
      print(`│  Size: ${(targetStats.size / 1024).toFixed(2)} KB`)
      print(`│  Last Refresh: ${v.lastRefresh?.toISOString() || 'Never'}`)
      print(`│  Staleness: ${staleness} ${typeof staleness === 'number' ? 'minutes' : ''}`)
      print(`│  Refresh Count: ${v.refreshCount}`)
      print("└────────────────────────────────────────────────────────────\n")
    })
    
    return views
  },
  
  // Query materialized view
  query(viewName, filter = {}, options = {}) {
    const meta = db.getCollection(this.metadataCollection).findOne({ viewName: viewName })
    
    if (!meta) {
      throw new Error(`Materialized view ${viewName} not found`)
    }
    
    return db.getCollection(meta.targetCollection)
      .find(filter, options)
      .toArray()
  },
  
  // Drop materialized view
  drop(viewName) {
    const meta = db.getCollection(this.metadataCollection).findOne({ viewName: viewName })
    
    if (meta) {
      db.getCollection(meta.targetCollection).drop()
      db.getCollection(this.metadataCollection).deleteOne({ viewName: viewName })
      print(`Dropped materialized view: ${viewName}`)
      return true
    }
    
    return false
  }
}

// Demo

// Register a materialized view
MaterializedViewManager.register(
  "dailySales",
  "orders",
  [
    { $match: { status: "completed" } },
    { $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
      totalRevenue: { $sum: "$total" },
      orderCount: { $sum: 1 }
    }},
    { $project: {
      _id: 0,
      date: "$_id",
      totalRevenue: 1,
      orderCount: 1,
      avgOrderValue: { $divide: ["$totalRevenue", "$orderCount"] }
    }}
  ],
  {
    refreshInterval: 3600000,
    mergeOn: "date"
  }
)

// Full refresh
MaterializedViewManager.fullRefresh("dailySales")

// Show status
MaterializedViewManager.status()

// Query the materialized view
print("\nMaterialized View Data:")
printjson(MaterializedViewManager.query("dailySales"))
```

---

[← Previous: Capped Collections](64-capped-collections.md) | [Next: Driver Best Practices →](66-driver-best-practices.md)
