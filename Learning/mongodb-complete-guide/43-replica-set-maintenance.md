# Chapter 43: Replica Set Maintenance

## Table of Contents
- [Maintenance Overview](#maintenance-overview)
- [Rolling Maintenance](#rolling-maintenance)
- [Member Maintenance](#member-maintenance)
- [Index Management](#index-management)
- [Compaction and Repair](#compaction-and-repair)
- [Backup Strategies](#backup-strategies)
- [Monitoring and Health Checks](#monitoring-and-health-checks)
- [Summary](#summary)

---

## Maintenance Overview

Replica sets enable maintenance operations without downtime through rolling procedures.

### Maintenance Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Replica Set Maintenance Types                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Rolling Operations (No Downtime)                                  │
│  ├── Software upgrades                                             │
│  ├── Index builds                                                  │
│  ├── Configuration changes                                         │
│  └── Hardware maintenance                                          │
│                                                                     │
│  Member-Specific Operations                                        │
│  ├── Resyncing members                                             │
│  ├── Replacing members                                             │
│  └── Adding/removing members                                       │
│                                                                     │
│  Data Maintenance                                                  │
│  ├── Compaction                                                    │
│  ├── Index optimization                                            │
│  └── Backup operations                                             │
│                                                                     │
│  Monitoring Operations                                             │
│  ├── Health checks                                                 │
│  ├── Replication lag monitoring                                    │
│  └── Performance analysis                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Maintenance Best Practices

| Practice | Reason |
|----------|--------|
| Use rolling procedures | Zero downtime |
| Start with secondaries | Primary stays available |
| Monitor during maintenance | Catch issues early |
| Have rollback plan | Quick recovery |
| Schedule during low traffic | Minimize impact |

---

## Rolling Maintenance

### Rolling Upgrade Procedure

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Rolling Upgrade Procedure                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Upgrade Secondary                                         │
│  ┌─────────┐    ┌───────────┐    ┌───────────┐                    │
│  │ PRIMARY │    │ SECONDARY │    │ SECONDARY │ ◄── Upgrading      │
│  │ (v4.4)  │    │  (v4.4)   │    │  (v5.0)   │                    │
│  └─────────┘    └───────────┘    └───────────┘                    │
│                                                                     │
│  Step 2: Upgrade Other Secondary                                   │
│  ┌─────────┐    ┌───────────┐    ┌───────────┐                    │
│  │ PRIMARY │    │ SECONDARY │    │ SECONDARY │                    │
│  │ (v4.4)  │    │  (v5.0)   │◄   │  (v5.0)   │                    │
│  └─────────┘    └───────────┘    └───────────┘                    │
│                                                                     │
│  Step 3: Step Down Primary, Upgrade                                │
│  ┌───────────┐  ┌───────────┐    ┌───────────┐                    │
│  │ SECONDARY │  │  PRIMARY  │    │ SECONDARY │                    │
│  │  (v5.0)   │◄ │  (v5.0)   │    │  (v5.0)   │                    │
│  └───────────┘  └───────────┘    └───────────┘                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Rolling Restart Script

```javascript
// Rolling restart procedure (execute manually on each member)

// 1. On each SECONDARY (one at a time):
// a. Connect to the secondary
// b. Shut down gracefully
db.adminCommand({ shutdown: 1 })

// c. Perform maintenance (upgrade, config change, etc.)
// d. Start mongod
// e. Wait for member to catch up before proceeding

// 2. Check secondary status before proceeding
function waitForSecondary(host, maxWaitSecs = 300) {
  const start = new Date()
  
  while ((new Date() - start) / 1000 < maxWaitSecs) {
    try {
      const status = rs.status()
      const member = status.members.find(m => m.name === host)
      
      if (member && member.stateStr === "SECONDARY" && member.health === 1) {
        print(`${host} is healthy secondary`)
        return true
      }
    } catch (e) {
      // Connection may be temporarily unavailable
    }
    
    sleep(5000)
  }
  
  print(`Timeout waiting for ${host}`)
  return false
}

// 3. On PRIMARY:
// a. Step down primary
rs.stepDown(60)  // Step down for 60 seconds

// b. Wait for new primary election
// c. Now the old primary is a secondary - shut it down
db.adminCommand({ shutdown: 1 })

// d. Perform maintenance
// e. Start mongod
```

### Maintenance Window Check

```javascript
// Check if safe to perform maintenance
function checkMaintenanceWindow() {
  const status = rs.status()
  const config = rs.conf()
  
  const checks = {
    passed: true,
    issues: []
  }
  
  // Check 1: All members healthy
  const unhealthy = status.members.filter(m => m.health !== 1)
  if (unhealthy.length > 0) {
    checks.passed = false
    checks.issues.push(`Unhealthy members: ${unhealthy.map(m => m.name).join(", ")}`)
  }
  
  // Check 2: Replication lag acceptable
  const primary = status.members.find(m => m.stateStr === "PRIMARY")
  const lagThreshold = 60  // seconds
  
  status.members.filter(m => m.stateStr === "SECONDARY").forEach(m => {
    const lag = (primary.optimeDate - m.optimeDate) / 1000
    if (lag > lagThreshold) {
      checks.passed = false
      checks.issues.push(`High replication lag on ${m.name}: ${lag}s`)
    }
  })
  
  // Check 3: Majority available
  const votingMembers = config.members.filter(m => m.votes !== 0).length
  const healthyVoting = status.members.filter(
    m => m.health === 1 && 
    config.members.find(c => c.host === m.name)?.votes !== 0
  ).length
  
  const majorityNeeded = Math.floor(votingMembers / 2) + 1
  if (healthyVoting < majorityNeeded + 1) {  // +1 for maintenance member
    checks.passed = false
    checks.issues.push("Not enough healthy members for maintenance")
  }
  
  return checks
}

// Check before maintenance
const check = checkMaintenanceWindow()
if (check.passed) {
  print("✓ Safe to proceed with maintenance")
} else {
  print("✗ NOT safe for maintenance:")
  check.issues.forEach(i => print(`  - ${i}`))
}
```

---

## Member Maintenance

### Resyncing a Member

```javascript
// When to resync:
// - Member data corrupted
// - Member fell too far behind (beyond oplog window)
// - New member added

// Method 1: Delete data directory and restart
// On the member to resync:
// 1. Stop mongod
// 2. Delete data directory: rm -rf /data/db/*
// 3. Start mongod
// Member will perform initial sync automatically

// Method 2: Use resync command (deprecated in newer versions)
db.adminCommand({ resync: 1 })

// Monitor resync progress
function monitorResync() {
  while (true) {
    try {
      const status = rs.status()
      const self = status.members.find(m => m.self)
      
      print(`State: ${self.stateStr}`)
      
      if (self.stateStr === "STARTUP2") {
        print("  Initial sync in progress...")
        if (self.initialSyncStatus) {
          const progress = self.initialSyncStatus
          print(`  Collections: ${progress.completedCollections}`)
        }
      } else if (self.stateStr === "SECONDARY") {
        print("  Resync complete!")
        break
      }
    } catch (e) {
      print("  Waiting for connection...")
    }
    
    sleep(10000)
  }
}
```

### Replacing a Member

```javascript
// Replace a failed or decommissioned member

// Step 1: Remove old member
rs.remove("old-member:27017")

// Step 2: Wait for removal to propagate
sleep(5000)

// Step 3: Add new member
rs.add({
  host: "new-member:27017",
  priority: 5  // Adjust as needed
})

// Step 4: Monitor new member sync
function monitorNewMember(host) {
  let lastProgress = 0
  
  while (true) {
    const status = rs.status()
    const member = status.members.find(m => m.name === host)
    
    if (!member) {
      print("Member not found in replica set")
      return
    }
    
    if (member.stateStr === "SECONDARY") {
      print(`${host}: Fully synced and healthy`)
      return
    }
    
    if (member.stateStr === "STARTUP2") {
      print(`${host}: Initial sync in progress...`)
    } else if (member.stateStr === "RECOVERING") {
      print(`${host}: Catching up with oplog...`)
    }
    
    sleep(10000)
  }
}

// monitorNewMember("new-member:27017")
```

### Stepping Down Primary

```javascript
// Graceful primary stepdown
rs.stepDown()

// With parameters
rs.stepDown(
  60,  // stepDownSecs: cannot be elected for this duration
  30   // secondaryCatchUpPeriodSecs: wait for secondary to catch up
)

// Force step down (use with caution)
rs.stepDown(60, 0)  // Don't wait for catchup

// Freeze member (prevent becoming primary)
rs.freeze(300)  // Cannot be elected for 300 seconds

// Unfreeze
rs.freeze(0)
```

---

## Index Management

### Rolling Index Build

```javascript
// Build indexes with minimal impact

// MongoDB 4.2+: Indexes build simultaneously on all members
// MongoDB 4.0-: Build on primary, then replicate

// Build index in background (pre-4.2)
db.collection.createIndex(
  { field: 1 },
  { background: true }
)

// MongoDB 4.4+: All builds are background by default

// Rolling index build procedure (pre-4.2):
// 1. Build on each secondary first
// 2. Step down primary
// 3. Build on old primary (now secondary)

// Hide index before building (test without impact)
db.collection.createIndex(
  { field: 1 },
  { hidden: true }
)

// Unhide after verification
db.runCommand({
  collMod: "collection",
  index: {
    keyPattern: { field: 1 },
    hidden: false
  }
})
```

### Index Maintenance

```javascript
// Check index usage
db.collection.aggregate([
  { $indexStats: {} }
])

// Find unused indexes
function findUnusedIndexes(collection, days = 7) {
  const stats = db[collection].aggregate([{ $indexStats: {} }]).toArray()
  const threshold = new Date(Date.now() - days * 24 * 60 * 60 * 1000)
  
  return stats.filter(s => {
    if (s.name === "_id_") return false  // Skip _id
    return !s.accesses.since || s.accesses.since < threshold
  })
}

// Drop unused index
db.collection.dropIndex("unused_index_name")

// Reindex collection (use carefully - blocks operations)
// Better: drop and recreate specific indexes
db.collection.reIndex()  // Avoid in production
```

### Index Build Monitoring

```javascript
// Monitor index build progress
function monitorIndexBuild(dbName, collectionName) {
  while (true) {
    const ops = db.currentOp({
      "command.createIndexes": collectionName,
      $or: [
        { "progress": { $exists: true } },
        { "msg": /Index Build/ }
      ]
    })
    
    if (ops.inprog.length === 0) {
      print("No index build in progress")
      break
    }
    
    ops.inprog.forEach(op => {
      if (op.progress) {
        const pct = (op.progress.done / op.progress.total * 100).toFixed(1)
        print(`Progress: ${pct}% (${op.progress.done}/${op.progress.total})`)
      } else {
        print(`Status: ${op.msg || "Building..."}`)
      }
    })
    
    sleep(5000)
  }
}
```

---

## Compaction and Repair

### Compact Operation

```javascript
// Compact reclaims disk space and defragments data
// Run on secondaries during maintenance windows

// Compact a collection
db.runCommand({
  compact: "collectionName",
  force: false  // Set true to run on primary (not recommended)
})

// Compact with options (WiredTiger)
db.runCommand({
  compact: "collectionName",
  freeSpaceTargetMB: 1000  // Free space target
})

// Note: compact blocks the collection
// For large collections, consider:
// 1. Run on one secondary at a time
// 2. Monitor progress
// 3. Step down primary before compacting
```

### When to Compact

| Scenario | Recommendation |
|----------|----------------|
| Many deletes | Compact to reclaim space |
| Large updates (growing docs) | Consider compaction |
| Pre-allocated space unused | Compact during maintenance |
| Regular operation | Usually not needed |

### Repair Operations

```javascript
// Repair (use as last resort)
// Requires standalone mode

// 1. Stop replica set member
// 2. Start in standalone mode
// mongod --dbpath /data/db --repair

// Or use command (when running)
db.repairDatabase()  // Deprecated - prefer compact

// Validate collection integrity
db.collection.validate({ full: true })

// Result shows:
// - Document count
// - Index details
// - Any corruption issues
```

---

## Backup Strategies

### Backup Methods

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Backup Strategies                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  File System Snapshot                                              │
│  ├── Fastest for large datasets                                    │
│  ├── Requires LVM/cloud snapshots                                  │
│  └── Must stop or freeze writes                                    │
│                                                                     │
│  mongodump                                                         │
│  ├── Logical backup                                                │
│  ├── Works with running system                                     │
│  └── Slower for large datasets                                     │
│                                                                     │
│  Ops Manager / Cloud Manager                                       │
│  ├── Continuous backup                                             │
│  ├── Point-in-time recovery                                        │
│  └── Managed service                                               │
│                                                                     │
│  Hidden Secondary                                                  │
│  ├── Dedicated backup member                                       │
│  ├── No impact on production                                       │
│  └── Can use any backup method                                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Backup from Secondary

```javascript
// Best practice: backup from hidden secondary

// 1. Configure hidden member for backups
cfg = rs.conf()
cfg.members[3].hidden = true
cfg.members[3].priority = 0
cfg.members[3].tags = { backup: "true" }
rs.reconfig(cfg)

// 2. Backup commands (run on backup member)

// mongodump
// mongodump --host backup-member:27017 --out /backup/$(date +%Y%m%d)

// With oplog for point-in-time
// mongodump --host backup-member:27017 --oplog --out /backup/$(date +%Y%m%d)
```

### Backup Verification

```javascript
// Verify backup integrity
function verifyBackup(backupPath) {
  // 1. Restore to test instance
  // mongorestore --host test-instance:27017 --drop backupPath
  
  // 2. Verify document counts
  const collections = db.getCollectionNames()
  const counts = {}
  
  collections.forEach(c => {
    counts[c] = db[c].countDocuments()
  })
  
  print("Collection counts:")
  Object.entries(counts).forEach(([name, count]) => {
    print(`  ${name}: ${count}`)
  })
  
  // 3. Validate collections
  print("\nValidation:")
  collections.forEach(c => {
    const result = db[c].validate()
    const status = result.valid ? "✓" : "✗"
    print(`  ${status} ${c}`)
  })
}
```

---

## Monitoring and Health Checks

### Health Check Script

```javascript
// Comprehensive replica set health check
function replicaSetHealthCheck() {
  print("=== Replica Set Health Check ===\n")
  
  try {
    const status = rs.status()
    const config = rs.conf()
    
    // 1. Basic Info
    print(`Replica Set: ${status.set}`)
    print(`Members: ${status.members.length}`)
    print(`My State: ${status.myState}`)
    print()
    
    // 2. Member Health
    print("Member Status:")
    let primaryCount = 0
    let healthyCount = 0
    
    status.members.forEach(m => {
      const healthy = m.health === 1
      const icon = healthy ? "✓" : "✗"
      
      if (healthy) healthyCount++
      if (m.stateStr === "PRIMARY") primaryCount++
      
      print(`  ${icon} ${m.name}: ${m.stateStr}`)
      
      if (!healthy && m.lastHeartbeatMessage) {
        print(`      Last message: ${m.lastHeartbeatMessage}`)
      }
    })
    print()
    
    // 3. Replication Lag
    print("Replication Lag:")
    const primary = status.members.find(m => m.stateStr === "PRIMARY")
    
    if (primary) {
      status.members
        .filter(m => m.stateStr === "SECONDARY")
        .forEach(m => {
          const lag = (primary.optimeDate - m.optimeDate) / 1000
          const icon = lag < 10 ? "✓" : lag < 60 ? "!" : "✗"
          print(`  ${icon} ${m.name}: ${lag.toFixed(1)} seconds`)
        })
    } else {
      print("  No primary found!")
    }
    print()
    
    // 4. Oplog Status
    print("Oplog Status:")
    try {
      const oplogStats = db.getSiblingDB("local").oplog.rs.stats()
      const oplogSizeMB = Math.round(oplogStats.maxSize / 1024 / 1024)
      const oplogUsedMB = Math.round(oplogStats.size / 1024 / 1024)
      const oplogPct = Math.round(oplogUsedMB / oplogSizeMB * 100)
      
      print(`  Size: ${oplogSizeMB} MB`)
      print(`  Used: ${oplogUsedMB} MB (${oplogPct}%)`)
    } catch (e) {
      print(`  Unable to get oplog stats`)
    }
    print()
    
    // 5. Summary
    print("Summary:")
    const issues = []
    
    if (primaryCount !== 1) issues.push(`Primary count: ${primaryCount} (expected 1)`)
    if (healthyCount < status.members.length) issues.push(`Unhealthy members: ${status.members.length - healthyCount}`)
    
    if (issues.length === 0) {
      print("  ✓ Replica set is healthy")
    } else {
      print("  Issues found:")
      issues.forEach(i => print(`    ✗ ${i}`))
    }
    
  } catch (e) {
    print("✗ Cannot check replica set status")
    print(`  Error: ${e.message}`)
  }
}

// Run health check
replicaSetHealthCheck()
```

### Monitoring Queries

```javascript
// Replication info
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()

// Current operations
db.currentOp()

// Server status
db.serverStatus().repl

// Connection pool
db.serverStatus().connections

// Opcounters
db.serverStatus().opcounters

// Replication metrics
db.serverStatus().metrics.repl
```

### Alert Thresholds

```javascript
// Define alert thresholds
const alerts = {
  replicationLag: 30,      // seconds
  oplogWindow: 24,         // hours
  memberHealth: 1,         // minimum healthy members
  connectionsPct: 80       // percent of max connections
}

function checkAlerts() {
  const issues = []
  const status = rs.status()
  const serverStatus = db.serverStatus()
  
  // Check replication lag
  const primary = status.members.find(m => m.stateStr === "PRIMARY")
  if (primary) {
    status.members
      .filter(m => m.stateStr === "SECONDARY")
      .forEach(m => {
        const lag = (primary.optimeDate - m.optimeDate) / 1000
        if (lag > alerts.replicationLag) {
          issues.push({
            level: "warning",
            message: `High replication lag on ${m.name}: ${lag}s`
          })
        }
      })
  }
  
  // Check member health
  const unhealthy = status.members.filter(m => m.health !== 1)
  if (unhealthy.length > 0) {
    issues.push({
      level: "critical",
      message: `Unhealthy members: ${unhealthy.map(m => m.name).join(", ")}`
    })
  }
  
  // Check connections
  const connPct = serverStatus.connections.current / 
                  serverStatus.connections.available * 100
  if (connPct > alerts.connectionsPct) {
    issues.push({
      level: "warning",
      message: `High connection usage: ${connPct.toFixed(1)}%`
    })
  }
  
  return issues
}

// Check alerts
const alertResults = checkAlerts()
if (alertResults.length === 0) {
  print("✓ No alerts")
} else {
  alertResults.forEach(a => {
    const icon = a.level === "critical" ? "🔴" : "🟡"
    print(`${icon} [${a.level.toUpperCase()}] ${a.message}`)
  })
}
```

---

## Summary

### Maintenance Operations

| Operation | Method | Impact |
|-----------|--------|--------|
| Software upgrade | Rolling | Zero downtime |
| Index build | Background | Minimal |
| Member resync | On secondary | None |
| Compaction | On secondary | Blocks collection |
| Configuration | rs.reconfig() | Brief election |

### Rolling Procedure

| Step | Action |
|------|--------|
| 1 | Check maintenance window |
| 2 | Upgrade secondaries (one at a time) |
| 3 | Step down primary |
| 4 | Upgrade old primary |
| 5 | Verify health |

### Backup Best Practices

| Practice | Reason |
|----------|--------|
| Use hidden secondary | No production impact |
| Include oplog | Point-in-time recovery |
| Verify backups | Ensure recoverability |
| Test restores | Confirm backup validity |

### What's Next?

In the next chapter, we'll begin Part 9: Sharding with Sharding Concepts.

---

## Practice Questions

1. What is rolling maintenance?
2. When should you resync a member?
3. How do you build indexes without downtime?
4. When should you compact a collection?
5. What's the best practice for backups?
6. How do you step down a primary?
7. What should you check before maintenance?
8. How do you monitor replication lag?

---

## Hands-On Exercises

### Exercise 1: Maintenance Checklist

```javascript
// Create maintenance checklist script

function maintenanceChecklist() {
  print("=== Maintenance Checklist ===\n")
  
  const checks = [
    {
      name: "Replica set status",
      check: () => {
        const status = rs.status()
        const healthy = status.members.filter(m => m.health === 1).length
        return {
          passed: healthy === status.members.length,
          detail: `${healthy}/${status.members.length} healthy`
        }
      }
    },
    {
      name: "Primary exists",
      check: () => {
        const status = rs.status()
        const primary = status.members.find(m => m.stateStr === "PRIMARY")
        return {
          passed: !!primary,
          detail: primary ? primary.name : "No primary"
        }
      }
    },
    {
      name: "Replication lag",
      check: () => {
        const status = rs.status()
        const primary = status.members.find(m => m.stateStr === "PRIMARY")
        if (!primary) return { passed: false, detail: "No primary" }
        
        const maxLag = Math.max(...status.members
          .filter(m => m.stateStr === "SECONDARY")
          .map(m => (primary.optimeDate - m.optimeDate) / 1000))
        
        return {
          passed: maxLag < 60,
          detail: `Max lag: ${maxLag.toFixed(1)}s`
        }
      }
    },
    {
      name: "No long-running ops",
      check: () => {
        const ops = db.currentOp({ "secs_running": { $gt: 60 } })
        return {
          passed: ops.inprog.length === 0,
          detail: `${ops.inprog.length} long-running operations`
        }
      }
    }
  ]
  
  let allPassed = true
  
  checks.forEach(c => {
    try {
      const result = c.check()
      const icon = result.passed ? "✓" : "✗"
      if (!result.passed) allPassed = false
      print(`${icon} ${c.name}: ${result.detail}`)
    } catch (e) {
      allPassed = false
      print(`✗ ${c.name}: Error - ${e.message}`)
    }
  })
  
  print()
  if (allPassed) {
    print("✓ All checks passed - safe to proceed")
  } else {
    print("✗ Some checks failed - review before proceeding")
  }
  
  return allPassed
}

// Run checklist
// maintenanceChecklist()
```

### Exercise 2: Rolling Upgrade Simulator

```javascript
// Simulate rolling upgrade procedure

print("=== Rolling Upgrade Simulation ===\n")

// Simulated cluster state
const cluster = {
  members: [
    { name: "mongo1:27017", state: "PRIMARY", version: "4.4" },
    { name: "mongo2:27017", state: "SECONDARY", version: "4.4" },
    { name: "mongo3:27017", state: "SECONDARY", version: "4.4" }
  ],
  targetVersion: "5.0"
}

function printClusterState() {
  cluster.members.forEach(m => {
    print(`  ${m.name}: ${m.state} (v${m.version})`)
  })
}

function upgradeMember(name) {
  const member = cluster.members.find(m => m.name === name)
  if (!member) return false
  
  member.version = cluster.targetVersion
  return true
}

function stepDownPrimary() {
  const primary = cluster.members.find(m => m.state === "PRIMARY")
  const secondary = cluster.members.find(m => m.state === "SECONDARY" && m.version === cluster.targetVersion)
  
  if (primary && secondary) {
    primary.state = "SECONDARY"
    secondary.state = "PRIMARY"
    return true
  }
  return false
}

// Simulate upgrade
print("Initial state:")
printClusterState()

print("\nStep 1: Upgrade first secondary")
upgradeMember("mongo3:27017")
printClusterState()

print("\nStep 2: Upgrade second secondary")
upgradeMember("mongo2:27017")
printClusterState()

print("\nStep 3: Step down primary")
stepDownPrimary()
printClusterState()

print("\nStep 4: Upgrade old primary")
upgradeMember("mongo1:27017")
printClusterState()

print("\n✓ Rolling upgrade complete!")
```

### Exercise 3: Backup Verification

```javascript
// Backup verification procedure

function verifyBackupProcedure() {
  print("=== Backup Verification Procedure ===\n")
  
  // Step 1: Get current database stats
  print("Step 1: Capture pre-backup statistics")
  const databases = db.adminCommand({ listDatabases: 1 }).databases
  const stats = {}
  
  databases.forEach(dbInfo => {
    if (dbInfo.name === "local" || dbInfo.name === "admin") return
    
    const targetDb = db.getSiblingDB(dbInfo.name)
    const collections = targetDb.getCollectionNames()
    
    stats[dbInfo.name] = {
      collections: collections.length,
      documents: {},
      indexes: {}
    }
    
    collections.forEach(c => {
      stats[dbInfo.name].documents[c] = targetDb[c].countDocuments()
      stats[dbInfo.name].indexes[c] = targetDb[c].getIndexes().length
    })
  })
  
  print("  Databases captured:", Object.keys(stats).length)
  
  // Step 2: Display summary
  print("\nStep 2: Database summary")
  Object.entries(stats).forEach(([db, info]) => {
    print(`  ${db}:`)
    print(`    Collections: ${info.collections}`)
    const totalDocs = Object.values(info.documents).reduce((a, b) => a + b, 0)
    print(`    Total documents: ${totalDocs}`)
  })
  
  // Step 3: Generate verification report
  print("\nStep 3: Verification commands (run after restore)")
  print(`
  // After restoring backup, run these comparisons:
  
  // 1. Check collection counts
  db.getCollectionNames().forEach(c => {
    const count = db[c].countDocuments()
    print(c + ": " + count)
  })
  
  // 2. Validate collections
  db.getCollectionNames().forEach(c => {
    const result = db[c].validate()
    print(c + ": " + (result.valid ? "Valid" : "INVALID"))
  })
  
  // 3. Sample document check
  db.getCollectionNames().forEach(c => {
    const sample = db[c].findOne()
    print(c + ": " + (sample ? "Has documents" : "Empty"))
  })
  `)
  
  return stats
}

// Run verification
verifyBackupProcedure()
```

### Exercise 4: Monitoring Dashboard

```javascript
// Simple monitoring dashboard

function monitoringDashboard() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           REPLICA SET MONITORING DASHBOARD                  ║")
  print("╚════════════════════════════════════════════════════════════╝")
  print()
  
  try {
    const status = rs.status()
    const serverStatus = db.serverStatus()
    
    // Cluster Overview
    print("┌─ CLUSTER OVERVIEW ─────────────────────────────────────────┐")
    print(`│  Replica Set: ${status.set.padEnd(44)}│`)
    print(`│  Members: ${String(status.members.length).padEnd(48)}│`)
    
    const primary = status.members.find(m => m.stateStr === "PRIMARY")
    print(`│  Primary: ${(primary ? primary.name : "NONE").padEnd(48)}│`)
    print("└────────────────────────────────────────────────────────────┘")
    print()
    
    // Member Status
    print("┌─ MEMBER STATUS ────────────────────────────────────────────┐")
    status.members.forEach(m => {
      const health = m.health === 1 ? "●" : "○"
      const state = m.stateStr.padEnd(12)
      const name = m.name.padEnd(30)
      print(`│  ${health} ${name} ${state}         │`)
    })
    print("└────────────────────────────────────────────────────────────┘")
    print()
    
    // Replication Lag
    print("┌─ REPLICATION LAG ──────────────────────────────────────────┐")
    if (primary) {
      status.members
        .filter(m => m.stateStr === "SECONDARY")
        .forEach(m => {
          const lag = ((primary.optimeDate - m.optimeDate) / 1000).toFixed(1)
          const indicator = parseFloat(lag) < 5 ? "✓" : parseFloat(lag) < 30 ? "!" : "✗"
          const name = m.name.padEnd(30)
          print(`│  ${indicator} ${name} ${lag.padStart(8)}s           │`)
        })
    } else {
      print("│  No primary - cannot calculate lag                        │")
    }
    print("└────────────────────────────────────────────────────────────┘")
    print()
    
    // Connections
    print("┌─ CONNECTIONS ──────────────────────────────────────────────┐")
    const conns = serverStatus.connections
    const connBar = "█".repeat(Math.floor(conns.current / conns.available * 20))
    const connPct = (conns.current / conns.available * 100).toFixed(1)
    print(`│  Current: ${String(conns.current).padEnd(10)} Available: ${String(conns.available).padEnd(10)}  │`)
    print(`│  Usage: [${connBar.padEnd(20)}] ${connPct}%             │`)
    print("└────────────────────────────────────────────────────────────┘")
    print()
    
    // Operations
    print("┌─ OPERATIONS (since startup) ───────────────────────────────┐")
    const ops = serverStatus.opcounters
    print(`│  Insert: ${String(ops.insert).padEnd(12)} Query: ${String(ops.query).padEnd(12)}       │`)
    print(`│  Update: ${String(ops.update).padEnd(12)} Delete: ${String(ops.delete).padEnd(12)}      │`)
    print("└────────────────────────────────────────────────────────────┘")
    
  } catch (e) {
    print("Error: " + e.message)
  }
  
  print()
  print("Last updated: " + new Date().toISOString())
}

// Display dashboard
monitoringDashboard()
```

---

[← Previous: Write Concerns](42-write-concerns.md) | [Next: Sharding Concepts →](44-sharding-concepts.md)
