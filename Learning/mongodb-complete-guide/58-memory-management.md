# Chapter 58: Memory Management

## Table of Contents
- [Memory Architecture](#memory-architecture)
- [WiredTiger Cache](#wiredtiger-cache)
- [Working Set](#working-set)
- [Memory Monitoring](#memory-monitoring)
- [Memory Optimization](#memory-optimization)
- [Summary](#summary)

---

## Memory Architecture

### MongoDB Memory Components

```
┌─────────────────────────────────────────────────────────────────────┐
│                   MongoDB Memory Architecture                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    System RAM                                │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │             WiredTiger Cache (Default: 50%)            │ │   │
│  │  │  ┌──────────────────┐  ┌───────────────────────────┐  │ │   │
│  │  │  │   Index Cache    │  │    Data Cache             │  │ │   │
│  │  │  │   (Internal)     │  │    (Document Pages)       │  │ │   │
│  │  │  └──────────────────┘  └───────────────────────────┘  │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │         Operating System File Cache                    │ │   │
│  │  │  (Managed by OS - caches disk pages)                  │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │                                                              │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │  Connection Memory  │  │  Aggregation/Sort Memory    │  │   │
│  │  │  (~1MB per conn)    │  │  (Default: 100MB limit)     │  │   │
│  │  └─────────────────────┘  └─────────────────────────────┘  │   │
│  │                                                              │   │
│  │  ┌─────────────────────┐  ┌─────────────────────────────┐  │   │
│  │  │  Query Planning     │  │  Other System Overhead      │  │   │
│  │  │  Cache              │  │  (mongod process, etc.)     │  │   │
│  │  └─────────────────────┘  └─────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Memory Allocation Formula

```javascript
// WiredTiger default cache size calculation
// 50% of (RAM - 1 GB), or 256 MB, whichever is larger

function calculateDefaultCacheSize(totalRAMGB) {
  const calculated = (totalRAMGB - 1) * 0.5
  const minimum = 0.256  // 256 MB
  return Math.max(calculated, minimum)
}

// Example
console.log(calculateDefaultCacheSize(16))  // 7.5 GB
console.log(calculateDefaultCacheSize(4))   // 1.5 GB
console.log(calculateDefaultCacheSize(1))   // 0.256 GB (minimum)
```

---

## WiredTiger Cache

### Cache Configuration

```yaml
# mongod.conf
storage:
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4  # Explicit cache size
```

```javascript
// Set at runtime (MongoDB 3.6+)
db.adminCommand({
  setParameter: 1,
  wiredTigerEngineRuntimeConfig: "cache_size=4G"
})
```

### Cache Statistics

```javascript
// Get detailed cache statistics
function getCacheStats() {
  const stats = db.serverStatus().wiredTiger.cache
  
  return {
    // Size metrics
    configured: stats["maximum bytes configured"],
    currentlyUsed: stats["bytes currently in the cache"],
    dirty: stats["tracked dirty bytes in the cache"],
    
    // Read metrics
    pagesRead: stats["pages read into cache"],
    bytesRead: stats["bytes read into cache"],
    
    // Write metrics  
    pagesWritten: stats["pages written from cache"],
    bytesWritten: stats["bytes written from cache"],
    
    // Eviction metrics
    evictedUnmodified: stats["unmodified pages evicted"],
    evictedModified: stats["modified pages evicted"],
    evictionBlocked: stats["application threads page eviction blocked"],
    
    // Hit/miss
    cacheHits: stats["pages requested from the cache"],
    cacheMisses: stats["pages not found in cache"]
  }
}

const cacheStats = getCacheStats()
print(JSON.stringify(cacheStats, null, 2))
```

### Cache Usage Analysis

```javascript
// Analyze cache health
function analyzeCacheHealth() {
  const cache = db.serverStatus().wiredTiger.cache
  
  const used = cache["bytes currently in the cache"]
  const max = cache["maximum bytes configured"]
  const dirty = cache["tracked dirty bytes in the cache"]
  const evictionBlocked = cache["application threads page eviction blocked"]
  
  const usedPct = (used / max * 100).toFixed(1)
  const dirtyPct = (dirty / max * 100).toFixed(1)
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║                 CACHE HEALTH ANALYSIS                       ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("┌─ CACHE UTILIZATION ───────────────────────────────────────┐")
  print(`│  Configured: ${(max / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Currently Used: ${(used / 1024 / 1024 / 1024).toFixed(2)} GB (${usedPct}%)`.padEnd(60) + "│")
  print(`│  Dirty Pages: ${(dirty / 1024 / 1024).toFixed(2)} MB (${dirtyPct}%)`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  if (parseFloat(usedPct) > 95) {
    print("│  ⚠ Cache nearly full - consider increasing cache size".padEnd(60) + "│")
  } else if (parseFloat(usedPct) < 50) {
    print("│  ✓ Cache has headroom - size may be appropriate".padEnd(60) + "│")
  } else {
    print("│  ✓ Cache utilization is healthy".padEnd(60) + "│")
  }
  
  if (parseFloat(dirtyPct) > 20) {
    print("│  ⚠ High dirty page ratio - check write throughput".padEnd(60) + "│")
  }
  
  if (evictionBlocked > 0) {
    print(`│  ⚠ Eviction blocked ${evictionBlocked} times - cache pressure`.padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

analyzeCacheHealth()
```

### Eviction Tuning

```yaml
# mongod.conf - Advanced eviction tuning
storage:
  wiredTiger:
    engineConfig:
      # Start eviction when cache is 80% full
      # Default is higher
      configString: "eviction_target=80,eviction_trigger=95,eviction_dirty_target=5,eviction_dirty_trigger=20"
```

```javascript
// Monitor eviction
function monitorEviction() {
  const cache = db.serverStatus().wiredTiger.cache
  
  return {
    // Eviction threads
    evictionServerRunning: cache["eviction server running"],
    
    // Pages evicted
    unmodifiedPagesEvicted: cache["unmodified pages evicted"],
    modifiedPagesEvicted: cache["modified pages evicted"],
    
    // Eviction pressure indicators
    applicationThreadsBlocked: cache["application threads page eviction blocked"],
    evictionCallsToFind: cache["eviction calls to get a page"],
    
    // Hazard pointer blocked
    hazardPointerBlocked: cache["hazard pointer blocked page eviction"]
  }
}
```

---

## Working Set

### Understanding Working Set

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Working Set Concept                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Total Data                                                         │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │   │
│  │                                                              │   │
│  │ ▓▓▓▓▓▓▓▓ = Hot Data (Frequently Accessed)                   │   │
│  │ ░░░░░░░░ = Cold Data (Rarely Accessed)                      │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Working Set = Hot Data + Associated Indexes                       │
│                                                                     │
│  Best Performance:                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Working Set ≤ WiredTiger Cache ≤ Available RAM             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  When Working Set > Cache:                                         │
│  • Page faults increase                                            │
│  • Query latency increases                                         │
│  • Disk I/O increases                                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Estimating Working Set Size

```javascript
// Estimate working set based on access patterns
function estimateWorkingSet(collectionName, hotDataPct = 20) {
  const coll = db.getCollection(collectionName)
  const stats = coll.stats()
  
  // Total data size
  const dataSize = stats.size
  
  // Index sizes
  const indexSize = stats.totalIndexSize
  
  // Hot data estimate (typically 10-30% of data)
  const hotDataSize = dataSize * (hotDataPct / 100)
  
  // Working set = hot data + indexes
  const workingSet = hotDataSize + indexSize
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║               WORKING SET ESTIMATE                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Collection: ${collectionName}`)
  print(`Hot data percentage: ${hotDataPct}%\n`)
  
  print("┌─ SIZE BREAKDOWN ──────────────────────────────────────────┐")
  print(`│  Total Data Size: ${(dataSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Total Index Size: ${(indexSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Estimated Hot Data: ${(hotDataSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("├────────────────────────────────────────────────────────────┤")
  print(`│  WORKING SET ESTIMATE: ${(workingSet / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Compare to cache
  const cacheSize = db.serverStatus().wiredTiger.cache["maximum bytes configured"]
  const ratio = (workingSet / cacheSize * 100).toFixed(1)
  
  print("┌─ CACHE COMPARISON ────────────────────────────────────────┐")
  print(`│  WiredTiger Cache: ${(cacheSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Working Set / Cache: ${ratio}%`.padEnd(60) + "│")
  
  if (parseFloat(ratio) > 100) {
    print("│  ⚠ Working set exceeds cache - expect page faults".padEnd(60) + "│")
  } else if (parseFloat(ratio) > 80) {
    print("│  ⚠ Working set near cache limit".padEnd(60) + "│")
  } else {
    print("│  ✓ Working set fits comfortably in cache".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
  
  return { workingSet, cacheSize, ratio }
}

// Usage
// estimateWorkingSet("orders", 20)
```

### Working Set Verification

```javascript
// Check if working set fits in memory
function verifyWorkingSet() {
  const serverStatus = db.serverStatus()
  
  // Page faults indicate working set exceeds memory
  const pageFaults = serverStatus.extra_info?.page_faults || 0
  
  // Cache read efficiency
  const cache = serverStatus.wiredTiger.cache
  const bytesReadFromDisk = cache["bytes read into cache"]
  const bytesServedFromCache = cache["pages requested from the cache"]
  
  // Check for memory pressure
  const evictionBlocked = cache["application threads page eviction blocked"]
  
  print("┌─ WORKING SET VERIFICATION ────────────────────────────────┐")
  print(`│  Page Faults: ${pageFaults}`.padEnd(60) + "│")
  print(`│  Eviction Blocked: ${evictionBlocked}`.padEnd(60) + "│")
  
  if (pageFaults > 100 || evictionBlocked > 0) {
    print("│  ⚠ Working set may exceed available memory".padEnd(60) + "│")
    print("│  Actions:".padEnd(60) + "│")
    print("│    • Increase RAM".padEnd(60) + "│")
    print("│    • Increase WiredTiger cache".padEnd(60) + "│")
    print("│    • Reduce working set size".padEnd(60) + "│")
  } else {
    print("│  ✓ Working set appears to fit in memory".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}
```

---

## Memory Monitoring

### Memory Status Commands

```javascript
// Comprehensive memory monitoring
function getMemoryStatus() {
  const serverStatus = db.serverStatus()
  
  const memory = {
    // System memory
    resident: serverStatus.mem?.resident,        // MB
    virtual: serverStatus.mem?.virtual,          // MB
    mapped: serverStatus.mem?.mapped,            // MB (MMAPv1 only)
    
    // WiredTiger cache
    wtCache: {
      configured: serverStatus.wiredTiger?.cache["maximum bytes configured"],
      used: serverStatus.wiredTiger?.cache["bytes currently in the cache"],
      dirty: serverStatus.wiredTiger?.cache["tracked dirty bytes in the cache"]
    },
    
    // Connection memory (estimated)
    connections: serverStatus.connections?.current,
    estimatedConnMem: serverStatus.connections?.current * 1024 * 1024  // ~1MB per connection
  }
  
  return memory
}

// Memory dashboard
function memoryDashboard() {
  const mem = getMemoryStatus()
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║                   MEMORY DASHBOARD                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("┌─ PROCESS MEMORY ──────────────────────────────────────────┐")
  print(`│  Resident Memory: ${mem.resident} MB`.padEnd(60) + "│")
  print(`│  Virtual Memory: ${mem.virtual} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  if (mem.wtCache.configured) {
    const usedPct = (mem.wtCache.used / mem.wtCache.configured * 100).toFixed(1)
    const dirtyPct = (mem.wtCache.dirty / mem.wtCache.configured * 100).toFixed(1)
    
    print("┌─ WIREDTIGER CACHE ─────────────────────────────────────────┐")
    print(`│  Configured: ${(mem.wtCache.configured / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
    print(`│  Used: ${(mem.wtCache.used / 1024 / 1024 / 1024).toFixed(2)} GB (${usedPct}%)`.padEnd(60) + "│")
    print(`│  Dirty: ${(mem.wtCache.dirty / 1024 / 1024).toFixed(2)} MB (${dirtyPct}%)`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  print("┌─ CONNECTION MEMORY ───────────────────────────────────────┐")
  print(`│  Active Connections: ${mem.connections}`.padEnd(60) + "│")
  print(`│  Estimated Memory: ${(mem.estimatedConnMem / 1024 / 1024).toFixed(0)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
}

memoryDashboard()
```

### Memory Over Time

```javascript
// Track memory usage over time
function trackMemoryUsage(intervalSec = 5, iterations = 12) {
  print("Tracking memory usage...\n")
  print("Time                    | Resident | Cache Used | Cache % | Dirty %")
  print("─".repeat(75))
  
  for (let i = 0; i < iterations; i++) {
    const status = db.serverStatus()
    const now = new Date().toISOString().substring(11, 19)
    
    const resident = status.mem?.resident || 0
    const cache = status.wiredTiger?.cache
    const cacheUsed = cache ? cache["bytes currently in the cache"] : 0
    const cacheMax = cache ? cache["maximum bytes configured"] : 1
    const dirty = cache ? cache["tracked dirty bytes in the cache"] : 0
    
    const cachePct = (cacheUsed / cacheMax * 100).toFixed(1)
    const dirtyPct = (dirty / cacheMax * 100).toFixed(1)
    
    print(`${now}               | ${String(resident).padStart(6)} MB | ${(cacheUsed / 1024 / 1024).toFixed(0).padStart(8)} MB | ${cachePct.padStart(6)}% | ${dirtyPct.padStart(6)}%`)
    
    if (i < iterations - 1) {
      sleep(intervalSec * 1000)
    }
  }
}

// Usage
// trackMemoryUsage(5, 12)  // Every 5 seconds, 12 times
```

### Memory Alerts

```javascript
// Check for memory issues
function checkMemoryAlerts() {
  const status = db.serverStatus()
  const alerts = []
  
  // Check cache utilization
  const cache = status.wiredTiger?.cache
  if (cache) {
    const used = cache["bytes currently in the cache"]
    const max = cache["maximum bytes configured"]
    const pct = used / max * 100
    
    if (pct > 95) {
      alerts.push({
        severity: "CRITICAL",
        message: `Cache utilization at ${pct.toFixed(1)}%`,
        action: "Increase cache size or add memory"
      })
    } else if (pct > 85) {
      alerts.push({
        severity: "WARNING",
        message: `Cache utilization at ${pct.toFixed(1)}%`,
        action: "Monitor closely, consider increasing cache"
      })
    }
    
    // Check dirty ratio
    const dirty = cache["tracked dirty bytes in the cache"]
    const dirtyPct = dirty / max * 100
    
    if (dirtyPct > 20) {
      alerts.push({
        severity: "WARNING",
        message: `Dirty page ratio at ${dirtyPct.toFixed(1)}%`,
        action: "Check write throughput and checkpoint settings"
      })
    }
    
    // Check eviction pressure
    const evictionBlocked = cache["application threads page eviction blocked"]
    if (evictionBlocked > 0) {
      alerts.push({
        severity: "CRITICAL",
        message: `Application threads blocked by eviction: ${evictionBlocked}`,
        action: "Cache under severe pressure - increase size"
      })
    }
  }
  
  // Check page faults
  const pageFaults = status.extra_info?.page_faults
  if (pageFaults && pageFaults > 100) {
    alerts.push({
      severity: "WARNING",
      message: `Page faults: ${pageFaults}`,
      action: "Working set may exceed available memory"
    })
  }
  
  // Print alerts
  if (alerts.length === 0) {
    print("✓ No memory alerts")
  } else {
    print("┌─ MEMORY ALERTS ────────────────────────────────────────────┐")
    alerts.forEach(alert => {
      const icon = alert.severity === "CRITICAL" ? "🔴" : "🟡"
      print(`│  ${icon} [${alert.severity}] ${alert.message}`.padEnd(60) + "│")
      print(`│     → ${alert.action}`.padEnd(60) + "│")
    })
    print("└────────────────────────────────────────────────────────────┘")
  }
  
  return alerts
}

checkMemoryAlerts()
```

---

## Memory Optimization

### Reducing Memory Footprint

```javascript
// Strategies to reduce memory usage

// 1. Use projections to fetch only needed fields
db.orders.find(
  { status: "pending" },
  { customerId: 1, total: 1, _id: 0 }  // Only these fields
)

// 2. Use covered queries (no document fetch needed)
db.orders.createIndex({ status: 1, customerId: 1, total: 1 })
db.orders.find(
  { status: "pending" },
  { customerId: 1, total: 1, _id: 0 }
).hint("status_1_customerId_1_total_1")

// 3. Limit result sets
db.orders.find({ status: "pending" }).limit(100)

// 4. Use aggregation $limit early in pipeline
db.orders.aggregate([
  { $match: { status: "pending" } },
  { $sort: { orderDate: -1 } },
  { $limit: 100 },  // Limit early
  { $lookup: { ... } }  // Expensive operation after limit
])
```

### Index Memory Management

```javascript
// Analyze index memory usage
function analyzeIndexMemory(collectionName) {
  const coll = db.getCollection(collectionName)
  const stats = coll.stats()
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              INDEX MEMORY ANALYSIS                          ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Collection: ${collectionName}\n`)
  
  const indexSizes = stats.indexSizes
  const totalIndexSize = stats.totalIndexSize
  
  print("┌─ INDEX SIZES ─────────────────────────────────────────────┐")
  
  // Sort by size
  const sorted = Object.entries(indexSizes)
    .sort((a, b) => b[1] - a[1])
  
  sorted.forEach(([name, size]) => {
    const pct = (size / totalIndexSize * 100).toFixed(1)
    const sizeMB = (size / 1024 / 1024).toFixed(2)
    print(`│  ${name.substring(0, 30).padEnd(32)} ${sizeMB.padStart(8)} MB  (${pct}%)`.padEnd(60) + "│")
  })
  
  print("├────────────────────────────────────────────────────────────┤")
  print(`│  TOTAL: ${(totalIndexSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Compare to cache
  const cacheSize = db.serverStatus().wiredTiger?.cache["maximum bytes configured"] || 0
  const indexCachePct = (totalIndexSize / cacheSize * 100).toFixed(1)
  
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  print(`│  Indexes use ${indexCachePct}% of WiredTiger cache`.padEnd(60) + "│")
  
  if (parseFloat(indexCachePct) > 50) {
    print("│  ⚠ Indexes consume >50% of cache".padEnd(60) + "│")
    print("│    Consider:".padEnd(60) + "│")
    print("│    • Removing unused indexes".padEnd(60) + "│")
    print("│    • Using partial indexes".padEnd(60) + "│")
    print("│    • Increasing cache size".padEnd(60) + "│")
  } else {
    print("│  ✓ Index memory usage is reasonable".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
}

// Usage
// analyzeIndexMemory("orders")
```

### Aggregation Memory

```javascript
// Aggregation memory limit is 100MB by default
// Use allowDiskUse for large aggregations

// May fail with memory error
db.largeCollection.aggregate([
  { $group: { _id: "$field", count: { $sum: 1 } } },
  { $sort: { count: -1 } }
])

// Use allowDiskUse for large datasets
db.largeCollection.aggregate(
  [
    { $group: { _id: "$field", count: { $sum: 1 } } },
    { $sort: { count: -1 } }
  ],
  { allowDiskUse: true }
)

// Or increase the limit (MongoDB 6.0+)
db.adminCommand({
  setParameter: 1,
  internalQueryMaxBlockingSortMemoryUsageBytes: 200 * 1024 * 1024  // 200MB
})
```

### Connection Pool Optimization

```javascript
// Monitor connection memory
function analyzeConnectionMemory() {
  const conn = db.serverStatus().connections
  
  // Estimate ~1MB per connection
  const estimatedMemMB = conn.current * 1
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║             CONNECTION MEMORY ANALYSIS                      ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("┌─ CONNECTION STATUS ───────────────────────────────────────┐")
  print(`│  Current Connections: ${conn.current}`.padEnd(60) + "│")
  print(`│  Available Connections: ${conn.available}`.padEnd(60) + "│")
  print(`│  Total Created: ${conn.totalCreated}`.padEnd(60) + "│")
  print("├────────────────────────────────────────────────────────────┤")
  print(`│  Estimated Memory: ~${estimatedMemMB} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  if (conn.current > 500) {
    print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
    print("│  ⚠ High connection count detected".padEnd(60) + "│")
    print("│  Consider:".padEnd(60) + "│")
    print("│    • Review application connection pooling".padEnd(60) + "│")
    print("│    • Reduce maxPoolSize in application".padEnd(60) + "│")
    print("│    • Check for connection leaks".padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
  }
}

analyzeConnectionMemory()
```

---

## Summary

### Memory Components

| Component | Default Size | Tunable |
|-----------|--------------|---------|
| WiredTiger Cache | 50% (RAM - 1GB) | Yes |
| OS File Cache | Managed by OS | No |
| Connection Memory | ~1MB per connection | Indirect |
| Aggregation Memory | 100MB limit | Yes |

### Memory Sizing Guidelines

| Total RAM | WiredTiger Cache | Notes |
|-----------|------------------|-------|
| 4 GB | 1.5 GB | Minimum production |
| 8 GB | 3.5 GB | Small workloads |
| 16 GB | 7.5 GB | Medium workloads |
| 32 GB | 15.5 GB | Large workloads |
| 64 GB | 31.5 GB | Very large workloads |

### Key Metrics to Monitor

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Cache utilization | < 80% | 80-95% | > 95% |
| Dirty page ratio | < 5% | 5-20% | > 20% |
| Eviction blocked | 0 | > 0 | Increasing |
| Page faults | < 10/s | 10-100/s | > 100/s |

---

## Practice Questions

1. What is the default WiredTiger cache size formula?
2. How do you identify if the working set exceeds cache?
3. What causes application threads to be blocked by eviction?
4. How can you reduce index memory footprint?
5. What is the default aggregation memory limit?
6. How do you estimate connection memory usage?
7. When should you use allowDiskUse?
8. What indicates memory pressure in MongoDB?

---

## Hands-On Exercises

### Exercise 1: Memory Health Check

```javascript
// Comprehensive memory health check

function memoryHealthCheck() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              MEMORY HEALTH CHECK                            ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const status = db.serverStatus()
  const scores = []
  
  // 1. Check resident memory
  print("┌─ 1. PROCESS MEMORY ───────────────────────────────────────┐")
  const resident = status.mem?.resident || 0
  const virtual = status.mem?.virtual || 0
  
  print(`│  Resident: ${resident} MB`.padEnd(60) + "│")
  print(`│  Virtual: ${virtual} MB`.padEnd(60) + "│")
  
  if (virtual > resident * 3) {
    print("│  ⚠ High virtual to resident ratio".padEnd(60) + "│")
    scores.push(0.5)
  } else {
    print("│  ✓ Memory ratio healthy".padEnd(60) + "│")
    scores.push(1)
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 2. Check cache utilization
  print("┌─ 2. WIREDTIGER CACHE ─────────────────────────────────────┐")
  const cache = status.wiredTiger?.cache
  if (cache) {
    const used = cache["bytes currently in the cache"]
    const max = cache["maximum bytes configured"]
    const pct = (used / max * 100).toFixed(1)
    
    print(`│  Usage: ${pct}%`.padEnd(60) + "│")
    
    if (parseFloat(pct) > 95) {
      print("│  ⚠ Cache critically high".padEnd(60) + "│")
      scores.push(0)
    } else if (parseFloat(pct) > 85) {
      print("│  ⚠ Cache utilization high".padEnd(60) + "│")
      scores.push(0.5)
    } else {
      print("│  ✓ Cache utilization healthy".padEnd(60) + "│")
      scores.push(1)
    }
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 3. Check dirty pages
  print("┌─ 3. DIRTY PAGES ──────────────────────────────────────────┐")
  if (cache) {
    const dirty = cache["tracked dirty bytes in the cache"]
    const max = cache["maximum bytes configured"]
    const dirtyPct = (dirty / max * 100).toFixed(1)
    
    print(`│  Dirty ratio: ${dirtyPct}%`.padEnd(60) + "│")
    
    if (parseFloat(dirtyPct) > 20) {
      print("│  ⚠ High dirty page ratio".padEnd(60) + "│")
      scores.push(0.5)
    } else {
      print("│  ✓ Dirty page ratio healthy".padEnd(60) + "│")
      scores.push(1)
    }
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 4. Check eviction
  print("┌─ 4. EVICTION PRESSURE ────────────────────────────────────┐")
  if (cache) {
    const blocked = cache["application threads page eviction blocked"]
    print(`│  Application threads blocked: ${blocked}`.padEnd(60) + "│")
    
    if (blocked > 0) {
      print("│  ⚠ Eviction pressure detected".padEnd(60) + "│")
      scores.push(0)
    } else {
      print("│  ✓ No eviction pressure".padEnd(60) + "│")
      scores.push(1)
    }
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 5. Check connections
  print("┌─ 5. CONNECTION MEMORY ────────────────────────────────────┐")
  const conn = status.connections
  const connMem = conn.current  // ~1MB each
  
  print(`│  Connections: ${conn.current}`.padEnd(60) + "│")
  print(`│  Estimated memory: ~${connMem} MB`.padEnd(60) + "│")
  
  if (conn.current > 1000) {
    print("│  ⚠ Very high connection count".padEnd(60) + "│")
    scores.push(0.5)
  } else {
    print("│  ✓ Connection count reasonable".padEnd(60) + "│")
    scores.push(1)
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Overall score
  const avgScore = scores.reduce((a, b) => a + b, 0) / scores.length
  const grade = avgScore >= 0.9 ? 'A' : avgScore >= 0.7 ? 'B' : avgScore >= 0.5 ? 'C' : 'D'
  
  print("╔════════════════════════════════════════════════════════════╗")
  print(`║  OVERALL MEMORY HEALTH: ${grade} (${(avgScore * 100).toFixed(0)}%)`.padEnd(61) + "║")
  print("╚════════════════════════════════════════════════════════════╝")
  
  return { scores, avgScore, grade }
}

memoryHealthCheck()
```

### Exercise 2: Cache Efficiency Calculator

```javascript
// Calculate cache efficiency metrics

function cacheEfficiencyCalculator() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║            CACHE EFFICIENCY CALCULATOR                      ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const cache = db.serverStatus().wiredTiger?.cache
  
  if (!cache) {
    print("WiredTiger cache stats not available")
    return
  }
  
  // Cache hit ratio
  const pagesRequested = cache["pages requested from the cache"] || 0
  const pagesNotFound = cache["pages not found in cache"] || 0
  const hitRatio = pagesRequested > 0 
    ? ((pagesRequested - pagesNotFound) / pagesRequested * 100).toFixed(2)
    : 100
  
  // Read/Write ratio
  const bytesRead = cache["bytes read into cache"] || 0
  const bytesWritten = cache["bytes written from cache"] || 0
  const readWriteRatio = bytesWritten > 0 
    ? (bytesRead / bytesWritten).toFixed(2)
    : "N/A"
  
  // Eviction efficiency
  const pagesEvicted = (cache["unmodified pages evicted"] || 0) + 
                       (cache["modified pages evicted"] || 0)
  const evictionBlocked = cache["application threads page eviction blocked"] || 0
  const evictionEfficiency = pagesEvicted > 0
    ? ((pagesEvicted - evictionBlocked) / pagesEvicted * 100).toFixed(2)
    : 100
  
  print("┌─ EFFICIENCY METRICS ──────────────────────────────────────┐")
  print(`│  Cache Hit Ratio: ${hitRatio}%`.padEnd(60) + "│")
  print(`│  Read/Write Ratio: ${readWriteRatio}`.padEnd(60) + "│")
  print(`│  Eviction Efficiency: ${evictionEfficiency}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ RAW METRICS ─────────────────────────────────────────────┐")
  print(`│  Pages requested: ${pagesRequested.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Pages not found: ${pagesNotFound.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Bytes read: ${(bytesRead / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Bytes written: ${(bytesWritten / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Pages evicted: ${pagesEvicted.toLocaleString()}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recommendations
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  
  if (parseFloat(hitRatio) < 95) {
    print("│  ⚠ Low hit ratio - working set may exceed cache".padEnd(60) + "│")
  }
  
  if (parseFloat(evictionEfficiency) < 95) {
    print("│  ⚠ Eviction pressure - consider increasing cache".padEnd(60) + "│")
  }
  
  if (parseFloat(hitRatio) >= 95 && parseFloat(evictionEfficiency) >= 95) {
    print("│  ✓ Cache efficiency is optimal".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
  
  return { hitRatio, readWriteRatio, evictionEfficiency }
}

cacheEfficiencyCalculator()
```

### Exercise 3: Memory Sizing Advisor

```javascript
// Advise on optimal memory configuration

function memorySizingAdvisor() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║             MEMORY SIZING ADVISOR                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Collect data sizes
  const dbs = db.adminCommand({ listDatabases: 1 }).databases
  let totalDataSize = 0
  let totalIndexSize = 0
  
  dbs.forEach(database => {
    if (!['admin', 'local', 'config'].includes(database.name)) {
      const dbStats = db.getSiblingDB(database.name).stats()
      totalDataSize += dbStats.dataSize || 0
      totalIndexSize += dbStats.indexSize || 0
    }
  })
  
  print("┌─ CURRENT DATA SIZES ──────────────────────────────────────┐")
  print(`│  Total Data: ${(totalDataSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Total Indexes: ${(totalIndexSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Estimate working set (20% of data + all indexes)
  const hotDataPct = 0.20
  const workingSet = (totalDataSize * hotDataPct) + totalIndexSize
  
  print("┌─ WORKING SET ESTIMATE (20% hot data) ─────────────────────┐")
  print(`│  Estimated Working Set: ${(workingSet / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Calculate recommended cache size (working set + 20% buffer)
  const recommendedCache = workingSet * 1.2
  
  // Calculate recommended total RAM
  // WiredTiger cache = 50% of (RAM - 1GB)
  // So RAM = (cache / 0.5) + 1GB
  const recommendedRAM = (recommendedCache / 0.5) + (1 * 1024 * 1024 * 1024)
  
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  print(`│  Recommended Cache: ${(recommendedCache / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Recommended Total RAM: ${(recommendedRAM / 1024 / 1024 / 1024).toFixed(0)} GB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Current vs recommended
  const currentCache = db.serverStatus().wiredTiger?.cache["maximum bytes configured"] || 0
  
  print("┌─ CURRENT VS RECOMMENDED ──────────────────────────────────┐")
  print(`│  Current Cache: ${(currentCache / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  
  if (currentCache < recommendedCache) {
    const deficit = ((recommendedCache - currentCache) / 1024 / 1024 / 1024).toFixed(2)
    print(`│  ⚠ Cache deficit: ${deficit} GB`.padEnd(60) + "│")
    print("│  Consider increasing cache or adding RAM".padEnd(60) + "│")
  } else {
    print("│  ✓ Current cache size is adequate".padEnd(60) + "│")
  }
  
  print("└────────────────────────────────────────────────────────────┘")
  
  return {
    totalDataSize,
    totalIndexSize,
    workingSet,
    recommendedCache,
    recommendedRAM,
    currentCache
  }
}

memorySizingAdvisor()
```

---

[← Previous: Performance Tuning](57-performance-tuning.md) | [Next: Storage Engines →](59-storage-engines.md)
