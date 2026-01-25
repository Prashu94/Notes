# Chapter 67: Connection Pooling

## Table of Contents
- [Connection Pooling Overview](#connection-pooling-overview)
- [Pool Configuration](#pool-configuration)
- [Pool Monitoring](#pool-monitoring)
- [Connection Lifecycle](#connection-lifecycle)
- [Advanced Pooling Patterns](#advanced-pooling-patterns)
- [Troubleshooting](#troubleshooting)
- [Summary](#summary)

---

## Connection Pooling Overview

### Why Connection Pooling?

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Connection Pooling Benefits                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Without Connection Pool:                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Request 1 ──► Open Connection ──► Query ──► Close          │   │
│  │  Request 2 ──► Open Connection ──► Query ──► Close          │   │
│  │  Request 3 ──► Open Connection ──► Query ──► Close          │   │
│  │                                                              │   │
│  │  Problems:                                                   │   │
│  │  • Connection overhead (TCP handshake, auth)                │   │
│  │  • Resource exhaustion                                       │   │
│  │  • Increased latency                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  With Connection Pool:                                             │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  ┌────────────────────────────────────────────────────┐     │   │
│  │  │           Connection Pool (Pre-established)        │     │   │
│  │  │  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐     │     │   │
│  │  │  │Conn1│  │Conn2│  │Conn3│  │Conn4│  │Conn5│     │     │   │
│  │  │  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘     │     │   │
│  │  └────────────────────────────────────────────────────┘     │   │
│  │       ▲           ▲           ▲                              │   │
│  │       │           │           │                              │   │
│  │  Request 1    Request 2   Request 3                         │   │
│  │                                                              │   │
│  │  Benefits:                                                   │   │
│  │  • Reuse existing connections                                │   │
│  │  • Bounded resource usage                                    │   │
│  │  • Reduced latency                                           │   │
│  │  • Better throughput                                         │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Pool Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Connection Pool Architecture                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MongoClient                               │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │              Connection Pool Manager                   │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌──────────────────┐  ┌──────────────────┐          │  │   │
│  │  │  │  Pool: Primary   │  │  Pool: Secondary │          │  │   │
│  │  │  │  ┌────┐ ┌────┐  │  │  ┌────┐ ┌────┐  │          │  │   │
│  │  │  │  │Idle│ │Busy│  │  │  │Idle│ │Busy│  │          │  │   │
│  │  │  │  └────┘ └────┘  │  │  └────┘ └────┘  │          │  │   │
│  │  │  └──────────────────┘  └──────────────────┘          │  │   │
│  │  │                                                        │  │   │
│  │  │  Responsibilities:                                     │  │   │
│  │  │  • Connection creation/destruction                     │  │   │
│  │  │  • Health checking                                     │  │   │
│  │  │  • Request queuing                                     │  │   │
│  │  │  • Load balancing                                      │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Pool Configuration

### Basic Configuration

```javascript
const { MongoClient } = require('mongodb')

// Node.js pool configuration
const client = new MongoClient('mongodb://localhost:27017', {
  // Pool size settings
  maxPoolSize: 100,        // Maximum connections per pool
  minPoolSize: 10,         // Minimum connections to maintain
  
  // Connection timeout settings
  connectTimeoutMS: 10000,       // Time to establish connection
  socketTimeoutMS: 45000,        // Socket inactivity timeout
  serverSelectionTimeoutMS: 30000, // Time to select server
  
  // Idle connection settings
  maxIdleTimeMS: 60000,    // Max time connection can be idle
  
  // Wait queue settings
  waitQueueTimeoutMS: 10000,  // Time to wait for available connection
  
  // Connection behavior
  retryWrites: true,
  retryReads: true,
  
  // Write concern
  w: 'majority',
  
  // Compression
  compressors: ['zstd', 'snappy', 'zlib']
})
```

### Python Pool Configuration

```python
from pymongo import MongoClient

client = MongoClient(
    'mongodb://localhost:27017',
    
    # Pool size
    maxPoolSize=100,
    minPoolSize=10,
    
    # Timeouts
    connectTimeoutMS=10000,
    socketTimeoutMS=45000,
    serverSelectionTimeoutMS=30000,
    
    # Idle settings
    maxIdleTimeMS=60000,
    
    # Wait queue
    waitQueueTimeoutMS=10000,
    
    # Retries
    retryWrites=True,
    retryReads=True,
    
    # Write concern
    w='majority'
)
```

### Environment-Based Configuration

```javascript
// Configuration based on deployment environment
function getPoolConfig(environment) {
  const configs = {
    development: {
      maxPoolSize: 10,
      minPoolSize: 2,
      maxIdleTimeMS: 30000,
      serverSelectionTimeoutMS: 5000
    },
    
    staging: {
      maxPoolSize: 50,
      minPoolSize: 5,
      maxIdleTimeMS: 60000,
      serverSelectionTimeoutMS: 10000
    },
    
    production: {
      maxPoolSize: 100,
      minPoolSize: 20,
      maxIdleTimeMS: 120000,
      serverSelectionTimeoutMS: 30000,
      waitQueueTimeoutMS: 15000
    },
    
    serverless: {
      // Serverless environments need smaller pools
      maxPoolSize: 10,
      minPoolSize: 0,
      maxIdleTimeMS: 10000,  // Short idle time
      serverSelectionTimeoutMS: 5000
    }
  }
  
  return configs[environment] || configs.development
}

// Usage
const config = getPoolConfig(process.env.NODE_ENV)
const client = new MongoClient(uri, config)
```

### Pool Size Calculation

```javascript
// Formula for calculating optimal pool size
function calculatePoolSize(options) {
  const {
    expectedConcurrentRequests,
    avgQueryTimeMs,
    requestsPerSecond,
    overheadFactor = 1.2
  } = options
  
  // Basic calculation: concurrent requests * overhead
  const basicSize = Math.ceil(expectedConcurrentRequests * overheadFactor)
  
  // Alternative: based on Little's Law
  // Pool size = arrival rate * average service time
  const littleLaw = Math.ceil((requestsPerSecond * avgQueryTimeMs / 1000) * overheadFactor)
  
  // Use the larger of the two
  const recommended = Math.max(basicSize, littleLaw)
  
  return {
    recommended,
    min: Math.ceil(recommended * 0.2),
    max: Math.ceil(recommended * 1.5)
  }
}

// Example
const poolSize = calculatePoolSize({
  expectedConcurrentRequests: 50,
  avgQueryTimeMs: 20,
  requestsPerSecond: 1000
})

console.log(poolSize)
// { recommended: 60, min: 12, max: 90 }
```

---

## Pool Monitoring

### Monitoring Pool Events

```javascript
const { MongoClient } = require('mongodb')

const client = new MongoClient(uri, {
  maxPoolSize: 50,
  minPoolSize: 5
})

// Connection pool events
client.on('connectionPoolCreated', (event) => {
  console.log('Pool created:', event.address)
})

client.on('connectionPoolClosed', (event) => {
  console.log('Pool closed:', event.address)
})

client.on('connectionCreated', (event) => {
  console.log('Connection created:', event.connectionId)
})

client.on('connectionReady', (event) => {
  console.log('Connection ready:', event.connectionId)
})

client.on('connectionClosed', (event) => {
  console.log('Connection closed:', event.connectionId, 'Reason:', event.reason)
})

client.on('connectionCheckOutStarted', (event) => {
  console.log('Checkout started:', event.address)
})

client.on('connectionCheckOutFailed', (event) => {
  console.log('Checkout failed:', event.reason)
})

client.on('connectionCheckedOut', (event) => {
  console.log('Connection checked out:', event.connectionId)
})

client.on('connectionCheckedIn', (event) => {
  console.log('Connection checked in:', event.connectionId)
})

client.on('connectionPoolCleared', (event) => {
  console.log('Pool cleared:', event.address)
})
```

### Pool Statistics Collector

```javascript
class PoolStatsCollector {
  constructor(client) {
    this.client = client
    this.stats = {
      totalCreated: 0,
      totalClosed: 0,
      checkouts: 0,
      checkins: 0,
      checkoutFailures: 0,
      checkoutWaitTime: [],
      activeConnections: 0,
      poolClears: 0
    }
    
    this.setupListeners()
  }
  
  setupListeners() {
    this.client.on('connectionCreated', () => {
      this.stats.totalCreated++
      this.stats.activeConnections++
    })
    
    this.client.on('connectionClosed', () => {
      this.stats.totalClosed++
      this.stats.activeConnections = Math.max(0, this.stats.activeConnections - 1)
    })
    
    this.client.on('connectionCheckOutStarted', (event) => {
      event._startTime = Date.now()
    })
    
    this.client.on('connectionCheckedOut', (event) => {
      this.stats.checkouts++
      if (event._startTime) {
        this.stats.checkoutWaitTime.push(Date.now() - event._startTime)
        // Keep last 1000 samples
        if (this.stats.checkoutWaitTime.length > 1000) {
          this.stats.checkoutWaitTime.shift()
        }
      }
    })
    
    this.client.on('connectionCheckedIn', () => {
      this.stats.checkins++
    })
    
    this.client.on('connectionCheckOutFailed', () => {
      this.stats.checkoutFailures++
    })
    
    this.client.on('connectionPoolCleared', () => {
      this.stats.poolClears++
    })
  }
  
  getStats() {
    const waitTimes = this.stats.checkoutWaitTime
    
    return {
      ...this.stats,
      checkoutWaitTime: undefined,  // Don't include raw data
      avgWaitTimeMs: waitTimes.length > 0 
        ? waitTimes.reduce((a, b) => a + b, 0) / waitTimes.length 
        : 0,
      maxWaitTimeMs: waitTimes.length > 0 ? Math.max(...waitTimes) : 0,
      p95WaitTimeMs: this.percentile(waitTimes, 95),
      utilizationRate: this.stats.checkouts > 0 
        ? ((this.stats.checkouts - this.stats.checkoutFailures) / this.stats.checkouts * 100).toFixed(2) + '%'
        : 'N/A'
    }
  }
  
  percentile(arr, p) {
    if (arr.length === 0) return 0
    const sorted = [...arr].sort((a, b) => a - b)
    const index = Math.ceil(arr.length * p / 100) - 1
    return sorted[index]
  }
  
  reset() {
    this.stats = {
      totalCreated: 0,
      totalClosed: 0,
      checkouts: 0,
      checkins: 0,
      checkoutFailures: 0,
      checkoutWaitTime: [],
      activeConnections: this.stats.activeConnections,
      poolClears: 0
    }
  }
}

// Usage
const statsCollector = new PoolStatsCollector(client)

// Expose stats endpoint
setInterval(() => {
  console.log('Pool Stats:', statsCollector.getStats())
}, 60000)
```

### Server Status Pool Info

```javascript
// Get pool information from server
async function getPoolInfo(client) {
  const admin = client.db('admin')
  
  // Server status
  const serverStatus = await admin.command({ serverStatus: 1 })
  
  // Current operations
  const currentOps = await admin.command({ currentOp: 1 })
  
  return {
    connections: {
      current: serverStatus.connections.current,
      available: serverStatus.connections.available,
      totalCreated: serverStatus.connections.totalCreated
    },
    network: {
      bytesIn: serverStatus.network.bytesIn,
      bytesOut: serverStatus.network.bytesOut,
      numRequests: serverStatus.network.numRequests
    },
    activeOperations: currentOps.inprog.length,
    operationsByType: currentOps.inprog.reduce((acc, op) => {
      acc[op.op] = (acc[op.op] || 0) + 1
      return acc
    }, {})
  }
}
```

---

## Connection Lifecycle

### Connection States

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Connection State Machine                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                     ┌─────────────┐                                 │
│                     │   Created   │                                 │
│                     └──────┬──────┘                                 │
│                            │                                        │
│                            ▼                                        │
│                     ┌─────────────┐                                 │
│                     │ Connecting  │                                 │
│                     └──────┬──────┘                                 │
│                            │                                        │
│              ┌─────────────┼─────────────┐                         │
│              │             │             │                          │
│              ▼             ▼             ▼                          │
│       ┌──────────┐  ┌──────────┐  ┌──────────┐                     │
│       │  Ready   │  │  Failed  │  │ Timeout  │                     │
│       │  (Idle)  │  │          │  │          │                     │
│       └────┬─────┘  └──────────┘  └──────────┘                     │
│            │                                                        │
│      ┌─────┴─────┐                                                 │
│      │           │                                                  │
│      ▼           ▼                                                  │
│ ┌─────────┐ ┌─────────┐                                            │
│ │ In Use  │ │ Closed  │ (idle timeout, pool clear, error)          │
│ │(Checked │ │         │                                            │
│ │  Out)   │ └─────────┘                                            │
│ └────┬────┘                                                        │
│      │                                                              │
│      ▼                                                              │
│ ┌─────────┐                                                        │
│ │Returned │ ──► Ready (Idle) or Closed                             │
│ │(Checked │                                                        │
│ │   In)   │                                                        │
│ └─────────┘                                                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Connection Health Checking

```javascript
// Custom health check implementation
class ConnectionHealthChecker {
  constructor(client, options = {}) {
    this.client = client
    this.options = {
      checkInterval: 30000,
      pingTimeout: 5000,
      maxFailures: 3,
      ...options
    }
    this.failures = 0
    this.lastCheck = null
    this.isHealthy = true
  }
  
  async start() {
    this.intervalId = setInterval(() => this.check(), this.options.checkInterval)
    await this.check()  // Initial check
  }
  
  stop() {
    if (this.intervalId) {
      clearInterval(this.intervalId)
    }
  }
  
  async check() {
    try {
      const start = Date.now()
      
      await Promise.race([
        this.client.db('admin').command({ ping: 1 }),
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Ping timeout')), this.options.pingTimeout)
        )
      ])
      
      this.lastCheck = {
        timestamp: new Date(),
        latencyMs: Date.now() - start,
        success: true
      }
      
      this.failures = 0
      this.isHealthy = true
      
    } catch (error) {
      this.failures++
      this.lastCheck = {
        timestamp: new Date(),
        error: error.message,
        success: false
      }
      
      if (this.failures >= this.options.maxFailures) {
        this.isHealthy = false
        this.onUnhealthy(error)
      }
    }
    
    return this.lastCheck
  }
  
  onUnhealthy(error) {
    console.error(`Connection unhealthy after ${this.failures} failures:`, error.message)
    // Implement alerting, failover, etc.
  }
  
  getStatus() {
    return {
      isHealthy: this.isHealthy,
      consecutiveFailures: this.failures,
      lastCheck: this.lastCheck
    }
  }
}
```

### Graceful Shutdown

```javascript
// Proper connection pool shutdown
class GracefulShutdown {
  constructor(client, options = {}) {
    this.client = client
    this.options = {
      timeout: 30000,
      ...options
    }
    this.isShuttingDown = false
    
    this.setupHandlers()
  }
  
  setupHandlers() {
    process.on('SIGTERM', () => this.shutdown('SIGTERM'))
    process.on('SIGINT', () => this.shutdown('SIGINT'))
    process.on('uncaughtException', (err) => {
      console.error('Uncaught exception:', err)
      this.shutdown('uncaughtException')
    })
  }
  
  async shutdown(signal) {
    if (this.isShuttingDown) {
      console.log('Shutdown already in progress')
      return
    }
    
    this.isShuttingDown = true
    console.log(`Received ${signal}, starting graceful shutdown...`)
    
    try {
      // Set a timeout for shutdown
      const shutdownPromise = this.performShutdown()
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Shutdown timeout')), this.options.timeout)
      )
      
      await Promise.race([shutdownPromise, timeoutPromise])
      
      console.log('Graceful shutdown completed')
      process.exit(0)
      
    } catch (error) {
      console.error('Error during shutdown:', error)
      process.exit(1)
    }
  }
  
  async performShutdown() {
    // 1. Stop accepting new requests
    console.log('Stopping new connections...')
    
    // 2. Wait for in-flight operations (application-specific)
    await this.waitForInFlightOperations()
    
    // 3. Close database connection
    console.log('Closing database connection...')
    await this.client.close()
    
    console.log('Database connection closed')
  }
  
  async waitForInFlightOperations() {
    // Implement based on your application
    // e.g., wait for HTTP server to drain, etc.
    return new Promise(resolve => setTimeout(resolve, 1000))
  }
}

// Usage
const client = new MongoClient(uri)
await client.connect()

const shutdown = new GracefulShutdown(client, { timeout: 30000 })
```

---

## Advanced Pooling Patterns

### Per-Tenant Connection Pools

```javascript
// Multi-tenant pool management
class TenantPoolManager {
  constructor(baseUri, defaultOptions = {}) {
    this.baseUri = baseUri
    this.defaultOptions = {
      maxPoolSize: 20,
      minPoolSize: 2,
      maxIdleTimeMS: 60000,
      ...defaultOptions
    }
    this.pools = new Map()
    this.lastAccess = new Map()
    
    // Cleanup inactive pools periodically
    this.cleanupInterval = setInterval(() => this.cleanup(), 300000)
  }
  
  async getPool(tenantId) {
    if (this.pools.has(tenantId)) {
      this.lastAccess.set(tenantId, Date.now())
      return this.pools.get(tenantId)
    }
    
    // Create new pool for tenant
    const client = new MongoClient(this.baseUri, {
      ...this.defaultOptions,
      appName: `tenant-${tenantId}`
    })
    
    await client.connect()
    
    this.pools.set(tenantId, client)
    this.lastAccess.set(tenantId, Date.now())
    
    console.log(`Created pool for tenant: ${tenantId}`)
    
    return client
  }
  
  async getDb(tenantId, dbName = null) {
    const client = await this.getPool(tenantId)
    const database = dbName || `tenant_${tenantId}`
    return client.db(database)
  }
  
  async cleanup() {
    const maxIdleTime = 600000  // 10 minutes
    const now = Date.now()
    
    for (const [tenantId, lastAccess] of this.lastAccess) {
      if (now - lastAccess > maxIdleTime) {
        await this.closePool(tenantId)
      }
    }
  }
  
  async closePool(tenantId) {
    const client = this.pools.get(tenantId)
    if (client) {
      await client.close()
      this.pools.delete(tenantId)
      this.lastAccess.delete(tenantId)
      console.log(`Closed pool for tenant: ${tenantId}`)
    }
  }
  
  async closeAll() {
    clearInterval(this.cleanupInterval)
    
    for (const [tenantId] of this.pools) {
      await this.closePool(tenantId)
    }
  }
  
  getStats() {
    return {
      activePools: this.pools.size,
      tenants: Array.from(this.pools.keys())
    }
  }
}

// Usage
const poolManager = new TenantPoolManager('mongodb://localhost:27017')

// In request handler
async function handleRequest(req, res) {
  const tenantId = req.headers['x-tenant-id']
  const db = await poolManager.getDb(tenantId)
  
  const data = await db.collection('items').find({}).toArray()
  res.json(data)
}
```

### Read/Write Split Pools

```javascript
// Separate pools for read and write operations
class ReadWritePoolManager {
  constructor(config) {
    this.writeClient = null
    this.readClient = null
    this.config = config
  }
  
  async initialize() {
    // Write pool - connects to primary
    this.writeClient = new MongoClient(this.config.writeUri, {
      maxPoolSize: this.config.writePoolSize || 50,
      readPreference: 'primary',
      w: 'majority'
    })
    
    // Read pool - connects to secondaries
    this.readClient = new MongoClient(this.config.readUri, {
      maxPoolSize: this.config.readPoolSize || 100,
      readPreference: 'secondaryPreferred'
    })
    
    await Promise.all([
      this.writeClient.connect(),
      this.readClient.connect()
    ])
    
    console.log('Read/Write pools initialized')
  }
  
  getWriteDb(dbName) {
    return this.writeClient.db(dbName)
  }
  
  getReadDb(dbName) {
    return this.readClient.db(dbName)
  }
  
  // Convenience method
  collection(dbName, collectionName) {
    return {
      // Write operations use write pool
      insertOne: (doc, options) => 
        this.getWriteDb(dbName).collection(collectionName).insertOne(doc, options),
      insertMany: (docs, options) => 
        this.getWriteDb(dbName).collection(collectionName).insertMany(docs, options),
      updateOne: (filter, update, options) => 
        this.getWriteDb(dbName).collection(collectionName).updateOne(filter, update, options),
      updateMany: (filter, update, options) => 
        this.getWriteDb(dbName).collection(collectionName).updateMany(filter, update, options),
      deleteOne: (filter, options) => 
        this.getWriteDb(dbName).collection(collectionName).deleteOne(filter, options),
      deleteMany: (filter, options) => 
        this.getWriteDb(dbName).collection(collectionName).deleteMany(filter, options),
      
      // Read operations use read pool
      find: (filter, options) => 
        this.getReadDb(dbName).collection(collectionName).find(filter, options),
      findOne: (filter, options) => 
        this.getReadDb(dbName).collection(collectionName).findOne(filter, options),
      countDocuments: (filter, options) => 
        this.getReadDb(dbName).collection(collectionName).countDocuments(filter, options),
      aggregate: (pipeline, options) => 
        this.getReadDb(dbName).collection(collectionName).aggregate(pipeline, options),
      
      // Force read from primary (for consistency)
      findFromPrimary: (filter, options) =>
        this.getWriteDb(dbName).collection(collectionName).findOne(filter, options)
    }
  }
  
  async close() {
    await Promise.all([
      this.writeClient?.close(),
      this.readClient?.close()
    ])
  }
}

// Usage
const pools = new ReadWritePoolManager({
  writeUri: 'mongodb://primary:27017',
  readUri: 'mongodb://secondary1:27017,secondary2:27017',
  writePoolSize: 50,
  readPoolSize: 100
})

await pools.initialize()

const users = pools.collection('myapp', 'users')

// Writes go to primary
await users.insertOne({ name: 'John' })

// Reads go to secondaries
const user = await users.findOne({ name: 'John' })

// Read from primary when consistency needed
const freshUser = await users.findFromPrimary({ name: 'John' })
```

---

## Troubleshooting

### Common Pool Issues

```javascript
// Issue: Connection timeout
// Symptom: "Server selection timed out"

// Solution: Increase timeouts or pool size
const client = new MongoClient(uri, {
  serverSelectionTimeoutMS: 30000,  // Increase from default
  maxPoolSize: 100,                  // More connections
  waitQueueTimeoutMS: 15000          // More time to wait
})

// Issue: Connection pool exhaustion
// Symptom: Requests waiting for connections

// Solution: Monitor and adjust pool size
async function diagnosePoolExhaustion(client) {
  const serverStatus = await client.db('admin').command({ serverStatus: 1 })
  
  console.log('Connection Stats:')
  console.log('  Current:', serverStatus.connections.current)
  console.log('  Available:', serverStatus.connections.available)
  console.log('  Total Created:', serverStatus.connections.totalCreated)
  
  // If current is near maxPoolSize and available is 0
  // Increase pool size or optimize queries
}

// Issue: Stale connections
// Symptom: Intermittent connection errors

// Solution: Configure proper idle timeout
const client = new MongoClient(uri, {
  maxIdleTimeMS: 30000,     // Close idle connections after 30s
  heartbeatFrequencyMS: 10000  // Check connection health every 10s
})

// Issue: Memory usage too high
// Symptom: High memory from too many connections

// Solution: Reduce pool size and configure pruning
const client = new MongoClient(uri, {
  maxPoolSize: 50,
  minPoolSize: 5,
  maxIdleTimeMS: 10000  // Aggressive idle cleanup
})
```

### Pool Diagnostic Tool

```javascript
async function diagnosePool(client) {
  console.log('╔════════════════════════════════════════════════════════════╗')
  console.log('║           CONNECTION POOL DIAGNOSTICS                       ║')
  console.log('╚════════════════════════════════════════════════════════════╝\n')
  
  try {
    // Server status
    const serverStatus = await client.db('admin').command({ serverStatus: 1 })
    
    console.log('┌─ SERVER CONNECTIONS ──────────────────────────────────────┐')
    console.log(`│  Current: ${serverStatus.connections.current}`.padEnd(60) + '│')
    console.log(`│  Available: ${serverStatus.connections.available}`.padEnd(60) + '│')
    console.log(`│  Total Created: ${serverStatus.connections.totalCreated}`.padEnd(60) + '│')
    console.log('└────────────────────────────────────────────────────────────┘\n')
    
    // Current operations
    const currentOps = await client.db('admin').command({ currentOp: 1 })
    const ops = currentOps.inprog
    
    const opsByType = ops.reduce((acc, op) => {
      acc[op.op] = (acc[op.op] || 0) + 1
      return acc
    }, {})
    
    console.log('┌─ ACTIVE OPERATIONS ───────────────────────────────────────┐')
    console.log(`│  Total: ${ops.length}`.padEnd(60) + '│')
    Object.entries(opsByType).forEach(([type, count]) => {
      console.log(`│    ${type}: ${count}`.padEnd(60) + '│')
    })
    console.log('└────────────────────────────────────────────────────────────┘\n')
    
    // Long running operations
    const longRunning = ops.filter(op => op.secs_running > 5)
    
    if (longRunning.length > 0) {
      console.log('┌─ LONG RUNNING OPERATIONS (>5s) ───────────────────────────┐')
      longRunning.forEach(op => {
        console.log(`│  ${op.op} on ${op.ns} - ${op.secs_running}s`.padEnd(60) + '│')
      })
      console.log('└────────────────────────────────────────────────────────────┘\n')
    }
    
    // Recommendations
    console.log('┌─ RECOMMENDATIONS ─────────────────────────────────────────┐')
    
    const utilization = serverStatus.connections.current / 
      (serverStatus.connections.current + serverStatus.connections.available) * 100
    
    if (utilization > 80) {
      console.log('│  ⚠️  High connection utilization (>80%)'.padEnd(60) + '│')
      console.log('│     Consider increasing maxPoolSize'.padEnd(60) + '│')
    }
    
    if (longRunning.length > 5) {
      console.log('│  ⚠️  Many long-running operations'.padEnd(60) + '│')
      console.log('│     Check query performance and indexes'.padEnd(60) + '│')
    }
    
    if (serverStatus.connections.available < 10) {
      console.log('│  ⚠️  Few available connections'.padEnd(60) + '│')
      console.log('│     Check for connection leaks'.padEnd(60) + '│')
    }
    
    console.log('│  ✓ Pool diagnostics complete'.padEnd(60) + '│')
    console.log('└────────────────────────────────────────────────────────────┘')
    
  } catch (error) {
    console.error('Diagnostic error:', error.message)
  }
}
```

---

## Summary

### Pool Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| maxPoolSize | 100 | Maximum connections |
| minPoolSize | 0 | Minimum connections to maintain |
| maxIdleTimeMS | 0 | Max idle time before closing |
| waitQueueTimeoutMS | 0 | Time to wait for available connection |
| connectTimeoutMS | 10000 | Time to establish connection |
| socketTimeoutMS | 0 | Socket inactivity timeout |

### Pool Sizing Guidelines

| Workload | maxPoolSize | minPoolSize |
|----------|-------------|-------------|
| Low traffic | 10-20 | 2-5 |
| Medium traffic | 50-100 | 10-20 |
| High traffic | 100-200 | 20-50 |
| Serverless | 5-10 | 0-1 |

### Best Practices

| Practice | Benefit |
|----------|---------|
| Monitor pool metrics | Early problem detection |
| Configure timeouts | Prevent hanging connections |
| Use appropriate pool size | Balance resources |
| Implement health checks | Detect unhealthy connections |
| Graceful shutdown | Clean resource cleanup |

---

## Practice Questions

1. What determines optimal connection pool size?
2. How does maxIdleTimeMS affect pool behavior?
3. What events can you monitor on a connection pool?
4. How do you handle connection pool exhaustion?
5. What is the purpose of minPoolSize?
6. How do read preferences affect pooling in replica sets?
7. When would you use per-tenant connection pools?
8. How do you diagnose pool-related performance issues?

---

[← Previous: Driver Best Practices](66-driver-best-practices.md) | [Next: Error Handling →](68-error-handling.md)
