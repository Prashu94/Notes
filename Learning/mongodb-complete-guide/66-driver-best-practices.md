# Chapter 66: Driver Best Practices

## Table of Contents
- [Driver Overview](#driver-overview)
- [Connection Management](#connection-management)
- [Query Patterns](#query-patterns)
- [Write Operations](#write-operations)
- [Error Handling Patterns](#error-handling-patterns)
- [Performance Optimization](#performance-optimization)
- [Summary](#summary)

---

## Driver Overview

### Official MongoDB Drivers

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Driver Ecosystem                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Official Drivers (maintained by MongoDB):                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  • Node.js (mongodb)         • Python (pymongo)             │   │
│  │  • Java (mongodb-driver)     • C# (.NET Driver)             │   │
│  │  • Go (mongo-go-driver)      • Ruby (mongo-ruby-driver)     │   │
│  │  • PHP (mongodb)             • Rust (mongodb)               │   │
│  │  • Swift (mongodb)           • Kotlin (mongodb-driver)      │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Driver Components:                                                │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Application                                                 │   │
│  │       │                                                      │   │
│  │       ▼                                                      │   │
│  │  ┌─────────────┐                                            │   │
│  │  │   Driver    │  ◄── BSON encoding/decoding                │   │
│  │  │             │  ◄── Connection pooling                    │   │
│  │  │             │  ◄── Server selection                      │   │
│  │  │             │  ◄── Retryable operations                  │   │
│  │  └─────────────┘                                            │   │
│  │       │                                                      │   │
│  │       ▼                                                      │   │
│  │  MongoDB Server                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Driver Installation

```bash
# Node.js
npm install mongodb

# Python
pip install pymongo

# Java (Maven)
# <dependency>
#   <groupId>org.mongodb</groupId>
#   <artifactId>mongodb-driver-sync</artifactId>
#   <version>4.11.0</version>
# </dependency>

# Go
go get go.mongodb.org/mongo-driver/mongo

# C# (.NET)
dotnet add package MongoDB.Driver
```

---

## Connection Management

### Singleton Pattern (Recommended)

```javascript
// Node.js - Singleton connection
// db.js
const { MongoClient } = require('mongodb')

class Database {
  constructor() {
    this.client = null
    this.db = null
  }
  
  async connect(uri, dbName, options = {}) {
    if (this.client) {
      return this.db
    }
    
    const defaultOptions = {
      maxPoolSize: 50,
      minPoolSize: 5,
      maxIdleTimeMS: 30000,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
      retryWrites: true,
      retryReads: true,
      w: 'majority'
    }
    
    this.client = new MongoClient(uri, { ...defaultOptions, ...options })
    await this.client.connect()
    
    this.db = this.client.db(dbName)
    
    // Handle process termination
    process.on('SIGINT', () => this.close())
    process.on('SIGTERM', () => this.close())
    
    return this.db
  }
  
  getDb() {
    if (!this.db) {
      throw new Error('Database not connected. Call connect() first.')
    }
    return this.db
  }
  
  getClient() {
    return this.client
  }
  
  async close() {
    if (this.client) {
      await this.client.close()
      this.client = null
      this.db = null
      console.log('Database connection closed')
    }
  }
}

// Export singleton instance
module.exports = new Database()
```

```javascript
// Usage in application
const db = require('./db')

async function main() {
  await db.connect(process.env.MONGODB_URI, 'myapp')
  
  const users = db.getDb().collection('users')
  const result = await users.find({ active: true }).toArray()
  
  console.log(result)
}

main().catch(console.error)
```

### Python Singleton Pattern

```python
# database.py
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import atexit

class Database:
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self, uri, db_name, **options):
        if self._client is not None:
            return self._db
        
        default_options = {
            'maxPoolSize': 50,
            'minPoolSize': 5,
            'maxIdleTimeMS': 30000,
            'serverSelectionTimeoutMS': 5000,
            'socketTimeoutMS': 45000,
            'retryWrites': True,
            'retryReads': True,
            'w': 'majority'
        }
        
        merged_options = {**default_options, **options}
        
        self._client = MongoClient(uri, **merged_options)
        
        # Verify connection
        try:
            self._client.admin.command('ping')
        except ConnectionFailure:
            raise Exception("Failed to connect to MongoDB")
        
        self._db = self._client[db_name]
        
        # Register cleanup
        atexit.register(self.close)
        
        return self._db
    
    @property
    def db(self):
        if self._db is None:
            raise Exception("Database not connected. Call connect() first.")
        return self._db
    
    @property
    def client(self):
        return self._client
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            self._db = None

# Singleton instance
database = Database()

# Usage
# from database import database
# database.connect(os.environ['MONGODB_URI'], 'myapp')
# users = database.db.users.find({'active': True})
```

### Connection String Best Practices

```javascript
// Connection string construction
const buildConnectionString = (config) => {
  const {
    username,
    password,
    hosts,  // ['host1:27017', 'host2:27017']
    database,
    replicaSet,
    authSource = 'admin',
    ssl = true
  } = config
  
  const credentials = username && password 
    ? `${encodeURIComponent(username)}:${encodeURIComponent(password)}@`
    : ''
  
  const hostList = hosts.join(',')
  
  const params = new URLSearchParams()
  if (replicaSet) params.append('replicaSet', replicaSet)
  if (authSource) params.append('authSource', authSource)
  if (ssl) params.append('tls', 'true')
  params.append('retryWrites', 'true')
  params.append('w', 'majority')
  
  return `mongodb+srv://${credentials}${hostList}/${database}?${params.toString()}`
}

// Environment-based configuration
const getMongoConfig = () => {
  const env = process.env.NODE_ENV || 'development'
  
  const configs = {
    development: {
      uri: 'mongodb://localhost:27017',
      dbName: 'myapp_dev',
      options: { maxPoolSize: 10 }
    },
    test: {
      uri: 'mongodb://localhost:27017',
      dbName: 'myapp_test',
      options: { maxPoolSize: 5 }
    },
    production: {
      uri: process.env.MONGODB_URI,
      dbName: process.env.MONGODB_DATABASE,
      options: {
        maxPoolSize: 100,
        minPoolSize: 10,
        ssl: true,
        sslValidate: true
      }
    }
  }
  
  return configs[env]
}
```

---

## Query Patterns

### Efficient Query Construction

```javascript
// Use projection to limit returned fields
// Bad - returns entire document
const users = await db.collection('users').find({ status: 'active' }).toArray()

// Good - only returns needed fields
const users = await db.collection('users')
  .find(
    { status: 'active' },
    { projection: { name: 1, email: 1 } }
  )
  .toArray()

// Use limit for pagination
const pageSize = 20
const page = 1
const skip = (page - 1) * pageSize

const users = await db.collection('users')
  .find({ status: 'active' })
  .sort({ createdAt: -1 })
  .skip(skip)
  .limit(pageSize)
  .toArray()

// Prefer cursor-based pagination for large datasets
const lastId = ObjectId('...')  // Last _id from previous page

const users = await db.collection('users')
  .find({ 
    status: 'active',
    _id: { $gt: lastId }
  })
  .sort({ _id: 1 })
  .limit(pageSize)
  .toArray()
```

### Query Builder Pattern

```javascript
// Query builder for complex queries
class QueryBuilder {
  constructor(collection) {
    this.collection = collection
    this.filter = {}
    this.options = {}
    this.pipeline = null
  }
  
  where(field, operator, value) {
    if (arguments.length === 2) {
      // Simple equality
      this.filter[field] = operator
    } else {
      // With operator
      this.filter[field] = { [`$${operator}`]: value }
    }
    return this
  }
  
  whereIn(field, values) {
    this.filter[field] = { $in: values }
    return this
  }
  
  whereBetween(field, min, max) {
    this.filter[field] = { $gte: min, $lte: max }
    return this
  }
  
  search(field, text) {
    this.filter[field] = { $regex: text, $options: 'i' }
    return this
  }
  
  select(...fields) {
    this.options.projection = {}
    fields.forEach(f => this.options.projection[f] = 1)
    return this
  }
  
  exclude(...fields) {
    this.options.projection = this.options.projection || {}
    fields.forEach(f => this.options.projection[f] = 0)
    return this
  }
  
  sort(field, direction = 1) {
    this.options.sort = this.options.sort || {}
    this.options.sort[field] = direction
    return this
  }
  
  limit(n) {
    this.options.limit = n
    return this
  }
  
  skip(n) {
    this.options.skip = n
    return this
  }
  
  async get() {
    return await this.collection.find(this.filter, this.options).toArray()
  }
  
  async first() {
    return await this.collection.findOne(this.filter, this.options)
  }
  
  async count() {
    return await this.collection.countDocuments(this.filter)
  }
  
  async exists() {
    const count = await this.collection.countDocuments(this.filter, { limit: 1 })
    return count > 0
  }
  
  async paginate(page = 1, perPage = 20) {
    const skip = (page - 1) * perPage
    const [data, total] = await Promise.all([
      this.collection.find(this.filter, { ...this.options, skip, limit: perPage }).toArray(),
      this.collection.countDocuments(this.filter)
    ])
    
    return {
      data,
      pagination: {
        page,
        perPage,
        total,
        totalPages: Math.ceil(total / perPage),
        hasMore: page * perPage < total
      }
    }
  }
}

// Usage
const query = new QueryBuilder(db.collection('products'))
  .where('status', 'active')
  .where('price', 'lte', 100)
  .whereIn('category', ['electronics', 'books'])
  .select('name', 'price', 'category')
  .sort('price', 1)
  .limit(10)

const products = await query.get()
```

### Streaming Large Results

```javascript
// Process large result sets with streams
async function processLargeCollection(db) {
  const cursor = db.collection('largeData').find({})
  
  let processed = 0
  const batchSize = 1000
  let batch = []
  
  for await (const doc of cursor) {
    batch.push(doc)
    
    if (batch.length >= batchSize) {
      await processBatch(batch)
      processed += batch.length
      console.log(`Processed ${processed} documents`)
      batch = []
    }
  }
  
  // Process remaining
  if (batch.length > 0) {
    await processBatch(batch)
    processed += batch.length
  }
  
  console.log(`Total processed: ${processed}`)
}

// Python streaming
def process_large_collection(db):
    cursor = db.large_data.find({}, batch_size=1000)
    
    processed = 0
    batch = []
    
    for doc in cursor:
        batch.append(doc)
        
        if len(batch) >= 1000:
            process_batch(batch)
            processed += len(batch)
            print(f"Processed {processed} documents")
            batch = []
    
    if batch:
        process_batch(batch)
        processed += len(batch)
    
    print(f"Total processed: {processed}")
```

---

## Write Operations

### Bulk Write Operations

```javascript
// Efficient bulk writes
async function bulkUpsert(db, collectionName, documents, keyField = '_id') {
  const collection = db.collection(collectionName)
  
  const operations = documents.map(doc => ({
    updateOne: {
      filter: { [keyField]: doc[keyField] },
      update: { $set: doc },
      upsert: true
    }
  }))
  
  const result = await collection.bulkWrite(operations, {
    ordered: false  // Continue on error
  })
  
  return {
    inserted: result.upsertedCount,
    modified: result.modifiedCount,
    matched: result.matchedCount
  }
}

// Batch insert with retry
async function batchInsert(db, collectionName, documents, batchSize = 1000) {
  const collection = db.collection(collectionName)
  const results = { inserted: 0, errors: [] }
  
  for (let i = 0; i < documents.length; i += batchSize) {
    const batch = documents.slice(i, i + batchSize)
    
    try {
      const result = await collection.insertMany(batch, { ordered: false })
      results.inserted += result.insertedCount
    } catch (error) {
      if (error.code === 11000) {
        // Duplicate key - count successful inserts
        results.inserted += error.result?.nInserted || 0
        results.errors.push({
          batch: Math.floor(i / batchSize),
          error: 'Duplicate keys found'
        })
      } else {
        throw error
      }
    }
    
    console.log(`Inserted ${results.inserted} of ${documents.length}`)
  }
  
  return results
}
```

### Write Concern Configuration

```javascript
// Write concern options
const writeConcerns = {
  // Fastest - no acknowledgment (fire and forget)
  unacknowledged: { w: 0 },
  
  // Default - acknowledged by primary
  acknowledged: { w: 1 },
  
  // Journaled - written to journal
  journaled: { w: 1, j: true },
  
  // Majority - replicated to majority
  majority: { w: 'majority' },
  
  // Majority with journal
  majorityJournaled: { w: 'majority', j: true },
  
  // Custom - specific number of nodes
  custom: { w: 3 },
  
  // With timeout
  withTimeout: { w: 'majority', wtimeout: 5000 }
}

// Apply write concern
await db.collection('orders').insertOne(
  { product: 'Widget', quantity: 10 },
  { writeConcern: writeConcerns.majorityJournaled }
)

// Collection-level write concern
const ordersCollection = db.collection('orders', {
  writeConcern: { w: 'majority', j: true }
})
```

### Optimistic Concurrency

```javascript
// Optimistic locking with version field
async function updateWithVersion(db, collectionName, id, updates, currentVersion) {
  const result = await db.collection(collectionName).updateOne(
    { 
      _id: id, 
      version: currentVersion 
    },
    { 
      $set: updates,
      $inc: { version: 1 }
    }
  )
  
  if (result.matchedCount === 0) {
    throw new Error('Document was modified by another process')
  }
  
  return result
}

// Retry on conflict
async function updateWithRetry(db, collectionName, id, updateFn, maxRetries = 3) {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    const doc = await db.collection(collectionName).findOne({ _id: id })
    
    if (!doc) {
      throw new Error('Document not found')
    }
    
    const updates = updateFn(doc)
    
    try {
      await updateWithVersion(db, collectionName, id, updates, doc.version)
      return { success: true, attempts: attempt + 1 }
    } catch (error) {
      if (error.message.includes('modified by another process')) {
        console.log(`Conflict detected, retrying (${attempt + 1}/${maxRetries})`)
        continue
      }
      throw error
    }
  }
  
  throw new Error(`Failed after ${maxRetries} attempts`)
}
```

---

## Error Handling Patterns

### Comprehensive Error Handler

```javascript
const { MongoError, MongoNetworkError, MongoServerError } = require('mongodb')

class MongoDBError extends Error {
  constructor(message, code, originalError) {
    super(message)
    this.name = 'MongoDBError'
    this.code = code
    this.originalError = originalError
  }
}

function handleMongoError(error) {
  // Network errors
  if (error instanceof MongoNetworkError) {
    return new MongoDBError(
      'Database connection failed',
      'NETWORK_ERROR',
      error
    )
  }
  
  // Server errors
  if (error instanceof MongoServerError) {
    switch (error.code) {
      case 11000:
        // Duplicate key
        const field = extractDuplicateField(error)
        return new MongoDBError(
          `Duplicate value for field: ${field}`,
          'DUPLICATE_KEY',
          error
        )
      
      case 121:
        // Document validation failure
        return new MongoDBError(
          'Document failed validation',
          'VALIDATION_ERROR',
          error
        )
      
      case 13:
        // Unauthorized
        return new MongoDBError(
          'Insufficient permissions',
          'UNAUTHORIZED',
          error
        )
      
      case 50:
        // Exceeded time limit
        return new MongoDBError(
          'Operation timed out',
          'TIMEOUT',
          error
        )
      
      default:
        return new MongoDBError(
          error.message,
          `MONGO_ERROR_${error.code}`,
          error
        )
    }
  }
  
  return error
}

function extractDuplicateField(error) {
  const match = error.message.match(/index: (\w+)/)
  return match ? match[1] : 'unknown'
}

// Wrapper for operations
async function withErrorHandling(operation) {
  try {
    return await operation()
  } catch (error) {
    throw handleMongoError(error)
  }
}

// Usage
try {
  await withErrorHandling(async () => {
    await db.collection('users').insertOne({ email: 'existing@example.com' })
  })
} catch (error) {
  if (error.code === 'DUPLICATE_KEY') {
    console.log('Email already exists')
  } else {
    throw error
  }
}
```

### Retry Pattern

```javascript
// Configurable retry logic
async function withRetry(operation, options = {}) {
  const {
    maxRetries = 3,
    initialDelay = 100,
    maxDelay = 5000,
    factor = 2,
    retryableErrors = ['NETWORK_ERROR', 'TIMEOUT']
  } = options
  
  let lastError
  let delay = initialDelay
  
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await operation()
    } catch (error) {
      lastError = handleMongoError(error)
      
      // Check if error is retryable
      if (!retryableErrors.includes(lastError.code)) {
        throw lastError
      }
      
      if (attempt === maxRetries) {
        break
      }
      
      console.log(`Attempt ${attempt} failed, retrying in ${delay}ms...`)
      await sleep(delay)
      
      delay = Math.min(delay * factor, maxDelay)
    }
  }
  
  throw lastError
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

// Usage
const result = await withRetry(
  () => db.collection('users').find({ active: true }).toArray(),
  { maxRetries: 5, initialDelay: 200 }
)
```

---

## Performance Optimization

### Index Hints

```javascript
// Force specific index usage
const results = await db.collection('products')
  .find({ category: 'electronics', price: { $lt: 500 } })
  .hint({ category: 1, price: 1 })
  .toArray()

// Explain to verify index usage
const explain = await db.collection('products')
  .find({ category: 'electronics' })
  .explain('executionStats')

console.log('Index used:', explain.queryPlanner.winningPlan.inputStage.indexName)
console.log('Documents examined:', explain.executionStats.totalDocsExamined)
```

### Read Preferences

```javascript
// Configure read preference
const { ReadPreference } = require('mongodb')

// Read from primary (default)
await collection.find({}).readPreference(ReadPreference.PRIMARY).toArray()

// Read from secondary
await collection.find({}).readPreference(ReadPreference.SECONDARY).toArray()

// Read from nearest
await collection.find({}).readPreference(ReadPreference.NEAREST).toArray()

// Primary preferred (fallback to secondary)
await collection.find({}).readPreference(ReadPreference.PRIMARY_PREFERRED).toArray()

// Secondary preferred (fallback to primary)
await collection.find({}).readPreference(ReadPreference.SECONDARY_PREFERRED).toArray()

// With tags for data locality
const readPref = new ReadPreference(ReadPreference.SECONDARY, [
  { region: 'us-east', dc: 'dc1' },
  { region: 'us-east' },
  {}  // Fallback to any secondary
])
```

### Aggregation Optimization

```javascript
// Optimize aggregation pipelines

// Bad - $match after $lookup
const badPipeline = [
  { $lookup: { from: 'orders', localField: '_id', foreignField: 'userId', as: 'orders' } },
  { $match: { status: 'active' } }  // Filters after expensive lookup
]

// Good - $match before $lookup
const goodPipeline = [
  { $match: { status: 'active' } },  // Filter first
  { $lookup: { from: 'orders', localField: '_id', foreignField: 'userId', as: 'orders' } }
]

// Use $project early to reduce document size
const optimizedPipeline = [
  { $match: { status: 'active' } },
  { $project: { _id: 1, name: 1, email: 1 } },  // Reduce document size
  { $lookup: { 
    from: 'orders', 
    localField: '_id', 
    foreignField: 'userId', 
    as: 'orders',
    pipeline: [  // Limit lookup results
      { $match: { status: 'completed' } },
      { $limit: 10 }
    ]
  }}
]

// Allow disk use for large aggregations
await db.collection('largeData').aggregate(pipeline, {
  allowDiskUse: true
}).toArray()
```

---

## Summary

### Connection Best Practices

| Practice | Benefit |
|----------|---------|
| Singleton pattern | Reuse connections |
| Connection pooling | Efficient resource use |
| Proper timeouts | Prevent hanging |
| Graceful shutdown | Clean resource cleanup |

### Query Best Practices

| Practice | Benefit |
|----------|---------|
| Use projections | Reduce data transfer |
| Cursor-based pagination | Consistent performance |
| Streaming for large data | Memory efficiency |
| Index hints when needed | Query optimization |

### Write Best Practices

| Practice | Benefit |
|----------|---------|
| Bulk operations | Reduced round trips |
| Appropriate write concern | Balance speed/safety |
| Optimistic locking | Concurrency control |
| Unordered bulk writes | Better throughput |

---

## Practice Questions

1. Why should you use the singleton pattern for MongoDB connections?
2. What is the difference between ordered and unordered bulk writes?
3. How do read preferences affect query routing in a replica set?
4. What is optimistic concurrency and when should you use it?
5. How do you handle duplicate key errors gracefully?
6. What are the trade-offs between different write concern levels?
7. How do you optimize aggregation pipelines?
8. When should you use cursor-based vs offset-based pagination?

---

## Hands-On Exercises

### Exercise 1: Repository Pattern Implementation

```javascript
// Generic repository pattern

class BaseRepository {
  constructor(db, collectionName) {
    this.collection = db.collection(collectionName)
    this.collectionName = collectionName
  }
  
  async findById(id) {
    return await this.collection.findOne({ _id: new ObjectId(id) })
  }
  
  async findOne(filter, options = {}) {
    return await this.collection.findOne(filter, options)
  }
  
  async find(filter = {}, options = {}) {
    const { sort, limit, skip, projection } = options
    
    let cursor = this.collection.find(filter)
    
    if (projection) cursor = cursor.project(projection)
    if (sort) cursor = cursor.sort(sort)
    if (skip) cursor = cursor.skip(skip)
    if (limit) cursor = cursor.limit(limit)
    
    return await cursor.toArray()
  }
  
  async paginate(filter = {}, options = {}) {
    const { page = 1, perPage = 20, sort = { _id: -1 } } = options
    const skip = (page - 1) * perPage
    
    const [data, total] = await Promise.all([
      this.collection.find(filter).sort(sort).skip(skip).limit(perPage).toArray(),
      this.collection.countDocuments(filter)
    ])
    
    return {
      data,
      meta: {
        page,
        perPage,
        total,
        totalPages: Math.ceil(total / perPage)
      }
    }
  }
  
  async create(data) {
    const doc = {
      ...data,
      createdAt: new Date(),
      updatedAt: new Date()
    }
    
    const result = await this.collection.insertOne(doc)
    return { _id: result.insertedId, ...doc }
  }
  
  async createMany(documents) {
    const docs = documents.map(doc => ({
      ...doc,
      createdAt: new Date(),
      updatedAt: new Date()
    }))
    
    const result = await this.collection.insertMany(docs)
    return result.insertedIds
  }
  
  async update(id, data) {
    const result = await this.collection.findOneAndUpdate(
      { _id: new ObjectId(id) },
      { 
        $set: { ...data, updatedAt: new Date() }
      },
      { returnDocument: 'after' }
    )
    
    return result
  }
  
  async delete(id) {
    const result = await this.collection.deleteOne({ _id: new ObjectId(id) })
    return result.deletedCount > 0
  }
  
  async softDelete(id) {
    return await this.update(id, { deletedAt: new Date() })
  }
  
  async count(filter = {}) {
    return await this.collection.countDocuments(filter)
  }
  
  async exists(filter) {
    const count = await this.collection.countDocuments(filter, { limit: 1 })
    return count > 0
  }
  
  async aggregate(pipeline, options = {}) {
    return await this.collection.aggregate(pipeline, options).toArray()
  }
}

// Specialized repository
class UserRepository extends BaseRepository {
  constructor(db) {
    super(db, 'users')
  }
  
  async findByEmail(email) {
    return await this.findOne({ email: email.toLowerCase() })
  }
  
  async findActive(options = {}) {
    return await this.find({ status: 'active', deletedAt: null }, options)
  }
  
  async search(query, options = {}) {
    const filter = {
      $or: [
        { name: { $regex: query, $options: 'i' } },
        { email: { $regex: query, $options: 'i' } }
      ],
      deletedAt: null
    }
    
    return await this.paginate(filter, options)
  }
  
  async updateLastLogin(id) {
    return await this.collection.updateOne(
      { _id: new ObjectId(id) },
      { $set: { lastLoginAt: new Date() } }
    )
  }
}

// Usage
const userRepo = new UserRepository(db)

// Create
const user = await userRepo.create({
  name: 'John Doe',
  email: 'john@example.com',
  status: 'active'
})

// Find
const found = await userRepo.findByEmail('john@example.com')

// Paginate
const page = await userRepo.paginate(
  { status: 'active' },
  { page: 1, perPage: 10, sort: { createdAt: -1 } }
)

// Search
const results = await userRepo.search('john', { page: 1, perPage: 20 })
```

### Exercise 2: Connection Health Monitor

```javascript
// MongoDB connection health monitor

class ConnectionHealthMonitor {
  constructor(client, options = {}) {
    this.client = client
    this.options = {
      checkInterval: 30000,
      pingTimeout: 5000,
      ...options
    }
    this.status = {
      connected: false,
      lastCheck: null,
      lastPingMs: null,
      errors: []
    }
    this.intervalId = null
  }
  
  async start() {
    await this.check()
    this.intervalId = setInterval(() => this.check(), this.options.checkInterval)
    console.log('Health monitor started')
  }
  
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
      this.intervalId = null
      console.log('Health monitor stopped')
    }
  }
  
  async check() {
    const startTime = Date.now()
    
    try {
      await Promise.race([
        this.client.db('admin').command({ ping: 1 }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Ping timeout')), this.options.pingTimeout)
        )
      ])
      
      this.status = {
        connected: true,
        lastCheck: new Date(),
        lastPingMs: Date.now() - startTime,
        errors: []
      }
      
    } catch (error) {
      this.status = {
        connected: false,
        lastCheck: new Date(),
        lastPingMs: null,
        errors: [...this.status.errors.slice(-9), {
          timestamp: new Date(),
          message: error.message
        }]
      }
      
      console.error(`Health check failed: ${error.message}`)
    }
    
    return this.status
  }
  
  async getDetailedStatus() {
    const serverStatus = await this.client.db('admin').command({ serverStatus: 1 })
    
    return {
      ...this.status,
      server: {
        version: serverStatus.version,
        uptime: serverStatus.uptime,
        connections: {
          current: serverStatus.connections.current,
          available: serverStatus.connections.available
        },
        memory: {
          resident: serverStatus.mem?.resident,
          virtual: serverStatus.mem?.virtual
        },
        opcounters: serverStatus.opcounters
      }
    }
  }
  
  isHealthy() {
    return this.status.connected && 
           this.status.lastPingMs !== null && 
           this.status.lastPingMs < 1000
  }
}

// Usage
const monitor = new ConnectionHealthMonitor(client)
await monitor.start()

// Health endpoint
app.get('/health', async (req, res) => {
  const status = await monitor.getDetailedStatus()
  res.status(monitor.isHealthy() ? 200 : 503).json(status)
})
```

---

[← Previous: Views](65-views.md) | [Next: Connection Pooling →](67-connection-pooling.md)
