# Chapter 34: Evaluation Operators

## Table of Contents
- [Introduction to Evaluation Operators](#introduction-to-evaluation-operators)
- [$regex Operator](#regex-operator)
- [$expr Operator](#expr-operator)
- [$where Operator](#where-operator)
- [$mod Operator](#mod-operator)
- [$text Operator](#text-operator)
- [$jsonSchema Operator](#jsonschema-operator)
- [Performance Considerations](#performance-considerations)
- [Summary](#summary)

---

## Introduction to Evaluation Operators

Evaluation operators allow complex query logic beyond simple comparisons. They include pattern matching, expression evaluation, and custom JavaScript execution.

### Evaluation Operators Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Evaluation Operators                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  $regex        - Pattern matching with regular expressions         │
│  $expr         - Use aggregation expressions in queries            │
│  $where        - JavaScript expression evaluation (avoid)          │
│  $mod          - Modulo operation for numeric fields               │
│  $text         - Full-text search                                  │
│  $jsonSchema   - Validate documents against JSON Schema            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sample Data Setup

```javascript
// Products collection
db.products.drop()
db.products.insertMany([
  { _id: 1, name: "Apple iPhone 15", sku: "PHONE-001", price: 999, cost: 700, category: "electronics", stock: 150 },
  { _id: 2, name: "Apple MacBook Pro", sku: "LAPTOP-001", price: 2499, cost: 1800, category: "electronics", stock: 50 },
  { _id: 3, name: "Samsung Galaxy S24", sku: "PHONE-002", price: 899, cost: 600, category: "electronics", stock: 200 },
  { _id: 4, name: "Sony WH-1000XM5", sku: "AUDIO-001", price: 399, cost: 250, category: "audio", stock: 75 },
  { _id: 5, name: "Apple AirPods Pro", sku: "AUDIO-002", price: 249, cost: 150, category: "audio", stock: 300 },
  { _id: 6, name: "Dell XPS 15", sku: "LAPTOP-002", price: 1899, cost: 1300, category: "electronics", stock: 40 },
  { _id: 7, name: "Bose QuietComfort", sku: "AUDIO-003", price: 349, cost: 200, category: "audio", stock: 60 }
])

// Users collection
db.users.drop()
db.users.insertMany([
  { _id: 1, email: "john.doe@gmail.com", username: "johndoe", firstName: "John", lastName: "Doe", credits: 100, spent: 50 },
  { _id: 2, email: "jane.smith@yahoo.com", username: "janesmith", firstName: "Jane", lastName: "Smith", credits: 200, spent: 180 },
  { _id: 3, email: "bob.wilson@company.com", username: "bobwilson", firstName: "Bob", lastName: "Wilson", credits: 50, spent: 60 },
  { _id: 4, email: "alice.brown@gmail.com", username: "alicebrown", firstName: "Alice", lastName: "Brown", credits: 300, spent: 100 },
  { _id: 5, email: "charlie_davis@test.org", username: "charlie_davis", firstName: "Charlie", lastName: "Davis", credits: 75, spent: 75 }
])

// Articles collection for text search
db.articles.drop()
db.articles.insertMany([
  { _id: 1, title: "Introduction to MongoDB", content: "MongoDB is a document database designed for ease of development.", author: "Alice", tags: ["mongodb", "database", "nosql"] },
  { _id: 2, title: "Advanced MongoDB Queries", content: "Learn about aggregation pipelines and complex queries.", author: "Bob", tags: ["mongodb", "queries", "advanced"] },
  { _id: 3, title: "SQL vs NoSQL Databases", content: "Comparing traditional SQL databases with modern NoSQL solutions.", author: "Charlie", tags: ["sql", "nosql", "comparison"] },
  { _id: 4, title: "Database Performance Tuning", content: "Optimize your database queries for better performance.", author: "Alice", tags: ["performance", "optimization", "database"] },
  { _id: 5, title: "MongoDB Atlas Cloud Service", content: "Deploy MongoDB in the cloud with Atlas managed service.", author: "Diana", tags: ["mongodb", "cloud", "atlas"] }
])
```

---

## $regex Operator

### Basic Pattern Matching

```javascript
// Find products starting with "Apple"
db.products.find({ name: { $regex: /^Apple/ } })
// Returns: iPhone 15, MacBook Pro, AirPods Pro

// Alternative syntax
db.products.find({ name: { $regex: "^Apple" } })

// Find products containing "Phone"
db.products.find({ name: { $regex: /Phone/i } })  // Case-insensitive
// Returns: iPhone 15, Galaxy S24

// Using $options for flags
db.products.find({ 
  name: { $regex: "phone", $options: "i" }
})
```

### Regex Options

| Option | Description | Example |
|--------|-------------|---------|
| `i` | Case-insensitive | `/apple/i` |
| `m` | Multi-line mode | `/^line/m` |
| `x` | Extended (ignore whitespace) | `/a b c/x` |
| `s` | Dot matches newline | `/a.b/s` |

### Pattern Examples

```javascript
// Starts with
db.products.find({ sku: { $regex: /^PHONE/ } })

// Ends with
db.users.find({ email: { $regex: /\.com$/ } })

// Contains
db.products.find({ name: { $regex: /Pro/ } })

// Word boundary
db.articles.find({ content: { $regex: /\bMongoDB\b/i } })

// Character class
db.users.find({ email: { $regex: /[._]/ } })  // Contains . or _

// Alternation (OR)
db.products.find({ name: { $regex: /Apple|Samsung/ } })

// Wildcard-like pattern
db.products.find({ sku: { $regex: /^.+-00[1-2]$/ } })
// Matches: PHONE-001, PHONE-002, LAPTOP-001, LAPTOP-002
```

### Regex with Index

```javascript
// Create index
db.products.createIndex({ name: 1 })

// ✓ Prefix regex CAN use index
db.products.find({ name: { $regex: /^Apple/ } }).explain("executionStats")
// Uses IXSCAN

// ⚠️ Non-prefix regex CANNOT use index efficiently
db.products.find({ name: { $regex: /Pro/ } }).explain("executionStats")
// May use COLLSCAN or IXSCAN with high docs examined

// ⚠️ Case-insensitive prefix requires collation or cannot use index
db.products.find({ name: { $regex: /^apple/i } }).explain("executionStats")
```

### Escaping Special Characters

```javascript
// Special regex characters: . * + ? ^ $ { } [ ] \ | ( )
// Escape with backslash

// Find emails with literal dot
db.users.find({ email: { $regex: /john\.doe/ } })

// Find SKUs with dash
db.products.find({ sku: { $regex: /PHONE\-001/ } })

// Dynamic regex (escape user input)
function escapeRegex(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
}

const userInput = "Apple (new)"
const safePattern = new RegExp(escapeRegex(userInput))
db.products.find({ name: { $regex: safePattern } })
```

---

## $expr Operator

### Basic $expr Usage

```javascript
// Compare two fields in same document
// Find products where price > 2x cost (50%+ margin)
db.products.find({
  $expr: { $gt: ["$price", { $multiply: ["$cost", 2] }] }
})
// Returns products with >50% profit margin

// Compare fields directly
// Find users who spent more than their credits
db.users.find({
  $expr: { $gt: ["$spent", "$credits"] }
})
// Returns: Bob (spent 60 > credits 50)
```

### $expr with Aggregation Operators

```javascript
// Use aggregation operators in queries
db.products.find({
  $expr: {
    $and: [
      { $gt: ["$stock", 100] },
      { $lt: ["$price", 500] }
    ]
  }
})
// Products with stock > 100 AND price < 500

// Calculate and compare
db.products.find({
  $expr: {
    $gte: [
      { $divide: [{ $subtract: ["$price", "$cost"] }, "$price"] },
      0.3  // 30% profit margin or higher
    ]
  }
})
```

### String Operations with $expr

```javascript
// Use string operators
db.users.find({
  $expr: {
    $gt: [{ $strLenCP: "$email" }, 20]
  }
})
// Users with email longer than 20 characters

// Compare string lengths
db.users.find({
  $expr: {
    $gt: [
      { $strLenCP: "$lastName" },
      { $strLenCP: "$firstName" }
    ]
  }
})
// Users where lastName is longer than firstName
```

### Date Operations with $expr

```javascript
// Add date field to products
db.products.updateMany({}, { $set: { lastUpdated: new Date() } })
db.products.updateOne({ _id: 1 }, { $set: { lastUpdated: new Date("2024-01-01") } })

// Find products updated in last 30 days
db.products.find({
  $expr: {
    $gte: [
      "$lastUpdated",
      { $subtract: ["$$NOW", 30 * 24 * 60 * 60 * 1000] }
    ]
  }
})

// Extract and compare date parts
db.products.find({
  $expr: {
    $eq: [{ $month: "$lastUpdated" }, 1]  // January
  }
})
```

### Conditional Logic with $expr

```javascript
// Use $cond for conditional queries
db.products.find({
  $expr: {
    $cond: {
      if: { $eq: ["$category", "electronics"] },
      then: { $gt: ["$price", 500] },
      else: { $gt: ["$price", 100] }
    }
  }
})
// Electronics > $500 OR other categories > $100

// Use $switch for multiple conditions
db.products.find({
  $expr: {
    $switch: {
      branches: [
        { case: { $eq: ["$category", "electronics"] }, then: { $gt: ["$stock", 50] } },
        { case: { $eq: ["$category", "audio"] }, then: { $gt: ["$stock", 100] } }
      ],
      default: true
    }
  }
})
```

---

## $where Operator

### ⚠️ Important Warning

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ⚠️ $where WARNING ⚠️                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  AVOID $where in production:                                       │
│  • Executes JavaScript for EVERY document                          │
│  • Cannot use indexes                                              │
│  • Security risk if user input not sanitized                       │
│  • Significantly slower than native operators                      │
│                                                                     │
│  Use $expr instead whenever possible!                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Basic $where Usage

```javascript
// Simple JavaScript expression
db.products.find({
  $where: "this.price > this.cost * 2"
})
// Same as $expr but slower

// Function form
db.products.find({
  $where: function() {
    return this.price > this.cost * 2
  }
})

// Complex logic that's hard with native operators
db.users.find({
  $where: function() {
    // Custom validation logic
    return this.firstName.length + this.lastName.length > 10
  }
})
```

### $where vs $expr Comparison

```javascript
// ✗ Using $where (slow)
console.time("$where")
db.products.find({
  $where: "this.price > this.cost * 2"
}).toArray()
console.timeEnd("$where")

// ✓ Using $expr (fast)
console.time("$expr")
db.products.find({
  $expr: { $gt: ["$price", { $multiply: ["$cost", 2] }] }
}).toArray()
console.timeEnd("$expr")
```

---

## $mod Operator

### Basic Modulo Queries

```javascript
// $mod: [divisor, remainder]
// Matches if: field % divisor == remainder

// Find products with even IDs
db.products.find({ _id: { $mod: [2, 0] } })
// Returns: _id 2, 4, 6

// Find products with odd IDs
db.products.find({ _id: { $mod: [2, 1] } })
// Returns: _id 1, 3, 5, 7

// Find every 3rd product (for batch processing)
db.products.find({ _id: { $mod: [3, 0] } })
// Returns: _id 3, 6
```

### $mod Use Cases

```javascript
// Batch processing - process different batches
// Batch 1: IDs where id % 3 == 0
db.products.find({ _id: { $mod: [3, 0] } })

// Batch 2: IDs where id % 3 == 1
db.products.find({ _id: { $mod: [3, 1] } })

// Batch 3: IDs where id % 3 == 2
db.products.find({ _id: { $mod: [3, 2] } })

// Find products with stock divisible by 25
db.products.find({ stock: { $mod: [25, 0] } })
// stock: 150 (150%25=0), 50 (50%25=0), 200 (200%25=0), 75 (75%25=0), 300 (300%25=0)

// Find products priced at X.99 pattern
db.products.find({
  $expr: {
    $eq: [{ $mod: ["$price", 100] }, 99]
  }
})
// Prices ending in 99: 999, 899, 399, etc.
```

---

## $text Operator

### Creating Text Index

```javascript
// Create text index
db.articles.createIndex({
  title: "text",
  content: "text"
})

// Or with weights
db.articles.createIndex(
  { title: "text", content: "text" },
  { weights: { title: 10, content: 1 } }
)
```

### Basic Text Search

```javascript
// Search for term
db.articles.find({ $text: { $search: "MongoDB" } })
// Returns articles containing "MongoDB"

// Search for phrase
db.articles.find({ $text: { $search: "\"document database\"" } })
// Exact phrase match

// Search for multiple terms (OR)
db.articles.find({ $text: { $search: "MongoDB queries" } })
// Contains MongoDB OR queries

// Exclude term
db.articles.find({ $text: { $search: "MongoDB -SQL" } })
// Contains MongoDB but NOT SQL
```

### Text Score

```javascript
// Get relevance score
db.articles.find(
  { $text: { $search: "MongoDB database" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } })

// Filter by minimum score
db.articles.find(
  { $text: { $search: "MongoDB database" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).toArray()
.filter(doc => doc.score > 1.0)
```

### Text Search Options

```javascript
// Case-sensitive search (requires case-sensitive index)
db.articles.find({
  $text: {
    $search: "MongoDB",
    $caseSensitive: true
  }
})

// Diacritic-sensitive
db.articles.find({
  $text: {
    $search: "café",
    $diacriticSensitive: true
  }
})

// Language-specific
db.articles.find({
  $text: {
    $search: "bases données",
    $language: "french"
  }
})
```

---

## $jsonSchema Operator

### Basic Schema Validation

```javascript
// Query documents matching schema
db.products.find({
  $jsonSchema: {
    required: ["name", "price", "category"],
    properties: {
      price: { bsonType: "number", minimum: 0 },
      stock: { bsonType: "int", minimum: 0 }
    }
  }
})

// Find documents NOT matching schema (validation failures)
db.products.find({
  $nor: [{
    $jsonSchema: {
      required: ["name", "price", "category"],
      properties: {
        price: { bsonType: "number", minimum: 0 }
      }
    }
  }]
})
```

### Complex Schema Queries

```javascript
// Schema with nested objects
db.orders.find({
  $jsonSchema: {
    bsonType: "object",
    required: ["customer", "items"],
    properties: {
      customer: {
        bsonType: "object",
        required: ["name", "email"],
        properties: {
          email: {
            bsonType: "string",
            pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
          }
        }
      },
      items: {
        bsonType: "array",
        minItems: 1,
        items: {
          bsonType: "object",
          required: ["product", "quantity"],
          properties: {
            quantity: { bsonType: "int", minimum: 1 }
          }
        }
      }
    }
  }
})
```

### Using $jsonSchema for Data Quality

```javascript
// Find documents with invalid email format
db.users.find({
  $nor: [{
    $jsonSchema: {
      properties: {
        email: {
          bsonType: "string",
          pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$"
        }
      }
    }
  }],
  email: { $exists: true }
})
```

---

## Performance Considerations

### Operator Performance Ranking

| Operator | Performance | Index Usage |
|----------|-------------|-------------|
| `$regex` (prefix) | Good | Yes |
| `$regex` (non-prefix) | Poor | No |
| `$expr` | Moderate | Limited |
| `$where` | Poor | No |
| `$mod` | Moderate | No |
| `$text` | Good | Requires text index |
| `$jsonSchema` | Moderate | No |

### Optimization Tips

```javascript
// 1. Combine with indexed fields
db.products.find({
  category: "electronics",  // Use indexed field first
  name: { $regex: /^Apple/ }
})

// 2. Use $expr sparingly
// If possible, restructure data to avoid $expr

// 3. Avoid $where completely
// Use $expr or aggregation instead

// 4. Create text index for text search
// Don't use $regex for full-text search

// 5. Use $regex prefix when possible
db.products.find({ name: { $regex: /^Apple/ } })  // Good
db.products.find({ name: { $regex: /Apple/ } })   // Slower
```

### Query Analysis

```javascript
// Analyze evaluation operator queries
function analyzeEvalQuery(query, description) {
  const explain = db.products.find(query).explain("executionStats")
  
  print("\n=== " + description + " ===")
  print("Query:", JSON.stringify(query).substring(0, 100))
  print("Execution time:", explain.executionStats.executionTimeMillis, "ms")
  print("Docs examined:", explain.executionStats.totalDocsExamined)
  print("Keys examined:", explain.executionStats.totalKeysExamined)
  
  // Check for COLLSCAN
  const hasCollscan = JSON.stringify(explain.queryPlanner.winningPlan).includes("COLLSCAN")
  print("Collection scan:", hasCollscan ? "Yes ⚠️" : "No ✓")
}

// Test different operators
analyzeEvalQuery({ name: { $regex: /^Apple/ } }, "Prefix regex")
analyzeEvalQuery({ name: { $regex: /Pro/ } }, "Contains regex")
analyzeEvalQuery({ $expr: { $gt: ["$price", 500] } }, "$expr comparison")
analyzeEvalQuery({ _id: { $mod: [2, 0] } }, "$mod even IDs")
```

---

## Summary

### Evaluation Operators

| Operator | Use Case | Performance |
|----------|----------|-------------|
| `$regex` | Pattern matching | Good with prefix |
| `$expr` | Field comparisons | Moderate |
| `$where` | Complex JS logic | Poor (avoid) |
| `$mod` | Modulo operations | Moderate |
| `$text` | Full-text search | Good (indexed) |
| `$jsonSchema` | Schema validation | Moderate |

### $regex Syntax

| Pattern | Meaning |
|---------|---------|
| `/^prefix/` | Starts with |
| `/suffix$/` | Ends with |
| `/contains/` | Contains |
| `/word\b/` | Word boundary |
| `/a|b/` | OR |
| `/[abc]/` | Character class |

### $expr Capabilities

| Feature | Example |
|---------|---------|
| Field comparison | `$gt: ["$price", "$cost"]` |
| Arithmetic | `$multiply: ["$qty", "$price"]` |
| String functions | `$strLenCP: "$name"` |
| Date operations | `$month: "$date"` |
| Conditional | `$cond`, `$switch` |

### What's Next?

In the next chapter, we'll explore Geospatial Queries for location-based data.

---

## Practice Questions

1. What regex pattern matches strings starting with "Apple"?
2. How do you compare two fields in a query?
3. Why should $where be avoided?
4. What does `{ field: { $mod: [5, 0] } }` match?
5. How do you create a text index?
6. What's the difference between $text search terms "a b" vs "\"a b\""?
7. How do you get relevance scores in text search?
8. When can $regex use an index?

---

## Hands-On Exercises

### Exercise 1: $regex Patterns

```javascript
// Practice regex queries

// 1. Find products starting with "Apple"
print("1. Products starting with Apple:")
db.products.find({ name: { $regex: /^Apple/ } }).forEach(p => print("  -", p.name))

// 2. Find products containing "Pro" (case-insensitive)
print("\n2. Products containing Pro:")
db.products.find({ name: { $regex: /Pro/i } }).forEach(p => print("  -", p.name))

// 3. Find users with gmail emails
print("\n3. Gmail users:")
db.users.find({ email: { $regex: /@gmail\.com$/ } }).forEach(u => print("  -", u.email))

// 4. Find SKUs matching pattern XXX-00X
print("\n4. SKUs matching pattern:")
db.products.find({ sku: { $regex: /^[A-Z]+-00\d$/ } }).forEach(p => print("  -", p.sku))

// 5. Find usernames with underscore
print("\n5. Usernames with underscore:")
db.users.find({ username: { $regex: /_/ } }).forEach(u => print("  -", u.username))
```

### Exercise 2: $expr Comparisons

```javascript
// Practice field comparisons with $expr

// 1. Products with price > 2x cost
print("1. Products with >50% markup:")
db.products.find({
  $expr: { $gt: ["$price", { $multiply: ["$cost", 2] }] }
}).forEach(p => {
  const margin = ((p.price - p.cost) / p.price * 100).toFixed(1)
  print("  -", p.name, ": $" + p.price, "cost $" + p.cost, "(" + margin + "% margin)")
})

// 2. Users who spent more than credits
print("\n2. Users overspent:")
db.users.find({
  $expr: { $gt: ["$spent", "$credits"] }
}).forEach(u => print("  -", u.username, ": credits", u.credits, "spent", u.spent))

// 3. Users with remaining credits > 100
print("\n3. Users with >100 remaining credits:")
db.users.find({
  $expr: { $gt: [{ $subtract: ["$credits", "$spent"] }, 100] }
}).forEach(u => {
  const remaining = u.credits - u.spent
  print("  -", u.username, ": remaining", remaining)
})

// 4. Products where name length > 15
print("\n4. Products with long names (>15 chars):")
db.products.find({
  $expr: { $gt: [{ $strLenCP: "$name" }, 15] }
}).forEach(p => print("  -", p.name, "(" + p.name.length + " chars)"))
```

### Exercise 3: $mod Operations

```javascript
// Practice modulo queries

// 1. Find even-ID products
print("1. Even-ID products:")
db.products.find({ _id: { $mod: [2, 0] } }).forEach(p => print("  -", p._id, p.name))

// 2. Find every 3rd product
print("\n2. Every 3rd product (ID % 3 == 0):")
db.products.find({ _id: { $mod: [3, 0] } }).forEach(p => print("  -", p._id, p.name))

// 3. Find products with stock divisible by 50
print("\n3. Stock divisible by 50:")
db.products.find({ stock: { $mod: [50, 0] } }).forEach(p => print("  -", p.name, ": stock", p.stock))

// 4. Batch processing simulation
print("\n4. Batch processing (3 batches):")
for (let batch = 0; batch < 3; batch++) {
  const items = db.products.find({ _id: { $mod: [3, batch] } }).toArray()
  print("  Batch", batch + 1, ":", items.map(p => p._id).join(", "))
}
```

### Exercise 4: Text Search

```javascript
// Practice text search

// Create text index if not exists
db.articles.createIndex({ title: "text", content: "text" })

// 1. Search for MongoDB
print("1. Articles about MongoDB:")
db.articles.find({ $text: { $search: "MongoDB" } }).forEach(a => print("  -", a.title))

// 2. Search for phrase
print("\n2. Articles with 'document database' phrase:")
db.articles.find({ $text: { $search: "\"document database\"" } }).forEach(a => print("  -", a.title))

// 3. Search with exclusion
print("\n3. Database articles (not SQL):")
db.articles.find({ $text: { $search: "database -SQL" } }).forEach(a => print("  -", a.title))

// 4. Search with scores
print("\n4. Search 'MongoDB queries' with scores:")
db.articles.find(
  { $text: { $search: "MongoDB queries" } },
  { score: { $meta: "textScore" } }
).sort({ score: { $meta: "textScore" } }).forEach(a => {
  print("  -", a.title, "(score:", a.score.toFixed(2) + ")")
})
```

### Exercise 5: Combined Operators

```javascript
// Combine evaluation operators

// 1. Electronics with Apple in name and price > cost * 1.5
print("1. Apple electronics with >50% markup:")
db.products.find({
  category: "electronics",
  name: { $regex: /^Apple/ },
  $expr: { $gt: ["$price", { $multiply: ["$cost", 1.5] }] }
}).forEach(p => print("  -", p.name))

// 2. Gmail users with positive credit balance
print("\n2. Gmail users with credits > spent:")
db.users.find({
  email: { $regex: /@gmail\.com$/ },
  $expr: { $gt: ["$credits", "$spent"] }
}).forEach(u => print("  -", u.email, ": balance", u.credits - u.spent))

// 3. Complex product search
print("\n3. Products: stock > 100, price ends in 99, audio category:")
db.products.find({
  category: "audio",
  stock: { $gt: 100 },
  $expr: { $eq: [{ $mod: ["$price", 100] }, 99] }
}).forEach(p => print("  -", p.name, ": $" + p.price, "stock", p.stock))

// 4. Performance comparison
print("\n4. Performance comparison:")

console.time("Indexed field + regex")
db.products.find({
  category: "electronics",
  name: { $regex: /^Apple/ }
}).toArray()
console.timeEnd("Indexed field + regex")

console.time("$expr only")
db.products.find({
  $expr: {
    $and: [
      { $eq: ["$category", "electronics"] },
      { $regexMatch: { input: "$name", regex: /^Apple/ } }
    ]
  }
}).toArray()
console.timeEnd("$expr only")
```

---

[← Previous: Element and Type Operators](33-element-type-operators.md) | [Next: Geospatial Queries →](35-geospatial-queries.md)
