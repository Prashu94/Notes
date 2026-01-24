# Chapter 44: Sharding Concepts

## Table of Contents
- [What is Sharding](#what-is-sharding)
- [When to Shard](#when-to-shard)
- [Sharded Cluster Architecture](#sharded-cluster-architecture)
- [Shard Keys](#shard-keys)
- [Chunks and Balancing](#chunks-and-balancing)
- [Query Routing](#query-routing)
- [Summary](#summary)

---

## What is Sharding

Sharding is MongoDB's approach to horizontal scaling, distributing data across multiple machines.

### Scaling Approaches

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Scaling Strategies                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Vertical Scaling (Scale Up)                                       │
│  ┌───────────────┐                                                 │
│  │  ┌─────────┐  │                                                 │
│  │  │ MongoDB │  │ ← Bigger machine                                │
│  │  │ Server  │  │   More CPU, RAM, Disk                           │
│  │  └─────────┘  │                                                 │
│  │  64 CPU       │                                                 │
│  │  512 GB RAM   │                                                 │
│  │  10 TB SSD    │                                                 │
│  └───────────────┘                                                 │
│  Limits: Hardware caps, cost, single point of failure              │
│                                                                     │
│  Horizontal Scaling (Scale Out) - Sharding                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐              │
│  │ Shard 1 │  │ Shard 2 │  │ Shard 3 │  │ Shard N │              │
│  │  Data   │  │  Data   │  │  Data   │  │  Data   │              │
│  │  A-G    │  │  H-N    │  │  O-T    │  │  U-Z    │              │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘              │
│  Benefits: Linear scaling, no single hardware limit                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sharding Benefits

| Benefit | Description |
|---------|-------------|
| Horizontal scaling | Add servers to increase capacity |
| High throughput | Distribute operations across shards |
| Large datasets | Exceed single server storage |
| Geographic distribution | Place data near users |

### Sharding Challenges

| Challenge | Consideration |
|-----------|---------------|
| Complexity | More moving parts to manage |
| Shard key selection | Critical and difficult to change |
| Cross-shard queries | Can be slower |
| Transactions | Additional complexity |

---

## When to Shard

### Indicators for Sharding

```javascript
// Check if you might need sharding

function assessShardingNeed() {
  const stats = db.serverStatus()
  const dbStats = db.stats()
  
  const indicators = []
  
  // Data size indicator
  const dataSizeGB = dbStats.dataSize / (1024 * 1024 * 1024)
  if (dataSizeGB > 500) {
    indicators.push({
      issue: "Large data size",
      detail: `${dataSizeGB.toFixed(1)} GB - approaching single server limits`,
      severity: "high"
    })
  } else if (dataSizeGB > 200) {
    indicators.push({
      issue: "Growing data size",
      detail: `${dataSizeGB.toFixed(1)} GB - plan for sharding`,
      severity: "medium"
    })
  }
  
  // Throughput indicator
  const opsSec = stats.opcounters.query + stats.opcounters.insert + 
                 stats.opcounters.update + stats.opcounters.delete
  // This is total since startup - check rate separately
  
  // Working set vs RAM
  const cacheUsedPct = stats.wiredTiger?.cache["bytes currently in the cache"] /
    stats.wiredTiger?.cache["maximum bytes configured"] * 100
  
  if (cacheUsedPct > 95) {
    indicators.push({
      issue: "Cache pressure",
      detail: `${cacheUsedPct.toFixed(1)}% cache used - working set exceeds RAM`,
      severity: "high"
    })
  }
  
  // Connection indicator
  const connPct = stats.connections.current / stats.connections.available * 100
  if (connPct > 70) {
    indicators.push({
      issue: "Connection pressure",
      detail: `${connPct.toFixed(1)}% connections used`,
      severity: "medium"
    })
  }
  
  return {
    dataSizeGB: dataSizeGB.toFixed(2),
    indicators,
    recommendation: indicators.some(i => i.severity === "high") 
      ? "Consider sharding soon"
      : indicators.length > 0 
        ? "Monitor and plan for sharding"
        : "Sharding not immediately needed"
  }
}

// assessShardingNeed()
```

### Decision Matrix

| Factor | Shard | Don't Shard |
|--------|-------|-------------|
| Data size | > 500GB | < 200GB |
| Write throughput | Can't keep up | Acceptable |
| Working set | > Available RAM | Fits in RAM |
| Geographic requirements | Multi-region | Single region |
| Growth rate | Rapid | Stable |

### Alternatives to Sharding

```
┌─────────────────────────────────────────────────────────────────────┐
│            Before Sharding, Consider...                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Optimize Queries                                               │
│     ├── Add appropriate indexes                                    │
│     ├── Rewrite inefficient queries                                │
│     └── Use aggregation pipeline                                   │
│                                                                     │
│  2. Optimize Schema                                                │
│     ├── Denormalize where appropriate                              │
│     ├── Reduce document size                                       │
│     └── Archive old data                                           │
│                                                                     │
│  3. Hardware Upgrade                                               │
│     ├── More RAM (working set fits)                                │
│     ├── Faster storage (NVMe SSDs)                                 │
│     └── More CPU cores                                             │
│                                                                     │
│  4. Read Scaling                                                   │
│     ├── Add secondaries                                            │
│     └── Read from secondaries                                      │
│                                                                     │
│  5. Caching Layer                                                  │
│     ├── Redis/Memcached                                            │
│     └── Application-level cache                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Sharded Cluster Architecture

### Component Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Sharded Cluster Architecture                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                      Applications                                   │
│                          │                                          │
│                          ▼                                          │
│              ┌────────────────────┐                                │
│              │   Query Router(s)   │                                │
│              │      (mongos)       │                                │
│              └────────────────────┘                                │
│                   │        │                                        │
│        ┌──────────┘        └──────────┐                            │
│        ▼                              ▼                            │
│   ┌─────────┐                   ┌─────────┐                        │
│   │ Config  │                   │ Config  │  Config Servers        │
│   │ Server  │◄─────────────────►│ Server  │  (Replica Set)         │
│   └─────────┘                   └─────────┘                        │
│                                                                     │
│        ┌──────────────────────────────────┐                        │
│        │                                  │                        │
│        ▼                                  ▼                        │
│   ┌──────────┐    ┌──────────┐    ┌──────────┐                    │
│   │  Shard   │    │  Shard   │    │  Shard   │  Data Shards       │
│   │(RS: A-G) │    │(RS: H-N) │    │(RS: O-Z) │  (Replica Sets)    │
│   └──────────┘    └──────────┘    └──────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Components

#### 1. Shards

```javascript
// Shards store the data
// Each shard is a replica set for high availability

// Shard contains:
// - Subset of sharded data (based on shard key ranges)
// - Unsharded collections (on primary shard)

// Check shard information
sh.status()
```

#### 2. Config Servers

```javascript
// Config servers store cluster metadata
// - Shard key ranges (chunks)
// - Shard locations
// - Cluster configuration

// Config server replica set (CSRS)
// Always a 3-member replica set

// Metadata stored in:
db.getSiblingDB("config").collections.find()
db.getSiblingDB("config").chunks.find()
db.getSiblingDB("config").shards.find()
```

#### 3. Query Routers (mongos)

```javascript
// mongos routes queries to appropriate shards
// Stateless - can have multiple for HA

// mongos responsibilities:
// - Parse queries
// - Determine target shards
// - Route and merge results
// - Handle scatter-gather queries

// Applications connect to mongos, not directly to shards
// mongodb://mongos1:27017,mongos2:27017/database
```

### Minimum Production Deployment

```
┌─────────────────────────────────────────────────────────────────────┐
│           Minimum Production Sharded Cluster                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Query Routers (mongos)                                            │
│  ├── mongos-1 (Primary access point)                               │
│  └── mongos-2 (Backup/Load balancing)                              │
│                                                                     │
│  Config Servers (Replica Set)                                      │
│  ├── config-1                                                      │
│  ├── config-2                                                      │
│  └── config-3                                                      │
│                                                                     │
│  Shard 1 (Replica Set)     Shard 2 (Replica Set)                  │
│  ├── shard1-1 (Primary)    ├── shard2-1 (Primary)                 │
│  ├── shard1-2 (Secondary)  ├── shard2-2 (Secondary)               │
│  └── shard1-3 (Secondary)  └── shard2-3 (Secondary)               │
│                                                                     │
│  Total: 2 mongos + 3 config + 6 shard members = 11 servers        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Shard Keys

### What is a Shard Key

```javascript
// Shard key determines how data is distributed
// It's an indexed field (or fields) in every document

// Example: Shard by userId
{
  _id: ObjectId("..."),
  userId: "user123",    // ← Shard key
  name: "Alice",
  email: "alice@example.com"
}

// MongoDB uses shard key to:
// 1. Determine which shard holds the data
// 2. Route queries efficiently
// 3. Distribute data evenly
```

### Shard Key Properties

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Good Shard Key Properties                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. HIGH CARDINALITY                                               │
│     ├── Many unique values                                         │
│     ├── Enables fine-grained distribution                          │
│     └── Example: userId, orderId, timestamp + other field          │
│                                                                     │
│  2. EVEN DISTRIBUTION                                              │
│     ├── Data spreads evenly across shards                          │
│     ├── No "hot spots" on single shard                             │
│     └── Example: Hashed keys, compound keys                        │
│                                                                     │
│  3. QUERY ISOLATION                                                │
│     ├── Common queries target single shard                         │
│     ├── Avoids scatter-gather queries                              │
│     └── Example: Key matches common query patterns                 │
│                                                                     │
│  4. WRITE SCALING                                                  │
│     ├── Writes distribute across shards                            │
│     ├── No single shard bottleneck                                 │
│     └── Example: Avoid monotonic keys for insert-heavy            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Shard Key Types

#### Ranged Shard Key

```javascript
// Data divided by key value ranges
sh.shardCollection("mydb.orders", { orderId: 1 })

// Distribution:
// Shard1: orderId 1-1000000
// Shard2: orderId 1000001-2000000
// Shard3: orderId 2000001-3000000

// Pros:
// - Range queries on shard key are efficient
// - Data locality for related documents

// Cons:
// - Can create hot spots with monotonic keys
// - Uneven distribution possible
```

#### Hashed Shard Key

```javascript
// Data distributed by hash of key value
sh.shardCollection("mydb.users", { _id: "hashed" })

// Distribution:
// Hash values spread randomly across shards
// Even distribution regardless of key pattern

// Pros:
// - Even data distribution
// - Good for monotonic keys (ObjectId, timestamps)
// - Write scaling

// Cons:
// - Range queries hit all shards
// - No data locality
```

#### Compound Shard Key

```javascript
// Multiple fields in shard key
sh.shardCollection("mydb.logs", { appId: 1, timestamp: 1 })

// Distribution based on combination:
// Shard1: appId=A, various timestamps
// Shard2: appId=B, various timestamps

// Pros:
// - Query isolation for common patterns
// - Better cardinality than single field
// - Can optimize for both reads and writes
```

### Shard Key Selection

```javascript
// Example: E-commerce orders

// Option 1: Order ID (monotonic - bad for writes)
{ orderId: 1 }
// All new inserts go to one shard

// Option 2: Hashed Order ID (good distribution, no range)
{ _id: "hashed" }
// Even distribution but scatter-gather for date ranges

// Option 3: Customer ID (query isolation)
{ customerId: 1 }
// Customer queries go to single shard
// Large customers create hot spots

// Option 4: Compound (balanced approach)
{ customerId: 1, orderId: 1 }
// Customer queries isolated
// Orders spread within customer
// Good balance of reads and writes
```

---

## Chunks and Balancing

### What are Chunks

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Chunks in Sharding                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Collection Data                                                   │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z          │ │
│  └───────────────────────────────────────────────────────────────┘ │
│                              │                                      │
│                              ▼                                      │
│               Split into Chunks (by shard key)                     │
│                                                                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐     │
│  │ Chunk 1 │ │ Chunk 2 │ │ Chunk 3 │ │ Chunk 4 │ │ Chunk 5 │     │
│  │  A-E    │ │  F-J    │ │  K-O    │ │  P-T    │ │  U-Z    │     │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────┘     │
│       │           │           │           │           │            │
│       ▼           ▼           ▼           ▼           ▼            │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                             │
│  │ Shard 1 │ │ Shard 2 │ │ Shard 3 │                             │
│  │ C1, C2  │ │ C3, C4  │ │   C5    │                             │
│  └─────────┘ └─────────┘ └─────────┘                             │
│                                                                     │
│  Default chunk size: 128 MB (configurable)                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Chunk Operations

```javascript
// View chunks
use config
db.chunks.find({ ns: "mydb.orders" })

// Chunk document example
{
  _id: "mydb.orders-orderId_MinKey",
  ns: "mydb.orders",
  min: { orderId: MinKey },
  max: { orderId: 1000000 },
  shard: "shard1",
  lastmod: Timestamp(1, 0)
}

// Chunk size configuration
use config
db.settings.save({ _id: "chunksize", value: 64 })  // 64 MB chunks
```

### Chunk Splitting

```javascript
// Chunks split when they exceed chunk size
// Splitting is automatic

// Manual split (if needed)
sh.splitAt("mydb.orders", { orderId: 500000 })
sh.splitFind("mydb.orders", { orderId: 250000 })

// View split points
db.chunks.find({ ns: "mydb.orders" }).sort({ min: 1 })
```

### Balancer

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Balancer Operation                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Before Balancing:                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                            │
│  │ Shard 1 │  │ Shard 2 │  │ Shard 3 │                            │
│  │ 100     │  │  20     │  │  30     │  (chunks)                  │
│  │ chunks  │  │ chunks  │  │ chunks  │                            │
│  └─────────┘  └─────────┘  └─────────┘                            │
│      ↓                                                             │
│  Balancer detects imbalance                                        │
│      ↓                                                             │
│  After Balancing:                                                  │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐                            │
│  │ Shard 1 │  │ Shard 2 │  │ Shard 3 │                            │
│  │  50     │  │  50     │  │  50     │                            │
│  │ chunks  │  │ chunks  │  │ chunks  │                            │
│  └─────────┘  └─────────┘  └─────────┘                            │
│                                                                     │
│  Threshold: Migration starts when difference > 2 chunks            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

```javascript
// Balancer commands
sh.getBalancerState()          // Check if enabled
sh.isBalancerRunning()         // Check if currently running

// Enable/disable balancer
sh.startBalancer()
sh.stopBalancer()

// Set balancer window (maintenance)
use config
db.settings.update(
  { _id: "balancer" },
  { $set: { activeWindow: { start: "02:00", stop: "06:00" } } },
  { upsert: true }
)
```

---

## Query Routing

### Targeted vs Scatter-Gather

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Query Routing Types                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  TARGETED QUERY (Efficient)                                        │
│  Query includes shard key                                          │
│                                                                     │
│     mongos                                                         │
│       │                                                            │
│       │ find({ customerId: "C123" })                               │
│       │                                                            │
│       ▼                                                            │
│    ┌─────────┐                                                     │
│    │ Shard 2 │ ◄── Direct to single shard                         │
│    └─────────┘                                                     │
│                                                                     │
│  SCATTER-GATHER (Less Efficient)                                   │
│  Query doesn't include shard key                                   │
│                                                                     │
│     mongos                                                         │
│       │                                                            │
│       │ find({ status: "active" })                                 │
│       │                                                            │
│       ├──────────┬──────────┬──────────┐                          │
│       ▼          ▼          ▼          ▼                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐                 │
│  │ Shard 1 │ │ Shard 2 │ │ Shard 3 │ │ Shard 4 │                 │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘                 │
│       │          │          │          │                          │
│       └──────────┴──────────┴──────────┘                          │
│                      │                                             │
│                      ▼                                             │
│                   mongos merges results                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Query Routing Examples

```javascript
// Shard key: { customerId: 1, orderId: 1 }

// Targeted queries (efficient):
db.orders.find({ customerId: "C123" })                    // ✓ Shard key prefix
db.orders.find({ customerId: "C123", orderId: "O456" })   // ✓ Full shard key
db.orders.find({ customerId: { $in: ["C1", "C2"] } })     // ✓ Multiple targets

// Scatter-gather queries (less efficient):
db.orders.find({ status: "pending" })           // ✗ No shard key
db.orders.find({ orderId: "O456" })             // ✗ Not key prefix
db.orders.find({}).sort({ createdAt: -1 })      // ✗ Full scan

// Explain shows routing
db.orders.find({ customerId: "C123" }).explain()
// Look for "shards" field to see targeted shards
```

### Optimizing Query Routing

```javascript
// Strategy 1: Always include shard key in queries
// If shard key is customerId:
db.orders.find({ customerId: "C123", status: "pending" })  // ✓ Good

// Strategy 2: Use compound shard key matching query patterns
// Common query: find by customerId and date range
// Good shard key: { customerId: 1, orderDate: 1 }

// Strategy 3: Consider zone sharding for data locality
sh.addShardToZone("shard1", "US")
sh.addShardToZone("shard2", "EU")
sh.updateZoneKeyRange("mydb.orders",
  { region: "US", orderId: MinKey },
  { region: "US", orderId: MaxKey },
  "US"
)
```

---

## Summary

### Sharding Components

| Component | Purpose | Count |
|-----------|---------|-------|
| Shard | Store data | 2+ (replica sets) |
| Config Server | Store metadata | 1 (3-member RS) |
| mongos | Route queries | 1+ (stateless) |

### Shard Key Characteristics

| Characteristic | Good | Bad |
|----------------|------|-----|
| Cardinality | High (many values) | Low (few values) |
| Distribution | Even | Skewed |
| Query Isolation | Matches queries | Random |
| Write Distribution | Spread writes | Hot spots |

### Chunk Management

| Operation | Description |
|-----------|-------------|
| Splitting | Divides large chunks |
| Migration | Moves chunks between shards |
| Balancing | Evens chunk distribution |

### What's Next?

In the next chapter, we'll dive deep into Shard Key Selection strategies.

---

## Practice Questions

1. What is horizontal scaling?
2. When should you consider sharding?
3. What are the three components of a sharded cluster?
4. What is a shard key?
5. What's the difference between ranged and hashed shard keys?
6. What is a chunk?
7. What does the balancer do?
8. What's the difference between targeted and scatter-gather queries?

---

## Hands-On Exercises

### Exercise 1: Sharding Decision Assessment

```javascript
// Assess whether a database needs sharding

function shardingAssessment(dbName) {
  print(`=== Sharding Assessment: ${dbName} ===\n`)
  
  const targetDb = db.getSiblingDB(dbName)
  const dbStats = targetDb.stats()
  
  // Data size
  const dataSizeGB = dbStats.dataSize / (1024 * 1024 * 1024)
  print(`Data Size: ${dataSizeGB.toFixed(2)} GB`)
  
  // Index size
  const indexSizeGB = dbStats.indexSize / (1024 * 1024 * 1024)
  print(`Index Size: ${indexSizeGB.toFixed(2)} GB`)
  
  // Collections
  const collections = targetDb.getCollectionNames()
  print(`Collections: ${collections.length}`)
  
  // Large collections
  print("\nLarge Collections (potential shard candidates):")
  collections.forEach(c => {
    const collStats = targetDb[c].stats()
    const sizeGB = collStats.size / (1024 * 1024 * 1024)
    if (sizeGB > 0.1) {  // > 100MB
      print(`  ${c}: ${sizeGB.toFixed(2)} GB, ${collStats.count} docs`)
    }
  })
  
  // Assessment
  print("\n--- Assessment ---")
  
  const recommendations = []
  
  if (dataSizeGB > 500) {
    recommendations.push("CRITICAL: Data exceeds 500GB - sharding recommended")
  } else if (dataSizeGB > 200) {
    recommendations.push("WARNING: Data exceeds 200GB - plan for sharding")
  } else if (dataSizeGB > 100) {
    recommendations.push("INFO: Data > 100GB - monitor growth rate")
  } else {
    recommendations.push("OK: Data size manageable without sharding")
  }
  
  if (recommendations.length === 0) {
    print("  ✓ No immediate sharding need detected")
  } else {
    recommendations.forEach(r => print(`  ${r}`))
  }
}

// Assess current database
// shardingAssessment("mydb")
```

### Exercise 2: Shard Key Analyzer

```javascript
// Analyze potential shard keys for a collection

function analyzeShardKeys(collectionName, fields) {
  print(`=== Shard Key Analysis: ${collectionName} ===\n`)
  
  const coll = db[collectionName]
  const count = coll.countDocuments()
  
  print(`Total Documents: ${count}\n`)
  
  fields.forEach(field => {
    print(`Field: ${field}`)
    print("-".repeat(40))
    
    // Cardinality
    const distinct = coll.distinct(field).length
    const cardinalityPct = (distinct / count * 100).toFixed(1)
    print(`  Cardinality: ${distinct} unique values (${cardinalityPct}%)`)
    
    // Distribution (top 5 values)
    const distribution = coll.aggregate([
      { $group: { _id: `$${field}`, count: { $sum: 1 } } },
      { $sort: { count: -1 } },
      { $limit: 5 }
    ]).toArray()
    
    print("  Top 5 values:")
    distribution.forEach(d => {
      const pct = (d.count / count * 100).toFixed(1)
      print(`    ${d._id}: ${d.count} (${pct}%)`)
    })
    
    // Check for nulls
    const nullCount = coll.countDocuments({ [field]: null })
    if (nullCount > 0) {
      print(`  ⚠ NULL values: ${nullCount}`)
    }
    
    // Monotonic check (for ObjectId-like fields)
    if (field === "_id") {
      print("  ⚠ Monotonic: Yes (ObjectId) - consider hashing")
    }
    
    // Score
    let score = 0
    if (cardinalityPct > 50) score += 3
    else if (cardinalityPct > 10) score += 2
    else score += 1
    
    const maxPct = distribution[0]?.count / count * 100 || 0
    if (maxPct < 5) score += 3
    else if (maxPct < 20) score += 2
    else score += 1
    
    print(`  Shard Key Score: ${score}/6`)
    print()
  })
}

// Create sample data
db.shardKeyTest.drop()
for (let i = 0; i < 1000; i++) {
  db.shardKeyTest.insertOne({
    userId: `user_${Math.floor(Math.random() * 100)}`,
    category: ["electronics", "clothing", "food", "books"][Math.floor(Math.random() * 4)],
    orderId: `order_${i}`,
    timestamp: new Date(Date.now() - Math.random() * 86400000 * 30)
  })
}

// Analyze potential shard keys
analyzeShardKeys("shardKeyTest", ["userId", "category", "orderId"])
```

### Exercise 3: Query Routing Simulator

```javascript
// Simulate query routing in a sharded cluster

print("=== Query Routing Simulator ===\n")

// Simulated cluster with 3 shards
const shards = {
  shard1: { min: "A", max: "I" },
  shard2: { min: "I", max: "Q" },
  shard3: { min: "Q", max: "{" }  // '{' is after 'Z' in ASCII
}

// Shard key: { customerId: 1 }
function routeQuery(query) {
  const result = {
    query: JSON.stringify(query),
    targetShards: [],
    routingType: "unknown"
  }
  
  // Check if query includes shard key
  if (query.customerId) {
    // Targeted routing
    const firstChar = query.customerId.charAt(0).toUpperCase()
    
    for (const [shard, range] of Object.entries(shards)) {
      if (firstChar >= range.min && firstChar < range.max) {
        result.targetShards.push(shard)
        break
      }
    }
    
    result.routingType = "targeted"
  } else {
    // Scatter-gather
    result.targetShards = Object.keys(shards)
    result.routingType = "scatter-gather"
  }
  
  return result
}

// Test queries
const queries = [
  { customerId: "Alice", status: "active" },
  { customerId: "Bob", orderId: "123" },
  { customerId: "Zara" },
  { status: "pending" },
  { orderId: "456" },
  { customerId: "Mike", date: { $gt: new Date("2024-01-01") } }
]

print("Shard Ranges:")
print("  shard1: A-H")
print("  shard2: I-P")
print("  shard3: Q-Z")
print()

print("Query Routing Results:\n")

queries.forEach((q, i) => {
  const result = routeQuery(q)
  const icon = result.routingType === "targeted" ? "✓" : "!"
  
  print(`${i + 1}. ${result.query}`)
  print(`   ${icon} Routing: ${result.routingType}`)
  print(`   Shards: ${result.targetShards.join(", ")}`)
  print()
})

print("Recommendation:")
print("  ✓ Always include customerId in queries for optimal routing")
```

### Exercise 4: Chunk Distribution Visualizer

```javascript
// Visualize chunk distribution across shards

print("=== Chunk Distribution Visualizer ===\n")

// Simulated chunk distribution
const chunkDistribution = {
  shard1: { chunks: 45, collections: { orders: 20, users: 15, products: 10 } },
  shard2: { chunks: 42, collections: { orders: 22, users: 12, products: 8 } },
  shard3: { chunks: 38, collections: { orders: 18, users: 10, products: 10 } }
}

const totalChunks = Object.values(chunkDistribution)
  .reduce((sum, s) => sum + s.chunks, 0)

// Visualization
print("Chunk Distribution by Shard:\n")

Object.entries(chunkDistribution).forEach(([shard, data]) => {
  const pct = (data.chunks / totalChunks * 100).toFixed(1)
  const barLength = Math.floor(data.chunks / 2)
  const bar = "█".repeat(barLength)
  
  print(`${shard}: ${bar} ${data.chunks} (${pct}%)`)
})

print()

// Balance assessment
const chunks = Object.values(chunkDistribution).map(s => s.chunks)
const maxChunks = Math.max(...chunks)
const minChunks = Math.min(...chunks)
const difference = maxChunks - minChunks

print("Balance Assessment:")
print(`  Max chunks: ${maxChunks}`)
print(`  Min chunks: ${minChunks}`)
print(`  Difference: ${difference}`)

if (difference <= 2) {
  print("  ✓ Cluster is well balanced")
} else if (difference <= 8) {
  print("  ! Cluster is slightly imbalanced - balancer will correct")
} else {
  print("  ✗ Cluster is imbalanced - check balancer status")
}

print()

// Collection breakdown
print("Chunks by Collection:\n")

const collectionTotals = {}
Object.values(chunkDistribution).forEach(shard => {
  Object.entries(shard.collections).forEach(([coll, count]) => {
    collectionTotals[coll] = (collectionTotals[coll] || 0) + count
  })
})

Object.entries(collectionTotals)
  .sort((a, b) => b[1] - a[1])
  .forEach(([coll, count]) => {
    const bar = "█".repeat(Math.floor(count / 3))
    print(`  ${coll.padEnd(12)}: ${bar} ${count}`)
  })
```

### Exercise 5: Sharding Capacity Planner

```javascript
// Plan sharding capacity

function capacityPlanner(params) {
  print("=== Sharding Capacity Planner ===\n")
  
  const {
    currentDataGB,
    monthlyGrowthGB,
    targetMonths,
    maxShardGB,
    replicationFactor
  } = params
  
  print("Input Parameters:")
  print(`  Current data: ${currentDataGB} GB`)
  print(`  Monthly growth: ${monthlyGrowthGB} GB`)
  print(`  Planning period: ${targetMonths} months`)
  print(`  Max shard size: ${maxShardGB} GB`)
  print(`  Replication factor: ${replicationFactor}x`)
  print()
  
  // Calculate projections
  const projections = []
  
  for (let month = 0; month <= targetMonths; month++) {
    const dataSize = currentDataGB + (monthlyGrowthGB * month)
    const storageNeeded = dataSize * replicationFactor
    const shardsNeeded = Math.ceil(dataSize / maxShardGB)
    
    projections.push({ month, dataSize, storageNeeded, shardsNeeded })
  }
  
  // Display projections
  print("Growth Projections:")
  print("┌───────┬──────────────┬─────────────────┬──────────────┐")
  print("│ Month │ Data (GB)    │ Storage (GB)    │ Shards       │")
  print("├───────┼──────────────┼─────────────────┼──────────────┤")
  
  projections.forEach(p => {
    if (p.month % 3 === 0 || p.month === targetMonths) {
      const month = String(p.month).padStart(5)
      const data = p.dataSize.toFixed(0).padStart(12)
      const storage = p.storageNeeded.toFixed(0).padStart(15)
      const shards = String(p.shardsNeeded).padStart(12)
      
      print(`│${month} │${data} │${storage} │${shards} │`)
    }
  })
  
  print("└───────┴──────────────┴─────────────────┴──────────────┘")
  
  // Recommendations
  const finalProjection = projections[projections.length - 1]
  
  print("\nRecommendations:")
  print(`  • Start with ${Math.max(2, projections[0].shardsNeeded)} shards`)
  print(`  • Plan for ${finalProjection.shardsNeeded} shards by month ${targetMonths}`)
  print(`  • Total storage needed: ${finalProjection.storageNeeded.toFixed(0)} GB`)
  print(`  • Consider adding shard every ${Math.floor(targetMonths / (finalProjection.shardsNeeded - projections[0].shardsNeeded + 1))} months`)
  
  return projections
}

// Example: E-commerce platform planning
capacityPlanner({
  currentDataGB: 200,
  monthlyGrowthGB: 50,
  targetMonths: 24,
  maxShardGB: 500,
  replicationFactor: 3
})
```

---

[← Previous: Replica Set Maintenance](43-replica-set-maintenance.md) | [Next: Shard Key Selection →](45-shard-key-selection.md)
