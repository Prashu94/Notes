# Chapter 8: Update Operations

## Table of Contents
- [Update Overview](#update-overview)
- [updateOne()](#updateone)
- [updateMany()](#updatemany)
- [replaceOne()](#replaceone)
- [Field Update Operators](#field-update-operators)
- [Array Update Operators](#array-update-operators)
- [Upsert Operations](#upsert-operations)
- [findAndModify Operations](#findandmodify-operations)
- [Summary](#summary)

---

## Update Overview

MongoDB provides several methods for updating documents, each suited for different use cases.

### Update Methods

| Method | Description |
|--------|-------------|
| `updateOne()` | Update first matching document |
| `updateMany()` | Update all matching documents |
| `replaceOne()` | Replace entire document |
| `findOneAndUpdate()` | Update and return document |
| `findOneAndReplace()` | Replace and return document |
| `bulkWrite()` | Batch update operations |

### Update Syntax

```javascript
db.collection.updateOne(
  { filter },           // Which documents to update
  { update },           // What changes to make
  { options }           // Additional options
)
```

---

## updateOne()

### Basic Update

```javascript
// Update single document
db.products.updateOne(
  { name: "Laptop" },           // Filter
  { $set: { price: 899 } }      // Update
)

// Result:
{
  acknowledged: true,
  matchedCount: 1,
  modifiedCount: 1
}
```

### Update with Multiple Fields

```javascript
db.products.updateOne(
  { name: "Laptop" },
  {
    $set: {
      price: 899,
      onSale: true,
      lastUpdated: new Date()
    }
  }
)
```

### Update Nested Fields

```javascript
// Update nested document field
db.users.updateOne(
  { _id: 1 },
  { $set: { "address.city": "Los Angeles" } }
)

// Update deeply nested field
db.users.updateOne(
  { _id: 1 },
  { $set: { "profile.settings.notifications.email": true } }
)
```

### Update with Options

```javascript
db.products.updateOne(
  { sku: "ABC123" },
  { $set: { price: 99.99 } },
  {
    upsert: false,                    // Don't insert if not found
    writeConcern: { w: "majority" },  // Write concern
    collation: { locale: "en" },      // Collation settings
    hint: { sku: 1 },                 // Index hint
    comment: "Price update"           // Operation comment
  }
)
```

---

## updateMany()

### Update All Matching Documents

```javascript
// Update all electronics
db.products.updateMany(
  { category: "Electronics" },
  { $set: { warranty: "1 year" } }
)

// Result:
{
  acknowledged: true,
  matchedCount: 5,
  modifiedCount: 5
}
```

### Bulk Price Update

```javascript
// Apply 10% discount to all products over $500
db.products.updateMany(
  { price: { $gt: 500 } },
  [
    {
      $set: {
        originalPrice: "$price",
        price: { $multiply: ["$price", 0.9] },
        discounted: true
      }
    }
  ]
)
```

### Update with Aggregation Pipeline (MongoDB 4.2+)

```javascript
// Using aggregation pipeline for complex updates
db.products.updateMany(
  { category: "Electronics" },
  [
    {
      $set: {
        lastModified: "$$NOW",
        priceCategory: {
          $switch: {
            branches: [
              { case: { $lt: ["$price", 100] }, then: "budget" },
              { case: { $lt: ["$price", 500] }, then: "mid-range" }
            ],
            default: "premium"
          }
        }
      }
    }
  ]
)
```

---

## replaceOne()

### Complete Document Replacement

```javascript
// Replace entire document (except _id)
db.products.replaceOne(
  { name: "Laptop" },
  {
    name: "Gaming Laptop",
    price: 1299,
    category: "Electronics",
    specs: {
      cpu: "Intel i7",
      ram: "16GB",
      storage: "512GB SSD"
    },
    updatedAt: new Date()
  }
)

// Note: All fields except _id are replaced
// Original fields not in replacement are removed!
```

### Replace vs Update

```javascript
// Original document:
{
  _id: 1,
  name: "Product",
  price: 100,
  stock: 50,
  tags: ["sale"]
}

// Using $set (keeps other fields)
db.products.updateOne(
  { _id: 1 },
  { $set: { price: 80 } }
)
// Result: { _id: 1, name: "Product", price: 80, stock: 50, tags: ["sale"] }

// Using replaceOne (removes unspecified fields)
db.products.replaceOne(
  { _id: 1 },
  { name: "Product", price: 80 }
)
// Result: { _id: 1, name: "Product", price: 80 }
// stock and tags are gone!
```

---

## Field Update Operators

### $set - Set Field Value

```javascript
// Set single field
db.products.updateOne(
  { _id: 1 },
  { $set: { status: "active" } }
)

// Set multiple fields
db.products.updateOne(
  { _id: 1 },
  {
    $set: {
      status: "active",
      price: 99.99,
      "metadata.updated": new Date()
    }
  }
)

// Set nested field (creates path if needed)
db.users.updateOne(
  { _id: 1 },
  { $set: { "preferences.theme.darkMode": true } }
)
```

### $unset - Remove Field

```javascript
// Remove single field
db.products.updateOne(
  { _id: 1 },
  { $unset: { temporaryField: "" } }  // Value doesn't matter
)

// Remove multiple fields
db.products.updateOne(
  { _id: 1 },
  {
    $unset: {
      oldField1: "",
      oldField2: "",
      "nested.oldField": ""
    }
  }
)
```

### $inc - Increment

```javascript
// Increment numeric field
db.products.updateOne(
  { _id: 1 },
  { $inc: { stock: 10 } }  // Add 10 to stock
)

// Decrement (use negative value)
db.products.updateOne(
  { _id: 1 },
  { $inc: { stock: -5 } }  // Subtract 5 from stock
)

// Multiple increments
db.users.updateOne(
  { _id: 1 },
  {
    $inc: {
      loginCount: 1,
      points: 10,
      "stats.views": 1
    }
  }
)
```

### $mul - Multiply

```javascript
// Multiply field value
db.products.updateOne(
  { _id: 1 },
  { $mul: { price: 1.1 } }  // Increase by 10%
)

// Discount
db.products.updateMany(
  { category: "Electronics" },
  { $mul: { price: 0.9 } }  // 10% off
)
```

### $min / $max - Update if Less/Greater

```javascript
// Set to new value only if less than current
db.products.updateOne(
  { _id: 1 },
  { $min: { price: 99 } }  // Set to 99 if current price > 99
)

// Set to new value only if greater than current
db.products.updateOne(
  { _id: 1 },
  { $max: { highScore: 500 } }  // Set to 500 if current < 500
)

// Useful for tracking min/max values
db.sensors.updateOne(
  { sensorId: "temp-001" },
  {
    $min: { minTemp: 18.5 },
    $max: { maxTemp: 32.1 },
    $set: { currentTemp: 25.3 }
  }
)
```

### $rename - Rename Field

```javascript
// Rename field
db.products.updateMany(
  {},
  { $rename: { "colour": "color" } }
)

// Rename nested field
db.users.updateMany(
  {},
  { $rename: { "address.zipcode": "address.postalCode" } }
)
```

### $setOnInsert - Set Only on Insert

```javascript
// Only applies during upsert insert
db.products.updateOne(
  { sku: "NEW001" },
  {
    $set: { name: "New Product", price: 99 },
    $setOnInsert: { 
      createdAt: new Date(),
      version: 1
    }
  },
  { upsert: true }
)
// createdAt and version only set if document is inserted
```

### $currentDate - Set Current Date

```javascript
// Set to current date
db.products.updateOne(
  { _id: 1 },
  {
    $currentDate: {
      lastModified: true,                    // Date type
      "timestamps.updated": { $type: "date" },
      "timestamps.epoch": { $type: "timestamp" }
    }
  }
)
```

---

## Array Update Operators

### $push - Add to Array

```javascript
// Add single element
db.products.updateOne(
  { _id: 1 },
  { $push: { tags: "new-tag" } }
)

// Add multiple elements
db.products.updateOne(
  { _id: 1 },
  { 
    $push: { 
      tags: { $each: ["tag1", "tag2", "tag3"] }
    }
  }
)

// Add with position
db.products.updateOne(
  { _id: 1 },
  {
    $push: {
      tags: {
        $each: ["urgent"],
        $position: 0  // Add at beginning
      }
    }
  }
)

// Add and maintain sorted order
db.leaderboard.updateOne(
  { _id: 1 },
  {
    $push: {
      scores: {
        $each: [{ player: "Alice", score: 95 }],
        $sort: { score: -1 }  // Sort descending
      }
    }
  }
)

// Add with slice (limit array size)
db.users.updateOne(
  { _id: 1 },
  {
    $push: {
      recentActivity: {
        $each: [{ action: "login", time: new Date() }],
        $slice: -10  // Keep last 10 elements
      }
    }
  }
)
```

### $push with All Modifiers

```javascript
// Complete example with all modifiers
db.posts.updateOne(
  { _id: 1 },
  {
    $push: {
      comments: {
        $each: [
          { user: "Alice", text: "Great!", time: new Date() },
          { user: "Bob", text: "Thanks!", time: new Date() }
        ],
        $position: 0,     // Add at beginning
        $sort: { time: -1 },  // Sort by time descending
        $slice: 100       // Keep only 100 comments
      }
    }
  }
)
```

### $addToSet - Add Unique Values

```javascript
// Add only if not exists
db.products.updateOne(
  { _id: 1 },
  { $addToSet: { tags: "unique-tag" } }
)

// Add multiple (only unique ones)
db.products.updateOne(
  { _id: 1 },
  {
    $addToSet: {
      tags: { $each: ["tag1", "tag2", "existing-tag"] }
    }
  }
)
```

### $pop - Remove First/Last Element

```javascript
// Remove last element
db.products.updateOne(
  { _id: 1 },
  { $pop: { tags: 1 } }
)

// Remove first element
db.products.updateOne(
  { _id: 1 },
  { $pop: { tags: -1 } }
)
```

### $pull - Remove by Value

```javascript
// Remove specific value
db.products.updateOne(
  { _id: 1 },
  { $pull: { tags: "old-tag" } }
)

// Remove with condition
db.products.updateOne(
  { _id: 1 },
  { $pull: { ratings: { $lt: 3 } } }  // Remove all ratings < 3
)

// Remove from array of objects
db.orders.updateOne(
  { _id: 1 },
  {
    $pull: {
      items: { product: "Discontinued Item" }
    }
  }
)
```

### $pullAll - Remove Multiple Values

```javascript
// Remove all specified values
db.products.updateOne(
  { _id: 1 },
  { $pullAll: { tags: ["tag1", "tag2", "tag3"] } }
)
```

### Positional Operators

```javascript
// $ - Update first matching element
db.orders.updateOne(
  { _id: 1, "items.product": "Laptop" },
  { $set: { "items.$.price": 899 } }
)

// $[] - Update all elements
db.orders.updateOne(
  { _id: 1 },
  { $inc: { "items.$[].quantity": 1 } }  // Increment all quantities
)

// $[<identifier>] - Update matching elements
db.orders.updateOne(
  { _id: 1 },
  { $set: { "items.$[elem].shipped": true } },
  { arrayFilters: [{ "elem.quantity": { $gte: 2 } }] }
)
```

### Array Filters for Complex Updates

```javascript
// Sample order document
{
  _id: 1,
  items: [
    { product: "A", qty: 5, status: "pending" },
    { product: "B", qty: 2, status: "pending" },
    { product: "C", qty: 10, status: "shipped" }
  ]
}

// Update items with qty >= 5 to "processing"
db.orders.updateOne(
  { _id: 1 },
  { $set: { "items.$[item].status": "processing" } },
  {
    arrayFilters: [
      { "item.qty": { $gte: 5 }, "item.status": "pending" }
    ]
  }
)

// Multiple conditions in array filters
db.orders.updateOne(
  { _id: 1 },
  {
    $set: {
      "items.$[high].priority": "high",
      "items.$[low].priority": "low"
    }
  },
  {
    arrayFilters: [
      { "high.qty": { $gte: 5 } },
      { "low.qty": { $lt: 5 } }
    ]
  }
)

// Nested array updates
// Document: { items: [{ name: "A", variants: [{ size: "S", stock: 10 }] }] }
db.products.updateOne(
  { _id: 1 },
  { $inc: { "items.$[item].variants.$[variant].stock": 5 } },
  {
    arrayFilters: [
      { "item.name": "A" },
      { "variant.size": "S" }
    ]
  }
)
```

---

## Upsert Operations

### Basic Upsert

```javascript
// Insert if not found, update if found
db.products.updateOne(
  { sku: "NEW001" },
  {
    $set: { name: "New Product", price: 99 },
    $setOnInsert: { createdAt: new Date() }
  },
  { upsert: true }
)

// Result when inserted:
{
  acknowledged: true,
  matchedCount: 0,
  modifiedCount: 0,
  upsertedId: ObjectId("...")
}

// Result when updated:
{
  acknowledged: true,
  matchedCount: 1,
  modifiedCount: 1
}
```

### Upsert Patterns

```javascript
// Counter pattern
db.counters.updateOne(
  { _id: "pageViews" },
  { $inc: { count: 1 } },
  { upsert: true }
)

// Last updated timestamp
db.cache.updateOne(
  { key: "userData" },
  {
    $set: { value: userData, updatedAt: new Date() },
    $setOnInsert: { createdAt: new Date() }
  },
  { upsert: true }
)

// Conditional insert with default values
db.users.updateOne(
  { email: "user@example.com" },
  {
    $set: { lastLogin: new Date() },
    $setOnInsert: {
      createdAt: new Date(),
      role: "user",
      isActive: true
    }
  },
  { upsert: true }
)
```

---

## findAndModify Operations

### findOneAndUpdate()

```javascript
// Update and return old document
const oldDoc = db.products.findOneAndUpdate(
  { sku: "ABC123" },
  { $inc: { stock: -1 } }
)

// Update and return new document
const newDoc = db.products.findOneAndUpdate(
  { sku: "ABC123" },
  { $inc: { stock: -1 } },
  { returnDocument: "after" }  // or "before" (default)
)

// With projection
const result = db.products.findOneAndUpdate(
  { sku: "ABC123" },
  { $inc: { stock: -1 } },
  {
    returnDocument: "after",
    projection: { sku: 1, stock: 1, _id: 0 }
  }
)

// With upsert
db.products.findOneAndUpdate(
  { sku: "NEW001" },
  {
    $set: { name: "New Product", price: 99 },
    $setOnInsert: { createdAt: new Date() }
  },
  {
    upsert: true,
    returnDocument: "after"
  }
)

// With sort (update first matching after sort)
db.jobs.findOneAndUpdate(
  { status: "pending" },
  { $set: { status: "processing", startedAt: new Date() } },
  {
    sort: { priority: -1, createdAt: 1 },
    returnDocument: "after"
  }
)
```

### findOneAndReplace()

```javascript
// Replace and return document
const result = db.products.findOneAndReplace(
  { sku: "ABC123" },
  {
    sku: "ABC123",
    name: "Replaced Product",
    price: 199,
    updatedAt: new Date()
  },
  { returnDocument: "after" }
)
```

### Atomic Update Patterns

```javascript
// Increment and return for unique IDs
function getNextSequence(name) {
  const result = db.counters.findOneAndUpdate(
    { _id: name },
    { $inc: { seq: 1 } },
    { upsert: true, returnDocument: "after" }
  )
  return result.seq
}

const orderId = getNextSequence("orderId")

// Claim a job atomically
function claimJob(workerId) {
  return db.jobs.findOneAndUpdate(
    { status: "pending" },
    {
      $set: {
        status: "processing",
        workerId: workerId,
        claimedAt: new Date()
      }
    },
    {
      sort: { priority: -1 },
      returnDocument: "after"
    }
  )
}

// Optimistic locking pattern
function updateWithVersion(id, updates) {
  const current = db.documents.findOne({ _id: id })
  
  const result = db.documents.findOneAndUpdate(
    { _id: id, version: current.version },
    {
      $set: { ...updates, updatedAt: new Date() },
      $inc: { version: 1 }
    },
    { returnDocument: "after" }
  )
  
  if (!result) {
    throw new Error("Document was modified by another process")
  }
  
  return result
}
```

---

## Bulk Write Operations

### Bulk Updates

```javascript
// Multiple update operations
db.products.bulkWrite([
  {
    updateOne: {
      filter: { sku: "ABC" },
      update: { $set: { price: 99 } }
    }
  },
  {
    updateMany: {
      filter: { category: "Electronics" },
      update: { $set: { department: "Tech" } }
    }
  },
  {
    replaceOne: {
      filter: { sku: "OLD" },
      replacement: { sku: "OLD", name: "Legacy", discontinued: true }
    }
  },
  {
    updateOne: {
      filter: { sku: "NEW" },
      update: { $setOnInsert: { createdAt: new Date() } },
      upsert: true
    }
  }
])
```

---

## Summary

### Update Operators Reference

| Category | Operators |
|----------|-----------|
| **Field** | $set, $unset, $inc, $mul, $min, $max, $rename, $setOnInsert, $currentDate |
| **Array** | $push, $pop, $pull, $pullAll, $addToSet |
| **Positional** | $ (first), $[] (all), $[identifier] (filtered) |

### Update Methods Comparison

| Method | Returns | Atomic | Use Case |
|--------|---------|--------|----------|
| updateOne() | Stats | Yes | Update first match |
| updateMany() | Stats | Per doc | Batch updates |
| replaceOne() | Stats | Yes | Full replacement |
| findOneAndUpdate() | Document | Yes | Update and return |
| findOneAndReplace() | Document | Yes | Replace and return |

### Best Practices

1. **Use specific update operators** instead of replace when possible
2. **Prefer $inc over read-modify-write** for counters
3. **Use arrayFilters** for complex array updates
4. **Consider upsert** for idempotent operations
5. **Use findOneAndUpdate** when you need the result

### What's Next?

In the next chapter, we'll explore Delete Operations, learning how to remove documents from collections.

---

## Practice Questions

1. What's the difference between $set and replaceOne()?
2. When would you use $inc vs read-modify-write?
3. Explain the difference between $ and $[] positional operators.
4. How do arrayFilters work with positional operators?
5. What's the benefit of $setOnInsert in upsert operations?
6. When should you use findOneAndUpdate vs updateOne?
7. How can you maintain array size limits with $push?
8. What is optimistic locking and how do you implement it?

---

## Hands-On Exercises

### Exercise 1: Basic Updates

```javascript
// Setup test data
db.inventory.insertMany([
  { item: "journal", qty: 25, size: { h: 14, w: 21 }, status: "A" },
  { item: "notebook", qty: 50, size: { h: 8.5, w: 11 }, status: "A" },
  { item: "paper", qty: 100, size: { h: 8.5, w: 11 }, status: "D" },
  { item: "planner", qty: 75, size: { h: 22.85, w: 30 }, status: "D" }
])

// 1. Update qty of journal to 30
db.inventory.updateOne(
  { item: "journal" },
  { $set: { qty: 30 } }
)

// 2. Increase all qty by 10
db.inventory.updateMany(
  {},
  { $inc: { qty: 10 } }
)

// 3. Set status to "P" for items with qty > 50
db.inventory.updateMany(
  { qty: { $gt: 50 } },
  { $set: { status: "P" } }
)
```

### Exercise 2: Array Updates

```javascript
// Setup
db.students.insertOne({
  _id: 1,
  name: "Alice",
  scores: [80, 85, 90],
  courses: [
    { name: "Math", grade: "A" },
    { name: "Science", grade: "B" }
  ]
})

// 1. Add a new score
db.students.updateOne(
  { _id: 1 },
  { $push: { scores: 95 } }
)

// 2. Update Math grade to "A+"
db.students.updateOne(
  { _id: 1, "courses.name": "Math" },
  { $set: { "courses.$.grade": "A+" } }
)

// 3. Add a new course
db.students.updateOne(
  { _id: 1 },
  {
    $push: {
      courses: { name: "History", grade: "B+" }
    }
  }
)

// 4. Remove scores below 85
db.students.updateOne(
  { _id: 1 },
  { $pull: { scores: { $lt: 85 } } }
)
```

### Exercise 3: Upsert and Find-And-Modify

```javascript
// Implement a counter that creates if not exists
db.counters.updateOne(
  { _id: "visitors" },
  { $inc: { count: 1 } },
  { upsert: true }
)

// Get and increment visitor count
const result = db.counters.findOneAndUpdate(
  { _id: "visitors" },
  { $inc: { count: 1 } },
  { upsert: true, returnDocument: "after" }
)
print("Visitor count:", result.count)

// Implement a job queue processor
db.jobs.insertMany([
  { task: "send-email", status: "pending", priority: 1 },
  { task: "process-image", status: "pending", priority: 2 },
  { task: "generate-report", status: "pending", priority: 3 }
])

// Claim highest priority pending job
const job = db.jobs.findOneAndUpdate(
  { status: "pending" },
  {
    $set: {
      status: "processing",
      startedAt: new Date()
    }
  },
  {
    sort: { priority: -1 },
    returnDocument: "after"
  }
)
```

---

[← Previous: Query Operations](07-query-operations.md) | [Next: Delete Operations →](09-delete-operations.md)
