# Chapter 9: Delete Operations

## Table of Contents
- [Delete Overview](#delete-overview)
- [deleteOne()](#deleteone)
- [deleteMany()](#deletemany)
- [findOneAndDelete()](#findoneanddelete)
- [Drop Operations](#drop-operations)
- [Soft Delete Pattern](#soft-delete-pattern)
- [TTL Indexes for Auto-Deletion](#ttl-indexes-for-auto-deletion)
- [Bulk Delete Operations](#bulk-delete-operations)
- [Summary](#summary)

---

## Delete Overview

MongoDB provides several methods for removing documents from collections.

### Delete Methods

| Method | Description |
|--------|-------------|
| `deleteOne()` | Delete first matching document |
| `deleteMany()` | Delete all matching documents |
| `findOneAndDelete()` | Delete and return document |
| `drop()` | Delete entire collection |
| `bulkWrite()` | Batch delete operations |

### Delete vs Remove (Legacy)

```javascript
// Modern methods (recommended)
db.collection.deleteOne({ filter })
db.collection.deleteMany({ filter })

// Legacy method (deprecated)
db.collection.remove({ filter })  // Avoid using
```

---

## deleteOne()

### Basic Syntax

```javascript
db.collection.deleteOne(
  { filter },    // Which document to delete
  { options }    // Additional options
)
```

### Delete Single Document

```javascript
// Delete by _id
db.products.deleteOne({ _id: ObjectId("507f1f77bcf86cd799439011") })

// Result:
{
  acknowledged: true,
  deletedCount: 1
}

// Delete by field value
db.products.deleteOne({ sku: "DISC001" })

// Delete first matching
db.logs.deleteOne({ level: "debug" })  // Deletes first debug log
```

### Delete with Options

```javascript
db.products.deleteOne(
  { sku: "ABC123" },
  {
    writeConcern: { w: "majority" },  // Write concern
    collation: { locale: "en" },       // Collation
    hint: { sku: 1 },                  // Index hint
    comment: "Remove discontinued"      // Operation comment
  }
)
```

### Check Before Delete

```javascript
// Find then delete pattern
const doc = db.products.findOne({ sku: "ABC123" })
if (doc) {
  // Maybe archive first
  db.products_archive.insertOne({
    ...doc,
    archivedAt: new Date()
  })
  
  // Then delete
  db.products.deleteOne({ _id: doc._id })
}
```

---

## deleteMany()

### Delete Multiple Documents

```javascript
// Delete all matching documents
db.products.deleteMany({ category: "Discontinued" })

// Result:
{
  acknowledged: true,
  deletedCount: 47
}
```

### Common Delete Patterns

```javascript
// Delete by status
db.orders.deleteMany({ status: "cancelled" })

// Delete by date range
db.logs.deleteMany({
  timestamp: { $lt: new Date("2024-01-01") }
})

// Delete by multiple conditions
db.sessions.deleteMany({
  $and: [
    { lastActivity: { $lt: new Date(Date.now() - 86400000) } },
    { isActive: false }
  ]
})

// Delete all documents (empty filter)
db.tempData.deleteMany({})  // Removes all documents
// Collection still exists, indexes retained

// Delete with complex query
db.users.deleteMany({
  $or: [
    { status: "banned" },
    { 
      lastLogin: { $lt: new Date("2020-01-01") },
      emailVerified: false 
    }
  ]
})
```

### Delete with Aggregation Conditions

```javascript
// Delete based on aggregation results
const inactiveUsers = db.users.aggregate([
  {
    $lookup: {
      from: "orders",
      localField: "_id",
      foreignField: "userId",
      as: "orders"
    }
  },
  {
    $match: {
      lastLogin: { $lt: new Date("2023-01-01") },
      orders: { $size: 0 }
    }
  },
  { $project: { _id: 1 } }
]).toArray()

const userIds = inactiveUsers.map(u => u._id)
db.users.deleteMany({ _id: { $in: userIds } })
```

---

## findOneAndDelete()

### Delete and Return Document

```javascript
// Delete and get deleted document
const deleted = db.products.findOneAndDelete({ sku: "ABC123" })

// deleted contains the removed document
{
  _id: ObjectId("..."),
  sku: "ABC123",
  name: "Product Name",
  price: 99.99
}

// Returns null if no document found
const notFound = db.products.findOneAndDelete({ sku: "NOTEXIST" })
// notFound is null
```

### With Options

```javascript
// With projection
const deleted = db.products.findOneAndDelete(
  { category: "Discontinued" },
  {
    projection: { sku: 1, name: 1, _id: 0 }
  }
)

// With sort (delete specific document)
const oldestLog = db.logs.findOneAndDelete(
  { level: "debug" },
  { sort: { timestamp: 1 } }  // Delete oldest first
)

// Combined options
const result = db.jobs.findOneAndDelete(
  { status: "failed", retries: { $gte: 3 } },
  {
    sort: { createdAt: 1 },          // Oldest first
    projection: { _id: 1, task: 1 },  // Return only these fields
    maxTimeMS: 5000                   // Timeout
  }
)
```

### Use Cases

```javascript
// Queue processing - get and remove item
function processNextJob() {
  const job = db.jobQueue.findOneAndDelete(
    { status: "pending" },
    { sort: { priority: -1, createdAt: 1 } }
  )
  
  if (job) {
    try {
      // Process the job
      processJob(job)
    } catch (error) {
      // Re-queue on failure
      db.jobQueue.insertOne({
        ...job,
        _id: new ObjectId(),
        status: "pending",
        retries: (job.retries || 0) + 1,
        lastError: error.message
      })
    }
  }
  
  return job
}

// Claim and delete token
function consumeToken(token) {
  const validToken = db.tokens.findOneAndDelete({
    token: token,
    expiresAt: { $gt: new Date() }
  })
  
  return validToken !== null
}
```

---

## Drop Operations

### Drop Collection

```javascript
// Remove entire collection
db.products.drop()

// Result: true if collection existed, false otherwise

// Check before dropping
if (db.getCollectionNames().includes("tempData")) {
  db.tempData.drop()
}
```

### Drop vs deleteMany

```javascript
// deleteMany({}) - Removes all documents
db.collection.deleteMany({})
// - Collection still exists
// - Indexes retained
// - Slower for large collections
// - Logged in oplog per document

// drop() - Removes collection entirely  
db.collection.drop()
// - Collection removed
// - Indexes removed
// - Faster for large collections
// - Single oplog entry
```

### Drop Database

```javascript
// Remove entire database
use databaseToDelete
db.dropDatabase()

// Result:
{ "ok": 1, "dropped": "databaseToDelete" }

// Warning: This is irreversible!
```

---

## Soft Delete Pattern

Instead of physically deleting documents, mark them as deleted.

### Basic Soft Delete

```javascript
// Add deleted flag instead of removing
db.users.updateOne(
  { _id: userId },
  {
    $set: {
      isDeleted: true,
      deletedAt: new Date(),
      deletedBy: currentUserId
    }
  }
)

// Query active documents
db.users.find({ isDeleted: { $ne: true } })

// Or use $exists for documents without the flag
db.users.find({
  $or: [
    { isDeleted: false },
    { isDeleted: { $exists: false } }
  ]
})
```

### Soft Delete with Helper Functions

```javascript
// Soft delete function
function softDelete(collection, filter, deletedBy) {
  return collection.updateMany(
    { ...filter, isDeleted: { $ne: true } },
    {
      $set: {
        isDeleted: true,
        deletedAt: new Date(),
        deletedBy: deletedBy
      }
    }
  )
}

// Restore function
function restore(collection, filter) {
  return collection.updateMany(
    { ...filter, isDeleted: true },
    {
      $unset: { isDeleted: "", deletedAt: "", deletedBy: "" }
    }
  )
}

// Permanent delete (cleanup old soft-deleted)
function permanentDelete(collection, olderThan) {
  return collection.deleteMany({
    isDeleted: true,
    deletedAt: { $lt: olderThan }
  })
}

// Usage
softDelete(db.users, { _id: userId }, adminId)
restore(db.users, { _id: userId })
permanentDelete(db.users, new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))
```

### Soft Delete with Views

```javascript
// Create view for active documents only
db.createView("activeUsers", "users", [
  { $match: { isDeleted: { $ne: true } } }
])

// Query through view
db.activeUsers.find({ role: "admin" })

// Create view for deleted documents
db.createView("deletedUsers", "users", [
  { $match: { isDeleted: true } }
])
```

### Soft Delete Index Strategy

```javascript
// Partial index for active documents
db.users.createIndex(
  { email: 1 },
  {
    unique: true,
    partialFilterExpression: { isDeleted: { $ne: true } }
  }
)

// This allows "deleted" users to have same email
// Active users still have unique emails
```

---

## TTL Indexes for Auto-Deletion

TTL (Time To Live) indexes automatically delete documents after a specified time.

### Create TTL Index

```javascript
// Delete documents 24 hours after createdAt
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 86400 }  // 24 hours in seconds
)

// Delete documents at specific time
db.notifications.createIndex(
  { expiresAt: 1 },
  { expireAfterSeconds: 0 }  // Delete when expiresAt is reached
)

// Documents must have the indexed date field
db.sessions.insertOne({
  userId: "user123",
  token: "abc123",
  createdAt: new Date()  // Required for TTL
})

db.notifications.insertOne({
  message: "Your trial expires soon",
  userId: "user123",
  expiresAt: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)  // 7 days
})
```

### TTL Index Behavior

```
┌─────────────────────────────────────────────────────────────────────┐
│                     TTL Index Behavior                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TTL Background Thread:                                             │
│  • Runs every 60 seconds                                           │
│  • Checks for expired documents                                    │
│  • Deletes in background                                           │
│                                                                     │
│  Document Lifecycle:                                                │
│  ┌─────────┐                                                       │
│  │ Created │ ──────────────────────────────────────────────────    │
│  └────┬────┘         Time passes (expireAfterSeconds)              │
│       │                                                             │
│       ▼                                                             │
│  ┌─────────────┐                                                   │
│  │   Expired   │ ◄── TTL thread identifies document                │
│  └──────┬──────┘                                                   │
│         │                                                           │
│         ▼                                                           │
│  ┌─────────────┐                                                   │
│  │   Deleted   │ ◄── Background deletion (not immediate)           │
│  └─────────────┘                                                   │
│                                                                     │
│  Note: Actual deletion may occur up to 60 seconds after expiry     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### TTL Use Cases

```javascript
// Session management
db.sessions.createIndex(
  { lastActivity: 1 },
  { expireAfterSeconds: 3600 }  // 1 hour
)

// Password reset tokens
db.resetTokens.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 900 }  // 15 minutes
)

// Event data retention
db.events.createIndex(
  { timestamp: 1 },
  { expireAfterSeconds: 2592000 }  // 30 days
)

// Cache with custom expiry
db.cache.createIndex(
  { expiresAt: 1 },
  { expireAfterSeconds: 0 }
)

// Insert with custom TTL
db.cache.insertOne({
  key: "user:123:profile",
  value: { name: "John" },
  expiresAt: new Date(Date.now() + 3600000)  // 1 hour
})

// Insert with longer TTL
db.cache.insertOne({
  key: "static:config",
  value: { theme: "dark" },
  expiresAt: new Date(Date.now() + 86400000)  // 24 hours
})
```

### Modify TTL Index

```javascript
// Cannot modify TTL directly, must use collMod
db.runCommand({
  collMod: "sessions",
  index: {
    keyPattern: { createdAt: 1 },
    expireAfterSeconds: 7200  // Change to 2 hours
  }
})
```

---

## Bulk Delete Operations

### Bulk Write with Deletes

```javascript
// Multiple delete operations
db.products.bulkWrite([
  {
    deleteOne: {
      filter: { sku: "DISC001" }
    }
  },
  {
    deleteMany: {
      filter: { category: "Discontinued" }
    }
  },
  {
    deleteOne: {
      filter: { sku: "OLD002" }
    }
  }
])

// Result:
{
  acknowledged: true,
  deletedCount: 48,
  insertedCount: 0,
  matchedCount: 0,
  modifiedCount: 0,
  upsertedCount: 0,
  insertedIds: {},
  upsertedIds: {}
}
```

### Batch Delete Pattern

```javascript
// Delete in batches for large collections
async function batchDelete(collection, filter, batchSize = 1000) {
  let totalDeleted = 0
  let deletedInBatch
  
  do {
    // Find batch of documents to delete
    const docs = collection.find(filter)
      .limit(batchSize)
      .toArray()
    
    if (docs.length === 0) break
    
    const ids = docs.map(d => d._id)
    
    // Delete batch
    const result = collection.deleteMany({
      _id: { $in: ids }
    })
    
    deletedInBatch = result.deletedCount
    totalDeleted += deletedInBatch
    
    print(`Deleted ${deletedInBatch} documents (total: ${totalDeleted})`)
    
  } while (deletedInBatch > 0)
  
  return totalDeleted
}

// Usage
batchDelete(db.logs, { level: "debug", date: { $lt: new Date("2024-01-01") } })
```

### Mixed Bulk Operations

```javascript
// Archive and delete pattern
const toArchive = db.orders.find({
  status: "completed",
  completedAt: { $lt: new Date("2023-01-01") }
}).toArray()

// Bulk write: insert into archive, delete from orders
db.orders_archive.bulkWrite(
  toArchive.map(doc => ({
    insertOne: {
      document: { ...doc, archivedAt: new Date() }
    }
  }))
)

db.orders.deleteMany({
  _id: { $in: toArchive.map(d => d._id) }
})
```

---

## Best Practices

### Safe Delete Patterns

```javascript
// 1. Always use specific filters
// ❌ Bad - too broad
db.users.deleteMany({ role: "user" })

// ✓ Good - specific
db.users.deleteMany({
  role: "user",
  isDeleted: true,
  deletedAt: { $lt: new Date("2023-01-01") }
})

// 2. Verify before delete
const count = db.users.countDocuments({
  lastLogin: { $lt: new Date("2020-01-01") }
})
print(`About to delete ${count} users`)

if (count < 1000) {  // Safety check
  db.users.deleteMany({
    lastLogin: { $lt: new Date("2020-01-01") }
  })
}

// 3. Archive before delete
function archiveAndDelete(sourceCollection, archiveCollection, filter) {
  const docs = sourceCollection.find(filter).toArray()
  
  if (docs.length > 0) {
    archiveCollection.insertMany(
      docs.map(d => ({ ...d, archivedAt: new Date() }))
    )
    
    sourceCollection.deleteMany({
      _id: { $in: docs.map(d => d._id) }
    })
  }
  
  return docs.length
}
```

### Performance Considerations

```javascript
// 1. Use indexes for delete filters
db.logs.createIndex({ timestamp: 1 })
db.logs.deleteMany({ timestamp: { $lt: cutoffDate } })

// 2. Batch large deletes
// Instead of:
db.logs.deleteMany({ level: "debug" })  // Might be millions

// Do:
let deleted
do {
  deleted = db.logs.deleteMany(
    { level: "debug" },
    { limit: 10000 }  // Note: limit not supported in deleteMany
  ).deletedCount
} while (deleted > 0)

// 3. Consider using TTL for automatic cleanup
// Instead of scheduled delete jobs

// 4. Drop collection if deleting most documents
const total = db.collection.countDocuments()
const toDelete = db.collection.countDocuments(filter)
if (toDelete > total * 0.8) {
  // Might be faster to keep docs and rebuild
}
```

---

## Summary

### Delete Methods Comparison

| Method | Returns | Use Case |
|--------|---------|----------|
| `deleteOne()` | Count | Remove single document |
| `deleteMany()` | Count | Remove multiple documents |
| `findOneAndDelete()` | Document | Delete and return |
| `drop()` | Boolean | Remove entire collection |

### Key Concepts

1. **deleteOne()** removes first matching document
2. **deleteMany({})** empties collection but keeps structure
3. **drop()** removes collection entirely
4. **Soft delete** preserves data for recovery
5. **TTL indexes** automate deletion based on time

### What's Next?

In the next chapter, we'll explore Bulk Write Operations in more detail.

---

## Practice Questions

1. What's the difference between deleteMany({}) and drop()?
2. When should you use soft delete vs hard delete?
3. How do TTL indexes work and when should you use them?
4. What's the benefit of findOneAndDelete() over deleteOne()?
5. How would you safely delete millions of documents?
6. What happens if a TTL index field is not a date?
7. How can you implement cascading deletes in MongoDB?
8. What are the performance implications of delete operations?

---

## Hands-On Exercises

### Exercise 1: Basic Delete Operations

```javascript
// Setup
db.testDelete.insertMany([
  { item: "journal", qty: 25, status: "A" },
  { item: "notebook", qty: 50, status: "A" },
  { item: "paper", qty: 100, status: "D" },
  { item: "planner", qty: 75, status: "D" },
  { item: "postcard", qty: 45, status: "A" }
])

// 1. Delete one document with status "D"
db.testDelete.deleteOne({ status: "D" })

// 2. Delete all documents with qty > 50
db.testDelete.deleteMany({ qty: { $gt: 50 } })

// 3. Delete and return the document with item "journal"
db.testDelete.findOneAndDelete({ item: "journal" })
```

### Exercise 2: Soft Delete Implementation

```javascript
// Implement soft delete for a users collection
db.users.insertMany([
  { name: "Alice", email: "alice@example.com", role: "admin" },
  { name: "Bob", email: "bob@example.com", role: "user" },
  { name: "Charlie", email: "charlie@example.com", role: "user" }
])

// 1. Implement softDelete function
function softDelete(userId) {
  return db.users.updateOne(
    { _id: userId },
    {
      $set: {
        isDeleted: true,
        deletedAt: new Date()
      }
    }
  )
}

// 2. Implement restore function
function restoreUser(userId) {
  return db.users.updateOne(
    { _id: userId },
    { $unset: { isDeleted: "", deletedAt: "" } }
  )
}

// 3. Create view for active users
db.createView("activeUsers", "users", [
  { $match: { isDeleted: { $ne: true } } }
])

// 4. Test the functions
const bob = db.users.findOne({ name: "Bob" })
softDelete(bob._id)
db.activeUsers.find()  // Bob not visible
restoreUser(bob._id)
db.activeUsers.find()  // Bob visible again
```

### Exercise 3: TTL Index

```javascript
// Create a sessions collection with TTL
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 60 }  // 1 minute for testing
)

// Insert some sessions
db.sessions.insertMany([
  { userId: "user1", token: "abc", createdAt: new Date() },
  { userId: "user2", token: "def", createdAt: new Date(Date.now() - 120000) }  // 2 minutes ago
])

// Check documents
db.sessions.find()

// Wait 60+ seconds and check again
// The second document should be auto-deleted
```

### Exercise 4: Bulk Delete

```javascript
// Setup test data
for (let i = 0; i < 100; i++) {
  db.bulkTest.insertOne({
    index: i,
    category: i % 3 === 0 ? "A" : (i % 3 === 1 ? "B" : "C"),
    value: Math.random() * 100
  })
}

// Bulk delete operations
db.bulkTest.bulkWrite([
  { deleteOne: { filter: { index: 0 } } },
  { deleteMany: { filter: { category: "A" } } },
  { deleteOne: { filter: { value: { $lt: 10 } } } }
])

// Check remaining
db.bulkTest.countDocuments()
```

---

[← Previous: Update Operations](08-update-operations.md) | [Next: Bulk Write Operations →](10-bulk-write-operations.md)
