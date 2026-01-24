# Chapter 40: Replica Set Configuration

## Table of Contents
- [Setting Up a Replica Set](#setting-up-a-replica-set)
- [Configuration Options](#configuration-options)
- [Member Configuration](#member-configuration)
- [Reconfiguration](#reconfiguration)
- [Adding and Removing Members](#adding-and-removing-members)
- [Priority and Voting](#priority-and-voting)
- [Tags and Tag Sets](#tags-and-tag-sets)
- [Summary](#summary)

---

## Setting Up a Replica Set

### Starting MongoDB with Replication

```bash
# Method 1: Command line
mongod --replSet "rs0" --port 27017 --dbpath /data/db1

# Method 2: Configuration file (mongod.conf)
# replication:
#   replSetName: "rs0"
#   oplogSizeMB: 2048

# Start multiple instances for replica set
# Node 1 (Primary candidate)
mongod --replSet "rs0" --port 27017 --dbpath /data/db1 --bind_ip localhost,192.168.1.101

# Node 2 (Secondary)
mongod --replSet "rs0" --port 27018 --dbpath /data/db2 --bind_ip localhost,192.168.1.102

# Node 3 (Secondary)
mongod --replSet "rs0" --port 27019 --dbpath /data/db3 --bind_ip localhost,192.168.1.103
```

### Configuration File Example

```yaml
# mongod.conf

# Storage
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true

# Network
net:
  port: 27017
  bindIp: 0.0.0.0

# Replication
replication:
  replSetName: "rs0"
  oplogSizeMB: 2048

# Security (recommended)
security:
  authorization: enabled
  keyFile: /etc/mongodb/keyfile
```

### Initiating the Replica Set

```javascript
// Connect to one of the mongod instances
// mongosh --host localhost --port 27017

// Initiate with default config
rs.initiate()

// Or initiate with explicit config
rs.initiate({
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1.example.com:27017" },
    { _id: 1, host: "mongo2.example.com:27017" },
    { _id: 2, host: "mongo3.example.com:27017" }
  ]
})

// Check status
rs.status()
```

### Full Configuration Example

```javascript
// Complete replica set configuration
rs.initiate({
  _id: "rs0",
  version: 1,
  members: [
    {
      _id: 0,
      host: "mongo1.example.com:27017",
      priority: 10,
      tags: { dc: "east", usage: "production" }
    },
    {
      _id: 1,
      host: "mongo2.example.com:27017",
      priority: 5,
      tags: { dc: "east", usage: "production" }
    },
    {
      _id: 2,
      host: "mongo3.example.com:27017",
      priority: 5,
      tags: { dc: "west", usage: "production" }
    },
    {
      _id: 3,
      host: "mongo4.example.com:27017",
      priority: 0,
      hidden: true,
      tags: { dc: "west", usage: "backup" }
    },
    {
      _id: 4,
      host: "mongo5.example.com:27017",
      priority: 0,
      secondaryDelaySecs: 3600,  // 1 hour delay
      tags: { dc: "west", usage: "delayed" }
    }
  ],
  settings: {
    chainingAllowed: true,
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {
      eastDC: { dc: 1 },
      multiDC: { dc: 2 }
    },
    getLastErrorDefaults: {
      w: "majority",
      wtimeout: 5000
    }
  }
})
```

---

## Configuration Options

### Replica Set Settings

```javascript
// View current configuration
rs.conf()

// Configuration structure
{
  _id: "rs0",                    // Replica set name
  version: 5,                    // Config version (auto-incremented)
  term: 1,                       // Election term
  protocolVersion: 1,            // Replication protocol (always 1)
  writeConcernMajorityJournalDefault: true,
  members: [...],                // Member configurations
  settings: {
    chainingAllowed: true,       // Secondaries can sync from secondaries
    heartbeatIntervalMillis: 2000,
    heartbeatTimeoutSecs: 10,
    electionTimeoutMillis: 10000,
    catchUpTimeoutMillis: -1,    // -1 = no limit
    catchUpTakeoverDelayMillis: 30000,
    getLastErrorModes: {},       // Custom write concerns
    getLastErrorDefaults: {      // Default write concern
      w: 1,
      wtimeout: 0
    },
    replicaSetId: ObjectId("...")
  }
}
```

### Settings Reference

| Setting | Default | Description |
|---------|---------|-------------|
| `chainingAllowed` | true | Allow secondary-to-secondary replication |
| `heartbeatIntervalMillis` | 2000 | Heartbeat frequency |
| `heartbeatTimeoutSecs` | 10 | Heartbeat timeout |
| `electionTimeoutMillis` | 10000 | Election wait time |
| `catchUpTimeoutMillis` | -1 | New primary catchup timeout |
| `catchUpTakeoverDelayMillis` | 30000 | Takeover delay during catchup |

### Modifying Settings

```javascript
// Get current config
cfg = rs.conf()

// Modify settings
cfg.settings.heartbeatTimeoutSecs = 15
cfg.settings.electionTimeoutMillis = 15000

// Apply changes
rs.reconfig(cfg)

// Or use replSetReconfig command
db.adminCommand({
  replSetReconfig: cfg,
  force: false  // Set true only in emergencies
})
```

---

## Member Configuration

### Member Options

```javascript
// Member configuration structure
{
  _id: 0,                          // Unique member ID
  host: "hostname:port",           // Member address
  arbiterOnly: false,              // Is arbiter
  buildIndexes: true,              // Build indexes
  hidden: false,                   // Hide from clients
  priority: 1,                     // Election priority (0-1000)
  tags: {},                        // Custom tags
  secondaryDelaySecs: 0,           // Replication delay
  votes: 1                         // Voting power (0 or 1)
}
```

### Member Options Reference

| Option | Default | Description |
|--------|---------|-------------|
| `_id` | Required | Unique ID (0 to 255) |
| `host` | Required | hostname:port |
| `arbiterOnly` | false | True for arbiters |
| `buildIndexes` | true | Build indexes (set false for backup nodes) |
| `hidden` | false | Hide from driver discovery |
| `priority` | 1 | Election priority |
| `tags` | {} | Custom tags for read preference |
| `secondaryDelaySecs` | 0 | Replication delay in seconds |
| `votes` | 1 | Voting rights |

### Configuring Different Member Types

```javascript
cfg = rs.conf()

// Standard secondary
cfg.members[1] = {
  _id: 1,
  host: "mongo2:27017",
  priority: 5,
  votes: 1
}

// Hidden member (for backups)
cfg.members[2] = {
  _id: 2,
  host: "mongo3:27017",
  priority: 0,     // Cannot become primary
  hidden: true,    // Not visible to clients
  votes: 1
}

// Delayed member (disaster recovery)
cfg.members[3] = {
  _id: 3,
  host: "mongo4:27017",
  priority: 0,
  secondaryDelaySecs: 3600,  // 1 hour behind
  hidden: true,              // Often hidden too
  votes: 0                   // Usually non-voting
}

// Arbiter
cfg.members[4] = {
  _id: 4,
  host: "arbiter:27017",
  arbiterOnly: true
}

// Non-voting member (read scaling)
cfg.members[5] = {
  _id: 5,
  host: "mongo5:27017",
  priority: 0,
  votes: 0
}

rs.reconfig(cfg)
```

---

## Reconfiguration

### Safe Reconfiguration

```javascript
// Always get current config first
cfg = rs.conf()

// Make changes
cfg.members[1].priority = 10

// Apply changes
rs.reconfig(cfg)

// The version is automatically incremented
```

### Force Reconfiguration

```javascript
// Use force only when majority is unavailable
// WARNING: Can cause data loss!

cfg = rs.conf()
cfg.members = cfg.members.filter(m => m._id !== 3)  // Remove failed member

// Force reconfiguration
rs.reconfig(cfg, { force: true })

// Or via command
db.adminCommand({
  replSetReconfig: cfg,
  force: true
})
```

### Reconfiguration Best Practices

```
┌─────────────────────────────────────────────────────────────────────┐
│              Reconfiguration Best Practices                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DO:                                                               │
│  ├── Always get current config first                               │
│  ├── Make one change at a time                                     │
│  ├── Wait for members to sync after changes                        │
│  ├── Test in non-production first                                  │
│  └── Monitor during reconfiguration                                │
│                                                                     │
│  DON'T:                                                            │
│  ├── Use force unless absolutely necessary                         │
│  ├── Change multiple members at once                               │
│  ├── Remove majority of members                                    │
│  └── Change primary and secondaries together                       │
│                                                                     │
│  Reconfiguration triggers:                                         │
│  ├── Adding/removing members                                       │
│  ├── Changing priorities                                           │
│  ├── Modifying tags                                                │
│  └── Updating settings                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Adding and Removing Members

### Adding Members

```javascript
// Method 1: rs.add()
rs.add("mongo4.example.com:27017")

// With options
rs.add({
  host: "mongo4.example.com:27017",
  priority: 5,
  votes: 1,
  tags: { dc: "east" }
})

// Method 2: Reconfigure
cfg = rs.conf()
cfg.members.push({
  _id: 4,  // Choose appropriate ID
  host: "mongo4.example.com:27017"
})
rs.reconfig(cfg)

// Add arbiter
rs.addArb("arbiter.example.com:27017")
```

### Removing Members

```javascript
// Method 1: rs.remove()
rs.remove("mongo4.example.com:27017")

// Method 2: Reconfigure
cfg = rs.conf()
cfg.members = cfg.members.filter(m => m.host !== "mongo4.example.com:27017")
rs.reconfig(cfg)

// Remove by member ID
cfg = rs.conf()
cfg.members = cfg.members.filter(m => m._id !== 4)
rs.reconfig(cfg)
```

### Replacing a Member

```javascript
// Replace failed member with new one

// Step 1: Remove old member
rs.remove("old-server:27017")

// Step 2: Wait for removal to propagate
sleep(5000)

// Step 3: Add new member with same ID if needed
cfg = rs.conf()
cfg.members.push({
  _id: 2,  // Can reuse old ID
  host: "new-server:27017",
  priority: 5
})
rs.reconfig(cfg)
```

### Member Migration

```javascript
// Change member hostname (rolling process)

// Option 1: Remove and re-add (causes initial sync)
rs.remove("old-hostname:27017")
rs.add("new-hostname:27017")

// Option 2: Modify config (no data movement if same machine)
cfg = rs.conf()
const memberIdx = cfg.members.findIndex(m => m.host === "old-hostname:27017")
cfg.members[memberIdx].host = "new-hostname:27017"
rs.reconfig(cfg)
```

---

## Priority and Voting

### Understanding Priority

```javascript
// Priority determines primary election preference
// Range: 0 to 1000
// Higher priority = more likely to be elected

cfg = rs.conf()

// Primary DC members - high priority
cfg.members[0].priority = 100
cfg.members[1].priority = 90

// DR DC members - lower priority
cfg.members[2].priority = 50
cfg.members[3].priority = 50

// Backup members - cannot be primary
cfg.members[4].priority = 0  // Never primary

rs.reconfig(cfg)
```

### Priority Rules

| Priority | Behavior |
|----------|----------|
| 0 | Cannot be elected primary |
| 1 (default) | Standard member |
| >1 | Preferred primary candidate |
| Highest | Most likely to be primary |

### Voting Configuration

```javascript
// Maximum 7 voting members per replica set
// Votes: 0 or 1

cfg = rs.conf()

// Voting members (max 7)
cfg.members[0].votes = 1
cfg.members[1].votes = 1
cfg.members[2].votes = 1
cfg.members[3].votes = 1
cfg.members[4].votes = 1
cfg.members[5].votes = 1
cfg.members[6].votes = 1

// Non-voting members (for read scaling)
cfg.members[7].votes = 0
cfg.members[7].priority = 0  // Non-voting must have priority 0
cfg.members[8].votes = 0
cfg.members[8].priority = 0

rs.reconfig(cfg)
```

### Stepping Down Primary

```javascript
// Force primary to step down
rs.stepDown()

// Step down with timeout
rs.stepDown(60)  // Step down for 60 seconds

// Step down with wait for secondary
rs.stepDown(60, 30)  // 60s stepdown, wait 30s for secondary catchup

// Freeze a member (prevent election)
rs.freeze(120)  // Cannot be elected for 120 seconds

// Unfreeze
rs.freeze(0)
```

---

## Tags and Tag Sets

### Configuring Tags

```javascript
// Tags enable custom read preferences and write concerns

cfg = rs.conf()

// Tag by data center
cfg.members[0].tags = { dc: "east", rack: "r1", usage: "production" }
cfg.members[1].tags = { dc: "east", rack: "r2", usage: "production" }
cfg.members[2].tags = { dc: "west", rack: "r1", usage: "production" }
cfg.members[3].tags = { dc: "west", rack: "r2", usage: "production" }
cfg.members[4].tags = { dc: "west", rack: "r3", usage: "analytics" }

rs.reconfig(cfg)
```

### Using Tags for Read Preference

```javascript
// Read from specific tag
db.getMongo().setReadPref("secondary", [{ dc: "west" }])

// Read from multiple possible tags
db.getMongo().setReadPref("secondary", [
  { dc: "west", usage: "analytics" },  // First preference
  { dc: "west" },                      // Second preference
  {}                                   // Any secondary
])

// In connection string
// mongodb://host1,host2,host3/?replicaSet=rs0&readPreference=secondary&readPreferenceTags=dc:west
```

### Custom Write Concerns with Tags

```javascript
// Define custom write concern modes
cfg = rs.conf()

cfg.settings.getLastErrorModes = {
  // Write acknowledged by at least one member in each DC
  multiDC: {
    dc: 2
  },
  // Write acknowledged by members in 2 different racks
  multiRack: {
    rack: 2
  },
  // Write to all production servers
  allProduction: {
    usage: 1  // At least one per unique "usage" value
  }
}

rs.reconfig(cfg)

// Using custom write concern
db.collection.insertOne(
  { data: "important" },
  { writeConcern: { w: "multiDC", wtimeout: 5000 } }
)
```

### Tag Set Patterns

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Common Tag Patterns                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Geographic Distribution                                           │
│  { dc: "us-east", region: "virginia", az: "us-east-1a" }          │
│                                                                     │
│  Hardware Tiers                                                    │
│  { tier: "ssd", memory: "high", cpu: "high" }                     │
│                                                                     │
│  Workload Isolation                                                │
│  { usage: "oltp" | "analytics" | "backup" }                       │
│                                                                     │
│  Environment                                                       │
│  { env: "production" | "staging" | "dev" }                        │
│                                                                     │
│  Application                                                       │
│  { app: "web" | "mobile" | "batch" }                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Setup Steps

| Step | Command/Action |
|------|----------------|
| 1. Start mongod | `--replSet` option |
| 2. Connect | `mongosh` |
| 3. Initiate | `rs.initiate()` |
| 4. Add members | `rs.add()` |
| 5. Configure | `rs.reconfig()` |

### Member Types

| Type | Priority | Votes | Hidden | Use Case |
|------|----------|-------|--------|----------|
| Standard | 1+ | 1 | No | Normal ops |
| Hidden | 0 | 0-1 | Yes | Backups |
| Delayed | 0 | 0 | Yes | Recovery |
| Arbiter | - | 1 | No | Voting only |
| Non-voting | 0 | 0 | No | Read scaling |

### Key Commands

| Command | Purpose |
|---------|---------|
| `rs.initiate()` | Create replica set |
| `rs.conf()` | View configuration |
| `rs.reconfig()` | Apply changes |
| `rs.add()` | Add member |
| `rs.remove()` | Remove member |
| `rs.stepDown()` | Step down primary |

### What's Next?

In the next chapter, we'll explore Read Preferences in detail.

---

## Practice Questions

1. What are the minimum steps to create a replica set?
2. What's the difference between priority 0 and hidden members?
3. When would you use a delayed secondary?
4. What is the maximum number of voting members?
5. How do tags help with read preferences?
6. When should you use force reconfiguration?
7. What happens when you add a new member?
8. How do custom write concerns work with tags?

---

## Hands-On Exercises

### Exercise 1: Replica Set Initialization

```javascript
// Simulate replica set setup (documentation purposes)

// Configuration for a 3-member replica set
const config = {
  _id: "rs0",
  members: [
    { _id: 0, host: "mongo1:27017", priority: 10 },
    { _id: 1, host: "mongo2:27017", priority: 5 },
    { _id: 2, host: "mongo3:27017", priority: 5 }
  ]
}

print("=== Replica Set Configuration ===")
printjson(config)

// Validation checks
print("\nValidation:")
print("  Members: " + config.members.length)
print("  Voting members: " + config.members.filter(m => m.votes !== 0).length)
print("  Highest priority: " + Math.max(...config.members.map(m => m.priority || 1)))
```

### Exercise 2: Member Configuration Templates

```javascript
// Create configuration templates for different scenarios

function createMemberConfig(scenario) {
  const templates = {
    "standard": {
      priority: 5,
      votes: 1,
      hidden: false
    },
    "high-priority": {
      priority: 100,
      votes: 1,
      hidden: false
    },
    "hidden-backup": {
      priority: 0,
      votes: 1,
      hidden: true,
      buildIndexes: true
    },
    "delayed": {
      priority: 0,
      votes: 0,
      hidden: true,
      secondaryDelaySecs: 3600
    },
    "analytics": {
      priority: 0,
      votes: 0,
      hidden: false,
      tags: { usage: "analytics" }
    },
    "arbiter": {
      arbiterOnly: true
    }
  }
  
  return templates[scenario] || templates["standard"]
}

// Test templates
print("=== Member Configuration Templates ===\n")

const scenarios = ["standard", "high-priority", "hidden-backup", "delayed", "analytics", "arbiter"]
scenarios.forEach(s => {
  print(`${s}:`)
  printjson(createMemberConfig(s))
  print("")
})
```

### Exercise 3: Tag Configuration

```javascript
// Design tag strategy for multi-DC deployment

const tagStrategy = {
  members: [
    {
      _id: 0,
      host: "mongo-east-1:27017",
      tags: { dc: "us-east", rack: "r1", tier: "ssd" }
    },
    {
      _id: 1,
      host: "mongo-east-2:27017",
      tags: { dc: "us-east", rack: "r2", tier: "ssd" }
    },
    {
      _id: 2,
      host: "mongo-west-1:27017",
      tags: { dc: "us-west", rack: "r1", tier: "ssd" }
    },
    {
      _id: 3,
      host: "mongo-west-2:27017",
      tags: { dc: "us-west", rack: "r2", tier: "hdd" }
    },
    {
      _id: 4,
      host: "mongo-analytics:27017",
      tags: { dc: "us-west", rack: "r3", tier: "hdd", usage: "analytics" }
    }
  ],
  settings: {
    getLastErrorModes: {
      multiDC: { dc: 2 },
      multiRack: { rack: 2 },
      allSSD: { tier: 1 }
    }
  }
}

print("=== Tag Strategy ===\n")

print("Members by DC:")
const byDC = {}
tagStrategy.members.forEach(m => {
  const dc = m.tags.dc
  if (!byDC[dc]) byDC[dc] = []
  byDC[dc].push(m.host)
})
printjson(byDC)

print("\nCustom Write Concerns:")
Object.entries(tagStrategy.settings.getLastErrorModes).forEach(([name, mode]) => {
  print(`  ${name}: ${JSON.stringify(mode)}`)
})
```

### Exercise 4: Reconfiguration Planning

```javascript
// Plan safe reconfiguration steps

function planReconfiguration(current, desired) {
  const changes = []
  
  // Find members to remove
  const currentHosts = current.members.map(m => m.host)
  const desiredHosts = desired.members.map(m => m.host)
  
  const toRemove = currentHosts.filter(h => !desiredHosts.includes(h))
  const toAdd = desiredHosts.filter(h => !currentHosts.includes(h))
  const toModify = current.members.filter(m => {
    const desiredM = desired.members.find(d => d.host === m.host)
    if (!desiredM) return false
    return JSON.stringify(m) !== JSON.stringify(desiredM)
  })
  
  // Plan steps
  toRemove.forEach(h => {
    changes.push({ action: "remove", host: h, risk: "medium" })
  })
  
  toModify.forEach(m => {
    changes.push({ action: "modify", host: m.host, risk: "low" })
  })
  
  toAdd.forEach(h => {
    changes.push({ action: "add", host: h, risk: "low" })
  })
  
  return changes
}

// Example
const currentConfig = {
  members: [
    { _id: 0, host: "mongo1:27017", priority: 5 },
    { _id: 1, host: "mongo2:27017", priority: 5 },
    { _id: 2, host: "mongo3:27017", priority: 5 }
  ]
}

const desiredConfig = {
  members: [
    { _id: 0, host: "mongo1:27017", priority: 10 },  // Modified
    { _id: 1, host: "mongo2:27017", priority: 5 },   // Same
    // mongo3 removed
    { _id: 3, host: "mongo4:27017", priority: 5 }    // Added
  ]
}

print("=== Reconfiguration Plan ===\n")
const plan = planReconfiguration(currentConfig, desiredConfig)
plan.forEach((step, i) => {
  print(`Step ${i + 1}: ${step.action} ${step.host} (risk: ${step.risk})`)
})
```

### Exercise 5: Health Check Script

```javascript
// Replica set health check (run on replica set)

function healthCheck() {
  print("=== Replica Set Health Check ===\n")
  
  try {
    const status = rs.status()
    const config = rs.conf()
    
    // Basic info
    print(`Replica Set: ${status.set}`)
    print(`Members: ${status.members.length}`)
    
    // Check each member
    print("\nMember Status:")
    let healthyCount = 0
    status.members.forEach(m => {
      const healthy = m.health === 1
      if (healthy) healthyCount++
      const icon = healthy ? "✓" : "✗"
      print(`  ${icon} ${m.name}: ${m.stateStr}`)
      if (m.lastHeartbeatMessage) {
        print(`    Last message: ${m.lastHeartbeatMessage}`)
      }
    })
    
    // Replication lag
    print("\nReplication Lag:")
    const primary = status.members.find(m => m.stateStr === "PRIMARY")
    if (primary) {
      status.members
        .filter(m => m.stateStr === "SECONDARY")
        .forEach(m => {
          const lag = (primary.optimeDate - m.optimeDate) / 1000
          const icon = lag < 10 ? "✓" : lag < 60 ? "!" : "✗"
          print(`  ${icon} ${m.name}: ${lag.toFixed(1)}s`)
        })
    }
    
    // Configuration checks
    print("\nConfiguration Checks:")
    const votingMembers = config.members.filter(m => m.votes !== 0).length
    print(`  Voting members: ${votingMembers} (max 7)`)
    print(`  Majority needed: ${Math.floor(votingMembers / 2) + 1}`)
    print(`  Currently healthy: ${healthyCount}`)
    
    const canElect = healthyCount >= Math.floor(votingMembers / 2) + 1
    print(`  Can elect primary: ${canElect ? "Yes" : "No"}`)
    
    // Overall status
    print("\n=== Overall Status ===")
    if (healthyCount === status.members.length && canElect) {
      print("✓ Replica set is healthy")
    } else {
      print("! Replica set has issues")
    }
    
  } catch (e) {
    print("✗ Cannot check replica set status")
    print("  Error: " + e.message)
  }
}

// Run health check
// healthCheck()  // Uncomment on replica set
```

---

[← Previous: Replica Set Architecture](39-replica-set-architecture.md) | [Next: Read Preferences →](41-read-preferences.md)
