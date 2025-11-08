# PostgreSQL Architecture

## Overview

PostgreSQL uses a client-server architecture with a process-based model. Understanding its architecture is crucial for optimization, troubleshooting, and administration.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Applications                   │
│    (psql, pgAdmin, Application Drivers, etc.)           │
└────────────────────┬────────────────────────────────────┘
                     │ TCP/IP or Unix Socket
                     ▼
┌─────────────────────────────────────────────────────────┐
│              PostgreSQL Server Process                   │
│  ┌─────────────────────────────────────────────────┐   │
│  │            Postmaster (Main Process)             │   │
│  └───────────────────┬─────────────────────────────┘   │
│                      │                                   │
│         ┌────────────┼────────────┐                     │
│         ▼            ▼            ▼                     │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐              │
│  │ Backend  │ │ Backend  │ │ Backend  │  ...         │
│  │ Process  │ │ Process  │ │ Process  │              │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘              │
│       │            │            │                       │
│  ┌────┴────────────┴────────────┴─────────────────┐   │
│  │          Shared Memory Area                     │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │     Shared Buffer Pool                   │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │     WAL Buffers                          │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  │  ┌─────────────────────────────────────────┐   │   │
│  │  │     Lock Tables / Semaphores             │   │   │
│  │  └─────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                    Storage Layer                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐             │
│  │   Data   │  │   WAL    │  │   CLOG   │             │
│  │   Files  │  │   Files  │  │   Files  │             │
│  └──────────┘  └──────────┘  └──────────┘             │
└─────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Postmaster (Main Server Process)

The **postmaster** is the first process started when PostgreSQL runs.

**Responsibilities**:
- Listen for incoming client connections
- Authenticate client connections
- Fork backend processes for each connection
- Manage background worker processes
- Monitor and restart failed processes

**Process Information**:
```bash
# View postmaster process
ps aux | grep postmaster
# Or
ps aux | grep postgres | grep -v grep
```

**Key Points**:
- One postmaster per PostgreSQL instance
- Runs with elevated privileges
- Spawns child processes for actual work
- Shutdown requires stopping this process

### 2. Backend Processes

Each client connection gets its own dedicated **backend process**.

**Characteristics**:
- One backend per client connection
- Independent memory space
- Communicates with client via TCP/IP or Unix socket
- Access shared memory for buffers and locks
- Executes SQL queries

**View Active Backends**:
```sql
-- View all backend processes
SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query,
    backend_start
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- Count active connections
SELECT COUNT(*) FROM pg_stat_activity;
```

**Backend Process Lifecycle**:
```
Client connects → Postmaster authenticates → Fork backend process →
Execute queries → Client disconnects → Backend terminates
```

### 3. Background Processes

PostgreSQL runs several background worker processes:

#### a) Background Writer (bgwriter)
- **Purpose**: Write dirty buffers from shared memory to disk
- **Goal**: Smooth out checkpoint I/O spikes
- **Configuration**:
  ```conf
  bgwriter_delay = 200ms
  bgwriter_lru_maxpages = 100
  bgwriter_lru_multiplier = 2.0
  ```

#### b) Checkpointer
- **Purpose**: Perform periodic checkpoints
- **Function**: Ensure all dirty pages written to disk
- **Configuration**:
  ```conf
  checkpoint_timeout = 5min
  checkpoint_completion_target = 0.9
  max_wal_size = 1GB
  ```

#### c) WAL Writer
- **Purpose**: Write Write-Ahead Log records to disk
- **Ensures**: Transaction durability
- **Configuration**:
  ```conf
  wal_writer_delay = 200ms
  wal_writer_flush_after = 1MB
  ```

#### d) Autovacuum Launcher & Workers
- **Purpose**: Automatic table maintenance
- **Tasks**: 
  - Reclaim storage from deleted rows
  - Update statistics for query planner
  - Prevent transaction ID wraparound
- **Configuration**:
  ```conf
  autovacuum = on
  autovacuum_max_workers = 3
  autovacuum_naptime = 1min
  ```

#### e) Statistics Collector
- **Purpose**: Collect database activity statistics
- **Data**: Query execution, table access, index usage
- **Views**: `pg_stat_*` system views

#### f) Logical Replication Workers
- **Purpose**: Handle logical replication
- **Components**:
  - Logical replication launcher
  - Logical replication workers

#### g) WAL Receiver/Sender (Replication)
- **WAL Sender**: Stream WAL to replicas
- **WAL Receiver**: Receive WAL on replicas
- **Enables**: Streaming replication

**View Background Processes**:
```sql
-- View all background processes
SELECT 
    pid,
    backend_type,
    backend_start,
    state
FROM pg_stat_activity
WHERE backend_type != 'client backend';

-- View autovacuum workers
SELECT * FROM pg_stat_progress_vacuum;
```

```bash
# View all PostgreSQL processes (Linux)
ps aux | grep postgres

# View process tree
pstree -p $(pgrep -f "postgres.*postmaster")
```

## Memory Architecture

### 1. Shared Memory

Memory shared between all PostgreSQL processes.

#### a) Shared Buffer Pool

**Purpose**: Cache database pages in memory

**Configuration**:
```conf
shared_buffers = 256MB    # 25% of RAM (typical)
```

**How It Works**:
1. Backend requests a page
2. Check if page in shared buffers
3. If found (hit), return immediately
4. If not (miss), read from disk and cache

**Monitor Buffer Cache**:
```sql
-- Buffer cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 
    AS cache_hit_ratio
FROM pg_statio_user_tables;

-- View buffer usage
CREATE EXTENSION pg_buffercache;

SELECT 
    c.relname,
    count(*) AS buffers,
    pg_size_pretty(count(*) * 8192) AS size
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
GROUP BY c.relname
ORDER BY count(*) DESC
LIMIT 10;
```

#### b) WAL Buffers

**Purpose**: Buffer Write-Ahead Log records before writing to disk

**Configuration**:
```conf
wal_buffers = 16MB    # Auto-sized based on shared_buffers
```

**Process**:
1. Transaction generates WAL records
2. Records written to WAL buffers
3. WAL writer flushes to disk
4. Commit returns to client

#### c) Lock Management

**Purpose**: Manage locks for concurrency control

**Types**:
- Table-level locks
- Row-level locks
- Advisory locks

**View Locks**:
```sql
-- View current locks
SELECT 
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE NOT granted;

-- View blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;
```

### 2. Process-Local Memory

Each backend process has its own local memory.

#### a) work_mem

**Purpose**: Memory for sorting and hash operations

**Configuration**:
```conf
work_mem = 4MB    # Per operation, not per query!
```

**Used For**:
- ORDER BY operations
- Hash joins
- Hash-based aggregates
- Merge joins

**Example**:
```sql
-- Set for current session
SET work_mem = '64MB';

-- Query using work_mem
SELECT * FROM large_table ORDER BY column LIMIT 100;
```

**Warning**: A complex query can use multiple work_mem allocations!

#### b) maintenance_work_mem

**Purpose**: Memory for maintenance operations

**Configuration**:
```conf
maintenance_work_mem = 64MB
```

**Used For**:
- VACUUM
- CREATE INDEX
- ALTER TABLE
- Foreign key checks

#### c) temp_buffers

**Purpose**: Buffer temporary tables

**Configuration**:
```conf
temp_buffers = 8MB
```

## Storage Architecture

### 1. Data Directory Structure

```
$PGDATA/
├── base/                  # Database files
│   ├── 1/                 # template1
│   ├── 13000/             # template0
│   └── 16384/             # User database
├── global/                # Cluster-wide tables
│   ├── pg_database
│   └── pg_control
├── pg_wal/                # Write-Ahead Log files
│   ├── 000000010000000000000001
│   └── ...
├── pg_xact/               # Transaction commit status
├── pg_subtrans/           # Subtransaction status
├── pg_multixact/          # Multixact status
├── pg_notify/             # LISTEN/NOTIFY status
├── pg_serial/             # Serializable transaction
├── pg_snapshots/          # Exported snapshots
├── pg_stat/               # Statistics files
├── pg_stat_tmp/           # Temporary statistics
├── pg_tblspc/             # Tablespace symbolic links
├── pg_twophase/           # Two-phase commit
├── pg_logical/            # Logical replication
│   ├── mappings/
│   ├── snapshots/
│   └── replorigin_checkpoint
├── postgresql.conf        # Main configuration
├── pg_hba.conf           # Authentication config
├── pg_ident.conf         # User mapping config
├── postmaster.opts       # Command-line options
├── postmaster.pid        # PID file
└── postgresql.auto.conf  # Auto-generated config
```

**View Data Directory**:
```sql
SHOW data_directory;
```

### 2. Database Files

Each database has its own subdirectory in `base/`.

**File Naming**:
- Files named by OID (Object ID)
- Large files split into 1GB segments
- Example: `12345`, `12345.1`, `12345.2`

**View Database OIDs**:
```sql
SELECT oid, datname FROM pg_database;
```

**Table Files**:
```sql
-- Find table file
SELECT pg_relation_filepath('table_name');

-- Example output: base/16384/16385
```

**File Components**:
- Main file: Table data
- `_fsm`: Free Space Map
- `_vm`: Visibility Map
- `_init`: Initialization fork (for unlogged tables)

### 3. Tablespaces

**Purpose**: Store database objects in different locations

**Create Tablespace**:
```sql
-- Create directory first
-- mkdir /mnt/ssd/pg_tablespace

CREATE TABLESPACE fast_storage 
    LOCATION '/mnt/ssd/pg_tablespace';

-- Create table in tablespace
CREATE TABLE fast_table (
    id SERIAL PRIMARY KEY,
    data TEXT
) TABLESPACE fast_storage;

-- Move existing table
ALTER TABLE existing_table SET TABLESPACE fast_storage;

-- View tablespaces
SELECT * FROM pg_tablespace;
```

**Use Cases**:
- Fast storage (SSD) for hot tables
- Slow storage (HDD) for archives
- Separate storage for indexes
- Balance I/O across disks

## Write-Ahead Logging (WAL)

### WAL Architecture

**Purpose**: Ensure data durability and enable recovery

**How It Works**:
```
1. Transaction makes changes
2. Changes written to WAL buffers
3. WAL records flushed to disk
4. COMMIT returns success
5. Data pages written to disk later (lazy)
```

**Benefits**:
- **Durability**: Changes survive crashes
- **Performance**: Sequential writes faster than random
- **Recovery**: Replay WAL after crash
- **Replication**: Ship WAL to replicas

### WAL Configuration

```conf
# WAL Level
wal_level = replica              # minimal, replica, or logical

# WAL Buffers
wal_buffers = 16MB              # -1 for auto

# Checkpoints
checkpoint_timeout = 5min
checkpoint_completion_target = 0.9
max_wal_size = 1GB
min_wal_size = 80MB

# WAL Archiving
archive_mode = on
archive_command = 'cp %p /path/to/archive/%f'

# Commit Behavior
synchronous_commit = on         # on, off, remote_apply, local, remote_write
```

### WAL Segments

**Characteristics**:
- Fixed size: 16MB (default)
- Numbered sequentially
- Recycled when no longer needed

**View WAL Files**:
```bash
# List WAL files
ls -lh $PGDATA/pg_wal/

# Current WAL location
psql -c "SELECT pg_current_wal_lsn();"
```

```sql
-- WAL statistics
SELECT * FROM pg_stat_wal;

-- Switch WAL file (forces new segment)
SELECT pg_switch_wal();
```

## Process Flow: Query Execution

### Step-by-Step Query Execution

```
1. Client sends query
   ↓
2. Backend receives query
   ↓
3. Parser: Parse SQL, build parse tree
   ↓
4. Analyzer/Rewriter: Transform query, check semantics
   ↓
5. Planner: Generate optimal execution plan
   ↓
6. Executor: Execute plan
   ├─ Check shared buffers
   ├─ Read from disk if needed
   ├─ Apply WHERE filters
   ├─ Perform joins
   └─ Return results
   ↓
7. Send results to client
```

### Example: SELECT Query

```sql
-- Query
SELECT u.name, o.total 
FROM users u 
JOIN orders o ON u.id = o.user_id 
WHERE o.total > 100;

-- Internal Steps:
-- 1. Parse: Validate syntax
-- 2. Analyze: Resolve table/column names
-- 3. Rewrite: Apply views, rules
-- 4. Plan: Choose join method, access paths
-- 5. Execute: 
--    - Scan users table
--    - Scan orders table with filter
--    - Perform join
--    - Return results
```

**View Query Plan**:
```sql
EXPLAIN ANALYZE
SELECT u.name, o.total 
FROM users u 
JOIN orders o ON u.id = o.user_id 
WHERE o.total > 100;
```

### Example: INSERT Query

```sql
-- Query
INSERT INTO users (name, email) VALUES ('John', 'john@example.com');

-- Internal Steps:
-- 1. Parse and validate
-- 2. Check constraints
-- 3. Generate WAL records
-- 4. Write to WAL buffers
-- 5. Acquire locks
-- 6. Update data in shared buffers (or disk)
-- 7. Update indexes
-- 8. Flush WAL to disk (on commit)
-- 9. Release locks
-- 10. Return success
```

## MVCC (Multi-Version Concurrency Control)

### How MVCC Works

**Concept**: Each transaction sees a consistent snapshot of data

**Implementation**:
- Each row has hidden columns: `xmin` (created by) and `xmax` (deleted by)
- Transactions have transaction IDs (XID)
- Visibility rules determine which version to see

**Example**:
```
Time  Transaction 1           Transaction 2
----  ---------------------   ---------------------
T1    BEGIN;                  
T2    SELECT * FROM users;    
      (sees version 1)
T3                            BEGIN;
T4                            UPDATE users SET name='Jane';
T5                            COMMIT;
T6    SELECT * FROM users;    
      (still sees version 1)
T7    COMMIT;
```

**View Row Versions**:
```sql
-- Enable showing hidden columns
SELECT 
    xmin,
    xmax,
    cmin,
    cmax,
    ctid,
    *
FROM users;
```

### Benefits of MVCC

1. **No read locks**: Readers don't block writers
2. **No write locks on reads**: Writers don't block readers
3. **Consistent reads**: Transactions see consistent data
4. **High concurrency**: Multiple transactions proceed independently

### Drawbacks

1. **Dead tuples**: Old versions accumulate
2. **Bloat**: Tables and indexes grow
3. **VACUUM needed**: Regular maintenance required

## Transaction Architecture

### Transaction States

```
┌─────────┐
│  BEGIN  │
└────┬────┘
     │
     ▼
┌─────────────┐
│  IN PROGRESS│───┐
└──────┬──────┘   │
       │          │ ROLLBACK
       │          │
       ▼          ▼
   ┌────────┐  ┌──────────┐
   │ COMMIT │  │ ABORTED  │
   └────┬───┘  └──────────┘
        │
        ▼
   ┌──────────┐
   │COMMITTED │
   └──────────┘
```

### Transaction ID (XID)

**Characteristics**:
- 32-bit integer
- Wraps around at ~2 billion
- Requires VACUUM to prevent wraparound

**View Transaction IDs**:
```sql
-- Current transaction ID
SELECT txid_current();

-- Transaction snapshot
SELECT txid_current_snapshot();

-- Check wraparound progress
SELECT 
    datname,
    age(datfrozenxid) AS xid_age,
    2147483647 - age(datfrozenxid) AS xids_until_wraparound
FROM pg_database
ORDER BY age(datfrozenxid) DESC;
```

## System Catalogs

PostgreSQL stores metadata in system catalogs.

**Key Catalogs**:
```sql
-- Databases
SELECT * FROM pg_database;

-- Tables
SELECT * FROM pg_tables;

-- Columns
SELECT * FROM pg_attribute;

-- Indexes
SELECT * FROM pg_indexes;

-- Views
SELECT * FROM pg_views;

-- Functions
SELECT * FROM pg_proc;

-- Users/Roles
SELECT * FROM pg_roles;

-- Tablespaces
SELECT * FROM pg_tablespace;

-- Extensions
SELECT * FROM pg_extension;
```

## Monitoring Architecture

```sql
-- Active queries
SELECT * FROM pg_stat_activity;

-- Database statistics
SELECT * FROM pg_stat_database;

-- Table statistics
SELECT * FROM pg_stat_user_tables;

-- Index statistics
SELECT * FROM pg_stat_user_indexes;

-- I/O statistics
SELECT * FROM pg_statio_user_tables;

-- Background writer stats
SELECT * FROM pg_stat_bgwriter;

-- Replication stats
SELECT * FROM pg_stat_replication;
```

## Summary

**Key Architectural Concepts**:
1. **Process Model**: Postmaster + Backend processes + Background workers
2. **Memory**: Shared buffers + Process-local memory
3. **Storage**: Data files + WAL + System catalogs
4. **MVCC**: Multiple versions for concurrency
5. **WAL**: Write-ahead logging for durability
6. **Background Workers**: Automated maintenance tasks

**Next Topics**:
- [Data Types](04-data-types.md)
- [Basic SQL Operations](05-basic-sql-operations.md)
- [Transactions and ACID](16-transactions-and-acid.md)

Understanding PostgreSQL's architecture helps you:
- Optimize performance
- Troubleshoot issues
- Configure properly
- Plan capacity
- Design better applications
