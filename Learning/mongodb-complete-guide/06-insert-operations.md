# Chapter 6: Insert Operations

## Table of Contents
- [Insert Overview](#insert-overview)
- [insertOne()](#insertone)
- [insertMany()](#insertmany)
- [Write Concern](#write-concern)
- [Ordered vs Unordered Inserts](#ordered-vs-unordered-inserts)
- [Bulk Operations](#bulk-operations)
- [Error Handling](#error-handling)
- [Performance Considerations](#performance-considerations)
- [Summary](#summary)

---

## Insert Overview

MongoDB provides multiple methods for inserting documents into collections.

### Insert Methods

| Method | Description |
|--------|-------------|
| `insertOne()` | Insert a single document |
| `insertMany()` | Insert multiple documents |
| `bulkWrite()` | Perform multiple operations in bulk |
| `insert()` | Legacy method (deprecated) |

### Insert Behavior

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Insert Operation Flow                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client Request                                                      │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 1. Document Validation                                       │   │
│  │    • Schema validation (if defined)                         │   │
│  │    • _id generation (if not provided)                       │   │
│  │    • BSON type validation                                   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 2. Index Updates                                             │   │
│  │    • Update all relevant indexes                            │   │
│  │    • Check unique constraints                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 3. Write to Journal                                          │   │
│  │    • Write-ahead logging (durability)                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ 4. Write to Storage                                          │   │
│  │    • WiredTiger cache                                       │   │
│  │    • Checkpoint to disk                                     │   │
│  └─────────────────────────────────────────────────────────────┘   │
│       │                                                             │
│       ▼                                                             │
│  Acknowledgment to Client                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## insertOne()

### Basic Syntax

```javascript
db.collection.insertOne(
   <document>,
   {
      writeConcern: <document>,
      comment: <any>
   }
)
```

### Basic Insert

```javascript
// Simple insert
db.users.insertOne({
  name: "John Doe",
  email: "john@example.com",
  age: 30
})

// Result:
{
  acknowledged: true,
  insertedId: ObjectId("507f1f77bcf86cd799439011")
}
```

### Insert with Custom _id

```javascript
// Using custom ObjectId
db.users.insertOne({
  _id: ObjectId("507f1f77bcf86cd799439099"),
  name: "Jane Doe",
  email: "jane@example.com"
})

// Using custom string _id
db.users.insertOne({
  _id: "user_jane_001",
  name: "Jane Doe",
  email: "jane@example.com"
})

// Using numeric _id
db.products.insertOne({
  _id: 12345,
  name: "Product A",
  price: 99.99
})

// Using compound _id
db.events.insertOne({
  _id: {
    date: ISODate("2024-01-15"),
    type: "login",
    userId: "user123"
  },
  details: { ip: "192.168.1.1" }
})
```

### Insert with Various Data Types

```javascript
// Complete document with all data types
db.examples.insertOne({
  // Auto-generated _id
  
  // String
  name: "Example Document",
  
  // Numbers
  intValue: NumberInt(42),
  longValue: NumberLong("9999999999"),
  doubleValue: 3.14159,
  decimalValue: NumberDecimal("123.456"),
  
  // Boolean
  isActive: true,
  
  // Date
  createdAt: new Date(),
  specificDate: ISODate("2024-06-15T10:30:00Z"),
  
  // Null
  deletedAt: null,
  
  // Array
  tags: ["mongodb", "database", "nosql"],
  scores: [85, 90, 78],
  
  // Embedded document
  address: {
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001",
    coordinates: {
      lat: 40.7128,
      lng: -74.0060
    }
  },
  
  // Array of embedded documents
  contacts: [
    { type: "email", value: "test@example.com", primary: true },
    { type: "phone", value: "+1-555-0100", primary: false }
  ],
  
  // Binary data
  thumbnail: BinData(0, "iVBORw0KGgoAAAANSUhEUgAAAAUA..."),
  
  // ObjectId reference
  categoryId: ObjectId("507f1f77bcf86cd799439012"),
  
  // UUID
  sessionId: UUID("550e8400-e29b-41d4-a716-446655440000")
})
```

### Insert with Write Concern

```javascript
// Insert with specific write concern
db.criticalData.insertOne(
  { 
    type: "critical",
    data: "important value" 
  },
  {
    writeConcern: {
      w: "majority",      // Wait for majority acknowledgment
      j: true,            // Wait for journal commit
      wtimeout: 5000      // Timeout after 5 seconds
    }
  }
)
```

---

## insertMany()

### Basic Syntax

```javascript
db.collection.insertMany(
   [ <document 1> , <document 2>, ... ],
   {
      writeConcern: <document>,
      ordered: <boolean>,
      comment: <any>
   }
)
```

### Basic Multi-Insert

```javascript
// Insert multiple documents
db.products.insertMany([
  { name: "Laptop", price: 999.99, category: "Electronics" },
  { name: "Mouse", price: 29.99, category: "Electronics" },
  { name: "Keyboard", price: 79.99, category: "Electronics" },
  { name: "Monitor", price: 399.99, category: "Electronics" },
  { name: "Headphones", price: 149.99, category: "Electronics" }
])

// Result:
{
  acknowledged: true,
  insertedIds: {
    '0': ObjectId("507f1f77bcf86cd799439011"),
    '1': ObjectId("507f1f77bcf86cd799439012"),
    '2': ObjectId("507f1f77bcf86cd799439013"),
    '3': ObjectId("507f1f77bcf86cd799439014"),
    '4': ObjectId("507f1f77bcf86cd799439015")
  }
}
```

### Insert with Custom IDs

```javascript
db.users.insertMany([
  { _id: "user001", name: "Alice", role: "admin" },
  { _id: "user002", name: "Bob", role: "user" },
  { _id: "user003", name: "Charlie", role: "user" },
  { _id: "user004", name: "Diana", role: "moderator" }
])
```

### Insert Generated Data

```javascript
// Generate and insert test data
const documents = [];
for (let i = 0; i < 1000; i++) {
  documents.push({
    index: i,
    name: `User ${i}`,
    email: `user${i}@example.com`,
    score: Math.floor(Math.random() * 100),
    active: Math.random() > 0.5,
    createdAt: new Date()
  });
}

db.testUsers.insertMany(documents)
```

### Insert with Different Schemas

```javascript
// Documents can have different structures
db.mixedCollection.insertMany([
  {
    type: "book",
    title: "MongoDB Guide",
    author: "John Smith",
    pages: 350,
    isbn: "978-0123456789"
  },
  {
    type: "movie",
    title: "Database Documentary",
    director: "Jane Doe",
    duration: 120,
    format: "digital"
  },
  {
    type: "music",
    title: "Coding Beats",
    artist: "DJ Data",
    tracks: 12,
    genre: "electronic"
  }
])
```

---

## Write Concern

### Write Concern Options

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Write Concern Levels                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  w: 0 (Fire and Forget)                                            │
│  ┌─────────┐                                                       │
│  │ Client  │──────────────────────────────────────────────────→    │
│  │         │  No acknowledgment, highest risk                      │
│  └─────────┘                                                       │
│                                                                     │
│  w: 1 (Primary Only - Default)                                     │
│  ┌─────────┐      ┌─────────┐                                      │
│  │ Client  │──────│ Primary │                                      │
│  │         │◄─────│         │ Acknowledged                         │
│  └─────────┘      └─────────┘                                      │
│                                                                     │
│  w: "majority" (Majority Acknowledgment)                           │
│  ┌─────────┐      ┌─────────┐                                      │
│  │ Client  │──────│ Primary │                                      │
│  │         │      └────┬────┘                                      │
│  │         │           │  Replicate                                │
│  │         │      ┌────▼────┐   ┌─────────┐                       │
│  │         │◄─────│Secondary│───│Secondary│                       │
│  └─────────┘      └─────────┘   └─────────┘                       │
│                Majority confirmed                                   │
│                                                                     │
│  j: true (Journal Committed)                                       │
│  Data written to journal before acknowledgment                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Write Concern Examples

```javascript
// w: 0 - No acknowledgment (fire and forget)
// Use for non-critical data, highest performance
db.logs.insertOne(
  { message: "debug log", timestamp: new Date() },
  { writeConcern: { w: 0 } }
)

// w: 1 - Primary acknowledgment (default)
db.users.insertOne(
  { name: "User" },
  { writeConcern: { w: 1 } }
)

// w: "majority" - Majority of replica set
db.orders.insertOne(
  { orderId: "ORD001", total: 100 },
  { writeConcern: { w: "majority" } }
)

// w: <number> - Specific number of nodes
db.criticalData.insertOne(
  { data: "critical" },
  { writeConcern: { w: 3 } }  // Wait for 3 nodes
)

// j: true - Journal committed
db.financial.insertOne(
  { transaction: "TXN001", amount: 1000 },
  { writeConcern: { w: 1, j: true } }
)

// Combined with timeout
db.orders.insertOne(
  { orderId: "ORD002" },
  {
    writeConcern: {
      w: "majority",
      j: true,
      wtimeout: 5000  // Timeout after 5 seconds
    }
  }
)
```

### Setting Default Write Concern

```javascript
// Set at database level
db.adminCommand({
  setDefaultRWConcern: 1,
  defaultWriteConcern: {
    w: "majority",
    j: true
  }
})

// Check current default
db.adminCommand({ getDefaultRWConcern: 1 })
```

---

## Ordered vs Unordered Inserts

### Ordered Inserts (Default)

```javascript
// Ordered: true (default)
// Stops on first error
db.users.insertMany(
  [
    { _id: 1, name: "Alice" },
    { _id: 2, name: "Bob" },
    { _id: 1, name: "Charlie" },  // Duplicate _id - ERROR
    { _id: 3, name: "Diana" }      // Won't be inserted
  ],
  { ordered: true }
)

// Only Alice and Bob are inserted
// Operation stops at Charlie's duplicate _id error
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Ordered Insert Behavior                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Documents: [Doc1, Doc2, Doc3 (error), Doc4, Doc5]                 │
│                                                                     │
│  Processing:                                                        │
│  Doc1 ──→ ✓ Inserted                                               │
│  Doc2 ──→ ✓ Inserted                                               │
│  Doc3 ──→ ✗ Error (duplicate key)                                  │
│  Doc4 ──→ SKIPPED (not attempted)                                  │
│  Doc5 ──→ SKIPPED (not attempted)                                  │
│                                                                     │
│  Result: 2 inserted, 1 error, 2 not attempted                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Unordered Inserts

```javascript
// Ordered: false
// Continues on errors, attempts all documents
db.users.insertMany(
  [
    { _id: 1, name: "Alice" },
    { _id: 2, name: "Bob" },
    { _id: 1, name: "Charlie" },  // Duplicate _id - ERROR
    { _id: 3, name: "Diana" }      // Still attempted and inserted
  ],
  { ordered: false }
)

// Alice, Bob, and Diana are inserted
// Charlie fails due to duplicate _id
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Unordered Insert Behavior                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Documents: [Doc1, Doc2, Doc3 (error), Doc4, Doc5]                 │
│                                                                     │
│  Processing (potentially parallel):                                 │
│  Doc1 ──→ ✓ Inserted                                               │
│  Doc2 ──→ ✓ Inserted                                               │
│  Doc3 ──→ ✗ Error (duplicate key)                                  │
│  Doc4 ──→ ✓ Inserted (continues despite error)                     │
│  Doc5 ──→ ✓ Inserted (continues despite error)                     │
│                                                                     │
│  Result: 4 inserted, 1 error                                       │
│                                                                     │
│  Benefits:                                                          │
│  • Higher throughput (potential parallelization)                   │
│  • All valid documents are inserted                                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Use Case | Recommendation |
|----------|----------------|
| Dependent documents (order matters) | ordered: true |
| Independent documents | ordered: false |
| Data import/migration | ordered: false |
| Transaction-like behavior | ordered: true |
| Maximum throughput | ordered: false |

---

## Bulk Operations

### Bulk Write Overview

```javascript
// bulkWrite() allows mixing different operations
db.collection.bulkWrite([
  { insertOne: { document: { ... } } },
  { updateOne: { filter: { ... }, update: { ... } } },
  { updateMany: { filter: { ... }, update: { ... } } },
  { deleteOne: { filter: { ... } } },
  { deleteMany: { filter: { ... } } },
  { replaceOne: { filter: { ... }, replacement: { ... } } }
])
```

### Bulk Insert Example

```javascript
// Bulk insert with other operations
db.inventory.bulkWrite([
  {
    insertOne: {
      document: {
        sku: "ABC123",
        name: "Widget A",
        quantity: 100,
        price: 25.99
      }
    }
  },
  {
    insertOne: {
      document: {
        sku: "DEF456",
        name: "Widget B",
        quantity: 50,
        price: 35.99
      }
    }
  },
  {
    insertOne: {
      document: {
        sku: "GHI789",
        name: "Widget C",
        quantity: 200,
        price: 15.99
      }
    }
  }
])
```

### Mixed Bulk Operations

```javascript
// Combination of inserts, updates, and deletes
db.products.bulkWrite([
  // Insert new product
  {
    insertOne: {
      document: { sku: "NEW001", name: "New Product", qty: 50 }
    }
  },
  // Update existing product
  {
    updateOne: {
      filter: { sku: "EXIST001" },
      update: { $inc: { qty: 10 } }
    }
  },
  // Upsert (insert if not exists)
  {
    updateOne: {
      filter: { sku: "MAYBE001" },
      update: { $setOnInsert: { name: "Maybe Product" }, $set: { qty: 100 } },
      upsert: true
    }
  },
  // Delete discontinued product
  {
    deleteOne: {
      filter: { sku: "OLD001" }
    }
  }
], { ordered: false })

// Result:
{
  acknowledged: true,
  insertedCount: 1,
  matchedCount: 1,
  modifiedCount: 1,
  deletedCount: 1,
  upsertedCount: 1,
  upsertedIds: { '2': ObjectId("...") }
}
```

### Bulk Write Options

```javascript
db.collection.bulkWrite(operations, {
  ordered: true,              // Process in order (default)
  writeConcern: {
    w: "majority",
    j: true
  },
  bypassDocumentValidation: false,  // Skip validation
  comment: "Bulk operation description"
})
```

---

## Error Handling

### Common Insert Errors

```javascript
// 1. Duplicate Key Error (E11000)
try {
  db.users.insertOne({ _id: "existing_id", name: "User" })
} catch (e) {
  if (e.code === 11000) {
    print("Duplicate key error: " + e.message)
  }
}

// 2. Document Validation Error
try {
  // Assuming validation requires email field
  db.users.insertOne({ name: "User" })  // Missing email
} catch (e) {
  if (e.code === 121) {  // Document validation failure
    print("Validation error: " + e.message)
  }
}

// 3. Document Size Error
// Documents > 16MB will fail

// 4. Write Concern Error
try {
  db.users.insertOne(
    { name: "User" },
    { writeConcern: { w: 5, wtimeout: 1000 } }  // If only 3 nodes
  )
} catch (e) {
  if (e.code === 100) {  // WriteConcernFailed
    print("Write concern not satisfied")
  }
}
```

### Error Handling Patterns

```javascript
// Try-catch pattern
function safeInsert(collection, document) {
  try {
    const result = collection.insertOne(document)
    return { success: true, id: result.insertedId }
  } catch (error) {
    return { 
      success: false, 
      error: error.message,
      code: error.code 
    }
  }
}

// Usage
const result = safeInsert(db.users, { name: "Test" })
if (!result.success) {
  print("Insert failed: " + result.error)
}
```

### Handling insertMany Errors

```javascript
// Get details about which inserts failed
try {
  db.users.insertMany([
    { _id: 1, name: "Alice" },
    { _id: 1, name: "Bob" },     // Duplicate
    { _id: 2, name: "Charlie" }
  ], { ordered: false })
} catch (e) {
  // e.result contains partial results
  print("Inserted: " + e.result.nInserted)
  
  // e.writeErrors contains error details
  e.writeErrors.forEach(err => {
    print(`Error at index ${err.index}: ${err.errmsg}`)
  })
}
```

### Idempotent Inserts

```javascript
// Using updateOne with upsert for idempotent behavior
db.users.updateOne(
  { email: "user@example.com" },  // Find by unique identifier
  {
    $setOnInsert: {               // Only on insert
      createdAt: new Date(),
      role: "user"
    },
    $set: {                       // Always set
      name: "User Name",
      lastSeen: new Date()
    }
  },
  { upsert: true }
)

// This can be run multiple times safely
// First run: inserts document
// Subsequent runs: updates lastSeen only
```

---

## Performance Considerations

### Batch Size Optimization

```javascript
// Optimal batch sizes for insertMany
// Typically 100-1000 documents per batch

// Process large datasets in batches
function batchInsert(collection, documents, batchSize = 1000) {
  let inserted = 0;
  
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize);
    const result = collection.insertMany(batch, { ordered: false });
    inserted += result.insertedIds.length;
    
    print(`Batch ${Math.floor(i/batchSize) + 1}: Inserted ${result.insertedIds.length} documents`);
  }
  
  return inserted;
}

// Usage
const docs = [...];  // Large array of documents
const totalInserted = batchInsert(db.largeColl, docs, 500);
```

### Insert Performance Tips

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Insert Performance Optimization                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Use Unordered Inserts                                           │
│     ordered: false allows parallel processing                       │
│                                                                     │
│  2. Batch Appropriately                                             │
│     • Network round trips reduced                                  │
│     • 100-1000 documents per batch                                 │
│     • Consider document size                                       │
│                                                                     │
│  3. Index Considerations                                            │
│     • More indexes = slower inserts                                │
│     • Build indexes after bulk load                                │
│     • Use background index builds                                  │
│                                                                     │
│  4. Write Concern Trade-offs                                        │
│     • w:0 fastest, least durable                                   │
│     • w:"majority" safest, slower                                  │
│     • Balance for your use case                                    │
│                                                                     │
│  5. Pre-allocate _id                                                │
│     • Generate ObjectIds client-side                               │
│     • Reduces server workload                                      │
│                                                                     │
│  6. Document Design                                                 │
│     • Smaller documents = faster inserts                           │
│     • Avoid very deep nesting                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Monitoring Insert Performance

```javascript
// Check insert performance
db.setProfilingLevel(2, { slowms: 100 })

// View slow inserts
db.system.profile.find({
  op: "insert",
  millis: { $gt: 100 }
}).sort({ ts: -1 }).limit(10)

// Check operation statistics
db.serverStatus().opcounters.insert

// Current operations
db.currentOp({ op: "insert" })
```

### Pre-allocated _id Pattern

```javascript
// Generate ObjectIds on client side
const documents = [];
for (let i = 0; i < 10000; i++) {
  documents.push({
    _id: new ObjectId(),  // Pre-generated
    data: `item ${i}`,
    timestamp: new Date()
  });
}

// Insert with pre-generated IDs
db.items.insertMany(documents, { ordered: false });
```

---

## Summary

### Insert Methods Comparison

| Method | Use Case | Error Handling |
|--------|----------|----------------|
| `insertOne()` | Single document | Simple try-catch |
| `insertMany()` | Multiple documents | Error array |
| `bulkWrite()` | Mixed operations | Detailed results |

### Key Options

| Option | Default | Description |
|--------|---------|-------------|
| `ordered` | true | Process sequentially |
| `writeConcern.w` | 1 | Acknowledgment level |
| `writeConcern.j` | false | Journal commit |
| `writeConcern.wtimeout` | none | Timeout for w > 1 |

### Best Practices

1. **Use `insertMany()`** for bulk inserts
2. **Set `ordered: false`** for independent documents
3. **Choose appropriate write concern** for your durability needs
4. **Handle errors gracefully** with try-catch
5. **Batch large inserts** for optimal performance
6. **Pre-generate _ids** for high-throughput scenarios

### What's Next?

In the next chapter, we'll explore Query Operations, learning how to find and retrieve documents from collections.

---

## Practice Questions

1. What is the difference between insertOne() and insertMany()?
2. Explain the different write concern levels and when to use each.
3. How do ordered and unordered inserts differ in error handling?
4. What happens when a document fails validation during insert?
5. How can you make insert operations idempotent?
6. What is the maximum document size MongoDB supports?
7. When should you use bulkWrite() instead of insertMany()?
8. How can you improve insert performance for large datasets?

---

## Hands-On Exercises

### Exercise 1: Basic Inserts

```javascript
// Create a test database
use insertExercises

// 1. Insert a single user document
db.users.insertOne({
  name: "Test User",
  email: "test@example.com",
  createdAt: new Date()
})

// 2. Insert multiple products
db.products.insertMany([
  { name: "Product A", price: 10, category: "Electronics" },
  { name: "Product B", price: 20, category: "Books" },
  { name: "Product C", price: 30, category: "Electronics" }
])

// 3. Try inserting a duplicate _id and handle the error
try {
  db.users.insertOne({ _id: ObjectId("...existing_id..."), name: "Duplicate" })
} catch (e) {
  print("Error: " + e.message)
}
```

### Exercise 2: Write Concerns

```javascript
// Test different write concerns

// 1. Fire and forget (w: 0)
const start1 = new Date()
for (let i = 0; i < 1000; i++) {
  db.testWC.insertOne({ i: i }, { writeConcern: { w: 0 } })
}
print("w:0 took: " + (new Date() - start1) + "ms")

// 2. Default (w: 1)
const start2 = new Date()
for (let i = 0; i < 1000; i++) {
  db.testWC.insertOne({ i: i }, { writeConcern: { w: 1 } })
}
print("w:1 took: " + (new Date() - start2) + "ms")

// Compare the performance difference
```

### Exercise 3: Bulk Operations

```javascript
// Perform mixed bulk operations

db.inventory.bulkWrite([
  // Insert new items
  { insertOne: { document: { sku: "A001", qty: 100, price: 10 } } },
  { insertOne: { document: { sku: "B001", qty: 50, price: 20 } } },
  
  // Update existing item (create if not exists)
  { updateOne: {
      filter: { sku: "C001" },
      update: { $set: { qty: 200, price: 15 } },
      upsert: true
  }},
  
  // Insert another item
  { insertOne: { document: { sku: "D001", qty: 75, price: 25 } } }
], { ordered: false })

// Verify the results
db.inventory.find().pretty()
```

### Exercise 4: Error Handling

```javascript
// Create a collection with validation
db.createCollection("validatedUsers", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name"],
      properties: {
        email: { bsonType: "string", pattern: "^.+@.+$" },
        name: { bsonType: "string", minLength: 1 }
      }
    }
  }
})

// Try inserting valid and invalid documents
const testDocs = [
  { name: "Valid User", email: "valid@example.com" },  // Valid
  { name: "Invalid Email", email: "not-an-email" },     // Invalid
  { email: "missing@name.com" },                        // Missing name
  { name: "Missing Email" }                             // Missing email
]

testDocs.forEach((doc, index) => {
  try {
    db.validatedUsers.insertOne(doc)
    print(`Document ${index}: Inserted successfully`)
  } catch (e) {
    print(`Document ${index}: Failed - ${e.message}`)
  }
})
```

---

[← Previous: Databases and Collections](05-databases-and-collections.md) | [Next: Query Operations →](07-query-operations.md)
