# Chapter 64: Capped Collections

## Table of Contents
- [Capped Collections Overview](#capped-collections-overview)
- [Creating Capped Collections](#creating-capped-collections)
- [Working with Capped Collections](#working-with-capped-collections)
- [Tailable Cursors](#tailable-cursors)
- [Use Cases and Patterns](#use-cases-and-patterns)
- [Summary](#summary)

---

## Capped Collections Overview

### What are Capped Collections?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Capped Collections Concept                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Capped collections are fixed-size collections that maintain        │
│  insertion order and automatically overwrite oldest documents       │
│  when the size limit is reached (circular buffer pattern).         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                  Capped Collection (100MB)                   │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │                                                       │  │   │
│  │  │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐          │  │   │
│  │  │  │ 1 │ │ 2 │ │ 3 │ │ 4 │ │ 5 │ │ 6 │ │ 7 │  ────►   │  │   │
│  │  │  └───┘ └───┘ └───┘ └───┘ └───┘ └───┘ └───┘          │  │   │
│  │  │   │                                                   │  │   │
│  │  │   ▼                                                   │  │   │
│  │  │  Oldest (auto-removed when full)                      │  │   │
│  │  │                                                       │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Key Properties:                                                   │
│  • Fixed maximum size                                              │
│  • Insertion order preserved                                       │
│  • Auto-removal of oldest documents                                │
│  • High insert throughput                                          │
│  • Cannot delete individual documents                              │
│  • Cannot update to increase document size                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Capped vs Regular Collections

| Feature | Capped Collection | Regular Collection |
|---------|------------------|-------------------|
| Size limit | Fixed maximum | Grows unlimited |
| Document deletion | Auto (oldest first) | Manual |
| Individual delete | ❌ Not allowed | ✓ Allowed |
| Insertion order | ✓ Guaranteed | ✓ With _id index |
| Size-increasing update | ❌ Not allowed | ✓ Allowed |
| Tailable cursors | ✓ Supported | ❌ Not supported |
| Sharding | ❌ Not supported | ✓ Supported |
| _id index | Optional | Required |

---

## Creating Capped Collections

### Basic Creation

```javascript
// Create capped collection with size limit
db.createCollection("logs", {
  capped: true,
  size: 104857600  // 100 MB in bytes
})

// Create with max documents limit
db.createCollection("recentEvents", {
  capped: true,
  size: 104857600,  // 100 MB
  max: 10000        // Maximum 10,000 documents
})

// Verify collection is capped
db.logs.isCapped()  // true

// Check collection options
db.logs.stats()
```

### Size Calculations

```javascript
// Size must be specified in bytes
// Common size conversions:

const sizes = {
  "1 MB": 1024 * 1024,           // 1048576
  "10 MB": 10 * 1024 * 1024,     // 10485760
  "100 MB": 100 * 1024 * 1024,   // 104857600
  "1 GB": 1024 * 1024 * 1024,    // 1073741824
  "10 GB": 10 * 1024 * 1024 * 1024
}

// Create 50 MB capped collection
db.createCollection("metrics", {
  capped: true,
  size: 50 * 1024 * 1024  // 50 MB
})
```

### Creating with Options

```javascript
// Capped collection with validation
db.createCollection("auditLog", {
  capped: true,
  size: 209715200,  // 200 MB
  max: 50000,
  validator: {
    $jsonSchema: {
      bsonType: "object",
      required: ["timestamp", "action", "user"],
      properties: {
        timestamp: { bsonType: "date" },
        action: { enum: ["create", "read", "update", "delete"] },
        user: { bsonType: "string" }
      }
    }
  }
})

// Capped collection with write concern
db.createCollection("criticalLogs", {
  capped: true,
  size: 104857600,
  writeConcern: { w: "majority", j: true }
})
```

### Converting to Capped Collection

```javascript
// Convert existing collection to capped
db.runCommand({
  convertToCapped: "existingCollection",
  size: 104857600  // 100 MB
})

// Note: This is NOT reversible!
// Documents exceeding the size limit will be removed

// Check if conversion succeeded
db.existingCollection.isCapped()
```

---

## Working with Capped Collections

### Inserting Documents

```javascript
// Insert single document
db.logs.insertOne({
  timestamp: new Date(),
  level: "INFO",
  message: "Application started",
  source: "app-server-01"
})

// Insert multiple documents
db.logs.insertMany([
  { timestamp: new Date(), level: "DEBUG", message: "Request received" },
  { timestamp: new Date(), level: "INFO", message: "Processing request" },
  { timestamp: new Date(), level: "DEBUG", message: "Request completed" }
])

// Ordered inserts (default)
// If one fails, subsequent inserts stop
db.logs.insertMany(documents, { ordered: true })

// Unordered inserts
// Continues even if some inserts fail
db.logs.insertMany(documents, { ordered: false })
```

### Querying Documents

```javascript
// Natural order (insertion order)
db.logs.find().sort({ $natural: 1 })

// Reverse natural order (most recent first)
db.logs.find().sort({ $natural: -1 })

// Get latest N documents
db.logs.find().sort({ $natural: -1 }).limit(10)

// Query with filter
db.logs.find({
  level: "ERROR",
  timestamp: { $gte: new Date(Date.now() - 3600000) }  // Last hour
}).sort({ $natural: -1 })
```

### Update Restrictions

```javascript
// ✓ Allowed: Update that doesn't change document size
db.logs.updateOne(
  { _id: ObjectId("...") },
  { $set: { processed: true } }  // Adding small field may work
)

// ✓ Allowed: Update with same size data
db.logs.updateOne(
  { _id: ObjectId("...") },
  { $set: { level: "WARN" } }  // Same size as "INFO"
)

// ❌ NOT Allowed: Update that increases document size significantly
db.logs.updateOne(
  { _id: ObjectId("...") },
  { $set: { details: "Very long string that increases size..." } }
)
// Error: Cannot change the size of a document in a capped collection

// ❌ NOT Allowed: Replace operations that change size
db.logs.replaceOne(
  { _id: ObjectId("...") },
  { ...largerDocument }
)
```

### Delete Operations

```javascript
// ❌ NOT Allowed: Delete individual documents
db.logs.deleteOne({ _id: ObjectId("...") })
// Error: cannot remove from a capped collection

// ❌ NOT Allowed: Delete multiple documents
db.logs.deleteMany({ level: "DEBUG" })
// Error: cannot remove from a capped collection

// ✓ Allowed: Drop the entire collection
db.logs.drop()

// ✓ Workaround: Use TTL index on regular collection instead
// if you need selective deletion
```

---

## Tailable Cursors

### Understanding Tailable Cursors

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tailable Cursor Behavior                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Regular Cursor:                                                   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Query ──► Returns matching docs ──► Cursor closes          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Tailable Cursor:                                                  │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                                                              │   │
│  │  Query ──► Returns matching docs ──► Waits for new docs     │   │
│  │                                           │                  │   │
│  │                                           ▼                  │   │
│  │                          New doc inserted ──► Returns to     │   │
│  │                                               client         │   │
│  │                                           │                  │   │
│  │                                           ▼                  │   │
│  │                                    Waits again...            │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Use Cases:                                                        │
│  • Log tailing (like Unix 'tail -f')                               │
│  • Real-time notifications                                         │
│  • Message queues                                                  │
│  • Event streaming                                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Using Tailable Cursors (Node.js)

```javascript
const { MongoClient } = require('mongodb')

async function tailLogs() {
  const client = new MongoClient('mongodb://localhost:27017')
  
  try {
    await client.connect()
    const db = client.db('myapp')
    const collection = db.collection('logs')
    
    // Create tailable cursor
    const cursor = collection.find({}, {
      tailable: true,
      awaitData: true,      // Wait for new data
      noCursorTimeout: true // Prevent timeout
    })
    
    console.log('Tailing logs... (Ctrl+C to stop)')
    
    // Process documents as they arrive
    while (await cursor.hasNext()) {
      const doc = await cursor.next()
      console.log(`[${doc.timestamp}] ${doc.level}: ${doc.message}`)
    }
    
  } catch (error) {
    console.error('Error:', error)
  } finally {
    await client.close()
  }
}

tailLogs()
```

### Tailable Cursor with Timeout Handling

```javascript
const { MongoClient } = require('mongodb')

async function robustTailableCursor(dbName, collectionName, processor) {
  const client = new MongoClient('mongodb://localhost:27017')
  let running = true
  
  // Handle graceful shutdown
  process.on('SIGINT', () => {
    console.log('\nShutting down...')
    running = false
  })
  
  try {
    await client.connect()
    const collection = client.db(dbName).collection(collectionName)
    
    // Track last seen document
    let lastId = null
    
    while (running) {
      try {
        // Build query - start from last seen document
        const query = lastId ? { _id: { $gt: lastId } } : {}
        
        const cursor = collection.find(query, {
          tailable: true,
          awaitData: true,
          maxAwaitTimeMS: 5000  // Wait up to 5 seconds
        })
        
        while (running && await cursor.hasNext()) {
          const doc = await cursor.next()
          lastId = doc._id
          
          // Process document
          await processor(doc)
        }
        
      } catch (error) {
        if (error.code === 136) {
          // Capped collection rolled over, reset position
          console.log('Collection rolled over, resetting position')
          lastId = null
        } else {
          console.error('Cursor error:', error.message)
        }
        
        // Wait before reconnecting
        await new Promise(resolve => setTimeout(resolve, 1000))
      }
    }
    
  } finally {
    await client.close()
  }
}

// Usage
robustTailableCursor('myapp', 'logs', async (doc) => {
  console.log(`Received: ${JSON.stringify(doc)}`)
})
```

### Using Tailable Cursors (Python)

```python
from pymongo import MongoClient, CursorType
import time

def tail_collection(db_name, collection_name, callback):
    client = MongoClient('mongodb://localhost:27017')
    collection = client[db_name][collection_name]
    
    # Create tailable cursor
    cursor = collection.find(
        {},
        cursor_type=CursorType.TAILABLE_AWAIT
    )
    
    print(f"Tailing {collection_name}...")
    
    while cursor.alive:
        try:
            doc = cursor.next()
            callback(doc)
        except StopIteration:
            # No more documents, wait a bit
            time.sleep(0.1)

def process_log(doc):
    print(f"[{doc['timestamp']}] {doc['level']}: {doc['message']}")

# Usage
tail_collection('myapp', 'logs', process_log)
```

---

## Use Cases and Patterns

### Application Logging

```javascript
// Create logging collection
db.createCollection("applicationLogs", {
  capped: true,
  size: 209715200,  // 200 MB
  max: 100000       // Max 100k entries
})

// Create index for queries
db.applicationLogs.createIndex({ level: 1, timestamp: -1 })
db.applicationLogs.createIndex({ "source.service": 1 })

// Log entry structure
const logEntry = {
  timestamp: new Date(),
  level: "ERROR",
  message: "Database connection failed",
  source: {
    service: "user-service",
    host: "app-server-01",
    pid: 12345
  },
  context: {
    requestId: "req-abc-123",
    userId: "user-456"
  },
  error: {
    name: "ConnectionError",
    message: "ECONNREFUSED",
    stack: "Error: ..."
  }
}

db.applicationLogs.insertOne(logEntry)

// Query recent errors
db.applicationLogs.find({
  level: "ERROR",
  timestamp: { $gte: new Date(Date.now() - 3600000) }
}).sort({ $natural: -1 }).limit(50)
```

### Simple Message Queue

```javascript
// Create message queue collection
db.createCollection("messageQueue", {
  capped: true,
  size: 52428800,  // 50 MB
  max: 10000
})

// Message structure
function enqueueMessage(queueName, payload, priority = "normal") {
  return db.messageQueue.insertOne({
    queue: queueName,
    payload: payload,
    priority: priority,
    status: "pending",
    createdAt: new Date(),
    attempts: 0
  })
}

// Worker processing (with tailable cursor)
async function processMessages(client, queueName) {
  const collection = client.db('myapp').collection('messageQueue')
  
  const cursor = collection.find(
    { queue: queueName, status: "pending" },
    { tailable: true, awaitData: true }
  )
  
  while (await cursor.hasNext()) {
    const message = await cursor.next()
    
    try {
      // Process message
      await handleMessage(message.payload)
      
      // Mark as processed (status update allowed)
      await collection.updateOne(
        { _id: message._id },
        { $set: { status: "done" } }  // Same size as "pending"
      )
    } catch (error) {
      // Mark as failed
      await collection.updateOne(
        { _id: message._id },
        { 
          $set: { status: "fail" },  // Same size
          $inc: { attempts: 1 }
        }
      )
    }
  }
}
```

### Session/Activity Tracking

```javascript
// Create activity collection
db.createCollection("userActivity", {
  capped: true,
  size: 104857600,  // 100 MB
  max: 50000
})

// Track user activity
function trackActivity(userId, action, details) {
  return db.userActivity.insertOne({
    timestamp: new Date(),
    userId: userId,
    action: action,
    details: details,
    sessionId: getCurrentSessionId(),
    userAgent: getUserAgent()
  })
}

// Get recent activity
function getRecentActivity(userId, limit = 20) {
  return db.userActivity.find({ userId: userId })
    .sort({ $natural: -1 })
    .limit(limit)
    .toArray()
}

// Activity analytics
db.userActivity.aggregate([
  {
    $match: {
      timestamp: { $gte: new Date(Date.now() - 86400000) }  // Last 24h
    }
  },
  {
    $group: {
      _id: "$action",
      count: { $sum: 1 },
      uniqueUsers: { $addToSet: "$userId" }
    }
  },
  {
    $project: {
      action: "$_id",
      count: 1,
      uniqueUserCount: { $size: "$uniqueUsers" }
    }
  },
  { $sort: { count: -1 } }
])
```

### Real-time Metrics Buffer

```javascript
// Create metrics buffer
db.createCollection("metricsBuffer", {
  capped: true,
  size: 52428800,  // 50 MB - rolling 50MB buffer
  max: 100000
})

// Ingest metrics
function recordMetric(metricName, value, tags = {}) {
  return db.metricsBuffer.insertOne({
    t: new Date(),  // Short field names for efficiency
    n: metricName,
    v: value,
    g: tags
  })
}

// Record multiple metrics
function recordMetrics(metrics) {
  const docs = metrics.map(m => ({
    t: new Date(),
    n: m.name,
    v: m.value,
    g: m.tags || {}
  }))
  
  return db.metricsBuffer.insertMany(docs, { ordered: false })
}

// Aggregate recent metrics
function getMetricStats(metricName, windowMinutes = 5) {
  const windowStart = new Date(Date.now() - windowMinutes * 60000)
  
  return db.metricsBuffer.aggregate([
    {
      $match: {
        n: metricName,
        t: { $gte: windowStart }
      }
    },
    {
      $group: {
        _id: null,
        avg: { $avg: "$v" },
        min: { $min: "$v" },
        max: { $max: "$v" },
        count: { $sum: 1 },
        sum: { $sum: "$v" }
      }
    }
  ]).toArray()
}
```

### Event Sourcing Buffer

```javascript
// Create event buffer for event sourcing
db.createCollection("eventBuffer", {
  capped: true,
  size: 209715200,  // 200 MB
  max: 100000
})

// Event structure
const event = {
  eventId: UUID(),
  timestamp: new Date(),
  aggregateType: "Order",
  aggregateId: "order-123",
  eventType: "OrderCreated",
  version: 1,
  payload: {
    customerId: "cust-456",
    items: [
      { productId: "prod-789", quantity: 2 }
    ],
    total: 99.99
  },
  metadata: {
    correlationId: "corr-abc",
    userId: "user-001"
  }
}

// Append event
function appendEvent(aggregateType, aggregateId, eventType, payload, metadata) {
  return db.eventBuffer.insertOne({
    eventId: UUID(),
    timestamp: new Date(),
    aggregateType: aggregateType,
    aggregateId: aggregateId,
    eventType: eventType,
    payload: payload,
    metadata: metadata
  })
}

// Stream events (tailable cursor)
async function streamEvents(fromTimestamp, callback) {
  const cursor = db.eventBuffer.find(
    { timestamp: { $gte: fromTimestamp } },
    { tailable: true, awaitData: true }
  )
  
  while (await cursor.hasNext()) {
    const event = await cursor.next()
    await callback(event)
  }
}
```

---

## Summary

### Capped Collection Characteristics

| Property | Value |
|----------|-------|
| Size | Fixed at creation |
| Document order | Insertion order preserved |
| Oldest documents | Auto-removed when full |
| Individual deletes | Not allowed |
| Size-increasing updates | Not allowed |
| Sharding | Not supported |

### When to Use Capped Collections

| Use Case | Recommendation |
|----------|---------------|
| Application logs | ✓ Good fit |
| Metrics buffer | ✓ Good fit |
| Session activity | ✓ Good fit |
| Simple message queue | ✓ Good fit |
| Audit trail | Consider TTL instead |
| Long-term storage | ❌ Use regular collection |
| Need selective delete | ❌ Use regular collection |

### Key Operations

| Operation | Allowed |
|-----------|---------|
| Insert | ✓ |
| Read | ✓ |
| Update (same size) | ✓ |
| Update (grow size) | ❌ |
| Delete single doc | ❌ |
| Drop collection | ✓ |

---

## Practice Questions

1. What happens when a capped collection reaches its size limit?
2. Why can't you delete individual documents from a capped collection?
3. What is a tailable cursor and when would you use it?
4. What are the limitations on updates in capped collections?
5. Can you convert a regular collection to a capped collection?
6. How does max documents work with size limit?
7. What's the difference between tailable and awaitData options?
8. When should you use TTL index instead of capped collection?

---

## Hands-On Exercises

### Exercise 1: Log Management System

```javascript
// Complete log management system using capped collection

// Setup
db.createCollection("systemLogs", {
  capped: true,
  size: 104857600,  // 100 MB
  max: 50000
})

db.systemLogs.createIndex({ level: 1 })
db.systemLogs.createIndex({ "source.service": 1 })
db.systemLogs.createIndex({ timestamp: 1 })

// Log levels with numeric priority
const LOG_LEVELS = {
  DEBUG: 10,
  INFO: 20,
  WARN: 30,
  ERROR: 40,
  FATAL: 50
}

// Logger class
class Logger {
  constructor(service, host) {
    this.service = service
    this.host = host
  }
  
  _log(level, message, context = {}) {
    const entry = {
      timestamp: new Date(),
      level: level,
      levelNum: LOG_LEVELS[level],
      message: message,
      source: {
        service: this.service,
        host: this.host,
        pid: typeof process !== 'undefined' ? process.pid : 0
      },
      context: context
    }
    
    db.systemLogs.insertOne(entry)
    return entry
  }
  
  debug(message, context) { return this._log("DEBUG", message, context) }
  info(message, context) { return this._log("INFO", message, context) }
  warn(message, context) { return this._log("WARN", message, context) }
  error(message, context) { return this._log("ERROR", message, context) }
  fatal(message, context) { return this._log("FATAL", message, context) }
}

// Log query functions
const LogQuery = {
  // Get recent logs
  recent(limit = 100) {
    return db.systemLogs.find()
      .sort({ $natural: -1 })
      .limit(limit)
      .toArray()
  },
  
  // Get logs by level (minimum)
  byMinLevel(minLevel, limit = 100) {
    return db.systemLogs.find({
      levelNum: { $gte: LOG_LEVELS[minLevel] }
    })
    .sort({ $natural: -1 })
    .limit(limit)
    .toArray()
  },
  
  // Get logs by service
  byService(service, limit = 100) {
    return db.systemLogs.find({
      "source.service": service
    })
    .sort({ $natural: -1 })
    .limit(limit)
    .toArray()
  },
  
  // Search logs
  search(text, limit = 100) {
    return db.systemLogs.find({
      message: { $regex: text, $options: "i" }
    })
    .sort({ $natural: -1 })
    .limit(limit)
    .toArray()
  },
  
  // Log statistics
  stats(minutes = 60) {
    const since = new Date(Date.now() - minutes * 60000)
    
    return db.systemLogs.aggregate([
      { $match: { timestamp: { $gte: since } } },
      {
        $group: {
          _id: {
            level: "$level",
            service: "$source.service"
          },
          count: { $sum: 1 }
        }
      },
      {
        $group: {
          _id: "$_id.service",
          levels: {
            $push: {
              level: "$_id.level",
              count: "$count"
            }
          },
          total: { $sum: "$count" }
        }
      },
      { $sort: { total: -1 } }
    ]).toArray()
  }
}

// Demo
const logger = new Logger("api-gateway", "server-01")

// Generate sample logs
logger.info("Server started", { port: 8080 })
logger.debug("Loading configuration", { file: "config.yaml" })
logger.info("Database connected", { host: "mongo-01" })
logger.warn("High memory usage", { percent: 85 })
logger.error("Request timeout", { endpoint: "/api/users", ms: 30000 })

// Query logs
print("Recent Errors:")
printjson(LogQuery.byMinLevel("ERROR", 10))

print("\nLog Statistics:")
printjson(LogQuery.stats(60))
```

### Exercise 2: Real-time Dashboard Feed

```javascript
// Real-time metrics feed using capped collection

// Create metrics feed collection
db.createCollection("dashboardFeed", {
  capped: true,
  size: 52428800,  // 50 MB
  max: 20000
})

// Metric types
const METRIC_TYPES = {
  GAUGE: "gauge",     // Current value
  COUNTER: "counter", // Cumulative count
  TIMER: "timer"      // Duration measurement
}

// Metrics publisher
const MetricsPublisher = {
  gauge(name, value, tags = {}) {
    return db.dashboardFeed.insertOne({
      t: new Date(),
      type: METRIC_TYPES.GAUGE,
      name: name,
      value: value,
      tags: tags
    })
  },
  
  counter(name, delta = 1, tags = {}) {
    return db.dashboardFeed.insertOne({
      t: new Date(),
      type: METRIC_TYPES.COUNTER,
      name: name,
      delta: delta,
      tags: tags
    })
  },
  
  timer(name, durationMs, tags = {}) {
    return db.dashboardFeed.insertOne({
      t: new Date(),
      type: METRIC_TYPES.TIMER,
      name: name,
      duration: durationMs,
      tags: tags
    })
  }
}

// Dashboard aggregation
const Dashboard = {
  // Get current gauge values
  currentGauges() {
    return db.dashboardFeed.aggregate([
      { $match: { type: METRIC_TYPES.GAUGE } },
      { $sort: { t: -1 } },
      {
        $group: {
          _id: {
            name: "$name",
            tags: "$tags"
          },
          latestValue: { $first: "$value" },
          timestamp: { $first: "$t" }
        }
      },
      {
        $project: {
          name: "$_id.name",
          tags: "$_id.tags",
          value: "$latestValue",
          timestamp: 1
        }
      }
    ]).toArray()
  },
  
  // Get counter totals
  counterTotals(windowMinutes = 5) {
    const since = new Date(Date.now() - windowMinutes * 60000)
    
    return db.dashboardFeed.aggregate([
      {
        $match: {
          type: METRIC_TYPES.COUNTER,
          t: { $gte: since }
        }
      },
      {
        $group: {
          _id: "$name",
          total: { $sum: "$delta" },
          count: { $sum: 1 }
        }
      },
      { $sort: { total: -1 } }
    ]).toArray()
  },
  
  // Get timer percentiles
  timerStats(name, windowMinutes = 5) {
    const since = new Date(Date.now() - windowMinutes * 60000)
    
    return db.dashboardFeed.aggregate([
      {
        $match: {
          type: METRIC_TYPES.TIMER,
          name: name,
          t: { $gte: since }
        }
      },
      {
        $group: {
          _id: null,
          count: { $sum: 1 },
          avg: { $avg: "$duration" },
          min: { $min: "$duration" },
          max: { $max: "$duration" },
          durations: { $push: "$duration" }
        }
      },
      {
        $project: {
          count: 1,
          avg: { $round: ["$avg", 2] },
          min: 1,
          max: 1,
          p50: {
            $arrayElemAt: [
              "$durations",
              { $floor: { $multiply: [{ $size: "$durations" }, 0.5] } }
            ]
          },
          p95: {
            $arrayElemAt: [
              "$durations",
              { $floor: { $multiply: [{ $size: "$durations" }, 0.95] } }
            ]
          }
        }
      }
    ]).toArray()
  },
  
  // Health overview
  healthOverview() {
    return {
      gauges: this.currentGauges(),
      counters: this.counterTotals(),
      timestamp: new Date()
    }
  }
}

// Demo - Generate sample metrics
function simulateMetrics() {
  // CPU gauge
  MetricsPublisher.gauge("system.cpu", Math.random() * 100, { host: "server-01" })
  
  // Memory gauge  
  MetricsPublisher.gauge("system.memory", 60 + Math.random() * 30, { host: "server-01" })
  
  // Request counters
  MetricsPublisher.counter("http.requests", 1, { method: "GET", status: 200 })
  MetricsPublisher.counter("http.requests", 1, { method: "POST", status: 201 })
  
  // Response time timer
  MetricsPublisher.timer("http.response_time", 50 + Math.random() * 200, { endpoint: "/api/users" })
}

// Run simulation
for (let i = 0; i < 100; i++) {
  simulateMetrics()
}

// Display dashboard
print("╔════════════════════════════════════════════════════════════╗")
print("║              REAL-TIME DASHBOARD                            ║")
print("╚════════════════════════════════════════════════════════════╝\n")

const health = Dashboard.healthOverview()

print("┌─ CURRENT GAUGES ───────────────────────────────────────────┐")
health.gauges.forEach(g => {
  print(`│  ${g.name}: ${g.value.toFixed(2)}`.padEnd(60) + "│")
})
print("└────────────────────────────────────────────────────────────┘\n")

print("┌─ COUNTER TOTALS (5 min) ───────────────────────────────────┐")
health.counters.forEach(c => {
  print(`│  ${c._id}: ${c.total}`.padEnd(60) + "│")
})
print("└────────────────────────────────────────────────────────────┘\n")

const timerStats = Dashboard.timerStats("http.response_time")
if (timerStats.length > 0) {
  const t = timerStats[0]
  print("┌─ RESPONSE TIME (5 min) ───────────────────────────────────┐")
  print(`│  Count: ${t.count}`.padEnd(60) + "│")
  print(`│  Avg: ${t.avg}ms`.padEnd(60) + "│")
  print(`│  Min: ${t.min}ms | Max: ${t.max}ms`.padEnd(60) + "│")
  print(`│  P50: ${t.p50}ms | P95: ${t.p95}ms`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
}
```

### Exercise 3: Capped Collection Monitor

```javascript
// Monitor capped collection status and usage

function cappedCollectionMonitor(collectionName) {
  const collection = db.getCollection(collectionName)
  
  // Check if capped
  if (!collection.isCapped()) {
    print(`ERROR: ${collectionName} is not a capped collection`)
    return
  }
  
  const stats = collection.stats()
  const config = db.getCollectionInfos({ name: collectionName })[0]
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         CAPPED COLLECTION MONITOR                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Basic info
  print(`Collection: ${collectionName}`)
  print(`Is Capped: ${stats.capped}\n`)
  
  // Size limits
  const maxSize = config.options.size
  const maxDocs = config.options.max || "unlimited"
  const currentSize = stats.size
  const currentDocs = stats.count
  
  const sizePercent = (currentSize / maxSize * 100).toFixed(1)
  const sizeBar = '█'.repeat(Math.round(sizePercent / 5)).padEnd(20)
  
  print("┌─ SIZE USAGE ──────────────────────────────────────────────┐")
  print(`│  Max Size: ${(maxSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Current Size: ${(currentSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Usage: [${sizeBar}] ${sizePercent}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ DOCUMENT COUNT ──────────────────────────────────────────┐")
  print(`│  Max Documents: ${maxDocs}`.padEnd(60) + "│")
  print(`│  Current Documents: ${currentDocs}`.padEnd(60) + "│")
  if (maxDocs !== "unlimited") {
    const docPercent = (currentDocs / maxDocs * 100).toFixed(1)
    const docBar = '█'.repeat(Math.round(docPercent / 5)).padEnd(20)
    print(`│  Usage: [${docBar}] ${docPercent}%`.padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Storage details
  print("┌─ STORAGE DETAILS ─────────────────────────────────────────┐")
  print(`│  Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Average Object Size: ${(stats.avgObjSize || 0).toFixed(0)} bytes`.padEnd(60) + "│")
  
  // Estimate remaining capacity
  if (stats.avgObjSize > 0) {
    const remainingSpace = maxSize - currentSize
    const estimatedRemaining = Math.floor(remainingSpace / stats.avgObjSize)
    print(`│  Estimated Remaining Docs: ~${estimatedRemaining}`.padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Time range of data
  const oldest = collection.findOne({}, { sort: { $natural: 1 } })
  const newest = collection.findOne({}, { sort: { $natural: -1 } })
  
  if (oldest && newest && oldest.timestamp && newest.timestamp) {
    const duration = (newest.timestamp - oldest.timestamp) / 1000 / 60  // minutes
    
    print("┌─ TIME RANGE ───────────────────────────────────────────────┐")
    print(`│  Oldest: ${oldest.timestamp.toISOString()}`.padEnd(60) + "│")
    print(`│  Newest: ${newest.timestamp.toISOString()}`.padEnd(60) + "│")
    print(`│  Span: ${duration.toFixed(1)} minutes`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Indexes
  const indexes = collection.getIndexes()
  print("┌─ INDEXES ─────────────────────────────────────────────────┐")
  indexes.forEach(idx => {
    const keys = Object.keys(idx.key).join(", ")
    print(`│  ${idx.name}: { ${keys} }`.padEnd(60) + "│")
  })
  print("└────────────────────────────────────────────────────────────┘")
  
  return {
    maxSize,
    currentSize,
    sizePercent: parseFloat(sizePercent),
    maxDocs,
    currentDocs,
    avgDocSize: stats.avgObjSize
  }
}

// Run monitor
cappedCollectionMonitor("systemLogs")
```

---

[← Previous: Time Series Collections](63-time-series.md) | [Next: Views →](65-views.md)
