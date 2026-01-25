# Chapter 59: Storage Engines

## Table of Contents
- [Storage Engine Overview](#storage-engine-overview)
- [WiredTiger Storage Engine](#wiredtiger-storage-engine)
- [In-Memory Storage Engine](#in-memory-storage-engine)
- [Storage Configuration](#storage-configuration)
- [Compression](#compression)
- [Encryption at Rest](#encryption-at-rest)
- [Summary](#summary)

---

## Storage Engine Overview

### What is a Storage Engine?

```
┌─────────────────────────────────────────────────────────────────────┐
│                    MongoDB Architecture                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              MongoDB Query Layer                             │   │
│  │  (Query Parser, Query Optimizer, Query Executor)            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│                            ▼                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Storage Engine API                              │   │
│  │  (Abstraction layer between MongoDB and storage engines)    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                            │                                        │
│          ┌─────────────────┼─────────────────┐                     │
│          ▼                 ▼                 ▼                     │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐          │
│  │  WiredTiger   │  │   In-Memory   │  │   MMAPv1      │          │
│  │  (Default)    │  │  (Enterprise) │  │  (Deprecated) │          │
│  └───────────────┘  └───────────────┘  └───────────────┘          │
│          │                 │                 │                     │
│          ▼                 ▼                 ▼                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    File System / Disk                        │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Storage Engine Comparison

| Feature | WiredTiger | In-Memory | MMAPv1 (Deprecated) |
|---------|------------|-----------|---------------------|
| Document-level locking | ✓ | ✓ | ✗ (Collection-level) |
| Compression | ✓ | ✗ | ✗ |
| Encryption at rest | ✓ | ✓ | ✗ |
| Data persistence | ✓ | ✗ | ✓ |
| Journaling | ✓ | ✗ | ✓ |
| Default since | MongoDB 3.2 | N/A | MongoDB 3.0 |

### Check Current Storage Engine

```javascript
// Check storage engine
db.serverStatus().storageEngine

// Output example
{
  "name": "wiredTiger",
  "supportsCommittedReads": true,
  "oldestRequiredTimestampForCrashRecovery": Timestamp(1705312800, 1),
  "supportsPendingDrops": true,
  "supportsSnapshots": true,
  "supportsSnapshotReadConcern": true,
  "readOnly": false,
  "persistent": true
}
```

---

## WiredTiger Storage Engine

### WiredTiger Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                  WiredTiger Architecture                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    WiredTiger Cache                          │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐   │   │
│  │  │   Clean Pages   │  │     Dirty Pages                 │   │   │
│  │  │  (from disk)    │  │  (modified, need writing)       │   │   │
│  │  └─────────────────┘  └─────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│              │                           │                          │
│              │                           │ Checkpoint                │
│              │                           │ (every 60s or 2GB)       │
│              ▼                           ▼                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    On-Disk Files                             │   │
│  │  ┌──────────────┐  ┌────────────┐  ┌──────────────────┐    │   │
│  │  │  Data Files  │  │  Indexes   │  │     Journal      │    │   │
│  │  │  (.wt)       │  │  (.wt)     │  │  (WiredTigerLog) │    │   │
│  │  └──────────────┘  └────────────┘  └──────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Key Features:                                                     │
│  • MVCC (Multi-Version Concurrency Control)                        │
│  • Document-level locking                                          │
│  • Compression (snappy, zlib, zstd)                                │
│  • Checkpointing for durability                                    │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### WiredTiger Configuration

```yaml
# mongod.conf - WiredTiger settings
storage:
  dbPath: /var/lib/mongodb
  journal:
    enabled: true
  wiredTiger:
    engineConfig:
      cacheSizeGB: 4
      journalCompressor: snappy
      directoryForIndexes: false
    collectionConfig:
      blockCompressor: snappy
    indexConfig:
      prefixCompression: true
```

### WiredTiger Statistics

```javascript
// Get WiredTiger statistics
function getWiredTigerStats() {
  const stats = db.serverStatus().wiredTiger
  
  return {
    // Cache statistics
    cache: {
      maxBytes: stats.cache["maximum bytes configured"],
      currentBytes: stats.cache["bytes currently in the cache"],
      dirtyBytes: stats.cache["tracked dirty bytes in the cache"],
      pagesRead: stats.cache["pages read into cache"],
      pagesWritten: stats.cache["pages written from cache"]
    },
    
    // Concurrent transactions
    transactions: {
      readTicketsAvailable: stats.concurrentTransactions.read.available,
      readTicketsTotal: stats.concurrentTransactions.read.totalTickets,
      writeTicketsAvailable: stats.concurrentTransactions.write.available,
      writeTicketsTotal: stats.concurrentTransactions.write.totalTickets
    },
    
    // Block manager (disk I/O)
    blockManager: {
      blocksRead: stats["block-manager"]["blocks read"],
      blocksWritten: stats["block-manager"]["blocks written"],
      bytesRead: stats["block-manager"]["bytes read"],
      bytesWritten: stats["block-manager"]["bytes written"]
    },
    
    // Connection statistics
    connection: {
      filesCurrentlyOpen: stats.connection["files currently open"],
      totalReadIO: stats.connection["total read I/Os"],
      totalWriteIO: stats.connection["total write I/Os"]
    }
  }
}

print(JSON.stringify(getWiredTigerStats(), null, 2))
```

### Checkpointing

```javascript
// WiredTiger creates checkpoints:
// - Every 60 seconds
// - Every 2 GB of journal data
// - On clean shutdown

// Force a checkpoint
db.adminCommand({ fsync: 1 })

// Check checkpoint statistics
const checkpoint = db.serverStatus().wiredTiger["checkpoint"]
print(`Checkpoints completed: ${checkpoint["completed"]}`)
print(`Checkpoint time (ms): ${checkpoint["time (msecs)"]}`)

// Monitor checkpoint progress
function monitorCheckpoints(durationSec = 60) {
  const start = db.serverStatus().wiredTiger.checkpoint
  
  print(`Monitoring checkpoints for ${durationSec} seconds...`)
  sleep(durationSec * 1000)
  
  const end = db.serverStatus().wiredTiger.checkpoint
  const checkpointsCompleted = end.completed - start.completed
  
  print(`Checkpoints completed: ${checkpointsCompleted}`)
  print(`Average time: ${checkpointsCompleted > 0 ? (end["time (msecs)"] - start["time (msecs)"]) / checkpointsCompleted : 0} ms`)
}
```

### Document-Level Concurrency

```javascript
// WiredTiger uses MVCC for document-level concurrency
// Multiple readers can access the same document simultaneously
// Writers get exclusive access to individual documents

// Check concurrency tickets
function checkConcurrencyTickets() {
  const tickets = db.serverStatus().wiredTiger.concurrentTransactions
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              CONCURRENCY TICKETS                            ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("┌─ READ TICKETS ────────────────────────────────────────────┐")
  print(`│  Available: ${tickets.read.available}`.padEnd(60) + "│")
  print(`│  Total: ${tickets.read.totalTickets}`.padEnd(60) + "│")
  print(`│  In Use: ${tickets.read.totalTickets - tickets.read.available}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  print("┌─ WRITE TICKETS ───────────────────────────────────────────┐")
  print(`│  Available: ${tickets.write.available}`.padEnd(60) + "│")
  print(`│  Total: ${tickets.write.totalTickets}`.padEnd(60) + "│")
  print(`│  In Use: ${tickets.write.totalTickets - tickets.write.available}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  // Warning if tickets are depleted
  if (tickets.read.available < 10 || tickets.write.available < 10) {
    print("\n⚠ Warning: Low ticket availability - possible contention")
  }
}

checkConcurrencyTickets()
```

---

## In-Memory Storage Engine

### In-Memory Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│               In-Memory Storage Engine                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Features:                                                         │
│  • All data stored in memory                                       │
│  • No disk persistence (data lost on restart)                      │
│  • Document-level concurrency                                      │
│  • Ultra-low latency                                               │
│  • Enterprise feature only                                         │
│                                                                     │
│  Use Cases:                                                        │
│  • Session stores                                                  │
│  • Real-time analytics                                             │
│  • Caching layers                                                  │
│  • High-frequency trading data                                     │
│                                                                     │
│  Memory Structure:                                                 │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    Allocated Memory                          │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────────┐   │   │
│  │  │   Data Pages    │  │        Index Pages              │   │   │
│  │  │                 │  │                                 │   │   │
│  │  └─────────────────┘  └─────────────────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Note: Data is NOT persisted to disk!                              │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### In-Memory Configuration

```yaml
# mongod.conf - In-Memory storage engine
storage:
  engine: inMemory
  inMemory:
    engineConfig:
      inMemorySizeGB: 8  # Allocated memory size
```

### In-Memory Replica Set

```javascript
// For durability with in-memory, use replica sets
// Primary: in-memory for speed
// Secondary: WiredTiger for persistence

// Primary config (in-memory)
// mongod --storageEngine inMemory --replSet myRS

// Secondary config (WiredTiger)
// mongod --storageEngine wiredTiger --replSet myRS

// The secondary provides persistence while primary provides speed
```

---

## Storage Configuration

### Data Directory Structure

```
/var/lib/mongodb/
├── collection-*.wt          # Collection data files
├── index-*.wt               # Index data files
├── _mdb_catalog.wt          # Metadata catalog
├── sizeStorer.wt            # Collection size info
├── storage.bson             # Storage options
├── WiredTiger               # WiredTiger version file
├── WiredTiger.lock          # Lock file
├── WiredTiger.turtle        # Checkpoint metadata
├── WiredTiger.wt            # WiredTiger metadata
├── WiredTigerHS.wt          # History store
├── diagnostic.data/         # Diagnostic data
└── journal/                 # Journal files
    ├── WiredTigerLog.*
    └── WiredTigerPreplog.*
```

### Storage Statistics

```javascript
// Get storage statistics for a collection
function getStorageStats(collName) {
  const coll = db.getCollection(collName)
  const stats = coll.stats()
  
  print("╔════════════════════════════════════════════════════════════╗")
  print(`║  STORAGE STATISTICS: ${collName}`.padEnd(61) + "║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print("┌─ SIZE METRICS ────────────────────────────────────────────┐")
  print(`│  Document Count: ${stats.count.toLocaleString()}`.padEnd(60) + "│")
  print(`│  Average Doc Size: ${(stats.avgObjSize / 1024).toFixed(2)} KB`.padEnd(60) + "│")
  print(`│  Data Size: ${(stats.size / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Storage Size: ${(stats.storageSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Index Size: ${(stats.totalIndexSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Calculate compression ratio
  if (stats.size > 0 && stats.storageSize > 0) {
    const compressionRatio = (stats.size / stats.storageSize).toFixed(2)
    print("┌─ COMPRESSION ──────────────────────────────────────────────┐")
    print(`│  Compression Ratio: ${compressionRatio}:1`.padEnd(60) + "│")
    print(`│  Space Savings: ${((1 - stats.storageSize / stats.size) * 100).toFixed(1)}%`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // WiredTiger specific stats
  if (stats.wiredTiger) {
    const wt = stats.wiredTiger
    print("┌─ WIREDTIGER STATS ─────────────────────────────────────────┐")
    print(`│  Block Manager Size: ${(wt["block-manager"]["file size in bytes"] / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
    print(`│  Blocks Read: ${wt["block-manager"]["blocks read"].toLocaleString()}`.padEnd(60) + "│")
    print(`│  Blocks Written: ${wt["block-manager"]["blocks written"].toLocaleString()}`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘")
  }
  
  return stats
}

// Usage
// getStorageStats("orders")
```

### Directory for Indexes

```yaml
# Store indexes in separate directory (for different storage)
storage:
  dbPath: /var/lib/mongodb
  wiredTiger:
    engineConfig:
      directoryForIndexes: true

# This creates:
# /var/lib/mongodb/collection-*.wt  (data)
# /var/lib/mongodb/index/index-*.wt (indexes - can be on faster SSD)
```

---

## Compression

### Compression Options

| Compressor | Ratio | Speed | CPU Usage | Use Case |
|------------|-------|-------|-----------|----------|
| none | 1:1 | Fastest | Lowest | Already compressed data |
| snappy | ~2:1 | Fast | Low | Default, balanced |
| zlib | ~3-4:1 | Slower | Medium | Storage-constrained |
| zstd | ~3-4:1 | Fast | Medium | MongoDB 4.2+, best balance |

### Configure Compression

```yaml
# mongod.conf
storage:
  wiredTiger:
    collectionConfig:
      blockCompressor: zstd  # snappy, zlib, zstd, none
    indexConfig:
      prefixCompression: true
```

```javascript
// Set compression per collection
db.createCollection("logs", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd"
    }
  }
})

// Check compression for existing collection
db.collection.stats().wiredTiger.creationString
// Look for "block_compressor=..." in the output
```

### Compression Analysis

```javascript
// Analyze compression effectiveness
function analyzeCompression(collName) {
  const coll = db.getCollection(collName)
  const stats = coll.stats()
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              COMPRESSION ANALYSIS                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  print(`Collection: ${collName}\n`)
  
  const dataSize = stats.size
  const storageSize = stats.storageSize
  const ratio = dataSize / storageSize
  const savings = (1 - storageSize / dataSize) * 100
  
  print("┌─ COMPRESSION METRICS ─────────────────────────────────────┐")
  print(`│  Uncompressed Size: ${(dataSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Compressed Size: ${(storageSize / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  Compression Ratio: ${ratio.toFixed(2)}:1`.padEnd(60) + "│")
  print(`│  Space Savings: ${savings.toFixed(1)}%`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Evaluate compression quality
  print("┌─ EVALUATION ──────────────────────────────────────────────┐")
  if (ratio >= 3) {
    print("│  ✓ Excellent compression".padEnd(60) + "│")
  } else if (ratio >= 2) {
    print("│  ✓ Good compression".padEnd(60) + "│")
  } else if (ratio >= 1.5) {
    print("│  ⚠ Moderate compression - data may already be compressed".padEnd(60) + "│")
  } else {
    print("│  ⚠ Low compression ratio".padEnd(60) + "│")
    print("│    Consider:".padEnd(60) + "│")
    print("│    • Data may already be compressed".padEnd(60) + "│")
    print("│    • Try zstd or zlib compressor".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘")
  
  return { dataSize, storageSize, ratio, savings }
}

// Usage
// analyzeCompression("orders")
```

### Compare Compressors

```javascript
// Test compression with different compressors
function compareCompressors(sourceColl, docCount = 1000) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           COMPRESSOR COMPARISON                             ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const compressors = ['none', 'snappy', 'zlib', 'zstd']
  const results = []
  
  // Get sample documents
  const docs = db.getCollection(sourceColl)
    .find()
    .limit(docCount)
    .toArray()
  
  if (docs.length === 0) {
    print("Source collection is empty")
    return
  }
  
  print(`Testing with ${docs.length} documents from ${sourceColl}\n`)
  
  compressors.forEach(compressor => {
    const testColl = `_compression_test_${compressor}`
    
    // Create collection with specific compressor
    db.getCollection(testColl).drop()
    db.createCollection(testColl, {
      storageEngine: {
        wiredTiger: {
          configString: `block_compressor=${compressor}`
        }
      }
    })
    
    // Insert documents
    const start = Date.now()
    db.getCollection(testColl).insertMany(docs)
    const insertTime = Date.now() - start
    
    // Get stats
    const stats = db.getCollection(testColl).stats()
    const ratio = stats.size / stats.storageSize
    
    results.push({
      compressor,
      ratio: ratio.toFixed(2),
      storageSize: (stats.storageSize / 1024).toFixed(0),
      insertTime
    })
    
    // Cleanup
    db.getCollection(testColl).drop()
  })
  
  // Print results
  print("┌─ RESULTS ─────────────────────────────────────────────────┐")
  print("│  Compressor      Ratio      Storage (KB)    Insert (ms)  │")
  print("├────────────────────────────────────────────────────────────┤")
  
  results.forEach(r => {
    print(`│  ${r.compressor.padEnd(14)} ${r.ratio.padStart(6)}:1    ${r.storageSize.padStart(10)} KB    ${String(r.insertTime).padStart(8)} ms  │`)
  })
  
  print("└────────────────────────────────────────────────────────────┘")
  
  return results
}

// Usage
// compareCompressors("orders", 5000)
```

---

## Encryption at Rest

### Encryption Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│               Encryption at Rest Architecture                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                    MongoDB Instance                          │   │
│  │                                                              │   │
│  │  Application Data (decrypted in memory)                     │   │
│  │                    │                                         │   │
│  │                    ▼                                         │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │         WiredTiger Encryption Layer                 │    │   │
│  │  │         (AES-256-CBC or AES-256-GCM)               │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  │                    │                                         │   │
│  │                    ▼                                         │   │
│  │  ┌─────────────────────────────────────────────────────┐    │   │
│  │  │         Encrypted Data on Disk                      │    │   │
│  │  └─────────────────────────────────────────────────────┘    │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                    │                                               │
│                    ▼                                               │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │              Key Management                                  │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────────────┐   │   │
│  │  │ Local Key │  │ KMIP      │  │ Cloud KMS (AWS, GCP,  │   │   │
│  │  │ File      │  │ Server    │  │ Azure Key Vault)      │   │   │
│  │  └───────────┘  └───────────┘  └───────────────────────┘   │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Enterprise Feature Only                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Enable Encryption (Enterprise)

```yaml
# mongod.conf - Local key file
security:
  enableEncryption: true
  encryptionKeyFile: /etc/mongodb/encryption-keyfile

# Create key file
# openssl rand -base64 32 > /etc/mongodb/encryption-keyfile
# chmod 600 /etc/mongodb/encryption-keyfile
```

### KMIP Integration

```yaml
# mongod.conf - KMIP server
security:
  enableEncryption: true
  kmip:
    serverName: kmip.example.com
    port: 5696
    clientCertificateFile: /etc/mongodb/kmip-client.pem
    serverCAFile: /etc/mongodb/kmip-ca.pem
```

### Verify Encryption

```javascript
// Check if encryption is enabled
function checkEncryption() {
  const status = db.serverStatus()
  
  print("╔════════════════════════════════════════════════════════════╗")
  print("║              ENCRYPTION STATUS                              ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  if (status.security && status.security.SSLServerHasCertificateAuthority !== undefined) {
    print("┌─ TLS/SSL STATUS ───────────────────────────────────────────┐")
    print(`│  TLS Enabled: ${status.security.SSLServerHasCertificateAuthority ? 'Yes' : 'Check config'}`.padEnd(60) + "│")
    print("└────────────────────────────────────────────────────────────┘\n")
  }
  
  // Check for encryption at rest
  const storageEngine = status.storageEngine
  print("┌─ ENCRYPTION AT REST ──────────────────────────────────────┐")
  print(`│  Storage Engine: ${storageEngine.name}`.padEnd(60) + "│")
  
  if (status.encryptionAtRest) {
    print(`│  Encryption: Enabled`.padEnd(60) + "│")
    print(`│  Mode: ${status.encryptionAtRest.encryptionMode}`.padEnd(60) + "│")
  } else {
    print(`│  Encryption at Rest: Not configured or Community Edition`.padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘")
}

checkEncryption()
```

---

## Summary

### Storage Engine Selection

| Scenario | Recommended Engine |
|----------|-------------------|
| General purpose | WiredTiger |
| Highest performance, no persistence | In-Memory |
| Legacy applications | Migrate to WiredTiger |

### WiredTiger Best Practices

| Practice | Benefit |
|----------|---------|
| Size cache appropriately | Better performance |
| Use SSD storage | Lower latency |
| Enable compression | Space savings |
| Monitor checkpoint times | Prevent I/O spikes |

### Compression Guidelines

| Data Type | Recommended Compressor |
|-----------|----------------------|
| Text/JSON data | zstd or zlib |
| Mixed data | snappy |
| Already compressed | none |
| Balanced workload | snappy (default) |

### Key Metrics to Monitor

| Metric | Target |
|--------|--------|
| Compression ratio | > 2:1 |
| Checkpoint time | < 60 seconds |
| Ticket availability | > 50% |
| Cache hit ratio | > 95% |

---

## Practice Questions

1. What is the default storage engine in MongoDB?
2. What are the key differences between WiredTiger and In-Memory engines?
3. How does WiredTiger achieve document-level concurrency?
4. What triggers a WiredTiger checkpoint?
5. Which compression algorithm provides the best balance of ratio and speed?
6. How do you enable encryption at rest?
7. What is the purpose of concurrency tickets?
8. When should you use the In-Memory storage engine?

---

## Hands-On Exercises

### Exercise 1: Storage Engine Monitor

```javascript
// Monitor storage engine health

function storageEngineMonitor() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║           STORAGE ENGINE MONITOR                            ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const status = db.serverStatus()
  const wt = status.wiredTiger
  
  if (!wt) {
    print("WiredTiger statistics not available")
    return
  }
  
  // Cache Health
  print("┌─ CACHE HEALTH ────────────────────────────────────────────┐")
  const cache = wt.cache
  const cacheUsed = cache["bytes currently in the cache"]
  const cacheMax = cache["maximum bytes configured"]
  const cachePct = (cacheUsed / cacheMax * 100).toFixed(1)
  
  print(`│  Usage: ${cachePct}%`.padEnd(60) + "│")
  print(`│  Size: ${(cacheUsed / 1024 / 1024 / 1024).toFixed(2)} / ${(cacheMax / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  
  if (parseFloat(cachePct) > 90) {
    print("│  ⚠ High cache utilization".padEnd(60) + "│")
  } else {
    print("│  ✓ Cache utilization healthy".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Concurrency
  print("┌─ CONCURRENCY ─────────────────────────────────────────────┐")
  const read = wt.concurrentTransactions.read
  const write = wt.concurrentTransactions.write
  
  const readInUse = read.totalTickets - read.available
  const writeInUse = write.totalTickets - write.available
  
  print(`│  Read tickets in use: ${readInUse} / ${read.totalTickets}`.padEnd(60) + "│")
  print(`│  Write tickets in use: ${writeInUse} / ${write.totalTickets}`.padEnd(60) + "│")
  
  if (read.available < 20 || write.available < 20) {
    print("│  ⚠ Low ticket availability - possible contention".padEnd(60) + "│")
  } else {
    print("│  ✓ Concurrency healthy".padEnd(60) + "│")
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Checkpoint
  print("┌─ CHECKPOINT STATUS ───────────────────────────────────────┐")
  const checkpoint = wt.checkpoint
  print(`│  Checkpoints completed: ${checkpoint.completed}`.padEnd(60) + "│")
  print(`│  Total checkpoint time: ${(checkpoint["time (msecs)"] / 1000).toFixed(1)} seconds`.padEnd(60) + "│")
  
  if (checkpoint.completed > 0) {
    const avgTime = checkpoint["time (msecs)"] / checkpoint.completed
    print(`│  Average checkpoint time: ${avgTime.toFixed(0)} ms`.padEnd(60) + "│")
    
    if (avgTime > 60000) {
      print("│  ⚠ Long checkpoint times - review I/O".padEnd(60) + "│")
    } else {
      print("│  ✓ Checkpoint times healthy".padEnd(60) + "│")
    }
  }
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Block Manager (I/O)
  print("┌─ BLOCK MANAGER (I/O) ─────────────────────────────────────┐")
  const bm = wt["block-manager"]
  print(`│  Blocks read: ${bm["blocks read"].toLocaleString()}`.padEnd(60) + "│")
  print(`│  Blocks written: ${bm["blocks written"].toLocaleString()}`.padEnd(60) + "│")
  print(`│  Bytes read: ${(bm["bytes read"] / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Bytes written: ${(bm["bytes written"] / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
}

storageEngineMonitor()
```

### Exercise 2: Collection Storage Analyzer

```javascript
// Analyze storage for all collections

function analyzeAllCollections() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║         COLLECTION STORAGE ANALYZER                         ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const collections = db.getCollectionNames().filter(n => !n.startsWith('system.'))
  
  if (collections.length === 0) {
    print("No user collections found")
    return
  }
  
  const results = []
  
  collections.forEach(collName => {
    try {
      const stats = db.getCollection(collName).stats()
      results.push({
        name: collName,
        count: stats.count,
        dataSize: stats.size,
        storageSize: stats.storageSize,
        indexSize: stats.totalIndexSize,
        avgObjSize: stats.avgObjSize,
        ratio: stats.size > 0 ? (stats.size / stats.storageSize).toFixed(2) : 0
      })
    } catch (e) {
      // Skip if can't get stats
    }
  })
  
  // Sort by storage size
  results.sort((a, b) => b.storageSize - a.storageSize)
  
  print("┌─ COLLECTIONS BY STORAGE SIZE ─────────────────────────────┐")
  print("│  Collection               Docs        Storage    Ratio    │")
  print("├────────────────────────────────────────────────────────────┤")
  
  let totalStorage = 0
  let totalIndex = 0
  
  results.forEach(r => {
    const name = r.name.substring(0, 22).padEnd(24)
    const count = r.count.toLocaleString().padStart(10)
    const storage = (r.storageSize / 1024 / 1024).toFixed(2).padStart(10)
    const ratio = r.ratio.toString().padStart(6)
    
    print(`│  ${name} ${count}   ${storage} MB  ${ratio}:1 │`)
    
    totalStorage += r.storageSize
    totalIndex += r.indexSize
  })
  
  print("├────────────────────────────────────────────────────────────┤")
  print(`│  TOTAL STORAGE: ${(totalStorage / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print(`│  TOTAL INDEX: ${(totalIndex / 1024 / 1024).toFixed(2)} MB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  return results
}

analyzeAllCollections()
```

### Exercise 3: Storage Capacity Planner

```javascript
// Plan storage capacity

function storageCapacityPlanner(growthRatePctPerMonth = 10, monthsToProject = 12) {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║          STORAGE CAPACITY PLANNER                           ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  // Get current storage
  const dbStats = db.stats()
  const currentDataSize = dbStats.dataSize
  const currentStorageSize = dbStats.storageSize
  const currentIndexSize = dbStats.indexSize
  
  print(`Growth rate: ${growthRatePctPerMonth}% per month`)
  print(`Projection period: ${monthsToProject} months\n`)
  
  print("┌─ CURRENT STATE ───────────────────────────────────────────┐")
  print(`│  Data Size: ${(currentDataSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Storage Size: ${(currentStorageSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Index Size: ${(currentIndexSize / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Total: ${((currentStorageSize + currentIndexSize) / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Project growth
  print("┌─ PROJECTED GROWTH ────────────────────────────────────────┐")
  print("│  Month       Data         Storage      Index        Total │")
  print("├────────────────────────────────────────────────────────────┤")
  
  const multiplier = 1 + (growthRatePctPerMonth / 100)
  
  for (let month = 0; month <= monthsToProject; month += 3) {
    const factor = Math.pow(multiplier, month)
    const projData = currentDataSize * factor
    const projStorage = currentStorageSize * factor
    const projIndex = currentIndexSize * factor
    const projTotal = projStorage + projIndex
    
    const monthStr = month === 0 ? "Now" : `+${month}m`
    print(`│  ${monthStr.padEnd(8)} ${(projData / 1024 / 1024 / 1024).toFixed(2).padStart(8)} GB  ${(projStorage / 1024 / 1024 / 1024).toFixed(2).padStart(8)} GB  ${(projIndex / 1024 / 1024 / 1024).toFixed(2).padStart(6)} GB  ${(projTotal / 1024 / 1024 / 1024).toFixed(2).padStart(8)} GB │`)
  }
  
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Recommendations
  const projectedTotal = (currentStorageSize + currentIndexSize) * Math.pow(multiplier, monthsToProject)
  
  print("┌─ RECOMMENDATIONS ─────────────────────────────────────────┐")
  print(`│  Projected total in ${monthsToProject} months: ${(projectedTotal / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print("│".padEnd(60) + "│")
  print("│  Consider:".padEnd(60) + "│")
  print(`│  • Provision at least ${(projectedTotal * 1.5 / 1024 / 1024 / 1024).toFixed(0)} GB for safety margin`.padEnd(60) + "│")
  print("│  • Use compression to reduce storage needs".padEnd(60) + "│")
  print("│  • Implement data archival strategy".padEnd(60) + "│")
  print("│  • Monitor growth rate monthly".padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘")
  
  return {
    current: {
      dataSize: currentDataSize,
      storageSize: currentStorageSize,
      indexSize: currentIndexSize
    },
    projected: {
      months: monthsToProject,
      totalSize: projectedTotal
    }
  }
}

// Usage
// storageCapacityPlanner(10, 12)  // 10% growth, 12 months
```

### Exercise 4: WiredTiger Health Dashboard

```javascript
// Comprehensive WiredTiger health dashboard

function wiredTigerDashboard() {
  print("╔════════════════════════════════════════════════════════════╗")
  print("║          WIREDTIGER HEALTH DASHBOARD                        ║")
  print("╚════════════════════════════════════════════════════════════╝\n")
  
  const wt = db.serverStatus().wiredTiger
  
  if (!wt) {
    print("WiredTiger not available")
    return
  }
  
  const health = {
    cache: { score: 0, max: 3 },
    concurrency: { score: 0, max: 2 },
    io: { score: 0, max: 2 },
    checkpoint: { score: 0, max: 2 }
  }
  
  // 1. Cache Health
  print("┌─ 1. CACHE HEALTH ─────────────────────────────────────────┐")
  const cache = wt.cache
  const cacheUsedPct = (cache["bytes currently in the cache"] / cache["maximum bytes configured"] * 100)
  const dirtyPct = (cache["tracked dirty bytes in the cache"] / cache["maximum bytes configured"] * 100)
  const evictionBlocked = cache["application threads page eviction blocked"]
  
  print(`│  Cache Utilization: ${cacheUsedPct.toFixed(1)}%`.padEnd(60) + "│")
  if (cacheUsedPct < 85) health.cache.score++
  
  print(`│  Dirty Pages: ${dirtyPct.toFixed(1)}%`.padEnd(60) + "│")
  if (dirtyPct < 20) health.cache.score++
  
  print(`│  Eviction Blocked: ${evictionBlocked}`.padEnd(60) + "│")
  if (evictionBlocked === 0) health.cache.score++
  
  print(`│  Score: ${health.cache.score}/${health.cache.max}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 2. Concurrency Health
  print("┌─ 2. CONCURRENCY HEALTH ───────────────────────────────────┐")
  const read = wt.concurrentTransactions.read
  const write = wt.concurrentTransactions.write
  
  const readAvailPct = (read.available / read.totalTickets * 100)
  const writeAvailPct = (write.available / write.totalTickets * 100)
  
  print(`│  Read Tickets Available: ${readAvailPct.toFixed(0)}%`.padEnd(60) + "│")
  if (readAvailPct > 50) health.concurrency.score++
  
  print(`│  Write Tickets Available: ${writeAvailPct.toFixed(0)}%`.padEnd(60) + "│")
  if (writeAvailPct > 50) health.concurrency.score++
  
  print(`│  Score: ${health.concurrency.score}/${health.concurrency.max}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 3. I/O Health
  print("┌─ 3. I/O HEALTH ───────────────────────────────────────────┐")
  const bm = wt["block-manager"]
  const bytesRead = bm["bytes read"]
  const bytesWritten = bm["bytes written"]
  
  print(`│  Total Read: ${(bytesRead / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  print(`│  Total Written: ${(bytesWritten / 1024 / 1024 / 1024).toFixed(2)} GB`.padEnd(60) + "│")
  
  // Score based on read/write balance (lower write amplification is better)
  const rwRatio = bytesWritten > 0 ? bytesRead / bytesWritten : 1
  print(`│  Read/Write Ratio: ${rwRatio.toFixed(2)}`.padEnd(60) + "│")
  
  health.io.score = 2  // Default good for now
  print(`│  Score: ${health.io.score}/${health.io.max}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // 4. Checkpoint Health
  print("┌─ 4. CHECKPOINT HEALTH ────────────────────────────────────┐")
  const cp = wt.checkpoint
  const avgCpTime = cp.completed > 0 ? cp["time (msecs)"] / cp.completed : 0
  
  print(`│  Checkpoints Completed: ${cp.completed}`.padEnd(60) + "│")
  print(`│  Average Checkpoint Time: ${avgCpTime.toFixed(0)} ms`.padEnd(60) + "│")
  
  if (avgCpTime < 30000) health.checkpoint.score++  // < 30 seconds
  if (avgCpTime < 60000) health.checkpoint.score++  // < 60 seconds
  
  print(`│  Score: ${health.checkpoint.score}/${health.checkpoint.max}`.padEnd(60) + "│")
  print("└────────────────────────────────────────────────────────────┘\n")
  
  // Overall Health
  const totalScore = health.cache.score + health.concurrency.score + 
                     health.io.score + health.checkpoint.score
  const maxScore = health.cache.max + health.concurrency.max + 
                   health.io.max + health.checkpoint.max
  const pct = (totalScore / maxScore * 100).toFixed(0)
  
  let grade = 'F'
  if (pct >= 90) grade = 'A'
  else if (pct >= 80) grade = 'B'
  else if (pct >= 70) grade = 'C'
  else if (pct >= 60) grade = 'D'
  
  print("╔════════════════════════════════════════════════════════════╗")
  print(`║  OVERALL WIREDTIGER HEALTH: ${grade} (${totalScore}/${maxScore} = ${pct}%)`.padEnd(61) + "║")
  print("╚════════════════════════════════════════════════════════════╝")
  
  return { health, totalScore, maxScore, grade }
}

wiredTigerDashboard()
```

---

[← Previous: Memory Management](58-memory-management.md) | [Next: Logging and Diagnostics →](60-logging-diagnostics.md)
