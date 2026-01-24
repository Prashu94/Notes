# Chapter 39: Replica Set Architecture

## Table of Contents
- [Introduction to Replication](#introduction-to-replication)
- [Replica Set Components](#replica-set-components)
- [Election Process](#election-process)
- [Data Synchronization](#data-synchronization)
- [Oplog Overview](#oplog-overview)
- [Automatic Failover](#automatic-failover)
- [Deployment Topologies](#deployment-topologies)
- [Summary](#summary)

---

## Introduction to Replication

Replication in MongoDB provides data redundancy and high availability. A replica set is a group of MongoDB instances that maintain the same data set.

### Why Replication?

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Benefits of Replication                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  High Availability                                                  │
│  ├── Automatic failover                                            │
│  ├── No single point of failure                                    │
│  └── Continuous service during maintenance                         │
│                                                                     │
│  Data Redundancy                                                   │
│  ├── Multiple copies of data                                       │
│  ├── Protection against data loss                                  │
│  └── Disaster recovery                                             │
│                                                                     │
│  Read Scalability                                                  │
│  ├── Distribute reads across secondaries                           │
│  ├── Geographic distribution                                       │
│  └── Analytics on secondaries                                      │
│                                                                     │
│  Maintenance Without Downtime                                      │
│  ├── Rolling upgrades                                              │
│  ├── Index builds on secondaries                                   │
│  └── Backup from secondaries                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Replica Set vs Standalone

| Feature | Standalone | Replica Set |
|---------|-----------|-------------|
| High availability | No | Yes |
| Automatic failover | No | Yes |
| Data redundancy | No | Yes |
| Read distribution | No | Yes |
| Transactions | No | Yes |
| Production use | Not recommended | Recommended |

---

## Replica Set Components

### Member Types

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Replica Set Architecture                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│                    ┌─────────────┐                                  │
│                    │   PRIMARY   │                                  │
│                    │  (Read/Write)│                                  │
│                    └──────┬──────┘                                  │
│                           │                                         │
│            ┌──────────────┼──────────────┐                         │
│            │              │              │                         │
│            ▼              ▼              ▼                         │
│     ┌───────────┐  ┌───────────┐  ┌───────────┐                   │
│     │ SECONDARY │  │ SECONDARY │  │  ARBITER  │                   │
│     │(Read-only)│  │(Read-only)│  │ (No data) │                   │
│     └───────────┘  └───────────┘  └───────────┘                   │
│                                                                     │
│  Replication Flow: Primary → Secondaries (async)                   │
│  Election: Majority vote determines new primary                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Member Roles

| Role | Description | Votes | Data |
|------|-------------|-------|------|
| Primary | Receives all writes | 1 | Yes |
| Secondary | Replicates from primary | 1 | Yes |
| Arbiter | Voting only | 1 | No |
| Hidden | Not visible to clients | 1 | Yes |
| Delayed | Time-delayed copy | 0-1 | Yes |

### Primary

```javascript
// The primary member:
// - Receives all write operations
// - Records operations in the oplog
// - Only one primary per replica set

// Check if connected to primary
db.hello()
// or
rs.hello()

// Result shows:
{
  isWritablePrimary: true,  // true if primary
  primary: "mongodb-primary:27017",
  me: "mongodb-primary:27017",
  setName: "rs0",
  // ...
}
```

### Secondary

```javascript
// Secondary members:
// - Replicate the primary's oplog
// - Apply operations to their data set
// - Can serve read operations (with read preference)

// Check secondary status
rs.status()

// Secondary member info
{
  name: "mongodb-secondary:27017",
  stateStr: "SECONDARY",
  syncSourceHost: "mongodb-primary:27017",
  // ...
}
```

### Arbiter

```javascript
// Arbiters:
// - Participate in elections
// - Do NOT hold data
// - Lightweight resource usage
// - Use only when needed for odd number of votes

// Add arbiter to replica set (on primary)
rs.addArb("mongodb-arbiter:27017")
```

### Hidden Members

```javascript
// Hidden members:
// - Invisible to client applications
// - Cannot become primary
// - Use for dedicated backups or reporting

// Configure member as hidden
cfg = rs.conf()
cfg.members[2].hidden = true
cfg.members[2].priority = 0  // Required for hidden
rs.reconfig(cfg)
```

### Delayed Members

```javascript
// Delayed members:
// - Maintain delayed copy of data
// - Useful for recovering from errors
// - Protection against human errors

// Configure 1-hour delay
cfg = rs.conf()
cfg.members[2].secondaryDelaySecs = 3600  // 1 hour
cfg.members[2].priority = 0
rs.reconfig(cfg)
```

---

## Election Process

### How Elections Work

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Election Process                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Trigger                                                        │
│     ├── Primary becomes unavailable                                │
│     ├── rs.stepDown() command                                      │
│     └── Reconfiguration                                            │
│                                                                     │
│  2. Election Called                                                │
│     └── Eligible member calls for election                         │
│                                                                     │
│  3. Voting                                                         │
│     ├── Each voting member casts one vote                          │
│     └── Candidate needs majority                                   │
│                                                                     │
│  4. New Primary                                                    │
│     └── Winner becomes new primary                                 │
│                                                                     │
│  Timeline: Typically 10-12 seconds                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Election Triggers

| Trigger | Description |
|---------|-------------|
| Primary failure | Primary crashes or network partition |
| Maintenance | Manual stepdown for upgrades |
| Reconfiguration | Member priority changes |
| Network issues | Primary loses majority connectivity |

### Voting Rules

```javascript
// Election requirements:
// 1. Majority of voting members must participate
// 2. Candidate must be up-to-date
// 3. Candidate must have highest priority among eligible

// For a 3-member set: need 2 votes
// For a 5-member set: need 3 votes
// For a 7-member set: need 4 votes

// Member priority affects elections
cfg = rs.conf()

// Higher priority = more likely to become primary
cfg.members[0].priority = 10  // Most likely primary
cfg.members[1].priority = 5   // Second choice
cfg.members[2].priority = 1   // Last resort

rs.reconfig(cfg)

// Priority 0 = can never become primary
cfg.members[2].priority = 0
rs.reconfig(cfg)
```

### Triggering Election

```javascript
// Force current primary to step down
rs.stepDown()

// Step down for specific duration (seconds)
rs.stepDown(60)  // Cannot be elected for 60 seconds

// Step down with options
rs.stepDown(60, 30)  // 60s stepdown, 30s wait for secondary
```

---

## Data Synchronization

### Replication Mechanism

```
┌─────────────────────────────────────────────────────────────────────┐
│                  Replication Flow                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Client Write                                                      │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────┐                                                       │
│  │ PRIMARY │ ────► Write to data files                             │
│  │         │ ────► Write to oplog                                  │
│  └────┬────┘                                                       │
│       │                                                            │
│       │ (Async replication)                                        │
│       │                                                            │
│       ▼                                                            │
│  ┌───────────┐     ┌───────────┐                                   │
│  │ SECONDARY │     │ SECONDARY │                                   │
│  │           │     │           │                                   │
│  │ Pull oplog│     │ Pull oplog│                                   │
│  │ Apply ops │     │ Apply ops │                                   │
│  └───────────┘     └───────────┘                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Sync Types

| Type | Description | When Used |
|------|-------------|-----------|
| Initial sync | Full data copy | New member joins |
| Replication | Continuous oplog tailing | Normal operation |
| Catchup | Fast-forward after lag | After maintenance |

### Initial Sync Process

```javascript
// Initial sync happens when:
// 1. New member added
// 2. Member's data is corrupted
// 3. Member has been offline too long

// Steps:
// 1. Clone all databases except local
// 2. Build indexes
// 3. Apply oplog entries during clone
// 4. Complete sync

// Monitor initial sync
rs.printSecondaryReplicationInfo()

// Resync a member (on the member to resync)
db.adminCommand({ resync: 1 })
```

---

## Oplog Overview

### What is the Oplog?

```javascript
// Oplog (operations log):
// - Capped collection in local database
// - Records all data modifications
// - Used for replication and recovery

// View oplog
use local
db.oplog.rs.find().limit(5)

// Oplog entry structure
{
  ts: Timestamp(1638360000, 1),  // Timestamp + counter
  t: NumberLong(1),              // Term
  h: NumberLong("123456789"),    // Hash
  v: 2,                          // Version
  op: "i",                       // Operation type
  ns: "mydb.users",              // Namespace
  ui: UUID("..."),               // Collection UUID
  o: {                           // Document
    _id: ObjectId("..."),
    name: "Alice"
  }
}
```

### Operation Types

| Code | Operation | Description |
|------|-----------|-------------|
| i | Insert | Document inserted |
| u | Update | Document updated |
| d | Delete | Document deleted |
| c | Command | Database command |
| n | No-op | Heartbeat/placeholder |

### Oplog Size

```javascript
// Check oplog size
rs.printReplicationInfo()

// Output:
configured oplog size:   990MB
log length start to end: 172800secs (48hrs)
oplog first event time:  Mon Dec 01 2024 00:00:00
oplog last event time:   Wed Dec 03 2024 00:00:00
now:                     Wed Dec 03 2024 00:00:00

// Change oplog size (MongoDB 3.6+)
db.adminCommand({ replSetResizeOplog: 1, size: 2000 })  // 2GB
```

### Oplog Window

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Oplog Window                                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ├────────────────── Oplog Window ──────────────────┤              │
│  │                                                   │              │
│  │  oldest     ◄── operations ──►     newest        │              │
│  │  entry                              entry        │              │
│                                                                     │
│  If secondary falls behind beyond oplog window:                    │
│  └── Full resync required (expensive!)                             │
│                                                                     │
│  Recommendations:                                                  │
│  ├── Size oplog for peak write periods                             │
│  ├── Monitor replication lag                                       │
│  └── Typically 24-48 hours minimum                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Automatic Failover

### Failover Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                   Automatic Failover                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Normal Operation:                                                 │
│  ┌─────────┐     ┌───────────┐     ┌───────────┐                  │
│  │ PRIMARY │ ──► │ SECONDARY │     │ SECONDARY │                  │
│  │ (active)│     │           │     │           │                  │
│  └─────────┘     └───────────┘     └───────────┘                  │
│                                                                     │
│  Primary Fails:                                                    │
│  ┌─────────┐     ┌───────────┐     ┌───────────┐                  │
│  │ PRIMARY │     │ SECONDARY │     │ SECONDARY │                  │
│  │  (down) │     │           │     │           │                  │
│  └─────────┘     └───────────┘     └───────────┘                  │
│                        │                                           │
│  Election:             ▼                                           │
│  ┌─────────┐     ┌───────────┐     ┌───────────┐                  │
│  │  (down) │     │  PRIMARY  │ ◄── │ SECONDARY │                  │
│  │         │     │  (elected)│     │  (voted)  │                  │
│  └─────────┘     └───────────┘     └───────────┘                  │
│                                                                     │
│  Timeline: 10-12 seconds (typically)                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Failover Timing

| Phase | Duration |
|-------|----------|
| Failure detection | 10 seconds (heartbeat) |
| Election | 0-2 seconds |
| Client reconnect | Automatic (driver) |
| Total | ~10-12 seconds |

### Rollback

```javascript
// Rollback occurs when:
// - Primary fails before replication
// - Old primary has writes not on new primary

// Rollback process:
// 1. Old primary reconnects as secondary
// 2. Identifies divergence point
// 3. Rolls back unreplicated writes
// 4. Saves rolled back data to rollback files

// Find rollback files
// Location: <dbpath>/rollback/

// Avoid rollbacks:
// - Use write concern: majority
// - Ensure majority acknowledgment
```

---

## Deployment Topologies

### Minimum Viable Replica Set

```
┌─────────────────────────────────────────────────────────────────────┐
│             3-Member Replica Set (Recommended Minimum)              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     ┌─────────┐     ┌───────────┐     ┌───────────┐               │
│     │ PRIMARY │     │ SECONDARY │     │ SECONDARY │               │
│     │ Data ✓  │     │  Data ✓   │     │  Data ✓   │               │
│     │ Vote ✓  │     │  Vote ✓   │     │  Vote ✓   │               │
│     └─────────┘     └───────────┘     └───────────┘               │
│                                                                     │
│  Pros:                                                             │
│  ├── Full data redundancy                                          │
│  ├── Can survive 1 member failure                                  │
│  └── All members can become primary                                │
│                                                                     │
│  Majority: 2 of 3                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### With Arbiter

```
┌─────────────────────────────────────────────────────────────────────┐
│           2 Data + 1 Arbiter (Cost-Sensitive Option)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│     ┌─────────┐     ┌───────────┐     ┌─────────┐                 │
│     │ PRIMARY │     │ SECONDARY │     │ ARBITER │                 │
│     │ Data ✓  │     │  Data ✓   │     │ Data ✗  │                 │
│     │ Vote ✓  │     │  Vote ✓   │     │ Vote ✓  │                 │
│     └─────────┘     └───────────┘     └─────────┘                 │
│                                                                     │
│  Pros:                                                             │
│  ├── Lower storage cost                                            │
│  └── Still maintains majority for elections                        │
│                                                                     │
│  Cons:                                                             │
│  ├── Only 2 copies of data                                         │
│  └── If secondary fails, no redundancy                             │
│                                                                     │
│  ⚠️ Not recommended for production                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### 5-Member Set

```
┌─────────────────────────────────────────────────────────────────────┐
│              5-Member Replica Set (High Availability)               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│               ┌─────────┐                                          │
│               │ PRIMARY │                                          │
│               └────┬────┘                                          │
│                    │                                               │
│     ┌──────┬──────┬──────┬──────┐                                 │
│     ▼      ▼      ▼      ▼      ▼                                 │
│  ┌─────┐┌─────┐┌─────┐┌─────┐                                     │
│  │SEC 1││SEC 2││SEC 3││SEC 4│                                     │
│  └─────┘└─────┘└─────┘└─────┘                                     │
│                                                                     │
│  Can survive: 2 member failures                                    │
│  Majority: 3 of 5                                                  │
│  Use case: High read distribution, critical data                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Geographically Distributed

```
┌─────────────────────────────────────────────────────────────────────┐
│              Geographically Distributed Replica Set                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Data Center A (Primary DC)     Data Center B (DR)                 │
│  ┌──────────────────────┐      ┌──────────────────────┐           │
│  │ ┌───────┐ ┌───────┐ │      │ ┌───────┐ ┌───────┐ │           │
│  │ │PRIMARY│ │SEC. 1 │ │◄────►│ │SEC. 2 │ │SEC. 3 │ │           │
│  │ └───────┘ └───────┘ │      │ └───────┘ └───────┘ │           │
│  └──────────────────────┘      └──────────────────────┘           │
│                                                                     │
│                Data Center C (Tie-breaker)                         │
│                ┌──────────────────────┐                            │
│                │      ┌───────┐       │                            │
│                │      │SEC. 4 │       │                            │
│                │      └───────┘       │                            │
│                └──────────────────────┘                            │
│                                                                     │
│  5 members across 3 data centers                                   │
│  ├── 2 in primary DC (priority: high)                              │
│  ├── 2 in DR DC (priority: medium)                                 │
│  └── 1 in third DC (priority: low, tie-breaker)                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Replica Set Components

| Component | Purpose | Data | Votes |
|-----------|---------|------|-------|
| Primary | Read/Write | Yes | 1 |
| Secondary | Read only | Yes | 1 |
| Arbiter | Elections | No | 1 |
| Hidden | Dedicated ops | Yes | 1 |
| Delayed | Time-delayed | Yes | 0-1 |

### Election Facts

| Fact | Detail |
|------|--------|
| Trigger | Primary failure/stepdown |
| Majority | Required for election |
| Time | ~10-12 seconds |
| Priority | Higher = more likely primary |

### Replication

| Aspect | Description |
|--------|-------------|
| Method | Async via oplog |
| Oplog | Capped collection |
| Sync | Initial + continuous |
| Rollback | Unreplicated writes |

### What's Next?

In the next chapter, we'll explore Replica Set Configuration in detail.

---

## Practice Questions

1. What's the difference between primary and secondary?
2. When should you use an arbiter?
3. What triggers an election?
4. What is the oplog and why is it important?
5. How does automatic failover work?
6. What is a hidden member used for?
7. Why use delayed members?
8. What causes rollback?

---

## Hands-On Exercises

### Exercise 1: Understanding Replica Set Status

```javascript
// Check replica set status (run on replica set)
rs.status()

// Key fields to examine:
// - set: replica set name
// - members[].stateStr: PRIIMARY, SECONDARY, ARBITER
// - members[].health: 1 = healthy, 0 = unhealthy
// - members[].syncSourceHost: where replicating from
// - members[].optimeDate: last optime applied

// Get configuration
rs.conf()

// Key configuration fields:
// - _id: replica set name
// - members[].host: hostname:port
// - members[].priority: election priority
// - members[].votes: voting rights

// Check replication info
rs.printReplicationInfo()
rs.printSecondaryReplicationInfo()
```

### Exercise 2: Replica Set Information

```javascript
// Get comprehensive status
function printReplicaSetInfo() {
  const status = rs.status()
  
  print("=== Replica Set: " + status.set + " ===\n")
  
  print("Members:")
  status.members.forEach(m => {
    const isPrimary = m.stateStr === "PRIMARY"
    const lag = m.optimeDate ? 
      Math.round((new Date() - m.optimeDate) / 1000) : "N/A"
    
    print(`  ${m.name}`)
    print(`    State: ${m.stateStr}`)
    print(`    Health: ${m.health === 1 ? "Healthy" : "Unhealthy"}`)
    if (!isPrimary) {
      print(`    Replication Lag: ${lag}s`)
      print(`    Sync Source: ${m.syncSourceHost || "N/A"}`)
    }
  })
  
  print("\nOplog:")
  const oplogInfo = db.getSiblingDB("local").oplog.rs.stats()
  print(`  Size: ${Math.round(oplogInfo.size / 1024 / 1024)}MB`)
  print(`  Max Size: ${Math.round(oplogInfo.maxSize / 1024 / 1024)}MB`)
}

// Run the function
printReplicaSetInfo()
```

### Exercise 3: Oplog Examination

```javascript
// Examine oplog contents
use local

// Recent operations
print("=== Recent Oplog Entries ===\n")
db.oplog.rs.find().sort({ $natural: -1 }).limit(10).forEach(op => {
  print(`Timestamp: ${op.ts}`)
  print(`Operation: ${op.op}`)
  print(`Namespace: ${op.ns}`)
  if (op.o) print(`Document: ${JSON.stringify(op.o).substring(0, 100)}...`)
  print("---")
})

// Count operations by type
print("\n=== Operations by Type ===")
db.oplog.rs.aggregate([
  { $group: { _id: "$op", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
]).forEach(printjson)

// Operations by namespace
print("\n=== Top Namespaces ===")
db.oplog.rs.aggregate([
  { $match: { ns: { $ne: "" } } },
  { $group: { _id: "$ns", count: { $sum: 1 } } },
  { $sort: { count: -1 } },
  { $limit: 10 }
]).forEach(printjson)
```

### Exercise 4: Member Configuration

```javascript
// Display member configuration details
function displayMemberConfig() {
  const config = rs.conf()
  
  print("=== Member Configuration ===\n")
  
  config.members.forEach(m => {
    print(`Member ${m._id}: ${m.host}`)
    print(`  Priority: ${m.priority}`)
    print(`  Votes: ${m.votes !== undefined ? m.votes : 1}`)
    print(`  Hidden: ${m.hidden || false}`)
    print(`  Secondary Delay: ${m.secondaryDelaySecs || 0}s`)
    print(`  Build Indexes: ${m.buildIndexes !== false}`)
    print(`  Tags: ${JSON.stringify(m.tags || {})}`)
    print("")
  })
  
  print("Settings:")
  if (config.settings) {
    print(`  Heartbeat Interval: ${config.settings.heartbeatIntervalMillis}ms`)
    print(`  Election Timeout: ${config.settings.electionTimeoutMillis}ms`)
    print(`  Catchup Timeout: ${config.settings.catchUpTimeoutMillis}ms`)
  }
}

displayMemberConfig()
```

### Exercise 5: Simulating Scenarios

```javascript
// Understanding election scenarios
// NOTE: These are explanatory - don't run on production!

// Scenario 1: Check if majority exists
function canAchieveMajority(totalMembers, availableMembers) {
  const majority = Math.floor(totalMembers / 2) + 1
  const canElect = availableMembers >= majority
  
  print(`Total members: ${totalMembers}`)
  print(`Available members: ${availableMembers}`)
  print(`Majority needed: ${majority}`)
  print(`Can elect primary: ${canElect}`)
  
  return canElect
}

// Test scenarios
print("=== Election Scenarios ===\n")

print("Scenario 1: 3-member set, 1 down")
canAchieveMajority(3, 2)

print("\nScenario 2: 3-member set, 2 down")
canAchieveMajority(3, 1)

print("\nScenario 3: 5-member set, 2 down")
canAchieveMajority(5, 3)

print("\nScenario 4: 5-member set, 3 down")
canAchieveMajority(5, 2)

// Calculate replication lag
function estimateReplicationLag() {
  const primary = rs.hello()
  if (!primary.isWritablePrimary) {
    print("Not connected to primary")
    return
  }
  
  const status = rs.status()
  const primaryOptime = status.members.find(m => m.stateStr === "PRIMARY").optimeDate
  
  print("\n=== Replication Lag ===\n")
  status.members
    .filter(m => m.stateStr === "SECONDARY")
    .forEach(m => {
      const lag = (primaryOptime - m.optimeDate) / 1000
      print(`${m.name}: ${lag.toFixed(2)} seconds`)
    })
}

// Run on replica set
// estimateReplicationLag()
```

---

[← Previous: Transaction Error Handling](38-transaction-error-handling.md) | [Next: Replica Set Configuration →](40-replica-set-configuration.md)
