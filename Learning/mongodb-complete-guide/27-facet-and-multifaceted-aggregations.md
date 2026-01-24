# Chapter 27: $facet and Multi-faceted Aggregations

## Table of Contents
- [Introduction to $facet](#introduction-to-facet)
- [Basic $facet Syntax](#basic-facet-syntax)
- [Multiple Analysis Paths](#multiple-analysis-paths)
- [Dashboard Queries](#dashboard-queries)
- [$bucket and $bucketAuto](#bucket-and-bucketauto)
- [$sortByCount](#sortbycount)
- [Combining Facets with Other Stages](#combining-facets-with-other-stages)
- [Performance Considerations](#performance-considerations)
- [Summary](#summary)

---

## Introduction to $facet

The `$facet` stage allows you to run multiple aggregation pipelines in parallel on the same input documents, producing multiple result sets in a single query.

### $facet Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                        $facet Operation                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Input Documents                                                    │
│  ┌───────────────────────────────┐                                 │
│  │ doc1, doc2, doc3, doc4, ...   │                                 │
│  └───────────────┬───────────────┘                                 │
│                  │                                                  │
│           ┌──────┴──────┬──────────┐                               │
│           │             │          │                               │
│           ▼             ▼          ▼                               │
│     ┌──────────┐  ┌──────────┐  ┌──────────┐                       │
│     │Pipeline 1│  │Pipeline 2│  │Pipeline 3│                       │
│     │ $group   │  │ $sort    │  │ $bucket  │                       │
│     │ $sort    │  │ $limit   │  │          │                       │
│     └────┬─────┘  └────┬─────┘  └────┬─────┘                       │
│          │             │             │                              │
│          ▼             ▼             ▼                              │
│     ┌──────────────────────────────────────────┐                   │
│     │ {                                         │                   │
│     │   "facet1": [ results... ],              │                   │
│     │   "facet2": [ results... ],              │                   │
│     │   "facet3": [ results... ]               │                   │
│     │ }                                         │                   │
│     └──────────────────────────────────────────┘                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// E-commerce products
db.products.drop()
db.products.insertMany([
  { _id: 1, name: "Laptop Pro", category: "Electronics", brand: "TechCo", price: 1299, rating: 4.5, reviews: 120, inStock: true },
  { _id: 2, name: "Wireless Mouse", category: "Electronics", brand: "TechCo", price: 49, rating: 4.2, reviews: 350, inStock: true },
  { _id: 3, name: "USB Hub", category: "Electronics", brand: "ConnectPlus", price: 29, rating: 3.8, reviews: 89, inStock: true },
  { _id: 4, name: "Running Shoes", category: "Sports", brand: "SpeedFit", price: 129, rating: 4.7, reviews: 245, inStock: true },
  { _id: 5, name: "Yoga Mat", category: "Sports", brand: "FitLife", price: 39, rating: 4.4, reviews: 180, inStock: false },
  { _id: 6, name: "Dumbbell Set", category: "Sports", brand: "IronPower", price: 89, rating: 4.6, reviews: 95, inStock: true },
  { _id: 7, name: "Coffee Maker", category: "Home", brand: "BrewMaster", price: 79, rating: 4.3, reviews: 210, inStock: true },
  { _id: 8, name: "Blender", category: "Home", brand: "KitchenPro", price: 59, rating: 4.1, reviews: 165, inStock: true },
  { _id: 9, name: "Air Purifier", category: "Home", brand: "CleanAir", price: 199, rating: 4.8, reviews: 78, inStock: false },
  { _id: 10, name: "Smart Watch", category: "Electronics", brand: "TechCo", price: 299, rating: 4.4, reviews: 420, inStock: true }
])
```

---

## Basic $facet Syntax

### Syntax Structure

```javascript
{
  $facet: {
    "outputField1": [ /* pipeline stages */ ],
    "outputField2": [ /* pipeline stages */ ],
    "outputField3": [ /* pipeline stages */ ]
  }
}
```

### Simple Example

```javascript
// Get count and sample in one query
db.products.aggregate([
  {
    $facet: {
      "totalCount": [
        { $count: "count" }
      ],
      "sample": [
        { $limit: 3 },
        { $project: { name: 1, price: 1 } }
      ]
    }
  }
])

// Output:
// {
//   totalCount: [ { count: 10 } ],
//   sample: [
//     { _id: 1, name: "Laptop Pro", price: 1299 },
//     { _id: 2, name: "Wireless Mouse", price: 49 },
//     { _id: 3, name: "USB Hub", price: 29 }
//   ]
// }
```

---

## Multiple Analysis Paths

### Statistical Analysis

```javascript
// Multiple statistical views
db.products.aggregate([
  {
    $facet: {
      // Overall statistics
      "statistics": [
        {
          $group: {
            _id: null,
            count: { $sum: 1 },
            avgPrice: { $avg: "$price" },
            minPrice: { $min: "$price" },
            maxPrice: { $max: "$price" },
            avgRating: { $avg: "$rating" }
          }
        }
      ],
      
      // By category
      "byCategory": [
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 },
            avgPrice: { $avg: "$price" }
          }
        },
        { $sort: { count: -1 } }
      ],
      
      // By brand
      "byBrand": [
        {
          $group: {
            _id: "$brand",
            productCount: { $sum: 1 },
            avgRating: { $avg: "$rating" }
          }
        },
        { $sort: { productCount: -1 } }
      ]
    }
  }
])
```

### Top/Bottom Analysis

```javascript
// Top and bottom products
db.products.aggregate([
  {
    $facet: {
      // Top rated
      "topRated": [
        { $sort: { rating: -1 } },
        { $limit: 3 },
        { $project: { name: 1, category: 1, rating: 1 } }
      ],
      
      // Most reviewed
      "mostReviewed": [
        { $sort: { reviews: -1 } },
        { $limit: 3 },
        { $project: { name: 1, reviews: 1 } }
      ],
      
      // Cheapest
      "cheapest": [
        { $sort: { price: 1 } },
        { $limit: 3 },
        { $project: { name: 1, price: 1 } }
      ],
      
      // Most expensive
      "mostExpensive": [
        { $sort: { price: -1 } },
        { $limit: 3 },
        { $project: { name: 1, price: 1 } }
      ]
    }
  }
])
```

---

## Dashboard Queries

### E-commerce Dashboard

```javascript
// Complete dashboard data
db.products.aggregate([
  {
    $facet: {
      // KPI metrics
      "metrics": [
        {
          $group: {
            _id: null,
            totalProducts: { $sum: 1 },
            avgPrice: { $avg: "$price" },
            avgRating: { $avg: "$rating" },
            totalReviews: { $sum: "$reviews" },
            inStockCount: {
              $sum: { $cond: ["$inStock", 1, 0] }
            }
          }
        },
        {
          $project: {
            _id: 0,
            totalProducts: 1,
            avgPrice: { $round: ["$avgPrice", 2] },
            avgRating: { $round: ["$avgRating", 2] },
            totalReviews: 1,
            inStockCount: 1,
            outOfStockCount: { $subtract: ["$totalProducts", "$inStockCount"] }
          }
        }
      ],
      
      // Category distribution
      "categoryBreakdown": [
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 },
            revenue: { $sum: "$price" }
          }
        },
        { $sort: { count: -1 } }
      ],
      
      // Brand performance
      "brandPerformance": [
        {
          $group: {
            _id: "$brand",
            products: { $sum: 1 },
            avgRating: { $avg: "$rating" },
            totalReviews: { $sum: "$reviews" }
          }
        },
        {
          $project: {
            brand: "$_id",
            products: 1,
            avgRating: { $round: ["$avgRating", 2] },
            totalReviews: 1,
            reviewsPerProduct: { $round: [{ $divide: ["$totalReviews", "$products"] }, 0] }
          }
        },
        { $sort: { avgRating: -1 } }
      ],
      
      // Stock status
      "stockStatus": [
        {
          $group: {
            _id: "$inStock",
            count: { $sum: 1 },
            products: { $push: "$name" }
          }
        }
      ],
      
      // Price tiers
      "priceTiers": [
        {
          $bucket: {
            groupBy: "$price",
            boundaries: [0, 50, 100, 200, 500, 2000],
            default: "Other",
            output: {
              count: { $sum: 1 },
              products: { $push: "$name" }
            }
          }
        }
      ]
    }
  }
])
```

### Search Results with Facets

```javascript
// E-commerce search facets (like Amazon filters)
db.products.aggregate([
  // Initial filter (search results)
  { $match: { price: { $lte: 500 } } },
  
  {
    $facet: {
      // Actual results (paginated)
      "results": [
        { $sort: { rating: -1 } },
        { $skip: 0 },
        { $limit: 5 },
        {
          $project: {
            name: 1,
            category: 1,
            price: 1,
            rating: 1
          }
        }
      ],
      
      // Total count for pagination
      "totalCount": [
        { $count: "count" }
      ],
      
      // Category facet (for filtering)
      "categoryFacet": [
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 }
          }
        },
        { $sort: { count: -1 } }
      ],
      
      // Brand facet
      "brandFacet": [
        {
          $group: {
            _id: "$brand",
            count: { $sum: 1 }
          }
        },
        { $sort: { count: -1 } }
      ],
      
      // Price range facet
      "priceRangeFacet": [
        {
          $bucket: {
            groupBy: "$price",
            boundaries: [0, 50, 100, 200, 500],
            default: "500+",
            output: { count: { $sum: 1 } }
          }
        }
      ],
      
      // Rating facet
      "ratingFacet": [
        {
          $bucket: {
            groupBy: "$rating",
            boundaries: [0, 3, 4, 4.5, 5],
            default: "5",
            output: { count: { $sum: 1 } }
          }
        }
      ],
      
      // Availability facet
      "availabilityFacet": [
        {
          $group: {
            _id: "$inStock",
            count: { $sum: 1 }
          }
        }
      ]
    }
  }
])
```

---

## $bucket and $bucketAuto

### $bucket - Manual Boundaries

```javascript
// Define price ranges manually
db.products.aggregate([
  {
    $bucket: {
      groupBy: "$price",
      boundaries: [0, 50, 100, 200, 500, 1500],
      default: "Other",
      output: {
        count: { $sum: 1 },
        products: { $push: { name: "$name", price: "$price" } },
        avgPrice: { $avg: "$price" }
      }
    }
  }
])

// Output:
// { _id: 0, count: 3, products: [...], avgPrice: 39 }      // 0-49
// { _id: 50, count: 3, products: [...], avgPrice: 75.67 }  // 50-99
// { _id: 100, count: 2, products: [...], avgPrice: 164 }   // 100-199
// { _id: 200, count: 1, products: [...], avgPrice: 299 }   // 200-499
// { _id: 500, count: 1, products: [...], avgPrice: 1299 }  // 500-1499
```

### $bucketAuto - Automatic Boundaries

```javascript
// Let MongoDB determine optimal boundaries
db.products.aggregate([
  {
    $bucketAuto: {
      groupBy: "$price",
      buckets: 4,  // Number of buckets
      output: {
        count: { $sum: 1 },
        products: { $push: "$name" },
        avgPrice: { $avg: "$price" }
      }
    }
  }
])

// Output with automatically calculated boundaries:
// { _id: { min: 29, max: 59 }, count: 4, ... }
// { _id: { min: 59, max: 129 }, count: 3, ... }
// { _id: { min: 129, max: 299 }, count: 2, ... }
// { _id: { min: 299, max: 1299 }, count: 1, ... }
```

### $bucketAuto with Granularity

```javascript
// Use preferred number series
db.products.aggregate([
  {
    $bucketAuto: {
      groupBy: "$price",
      buckets: 4,
      granularity: "R5",  // Renard series for "nice" boundaries
      output: {
        count: { $sum: 1 },
        avgPrice: { $avg: "$price" }
      }
    }
  }
])

// Granularity options: R5, R10, R20, R40, R80, 1-2-5, E6, E12, E24, E48, E96, E192, POWERSOF2
```

### Rating Buckets

```javascript
// Create rating categories
db.products.aggregate([
  {
    $bucket: {
      groupBy: "$rating",
      boundaries: [0, 3, 4, 4.5, 5.1],
      default: "Unrated",
      output: {
        count: { $sum: 1 },
        products: { $push: "$name" },
        label: {
          $first: {
            $switch: {
              branches: [
                { case: { $lt: ["$rating", 3] }, then: "Poor" },
                { case: { $lt: ["$rating", 4] }, then: "Average" },
                { case: { $lt: ["$rating", 4.5] }, then: "Good" },
                { case: { $gte: ["$rating", 4.5] }, then: "Excellent" }
              ],
              default: "Unknown"
            }
          }
        }
      }
    }
  }
])
```

---

## $sortByCount

### Basic $sortByCount

```javascript
// Count and sort by category
db.products.aggregate([
  { $sortByCount: "$category" }
])

// Output:
// { _id: "Electronics", count: 4 }
// { _id: "Sports", count: 3 }
// { _id: "Home", count: 3 }

// Equivalent to:
db.products.aggregate([
  { $group: { _id: "$category", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])
```

### $sortByCount by Brand

```javascript
// Brand popularity
db.products.aggregate([
  { $sortByCount: "$brand" }
])

// Output:
// { _id: "TechCo", count: 3 }
// { _id: "SpeedFit", count: 1 }
// ...
```

### Combined with $facet

```javascript
// Multiple sortByCount facets
db.products.aggregate([
  {
    $facet: {
      "byCategory": [
        { $sortByCount: "$category" }
      ],
      "byBrand": [
        { $sortByCount: "$brand" }
      ],
      "byStockStatus": [
        { $sortByCount: "$inStock" }
      ]
    }
  }
])
```

---

## Combining Facets with Other Stages

### Pre-filtering

```javascript
// Filter before facets
db.products.aggregate([
  // Pre-filter
  { $match: { inStock: true } },
  
  {
    $facet: {
      "stats": [
        {
          $group: {
            _id: null,
            count: { $sum: 1 },
            avgPrice: { $avg: "$price" }
          }
        }
      ],
      "byCategory": [
        { $sortByCount: "$category" }
      ]
    }
  }
])
```

### Post-processing

```javascript
// Process facet results
db.products.aggregate([
  {
    $facet: {
      "byCategory": [
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 },
            totalRevenue: { $sum: "$price" }
          }
        }
      ],
      "overall": [
        {
          $group: {
            _id: null,
            totalProducts: { $sum: 1 },
            totalRevenue: { $sum: "$price" }
          }
        }
      ]
    }
  },
  // Post-process to add percentages
  {
    $project: {
      categories: {
        $map: {
          input: "$byCategory",
          as: "cat",
          in: {
            category: "$$cat._id",
            count: "$$cat.count",
            revenue: "$$cat.totalRevenue",
            revenuePercent: {
              $round: [
                {
                  $multiply: [
                    { $divide: ["$$cat.totalRevenue", { $arrayElemAt: ["$overall.totalRevenue", 0] }] },
                    100
                  ]
                },
                1
              ]
            }
          }
        }
      }
    }
  }
])
```

### Flatten Results

```javascript
// Flatten facet output
db.products.aggregate([
  {
    $facet: {
      "count": [{ $count: "total" }],
      "avgPrice": [{ $group: { _id: null, avg: { $avg: "$price" } } }]
    }
  },
  {
    $project: {
      totalProducts: { $arrayElemAt: ["$count.total", 0] },
      averagePrice: { $round: [{ $arrayElemAt: ["$avgPrice.avg", 0] }, 2] }
    }
  }
])

// Output:
// { totalProducts: 10, averagePrice: 227 }
```

---

## Performance Considerations

### Facet Limitations

```
┌─────────────────────────────────────────────────────────────────────┐
│                    $facet Limitations                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Output limited to 16MB (single document limit)                 │
│                                                                     │
│  2. Each sub-pipeline gets same input documents                    │
│     (not filtered by other pipelines)                              │
│                                                                     │
│  3. Cannot use these stages inside $facet:                         │
│     • $collStats                                                   │
│     • $facet (no nesting)                                         │
│     • $geoNear                                                     │
│     • $indexStats                                                  │
│     • $out                                                         │
│     • $merge                                                       │
│     • $planCacheStats                                              │
│                                                                     │
│  4. Memory usage = sum of all pipeline results                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Optimization Tips

```javascript
// ✓ Good: Filter before $facet
db.products.aggregate([
  { $match: { inStock: true } },  // Reduces documents BEFORE facet
  {
    $facet: {
      "results": [ { $limit: 10 } ],
      "count": [ { $count: "total" } ]
    }
  }
])

// ✗ Less efficient: No pre-filtering
db.products.aggregate([
  {
    $facet: {
      "results": [
        { $match: { inStock: true } },  // Filtering in EACH pipeline
        { $limit: 10 }
      ],
      "count": [
        { $match: { inStock: true } },  // Repeated filtering
        { $count: "total" }
      ]
    }
  }
])
```

### Memory Management

```javascript
// For large datasets, use allowDiskUse
db.products.aggregate(
  [
    {
      $facet: {
        "allProducts": [ { $sort: { price: 1 } } ],
        "stats": [ { $group: { _id: null, avg: { $avg: "$price" } } } ]
      }
    }
  ],
  { allowDiskUse: true }
)
```

---

## Summary

### Stage Reference

| Stage | Description |
|-------|-------------|
| **$facet** | Run multiple pipelines in parallel |
| **$bucket** | Group by value ranges (manual boundaries) |
| **$bucketAuto** | Group by value ranges (auto boundaries) |
| **$sortByCount** | Group and sort by count |

### $bucket Options

| Option | Description |
|--------|-------------|
| **groupBy** | Expression to group by |
| **boundaries** | Array of boundary values |
| **default** | Bucket for out-of-range values |
| **output** | Accumulator expressions |

### $bucketAuto Options

| Option | Description |
|--------|-------------|
| **groupBy** | Expression to group by |
| **buckets** | Number of buckets to create |
| **granularity** | Preferred number series |
| **output** | Accumulator expressions |

### What's Next?

In the next chapter, we'll explore Window Functions.

---

## Practice Questions

1. What is the purpose of $facet in aggregation?
2. How many pipelines can run inside a single $facet?
3. What stages cannot be used inside $facet?
4. What's the difference between $bucket and $bucketAuto?
5. What is $sortByCount equivalent to?
6. Why filter before $facet instead of inside?
7. What's the output size limit for $facet?
8. How do you flatten $facet results?

---

## Hands-On Exercises

### Exercise 1: Basic Facets

```javascript
// Using the products data:

// 1. Get products count and sample
db.products.aggregate([
  {
    $facet: {
      "count": [{ $count: "total" }],
      "sample": [
        { $sample: { size: 3 } },
        { $project: { name: 1, price: 1 } }
      ]
    }
  }
])

// 2. Top and bottom by price
db.products.aggregate([
  {
    $facet: {
      "cheapest": [
        { $sort: { price: 1 } },
        { $limit: 3 },
        { $project: { name: 1, price: 1 } }
      ],
      "expensive": [
        { $sort: { price: -1 } },
        { $limit: 3 },
        { $project: { name: 1, price: 1 } }
      ]
    }
  }
])

// 3. Category summary
db.products.aggregate([
  {
    $facet: {
      "categories": [
        { $sortByCount: "$category" }
      ],
      "brands": [
        { $sortByCount: "$brand" }
      ]
    }
  }
])
```

### Exercise 2: Dashboard Data

```javascript
// Complete dashboard with all metrics

db.products.aggregate([
  {
    $facet: {
      // Summary metrics
      "summary": [
        {
          $group: {
            _id: null,
            totalProducts: { $sum: 1 },
            totalValue: { $sum: "$price" },
            avgPrice: { $avg: "$price" },
            avgRating: { $avg: "$rating" },
            inStock: { $sum: { $cond: ["$inStock", 1, 0] } }
          }
        },
        {
          $project: {
            _id: 0,
            totalProducts: 1,
            totalValue: 1,
            avgPrice: { $round: ["$avgPrice", 2] },
            avgRating: { $round: ["$avgRating", 2] },
            inStock: 1,
            outOfStock: { $subtract: ["$totalProducts", "$inStock"] }
          }
        }
      ],
      
      // Category breakdown
      "byCategory": [
        {
          $group: {
            _id: "$category",
            count: { $sum: 1 },
            avgPrice: { $avg: "$price" },
            avgRating: { $avg: "$rating" }
          }
        },
        {
          $project: {
            category: "$_id",
            count: 1,
            avgPrice: { $round: ["$avgPrice", 2] },
            avgRating: { $round: ["$avgRating", 2] }
          }
        },
        { $sort: { count: -1 } }
      ],
      
      // Top performers
      "topRated": [
        { $sort: { rating: -1 } },
        { $limit: 5 },
        { $project: { name: 1, rating: 1, reviews: 1 } }
      ],
      
      // Price distribution
      "priceDistribution": [
        {
          $bucket: {
            groupBy: "$price",
            boundaries: [0, 50, 100, 200, 500, 2000],
            default: "2000+",
            output: { count: { $sum: 1 } }
          }
        }
      ]
    }
  }
])
```

### Exercise 3: Search with Filters

```javascript
// Implement search with filter facets

function searchProducts(query = {}, page = 1, pageSize = 5) {
  const skip = (page - 1) * pageSize
  
  return db.products.aggregate([
    // Apply search filter if provided
    { $match: query },
    
    {
      $facet: {
        // Paginated results
        "results": [
          { $sort: { rating: -1, reviews: -1 } },
          { $skip: skip },
          { $limit: pageSize },
          {
            $project: {
              name: 1,
              category: 1,
              brand: 1,
              price: 1,
              rating: 1,
              inStock: 1
            }
          }
        ],
        
        // Metadata
        "metadata": [
          { $count: "total" }
        ],
        
        // Filter options
        "filters": [
          {
            $facet: {
              "categories": [
                { $sortByCount: "$category" }
              ],
              "brands": [
                { $sortByCount: "$brand" }
              ],
              "priceRanges": [
                {
                  $bucket: {
                    groupBy: "$price",
                    boundaries: [0, 50, 100, 250, 500, 2000],
                    default: "2000+",
                    output: { count: { $sum: 1 } }
                  }
                }
              ],
              "ratings": [
                {
                  $bucket: {
                    groupBy: "$rating",
                    boundaries: [0, 3, 4, 4.5, 5.1],
                    output: { count: { $sum: 1 } }
                  }
                }
              ],
              "availability": [
                { $sortByCount: "$inStock" }
              ]
            }
          }
        ]
      }
    },
    
    // Flatten output
    {
      $project: {
        results: 1,
        total: { $arrayElemAt: ["$metadata.total", 0] },
        page: { $literal: page },
        pageSize: { $literal: pageSize },
        filters: { $arrayElemAt: ["$filters", 0] }
      }
    }
  ]).toArray()
}

// Test
print("All products:")
printjson(searchProducts())

print("\nElectronics only:")
printjson(searchProducts({ category: "Electronics" }))

print("\nIn stock, under $100:")
printjson(searchProducts({ inStock: true, price: { $lt: 100 } }))
```

### Exercise 4: Price Bucketing

```javascript
// Different bucketing strategies

// 1. Manual price tiers
db.products.aggregate([
  {
    $bucket: {
      groupBy: "$price",
      boundaries: [0, 50, 100, 200, 500, 1500],
      default: "Premium",
      output: {
        count: { $sum: 1 },
        products: { $push: "$name" },
        avgRating: { $avg: "$rating" }
      }
    }
  },
  {
    $project: {
      priceRange: {
        $concat: [
          "$",
          { $toString: "$_id" },
          " - $",
          { $toString: { $add: ["$_id", 49] } }
        ]
      },
      count: 1,
      products: 1,
      avgRating: { $round: ["$avgRating", 2] }
    }
  }
])

// 2. Automatic bucketing
db.products.aggregate([
  {
    $bucketAuto: {
      groupBy: "$price",
      buckets: 4,
      output: {
        count: { $sum: 1 },
        products: { $push: "$name" },
        minPrice: { $min: "$price" },
        maxPrice: { $max: "$price" }
      }
    }
  }
])

// 3. Rating tiers with labels
db.products.aggregate([
  {
    $addFields: {
      ratingTier: {
        $switch: {
          branches: [
            { case: { $gte: ["$rating", 4.5] }, then: "Excellent" },
            { case: { $gte: ["$rating", 4.0] }, then: "Very Good" },
            { case: { $gte: ["$rating", 3.5] }, then: "Good" },
            { case: { $gte: ["$rating", 3.0] }, then: "Average" }
          ],
          default: "Below Average"
        }
      }
    }
  },
  { $sortByCount: "$ratingTier" }
])
```

### Exercise 5: Category Analysis

```javascript
// Deep category analysis

db.products.aggregate([
  {
    $facet: {
      // Per category stats
      "categoryStats": [
        {
          $group: {
            _id: "$category",
            productCount: { $sum: 1 },
            brands: { $addToSet: "$brand" },
            avgPrice: { $avg: "$price" },
            avgRating: { $avg: "$rating" },
            totalReviews: { $sum: "$reviews" },
            priceRange: {
              $push: "$price"
            }
          }
        },
        {
          $project: {
            category: "$_id",
            productCount: 1,
            brandCount: { $size: "$brands" },
            brands: 1,
            avgPrice: { $round: ["$avgPrice", 2] },
            avgRating: { $round: ["$avgRating", 2] },
            totalReviews: 1,
            minPrice: { $min: "$priceRange" },
            maxPrice: { $max: "$priceRange" }
          }
        }
      ],
      
      // Cross-category comparison
      "comparison": [
        {
          $group: {
            _id: null,
            categories: { $addToSet: "$category" },
            overallAvgPrice: { $avg: "$price" },
            overallAvgRating: { $avg: "$rating" }
          }
        }
      ]
    }
  },
  // Add relative metrics
  {
    $project: {
      categoryStats: {
        $map: {
          input: "$categoryStats",
          as: "cat",
          in: {
            category: "$$cat.category",
            productCount: "$$cat.productCount",
            brandCount: "$$cat.brandCount",
            brands: "$$cat.brands",
            avgPrice: "$$cat.avgPrice",
            avgRating: "$$cat.avgRating",
            totalReviews: "$$cat.totalReviews",
            priceRange: {
              min: "$$cat.minPrice",
              max: "$$cat.maxPrice"
            },
            // Compare to overall
            priceVsOverall: {
              $round: [
                {
                  $subtract: [
                    "$$cat.avgPrice",
                    { $arrayElemAt: ["$comparison.overallAvgPrice", 0] }
                  ]
                },
                2
              ]
            }
          }
        }
      }
    }
  }
])
```

---

[← Previous: $unwind and Array Processing](26-unwind-and-array-processing.md) | [Next: Window Functions →](28-window-functions.md)
