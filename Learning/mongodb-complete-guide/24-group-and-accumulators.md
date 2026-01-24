# Chapter 24: $group and Accumulators

## Table of Contents
- [Introduction to $group](#introduction-to-group)
- [Basic Grouping](#basic-grouping)
- [Accumulator Operators](#accumulator-operators)
- [$sum Accumulator](#sum-accumulator)
- [$avg Accumulator](#avg-accumulator)
- [$min and $max](#min-and-max)
- [$first and $last](#first-and-last)
- [$push and $addToSet](#push-and-addtoset)
- [$count Accumulator](#count-accumulator)
- [$stdDevPop and $stdDevSamp](#stddevpop-and-stddevsamp)
- [Multiple Group Stages](#multiple-group-stages)
- [Summary](#summary)

---

## Introduction to $group

The `$group` stage is the cornerstone of aggregation, allowing you to group documents by a specified key and perform calculations on the grouped data.

### $group Syntax

```javascript
{
  $group: {
    _id: <expression>,        // Grouping key
    <field1>: { <accumulator1>: <expression1> },
    <field2>: { <accumulator2>: <expression2> },
    ...
  }
}
```

### Visual Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                        $group Operation                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Input Documents:                                                   │
│  ┌────────────────┐ ┌────────────────┐ ┌────────────────┐          │
│  │ customer: John │ │ customer: Jane │ │ customer: John │          │
│  │ total: 100     │ │ total: 125     │ │ total: 90      │          │
│  └────────────────┘ └────────────────┘ └────────────────┘          │
│                                                                     │
│                     $group by customer                              │
│                           │                                         │
│                           ▼                                         │
│                                                                     │
│  Grouped Results:                                                   │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ _id: "John"                                              │       │
│  │ totalSpent: 190 (sum)                                   │       │
│  │ orderCount: 2 (count)                                   │       │
│  └─────────────────────────────────────────────────────────┘       │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ _id: "Jane"                                              │       │
│  │ totalSpent: 125 (sum)                                   │       │
│  │ orderCount: 1 (count)                                   │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Setup sample data
db.sales.drop()
db.sales.insertMany([
  { _id: 1, product: "Widget", category: "Electronics", quantity: 5, price: 25, date: ISODate("2024-01-15"), salesperson: "Alice" },
  { _id: 2, product: "Gadget", category: "Electronics", quantity: 2, price: 50, date: ISODate("2024-01-15"), salesperson: "Bob" },
  { _id: 3, product: "Widget", category: "Electronics", quantity: 10, price: 25, date: ISODate("2024-01-16"), salesperson: "Alice" },
  { _id: 4, product: "Book", category: "Media", quantity: 8, price: 15, date: ISODate("2024-01-16"), salesperson: "Charlie" },
  { _id: 5, product: "Gadget", category: "Electronics", quantity: 3, price: 50, date: ISODate("2024-01-17"), salesperson: "Bob" },
  { _id: 6, product: "DVD", category: "Media", quantity: 12, price: 10, date: ISODate("2024-01-17"), salesperson: "Alice" },
  { _id: 7, product: "Widget", category: "Electronics", quantity: 4, price: 25, date: ISODate("2024-01-18"), salesperson: "Charlie" },
  { _id: 8, product: "Book", category: "Media", quantity: 5, price: 15, date: ISODate("2024-01-18"), salesperson: "Bob" }
])
```

---

## Basic Grouping

### Group by Single Field

```javascript
// Group by category
db.sales.aggregate([
  {
    $group: {
      _id: "$category"
    }
  }
])

// Output:
// { _id: "Electronics" }
// { _id: "Media" }
```

### Group by Multiple Fields

```javascript
// Group by category and salesperson
db.sales.aggregate([
  {
    $group: {
      _id: {
        category: "$category",
        salesperson: "$salesperson"
      }
    }
  }
])

// Output:
// { _id: { category: "Electronics", salesperson: "Alice" } }
// { _id: { category: "Electronics", salesperson: "Bob" } }
// { _id: { category: "Media", salesperson: "Charlie" } }
// ...
```

### Group All Documents

```javascript
// Use _id: null to aggregate all documents
db.sales.aggregate([
  {
    $group: {
      _id: null,
      totalSales: { $sum: 1 },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  }
])

// Output:
// { _id: null, totalSales: 8, totalRevenue: 1065 }
```

### Group by Computed Value

```javascript
// Group by year-month
db.sales.aggregate([
  {
    $group: {
      _id: {
        year: { $year: "$date" },
        month: { $month: "$date" }
      },
      count: { $sum: 1 },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  }
])

// Group by day of week
db.sales.aggregate([
  {
    $group: {
      _id: { $dayOfWeek: "$date" },
      sales: { $sum: 1 }
    }
  }
])
```

---

## Accumulator Operators

### Overview

| Accumulator | Description |
|-------------|-------------|
| `$sum` | Sum of values |
| `$avg` | Average of values |
| `$min` | Minimum value |
| `$max` | Maximum value |
| `$first` | First value in group |
| `$last` | Last value in group |
| `$push` | Array of all values |
| `$addToSet` | Array of unique values |
| `$count` | Count of documents |
| `$stdDevPop` | Population standard deviation |
| `$stdDevSamp` | Sample standard deviation |
| `$mergeObjects` | Merge documents |

---

## $sum Accumulator

### Count Documents

```javascript
// Count documents per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      salesCount: { $sum: 1 }
    }
  }
])

// Output:
// { _id: "Electronics", salesCount: 5 }
// { _id: "Media", salesCount: 3 }
```

### Sum Field Values

```javascript
// Sum quantities per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      totalQuantity: { $sum: "$quantity" }
    }
  }
])

// Output:
// { _id: "Electronics", totalQuantity: 24 }
// { _id: "Media", totalQuantity: 25 }
```

### Sum Computed Values

```javascript
// Calculate revenue (quantity × price)
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  }
])

// Output:
// { _id: "Electronics", revenue: 625 }
// { _id: "Media", revenue: 315 }
```

### Conditional Sum

```javascript
// Count high-value sales (revenue > $100)
db.sales.aggregate([
  {
    $group: {
      _id: "$salesperson",
      totalSales: { $sum: 1 },
      highValueSales: {
        $sum: {
          $cond: [
            { $gt: [{ $multiply: ["$quantity", "$price"] }, 100] },
            1,
            0
          ]
        }
      }
    }
  }
])
```

---

## $avg Accumulator

### Basic Average

```javascript
// Average quantity per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      avgQuantity: { $avg: "$quantity" }
    }
  }
])

// Output:
// { _id: "Electronics", avgQuantity: 4.8 }
// { _id: "Media", avgQuantity: 8.33... }
```

### Weighted Average

```javascript
// Weighted average price (by quantity)
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      // Total revenue
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      // Total quantity
      totalQuantity: { $sum: "$quantity" }
    }
  },
  {
    $project: {
      category: "$_id",
      weightedAvgPrice: { $divide: ["$totalRevenue", "$totalQuantity"] }
    }
  }
])
```

### Average with Rounding

```javascript
// Round average to 2 decimal places
db.sales.aggregate([
  {
    $group: {
      _id: "$salesperson",
      avgSaleValue: {
        $avg: { $multiply: ["$quantity", "$price"] }
      }
    }
  },
  {
    $project: {
      salesperson: "$_id",
      avgSaleValue: { $round: ["$avgSaleValue", 2] }
    }
  }
])
```

---

## $min and $max

### Basic Min/Max

```javascript
// Find min and max prices per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      minPrice: { $min: "$price" },
      maxPrice: { $max: "$price" }
    }
  }
])

// Output:
// { _id: "Electronics", minPrice: 25, maxPrice: 50 }
// { _id: "Media", minPrice: 10, maxPrice: 15 }
```

### Date Min/Max

```javascript
// Find first and last sale dates
db.sales.aggregate([
  {
    $group: {
      _id: "$salesperson",
      firstSale: { $min: "$date" },
      lastSale: { $max: "$date" }
    }
  }
])
```

### Range Calculation

```javascript
// Calculate price range per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      minPrice: { $min: "$price" },
      maxPrice: { $max: "$price" }
    }
  },
  {
    $project: {
      category: "$_id",
      priceRange: { $subtract: ["$maxPrice", "$minPrice"] },
      minPrice: 1,
      maxPrice: 1
    }
  }
])
```

---

## $first and $last

### Basic First/Last

```javascript
// Get first and last sale per category (requires prior $sort)
db.sales.aggregate([
  { $sort: { date: 1 } },  // Sort first!
  {
    $group: {
      _id: "$category",
      firstProduct: { $first: "$product" },
      lastProduct: { $last: "$product" },
      firstDate: { $first: "$date" },
      lastDate: { $last: "$date" }
    }
  }
])
```

### Top Per Group

```javascript
// Get highest sale per salesperson
db.sales.aggregate([
  {
    $addFields: {
      revenue: { $multiply: ["$quantity", "$price"] }
    }
  },
  { $sort: { salesperson: 1, revenue: -1 } },
  {
    $group: {
      _id: "$salesperson",
      topSale: { $first: "$$ROOT" }
    }
  }
])
```

### Important: $first/$last and Sort Order

```javascript
// ⚠️ Without $sort, $first/$last are non-deterministic

// ✓ Correct: Sort before group
db.sales.aggregate([
  { $sort: { date: -1 } },  // Sort descending
  {
    $group: {
      _id: "$category",
      mostRecent: { $first: "$product" }  // Gets most recent
    }
  }
])

// ✗ Problematic: No sort
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      firstProduct: { $first: "$product" }  // Order undefined!
    }
  }
])
```

---

## $push and $addToSet

### $push - Collect All Values

```javascript
// Collect all products per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      products: { $push: "$product" }
    }
  }
])

// Output:
// { _id: "Electronics", products: ["Widget", "Gadget", "Widget", "Gadget", "Widget"] }
// { _id: "Media", products: ["Book", "DVD", "Book"] }
```

### $addToSet - Unique Values Only

```javascript
// Collect unique products per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      products: { $addToSet: "$product" }
    }
  }
])

// Output:
// { _id: "Electronics", products: ["Widget", "Gadget"] }
// { _id: "Media", products: ["Book", "DVD"] }
```

### Push Entire Documents

```javascript
// Collect all sales per salesperson
db.sales.aggregate([
  {
    $group: {
      _id: "$salesperson",
      sales: {
        $push: {
          product: "$product",
          quantity: "$quantity",
          revenue: { $multiply: ["$quantity", "$price"] }
        }
      }
    }
  }
])
```

### Push with $$ROOT

```javascript
// Push entire documents
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      allSales: { $push: "$$ROOT" }
    }
  }
])
```

### Limit Array Size

```javascript
// Get top 3 sales per category
db.sales.aggregate([
  {
    $addFields: {
      revenue: { $multiply: ["$quantity", "$price"] }
    }
  },
  { $sort: { revenue: -1 } },
  {
    $group: {
      _id: "$category",
      topSales: { $push: "$$ROOT" }
    }
  },
  {
    $project: {
      category: "$_id",
      topSales: { $slice: ["$topSales", 3] }
    }
  }
])
```

---

## $count Accumulator

### Basic $count

```javascript
// MongoDB 5.0+: $count accumulator
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      salesCount: { $count: {} }
    }
  }
])

// Equivalent using $sum
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      salesCount: { $sum: 1 }
    }
  }
])
```

---

## $stdDevPop and $stdDevSamp

### Population Standard Deviation

```javascript
// Standard deviation of prices per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      avgPrice: { $avg: "$price" },
      stdDevPrice: { $stdDevPop: "$price" }
    }
  }
])
```

### Sample Standard Deviation

```javascript
// Sample std dev (for sample data)
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      avgPrice: { $avg: "$price" },
      stdDevSamp: { $stdDevSamp: "$price" }
    }
  }
])
```

### Statistical Analysis

```javascript
// Full statistical summary
db.sales.aggregate([
  {
    $addFields: {
      revenue: { $multiply: ["$quantity", "$price"] }
    }
  },
  {
    $group: {
      _id: "$category",
      count: { $sum: 1 },
      totalRevenue: { $sum: "$revenue" },
      avgRevenue: { $avg: "$revenue" },
      minRevenue: { $min: "$revenue" },
      maxRevenue: { $max: "$revenue" },
      stdDev: { $stdDevPop: "$revenue" }
    }
  },
  {
    $project: {
      category: "$_id",
      count: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      avgRevenue: { $round: ["$avgRevenue", 2] },
      minRevenue: 1,
      maxRevenue: 1,
      stdDev: { $round: ["$stdDev", 2] }
    }
  }
])
```

---

## Multiple Group Stages

### Group Then Regroup

```javascript
// Sales by category and salesperson, then totals by category
db.sales.aggregate([
  // First group: by category and salesperson
  {
    $group: {
      _id: {
        category: "$category",
        salesperson: "$salesperson"
      },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  // Second group: rollup by category
  {
    $group: {
      _id: "$_id.category",
      salespeople: {
        $push: {
          name: "$_id.salesperson",
          revenue: "$revenue"
        }
      },
      totalRevenue: { $sum: "$revenue" }
    }
  }
])
```

### Percentile Calculation

```javascript
// Calculate revenue percentile ranks
db.sales.aggregate([
  {
    $addFields: {
      revenue: { $multiply: ["$quantity", "$price"] }
    }
  },
  { $sort: { revenue: 1 } },
  {
    $group: {
      _id: null,
      sales: { $push: "$$ROOT" },
      count: { $sum: 1 }
    }
  },
  { $unwind: { path: "$sales", includeArrayIndex: "rank" } },
  {
    $project: {
      product: "$sales.product",
      revenue: "$sales.revenue",
      percentile: {
        $multiply: [
          { $divide: ["$rank", { $subtract: ["$count", 1] }] },
          100
        ]
      }
    }
  }
])
```

### Group with $facet

```javascript
// Multiple groupings in parallel
db.sales.aggregate([
  {
    $facet: {
      "byCategory": [
        {
          $group: {
            _id: "$category",
            revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
          }
        }
      ],
      "bySalesperson": [
        {
          $group: {
            _id: "$salesperson",
            revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
          }
        }
      ],
      "byProduct": [
        {
          $group: {
            _id: "$product",
            quantity: { $sum: "$quantity" }
          }
        }
      ]
    }
  }
])
```

---

## Summary

### Accumulator Reference

| Accumulator | Purpose | Example |
|-------------|---------|---------|
| **$sum** | Count/Sum | `$sum: 1`, `$sum: "$qty"` |
| **$avg** | Average | `$avg: "$price"` |
| **$min** | Minimum | `$min: "$date"` |
| **$max** | Maximum | `$max: "$score"` |
| **$first** | First (requires sort) | `$first: "$name"` |
| **$last** | Last (requires sort) | `$last: "$value"` |
| **$push** | All values array | `$push: "$item"` |
| **$addToSet** | Unique values | `$addToSet: "$tag"` |
| **$count** | Count (5.0+) | `$count: {}` |
| **$stdDevPop** | Std Dev (pop) | `$stdDevPop: "$value"` |
| **$stdDevSamp** | Std Dev (sample) | `$stdDevSamp: "$value"` |

### Key Patterns

| Pattern | Usage |
|---------|-------|
| **Group all** | `_id: null` |
| **Group by field** | `_id: "$field"` |
| **Group by multiple** | `_id: { f1: "$f1", f2: "$f2" }` |
| **Group by computed** | `_id: { $year: "$date" }` |

### What's Next?

In the next chapter, we'll explore $lookup for joining collections.

---

## Practice Questions

1. What's the difference between `$push` and `$addToSet`?
2. Why is $sort important before using $first/$last?
3. How do you group all documents together?
4. What's the difference between `$stdDevPop` and `$stdDevSamp`?
5. How do you calculate a weighted average?
6. How can you limit the size of arrays created by $push?
7. What does `$$ROOT` represent in $group?
8. How do you perform multiple groupings in parallel?

---

## Hands-On Exercises

### Exercise 1: Basic Grouping

```javascript
// Using the sales data:

// 1. Count sales per salesperson
db.sales.aggregate([
  {
    $group: {
      _id: "$salesperson",
      salesCount: { $sum: 1 }
    }
  },
  { $sort: { salesCount: -1 } }
])

// 2. Total revenue per category
db.sales.aggregate([
  {
    $group: {
      _id: "$category",
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  }
])

// 3. Average sale value per day
db.sales.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
      avgSaleValue: { $avg: { $multiply: ["$quantity", "$price"] } }
    }
  },
  { $sort: { "_id": 1 } }
])
```

### Exercise 2: Multi-Level Aggregation

```javascript
// Sales analysis with multiple stages

// Revenue by category and product
db.sales.aggregate([
  {
    $group: {
      _id: {
        category: "$category",
        product: "$product"
      },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      quantitySold: { $sum: "$quantity" }
    }
  },
  { $sort: { "_id.category": 1, revenue: -1 } },
  {
    $group: {
      _id: "$_id.category",
      products: {
        $push: {
          name: "$_id.product",
          revenue: "$revenue",
          quantity: "$quantitySold"
        }
      },
      totalRevenue: { $sum: "$revenue" }
    }
  }
])
```

### Exercise 3: Statistical Summary

```javascript
// Full statistical report

db.sales.aggregate([
  {
    $addFields: {
      saleValue: { $multiply: ["$quantity", "$price"] }
    }
  },
  {
    $group: {
      _id: null,
      totalSales: { $sum: 1 },
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: "$saleValue" },
      avgSaleValue: { $avg: "$saleValue" },
      minSale: { $min: "$saleValue" },
      maxSale: { $max: "$saleValue" },
      stdDev: { $stdDevPop: "$saleValue" },
      products: { $addToSet: "$product" },
      salespeople: { $addToSet: "$salesperson" }
    }
  },
  {
    $project: {
      _id: 0,
      totalSales: 1,
      totalQuantity: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      avgSaleValue: { $round: ["$avgSaleValue", 2] },
      minSale: 1,
      maxSale: 1,
      stdDev: { $round: ["$stdDev", 2] },
      uniqueProducts: { $size: "$products" },
      uniqueSalespeople: { $size: "$salespeople" }
    }
  }
])
```

### Exercise 4: Top N Per Group

```javascript
// Get top 2 products per category by quantity sold

db.sales.aggregate([
  {
    $group: {
      _id: {
        category: "$category",
        product: "$product"
      },
      totalQuantity: { $sum: "$quantity" }
    }
  },
  { $sort: { "_id.category": 1, totalQuantity: -1 } },
  {
    $group: {
      _id: "$_id.category",
      products: {
        $push: {
          name: "$_id.product",
          quantity: "$totalQuantity"
        }
      }
    }
  },
  {
    $project: {
      category: "$_id",
      topProducts: { $slice: ["$products", 2] }
    }
  }
])
```

### Exercise 5: Salesperson Performance

```javascript
// Comprehensive salesperson analysis

db.sales.aggregate([
  {
    $addFields: {
      revenue: { $multiply: ["$quantity", "$price"] }
    }
  },
  { $sort: { salesperson: 1, date: 1 } },
  {
    $group: {
      _id: "$salesperson",
      totalSales: { $sum: 1 },
      totalRevenue: { $sum: "$revenue" },
      avgRevenue: { $avg: "$revenue" },
      topSale: { $max: "$revenue" },
      categories: { $addToSet: "$category" },
      products: { $addToSet: "$product" },
      firstSaleDate: { $first: "$date" },
      lastSaleDate: { $last: "$date" }
    }
  },
  {
    $project: {
      salesperson: "$_id",
      _id: 0,
      totalSales: 1,
      totalRevenue: { $round: ["$totalRevenue", 2] },
      avgRevenue: { $round: ["$avgRevenue", 2] },
      topSale: 1,
      categoriesCount: { $size: "$categories" },
      productsCount: { $size: "$products" },
      daysActive: {
        $add: [
          { 
            $dateDiff: {
              startDate: "$firstSaleDate",
              endDate: "$lastSaleDate",
              unit: "day"
            }
          },
          1
        ]
      }
    }
  },
  { $sort: { totalRevenue: -1 } }
])
```

### Exercise 6: Daily Summary with Running Totals

```javascript
// Daily sales with cumulative totals

db.sales.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
      dailyRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      salesCount: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } },
  {
    $group: {
      _id: null,
      days: { $push: "$$ROOT" }
    }
  },
  { $unwind: { path: "$days", includeArrayIndex: "idx" } },
  {
    $project: {
      date: "$days._id",
      dailyRevenue: "$days.dailyRevenue",
      salesCount: "$days.salesCount",
      // Running total approximation (simplified)
      dayNumber: { $add: ["$idx", 1] }
    }
  }
])
```

---

[← Previous: Aggregation Pipeline Basics](23-aggregation-pipeline-basics.md) | [Next: $lookup and Joins →](25-lookup-and-joins.md)
