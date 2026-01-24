# Chapter 3: MongoDB Architecture

## Table of Contents
- [Overview of MongoDB Architecture](#overview-of-mongodb-architecture)
- [Server Components](#server-components)
- [Storage Engine](#storage-engine)
- [Memory Management](#memory-management)
- [Data Organization](#data-organization)
- [Query Engine](#query-engine)
- [Concurrency Control](#concurrency-control)
- [Journaling and Durability](#journaling-and-durability)
- [Network Layer](#network-layer)
- [Summary](#summary)

---

## Overview of MongoDB Architecture

MongoDB uses a layered architecture designed for flexibility, performance, and scalability.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Client Application                               │
├─────────────────────────────────────────────────────────────────────────┤
│                         MongoDB Driver                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                          Network Layer                                   │
│                    (Wire Protocol / TCP/IP)                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                        Query Layer                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │    │
│  │  │Query Planner │ │Query Executor│ │Aggregation Framework │   │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                      Document Layer                             │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │    │
│  │  │ BSON Parser  │ │Index Manager │ │ Validation Engine    │   │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │                     Storage Engine                              │    │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐   │    │
│  │  │   WiredTiger │ │    Cache     │ │   Journal / WAL      │   │    │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘   │    │
│  └────────────────────────────────────────────────────────────────┘    │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                      File System / Disk Storage                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### Architecture Principles

| Principle | Description |
|-----------|-------------|
| **Modularity** | Pluggable storage engines |
| **Document Model** | Flexible schema with BSON documents |
| **Scalability** | Horizontal scaling through sharding |
| **High Availability** | Automatic failover with replica sets |
| **Performance** | In-memory caching, optimized queries |

---

## Server Components

### mongod - The Core Database Server

`mongod` is the primary daemon process that handles data requests, manages data access, and performs background operations.

```bash
# Start mongod with default settings
mongod

# Start with configuration file
mongod --config /etc/mongod.conf

# Common command line options
mongod \
  --dbpath /data/db \
  --port 27017 \
  --bind_ip 0.0.0.0 \
  --logpath /var/log/mongodb/mongod.log \
  --logappend \
  --fork
```

### mongod Responsibilities

```
┌─────────────────────────────────────────────────────────────┐
│                        mongod Process                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Connection Pool │  │ Thread Pool     │                 │
│  │ Management      │  │ (Request        │                 │
│  │                 │  │  Handling)      │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Query Processor │  │ Write Operation │                 │
│  │ & Optimizer     │  │ Handler         │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Index Manager   │  │ Storage Engine  │                 │
│  │                 │  │ Interface       │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Replication     │  │ Background      │                 │
│  │ Manager         │  │ Tasks           │                 │
│  └─────────────────┘  └─────────────────┘                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### mongos - The Sharding Router

`mongos` routes queries and write operations to shards in a sharded cluster.

```bash
# Start mongos
mongos --configdb configReplSet/config1:27019,config2:27019,config3:27019

# mongos with configuration
mongos --config /etc/mongos.conf
```

### mongos Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Client Applications                        │
└──────────────────────────────────┬──────────────────────────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │          mongos             │
                    │   (Query Router)            │
                    │                             │
                    │  ┌───────────────────────┐ │
                    │  │   Routing Table       │ │
                    │  │   (Chunk Metadata)    │ │
                    │  └───────────────────────┘ │
                    └──────────────┬──────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         │                         │                         │
         ▼                         ▼                         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│    Shard 1      │    │    Shard 2      │    │    Shard 3      │
│   (mongod)      │    │   (mongod)      │    │   (mongod)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Config Servers

Store cluster metadata and routing information for sharded clusters.

```
┌─────────────────────────────────────────────────────────────┐
│                    Config Server Replica Set                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Stores:                                                    │
│  • Shard information                                        │
│  • Chunk ranges and locations                              │
│  • Database and collection settings                        │
│  • Authentication and authorization data                   │
│  • Balancer settings                                       │
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │  Config 1   │  │  Config 2   │  │  Config 3   │        │
│  │  (PRIMARY)  │  │(SECONDARY)  │  │(SECONDARY)  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Storage Engine

### WiredTiger Storage Engine

WiredTiger is MongoDB's default storage engine since version 3.2.

```
┌─────────────────────────────────────────────────────────────────────┐
│                       WiredTiger Architecture                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     In-Memory Cache                          │   │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────────────────┐ │   │
│  │  │Internal Cache│ │ File System  │ │  Modified Pages      │ │   │
│  │  │(default 50%) │ │   Cache      │ │   (Dirty Pages)      │ │   │
│  │  └──────────────┘ └──────────────┘ └──────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│                                ▼                                    │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                     Block Manager                            │   │
│  │          (Handles reading/writing data blocks)               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                │                                    │
│                ┌───────────────┴───────────────┐                   │
│                ▼                               ▼                    │
│  ┌──────────────────────────┐    ┌──────────────────────────┐     │
│  │    Data Files (.wt)      │    │    Journal Files (WAL)   │     │
│  │                          │    │                          │     │
│  │  • collection-*.wt       │    │  • WiredTigerLog.*       │     │
│  │  • index-*.wt            │    │  • Write-Ahead Logging   │     │
│  └──────────────────────────┘    └──────────────────────────┘     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### WiredTiger Features

| Feature | Description |
|---------|-------------|
| **Document-Level Concurrency** | Multiple writers can modify different documents simultaneously |
| **Compression** | snappy (default), zlib, zstd for data and indexes |
| **Checkpoints** | Periodic snapshots for durability |
| **Journal (WAL)** | Write-ahead log for crash recovery |
| **Cache** | In-memory cache for frequently accessed data |

### Data Compression

```javascript
// Configure compression for a collection
db.createCollection("logs", {
  storageEngine: {
    wiredTiger: {
      configString: "block_compressor=zstd"
    }
  }
});

// Compression options:
// - "snappy" (default) - Fast compression
// - "zlib" - Higher compression ratio
// - "zstd" - Best balance of speed and compression
// - "none" - No compression
```

### Checking Storage Statistics

```javascript
// Collection storage stats
db.collection.stats()

// Output includes:
{
  "ns": "mydb.collection",
  "size": 1048576,           // Data size in bytes
  "count": 10000,            // Document count
  "avgObjSize": 104,         // Average document size
  "storageSize": 524288,     // Allocated storage
  "totalIndexSize": 36864,   // Total index size
  "indexSizes": {
    "_id_": 20480,
    "name_1": 16384
  },
  "wiredTiger": {
    "compression ratio": 2.5  // Compression effectiveness
  }
}

// Database stats
db.stats()

// Server storage engine info
db.serverStatus().storageEngine
```

---

## Memory Management

### WiredTiger Cache

WiredTiger uses an internal cache for optimal performance.

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Memory Architecture                             │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Total System Memory                                                │
│  ├─ Operating System                                                │
│  ├─ Other Applications                                              │
│  └─ MongoDB                                                         │
│      ├─ WiredTiger Internal Cache (configurable)                   │
│      │   └─ Default: 50% of (RAM - 1GB), or minimum 256MB          │
│      ├─ Connections & Operations                                    │
│      ├─ Aggregation Pipeline Memory                                │
│      └─ Index Build Memory                                          │
│                                                                     │
│  File System Cache (OS managed)                                     │
│  └─ Frequently accessed files                                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Cache Configuration

```yaml
# mongod.conf
storage:
  wiredTiger:
    engineConfig:
      # Cache size in GB
      cacheSizeGB: 4
```

```javascript
// Check cache statistics
db.serverStatus().wiredTiger.cache

// Key metrics:
{
  "bytes currently in the cache": 1073741824,
  "bytes read into cache": 524288000,
  "bytes written from cache": 262144000,
  "maximum bytes configured": 4294967296,
  "pages read into cache": 10000,
  "pages written from cache": 5000
}
```

### Memory Usage Guidelines

| System RAM | Recommended Cache Size |
|------------|----------------------|
| 4 GB | 1 GB |
| 8 GB | 3 GB |
| 16 GB | 7 GB |
| 32 GB | 15 GB |
| 64 GB | 30 GB |

### Cache Eviction

```
┌─────────────────────────────────────────────────────────────┐
│                   Cache Eviction Process                     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cache Full → Eviction Triggered                            │
│                                                             │
│  1. Application threads assist with eviction               │
│  2. Eviction threads run in background                     │
│  3. LRU (Least Recently Used) algorithm                    │
│  4. Dirty pages written to disk                            │
│  5. Clean pages discarded                                  │
│                                                             │
│  Eviction Thresholds:                                       │
│  • eviction_trigger: 95% (start eviction)                  │
│  • eviction_target: 80% (target after eviction)            │
│  • eviction_dirty_trigger: 5% dirty pages                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Organization

### Physical Data Layout

```
/data/db/                           # dbPath
├── WiredTiger                      # WiredTiger metadata
├── WiredTiger.lock                 # Lock file
├── WiredTiger.turtle                # WiredTiger bootstrap
├── WiredTiger.wt                   # WiredTiger metadata table
├── WiredTigerHS.wt                 # History store
├── _mdb_catalog.wt                 # MongoDB catalog
├── collection-0-*.wt              # Collection data files
├── collection-2-*.wt              
├── index-1-*.wt                   # Index files
├── index-3-*.wt
├── journal/                        # Journal directory
│   ├── WiredTigerLog.0000000001   # Journal files
│   └── WiredTigerPreplog.0000000001
├── diagnostic.data/               # Diagnostic data
├── mongod.lock                    # Process lock
└── storage.bson                   # Storage metadata
```

### Logical Data Hierarchy

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MongoDB Instance (mongod)                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │                        Database                              │   │
│  │  Name: "ecommerce"                                          │   │
│  │                                                              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │                    Collection                          │  │   │
│  │  │  Name: "products"                                      │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌────────────────────────────────────────────────┐   │  │   │
│  │  │  │                  Documents                      │   │  │   │
│  │  │  │                                                │   │  │   │
│  │  │  │  { _id: 1, name: "Laptop", price: 999 }       │   │  │   │
│  │  │  │  { _id: 2, name: "Phone", price: 599 }        │   │  │   │
│  │  │  │  { _id: 3, name: "Tablet", price: 399 }       │   │  │   │
│  │  │  │                                                │   │  │   │
│  │  │  └────────────────────────────────────────────────┘   │  │   │
│  │  │                                                        │  │   │
│  │  │  ┌────────────────────────────────────────────────┐   │  │   │
│  │  │  │                   Indexes                       │   │  │   │
│  │  │  │  • _id (default)                               │   │  │   │
│  │  │  │  • name_text                                   │   │  │   │
│  │  │  │  • price_1                                     │   │  │   │
│  │  │  └────────────────────────────────────────────────┘   │  │   │
│  │  │                                                        │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  │  ┌───────────────────────────────────────────────────────┐  │   │
│  │  │  Collection: "orders"                                  │  │   │
│  │  └───────────────────────────────────────────────────────┘  │   │
│  │                                                              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database: "admin" (System)                                  │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database: "local" (Replication)                             │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### System Databases

| Database | Purpose |
|----------|---------|
| **admin** | Administrative operations, user authentication |
| **local** | Replica set oplog, instance-specific data |
| **config** | Sharding metadata (sharded clusters only) |

```javascript
// View system databases
show dbs

// System collections in admin database
use admin
show collections
// system.users - User accounts
// system.roles - Custom roles
// system.version - Version info

// Local database (replica sets)
use local
show collections
// oplog.rs - Replication oplog
// startup_log - Server startup history
```

---

## Query Engine

### Query Processing Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Query Processing Pipeline                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Query Parsing                                                   │
│     └─ Parse query into internal representation                    │
│                                                                     │
│  2. Query Analysis                                                  │
│     └─ Analyze query structure and predicates                      │
│                                                                     │
│  3. Query Planning                                                  │
│     ├─ Identify candidate indexes                                  │
│     ├─ Generate execution plans                                    │
│     └─ Choose optimal plan (cost-based)                            │
│                                                                     │
│  4. Plan Caching                                                    │
│     └─ Cache winning plan for similar queries                      │
│                                                                     │
│  5. Query Execution                                                 │
│     ├─ Execute chosen plan                                         │
│     ├─ Fetch documents from storage                                │
│     └─ Apply projections and transformations                       │
│                                                                     │
│  6. Result Return                                                   │
│     └─ Return results to client via cursor                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Query Optimizer

```javascript
// View query execution plan
db.products.find({ category: "electronics", price: { $lt: 500 } })
  .explain("executionStats")

// Sample output
{
  "queryPlanner": {
    "plannerVersion": 1,
    "winningPlan": {
      "stage": "FETCH",
      "inputStage": {
        "stage": "IXSCAN",
        "keyPattern": { "category": 1, "price": 1 },
        "indexName": "category_1_price_1"
      }
    },
    "rejectedPlans": [
      // Other considered plans
    ]
  },
  "executionStats": {
    "executionSuccess": true,
    "nReturned": 150,
    "executionTimeMillis": 5,
    "totalKeysExamined": 150,
    "totalDocsExamined": 150
  }
}
```

### Query Plan Cache

```javascript
// View plan cache
db.products.aggregate([{ $planCacheStats: {} }])

// Clear plan cache for a collection
db.products.getPlanCache().clear()

// List cached plans
db.products.getPlanCache().list()
```

---

## Concurrency Control

### Document-Level Locking

```
┌─────────────────────────────────────────────────────────────────────┐
│                   WiredTiger Concurrency Model                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Granularity Levels:                                                │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Global Level                                                │   │
│  │  └─ Intent locks for administrative operations              │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                                          │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Database Level                                              │   │
│  │  └─ Intent locks (IS/IX) for database operations            │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                                          │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Collection Level                                            │   │
│  │  └─ Intent locks (IS/IX) for collection operations          │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                          │                                          │
│                          ▼                                          │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Document Level (WiredTiger)                                 │   │
│  │  └─ Optimistic concurrency control                          │   │
│  │  └─ Document-level locking for writes                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Lock Types

| Lock Type | Symbol | Description |
|-----------|--------|-------------|
| Shared | S | Read operations |
| Exclusive | X | Write operations |
| Intent Shared | IS | Intent to read at lower level |
| Intent Exclusive | IX | Intent to write at lower level |

### Checking Lock Status

```javascript
// Current operations with locks
db.currentOp({ "locks": { $exists: true } })

// Server status locks
db.serverStatus().locks

// Output example:
{
  "Global": {
    "acquireCount": {
      "r": 100000,  // Shared (read) locks acquired
      "w": 50000,   // Exclusive (write) locks acquired
      "W": 100      // Global exclusive
    }
  },
  "Database": {
    "acquireCount": { "r": 100000, "w": 50000 }
  },
  "Collection": {
    "acquireCount": { "r": 100000, "w": 50000 }
  }
}
```

### MVCC (Multi-Version Concurrency Control)

```
┌─────────────────────────────────────────────────────────────────────┐
│                            MVCC in WiredTiger                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Snapshot Isolation:                                                │
│  • Each transaction sees consistent snapshot of data                │
│  • Readers don't block writers                                      │
│  • Writers don't block readers                                      │
│                                                                     │
│  Timeline:                                                          │
│                                                                     │
│  T1: ──────[Read Snapshot]──────────────────────────────────        │
│              │                                                      │
│  T2: ────────────[Write]────────────────────────────────────        │
│                    │                                                │
│  T3: ─────────────────────[Read Snapshot]───────────────────        │
│                                │                                    │
│                                                                     │
│  • T1 sees data before T2's write                                  │
│  • T3 sees T2's write (committed before T3 started)                │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Journaling and Durability

### Write-Ahead Logging (WAL)

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Journaling Process                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Write Operation Received                                        │
│     │                                                               │
│     ▼                                                               │
│  2. Write to Journal (WAL)                                          │
│     │  └─ Write operation logged immediately                       │
│     │  └─ Journal sync interval: 100ms (default)                   │
│     ▼                                                               │
│  3. Acknowledge to Client (with j:true)                            │
│     │                                                               │
│     ▼                                                               │
│  4. Write to Cache                                                  │
│     │  └─ Data written to WiredTiger cache                         │
│     │                                                               │
│     ▼                                                               │
│  5. Checkpoint (Background)                                         │
│        └─ Dirty pages flushed to data files                        │
│        └─ Every 60 seconds or 2GB journal data                     │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Journal Configuration

```yaml
# mongod.conf
storage:
  journal:
    enabled: true
    commitIntervalMs: 100  # Journal sync interval
```

### Write Concern and Durability

```javascript
// Write concern levels
db.orders.insertOne(
  { item: "abc", qty: 100 },
  {
    writeConcern: {
      w: 1,           // Acknowledged by primary
      j: true,        // Written to journal
      wtimeout: 5000  // Timeout in milliseconds
    }
  }
)

// Write concern options:
// w: 0 - No acknowledgment (fire and forget)
// w: 1 - Primary acknowledgment (default)
// w: "majority" - Majority of replica set members
// j: true - Journal committed
```

### Checkpoint Process

```javascript
// Force a checkpoint
db.adminCommand({ fsync: 1 })

// Check last checkpoint time
db.serverStatus().wiredTiger.connection
// "last checkpoint time" field

// Checkpoint configuration
// Default: every 60 seconds or 2GB journal data
```

### Recovery Process

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Crash Recovery Process                          │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. Server Crash / Unclean Shutdown                                 │
│                                                                     │
│  2. Server Restart                                                  │
│     │                                                               │
│     ▼                                                               │
│  3. Load Last Checkpoint                                            │
│     │  └─ Data files reflect state at last checkpoint              │
│     │                                                               │
│     ▼                                                               │
│  4. Replay Journal Entries                                          │
│     │  └─ Apply all operations since last checkpoint               │
│     │  └─ Brings data to consistent state                          │
│     │                                                               │
│     ▼                                                               │
│  5. Recovery Complete                                               │
│     │  └─ Server ready to accept connections                       │
│     │                                                               │
│                                                                     │
│  Recovery Time ≈ Time to replay operations since checkpoint         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Network Layer

### Wire Protocol

MongoDB uses a binary protocol over TCP/IP for client-server communication.

```
┌─────────────────────────────────────────────────────────────────────┐
│                     MongoDB Wire Protocol                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Message Structure:                                                 │
│  ┌────────────────────────────────────────────────────────────┐    │
│  │ Message Header (16 bytes)                                   │    │
│  │ ├─ messageLength (4 bytes)                                 │    │
│  │ ├─ requestID (4 bytes)                                     │    │
│  │ ├─ responseTo (4 bytes)                                    │    │
│  │ └─ opCode (4 bytes)                                        │    │
│  ├────────────────────────────────────────────────────────────┤    │
│  │ Message Body (variable)                                     │    │
│  │ └─ BSON document(s)                                        │    │
│  └────────────────────────────────────────────────────────────┘    │
│                                                                     │
│  Op Codes:                                                          │
│  • OP_MSG (2013) - Modern message format                           │
│  • OP_QUERY (2004) - Query (deprecated)                            │
│  • OP_REPLY (1) - Reply to query                                   │
│  • OP_UPDATE (2001) - Update (deprecated)                          │
│  • OP_INSERT (2002) - Insert (deprecated)                          │
│  • OP_DELETE (2006) - Delete (deprecated)                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Connection Management

```javascript
// Server connection statistics
db.serverStatus().connections

// Output:
{
  "current": 50,        // Current active connections
  "available": 51150,   // Available connections
  "totalCreated": 500,  // Total connections created
  "active": 10          // Currently executing operations
}

// Connection pool settings (driver-side)
// Each driver has its own connection pool configuration
```

### Network Configuration

```yaml
# mongod.conf
net:
  port: 27017
  bindIp: 127.0.0.1,192.168.1.100
  bindIpAll: false
  maxIncomingConnections: 65536
  
  # TLS/SSL
  tls:
    mode: requireTLS
    certificateKeyFile: /path/to/server.pem
    CAFile: /path/to/ca.pem

  # Compression
  compression:
    compressors: snappy,zstd,zlib
```

### Connection States

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Connection Lifecycle                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    Authentication    ┌──────────────────┐        │
│  │   Connect    │ ──────────────────── │  Authenticated   │        │
│  └──────────────┘                      └──────────────────┘        │
│                                                │                    │
│                                                ▼                    │
│                                        ┌──────────────────┐        │
│                                        │     Active       │        │
│                                        │  (Executing ops) │        │
│                                        └──────────────────┘        │
│                                                │                    │
│                              ┌─────────────────┴─────────────────┐ │
│                              ▼                                   ▼ │
│                   ┌──────────────────┐              ┌────────────┐ │
│                   │      Idle        │              │  Timeout/  │ │
│                   │  (Waiting in pool)│             │  Close     │ │
│                   └──────────────────┘              └────────────┘ │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Summary

### Key Architectural Components

| Component | Purpose |
|-----------|---------|
| **mongod** | Core database server process |
| **mongos** | Sharding query router |
| **WiredTiger** | Default storage engine |
| **Journal** | Write-ahead log for durability |
| **Query Engine** | Query planning and execution |

### Performance Features

1. **Document-level locking** for high concurrency
2. **In-memory caching** with configurable size
3. **Data compression** to reduce storage
4. **Query optimization** with plan caching
5. **MVCC** for non-blocking reads

### Durability Guarantees

1. **Write-Ahead Logging** for crash recovery
2. **Configurable write concern** for consistency
3. **Checkpoints** for data persistence
4. **Replica set journaling** for distributed durability

### What's Next?

In the next chapter, we'll explore Documents and BSON in detail, understanding how MongoDB stores and represents data.

---

## Practice Questions

1. What is the role of WiredTiger in MongoDB?
2. Explain the difference between mongod and mongos.
3. How does MongoDB achieve document-level concurrency?
4. What is the purpose of the journal in MongoDB?
5. Describe the query processing pipeline.
6. How does WiredTiger cache management work?
7. What are checkpoints and why are they important?
8. Explain MVCC and its benefits for read operations.

---

## Hands-On Exercises

### Exercise 1: Explore Server Status

```javascript
// Connect to MongoDB and run:
db.serverStatus()

// Examine the following sections:
// - connections
// - storageEngine
// - wiredTiger.cache
// - locks
```

### Exercise 2: Query Explain Plans

```javascript
// Create a collection with sample data
for (let i = 0; i < 10000; i++) {
  db.test.insertOne({
    x: Math.random() * 100,
    y: Math.random() * 100
  });
}

// Create an index
db.test.createIndex({ x: 1 });

// Compare explain plans
db.test.find({ x: { $gt: 50 } }).explain("executionStats")
db.test.find({ y: { $gt: 50 } }).explain("executionStats")
```

### Exercise 3: Storage Statistics

```javascript
// Examine storage details
db.collection.stats()

// Check compression ratio
db.runCommand({ collStats: "collection" }).wiredTiger
```

---

[← Previous: Installation and Setup](02-installation-and-setup.md) | [Next: Documents and BSON →](04-documents-and-bson.md)
