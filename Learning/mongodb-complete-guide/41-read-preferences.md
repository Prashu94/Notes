# Chapter 41: Read Preferences

## Table of Contents
- [Understanding Read Preferences](#understanding-read-preferences)
- [Read Preference Modes](#read-preference-modes)
- [Tag Sets](#tag-sets)
- [MaxStalenessSeconds](#maxstalenessseconds)
- [Hedged Reads](#hedged-reads)
- [Read Preference in Practice](#read-preference-in-practice)
- [Summary](#summary)

---

## Understanding Read Preferences

Read preferences control how MongoDB routes read operations to members of a replica set.

### Read Preference Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Read Preference Flow                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application                                                       │
│       │                                                            │
│       │ Read Request + Read Preference                             │
│       ▼                                                            │
│  ┌─────────────────────┐                                           │
│  │    MongoDB Driver   │                                           │
│  │  (Route based on    │                                           │
│  │   read preference)  │                                           │
│  └──────────┬──────────┘                                           │
│             │                                                       │
│   ┌─────────┴─────────┐                                            │
│   │                   │                                            │
│   ▼                   ▼                                            │
│ ┌─────────┐    ┌───────────┐                                       │
│ │ PRIMARY │    │ SECONDARY │                                       │
│ │(default)│    │(if allowed)│                                       │
│ └─────────┘    └───────────┘                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Use Read Preferences?

| Use Case | Recommended Mode |
|----------|------------------|
| Strong consistency | primary |
| Disaster recovery reads | primaryPreferred |
| Read scaling | secondary |
| Geographic locality | nearest |
| Analytics workloads | secondary + tags |

---

## Read Preference Modes

### Available Modes

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Read Preference Modes                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  primary                                                           │
│  └── Read only from primary (default)                              │
│      Guarantees latest data                                        │
│                                                                     │
│  primaryPreferred                                                  │
│  └── Primary if available, else secondary                          │
│      Best for high availability                                    │
│                                                                     │
│  secondary                                                         │
│  └── Read only from secondaries                                    │
│      May read stale data                                           │
│                                                                     │
│  secondaryPreferred                                                │
│  └── Secondary if available, else primary                          │
│      Offload reads from primary                                    │
│                                                                     │
│  nearest                                                           │
│  └── Read from member with lowest network latency                  │
│      Best for geographic distribution                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Mode Details

| Mode | Primary | Secondary | Use Case |
|------|---------|-----------|----------|
| `primary` | Always | Never | Default, consistency |
| `primaryPreferred` | Preferred | Fallback | High availability |
| `secondary` | Never | Always | Read scaling |
| `secondaryPreferred` | Fallback | Preferred | Offload primary |
| `nearest` | If lowest latency | If lowest latency | Latency-sensitive |

### Setting Read Preference

```javascript
// In mongosh - session level
db.getMongo().setReadPref("secondary")

// Per operation
db.collection.find().readPref("secondary")

// Per collection
db.getSiblingDB("mydb").getCollection("mycoll").find().readPref("nearest")
```

### Connection String

```javascript
// In connection string
const uri = "mongodb://host1,host2,host3/?replicaSet=rs0&readPreference=secondary"

// With Node.js driver
const { MongoClient } = require('mongodb')
const client = new MongoClient(uri, {
  readPreference: 'secondaryPreferred'
})

// Per-database/collection override
const db = client.db('mydb', { readPreference: 'primary' })
const collection = db.collection('users', { readPreference: 'nearest' })
```

---

## Tag Sets

### Understanding Tag Sets

```javascript
// Tags allow fine-grained routing control
// Configure tags in replica set config

cfg = rs.conf()
cfg.members[0].tags = { dc: "east", rack: "r1" }
cfg.members[1].tags = { dc: "east", rack: "r2" }
cfg.members[2].tags = { dc: "west", rack: "r1" }
rs.reconfig(cfg)
```

### Using Tags in Read Preference

```javascript
// Read from specific data center
db.getMongo().setReadPref("secondary", [{ dc: "west" }])

// Read from east DC, rack r1
db.collection.find().readPref("secondary", [{ dc: "east", rack: "r1" }])

// Fallback tag sets (try in order)
db.getMongo().setReadPref("secondary", [
  { dc: "west", rack: "r1" },   // First choice
  { dc: "west" },               // Second choice
  {}                            // Any secondary
])
```

### Tag Set Matching Rules

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Tag Set Matching                                  │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Tag Set: [{ dc: "west", rack: "r1" }]                             │
│                                                                     │
│  Member Tags               | Match?                                │
│  ─────────────────────────┼───────                                │
│  { dc: "west", rack: "r1" }  | ✓ Yes (exact match)                │
│  { dc: "west", rack: "r1",   | ✓ Yes (superset)                   │
│    tier: "ssd" }              |                                    │
│  { dc: "west" }               | ✗ No (missing rack)               │
│  { dc: "east", rack: "r1" }  | ✗ No (wrong dc)                   │
│                                                                     │
│  Rule: Member tags must contain ALL specified tag key-value pairs │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Tag Set Examples

```javascript
// Geographic read preference
// Read from local DC first, then any DC
db.getMongo().setReadPref("nearest", [
  { dc: "us-west" },  // Prefer local
  {}                  // Fallback to any
])

// Workload isolation
// Analytics queries go to analytics-tagged nodes
db.getMongo().setReadPref("secondary", [
  { workload: "analytics" }
])

// Hardware tier preference
// Prefer SSD nodes for faster reads
db.getMongo().setReadPref("secondaryPreferred", [
  { tier: "ssd" },
  { tier: "hdd" }
])

// Multi-criteria
db.getMongo().setReadPref("secondary", [
  { dc: "us-west", tier: "ssd", workload: "analytics" },
  { dc: "us-west", tier: "ssd" },
  { dc: "us-west" },
  {}
])
```

---

## MaxStalenessSeconds

### Understanding Staleness

```javascript
// maxStalenessSeconds limits how stale a secondary's data can be
// Minimum value: 90 seconds
// Must be at least heartbeat interval + 10 seconds

// Set max staleness of 2 minutes
db.getMongo().setReadPref("secondary", [], { maxStalenessSeconds: 120 })

// In connection string
// mongodb://host1,host2/?readPreference=secondary&maxStalenessSeconds=120
```

### Staleness Calculation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Staleness Calculation                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  For secondaries:                                                  │
│  staleness = (secondary's lastWrite timestamp)                     │
│            - (secondary's lastWrite timestamp received from primary)│
│                                                                     │
│  If staleness > maxStalenessSeconds:                               │
│  └── Member excluded from selection                                │
│                                                                     │
│  Example Timeline:                                                 │
│  ├── Primary writes at T=100                                       │
│  ├── Secondary applies at T=105                                    │
│  ├── Secondary reports lastWrite = 100                             │
│  ├── Current time = 200                                            │
│  └── Staleness = 200 - 100 = 100 seconds                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### MaxStaleness Best Practices

| Scenario | Recommended Value |
|----------|-------------------|
| Strict freshness | 90-120 seconds |
| Balanced | 120-300 seconds |
| Relaxed (analytics) | 300+ seconds |
| No staleness check | Omit parameter |

```javascript
// For time-sensitive data
db.getMongo().setReadPref("secondary", [], { maxStalenessSeconds: 90 })

// For analytics (more relaxed)
db.getMongo().setReadPref("secondary", [{ workload: "analytics" }], { 
  maxStalenessSeconds: 300 
})

// Combined with tags
db.collection.find().readPref("secondaryPreferred", 
  [{ dc: "local" }], 
  { maxStalenessSeconds: 120 }
)
```

---

## Hedged Reads

### Understanding Hedged Reads

```javascript
// Hedged reads send read to multiple members
// Returns first result received
// Available for sharded clusters with read preference "nearest"

// MongoDB 4.4+ feature
// Configured at mongos level

// In connection string (for mongos)
// mongodb://mongos1,mongos2/?readPreference=nearest&hedge=true
```

### Hedged Read Configuration

```javascript
// Server-side configuration
// In mongos, set readHedgingMode

// Enable hedging
db.adminCommand({
  setParameter: 1,
  readHedgingMode: "on"
})

// Disable hedging
db.adminCommand({
  setParameter: 1,
  readHedgingMode: "off"
})

// Check current setting
db.adminCommand({ getParameter: 1, readHedgingMode: 1 })
```

### Hedged Reads Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Hedged Reads Flow                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application Read Request                                          │
│           │                                                        │
│           ▼                                                        │
│       mongos ──────────┬────────────┐                              │
│           │            │            │                              │
│           ▼            ▼            ▼                              │
│       ┌─────┐      ┌─────┐      ┌─────┐                           │
│       │Node1│      │Node2│      │Node3│                           │
│       │ 5ms │      │10ms │      │ 8ms │                           │
│       └──┬──┘      └──┬──┘      └──┬──┘                           │
│          │            │            │                              │
│          ▼            │            │                              │
│      First            ✗            ✗                              │
│      Response     (cancelled)  (cancelled)                        │
│          │                                                        │
│          ▼                                                        │
│     Return to Client (5ms response time)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Read Preference in Practice

### Common Patterns

```javascript
// Pattern 1: Default (Strong Consistency)
// Use for: Financial data, inventory, user sessions
db.getMongo().setReadPref("primary")
// or simply don't set read preference (primary is default)

// Pattern 2: High Availability Reads
// Use for: Non-critical reads that must always succeed
db.getMongo().setReadPref("primaryPreferred")

// Pattern 3: Read Scaling
// Use for: High read volume, can tolerate slight staleness
db.getMongo().setReadPref("secondaryPreferred")

// Pattern 4: Analytics
// Use for: Reports, dashboards, batch processing
db.getMongo().setReadPref("secondary", [{ usage: "analytics" }])

// Pattern 5: Geographic Locality
// Use for: Multi-region deployments
db.getMongo().setReadPref("nearest", [
  { region: userRegion },
  {}  // Fallback to any region
])
```

### Operation-Specific Read Preference

```javascript
// Different read preferences for different operations

// User profile - strong consistency
const profile = db.users.findOne(
  { _id: userId }
).readPref("primary")

// Product catalog - can be slightly stale
const products = db.products.find(
  { category: "electronics" }
).readPref("secondaryPreferred")

// Analytics dashboard - definitely use secondary
const stats = db.orders.aggregate([
  { $match: { date: { $gte: lastMonth } } },
  { $group: { _id: "$status", count: { $sum: 1 } } }
]).readPref("secondary")

// Real-time inventory - must be current
const inventory = db.inventory.findOne(
  { productId: "SKU123" }
).readPref("primary")
```

### Transactions and Read Preference

```javascript
// In transactions, read preference has restrictions

const session = db.getMongo().startSession()

session.startTransaction({
  readConcern: { level: "snapshot" },
  writeConcern: { w: "majority" }
})

// First read in transaction sets the read preference
// All subsequent reads must use same preference

// Reads in a transaction should use primary or primaryPreferred
// for write transactions
```

### Monitoring Read Distribution

```javascript
// Check which members are receiving reads
// On each member, check serverStatus

db.serverStatus().opcounters

// Result includes:
{
  query: 12345,    // Find operations
  getmore: 6789,   // Cursor iterations
  // ...
}

// Monitor read preference usage via profiler
db.setProfilingLevel(2)  // Enable full profiling

// Then check profiler for read operations
db.system.profile.find({
  op: "query"
}).sort({ ts: -1 }).limit(10)
```

### Best Practices

```
┌─────────────────────────────────────────────────────────────────────┐
│                Read Preference Best Practices                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Use primary for:                                               │
│     ├── Read-after-write consistency                               │
│     ├── Critical business data                                     │
│     └── Real-time inventory/balances                               │
│                                                                     │
│  2. Use secondaryPreferred for:                                    │
│     ├── High availability reads                                    │
│     ├── Read-heavy workloads                                       │
│     └── When slight staleness is acceptable                        │
│                                                                     │
│  3. Use nearest for:                                               │
│     ├── Latency-sensitive reads                                    │
│     ├── Geographically distributed apps                            │
│     └── When data freshness is less critical                       │
│                                                                     │
│  4. Always use tags for:                                           │
│     ├── Workload isolation                                         │
│     ├── Geographic targeting                                       │
│     └── Hardware tier selection                                    │
│                                                                     │
│  5. Consider maxStalenessSeconds for:                              │
│     ├── Time-sensitive data                                        │
│     └── Balanced freshness/availability                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Read Preference Modes

| Mode | Primary | Secondary | Best For |
|------|---------|-----------|----------|
| primary | Always | Never | Consistency |
| primaryPreferred | Preferred | Fallback | HA reads |
| secondary | Never | Always | Scaling |
| secondaryPreferred | Fallback | Preferred | Offload |
| nearest | Lowest latency | Lowest latency | Latency |

### Key Concepts

| Concept | Purpose |
|---------|---------|
| Tag sets | Route to specific members |
| maxStalenessSeconds | Limit data staleness |
| Hedged reads | Reduce latency variance |

### Setting Read Preference

| Level | Method |
|-------|--------|
| Connection | Connection string |
| Client | Driver options |
| Database | db.getMongo().setReadPref() |
| Collection | Collection options |
| Operation | cursor.readPref() |

### What's Next?

In the next chapter, we'll explore Write Concerns in detail.

---

## Practice Questions

1. What's the default read preference?
2. When would you use primaryPreferred vs secondaryPreferred?
3. How do tag sets work with read preferences?
4. What is the minimum maxStalenessSeconds value?
5. What are hedged reads?
6. Why would you avoid reading from secondaries for some data?
7. How do you set read preference per operation?
8. What restrictions apply to read preference in transactions?

---

## Hands-On Exercises

### Exercise 1: Read Preference Basics

```javascript
// Demonstrate different read preferences

// Check current read preference
print("=== Current Read Preference ===")
print(db.getMongo().getReadPrefMode())

// Test primary (default)
print("\n=== Primary Mode ===")
db.getMongo().setReadPref("primary")
print("Mode:", db.getMongo().getReadPrefMode())

// Test secondary
print("\n=== Secondary Mode ===")
db.getMongo().setReadPref("secondary")
print("Mode:", db.getMongo().getReadPrefMode())

// Test secondaryPreferred
print("\n=== SecondaryPreferred Mode ===")
db.getMongo().setReadPref("secondaryPreferred")
print("Mode:", db.getMongo().getReadPrefMode())

// Test nearest
print("\n=== Nearest Mode ===")
db.getMongo().setReadPref("nearest")
print("Mode:", db.getMongo().getReadPrefMode())

// Reset to primary
db.getMongo().setReadPref("primary")
print("\nReset to primary")
```

### Exercise 2: Tag-Based Read Preference

```javascript
// Demonstrate tag-based routing

// Sample tag configuration (documentation)
const tagConfig = {
  members: [
    { _id: 0, host: "mongo1:27017", tags: { dc: "us-east", rack: "r1" } },
    { _id: 1, host: "mongo2:27017", tags: { dc: "us-east", rack: "r2" } },
    { _id: 2, host: "mongo3:27017", tags: { dc: "us-west", rack: "r1" } }
  ]
}

print("=== Tag-Based Read Preference Examples ===\n")

// Example 1: Read from specific DC
print("1. Read from us-west DC:")
print('   db.getMongo().setReadPref("secondary", [{ dc: "us-west" }])')

// Example 2: Fallback chain
print("\n2. Fallback chain:")
print('   db.getMongo().setReadPref("secondary", [')
print('     { dc: "us-west", rack: "r1" },  // First choice')
print('     { dc: "us-west" },               // Second choice')
print('     {}                               // Any secondary')
print('   ])')

// Example 3: Multiple criteria
print("\n3. Multiple criteria:")
print('   db.getMongo().setReadPref("nearest", [')
print('     { dc: "local", tier: "ssd" },')
print('     { dc: "local" },')
print('     { tier: "ssd" },')
print('     {}')
print('   ])')

// Simulate tag matching
function matchTags(memberTags, requestedTags) {
  for (const [key, value] of Object.entries(requestedTags)) {
    if (memberTags[key] !== value) return false
  }
  return true
}

print("\n=== Tag Matching Simulation ===")
const memberTags = { dc: "us-west", rack: "r1", tier: "ssd" }
const testCases = [
  { dc: "us-west" },
  { dc: "us-west", rack: "r1" },
  { dc: "us-east" },
  { tier: "ssd" },
  { dc: "us-west", tier: "hdd" }
]

print("Member tags:", JSON.stringify(memberTags))
testCases.forEach(t => {
  const match = matchTags(memberTags, t)
  print(`  ${JSON.stringify(t)} → ${match ? "✓ Match" : "✗ No match"}`)
})
```

### Exercise 3: MaxStalenessSeconds

```javascript
// Understand maxStalenessSeconds

print("=== MaxStalenessSeconds Guide ===\n")

// Configuration examples
const scenarios = [
  {
    name: "Financial data",
    maxStaleness: 90,
    readPref: "secondaryPreferred",
    reason: "Need near-real-time data"
  },
  {
    name: "Product catalog",
    maxStaleness: 300,
    readPref: "secondary",
    reason: "Catalog changes rarely"
  },
  {
    name: "Analytics dashboard",
    maxStaleness: 600,
    readPref: "secondary",
    reason: "Historical data, freshness less critical"
  },
  {
    name: "Real-time inventory",
    maxStaleness: null,
    readPref: "primary",
    reason: "Must be current, use primary"
  }
]

scenarios.forEach(s => {
  print(`${s.name}:`)
  print(`  Read Preference: ${s.readPref}`)
  print(`  Max Staleness: ${s.maxStaleness ? s.maxStaleness + "s" : "N/A (use primary)"}`)
  print(`  Reason: ${s.reason}`)
  print()
})

// Staleness calculation example
print("=== Staleness Calculation Example ===")
const primaryLastWrite = new Date("2024-01-01T10:00:00Z")
const secondaryLastWrite = new Date("2024-01-01T09:58:30Z")
const currentTime = new Date("2024-01-01T10:00:00Z")

const staleness = (primaryLastWrite - secondaryLastWrite) / 1000
print(`Primary last write: ${primaryLastWrite.toISOString()}`)
print(`Secondary last write: ${secondaryLastWrite.toISOString()}`)
print(`Calculated staleness: ${staleness} seconds`)
print(`Would be selected if maxStalenessSeconds >= ${staleness}`)
```

### Exercise 4: Read Preference Decision Matrix

```javascript
// Decision matrix for choosing read preference

print("=== Read Preference Decision Matrix ===\n")

function recommendReadPref(requirements) {
  const { consistency, availability, latency, canReadStale, volume } = requirements
  
  if (consistency === "strong") {
    return { mode: "primary", reason: "Strong consistency required" }
  }
  
  if (!canReadStale) {
    return { mode: "primaryPreferred", reason: "Cannot tolerate stale reads" }
  }
  
  if (latency === "critical") {
    return { mode: "nearest", reason: "Latency is critical" }
  }
  
  if (availability === "critical") {
    return { mode: "secondaryPreferred", reason: "High availability needed" }
  }
  
  if (volume === "high") {
    return { mode: "secondary", reason: "Offload read volume from primary" }
  }
  
  return { mode: "primary", reason: "Default for consistency" }
}

// Test scenarios
const testScenarios = [
  { name: "User authentication", consistency: "strong", availability: "high", latency: "normal", canReadStale: false, volume: "medium" },
  { name: "Product search", consistency: "eventual", availability: "critical", latency: "critical", canReadStale: true, volume: "high" },
  { name: "Order history", consistency: "eventual", availability: "high", latency: "normal", canReadStale: true, volume: "medium" },
  { name: "Analytics dashboard", consistency: "eventual", availability: "normal", latency: "normal", canReadStale: true, volume: "high" },
  { name: "Inventory check", consistency: "strong", availability: "high", latency: "critical", canReadStale: false, volume: "high" }
]

testScenarios.forEach(scenario => {
  const recommendation = recommendReadPref(scenario)
  print(`${scenario.name}:`)
  print(`  Requirements: ${JSON.stringify(scenario)}`)
  print(`  Recommendation: ${recommendation.mode}`)
  print(`  Reason: ${recommendation.reason}`)
  print()
})
```

### Exercise 5: Read Preference Configuration Helper

```javascript
// Helper to generate read preference configurations

function createReadPrefConfig(options) {
  const config = {
    mode: options.mode || "primary",
    tagSets: [],
    maxStalenessSeconds: options.maxStaleness
  }
  
  // Build tag sets
  if (options.preferredDC) {
    config.tagSets.push({ dc: options.preferredDC })
  }
  if (options.preferredTier) {
    config.tagSets.push({ tier: options.preferredTier })
  }
  if (options.workload) {
    config.tagSets.push({ workload: options.workload })
  }
  
  // Add fallback
  if (config.tagSets.length > 0) {
    config.tagSets.push({})  // Fallback to any matching member
  }
  
  return config
}

// Generate configurations
print("=== Read Preference Configuration Generator ===\n")

const configs = [
  createReadPrefConfig({
    mode: "secondary",
    preferredDC: "us-west",
    preferredTier: "ssd",
    maxStaleness: 120
  }),
  createReadPrefConfig({
    mode: "nearest",
    preferredDC: "us-east"
  }),
  createReadPrefConfig({
    mode: "secondary",
    workload: "analytics",
    maxStaleness: 300
  })
]

configs.forEach((cfg, i) => {
  print(`Configuration ${i + 1}:`)
  print(`  Mode: ${cfg.mode}`)
  print(`  Tag Sets: ${JSON.stringify(cfg.tagSets)}`)
  print(`  Max Staleness: ${cfg.maxStalenessSeconds || "not set"}`)
  
  // Generate code
  print(`  Code:`)
  if (cfg.tagSets.length > 0 || cfg.maxStalenessSeconds) {
    print(`    db.getMongo().setReadPref("${cfg.mode}",`)
    print(`      ${JSON.stringify(cfg.tagSets)},`)
    print(`      ${cfg.maxStalenessSeconds ? `{ maxStalenessSeconds: ${cfg.maxStalenessSeconds} }` : '{}'})`)
  } else {
    print(`    db.getMongo().setReadPref("${cfg.mode}")`)
  }
  print()
})
```

---

[← Previous: Replica Set Configuration](40-replica-set-configuration.md) | [Next: Write Concerns →](42-write-concerns.md)
