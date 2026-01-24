# Chapter 5: Databases and Collections

## Table of Contents
- [Database Concepts](#database-concepts)
- [Creating and Managing Databases](#creating-and-managing-databases)
- [Collection Fundamentals](#collection-fundamentals)
- [Collection Types](#collection-types)
- [Collection Options and Settings](#collection-options-and-settings)
- [Namespaces](#namespaces)
- [System Collections](#system-collections)
- [Best Practices](#best-practices)
- [Summary](#summary)

---

## Database Concepts

### What is a MongoDB Database?

A database in MongoDB is a container for collections. Each database has its own set of files on the file system and maintains separate namespace, permissions, and configuration.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      MongoDB Instance                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database: ecommerce                                         │   │
│  │  ├── Collection: products                                   │   │
│  │  ├── Collection: orders                                     │   │
│  │  ├── Collection: customers                                  │   │
│  │  └── Collection: reviews                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database: analytics                                         │   │
│  │  ├── Collection: events                                     │   │
│  │  ├── Collection: sessions                                   │   │
│  │  └── Collection: metrics                                    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database: admin (System)                                    │   │
│  │  Database: local (System)                                    │   │
│  │  Database: config (System - Sharded Clusters)                │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Database Characteristics

| Characteristic | Description |
|----------------|-------------|
| **Namespace** | Isolated namespace for collections |
| **Storage** | Separate data files per database |
| **Authentication** | Database-level user permissions |
| **Replication** | All databases replicated together |
| **Profiling** | Per-database profiling settings |

---

## Creating and Managing Databases

### Creating Databases

```javascript
// Databases are created implicitly when first used
// Simply switch to the database and insert data

// Switch to database (creates if doesn't exist)
use myNewDatabase

// Database exists only after first write
db.myCollection.insertOne({ name: "first document" })

// Verify database exists
show dbs
```

### Listing Databases

```javascript
// Show all databases
show dbs

// Or using command
db.adminCommand({ listDatabases: 1 })

// Output:
{
  "databases": [
    { "name": "admin", "sizeOnDisk": 40960, "empty": false },
    { "name": "config", "sizeOnDisk": 110592, "empty": false },
    { "name": "ecommerce", "sizeOnDisk": 73728, "empty": false },
    { "name": "local", "sizeOnDisk": 73728, "empty": false }
  ],
  "totalSize": 299008,
  "ok": 1
}

// Filter databases by name pattern
db.adminCommand({
  listDatabases: 1,
  nameOnly: true,
  filter: { name: /^app/ }
})

// List databases with size info
db.adminCommand({
  listDatabases: 1,
  filter: { sizeOnDisk: { $gt: 100000 } }
})
```

### Database Information

```javascript
// Get current database name
db.getName()  // "myDatabase"

// or simply
db

// Get database statistics
db.stats()

// Output:
{
  "db": "ecommerce",
  "collections": 5,
  "views": 1,
  "objects": 10000,
  "avgObjSize": 256,
  "dataSize": 2560000,
  "storageSize": 1048576,
  "indexes": 10,
  "indexSize": 524288,
  "totalSize": 1572864,
  "scaleFactor": 1,
  "ok": 1
}

// Scale sizes (KB, MB, GB)
db.stats(1024)      // KB
db.stats(1048576)   // MB
```

### Switching Databases

```javascript
// Switch to existing or new database
use ecommerce

// Check current database
db

// Run command on different database
db.getSiblingDB("admin").runCommand({ ping: 1 })

// Or
use admin
db.runCommand({ ping: 1 })
```

### Dropping Databases

```javascript
// Drop current database
db.dropDatabase()

// Output:
{ "ok": 1, "dropped": "myDatabase" }

// Note: This permanently deletes all collections and data!
// Always confirm before dropping in production

// Drop specific database
use databaseToDelete
db.dropDatabase()
```

### Database Naming Rules

```javascript
// Valid database names
// - Case-sensitive
// - Maximum 64 characters
// - Cannot contain: /\. "$*<>:|?
// - Cannot be empty string

// Valid examples:
use myDatabase
use my_database
use myDatabase123
use MyDatabase  // Different from mydatabase

// Invalid examples (will cause errors):
// use my.database   // Contains dot
// use my/database   // Contains slash
// use my database   // Contains space
// use $database     // Starts with $
```

---

## Collection Fundamentals

### What is a Collection?

A collection is a grouping of MongoDB documents, equivalent to a table in relational databases but without enforced schema.

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Collection: products                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Document 1:                                                        │
│  { "_id": 1, "name": "Laptop", "price": 999, "category": "Electronics" }│
│                                                                     │
│  Document 2:                                                        │
│  { "_id": 2, "name": "Book", "price": 29, "author": "John Doe" }   │
│                                                                     │
│  Document 3:                                                        │
│  { "_id": 3, "name": "Shirt", "price": 49, "size": "L", "color": "Blue" }│
│                                                                     │
│  Note: Documents have different fields - schema is flexible!        │
│                                                                     │
│  Indexes:                                                           │
│  ├── _id (default)                                                 │
│  ├── name_1                                                        │
│  └── category_1_price_1                                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Creating Collections

```javascript
// Implicit creation (on first insert)
db.newCollection.insertOne({ field: "value" })

// Explicit creation
db.createCollection("logs")

// Create with options
db.createCollection("events", {
  capped: true,
  size: 10485760,    // 10 MB
  max: 10000         // Maximum documents
})

// Create with validation
db.createCollection("users", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["email", "name"],
      properties: {
        email: {
          bsonType: "string",
          pattern: "^.+@.+$",
          description: "must be a valid email"
        },
        name: {
          bsonType: "string",
          minLength: 1
        }
      }
    }
  }
})

// Create with storage engine options
db.createCollection("highPerformance", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd"
    }
  }
})
```

### Listing Collections

```javascript
// Show all collections
show collections

// Or
db.getCollectionNames()

// Detailed collection info
db.getCollectionInfos()

// Filter collections
db.getCollectionInfos({ name: /^user/ })

// Using command
db.runCommand({ listCollections: 1 })

// With filter
db.runCommand({
  listCollections: 1,
  filter: { type: "collection" }  // Exclude views
})
```

### Collection Statistics

```javascript
// Get collection stats
db.products.stats()

// Output:
{
  "ns": "ecommerce.products",
  "count": 10000,
  "size": 2560000,
  "avgObjSize": 256,
  "storageSize": 1048576,
  "capped": false,
  "nindexes": 3,
  "totalIndexSize": 262144,
  "indexSizes": {
    "_id_": 102400,
    "name_1": 81920,
    "category_1": 77824
  }
}

// Human-readable sizes
db.products.stats(1024)  // KB

// Specific metrics
db.products.count()           // Document count
db.products.dataSize()        // Data size in bytes
db.products.storageSize()     // Storage size
db.products.totalIndexSize()  // Total index size
```

### Renaming Collections

```javascript
// Rename collection
db.oldName.renameCollection("newName")

// Rename across databases (requires admin privileges)
db.adminCommand({
  renameCollection: "sourceDb.sourceCollection",
  to: "targetDb.targetCollection"
})

// Drop target if exists
db.adminCommand({
  renameCollection: "sourceDb.sourceCollection",
  to: "targetDb.targetCollection",
  dropTarget: true
})
```

### Dropping Collections

```javascript
// Drop a collection
db.collectionName.drop()

// Returns true if successful, false if collection doesn't exist

// Check if collection exists before dropping
if (db.getCollectionNames().includes("collectionName")) {
  db.collectionName.drop()
}
```

### Collection Naming Rules

```javascript
// Valid collection names:
// - Cannot be empty string
// - Cannot contain null character
// - Cannot start with "system." (reserved)
// - Cannot contain "$" (reserved for system use)
// - Maximum 255 bytes

// Valid examples:
db.users.insertOne({})
db.user_profiles.insertOne({})
db.userProfiles.insertOne({})
db.users2024.insertOne({})

// Invalid examples:
// db.system.myCollection  // Starts with system.
// db.my$collection        // Contains $
// db[""]                  // Empty string
```

---

## Collection Types

### Standard Collections

```javascript
// Standard collections - most common type
db.createCollection("products")

// Characteristics:
// - Dynamic schema
// - No size limits (other than disk)
// - Support all operations
// - Can be sharded
// - Can have indexes
```

### Capped Collections

```javascript
// Capped collections - fixed-size with FIFO behavior
db.createCollection("logs", {
  capped: true,
  size: 10485760,    // 10 MB maximum size (required)
  max: 5000          // Optional: maximum document count
})

// Characteristics:
// - Fixed size (bytes)
// - Optional document limit
// - FIFO (First In, First Out) - oldest docs removed first
// - High-performance inserts
// - Cannot be sharded
// - Cannot delete individual documents
// - Documents cannot grow beyond original size

// Check if collection is capped
db.logs.isCapped()  // true

// Convert standard collection to capped
db.runCommand({
  convertToCapped: "existingCollection",
  size: 10485760
})
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Capped Collection Behavior                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Size Limit: 10 MB                                                  │
│                                                                     │
│  Insert Order:  [Doc1] → [Doc2] → [Doc3] → [Doc4] → [Doc5]         │
│                                                                     │
│  When full:     [Doc6] replaces [Doc1]                             │
│                 [Doc7] replaces [Doc2]                             │
│                 ...and so on (circular buffer)                      │
│                                                                     │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  [Doc4] │ [Doc5] │ [Doc6] │ [Doc7] │ [Doc8] │ [Doc9] │ ...  │  │
│  │   ←←←←←←← Oldest                      Newest →→→→→→→        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  Use Cases:                                                         │
│  • Logging / Audit trails                                          │
│  • Caching recent data                                             │
│  • Real-time analytics buffers                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Time Series Collections

```javascript
// Time series collections - optimized for time-based data
db.createCollection("sensorReadings", {
  timeseries: {
    timeField: "timestamp",      // Required: field containing time
    metaField: "sensorId",       // Optional: metadata field
    granularity: "seconds"       // Optional: seconds, minutes, hours
  },
  expireAfterSeconds: 86400      // Optional: TTL (1 day)
})

// Insert time series data
db.sensorReadings.insertMany([
  {
    sensorId: "sensor001",
    timestamp: new Date(),
    temperature: 23.5,
    humidity: 65
  },
  {
    sensorId: "sensor002",
    timestamp: new Date(),
    temperature: 24.1,
    humidity: 62
  }
])

// Time series collection options
db.createCollection("metrics", {
  timeseries: {
    timeField: "ts",
    metaField: "metadata",
    granularity: "minutes",
    bucketMaxSpanSeconds: 3600,    // MongoDB 6.3+
    bucketRoundingSeconds: 60      // MongoDB 6.3+
  }
})
```

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Time Series Collection                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Automatic Bucketing:                                               │
│                                                                     │
│  Original Documents:                                                │
│  { sensorId: "s1", ts: T1, temp: 23.5 }                            │
│  { sensorId: "s1", ts: T2, temp: 23.6 }                            │
│  { sensorId: "s1", ts: T3, temp: 23.4 }                            │
│                                                                     │
│  Internal Storage (Bucketed):                                       │
│  {                                                                  │
│    meta: { sensorId: "s1" },                                       │
│    control: { min: T1, max: T3 },                                  │
│    data: {                                                         │
│      ts: [T1, T2, T3],                                            │
│      temp: [23.5, 23.6, 23.4]                                     │
│    }                                                                │
│  }                                                                  │
│                                                                     │
│  Benefits:                                                          │
│  • Compressed storage                                               │
│  • Faster time-range queries                                       │
│  • Efficient aggregations                                          │
│  • Automatic data expiration                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Views

```javascript
// Views are virtual collections based on aggregation pipelines
db.createView(
  "activeUsers",           // View name
  "users",                 // Source collection
  [                        // Pipeline
    { $match: { status: "active" } },
    { $project: { password: 0 } }
  ]
)

// Query view like a regular collection
db.activeUsers.find({ role: "admin" })

// View with complex pipeline
db.createView("orderSummary", "orders", [
  {
    $group: {
      _id: "$customerId",
      totalOrders: { $sum: 1 },
      totalAmount: { $sum: "$amount" }
    }
  },
  {
    $lookup: {
      from: "customers",
      localField: "_id",
      foreignField: "_id",
      as: "customer"
    }
  },
  { $unwind: "$customer" },
  {
    $project: {
      customerName: "$customer.name",
      totalOrders: 1,
      totalAmount: 1
    }
  }
])

// Modify view
db.runCommand({
  collMod: "activeUsers",
  viewOn: "users",
  pipeline: [
    { $match: { status: "active", verified: true } }
  ]
})

// Drop view
db.activeUsers.drop()
```

```javascript
// View properties:
// - Read-only (cannot insert/update/delete)
// - No indexes on views directly
// - Uses underlying collection's indexes
// - Can be created on sharded collections
// - Pipeline runs on each query

// List views
db.getCollectionInfos({ type: "view" })
```

---

## Collection Options and Settings

### Collation (Text Sorting/Comparison)

```javascript
// Create collection with collation
db.createCollection("names", {
  collation: {
    locale: "en",           // Language
    strength: 2,            // Case insensitive
    caseLevel: false,
    caseFirst: "off",
    numericOrdering: true   // "10" > "9"
  }
})

// Insert and query with collation
db.names.insertMany([
  { name: "Apple" },
  { name: "apple" },
  { name: "APPLE" }
])

// Case-insensitive find (uses collection collation)
db.names.find({ name: "apple" })  // Returns all three

// Override collation in query
db.names.find({ name: "apple" }).collation({ locale: "en", strength: 3 })
```

### Collation Strength Levels

| Strength | Comparison |
|----------|------------|
| 1 | Base characters only (a = á = A) |
| 2 | Base + accents (a ≠ á, a = A) |
| 3 | Base + accents + case (a ≠ á ≠ A) |
| 4 | Base + accents + case + punctuation |
| 5 | Identical |

### Storage Engine Options

```javascript
// WiredTiger configuration
db.createCollection("optimized", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd,leaf_page_max=32KB"
    }
  }
})

// Available compressors:
// - snappy (default) - fast compression
// - zlib - higher compression ratio
// - zstd - balance of speed and compression
// - none - no compression
```

### Validation Levels and Actions

```javascript
// Create collection with validation
db.createCollection("products", {
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price"],
      properties: {
        name: { bsonType: "string" },
        price: { bsonType: "number", minimum: 0 }
      }
    }
  },
  validationLevel: "moderate",   // strict, moderate, off
  validationAction: "warn"       // error, warn
})

// Validation levels:
// strict - validate all inserts and updates
// moderate - validate inserts and updates to valid documents
// off - no validation

// Validation actions:
// error - reject invalid documents
// warn - allow but log warning
```

### Modify Collection Options

```javascript
// Modify collection settings
db.runCommand({
  collMod: "products",
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["name", "price", "sku"],
      properties: {
        sku: { bsonType: "string" }
      }
    }
  },
  validationLevel: "strict",
  validationAction: "error"
})

// Modify index options
db.runCommand({
  collMod: "products",
  index: {
    keyPattern: { name: 1 },
    hidden: true  // Hide index from query planner
  }
})
```

---

## Namespaces

### Understanding Namespaces

```javascript
// Namespace = database.collection
// Example: ecommerce.products

// Full namespace length limit: 255 bytes

// Namespace usage:
// - Identify collections uniquely
// - Used in logging and monitoring
// - Referenced in commands and drivers
```

### System Namespaces

```javascript
// System collections follow pattern: database.system.*

// admin database system collections
admin.system.users      // User accounts
admin.system.roles      // Custom roles
admin.system.version    // Schema version

// local database (replica sets)
local.oplog.rs          // Replication oplog
local.startup_log       // Server startup history
local.system.replset    // Replica set config

// config database (sharded clusters)
config.shards           // Shard information
config.chunks           // Chunk metadata
config.databases        // Database sharding info
```

---

## System Collections

### Admin Database Collections

```javascript
// View system users
use admin
db.system.users.find()

// View system roles
db.system.roles.find()

// These collections are managed through commands:
db.createUser({...})
db.createRole({...})
```

### Local Database Collections

```javascript
use local

// Oplog (replica sets only)
db.oplog.rs.find().sort({ ts: -1 }).limit(5)

// Startup log
db.startup_log.find().sort({ startTime: -1 }).limit(1)

// Replica set configuration
db.system.replset.findOne()
```

### Config Database (Sharded Clusters)

```javascript
use config

// List shards
db.shards.find()

// Chunk distribution
db.chunks.find({ ns: "mydb.mycollection" })

// Database configs
db.databases.find()

// Collection sharding info
db.collections.find()
```

---

## Best Practices

### Database Organization

```javascript
// ✅ DO: Logical separation of concerns
// Database per application or bounded context
ecommerce_db       // E-commerce application
analytics_db       // Analytics data
auth_db            // Authentication/authorization

// ✅ DO: Environment separation
myapp_dev          // Development
myapp_staging      // Staging
myapp_prod         // Production

// ❌ DON'T: Mix unrelated data in one database
// all_data_db  // Contains everything
```

### Collection Naming Conventions

```javascript
// ✅ DO: Use consistent naming
// Plural nouns
db.users
db.products
db.orders

// Snake_case or camelCase (be consistent)
db.order_items
db.orderItems

// ✅ DO: Use prefixes for related collections
db.log_errors
db.log_access
db.log_audit

// ❌ DON'T: Use inconsistent naming
// db.User, db.products, db.ORDER
```

### Collection Design Guidelines

```javascript
// ✅ DO: Design collections around query patterns
// If you frequently query orders by customer:
{
  _id: "order123",
  customerId: "cust456",
  customerName: "John Doe",  // Denormalized for queries
  items: [...]
}

// ✅ DO: Use separate collections for large arrays
// Instead of embedding 10,000 comments in a blog post:
// blog_posts collection
{ _id: "post1", title: "My Post", commentCount: 10000 }

// comments collection (references blog post)
{ _id: "c1", postId: "post1", content: "Great!" }

// ✅ DO: Consider collection size and growth
// Use capped collections for logs
// Use TTL indexes for session data
// Use time series collections for metrics
```

### Monitoring Collections

```javascript
// Regular health checks
db.collection.stats()
db.collection.validate()

// Monitor collection size
db.collection.aggregate([
  {
    $group: {
      _id: null,
      count: { $sum: 1 },
      avgSize: { $avg: { $bsonSize: "$$ROOT" } }
    }
  }
])

// Check for large documents
db.collection.aggregate([
  { $project: { size: { $bsonSize: "$$ROOT" } } },
  { $match: { size: { $gt: 1000000 } } },  // > 1MB
  { $sort: { size: -1 } },
  { $limit: 10 }
])
```

---

## Summary

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Database** | Container for collections with isolated namespace |
| **Collection** | Grouping of documents (schema-flexible) |
| **Capped Collection** | Fixed-size collection with FIFO behavior |
| **Time Series** | Optimized for time-based data |
| **View** | Virtual collection from aggregation pipeline |
| **Namespace** | Full path: database.collection |

### Collection Types Comparison

| Type | Use Case | Features |
|------|----------|----------|
| Standard | General purpose | Full functionality |
| Capped | Logs, buffers | Fixed size, fast writes |
| Time Series | Metrics, IoT | Optimized storage, TTL |
| View | Reporting, security | Read-only, computed |

### What's Next?

In the next chapter, we'll dive into Insert Operations, learning how to add documents to collections with various options and techniques.

---

## Practice Questions

1. How do databases and collections differ from relational database concepts?
2. What are the naming restrictions for databases and collections?
3. When would you use a capped collection vs a standard collection?
4. How do time series collections optimize storage and queries?
5. What is the purpose of views in MongoDB?
6. How do validation levels and actions affect document operations?
7. What are system collections and where are they located?
8. How do namespaces work in MongoDB?

---

## Hands-On Exercises

### Exercise 1: Database and Collection Management

```javascript
// Create a new database and collections
use exerciseDB

// Create standard collection
db.createCollection("users")

// Create capped collection
db.createCollection("logs", {
  capped: true,
  size: 1048576,
  max: 1000
})

// Verify collections
show collections
db.getCollectionInfos()

// Check collection stats
db.users.stats()
db.logs.stats()
```

### Exercise 2: Time Series Collection

```javascript
// Create time series collection
db.createCollection("metrics", {
  timeseries: {
    timeField: "timestamp",
    metaField: "device",
    granularity: "seconds"
  },
  expireAfterSeconds: 3600
})

// Insert sample data
for (let i = 0; i < 100; i++) {
  db.metrics.insertOne({
    device: { id: "dev001", type: "sensor" },
    timestamp: new Date(Date.now() - i * 1000),
    value: Math.random() * 100
  })
}

// Query time series data
db.metrics.aggregate([
  {
    $match: {
      timestamp: {
        $gte: new Date(Date.now() - 60000)
      }
    }
  },
  {
    $group: {
      _id: "$device.id",
      avgValue: { $avg: "$value" },
      count: { $sum: 1 }
    }
  }
])
```

### Exercise 3: Views

```javascript
// Create sample data
db.employees.insertMany([
  { name: "Alice", department: "Engineering", salary: 80000, active: true },
  { name: "Bob", department: "Sales", salary: 60000, active: true },
  { name: "Charlie", department: "Engineering", salary: 90000, active: false }
])

// Create view for active employees
db.createView("activeEmployees", "employees", [
  { $match: { active: true } },
  { $project: { salary: 0 } }  // Hide salary
])

// Create department summary view
db.createView("departmentSummary", "employees", [
  { $match: { active: true } },
  {
    $group: {
      _id: "$department",
      count: { $sum: 1 },
      avgSalary: { $avg: "$salary" }
    }
  }
])

// Query views
db.activeEmployees.find()
db.departmentSummary.find()
```

---

[← Previous: Documents and BSON](04-documents-and-bson.md) | [Next: Insert Operations →](06-insert-operations.md)
