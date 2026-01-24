# Chapter 46: Sharded Cluster Setup

## Table of Contents
- [Prerequisites](#prerequisites)
- [Development Setup](#development-setup)
- [Production Setup](#production-setup)
- [Enable Sharding](#enable-sharding)
- [Shard Collections](#shard-collections)
- [Verification](#verification)
- [Summary](#summary)

---

## Prerequisites

### Required Components

```
┌─────────────────────────────────────────────────────────────────────┐
│              Sharded Cluster Components                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Minimum Production Setup:                                         │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ CONFIG SERVERS (Replica Set)                            │       │
│  │ ├── config1:27019                                       │       │
│  │ ├── config2:27019                                       │       │
│  │ └── config3:27019                                       │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ SHARDS (Each a Replica Set)                             │       │
│  │                                                          │       │
│  │ Shard1-RS:        Shard2-RS:        (Add more as needed) │       │
│  │ ├── shard1a:27018 ├── shard2a:27018                     │       │
│  │ ├── shard1b:27018 ├── shard2b:27018                     │       │
│  │ └── shard1c:27018 └── shard2c:27018                     │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────┐       │
│  │ QUERY ROUTERS (mongos)                                  │       │
│  │ ├── mongos1:27017                                       │       │
│  │ └── mongos2:27017 (for HA)                              │       │
│  └─────────────────────────────────────────────────────────┘       │
│                                                                     │
│  Total: 3 config + 6 shard (2 shards × 3 members) + 2 mongos      │
│       = 11 servers minimum                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Port Conventions

| Component | Default Port | Range |
|-----------|--------------|-------|
| mongod (standalone) | 27017 | - |
| Shard servers | 27018 | 27018-27028 |
| Config servers | 27019 | 27019-27021 |
| mongos | 27017 | 27017 |

---

## Development Setup

### Single-Machine Development Cluster

```bash
# Create directories
mkdir -p ~/mongodb-cluster/{config1,config2,config3}
mkdir -p ~/mongodb-cluster/{shard1a,shard1b,shard1c}
mkdir -p ~/mongodb-cluster/{shard2a,shard2b,shard2c}
```

### Step 1: Start Config Server Replica Set

```bash
# Start config servers
mongod --configsvr --replSet configRS --port 27019 \
  --dbpath ~/mongodb-cluster/config1 \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/config1/mongod.log

mongod --configsvr --replSet configRS --port 27020 \
  --dbpath ~/mongodb-cluster/config2 \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/config2/mongod.log

mongod --configsvr --replSet configRS --port 27021 \
  --dbpath ~/mongodb-cluster/config3 \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/config3/mongod.log
```

```javascript
// Initialize config replica set
mongosh --port 27019

rs.initiate({
  _id: "configRS",
  configsvr: true,
  members: [
    { _id: 0, host: "localhost:27019" },
    { _id: 1, host: "localhost:27020" },
    { _id: 2, host: "localhost:27021" }
  ]
})

// Verify
rs.status()
```

### Step 2: Start Shard Replica Sets

```bash
# Shard 1 Replica Set
mongod --shardsvr --replSet shard1RS --port 27018 \
  --dbpath ~/mongodb-cluster/shard1a \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard1a/mongod.log

mongod --shardsvr --replSet shard1RS --port 27028 \
  --dbpath ~/mongodb-cluster/shard1b \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard1b/mongod.log

mongod --shardsvr --replSet shard1RS --port 27038 \
  --dbpath ~/mongodb-cluster/shard1c \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard1c/mongod.log

# Shard 2 Replica Set
mongod --shardsvr --replSet shard2RS --port 27118 \
  --dbpath ~/mongodb-cluster/shard2a \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard2a/mongod.log

mongod --shardsvr --replSet shard2RS --port 27128 \
  --dbpath ~/mongodb-cluster/shard2b \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard2b/mongod.log

mongod --shardsvr --replSet shard2RS --port 27138 \
  --dbpath ~/mongodb-cluster/shard2c \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/shard2c/mongod.log
```

```javascript
// Initialize Shard 1 RS
mongosh --port 27018

rs.initiate({
  _id: "shard1RS",
  members: [
    { _id: 0, host: "localhost:27018" },
    { _id: 1, host: "localhost:27028" },
    { _id: 2, host: "localhost:27038" }
  ]
})

// Initialize Shard 2 RS
mongosh --port 27118

rs.initiate({
  _id: "shard2RS",
  members: [
    { _id: 0, host: "localhost:27118" },
    { _id: 1, host: "localhost:27128" },
    { _id: 2, host: "localhost:27138" }
  ]
})
```

### Step 3: Start mongos Router

```bash
# Start mongos
mongos --configdb configRS/localhost:27019,localhost:27020,localhost:27021 \
  --port 27017 \
  --bind_ip localhost --fork \
  --logpath ~/mongodb-cluster/mongos.log
```

### Step 4: Add Shards to Cluster

```javascript
// Connect to mongos
mongosh --port 27017

// Add shards
sh.addShard("shard1RS/localhost:27018,localhost:27028,localhost:27038")
sh.addShard("shard2RS/localhost:27118,localhost:27128,localhost:27138")

// Verify
sh.status()
```

---

## Production Setup

### Configuration Files

#### Config Server Configuration

```yaml
# config-server.conf
systemLog:
  destination: file
  path: /var/log/mongodb/config.log
  logAppend: true

storage:
  dbPath: /var/lib/mongodb/config

net:
  port: 27019
  bindIp: 0.0.0.0

replication:
  replSetName: configRS

sharding:
  clusterRole: configsvr

security:
  keyFile: /etc/mongodb/cluster.key
  authorization: enabled
```

#### Shard Server Configuration

```yaml
# shard-server.conf
systemLog:
  destination: file
  path: /var/log/mongodb/shard.log
  logAppend: true

storage:
  dbPath: /var/lib/mongodb/shard
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4

net:
  port: 27018
  bindIp: 0.0.0.0

replication:
  replSetName: shard1RS

sharding:
  clusterRole: shardsvr

security:
  keyFile: /etc/mongodb/cluster.key
  authorization: enabled
```

#### mongos Configuration

```yaml
# mongos.conf
systemLog:
  destination: file
  path: /var/log/mongodb/mongos.log
  logAppend: true

net:
  port: 27017
  bindIp: 0.0.0.0

sharding:
  configDB: configRS/config1:27019,config2:27019,config3:27019

security:
  keyFile: /etc/mongodb/cluster.key
```

### Generate Key File

```bash
# Generate key file for authentication
openssl rand -base64 756 > /etc/mongodb/cluster.key
chmod 400 /etc/mongodb/cluster.key
chown mongodb:mongodb /etc/mongodb/cluster.key

# Copy to all servers
scp /etc/mongodb/cluster.key user@server:/etc/mongodb/
```

### Production Startup Sequence

```bash
# 1. Start all config servers
sudo systemctl start mongod-config

# 2. Initialize config replica set (on one config server)
mongosh --port 27019

# 3. Start all shard servers
sudo systemctl start mongod-shard

# 4. Initialize each shard replica set
# 5. Start mongos routers
sudo systemctl start mongos

# 6. Add shards through mongos
```

---

## Enable Sharding

### Enable Sharding on Database

```javascript
// Connect to mongos
mongosh --host mongos-server:27017

// Enable sharding for a database
sh.enableSharding("myDatabase")

// Or using admin command
use admin
db.runCommand({ enableSharding: "myDatabase" })

// Verify
sh.status()
// Look for:
// databases:
//   { "_id" : "myDatabase", "primary" : "shard1RS", "partitioned" : true }
```

### Set Primary Shard (Optional)

```javascript
// Move primary shard for a database
db.adminCommand({
  movePrimary: "myDatabase",
  to: "shard2RS"
})

// Primary shard stores:
// - Unsharded collections
// - First chunks of new sharded collections
```

---

## Shard Collections

### Basic Sharding

```javascript
// Create index first (required)
use myDatabase
db.orders.createIndex({ customerId: 1 })

// Shard the collection
sh.shardCollection("myDatabase.orders", { customerId: 1 })

// Or with admin command
db.adminCommand({
  shardCollection: "myDatabase.orders",
  key: { customerId: 1 }
})
```

### Hashed Shard Key

```javascript
// Create hashed index
db.users.createIndex({ _id: "hashed" })

// Shard with hashed key
sh.shardCollection("myDatabase.users", { _id: "hashed" })

// With number of initial chunks (pre-splitting)
sh.shardCollection(
  "myDatabase.logs",
  { _id: "hashed" },
  false,  // unique
  { numInitialChunks: 100 }
)
```

### Compound Shard Key

```javascript
// Create compound index
db.events.createIndex({ tenantId: 1, eventId: 1 })

// Shard with compound key
sh.shardCollection(
  "myDatabase.events",
  { tenantId: 1, eventId: 1 }
)
```

### Unique Shard Key

```javascript
// Unique shard key must be the shard key only
// or prefix of unique index

db.users.createIndex({ email: 1 }, { unique: true })

sh.shardCollection(
  "myDatabase.users",
  { email: 1 },
  true  // unique: true
)

// For compound unique:
db.orders.createIndex({ customerId: 1, orderId: 1 }, { unique: true })
sh.shardCollection(
  "myDatabase.orders",
  { customerId: 1, orderId: 1 },
  true
)
```

### Presplit Chunks

```javascript
// For known data distribution, presplit chunks
// Especially useful for bulk imports

// Split at specific points
sh.splitAt("myDatabase.orders", { customerId: "C100000" })
sh.splitAt("myDatabase.orders", { customerId: "C200000" })
sh.splitAt("myDatabase.orders", { customerId: "C300000" })

// Move chunks to specific shards
sh.moveChunk(
  "myDatabase.orders",
  { customerId: "C100000" },
  "shard2RS"
)
```

---

## Verification

### Cluster Status

```javascript
// Comprehensive status
sh.status()

// Detailed output
sh.status(true)

// Output includes:
// - Sharding version
// - Shards (names, hosts, state)
// - Active mongoses
// - Databases and their partitioning status
// - Sharded collections with chunk distribution
```

### Sample Status Output

```
--- Sharding Status ---
  sharding version: {
    "_id" : 1,
    "minCompatibleVersion" : 5,
    "currentVersion" : 6,
    "clusterId" : ObjectId("...")
  }
  
  shards:
    { "_id" : "shard1RS", "host" : "shard1RS/host1:27018,host2:27018,host3:27018", "state" : 1 }
    { "_id" : "shard2RS", "host" : "shard2RS/host4:27018,host5:27018,host6:27018", "state" : 1 }
    
  active mongoses:
    "5.0.0" : 2
    
  databases:
    { "_id" : "myDatabase", "primary" : "shard1RS", "partitioned" : true }
    
    myDatabase.orders
      shard key: { "customerId" : 1 }
      unique: false
      balancing: true
      chunks:
        shard1RS  3
        shard2RS  3
      { "customerId" : { "$minKey" : 1 } } -->> { "customerId" : "C100000" } on : shard1RS
      { "customerId" : "C100000" } -->> { "customerId" : "C200000" } on : shard1RS
      ...
```

### Verify Data Distribution

```javascript
// Check collection distribution
db.orders.getShardDistribution()

// Output:
// Shard shard1RS at shard1RS/host1:27018,host2:27018,host3:27018
//  data : 1.2GiB docs : 5000000 chunks : 45
//  estimated data per chunk : 27.3MiB
//  estimated docs per chunk : 111111

// Shard shard2RS at shard2RS/host4:27018,host5:27018,host6:27018
//  data : 1.1GiB docs : 4800000 chunks : 43
//  estimated data per chunk : 26.2MiB
//  estimated docs per chunk : 111627

// Totals
//  data : 2.3GiB docs : 9800000 chunks : 88
//  Shard shard1RS contains 52.04% data, 51.02% docs in cluster
//  Shard shard2RS contains 47.96% data, 48.98% docs in cluster
```

### Check Chunk Distribution

```javascript
// View chunks for a collection
use config
db.chunks.find({ ns: "myDatabase.orders" }).pretty()

// Count chunks per shard
db.chunks.aggregate([
  { $match: { ns: "myDatabase.orders" } },
  { $group: { _id: "$shard", count: { $sum: 1 } } }
])

// Find jumbo chunks
db.chunks.find({ 
  ns: "myDatabase.orders",
  jumbo: true 
})
```

### Query Routing Verification

```javascript
// Use explain to verify query routing
db.orders.find({ customerId: "C123" }).explain()

// Look for "shards" field in the output
// Single shard = targeted query
// Multiple shards = scatter-gather
```

---

## Summary

### Setup Sequence

| Step | Action | Command |
|------|--------|---------|
| 1 | Create directories | mkdir |
| 2 | Start config servers | mongod --configsvr |
| 3 | Init config RS | rs.initiate() |
| 4 | Start shard servers | mongod --shardsvr |
| 5 | Init shard RS | rs.initiate() |
| 6 | Start mongos | mongos --configdb |
| 7 | Add shards | sh.addShard() |
| 8 | Enable sharding | sh.enableSharding() |
| 9 | Shard collections | sh.shardCollection() |

### Configuration Options

| Component | Key Options |
|-----------|-------------|
| Config Server | --configsvr, --replSet |
| Shard Server | --shardsvr, --replSet |
| mongos | --configdb |

### Verification Commands

| Command | Purpose |
|---------|---------|
| sh.status() | Cluster overview |
| getShardDistribution() | Data distribution |
| db.chunks.find() | Chunk details |
| explain() | Query routing |

### What's Next?

In the next chapter, we'll explore Chunk Management in detail.

---

## Practice Questions

1. What components make up a sharded cluster?
2. Why are config servers a replica set?
3. What is the role of mongos?
4. How do you enable sharding on a database?
5. What must exist before sharding a collection?
6. How do you verify data distribution?
7. What is a primary shard?
8. How do you presplit chunks?

---

## Hands-On Exercises

### Exercise 1: Cluster Setup Script

```javascript
// Script to verify sharded cluster setup

function verifyClusterSetup() {
  print("=== Sharded Cluster Verification ===\n")
  
  // Check if connected to mongos
  const isMongos = db.runCommand({ ismaster: 1 }).msg === "isdbgrid"
  
  if (!isMongos) {
    print("✗ ERROR: Not connected to mongos")
    print("  Connect to mongos to verify cluster")
    return
  }
  
  print("✓ Connected to mongos\n")
  
  // Get cluster status
  const status = sh.status(true)
  
  // Check config servers
  print("Config Servers:")
  try {
    const configStatus = db.adminCommand({ 
      replSetGetStatus: 1, 
      $readPreference: { mode: "primary" } 
    })
    print(`  ✓ Config RS: Running`)
  } catch (e) {
    print(`  Status: Check config server logs`)
  }
  print()
  
  // Check shards
  print("Shards:")
  const shards = db.adminCommand({ listShards: 1 })
  
  if (shards.shards && shards.shards.length > 0) {
    shards.shards.forEach(shard => {
      const state = shard.state === 1 ? "✓ Active" : "! Check"
      print(`  ${state}: ${shard._id} - ${shard.host}`)
    })
  } else {
    print("  ✗ No shards found - use sh.addShard()")
  }
  print()
  
  // Check databases
  print("Sharded Databases:")
  const dbs = db.adminCommand({ listDatabases: 1 })
  let shardedDBCount = 0
  
  dbs.databases.forEach(dbInfo => {
    if (dbInfo.partitioned) {
      print(`  ✓ ${dbInfo.name} (partitioned)`)
      shardedDBCount++
    }
  })
  
  if (shardedDBCount === 0) {
    print("  None - use sh.enableSharding('dbName')")
  }
  print()
  
  // Check sharded collections
  print("Sharded Collections:")
  const collections = db.getSiblingDB("config").collections.find({ dropped: false })
  let collCount = 0
  
  collections.forEach(coll => {
    print(`  ✓ ${coll._id}`)
    print(`    Key: ${JSON.stringify(coll.key)}`)
    print(`    Unique: ${coll.unique || false}`)
    collCount++
  })
  
  if (collCount === 0) {
    print("  None - use sh.shardCollection()")
  }
  print()
  
  // Summary
  print("--- Summary ---")
  print(`  Shards: ${shards.shards?.length || 0}`)
  print(`  Sharded databases: ${shardedDBCount}`)
  print(`  Sharded collections: ${collCount}`)
}

// Run verification (must be connected to mongos)
// verifyClusterSetup()
```

### Exercise 2: Collection Sharding Helper

```javascript
// Helper to shard a collection with validation

function shardCollectionSafely(namespace, key, options = {}) {
  print(`=== Sharding Collection: ${namespace} ===\n`)
  
  const [dbName, collName] = namespace.split(".")
  const targetDb = db.getSiblingDB(dbName)
  
  // Step 1: Check if database is sharding-enabled
  print("Step 1: Checking database...")
  const dbInfo = db.getSiblingDB("config").databases.findOne({ _id: dbName })
  
  if (!dbInfo || !dbInfo.partitioned) {
    print(`  Enabling sharding for database: ${dbName}`)
    sh.enableSharding(dbName)
    print("  ✓ Database sharding enabled")
  } else {
    print("  ✓ Database already sharding-enabled")
  }
  
  // Step 2: Check if collection already sharded
  print("\nStep 2: Checking collection...")
  const collInfo = db.getSiblingDB("config").collections.findOne({ _id: namespace })
  
  if (collInfo && !collInfo.dropped) {
    print(`  ✗ Collection already sharded with key: ${JSON.stringify(collInfo.key)}`)
    return { success: false, reason: "Already sharded" }
  }
  print("  ✓ Collection not yet sharded")
  
  // Step 3: Check/create required index
  print("\nStep 3: Checking index...")
  const keyFields = Object.keys(key)
  const isHashed = Object.values(key).includes("hashed")
  
  const indexes = targetDb[collName].getIndexes()
  const hasIndex = indexes.some(idx => {
    const idxKeys = Object.keys(idx.key)
    return keyFields.every((k, i) => idxKeys[i] === k)
  })
  
  if (!hasIndex) {
    print(`  Creating index: ${JSON.stringify(key)}`)
    targetDb[collName].createIndex(key)
    print("  ✓ Index created")
  } else {
    print("  ✓ Required index exists")
  }
  
  // Step 4: Shard the collection
  print("\nStep 4: Sharding collection...")
  
  try {
    const result = sh.shardCollection(namespace, key, options.unique || false)
    
    if (result.ok) {
      print("  ✓ Collection sharded successfully")
    } else {
      print(`  ✗ Sharding failed: ${result.errmsg}`)
      return { success: false, reason: result.errmsg }
    }
  } catch (e) {
    print(`  ✗ Error: ${e.message}`)
    return { success: false, reason: e.message }
  }
  
  // Step 5: Verify
  print("\nStep 5: Verification...")
  const newCollInfo = db.getSiblingDB("config").collections.findOne({ _id: namespace })
  
  if (newCollInfo) {
    print(`  ✓ Shard key: ${JSON.stringify(newCollInfo.key)}`)
    print(`  ✓ Unique: ${newCollInfo.unique || false}`)
    
    // Count initial chunks
    const chunks = db.getSiblingDB("config").chunks.countDocuments({ ns: namespace })
    print(`  ✓ Initial chunks: ${chunks}`)
  }
  
  print("\n✓ Collection sharding complete!")
  return { success: true }
}

// Example usage:
// shardCollectionSafely("mydb.orders", { customerId: 1, orderId: 1 })
// shardCollectionSafely("mydb.users", { _id: "hashed" })
```

### Exercise 3: Data Distribution Monitor

```javascript
// Monitor data distribution across shards

function monitorDistribution(namespace) {
  print(`=== Data Distribution: ${namespace} ===\n`)
  
  const config = db.getSiblingDB("config")
  
  // Get shard list
  const shards = db.adminCommand({ listShards: 1 }).shards
  
  // Get chunk distribution
  const chunkDist = config.chunks.aggregate([
    { $match: { ns: namespace } },
    { $group: {
      _id: "$shard",
      chunks: { $sum: 1 },
      jumbo: { $sum: { $cond: ["$jumbo", 1, 0] } }
    }}
  ]).toArray()
  
  // Create distribution map
  const distribution = {}
  shards.forEach(s => {
    distribution[s._id] = { chunks: 0, jumbo: 0, percentage: 0 }
  })
  
  let totalChunks = 0
  chunkDist.forEach(d => {
    distribution[d._id] = d
    totalChunks += d.chunks
  })
  
  // Calculate percentages
  Object.keys(distribution).forEach(shard => {
    distribution[shard].percentage = 
      totalChunks > 0 ? (distribution[shard].chunks / totalChunks * 100).toFixed(1) : 0
  })
  
  // Display
  print("Chunk Distribution:\n")
  print("┌────────────────┬──────────┬────────────┬──────────┐")
  print("│ Shard          │ Chunks   │ Percentage │ Jumbo    │")
  print("├────────────────┼──────────┼────────────┼──────────┤")
  
  Object.entries(distribution).forEach(([shard, data]) => {
    const shardName = shard.padEnd(14)
    const chunks = String(data.chunks).padStart(8)
    const pct = (data.percentage + "%").padStart(10)
    const jumbo = String(data.jumbo).padStart(8)
    
    print(`│ ${shardName} │${chunks} │${pct} │${jumbo} │`)
  })
  
  print("└────────────────┴──────────┴────────────┴──────────┘")
  
  // Balance assessment
  print("\nBalance Assessment:")
  const percentages = Object.values(distribution).map(d => parseFloat(d.percentage))
  const maxPct = Math.max(...percentages)
  const minPct = Math.min(...percentages)
  const imbalance = maxPct - minPct
  
  if (imbalance < 10) {
    print(`  ✓ Well balanced (${imbalance.toFixed(1)}% difference)`)
  } else if (imbalance < 25) {
    print(`  ! Slightly imbalanced (${imbalance.toFixed(1)}% difference)`)
  } else {
    print(`  ✗ Significantly imbalanced (${imbalance.toFixed(1)}% difference)`)
  }
  
  // Jumbo chunk warning
  const totalJumbo = chunkDist.reduce((sum, d) => sum + d.jumbo, 0)
  if (totalJumbo > 0) {
    print(`  ⚠ Warning: ${totalJumbo} jumbo chunks detected`)
  }
  
  return distribution
}

// Usage (connected to mongos):
// monitorDistribution("mydb.orders")
```

### Exercise 4: Cluster Health Dashboard

```javascript
// Sharded cluster health dashboard

function clusterHealthDashboard() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           SHARDED CLUSTER HEALTH DASHBOARD                  ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Verify mongos connection
  const isMongos = db.runCommand({ ismaster: 1 }).msg === "isdbgrid"
  if (!isMongos) {
    print("ERROR: Connect to mongos to view cluster health")
    return
  }
  
  // Balancer status
  print("┌─ BALANCER STATUS ─────────────────────────────────────────┐")
  const balancerState = sh.getBalancerState()
  const balancerRunning = sh.isBalancerRunning()
  
  print(`│  Enabled: ${balancerState ? "Yes" : "No"}`.padEnd(60) + "│")
  print(`│  Running: ${balancerRunning ? "Yes" : "No"}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Shard status
  print("┌─ SHARD STATUS ────────────────────────────────────────────┐")
  const shards = db.adminCommand({ listShards: 1 }).shards || []
  
  shards.forEach(shard => {
    const status = shard.state === 1 ? "●" : "○"
    const line = `│  ${status} ${shard._id}: ${shard.host}`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  
  if (shards.length === 0) {
    print("│  No shards configured".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // mongos status
  print("┌─ MONGOS INSTANCES ────────────────────────────────────────┐")
  const mongoses = db.getSiblingDB("config").mongos.find().toArray()
  
  mongoses.forEach(m => {
    const age = Math.floor((new Date() - m.ping) / 1000 / 60)
    const status = age < 5 ? "●" : age < 60 ? "◐" : "○"
    const line = `│  ${status} ${m._id} (v${m.mongoVersion}, ping ${age}m ago)`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  
  if (mongoses.length === 0) {
    print("│  No mongos instances found".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Sharded collections summary
  print("┌─ SHARDED COLLECTIONS ─────────────────────────────────────┐")
  const collections = db.getSiblingDB("config").collections.find({ dropped: false }).toArray()
  
  collections.slice(0, 5).forEach(coll => {
    const chunks = db.getSiblingDB("config").chunks.countDocuments({ ns: coll._id })
    const line = `│  ${coll._id}: ${chunks} chunks`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  
  if (collections.length > 5) {
    print(`│  ... and ${collections.length - 5} more collections`.padEnd(60) + "│")
  }
  
  if (collections.length === 0) {
    print("│  No sharded collections".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Summary stats
  print("┌─ SUMMARY ─────────────────────────────────────────────────┐")
  const totalChunks = db.getSiblingDB("config").chunks.countDocuments()
  print(`│  Total Shards: ${shards.length}`.padEnd(60) + "│")
  print(`│  Total Collections: ${collections.length}`.padEnd(60) + "│")
  print(`│  Total Chunks: ${totalChunks}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  print("\nLast updated: " + new Date().toISOString())
}

// Run dashboard (must be connected to mongos)
// clusterHealthDashboard()
```

---

[← Previous: Shard Key Selection](45-shard-key-selection.md) | [Next: Chunk Management →](47-chunk-management.md)
