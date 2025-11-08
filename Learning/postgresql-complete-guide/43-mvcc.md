# MVCC (Multi-Version Concurrency Control)

## Overview

Multi-Version Concurrency Control (MVCC) is PostgreSQL's foundational concurrency mechanism that allows multiple transactions to access the same data simultaneously without blocking each other. This comprehensive guide covers MVCC internals, transaction IDs, tuple visibility, vacuum processes, transaction wraparound, and performance optimization.

## Table of Contents

- [MVCC Fundamentals](#mvcc-fundamentals)
- [Transaction IDs](#transaction-ids)
- [Tuple Visibility](#tuple-visibility)
- [Snapshot Isolation](#snapshot-isolation)
- [VACUUM and Dead Tuples](#vacuum-and-dead-tuples)
- [Transaction Wraparound](#transaction-wraparound)
- [Bloat Management](#bloat-management)
- [Performance Implications](#performance-implications)
- [Best Practices](#best-practices)

## MVCC Fundamentals

### How MVCC Works

```sql
-- MVCC Core Principles:
-- 1. Each transaction sees a "snapshot" of the database
-- 2. Multiple versions of the same row can exist simultaneously
-- 3. Readers don't block writers, writers don't block readers
-- 4. Each row version has visibility information (xmin, xmax)

-- Traditional locking (NOT PostgreSQL):
-- Transaction 1: SELECT * FROM accounts WHERE id = 1; -- Acquires read lock
-- Transaction 2: UPDATE accounts SET balance = 2000 WHERE id = 1; -- BLOCKED!
-- Low concurrency, poor performance

-- PostgreSQL MVCC:
-- Transaction 1: SELECT * FROM accounts WHERE id = 1; -- Reads current version
-- Transaction 2: UPDATE accounts SET balance = 2000 WHERE id = 1; -- Creates new version
-- Transaction 1: SELECT * FROM accounts WHERE id = 1; -- Still sees old version
-- High concurrency, excellent performance

-- MVCC Benefits:
-- ✓ High concurrency (readers/writers don't block each other)
-- ✓ Consistent reads (transaction sees stable snapshot)
-- ✓ No read locks needed
-- ✓ Predictable performance

-- MVCC Costs:
-- ✗ Dead tuples (old versions) consume space
-- ✗ VACUUM required to reclaim space
-- ✗ Transaction ID wraparound concerns
-- ✗ Increased storage overhead

-- View MVCC in action
CREATE TABLE mvcc_example (
    id SERIAL PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO mvcc_example (value) VALUES ('version 1');

-- Check hidden columns
SELECT
    id,
    value,
    xmin::TEXT AS created_by_xid,  -- Transaction that created this version
    xmax::TEXT AS deleted_by_xid,  -- Transaction that deleted/updated (0 = active)
    ctid                            -- Physical location (page, tuple)
FROM mvcc_example;

-- Example output:
-- id | value     | created_by_xid | deleted_by_xid | ctid
-- ---|-----------|----------------|----------------|------
-- 1  | version 1 | 1001           | 0              | (0,1)

-- Update creates new version
UPDATE mvcc_example SET value = 'version 2' WHERE id = 1;

-- Old version marked as deleted (xmax set to updating transaction)
-- New version created (new xmin)

-- Using pageinspect extension to see both versions
CREATE EXTENSION IF NOT EXISTS pageinspect;

-- View all tuple versions (including dead ones)
SELECT
    lp AS tuple_index,
    lp_flags,
    t_xmin,
    t_xmax,
    t_ctid
FROM heap_page_items(get_raw_page('mvcc_example', 0));

-- Output shows multiple versions:
-- tuple_index | lp_flags | t_xmin | t_xmax | t_ctid
-- ------------|----------|--------|--------|--------
-- 1           | 1        | 1001   | 1002   | (0,2)  -- Old version (dead)
-- 2           | 1        | 1002   | 0      | (0,2)  -- Current version
```

### MVCC vs Traditional Locking

```sql
-- Comparison: MVCC vs Lock-Based Concurrency

-- Scenario: Two concurrent transactions

-- === MVCC (PostgreSQL) ===

-- Transaction 1 (T1)
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000 (reads current version)
-- Does NOT acquire read lock

-- Transaction 2 (T2) - Concurrent
BEGIN;
UPDATE accounts SET balance = 2000 WHERE id = 1;
-- Creates new version with xmin = T2's transaction ID
-- Does NOT block T1
COMMIT;

-- Transaction 1 continues
SELECT balance FROM accounts WHERE id = 1;
-- In READ COMMITTED: Sees 2000 (new snapshot)
-- In REPEATABLE READ: Sees 1000 (original snapshot)
COMMIT;

-- Result: T1 and T2 execute concurrently without blocking
-- Time saved: No waiting for locks

-- === Traditional Lock-Based (NOT PostgreSQL) ===

-- Transaction 1
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- Acquires READ LOCK
-- Lock held until commit

-- Transaction 2 - Concurrent
BEGIN;
UPDATE accounts SET balance = 2000 WHERE id = 1;
-- Attempts to acquire WRITE LOCK
-- BLOCKED waiting for T1's READ LOCK to be released!

-- Transaction 1
-- ... continues working ...
COMMIT; -- Finally releases READ LOCK

-- Transaction 2 can now proceed
-- Time wasted: Waiting for T1 to complete

-- MVCC Advantages:
-- 1. Higher throughput (no blocking)
-- 2. Predictable performance (no lock waits)
-- 3. Better scalability (more concurrent users)
-- 4. Simpler application code (fewer deadlocks)

-- MVCC Tradeoffs:
-- 1. Storage overhead (multiple versions)
-- 2. VACUUM maintenance required
-- 3. Transaction ID management
-- 4. Potential for UPDATE conflicts in REPEATABLE READ/SERIALIZABLE
```

## Transaction IDs

### Transaction ID Management

```sql
-- Transaction IDs (XIDs) are 32-bit integers
-- Range: 0 to 4,294,967,295 (2^32)
-- Special XIDs:
--   0: Invalid XID
--   1: Bootstrap XID
--   2: Frozen XID (used by VACUUM FREEZE)
--   3+: Regular transaction XIDs

-- View current transaction ID
SELECT txid_current(); -- Returns current transaction's XID

-- View current transaction without allocating new XID
SELECT txid_current_if_assigned(); -- NULL if no XID assigned yet

-- Transaction ID visibility
-- Transaction A sees transaction B as:
-- - IN PROGRESS: If B is still running
-- - COMMITTED: If B committed before A's snapshot
-- - ABORTED: If B rolled back

-- Check transaction status
SELECT txid_status(12345);
-- Returns: 'committed', 'aborted', 'in progress', or NULL (too old)

-- Transaction snapshot
-- Shows which transactions are visible to current transaction
SELECT txid_current_snapshot();
-- Format: xmin:xmax:xip_list
-- Example: 1000:1005:1001,1003
--   xmin (1000): Transactions < 1000 are committed
--   xmax (1005): Transactions >= 1005 haven't started
--   xip_list (1001,1003): These transactions are in progress

-- Snapshot components
SELECT
    txid_snapshot_xmin(txid_current_snapshot()) AS xmin,
    txid_snapshot_xmax(txid_current_snapshot()) AS xmax,
    txid_snapshot_xip(txid_current_snapshot()) AS in_progress;

-- View transaction ID usage per database
SELECT
    datname,
    age(datfrozenxid) AS xid_age,
    datfrozenxid,
    2^31 - 1000000 - age(datfrozenxid) AS xids_remaining
FROM pg_database
ORDER BY xid_age DESC;

-- Monitor transaction ID consumption rate
CREATE TABLE xid_monitoring (
    recorded_at TIMESTAMP DEFAULT NOW(),
    current_xid BIGINT,
    xids_consumed BIGINT
);

-- Record XID periodically
INSERT INTO xid_monitoring (current_xid, xids_consumed)
SELECT
    txid_current(),
    txid_current() - COALESCE(
        (SELECT current_xid FROM xid_monitoring ORDER BY recorded_at DESC LIMIT 1),
        txid_current()
    );

-- Calculate XID consumption rate
SELECT
    DATE_TRUNC('hour', recorded_at) AS hour,
    MAX(xids_consumed) AS xids_per_period,
    MAX(xids_consumed) / 3600.0 AS xids_per_second
FROM xid_monitoring
GROUP BY hour
ORDER BY hour DESC;
```

### Transaction ID Wraparound

```sql
-- Transaction IDs wrap around after 2^32 transactions
-- Without protection, old transactions would appear "in the future"
-- PostgreSQL uses VACUUM FREEZE to prevent this

-- Wraparound protection threshold
SHOW autovacuum_freeze_max_age; -- Default: 200,000,000 transactions

-- Check wraparound danger per table
SELECT
    schemaname,
    tablename,
    age(relfrozenxid) AS xid_age,
    autovacuum_freeze_max_age AS freeze_threshold,
    autovacuum_freeze_max_age - age(relfrozenxid) AS xids_until_wraparound_vacuum
FROM pg_stat_user_tables
JOIN pg_class ON pg_class.oid = relid
CROSS JOIN (SELECT setting::INT AS autovacuum_freeze_max_age FROM pg_settings WHERE name = 'autovacuum_freeze_max_age') AS config
ORDER BY xid_age DESC;

-- Alert when close to wraparound
SELECT
    datname,
    age(datfrozenxid) AS xid_age,
    2^31 - 1000000 AS danger_threshold,
    CASE
        WHEN age(datfrozenxid) > 2^31 - 1000000 THEN 'CRITICAL - IMMEDIATE ACTION REQUIRED'
        WHEN age(datfrozenxid) > 200000000 THEN 'WARNING - Schedule manual VACUUM FREEZE'
        ELSE 'OK'
    END AS status
FROM pg_database
ORDER BY xid_age DESC;

-- Manual VACUUM FREEZE (freezes all eligible tuples)
VACUUM FREEZE mvcc_example;

-- Aggressive vacuum (freezes more aggressively)
VACUUM (FREEZE, VERBOSE, ANALYZE) mvcc_example;

-- Monitor autovacuum progress
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY age(relfrozenxid) DESC;

-- Configure autovacuum for wraparound prevention (postgresql.conf)
-- autovacuum = on (must be enabled)
-- autovacuum_freeze_max_age = 200000000 (default)
-- vacuum_freeze_min_age = 50000000
-- vacuum_freeze_table_age = 150000000
```

## Tuple Visibility

### Visibility Rules

```sql
-- Each tuple (row version) has visibility metadata
-- xmin: Transaction ID that created this version
-- xmax: Transaction ID that deleted/updated this version (0 if current)

-- Visibility algorithm for transaction T viewing tuple:
-- 1. If xmin is in T's snapshot and committed, tuple was created before T
-- 2. If xmax is 0 or not in T's snapshot or not committed, tuple is not deleted
-- 3. If both conditions met, tuple is VISIBLE

-- Example: Demonstrating visibility

CREATE TABLE visibility_demo (
    id SERIAL PRIMARY KEY,
    value TEXT
);

-- Transaction 1: Insert
BEGIN; -- XID = 1001
INSERT INTO visibility_demo (value) VALUES ('row 1');
-- Tuple: xmin = 1001, xmax = 0
COMMIT;

-- View tuple metadata
SELECT
    id,
    value,
    xmin::TEXT AS created_by,
    xmax::TEXT AS deleted_by,
    CASE WHEN xmax = 0 THEN 'visible' ELSE 'deleted' END AS status
FROM visibility_demo;
-- Output: id=1, value='row 1', created_by=1001, deleted_by=0, status='visible'

-- Transaction 2: Update
BEGIN; -- XID = 1002
UPDATE visibility_demo SET value = 'row 1 updated' WHERE id = 1;
-- Old tuple: xmin = 1001, xmax = 1002 (marked as deleted)
-- New tuple: xmin = 1002, xmax = 0 (current version)
COMMIT;

-- Transaction 3: Concurrent read (before T2 commits)
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ; -- XID = 1003, snapshot before T2 commit
SELECT * FROM visibility_demo WHERE id = 1;
-- Sees old version: 'row 1'
-- Why? xmax = 1002 (T2) is not committed in T3's snapshot

-- Transaction 2 commits
COMMIT;

-- Transaction 3 continues
SELECT * FROM visibility_demo WHERE id = 1;
-- Still sees old version: 'row 1'
-- Why? Snapshot taken at BEGIN, doesn't include T2

COMMIT;

-- New transaction sees latest version
BEGIN;
SELECT * FROM visibility_demo WHERE id = 1;
-- Sees new version: 'row 1 updated'
COMMIT;

-- Visibility with deleted tuples
BEGIN; -- XID = 1004
DELETE FROM visibility_demo WHERE id = 1;
-- Tuple: xmin = 1002, xmax = 1004
COMMIT;

SELECT
    id,
    value,
    xmin::TEXT AS created_by,
    xmax::TEXT AS deleted_by,
    CASE WHEN xmax = 0 THEN 'visible' ELSE 'deleted' END AS status
FROM visibility_demo;
-- Tuple marked as deleted but still exists physically until VACUUM
```

### Tuple Header Information

```sql
-- Tuple header contains visibility information
-- View with pageinspect extension

CREATE EXTENSION IF NOT EXISTS pageinspect;

-- Create test data
CREATE TABLE tuple_header_demo (id INT, value TEXT);
INSERT INTO tuple_header_demo VALUES (1, 'test');

-- View tuple header information
SELECT
    lp AS item_number,
    lp_off AS offset,
    lp_flags AS flags,
    lp_len AS length,
    t_xmin AS xmin,
    t_xmax AS xmax,
    t_field3 AS cid_or_xvac,
    t_ctid AS ctid,
    t_infomask2,
    t_infomask,
    t_hoff AS header_length,
    t_bits,
    t_oid
FROM heap_page_items(get_raw_page('tuple_header_demo', 0));

-- Infomask bits (t_infomask) indicate tuple state:
-- HEAP_HASNULL        (0x0001): Has null values
-- HEAP_HASVARWIDTH    (0x0002): Has variable-width attributes
-- HEAP_HASEXTERNAL    (0x0004): Has out-of-line values (TOAST)
-- HEAP_HASOID         (0x0008): Has OID
-- HEAP_XMAX_COMMITTED (0x0400): xmax committed
-- HEAP_XMAX_INVALID   (0x0800): xmax invalid/aborted
-- HEAP_XMIN_COMMITTED (0x0100): xmin committed
-- HEAP_XMIN_INVALID   (0x0200): xmin invalid/aborted
-- HEAP_UPDATED        (0x2000): Tuple updated

-- Update and view changes
UPDATE tuple_header_demo SET value = 'updated' WHERE id = 1;

SELECT
    lp AS item_number,
    t_xmin AS xmin,
    t_xmax AS xmax,
    t_ctid AS ctid
FROM heap_page_items(get_raw_page('tuple_header_demo', 0));

-- Old tuple: xmax set, t_ctid points to new tuple location
-- New tuple: xmin set, xmax = 0
```

## Snapshot Isolation

### Snapshot Management

```sql
-- PostgreSQL uses Snapshot Isolation for REPEATABLE READ
-- Each transaction gets consistent snapshot of database

-- READ COMMITTED: New snapshot for each statement
BEGIN TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT * FROM accounts; -- Snapshot 1
-- Another transaction commits changes
SELECT * FROM accounts; -- Snapshot 2 (sees new changes)
COMMIT;

-- REPEATABLE READ: Single snapshot for entire transaction
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT * FROM accounts; -- Snapshot taken here
-- Another transaction commits changes
SELECT * FROM accounts; -- Same snapshot (doesn't see changes)
COMMIT;

-- SERIALIZABLE: Snapshot isolation + conflict detection
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts; -- sum = 10000
-- Another transaction inserts new account
INSERT INTO accounts (balance) VALUES (1000); -- By different transaction
-- Back to first transaction
INSERT INTO audit (total) VALUES ((SELECT SUM(balance) FROM accounts));
COMMIT; -- May fail with serialization error if conflict detected

-- Snapshot export/import (for parallel workers)

-- Export snapshot
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT pg_export_snapshot(); -- Returns snapshot ID: '00000003-00000001-1'

-- Different session imports same snapshot
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SET TRANSACTION SNAPSHOT '00000003-00000001-1';
-- Both sessions now see identical database state

-- Use case: pg_dump parallel export
-- pg_dump --snapshot=00000003-00000001-1 ...

-- View active snapshots
SELECT
    pid,
    usename,
    datname,
    state,
    backend_xid,
    backend_xmin,
    query_start,
    state_change,
    query
FROM pg_stat_activity
WHERE backend_xid IS NOT NULL OR backend_xmin IS NOT NULL
ORDER BY query_start;
```

## VACUUM and Dead Tuples

### Dead Tuple Management

```sql
-- Dead tuples are old row versions no longer visible to any transaction
-- VACUUM reclaims space occupied by dead tuples

-- Check dead tuples per table
SELECT
    schemaname,
    tablename,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY n_dead_tup DESC;

-- Manual VACUUM
VACUUM mvcc_example;

-- VACUUM VERBOSE (shows detailed output)
VACUUM VERBOSE mvcc_example;

-- VACUUM FULL (rewrites entire table, reclaims all space)
-- Warning: Requires ACCESS EXCLUSIVE lock, blocks all access
VACUUM FULL mvcc_example;

-- VACUUM ANALYZE (vacuum + update statistics)
VACUUM ANALYZE mvcc_example;

-- Autovacuum monitoring
SELECT
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY last_autovacuum DESC NULLS LAST;

-- Configure autovacuum per table
ALTER TABLE mvcc_example SET (
    autovacuum_vacuum_threshold = 50,
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_vacuum_cost_delay = 10
);

-- Autovacuum trigger formula:
-- vacuum_threshold = autovacuum_vacuum_threshold + autovacuum_vacuum_scale_factor * n_live_tup
-- Default: 50 + 0.2 * n_live_tup

-- View autovacuum progress
SELECT
    p.pid,
    p.datname,
    p.relid::regclass AS table_name,
    p.phase,
    p.heap_blks_total,
    p.heap_blks_scanned,
    p.heap_blks_vacuumed,
    ROUND(100.0 * p.heap_blks_scanned / NULLIF(p.heap_blks_total, 0), 2) AS pct_complete,
    a.query
FROM pg_stat_progress_vacuum p
JOIN pg_stat_activity a ON p.pid = a.pid;

-- Aggressive vacuum for bloat reduction
VACUUM (VERBOSE, ANALYZE, FREEZE, INDEX_CLEANUP ON) mvcc_example;
```

### VACUUM Configuration

```sql
-- Global autovacuum settings (postgresql.conf)

-- Enable autovacuum
-- autovacuum = on

-- Autovacuum launcher settings
-- autovacuum_max_workers = 3
-- autovacuum_naptime = 60s (check interval)

-- Vacuum thresholds
-- autovacuum_vacuum_threshold = 50 (minimum dead tuples)
-- autovacuum_vacuum_scale_factor = 0.2 (fraction of table size)
-- autovacuum_analyze_threshold = 50
-- autovacuum_analyze_scale_factor = 0.1

-- Vacuum cost-based delay (throttling)
-- autovacuum_vacuum_cost_delay = 2ms
-- autovacuum_vacuum_cost_limit = 200

-- Freeze settings
-- autovacuum_freeze_max_age = 200000000
-- vacuum_freeze_min_age = 50000000
-- vacuum_freeze_table_age = 150000000

-- View current settings
SELECT name, setting, unit, short_desc
FROM pg_settings
WHERE name LIKE 'autovacuum%' OR name LIKE 'vacuum%'
ORDER BY name;

-- Disable autovacuum for specific table (not recommended)
ALTER TABLE mvcc_example SET (autovacuum_enabled = false);

-- Re-enable
ALTER TABLE mvcc_example SET (autovacuum_enabled = true);

-- Customize per-table autovacuum
ALTER TABLE high_churn_table SET (
    autovacuum_vacuum_threshold = 100,
    autovacuum_vacuum_scale_factor = 0.05,  -- More aggressive
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.05
);
```

## Transaction Wraparound

### Preventing Wraparound

```sql
-- Transaction ID wraparound occurs after 2^32 (4 billion) transactions
-- PostgreSQL prevents this by freezing old tuples

-- Check wraparound status
SELECT
    datname,
    age(datfrozenxid) AS xid_age,
    datfrozenxid,
    ROUND(100.0 * age(datfrozenxid) / 2147483648, 2) AS pct_to_wraparound,
    CASE
        WHEN age(datfrozenxid) > 2000000000 THEN 'CRITICAL'
        WHEN age(datfrozenxid) > 1500000000 THEN 'WARNING'
        WHEN age(datfrozenxid) > 1000000000 THEN 'CAUTION'
        ELSE 'OK'
    END AS status
FROM pg_database
ORDER BY xid_age DESC;

-- Check per-table wraparound risk
SELECT
    n.nspname AS schema,
    c.relname AS table_name,
    c.relkind,
    age(c.relfrozenxid) AS xid_age,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS size,
    CASE
        WHEN age(c.relfrozenxid) > 2000000000 THEN 'CRITICAL - VACUUM IMMEDIATELY'
        WHEN age(c.relfrozenxid) > 1500000000 THEN 'WARNING - VACUUM SOON'
        WHEN age(c.relfrozenxid) > 1000000000 THEN 'CAUTION'
        ELSE 'OK'
    END AS status
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE c.relkind IN ('r', 'm', 't')
AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY age(c.relfrozenxid) DESC
LIMIT 20;

-- Emergency wraparound prevention
-- If database is near wraparound, PostgreSQL enters "emergency" mode
-- Only superuser can connect, must run VACUUM

-- Manual VACUUM FREEZE all tables
VACUUM FREEZE;

-- Vacuum specific table
VACUUM FREEZE mvcc_example;

-- Monitor autovacuum for wraparound prevention
SELECT
    schemaname,
    tablename,
    last_autovacuum,
    autovacuum_count,
    age(relfrozenxid) AS xid_age
FROM pg_stat_user_tables
JOIN pg_class ON pg_class.oid = relid
ORDER BY xid_age DESC;

-- Set alerts for wraparound danger
-- Alert if any database > 1.5 billion XIDs old
SELECT COUNT(*) FROM pg_database WHERE age(datfrozenxid) > 1500000000;
```

## Bloat Management

### Detecting Bloat

```sql
-- Bloat: Wasted space from dead tuples and fragmentation

-- Estimate table bloat
SELECT
    schemaname,
    tablename,
    ROUND(CASE WHEN otta=0 THEN 0.0 ELSE sml.relpages/otta::NUMERIC END,1) AS tbloat,
    CASE WHEN relpages < otta THEN 0 ELSE bs*(sml.relpages-otta)::BIGINT END AS wastedbytes,
    pg_size_pretty(CASE WHEN relpages < otta THEN 0 ELSE bs*(sml.relpages-otta)::BIGINT END) AS wastedsize,
    iname AS index_name,
    ROUND(CASE WHEN iotta=0 OR ipages=0 THEN 0.0 ELSE ipages/iotta::NUMERIC END,1) AS ibloat,
    CASE WHEN ipages < iotta THEN 0 ELSE bs*(ipages-iotta) END AS wastedibytes,
    pg_size_pretty(CASE WHEN ipages < iotta THEN 0 ELSE bs*(ipages-iotta) END) AS wastedisize
FROM (
    SELECT
        schemaname, tablename, cc.relpages, bs,
        CEIL((cc.reltuples*((datahdr+ma-
            (CASE WHEN datahdr%ma=0 THEN ma ELSE datahdr%ma END))+nullhdr2+4))/(bs-20::FLOAT)) AS otta,
        COALESCE(c2.relname,'?') AS iname, COALESCE(c2.reltuples,0) AS ituples, COALESCE(c2.relpages,0) AS ipages,
        COALESCE(CEIL((c2.reltuples*(datahdr-12))/(bs-20::FLOAT)),0) AS iotta
    FROM (
        SELECT
            ma,bs,schemaname,tablename,
            (datawidth+(hdr+ma-(CASE WHEN hdr%ma=0 THEN ma ELSE hdr%ma END)))::NUMERIC AS datahdr,
            (maxfracsum*(nullhdr+ma-(CASE WHEN nullhdr%ma=0 THEN ma ELSE nullhdr%ma END))) AS nullhdr2
        FROM (
            SELECT
                schemaname, tablename, hdr, ma, bs,
                SUM((1-null_frac)*avg_width) AS datawidth,
                MAX(null_frac) AS maxfracsum,
                hdr+(
                    SELECT 1+COUNT(*)/8
                    FROM pg_stats s2
                    WHERE null_frac<>0 AND s2.schemaname = s.schemaname AND s2.tablename = s.tablename
                ) AS nullhdr
            FROM pg_stats s, (
                SELECT
                    (SELECT current_setting('block_size')::NUMERIC) AS bs,
                    CASE WHEN SUBSTRING(v,12,3) IN ('8.0','8.1','8.2') THEN 27 ELSE 23 END AS hdr,
                    CASE WHEN v ~ 'mingw32' THEN 8 ELSE 4 END AS ma
                FROM (SELECT version() AS v) AS foo
            ) AS constants
            GROUP BY 1,2,3,4,5
        ) AS foo
    ) AS rs
    JOIN pg_class cc ON cc.relname = rs.tablename
    JOIN pg_namespace nn ON cc.relnamespace = nn.oid AND nn.nspname = rs.schemaname AND nn.nspname <> 'information_schema'
    LEFT JOIN pg_index i ON indrelid = cc.oid
    LEFT JOIN pg_class c2 ON c2.oid = i.indexrelid
) AS sml
ORDER BY wastedbytes DESC;

-- Simpler bloat check with pgstattuple extension
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS size,
    pgstattuple(schemaname||'.'||tablename).tuple_count AS live_tuples,
    pgstattuple(schemaname||'.'||tablename).dead_tuple_count AS dead_tuples,
    pgstattuple(schemaname||'.'||tablename).free_percent AS free_space_pct,
    ROUND(pgstattuple(schemaname||'.'||tablename).dead_tuple_percent, 2) AS dead_tuple_pct
FROM pg_stat_user_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Index bloat
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) AS index_size,
    pgstatindex(schemaname||'.'||indexname).avg_leaf_density AS leaf_density,
    pgstatindex(schemaname||'.'||indexname).leaf_fragmentation AS fragmentation
FROM pg_stat_user_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC
LIMIT 10;
```

### Reducing Bloat

```sql
-- Method 1: VACUUM (reclaims space within table, doesn't shrink file)
VACUUM VERBOSE mvcc_example;

-- Method 2: VACUUM FULL (rewrites entire table, shrinks file)
-- WARNING: Requires ACCESS EXCLUSIVE lock!
VACUUM FULL mvcc_example;

-- Method 3: pg_repack (online table repack, requires extension)
-- Rebuilds table without blocking reads/writes
-- Install: CREATE EXTENSION pg_repack;
-- Run: pg_repack -t mvcc_example

-- Method 4: CREATE TABLE ... AS + RENAME (manual rebuild)
BEGIN;
CREATE TABLE mvcc_example_new AS SELECT * FROM mvcc_example;
DROP TABLE mvcc_example;
ALTER TABLE mvcc_example_new RENAME TO mvcc_example;
-- Recreate indexes, constraints, etc.
COMMIT;

-- Method 5: Increase fillfactor (prevents page-level bloat)
ALTER TABLE high_update_table SET (fillfactor = 80);
-- Leaves 20% free space per page for HOT updates
VACUUM FULL high_update_table; -- Apply fillfactor

-- Method 6: Regular autovacuum (prevention)
ALTER TABLE mvcc_example SET (
    autovacuum_vacuum_scale_factor = 0.1,  -- More frequent
    autovacuum_vacuum_threshold = 50
);
```

## Performance Implications

### MVCC Performance Tuning

```sql
-- 1. Tune autovacuum for workload

-- High-churn tables (many UPDATEs/DELETEs)
ALTER TABLE high_churn SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02,
    fillfactor = 80
);

-- Large tables
ALTER TABLE large_table SET (
    autovacuum_vacuum_cost_delay = 5,  -- More aggressive
    autovacuum_vacuum_cost_limit = 1000
);

-- 2. Monitor dead tuple ratio
SELECT
    schemaname,
    tablename,
    n_dead_tup,
    n_live_tup,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;

-- Alert if dead tuple ratio > 20%
SELECT COUNT(*) FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
AND n_dead_tup::FLOAT / NULLIF(n_live_tup, 0) > 0.2;

-- 3. Use HOT updates when possible
-- HOT (Heap-Only Tuple): Update doesn't create new index entries
-- Requirements:
--   - Updated columns not indexed
--   - Free space available on same page (fillfactor)

-- Check HOT update ratio
SELECT
    schemaname,
    tablename,
    n_tup_upd AS total_updates,
    n_tup_hot_upd AS hot_updates,
    ROUND(100.0 * n_tup_hot_upd / NULLIF(n_tup_upd, 0), 2) AS hot_pct
FROM pg_stat_user_tables
WHERE n_tup_upd > 0
ORDER BY hot_pct ASC;

-- Improve HOT update ratio:
-- - Reduce fillfactor to leave free space
-- - Avoid indexing frequently updated columns
-- - Run VACUUM more frequently

-- 4. Monitor transaction age
SELECT
    pid,
    usename,
    datname,
    state,
    age(backend_xid) AS xid_age,
    age(backend_xmin) AS xmin_age,
    now() - xact_start AS transaction_duration,
    query
FROM pg_stat_activity
WHERE backend_xmin IS NOT NULL
ORDER BY xmin_age DESC;

-- Long-running transactions prevent VACUUM from cleaning dead tuples
-- Alert if transaction > 1 hour
SELECT COUNT(*) FROM pg_stat_activity
WHERE state = 'idle in transaction'
AND now() - xact_start > interval '1 hour';

-- 5. Optimize for REPEATABLE READ/SERIALIZABLE
-- These isolation levels hold snapshots longer
-- Prefer READ COMMITTED when possible
SHOW default_transaction_isolation;
```

## Best Practices

### MVCC Best Practices Checklist

```text
MVCC Best Practices:

1. Understand MVCC Benefits and Costs
   ✓ High concurrency (readers don't block writers)
   ✓ Consistent snapshots per transaction
   ✗ Dead tuples require VACUUM
   ✗ Transaction ID wraparound concerns

2. Configure Autovacuum Appropriately
   ✓ Enable autovacuum (autovacuum = on)
   ✓ Tune per-table settings for high-churn tables
   ✓ Monitor autovacuum effectiveness
   ✓ Increase autovacuum workers if needed

3. Monitor Dead Tuples
   ✓ Alert if dead tuple ratio > 20%
   ✓ Check n_dead_tup regularly
   ✓ Ensure autovacuum is keeping up

4. Prevent Transaction Wraparound
   ✓ Monitor age(datfrozenxid) per database
   ✓ Alert if approaching 1.5 billion XIDs
   ✓ Run manual VACUUM FREEZE if needed
   ✓ Never disable autovacuum globally

5. Manage Bloat Proactively
   ✓ Monitor table and index bloat
   ✓ Use VACUUM FULL or pg_repack for severe bloat
   ✓ Set appropriate fillfactor for high-update tables
   ✓ Regular autovacuum prevents bloat accumulation

6. Optimize HOT Updates
   ✓ Avoid indexing frequently updated columns
   ✓ Set fillfactor = 80-90 for high-update tables
   ✓ Monitor HOT update ratio

7. Keep Transactions Short
   ✓ Minimize transaction duration
   ✓ Don't hold transactions open while waiting for user input
   ✓ Long transactions prevent VACUUM cleanup

8. Choose Appropriate Isolation Level
   ✓ READ COMMITTED: Default, most web apps
   ✓ REPEATABLE READ: Reports, consistency requirements
   ✓ SERIALIZABLE: Critical integrity, financial transactions

9. Monitor Transaction ID Usage
   ✓ Track XID consumption rate
   ✓ Identify XID-intensive workloads
   ✓ Plan for XID wraparound

10. Regular Maintenance
    ✓ Schedule VACUUM during maintenance windows
    ✓ Run ANALYZE after bulk data changes
    ✓ Monitor autovacuum logs
    ✓ Review vacuum settings quarterly

Common Mistakes to Avoid:
✗ Disabling autovacuum
✗ Ignoring wraparound warnings
✗ Long-running idle transactions
✗ Not monitoring dead tuple ratio
✗ Over-indexing frequently updated columns
✗ Not setting fillfactor on high-update tables
✗ Ignoring bloat until performance degrades
✗ Using VACUUM FULL during peak hours (blocks access)
```

## Summary

MVCC (Multi-Version Concurrency Control) is PostgreSQL's core concurrency mechanism:

- **MVCC Benefits**: Readers don't block writers, high concurrency, consistent snapshots
- **Transaction IDs**: 32-bit XIDs track tuple visibility, wraparound protection required
- **Tuple Visibility**: xmin/xmax determine which transaction sees which row version
- **Snapshots**: Each transaction sees consistent database state (isolation levels)
- **VACUUM**: Reclaims space from dead tuples, prevents transaction wraparound
- **Bloat**: Dead tuples and fragmentation waste space, reduced by regular VACUUM
- **HOT Updates**: Optimize updates by avoiding new index entries (fillfactor, column selection)
- **Best Practices**: Enable autovacuum, monitor dead tuples, prevent wraparound, manage bloat, keep transactions short

MVCC enables PostgreSQL's exceptional concurrency but requires proper maintenance through VACUUM.

## Next Steps

- Study [Concurrency Control](./42-concurrency-control.md)
- Learn [Transaction Management](./06-transactions.md)
- Explore [Vacuum and Maintenance](./18-vacuuming-and-maintenance.md)
- Practice [Performance Tuning](./34-configuration-and-tuning.md)
