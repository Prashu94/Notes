# Chapter 42: Write Concerns

## Table of Contents
- [Understanding Write Concerns](#understanding-write-concerns)
- [Write Concern Levels](#write-concern-levels)
- [w Option](#w-option)
- [j Option (Journaling)](#j-option-journaling)
- [wtimeout Option](#wtimeout-option)
- [Custom Write Concerns](#custom-write-concerns)
- [Write Concern in Practice](#write-concern-in-practice)
- [Summary](#summary)

---

## Understanding Write Concerns

Write concern describes the level of acknowledgment requested from MongoDB for write operations. It controls durability and consistency guarantees.

### Write Concern Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Write Concern Flow                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Application Write                                                 │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────┐                                                       │
│  │ PRIMARY │ ◄── Write received                                    │
│  └────┬────┘                                                       │
│       │                                                            │
│       ├── Apply to memory                                          │
│       ├── Write to journal (if j:true)                             │
│       └── Replicate to secondaries                                 │
│             │                                                       │
│     ┌───────┴───────┐                                              │
│     ▼               ▼                                              │
│ ┌───────────┐ ┌───────────┐                                        │
│ │ SECONDARY │ │ SECONDARY │                                        │
│ └───────────┘ └───────────┘                                        │
│                                                                     │
│  Acknowledgment based on write concern:                            │
│  ├── w:1    → Primary acknowledged                                 │
│  ├── w:2    → Primary + 1 secondary acknowledged                   │
│  ├── w:majority → Majority acknowledged                            │
│  └── j:true → Journaled before ack                                 │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Why Write Concerns Matter

| Write Concern | Durability | Performance | Use Case |
|--------------|------------|-------------|----------|
| w:0 | Lowest | Fastest | Fire-and-forget |
| w:1 | Low | Fast | Default |
| w:majority | High | Slower | Critical data |
| j:true | Higher | Slower | Financial transactions |

---

## Write Concern Levels

### Standard Levels

```javascript
// Write concern structure
{
  w: <value>,      // Acknowledgment level
  j: <boolean>,    // Journal acknowledgment
  wtimeout: <ms>   // Timeout for acknowledgment
}

// Examples
{ w: 0 }              // Unacknowledged
{ w: 1 }              // Primary acknowledged (default)
{ w: "majority" }     // Majority acknowledged
{ w: 2 }              // Primary + 1 secondary
{ w: 1, j: true }     // Primary with journal
{ w: "majority", j: true, wtimeout: 5000 }  // Full durability
```

### Write Concern Comparison

```
┌─────────────────────────────────────────────────────────────────────┐
│                Write Concern Comparison                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  w: 0 (Unacknowledged)                                             │
│  ├── No acknowledgment                                             │
│  ├── Cannot detect errors                                          │
│  ├── Fastest but least safe                                        │
│  └── Use for: Logging, metrics                                     │
│                                                                     │
│  w: 1 (Primary)                                                    │
│  ├── Primary acknowledges                                          │
│  ├── Can detect errors                                             │
│  ├── May be lost on failover                                       │
│  └── Use for: General operations                                   │
│                                                                     │
│  w: majority                                                       │
│  ├── Majority of voting members acknowledge                        │
│  ├── Survives failover                                             │
│  ├── Cannot be rolled back                                         │
│  └── Use for: Critical data                                        │
│                                                                     │
│  w: <number>                                                       │
│  ├── Specific count acknowledges                                   │
│  ├── Useful for specific durability                                │
│  └── Use for: Custom requirements                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## w Option

### w: 0 (Unacknowledged)

```javascript
// Fire and forget - no acknowledgment
db.logs.insertOne(
  { level: "info", message: "User logged in", timestamp: new Date() },
  { writeConcern: { w: 0 } }
)
// Returns immediately, doesn't wait for acknowledgment

// Use cases:
// - High-volume logging
// - Metrics collection
// - Data that can be lost

// ⚠️ Risks:
// - Cannot detect write failures
// - No error information
// - Data may be lost
```

### w: 1 (Primary Only)

```javascript
// Default write concern - primary acknowledges
db.users.insertOne(
  { name: "Alice", email: "alice@example.com" },
  { writeConcern: { w: 1 } }
)
// Returns after primary confirms write

// This is equivalent to:
db.users.insertOne({ name: "Alice", email: "alice@example.com" })

// Use cases:
// - General operations
// - Non-critical data
// - Performance-sensitive writes

// Considerations:
// - May be lost if primary fails before replication
// - Good balance of speed and safety
```

### w: "majority"

```javascript
// Wait for majority of voting members to acknowledge
db.orders.insertOne(
  { orderId: "ORD-001", total: 100, status: "pending" },
  { writeConcern: { w: "majority" } }
)

// Majority calculation:
// 3-member set: 2 members (primary + 1 secondary)
// 5-member set: 3 members
// 7-member set: 4 members

// Use cases:
// - Critical business data
// - Financial transactions
// - Data that cannot be lost

// Benefits:
// - Survives primary failover
// - Cannot be rolled back
```

### w: <number>

```javascript
// Wait for specific number of members
db.collection.insertOne(
  { data: "important" },
  { writeConcern: { w: 3 } }  // Wait for 3 members
)

// w: 2 - Primary + 1 secondary
db.collection.insertOne(
  { data: "important" },
  { writeConcern: { w: 2 } }
)

// Use cases:
// - Specific durability requirements
// - Cross-DC acknowledgment
```

---

## j Option (Journaling)

### Understanding Journaling

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Journal Write Flow                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Write Operation                                                   │
│       │                                                            │
│       ▼                                                            │
│  ┌─────────────┐                                                   │
│  │   Memory    │ ◄── Applied first                                 │
│  │  (fast)     │                                                   │
│  └──────┬──────┘                                                   │
│         │                                                          │
│         ▼                                                          │
│  ┌─────────────┐                                                   │
│  │   Journal   │ ◄── j:true waits here                             │
│  │  (on disk)  │                                                   │
│  └──────┬──────┘                                                   │
│         │                                                          │
│         ▼                                                          │
│  ┌─────────────┐                                                   │
│  │  Data Files │ ◄── Periodic flush (checkpoint)                   │
│  │  (on disk)  │                                                   │
│  └─────────────┘                                                   │
│                                                                     │
│  j:true ensures write survives server crash                        │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Using j Option

```javascript
// Wait for journal commit
db.transactions.insertOne(
  { txnId: "TXN-001", amount: 1000, type: "debit" },
  { writeConcern: { w: 1, j: true } }
)

// Combined with majority
db.transactions.insertOne(
  { txnId: "TXN-002", amount: 500, type: "credit" },
  { writeConcern: { w: "majority", j: true } }
)
// Maximum durability - majority + journaled

// Use cases for j:true:
// - Financial data
// - Audit logs
// - Data that must survive crashes
```

### Journal Commit Interval

```javascript
// MongoDB commits journal:
// - Every 100ms (default)
// - Or when j:true write is waiting

// Check journal settings
db.adminCommand({ getParameter: 1, journalCommitInterval: 1 })

// ⚠️ Note: j:true increases write latency
// Use only when durability is critical
```

---

## wtimeout Option

### Setting Timeouts

```javascript
// Wait up to 5 seconds for acknowledgment
db.orders.insertOne(
  { orderId: "ORD-003", items: [], total: 0 },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)

// If timeout exceeded:
// - Write may have succeeded on some members
// - Error returned to application
// - Application must handle appropriately

// ⚠️ wtimeout does NOT cancel the write
// It only limits how long driver waits for acknowledgment
```

### Handling Timeout Errors

```javascript
// Handle write concern timeout
try {
  db.orders.insertOne(
    { orderId: "ORD-004" },
    { writeConcern: { w: "majority", wtimeout: 1000 } }
  )
} catch (error) {
  if (error.code === 64) {  // WriteConcernFailed
    print("Write concern timeout - write may have succeeded")
    // Check if write actually succeeded
    const exists = db.orders.findOne({ orderId: "ORD-004" })
    if (exists) {
      print("Write succeeded despite timeout")
    } else {
      print("Write failed or not yet replicated")
    }
  } else {
    throw error
  }
}
```

### Timeout Best Practices

| Scenario | Recommended Timeout |
|----------|---------------------|
| Fast local writes | 1000-3000ms |
| Cross-DC replication | 5000-10000ms |
| High latency network | 10000-30000ms |
| Bulk operations | Longer timeouts |

---

## Custom Write Concerns

### Tag-Based Write Concerns

```javascript
// First, configure replica set with tags
cfg = rs.conf()
cfg.members[0].tags = { dc: "east" }
cfg.members[1].tags = { dc: "east" }
cfg.members[2].tags = { dc: "west" }
cfg.members[3].tags = { dc: "west" }
rs.reconfig(cfg)

// Define custom write concern modes
cfg = rs.conf()
cfg.settings.getLastErrorModes = {
  // Write to both data centers
  multiDC: { dc: 2 },
  
  // Write to at least one member in each rack
  multiRack: { rack: 2 }
}
rs.reconfig(cfg)

// Use custom write concern
db.criticalData.insertOne(
  { data: "cross-DC important" },
  { writeConcern: { w: "multiDC", wtimeout: 10000 } }
)
```

### Custom Write Concern Examples

```javascript
// Scenario: Multi-region deployment
// Requirement: Write must be in 2 different regions

// Configuration
cfg.members[0].tags = { region: "us-east", az: "us-east-1a" }
cfg.members[1].tags = { region: "us-east", az: "us-east-1b" }
cfg.members[2].tags = { region: "us-west", az: "us-west-1a" }
cfg.members[3].tags = { region: "eu-west", az: "eu-west-1a" }

cfg.settings.getLastErrorModes = {
  // At least 2 different regions
  multiRegion: { region: 2 },
  
  // At least 2 different availability zones
  multiAZ: { az: 2 },
  
  // Must include US region
  includeUS: { region: 1 }
}

// Use
db.important.insertOne(
  { data: "globally important" },
  { writeConcern: { w: "multiRegion", wtimeout: 30000 } }
)
```

---

## Write Concern in Practice

### Setting Default Write Concern

```javascript
// Connection-level default (in connection string)
// mongodb://host1,host2/?w=majority&wtimeoutMS=5000

// Database-level default (MongoDB 4.4+)
db.adminCommand({
  setDefaultRWConcern: 1,
  defaultWriteConcern: { w: "majority", wtimeout: 5000 }
})

// Check current defaults
db.adminCommand({ getDefaultRWConcern: 1 })
```

### Operation-Level Write Concern

```javascript
// Insert
db.collection.insertOne(
  { doc: 1 },
  { writeConcern: { w: "majority" } }
)

// Update
db.collection.updateOne(
  { _id: 1 },
  { $set: { status: "active" } },
  { writeConcern: { w: "majority" } }
)

// Delete
db.collection.deleteOne(
  { _id: 1 },
  { writeConcern: { w: "majority" } }
)

// Bulk write
db.collection.bulkWrite([
  { insertOne: { document: { x: 1 } } },
  { updateOne: { filter: { x: 1 }, update: { $set: { y: 2 } } } }
], { writeConcern: { w: "majority" } })
```

### Write Concern Patterns

```javascript
// Pattern 1: Fire and Forget (Logging)
function logEvent(event) {
  db.logs.insertOne(
    { ...event, timestamp: new Date() },
    { writeConcern: { w: 0 } }
  )
}

// Pattern 2: Standard Operations
function createUser(user) {
  return db.users.insertOne(user)  // Default w:1
}

// Pattern 3: Critical Data
function createOrder(order) {
  return db.orders.insertOne(order, {
    writeConcern: { w: "majority", j: true }
  })
}

// Pattern 4: Financial Transactions
function processPayment(payment) {
  const session = db.getMongo().startSession()
  
  try {
    session.startTransaction({
      writeConcern: { w: "majority", j: true }
    })
    
    // Operations...
    
    session.commitTransaction()
  } catch (e) {
    session.abortTransaction()
    throw e
  } finally {
    session.endSession()
  }
}
```

### Monitoring Write Concern

```javascript
// Check write concern errors in serverStatus
db.serverStatus().wiredTiger.concurrentTransactions

// Monitor via profiler
db.setProfilingLevel(2)

// Check profile for write concern issues
db.system.profile.find({
  "writeConcern": { $exists: true }
}).sort({ ts: -1 }).limit(10)

// GetLastError stats
db.serverStatus().getLastErrorModes
```

### Performance Impact

```
┌─────────────────────────────────────────────────────────────────────┐
│            Write Concern Performance Impact                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Write Concern    │ Relative Latency │ Durability                  │
│  ─────────────────┼──────────────────┼────────────                 │
│  w: 0             │ Fastest (1x)     │ None                        │
│  w: 1             │ Fast (1.1x)      │ Memory only                 │
│  w: 1, j: true    │ Medium (2x)      │ Journaled                   │
│  w: majority      │ Slow (2-3x)      │ Replicated                  │
│  w: majority, j   │ Slowest (3-4x)   │ Replicated + Journaled      │
│                                                                     │
│  Factors affecting latency:                                        │
│  ├── Network latency between members                               │
│  ├── Disk I/O speed (for journaling)                               │
│  ├── Number of members                                             │
│  └── Current load                                                  │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Write Concern Options

| Option | Values | Purpose |
|--------|--------|---------|
| `w` | 0, 1, "majority", number | Acknowledgment level |
| `j` | true, false | Journal confirmation |
| `wtimeout` | milliseconds | Maximum wait time |

### w Values

| Value | Acknowledgment |
|-------|----------------|
| 0 | None (fire-and-forget) |
| 1 | Primary only (default) |
| "majority" | Majority of voting members |
| n | Specific number of members |
| "tagName" | Custom tag-based |

### Recommendations

| Use Case | Write Concern |
|----------|---------------|
| Logging/Metrics | w:0 |
| General operations | w:1 (default) |
| Important data | w:"majority" |
| Critical/Financial | w:"majority", j:true |
| Cross-DC durability | Custom tags |

### What's Next?

In the next chapter, we'll explore Replica Set Maintenance operations.

---

## Practice Questions

1. What's the default write concern?
2. What does w:"majority" guarantee?
3. When would you use w:0?
4. What does the j option do?
5. What happens if wtimeout is exceeded?
6. How do you create custom write concerns?
7. What's the performance impact of j:true?
8. How do you set default write concern?

---

## Hands-On Exercises

### Exercise 1: Write Concern Basics

```javascript
// Test different write concerns

// Setup test collection
db.writeConcernTest.drop()

print("=== Write Concern Tests ===\n")

// w:0 - Unacknowledged
print("1. w:0 (Unacknowledged)")
const start0 = new Date()
db.writeConcernTest.insertOne(
  { test: "w0", timestamp: new Date() },
  { writeConcern: { w: 0 } }
)
print(`   Time: ${new Date() - start0}ms (returns immediately)`)

// w:1 - Primary (default)
print("\n2. w:1 (Primary)")
const start1 = new Date()
db.writeConcernTest.insertOne(
  { test: "w1", timestamp: new Date() },
  { writeConcern: { w: 1 } }
)
print(`   Time: ${new Date() - start1}ms`)

// Note: The following require a replica set
// w:majority
print("\n3. w:majority (requires replica set)")
print("   Code: { writeConcern: { w: 'majority' } }")

// w:majority with journal
print("\n4. w:majority, j:true (maximum durability)")
print("   Code: { writeConcern: { w: 'majority', j: true } }")

// Verify documents
print("\nDocuments created:")
db.writeConcernTest.find().forEach(printjson)
```

### Exercise 2: Write Concern Decision Helper

```javascript
// Help choose appropriate write concern

function recommendWriteConcern(requirements) {
  const {
    canLoseData,
    mustSurviveFailover,
    mustSurviveCrash,
    performanceCritical,
    crossDC
  } = requirements
  
  let writeConcern = { w: 1 }
  let reason = []
  
  if (canLoseData && performanceCritical) {
    writeConcern = { w: 0 }
    reason.push("Fire-and-forget for performance")
  } else if (mustSurviveFailover) {
    writeConcern.w = "majority"
    reason.push("Majority for failover survival")
  }
  
  if (mustSurviveCrash && writeConcern.w !== 0) {
    writeConcern.j = true
    reason.push("Journal for crash survival")
  }
  
  if (crossDC && writeConcern.w === "majority") {
    writeConcern.wtimeout = 10000
    reason.push("Extended timeout for cross-DC")
  } else if (writeConcern.w !== 0) {
    writeConcern.wtimeout = 5000
    reason.push("Standard timeout")
  }
  
  return { writeConcern, reason }
}

// Test scenarios
print("=== Write Concern Recommendations ===\n")

const scenarios = [
  {
    name: "Logging",
    requirements: { canLoseData: true, mustSurviveFailover: false, mustSurviveCrash: false, performanceCritical: true, crossDC: false }
  },
  {
    name: "User Profile",
    requirements: { canLoseData: false, mustSurviveFailover: true, mustSurviveCrash: false, performanceCritical: false, crossDC: false }
  },
  {
    name: "Financial Transaction",
    requirements: { canLoseData: false, mustSurviveFailover: true, mustSurviveCrash: true, performanceCritical: false, crossDC: false }
  },
  {
    name: "Global Critical Data",
    requirements: { canLoseData: false, mustSurviveFailover: true, mustSurviveCrash: true, performanceCritical: false, crossDC: true }
  }
]

scenarios.forEach(s => {
  const { writeConcern, reason } = recommendWriteConcern(s.requirements)
  print(`${s.name}:`)
  print(`  Write Concern: ${JSON.stringify(writeConcern)}`)
  print(`  Reasons: ${reason.join(", ")}`)
  print()
})
```

### Exercise 3: Write Concern Timeout Handling

```javascript
// Handle write concern timeouts properly

function safeWrite(collection, document, writeConcern, maxRetries = 3) {
  let attempt = 0
  
  while (attempt < maxRetries) {
    attempt++
    
    try {
      const result = db[collection].insertOne(document, { writeConcern })
      return { success: true, result, attempts: attempt }
      
    } catch (error) {
      // Check if it's a write concern error
      const isWriteConcernError = error.code === 64 || 
        error.codeName === "WriteConcernFailed"
      
      if (isWriteConcernError) {
        print(`  Attempt ${attempt}: Write concern timeout`)
        
        // Check if document was actually written
        const exists = db[collection].findOne({ _id: document._id })
        if (exists) {
          print(`  Document was written despite timeout`)
          return { success: true, result: exists, attempts: attempt }
        }
        
        // Retry if document doesn't exist
        if (attempt < maxRetries) {
          print(`  Retrying...`)
          continue
        }
      }
      
      return { success: false, error: error.message, attempts: attempt }
    }
  }
  
  return { success: false, error: "Max retries exceeded", attempts: attempt }
}

// Test
print("=== Write Concern Timeout Handling ===\n")

const testDoc = {
  _id: "test-" + Date.now(),
  data: "Important data",
  timestamp: new Date()
}

const result = safeWrite("timeoutTest", testDoc, { w: 1, wtimeout: 5000 })
print("Result:", JSON.stringify(result))
```

### Exercise 4: Custom Write Concern Design

```javascript
// Design custom write concerns for different scenarios

print("=== Custom Write Concern Design ===\n")

// Scenario: Multi-region deployment
const deployment = {
  regions: ["us-east", "us-west", "eu-west"],
  membersPerRegion: 2,
  requirements: {
    criticalData: "Write to at least 2 regions",
    standardData: "Write to local region",
    analyticsData: "Write acknowledged by any member"
  }
}

print("Deployment:")
print(`  Regions: ${deployment.regions.join(", ")}`)
print(`  Members per region: ${deployment.membersPerRegion}`)
print(`  Total members: ${deployment.regions.length * deployment.membersPerRegion}`)

print("\nTag Configuration:")
deployment.regions.forEach((region, i) => {
  for (let j = 0; j < deployment.membersPerRegion; j++) {
    print(`  member${i * deployment.membersPerRegion + j}: { region: "${region}" }`)
  }
})

print("\nCustom Write Concern Modes:")
print(`  multiRegion: { region: 2 }  // ${deployment.requirements.criticalData}`)

print("\nUsage Examples:")
print(`
// Critical data - multi-region
db.criticalData.insertOne(
  { important: true },
  { writeConcern: { w: "multiRegion", wtimeout: 30000 } }
)

// Standard data - majority
db.standardData.insertOne(
  { standard: true },
  { writeConcern: { w: "majority", wtimeout: 5000 } }
)

// Analytics - fast
db.analyticsData.insertOne(
  { metric: 123 },
  { writeConcern: { w: 1 } }
)
`)
```

### Exercise 5: Write Concern Comparison Test

```javascript
// Compare write concern performance (requires replica set)

print("=== Write Concern Performance Comparison ===\n")

// Simulated test (actual tests need replica set)
const writeConcerns = [
  { name: "w:0", wc: { w: 0 }, description: "Unacknowledged" },
  { name: "w:1", wc: { w: 1 }, description: "Primary only" },
  { name: "w:1,j:true", wc: { w: 1, j: true }, description: "Primary + journal" },
  { name: "w:majority", wc: { w: "majority" }, description: "Majority" },
  { name: "w:majority,j:true", wc: { w: "majority", j: true }, description: "Majority + journal" }
]

print("Write Concern Options:\n")
print("┌─────────────────────┬─────────────────────────┬─────────┬─────────────┐")
print("│ Write Concern       │ Description             │ Safety  │ Performance │")
print("├─────────────────────┼─────────────────────────┼─────────┼─────────────┤")

writeConcerns.forEach(wc => {
  let safety, perf
  
  switch (wc.name) {
    case "w:0":
      safety = "None"
      perf = "★★★★★"
      break
    case "w:1":
      safety = "Low"
      perf = "★★★★☆"
      break
    case "w:1,j:true":
      safety = "Medium"
      perf = "★★★☆☆"
      break
    case "w:majority":
      safety = "High"
      perf = "★★☆☆☆"
      break
    case "w:majority,j:true":
      safety = "Highest"
      perf = "★☆☆☆☆"
      break
  }
  
  const name = wc.name.padEnd(19)
  const desc = wc.description.padEnd(23)
  const safetyPad = safety.padEnd(7)
  
  print(`│ ${name} │ ${desc} │ ${safetyPad} │ ${perf}       │`)
})

print("└─────────────────────┴─────────────────────────┴─────────┴─────────────┘")

print("\nRecommendations:")
print("• Use w:0 only for disposable data (logs, metrics)")
print("• Use w:1 for general operations (default)")
print("• Use w:majority for important business data")
print("• Use w:majority,j:true for financial/critical data")
```

---

[← Previous: Read Preferences](41-read-preferences.md) | [Next: Replica Set Maintenance →](43-replica-set-maintenance.md)
