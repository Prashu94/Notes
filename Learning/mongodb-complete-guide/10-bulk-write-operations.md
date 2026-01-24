# Chapter 10: Bulk Write Operations

## Table of Contents
- [Bulk Operations Overview](#bulk-operations-overview)
- [bulkWrite() Method](#bulkwrite-method)
- [Ordered vs Unordered Bulk Operations](#ordered-vs-unordered-bulk-operations)
- [Write Concerns for Bulk Operations](#write-concerns-for-bulk-operations)
- [Error Handling](#error-handling)
- [Performance Optimization](#performance-optimization)
- [Real-World Use Cases](#real-world-use-cases)
- [Summary](#summary)

---

## Bulk Operations Overview

Bulk operations allow you to perform multiple write operations in a single request, reducing network round trips and improving performance.

### Why Use Bulk Operations?

```
┌─────────────────────────────────────────────────────────────────────┐
│                Individual Operations vs Bulk Operations              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Individual Operations:                                             │
│  ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐             │
│  │Client  │───►│Server  │───►│Client  │───►│Server  │ ...         │
│  │Op 1    │◄───│Result  │◄───│Op 2    │◄───│Result  │             │
│  └────────┘    └────────┘    └────────┘    └────────┘             │
│                                                                     │
│  Network round trips: N (one per operation)                         │
│  Latency: High                                                      │
│                                                                     │
│  Bulk Operations:                                                   │
│  ┌────────────────────────┐    ┌────────────────────────┐          │
│  │Client                  │───►│Server                  │          │
│  │[Op1, Op2, Op3, Op4...] │◄───│[Result1, Result2...]   │          │
│  └────────────────────────┘    └────────────────────────┘          │
│                                                                     │
│  Network round trips: 1                                             │
│  Latency: Low                                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Supported Bulk Operations

| Operation | Description |
|-----------|-------------|
| `insertOne` | Insert a single document |
| `updateOne` | Update first matching document |
| `updateMany` | Update all matching documents |
| `deleteOne` | Delete first matching document |
| `deleteMany` | Delete all matching documents |
| `replaceOne` | Replace first matching document |

---

## bulkWrite() Method

### Basic Syntax

```javascript
db.collection.bulkWrite(
  [
    { operation1 },
    { operation2 },
    ...
  ],
  {
    ordered: <boolean>,
    writeConcern: <document>,
    bypassDocumentValidation: <boolean>,
    comment: <any>
  }
)
```

### Insert Operations

```javascript
db.products.bulkWrite([
  {
    insertOne: {
      document: {
        sku: "ABC001",
        name: "Product A",
        price: 99.99,
        stock: 100
      }
    }
  },
  {
    insertOne: {
      document: {
        sku: "ABC002",
        name: "Product B",
        price: 149.99,
        stock: 50
      }
    }
  },
  {
    insertOne: {
      document: {
        sku: "ABC003",
        name: "Product C",
        price: 199.99,
        stock: 25
      }
    }
  }
])

// Result:
{
  acknowledged: true,
  insertedCount: 3,
  insertedIds: {
    0: ObjectId("..."),
    1: ObjectId("..."),
    2: ObjectId("...")
  },
  matchedCount: 0,
  modifiedCount: 0,
  deletedCount: 0,
  upsertedCount: 0,
  upsertedIds: {}
}
```

### Update Operations

```javascript
db.products.bulkWrite([
  // Update single document
  {
    updateOne: {
      filter: { sku: "ABC001" },
      update: { $set: { price: 89.99 } }
    }
  },
  // Update with upsert
  {
    updateOne: {
      filter: { sku: "NEW001" },
      update: {
        $set: { name: "New Product", price: 79.99 },
        $setOnInsert: { createdAt: new Date() }
      },
      upsert: true
    }
  },
  // Update multiple documents
  {
    updateMany: {
      filter: { category: "Electronics" },
      update: { $inc: { stock: 10 } }
    }
  }
])
```

### Delete Operations

```javascript
db.products.bulkWrite([
  // Delete single document
  {
    deleteOne: {
      filter: { sku: "DISC001" }
    }
  },
  // Delete multiple documents
  {
    deleteMany: {
      filter: { 
        stock: 0,
        discontinued: true
      }
    }
  }
])
```

### Replace Operations

```javascript
db.products.bulkWrite([
  {
    replaceOne: {
      filter: { sku: "OLD001" },
      replacement: {
        sku: "OLD001",
        name: "Updated Product",
        price: 129.99,
        stock: 75,
        lastModified: new Date()
      },
      upsert: false
    }
  }
])
```

### Mixed Operations

```javascript
// Comprehensive example with all operation types
db.inventory.bulkWrite([
  // Insert new items
  {
    insertOne: {
      document: { sku: "NEW001", name: "New Item", qty: 100, price: 50 }
    }
  },
  
  // Update existing item
  {
    updateOne: {
      filter: { sku: "EXIST001" },
      update: { 
        $inc: { qty: 20 },
        $set: { lastRestocked: new Date() }
      }
    }
  },
  
  // Upsert item
  {
    updateOne: {
      filter: { sku: "MAYBE001" },
      update: {
        $set: { name: "Maybe Item", qty: 50, price: 30 },
        $setOnInsert: { createdAt: new Date() }
      },
      upsert: true
    }
  },
  
  // Update multiple items
  {
    updateMany: {
      filter: { category: "Seasonal" },
      update: { $mul: { price: 0.8 } }  // 20% discount
    }
  },
  
  // Replace item completely
  {
    replaceOne: {
      filter: { sku: "REPLACE001" },
      replacement: {
        sku: "REPLACE001",
        name: "Replaced Item",
        qty: 200,
        price: 75,
        version: 2
      }
    }
  },
  
  // Delete single item
  {
    deleteOne: {
      filter: { sku: "DEL001" }
    }
  },
  
  // Delete multiple items
  {
    deleteMany: {
      filter: { discontinued: true, qty: 0 }
    }
  }
])
```

---

## Ordered vs Unordered Bulk Operations

### Ordered Operations (Default)

```javascript
// Ordered: true (default)
// Operations execute sequentially
// Stops on first error
db.products.bulkWrite([
  { insertOne: { document: { _id: 1, name: "A" } } },
  { insertOne: { document: { _id: 2, name: "B" } } },
  { insertOne: { document: { _id: 1, name: "C" } } },  // Duplicate - ERROR
  { insertOne: { document: { _id: 3, name: "D" } } }   // Not executed
], { ordered: true })

// Result: Only documents with _id 1 and 2 are inserted
// Error thrown for duplicate _id
// Document with _id 3 is not attempted
```

### Unordered Operations

```javascript
// Ordered: false
// Operations may execute in parallel
// Continues after errors
db.products.bulkWrite([
  { insertOne: { document: { _id: 1, name: "A" } } },
  { insertOne: { document: { _id: 2, name: "B" } } },
  { insertOne: { document: { _id: 1, name: "C" } } },  // Duplicate - ERROR
  { insertOne: { document: { _id: 3, name: "D" } } }   // Still executed
], { ordered: false })

// Result: Documents with _id 1, 2, and 3 are inserted
// Error recorded for duplicate _id
// All valid operations complete
```

### Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│              Ordered vs Unordered Comparison                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Ordered (true):                                                    │
│  ┌───┐ → ┌───┐ → ┌───┐ → ┌───┐                                    │
│  │Op1│   │Op2│   │Op3│   │Op4│                                    │
│  └───┘   └───┘   └─┬─┘   └───┘                                    │
│                    │ Error                                          │
│                    ▼                                                │
│                  STOP (Op4 not executed)                           │
│                                                                     │
│  Use when: Order matters, dependent operations                     │
│                                                                     │
│  Unordered (false):                                                │
│  ┌───┐   ┌───┐   ┌───┐   ┌───┐                                    │
│  │Op1│   │Op2│   │Op3│   │Op4│  (potentially parallel)            │
│  └─┬─┘   └─┬─┘   └─┬─┘   └─┬─┘                                    │
│    │       │       │       │                                        │
│    ▼       ▼       ▼       ▼                                        │
│   OK      OK    Error     OK                                        │
│                                                                     │
│  Use when: Order doesn't matter, maximum throughput needed         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### When to Use Each

| Scenario | Recommendation |
|----------|----------------|
| Data import/migration | Unordered |
| Sequential processing required | Ordered |
| Parent-child relationships | Ordered |
| Independent updates | Unordered |
| Maximum performance needed | Unordered |
| Rollback on any error | Ordered |

---

## Write Concerns for Bulk Operations

### Write Concern Options

```javascript
db.products.bulkWrite(
  [
    { insertOne: { document: { name: "Product" } } }
  ],
  {
    writeConcern: {
      w: "majority",    // Wait for majority acknowledgment
      j: true,          // Wait for journal commit
      wtimeout: 5000    // Timeout after 5 seconds
    }
  }
)
```

### Write Concern Levels

```javascript
// w: 0 - No acknowledgment (fire and forget)
db.logs.bulkWrite(operations, {
  writeConcern: { w: 0 }
})

// w: 1 - Primary acknowledgment (default)
db.products.bulkWrite(operations, {
  writeConcern: { w: 1 }
})

// w: "majority" - Majority of replica set
db.orders.bulkWrite(operations, {
  writeConcern: { w: "majority" }
})

// w: <number> - Specific number of nodes
db.critical.bulkWrite(operations, {
  writeConcern: { w: 3 }
})

// With journal
db.financial.bulkWrite(operations, {
  writeConcern: { w: "majority", j: true }
})
```

---

## Error Handling

### BulkWriteError

```javascript
try {
  db.products.bulkWrite([
    { insertOne: { document: { _id: 1, name: "A" } } },
    { insertOne: { document: { _id: 1, name: "B" } } },  // Duplicate
    { insertOne: { document: { _id: 2, name: "C" } } }
  ], { ordered: false })
} catch (e) {
  // BulkWriteError properties
  print("Error code:", e.code)
  print("Write errors:", e.writeErrors.length)
  
  // Successful operations still recorded
  print("Inserted:", e.result.nInserted)
  print("Modified:", e.result.nModified)
  print("Deleted:", e.result.nRemoved)
  
  // Details of each error
  e.writeErrors.forEach((error, index) => {
    print(`Error ${index}:`)
    print(`  Operation index: ${error.index}`)
    print(`  Error code: ${error.code}`)
    print(`  Message: ${error.errmsg}`)
  })
}
```

### Error Recovery Pattern

```javascript
function robustBulkWrite(collection, operations, maxRetries = 3) {
  let retries = 0
  let remainingOps = [...operations]
  let totalResult = {
    insertedCount: 0,
    matchedCount: 0,
    modifiedCount: 0,
    deletedCount: 0,
    upsertedCount: 0,
    errors: []
  }
  
  while (remainingOps.length > 0 && retries < maxRetries) {
    try {
      const result = collection.bulkWrite(remainingOps, { ordered: false })
      
      totalResult.insertedCount += result.insertedCount
      totalResult.matchedCount += result.matchedCount
      totalResult.modifiedCount += result.modifiedCount
      totalResult.deletedCount += result.deletedCount
      totalResult.upsertedCount += result.upsertedCount
      
      remainingOps = []  // All succeeded
      
    } catch (e) {
      if (e.writeErrors) {
        // Record errors
        totalResult.errors.push(...e.writeErrors)
        
        // Remove successful operations
        const failedIndices = new Set(e.writeErrors.map(err => err.index))
        remainingOps = remainingOps.filter((_, i) => failedIndices.has(i))
        
        // Update counts from partial success
        totalResult.insertedCount += e.result.nInserted || 0
        totalResult.modifiedCount += e.result.nModified || 0
        totalResult.deletedCount += e.result.nRemoved || 0
      }
      
      retries++
      
      if (retries < maxRetries && remainingOps.length > 0) {
        print(`Retry ${retries}/${maxRetries} for ${remainingOps.length} failed operations`)
        sleep(1000 * retries)  // Exponential backoff
      }
    }
  }
  
  return totalResult
}
```

### Handling Specific Error Types

```javascript
function handleBulkErrors(error) {
  const results = {
    duplicates: [],
    validationErrors: [],
    otherErrors: []
  }
  
  if (error.writeErrors) {
    error.writeErrors.forEach(err => {
      switch (err.code) {
        case 11000:  // Duplicate key
          results.duplicates.push({
            index: err.index,
            key: err.keyValue
          })
          break
        case 121:    // Document validation failed
          results.validationErrors.push({
            index: err.index,
            message: err.errmsg
          })
          break
        default:
          results.otherErrors.push(err)
      }
    })
  }
  
  return results
}
```

---

## Performance Optimization

### Batch Size Optimization

```javascript
// Optimal batch size depends on:
// - Document size
// - Network latency
// - Server resources

// General guideline: 100-1000 operations per batch

function optimizedBulkWrite(collection, operations, batchSize = 500) {
  const results = []
  
  for (let i = 0; i < operations.length; i += batchSize) {
    const batch = operations.slice(i, i + batchSize)
    
    try {
      const result = collection.bulkWrite(batch, { ordered: false })
      results.push({ success: true, result })
    } catch (e) {
      results.push({ success: false, error: e, result: e.result })
    }
    
    // Optional: yield between batches for large operations
    if (i + batchSize < operations.length) {
      sleep(10)  // Small delay between batches
    }
  }
  
  return results
}
```

### Performance Comparison

```javascript
// Test data
const testDocs = Array.from({ length: 10000 }, (_, i) => ({
  index: i,
  value: Math.random()
}))

// Method 1: Individual inserts
console.time("Individual")
testDocs.forEach(doc => {
  db.test1.insertOne(doc)
})
console.timeEnd("Individual")

// Method 2: insertMany
console.time("InsertMany")
db.test2.insertMany(testDocs)
console.timeEnd("InsertMany")

// Method 3: Bulk write
console.time("BulkWrite")
db.test3.bulkWrite(
  testDocs.map(doc => ({ insertOne: { document: doc } })),
  { ordered: false }
)
console.timeEnd("BulkWrite")

// Typical results:
// Individual: ~5000ms
// InsertMany: ~200ms
// BulkWrite: ~250ms (more overhead but flexible operations)
```

### Memory Management

```javascript
// For very large operations, process in chunks to manage memory
function streamBulkWrite(collection, documentGenerator, batchSize = 1000) {
  let batch = []
  let totalProcessed = 0
  
  for (const doc of documentGenerator) {
    batch.push({ insertOne: { document: doc } })
    
    if (batch.length >= batchSize) {
      collection.bulkWrite(batch, { ordered: false })
      totalProcessed += batch.length
      print(`Processed ${totalProcessed} documents`)
      batch = []  // Clear batch to free memory
    }
  }
  
  // Process remaining documents
  if (batch.length > 0) {
    collection.bulkWrite(batch, { ordered: false })
    totalProcessed += batch.length
  }
  
  return totalProcessed
}

// Generator function for large datasets
function* generateDocuments(count) {
  for (let i = 0; i < count; i++) {
    yield {
      index: i,
      timestamp: new Date(),
      data: `Document ${i}`
    }
  }
}

// Usage
const total = streamBulkWrite(
  db.largeCollection,
  generateDocuments(100000),
  1000
)
```

---

## Real-World Use Cases

### E-commerce Order Processing

```javascript
// Process multiple order updates
function processOrders(orders) {
  const operations = orders.map(order => ({
    updateOne: {
      filter: { orderId: order.orderId },
      update: {
        $set: {
          status: order.newStatus,
          processedAt: new Date(),
          trackingNumber: order.trackingNumber
        },
        $push: {
          statusHistory: {
            status: order.newStatus,
            timestamp: new Date(),
            note: order.note
          }
        }
      }
    }
  }))
  
  // Also update inventory
  orders.forEach(order => {
    if (order.newStatus === 'shipped') {
      order.items.forEach(item => {
        operations.push({
          updateOne: {
            filter: { sku: item.sku },
            update: { $inc: { reserved: -item.quantity } }
          }
        })
      })
    }
  })
  
  return db.orders.bulkWrite(operations, { ordered: false })
}
```

### Data Migration

```javascript
// Migrate data between collections with transformation
function migrateWithTransformation(sourceCollection, targetCollection, batchSize = 1000) {
  let processed = 0
  let cursor = sourceCollection.find()
  let batch = []
  
  while (cursor.hasNext()) {
    const doc = cursor.next()
    
    // Transform document
    const transformed = {
      _id: doc._id,
      // Flatten nested structure
      firstName: doc.name?.first || "",
      lastName: doc.name?.last || "",
      email: doc.contact?.email || "",
      // Add new fields
      migratedAt: new Date(),
      version: 2
    }
    
    batch.push({ insertOne: { document: transformed } })
    
    if (batch.length >= batchSize) {
      targetCollection.bulkWrite(batch, { ordered: false })
      processed += batch.length
      print(`Migrated ${processed} documents`)
      batch = []
    }
  }
  
  if (batch.length > 0) {
    targetCollection.bulkWrite(batch, { ordered: false })
    processed += batch.length
  }
  
  return processed
}
```

### Sync External Data

```javascript
// Sync data from external API
function syncExternalProducts(apiProducts) {
  const operations = apiProducts.map(product => ({
    updateOne: {
      filter: { externalId: product.id },
      update: {
        $set: {
          name: product.name,
          price: product.price,
          description: product.description,
          lastSyncAt: new Date()
        },
        $setOnInsert: {
          externalId: product.id,
          createdAt: new Date()
        }
      },
      upsert: true
    }
  }))
  
  return db.products.bulkWrite(operations, { ordered: false })
}
```

### Batch Status Updates

```javascript
// Update status for multiple entities
function batchStatusUpdate(entityType, entityIds, newStatus, reason) {
  const collection = db[entityType]
  const timestamp = new Date()
  
  const operations = entityIds.map(id => ({
    updateOne: {
      filter: { _id: id },
      update: {
        $set: {
          status: newStatus,
          statusUpdatedAt: timestamp
        },
        $push: {
          statusLog: {
            status: newStatus,
            reason: reason,
            timestamp: timestamp
          }
        }
      }
    }
  }))
  
  return collection.bulkWrite(operations, { ordered: false })
}

// Usage
batchStatusUpdate(
  "orders",
  ["ord1", "ord2", "ord3"],
  "cancelled",
  "Customer request"
)
```

---

## Summary

### Key Methods

| Method | Use Case |
|--------|----------|
| `bulkWrite()` | Mixed operations in single request |
| `insertMany()` | Bulk inserts only |
| `updateMany()` | Update multiple with same criteria |
| `deleteMany()` | Delete multiple with same criteria |

### Operation Types in bulkWrite

| Operation | Required Fields |
|-----------|-----------------|
| `insertOne` | document |
| `updateOne` | filter, update, [upsert] |
| `updateMany` | filter, update, [upsert] |
| `replaceOne` | filter, replacement, [upsert] |
| `deleteOne` | filter |
| `deleteMany` | filter |

### Performance Tips

1. **Use unordered** for independent operations
2. **Batch appropriately** (100-1000 operations)
3. **Handle errors gracefully** with retry logic
4. **Monitor memory** for large operations
5. **Choose appropriate write concern**

### What's Next?

In the next chapter, we'll explore Data Modeling Concepts for designing effective document schemas.

---

## Practice Questions

1. When should you use ordered vs unordered bulk operations?
2. How does bulkWrite() differ from multiple individual operations?
3. What happens when an error occurs in ordered vs unordered mode?
4. How do you handle partial failures in bulk operations?
5. What is the optimal batch size for bulk operations?
6. How can you implement upsert in bulk operations?
7. What are the memory considerations for large bulk operations?
8. How do write concerns affect bulk operation performance?

---

## Hands-On Exercises

### Exercise 1: Basic Bulk Write

```javascript
// Create a products collection and perform bulk operations
db.bulkProducts.drop()

db.bulkProducts.bulkWrite([
  { insertOne: { document: { sku: "A001", name: "Product A", price: 100, stock: 50 } } },
  { insertOne: { document: { sku: "A002", name: "Product B", price: 200, stock: 30 } } },
  { insertOne: { document: { sku: "A003", name: "Product C", price: 150, stock: 40 } } },
  { updateOne: { filter: { sku: "A001" }, update: { $inc: { stock: 10 } } } },
  { updateMany: { filter: { price: { $gt: 100 } }, update: { $set: { premium: true } } } },
  { deleteOne: { filter: { sku: "A003" } } }
])

// Verify results
db.bulkProducts.find()
```

### Exercise 2: Error Handling

```javascript
// Test error handling with duplicates
db.errorTest.drop()
db.errorTest.createIndex({ sku: 1 }, { unique: true })

try {
  db.errorTest.bulkWrite([
    { insertOne: { document: { sku: "SKU001", name: "First" } } },
    { insertOne: { document: { sku: "SKU002", name: "Second" } } },
    { insertOne: { document: { sku: "SKU001", name: "Duplicate" } } },
    { insertOne: { document: { sku: "SKU003", name: "Third" } } }
  ], { ordered: false })
} catch (e) {
  print("Error occurred:", e.writeErrors.length, "errors")
  print("Successfully inserted:", e.result.nInserted)
  e.writeErrors.forEach(err => {
    print(`  Index ${err.index}: ${err.errmsg}`)
  })
}

// Check what was inserted
db.errorTest.find()
```

### Exercise 3: Upsert Pattern

```javascript
// Implement sync pattern with upsert
const externalData = [
  { id: "ext1", name: "External Product 1", price: 99 },
  { id: "ext2", name: "External Product 2", price: 149 },
  { id: "ext3", name: "External Product 3", price: 199 }
]

db.syncTest.bulkWrite(
  externalData.map(item => ({
    updateOne: {
      filter: { externalId: item.id },
      update: {
        $set: {
          name: item.name,
          price: item.price,
          lastSync: new Date()
        },
        $setOnInsert: {
          externalId: item.id,
          createdAt: new Date()
        }
      },
      upsert: true
    }
  })),
  { ordered: false }
)

// Run again to see update behavior
db.syncTest.bulkWrite(
  externalData.map(item => ({
    updateOne: {
      filter: { externalId: item.id },
      update: {
        $set: {
          name: item.name + " Updated",
          price: item.price * 1.1,
          lastSync: new Date()
        },
        $setOnInsert: {
          externalId: item.id,
          createdAt: new Date()
        }
      },
      upsert: true
    }
  })),
  { ordered: false }
)

db.syncTest.find()
```

### Exercise 4: Performance Comparison

```javascript
// Compare individual vs bulk operations
const testSize = 1000

// Generate test data
const docs = Array.from({ length: testSize }, (_, i) => ({
  index: i,
  value: Math.random(),
  timestamp: new Date()
}))

// Test individual inserts
db.perfTest1.drop()
const start1 = new Date()
docs.forEach(doc => db.perfTest1.insertOne(doc))
const time1 = new Date() - start1

// Test insertMany
db.perfTest2.drop()
const start2 = new Date()
db.perfTest2.insertMany(docs)
const time2 = new Date() - start2

// Test bulkWrite
db.perfTest3.drop()
const start3 = new Date()
db.perfTest3.bulkWrite(
  docs.map(doc => ({ insertOne: { document: doc } })),
  { ordered: false }
)
const time3 = new Date() - start3

print(`Individual inserts: ${time1}ms`)
print(`insertMany: ${time2}ms`)
print(`bulkWrite: ${time3}ms`)
```

---

[← Previous: Delete Operations](09-delete-operations.md) | [Next: Data Modeling Concepts →](11-data-modeling-concepts.md)
