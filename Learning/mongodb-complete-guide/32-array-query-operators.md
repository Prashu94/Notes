# Chapter 32: Array Query Operators

## Table of Contents
- [Introduction to Array Queries](#introduction-to-array-queries)
- [Basic Array Matching](#basic-array-matching)
- [$elemMatch Operator](#elemmatch-operator)
- [$all Operator](#all-operator)
- [$size Operator](#size-operator)
- [Array Indexing](#array-indexing)
- [Querying Arrays of Objects](#querying-arrays-of-objects)
- [Combining Array Operators](#combining-array-operators)
- [Summary](#summary)

---

## Introduction to Array Queries

MongoDB provides powerful operators for querying arrays. Understanding how these operators work is essential for effective document-based data modeling.

### Array Query Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Array Query Operators                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $elemMatch   - Match array element satisfying multiple conditions │
│  $all         - Match arrays containing all specified elements     │
│  $size        - Match arrays with specific length                  │
│  $in          - Match if any array element matches any value       │
│  $nin         - Match if no array element matches any value        │
│  field.index  - Match specific array position                      │
│  field.$      - Positional projection operator                     │
│  field.$[]    - All positional operator (update)                   │
│  field.$[id]  - Filtered positional operator (update)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Products with tags (simple arrays)
db.products.drop()
db.products.insertMany([
  { 
    _id: 1, 
    name: "Laptop", 
    tags: ["electronics", "computer", "portable"],
    ratings: [4, 5, 4, 3, 5]
  },
  { 
    _id: 2, 
    name: "Smartphone", 
    tags: ["electronics", "mobile", "portable"],
    ratings: [5, 5, 4, 5]
  },
  { 
    _id: 3, 
    name: "Desk", 
    tags: ["furniture", "office"],
    ratings: [3, 4, 4]
  },
  { 
    _id: 4, 
    name: "Monitor", 
    tags: ["electronics", "computer", "display"],
    ratings: [4, 4, 5, 4, 4]
  },
  { 
    _id: 5, 
    name: "Chair", 
    tags: ["furniture", "office", "ergonomic"],
    ratings: [5, 5, 5]
  }
])

// Orders with items (arrays of objects)
db.orders.drop()
db.orders.insertMany([
  {
    _id: 1,
    customer: "Alice",
    items: [
      { product: "Laptop", quantity: 1, price: 1200 },
      { product: "Mouse", quantity: 2, price: 25 }
    ],
    status: "completed"
  },
  {
    _id: 2,
    customer: "Bob",
    items: [
      { product: "Monitor", quantity: 2, price: 350 },
      { product: "Keyboard", quantity: 1, price: 75 }
    ],
    status: "pending"
  },
  {
    _id: 3,
    customer: "Charlie",
    items: [
      { product: "Chair", quantity: 4, price: 200 },
      { product: "Desk", quantity: 2, price: 400 }
    ],
    status: "completed"
  },
  {
    _id: 4,
    customer: "Diana",
    items: [
      { product: "Laptop", quantity: 1, price: 1200 },
      { product: "Monitor", quantity: 1, price: 350 },
      { product: "Keyboard", quantity: 1, price: 75 }
    ],
    status: "shipped"
  }
])

// Students with scores (arrays of objects with varied structures)
db.students.drop()
db.students.insertMany([
  {
    _id: 1,
    name: "John",
    scores: [
      { subject: "Math", score: 85, grade: "B" },
      { subject: "English", score: 92, grade: "A" },
      { subject: "Science", score: 78, grade: "C" }
    ]
  },
  {
    _id: 2,
    name: "Jane",
    scores: [
      { subject: "Math", score: 95, grade: "A" },
      { subject: "English", score: 88, grade: "B" },
      { subject: "Science", score: 91, grade: "A" }
    ]
  },
  {
    _id: 3,
    name: "Mike",
    scores: [
      { subject: "Math", score: 72, grade: "C" },
      { subject: "English", score: 85, grade: "B" },
      { subject: "Science", score: 88, grade: "B" }
    ]
  }
])
```

---

## Basic Array Matching

### Exact Array Match

```javascript
// Match exact array (order and elements must match exactly)
db.products.find({ tags: ["electronics", "computer", "portable"] })
// Returns: Laptop only

// Different order - NO MATCH
db.products.find({ tags: ["computer", "electronics", "portable"] })
// Returns: nothing

// Different length - NO MATCH
db.products.find({ tags: ["electronics", "computer"] })
// Returns: nothing
```

### Single Element Match

```javascript
// Match if array contains the element
db.products.find({ tags: "electronics" })
// Returns: Laptop, Smartphone, Monitor

// Match multiple possible values with $in
db.products.find({ tags: { $in: ["electronics", "furniture"] } })
// Returns: all products (each has at least one)

// Match NOT containing value
db.products.find({ tags: { $ne: "electronics" } })
// Returns: Desk, Chair
```

### Range Queries on Arrays

```javascript
// Match if ANY element satisfies condition
db.products.find({ ratings: { $gt: 4 } })
// Returns: products with at least one rating > 4

// This is DIFFERENT from scalar field behavior!
// { ratings: { $gt: 3, $lt: 5 } }
// Matches if ANY element > 3 AND ANY element < 5
// (not necessarily the same element)

db.products.find({ ratings: { $gt: 3, $lt: 5 } })
// Returns products where:
// - some rating > 3 (could be 4 or 5)
// - AND some rating < 5 (could be 3 or 4)
```

---

## $elemMatch Operator

### Understanding $elemMatch

```javascript
// $elemMatch ensures ALL conditions match SAME element

// Without $elemMatch - conditions can match different elements
db.products.find({
  ratings: { $gte: 4, $lte: 4 }
})
// Matches if: some rating >= 4 AND some rating <= 4
// Could be rating=5 (>=4) and rating=3 (<=4)

// With $elemMatch - all conditions must match same element
db.products.find({
  ratings: { $elemMatch: { $gte: 4, $lte: 4 } }
})
// Matches only if: some single rating is exactly 4
```

### $elemMatch with Objects

```javascript
// Find orders with item: quantity > 1 AND price > 100
// WRONG: These could match different items
db.orders.find({
  "items.quantity": { $gt: 1 },
  "items.price": { $gt: 100 }
})
// Matches: Bob's order (Monitor qty=2, price=350)
// Also matches incorrectly if qty>1 and price>100 are in different items

// CORRECT: Same item must satisfy both conditions
db.orders.find({
  items: {
    $elemMatch: {
      quantity: { $gt: 1 },
      price: { $gt: 100 }
    }
  }
})
// Returns: Bob (Monitor qty=2, price=350), Charlie (Chair qty=4, price=200)
```

### $elemMatch for Projection

```javascript
// Project only the first matching array element
db.students.find(
  { "scores.score": { $gte: 90 } },
  { name: 1, "scores.$": 1 }
)
// Returns first matching score for each student

// Use $elemMatch projection for more control
db.students.find(
  { name: "Jane" },
  { 
    name: 1,
    scores: { $elemMatch: { grade: "A" } }
  }
)
// Returns Jane with only first score where grade = "A"
```

### Complex $elemMatch

```javascript
// Multiple conditions on nested object
db.students.find({
  scores: {
    $elemMatch: {
      subject: "Math",
      score: { $gte: 80 },
      grade: { $in: ["A", "B"] }
    }
  }
})
// Returns students with Math score >= 80 AND grade A or B

// Nested $or within $elemMatch
db.orders.find({
  items: {
    $elemMatch: {
      $or: [
        { product: "Laptop" },
        { price: { $gt: 300 } }
      ]
    }
  }
})
```

---

## $all Operator

### Basic $all Usage

```javascript
// Match arrays containing ALL specified elements (any order)
db.products.find({ tags: { $all: ["electronics", "portable"] } })
// Returns: Laptop, Smartphone (both have electronics AND portable)

// Order doesn't matter
db.products.find({ tags: { $all: ["portable", "electronics"] } })
// Same result

// All values must be present
db.products.find({ tags: { $all: ["electronics", "portable", "office"] } })
// Returns: nothing (no product has all three)
```

### $all vs Exact Match vs $in

```javascript
// EXACT MATCH: Order and length must match exactly
db.products.find({ tags: ["electronics", "computer", "portable"] })
// Only Laptop

// $all: All specified must be present, order doesn't matter
db.products.find({ tags: { $all: ["computer", "electronics"] } })
// Laptop and Monitor

// $in: At least one must be present
db.products.find({ tags: { $in: ["computer", "furniture"] } })
// Laptop, Monitor, Desk, Chair
```

### $all with $elemMatch

```javascript
// $all with $elemMatch for arrays of objects
db.students.find({
  scores: {
    $all: [
      { $elemMatch: { subject: "Math", score: { $gte: 80 } } },
      { $elemMatch: { subject: "Science", score: { $gte: 80 } } }
    ]
  }
})
// Returns students with both:
// - Math score >= 80
// - Science score >= 80
// (Jane matches)
```

---

## $size Operator

### Basic $size Usage

```javascript
// Match arrays with exact size
db.products.find({ tags: { $size: 3 } })
// Returns: Laptop, Smartphone, Chair (all have exactly 3 tags)

db.products.find({ tags: { $size: 2 } })
// Returns: Desk (has exactly 2 tags)

db.products.find({ ratings: { $size: 5 } })
// Returns: Laptop, Monitor
```

### Limitations of $size

```javascript
// ⚠️ $size cannot use indexes
// ⚠️ $size does not accept ranges

// This does NOT work:
// db.products.find({ tags: { $size: { $gt: 2 } } })  // ERROR!

// Workaround: Use $expr with $size operator
db.products.find({
  $expr: { $gt: [{ $size: "$tags" }, 2] }
})
// Returns products with more than 2 tags

// Or check if specific position exists
db.products.find({ "tags.2": { $exists: true } })
// Returns products with at least 3 tags (index 2 exists)

db.products.find({ 
  "tags.2": { $exists: true },
  "tags.3": { $exists: false }
})
// Returns products with exactly 3 tags
```

### Size-Based Patterns

```javascript
// Find non-empty arrays
db.products.find({
  $expr: { $gt: [{ $size: "$ratings" }, 0] }
})

// Or simpler (if field always exists):
db.products.find({ "ratings.0": { $exists: true } })

// Find empty arrays
db.products.find({ ratings: { $size: 0 } })
// Or
db.products.find({ ratings: [] })
```

---

## Array Indexing

### Position-Based Queries

```javascript
// Query specific array position (0-indexed)
db.products.find({ "tags.0": "electronics" })
// Products where first tag is "electronics"

db.products.find({ "tags.1": "computer" })
// Products where second tag is "computer"

// Range on specific position
db.products.find({ "ratings.0": { $gte: 4 } })
// Products where first rating is >= 4
```

### Negative Index (Not Supported in Queries)

```javascript
// ⚠️ Negative indexing NOT supported in queries
// db.products.find({ "tags.-1": "portable" })  // Won't work as expected

// Use aggregation for last element:
db.products.aggregate([
  {
    $match: {
      $expr: {
        $eq: [
          { $arrayElemAt: ["$tags", -1] },
          "portable"
        ]
      }
    }
  }
])
```

### Positional Projection

```javascript
// $ returns first matching element
db.students.find(
  { "scores.score": { $gte: 90 } },
  { name: 1, "scores.$": 1 }
)
// Returns name and first score with score >= 90

// $slice returns subset of array
db.products.find(
  {},
  { name: 1, ratings: { $slice: 3 } }
)
// Returns first 3 ratings

db.products.find(
  {},
  { name: 1, ratings: { $slice: -2 } }
)
// Returns last 2 ratings

db.products.find(
  {},
  { name: 1, ratings: { $slice: [1, 2] } }
)
// Skip 1, return 2 (ratings at index 1 and 2)
```

---

## Querying Arrays of Objects

### Dot Notation for Nested Fields

```javascript
// Query nested field in array elements
db.orders.find({ "items.product": "Laptop" })
// Returns orders containing a Laptop

db.orders.find({ "items.price": { $gt: 500 } })
// Returns orders with any item price > 500

// Multiple conditions (MAY match different elements)
db.orders.find({
  "items.product": "Laptop",
  "items.quantity": 1
})
// Could match order where one item is Laptop, another has qty 1
```

### Ensuring Same Element Match

```javascript
// ✓ $elemMatch ensures same element
db.orders.find({
  items: {
    $elemMatch: {
      product: "Laptop",
      quantity: 1
    }
  }
})
// Returns orders where same item is Laptop AND qty 1

// Complex nested conditions
db.students.find({
  scores: {
    $elemMatch: {
      subject: { $in: ["Math", "Science"] },
      score: { $gte: 85 },
      grade: "A"
    }
  }
})
```

### Querying Multiple Levels

```javascript
// Setup deeply nested data
db.catalog.drop()
db.catalog.insertOne({
  _id: 1,
  category: "Electronics",
  products: [
    {
      name: "Phone",
      variants: [
        { color: "Black", price: 999, stock: 50 },
        { color: "White", price: 999, stock: 30 },
        { color: "Blue", price: 1049, stock: 10 }
      ]
    },
    {
      name: "Tablet",
      variants: [
        { color: "Silver", price: 799, stock: 25 },
        { color: "Gold", price: 849, stock: 15 }
      ]
    }
  ]
})

// Query nested array element
db.catalog.find({ "products.variants.color": "Blue" })

// $elemMatch at each level
db.catalog.find({
  products: {
    $elemMatch: {
      name: "Phone",
      variants: {
        $elemMatch: {
          color: "Blue",
          stock: { $gt: 0 }
        }
      }
    }
  }
})
```

---

## Combining Array Operators

### $all with $size

```javascript
// Products with exactly these tags
db.products.find({
  tags: {
    $all: ["electronics", "portable"],
    $size: 3
  }
})
// Must have electronics AND portable AND exactly 3 tags total
```

### $elemMatch with Comparison

```javascript
// Complex array query
db.orders.find({
  items: {
    $elemMatch: {
      quantity: { $gte: 2 },
      price: { $gte: 100, $lte: 500 }
    }
  }
})
// Items with qty >= 2 AND 100 <= price <= 500
```

### Multiple Array Conditions

```javascript
// Products matching multiple array criteria
db.products.find({
  $and: [
    { tags: { $all: ["electronics"] } },
    { ratings: { $elemMatch: { $gte: 5 } } },
    { $expr: { $gte: [{ $size: "$ratings" }, 4] } }
  ]
})
// Electronics products with at least one 5-star rating and 4+ total ratings
```

### Aggregation for Complex Queries

```javascript
// When query operators aren't enough
db.orders.aggregate([
  {
    $match: {
      // Find orders with high-value items
      items: {
        $elemMatch: {
          $expr: {
            $gte: [
              { $multiply: ["$quantity", "$price"] },
              500
            ]
          }
        }
      }
    }
  }
])

// Better approach with aggregation
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $match: {
      $expr: {
        $gte: [
          { $multiply: ["$items.quantity", "$items.price"] },
          500
        ]
      }
    }
  },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      highValueItems: { $push: "$items" }
    }
  }
])
```

---

## Summary

### Array Query Operators

| Operator | Purpose | Example |
|----------|---------|---------|
| **Exact match** | Array equals exactly | `{ tags: ["a", "b"] }` |
| **Element match** | Contains element | `{ tags: "a" }` |
| **$all** | Contains all specified | `{ tags: { $all: ["a", "b"] } }` |
| **$size** | Exact array length | `{ tags: { $size: 3 } }` |
| **$elemMatch** | Element satisfies all | `{ arr: { $elemMatch: {...} } }` |
| **$in** | Element in list | `{ tags: { $in: ["a", "b"] } }` |
| **Position** | Specific index | `{ "tags.0": "a" }` |

### Query Behavior Comparison

| Query | Behavior |
|-------|----------|
| `{ arr: value }` | Array contains value |
| `{ arr: [a, b] }` | Array equals exactly [a, b] |
| `{ arr: { $all: [a, b] } }` | Array contains both a AND b |
| `{ arr: { $in: [a, b] } }` | Array contains a OR b |
| `{ arr: { $gt: x, $lt: y } }` | Some element >x AND some element <y |
| `{ arr: { $elemMatch: {...} } }` | Single element satisfies all |

### Projection Operators

| Operator | Purpose |
|----------|---------|
| `$` | First matching element |
| `$elemMatch` | First element matching criteria |
| `$slice` | Subset of array |

### What's Next?

In the next chapter, we'll explore Element and Type Operators.

---

## Practice Questions

1. What's the difference between `{ tags: "a" }` and `{ tags: ["a"] }`?
2. When should you use $elemMatch vs dot notation?
3. Can $size accept range queries?
4. How do you query the last element of an array?
5. What does `{ "arr.0": "value" }` match?
6. How does $all differ from $in?
7. What happens with `{ arr: { $gt: 5, $lt: 10 } }` on an array?
8. How do you find documents with arrays of specific size ranges?

---

## Hands-On Exercises

### Exercise 1: Basic Array Queries

```javascript
// Practice with products collection

// 1. Find all electronics products
print("1. Electronics products:")
db.products.find({ tags: "electronics" }).forEach(p => print("  -", p.name))

// 2. Find products with "electronics" AND "computer" tags
print("\n2. Electronics AND computer:")
db.products.find({ tags: { $all: ["electronics", "computer"] } }).forEach(p => print("  -", p.name))

// 3. Find products with exactly 3 tags
print("\n3. Exactly 3 tags:")
db.products.find({ tags: { $size: 3 } }).forEach(p => print("  -", p.name, ":", p.tags))

// 4. Find products with first tag "furniture"
print("\n4. First tag is furniture:")
db.products.find({ "tags.0": "furniture" }).forEach(p => print("  -", p.name))

// 5. Find products with any rating of 5
print("\n5. Has 5-star rating:")
db.products.find({ ratings: 5 }).forEach(p => print("  -", p.name))
```

### Exercise 2: $elemMatch Practice

```javascript
// Practice with orders collection

// 1. Orders with any item qty > 1 AND price > 100 (same item)
print("1. Items with qty > 1 AND price > 100:")
db.orders.find({
  items: { $elemMatch: { quantity: { $gt: 1 }, price: { $gt: 100 } } }
}).forEach(o => {
  print("  Order", o._id, "- Customer:", o.customer)
})

// 2. Compare with vs without $elemMatch
print("\n2. Without $elemMatch (qty > 1, price > 100 - could be different items):")
db.orders.find({
  "items.quantity": { $gt: 1 },
  "items.price": { $gt: 100 }
}).forEach(o => {
  print("  Order", o._id, "- Customer:", o.customer)
})

// 3. Orders containing Laptop with qty exactly 1
print("\n3. Laptop orders with qty = 1:")
db.orders.find({
  items: { $elemMatch: { product: "Laptop", quantity: 1 } }
}).forEach(o => print("  -", o.customer))
```

### Exercise 3: Student Scores

```javascript
// Practice with students collection

// 1. Students with any A grade
print("1. Students with A grade:")
db.students.find({ "scores.grade": "A" }).forEach(s => print("  -", s.name))

// 2. Students with A in Math specifically
print("\n2. Students with A in Math:")
db.students.find({
  scores: { $elemMatch: { subject: "Math", grade: "A" } }
}).forEach(s => print("  -", s.name))

// 3. Students with all scores >= 80
print("\n3. Students with all scores >= 80:")
db.students.find({
  "scores.score": { $not: { $lt: 80 } }
}).forEach(s => print("  -", s.name))

// 4. Students with Math score > English score (use aggregation)
print("\n4. Students with Math > English:")
db.students.aggregate([
  { $unwind: "$scores" },
  {
    $group: {
      _id: "$_id",
      name: { $first: "$name" },
      scores: { $push: { k: "$scores.subject", v: "$scores.score" } }
    }
  },
  {
    $project: {
      name: 1,
      scoreMap: { $arrayToObject: "$scores" }
    }
  },
  {
    $match: {
      $expr: { $gt: ["$scoreMap.Math", "$scoreMap.English"] }
    }
  }
]).forEach(s => print("  -", s.name))
```

### Exercise 4: Size Queries

```javascript
// Practice array size queries

// 1. Products with more than 3 ratings
print("1. Products with > 3 ratings:")
db.products.find({
  $expr: { $gt: [{ $size: "$ratings" }, 3] }
}).forEach(p => print("  -", p.name, ":", p.ratings.length, "ratings"))

// 2. Products with 2-3 tags
print("\n2. Products with 2-3 tags:")
db.products.find({
  "tags.1": { $exists: true },
  "tags.3": { $exists: false }
}).forEach(p => print("  -", p.name, ":", p.tags.length, "tags"))

// 3. Orders with exactly 2 items
print("\n3. Orders with exactly 2 items:")
db.orders.find({ items: { $size: 2 } }).forEach(o => print("  -", o.customer))

// 4. Orders with 3+ items
print("\n4. Orders with 3+ items:")
db.orders.find({
  "items.2": { $exists: true }
}).forEach(o => print("  -", o.customer, ":", o.items.length, "items"))
```

### Exercise 5: Complex Array Queries

```javascript
// Combine multiple array operators

// 1. Electronics products with 5 ratings and at least one perfect score
print("1. Electronics with 5 ratings and perfect score:")
db.products.find({
  tags: "electronics",
  ratings: { $size: 5 },
  ratings: 5
}).forEach(p => print("  -", p.name))

// Better version using $and
db.products.find({
  $and: [
    { tags: "electronics" },
    { ratings: { $size: 5 } },
    { ratings: 5 }
  ]
}).forEach(p => print("  -", p.name))

// 2. Orders with total value > 1000 (per item)
print("\n2. Orders with high-value items (qty * price > 500):")
db.orders.aggregate([
  { $unwind: "$items" },
  {
    $match: {
      $expr: { $gt: [{ $multiply: ["$items.quantity", "$items.price"] }, 500] }
    }
  },
  {
    $group: {
      _id: "$_id",
      customer: { $first: "$customer" },
      highValueItems: {
        $push: {
          product: "$items.product",
          value: { $multiply: ["$items.quantity", "$items.price"] }
        }
      }
    }
  }
]).forEach(o => {
  print("  -", o.customer)
  o.highValueItems.forEach(i => print("      ", i.product, ":", i.value))
})

// 3. Students who passed all subjects (score >= 70)
print("\n3. Students who passed all subjects:")
db.students.find({
  scores: {
    $not: {
      $elemMatch: { score: { $lt: 70 } }
    }
  }
}).forEach(s => print("  -", s.name))
```

---

[← Previous: Query Optimization](31-query-optimization.md) | [Next: Element and Type Operators →](33-element-type-operators.md)
