# Chapter 23: Aggregation Pipeline Basics

## Table of Contents
- [Introduction to Aggregation](#introduction-to-aggregation)
- [Pipeline Concept](#pipeline-concept)
- [Basic Pipeline Stages](#basic-pipeline-stages)
- [$match Stage](#match-stage)
- [$project Stage](#project-stage)
- [$sort Stage](#sort-stage)
- [$limit and $skip Stages](#limit-and-skip-stages)
- [$count Stage](#count-stage)
- [Pipeline Order and Optimization](#pipeline-order-and-optimization)
- [Summary](#summary)

---

## Introduction to Aggregation

The aggregation framework is MongoDB's data processing pipeline for transforming and analyzing data. It processes documents through a series of stages.

### Aggregation vs Find

```
┌─────────────────────────────────────────────────────────────────────┐
│              find() vs aggregate() Comparison                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  find()                                                             │
│  ├── Filter documents                                              │
│  ├── Project fields                                                │
│  ├── Sort results                                                  │
│  └── Limit/skip                                                    │
│                                                                     │
│  aggregate()                                                        │
│  ├── All find() capabilities, plus:                                │
│  ├── Group documents                                               │
│  ├── Calculate totals, averages                                    │
│  ├── Join collections                                              │
│  ├── Reshape documents                                             │
│  ├── Create computed fields                                        │
│  ├── Unwind arrays                                                 │
│  └── Window functions                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic Syntax

```javascript
db.collection.aggregate([
  { $stage1: { /* stage definition */ } },
  { $stage2: { /* stage definition */ } },
  { $stage3: { /* stage definition */ } }
])
```

---

## Pipeline Concept

### Pipeline Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Aggregation Pipeline Flow                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Collection                                                         │
│      │                                                             │
│      ▼                                                             │
│  ┌──────────┐                                                      │
│  │ $match   │ ──► Filter documents                                 │
│  └────┬─────┘                                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌──────────┐                                                      │
│  │ $project │ ──► Transform/reshape documents                      │
│  └────┬─────┘                                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌──────────┐                                                      │
│  │ $group   │ ──► Aggregate by key                                 │
│  └────┬─────┘                                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌──────────┐                                                      │
│  │ $sort    │ ──► Order results                                    │
│  └────┬─────┘                                                      │
│       │                                                            │
│       ▼                                                            │
│   Results                                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Setup sample data
db.orders.drop()
db.orders.insertMany([
  {
    _id: 1,
    customer: "John",
    status: "completed",
    items: [
      { product: "Widget", quantity: 2, price: 25.00 },
      { product: "Gadget", quantity: 1, price: 50.00 }
    ],
    total: 100.00,
    date: ISODate("2024-01-15")
  },
  {
    _id: 2,
    customer: "Jane",
    status: "completed",
    items: [
      { product: "Widget", quantity: 5, price: 25.00 }
    ],
    total: 125.00,
    date: ISODate("2024-01-16")
  },
  {
    _id: 3,
    customer: "John",
    status: "pending",
    items: [
      { product: "Gizmo", quantity: 3, price: 30.00 }
    ],
    total: 90.00,
    date: ISODate("2024-01-17")
  },
  {
    _id: 4,
    customer: "Bob",
    status: "completed",
    items: [
      { product: "Gadget", quantity: 2, price: 50.00 },
      { product: "Widget", quantity: 1, price: 25.00 }
    ],
    total: 125.00,
    date: ISODate("2024-01-17")
  },
  {
    _id: 5,
    customer: "Jane",
    status: "cancelled",
    items: [
      { product: "Gizmo", quantity: 1, price: 30.00 }
    ],
    total: 30.00,
    date: ISODate("2024-01-18")
  }
])
```

---

## Basic Pipeline Stages

### Stage Types Overview

| Stage | Description |
|-------|-------------|
| `$match` | Filter documents |
| `$project` | Reshape documents |
| `$group` | Aggregate by key |
| `$sort` | Order results |
| `$limit` | Limit results |
| `$skip` | Skip documents |
| `$count` | Count documents |
| `$unwind` | Deconstruct arrays |
| `$lookup` | Join collections |
| `$addFields` | Add new fields |

### Simple Pipeline Example

```javascript
// Find completed orders, show customer and total, sorted by total
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $project: { customer: 1, total: 1, _id: 0 } },
  { $sort: { total: -1 } }
])

// Output:
// { customer: "Jane", total: 125 }
// { customer: "Bob", total: 125 }
// { customer: "John", total: 100 }
```

---

## $match Stage

### Basic Filtering

```javascript
// Filter by single field
db.orders.aggregate([
  { $match: { status: "completed" } }
])

// Multiple conditions (AND)
db.orders.aggregate([
  { 
    $match: { 
      status: "completed",
      total: { $gte: 100 }
    } 
  }
])

// OR conditions
db.orders.aggregate([
  {
    $match: {
      $or: [
        { status: "completed" },
        { total: { $gt: 100 } }
      ]
    }
  }
])
```

### Using Query Operators

```javascript
// Comparison operators
db.orders.aggregate([
  { $match: { total: { $gte: 100, $lte: 150 } } }
])

// Array contains
db.orders.aggregate([
  { $match: { "items.product": "Widget" } }
])

// Date range
db.orders.aggregate([
  {
    $match: {
      date: {
        $gte: ISODate("2024-01-16"),
        $lt: ISODate("2024-01-18")
      }
    }
  }
])

// Regular expression
db.orders.aggregate([
  { $match: { customer: /^J/ } }
])
```

### $match Performance

```javascript
// ✓ Good: $match early in pipeline (uses index)
db.orders.aggregate([
  { $match: { status: "completed" } },  // Uses index
  { $project: { customer: 1, total: 1 } }
])

// ✗ Less efficient: $match after transformations
db.orders.aggregate([
  { $project: { customer: 1, total: 1, status: 1 } },
  { $match: { status: "completed" } }  // After $project
])

// $match at start can use indexes
db.orders.createIndex({ status: 1 })
```

---

## $project Stage

### Field Selection

```javascript
// Include fields (1) and exclude (0)
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      total: 1,
      date: 1,
      _id: 0  // Exclude _id
    }
  }
])

// Exclude specific fields
db.orders.aggregate([
  {
    $project: {
      items: 0,
      _id: 0
    }
  }
])
```

### Field Renaming

```javascript
// Rename fields
db.orders.aggregate([
  {
    $project: {
      customerName: "$customer",
      orderTotal: "$total",
      orderDate: "$date"
    }
  }
])

// Output:
// { customerName: "John", orderTotal: 100, orderDate: ISODate("...") }
```

### Computed Fields

```javascript
// Add calculated fields
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      total: 1,
      tax: { $multiply: ["$total", 0.08] },
      grandTotal: { $multiply: ["$total", 1.08] }
    }
  }
])

// String manipulation
db.orders.aggregate([
  {
    $project: {
      customer: { $toUpper: "$customer" },
      status: { $concat: ["Status: ", "$status"] }
    }
  }
])

// Conditional fields
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      total: 1,
      category: {
        $cond: {
          if: { $gte: ["$total", 100] },
          then: "High Value",
          else: "Standard"
        }
      }
    }
  }
])
```

### Nested Field Access

```javascript
// Access nested fields
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      firstItem: { $arrayElemAt: ["$items", 0] },
      itemCount: { $size: "$items" }
    }
  }
])

// Restructure embedded documents
db.orders.aggregate([
  {
    $project: {
      orderInfo: {
        customer: "$customer",
        date: "$date"
      },
      financials: {
        subtotal: "$total",
        tax: { $multiply: ["$total", 0.08] }
      }
    }
  }
])
```

---

## $sort Stage

### Basic Sorting

```javascript
// Ascending sort
db.orders.aggregate([
  { $sort: { total: 1 } }
])

// Descending sort
db.orders.aggregate([
  { $sort: { total: -1 } }
])

// Multiple fields
db.orders.aggregate([
  { $sort: { status: 1, total: -1 } }
])
```

### Sort with Index

```javascript
// Sort uses index when:
// 1. $sort is early in pipeline
// 2. Preceded only by $match on same index

db.orders.createIndex({ status: 1, total: -1 })

// Uses index for sort
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { total: -1 } }
])
```

### Sort Memory Limit

```javascript
// Default: 100MB memory limit for sort
// For larger sorts, allow disk use:
db.orders.aggregate(
  [
    { $sort: { total: -1 } }
  ],
  { allowDiskUse: true }
)
```

---

## $limit and $skip Stages

### $limit

```javascript
// Get top 3 orders by total
db.orders.aggregate([
  { $sort: { total: -1 } },
  { $limit: 3 }
])
```

### $skip

```javascript
// Skip first 2 documents
db.orders.aggregate([
  { $sort: { total: -1 } },
  { $skip: 2 }
])
```

### Pagination

```javascript
// Pagination pattern
function getOrdersPage(page, pageSize) {
  const skip = (page - 1) * pageSize
  
  return db.orders.aggregate([
    { $match: { status: "completed" } },
    { $sort: { date: -1 } },
    { $skip: skip },
    { $limit: pageSize },
    { $project: { customer: 1, total: 1, date: 1 } }
  ]).toArray()
}

// Get page 1 (first 10)
getOrdersPage(1, 10)

// Get page 2 (next 10)
getOrdersPage(2, 10)
```

### Efficient Pagination

```javascript
// Better: Range-based pagination (for large datasets)
function getOrdersAfter(lastDate, lastId, limit) {
  return db.orders.aggregate([
    {
      $match: {
        $or: [
          { date: { $lt: lastDate } },
          { 
            date: lastDate,
            _id: { $gt: lastId }
          }
        ]
      }
    },
    { $sort: { date: -1, _id: 1 } },
    { $limit: limit }
  ]).toArray()
}
```

---

## $count Stage

### Basic Count

```javascript
// Count all documents
db.orders.aggregate([
  { $count: "totalOrders" }
])
// Output: { totalOrders: 5 }

// Count with filter
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $count: "completedOrders" }
])
// Output: { completedOrders: 3 }
```

### Count Alternatives

```javascript
// Using $group
db.orders.aggregate([
  {
    $group: {
      _id: null,
      count: { $sum: 1 }
    }
  }
])

// Multiple counts
db.orders.aggregate([
  {
    $group: {
      _id: null,
      total: { $sum: 1 },
      completed: {
        $sum: { $cond: [{ $eq: ["$status", "completed"] }, 1, 0] }
      },
      pending: {
        $sum: { $cond: [{ $eq: ["$status", "pending"] }, 1, 0] }
      }
    }
  }
])
```

---

## Pipeline Order and Optimization

### Optimal Pipeline Order

```javascript
// ✓ Optimized pipeline
db.orders.aggregate([
  { $match: { status: "completed" } },  // 1. Filter early
  { $sort: { total: -1 } },              // 2. Sort (can use index)
  { $limit: 10 },                         // 3. Limit early
  {                                       // 4. Project last
    $project: {
      customer: 1,
      total: 1,
      date: 1
    }
  }
])

// ✗ Less optimized
db.orders.aggregate([
  { $project: { customer: 1, total: 1, status: 1 } },
  { $sort: { total: -1 } },
  { $match: { status: "completed" } },  // Match after project
  { $limit: 10 }
])
```

### Pipeline Optimization Rules

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Pipeline Optimization Rules                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. $match as early as possible                                    │
│     • Reduces documents for subsequent stages                      │
│     • Can use indexes                                              │
│                                                                     │
│  2. $sort + $limit together                                        │
│     • MongoDB optimizes to top-k sort                              │
│                                                                     │
│  3. $project/$addFields late                                       │
│     • Don't block index usage                                      │
│                                                                     │
│  4. Multiple $match stages                                         │
│     • MongoDB combines adjacent $match stages                      │
│                                                                     │
│  5. Avoid unnecessary stages                                       │
│     • Each stage has overhead                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### View Explain Plan

```javascript
// See how MongoDB executes pipeline
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { total: -1 } },
  { $limit: 5 }
]).explain("executionStats")
```

---

## Summary

### Basic Stages

| Stage | Purpose |
|-------|---------|
| **$match** | Filter documents |
| **$project** | Reshape/compute fields |
| **$sort** | Order results |
| **$limit** | Limit output |
| **$skip** | Skip documents |
| **$count** | Count documents |

### Key Principles

| Principle | Description |
|-----------|-------------|
| **Early filtering** | $match first for performance |
| **Index usage** | $match/$sort can use indexes |
| **Memory limits** | allowDiskUse for large sorts |
| **Pipeline order** | Order affects performance |

### What's Next?

In the next chapter, we'll explore $group and Accumulator Operators.

---

## Practice Questions

1. What's the difference between find() and aggregate()?
2. Why should $match be early in the pipeline?
3. How do you rename fields in $project?
4. What's the memory limit for $sort?
5. How do you implement pagination with aggregation?
6. What's the difference between $limit before and after $sort?
7. How do you see the aggregation explain plan?
8. What optimizations does MongoDB apply automatically?

---

## Hands-On Exercises

### Exercise 1: Basic Pipeline

```javascript
// Using the orders data, create pipelines:

// 1. Find all completed orders, show only customer and total
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $project: { customer: 1, total: 1, _id: 0 } }
])

// 2. Find orders over $100, sorted by date
db.orders.aggregate([
  { $match: { total: { $gt: 100 } } },
  { $sort: { date: -1 } },
  { $project: { customer: 1, total: 1, date: 1 } }
])

// 3. Get the 2 most recent orders
db.orders.aggregate([
  { $sort: { date: -1 } },
  { $limit: 2 },
  { $project: { customer: 1, date: 1, total: 1 } }
])
```

### Exercise 2: Computed Fields

```javascript
// Add computed fields

// 1. Add tax (8%) and grand total
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      subtotal: "$total",
      tax: { $round: [{ $multiply: ["$total", 0.08] }, 2] },
      grandTotal: { $round: [{ $multiply: ["$total", 1.08] }, 2] }
    }
  }
])

// 2. Categorize orders by value
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      total: 1,
      tier: {
        $switch: {
          branches: [
            { case: { $gte: ["$total", 150] }, then: "Premium" },
            { case: { $gte: ["$total", 100] }, then: "Standard" }
          ],
          default: "Basic"
        }
      }
    }
  }
])

// 3. Format date and uppercase customer name
db.orders.aggregate([
  {
    $project: {
      customerName: { $toUpper: "$customer" },
      orderDate: { 
        $dateToString: { 
          format: "%Y-%m-%d", 
          date: "$date" 
        } 
      },
      total: 1
    }
  }
])
```

### Exercise 3: Pagination

```javascript
// Implement pagination for orders

// Page function
function getOrderPage(status, page, pageSize) {
  return db.orders.aggregate([
    { $match: { status: status } },
    { $sort: { date: -1, _id: 1 } },
    { $skip: (page - 1) * pageSize },
    { $limit: pageSize },
    {
      $project: {
        customer: 1,
        total: 1,
        date: { $dateToString: { format: "%Y-%m-%d", date: "$date" } }
      }
    }
  ]).toArray()
}

// Test
print("Page 1:")
printjson(getOrderPage("completed", 1, 2))

print("\nPage 2:")
printjson(getOrderPage("completed", 2, 2))
```

### Exercise 4: Multiple Counts

```javascript
// Get various statistics in single pipeline

db.orders.aggregate([
  {
    $facet: {
      // Total orders
      "totalOrders": [
        { $count: "count" }
      ],
      // Orders by status
      "byStatus": [
        { $group: { _id: "$status", count: { $sum: 1 } } }
      ],
      // Revenue stats
      "revenue": [
        {
          $group: {
            _id: null,
            totalRevenue: { $sum: "$total" },
            avgOrder: { $avg: "$total" },
            minOrder: { $min: "$total" },
            maxOrder: { $max: "$total" }
          }
        }
      ]
    }
  }
])
```

### Exercise 5: Pipeline Optimization

```javascript
// Compare optimized vs non-optimized pipelines

// Non-optimized (project before match)
print("Non-optimized:")
const start1 = new Date()
db.orders.aggregate([
  { $project: { customer: 1, total: 1, status: 1 } },
  { $match: { status: "completed" } },
  { $sort: { total: -1 } }
]).toArray()
print("Time:", new Date() - start1, "ms")

// Optimized (match first)
print("\nOptimized:")
const start2 = new Date()
db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { total: -1 } },
  { $project: { customer: 1, total: 1 } }
]).toArray()
print("Time:", new Date() - start2, "ms")

// View explain
print("\nOptimized explain:")
const plan = db.orders.aggregate([
  { $match: { status: "completed" } },
  { $sort: { total: -1 } },
  { $project: { customer: 1, total: 1 } }
]).explain()
print("Uses index:", plan.stages[0].$cursor?.queryPlanner?.winningPlan?.inputStage?.indexName || "COLLSCAN")
```

---

[← Previous: Index Management](22-index-management.md) | [Next: $group and Accumulators →](24-group-and-accumulators.md)
