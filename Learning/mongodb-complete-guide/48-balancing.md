# Chapter 48: Balancing

## Table of Contents
- [Understanding the Balancer](#understanding-the-balancer)
- [Balancer Configuration](#balancer-configuration)
- [Balancer Windows](#balancer-windows)
- [Migration Thresholds](#migration-thresholds)
- [Balancer Operations](#balancer-operations)
- [Troubleshooting](#troubleshooting)
- [Summary](#summary)

---

## Understanding the Balancer

The balancer is a background process that distributes chunks evenly across shards.

### How the Balancer Works

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Balancer Operation                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Monitor Phase                                                  │
│     Balancer checks chunk distribution every few seconds           │
│                                                                     │
│     ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│     │ Shard 1 │  │ Shard 2 │  │ Shard 3 │                         │
│     │ 50 chks │  │ 35 chks │  │ 20 chks │  ← Imbalance detected   │
│     └─────────┘  └─────────┘  └─────────┘                         │
│                                                                     │
│  2. Selection Phase                                                │
│     Select source (most chunks) and destination (fewest)           │
│     Source: Shard 1, Destination: Shard 3                          │
│                                                                     │
│  3. Migration Phase                                                │
│     ┌─────────┐                ┌─────────┐                         │
│     │ Shard 1 │ ═══ chunk ═══► │ Shard 3 │                         │
│     └─────────┘                └─────────┘                         │
│                                                                     │
│  4. Repeat                                                         │
│     Continue until difference ≤ threshold (default: 2-8 chunks)    │
│                                                                     │
│     ┌─────────┐  ┌─────────┐  ┌─────────┐                         │
│     │ Shard 1 │  │ Shard 2 │  │ Shard 3 │                         │
│     │ 35 chks │  │ 35 chks │  │ 35 chks │  ← Balanced!            │
│     └─────────┘  └─────────┘  └─────────┘                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Balancer Components

| Component | Role |
|-----------|------|
| Config Server Primary | Runs the balancer process |
| mongos | Coordinates migrations |
| Shards | Source/destination of chunk moves |
| config.locks | Prevents concurrent migrations |

### Balancer States

```javascript
// Check balancer state
sh.getBalancerState()
// Returns: true (enabled) or false (disabled)

// Check if balancer is currently running
sh.isBalancerRunning()
// Returns: true (actively migrating) or false (idle)

// Get detailed balancer status
db.adminCommand({ balancerStatus: 1 })
// Returns:
// {
//   mode: "full",           // "full", "off", or window-based
//   inBalancerRound: false,
//   numBalancerRounds: 1234
// }
```

---

## Balancer Configuration

### Enable/Disable Balancer

```javascript
// Enable balancer (default)
sh.startBalancer()

// Disable balancer
sh.stopBalancer()

// Using admin command
db.adminCommand({ balancerStart: 1 })
db.adminCommand({ balancerStop: 1 })
```

### Collection-Level Balancing

```javascript
// Disable balancing for a specific collection
sh.disableBalancing("mydb.orders")

// Re-enable balancing for a collection
sh.enableBalancing("mydb.orders")

// Check balancing status for a collection
db.getSiblingDB("config").collections.findOne(
  { _id: "mydb.orders" },
  { noBalance: 1 }
)
```

### Why Disable Balancing?

| Scenario | Reason |
|----------|--------|
| Bulk imports | Prevent migrations during load |
| Maintenance | Reduce system load |
| Backup operations | Consistent backup |
| Performance testing | Controlled environment |
| Zone configuration | Set up zones before balancing |

---

## Balancer Windows

### Configure Balancer Window

```javascript
// Set balancer to run only during specific hours
use config

// Create or update balancer settings
db.settings.updateOne(
  { _id: "balancer" },
  {
    $set: {
      activeWindow: {
        start: "23:00",  // Start at 11 PM
        stop: "06:00"    // Stop at 6 AM
      }
    }
  },
  { upsert: true }
)

// View current window
db.settings.findOne({ _id: "balancer" })
```

### Remove Balancer Window

```javascript
// Remove window (balancer runs 24/7)
use config
db.settings.updateOne(
  { _id: "balancer" },
  { $unset: { activeWindow: 1 } }
)
```

### Window Best Practices

```
┌─────────────────────────────────────────────────────────────────────┐
│               Balancer Window Strategies                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Production Workload Pattern:                                      │
│                                                                     │
│  Traffic                                                           │
│    ▲                                                               │
│    │     ╭──────╮                                                  │
│    │    ╱        ╲      ← Peak hours (9 AM - 6 PM)                │
│    │   ╱          ╲                                                │
│    │  ╱            ╲                                               │
│    │ ╱              ╲──────                                        │
│    └─────────────────────────► Time                                │
│      12AM  6AM  12PM  6PM  12AM                                    │
│                                                                     │
│  Recommended Window: { start: "23:00", stop: "05:00" }            │
│                                                                     │
│  ────────────────────────────────────────────────────────────────  │
│                                                                     │
│  Multi-Region Considerations:                                      │
│  - No single "off-peak" time globally                              │
│  - Options:                                                        │
│    1. Use zones to minimize cross-region migrations                │
│    2. Accept some balancing during business hours                  │
│    3. Use short, overlapping windows                               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Migration Thresholds

### Default Thresholds

| Total Chunks | Migration Threshold |
|--------------|---------------------|
| < 20 | 2 |
| 20 - 79 | 4 |
| ≥ 80 | 8 |

```javascript
// The balancer migrates when chunk difference > threshold
// Example: 3 shards with chunks: [50, 45, 40]
// Difference: 10 (50 - 40)
// Threshold (80+ chunks total): 8
// Result: Migration triggered (10 > 8)
```

### Migration Limits

```javascript
// Check current balancer round limits
db.adminCommand({ balancerCollectionStatus: "mydb.orders" })

// The balancer performs at most:
// - 1 migration per shard (as source) at a time
// - Multiple concurrent migrations across different shards

// Example with 4 shards:
// Max concurrent migrations: 2 (each needs source + destination)
```

### Throttling Migrations

```javascript
// Secondary throttle - wait for secondary replication
use config
db.settings.updateOne(
  { _id: "balancer" },
  { $set: { _secondaryThrottle: true } },
  { upsert: true }
)

// With specific write concern
db.settings.updateOne(
  { _id: "balancer" },
  { $set: { 
    _secondaryThrottle: { w: "majority" },
    _waitForDelete: true  // Wait for orphaned doc cleanup
  }},
  { upsert: true }
)
```

---

## Balancer Operations

### Check Balancer Status

```javascript
// Simple status check
sh.getBalancerState()   // Is enabled?
sh.isBalancerRunning()  // Is active?

// Detailed status
db.adminCommand({ balancerStatus: 1 })

// Current migration
db.getSiblingDB("config").locks.findOne({ _id: "balancer" })

// Active migrations
db.currentOp({ "command.moveChunk": { $exists: true } })
```

### Monitor Migration Progress

```javascript
// Watch migrations in real-time
function watchMigrations() {
  print("Watching migrations (Ctrl+C to stop)...")
  
  while (true) {
    const ops = db.currentOp({
      $or: [
        { "command.moveChunk": { $exists: true } },
        { "command._recvChunkStart": { $exists: true } }
      ]
    })
    
    if (ops.inprog.length > 0) {
      print(`\n[${new Date().toISOString()}] Active migrations:`)
      ops.inprog.forEach(op => {
        if (op.command?.moveChunk) {
          print(`  moveChunk: ${op.command.moveChunk}`)
          print(`    to: ${op.command.to}`)
        }
        if (op.progress) {
          const pct = (op.progress.done / op.progress.total * 100).toFixed(1)
          print(`    progress: ${pct}%`)
        }
      })
    } else {
      print(".", { newline: false })
    }
    
    sleep(5000)
  }
}

// watchMigrations()
```

### Migration History

```javascript
// View recent migrations
db.getSiblingDB("config").changelog.find({
  what: { $regex: /moveChunk/ }
}).sort({ time: -1 }).limit(10).pretty()

// Migration statistics
db.getSiblingDB("config").changelog.aggregate([
  { $match: { 
    what: "moveChunk.commit",
    time: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
  }},
  { $group: {
    _id: { from: "$details.from", to: "$details.to" },
    count: { $sum: 1 }
  }},
  { $sort: { count: -1 } }
])
```

### Force Balancer Round

```javascript
// Trigger immediate balancing check
db.adminCommand({ balancerStart: 1 })

// Note: This just enables the balancer if disabled
// The balancer checks for imbalance every few seconds when enabled
```

---

## Troubleshooting

### Common Issues

#### Balancer Not Running

```javascript
// Check if balancer is enabled
sh.getBalancerState()
// If false: sh.startBalancer()

// Check balancer lock
db.getSiblingDB("config").locks.findOne({ _id: "balancer" })

// Check for stuck locks (older versions)
// If state: 2 with old timestamp, may need manual intervention

// Check balancer window
db.getSiblingDB("config").settings.findOne({ _id: "balancer" })
// May be outside active window
```

#### Migrations Failing

```javascript
// Check changelog for errors
db.getSiblingDB("config").changelog.find({
  what: "moveChunk.from",
  "details.errmsg": { $exists: true }
}).sort({ time: -1 }).limit(5)

// Common errors:
// - "chunk too large" - jumbo chunk
// - "shard not found" - shard removed
// - "could not acquire lock" - concurrent operation
// - "destination shard disk full" - storage issue
```

#### Imbalanced After Balancing

```javascript
// Check for disabled collections
db.getSiblingDB("config").collections.find({ noBalance: true })

// Check for jumbo chunks
db.getSiblingDB("config").chunks.find({ jumbo: true })

// Check zone configuration
sh.status()  // Look for zones
```

### Diagnostics Script

```javascript
function balancerDiagnostics() {
  print("=== Balancer Diagnostics ===\n")
  
  // 1. Balancer state
  const state = sh.getBalancerState()
  const running = sh.isBalancerRunning()
  print(`Balancer Enabled: ${state}`)
  print(`Balancer Running: ${running}`)
  
  // 2. Active window
  const settings = db.getSiblingDB("config").settings.findOne({ _id: "balancer" })
  if (settings?.activeWindow) {
    print(`Active Window: ${settings.activeWindow.start} - ${settings.activeWindow.stop}`)
    
    // Check if currently in window
    const now = new Date()
    const hours = now.getHours().toString().padStart(2, '0')
    const mins = now.getMinutes().toString().padStart(2, '0')
    const currentTime = `${hours}:${mins}`
    print(`Current Time: ${currentTime}`)
  } else {
    print("Active Window: None (24/7)")
  }
  print()
  
  // 3. Collection balancing status
  print("Collection Balancing Status:")
  const collections = db.getSiblingDB("config").collections.find().toArray()
  collections.forEach(c => {
    const status = c.noBalance ? "DISABLED" : "enabled"
    print(`  ${c._id}: ${status}`)
  })
  print()
  
  // 4. Current distribution
  print("Chunk Distribution:")
  const distribution = db.getSiblingDB("config").chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  const maxChunks = distribution[0]?.count || 0
  const minChunks = distribution[distribution.length - 1]?.count || 0
  
  distribution.forEach(d => {
    const bar = "█".repeat(Math.floor(d.count / maxChunks * 20))
    print(`  ${d._id}: ${bar} ${d.count}`)
  })
  print(`  Difference: ${maxChunks - minChunks}`)
  print()
  
  // 5. Recent migrations
  print("Recent Migrations (last hour):")
  const migrations = db.getSiblingDB("config").changelog.countDocuments({
    what: "moveChunk.commit",
    time: { $gte: new Date(Date.now() - 60 * 60 * 1000) }
  })
  print(`  Completed: ${migrations}`)
  
  // 6. Active migrations
  const active = db.currentOp({
    "command.moveChunk": { $exists: true }
  })
  print(`  Active: ${active.inprog.length}`)
  print()
  
  // 7. Jumbo chunks
  const jumbo = db.getSiblingDB("config").chunks.countDocuments({ jumbo: true })
  if (jumbo > 0) {
    print(`⚠ Jumbo Chunks: ${jumbo}`)
    print("  These cannot be migrated automatically")
  } else {
    print("✓ No jumbo chunks")
  }
}

balancerDiagnostics()
```

### Manual Intervention

```javascript
// Force move a stuck chunk
sh.moveChunk(
  "mydb.orders",
  { customerId: "problematic-value" },
  "shard2RS"
)

// Clear jumbo flag
db.adminCommand({
  clearJumboFlag: "mydb.orders",
  find: { customerId: "large-customer" }
})

// Remove stuck balancer lock (use with caution!)
// Only if lock is clearly stuck (old timestamp, no active migration)
// db.getSiblingDB("config").locks.remove({ _id: "balancer" })
```

---

## Summary

### Balancer Settings

| Setting | Purpose | Command |
|---------|---------|---------|
| Enable | Start balancing | sh.startBalancer() |
| Disable | Stop balancing | sh.stopBalancer() |
| Window | Limit active hours | settings.activeWindow |
| Collection | Per-collection control | sh.disableBalancing() |

### Monitoring Commands

| Command | Information |
|---------|-------------|
| sh.getBalancerState() | Enabled/disabled |
| sh.isBalancerRunning() | Currently active |
| balancerStatus | Detailed status |
| config.changelog | Migration history |

### Best Practices

| Practice | Reason |
|----------|--------|
| Set balancer window | Reduce peak hour impact |
| Monitor regularly | Catch issues early |
| Check jumbo chunks | They block balancing |
| Disable during imports | Prevent unnecessary migrations |

### What's Next?

In the next chapter, we'll cover Sharded Cluster Administration.

---

## Practice Questions

1. What triggers the balancer to migrate chunks?
2. How do you set a balancer window?
3. What is the migration threshold?
4. How can you disable balancing for one collection?
5. What causes migrations to fail?
6. How do you check if the balancer is running?
7. What are jumbo chunks and how do they affect balancing?
8. When should you disable the balancer?

---

## Hands-On Exercises

### Exercise 1: Balancer Status Dashboard

```javascript
// Create a balancer status dashboard

function balancerDashboard() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║               BALANCER STATUS DASHBOARD                     ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const config = db.getSiblingDB("config")
  
  // Balancer Status
  print("┌─ BALANCER STATE ──────────────────────────────────────────┐")
  const state = sh.getBalancerState()
  const running = sh.isBalancerRunning()
  
  const stateIcon = state ? "●" : "○"
  const runningIcon = running ? "●" : "○"
  
  print(`│  ${stateIcon} Enabled: ${state ? "Yes" : "No"}`.padEnd(60) + "│")
  print(`│  ${runningIcon} Running: ${running ? "Yes" : "No"}`.padEnd(60) + "│")
  
  // Window
  const settings = config.settings.findOne({ _id: "balancer" })
  if (settings?.activeWindow) {
    print(`│  Window: ${settings.activeWindow.start} - ${settings.activeWindow.stop}`.padEnd(60) + "│")
  } else {
    print("│  Window: 24/7".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Distribution
  print("┌─ CHUNK DISTRIBUTION ──────────────────────────────────────┐")
  const dist = config.chunks.aggregate([
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  const total = dist.reduce((sum, d) => sum + d.count, 0)
  const maxCount = dist[0]?.count || 1
  
  dist.forEach(d => {
    const pct = (d.count / total * 100).toFixed(1)
    const barLen = Math.floor(d.count / maxCount * 25)
    const bar = "█".repeat(barLen)
    const line = `│  ${d._id}: ${bar} ${d.count} (${pct}%)`.substring(0, 59).padEnd(60) + "│"
    print(line)
  })
  
  const diff = (dist[0]?.count || 0) - (dist[dist.length - 1]?.count || 0)
  const balanced = diff <= 8 ? "✓ Balanced" : "! Imbalanced"
  print(`│  Status: ${balanced} (diff: ${diff})`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recent Activity
  print("┌─ RECENT ACTIVITY (1 hour) ────────────────────────────────┐")
  const hour = new Date(Date.now() - 60 * 60 * 1000)
  
  const moves = config.changelog.countDocuments({
    what: "moveChunk.commit",
    time: { $gte: hour }
  })
  
  const splits = config.changelog.countDocuments({
    what: "split",
    time: { $gte: hour }
  })
  
  print(`│  Migrations: ${moves}`.padEnd(60) + "│")
  print(`│  Splits: ${splits}`.padEnd(60) + "│")
  
  // Active operations
  const active = db.currentOp({ "command.moveChunk": { $exists: true } })
  print(`│  Active migrations: ${active.inprog.length}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Issues
  print("┌─ ISSUES ──────────────────────────────────────────────────┐")
  const jumbo = config.chunks.countDocuments({ jumbo: true })
  const disabled = config.collections.countDocuments({ noBalance: true })
  
  if (jumbo === 0 && disabled === 0 && diff <= 8) {
    print("│  ✓ No issues detected".padEnd(60) + "│")
  } else {
    if (jumbo > 0) {
      print(`│  ⚠ Jumbo chunks: ${jumbo}`.padEnd(60) + "│")
    }
    if (disabled > 0) {
      print(`│  ! Disabled collections: ${disabled}`.padEnd(60) + "│")
    }
    if (diff > 8) {
      print(`│  ! Chunk imbalance: ${diff}`.padEnd(60) + "│")
    }
  }
  print("└────────────────────────────────────────────────────────────┘")
  
  print("\nLast updated: " + new Date().toISOString())
}

// Run dashboard
// balancerDashboard()
```

### Exercise 2: Balancer Window Manager

```javascript
// Manage balancer windows

function manageBalancerWindow(action, options = {}) {
  print("=== Balancer Window Manager ===\n")
  
  const config = db.getSiblingDB("config")
  
  if (action === "show") {
    const settings = config.settings.findOne({ _id: "balancer" })
    
    if (settings?.activeWindow) {
      print(`Current Window: ${settings.activeWindow.start} - ${settings.activeWindow.stop}`)
      
      // Check if currently active
      const now = new Date()
      const hours = now.getHours().toString().padStart(2, '0')
      const mins = now.getMinutes().toString().padStart(2, '0')
      const currentTime = `${hours}:${mins}`
      
      const inWindow = isTimeInWindow(currentTime, 
        settings.activeWindow.start, 
        settings.activeWindow.stop)
      
      print(`Current time: ${currentTime}`)
      print(`Balancer active: ${inWindow ? "Yes" : "No"}`)
    } else {
      print("No window set - balancer runs 24/7")
    }
    
  } else if (action === "set") {
    const { start, stop } = options
    
    if (!start || !stop) {
      print("Error: start and stop times required")
      print("Example: manageBalancerWindow('set', { start: '23:00', stop: '05:00' })")
      return
    }
    
    // Validate format
    const timeRegex = /^([01]?[0-9]|2[0-3]):[0-5][0-9]$/
    if (!timeRegex.test(start) || !timeRegex.test(stop)) {
      print("Error: Invalid time format. Use HH:MM (24-hour)")
      return
    }
    
    config.settings.updateOne(
      { _id: "balancer" },
      { $set: { activeWindow: { start, stop } } },
      { upsert: true }
    )
    
    print(`✓ Balancer window set: ${start} - ${stop}`)
    
  } else if (action === "clear") {
    config.settings.updateOne(
      { _id: "balancer" },
      { $unset: { activeWindow: 1 } }
    )
    
    print("✓ Balancer window cleared - runs 24/7")
    
  } else {
    print("Actions: show, set, clear")
    print("Example: manageBalancerWindow('set', { start: '23:00', stop: '05:00' })")
  }
}

function isTimeInWindow(current, start, stop) {
  // Simple comparison (doesn't handle crossing midnight perfectly)
  if (start < stop) {
    return current >= start && current < stop
  } else {
    // Window crosses midnight
    return current >= start || current < stop
  }
}

// Examples:
// manageBalancerWindow("show")
// manageBalancerWindow("set", { start: "23:00", stop: "05:00" })
// manageBalancerWindow("clear")
```

### Exercise 3: Migration Monitor

```javascript
// Monitor migrations in detail

function monitorMigrations(durationMinutes = 5) {
  print(`=== Migration Monitor (${durationMinutes} minutes) ===\n`)
  
  const startTime = new Date()
  const endTime = new Date(startTime.getTime() + durationMinutes * 60 * 1000)
  
  const stats = {
    completed: 0,
    failed: 0,
    inProgress: 0,
    byCollection: {}
  }
  
  print("Monitoring... (Ctrl+C to stop)\n")
  
  let lastCheck = 0
  
  while (new Date() < endTime) {
    // Check active migrations
    const active = db.currentOp({
      "command.moveChunk": { $exists: true }
    })
    
    stats.inProgress = active.inprog.length
    
    if (active.inprog.length > 0) {
      active.inprog.forEach(op => {
        const ns = op.command.moveChunk
        print(`[${new Date().toLocaleTimeString()}] Active: ${ns}`)
        print(`  From: ${op.command.from} To: ${op.command.to}`)
        if (op.progress) {
          const pct = (op.progress.done / op.progress.total * 100).toFixed(1)
          print(`  Progress: ${pct}%`)
        }
      })
    }
    
    // Check recent completions
    const recentMigrations = db.getSiblingDB("config").changelog.find({
      what: { $in: ["moveChunk.commit", "moveChunk.from"] },
      time: { $gt: new Date(startTime.getTime() + lastCheck) }
    }).toArray()
    
    recentMigrations.forEach(m => {
      if (m.what === "moveChunk.commit") {
        stats.completed++
        const ns = m.ns
        stats.byCollection[ns] = (stats.byCollection[ns] || 0) + 1
        print(`[${m.time.toLocaleTimeString()}] ✓ Completed: ${ns}`)
      } else if (m.details?.errmsg) {
        stats.failed++
        print(`[${m.time.toLocaleTimeString()}] ✗ Failed: ${m.details.errmsg}`)
      }
    })
    
    lastCheck = new Date().getTime() - startTime.getTime()
    sleep(10000)  // Check every 10 seconds
  }
  
  // Summary
  print("\n=== Summary ===")
  print(`Duration: ${durationMinutes} minutes`)
  print(`Completed migrations: ${stats.completed}`)
  print(`Failed migrations: ${stats.failed}`)
  print(`Currently in progress: ${stats.inProgress}`)
  
  if (Object.keys(stats.byCollection).length > 0) {
    print("\nBy Collection:")
    Object.entries(stats.byCollection).forEach(([ns, count]) => {
      print(`  ${ns}: ${count}`)
    })
  }
  
  return stats
}

// Usage
// monitorMigrations(5)  // Monitor for 5 minutes
```

### Exercise 4: Collection Balance Optimizer

```javascript
// Optimize collection balancing

function optimizeCollectionBalance(namespace) {
  print(`=== Collection Balance Optimizer: ${namespace} ===\n`)
  
  const config = db.getSiblingDB("config")
  
  // Get current state
  const collInfo = config.collections.findOne({ _id: namespace })
  if (!collInfo) {
    print("Collection not sharded")
    return
  }
  
  // Check balancing enabled
  print("Current Settings:")
  print(`  Balancing: ${collInfo.noBalance ? "Disabled" : "Enabled"}`)
  
  // Get distribution
  const dist = config.chunks.aggregate([
    { $match: { ns: namespace } },
    { $group: { _id: "$shard", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ]).toArray()
  
  print("\nCurrent Distribution:")
  const total = dist.reduce((sum, d) => sum + d.count, 0)
  const avg = total / dist.length
  const maxDiff = dist[0].count - dist[dist.length - 1].count
  
  dist.forEach(d => {
    const diff = (d.count - avg).toFixed(1)
    const sign = diff > 0 ? "+" : ""
    print(`  ${d._id}: ${d.count} chunks (${sign}${diff} from avg)`)
  })
  
  print(`\nTotal chunks: ${total}`)
  print(`Average per shard: ${avg.toFixed(1)}`)
  print(`Max difference: ${maxDiff}`)
  
  // Check jumbo chunks
  const jumbo = config.chunks.countDocuments({ ns: namespace, jumbo: true })
  if (jumbo > 0) {
    print(`\n⚠ Jumbo chunks: ${jumbo}`)
  }
  
  // Recommendations
  print("\nRecommendations:")
  
  if (maxDiff > 8) {
    print("  1. Enable balancing if disabled: sh.enableBalancing('" + namespace + "')")
    print("  2. Check for jumbo chunks blocking migration")
    print("  3. Verify balancer is running: sh.isBalancerRunning()")
  } else if (maxDiff > 4) {
    print("  1. Cluster is slightly imbalanced")
    print("  2. Balancer should correct automatically")
    print("  3. Monitor: db.getSiblingDB('config').changelog.find({what:'moveChunk.commit'}).sort({time:-1}).limit(5)")
  } else {
    print("  ✓ Collection is well balanced")
    print("  No action needed")
  }
  
  // Estimate time to balance
  if (maxDiff > 8 && !collInfo.noBalance) {
    const chunksToMove = Math.ceil((maxDiff * dist.length) / 2)
    const estimatedMinutes = chunksToMove * 2  // Rough estimate: 2 min per chunk
    print(`\nEstimated time to balance: ~${estimatedMinutes} minutes`)
  }
  
  return { dist, total, avg, maxDiff, jumbo }
}

// Usage
// optimizeCollectionBalance("mydb.orders")
```

### Exercise 5: Balancer Troubleshooter

```javascript
// Troubleshoot balancer issues

function troubleshootBalancer() {
  print("=== Balancer Troubleshooter ===\n")
  
  const issues = []
  const config = db.getSiblingDB("config")
  
  // Check 1: Balancer enabled
  print("Check 1: Balancer State")
  const state = sh.getBalancerState()
  if (!state) {
    issues.push({
      issue: "Balancer is disabled",
      fix: "sh.startBalancer()"
    })
    print("  ✗ Balancer is DISABLED")
  } else {
    print("  ✓ Balancer is enabled")
  }
  
  // Check 2: Active window
  print("\nCheck 2: Active Window")
  const settings = config.settings.findOne({ _id: "balancer" })
  if (settings?.activeWindow) {
    const now = new Date()
    const hours = now.getHours().toString().padStart(2, '0')
    const mins = now.getMinutes().toString().padStart(2, '0')
    const current = `${hours}:${mins}`
    
    print(`  Window: ${settings.activeWindow.start} - ${settings.activeWindow.stop}`)
    print(`  Current: ${current}`)
    
    // Simple check (doesn't handle midnight crossing)
    const inWindow = current >= settings.activeWindow.start || 
                     current < settings.activeWindow.stop
    
    if (!inWindow) {
      issues.push({
        issue: "Outside balancer window",
        fix: "Wait for window or adjust: db.settings.updateOne({_id:'balancer'}, {$set:{activeWindow:{start:'00:00',stop:'23:59'}}})"
      })
      print("  ! Currently OUTSIDE active window")
    }
  } else {
    print("  ✓ No window restriction")
  }
  
  // Check 3: Collection balancing
  print("\nCheck 3: Collection Balancing")
  const disabledColls = config.collections.find({ noBalance: true }).toArray()
  if (disabledColls.length > 0) {
    issues.push({
      issue: `${disabledColls.length} collections have balancing disabled`,
      fix: "sh.enableBalancing('namespace')"
    })
    disabledColls.forEach(c => print(`  ✗ ${c._id}: Balancing DISABLED`))
  } else {
    print("  ✓ All collections have balancing enabled")
  }
  
  // Check 4: Jumbo chunks
  print("\nCheck 4: Jumbo Chunks")
  const jumboCount = config.chunks.countDocuments({ jumbo: true })
  if (jumboCount > 0) {
    issues.push({
      issue: `${jumboCount} jumbo chunks cannot be migrated`,
      fix: "db.adminCommand({clearJumboFlag:'namespace',find:{key:value}}) or refine shard key"
    })
    print(`  ✗ ${jumboCount} jumbo chunks found`)
  } else {
    print("  ✓ No jumbo chunks")
  }
  
  // Check 5: Shard availability
  print("\nCheck 5: Shard Availability")
  const shards = db.adminCommand({ listShards: 1 }).shards || []
  const unavailable = shards.filter(s => s.state !== 1)
  if (unavailable.length > 0) {
    issues.push({
      issue: `${unavailable.length} shards unavailable`,
      fix: "Check shard server status"
    })
    unavailable.forEach(s => print(`  ✗ ${s._id}: Unavailable`))
  } else {
    print(`  ✓ All ${shards.length} shards available`)
  }
  
  // Summary
  print("\n" + "=".repeat(50))
  
  if (issues.length === 0) {
    print("\n✓ No issues found - balancer should be working correctly")
  } else {
    print(`\n✗ Found ${issues.length} issue(s):\n`)
    issues.forEach((issue, i) => {
      print(`${i + 1}. ${issue.issue}`)
      print(`   Fix: ${issue.fix}`)
      print()
    })
  }
  
  return issues
}

// Run troubleshooter
// troubleshootBalancer()
```

---

[← Previous: Chunk Management](47-chunk-management.md) | [Next: Sharded Cluster Administration →](49-sharded-cluster-administration.md)
