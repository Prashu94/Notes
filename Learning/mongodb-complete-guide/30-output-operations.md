# Chapter 30: Output Operations

## Table of Contents
- [Introduction to Output Operations](#introduction-to-output-operations)
- [$out Stage](#out-stage)
- [$merge Stage](#merge-stage)
- [Comparing $out and $merge](#comparing-out-and-merge)
- [Writing to Different Databases](#writing-to-different-databases)
- [Incremental Processing](#incremental-processing)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Introduction to Output Operations

MongoDB provides two stages for writing aggregation results to collections: `$out` and `$merge`. These enable ETL operations, materialized views, and data transformations.

### Output Operations Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Output Stage Comparison                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $out (since MongoDB 2.6)                                          │
│  ├── Replaces entire collection                                    │
│  ├── Atomic operation                                              │
│  ├── Cannot output to sharded collection                           │
│  └── Simpler but less flexible                                     │
│                                                                     │
│  $merge (since MongoDB 4.2)                                        │
│  ├── Insert, update, or replace documents                          │
│  ├── Can output to sharded collections                             │
│  ├── Supports incremental processing                               │
│  └── More flexible with multiple behaviors                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Source data
db.sales.drop()
db.sales.insertMany([
  { _id: 1, date: ISODate("2024-01-15"), product: "Widget", region: "East", quantity: 10, price: 25 },
  { _id: 2, date: ISODate("2024-01-15"), product: "Gadget", region: "East", quantity: 5, price: 50 },
  { _id: 3, date: ISODate("2024-01-16"), product: "Widget", region: "West", quantity: 15, price: 25 },
  { _id: 4, date: ISODate("2024-01-16"), product: "Gadget", region: "West", quantity: 8, price: 50 },
  { _id: 5, date: ISODate("2024-01-17"), product: "Widget", region: "East", quantity: 20, price: 25 },
  { _id: 6, date: ISODate("2024-01-17"), product: "Gizmo", region: "West", quantity: 12, price: 30 }
])
```

---

## $out Stage

### Basic Syntax

```javascript
{
  $out: "<output-collection>"
}

// Or with database specification (MongoDB 4.4+)
{
  $out: {
    db: "<database>",
    coll: "<collection>"
  }
}
```

### Simple $out Example

```javascript
// Create summary table
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  { $out: "product_summary" }
])

// Verify output
db.product_summary.find()

// Output:
// { _id: "Widget", totalQuantity: 45, totalRevenue: 1125 }
// { _id: "Gadget", totalQuantity: 13, totalRevenue: 650 }
// { _id: "Gizmo", totalQuantity: 12, totalRevenue: 360 }
```

### $out Behavior

```javascript
// ⚠️ $out REPLACES the entire collection

// First aggregation
db.sales.aggregate([
  { $match: { region: "East" } },
  { $group: { _id: "$product", count: { $sum: 1 } } },
  { $out: "regional_summary" }
])

print("After first $out:")
db.regional_summary.find().forEach(printjson)

// Second aggregation REPLACES the collection
db.sales.aggregate([
  { $match: { region: "West" } },
  { $group: { _id: "$product", count: { $sum: 1 } } },
  { $out: "regional_summary" }  // Replaces previous data!
])

print("\nAfter second $out (data replaced):")
db.regional_summary.find().forEach(printjson)
```

### $out to Different Database

```javascript
// Output to different database (MongoDB 4.4+)
db.sales.aggregate([
  {
    $group: {
      _id: { date: "$date", region: "$region" },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $out: {
      db: "analytics",
      coll: "daily_revenue"
    }
  }
])

// Verify in other database
use analytics
db.daily_revenue.find()
use test  // Return to original db
```

### $out Limitations

```
┌─────────────────────────────────────────────────────────────────────┐
│                      $out Limitations                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Cannot output to sharded collection                            │
│                                                                     │
│  2. Replaces entire collection (no partial updates)                │
│                                                                     │
│  3. Must be last stage in pipeline                                 │
│                                                                     │
│  4. Cannot output to capped collection                             │
│                                                                     │
│  5. Collection indexes preserved, but may need rebuilding          │
│                                                                     │
│  6. Atomicity: Creates temp collection, then renames               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## $merge Stage

### Basic Syntax

```javascript
{
  $merge: {
    into: "<collection>" | { db: "<db>", coll: "<coll>" },
    on: "<identifier field>" | [ "<field1>", "<field2>", ... ],
    let: { <var>: <expression>, ... },
    whenMatched: "replace" | "keepExisting" | "merge" | "fail" | [ pipeline ],
    whenNotMatched: "insert" | "discard" | "fail"
  }
}
```

### whenMatched Options

| Option | Description |
|--------|-------------|
| `"replace"` | Replace matching document with new one |
| `"keepExisting"` | Keep the existing document |
| `"merge"` | Merge fields (shallow merge) |
| `"fail"` | Fail the operation |
| `[pipeline]` | Apply update pipeline |

### whenNotMatched Options

| Option | Description |
|--------|-------------|
| `"insert"` | Insert new document |
| `"discard"` | Don't insert, skip |
| `"fail"` | Fail the operation |

### Basic $merge Example

```javascript
// Create or update product summary
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      lastUpdated: { $max: "$date" }
    }
  },
  {
    $merge: {
      into: "product_stats",
      on: "_id",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])

// Verify
db.product_stats.find()
```

### $merge with Merge Fields

```javascript
// Merge fields (keep existing, add new)
db.product_stats.drop()
db.product_stats.insertMany([
  { _id: "Widget", category: "Electronics", rating: 4.5 },
  { _id: "Gadget", category: "Electronics", rating: 4.2 }
])

// Merge sales data (preserves category and rating)
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      totalSales: { $sum: "$quantity" }
    }
  },
  {
    $merge: {
      into: "product_stats",
      on: "_id",
      whenMatched: "merge",       // Merges fields
      whenNotMatched: "insert"
    }
  }
])

// Result: existing fields preserved, new fields added
db.product_stats.find()
// { _id: "Widget", category: "Electronics", rating: 4.5, totalSales: 45 }
// { _id: "Gadget", category: "Electronics", rating: 4.2, totalSales: 13 }
// { _id: "Gizmo", totalSales: 12 }  // New document
```

### $merge with Update Pipeline

```javascript
// Use pipeline for complex updates
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      newSales: { $sum: "$quantity" },
      newRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $merge: {
      into: "product_cumulative",
      on: "_id",
      let: { newSales: "$newSales", newRevenue: "$newRevenue" },
      whenMatched: [
        {
          $set: {
            totalSales: { $add: ["$totalSales", "$$newSales"] },
            totalRevenue: { $add: ["$totalRevenue", "$$newRevenue"] },
            updateCount: { $add: [{ $ifNull: ["$updateCount", 0] }, 1] },
            lastUpdated: "$$NOW"
          }
        }
      ],
      whenNotMatched: "insert"
    }
  }
])
```

### $merge on Compound Key

```javascript
// Merge on multiple fields
db.sales.aggregate([
  {
    $group: {
      _id: { product: "$product", region: "$region" },
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $project: {
      _id: 0,
      product: "$_id.product",
      region: "$_id.region",
      totalQuantity: 1,
      totalRevenue: 1
    }
  },
  {
    $merge: {
      into: "regional_product_stats",
      on: ["product", "region"],  // Compound key
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])

// Note: Need unique index on compound key
db.regional_product_stats.createIndex({ product: 1, region: 1 }, { unique: true })
```

---

## Comparing $out and $merge

### Feature Comparison

| Feature | $out | $merge |
|---------|------|--------|
| Replace collection | ✅ Always | ✅ Optional |
| Update existing docs | ❌ | ✅ |
| Insert only | ❌ | ✅ |
| Sharded output | ❌ | ✅ |
| Same collection | ❌ | ✅ |
| Compound match key | ❌ | ✅ |
| Pipeline updates | ❌ | ✅ |
| Simpler syntax | ✅ | ❌ |

### When to Use Each

```javascript
// Use $out when:
// - Creating complete snapshot/backup
// - Full refresh of materialized view
// - Simple ETL with complete replacement

// Full replacement - use $out
db.sales.aggregate([
  {
    $group: {
      _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  { $out: "daily_revenue_snapshot" }  // Complete replacement
])

// Use $merge when:
// - Incremental updates
// - Maintaining running totals
// - Updating specific documents
// - Output to sharded collection

// Incremental update - use $merge
db.sales.aggregate([
  { $match: { date: { $gte: ISODate("2024-01-17") } } },  // Only new data
  {
    $group: {
      _id: "$product",
      additionalQuantity: { $sum: "$quantity" }
    }
  },
  {
    $merge: {
      into: "product_totals",
      on: "_id",
      whenMatched: [
        { $set: { quantity: { $add: ["$quantity", "$$new.additionalQuantity"] } } }
      ],
      whenNotMatched: "insert"
    }
  }
])
```

---

## Writing to Different Databases

### Cross-Database with $out

```javascript
// Write to different database
db.sales.aggregate([
  {
    $group: {
      _id: "$region",
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $out: {
      db: "reporting",
      coll: "regional_totals"
    }
  }
])

// Verify
use reporting
db.regional_totals.find()
use test
```

### Cross-Database with $merge

```javascript
// Merge to different database
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      stats: {
        quantity: { $sum: "$quantity" },
        revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
      }
    }
  },
  {
    $merge: {
      into: { db: "warehouse", coll: "inventory_stats" },
      on: "_id",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])
```

---

## Incremental Processing

### Running Totals Pattern

```javascript
// Initialize cumulative collection
db.product_cumulative.drop()

// Process initial data
db.sales.aggregate([
  { $match: { date: { $lt: ISODate("2024-01-17") } } },
  {
    $group: {
      _id: "$product",
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      orderCount: { $sum: 1 }
    }
  },
  {
    $addFields: {
      processedThrough: ISODate("2024-01-16"),
      createdAt: "$$NOW"
    }
  },
  {
    $merge: {
      into: "product_cumulative",
      on: "_id",
      whenMatched: "fail",
      whenNotMatched: "insert"
    }
  }
])

print("After initial load:")
db.product_cumulative.find().forEach(printjson)

// Process new data (incremental)
db.sales.aggregate([
  { $match: { date: { $gte: ISODate("2024-01-17") } } },
  {
    $group: {
      _id: "$product",
      newQuantity: { $sum: "$quantity" },
      newRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      newOrders: { $sum: 1 }
    }
  },
  {
    $merge: {
      into: "product_cumulative",
      on: "_id",
      let: {
        newQty: "$newQuantity",
        newRev: "$newRevenue",
        newOrd: "$newOrders"
      },
      whenMatched: [
        {
          $set: {
            totalQuantity: { $add: ["$totalQuantity", "$$newQty"] },
            totalRevenue: { $add: ["$totalRevenue", "$$newRev"] },
            orderCount: { $add: ["$orderCount", "$$newOrd"] },
            processedThrough: ISODate("2024-01-17"),
            lastUpdated: "$$NOW"
          }
        }
      ],
      whenNotMatched: "insert"
    }
  }
])

print("\nAfter incremental update:")
db.product_cumulative.find().forEach(printjson)
```

### Time-Series Aggregation

```javascript
// Hourly aggregation with incremental updates
db.events.drop()
db.events.insertMany([
  { timestamp: ISODate("2024-01-15T10:00:00Z"), type: "click", count: 5 },
  { timestamp: ISODate("2024-01-15T10:15:00Z"), type: "click", count: 3 },
  { timestamp: ISODate("2024-01-15T10:30:00Z"), type: "view", count: 10 },
  { timestamp: ISODate("2024-01-15T11:00:00Z"), type: "click", count: 8 }
])

// Aggregate to hourly buckets
db.events.aggregate([
  {
    $group: {
      _id: {
        hour: {
          $dateToString: {
            format: "%Y-%m-%dT%H:00:00Z",
            date: "$timestamp"
          }
        },
        type: "$type"
      },
      totalCount: { $sum: "$count" }
    }
  },
  {
    $project: {
      _id: 0,
      hour: { $toDate: "$_id.hour" },
      type: "$_id.type",
      count: "$totalCount"
    }
  },
  {
    $merge: {
      into: "hourly_metrics",
      on: ["hour", "type"],
      whenMatched: [
        { $set: { count: { $add: ["$count", "$$new.count"] } } }
      ],
      whenNotMatched: "insert"
    }
  }
])

// Need unique index
db.hourly_metrics.createIndex({ hour: 1, type: 1 }, { unique: true })
```

---

## Error Handling

### whenMatched: "fail"

```javascript
// Fail on duplicate
db.unique_products.drop()
db.unique_products.insertOne({ _id: "Widget", name: "Widget Pro" })

try {
  db.sales.aggregate([
    {
      $group: {
        _id: "$product",
        count: { $sum: 1 }
      }
    },
    {
      $merge: {
        into: "unique_products",
        on: "_id",
        whenMatched: "fail",  // Will fail if Widget exists
        whenNotMatched: "insert"
      }
    }
  ])
} catch (e) {
  print("Error:", e.message)
}
```

### whenNotMatched: "fail"

```javascript
// Fail if no match (update-only mode)
db.known_products.drop()
db.known_products.insertMany([
  { _id: "Widget" },
  { _id: "Gadget" }
])

try {
  db.sales.aggregate([
    {
      $group: {
        _id: "$product",  // Includes "Gizmo" which isn't in known_products
        count: { $sum: 1 }
      }
    },
    {
      $merge: {
        into: "known_products",
        on: "_id",
        whenMatched: "merge",
        whenNotMatched: "fail"  // Will fail for "Gizmo"
      }
    }
  ])
} catch (e) {
  print("Error:", e.message)
}
```

### Handling with Discard

```javascript
// Silently skip non-matching (update existing only)
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      count: { $sum: 1 }
    }
  },
  {
    $merge: {
      into: "known_products",
      on: "_id",
      whenMatched: "merge",
      whenNotMatched: "discard"  // Skip unknowns
    }
  }
])

print("Only existing products updated:")
db.known_products.find().forEach(printjson)
```

---

## Best Practices

### Index the Match Fields

```javascript
// Always create unique index for $merge target
db.target_collection.createIndex(
  { matchField1: 1, matchField2: 1 },
  { unique: true }
)
```

### Atomic Updates

```javascript
// Use $merge for atomic upserts
db.counters.createIndex({ _id: 1 }, { unique: true })

// Atomic increment
db.events.aggregate([
  { $group: { _id: "$type", count: { $sum: 1 } } },
  {
    $merge: {
      into: "counters",
      on: "_id",
      whenMatched: [
        { $set: { count: { $add: ["$count", "$$new.count"] } } }
      ],
      whenNotMatched: "insert"
    }
  }
])
```

### Batch Processing

```javascript
// Process in date batches
function processDateRange(startDate, endDate) {
  return db.sales.aggregate([
    {
      $match: {
        date: { $gte: startDate, $lt: endDate }
      }
    },
    {
      $group: {
        _id: { 
          date: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
          product: "$product" 
        },
        quantity: { $sum: "$quantity" },
        revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
      }
    },
    {
      $project: {
        _id: 0,
        date: "$_id.date",
        product: "$_id.product",
        quantity: 1,
        revenue: 1
      }
    },
    {
      $merge: {
        into: "daily_product_stats",
        on: ["date", "product"],
        whenMatched: "replace",
        whenNotMatched: "insert"
      }
    }
  ])
}

// Process day by day
processDateRange(ISODate("2024-01-15"), ISODate("2024-01-16"))
processDateRange(ISODate("2024-01-16"), ISODate("2024-01-17"))
processDateRange(ISODate("2024-01-17"), ISODate("2024-01-18"))
```

### Materialized View Pattern

```javascript
// Create materialized view function
function refreshMaterializedView() {
  return db.sales.aggregate([
    {
      $group: {
        _id: null,
        totalOrders: { $sum: 1 },
        totalQuantity: { $sum: "$quantity" },
        totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
        avgOrderValue: { $avg: { $multiply: ["$quantity", "$price"] } },
        uniqueProducts: { $addToSet: "$product" },
        uniqueRegions: { $addToSet: "$region" }
      }
    },
    {
      $project: {
        _id: "sales_summary",
        totalOrders: 1,
        totalQuantity: 1,
        totalRevenue: 1,
        avgOrderValue: { $round: ["$avgOrderValue", 2] },
        productCount: { $size: "$uniqueProducts" },
        regionCount: { $size: "$uniqueRegions" },
        refreshedAt: "$$NOW"
      }
    },
    {
      $merge: {
        into: "materialized_views",
        on: "_id",
        whenMatched: "replace",
        whenNotMatched: "insert"
      }
    }
  ])
}

// Refresh periodically
refreshMaterializedView()

// Query materialized view (fast)
db.materialized_views.findOne({ _id: "sales_summary" })
```

---

## Summary

### $out vs $merge

| Aspect | $out | $merge |
|--------|------|--------|
| **Operation** | Replace | Flexible |
| **Use case** | Full refresh | Incremental |
| **Sharded output** | No | Yes |
| **Self-reference** | No | Yes |
| **Complexity** | Simple | More complex |

### $merge Options

| Option | Values |
|--------|--------|
| **whenMatched** | replace, keepExisting, merge, fail, [pipeline] |
| **whenNotMatched** | insert, discard, fail |
| **on** | Field or array of fields |

### Best Practices Summary

| Practice | Description |
|----------|-------------|
| Index match fields | Create unique index on merge keys |
| Use $merge for updates | Prefer over $out for incremental |
| Handle errors | Use fail/discard appropriately |
| Batch large operations | Process in date/id ranges |
| Refresh views | Use for materialized views |

### What's Next?

In the next chapter, we'll begin Part 6: Advanced Queries, starting with Query Optimization.

---

## Practice Questions

1. What's the main difference between $out and $merge?
2. Can $out write to a sharded collection?
3. What does whenMatched: "merge" do?
4. How do you merge on a compound key?
5. When would you use whenNotMatched: "discard"?
6. How do you write aggregation results to a different database?
7. What index is required for $merge?
8. How do you implement incremental processing with $merge?

---

## Hands-On Exercises

### Exercise 1: Basic $out

```javascript
// Create summary tables with $out

// 1. Product summary
db.sales.aggregate([
  {
    $group: {
      _id: "$product",
      totalQuantity: { $sum: "$quantity" },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } },
      avgPrice: { $avg: "$price" }
    }
  },
  {
    $project: {
      product: "$_id",
      _id: 0,
      totalQuantity: 1,
      totalRevenue: 1,
      avgPrice: { $round: ["$avgPrice", 2] }
    }
  },
  { $out: "product_summary_v1" }
])

print("Product Summary:")
db.product_summary_v1.find().forEach(printjson)

// 2. Regional summary
db.sales.aggregate([
  {
    $group: {
      _id: "$region",
      orderCount: { $sum: 1 },
      totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  { $out: "regional_summary_v1" }
])

print("\nRegional Summary:")
db.regional_summary_v1.find().forEach(printjson)
```

### Exercise 2: $merge Operations

```javascript
// Different merge behaviors

// Setup target collection
db.merge_target.drop()
db.merge_target.insertMany([
  { _id: "Widget", existingField: "preserved", count: 100 },
  { _id: "Gadget", existingField: "preserved", count: 50 }
])

print("Before merge:")
db.merge_target.find().forEach(printjson)

// Test 1: Replace
db.sales.aggregate([
  { $group: { _id: "$product", newCount: { $sum: "$quantity" } } },
  {
    $merge: {
      into: "merge_test_replace",
      on: "_id",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])

// Test 2: Merge (preserve existing fields)
db.merge_target.drop()
db.merge_target.insertMany([
  { _id: "Widget", existingField: "preserved", count: 100 },
  { _id: "Gadget", existingField: "preserved", count: 50 }
])

db.sales.aggregate([
  { $group: { _id: "$product", newCount: { $sum: "$quantity" } } },
  {
    $merge: {
      into: "merge_target",
      on: "_id",
      whenMatched: "merge",
      whenNotMatched: "insert"
    }
  }
])

print("\nAfter merge (existing fields preserved):")
db.merge_target.find().forEach(printjson)
```

### Exercise 3: Incremental Updates

```javascript
// Implement incremental processing

// Initialize
db.running_totals.drop()
db.running_totals.createIndex({ product: 1 }, { unique: true })

// First batch (Jan 15-16)
db.sales.aggregate([
  { $match: { date: { $lt: ISODate("2024-01-17") } } },
  {
    $group: {
      _id: "$product",
      quantity: { $sum: "$quantity" },
      revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $project: {
      _id: 0,
      product: "$_id",
      quantity: 1,
      revenue: 1,
      lastProcessed: ISODate("2024-01-16")
    }
  },
  {
    $merge: {
      into: "running_totals",
      on: "product",
      whenMatched: "replace",
      whenNotMatched: "insert"
    }
  }
])

print("After first batch:")
db.running_totals.find().forEach(printjson)

// Second batch (Jan 17+)
db.sales.aggregate([
  { $match: { date: { $gte: ISODate("2024-01-17") } } },
  {
    $group: {
      _id: "$product",
      addQuantity: { $sum: "$quantity" },
      addRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
    }
  },
  {
    $merge: {
      into: "running_totals",
      on: "_id",  // Matches product field
      let: { addQ: "$addQuantity", addR: "$addRevenue" },
      whenMatched: [
        {
          $set: {
            quantity: { $add: ["$quantity", "$$addQ"] },
            revenue: { $add: ["$revenue", "$$addR"] },
            lastProcessed: ISODate("2024-01-17")
          }
        }
      ],
      whenNotMatched: "insert"
    }
  }
])

print("\nAfter second batch (incremental):")
db.running_totals.find().forEach(printjson)
```

### Exercise 4: Materialized View

```javascript
// Create a dashboard materialized view

function refreshDashboard() {
  db.sales.aggregate([
    {
      $facet: {
        "overview": [
          {
            $group: {
              _id: null,
              totalOrders: { $sum: 1 },
              totalQuantity: { $sum: "$quantity" },
              totalRevenue: { $sum: { $multiply: ["$quantity", "$price"] } }
            }
          }
        ],
        "byProduct": [
          {
            $group: {
              _id: "$product",
              quantity: { $sum: "$quantity" },
              revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
            }
          }
        ],
        "byRegion": [
          {
            $group: {
              _id: "$region",
              quantity: { $sum: "$quantity" },
              revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
            }
          }
        ],
        "byDate": [
          {
            $group: {
              _id: { $dateToString: { format: "%Y-%m-%d", date: "$date" } },
              orders: { $sum: 1 },
              revenue: { $sum: { $multiply: ["$quantity", "$price"] } }
            }
          },
          { $sort: { _id: 1 } }
        ]
      }
    },
    {
      $project: {
        _id: "dashboard",
        overview: { $arrayElemAt: ["$overview", 0] },
        byProduct: 1,
        byRegion: 1,
        byDate: 1,
        generatedAt: "$$NOW"
      }
    },
    {
      $merge: {
        into: "dashboard_cache",
        on: "_id",
        whenMatched: "replace",
        whenNotMatched: "insert"
      }
    }
  ])
  
  print("Dashboard refreshed at:", new Date())
}

// Refresh
refreshDashboard()

// Query cached dashboard
print("\nCached Dashboard:")
printjson(db.dashboard_cache.findOne({ _id: "dashboard" }))
```

### Exercise 5: Error Handling

```javascript
// Test different error scenarios

// Setup
db.strict_update.drop()
db.strict_update.insertMany([
  { _id: "Widget", approved: true },
  { _id: "Gadget", approved: true }
])

// Test 1: Fail on new documents
print("Test 1: whenNotMatched: 'fail'")
try {
  db.sales.aggregate([
    { $group: { _id: "$product", count: { $sum: 1 } } },
    {
      $merge: {
        into: "strict_update",
        on: "_id",
        whenMatched: "merge",
        whenNotMatched: "fail"  // Will fail for Gizmo
      }
    }
  ])
  print("Success!")
} catch (e) {
  print("Error:", e.message)
}

// Test 2: Discard unknowns
print("\nTest 2: whenNotMatched: 'discard'")
db.sales.aggregate([
  { $group: { _id: "$product", count: { $sum: 1 } } },
  {
    $merge: {
      into: "strict_update",
      on: "_id",
      whenMatched: "merge",
      whenNotMatched: "discard"  // Silently skip Gizmo
    }
  }
])
print("Result (only approved products updated):")
db.strict_update.find().forEach(printjson)

// Test 3: Fail on duplicates
print("\nTest 3: whenMatched: 'fail'")
db.new_products.drop()
try {
  db.sales.aggregate([
    { $group: { _id: "$product", count: { $sum: 1 } } },
    {
      $merge: {
        into: "new_products",
        on: "_id",
        whenMatched: "fail",
        whenNotMatched: "insert"
      }
    }
  ])
  print("First run: Success!")
  
  // Run again - should fail
  db.sales.aggregate([
    { $group: { _id: "$product", count: { $sum: 1 } } },
    {
      $merge: {
        into: "new_products",
        on: "_id",
        whenMatched: "fail",  // Will fail on second run
        whenNotMatched: "insert"
      }
    }
  ])
} catch (e) {
  print("Second run Error:", e.message)
}
```

---

[← Previous: Aggregation Performance](29-aggregation-performance.md) | [Next: Query Optimization →](31-query-optimization.md)
