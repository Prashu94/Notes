# Chapter 33: Element and Type Operators

## Table of Contents
- [Introduction to Element Operators](#introduction-to-element-operators)
- [$exists Operator](#exists-operator)
- [$type Operator](#type-operator)
- [BSON Type Reference](#bson-type-reference)
- [Null and Missing Field Handling](#null-and-missing-field-handling)
- [Schema Validation Patterns](#schema-validation-patterns)
- [Combining Element Operators](#combining-element-operators)
- [Summary](#summary)

---

## Introduction to Element Operators

Element operators query documents based on field existence and data type. These operators are essential for working with MongoDB's flexible schema.

### Element Operators Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Element Operators                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $exists   - Check if field exists in document                     │
│              { field: { $exists: true/false } }                    │
│                                                                     │
│  $type     - Check field's BSON data type                          │
│              { field: { $type: "string" } }                        │
│              { field: { $type: ["string", "int"] } }              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Create collection with varied document structures
db.documents.drop()
db.documents.insertMany([
  { 
    _id: 1, 
    name: "Document 1",
    value: 42,
    status: "active",
    metadata: { version: 1, author: "Alice" }
  },
  { 
    _id: 2, 
    name: "Document 2",
    value: "string value",
    status: null,
    tags: ["important", "review"]
  },
  { 
    _id: 3, 
    name: "Document 3",
    value: 3.14,
    // status field missing
    count: NumberLong(1000)
  },
  { 
    _id: 4, 
    name: "Document 4",
    value: true,
    status: "inactive",
    date: new Date("2024-01-15")
  },
  { 
    _id: 5, 
    name: "Document 5",
    value: [1, 2, 3],
    status: "",
    metadata: null
  },
  {
    _id: 6,
    name: "Document 6",
    value: ObjectId(),
    status: "active",
    data: BinData(0, "SGVsbG8gV29ybGQ=")
  },
  {
    _id: 7,
    name: "Document 7",
    value: NumberDecimal("99.99"),
    regex: /pattern/i,
    timestamp: Timestamp(1, 1)
  }
])

// Users with varied schemas
db.users.drop()
db.users.insertMany([
  { _id: 1, name: "Alice", email: "alice@example.com", age: 30, verified: true },
  { _id: 2, name: "Bob", email: null, age: "twenty-five" },  // age is string
  { _id: 3, name: "Charlie", phone: "555-0123" },  // email missing
  { _id: 4, name: "Diana", email: "", age: 28, verified: false },
  { _id: 5, name: "Eve", email: "eve@example.com" }  // age missing
])
```

---

## $exists Operator

### Basic $exists Usage

```javascript
// Find documents where field EXISTS
db.documents.find({ status: { $exists: true } })
// Returns: Documents 1, 2, 4, 5, 6 (have status field, even if null)

// Find documents where field does NOT exist
db.documents.find({ status: { $exists: false } })
// Returns: Documents 3, 7 (status field is completely absent)
```

### $exists vs null

```javascript
// ⚠️ IMPORTANT: { field: null } matches BOTH:
// - field exists with null value
// - field doesn't exist at all

// Documents where status IS null or MISSING
db.documents.find({ status: null })
// Returns: Documents 2, 3, 7
// Doc 2: status is null
// Doc 3: status doesn't exist
// Doc 7: status doesn't exist

// Documents where status EXISTS AND is null
db.documents.find({ 
  status: { $exists: true, $eq: null }
})
// Returns: Document 2 only

// Documents where status DOESN'T EXIST
db.documents.find({ status: { $exists: false } })
// Returns: Documents 3, 7
```

### Practical $exists Patterns

```javascript
// Find users with email field (present)
db.users.find({ email: { $exists: true } })
// Alice, Bob, Diana, Eve (even though Bob's is null, Diana's is "")

// Find users without email field
db.users.find({ email: { $exists: false } })
// Charlie

// Find users with optional field populated (not null, not missing)
db.users.find({
  email: { $exists: true, $ne: null, $ne: "" }
})
// Alice, Eve

// Find incomplete profiles (missing required fields)
db.users.find({
  $or: [
    { email: { $exists: false } },
    { age: { $exists: false } }
  ]
})
// Charlie (no email), Eve (no age)
```

### Nested Field $exists

```javascript
// Check for nested field existence
db.documents.find({ "metadata.version": { $exists: true } })
// Returns: Document 1

// Check parent exists but child doesn't
db.documents.find({
  metadata: { $exists: true },
  "metadata.author": { $exists: false }
})

// Caution: null parent
db.documents.find({ metadata: { $exists: true } })
// Returns Documents 1 and 5 (5 has metadata: null)
```

---

## $type Operator

### Using Type Names

```javascript
// Find documents with string values
db.documents.find({ value: { $type: "string" } })
// Returns: Document 2

// Find documents with number values
db.documents.find({ value: { $type: "number" } })
// Returns: Documents 1, 3, 7 (int, double, decimal)

// Find documents with array values
db.documents.find({ value: { $type: "array" } })
// Returns: Document 5

// Find documents with boolean values
db.documents.find({ value: { $type: "bool" } })
// Returns: Document 4

// Find documents with date values
db.documents.find({ date: { $type: "date" } })
// Returns: Document 4

// Find documents with null values
db.documents.find({ status: { $type: "null" } })
// Returns: Document 2
```

### Using Type Numbers

```javascript
// Type numbers (legacy, but still valid)
// 1 = double, 2 = string, 3 = object, 4 = array, etc.

db.documents.find({ value: { $type: 2 } })  // string
// Same as: { value: { $type: "string" } }

db.documents.find({ value: { $type: 1 } })  // double
// Returns: Document 3 (3.14)

db.documents.find({ count: { $type: 18 } })  // long
// Returns: Document 3
```

### Multiple Types

```javascript
// Match any of multiple types
db.documents.find({ 
  value: { $type: ["string", "int", "double"] }
})
// Returns: Documents 1, 2, 3

// Find fields that could be string OR number
db.users.find({
  age: { $type: ["string", "int", "double", "long"] }
})
// Alice (30), Bob ("twenty-five"), Diana (28)
```

### Alias Types

```javascript
// "number" alias matches: double, int, long, decimal
db.documents.find({ value: { $type: "number" } })
// Returns: Documents 1, 3, 7

// Specific numeric types
db.documents.find({ value: { $type: "int" } })
// Returns: Document 1 (42)

db.documents.find({ value: { $type: "double" } })
// Returns: Document 3 (3.14)

db.documents.find({ value: { $type: "decimal" } })
// Returns: Document 7 (NumberDecimal)

db.documents.find({ count: { $type: "long" } })
// Returns: Document 3
```

---

## BSON Type Reference

### Complete Type Table

| Type Name | Number | Alias | Notes |
|-----------|--------|-------|-------|
| Double | 1 | "double" | 64-bit floating point |
| String | 2 | "string" | UTF-8 string |
| Object | 3 | "object" | Embedded document |
| Array | 4 | "array" | Array |
| Binary data | 5 | "binData" | Binary data |
| Undefined | 6 | "undefined" | Deprecated |
| ObjectId | 7 | "objectId" | 12-byte ObjectId |
| Boolean | 8 | "bool" | true/false |
| Date | 9 | "date" | UTC datetime |
| Null | 10 | "null" | Null value |
| Regular Expression | 11 | "regex" | Regular expression |
| JavaScript | 13 | "javascript" | JavaScript code |
| Symbol | 14 | "symbol" | Deprecated |
| JavaScript with scope | 15 | "javascriptWithScope" | Deprecated |
| 32-bit integer | 16 | "int" | 32-bit signed integer |
| Timestamp | 17 | "timestamp" | Internal timestamp |
| 64-bit integer | 18 | "long" | 64-bit signed integer |
| Decimal128 | 19 | "decimal" | 128-bit decimal |
| Min key | -1 | "minKey" | Lowest BSON type |
| Max key | 127 | "maxKey" | Highest BSON type |

### Testing Different Types

```javascript
// ObjectId
db.documents.find({ value: { $type: "objectId" } })
// Document 6

// Binary Data
db.documents.find({ data: { $type: "binData" } })
// Document 6

// Regex
db.documents.find({ regex: { $type: "regex" } })
// Document 7

// Timestamp
db.documents.find({ timestamp: { $type: "timestamp" } })
// Document 7

// Embedded object
db.documents.find({ metadata: { $type: "object" } })
// Document 1
```

---

## Null and Missing Field Handling

### Understanding Null Semantics

```javascript
// Three states to consider:
// 1. Field exists with value (not null)
// 2. Field exists with null value
// 3. Field doesn't exist

db.users.find({})
// Alice: email = "alice@example.com" (has value)
// Bob: email = null (null value)
// Charlie: no email field (missing)
// Diana: email = "" (empty string)
// Eve: email = "eve@example.com" (has value)
```

### Query Patterns for Each State

```javascript
// 1. Field has non-null value
db.users.find({ email: { $ne: null } })
// Alice, Diana, Eve (Diana has "", which is not null)

// 2. Field is null (explicitly)
db.users.find({
  email: { $exists: true, $type: "null" }
})
// Bob only

// 3. Field is missing
db.users.find({ email: { $exists: false } })
// Charlie only

// 4. Field is null OR missing
db.users.find({ email: null })
// Bob, Charlie

// 5. Field exists with any value (including null)
db.users.find({ email: { $exists: true } })
// Alice, Bob, Diana, Eve

// 6. Field has truthy value (not null, not "", not missing)
db.users.find({
  email: { $exists: true, $ne: null, $ne: "" }
})
// Alice, Eve
```

### Practical Null Handling

```javascript
// Find users needing email verification
db.users.find({
  $or: [
    { email: { $exists: false } },
    { email: null },
    { email: "" }
  ]
})
// Bob, Charlie, Diana

// Find users with valid email
db.users.find({
  email: { $exists: true, $ne: null, $ne: "", $regex: /@/ }
})
// Alice, Eve

// Data quality check: find documents with unexpected nulls
db.users.find({
  $or: [
    { name: null },
    { name: { $exists: false } }
  ]
})
```

---

## Schema Validation Patterns

### Detecting Schema Inconsistencies

```javascript
// Find documents with wrong type for age
db.users.find({
  age: { $exists: true, $not: { $type: "number" } }
})
// Bob (age is string)

// Find documents with unexpected field types
db.documents.aggregate([
  {
    $project: {
      _id: 1,
      name: 1,
      valueType: { $type: "$value" }
    }
  }
])
// Shows type of value field for each document

// Group by field type
db.documents.aggregate([
  {
    $group: {
      _id: { $type: "$value" },
      count: { $sum: 1 },
      docs: { $push: "$_id" }
    }
  }
])
```

### Schema Discovery

```javascript
// Find all unique field patterns
db.users.aggregate([
  {
    $project: {
      fields: { $objectToArray: "$$ROOT" }
    }
  },
  { $unwind: "$fields" },
  {
    $group: {
      _id: "$fields.k",
      types: { $addToSet: { $type: "$fields.v" } },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
])

// Find documents with extra/unexpected fields
const expectedFields = ["_id", "name", "email", "age", "verified"]
db.users.find({
  $or: expectedFields.map(f => ({ [f]: { $exists: false } }))
})
```

### Type Coercion Queries

```javascript
// Find numeric strings that could be converted
db.users.find({
  age: { 
    $type: "string",
    $regex: /^\d+$/
  }
})

// Find dates stored as strings
db.documents.find({
  date: {
    $type: "string",
    $regex: /^\d{4}-\d{2}-\d{2}/
  }
})
```

---

## Combining Element Operators

### Complex Existence Checks

```javascript
// Field exists AND has specific type
db.documents.find({
  value: { 
    $exists: true, 
    $type: "number" 
  }
})
// Documents 1, 3, 7

// Field exists AND is NOT null AND is NOT empty string
db.users.find({
  email: {
    $exists: true,
    $ne: null,
    $ne: ""
  }
})
// Alice, Eve
```

### With Other Query Operators

```javascript
// Combine with comparison operators
db.documents.find({
  value: {
    $type: "number",
    $gt: 10
  }
})
// Document 1 (42), but not Document 3 (3.14)

// Combine with $or
db.documents.find({
  $or: [
    { status: { $exists: false } },
    { status: { $type: "null" } },
    { status: "" }
  ]
})
// Documents 2, 3, 5, 7

// Combine with $and for multiple fields
db.users.find({
  $and: [
    { email: { $exists: true, $type: "string", $ne: "" } },
    { age: { $exists: true, $type: "number" } }
  ]
})
// Alice, Diana
```

### Array Element Types

```javascript
// Check if array contains elements of specific type
db.documents.find({
  value: { $type: "array" },
  "value.0": { $type: "number" }
})
// Document 5 (value is [1, 2, 3])

// Find arrays with mixed types
db.test.insertMany([
  { _id: 1, arr: [1, 2, 3] },
  { _id: 2, arr: ["a", "b", "c"] },
  { _id: 3, arr: [1, "two", 3] }
])

// Find arrays with string elements
db.test.find({ arr: { $type: "string" } })
// Documents 2 and 3
```

---

## Summary

### $exists Behavior

| Query | Matches |
|-------|---------|
| `{ field: { $exists: true } }` | Field present (even if null) |
| `{ field: { $exists: false } }` | Field absent |
| `{ field: null }` | Field null OR absent |
| `{ field: { $exists: true, $eq: null } }` | Field present AND null |
| `{ field: { $ne: null } }` | Field present AND not null |

### Common Type Aliases

| Alias | Description |
|-------|-------------|
| "number" | double, int, long, decimal |
| "string" | UTF-8 string |
| "object" | Embedded document |
| "array" | Array |
| "bool" | Boolean |
| "date" | Date |
| "null" | Null value |
| "objectId" | ObjectId |

### Best Practices

| Practice | Description |
|----------|-------------|
| Use type aliases | More readable than numbers |
| Handle null explicitly | Don't assume missing = null |
| Validate types | Use $type for schema validation |
| Check existence first | Combine $exists with $type |

### What's Next?

In the next chapter, we'll explore Evaluation Operators including $regex, $expr, $where, and $mod.

---

## Practice Questions

1. What's the difference between `{ field: null }` and `{ field: { $exists: false } }`?
2. How do you find documents where a field exists and is not null?
3. What type alias matches all numeric types?
4. How do you detect schema inconsistencies with $type?
5. What does `{ field: { $type: ["string", "null"] } }` match?
6. How do you find documents with missing required fields?
7. What's the BSON type number for 64-bit integer?
8. How do you check if an array contains elements of a specific type?

---

## Hands-On Exercises

### Exercise 1: $exists Queries

```javascript
// Practice $exists with users collection

// 1. Find all users (baseline)
print("All users:")
db.users.find({}, { _id: 0, name: 1, email: 1, age: 1 }).forEach(printjson)

// 2. Users WITH email field (any value)
print("\n2. Users with email field:")
db.users.find({ email: { $exists: true } }, { _id: 0, name: 1, email: 1 }).forEach(printjson)

// 3. Users WITHOUT email field
print("\n3. Users without email field:")
db.users.find({ email: { $exists: false } }, { _id: 0, name: 1 }).forEach(printjson)

// 4. Users with email null or missing
print("\n4. Users with email null or missing:")
db.users.find({ email: null }, { _id: 0, name: 1, email: 1 }).forEach(printjson)

// 5. Users with email null (explicitly)
print("\n5. Users with email explicitly null:")
db.users.find({ 
  email: { $exists: true, $type: "null" } 
}, { _id: 0, name: 1, email: 1 }).forEach(printjson)

// 6. Users with valid email (exists, not null, not empty)
print("\n6. Users with valid email:")
db.users.find({
  email: { $exists: true, $ne: null, $ne: "" }
}, { _id: 0, name: 1, email: 1 }).forEach(printjson)
```

### Exercise 2: $type Queries

```javascript
// Practice $type with documents collection

// 1. Group documents by value type
print("1. Documents grouped by value type:")
db.documents.aggregate([
  {
    $group: {
      _id: { $type: "$value" },
      count: { $sum: 1 },
      documents: { $push: { id: "$_id", name: "$name" } }
    }
  },
  { $sort: { _id: 1 } }
]).forEach(printjson)

// 2. Find documents with numeric values
print("\n2. Documents with numeric values:")
db.documents.find({ value: { $type: "number" } }, { _id: 1, name: 1, value: 1 }).forEach(printjson)

// 3. Find documents with specific numeric types
print("\n3. Specific numeric types:")
print("  Int32:", db.documents.find({ value: { $type: "int" } }).map(d => d._id))
print("  Double:", db.documents.find({ value: { $type: "double" } }).map(d => d._id))
print("  Decimal:", db.documents.find({ value: { $type: "decimal" } }).map(d => d._id))
print("  Long:", db.documents.find({ count: { $type: "long" } }).map(d => d._id))

// 4. Find documents with object or array metadata
print("\n4. Documents with object or array values:")
db.documents.find({ 
  value: { $type: ["object", "array"] } 
}, { _id: 1, name: 1, value: 1 }).forEach(printjson)
```

### Exercise 3: Schema Validation

```javascript
// Detect schema inconsistencies

// 1. Find users with wrong type for age
print("1. Users with non-numeric age:")
db.users.find({
  age: { $exists: true, $not: { $type: "number" } }
}).forEach(u => print("  -", u.name, ": age =", u.age, "(type:", typeof u.age + ")"))

// 2. Check all fields for type consistency
print("\n2. Field type analysis for users:")
db.users.aggregate([
  {
    $project: {
      fields: { $objectToArray: "$$ROOT" }
    }
  },
  { $unwind: "$fields" },
  {
    $group: {
      _id: "$fields.k",
      types: { $addToSet: { $type: "$fields.v" } },
      count: { $sum: 1 }
    }
  },
  { $sort: { _id: 1 } }
]).forEach(f => {
  const warning = f.types.length > 1 ? " ⚠️ INCONSISTENT" : ""
  print("  ", f._id, ":", f.types.join(", "), warning)
})

// 3. Find documents with missing required fields
print("\n3. Users missing required fields:")
const requiredFields = ["name", "email"]
db.users.find({
  $or: requiredFields.map(f => ({ [f]: { $exists: false } }))
}).forEach(u => {
  const missing = requiredFields.filter(f => u[f] === undefined)
  print("  -", u.name || "?", "missing:", missing.join(", "))
})
```

### Exercise 4: Null vs Missing

```javascript
// Demonstrate null handling

// Setup test data
db.nullTest.drop()
db.nullTest.insertMany([
  { _id: 1, field: "has value" },
  { _id: 2, field: null },
  { _id: 3 },  // field missing
  { _id: 4, field: "" },
  { _id: 5, field: 0 },
  { _id: 6, field: false }
])

print("Test data:")
db.nullTest.find().forEach(printjson)

// Test different queries
const queries = [
  { name: "field: null", query: { field: null } },
  { name: "field: { $exists: true }", query: { field: { $exists: true } } },
  { name: "field: { $exists: false }", query: { field: { $exists: false } } },
  { name: "field: { $ne: null }", query: { field: { $ne: null } } },
  { name: "field: { $type: 'null' }", query: { field: { $type: "null" } } },
  { name: "field: ''", query: { field: "" } },
  { name: "field: { $in: [null, ''] }", query: { field: { $in: [null, ""] } } }
]

print("\nQuery results:")
queries.forEach(q => {
  const results = db.nullTest.find(q.query).map(d => d._id)
  print(" ", q.name, "→ IDs:", results.join(", ") || "none")
})
```

### Exercise 5: Type-Based Data Cleaning

```javascript
// Find and report type issues

// Create messy data
db.messy.drop()
db.messy.insertMany([
  { _id: 1, age: 25, score: 95.5, date: new Date() },
  { _id: 2, age: "thirty", score: "88", date: "2024-01-15" },
  { _id: 3, age: 35, score: null, date: new Date() },
  { _id: 4, age: null, score: 77, date: null },
  { _id: 5, age: "40", score: 82, date: ISODate("2024-01-20") }
])

print("=== Data Type Report ===\n")

// Analyze each field
const fields = ["age", "score", "date"]
fields.forEach(field => {
  print(`Field: ${field}`)
  
  // Get type distribution
  const types = db.messy.aggregate([
    {
      $group: {
        _id: { $type: "$" + field },
        count: { $sum: 1 },
        ids: { $push: "$_id" }
      }
    }
  ]).toArray()
  
  types.forEach(t => {
    print(`  ${t._id}: ${t.count} docs (IDs: ${t.ids.join(", ")})`)
  })
  print("")
})

// Find documents needing cleanup
print("Documents needing cleanup:")
db.messy.find({
  $or: [
    { age: { $not: { $type: ["number", "null"] } } },
    { score: { $not: { $type: ["number", "null"] } } },
    { date: { $not: { $type: ["date", "null"] } } }
  ]
}).forEach(d => {
  print(`  ID ${d._id}:`)
  if (d.age && typeof d.age !== "number") print(`    - age: ${d.age} (${typeof d.age})`)
  if (d.score && typeof d.score !== "number") print(`    - score: ${d.score} (${typeof d.score})`)
  if (d.date && !(d.date instanceof Date)) print(`    - date: ${d.date} (${typeof d.date})`)
})
```

---

[← Previous: Array Query Operators](32-array-query-operators.md) | [Next: Evaluation Operators →](34-evaluation-operators.md)
