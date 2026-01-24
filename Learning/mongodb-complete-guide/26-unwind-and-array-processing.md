# Chapter 26: $unwind and Array Processing

## Table of Contents
- [Introduction to $unwind](#introduction-to-unwind)
- [Basic $unwind](#basic-unwind)
- [Preserving Empty Arrays](#preserving-empty-arrays)
- [Array Index](#array-index)
- [Unwinding Nested Arrays](#unwinding-nested-arrays)
- [Array Operators in Aggregation](#array-operators-in-aggregation)
- [Grouping After Unwind](#grouping-after-unwind)
- [Common Patterns](#common-patterns)
- [Summary](#summary)

---

## Introduction to $unwind

The `$unwind` stage deconstructs an array field, creating a separate document for each array element.

### $unwind Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                       $unwind Operation                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Input Document:                                                    │
│  ┌─────────────────────────────────────────┐                       │
│  │ _id: 1                                   │                       │
│  │ customer: "John"                         │                       │
│  │ items: ["Widget", "Gadget", "Book"]     │                       │
│  └─────────────────────────────────────────┘                       │
│                                                                     │
│                    $unwind: "$items"                                │
│                           │                                         │
│                           ▼                                         │
│                                                                     │
│  Output Documents:                                                  │
│  ┌──────────────────────────┐                                      │
│  │ _id: 1                    │                                      │
│  │ customer: "John"          │                                      │
│  │ items: "Widget"          │                                      │
│  └──────────────────────────┘                                      │
│  ┌──────────────────────────┐                                      │
│  │ _id: 1                    │                                      │
│  │ customer: "John"          │                                      │
│  │ items: "Gadget"          │                                      │
│  └──────────────────────────┘                                      │
│  ┌──────────────────────────┐                                      │
│  │ _id: 1                    │                                      │
│  │ customer: "John"          │                                      │
│  │ items: "Book"            │                                      │
│  └──────────────────────────┘                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Orders with items array
db.orders.drop()
db.orders.insertMany([
  {
    _id: 1,
    customer: "John",
    date: ISODate("2024-01-15"),
    items: [
      { product: "Widget", quantity: 2, price: 25 },
      { product: "Gadget", quantity: 1, price: 50 }
    ],
    tags: ["electronics", "sale"]
  },
  {
    _id: 2,
    customer: "Jane",
    date: ISODate("2024-01-16"),
    items: [
      { product: "Book", quantity: 3, price: 15 }
    ],
    tags: ["media"]
  },
  {
    _id: 3,
    customer: "Bob",
    date: ISODate("2024-01-17"),
    items: [],  // Empty array
    tags: []
  },
  {
    _id: 4,
    customer: "Alice",
    date: ISODate("2024-01-18"),
    items: [
      { product: "DVD", quantity: 5, price: 10 },
      { product: "CD", quantity: 10, price: 5 },
      { product: "Book", quantity: 2, price: 15 }
    ],
    tags: ["media", "sale", "clearance"]
  }
])
```

---

## Basic $unwind

### Simple Syntax

```javascript
// Short form
{ $unwind: "$arrayField" }

// Full form
{
  $unwind: {
    path: "$arrayField",
    includeArrayIndex: "indexField",
    preserveNullAndEmptyArrays: false
  }
}
```

### Basic Example

```javascript
// Unwind items array
db.orders.aggregate([
  { $unwind: "$items" }
])

// Output (partial):
// { _id: 1, customer: "John", items: { product: "Widget", ... } }
// { _id: 1, customer: "John", items: { product: "Gadget", ... } }
// { _id: 2, customer: "Jane", items: { product: "Book", ... } }
// { _id: 4, customer: "Alice", items: { product: "DVD", ... } }
// { _id: 4, customer: "Alice", items: { product: "CD", ... } }
// { _id: 4, customer: "Alice", items: { product: "Book", ... } }
// Note: Bob's order (empty array) is excluded
```

### Unwind Then Access

```javascript
// Access unwound element fields
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $project: {
      customer: 1,
      product: "$items.product",
      quantity: "$items.quantity",
      lineTotal: { $multiply: ["$items.quantity", "$items.price"] }
    }
  }
])
```

---

## Preserving Empty Arrays

### Default Behavior

```javascript
// By default, documents with empty/missing arrays are excluded
db.orders.aggregate([
  { $unwind: "$items" },
  { $count: "itemCount" }
])
// Result: 6 (Bob's order excluded)
```

### preserveNullAndEmptyArrays

```javascript
// Include documents with empty/null arrays
db.orders.aggregate([
  {
    $unwind: {
      path: "$items",
      preserveNullAndEmptyArrays: true
    }
  }
])

// Output includes Bob's order:
// { _id: 3, customer: "Bob", date: ..., items: null, tags: [] }
```

### Handling Preserved Nulls

```javascript
// Handle null items after preserve
db.orders.aggregate([
  {
    $unwind: {
      path: "$items",
      preserveNullAndEmptyArrays: true
    }
  },
  {
    $project: {
      customer: 1,
      product: { $ifNull: ["$items.product", "No items"] },
      quantity: { $ifNull: ["$items.quantity", 0] },
      hasItems: { $cond: [{ $eq: ["$items", null] }, false, true] }
    }
  }
])
```

---

## Array Index

### includeArrayIndex

```javascript
// Include the array index
db.orders.aggregate([
  {
    $unwind: {
      path: "$items",
      includeArrayIndex: "itemIndex"
    }
  },
  {
    $project: {
      customer: 1,
      itemIndex: 1,
      product: "$items.product"
    }
  }
])

// Output:
// { _id: 1, customer: "John", itemIndex: 0, product: "Widget" }
// { _id: 1, customer: "John", itemIndex: 1, product: "Gadget" }
// { _id: 2, customer: "Jane", itemIndex: 0, product: "Book" }
// ...
```

### Using Index for Position

```javascript
// Get first item of each order
db.orders.aggregate([
  {
    $unwind: {
      path: "$items",
      includeArrayIndex: "idx"
    }
  },
  { $match: { idx: 0 } },
  {
    $project: {
      customer: 1,
      firstItem: "$items.product"
    }
  }
])

// Get last item using $facet (alternative approach)
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      lastItem: { $arrayElemAt: ["$items", -1] }
    }
  }
])
```

---

## Unwinding Nested Arrays

### Setup Nested Data

```javascript
// Orders with nested variants
db.ordersNested.drop()
db.ordersNested.insertMany([
  {
    _id: 1,
    customer: "John",
    items: [
      {
        product: "T-Shirt",
        variants: [
          { size: "S", quantity: 2 },
          { size: "M", quantity: 3 },
          { size: "L", quantity: 1 }
        ]
      },
      {
        product: "Jeans",
        variants: [
          { size: "32", quantity: 2 },
          { size: "34", quantity: 1 }
        ]
      }
    ]
  }
])
```

### Multiple Unwinds

```javascript
// Unwind both levels
db.ordersNested.aggregate([
  { $unwind: "$items" },
  { $unwind: "$items.variants" },
  {
    $project: {
      customer: 1,
      product: "$items.product",
      size: "$items.variants.size",
      quantity: "$items.variants.quantity"
    }
  }
])

// Output:
// { _id: 1, customer: "John", product: "T-Shirt", size: "S", quantity: 2 }
// { _id: 1, customer: "John", product: "T-Shirt", size: "M", quantity: 3 }
// { _id: 1, customer: "John", product: "T-Shirt", size: "L", quantity: 1 }
// { _id: 1, customer: "John", product: "Jeans", size: "32", quantity: 2 }
// { _id: 1, customer: "John", product: "Jeans", size: "34", quantity: 1 }
```

### Flatten Completely

```javascript
// Full flatten with tracking
db.ordersNested.aggregate([
  {
    $unwind: {
      path: "$items",
      includeArrayIndex: "itemIndex"
    }
  },
  {
    $unwind: {
      path: "$items.variants",
      includeArrayIndex: "variantIndex"
    }
  },
  {
    $project: {
      customer: 1,
      itemIndex: 1,
      variantIndex: 1,
      product: "$items.product",
      size: "$items.variants.size",
      quantity: "$items.variants.quantity"
    }
  }
])
```

---

## Array Operators in Aggregation

### $size - Array Length

```javascript
// Count items per order
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      itemCount: { $size: "$items" },
      tagCount: { $size: "$tags" }
    }
  }
])
```

### $arrayElemAt - Get Element

```javascript
// Get specific elements
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      firstItem: { $arrayElemAt: ["$items", 0] },
      lastItem: { $arrayElemAt: ["$items", -1] }
    }
  }
])
```

### $slice - Get Subset

```javascript
// Get first 2 items
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      firstTwoItems: { $slice: ["$items", 2] }
    }
  }
])

// Get last 2 items
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      lastTwoItems: { $slice: ["$items", -2] }
    }
  }
])

// Skip 1, take 2
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      middleItems: { $slice: ["$items", 1, 2] }
    }
  }
])
```

### $filter - Filter Array

```javascript
// Filter items by price
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      expensiveItems: {
        $filter: {
          input: "$items",
          as: "item",
          cond: { $gt: ["$$item.price", 20] }
        }
      }
    }
  }
])
```

### $map - Transform Array

```javascript
// Transform each item
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      itemSummaries: {
        $map: {
          input: "$items",
          as: "item",
          in: {
            name: "$$item.product",
            total: { $multiply: ["$$item.quantity", "$$item.price"] }
          }
        }
      }
    }
  }
])
```

### $reduce - Aggregate Array

```javascript
// Calculate order total
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      orderTotal: {
        $reduce: {
          input: "$items",
          initialValue: 0,
          in: {
            $add: [
              "$$value",
              { $multiply: ["$$this.quantity", "$$this.price"] }
            ]
          }
        }
      }
    }
  }
])
```

### $in - Check Membership

```javascript
// Check if tag exists
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      isOnSale: { $in: ["sale", "$tags"] },
      isMedia: { $in: ["media", "$tags"] }
    }
  }
])
```

### $concatArrays - Merge Arrays

```javascript
// Combine arrays
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      allData: {
        $concatArrays: [
          { $map: { input: "$items", in: "$$this.product" } },
          "$tags"
        ]
      }
    }
  }
])
```

### $setUnion, $setIntersection, $setDifference

```javascript
// Set operations
db.orders.aggregate([
  {
    $facet: {
      "order1Tags": [
        { $match: { _id: 1 } },
        { $project: { tags: 1 } }
      ],
      "order4Tags": [
        { $match: { _id: 4 } },
        { $project: { tags: 1 } }
      ]
    }
  },
  {
    $project: {
      tags1: { $arrayElemAt: ["$order1Tags.tags", 0] },
      tags4: { $arrayElemAt: ["$order4Tags.tags", 0] },
      union: {
        $setUnion: [
          { $arrayElemAt: ["$order1Tags.tags", 0] },
          { $arrayElemAt: ["$order4Tags.tags", 0] }
        ]
      },
      intersection: {
        $setIntersection: [
          { $arrayElemAt: ["$order1Tags.tags", 0] },
          { $arrayElemAt: ["$order4Tags.tags", 0] }
        ]
      }
    }
  }
])
```

---

## Grouping After Unwind

### Unwind Then Group

```javascript
// Product sales summary
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product",
      totalQuantity: { $sum: "$items.quantity" },
      totalRevenue: { $sum: { $multiply: ["$items.quantity", "$items.price"] } },
      orderCount: { $sum: 1 }
    }
  },
  { $sort: { totalRevenue: -1 } }
])

// Output:
// { _id: "Widget", totalQuantity: 2, totalRevenue: 50, orderCount: 1 }
// { _id: "Gadget", totalQuantity: 1, totalRevenue: 50, orderCount: 1 }
// ...
```

### Regroup to Original Structure

```javascript
// Unwind, transform, regroup
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $addFields: {
      "items.lineTotal": { $multiply: ["$items.quantity", "$items.price"] }
    }
  },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      date: { $first: "$date" },
      items: { $push: "$items" },
      orderTotal: { $sum: "$items.lineTotal" }
    }
  }
])
```

### Tag Analysis

```javascript
// Unwind tags, analyze
db.orders.aggregate([
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$tags",
      count: { $sum: 1 },
      customers: { $addToSet: "$customer" }
    }
  },
  { $sort: { count: -1 } }
])

// Output:
// { _id: "sale", count: 2, customers: ["John", "Alice"] }
// { _id: "media", count: 2, customers: ["Jane", "Alice"] }
// { _id: "electronics", count: 1, customers: ["John"] }
// { _id: "clearance", count: 1, customers: ["Alice"] }
```

---

## Common Patterns

### Flatten and Calculate

```javascript
// Calculate line totals and order summary
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      date: { $first: "$date" },
      itemCount: { $sum: 1 },
      totalQuantity: { $sum: "$items.quantity" },
      subtotal: { $sum: { $multiply: ["$items.quantity", "$items.price"] } }
    }
  },
  {
    $addFields: {
      tax: { $multiply: ["$subtotal", 0.08] },
      total: { $multiply: ["$subtotal", 1.08] }
    }
  },
  { $sort: { total: -1 } }
])
```

### Top N Items Per Document

```javascript
// Get top 2 most expensive items per order
db.orders.aggregate([
  { $unwind: "$items" },
  { $sort: { _id: 1, "items.price": -1 } },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      allItems: { $push: "$items" }
    }
  },
  {
    $project: {
      customer: 1,
      topTwoItems: { $slice: ["$allItems", 2] }
    }
  }
])
```

### Cross-Document Analysis

```javascript
// Find products that appear together
db.orders.aggregate([
  // Get orders with 2+ items
  { $match: { $expr: { $gte: [{ $size: "$items" }, 2] } } },
  // Unwind to get all pairs
  { $unwind: "$items" },
  {
    $group: {
      _id: "$_id",
      products: { $push: "$items.product" }
    }
  },
  // Self-join to create pairs
  {
    $project: {
      pairs: {
        $reduce: {
          input: { $range: [0, { $subtract: [{ $size: "$products" }, 1] }] },
          initialValue: [],
          in: {
            $concatArrays: [
              "$$value",
              {
                $map: {
                  input: { $range: [{ $add: ["$$this", 1] }, { $size: "$products" }] },
                  as: "j",
                  in: {
                    $cond: [
                      { $lt: [{ $arrayElemAt: ["$products", "$$this"] }, { $arrayElemAt: ["$products", "$$j"] }] },
                      [{ $arrayElemAt: ["$products", "$$this"] }, { $arrayElemAt: ["$products", "$$j"] }],
                      [{ $arrayElemAt: ["$products", "$$j"] }, { $arrayElemAt: ["$products", "$$this"] }]
                    ]
                  }
                }
              }
            ]
          }
        }
      }
    }
  },
  { $unwind: "$pairs" },
  {
    $group: {
      _id: "$pairs",
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
])
```

### Array Statistics

```javascript
// Statistics on array items
db.orders.aggregate([
  { $match: { items: { $ne: [] } } },
  {
    $project: {
      customer: 1,
      itemCount: { $size: "$items" },
      prices: "$items.price",
      quantities: "$items.quantity"
    }
  },
  {
    $project: {
      customer: 1,
      itemCount: 1,
      avgPrice: { $avg: "$prices" },
      maxPrice: { $max: "$prices" },
      minPrice: { $min: "$prices" },
      totalQuantity: { $sum: "$quantities" }
    }
  }
])
```

---

## Summary

### $unwind Options

| Option | Description |
|--------|-------------|
| **path** | Array field to unwind |
| **preserveNullAndEmptyArrays** | Keep docs with empty/null arrays |
| **includeArrayIndex** | Include original array index |

### Array Operators

| Operator | Description |
|----------|-------------|
| **$size** | Array length |
| **$arrayElemAt** | Get element by index |
| **$slice** | Get subset |
| **$filter** | Filter elements |
| **$map** | Transform elements |
| **$reduce** | Aggregate to single value |
| **$in** | Check membership |
| **$concatArrays** | Merge arrays |

### Common Patterns

| Pattern | Usage |
|---------|-------|
| **Unwind + Group** | Aggregate array elements |
| **Unwind + Filter + Group** | Selective aggregation |
| **Unwind + Transform + Regroup** | Modify array elements |
| **Multiple Unwinds** | Flatten nested arrays |

### What's Next?

In the next chapter, we'll explore $facet and Multi-faceted Aggregations.

---

## Practice Questions

1. What does $unwind do to documents with empty arrays by default?
2. How do you preserve documents with empty/null arrays?
3. How do you get the original array index after unwinding?
4. What's the difference between $filter and $map?
5. How do you unwind nested arrays?
6. How do you calculate array statistics without $unwind?
7. How do you regroup unwound documents?
8. When should you avoid using $unwind?

---

## Hands-On Exercises

### Exercise 1: Basic Unwind

```javascript
// Using the orders data:

// 1. List all items from all orders
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $project: {
      orderId: "$_id",
      customer: 1,
      product: "$items.product",
      quantity: "$items.quantity",
      price: "$items.price"
    }
  }
])

// 2. Count total items across all orders
db.orders.aggregate([
  { $unwind: "$items" },
  { $count: "totalItems" }
])

// 3. List items with their position in order
db.orders.aggregate([
  {
    $unwind: {
      path: "$items",
      includeArrayIndex: "position"
    }
  },
  {
    $project: {
      orderId: "$_id",
      position: { $add: ["$position", 1] },  // 1-based
      product: "$items.product"
    }
  }
])
```

### Exercise 2: Product Analysis

```javascript
// Analyze products from items

// 1. Total quantity sold per product
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product",
      totalSold: { $sum: "$items.quantity" },
      orders: { $sum: 1 },
      avgQuantityPerOrder: { $avg: "$items.quantity" }
    }
  },
  { $sort: { totalSold: -1 } }
])

// 2. Revenue by product
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product",
      revenue: { $sum: { $multiply: ["$items.quantity", "$items.price"] } },
      unitsSold: { $sum: "$items.quantity" }
    }
  },
  {
    $project: {
      product: "$_id",
      revenue: 1,
      unitsSold: 1,
      avgRevPerUnit: { $divide: ["$revenue", "$unitsSold"] }
    }
  },
  { $sort: { revenue: -1 } }
])

// 3. Customers who bought each product
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $group: {
      _id: "$items.product",
      customers: { $addToSet: "$customer" }
    }
  },
  {
    $project: {
      product: "$_id",
      customers: 1,
      customerCount: { $size: "$customers" }
    }
  }
])
```

### Exercise 3: Array Operators

```javascript
// Use array operators without unwind

// 1. Order totals using $reduce
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      itemCount: { $size: "$items" },
      total: {
        $reduce: {
          input: "$items",
          initialValue: 0,
          in: { $add: ["$$value", { $multiply: ["$$this.quantity", "$$this.price"] }] }
        }
      }
    }
  }
])

// 2. Filter high-value items
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      expensiveItems: {
        $filter: {
          input: "$items",
          as: "item",
          cond: { $gte: ["$$item.price", 20] }
        }
      }
    }
  }
])

// 3. Transform items with $map
db.orders.aggregate([
  {
    $project: {
      customer: 1,
      itemSummary: {
        $map: {
          input: "$items",
          as: "item",
          in: {
            name: { $toUpper: "$$item.product" },
            lineTotal: { $multiply: ["$$item.quantity", "$$item.price"] }
          }
        }
      }
    }
  }
])
```

### Exercise 4: Tag Analysis

```javascript
// Analyze tags

// 1. Count orders per tag
db.orders.aggregate([
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$tags",
      orderCount: { $sum: 1 },
      customers: { $addToSet: "$customer" }
    }
  },
  { $sort: { orderCount: -1 } }
])

// 2. Find orders with multiple tags
db.orders.aggregate([
  { $match: { $expr: { $gt: [{ $size: "$tags" }, 1] } } },
  {
    $project: {
      customer: 1,
      tagCount: { $size: "$tags" },
      tags: 1
    }
  }
])

// 3. Tag co-occurrence
db.orders.aggregate([
  { $match: { $expr: { $gte: [{ $size: "$tags" }, 2] } } },
  { $unwind: "$tags" },
  {
    $group: {
      _id: "$_id",
      tags: { $push: "$tags" }
    }
  },
  { $unwind: { path: "$tags", includeArrayIndex: "i" } },
  {
    $lookup: {
      from: "orders",
      let: { orderId: "$_id", tag1: "$tags", idx: "$i" },
      pipeline: [
        { $match: { $expr: { $eq: ["$_id", "$$orderId"] } } },
        { $unwind: { path: "$tags", includeArrayIndex: "j" } },
        { $match: { $expr: { $gt: ["$j", "$$idx"] } } },
        { $project: { tag2: "$tags" } }
      ],
      as: "pairs"
    }
  },
  { $unwind: "$pairs" },
  {
    $group: {
      _id: { tag1: "$tags", tag2: "$pairs.tag2" },
      count: { $sum: 1 }
    }
  },
  { $sort: { count: -1 } }
])
```

### Exercise 5: Order Line Analysis

```javascript
// Detailed order line analysis

// 1. Calculate line totals and regroup
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $addFields: {
      "items.lineTotal": { $multiply: ["$items.quantity", "$items.price"] }
    }
  },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      date: { $first: "$date" },
      items: { $push: "$items" },
      subtotal: { $sum: "$items.lineTotal" },
      itemCount: { $sum: 1 },
      totalUnits: { $sum: "$items.quantity" }
    }
  },
  {
    $addFields: {
      avgItemValue: { $divide: ["$subtotal", "$itemCount"] }
    }
  },
  { $sort: { subtotal: -1 } }
])

// 2. Find most expensive item per order
db.orders.aggregate([
  { $match: { items: { $ne: [] } } },
  {
    $addFields: {
      mostExpensive: {
        $reduce: {
          input: "$items",
          initialValue: { price: 0 },
          in: {
            $cond: [
              { $gt: ["$$this.price", "$$value.price"] },
              "$$this",
              "$$value"
            ]
          }
        }
      }
    }
  },
  {
    $project: {
      customer: 1,
      mostExpensiveItem: "$mostExpensive.product",
      price: "$mostExpensive.price"
    }
  }
])

// 3. Orders with items above average price
db.orders.aggregate([
  {
    $addFields: {
      avgPrice: { $avg: "$items.price" }
    }
  },
  {
    $addFields: {
      aboveAvgItems: {
        $filter: {
          input: "$items",
          as: "item",
          cond: { $gt: ["$$item.price", "$avgPrice"] }
        }
      }
    }
  },
  {
    $project: {
      customer: 1,
      avgPrice: { $round: ["$avgPrice", 2] },
      aboveAvgItems: 1,
      count: { $size: "$aboveAvgItems" }
    }
  }
])
```

---

[← Previous: $lookup and Joins](25-lookup-and-joins.md) | [Next: $facet and Multi-faceted Aggregations →](27-facet-and-multifaceted-aggregations.md)
