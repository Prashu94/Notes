# Chapter 22: Index Management

## Table of Contents
- [Viewing Indexes](#viewing-indexes)
- [Creating Indexes](#creating-indexes)
- [Dropping Indexes](#dropping-indexes)
- [Rebuilding Indexes](#rebuilding-indexes)
- [Index Build Operations](#index-build-operations)
- [Index Statistics](#index-statistics)
- [Plan Cache Management](#plan-cache-management)
- [Index Recommendations](#index-recommendations)
- [Monitoring Index Performance](#monitoring-index-performance)
- [Summary](#summary)

---

## Viewing Indexes

### List All Indexes

```javascript
// Get all indexes on a collection
db.collection.getIndexes()

// Output example:
[
  {
    "v": 2,
    "key": { "_id": 1 },
    "name": "_id_"
  },
  {
    "v": 2,
    "key": { "email": 1 },
    "name": "email_1",
    "unique": true
  },
  {
    "v": 2,
    "key": { "status": 1, "createdAt": -1 },
    "name": "status_1_createdAt_-1"
  }
]
```

### Index Information

```javascript
// Collection stats including index info
db.collection.stats()

// Output includes:
{
  "ns": "database.collection",
  "count": 100000,
  "size": 15728640,
  "avgObjSize": 157,
  "storageSize": 6258688,
  "totalIndexSize": 4587520,
  "indexSizes": {
    "_id_": 2293760,
    "email_1": 1146880,
    "status_1_createdAt_-1": 1146880
  },
  "nindexes": 3
}
```

### Index Details

```javascript
// Detailed index specifications
db.collection.getIndexSpecs()

// Check if index exists
function indexExists(collectionName, indexName) {
  const indexes = db[collectionName].getIndexes()
  return indexes.some(idx => idx.name === indexName)
}

// Check index keys
function getIndexKeys(collectionName, indexName) {
  const indexes = db[collectionName].getIndexes()
  const idx = indexes.find(i => i.name === indexName)
  return idx ? idx.key : null
}
```

---

## Creating Indexes

### Single Index Creation

```javascript
// Basic creation
db.users.createIndex({ email: 1 })

// With options
db.users.createIndex(
  { email: 1 },
  {
    name: "email_unique_idx",
    unique: true,
    background: true,  // Deprecated in 4.2+
    sparse: true
  }
)
```

### Multiple Index Creation

```javascript
// Create multiple indexes at once
db.products.createIndexes([
  { key: { sku: 1 }, name: "sku_idx", unique: true },
  { key: { category: 1, price: 1 }, name: "category_price_idx" },
  { key: { tags: 1 }, name: "tags_idx" }
])
```

### Index Creation Options

```javascript
// Common options
db.collection.createIndex(
  { field: 1 },
  {
    // Naming
    name: "custom_index_name",
    
    // Constraints
    unique: true,
    sparse: true,
    
    // Partial index
    partialFilterExpression: { status: "active" },
    
    // TTL
    expireAfterSeconds: 3600,
    
    // Collation
    collation: { locale: "en", strength: 2 },
    
    // Hidden index (4.4+)
    hidden: true,
    
    // Commit quorum for replica sets
    commitQuorum: "votingMembers"
  }
)
```

### Background Index Build

```javascript
// MongoDB 4.2+: Background builds are default
// The server uses an optimized build process

// For replica sets, use commitQuorum
db.collection.createIndex(
  { field: 1 },
  { commitQuorum: "majority" }
)

// commitQuorum options:
// - "votingMembers" (default): All voting members
// - "majority": Majority of voting members
// - Number: Specific number of members
// - 0: Primary only (not recommended)
```

---

## Dropping Indexes

### Drop by Name

```javascript
// Drop single index by name
db.users.dropIndex("email_1")

// Drop by key specification
db.users.dropIndex({ email: 1 })
```

### Drop Multiple Indexes

```javascript
// Drop all indexes except _id
db.users.dropIndexes()

// Drop specific indexes (MongoDB 4.2+)
db.users.dropIndexes(["email_1", "name_1"])
```

### Safe Index Dropping

```javascript
// Check index usage before dropping
function safeDropIndex(collectionName, indexName) {
  // Get index stats
  const stats = db[collectionName].aggregate([
    { $indexStats: {} }
  ]).toArray()
  
  const indexStat = stats.find(s => s.name === indexName)
  
  if (!indexStat) {
    print(`Index ${indexName} not found`)
    return
  }
  
  const daysSinceUse = indexStat.accesses.ops === 0 ? 
    "Never used" : 
    Math.floor((new Date() - indexStat.accesses.since) / 86400000)
  
  print(`Index: ${indexName}`)
  print(`Operations: ${indexStat.accesses.ops}`)
  print(`Since: ${indexStat.accesses.since}`)
  
  if (indexStat.accesses.ops === 0) {
    print(`Dropping unused index: ${indexName}`)
    db[collectionName].dropIndex(indexName)
  } else {
    print(`Index is in use. Manual review required.`)
  }
}
```

---

## Rebuilding Indexes

### Rebuild All Indexes

```javascript
// Rebuild all indexes on collection
db.collection.reIndex()

// Note: reIndex() is deprecated in 4.2+
// Use drop and recreate instead
```

### Modern Approach: Drop and Recreate

```javascript
// Get current indexes
const indexes = db.collection.getIndexes()
  .filter(idx => idx.name !== "_id_")

// Store index definitions
const indexDefs = indexes.map(idx => ({
  key: idx.key,
  options: {
    name: idx.name,
    unique: idx.unique,
    sparse: idx.sparse,
    partialFilterExpression: idx.partialFilterExpression
  }
}))

// Drop all non-_id indexes
db.collection.dropIndexes()

// Recreate indexes
indexDefs.forEach(def => {
  db.collection.createIndex(def.key, def.options)
})
```

### Compact Collection

```javascript
// Compact collection and rebuild indexes
db.runCommand({ compact: "collection" })

// With options
db.runCommand({
  compact: "collection",
  force: true  // Run even on replica set primary
})
```

---

## Index Build Operations

### Monitor Index Builds

```javascript
// Check current operations
db.currentOp({ "command.createIndexes": { $exists: true } })

// Output:
{
  "inprog": [
    {
      "opid": 123,
      "type": "op",
      "ns": "mydb.collection",
      "command": {
        "createIndexes": "collection",
        "indexes": [{ "key": { "field": 1 }, "name": "field_1" }]
      },
      "msg": "Index Build: inserting keys into index",
      "progress": {
        "done": 50000,
        "total": 100000
      }
    }
  ]
}
```

### Kill Index Build

```javascript
// Find and kill index build
const ops = db.currentOp({ 
  "command.createIndexes": { $exists: true } 
})

if (ops.inprog.length > 0) {
  db.killOp(ops.inprog[0].opid)
}

// Using dropIndexes on building index (4.4+)
db.collection.dropIndexes("field_1")
```

### Resume Failed Builds

```javascript
// After crash, index builds resume automatically in 4.4+
// Check for incomplete indexes
db.collection.getIndexes().forEach(idx => {
  if (idx.buildUUID) {
    print(`Index ${idx.name} is still building`)
  }
})
```

---

## Index Statistics

### $indexStats Aggregation

```javascript
// Get index usage statistics
db.collection.aggregate([{ $indexStats: {} }])

// Output:
[
  {
    "name": "_id_",
    "key": { "_id": 1 },
    "host": "hostname:27017",
    "accesses": {
      "ops": 1523456,
      "since": ISODate("2024-01-01T00:00:00Z")
    }
  },
  {
    "name": "email_1",
    "key": { "email": 1 },
    "host": "hostname:27017",
    "accesses": {
      "ops": 89234,
      "since": ISODate("2024-01-01T00:00:00Z")
    }
  }
]
```

### Analyze Index Usage

```javascript
// Find unused indexes
function findUnusedIndexes(collectionName) {
  const stats = db[collectionName].aggregate([
    { $indexStats: {} }
  ]).toArray()
  
  const unused = stats.filter(s => 
    s.name !== "_id_" && s.accesses.ops === 0
  )
  
  print(`\nUnused indexes in ${collectionName}:`)
  unused.forEach(idx => {
    print(`  - ${idx.name}: ${JSON.stringify(idx.key)}`)
  })
  
  return unused
}

// Find most used indexes
function findMostUsedIndexes(collectionName, limit = 5) {
  const stats = db[collectionName].aggregate([
    { $indexStats: {} }
  ]).toArray()
  
  stats.sort((a, b) => b.accesses.ops - a.accesses.ops)
  
  print(`\nTop ${limit} used indexes in ${collectionName}:`)
  stats.slice(0, limit).forEach((idx, i) => {
    print(`  ${i + 1}. ${idx.name}: ${idx.accesses.ops} ops`)
  })
}
```

### Index Size Analysis

```javascript
// Get index sizes
function analyzeIndexSizes(collectionName) {
  const stats = db[collectionName].stats()
  
  print(`\nIndex sizes for ${collectionName}:`)
  print(`Total index size: ${formatBytes(stats.totalIndexSize)}`)
  print(`\nIndividual indexes:`)
  
  Object.entries(stats.indexSizes)
    .sort((a, b) => b[1] - a[1])
    .forEach(([name, size]) => {
      print(`  ${name}: ${formatBytes(size)}`)
    })
}

function formatBytes(bytes) {
  const units = ['B', 'KB', 'MB', 'GB']
  let i = 0
  while (bytes >= 1024 && i < units.length - 1) {
    bytes /= 1024
    i++
  }
  return `${bytes.toFixed(2)} ${units[i]}`
}
```

---

## Plan Cache Management

### View Plan Cache

```javascript
// List cached query plans
db.collection.getPlanCache().list()

// Output includes query shapes and cached plans
```

### Clear Plan Cache

```javascript
// Clear all cached plans
db.collection.getPlanCache().clear()

// Clear specific query shape (deprecated)
// Use clear() after index changes
```

### When to Clear Cache

```javascript
// Clear plan cache after:
// 1. Creating new indexes
// 2. Dropping indexes
// 3. Modifying index options
// 4. Performance issues after schema changes

// Example workflow
db.collection.createIndex({ newField: 1 })
db.collection.getPlanCache().clear()
```

---

## Index Recommendations

### Analyze Slow Queries

```javascript
// Enable profiling for slow queries
db.setProfilingLevel(1, { slowms: 100 })

// Find slow queries without index
db.system.profile.find({
  "planSummary": "COLLSCAN",
  "millis": { $gt: 100 }
}).sort({ ts: -1 }).limit(10)
```

### Identify Missing Indexes

```javascript
// Find collection scans
function findCollectionScans() {
  return db.system.profile.aggregate([
    {
      $match: {
        op: { $in: ["query", "command"] },
        planSummary: "COLLSCAN"
      }
    },
    {
      $group: {
        _id: {
          ns: "$ns",
          queryHash: "$queryHash"
        },
        count: { $sum: 1 },
        avgMillis: { $avg: "$millis" },
        sample: { $first: "$command" }
      }
    },
    { $sort: { count: -1 } }
  ]).toArray()
}
```

### Index Advisor Pattern

```javascript
// Simple index suggestion based on query patterns
function suggestIndexes(collectionName) {
  const scans = db.system.profile.find({
    ns: `${db.getName()}.${collectionName}`,
    planSummary: "COLLSCAN"
  }).toArray()
  
  const suggestions = new Map()
  
  scans.forEach(scan => {
    const filter = scan.command?.filter || scan.query || {}
    const sort = scan.command?.sort || {}
    
    const keys = [
      ...Object.keys(filter),
      ...Object.keys(sort)
    ].filter(k => k !== '$query' && k !== '$orderby')
    
    if (keys.length > 0) {
      const keyStr = keys.join(',')
      const count = suggestions.get(keyStr) || 0
      suggestions.set(keyStr, count + 1)
    }
  })
  
  print(`\nSuggested indexes for ${collectionName}:`)
  suggestions.forEach((count, keys) => {
    print(`  { ${keys.split(',').map(k => `${k}: 1`).join(', ')} } - ${count} queries`)
  })
}
```

---

## Monitoring Index Performance

### Using explain()

```javascript
// Check index usage
db.collection.find({ field: "value" }).explain("executionStats")

// Key metrics:
// - totalKeysExamined: Index entries scanned
// - totalDocsExamined: Documents scanned
// - executionTimeMillis: Query time
// - stage: IXSCAN (good) vs COLLSCAN (bad)
```

### Performance Dashboard Query

```javascript
// Comprehensive index performance check
function indexPerformanceReport(collectionName) {
  print(`\n=== Index Performance Report: ${collectionName} ===\n`)
  
  // Collection stats
  const stats = db[collectionName].stats()
  print(`Documents: ${stats.count}`)
  print(`Data size: ${formatBytes(stats.size)}`)
  print(`Index count: ${stats.nindexes}`)
  print(`Total index size: ${formatBytes(stats.totalIndexSize)}`)
  
  // Index usage
  print(`\n--- Index Usage ---`)
  const indexStats = db[collectionName].aggregate([
    { $indexStats: {} }
  ]).toArray()
  
  indexStats.forEach(idx => {
    const opsPerHour = idx.accesses.since ?
      (idx.accesses.ops / ((Date.now() - idx.accesses.since.getTime()) / 3600000)).toFixed(2) :
      0
    print(`${idx.name}:`)
    print(`  Total ops: ${idx.accesses.ops}`)
    print(`  Ops/hour: ${opsPerHour}`)
    print(`  Size: ${formatBytes(stats.indexSizes[idx.name])}`)
  })
  
  // Unused indexes
  const unused = indexStats.filter(s => 
    s.name !== "_id_" && s.accesses.ops === 0
  )
  
  if (unused.length > 0) {
    print(`\n--- Unused Indexes (consider dropping) ---`)
    unused.forEach(idx => {
      print(`  ${idx.name}: ${formatBytes(stats.indexSizes[idx.name])}`)
    })
  }
  
  // Index to data ratio
  const ratio = (stats.totalIndexSize / stats.size * 100).toFixed(1)
  print(`\n--- Summary ---`)
  print(`Index/Data ratio: ${ratio}%`)
  if (ratio > 50) {
    print(`WARNING: High index overhead. Consider removing unused indexes.`)
  }
}
```

### Automated Monitoring Script

```javascript
// Run periodic index health check
function indexHealthCheck() {
  const collections = db.getCollectionNames()
    .filter(c => !c.startsWith('system.'))
  
  collections.forEach(coll => {
    const stats = db[coll].aggregate([
      { $indexStats: {} }
    ]).toArray()
    
    const collStats = db[coll].stats()
    
    // Check for issues
    stats.forEach(idx => {
      // Unused index
      if (idx.name !== "_id_" && idx.accesses.ops === 0) {
        print(`[WARN] ${coll}.${idx.name}: Unused index`)
      }
      
      // Large index
      const size = collStats.indexSizes[idx.name]
      if (size > 1024 * 1024 * 1024) { // > 1GB
        print(`[INFO] ${coll}.${idx.name}: Large index (${formatBytes(size)})`)
      }
    })
  })
}
```

---

## Summary

### Index Management Commands

| Command | Description |
|---------|-------------|
| `getIndexes()` | List indexes |
| `createIndex()` | Create index |
| `createIndexes()` | Create multiple |
| `dropIndex()` | Drop single index |
| `dropIndexes()` | Drop multiple/all |
| `getPlanCache()` | Access plan cache |

### Key Metrics

| Metric | Description |
|--------|-------------|
| **accesses.ops** | Times index used |
| **totalIndexSize** | Total index storage |
| **indexSizes** | Per-index sizes |
| **totalKeysExamined** | Index entries scanned |

### What's Next?

In the next chapter, we'll explore the Aggregation Framework Pipeline.

---

## Practice Questions

1. How do you find unused indexes?
2. What happens when you drop all indexes?
3. How do you monitor index build progress?
4. When should you clear the plan cache?
5. How do you analyze index sizes?
6. What is commitQuorum for index builds?
7. How do you identify queries needing indexes?
8. What's the index to data size ratio significance?

---

## Hands-On Exercises

### Exercise 1: Index Discovery

```javascript
// Setup
db.idx_mgmt_test.drop()
for (let i = 0; i < 10000; i++) {
  db.idx_mgmt_test.insertOne({
    email: `user${i}@example.com`,
    name: `User ${i}`,
    status: i % 2 === 0 ? "active" : "inactive",
    category: ["A", "B", "C"][i % 3],
    score: Math.random() * 100,
    createdAt: new Date(Date.now() - Math.random() * 86400000 * 30)
  })
}

// Create some indexes
db.idx_mgmt_test.createIndex({ email: 1 }, { unique: true })
db.idx_mgmt_test.createIndex({ status: 1, createdAt: -1 })
db.idx_mgmt_test.createIndex({ category: 1 })
db.idx_mgmt_test.createIndex({ score: 1 })

// List all indexes
print("All indexes:")
db.idx_mgmt_test.getIndexes().forEach(idx => {
  print(`  ${idx.name}: ${JSON.stringify(idx.key)}`)
})

// Get index sizes
print("\nIndex sizes:")
const stats = db.idx_mgmt_test.stats()
Object.entries(stats.indexSizes).forEach(([name, size]) => {
  print(`  ${name}: ${(size / 1024).toFixed(2)} KB`)
})
```

### Exercise 2: Index Usage Analysis

```javascript
// Run some queries
for (let i = 0; i < 100; i++) {
  db.idx_mgmt_test.findOne({ email: `user${i}@example.com` })
}

for (let i = 0; i < 50; i++) {
  db.idx_mgmt_test.find({ status: "active" }).sort({ createdAt: -1 }).limit(10).toArray()
}

// Note: score index not used

// Check index stats
print("Index usage statistics:")
db.idx_mgmt_test.aggregate([{ $indexStats: {} }])
  .forEach(stat => {
    print(`\n${stat.name}:`)
    print(`  Operations: ${stat.accesses.ops}`)
    print(`  Since: ${stat.accesses.since}`)
  })

// Identify unused
print("\nUnused indexes:")
db.idx_mgmt_test.aggregate([{ $indexStats: {} }])
  .forEach(stat => {
    if (stat.name !== "_id_" && stat.accesses.ops === 0) {
      print(`  - ${stat.name}`)
    }
  })
```

### Exercise 3: Plan Cache

```javascript
// Run queries to populate cache
for (let i = 0; i < 10; i++) {
  db.idx_mgmt_test.find({ status: "active", category: "A" }).toArray()
}

// View plan cache
print("Plan cache entries:")
const cache = db.idx_mgmt_test.getPlanCache().list()
print(`  Total entries: ${cache.length}`)

// Add new index
db.idx_mgmt_test.createIndex({ status: 1, category: 1 })

// Clear cache after adding index
db.idx_mgmt_test.getPlanCache().clear()
print("Plan cache cleared after index change")

// Verify same query uses new index
const plan = db.idx_mgmt_test.find({ status: "active", category: "A" })
  .explain()
print("Query now uses:", plan.queryPlanner.winningPlan.inputStage?.indexName || "COLLSCAN")
```

### Exercise 4: Index Health Report

```javascript
// Create health report function
function createHealthReport(collName) {
  const stats = db[collName].stats()
  const indexStats = db[collName].aggregate([{ $indexStats: {} }]).toArray()
  
  print(`\n╔════════════════════════════════════════╗`)
  print(`║  INDEX HEALTH REPORT: ${collName.padEnd(17)}║`)
  print(`╠════════════════════════════════════════╣`)
  
  // Overview
  print(`║ Total Documents: ${stats.count.toString().padStart(20)} ║`)
  print(`║ Total Index Size: ${(stats.totalIndexSize/1024/1024).toFixed(2).padStart(17)} MB ║`)
  print(`║ Number of Indexes: ${stats.nindexes.toString().padStart(18)} ║`)
  
  print(`╠════════════════════════════════════════╣`)
  print(`║  INDEX DETAILS                         ║`)
  print(`╠════════════════════════════════════════╣`)
  
  indexStats.forEach(idx => {
    const size = (stats.indexSizes[idx.name] / 1024).toFixed(1)
    const used = idx.accesses.ops > 0 ? "✓" : "✗"
    print(`║ ${used} ${idx.name.substring(0, 25).padEnd(25)} ${size.padStart(8)} KB ║`)
  })
  
  print(`╚════════════════════════════════════════╝`)
}

createHealthReport("idx_mgmt_test")
```

### Exercise 5: Safe Index Cleanup

```javascript
// Function to safely remove unused indexes
function cleanupUnusedIndexes(collName, dryRun = true) {
  print(`\nAnalyzing unused indexes for: ${collName}`)
  print(`Mode: ${dryRun ? "DRY RUN (no changes)" : "LIVE (will drop indexes)"}`)
  
  const indexStats = db[collName].aggregate([{ $indexStats: {} }]).toArray()
  const stats = db[collName].stats()
  
  const unused = indexStats.filter(s => 
    s.name !== "_id_" && s.accesses.ops === 0
  )
  
  if (unused.length === 0) {
    print("No unused indexes found.")
    return
  }
  
  let totalSaved = 0
  
  unused.forEach(idx => {
    const size = stats.indexSizes[idx.name]
    totalSaved += size
    
    print(`\n${idx.name}:`)
    print(`  Size: ${(size / 1024).toFixed(2)} KB`)
    print(`  Keys: ${JSON.stringify(idx.key)}`)
    
    if (!dryRun) {
      db[collName].dropIndex(idx.name)
      print(`  Status: DROPPED`)
    } else {
      print(`  Status: Would be dropped`)
    }
  })
  
  print(`\nTotal space ${dryRun ? "would be" : ""} freed: ${(totalSaved / 1024).toFixed(2)} KB`)
}

// Dry run first
cleanupUnusedIndexes("idx_mgmt_test", true)

// Uncomment to actually drop
// cleanupUnusedIndexes("idx_mgmt_test", false)
```

---

[← Previous: Geospatial Indexes](21-geospatial-indexes.md) | [Next: Aggregation Pipeline Basics →](23-aggregation-pipeline-basics.md)
