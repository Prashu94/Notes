# Chapter 28: Window Functions

## Table of Contents
- [Introduction to Window Functions](#introduction-to-window-functions)
- [$setWindowFields Stage](#setwindowfields-stage)
- [Window Operators](#window-operators)
- [Ranking Functions](#ranking-functions)
- [Aggregate Window Functions](#aggregate-window-functions)
- [Document-Based Windows](#document-based-windows)
- [Range-Based Windows](#range-based-windows)
- [Practical Applications](#practical-applications)
- [Summary](#summary)

---

## Introduction to Window Functions

Window functions (introduced in MongoDB 5.0) perform calculations across a set of documents related to the current document, without grouping them into a single output.

### Window Function Concept

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Window Functions Concept                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $group: Combines rows into single output                          │
│  ┌─────┐ ┌─────┐ ┌─────┐                                           │
│  │ A:1 │ │ A:2 │ │ A:3 │  ───►  { _id: "A", sum: 6 }              │
│  └─────┘ └─────┘ └─────┘                                           │
│                                                                     │
│  Window: Keeps rows, adds calculated field                         │
│  ┌─────┐ ┌─────┐ ┌─────┐                                           │
│  │ A:1 │ │ A:2 │ │ A:3 │                                           │
│  └──┬──┘ └──┬──┘ └──┬──┘                                           │
│     │       │       │                                               │
│     ▼       ▼       ▼                                               │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                               │
│  │ A:1     │ │ A:2     │ │ A:3     │                               │
│  │ sum:6   │ │ sum:6   │ │ sum:6   │                               │
│  │ rank:1  │ │ rank:2  │ │ rank:3  │                               │
│  └─────────┘ └─────────┘ └─────────┘                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Sales data
db.sales.drop()
db.sales.insertMany([
  { _id: 1, date: ISODate("2024-01-01"), product: "Widget", region: "East", quantity: 10, revenue: 250 },
  { _id: 2, date: ISODate("2024-01-01"), product: "Gadget", region: "East", quantity: 5, revenue: 250 },
  { _id: 3, date: ISODate("2024-01-02"), product: "Widget", region: "East", quantity: 15, revenue: 375 },
  { _id: 4, date: ISODate("2024-01-02"), product: "Widget", region: "West", quantity: 20, revenue: 500 },
  { _id: 5, date: ISODate("2024-01-03"), product: "Gadget", region: "West", quantity: 8, revenue: 400 },
  { _id: 6, date: ISODate("2024-01-03"), product: "Widget", region: "East", quantity: 12, revenue: 300 },
  { _id: 7, date: ISODate("2024-01-04"), product: "Gadget", region: "East", quantity: 10, revenue: 500 },
  { _id: 8, date: ISODate("2024-01-04"), product: "Widget", region: "West", quantity: 18, revenue: 450 },
  { _id: 9, date: ISODate("2024-01-05"), product: "Gadget", region: "West", quantity: 15, revenue: 750 },
  { _id: 10, date: ISODate("2024-01-05"), product: "Widget", region: "East", quantity: 8, revenue: 200 }
])

// Employee data for ranking
db.employees.drop()
db.employees.insertMany([
  { _id: 1, name: "Alice", department: "Engineering", salary: 95000 },
  { _id: 2, name: "Bob", department: "Engineering", salary: 85000 },
  { _id: 3, name: "Charlie", department: "Engineering", salary: 85000 },
  { _id: 4, name: "Diana", department: "Sales", salary: 75000 },
  { _id: 5, name: "Eve", department: "Sales", salary: 80000 },
  { _id: 6, name: "Frank", department: "Sales", salary: 70000 },
  { _id: 7, name: "Grace", department: "HR", salary: 65000 },
  { _id: 8, name: "Henry", department: "HR", salary: 60000 }
])
```

---

## $setWindowFields Stage

### Basic Syntax

```javascript
{
  $setWindowFields: {
    partitionBy: <expression>,     // Optional: partition documents
    sortBy: { <field>: <order> },  // Required for many operators
    output: {
      <outputField>: {
        <windowOperator>: <expression>,
        window: {                   // Optional: window specification
          documents: [ <lower>, <upper> ],
          // OR
          range: [ <lower>, <upper> ],
          unit: <timeUnit>          // For date ranges
        }
      }
    }
  }
}
```

### Simple Example

```javascript
// Add running total
db.sales.aggregate([
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        runningTotal: {
          $sum: "$revenue",
          window: {
            documents: ["unbounded", "current"]
          }
        }
      }
    }
  },
  { $project: { date: 1, revenue: 1, runningTotal: 1 } }
])
```

---

## Window Operators

### Available Operators

| Category | Operators |
|----------|-----------|
| **Ranking** | `$rank`, `$denseRank`, `$documentNumber` |
| **Aggregate** | `$sum`, `$avg`, `$min`, `$max`, `$count`, `$stdDevPop`, `$stdDevSamp` |
| **Position** | `$first`, `$last`, `$shift` |
| **Accumulator** | `$push`, `$addToSet` |
| **Derivative** | `$derivative`, `$integral` |
| **Exponential** | `$expMovingAvg` |
| **Covariance** | `$covariancePop`, `$covarianceSamp` |

---

## Ranking Functions

### $rank

```javascript
// Rank employees by salary within department
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        salaryRank: { $rank: {} }
      }
    }
  }
])

// Output:
// { name: "Alice", department: "Engineering", salary: 95000, salaryRank: 1 }
// { name: "Bob", department: "Engineering", salary: 85000, salaryRank: 2 }
// { name: "Charlie", department: "Engineering", salary: 85000, salaryRank: 2 }
// { name: "Eve", department: "Sales", salary: 80000, salaryRank: 1 }
// ...
```

### $denseRank

```javascript
// Dense rank (no gaps)
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        rank: { $rank: {} },
        denseRank: { $denseRank: {} }
      }
    }
  },
  { $match: { department: "Engineering" } }
])

// Output:
// { name: "Alice", salary: 95000, rank: 1, denseRank: 1 }
// { name: "Bob", salary: 85000, rank: 2, denseRank: 2 }
// { name: "Charlie", salary: 85000, rank: 2, denseRank: 2 }
// (next would be rank: 4, denseRank: 3)
```

### $documentNumber

```javascript
// Sequential row number
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        rowNum: { $documentNumber: {} }
      }
    }
  }
])

// Output:
// { name: "Alice", department: "Engineering", salary: 95000, rowNum: 1 }
// { name: "Bob", department: "Engineering", salary: 85000, rowNum: 2 }
// { name: "Charlie", department: "Engineering", salary: 85000, rowNum: 3 }
// ...
```

### Ranking Comparison

```javascript
// Compare all ranking functions
db.employees.aggregate([
  {
    $setWindowFields: {
      sortBy: { salary: -1 },
      output: {
        rank: { $rank: {} },
        denseRank: { $denseRank: {} },
        rowNumber: { $documentNumber: {} }
      }
    }
  },
  {
    $project: {
      name: 1,
      salary: 1,
      rank: 1,
      denseRank: 1,
      rowNumber: 1
    }
  }
])
```

---

## Aggregate Window Functions

### Running Total

```javascript
// Running total by date
db.sales.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        cumulativeRevenue: {
          $sum: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      cumulativeRevenue: 1
    }
  }
])
```

### Running Average

```javascript
// Running average revenue
db.sales.aggregate([
  {
    $setWindowFields: {
      sortBy: { date: 1, _id: 1 },
      output: {
        runningAvg: {
          $avg: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      runningAvg: { $round: ["$runningAvg", 2] }
    }
  }
])
```

### Partition Running Total

```javascript
// Running total per product
db.sales.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$product",
      sortBy: { date: 1 },
      output: {
        productCumulativeRevenue: {
          $sum: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      product: 1,
      revenue: 1,
      productCumulativeRevenue: 1
    }
  }
])
```

### Min/Max Over Window

```javascript
// Track high water mark
db.sales.aggregate([
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        maxRevenueSoFar: {
          $max: "$revenue",
          window: { documents: ["unbounded", "current"] }
        },
        minRevenueSoFar: {
          $min: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      maxRevenueSoFar: 1,
      minRevenueSoFar: 1,
      isNewHigh: { $eq: ["$revenue", "$maxRevenueSoFar"] }
    }
  }
])
```

---

## Document-Based Windows

### Fixed Window Size

```javascript
// 3-day moving average (current + 2 previous)
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        movingAvg3Day: {
          $avg: "$dailyRevenue",
          window: { documents: [-2, 0] }  // 2 before + current
        }
      }
    }
  },
  {
    $project: {
      date: "$_id",
      dailyRevenue: 1,
      movingAvg3Day: { $round: ["$movingAvg3Day", 2] }
    }
  }
])
```

### Window Boundaries

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Document Window Boundaries                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  documents: [lower, upper]                                         │
│                                                                     │
│  "unbounded" = from/to the partition boundary                      │
│  "current"   = the current document                                │
│  -N          = N documents before current                          │
│  +N          = N documents after current                           │
│                                                                     │
│  Examples:                                                         │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ ["unbounded", "current"]  = All from start to current      │    │
│  │ ["unbounded", "unbounded"]= All documents in partition     │    │
│  │ [-2, 0]                   = Previous 2 + current           │    │
│  │ [0, 2]                    = Current + next 2               │    │
│  │ [-1, 1]                   = Previous, current, next        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Centered Window

```javascript
// Centered 5-point moving average
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        centeredAvg: {
          $avg: "$dailyRevenue",
          window: { documents: [-2, 2] }  // 2 before, current, 2 after
        }
      }
    }
  }
])
```

### $shift - Access Adjacent Documents

```javascript
// Compare to previous day
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        previousDayRevenue: {
          $shift: {
            output: "$dailyRevenue",
            by: -1,
            default: 0
          }
        }
      }
    }
  },
  {
    $project: {
      date: "$_id",
      dailyRevenue: 1,
      previousDayRevenue: 1,
      change: { $subtract: ["$dailyRevenue", "$previousDayRevenue"] },
      changePercent: {
        $cond: [
          { $eq: ["$previousDayRevenue", 0] },
          null,
          {
            $round: [
              {
                $multiply: [
                  { $divide: [{ $subtract: ["$dailyRevenue", "$previousDayRevenue"] }, "$previousDayRevenue"] },
                  100
                ]
              },
              2
            ]
          }
        ]
      }
    }
  }
])
```

---

## Range-Based Windows

### Numeric Range

```javascript
// Sum of sales within $100 revenue range
db.sales.aggregate([
  {
    $setWindowFields: {
      sortBy: { revenue: 1 },
      output: {
        revenueInRange: {
          $sum: "$revenue",
          window: {
            range: [-100, 100]
          }
        }
      }
    }
  }
])
```

### Time-Based Range

```javascript
// Sum of last 2 days
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        twoDay Revenue: {
          $sum: "$dailyRevenue",
          window: {
            range: [-2, 0],
            unit: "day"
          }
        }
      }
    }
  }
])
```

### Exponential Moving Average

```javascript
// Exponential moving average
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        ema: {
          $expMovingAvg: {
            input: "$dailyRevenue",
            N: 3  // Number of periods
          }
        }
      }
    }
  },
  {
    $project: {
      date: "$_id",
      dailyRevenue: 1,
      ema: { $round: ["$ema", 2] }
    }
  }
])

// Alternative: using alpha (smoothing factor)
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        ema: {
          $expMovingAvg: {
            input: "$dailyRevenue",
            alpha: 0.5  // Smoothing factor (0-1)
          }
        }
      }
    }
  }
])
```

---

## Practical Applications

### Sales Performance Dashboard

```javascript
// Comprehensive sales analytics
db.sales.aggregate([
  {
    $group: {
      _id: { date: "$date", region: "$region" },
      dailyRevenue: { $sum: "$revenue" },
      totalQuantity: { $sum: "$quantity" }
    }
  },
  { $sort: { "_id.date": 1 } },
  {
    $setWindowFields: {
      partitionBy: "$_id.region",
      sortBy: { "_id.date": 1 },
      output: {
        // Running total for region
        regionCumulativeRevenue: {
          $sum: "$dailyRevenue",
          window: { documents: ["unbounded", "current"] }
        },
        // 3-day moving average
        regionMovingAvg: {
          $avg: "$dailyRevenue",
          window: { documents: [-2, 0] }
        },
        // Rank within region
        dayRank: { $rank: {} }
      }
    }
  },
  {
    $project: {
      date: "$_id.date",
      region: "$_id.region",
      dailyRevenue: 1,
      regionCumulativeRevenue: 1,
      regionMovingAvg: { $round: ["$regionMovingAvg", 2] },
      dayRank: 1
    }
  }
])
```

### Employee Salary Analysis

```javascript
// Salary analytics with percentiles
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        // Ranking
        deptRank: { $denseRank: {} },
        rowNum: { $documentNumber: {} },
        
        // Department stats
        deptAvgSalary: {
          $avg: "$salary",
          window: { documents: ["unbounded", "unbounded"] }
        },
        deptMaxSalary: {
          $max: "$salary",
          window: { documents: ["unbounded", "unbounded"] }
        },
        deptMinSalary: {
          $min: "$salary",
          window: { documents: ["unbounded", "unbounded"] }
        },
        deptTotalSalary: {
          $sum: "$salary",
          window: { documents: ["unbounded", "unbounded"] }
        },
        deptCount: {
          $count: {},
          window: { documents: ["unbounded", "unbounded"] }
        }
      }
    }
  },
  {
    $project: {
      name: 1,
      department: 1,
      salary: 1,
      deptRank: 1,
      deptAvgSalary: { $round: ["$deptAvgSalary", 0] },
      salaryVsAvg: { $round: [{ $subtract: ["$salary", "$deptAvgSalary"] }, 0] },
      percentOfMax: {
        $round: [{ $multiply: [{ $divide: ["$salary", "$deptMaxSalary"] }, 100] }, 1]
      },
      percentOfTotal: {
        $round: [{ $multiply: [{ $divide: ["$salary", "$deptTotalSalary"] }, 100] }, 1]
      }
    }
  }
])
```

### Top N Per Group

```javascript
// Top 2 highest paid per department
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        deptRank: { $rank: {} }
      }
    }
  },
  { $match: { deptRank: { $lte: 2 } } },
  {
    $project: {
      name: 1,
      department: 1,
      salary: 1,
      deptRank: 1
    }
  }
])
```

### Year-over-Year Comparison

```javascript
// Setup monthly data
db.monthlySales.drop()
db.monthlySales.insertMany([
  { month: ISODate("2023-01-01"), revenue: 10000 },
  { month: ISODate("2023-02-01"), revenue: 12000 },
  { month: ISODate("2023-03-01"), revenue: 15000 },
  { month: ISODate("2024-01-01"), revenue: 11000 },
  { month: ISODate("2024-02-01"), revenue: 14000 },
  { month: ISODate("2024-03-01"), revenue: 18000 }
])

// Compare to same month last year
db.monthlySales.aggregate([
  {
    $addFields: {
      monthOfYear: { $month: "$month" }
    }
  },
  {
    $setWindowFields: {
      partitionBy: "$monthOfYear",
      sortBy: { month: 1 },
      output: {
        previousYearRevenue: {
          $shift: {
            output: "$revenue",
            by: -1,
            default: null
          }
        }
      }
    }
  },
  {
    $project: {
      month: 1,
      revenue: 1,
      previousYearRevenue: 1,
      yoyGrowth: {
        $cond: [
          { $eq: ["$previousYearRevenue", null] },
          null,
          {
            $round: [
              {
                $multiply: [
                  { $divide: [{ $subtract: ["$revenue", "$previousYearRevenue"] }, "$previousYearRevenue"] },
                  100
                ]
              },
              1
            ]
          }
        ]
      }
    }
  },
  { $sort: { month: 1 } }
])
```

### Gap Detection

```javascript
// Find gaps in sequential data
db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      totalRevenue: { $sum: "$revenue" }
    }
  },
  { $sort: { _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { _id: 1 },
      output: {
        previousDate: {
          $shift: {
            output: "$_id",
            by: -1
          }
        }
      }
    }
  },
  {
    $addFields: {
      daysSincePrevious: {
        $cond: [
          { $eq: ["$previousDate", null] },
          null,
          {
            $dateDiff: {
              startDate: "$previousDate",
              endDate: "$_id",
              unit: "day"
            }
          }
        ]
      }
    }
  },
  {
    $match: {
      daysSincePrevious: { $gt: 1 }
    }
  },
  {
    $project: {
      date: "$_id",
      previousDate: 1,
      gapDays: { $subtract: ["$daysSincePrevious", 1] }
    }
  }
])
```

---

## Summary

### Window Operators Reference

| Operator | Description |
|----------|-------------|
| **$rank** | Rank with gaps for ties |
| **$denseRank** | Rank without gaps |
| **$documentNumber** | Sequential row number |
| **$sum** | Running/window sum |
| **$avg** | Running/window average |
| **$min** | Window minimum |
| **$max** | Window maximum |
| **$count** | Window count |
| **$first** | First in window |
| **$last** | Last in window |
| **$shift** | Access adjacent documents |
| **$expMovingAvg** | Exponential moving average |

### Window Boundaries

| Specification | Description |
|---------------|-------------|
| `["unbounded", "current"]` | All previous + current |
| `["unbounded", "unbounded"]` | All in partition |
| `[-N, 0]` | Previous N + current |
| `[0, N]` | Current + next N |
| `[-N, N]` | Centered window |
| `range: [-X, X]` | Numeric range |
| `range: [-X, X], unit: "day"` | Time range |

### What's Next?

In the next chapter, we'll explore Aggregation Performance and Optimization.

---

## Practice Questions

1. What's the difference between $group and window functions?
2. How does $rank differ from $denseRank?
3. What does the window `["unbounded", "current"]` mean?
4. How do you calculate a 3-day moving average?
5. What's the purpose of $shift?
6. How do you get the top N per group using window functions?
7. What's the difference between document and range windows?
8. How do you calculate year-over-year change?

---

## Hands-On Exercises

### Exercise 1: Basic Rankings

```javascript
// Using the employees data:

// 1. Rank all employees by salary (global)
db.employees.aggregate([
  {
    $setWindowFields: {
      sortBy: { salary: -1 },
      output: {
        overallRank: { $rank: {} }
      }
    }
  },
  { $sort: { overallRank: 1 } }
])

// 2. Rank within department
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        deptRank: { $rank: {} },
        denseRank: { $denseRank: {} },
        rowNum: { $documentNumber: {} }
      }
    }
  },
  { $sort: { department: 1, deptRank: 1 } }
])

// 3. Get highest paid per department
db.employees.aggregate([
  {
    $setWindowFields: {
      partitionBy: "$department",
      sortBy: { salary: -1 },
      output: {
        rank: { $rank: {} }
      }
    }
  },
  { $match: { rank: 1 } },
  { $project: { name: 1, department: 1, salary: 1 } }
])
```

### Exercise 2: Running Calculations

```javascript
// Using sales data:

// 1. Running total revenue
db.sales.aggregate([
  { $sort: { date: 1, _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1, _id: 1 },
      output: {
        runningTotal: {
          $sum: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  { $project: { date: 1, revenue: 1, runningTotal: 1 } }
])

// 2. Running total per product
db.sales.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      partitionBy: "$product",
      sortBy: { date: 1, _id: 1 },
      output: {
        productRunningTotal: {
          $sum: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  { $project: { date: 1, product: 1, revenue: 1, productRunningTotal: 1 } }
])

// 3. Running average
db.sales.aggregate([
  { $sort: { date: 1, _id: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1, _id: 1 },
      output: {
        runningAvg: {
          $avg: "$revenue",
          window: { documents: ["unbounded", "current"] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      runningAvg: { $round: ["$runningAvg", 2] }
    }
  }
])
```

### Exercise 3: Moving Averages

```javascript
// Daily aggregated moving averages

// 1. Prepare daily data
const dailyData = db.sales.aggregate([
  {
    $group: {
      _id: "$date",
      dailyRevenue: { $sum: "$revenue" },
      dailyQuantity: { $sum: "$quantity" }
    }
  },
  { $sort: { _id: 1 } }
]).toArray()

// Create temp collection
db.dailySales.drop()
db.dailySales.insertMany(dailyData.map(d => ({
  date: d._id,
  revenue: d.dailyRevenue,
  quantity: d.dailyQuantity
})))

// 2. 3-day simple moving average
db.dailySales.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        sma3: {
          $avg: "$revenue",
          window: { documents: [-2, 0] }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      sma3: { $round: ["$sma3", 2] }
    }
  }
])

// 3. Exponential moving average
db.dailySales.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        ema: {
          $expMovingAvg: {
            input: "$revenue",
            N: 3
          }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      ema: { $round: ["$ema", 2] }
    }
  }
])
```

### Exercise 4: Day-over-Day Comparison

```javascript
// Compare each day to previous

db.dailySales.aggregate([
  { $sort: { date: 1 } },
  {
    $setWindowFields: {
      sortBy: { date: 1 },
      output: {
        previousRevenue: {
          $shift: {
            output: "$revenue",
            by: -1,
            default: null
          }
        },
        previousDate: {
          $shift: {
            output: "$date",
            by: -1,
            default: null
          }
        }
      }
    }
  },
  {
    $project: {
      date: 1,
      revenue: 1,
      previousRevenue: 1,
      change: {
        $cond: [
          { $eq: ["$previousRevenue", null] },
          null,
          { $subtract: ["$revenue", "$previousRevenue"] }
        ]
      },
      changePercent: {
        $cond: [
          { $eq: ["$previousRevenue", null] },
          null,
          {
            $round: [
              {
                $multiply: [
                  { $divide: [{ $subtract: ["$revenue", "$previousRevenue"] }, "$previousRevenue"] },
                  100
                ]
              },
              1
            ]
          }
        ]
      }
    }
  }
])
```

### Exercise 5: Comprehensive Analytics

```javascript
// Full sales analytics dashboard

db.sales.aggregate([
  // First aggregate by date and region
  {
    $group: {
      _id: { date: "$date", region: "$region" },
      revenue: { $sum: "$revenue" },
      quantity: { $sum: "$quantity" },
      transactions: { $sum: 1 }
    }
  },
  { $sort: { "_id.date": 1 } },
  
  // Add window calculations
  {
    $setWindowFields: {
      partitionBy: "$_id.region",
      sortBy: { "_id.date": 1 },
      output: {
        // Running metrics
        cumulativeRevenue: {
          $sum: "$revenue",
          window: { documents: ["unbounded", "current"] }
        },
        // Moving average
        movingAvg: {
          $avg: "$revenue",
          window: { documents: [-2, 0] }
        },
        // Max so far
        maxRevenueSoFar: {
          $max: "$revenue",
          window: { documents: ["unbounded", "current"] }
        },
        // Previous day
        previousRevenue: {
          $shift: { output: "$revenue", by: -1 }
        },
        // Rank
        dayRank: { $rank: {} }
      }
    }
  },
  
  // Add calculated fields
  {
    $addFields: {
      isNewHigh: { $eq: ["$revenue", "$maxRevenueSoFar"] },
      dayOverDayChange: {
        $cond: [
          { $eq: ["$previousRevenue", null] },
          null,
          { $subtract: ["$revenue", "$previousRevenue"] }
        ]
      }
    }
  },
  
  // Final projection
  {
    $project: {
      date: "$_id.date",
      region: "$_id.region",
      revenue: 1,
      quantity: 1,
      transactions: 1,
      cumulativeRevenue: 1,
      movingAvg: { $round: ["$movingAvg", 2] },
      dayRank: 1,
      isNewHigh: 1,
      dayOverDayChange: 1
    }
  },
  
  { $sort: { "_id.region": 1, date: 1 } }
])
```

---

[← Previous: $facet and Multi-faceted Aggregations](27-facet-and-multifaceted-aggregations.md) | [Next: Aggregation Performance →](29-aggregation-performance.md)
