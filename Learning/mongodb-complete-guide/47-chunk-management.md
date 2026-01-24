# Chapter 47: Chunk Management

## Table of Contents
- [Understanding Chunks](#understanding-chunks)
- [Chunk Operations](#chunk-operations)
- [Chunk Splitting](#chunk-splitting)
- [Chunk Migration](#chunk-migration)
- [Jumbo Chunks](#jumbo-chunks)
- [Monitoring Chunks](#monitoring-chunks)
- [Summary](#summary)

---

## Understanding Chunks

Chunks are the fundamental unit of data distribution in a sharded cluster.

### Chunk Basics

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Chunk Structure                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Sharded Collection: orders                                        │
│  Shard Key: { customerId: 1 }                                      │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Chunk 1                                   │   │
│  │  Range: MinKey → "C100000"                                  │   │
│  │  Shard: shard1RS                                            │   │
│  │  Documents: ~50,000                                         │   │
│  │  Size: ~64 MB                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Chunk 2                                   │   │
│  │  Range: "C100000" → "C200000"                               │   │
│  │  Shard: shard2RS                                            │   │
│  │  Documents: ~48,000                                         │   │
│  │  Size: ~61 MB                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Chunk 3                                   │   │
│  │  Range: "C200000" → MaxKey                                  │   │
│  │  Shard: shard1RS                                            │   │
│  │  Documents: ~52,000                                         │   │
│  │  Size: ~66 MB                                               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Default chunk size: 128 MB (configurable: 1-1024 MB)              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Chunk Metadata

```javascript
// Chunk document in config.chunks
{
  _id: "mydb.orders-customerId_MinKey",
  ns: "mydb.orders",
  min: { customerId: MinKey },
  max: { customerId: "C100000" },
  shard: "shard1RS",
  lastmod: Timestamp(2, 1),
  lastmodEpoch: ObjectId("...")
}

// View chunks for a collection
use config
db.chunks.find({ ns: "mydb.orders" }).pretty()
```

### Chunk Size Configuration

```javascript
// Check current chunk size
use config
db.settings.findOne({ _id: "chunksize" })

// Set chunk size (in MB)
db.settings.updateOne(
  { _id: "chunksize" },
  { $set: { value: 64 } },
  { upsert: true }
)

// Note: Smaller chunks = more migrations, better distribution
//       Larger chunks = fewer migrations, potential hot spots

// Recommendations:
// - 64 MB: Fast-changing data, frequent rebalancing needed
// - 128 MB: Default, good for most workloads
// - 256 MB: Large documents, stable data distribution
```

---

## Chunk Operations

### View Chunk Information

```javascript
// Count chunks per collection
use config
db.chunks.aggregate([
  { $group: { _id: "$ns", count: { $sum: 1 } } }
])

// Count chunks per shard for a collection
db.chunks.aggregate([
  { $match: { ns: "mydb.orders" } },
  { $group: { _id: "$shard", count: { $sum: 1 } } }
])

// Find chunk ranges
db.chunks.find(
  { ns: "mydb.orders" },
  { min: 1, max: 1, shard: 1 }
).sort({ min: 1 })
```

### Find Chunk for a Document

```javascript
// Determine which chunk holds a specific shard key value
function findChunkForValue(namespace, shardKeyValue) {
  const chunk = db.getSiblingDB("config").chunks.findOne({
    ns: namespace,
    min: { $lte: shardKeyValue },
    max: { $gt: shardKeyValue }
  })
  
  return chunk
}

// Example
const chunk = findChunkForValue(
  "mydb.orders",
  { customerId: "C150000" }
)

print(`Shard: ${chunk.shard}`)
print(`Range: ${JSON.stringify(chunk.min)} → ${JSON.stringify(chunk.max)}`)
```

---

## Chunk Splitting

### Automatic Splitting

```javascript
// Splitting happens automatically when:
// 1. Chunk exceeds configured size
// 2. Insert/update operations occur

// The mongos tracks chunk sizes and triggers splits
// Split creates two smaller chunks from one

// Before split:
// Chunk: MinKey → MaxKey (150 MB)

// After split:
// Chunk1: MinKey → "M12345"  (75 MB)
// Chunk2: "M12345" → MaxKey  (75 MB)
```

### Manual Splitting

```javascript
// Split at a specific point
sh.splitAt("mydb.orders", { customerId: "C500000" })

// Split at the middle of a chunk (find split point automatically)
sh.splitFind("mydb.orders", { customerId: "C250000" })

// Useful for:
// - Pre-splitting before bulk imports
// - Breaking up hot chunks
// - Manual rebalancing
```

### Pre-Splitting for Bulk Import

```javascript
// Pre-split chunks before large data import
// Prevents all data going to one shard initially

// For hashed shard key (easier)
sh.shardCollection(
  "mydb.logs",
  { _id: "hashed" },
  false,
  { numInitialChunks: 100 }  // Creates 100 chunks upfront
)

// For ranged shard key (manual)
// 1. Shard the collection
sh.shardCollection("mydb.customers", { customerId: 1 })

// 2. Create split points
const alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for (let i = 0; i < alphabet.length; i++) {
  sh.splitAt("mydb.customers", { customerId: alphabet[i] })
}

// 3. Distribute chunks across shards
// (balancer will do this, or use manual moves)
```

### Split Script Example

```javascript
// Pre-split based on known data distribution

function presplitCollection(namespace, keyField, splitPoints) {
  print(`Pre-splitting ${namespace}...`)
  
  splitPoints.forEach((point, i) => {
    try {
      sh.splitAt(namespace, { [keyField]: point })
      print(`  ✓ Split at ${point}`)
    } catch (e) {
      print(`  ✗ Failed at ${point}: ${e.message}`)
    }
  })
  
  // Verify
  const chunks = db.getSiblingDB("config").chunks.countDocuments({ ns: namespace })
  print(`\nTotal chunks: ${chunks}`)
}

// Usage
presplitCollection(
  "mydb.orders",
  "customerId",
  ["C100000", "C200000", "C300000", "C400000", "C500000"]
)
```

---

## Chunk Migration

### Understanding Migration

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Chunk Migration Process                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Step 1: Balancer identifies imbalance                             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                       │
│  │ Shard 1 │     │ Shard 2 │     │ Shard 3 │                       │
│  │ 50      │     │ 50      │     │ 30      │  chunks               │
│  └─────────┘     └─────────┘     └─────────┘                       │
│                                                                     │
│  Step 2: Migration initiated (Shard 1 → Shard 3)                   │
│  ┌─────────┐                     ┌─────────┐                       │
│  │ Shard 1 │ ─── Chunk ──────► │ Shard 3 │                        │
│  │ Source  │     copying...     │ Target  │                        │
│  └─────────┘                     └─────────┘                       │
│                                                                     │
│  Step 3: Catch up and commit                                       │
│  - Source applies incoming writes                                  │
│  - Target catches up with changes                                  │
│  - Config servers update chunk ownership                           │
│                                                                     │
│  Step 4: Cleanup                                                   │
│  - Source deletes migrated data (async)                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Manual Chunk Migration

```javascript
// Move a chunk to a specific shard
sh.moveChunk(
  "mydb.orders",
  { customerId: "C150000" },  // Find chunk containing this value
  "shard2RS"                   // Destination shard
)

// Move chunk by specifying range
db.adminCommand({
  moveChunk: "mydb.orders",
  find: { customerId: "C150000" },
  to: "shard2RS"
})
```

### Migration Throttling

```javascript
// Control migration rate
use config

// Set secondary throttle (replication wait during migration)
db.settings.updateOne(
  { _id: "balancer" },
  { $set: { "_secondaryThrottle": true } },
  { upsert: true }
)

// Set write concern for migrations
db.settings.updateOne(
  { _id: "balancer" },
  { $set: { "_waitForDelete": true } },
  { upsert: true }
)
```

### Monitor Active Migrations

```javascript
// Check current migration status
sh.isBalancerRunning()

// View active migrations
use config
db.locks.find({ state: 2 })

// Current operations
db.currentOp({ "command.moveChunk": { $exists: true } })

// Migration history
db.changelog.find({ what: "moveChunk.commit" }).sort({ time: -1 }).limit(10)
```

---

## Jumbo Chunks

### What are Jumbo Chunks

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Jumbo Chunks                                      │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  A jumbo chunk:                                                    │
│  - Exceeds the configured chunk size (default 128 MB)              │
│  - Cannot be split (all documents have same shard key value)       │
│  - Cannot be moved by the balancer                                 │
│                                                                     │
│  Example: Low cardinality shard key                                │
│                                                                     │
│  Shard Key: { status: 1 }                                          │
│                                                                     │
│  ┌─────────────────────────────────────────┐                       │
│  │           JUMBO CHUNK                    │                       │
│  │  Range: "active" → "active"             │                       │
│  │  Size: 500 MB (all status="active")     │                       │
│  │  Cannot split - same key value!         │                       │
│  └─────────────────────────────────────────┘                       │
│                                                                     │
│  ┌─────────────┐                                                   │
│  │ Normal      │                                                   │
│  │ "inactive"  │  50 MB                                            │
│  └─────────────┘                                                   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Identify Jumbo Chunks

```javascript
// Find jumbo chunks
use config
db.chunks.find({ jumbo: true })

// Count jumbo chunks per collection
db.chunks.aggregate([
  { $match: { jumbo: true } },
  { $group: { _id: "$ns", count: { $sum: 1 } } }
])

// Find large chunks that might become jumbo
db.chunks.find({
  ns: "mydb.orders",
  $where: function() {
    // This is approximate - actual size needs dataSize command
    return this.nObjects > 100000;  // If tracked
  }
})
```

### Resolving Jumbo Chunks

```javascript
// Option 1: Clear jumbo flag (if chunk can now be split)
db.getSiblingDB("config").chunks.updateOne(
  { _id: "chunk-id-here" },
  { $unset: { jumbo: 1 } }
)

// Option 2: Force split (MongoDB 4.4+)
db.adminCommand({
  clearJumboFlag: "mydb.orders",
  find: { customerId: "problematic-value" }
})

// Option 3: Refine shard key (MongoDB 5.0+)
// Add more fields to increase cardinality
db.adminCommand({
  refineCollectionShardKey: "mydb.orders",
  key: { customerId: 1, orderId: 1 }
})

// Option 4: Reshard with better key
// Most drastic but may be necessary
```

### Preventing Jumbo Chunks

```javascript
// 1. Choose high-cardinality shard keys
// Bad:  { status: 1 }      // Few unique values
// Good: { customerId: 1 }  // Many unique values

// 2. Use compound shard keys
// Bad:  { country: 1 }
// Good: { country: 1, city: 1, customerId: 1 }

// 3. Use hashed shard keys when appropriate
sh.shardCollection("mydb.logs", { _id: "hashed" })

// 4. Pre-split before bulk imports
// 5. Monitor chunk sizes regularly
```

---

## Monitoring Chunks

### Chunk Distribution Report

```javascript
// Comprehensive chunk distribution report

function chunkDistributionReport(namespace) {
  print(`=== Chunk Distribution Report: ${namespace} ===\n`)
  
  const config = db.getSiblingDB("config")
  
  // Get collection info
  const collInfo = config.collections.findOne({ _id: namespace })
  if (!collInfo) {
    print("Collection not sharded")
    return
  }
  
  print(`Shard Key: ${JSON.stringify(collInfo.key)}`)
  print(`Unique: ${collInfo.unique || false}\n`)
  
  // Get chunk distribution
  const distribution = config.chunks.aggregate([
    { $match: { ns: namespace } },
    { $group: {
      _id: "$shard",
      chunks: { $sum: 1 },
      jumbo: { $sum: { $cond: ["$jumbo", 1, 0] } }
    }},
    { $sort: { chunks: -1 } }
  ]).toArray()
  
  // Calculate totals
  const totalChunks = distribution.reduce((sum, d) => sum + d.chunks, 0)
  const totalJumbo = distribution.reduce((sum, d) => sum + d.jumbo, 0)
  
  // Display table
  print("Distribution by Shard:\n")
  print("┌────────────────┬────────┬────────────┬────────┐")
  print("│ Shard          │ Chunks │ Percentage │ Jumbo  │")
  print("├────────────────┼────────┼────────────┼────────┤")
  
  distribution.forEach(d => {
    const pct = (d.chunks / totalChunks * 100).toFixed(1) + "%"
    print(`│ ${d._id.padEnd(14)} │ ${String(d.chunks).padStart(6)} │ ${pct.padStart(10)} │ ${String(d.jumbo).padStart(6)} │`)
  })
  
  print("├────────────────┼────────┼────────────┼────────┤")
  print(`│ ${"TOTAL".padEnd(14)} │ ${String(totalChunks).padStart(6)} │ ${"100%".padStart(10)} │ ${String(totalJumbo).padStart(6)} │`)
  print("└────────────────┴────────┴────────────┴────────┘")
  
  // Imbalance check
  if (distribution.length > 1) {
    const max = distribution[0].chunks
    const min = distribution[distribution.length - 1].chunks
    const imbalance = ((max - min) / max * 100).toFixed(1)
    
    print(`\nImbalance: ${imbalance}%`)
    if (imbalance < 10) {
      print("  ✓ Well balanced")
    } else if (imbalance < 30) {
      print("  ! Moderate imbalance - balancer should correct")
    } else {
      print("  ✗ Significant imbalance - check balancer status")
    }
  }
  
  // Jumbo warning
  if (totalJumbo > 0) {
    print(`\n⚠ Warning: ${totalJumbo} jumbo chunks detected`)
    print("  Jumbo chunks cannot be moved or split automatically")
  }
  
  return { totalChunks, totalJumbo, distribution }
}

// Usage
// chunkDistributionReport("mydb.orders")
```

### Chunk Range Visualizer

```javascript
// Visualize chunk ranges

function visualizeChunkRanges(namespace, limit = 20) {
  print(`=== Chunk Ranges: ${namespace} ===\n`)
  
  const chunks = db.getSiblingDB("config").chunks
    .find({ ns: namespace })
    .sort({ min: 1 })
    .limit(limit)
    .toArray()
  
  if (chunks.length === 0) {
    print("No chunks found")
    return
  }
  
  chunks.forEach((chunk, i) => {
    const min = JSON.stringify(chunk.min).substring(0, 25)
    const max = JSON.stringify(chunk.max).substring(0, 25)
    const jumbo = chunk.jumbo ? " [JUMBO]" : ""
    
    print(`Chunk ${(i + 1).toString().padStart(2)}: ${chunk.shard}`)
    print(`         ${min} → ${max}${jumbo}`)
  })
  
  if (chunks.length === limit) {
    const totalChunks = db.getSiblingDB("config").chunks.countDocuments({ ns: namespace })
    print(`\n... and ${totalChunks - limit} more chunks`)
  }
}

// Usage
// visualizeChunkRanges("mydb.orders", 10)
```

### Chunk Activity Monitor

```javascript
// Monitor chunk splits and migrations

function chunkActivityMonitor(hours = 24) {
  print(`=== Chunk Activity (Last ${hours} Hours) ===\n`)
  
  const since = new Date(Date.now() - hours * 60 * 60 * 1000)
  const changelog = db.getSiblingDB("config").changelog
  
  // Splits
  const splits = changelog.aggregate([
    { $match: { 
      what: "split",
      time: { $gte: since }
    }},
    { $group: {
      _id: "$ns",
      count: { $sum: 1 }
    }}
  ]).toArray()
  
  print("Splits:")
  if (splits.length === 0) {
    print("  No splits")
  } else {
    splits.forEach(s => print(`  ${s._id}: ${s.count}`))
  }
  print()
  
  // Migrations
  const migrations = changelog.aggregate([
    { $match: {
      what: { $regex: /moveChunk/ },
      time: { $gte: since }
    }},
    { $group: {
      _id: { ns: "$ns", what: "$what" },
      count: { $sum: 1 }
    }}
  ]).toArray()
  
  print("Migrations:")
  if (migrations.length === 0) {
    print("  No migrations")
  } else {
    migrations.forEach(m => print(`  ${m._id.ns} (${m._id.what}): ${m.count}`))
  }
  print()
  
  // Failed operations
  const failures = changelog.find({
    time: { $gte: since },
    $or: [
      { "details.error": { $exists: true } },
      { "details.errmsg": { $exists: true } }
    ]
  }).toArray()
  
  print("Failures:")
  if (failures.length === 0) {
    print("  No failures")
  } else {
    failures.forEach(f => {
      print(`  ${f.time}: ${f.what}`)
      print(`    ${f.details.errmsg || f.details.error}`)
    })
  }
}

// Usage
// chunkActivityMonitor(24)
```

---

## Summary

### Chunk Concepts

| Concept | Description |
|---------|-------------|
| Chunk | Contiguous range of shard key values |
| Default Size | 128 MB |
| Min Size | 1 MB |
| Max Size | 1024 MB |
| Jumbo | Oversized, unsplittable chunk |

### Chunk Operations

| Operation | Command | Use Case |
|-----------|---------|----------|
| Split | sh.splitAt() | Manual splitting |
| Move | sh.moveChunk() | Manual rebalancing |
| Find | config.chunks.find() | Inspect chunks |

### Best Practices

| Practice | Reason |
|----------|--------|
| Pre-split before bulk load | Better initial distribution |
| Monitor jumbo chunks | Prevent hot spots |
| Choose high-cardinality keys | Avoid unsplittable chunks |
| Let balancer handle moves | Automatic optimization |

### What's Next?

In the next chapter, we'll explore the Balancer in detail.

---

## Practice Questions

1. What is a chunk in MongoDB sharding?
2. What is the default chunk size?
3. When does automatic splitting occur?
4. What is a jumbo chunk?
5. How can you prevent jumbo chunks?
6. How do you manually move a chunk?
7. What happens during chunk migration?
8. How do you monitor chunk distribution?

---

## Hands-On Exercises

### Exercise 1: Chunk Inspector

```javascript
// Inspect chunks for a sharded collection

function inspectChunks(namespace) {
  print(`=== Chunk Inspector: ${namespace} ===\n`)
  
  const config = db.getSiblingDB("config")
  
  // Collection info
  const collInfo = config.collections.findOne({ _id: namespace })
  if (!collInfo) {
    print("Collection not found or not sharded")
    return null
  }
  
  print(`Shard Key: ${JSON.stringify(collInfo.key)}`)
  print(`Unique: ${collInfo.unique || false}\n`)
  
  // Chunk stats
  const stats = config.chunks.aggregate([
    { $match: { ns: namespace } },
    { $facet: {
      total: [{ $count: "count" }],
      byShard: [
        { $group: { _id: "$shard", count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ],
      jumbo: [
        { $match: { jumbo: true } },
        { $count: "count" }
      ]
    }}
  ]).toArray()[0]
  
  const totalChunks = stats.total[0]?.count || 0
  const jumboChunks = stats.jumbo[0]?.count || 0
  
  print(`Total Chunks: ${totalChunks}`)
  print(`Jumbo Chunks: ${jumboChunks}`)
  print()
  
  // Distribution
  print("Distribution by Shard:")
  stats.byShard.forEach(s => {
    const pct = (s.count / totalChunks * 100).toFixed(1)
    const bar = "█".repeat(Math.floor(s.count / totalChunks * 20))
    print(`  ${s._id}: ${bar} ${s.count} (${pct}%)`)
  })
  print()
  
  // Sample chunks
  print("Sample Chunks:")
  const samples = config.chunks.find({ ns: namespace })
    .sort({ min: 1 })
    .limit(3)
    .toArray()
  
  samples.forEach((chunk, i) => {
    print(`  ${i + 1}. Range: ${JSON.stringify(chunk.min)} → ${JSON.stringify(chunk.max)}`)
    print(`     Shard: ${chunk.shard}${chunk.jumbo ? " [JUMBO]" : ""}`)
  })
  
  return { collInfo, totalChunks, jumboChunks, byShard: stats.byShard }
}

// Usage (must be connected to mongos)
// inspectChunks("mydb.orders")
```

### Exercise 2: Pre-Split Calculator

```javascript
// Calculate optimal pre-split points

function calculatePreSplits(namespace, numShards, splitStrategy = "even") {
  print(`=== Pre-Split Calculator ===\n`)
  print(`Collection: ${namespace}`)
  print(`Shards: ${numShards}`)
  print(`Strategy: ${splitStrategy}\n`)
  
  // Get collection info
  const config = db.getSiblingDB("config")
  const collInfo = config.collections.findOne({ _id: namespace })
  
  if (!collInfo) {
    print("Collection must be sharded first")
    return
  }
  
  const shardKey = collInfo.key
  const keyField = Object.keys(shardKey)[0]
  
  print(`Shard Key Field: ${keyField}`)
  print()
  
  // Calculate recommended chunks
  const chunksPerShard = 8  // Recommended for initial distribution
  const totalChunks = numShards * chunksPerShard
  
  print(`Recommended Setup:`)
  print(`  Chunks per shard: ${chunksPerShard}`)
  print(`  Total chunks: ${totalChunks}`)
  print()
  
  // Generate split commands based on strategy
  print(`Split Commands (${splitStrategy} strategy):`)
  print()
  
  if (splitStrategy === "alphabetic") {
    // For string-based shard keys
    const chars = "BCDEFGHIJKLMNOPQRSTUVWXYZ"
    const step = Math.floor(26 / (totalChunks - 1))
    
    for (let i = step; i < 26; i += step) {
      const splitPoint = chars[i - 1]
      print(`sh.splitAt("${namespace}", { ${keyField}: "${splitPoint}" })`)
    }
  } else if (splitStrategy === "numeric") {
    // For numeric shard keys
    const maxValue = 1000000  // Adjust based on your data
    const step = Math.floor(maxValue / totalChunks)
    
    for (let i = 1; i < totalChunks; i++) {
      const splitPoint = i * step
      print(`sh.splitAt("${namespace}", { ${keyField}: ${splitPoint} })`)
    }
  } else if (splitStrategy === "hashed") {
    // For hashed shard keys, use numInitialChunks
    print(`// For hashed keys, use numInitialChunks when sharding:`)
    print(`sh.shardCollection("${namespace}", { ${keyField}: "hashed" }, false, { numInitialChunks: ${totalChunks} })`)
  }
  
  print()
  print(`After splitting, use sh.status() to verify distribution`)
}

// Usage examples:
// calculatePreSplits("mydb.customers", 3, "alphabetic")
// calculatePreSplits("mydb.orders", 4, "numeric")
// calculatePreSplits("mydb.logs", 3, "hashed")
```

### Exercise 3: Jumbo Chunk Detector

```javascript
// Detect and analyze jumbo chunks

function analyzeJumboChunks(namespace) {
  print(`=== Jumbo Chunk Analysis: ${namespace || "all collections"} ===\n`)
  
  const config = db.getSiblingDB("config")
  
  // Build query
  const query = { jumbo: true }
  if (namespace) {
    query.ns = namespace
  }
  
  // Find jumbo chunks
  const jumboChunks = config.chunks.find(query).toArray()
  
  if (jumboChunks.length === 0) {
    print("✓ No jumbo chunks found")
    return []
  }
  
  print(`Found ${jumboChunks.length} jumbo chunk(s):\n`)
  
  // Group by collection
  const byCollection = {}
  jumboChunks.forEach(chunk => {
    if (!byCollection[chunk.ns]) {
      byCollection[chunk.ns] = []
    }
    byCollection[chunk.ns].push(chunk)
  })
  
  // Analyze each
  Object.entries(byCollection).forEach(([ns, chunks]) => {
    print(`Collection: ${ns}`)
    print(`  Jumbo chunks: ${chunks.length}`)
    
    chunks.forEach((chunk, i) => {
      print(`\n  Chunk ${i + 1}:`)
      print(`    Range: ${JSON.stringify(chunk.min)} → ${JSON.stringify(chunk.max)}`)
      print(`    Shard: ${chunk.shard}`)
      
      // Check if min equals max (single value chunk)
      const minStr = JSON.stringify(chunk.min)
      const maxStr = JSON.stringify(chunk.max)
      const isSingleValue = minStr === maxStr || 
        Object.keys(chunk.min).every(k => chunk.min[k] === chunk.max[k])
      
      if (isSingleValue) {
        print(`    ⚠ Single-value chunk (cannot be split)`)
      }
    })
    
    print()
  })
  
  // Recommendations
  print("Recommendations:")
  print("  1. Check shard key cardinality")
  print("  2. Consider refining shard key (MongoDB 5.0+)")
  print("  3. For MongoDB 4.4+, try clearJumboFlag command")
  print("  4. Review data distribution for skewed values")
  
  return jumboChunks
}

// Usage
// analyzeJumboChunks("mydb.orders")
// analyzeJumboChunks()  // All collections
```

### Exercise 4: Chunk Migration Simulator

```javascript
// Simulate chunk migrations

print("=== Chunk Migration Simulator ===\n")

// Simulated cluster state
const clusterState = {
  shards: {
    "shard1": { chunks: 45, load: 0.8 },
    "shard2": { chunks: 35, load: 0.6 },
    "shard3": { chunks: 20, load: 0.3 }
  },
  migrationThreshold: 8,  // Migrate when difference > threshold
  maxMigrationsPerRound: 1
}

function printState() {
  print("\nCurrent State:")
  Object.entries(clusterState.shards).forEach(([name, data]) => {
    const bar = "█".repeat(Math.floor(data.chunks / 2))
    print(`  ${name}: ${bar} ${data.chunks} chunks`)
  })
}

function simulateMigration() {
  const shards = Object.entries(clusterState.shards)
    .map(([name, data]) => ({ name, ...data }))
    .sort((a, b) => b.chunks - a.chunks)
  
  const source = shards[0]
  const target = shards[shards.length - 1]
  const diff = source.chunks - target.chunks
  
  if (diff <= clusterState.migrationThreshold) {
    print("\n✓ Cluster is balanced (difference ≤ threshold)")
    return false
  }
  
  print(`\nMigrating: ${source.name} → ${target.name}`)
  clusterState.shards[source.name].chunks--
  clusterState.shards[target.name].chunks++
  
  return true
}

// Initial state
print("Initial Cluster State:")
printState()
print(`\nMigration Threshold: ${clusterState.migrationThreshold} chunks`)

// Simulate balancing rounds
let round = 0
while (simulateMigration() && round < 50) {
  round++
  print(`\nRound ${round}:`)
  printState()
}

print(`\nBalancing complete after ${round} rounds`)
```

### Exercise 5: Chunk Size Advisor

```javascript
// Advise on optimal chunk size

function chunkSizeAdvisor(namespace) {
  print(`=== Chunk Size Advisor: ${namespace} ===\n`)
  
  // Get current configuration
  const currentSize = db.getSiblingDB("config").settings.findOne({ _id: "chunksize" })
  const chunkSizeMB = currentSize?.value || 128
  
  print(`Current chunk size: ${chunkSizeMB} MB`)
  
  // Analyze collection
  const config = db.getSiblingDB("config")
  const collInfo = config.collections.findOne({ _id: namespace })
  
  if (!collInfo) {
    print("Collection not sharded")
    return
  }
  
  // Count chunks and jumbo
  const stats = config.chunks.aggregate([
    { $match: { ns: namespace } },
    { $group: {
      _id: null,
      total: { $sum: 1 },
      jumbo: { $sum: { $cond: ["$jumbo", 1, 0] } }
    }}
  ]).toArray()[0] || { total: 0, jumbo: 0 }
  
  print(`Total chunks: ${stats.total}`)
  print(`Jumbo chunks: ${stats.jumbo}`)
  
  // Get migration activity
  const recentMigrations = config.changelog.countDocuments({
    what: "moveChunk.commit",
    time: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
  })
  
  print(`Migrations (24h): ${recentMigrations}`)
  print()
  
  // Recommendations
  print("Recommendations:")
  
  if (stats.jumbo > 0) {
    print(`  ⚠ ${stats.jumbo} jumbo chunks - chunk size may be too small for your shard key`)
    print("    Consider: Increase chunk size or refine shard key")
  }
  
  if (recentMigrations > 100) {
    print("  ⚠ High migration activity")
    print("    Consider: Increase chunk size (fewer, larger chunks)")
  } else if (recentMigrations < 5 && stats.total > 10) {
    print("  ✓ Low migration activity - chunk size seems appropriate")
  }
  
  // Suggested sizes
  print("\nSuggested Chunk Sizes:")
  print("  64 MB  - High write volume, frequent rebalancing OK")
  print("  128 MB - Default, balanced for most workloads")
  print("  256 MB - Large documents, minimize migrations")
  print()
  
  print("To change chunk size:")
  print(`  use config`)
  print(`  db.settings.updateOne({ _id: "chunksize" }, { $set: { value: <size_mb> }}, { upsert: true })`)
}

// Usage
// chunkSizeAdvisor("mydb.orders")
```

---

[← Previous: Sharded Cluster Setup](46-sharded-cluster-setup.md) | [Next: Balancing →](48-balancing.md)
