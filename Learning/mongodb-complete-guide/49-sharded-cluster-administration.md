# Chapter 49: Sharded Cluster Administration

## Table of Contents
- [Cluster Maintenance](#cluster-maintenance)
- [Adding and Removing Shards](#adding-and-removing-shards)
- [Zone Sharding](#zone-sharding)
- [Monitoring](#monitoring)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)
- [Summary](#summary)

---

## Cluster Maintenance

### Health Check Routine

```javascript
// Comprehensive cluster health check

function clusterHealthCheck() {
  print("=== Sharded Cluster Health Check ===\n")
  
  let healthy = true
  
  // 1. Check mongos connection
  print("1. Connection Check")
  const isMongos = db.runCommand({ ismaster: 1 }).msg === "isdbgrid"
  if (!isMongos) {
    print("   ✗ NOT connected to mongos")
    return false
  }
  print("   ✓ Connected to mongos")
  
  // 2. Check config servers
  print("\n2. Config Servers")
  try {
    const configStatus = db.adminCommand({
      replSetGetStatus: 1,
      $readPreference: { mode: "nearest" }
    })
    print("   ✓ Config replica set responding")
  } catch (e) {
    print("   ! Unable to check config RS directly")
  }
  
  // 3. Check shards
  print("\n3. Shards")
  const shards = db.adminCommand({ listShards: 1 })
  let shardIssues = 0
  
  shards.shards.forEach(shard => {
    if (shard.state === 1) {
      print(`   ✓ ${shard._id}: Active`)
    } else {
      print(`   ✗ ${shard._id}: State ${shard.state}`)
      shardIssues++
      healthy = false
    }
  })
  
  // 4. Balancer status
  print("\n4. Balancer")
  const balancerState = sh.getBalancerState()
  const balancerRunning = sh.isBalancerRunning()
  print(`   Enabled: ${balancerState}`)
  print(`   Running: ${balancerRunning}`)
  
  // 5. Chunk distribution
  print("\n5. Chunk Distribution")
  const dist = db.getSiblingDB("config").chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  if (dist.length > 0) {
    const maxDiff = dist[0].count - dist[dist.length - 1].count
    dist.forEach(d => print(`   ${d._id}: ${d.count} chunks`))
    print(`   Imbalance: ${maxDiff} chunks`)
    
    if (maxDiff > 20) {
      print("   ! Significant imbalance")
      healthy = false
    }
  }
  
  // 6. Jumbo chunks
  print("\n6. Jumbo Chunks")
  const jumbo = db.getSiblingDB("config").chunks.countDocuments({ jumbo: true })
  if (jumbo === 0) {
    print("   ✓ No jumbo chunks")
  } else {
    print(`   ⚠ ${jumbo} jumbo chunks found`)
  }
  
  // Summary
  print("\n" + "=".repeat(40))
  if (healthy) {
    print("✓ Cluster is HEALTHY")
  } else {
    print("✗ Cluster has ISSUES - review above")
  }
  
  return healthy
}

clusterHealthCheck()
```

### Rolling Restart

```javascript
// Steps for rolling restart of sharded cluster

/*
Rolling Restart Procedure:

1. DISABLE BALANCER
   sh.stopBalancer()
   // Wait for active migrations to complete
   while (sh.isBalancerRunning()) { sleep(1000) }

2. RESTART EACH SHARD (one at a time)
   For each shard replica set:
   a. Restart secondaries (one at a time)
      - mongod --shutdown on secondary
      - Wait for it to come back
      - Verify rs.status() shows it as SECONDARY
   
   b. Step down and restart primary
      - rs.stepDown()
      - mongod --shutdown
      - Restart and verify

3. RESTART CONFIG SERVERS
   Same procedure as shards:
   - Secondaries first
   - Then primary

4. RESTART MONGOS (can do in parallel)
   - Simply restart each mongos
   - Applications will reconnect

5. RE-ENABLE BALANCER
   sh.startBalancer()

IMPORTANT:
- Always maintain majority in each replica set
- Monitor cluster during process
- Have rollback plan ready
*/
```

### Configuration Changes

```javascript
// Common configuration changes

// 1. Update chunk size
use config
db.settings.updateOne(
  { _id: "chunksize" },
  { $set: { value: 64 } },  // 64 MB
  { upsert: true }
)

// 2. Set balancer window
db.settings.updateOne(
  { _id: "balancer" },
  { $set: { 
    activeWindow: { start: "02:00", stop: "06:00" }
  }},
  { upsert: true }
)

// 3. Disable balancing for collection
sh.disableBalancing("mydb.orders")

// 4. Check current settings
db.settings.find().pretty()
```

---

## Adding and Removing Shards

### Adding a New Shard

```javascript
// Step 1: Set up new shard replica set (on new servers)
// mongod --shardsvr --replSet newShardRS --port 27018 --dbpath /data/db

// Step 2: Initialize the new replica set
// mongosh --port 27018
rs.initiate({
  _id: "newShardRS",
  members: [
    { _id: 0, host: "newhost1:27018" },
    { _id: 1, host: "newhost2:27018" },
    { _id: 2, host: "newhost3:27018" }
  ]
})

// Step 3: Add shard to cluster (from mongos)
sh.addShard("newShardRS/newhost1:27018,newhost2:27018,newhost3:27018")

// Step 4: Verify
sh.status()

// Step 5: Balancer will automatically migrate chunks to new shard
// Monitor:
db.getSiblingDB("config").changelog.find({
  what: "moveChunk.commit"
}).sort({ time: -1 }).limit(10)
```

### Removing a Shard

```javascript
// Step 1: Start draining the shard
db.adminCommand({ removeShard: "shardToRemove" })

// Response shows draining status:
// {
//   "msg" : "draining started successfully",
//   "state" : "started",
//   "shard" : "shardToRemove",
//   "note" : "you need to drop or movePrimary these databases",
//   "dbsToMove" : [ "testdb" ]  // Databases with primary shard here
// }

// Step 2: Move primary for affected databases
db.adminCommand({
  movePrimary: "testdb",
  to: "otherShard"
})

// Step 3: Monitor draining progress
db.adminCommand({ removeShard: "shardToRemove" })
// Check "remaining" field for chunks left to migrate

// Step 4: Wait for draining to complete
// The shard is removed automatically when all chunks are migrated

// Monitor draining:
function monitorDraining(shardName) {
  while (true) {
    const status = db.adminCommand({ removeShard: shardName })
    
    if (status.state === "completed") {
      print("✓ Shard removal complete")
      break
    }
    
    print(`Remaining chunks: ${status.remaining?.chunks || 0}`)
    print(`Remaining dbs: ${status.remaining?.dbs || 0}`)
    sleep(30000)  // Check every 30 seconds
  }
}
```

### Cancel Shard Removal

```javascript
// If you need to cancel shard removal
// Re-add the shard
sh.addShard("shardToRemove/host1:27018,host2:27018,host3:27018")
```

---

## Zone Sharding

### Understanding Zones

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Zone Sharding                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Zones associate shard key ranges with specific shards              │
│                                                                     │
│  Example: Geographic Data Locality                                  │
│                                                                     │
│  ┌─────────────────┐     ┌─────────────────┐                       │
│  │   US Zone       │     │   EU Zone       │                       │
│  │                 │     │                 │                       │
│  │  ┌───────────┐  │     │  ┌───────────┐  │                       │
│  │  │ shard-us1 │  │     │  │ shard-eu1 │  │                       │
│  │  └───────────┘  │     │  └───────────┘  │                       │
│  │  ┌───────────┐  │     │  ┌───────────┐  │                       │
│  │  │ shard-us2 │  │     │  │ shard-eu2 │  │                       │
│  │  └───────────┘  │     │  └───────────┘  │                       │
│  │                 │     │                 │                       │
│  │  region: "US"   │     │  region: "EU"   │                       │
│  └─────────────────┘     └─────────────────┘                       │
│                                                                     │
│  Users in US → Data on US shards → Low latency                     │
│  Users in EU → Data on EU shards → Low latency                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Configure Zones

```javascript
// Step 1: Add shards to zones
sh.addShardToZone("shard-us1", "US")
sh.addShardToZone("shard-us2", "US")
sh.addShardToZone("shard-eu1", "EU")
sh.addShardToZone("shard-eu2", "EU")

// Step 2: Define zone ranges for collection
// Shard key must include the zone field
sh.updateZoneKeyRange(
  "mydb.users",                          // namespace
  { region: "US", _id: MinKey },         // min key
  { region: "US", _id: MaxKey },         // max key
  "US"                                   // zone name
)

sh.updateZoneKeyRange(
  "mydb.users",
  { region: "EU", _id: MinKey },
  { region: "EU", _id: MaxKey },
  "EU"
)

// Step 3: Shard the collection with appropriate key
sh.shardCollection("mydb.users", { region: 1, _id: 1 })

// Verify zones
sh.status()
```

### Zone Use Cases

```javascript
// Use Case 1: Geographic data residency
// Keep EU data in EU data centers for GDPR compliance
sh.addShardToZone("eu-shard1", "EU")
sh.addShardToZone("eu-shard2", "EU")
sh.updateZoneKeyRange("db.customers", 
  { country: "DE", _id: MinKey }, 
  { country: "DE", _id: MaxKey }, 
  "EU"
)

// Use Case 2: Tiered storage
// Recent data on fast storage, old data on slower storage
sh.addShardToZone("shard-ssd", "hot")
sh.addShardToZone("shard-hdd", "cold")

sh.updateZoneKeyRange("db.logs",
  { timestamp: new Date("2024-01-01"), _id: MinKey },
  { timestamp: new Date("2099-12-31"), _id: MaxKey },
  "hot"
)

sh.updateZoneKeyRange("db.logs",
  { timestamp: new Date("2000-01-01"), _id: MinKey },
  { timestamp: new Date("2024-01-01"), _id: MaxKey },
  "cold"
)

// Use Case 3: Hardware-based partitioning
// Large documents on shards with more storage
sh.addShardToZone("big-storage-shard", "large-docs")
sh.updateZoneKeyRange("db.files",
  { size: 1000000, _id: MinKey },  // > 1MB
  { size: MaxKey, _id: MaxKey },
  "large-docs"
)
```

### Remove Zones

```javascript
// Remove zone range
sh.removeRangeFromZone(
  "mydb.users",
  { region: "US", _id: MinKey },
  { region: "US", _id: MaxKey }
)

// Remove shard from zone
sh.removeShardFromZone("shard-us1", "US")
```

---

## Monitoring

### Key Metrics

```javascript
// Essential monitoring queries

// 1. Cluster overview
sh.status()

// 2. Shard statistics
db.adminCommand({ listShards: 1 })

// 3. Database statistics
db.stats()

// 4. Collection statistics
db.collection.stats()

// 5. Current operations
db.currentOp()

// 6. Server status
db.serverStatus()
```

### Monitoring Script

```javascript
function monitorCluster() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           SHARDED CLUSTER MONITOR                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Shards
  print("┌─ SHARDS ──────────────────────────────────────────────────┐")
  const shards = db.adminCommand({ listShards: 1 }).shards || []
  shards.forEach(s => {
    const status = s.state === 1 ? "●" : "○"
    const line = `│  ${status} ${s._id}: ${s.host}`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Chunks per shard
  print("┌─ CHUNK DISTRIBUTION ──────────────────────────────────────┐")
  const dist = db.getSiblingDB("config").chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  const total = dist.reduce((sum, d) => sum + d.count, 0)
  dist.forEach(d => {
    const pct = (d.count / total * 100).toFixed(1)
    const bar = "█".repeat(Math.floor(d.count / dist[0].count * 20))
    const line = `│  ${d._id}: ${bar} ${d.count} (${pct}%)`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Balancer
  print("┌─ BALANCER ────────────────────────────────────────────────┐")
  print(`│  Enabled: ${sh.getBalancerState()}`.padEnd(60) + "│")
  print(`│  Running: ${sh.isBalancerRunning()}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recent activity
  print("┌─ ACTIVITY (last hour) ────────────────────────────────────┐")
  const hour = new Date(Date.now() - 60 * 60 * 1000)
  const migrations = db.getSiblingDB("config").changelog.countDocuments({
    what: "moveChunk.commit",
    time: { $gte: hour }
  })
  const splits = db.getSiblingDB("config").changelog.countDocuments({
    what: "split",
    time: { $gte: hour }
  })
  print(`│  Migrations: ${migrations}`.padEnd(60) + "│")
  print(`│  Splits: ${splits}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  print("\nUpdated: " + new Date().toISOString())
}

monitorCluster()
```

### Alerts Configuration

```javascript
// Alert thresholds
const alerts = {
  chunkImbalance: 20,      // Alert if difference > 20 chunks
  jumboChunks: 5,          // Alert if > 5 jumbo chunks
  shardDownMinutes: 5,     // Alert if shard down > 5 min
  migrationFailures: 10    // Alert if > 10 failures per hour
}

function checkAlerts() {
  const issues = []
  
  // Check chunk imbalance
  const dist = db.getSiblingDB("config").chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  if (dist.length > 1) {
    const diff = dist[0].count - dist[dist.length - 1].count
    if (diff > alerts.chunkImbalance) {
      issues.push(`High chunk imbalance: ${diff}`)
    }
  }
  
  // Check jumbo chunks
  const jumbo = db.getSiblingDB("config").chunks.countDocuments({ jumbo: true })
  if (jumbo > alerts.jumboChunks) {
    issues.push(`High jumbo chunk count: ${jumbo}`)
  }
  
  // Check migration failures
  const failures = db.getSiblingDB("config").changelog.countDocuments({
    what: "moveChunk.from",
    "details.errmsg": { $exists: true },
    time: { $gte: new Date(Date.now() - 60 * 60 * 1000) }
  })
  if (failures > alerts.migrationFailures) {
    issues.push(`High migration failures: ${failures}`)
  }
  
  return issues
}
```

---

## Backup and Recovery

### Backup Strategy

```
┌─────────────────────────────────────────────────────────────────────┐
│               Sharded Cluster Backup Strategy                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Option 1: Consistent Backup (Recommended)                         │
│  ─────────────────────────────────────────                         │
│  1. Stop balancer                                                  │
│  2. Back up config servers                                         │
│  3. Back up each shard simultaneously                              │
│  4. Re-enable balancer                                             │
│                                                                     │
│  Option 2: Per-Shard Backup                                        │
│  ─────────────────────────────                                     │
│  - Back up each shard independently                                │
│  - Back up config servers                                          │
│  - Less consistent but simpler                                     │
│                                                                     │
│  Option 3: MongoDB Atlas/Ops Manager                               │
│  ────────────────────────────────────                              │
│  - Automated consistent backups                                    │
│  - Point-in-time recovery                                          │
│  - Recommended for production                                      │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Manual Backup Procedure

```javascript
// Step 1: Stop the balancer
sh.stopBalancer()

// Wait for balancer to stop
while (sh.isBalancerRunning()) {
  print("Waiting for balancer to stop...")
  sleep(1000)
}
print("Balancer stopped")

// Step 2: Lock all shards (optional for filesystem snapshots)
// On each shard:
// db.fsyncLock()

// Step 3: Perform backups
// Config servers: mongodump --host configRS/config1,config2,config3 --out /backup/config
// Each shard: mongodump --host shardRS/shard1,shard2,shard3 --out /backup/shard

// Step 4: Unlock shards (if locked)
// db.fsyncUnlock()

// Step 5: Re-enable balancer
sh.startBalancer()
```

### Restore Procedure

```javascript
/*
Restore Steps:

1. Stop all mongos instances

2. Restore config servers
   mongorestore --host configRS/config1,config2,config3 /backup/config

3. Restore each shard
   mongorestore --host shard1RS/shard1a,shard1b,shard1c /backup/shard1
   mongorestore --host shard2RS/shard2a,shard2b,shard2c /backup/shard2

4. Start mongos instances

5. Verify
   sh.status()

6. Enable balancer
   sh.startBalancer()
*/
```

---

## Troubleshooting

### Common Issues

#### Shard Unreachable

```javascript
// Check shard status
db.adminCommand({ listShards: 1 })

// If shard shows state != 1:
// 1. Check network connectivity to shard
// 2. Check if shard replica set is healthy
// 3. Verify shard servers are running
// 4. Check mongos logs for connection errors
```

#### Migrations Failing

```javascript
// Check recent migration errors
db.getSiblingDB("config").changelog.find({
  what: "moveChunk.from",
  "details.errmsg": { $exists: true }
}).sort({ time: -1 }).limit(5)

// Common causes:
// - Network issues between shards
// - Disk full on destination
// - Jumbo chunks
// - Concurrent operations on chunk
```

#### Balancer Not Working

```javascript
// Diagnostic steps
sh.getBalancerState()      // Should be true
sh.isBalancerRunning()     // Check if active

// Check balancer lock
db.getSiblingDB("config").locks.findOne({ _id: "balancer" })

// Check for disabled collections
db.getSiblingDB("config").collections.find({ noBalance: true })

// Check active window
db.getSiblingDB("config").settings.findOne({ _id: "balancer" })
```

### Diagnostic Script

```javascript
function clusterDiagnostics() {
  print("=== Cluster Diagnostics ===\n")
  
  const issues = []
  
  // 1. Shards
  print("1. Shard Status:")
  const shards = db.adminCommand({ listShards: 1 }).shards || []
  shards.forEach(s => {
    if (s.state !== 1) {
      issues.push(`Shard ${s._id} has state ${s.state}`)
      print(`   ✗ ${s._id}: ISSUE (state: ${s.state})`)
    } else {
      print(`   ✓ ${s._id}: OK`)
    }
  })
  
  // 2. Balancer
  print("\n2. Balancer:")
  if (!sh.getBalancerState()) {
    issues.push("Balancer is disabled")
    print("   ✗ Disabled")
  } else {
    print("   ✓ Enabled")
  }
  
  // 3. Distribution
  print("\n3. Chunk Distribution:")
  const dist = db.getSiblingDB("config").chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  if (dist.length > 1) {
    const diff = dist[0].count - dist[dist.length - 1].count
    if (diff > 20) {
      issues.push(`High imbalance: ${diff} chunks difference`)
      print(`   ✗ Imbalanced (diff: ${diff})`)
    } else {
      print(`   ✓ Balanced (diff: ${diff})`)
    }
  }
  
  // 4. Jumbo chunks
  print("\n4. Jumbo Chunks:")
  const jumbo = db.getSiblingDB("config").chunks.countDocuments({ jumbo: true })
  if (jumbo > 0) {
    issues.push(`${jumbo} jumbo chunks`)
    print(`   ⚠ ${jumbo} jumbo chunks found`)
  } else {
    print("   ✓ None")
  }
  
  // 5. Recent errors
  print("\n5. Recent Errors (1 hour):")
  const errors = db.getSiblingDB("config").changelog.find({
    "details.errmsg": { $exists: true },
    time: { $gte: new Date(Date.now() - 60 * 60 * 1000) }
  }).toArray()
  
  if (errors.length > 0) {
    issues.push(`${errors.length} errors in last hour`)
    print(`   ⚠ ${errors.length} errors`)
    errors.slice(0, 3).forEach(e => {
      print(`     - ${e.what}: ${e.details.errmsg}`)
    })
  } else {
    print("   ✓ None")
  }
  
  // Summary
  print("\n" + "=".repeat(40))
  if (issues.length === 0) {
    print("✓ No issues detected")
  } else {
    print(`✗ ${issues.length} issue(s) found:`)
    issues.forEach(i => print(`  - ${i}`))
  }
  
  return issues
}

clusterDiagnostics()
```

---

## Summary

### Administration Tasks

| Task | Command |
|------|---------|
| Add shard | sh.addShard() |
| Remove shard | removeShard |
| Enable balancer | sh.startBalancer() |
| Disable balancer | sh.stopBalancer() |
| Add zone | sh.addShardToZone() |
| Set zone range | sh.updateZoneKeyRange() |

### Monitoring Points

| Metric | Check |
|--------|-------|
| Shard health | listShards |
| Chunk distribution | config.chunks |
| Balancer status | sh.getBalancerState() |
| Migration activity | config.changelog |
| Jumbo chunks | chunks.jumbo |

### Best Practices

| Practice | Reason |
|----------|--------|
| Regular health checks | Early problem detection |
| Monitor chunk distribution | Prevent hot spots |
| Plan shard additions | Smooth scaling |
| Test backup/restore | Disaster recovery |
| Document configurations | Operational clarity |

### What's Next?

In the next chapter, we'll begin Part 10: Security with Authentication.

---

## Practice Questions

1. How do you add a new shard to a cluster?
2. What is the process for removing a shard?
3. What are zones and when would you use them?
4. How do you back up a sharded cluster?
5. What should you monitor in a sharded cluster?
6. How do you troubleshoot failed migrations?
7. When should you disable the balancer?
8. How do you check cluster health?

---

## Hands-On Exercises

### Exercise 1: Cluster Administration Toolkit

```javascript
// Create a reusable administration toolkit

const ClusterAdmin = {
  
  // Health check
  healthCheck: function() {
    print("=== Health Check ===")
    const shards = db.adminCommand({ listShards: 1 }).shards || []
    const healthy = shards.filter(s => s.state === 1).length
    print(`Shards: ${healthy}/${shards.length} healthy`)
    print(`Balancer: ${sh.getBalancerState() ? "enabled" : "disabled"}`)
    return healthy === shards.length
  },
  
  // Show distribution
  distribution: function() {
    print("=== Chunk Distribution ===")
    const dist = db.getSiblingDB("config").chunks.aggregate([
      { $group: { _id: "$shard", count: { $sum: 1 } } },
      { $sort: { count: -1 } }
    ]).toArray()
    
    dist.forEach(d => {
      print(`  ${d._id}: ${d.count} chunks`)
    })
  },
  
  // Show zones
  zones: function() {
    print("=== Zones ===")
    const tags = db.getSiblingDB("config").tags.find().toArray()
    
    if (tags.length === 0) {
      print("  No zones configured")
    } else {
      tags.forEach(t => {
        print(`  ${t.ns}: ${t.tag}`)
        print(`    ${JSON.stringify(t.min)} → ${JSON.stringify(t.max)}`)
      })
    }
  },
  
  // Recent activity
  activity: function(hours = 1) {
    print(`=== Activity (last ${hours}h) ===`)
    const since = new Date(Date.now() - hours * 60 * 60 * 1000)
    
    const migrations = db.getSiblingDB("config").changelog.countDocuments({
      what: "moveChunk.commit",
      time: { $gte: since }
    })
    
    const splits = db.getSiblingDB("config").changelog.countDocuments({
      what: "split",
      time: { $gte: since }
    })
    
    print(`  Migrations: ${migrations}`)
    print(`  Splits: ${splits}`)
  },
  
  // Pre-maintenance
  preMaintenance: function() {
    print("=== Pre-Maintenance ===")
    sh.stopBalancer()
    
    // Wait for migrations
    let attempts = 0
    while (sh.isBalancerRunning() && attempts < 60) {
      print("  Waiting for migrations to complete...")
      sleep(5000)
      attempts++
    }
    
    print("  ✓ Balancer stopped")
    print("  Ready for maintenance")
  },
  
  // Post-maintenance
  postMaintenance: function() {
    print("=== Post-Maintenance ===")
    sh.startBalancer()
    print("  ✓ Balancer started")
    this.healthCheck()
  }
}

// Usage:
// ClusterAdmin.healthCheck()
// ClusterAdmin.distribution()
// ClusterAdmin.zones()
// ClusterAdmin.activity(24)
// ClusterAdmin.preMaintenance()
// ClusterAdmin.postMaintenance()
```

### Exercise 2: Zone Configuration Helper

```javascript
// Helper for setting up zone sharding

function configureZones(config) {
  print("=== Zone Configuration ===\n")
  
  const { namespace, shardKey, zones } = config
  
  // Validate
  if (!namespace || !shardKey || !zones || zones.length === 0) {
    print("Error: Invalid configuration")
    print("Required: namespace, shardKey, zones[]")
    return false
  }
  
  print(`Namespace: ${namespace}`)
  print(`Shard Key: ${JSON.stringify(shardKey)}`)
  print()
  
  // Configure each zone
  zones.forEach(zone => {
    print(`Setting up zone: ${zone.name}`)
    
    // Add shards to zone
    zone.shards.forEach(shard => {
      print(`  Adding ${shard} to zone ${zone.name}`)
      sh.addShardToZone(shard, zone.name)
    })
    
    // Set zone ranges
    zone.ranges.forEach(range => {
      print(`  Adding range: ${JSON.stringify(range.min)} → ${JSON.stringify(range.max)}`)
      sh.updateZoneKeyRange(namespace, range.min, range.max, zone.name)
    })
    
    print()
  })
  
  // Verify
  print("=== Verification ===")
  
  // Show shard-zone mappings
  const shardTags = db.getSiblingDB("config").shards.find({}, { tags: 1 }).toArray()
  print("\nShard-Zone Mappings:")
  shardTags.forEach(s => {
    print(`  ${s._id}: ${(s.tags || []).join(", ") || "none"}`)
  })
  
  // Show zone ranges
  const tags = db.getSiblingDB("config").tags.find({ ns: namespace }).toArray()
  print("\nZone Ranges:")
  tags.forEach(t => {
    print(`  ${t.tag}: ${JSON.stringify(t.min)} → ${JSON.stringify(t.max)}`)
  })
  
  return true
}

// Example usage:
/*
configureZones({
  namespace: "mydb.users",
  shardKey: { region: 1, _id: 1 },
  zones: [
    {
      name: "US",
      shards: ["shard-us1", "shard-us2"],
      ranges: [
        { min: { region: "US", _id: MinKey }, max: { region: "US", _id: MaxKey } }
      ]
    },
    {
      name: "EU",
      shards: ["shard-eu1", "shard-eu2"],
      ranges: [
        { min: { region: "EU", _id: MinKey }, max: { region: "EU", _id: MaxKey } }
      ]
    }
  ]
})
*/
```

### Exercise 3: Shard Capacity Planner

```javascript
// Plan shard capacity and additions

function capacityPlanner(options = {}) {
  print("=== Shard Capacity Planner ===\n")
  
  const {
    targetGrowthMonths = 12,
    maxShardSizeGB = 500,
    replicationFactor = 3
  } = options
  
  // Get current state
  const shards = db.adminCommand({ listShards: 1 }).shards || []
  print(`Current Shards: ${shards.length}`)
  
  // Calculate current data per shard (estimate)
  let totalDataGB = 0
  const databases = db.adminCommand({ listDatabases: 1 }).databases
  databases.forEach(dbInfo => {
    totalDataGB += dbInfo.sizeOnDisk / (1024 * 1024 * 1024)
  })
  
  const dataPerShardGB = totalDataGB / shards.length
  print(`Total Data: ${totalDataGB.toFixed(2)} GB`)
  print(`Per Shard (avg): ${dataPerShardGB.toFixed(2)} GB`)
  print()
  
  // Get recent growth (simplified - use metrics for real calculation)
  print("Growth Projections:")
  
  // Assume 20% monthly growth for example
  const monthlyGrowthRate = 0.2
  
  let projectedData = totalDataGB
  let shardsNeeded = shards.length
  
  for (let month = 1; month <= targetGrowthMonths; month++) {
    projectedData *= (1 + monthlyGrowthRate)
    const neededShards = Math.ceil(projectedData / maxShardSizeGB)
    
    if (neededShards > shardsNeeded) {
      print(`  Month ${month}: ${projectedData.toFixed(0)} GB - ADD ${neededShards - shardsNeeded} shard(s)`)
      shardsNeeded = neededShards
    } else if (month % 3 === 0) {
      print(`  Month ${month}: ${projectedData.toFixed(0)} GB - ${shardsNeeded} shards OK`)
    }
  }
  
  print()
  print("Summary:")
  print(`  Current shards: ${shards.length}`)
  print(`  Shards needed in ${targetGrowthMonths} months: ${shardsNeeded}`)
  print(`  Shards to add: ${shardsNeeded - shards.length}`)
  print(`  Storage per shard: ${(projectedData * replicationFactor / shardsNeeded).toFixed(0)} GB (with ${replicationFactor}x replication)`)
}

// Usage
capacityPlanner({
  targetGrowthMonths: 12,
  maxShardSizeGB: 500,
  replicationFactor: 3
})
```

### Exercise 4: Migration Impact Analyzer

```javascript
// Analyze impact of chunk migrations

function migrationImpactAnalyzer(hours = 24) {
  print(`=== Migration Impact Analysis (last ${hours}h) ===\n`)
  
  const since = new Date(Date.now() - hours * 60 * 60 * 1000)
  const changelog = db.getSiblingDB("config").changelog
  
  // Get all migrations
  const migrations = changelog.find({
    what: "moveChunk.commit",
    time: { $gte: since }
  }).toArray()
  
  print(`Total Migrations: ${migrations.length}`)
  
  if (migrations.length === 0) {
    print("No migrations in this period")
    return
  }
  
  // Analyze by hour
  const byHour = {}
  migrations.forEach(m => {
    const hour = m.time.getHours()
    byHour[hour] = (byHour[hour] || 0) + 1
  })
  
  print("\nMigrations by Hour:")
  for (let h = 0; h < 24; h++) {
    const count = byHour[h] || 0
    const bar = "█".repeat(count)
    print(`  ${h.toString().padStart(2, '0')}:00 │ ${bar} ${count}`)
  }
  
  // Analyze by collection
  const byCollection = {}
  migrations.forEach(m => {
    const ns = m.ns
    byCollection[ns] = (byCollection[ns] || 0) + 1
  })
  
  print("\nMigrations by Collection:")
  Object.entries(byCollection)
    .sort((a, b) => b[1] - a[1])
    .forEach(([ns, count]) => {
      print(`  ${ns}: ${count}`)
    })
  
  // Analyze source/destination patterns
  const patterns = {}
  migrations.forEach(m => {
    const key = `${m.details.from} → ${m.details.to}`
    patterns[key] = (patterns[key] || 0) + 1
  })
  
  print("\nMigration Patterns:")
  Object.entries(patterns)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .forEach(([pattern, count]) => {
      print(`  ${pattern}: ${count}`)
    })
  
  // Recommendations
  print("\nRecommendations:")
  
  const avgPerHour = migrations.length / hours
  if (avgPerHour > 10) {
    print("  ⚠ High migration rate - consider larger chunk size")
  }
  
  const peakHour = Object.entries(byHour).sort((a, b) => b[1] - a[1])[0]
  if (peakHour && peakHour[1] > avgPerHour * 3) {
    print(`  ⚠ Peak at ${peakHour[0]}:00 - consider balancer window`)
  }
}

// Usage
migrationImpactAnalyzer(24)
```

---

[← Previous: Balancing](48-balancing.md) | [Next: Authentication →](50-authentication.md)
