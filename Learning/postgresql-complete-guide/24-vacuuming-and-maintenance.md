# Vacuuming and Maintenance

## Overview

PostgreSQL uses Multi-Version Concurrency Control (MVCC) which creates dead tuples that must be cleaned up. VACUUM, ANALYZE, and related maintenance operations are essential for database health, performance, and preventing transaction ID wraparound issues.

## Table of Contents
- [Understanding VACUUM](#understanding-vacuum)
- [VACUUM Operations](#vacuum-operations)
- [ANALYZE Operations](#analyze-operations)
- [Autovacuum Configuration](#autovacuum-configuration)
- [Transaction ID Wraparound](#transaction-id-wraparound)
- [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
- [Best Practices](#best-practices)
- [Advanced Maintenance](#advanced-maintenance)

## Understanding VACUUM

### Why VACUUM is Needed

PostgreSQL's MVCC creates multiple versions of rows:

```sql
-- Create table
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    price NUMERIC
);

INSERT INTO products VALUES (1, 'Widget', 10.00);

-- Update creates new row version, old version becomes "dead tuple"
UPDATE products SET price = 12.00 WHERE product_id = 1;
-- Now: 1 live tuple + 1 dead tuple

UPDATE products SET price = 15.00 WHERE product_id = 1;
-- Now: 1 live tuple + 2 dead tuples

-- VACUUM removes dead tuples and marks space as reusable
VACUUM products;
-- Now: 1 live tuple, space from dead tuples available for reuse

-- Dead tuples accumulate from:
-- 1. UPDATE operations (old version becomes dead)
-- 2. DELETE operations (deleted row becomes dead)
-- 3. Rolled back transactions
-- 4. Aborted inserts
```

### What VACUUM Does

```sql
-- VACUUM performs these tasks:
-- 1. Remove dead tuples
-- 2. Mark space as reusable (doesn't return to OS)
-- 3. Update visibility map (for index-only scans)
-- 4. Freeze old transaction IDs (prevent wraparound)
-- 5. Update FSM (Free Space Map)

-- Check dead tuples
SELECT 
    schemaname,
    relname,
    n_live_tup,
    n_dead_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) as dead_pct,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

## VACUUM Operations

### Basic VACUUM

```sql
-- VACUUM entire database
VACUUM;

-- VACUUM specific table
VACUUM products;

-- VACUUM specific tables
VACUUM products, customers, orders;

-- VACUUM with progress monitoring
VACUUM VERBOSE products;

-- Output shows:
-- INFO:  vacuuming "public.products"
-- INFO:  "products": found 1000 removable, 5000 nonremovable row versions
-- INFO:  "products": removed 1000 row versions in 100 pages
```

### VACUUM FULL

Reclaims space but locks table:

```sql
-- Regular VACUUM (concurrent, doesn't return space to OS)
VACUUM products;
-- Space marked reusable but not returned to filesystem

-- VACUUM FULL (exclusive lock, returns space to OS)
VACUUM FULL products;
-- Rewrites entire table, returns unused space to OS

-- When to use VACUUM FULL:
-- 1. Table severely bloated (> 50% dead tuples)
-- 2. Can afford downtime (locks table)
-- 3. Disk space is critical

-- Alternatives to VACUUM FULL (no lock):
-- 1. pg_repack extension
CREATE EXTENSION pg_repack;
pg_repack -d database -t products

-- 2. CLUSTER (reorders by index)
CLUSTER products USING products_pkey;

-- 3. Recreate table
CREATE TABLE products_new AS SELECT * FROM products;
DROP TABLE products;
ALTER TABLE products_new RENAME TO products;
-- Don't forget to recreate indexes, constraints, etc.
```

### VACUUM FREEZE

Force tuple freezing:

```sql
-- Regular VACUUM with freezing
VACUUM FREEZE products;
-- Freezes all tuples immediately

-- Difference from regular VACUUM:
-- Regular VACUUM: Freezes only tuples > vacuum_freeze_min_age (50M xids)
-- VACUUM FREEZE: Freezes all tuples regardless of age

-- Use when:
-- 1. Preventing transaction ID wraparound
-- 2. Preparing for long-term archival
-- 3. After bulk data load

-- Check tuple freezing status
SELECT 
    relname,
    age(relfrozenxid) as xid_age,
    pg_size_pretty(pg_total_relation_size(oid)) as size
FROM pg_class
WHERE relkind = 'r'
ORDER BY age(relfrozenxid) DESC;
```

### VACUUM Options

```sql
-- VACUUM with all options
VACUUM (
    FULL FALSE,           -- Don't rewrite table
    FREEZE TRUE,          -- Freeze all tuples
    VERBOSE TRUE,         -- Show detailed output
    ANALYZE TRUE,         -- Update statistics
    DISABLE_PAGE_SKIPPING TRUE,  -- Don't skip pages
    SKIP_LOCKED FALSE,    -- Wait for locks (don't skip)
    INDEX_CLEANUP TRUE,   -- Clean up indexes
    TRUNCATE TRUE,        -- Return empty pages at end
    PARALLEL 4            -- Use 4 parallel workers (PG 13+)
) products;

-- Practical examples:

-- Fast VACUUM (skip locked tables)
VACUUM (SKIP_LOCKED) products;

-- VACUUM without index cleanup (faster)
VACUUM (INDEX_CLEANUP OFF) products;

-- Parallel VACUUM (PostgreSQL 13+)
VACUUM (PARALLEL 4) large_table;
```

## ANALYZE Operations

### Understanding ANALYZE

```sql
-- ANALYZE collects statistics for query planner
ANALYZE;              -- All tables
ANALYZE products;     -- Specific table
ANALYZE products (name, price);  -- Specific columns

-- What ANALYZE does:
-- 1. Samples table data
-- 2. Calculates column statistics (min, max, distribution)
-- 3. Estimates number of distinct values
-- 4. Builds histogram of value distribution
-- 5. Updates pg_statistic system catalog

-- View statistics
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    most_common_vals,
    histogram_bounds
FROM pg_stats
WHERE tablename = 'products';
```

### Statistics Target

```sql
-- Default statistics target: 100 (samples)
-- Range: 1-10000

-- Increase for selective columns
ALTER TABLE products ALTER COLUMN category SET STATISTICS 1000;
-- More samples = better estimates, but slower ANALYZE

-- Decrease for uniform columns
ALTER TABLE products ALTER COLUMN id SET STATISTICS 10;

-- Check statistics targets
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    correlation,
    null_frac
FROM pg_stats
WHERE tablename = 'products'
ORDER BY attname;

-- After changing statistics target
ANALYZE products;
```

### VACUUM ANALYZE

Combine both operations:

```sql
-- VACUUM and ANALYZE together (common)
VACUUM ANALYZE;              -- All tables
VACUUM ANALYZE products;     -- Specific table

-- Equivalent to:
VACUUM products;
ANALYZE products;

-- VACUUM FULL ANALYZE
VACUUM FULL ANALYZE products;
-- Reclaims space and updates statistics
```

## Autovacuum Configuration

### Global Autovacuum Settings

```sql
-- Check current autovacuum settings
SHOW autovacuum;                          -- on/off
SHOW autovacuum_max_workers;             -- Default: 3
SHOW autovacuum_naptime;                 -- Default: 1min
SHOW autovacuum_vacuum_threshold;       -- Default: 50
SHOW autovacuum_vacuum_scale_factor;    -- Default: 0.2 (20%)
SHOW autovacuum_analyze_threshold;      -- Default: 50
SHOW autovacuum_analyze_scale_factor;   -- Default: 0.1 (10%)

-- Autovacuum triggers when:
-- dead_tuples > threshold + (scale_factor * live_tuples)

-- Example: Table with 1,000,000 rows
-- VACUUM triggers at: 50 + (0.2 * 1,000,000) = 200,050 dead tuples
-- ANALYZE triggers at: 50 + (0.1 * 1,000,000) = 100,050 changes

-- Adjust in postgresql.conf:
-- autovacuum = on
-- autovacuum_max_workers = 4
-- autovacuum_naptime = 30s
-- autovacuum_vacuum_scale_factor = 0.05
-- autovacuum_analyze_scale_factor = 0.02
```

### Per-Table Autovacuum Settings

```sql
-- High-traffic table: More aggressive autovacuum
ALTER TABLE orders SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_threshold = 50,
    autovacuum_vacuum_scale_factor = 0.01,  -- 1% instead of 20%
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.005,  -- 0.5% instead of 10%
    autovacuum_vacuum_cost_delay = 5,        -- Slower, less I/O impact
    autovacuum_vacuum_cost_limit = 200
);

-- Low-traffic table: Less aggressive
ALTER TABLE archive_logs SET (
    autovacuum_vacuum_scale_factor = 0.5,
    autovacuum_analyze_scale_factor = 0.2
);

-- Disable autovacuum (not recommended)
ALTER TABLE temp_table SET (autovacuum_enabled = false);

-- Reset to defaults
ALTER TABLE orders RESET (autovacuum_vacuum_scale_factor);
```

### Monitoring Autovacuum

```sql
-- Check autovacuum activity
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    last_analyze,
    last_autoanalyze,
    analyze_count,
    autoanalyze_count
FROM pg_stat_user_tables
ORDER BY autovacuum_count DESC;

-- Find tables that need autovacuum
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / NULLIF(n_live_tup, 1), 2) as dead_pct,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;

-- Monitor running autovacuum
SELECT 
    pid,
    now() - query_start as duration,
    query
FROM pg_stat_activity
WHERE query LIKE '%autovacuum%'
  AND query NOT LIKE '%pg_stat_activity%';
```

## Transaction ID Wraparound

### Understanding Wraparound

```sql
-- PostgreSQL uses 32-bit transaction IDs (4 billion transactions)
-- After 4 billion transactions, IDs wrap around
-- Old transactions become "in the future" and invisible

-- Check transaction age
SELECT 
    datname,
    age(datfrozenxid) as xid_age,
    2147483647 - age(datfrozenxid) as xids_remaining
FROM pg_database
ORDER BY age(datfrozenxid) DESC;

-- Warning levels:
-- < 200M: Safe (green)
-- 200M - 1B: Caution (yellow)
-- 1B - 2B: Warning (orange)
-- > 2B: Critical (red) - automatic VACUUM FREEZE

-- Check table ages
SELECT 
    schemaname,
    relname,
    age(relfrozenxid) as xid_age,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||relname)) as size
FROM pg_stat_user_tables
ORDER BY age(relfrozenxid) DESC
LIMIT 20;
```

### Preventing Wraparound

```sql
-- Settings to prevent wraparound
SHOW vacuum_freeze_min_age;      -- Default: 50M
SHOW vacuum_freeze_table_age;    -- Default: 150M
SHOW autovacuum_freeze_max_age;  -- Default: 200M

-- Adjust in postgresql.conf:
-- autovacuum_freeze_max_age = 200000000
-- vacuum_freeze_min_age = 50000000

-- Manual freeze for old tables
VACUUM FREEZE old_table;

-- Monitor for wraparound danger
SELECT 
    datname,
    age(datfrozenxid),
    CASE 
        WHEN age(datfrozenxid) < 200000000 THEN 'OK'
        WHEN age(datfrozenxid) < 1000000000 THEN 'WARNING'
        ELSE 'CRITICAL'
    END as status
FROM pg_database
ORDER BY age(datfrozenxid) DESC;
```

### Handling Wraparound Emergency

```sql
-- If approaching wraparound:

-- 1. Check current age
SELECT max(age(datfrozenxid)) FROM pg_database;

-- 2. Find problem tables
SELECT 
    schemaname,
    relname,
    age(relfrozenxid) as xid_age
FROM pg_stat_user_tables
WHERE age(relfrozenxid) > 150000000
ORDER BY age(relfrozenxid) DESC;

-- 3. Aggressive VACUUM FREEZE
VACUUM FREEZE VERBOSE problem_table;

-- 4. If database is unresponsive:
-- Start PostgreSQL in single-user mode
postgres --single -D /var/lib/postgresql/data database_name
VACUUM FREEZE;
```

## Monitoring and Troubleshooting

### Table Bloat Detection

```sql
-- Install pgstattuple extension
CREATE EXTENSION pgstattuple;

-- Check table bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    round(100 * (1 - (pg_stat_get_live_tuples(schemaname||'.'||tablename)::float / 
          NULLIF(pg_stat_get_tuples_returned(schemaname||'.'||tablename), 0))), 2) as bloat_pct
FROM pg_stat_user_tables
WHERE pg_stat_get_tuples_returned(schemaname||'.'||tablename) > 0
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Detailed bloat analysis
SELECT * FROM pgstattuple('products');
-- Shows:
-- table_len: Total table size
-- tuple_count: Number of tuples
-- tuple_len: Space used by tuples
-- dead_tuple_count: Number of dead tuples
-- dead_tuple_len: Space used by dead tuples
-- free_space: Available space
```

### Index Bloat

```sql
-- Check index bloat
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Detailed index bloat
SELECT * FROM pgstatindex('idx_products_name');
-- Shows:
-- version, tree_level, index_size
-- avg_leaf_density: How full leaf pages are (100% = no bloat)
-- leaf_fragmentation: Physical disorder

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_products_name;
```

### Long-Running Transactions

```sql
-- Find long-running transactions (prevent VACUUM)
SELECT 
    pid,
    now() - xact_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
  AND xact_start IS NOT NULL
ORDER BY xact_start
LIMIT 10;

-- Kill problematic transaction
SELECT pg_terminate_backend(pid);

-- Check for idle transactions
SELECT 
    pid,
    now() - state_change as idle_duration,
    state,
    query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY state_change
LIMIT 10;
```

### VACUUM Progress Monitoring

```sql
-- Monitor VACUUM progress (PostgreSQL 9.6+)
SELECT 
    pid,
    datname,
    relid::regclass as table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    round(100.0 * heap_blks_scanned / NULLIF(heap_blks_total, 0), 2) as pct_complete,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;

-- Phases:
-- initializing
-- scanning heap
-- vacuuming indexes
-- vacuuming heap
-- cleaning up indexes
-- truncating heap
-- performing final cleanup
```

## Best Practices

### 1. Regular Monitoring

```sql
-- Create monitoring function
CREATE OR REPLACE FUNCTION check_vacuum_health()
RETURNS TABLE(
    table_name TEXT,
    dead_tuples BIGINT,
    dead_pct NUMERIC,
    last_vacuum TIMESTAMP,
    last_autovacuum TIMESTAMP,
    status TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname || '.' || relname,
        n_dead_tup,
        round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2),
        pg_stat_user_tables.last_vacuum,
        last_autovacuum,
        CASE 
            WHEN n_dead_tup > 100000 AND round(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) > 20 
                THEN 'CRITICAL'
            WHEN n_dead_tup > 50000 
                THEN 'WARNING'
            ELSE 'OK'
        END
    FROM pg_stat_user_tables
    ORDER BY n_dead_tup DESC;
END;
$$ LANGUAGE plpgsql;

-- Run daily
SELECT * FROM check_vacuum_health();
```

### 2. Scheduling Manual VACUUM

```sql
-- For critical tables, schedule manual VACUUM during maintenance windows

-- Using cron:
-- 0 2 * * * psql -d database -c "VACUUM ANALYZE critical_table;"

-- Using pg_cron extension:
CREATE EXTENSION pg_cron;

SELECT cron.schedule(
    'vacuum-critical-tables',
    '0 2 * * *',
    'VACUUM ANALYZE orders, customers, transactions'
);
```

### 3. Tuning for Workload

```sql
-- OLTP workload (many small transactions)
ALTER TABLE high_traffic_table SET (
    autovacuum_vacuum_scale_factor = 0.02,
    autovacuum_analyze_scale_factor = 0.01
);

-- OLAP/Warehouse (bulk operations)
ALTER TABLE warehouse_table SET (
    autovacuum_vacuum_scale_factor = 0.1,
    autovacuum_analyze_scale_factor = 0.05
);

-- Insert-only tables
ALTER TABLE logs SET (
    autovacuum_vacuum_scale_factor = 0.5,
    autovacuum_enabled = false  -- Manual VACUUM periodically
);
```

### 4. Handling Large Tables

```sql
-- For very large tables (100+ GB):

-- 1. Use parallel VACUUM (PG 13+)
VACUUM (PARALLEL 4) huge_table;

-- 2. Break into smaller operations
VACUUM (TRUNCATE OFF) huge_table;  -- Don't truncate at end

-- 3. Consider partitioning
-- VACUUM each partition separately

-- 4. Increase maintenance_work_mem
SET maintenance_work_mem = '2GB';
VACUUM huge_table;
```

## Advanced Maintenance

### VACUUM Configuration Tuning

```sql
-- Balance I/O impact vs speed

-- postgresql.conf settings:
-- vacuum_cost_delay = 2ms (default: 0 = no delay)
-- vacuum_cost_limit = 200 (default: 200)
-- vacuum_cost_page_hit = 1 (default: 1)
-- vacuum_cost_page_miss = 10 (default: 10)
-- vacuum_cost_page_dirty = 20 (default: 20)

-- Aggressive VACUUM (more I/O)
SET vacuum_cost_delay = 0;
VACUUM products;

-- Gentle VACUUM (less I/O impact)
SET vacuum_cost_delay = 10;
SET vacuum_cost_limit = 100;
VACUUM products;
```

### Visibility Map Maintenance

```sql
-- Check visibility map status
SELECT 
    schemaname,
    relname,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname)) as table_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||relname, 'vm')) as vm_size
FROM pg_stat_user_tables
ORDER BY pg_relation_size(schemaname||'.'||relname) DESC;

-- Force visibility map update
VACUUM (DISABLE_PAGE_SKIPPING) products;
```

### Free Space Map (FSM)

```sql
-- Check free space map
CREATE EXTENSION pg_freespacemap;

SELECT * FROM pg_freespace('products');
-- Shows available space per page

-- When FSM is inaccurate, VACUUM won't find reusable space
-- Solution: VACUUM FULL or CLUSTER
```

## Summary

PostgreSQL vacuuming and maintenance includes:
- **VACUUM**: Removes dead tuples, prevents bloat
- **ANALYZE**: Updates statistics for query planner
- **Autovacuum**: Automatic maintenance (critical to keep enabled)
- **Transaction ID freezing**: Prevents wraparound issues
- **Monitoring**: Regular checks for bloat and vacuum health
- **Tuning**: Per-table and global configuration

Proper maintenance is essential for database health and performance.

## Next Steps

- Learn about [MVCC](./43-mvcc.md) internals
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Study [Configuration and Tuning](./34-configuration-and-tuning.md)
- Practice [Backup and Recovery](./35-backup-and-recovery.md)
