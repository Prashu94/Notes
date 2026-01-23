# PostgreSQL Internals

## Overview

Understanding PostgreSQL internals helps database administrators and developers make better decisions about performance tuning, troubleshooting, and system design. This guide explores the internal architecture, components, and mechanisms that power PostgreSQL.

## Table of Contents
- [Process Architecture](#process-architecture)
- [Memory Architecture](#memory-architecture)
- [Storage Architecture](#storage-architecture)
- [Buffer Management](#buffer-management)
- [Write-Ahead Logging (WAL)](#write-ahead-logging-wal)
- [Query Processing](#query-processing)
- [Executor Engine](#executor-engine)
- [System Catalogs](#system-catalogs)
- [Visibility and MVCC](#visibility-and-mvcc)
- [Lock Management](#lock-management)
- [Background Processes](#background-processes)
- [Checkpoint Mechanism](#checkpoint-mechanism)
- [Statistics Collector](#statistics-collector)

---

## Process Architecture

### Postmaster Process

The postmaster is the main PostgreSQL daemon that manages all server operations:

```bash
# View PostgreSQL processes
ps aux | grep postgres

# Typical output:
# postgres: postmaster
# postgres: checkpointer
# postgres: background writer
# postgres: walwriter
# postgres: autovacuum launcher
# postgres: stats collector
# postgres: logical replication launcher
```

### Process Types

```sql
-- View backend processes
SELECT pid, usename, application_name, state, query
FROM pg_stat_activity
WHERE backend_type = 'client backend';

-- View all processes
SELECT pid, backend_type, state
FROM pg_stat_activity;
```

### Backend Process Lifecycle

```
Client Connection Request
         │
         ▼
    ┌─────────┐
    │Postmaster│
    └────┬────┘
         │ fork()
         ▼
    ┌─────────┐
    │ Backend │──► Handles client queries
    └─────────┘
         │
         ▼ (on disconnect)
    Process exits
```

### Process Communication

```sql
-- Shared memory for inter-process communication
-- View shared memory usage
SHOW shared_buffers;
SHOW work_mem;

-- IPC mechanisms:
-- 1. Shared memory segments
-- 2. Semaphores for synchronization
-- 3. Signals for notifications
-- 4. Lightweight locks (LWLocks)
```

---

## Memory Architecture

### Shared Memory

```
┌─────────────────────────────────────────┐
│           Shared Memory                  │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────┐  │
│  │  Shared Buffers │  │ WAL Buffers  │  │
│  │  (data cache)   │  │              │  │
│  └─────────────────┘  └──────────────┘  │
├─────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────┐  │
│  │   Lock Tables   │  │  Proc Array  │  │
│  │                 │  │              │  │
│  └─────────────────┘  └──────────────┘  │
├─────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐│
│  │       CLOG (Commit Log)             ││
│  └─────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

### Shared Buffers

```sql
-- Configure shared buffers (typically 25% of RAM)
-- In postgresql.conf:
-- shared_buffers = 4GB

-- Check buffer usage
SELECT 
    c.relname,
    pg_size_pretty(count(*) * 8192) AS buffer_size,
    round(100.0 * count(*) / (SELECT setting::int FROM pg_settings 
        WHERE name = 'shared_buffers'), 2) AS buffer_percent
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
WHERE c.relname NOT LIKE 'pg_%'
GROUP BY c.relname
ORDER BY count(*) DESC
LIMIT 20;

-- Buffer states
SELECT 
    CASE 
        WHEN isdirty THEN 'dirty'
        ELSE 'clean'
    END AS buffer_state,
    count(*) AS pages
FROM pg_buffercache
GROUP BY isdirty;
```

### Local Memory

```sql
-- Per-backend memory allocations
SHOW work_mem;           -- Sort/hash operations
SHOW maintenance_work_mem; -- VACUUM, CREATE INDEX
SHOW temp_buffers;       -- Temporary tables

-- Memory context structure (conceptual)
-- TopMemoryContext
--   ├── MessageContext
--   ├── TopTransactionContext
--   │     └── CurTransactionContext
--   ├── QueryContext
--   │     ├── ExecutorState
--   │     └── ExprContext
--   └── CacheMemoryContext
```

### Memory Allocation

```sql
-- PostgreSQL uses memory contexts for efficient allocation
-- Memory is organized in hierarchical contexts
-- Freeing a context frees all child allocations

-- Check memory usage per backend (requires pg_stat_statements)
SELECT 
    pid,
    usename,
    pg_size_pretty(
        (SELECT setting::bigint * 1024 FROM pg_settings WHERE name = 'work_mem')
    ) AS work_mem_setting,
    state,
    query
FROM pg_stat_activity
WHERE state = 'active';
```

---

## Storage Architecture

### Data Directory Structure

```bash
$PGDATA/
├── base/                    # Database files
│   ├── 1/                   # template1 database (OID)
│   ├── 12345/               # User database (OID)
│   │   ├── 16384            # Table file (relfilenode)
│   │   ├── 16384_fsm        # Free space map
│   │   ├── 16384_vm         # Visibility map
│   │   └── PG_VERSION       # Database version
│   └── 12406/               # Another database
├── global/                  # Cluster-wide tables
│   ├── pg_control           # Control file
│   └── pg_database          # Database list
├── pg_wal/                  # WAL files (write-ahead log)
│   ├── 000000010000000000000001
│   └── archive_status/
├── pg_xact/                 # Transaction commit status (CLOG)
├── pg_multixact/            # Multitransaction status
├── pg_subtrans/             # Subtransaction data
├── pg_twophase/             # Two-phase commit data
├── pg_tblspc/               # Tablespace symlinks
├── pg_stat/                 # Statistics files
├── pg_stat_tmp/             # Temporary stats
├── pg_snapshots/            # Exported snapshots
├── pg_commit_ts/            # Commit timestamps
├── pg_replslot/             # Replication slots
├── pg_logical/              # Logical replication data
├── postgresql.conf          # Main configuration
├── pg_hba.conf              # Authentication config
├── pg_ident.conf            # User mapping
├── postmaster.pid           # PID file
└── postmaster.opts          # Command line options
```

### Page Structure (8KB default)

```
┌──────────────────────────────────────────┐
│           Page Header (24 bytes)          │
│  - LSN (8 bytes)                         │
│  - Checksum (2 bytes)                    │
│  - Flags (2 bytes)                       │
│  - Lower pointer (2 bytes)               │
│  - Upper pointer (2 bytes)               │
│  - Special space (2 bytes)               │
│  - Page size + version (2 bytes)         │
│  - Prune XID (4 bytes)                   │
├──────────────────────────────────────────┤
│         Line Pointers (Item IDs)          │
│  [LP1][LP2][LP3]...  ──────────────────► │
├──────────────────────────────────────────┤
│              Free Space                   │
│                                          │
│                                          │
├──────────────────────────────────────────┤
│   ◄──────────────────  Tuples (Items)    │
│         [Tuple 3][Tuple 2][Tuple 1]      │
├──────────────────────────────────────────┤
│            Special Space                  │
│   (Used by indexes, e.g., B-tree data)   │
└──────────────────────────────────────────┘
```

### Tuple Structure (Heap Tuple Header)

```sql
-- HeapTupleHeaderData structure (23 bytes minimum)
-- t_xmin: Transaction ID that inserted this tuple
-- t_xmax: Transaction ID that deleted/updated this tuple  
-- t_cid: Command ID within transaction
-- t_ctid: Current tuple ID (self-referencing or points to updated version)
-- t_infomask: Various flags
-- t_infomask2: More flags, including number of attributes
-- t_hoff: Offset to user data

-- View tuple header information using pageinspect extension
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- Examine raw page data
SELECT lp, t_xmin, t_xmax, t_ctid, t_infomask::bit(16)
FROM heap_page_items(get_raw_page('your_table', 0));
```

### TOAST (The Oversized-Attribute Storage Technique)

```sql
-- TOAST handles large values (> ~2KB)
-- Strategies:
-- PLAIN: No compression, no out-of-line storage
-- EXTENDED: Compress, then out-of-line (default for compressible)
-- EXTERNAL: Out-of-line, no compression
-- MAIN: Compress first, out-of-line as last resort

-- Check TOAST table
SELECT 
    c.relname AS table_name,
    t.relname AS toast_table,
    pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
    pg_size_pretty(pg_relation_size(t.oid)) AS toast_size
FROM pg_class c
JOIN pg_class t ON c.reltoastrelid = t.oid
WHERE c.relkind = 'r';

-- Change TOAST strategy
ALTER TABLE large_data ALTER COLUMN content SET STORAGE EXTERNAL;
```

---

## Buffer Management

### Buffer Pool

```sql
-- Install pg_buffercache extension
CREATE EXTENSION pg_buffercache;

-- View buffer cache contents
SELECT 
    c.relname,
    count(*) AS buffers,
    pg_size_pretty(count(*) * 8192) AS size,
    round(100.0 * count(*) * 8192 / pg_relation_size(c.oid), 2) AS percent_cached
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
    AND b.reldatabase IN (0, (SELECT oid FROM pg_database WHERE datname = current_database()))
WHERE c.relname NOT LIKE 'pg_%'
GROUP BY c.relname, c.oid
ORDER BY buffers DESC
LIMIT 10;

-- Buffer usage count (frequency of access)
SELECT 
    usagecount,
    count(*) AS buffers,
    round(100.0 * count(*) / (SELECT count(*) FROM pg_buffercache), 2) AS percent
FROM pg_buffercache
GROUP BY usagecount
ORDER BY usagecount;
```

### Clock Sweep Algorithm

```
PostgreSQL uses a clock-sweep algorithm for buffer replacement:

1. Each buffer has a usage counter (0-5)
2. When accessed, counter increments (max 5)  
3. When needing a free buffer:
   - Sweep circularly through buffers
   - Decrement counter if > 0
   - Evict buffer if counter = 0

This provides LRU-like behavior efficiently:
- Frequently accessed pages stay in cache
- Rarely accessed pages get evicted
- Single-pass scans don't pollute cache
```

### Buffer States

```sql
-- Buffer pin and lock states
SELECT 
    CASE pinning_backends
        WHEN 0 THEN 'unpinned'
        ELSE 'pinned'
    END AS pin_state,
    isdirty,
    usagecount,
    count(*) AS buffers
FROM pg_buffercache
GROUP BY pinning_backends, isdirty, usagecount
ORDER BY pinning_backends, isdirty, usagecount;
```

---

## Write-Ahead Logging (WAL)

### WAL Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    WAL Pipeline                          │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Transaction ──► WAL Buffer ──► WAL Writer ──► Disk     │
│       │              │               │           │       │
│       │              │               │           │       │
│       ▼              ▼               ▼           ▼       │
│   XLogInsert    XLogFlush       fsync()     WAL Files   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### WAL Record Structure

```sql
-- WAL record components:
-- 1. Header: length, resource manager ID, info bits
-- 2. Data: Before/after images, tuple data
-- 3. Block references: Target blocks being modified

-- View WAL settings
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE '%wal%' OR name LIKE '%checkpoint%'
ORDER BY name;

-- WAL statistics
SELECT * FROM pg_stat_wal;

-- Current WAL position
SELECT pg_current_wal_lsn();
SELECT pg_current_wal_insert_lsn();

-- WAL file size
SHOW wal_segment_size;  -- Default 16MB
```

### WAL Levels

```sql
-- WAL levels (increasing verbosity):
-- minimal: Crash recovery only
-- replica: Streaming replication + PITR (default)
-- logical: Logical replication

SHOW wal_level;

-- Change requires restart:
-- ALTER SYSTEM SET wal_level = 'logical';
```

### Inspecting WAL

```sql
-- Use pg_waldump (command line tool)
-- pg_waldump /path/to/pg_wal/000000010000000000000001

-- View WAL statistics
SELECT 
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count
FROM pg_stat_archiver;
```

---

## Query Processing

### Query Processing Pipeline

```
SQL Query
    │
    ▼
┌─────────────────┐
│     Parser      │  ──► Parse tree
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Analyzer     │  ──► Query tree (semantic analysis)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Rewriter     │  ──► Rewritten tree (views, rules)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Planner      │  ──► Plan tree (optimal execution plan)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Executor     │  ──► Results
└─────────────────┘
```

### Parser

```sql
-- Parser creates raw parse tree from SQL text
-- Lexer tokenizes input
-- Grammar rules (gram.y) build tree structure

-- View parse tree (debug)
SET debug_print_parse = on;
SET client_min_messages = log;
SELECT * FROM pg_class LIMIT 1;
SET debug_print_parse = off;
```

### Analyzer/Semantic Analysis

```sql
-- Analyzer resolves names and types
-- Checks table/column existence
-- Validates function calls
-- Performs type checking

-- View analyzed query tree
SET debug_print_rewritten = on;
SELECT * FROM pg_class WHERE oid = 1;
SET debug_print_rewritten = off;
```

### Planner/Optimizer

```sql
-- Planner generates optimal execution plan
-- Cost-based optimization (CBO)
-- Considers multiple access paths, join orders

-- Cost estimation parameters
SHOW seq_page_cost;      -- Sequential page read cost (1.0)
SHOW random_page_cost;   -- Random page read cost (4.0)
SHOW cpu_tuple_cost;     -- Processing each row (0.01)
SHOW cpu_index_tuple_cost; -- Index entry processing (0.005)
SHOW cpu_operator_cost;  -- Operator/function cost (0.0025)

-- View planner output
EXPLAIN (VERBOSE) SELECT * FROM orders WHERE total > 100;

-- Planner statistics
SELECT 
    relname,
    reltuples,
    relpages,
    relallvisible
FROM pg_class
WHERE relname = 'orders';
```

### Plan Types

```sql
-- Sequential Scan: Read all rows
EXPLAIN SELECT * FROM large_table;

-- Index Scan: Use index to find rows
EXPLAIN SELECT * FROM users WHERE id = 1;

-- Index Only Scan: Answer from index alone
EXPLAIN SELECT id FROM users WHERE id < 100;

-- Bitmap Scan: Two-phase index scan
EXPLAIN SELECT * FROM orders WHERE status IN ('pending', 'processing');

-- Nested Loop Join: For each outer row, scan inner
EXPLAIN SELECT * FROM orders o JOIN users u ON o.user_id = u.id;

-- Hash Join: Build hash table, probe
EXPLAIN SELECT * FROM orders o JOIN products p ON o.product_id = p.id;

-- Merge Join: Sort both, merge
EXPLAIN SELECT * FROM orders o JOIN customers c ON o.customer_id = c.id 
ORDER BY c.id;
```

---

## Executor Engine

### Execution Model

```sql
-- PostgreSQL uses "demand-pull" model
-- Parent nodes pull tuples from children
-- Allows streaming without materializing

-- Executor node interface (conceptual):
-- ExecInitNode(): Initialize state
-- ExecProcNode(): Get next tuple
-- ExecEndNode(): Cleanup
```

### Node Types

```sql
-- Scan Nodes
-- SeqScan: Sequential table scan
-- IndexScan: B-tree index scan
-- BitmapIndexScan + BitmapHeapScan: Bitmap scan
-- TidScan: Direct tuple ID access
-- FunctionScan: Scan function result

-- Join Nodes
-- NestLoop: Nested loop join
-- MergeJoin: Sort-merge join
-- HashJoin: Hash join

-- Materialization Nodes
-- Sort: Sort rows
-- Hash: Build hash table
-- Materialize: Cache results
-- Unique: Remove duplicates

-- Aggregation Nodes
-- Agg: Aggregate functions
-- GroupAgg: Grouped aggregation
-- HashAgg: Hash-based grouping
-- WindowAgg: Window functions

-- Control Nodes
-- Append: UNION ALL
-- MergeAppend: Sorted UNION ALL
-- SubqueryScan: Subquery
-- Result: Constant result
-- Limit: LIMIT/OFFSET
```

### Parallel Execution

```sql
-- Parallel query execution
SET max_parallel_workers_per_gather = 4;

EXPLAIN (ANALYZE) SELECT count(*) FROM large_table;

-- Parallel nodes:
-- Gather: Collect results from parallel workers
-- Gather Merge: Merge sorted parallel results
-- Parallel Seq Scan: Parallel sequential scan
-- Parallel Index Scan: Parallel index scan
-- Parallel Hash Join: Parallel hash join
```

---

## System Catalogs

### Core Catalog Tables

```sql
-- pg_database: Databases
SELECT datname, oid, encoding, datcollate 
FROM pg_database;

-- pg_namespace: Schemas
SELECT nspname, oid, nspowner 
FROM pg_namespace;

-- pg_class: Tables, indexes, views, sequences
SELECT relname, relkind, reltuples, relpages
FROM pg_class
WHERE relkind = 'r' AND relnamespace = 'public'::regnamespace;

-- pg_attribute: Columns
SELECT attname, atttypid::regtype, attnum, attnotnull
FROM pg_attribute
WHERE attrelid = 'users'::regclass AND attnum > 0;

-- pg_type: Data types
SELECT typname, typlen, typtype 
FROM pg_type 
WHERE typnamespace = 'pg_catalog'::regnamespace;

-- pg_index: Index information
SELECT 
    i.relname AS index_name,
    t.relname AS table_name,
    a.attname AS column_name
FROM pg_index idx
JOIN pg_class i ON idx.indexrelid = i.oid
JOIN pg_class t ON idx.indrelid = t.oid
JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(idx.indkey)
WHERE t.relname = 'users';

-- pg_constraint: Constraints
SELECT conname, contype, condeferrable, condeferred
FROM pg_constraint
WHERE conrelid = 'orders'::regclass;
```

### Statistics Catalogs

```sql
-- pg_statistic: Column statistics (internal format)
-- Better to use pg_stats view:
SELECT 
    tablename,
    attname,
    n_distinct,
    most_common_vals,
    most_common_freqs,
    histogram_bounds
FROM pg_stats
WHERE tablename = 'orders';

-- pg_stat_user_tables: Table activity
SELECT 
    relname,
    seq_scan,
    idx_scan,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables;
```

---

## Visibility and MVCC

### Transaction IDs

```sql
-- Get current transaction ID
SELECT txid_current();

-- Transaction ID is 32-bit (wraps around)
-- Special values:
-- 0: Invalid
-- 1: Bootstrap
-- 2: Frozen (always visible)

-- Tuple visibility check (conceptual):
-- 1. Check t_xmin: Is inserting transaction committed and visible?
-- 2. Check t_xmax: Is tuple deleted/updated?
-- 3. Check hint bits for optimization
```

### Snapshot Management

```sql
-- View current snapshot
SELECT 
    txid_current_snapshot(),
    txid_snapshot_xmin(txid_current_snapshot()) AS xmin,
    txid_snapshot_xmax(txid_current_snapshot()) AS xmax;

-- Snapshot components:
-- xmin: Oldest active transaction (all < xmin are visible)
-- xmax: First unassigned XID (all >= xmax are invisible)
-- xip: List of in-progress transactions
```

### Hint Bits

```sql
-- Hint bits optimize visibility checks
-- Set on first access, avoid repeated clog lookups

-- HEAP_XMIN_COMMITTED: Insert transaction committed
-- HEAP_XMIN_INVALID: Insert transaction aborted
-- HEAP_XMAX_COMMITTED: Delete/update transaction committed
-- HEAP_XMAX_INVALID: Delete/update transaction aborted

-- View hint bits using pageinspect
SELECT t_infomask::bit(16) 
FROM heap_page_items(get_raw_page('users', 0));
```

### Transaction Age and Wraparound

```sql
-- Check age of oldest transaction
SELECT datname, age(datfrozenxid) AS age
FROM pg_database
ORDER BY age DESC;

-- Tables needing freeze
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    age(relfrozenxid) AS xid_age
FROM pg_stat_user_tables
JOIN pg_class ON relname = pg_stat_user_tables.relname
ORDER BY age(relfrozenxid) DESC;

-- Warning: age > 2 billion causes data loss!
-- autovacuum_freeze_max_age default: 200 million
```

---

## Lock Management

### Lock Types

```sql
-- View current locks
SELECT 
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE relation IS NOT NULL;

-- Lock modes (from weakest to strongest):
-- ACCESS SHARE: SELECT
-- ROW SHARE: SELECT FOR UPDATE/SHARE
-- ROW EXCLUSIVE: UPDATE, DELETE, INSERT
-- SHARE UPDATE EXCLUSIVE: VACUUM, ANALYZE, CREATE INDEX CONCURRENTLY
-- SHARE: CREATE INDEX (not concurrent)
-- SHARE ROW EXCLUSIVE: CREATE TRIGGER
-- EXCLUSIVE: REFRESH MATERIALIZED VIEW CONCURRENTLY
-- ACCESS EXCLUSIVE: DROP, TRUNCATE, ALTER TABLE
```

### Lock Conflicts

```sql
-- Lock conflict matrix
-- Locks conflict if they're both in the same row AND different columns:
--                    ACCESS  ROW    ROW      SHARE   SHARE   SHARE    EXCLUSIVE ACCESS
--                    SHARE   SHARE  EXCL     UPDATE  SHARE   ROW EXCL           EXCL
-- ACCESS SHARE                                               X         X        X
-- ROW SHARE                                  X       X       X         X        X
-- ROW EXCLUSIVE               X     X        X       X       X         X        X
-- SHARE UPDATE EXCL    X      X     X        X       X       X         X        X
-- SHARE                       X     X        X               X         X        X
-- SHARE ROW EXCLUSIVE  X      X     X        X       X       X         X        X
-- EXCLUSIVE           X       X     X        X       X       X         X        X
-- ACCESS EXCLUSIVE    X       X     X        X       X       X         X        X

-- Detect blocking
SELECT 
    blocked.pid AS blocked_pid,
    blocked.query AS blocked_query,
    blocking.pid AS blocking_pid,
    blocking.query AS blocking_query
FROM pg_stat_activity blocked
JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid AND NOT blocked_locks.granted
JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
    AND blocked_locks.database IS NOT DISTINCT FROM blocking_locks.database
    AND blocked_locks.relation IS NOT DISTINCT FROM blocking_locks.relation
    AND blocked_locks.page IS NOT DISTINCT FROM blocking_locks.page
    AND blocked_locks.tuple IS NOT DISTINCT FROM blocking_locks.tuple
    AND blocked_locks.virtualxid IS NOT DISTINCT FROM blocking_locks.virtualxid
    AND blocked_locks.transactionid IS NOT DISTINCT FROM blocking_locks.transactionid
    AND blocked.pid != blocking_locks.pid
JOIN pg_stat_activity blocking ON blocking_locks.pid = blocking.pid
WHERE NOT blocked_locks.granted;
```

### Lightweight Locks (LWLocks)

```sql
-- LWLocks protect shared memory structures
-- Finer-grained than heavy-weight locks

SELECT * FROM pg_stat_activity WHERE wait_event_type = 'LWLock';

-- Common LWLocks:
-- BufferContent: Protecting buffer page
-- BufferMapping: Buffer hash table
-- WALInsert: WAL insertion
-- ProcArray: Process array access
-- CheckpointLock: Checkpoint coordination
```

---

## Background Processes

### Background Writer

```sql
-- Writes dirty buffers to disk
-- Reduces checkpoint I/O spikes
-- Configured via:
SHOW bgwriter_delay;      -- Time between rounds (200ms)
SHOW bgwriter_lru_maxpages; -- Max pages per round (100)
SHOW bgwriter_lru_multiplier; -- Estimation multiplier (2.0)

-- Statistics
SELECT * FROM pg_stat_bgwriter;
```

### Checkpointer

```sql
-- Writes all dirty buffers and WAL
-- Creates consistent recovery point
-- Configured via:
SHOW checkpoint_timeout;     -- Time between checkpoints (5min)
SHOW checkpoint_completion_target; -- Spread writes over this fraction
SHOW max_wal_size;          -- Trigger checkpoint at this WAL size

-- View checkpoint activity
SELECT 
    checkpoints_timed,
    checkpoints_req,
    checkpoint_write_time,
    checkpoint_sync_time,
    buffers_checkpoint,
    buffers_clean,
    maxwritten_clean
FROM pg_stat_bgwriter;
```

### WAL Writer

```sql
-- Flushes WAL buffers to disk
-- Runs every wal_writer_delay (200ms)
SHOW wal_writer_delay;

-- WAL statistics
SELECT * FROM pg_stat_wal;
```

### Autovacuum

```sql
-- Reclaims dead tuple space
-- Updates statistics
-- Prevents transaction ID wraparound

SHOW autovacuum;
SHOW autovacuum_vacuum_threshold;     -- 50 tuples
SHOW autovacuum_vacuum_scale_factor;  -- 20% of table
SHOW autovacuum_analyze_threshold;    -- 50 tuples
SHOW autovacuum_analyze_scale_factor; -- 10% of table

-- View autovacuum activity
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables;
```

### Stats Collector

```sql
-- Collects statistics about database activity
-- Writes to pg_stat_tmp periodically

SHOW stats_temp_directory;

-- Reset statistics
SELECT pg_stat_reset();
SELECT pg_stat_reset_single_table_counters('users'::regclass);
```

---

## Checkpoint Mechanism

### Checkpoint Process

```
Checkpoint Trigger (timeout/WAL size/manual)
              │
              ▼
┌─────────────────────────────────────┐
│  1. Write all dirty buffers to disk │
│     (spread over completion_target) │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. fsync() all files               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Update pg_control file          │
│     (record checkpoint location)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Remove old WAL segments         │
└─────────────────────────────────────┘
```

### Checkpoint Tuning

```sql
-- Balance recovery time vs I/O load
-- More frequent checkpoints = faster recovery, more I/O
-- Less frequent = slower recovery, less I/O

-- Recommended settings for busy systems:
-- checkpoint_timeout = '15min'
-- checkpoint_completion_target = 0.9
-- max_wal_size = '4GB'
-- min_wal_size = '1GB'

-- Force checkpoint
CHECKPOINT;

-- Check if checkpoint needed
SELECT pg_current_wal_lsn() - '0/0'::pg_lsn AS wal_bytes;
```

---

## Statistics Collector

### Table Statistics

```sql
-- Enable extended statistics
CREATE STATISTICS stats_name ON column1, column2 FROM table_name;

-- View statistics
SELECT 
    stxname,
    stxkeys,
    stxkind  -- 'd' = ndistinct, 'f' = functional dependencies, 'm' = MCV
FROM pg_statistic_ext;

-- Analyze to collect statistics
ANALYZE table_name;
ANALYZE table_name (column1, column2);
```

### Query Statistics

```sql
-- Enable pg_stat_statements
CREATE EXTENSION pg_stat_statements;

-- View query statistics
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows,
    shared_blks_hit,
    shared_blks_read
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### I/O Statistics

```sql
-- Block-level I/O statistics
SELECT 
    relname,
    heap_blks_read,
    heap_blks_hit,
    idx_blks_read,
    idx_blks_hit,
    toast_blks_read,
    toast_blks_hit
FROM pg_statio_user_tables
ORDER BY heap_blks_read DESC;

-- Calculate hit ratio
SELECT 
    sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS heap_hit_ratio,
    sum(idx_blks_hit) / nullif(sum(idx_blks_hit) + sum(idx_blks_read), 0) AS idx_hit_ratio
FROM pg_statio_user_tables;
```

---

## Performance Internals

### JIT Compilation

```sql
-- Just-In-Time compilation for expensive queries
SHOW jit;
SHOW jit_above_cost;
SHOW jit_inline_above_cost;
SHOW jit_optimize_above_cost;

-- View JIT usage in explain
EXPLAIN (ANALYZE, VERBOSE) 
SELECT sum(amount) FROM large_sales WHERE year = 2024;
```

### Parallel Query

```sql
-- Parallel execution settings
SHOW max_parallel_workers;
SHOW max_parallel_workers_per_gather;
SHOW parallel_tuple_cost;
SHOW parallel_setup_cost;
SHOW min_parallel_table_scan_size;

-- Force parallel query for testing
SET force_parallel_mode = on;
```

---

## Debugging and Diagnostics

### Debug Output

```sql
-- Enable debug output (development only!)
SET debug_print_parse = on;
SET debug_print_rewritten = on;
SET debug_print_plan = on;
SET debug_pretty_print = on;

-- Log all statements
SET log_statement = 'all';

-- Log slow queries
SET log_min_duration_statement = '1s';
```

### System Views

```sql
-- Active sessions
SELECT * FROM pg_stat_activity;

-- Replication status
SELECT * FROM pg_stat_replication;

-- Database size
SELECT pg_database_size(current_database());

-- Table sizes
SELECT pg_total_relation_size('table_name');
```

---

## Summary

Understanding PostgreSQL internals enables:

1. **Better Performance Tuning**: Know what parameters affect what subsystems
2. **Effective Troubleshooting**: Identify bottlenecks in specific components
3. **Proper Capacity Planning**: Understand memory and storage requirements
4. **Optimal Schema Design**: Design for PostgreSQL's strengths
5. **Informed Monitoring**: Know what metrics matter

### Key Components to Monitor

| Component | Key Metrics |
|-----------|------------|
| Buffer Cache | Hit ratio, dirty pages |
| WAL | Write rate, lag |
| Checkpoints | Frequency, duration |
| Vacuum | Dead tuples, XID age |
| Locks | Blocked queries, wait events |
| Statistics | Autovacuum activity, analyze |

---

## Next Steps

- [Real-World Use Cases](49-real-world-use-cases.md)
- [Common Patterns and Anti-Patterns](50-patterns-and-antipatterns.md)
- [Migration Strategies](51-migration-strategies.md)
- [Troubleshooting Guide](52-troubleshooting-guide.md)
