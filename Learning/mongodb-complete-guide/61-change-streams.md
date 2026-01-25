# Chapter 61: Change Streams

## Table of Contents
- [Change Streams Overview](#change-streams-overview)
- [Opening Change Streams](#opening-change-streams)
- [Change Event Types](#change-event-types)
- [Filtering and Aggregation](#filtering-and-aggregation)
- [Resume Tokens](#resume-tokens)
- [Production Patterns](#production-patterns)
- [Summary](#summary)

---

## Change Streams Overview

### What are Change Streams?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Change Streams Architecture                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Application                               │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │   │
│  │  │ Web Server  │  │   Worker    │  │  Analytics Service  │  │   │
│  │  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘  │   │
│  │         │                │                     │             │   │
│  │         └────────────────┼─────────────────────┘             │   │
│  │                          │                                   │   │
│  │                          ▼                                   │   │
│  │              ┌───────────────────────┐                      │   │
│  │              │    Change Stream      │                      │   │
│  │              │    (cursor)           │                      │   │
│  │              └───────────┬───────────┘                      │   │
│  └──────────────────────────┼───────────────────────────────────┘   │
│                             │                                       │
│                             ▼                                       │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MongoDB Replica Set                       │   │
│  │                                                              │   │
│  │  ┌──────────────────────────────────────────────────────┐   │   │
│  │  │                      Oplog                            │   │   │
│  │  │  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐  ┌──────┐   │   │   │
│  │  │  │Insert│  │Update│  │Delete│  │Insert│  │Update│   │   │   │
│  │  │  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘   │   │   │
│  │  └──────────────────────────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Benefits:                                                         │
│  • Real-time data synchronization                                  │
│  • Event-driven architectures                                      │
│  • No polling required                                             │
│  • Resumable after disconnection                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Requirements

| Requirement | Description |
|-------------|-------------|
| Replica Set | Change streams require replica set or sharded cluster |
| Read Concern | Majority read concern must be available |
| MongoDB Version | 3.6+ (enhanced in 4.0, 4.2, 6.0) |
| WiredTiger | Required storage engine |

---

## Opening Change Streams

### Collection Level

```javascript
// Watch a single collection
const changeStream = db.orders.watch()

// Iterate through changes
while (changeStream.hasNext()) {
  const change = changeStream.next()
  print(JSON.stringify(change, null, 2))
}

// Or use forEach
db.orders.watch().forEach(change => {
  print(`Operation: ${change.operationType}`)
  print(`Document ID: ${change.documentKey._id}`)
})
```

### Database Level

```javascript
// Watch all collections in a database
const dbChangeStream = db.watch()

dbChangeStream.forEach(change => {
  print(`Collection: ${change.ns.coll}`)
  print(`Operation: ${change.operationType}`)
})
```

### Cluster Level

```javascript
// Watch entire cluster (MongoDB 4.0+)
const clusterStream = db.getMongo().watch()

clusterStream.forEach(change => {
  print(`Database: ${change.ns.db}`)
  print(`Collection: ${change.ns.coll}`)
  print(`Operation: ${change.operationType}`)
})
```

### With Options

```javascript
// Open with options
const options = {
  fullDocument: 'updateLookup',  // Include full document on updates
  fullDocumentBeforeChange: 'whenAvailable',  // MongoDB 6.0+
  maxAwaitTimeMS: 5000,
  batchSize: 100
}

const changeStream = db.orders.watch([], options)
```

---

## Change Event Types

### Event Structure

```javascript
// Example change event
{
  "_id": {
    "_data": "826..."  // Resume token
  },
  "operationType": "insert",
  "clusterTime": Timestamp(1705312800, 1),
  "wallTime": ISODate("2024-01-15T10:00:00.000Z"),
  "fullDocument": {
    "_id": ObjectId("..."),
    "customerId": "C123",
    "total": 150.00,
    "status": "pending"
  },
  "ns": {
    "db": "ecommerce",
    "coll": "orders"
  },
  "documentKey": {
    "_id": ObjectId("...")
  }
}
```

### Operation Types

| Operation Type | Description | Available Since |
|----------------|-------------|-----------------|
| insert | New document inserted | 3.6 |
| update | Document updated | 3.6 |
| replace | Document replaced | 3.6 |
| delete | Document deleted | 3.6 |
| drop | Collection dropped | 4.0 |
| rename | Collection renamed | 4.0 |
| dropDatabase | Database dropped | 4.0 |
| invalidate | Stream invalidated | 3.6 |

### Insert Event

```javascript
// Insert event
{
  "operationType": "insert",
  "fullDocument": {
    "_id": ObjectId("65a5b8c..."),
    "name": "John Doe",
    "email": "john@example.com",
    "createdAt": ISODate("2024-01-15T10:00:00Z")
  },
  "ns": { "db": "mydb", "coll": "users" },
  "documentKey": { "_id": ObjectId("65a5b8c...") }
}
```

### Update Event

```javascript
// Update event
{
  "operationType": "update",
  "ns": { "db": "mydb", "coll": "users" },
  "documentKey": { "_id": ObjectId("65a5b8c...") },
  "updateDescription": {
    "updatedFields": {
      "status": "active",
      "lastLogin": ISODate("2024-01-15T12:00:00Z")
    },
    "removedFields": ["tempField"],
    "truncatedArrays": []
  },
  // With fullDocument: 'updateLookup'
  "fullDocument": {
    "_id": ObjectId("65a5b8c..."),
    "name": "John Doe",
    "email": "john@example.com",
    "status": "active",
    "lastLogin": ISODate("2024-01-15T12:00:00Z")
  }
}
```

### Delete Event

```javascript
// Delete event
{
  "operationType": "delete",
  "ns": { "db": "mydb", "coll": "users" },
  "documentKey": { "_id": ObjectId("65a5b8c...") }
  // Note: fullDocument not available for deletes
  // Use fullDocumentBeforeChange in MongoDB 6.0+
}
```

### Pre-Image and Post-Image (MongoDB 6.0+)

```javascript
// Enable change stream pre and post images for collection
db.createCollection("orders", {
  changeStreamPreAndPostImages: { enabled: true }
})

// Or modify existing collection
db.runCommand({
  collMod: "orders",
  changeStreamPreAndPostImages: { enabled: true }
})

// Watch with pre and post images
const stream = db.orders.watch([], {
  fullDocument: 'whenAvailable',
  fullDocumentBeforeChange: 'whenAvailable'
})

// Update event with before/after images
{
  "operationType": "update",
  "fullDocumentBeforeChange": {
    "_id": ObjectId("..."),
    "status": "pending",
    "total": 100
  },
  "fullDocument": {
    "_id": ObjectId("..."),
    "status": "shipped",
    "total": 100
  },
  "updateDescription": {
    "updatedFields": { "status": "shipped" },
    "removedFields": []
  }
}
```

---

## Filtering and Aggregation

### Using Aggregation Pipeline

```javascript
// Filter for specific operations
const pipeline = [
  { $match: { operationType: 'insert' } }
]

const stream = db.orders.watch(pipeline)
```

### Filter by Document Fields

```javascript
// Watch for high-value orders only
const pipeline = [
  { $match: { 
    'fullDocument.total': { $gte: 1000 },
    operationType: { $in: ['insert', 'update'] }
  }}
]

const stream = db.orders.watch(pipeline)
```

### Filter by Update Fields

```javascript
// Watch for status changes
const pipeline = [
  { $match: {
    $or: [
      { operationType: 'insert' },
      { 
        operationType: 'update',
        'updateDescription.updatedFields.status': { $exists: true }
      }
    ]
  }}
]

const stream = db.orders.watch(pipeline)
```

### Project Specific Fields

```javascript
// Project only needed fields
const pipeline = [
  { $match: { operationType: { $in: ['insert', 'update'] } } },
  { $project: {
    operationType: 1,
    'documentKey._id': 1,
    'fullDocument.customerId': 1,
    'fullDocument.status': 1,
    'fullDocument.total': 1
  }}
]

const stream = db.orders.watch(pipeline)
```

### Add Computed Fields

```javascript
// Add timestamps and computed fields
const pipeline = [
  { $addFields: {
    processedAt: '$$NOW',
    isHighValue: { $gte: ['$fullDocument.total', 500] }
  }}
]

const stream = db.orders.watch(pipeline)
```

---

## Resume Tokens

### Understanding Resume Tokens

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Resume Token Flow                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Open Change Stream                                             │
│     ┌─────────────────────┐                                        │
│     │  stream = watch()   │                                        │
│     └──────────┬──────────┘                                        │
│                │                                                    │
│  2. Receive Events                                                 │
│     ┌──────────▼──────────┐                                        │
│     │  Event 1 (token A)  │ ─── Save token A                       │
│     │  Event 2 (token B)  │ ─── Save token B                       │
│     │  Event 3 (token C)  │ ─── Save token C                       │
│     └──────────┬──────────┘                                        │
│                │                                                    │
│  3. Disconnection                                                  │
│     ┌──────────▼──────────┐                                        │
│     │  Connection Lost    │                                        │
│     └──────────┬──────────┘                                        │
│                │                                                    │
│  4. Resume from Last Token                                         │
│     ┌──────────▼──────────┐                                        │
│     │  watch([], {        │                                        │
│     │    resumeAfter:     │                                        │
│     │    savedToken       │                                        │
│     │  })                 │                                        │
│     └──────────┬──────────┘                                        │
│                │                                                    │
│  5. Continue from Event 4                                          │
│     ┌──────────▼──────────┐                                        │
│     │  Event 4 (token D)  │                                        │
│     │  Event 5 (token E)  │                                        │
│     └─────────────────────┘                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Saving and Using Resume Tokens

```javascript
// Save resume token during processing
let lastResumeToken = null

const stream = db.orders.watch()

stream.forEach(change => {
  // Process the change
  processChange(change)
  
  // Save the resume token
  lastResumeToken = change._id
  saveResumeToken(lastResumeToken)  // Persist to storage
})

// Resume after disconnection
function resumeChangeStream() {
  const savedToken = loadResumeToken()  // Load from storage
  
  const options = savedToken 
    ? { resumeAfter: savedToken }
    : {}
  
  return db.orders.watch([], options)
}
```

### Resume Options

```javascript
// resumeAfter - Resume after a specific event
const stream = db.orders.watch([], {
  resumeAfter: savedResumeToken
})

// startAfter - Start after a specific event (MongoDB 4.2+)
// Use when the previous stream was invalidated
const stream = db.orders.watch([], {
  startAfter: savedResumeToken
})

// startAtOperationTime - Start at a specific cluster time
const stream = db.orders.watch([], {
  startAtOperationTime: Timestamp(1705312800, 1)
})
```

### Persisting Resume Tokens

```javascript
// Store resume token in MongoDB
function saveResumeToken(collectionName, token) {
  db.changeStreamTokens.updateOne(
    { _id: collectionName },
    { 
      $set: { 
        token: token,
        updatedAt: new Date()
      }
    },
    { upsert: true }
  )
}

function loadResumeToken(collectionName) {
  const doc = db.changeStreamTokens.findOne({ _id: collectionName })
  return doc?.token || null
}
```

---

## Production Patterns

### Error Handling and Reconnection

```javascript
// Robust change stream with reconnection
async function watchWithReconnection(collection, pipeline = []) {
  let resumeToken = await loadResumeToken(collection.name)
  
  while (true) {
    try {
      const options = resumeToken 
        ? { resumeAfter: resumeToken, fullDocument: 'updateLookup' }
        : { fullDocument: 'updateLookup' }
      
      const stream = collection.watch(pipeline, options)
      
      console.log('Change stream opened')
      
      while (await stream.hasNext()) {
        const change = await stream.next()
        
        // Process the change
        await processChange(change)
        
        // Save resume token
        resumeToken = change._id
        await saveResumeToken(collection.name, resumeToken)
      }
    } catch (error) {
      console.error('Change stream error:', error.message)
      
      // Check if error is resumable
      if (error.hasErrorLabel && error.hasErrorLabel('ResumableChangeStreamError')) {
        console.log('Resumable error - reconnecting in 1 second...')
        await sleep(1000)
        continue
      }
      
      // Non-resumable error
      if (error.code === 40585) {  // InvalidateEvent
        console.log('Stream invalidated - starting fresh')
        resumeToken = null
        continue
      }
      
      throw error
    }
  }
}
```

### Event-Driven Architecture

```javascript
// Event bus pattern with change streams
class ChangeStreamEventBus {
  constructor(db) {
    this.db = db
    this.handlers = new Map()
    this.streams = []
  }
  
  // Register handler for collection events
  on(collection, eventType, handler) {
    const key = `${collection}:${eventType}`
    if (!this.handlers.has(key)) {
      this.handlers.set(key, [])
    }
    this.handlers.get(key).push(handler)
  }
  
  // Start watching collections
  async start(collections) {
    for (const collName of collections) {
      const coll = this.db.getCollection(collName)
      const stream = coll.watch([], { fullDocument: 'updateLookup' })
      
      this.streams.push(stream)
      
      // Process changes
      this.processStream(collName, stream)
    }
  }
  
  async processStream(collName, stream) {
    while (await stream.hasNext()) {
      const change = await stream.next()
      const key = `${collName}:${change.operationType}`
      
      const handlers = this.handlers.get(key) || []
      for (const handler of handlers) {
        try {
          await handler(change)
        } catch (error) {
          console.error(`Handler error: ${error.message}`)
        }
      }
    }
  }
  
  // Stop all streams
  close() {
    this.streams.forEach(stream => stream.close())
  }
}

// Usage
const eventBus = new ChangeStreamEventBus(db)

eventBus.on('orders', 'insert', async (change) => {
  console.log('New order:', change.fullDocument._id)
  await sendOrderConfirmation(change.fullDocument)
})

eventBus.on('orders', 'update', async (change) => {
  if (change.updateDescription.updatedFields.status === 'shipped') {
    await sendShippingNotification(change.fullDocument)
  }
})

await eventBus.start(['orders', 'users', 'products'])
```

### Real-Time Sync Pattern

```javascript
// Sync to external system
async function syncToElasticsearch(collection, esClient, indexName) {
  const pipeline = [
    { $match: { 
      operationType: { $in: ['insert', 'update', 'replace', 'delete'] }
    }}
  ]
  
  const stream = collection.watch(pipeline, {
    fullDocument: 'updateLookup'
  })
  
  while (await stream.hasNext()) {
    const change = await stream.next()
    
    try {
      switch (change.operationType) {
        case 'insert':
        case 'update':
        case 'replace':
          await esClient.index({
            index: indexName,
            id: change.documentKey._id.toString(),
            body: change.fullDocument
          })
          break
          
        case 'delete':
          await esClient.delete({
            index: indexName,
            id: change.documentKey._id.toString()
          })
          break
      }
      
      console.log(`Synced: ${change.operationType} ${change.documentKey._id}`)
    } catch (error) {
      console.error('Sync error:', error)
      // Handle error (retry, dead letter queue, etc.)
    }
  }
}
```

### Aggregation Pipeline Processing

```javascript
// Complex event processing
const pipeline = [
  // Filter for order events
  { $match: { 
    operationType: { $in: ['insert', 'update'] },
    'fullDocument.status': { $exists: true }
  }},
  
  // Add computed fields
  { $addFields: {
    eventId: { $toString: '$_id._data' },
    timestamp: '$clusterTime',
    orderValue: '$fullDocument.total',
    isHighPriority: { 
      $or: [
        { $gte: ['$fullDocument.total', 1000] },
        { $eq: ['$fullDocument.priority', 'high'] }
      ]
    }
  }},
  
  // Project final shape
  { $project: {
    eventId: 1,
    timestamp: 1,
    operationType: 1,
    orderId: '$documentKey._id',
    customerId: '$fullDocument.customerId',
    status: '$fullDocument.status',
    orderValue: 1,
    isHighPriority: 1
  }}
]

const stream = db.orders.watch(pipeline)
```

---

## Summary

### Change Stream Options

| Option | Description | Default |
|--------|-------------|---------|
| fullDocument | Include full document | 'default' |
| fullDocumentBeforeChange | Include pre-image | None |
| resumeAfter | Resume token | None |
| startAfter | Start after token | None |
| startAtOperationTime | Start time | None |
| maxAwaitTimeMS | Max wait time | None |
| batchSize | Batch size | None |

### Use Cases

| Use Case | Description |
|----------|-------------|
| Real-time sync | Sync data to external systems |
| Event sourcing | Capture all changes as events |
| Notifications | Trigger notifications on changes |
| Caching | Invalidate cache on updates |
| Audit logging | Log all data changes |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Save resume tokens | Enable recovery after disconnection |
| Use pipeline filters | Reduce processing overhead |
| Handle errors gracefully | Ensure reliability |
| Use fullDocument option | Get complete context |

---

## Practice Questions

1. What is required to use change streams in MongoDB?
2. What is a resume token and why is it important?
3. How do you filter change stream events?
4. What is the difference between resumeAfter and startAfter?
5. How do you get the full document on update events?
6. What happens when a change stream is invalidated?
7. How do you watch changes at the cluster level?
8. What are pre-images and post-images in MongoDB 6.0+?

---

## Hands-On Exercises

### Exercise 1: Change Stream Monitor

```javascript
// Real-time change stream monitor

function changeStreamMonitor(collectionName, durationSec = 60) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           CHANGE STREAM MONITOR                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Watching: ${collectionName}`)
  print(`Duration: ${durationSec} seconds`)
  print("Waiting for changes...\n")
  
  const coll = db.getCollection(collectionName)
  const stream = coll.watch([], { 
    fullDocument: 'updateLookup',
    maxAwaitTimeMS: 1000
  })
  
  const stats = {
    insert: 0,
    update: 0,
    replace: 0,
    delete: 0,
    total: 0
  }
  
  const startTime = Date.now()
  const endTime = startTime + (durationSec * 1000)
  
  print("┌─ EVENTS ──────────────────────────────────────────────────┐")
  
  while (Date.now() < endTime) {
    if (stream.hasNext()) {
      const change = stream.next()
      stats[change.operationType]++
      stats.total++
      
      const time = new Date().toISOString().substring(11, 19)
      const op = change.operationType.toUpperCase().padEnd(8)
      const docId = change.documentKey._id.toString().substring(0, 24)
      
      print(`│  ${time}  ${op}  ${docId}`.padEnd(60) + "│")
    }
  }
  
  stream.close()
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ SUMMARY ─────────────────────────────────────────────────┐")
  print(`│  Total Events: ${stats.total}`.padEnd(60) + "│")
  print(`│  Inserts: ${stats.insert}`.padEnd(60) + "│")
  print(`│  Updates: ${stats.update}`.padEnd(60) + "│")
  print(`│  Replaces: ${stats.replace}`.padEnd(60) + "│")
  print(`│  Deletes: ${stats.delete}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  return stats
}

// Usage (run in one terminal, make changes in another)
// changeStreamMonitor("orders", 60)
```

### Exercise 2: Event Logger

```javascript
// Log all changes to an audit collection

function startEventLogger(sourceCollection, auditCollection = 'audit_log') {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              EVENT LOGGER                                   ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Source: ${sourceCollection}`)
  print(`Audit: ${auditCollection}`)
  print("Press Ctrl+C to stop\n")
  
  const source = db.getCollection(sourceCollection)
  const audit = db.getCollection(auditCollection)
  
  // Create index for efficient queries
  audit.createIndex({ timestamp: -1 })
  audit.createIndex({ sourceCollection: 1, operationType: 1 })
  
  const stream = source.watch([], {
    fullDocument: 'updateLookup'
  })
  
  let count = 0
  
  while (stream.hasNext()) {
    const change = stream.next()
    
    // Create audit record
    const auditRecord = {
      timestamp: new Date(),
      sourceCollection: sourceCollection,
      operationType: change.operationType,
      documentId: change.documentKey._id,
      resumeToken: change._id,
      clusterTime: change.clusterTime
    }
    
    // Add operation-specific data
    if (change.fullDocument) {
      auditRecord.document = change.fullDocument
    }
    
    if (change.updateDescription) {
      auditRecord.changes = {
        updatedFields: change.updateDescription.updatedFields,
        removedFields: change.updateDescription.removedFields
      }
    }
    
    // Insert audit record
    audit.insertOne(auditRecord)
    
    count++
    print(`[${new Date().toISOString()}] ${change.operationType}: ${change.documentKey._id} (Total: ${count})`)
  }
}

// Query audit log
function queryAuditLog(options = {}) {
  const {
    collection = null,
    operationType = null,
    startTime = null,
    endTime = null,
    limit = 20
  } = options
  
  const query = {}
  
  if (collection) query.sourceCollection = collection
  if (operationType) query.operationType = operationType
  if (startTime || endTime) {
    query.timestamp = {}
    if (startTime) query.timestamp.$gte = startTime
    if (endTime) query.timestamp.$lte = endTime
  }
  
  return db.audit_log.find(query)
    .sort({ timestamp: -1 })
    .limit(limit)
    .toArray()
}

// Usage
// startEventLogger("orders")
// queryAuditLog({ operationType: "update", limit: 10 })
```

### Exercise 3: Real-Time Dashboard Data

```javascript
// Generate real-time dashboard statistics

function realtimeDashboard(collections) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           REAL-TIME DASHBOARD                               ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const stats = {}
  
  // Initialize stats for each collection
  collections.forEach(coll => {
    stats[coll] = {
      inserts: 0,
      updates: 0,
      deletes: 0,
      lastEvent: null
    }
  })
  
  // Watch each collection
  const streams = collections.map(collName => {
    const stream = db.getCollection(collName).watch([], {
      maxAwaitTimeMS: 500
    })
    return { name: collName, stream }
  })
  
  // Display function
  function displayStats() {
    print("\033[2J\033[H")  // Clear screen
    print("╔════════════════════════════════════════════════════════════╗")
    print("║           REAL-TIME DASHBOARD                               ║")
    print("║           " + new Date().toISOString().padEnd(47) + "║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    collections.forEach(coll => {
      const s = stats[coll]
      print(`┌─ ${coll.toUpperCase()} ${"─".repeat(55 - coll.length)}┐`)
      print(`│  Inserts: ${s.inserts}  Updates: ${s.updates}  Deletes: ${s.deletes}`.padEnd(60) + "│")
      print(`│  Last Event: ${s.lastEvent || 'None'}`.padEnd(60) + "│")
      print("└────────────────────────────────────────────────────────────┘\n")
    })
  }
  
  // Process loop
  let running = true
  const interval = setInterval(displayStats, 1000)
  
  while (running) {
    streams.forEach(({ name, stream }) => {
      if (stream.hasNext()) {
        const change = stream.next()
        
        if (change.operationType === 'insert') stats[name].inserts++
        if (change.operationType === 'update') stats[name].updates++
        if (change.operationType === 'delete') stats[name].deletes++
        
        stats[name].lastEvent = `${change.operationType} at ${new Date().toISOString()}`
      }
    })
  }
  
  clearInterval(interval)
  streams.forEach(({ stream }) => stream.close())
}

// Usage
// realtimeDashboard(["orders", "products", "users"])
```

### Exercise 4: Change Stream with Retry Logic

```javascript
// Production-ready change stream with retry

function robustChangeStream(collectionName, processor) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         ROBUST CHANGE STREAM                                ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const tokenCollection = 'change_stream_tokens'
  
  // Load saved token
  function loadToken() {
    const doc = db.getCollection(tokenCollection).findOne({ _id: collectionName })
    return doc?.token || null
  }
  
  // Save token
  function saveToken(token) {
    db.getCollection(tokenCollection).updateOne(
      { _id: collectionName },
      { $set: { token: token, updatedAt: new Date() } },
      { upsert: true }
    )
  }
  
  // Main loop
  let retryCount = 0
  const maxRetries = 10
  const retryDelayMs = 1000
  
  while (retryCount < maxRetries) {
    try {
      const token = loadToken()
      const options = {
        fullDocument: 'updateLookup'
      }
      
      if (token) {
        options.resumeAfter = token
        print(`Resuming from saved token...`)
      } else {
        print(`Starting fresh (no saved token)`)
      }
      
      const stream = db.getCollection(collectionName).watch([], options)
      
      print(`Watching ${collectionName}...\n`)
      retryCount = 0  // Reset on successful connection
      
      while (stream.hasNext()) {
        const change = stream.next()
        
        // Process the change
        try {
          processor(change)
          print(`Processed: ${change.operationType} ${change.documentKey._id}`)
        } catch (procError) {
          print(`Processing error: ${procError.message}`)
          // Continue processing other events
        }
        
        // Save token after successful processing
        saveToken(change._id)
      }
      
    } catch (error) {
      retryCount++
      print(`\nError: ${error.message}`)
      print(`Retry ${retryCount}/${maxRetries} in ${retryDelayMs}ms...`)
      
      sleep(retryDelayMs * retryCount)  // Exponential backoff
    }
  }
  
  print(`\nMax retries exceeded. Exiting.`)
}

// Example processor
function exampleProcessor(change) {
  // Your business logic here
  if (change.operationType === 'insert') {
    // Handle new document
  } else if (change.operationType === 'update') {
    // Handle update
  }
}

// Usage
// robustChangeStream("orders", exampleProcessor)
```

---

[← Previous: Logging and Diagnostics](60-logging-diagnostics.md) | [Next: GridFS →](62-gridfs.md)
