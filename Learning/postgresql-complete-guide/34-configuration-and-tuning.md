# Configuration and Tuning

## Overview

PostgreSQL performance heavily depends on proper configuration. This comprehensive guide covers configuration files, memory settings, connection management, query tuning, autovacuum tuning, and hardware considerations to optimize PostgreSQL for various workloads.

## Table of Contents
- [Configuration Files](#configuration-files)
- [Memory Configuration](#memory-configuration)
- [Connection Management](#connection-management)
- [Query Planner Settings](#query-planner-settings)
- [Write Ahead Log (WAL)](#write-ahead-log-wal)
- [Autovacuum Tuning](#autovacuum-tuning)
- [Checkpoint Configuration](#checkpoint-configuration)
- [Parallel Query Settings](#parallel-query-settings)
- [Workload-Specific Tuning](#workload-specific-tuning)
- [Hardware Considerations](#hardware-considerations)

## Configuration Files

### Main Configuration Files

```sql
-- Three main configuration files:

-- 1. postgresql.conf - Main configuration file
-- Location: SHOW config_file;
SHOW config_file;
-- /var/lib/postgresql/data/postgresql.conf

-- 2. pg_hba.conf - Host-based authentication
SHOW hba_file;
-- /var/lib/postgresql/data/pg_hba.conf

-- 3. pg_ident.conf - User name mapping
SHOW ident_file;
-- /var/lib/postgresql/data/pg_ident.conf

-- View all configuration parameters
SELECT name, setting, unit, category, short_desc
FROM pg_settings
ORDER BY category, name;

-- Search for specific settings
SELECT name, setting, unit
FROM pg_settings
WHERE name LIKE '%shared_buffers%';
```

### Modifying Configuration

```sql
-- Three ways to modify configuration:

-- 1. Edit postgresql.conf and reload
-- $ vim /var/lib/postgresql/data/postgresql.conf
-- Change: shared_buffers = 4GB
-- Reload configuration:
SELECT pg_reload_conf();

-- 2. ALTER SYSTEM (persists across restarts)
ALTER SYSTEM SET shared_buffers = '4GB';
SELECT pg_reload_conf();
-- Writes to postgresql.auto.conf

-- 3. SET (session-only, temporary)
SET work_mem = '256MB';
SHOW work_mem;
-- Reset at session end

-- View pending restart settings
SELECT name, setting, pending_restart
FROM pg_settings
WHERE pending_restart = true;

-- Some settings require restart
-- shared_buffers, max_connections, etc.
-- $ pg_ctl restart

-- Check configuration context
SELECT 
    name,
    setting,
    context  -- postmaster, sighup, user, etc.
FROM pg_settings
WHERE name IN ('shared_buffers', 'work_mem', 'max_connections')
ORDER BY name;
```

### Configuration Hierarchy

```sql
-- Configuration precedence (highest to lowest):

-- 1. Session level (SET command)
SET work_mem = '256MB';

-- 2. Database level
ALTER DATABASE mydb SET work_mem = '128MB';

-- 3. User level
ALTER ROLE app_user SET work_mem = '64MB';

-- 4. postgresql.auto.conf (ALTER SYSTEM)
-- ALTER SYSTEM SET work_mem = '32MB';

-- 5. postgresql.conf (manual edits)
-- work_mem = 16MB

-- View effective setting and source
SELECT 
    name,
    setting,
    source,
    sourcefile,
    sourceline
FROM pg_settings
WHERE name = 'work_mem';

-- Reset to default
RESET work_mem;
-- Or
SET work_mem TO DEFAULT;
```

## Memory Configuration

### Shared Buffers

```sql
-- shared_buffers: PostgreSQL's main cache
-- Recommended: 25% of system RAM (up to 8-16GB)
-- Beyond 16GB, diminishing returns (OS cache is effective)

-- Small system (4GB RAM)
-- shared_buffers = 1GB

-- Medium system (16GB RAM)
-- shared_buffers = 4GB

-- Large system (64GB RAM)
-- shared_buffers = 8GB - 16GB

-- Check current setting
SHOW shared_buffers;

-- View buffer usage
SELECT 
    buffers_checkpoint,
    buffers_clean,
    buffers_backend,
    maxwritten_clean
FROM pg_stat_bgwriter;

-- Buffer hit ratio (should be > 90%)
SELECT 
    sum(heap_blks_read) as heap_read,
    sum(heap_blks_hit) as heap_hit,
    round(sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100, 2) as cache_hit_ratio
FROM pg_statio_user_tables;
```

### Work Memory

```sql
-- work_mem: Memory for sorting, hashing, joins
-- Used per operation, per query (can be multiple per query!)
-- Default: 4MB (too low for most systems)

-- Calculation:
-- work_mem = Available RAM / (max_connections * 2 to 3)

-- Example: 16GB RAM, 100 connections
-- work_mem = 16GB / (100 * 3) = ~50MB

-- Conservative setting
-- work_mem = 32MB

-- More aggressive (for fewer concurrent queries)
-- work_mem = 128MB

-- Check current setting
SHOW work_mem;

-- Identify queries needing more work_mem
SELECT 
    query,
    calls,
    total_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
WHERE query LIKE '%ORDER BY%' OR query LIKE '%GROUP BY%'
ORDER BY total_time DESC
LIMIT 10;

-- Look for "external sort" in EXPLAIN
EXPLAIN (ANALYZE, BUFFERS) 
SELECT * FROM large_table ORDER BY some_column LIMIT 100;
-- If "external sort" appears, increase work_mem

-- Set per session for heavy queries
SET work_mem = '256MB';
SELECT * FROM large_table ORDER BY some_column;
RESET work_mem;
```

### Maintenance Work Memory

```sql
-- maintenance_work_mem: Memory for VACUUM, CREATE INDEX, etc.
-- Larger value = faster maintenance operations
-- Recommended: 5-10% of RAM, up to 1-2GB

-- Small system (4GB RAM)
-- maintenance_work_mem = 256MB

-- Medium system (16GB RAM)
-- maintenance_work_mem = 1GB

-- Large system (64GB RAM)
-- maintenance_work_mem = 2GB

-- Check current setting
SHOW maintenance_work_mem;

-- Set temporarily for index creation
SET maintenance_work_mem = '2GB';
CREATE INDEX idx_large_table ON large_table(column);
RESET maintenance_work_mem;

-- Autovacuum uses autovacuum_work_mem (or maintenance_work_mem if not set)
ALTER SYSTEM SET autovacuum_work_mem = '1GB';
SELECT pg_reload_conf();
```

### Effective Cache Size

```sql
-- effective_cache_size: Hint to planner about OS cache
-- NOT actual memory allocation, just a hint
-- Should be set to available RAM for PostgreSQL + OS cache
-- Recommended: 50-75% of total RAM

-- Small system (4GB RAM)
-- effective_cache_size = 3GB

-- Medium system (16GB RAM)
-- effective_cache_size = 12GB

-- Large system (64GB RAM)
-- effective_cache_size = 48GB

-- Check current setting
SHOW effective_cache_size;

-- Affects query planner decisions (index vs seq scan)
-- Higher value = planner more likely to use indexes
```

### Memory Summary

```sql
-- View all memory settings
SELECT 
    name,
    setting,
    unit,
    short_desc
FROM pg_settings
WHERE name IN (
    'shared_buffers',
    'work_mem',
    'maintenance_work_mem',
    'effective_cache_size',
    'temp_buffers',
    'autovacuum_work_mem'
)
ORDER BY name;

-- Recommended starting point (16GB RAM system):
-- shared_buffers = 4GB
-- work_mem = 32MB
-- maintenance_work_mem = 1GB
-- effective_cache_size = 12GB
```

## Connection Management

### Max Connections

```sql
-- max_connections: Maximum concurrent connections
-- Each connection consumes memory
-- Default: 100 (often too high for small systems)

-- Small application (< 50 concurrent users)
-- max_connections = 50

-- Medium application (100-200 concurrent users)
-- max_connections = 100

-- Large application (use connection pooler!)
-- max_connections = 200 (with PgBouncer/PgPool)

-- Check current setting
SHOW max_connections;

-- View current connections
SELECT count(*) FROM pg_stat_activity;

-- Connection states
SELECT 
    state,
    count(*) as connection_count
FROM pg_stat_activity
GROUP BY state
ORDER BY connection_count DESC;

-- Memory per connection estimate
-- Each connection: ~10MB (depends on work_mem and other settings)
-- 100 connections = ~1GB base memory

-- Reserve connections for superuser
-- superuser_reserved_connections = 3
```

### Connection Pooling

```sql
-- Use connection pooler for high-traffic applications

-- PgBouncer configuration example:
-- [databases]
-- mydb = host=localhost port=5432 dbname=mydb
-- 
-- [pgbouncer]
-- listen_addr = 0.0.0.0
-- listen_port = 6432
-- auth_type = scram-sha-256
-- pool_mode = transaction
-- max_client_conn = 1000
-- default_pool_size = 25

-- With PgBouncer:
-- Application: 1000 connections to PgBouncer
-- PgBouncer: 25 connections to PostgreSQL
-- PostgreSQL: max_connections = 50 (comfortable)

-- Connection pooling modes:
-- session: One server connection per client (safest)
-- transaction: Server connection released after transaction (efficient)
-- statement: Server connection released after statement (most aggressive)

-- Monitor connection pool
-- SELECT * FROM pg_stat_activity; (shows pooler connections)
```

### Idle Connections

```sql
-- idle_in_transaction_session_timeout: Kill idle transactions
-- Default: 0 (disabled)
-- Recommended: 60000 (1 minute) to prevent locks

ALTER SYSTEM SET idle_in_transaction_session_timeout = '60s';
SELECT pg_reload_conf();

-- statement_timeout: Kill long-running queries
-- Default: 0 (disabled)
-- Set per application needs

SET statement_timeout = '30s';  -- 30 second timeout

-- Find idle in transaction connections
SELECT 
    pid,
    usename,
    state,
    query_start,
    state_change,
    now() - state_change as idle_time
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes'
ORDER BY idle_time DESC;

-- Kill idle transactions
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '30 minutes';
```

## Query Planner Settings

### Random Page Cost

```sql
-- random_page_cost: Cost of random disk access
-- Default: 4.0 (assumes spinning disk)
-- SSD: 1.0 - 1.5
-- Fast SSD/NVMe: 1.0

-- Affects index vs sequential scan decisions
-- Lower value = planner prefers index scans

-- Check current setting
SHOW random_page_cost;

-- For SSD
ALTER SYSTEM SET random_page_cost = 1.1;
SELECT pg_reload_conf();

-- For NVMe
ALTER SYSTEM SET random_page_cost = 1.0;
SELECT pg_reload_conf();

-- Test impact on query plan
EXPLAIN SELECT * FROM large_table WHERE id = 1000;
-- Before: Seq Scan
-- After (with lower random_page_cost): Index Scan
```

### Effective IO Concurrency

```sql
-- effective_io_concurrency: Number of concurrent disk I/O operations
-- Default: 1 (conservative)
-- HDD RAID: 2-4
-- SSD: 200-300
-- NVMe: 200-300

-- Check current setting
SHOW effective_io_concurrency;

-- For SSD
ALTER SYSTEM SET effective_io_concurrency = 200;
SELECT pg_reload_conf();

-- Used for bitmap heap scans and parallel query
-- Higher value = more aggressive prefetching
```

### Statistics Target

```sql
-- default_statistics_target: Detail of column statistics
-- Default: 100
-- Higher = more accurate plans, slower ANALYZE
-- Range: 10 - 10000

-- For critical columns with skewed distributions
ALTER TABLE orders ALTER COLUMN customer_id SET STATISTICS 1000;
ANALYZE orders;

-- Global setting
-- default_statistics_target = 100 (default, good for most)
-- default_statistics_target = 500 (more accuracy for complex queries)

-- Check statistics quality
SELECT 
    schemaname,
    tablename,
    attname,
    n_distinct,
    most_common_vals,
    most_common_freqs
FROM pg_stats
WHERE tablename = 'orders'
  AND attname = 'customer_id';

-- Re-analyze after statistics target change
ANALYZE orders;
```

## Write Ahead Log (WAL)

### WAL Configuration

```sql
-- wal_level: Amount of information written to WAL
-- minimal: Only for crash recovery (no replication)
-- replica: Supports replication (default)
-- logical: Logical replication support

SHOW wal_level;
-- wal_level = replica (good default)

-- wal_buffers: Memory for WAL data before disk write
-- Default: -1 (auto, typically shared_buffers / 32)
-- Manual: 16MB for most workloads

-- wal_buffers = 16MB

-- max_wal_size: Checkpoint triggering threshold
-- Default: 1GB (often too low)
-- Recommended: 2-4GB (reduce checkpoint frequency)

ALTER SYSTEM SET max_wal_size = '4GB';
SELECT pg_reload_conf();

-- min_wal_size: Keep WAL files for reuse
-- Default: 80MB
-- Recommended: 1-2GB (reduce WAL file creation overhead)

ALTER SYSTEM SET min_wal_size = '2GB';
SELECT pg_reload_conf();

-- Check WAL usage
SELECT 
    count(*) as wal_files,
    pg_size_pretty(sum(size)) as total_size
FROM pg_ls_waldir();
```

### WAL Archiving

```sql
-- Enable WAL archiving for point-in-time recovery

-- archive_mode: Enable archiving
ALTER SYSTEM SET archive_mode = 'on';

-- archive_command: Command to archive WAL files
ALTER SYSTEM SET archive_command = 'cp %p /archive/%f';
-- Or for compression:
-- archive_command = 'gzip < %p > /archive/%f.gz'

-- archive_timeout: Force WAL switch interval
-- Default: 0 (disabled)
-- Recommended: 300 (5 minutes) for timely archiving
ALTER SYSTEM SET archive_timeout = '5min';

-- Requires restart
-- $ pg_ctl restart

-- Monitor archiving
SELECT 
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time
FROM pg_stat_archiver;
```

## Autovacuum Tuning

### Autovacuum Settings

```sql
-- autovacuum: Automatically clean up dead tuples
-- Essential for performance, should always be ON

-- Check if enabled
SHOW autovacuum;  -- Should be 'on'

-- Core autovacuum settings:

-- autovacuum_max_workers: Parallel autovacuum processes
-- Default: 3
-- Recommended: 4-6 for large databases
ALTER SYSTEM SET autovacuum_max_workers = 6;

-- autovacuum_naptime: Time between autovacuum runs
-- Default: 1min
-- Busy systems: 30s
-- Less busy: 5min
ALTER SYSTEM SET autovacuum_naptime = '30s';

-- autovacuum_vacuum_threshold: Min rows before vacuum
-- Default: 50
ALTER SYSTEM SET autovacuum_vacuum_threshold = 50;

-- autovacuum_vacuum_scale_factor: Fraction of table size
-- Default: 0.2 (vacuum when 20% of table is dead tuples)
-- Large tables: 0.05 (vacuum sooner)
ALTER SYSTEM SET autovacuum_vacuum_scale_factor = 0.1;

-- autovacuum_analyze_threshold: Min rows before analyze
-- Default: 50
ALTER SYSTEM SET autovacuum_analyze_threshold = 50;

-- autovacuum_analyze_scale_factor: Fraction for analyze
-- Default: 0.1 (analyze when 10% changed)
ALTER SYSTEM SET autovacuum_analyze_scale_factor = 0.05;

-- Apply changes
SELECT pg_reload_conf();
```

### Table-Specific Autovacuum

```sql
-- Override autovacuum settings per table

-- High-traffic table (frequent updates)
ALTER TABLE orders SET (
    autovacuum_vacuum_scale_factor = 0.01,  -- Vacuum at 1% dead tuples
    autovacuum_analyze_scale_factor = 0.01,
    autovacuum_vacuum_cost_delay = 10  -- Less sleep = faster vacuum
);

-- Very large table (slow autovacuum)
ALTER TABLE huge_table SET (
    autovacuum_vacuum_scale_factor = 0.001,  -- Vacuum at 0.1%
    autovacuum_vacuum_cost_limit = 5000  -- Higher I/O budget
);

-- Rarely updated table (less frequent vacuum)
ALTER TABLE config SET (
    autovacuum_vacuum_scale_factor = 0.5,  -- Vacuum at 50%
    autovacuum_naptime = 300  -- 5 minutes
);

-- Disable autovacuum (not recommended!)
ALTER TABLE temp_staging SET (
    autovacuum_enabled = false
);

-- View table autovacuum settings
SELECT 
    schemaname,
    relname,
    reloptions
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE reloptions IS NOT NULL;
```

### Monitoring Autovacuum

```sql
-- Current autovacuum activity
SELECT 
    pid,
    usename,
    query_start,
    state,
    query
FROM pg_stat_activity
WHERE query LIKE '%autovacuum%'
  AND query NOT LIKE '%pg_stat_activity%';

-- Last vacuum/analyze times
SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- Tables needing vacuum
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
  AND (n_dead_tup::float / nullif(n_live_tup + n_dead_tup, 0)) > 0.1
ORDER BY dead_ratio DESC;
```

## Checkpoint Configuration

### Checkpoint Settings

```sql
-- Checkpoints: Write dirty buffers to disk
-- Too frequent = high I/O overhead
-- Too infrequent = long recovery time

-- checkpoint_timeout: Time between checkpoints
-- Default: 5min (too frequent for many workloads)
-- Recommended: 15-30min
ALTER SYSTEM SET checkpoint_timeout = '15min';

-- checkpoint_completion_target: Spread checkpoint I/O
-- Default: 0.5 (complete in 50% of checkpoint interval)
-- Recommended: 0.9 (spread I/O, reduce spikes)
ALTER SYSTEM SET checkpoint_completion_target = 0.9;

-- max_wal_size: WAL size triggering checkpoint
-- Default: 1GB
-- Recommended: 2-4GB (reduce checkpoint frequency)
ALTER SYSTEM SET max_wal_size = '4GB';

-- Apply changes
SELECT pg_reload_conf();

-- Monitor checkpoints
SELECT 
    checkpoints_timed,
    checkpoints_req,
    checkpoint_write_time,
    checkpoint_sync_time,
    buffers_checkpoint,
    buffers_clean,
    buffers_backend
FROM pg_stat_bgwriter;

-- If checkpoints_req >> checkpoints_timed, increase max_wal_size
-- Goal: checkpoints_timed > 90% of total checkpoints
```

### Checkpoint Monitoring

```sql
-- Checkpoint frequency
-- Should be mostly time-triggered, not request-triggered

WITH checkpoint_stats AS (
    SELECT 
        checkpoints_timed,
        checkpoints_req,
        checkpoint_write_time,
        checkpoint_sync_time
    FROM pg_stat_bgwriter
)
SELECT 
    checkpoints_timed,
    checkpoints_req,
    round(100.0 * checkpoints_timed / nullif(checkpoints_timed + checkpoints_req, 0), 2) as timed_percent,
    checkpoint_write_time / 1000.0 as write_time_sec,
    checkpoint_sync_time / 1000.0 as sync_time_sec
FROM checkpoint_stats;

-- If timed_percent < 90%, increase max_wal_size

-- Log checkpoints for analysis
ALTER SYSTEM SET log_checkpoints = on;
SELECT pg_reload_conf();

-- Check logs:
-- $ grep "checkpoint" /var/log/postgresql/postgresql-*.log
-- Example output:
-- checkpoint starting: time
-- checkpoint complete: wrote 1234 buffers (5.0%); 0 WAL file(s) added...
```

## Parallel Query Settings

### Parallel Query Configuration

```sql
-- max_parallel_workers_per_gather: Workers per parallel operation
-- Default: 2
-- Recommended: 2-4 for most systems
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;

-- max_parallel_workers: Total parallel workers
-- Default: 8
-- Should be <= number of CPU cores
ALTER SYSTEM SET max_parallel_workers = 8;

-- max_worker_processes: Background worker limit
-- Default: 8
-- Should be >= max_parallel_workers
ALTER SYSTEM SET max_worker_processes = 10;

-- min_parallel_table_scan_size: Min table size for parallel scan
-- Default: 8MB
-- Smaller = more queries use parallelism
ALTER SYSTEM SET min_parallel_table_scan_size = '1MB';

-- min_parallel_index_scan_size: Min index size for parallel scan
-- Default: 512kB
ALTER SYSTEM SET min_parallel_index_scan_size = '128kB';

-- Apply changes (requires restart for max_worker_processes)
SELECT pg_reload_conf();

-- Test parallel query
EXPLAIN (ANALYZE, BUFFERS)
SELECT count(*) FROM large_table;
-- Look for "Gather" and "Parallel Seq Scan" nodes

-- Force parallel query for testing
SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 0;
SET parallel_tuple_cost = 0;
```

### Parallel Query Monitoring

```sql
-- View parallel workers
SELECT 
    pid,
    wait_event_type,
    wait_event,
    state,
    query
FROM pg_stat_activity
WHERE backend_type = 'parallel worker';

-- Check if parallel plans are used
SELECT 
    query,
    calls,
    total_time / calls as avg_time,
    rows / calls as avg_rows
FROM pg_stat_statements
WHERE query LIKE '%Gather%'  -- Parallel query indicator
ORDER BY total_time DESC
LIMIT 10;
```

## Workload-Specific Tuning

### OLTP (Online Transaction Processing)

```sql
-- Characteristics: Many short transactions, high concurrency

-- Memory settings (16GB RAM)
-- shared_buffers = 4GB
-- work_mem = 16MB  (many concurrent queries)
-- maintenance_work_mem = 512MB
-- effective_cache_size = 12GB

-- Connection settings
-- max_connections = 200 (with connection pooler)

-- Checkpoint settings
-- checkpoint_timeout = 5min  (more frequent for OLTP)
-- max_wal_size = 2GB

-- Other settings
-- random_page_cost = 1.1  (SSD)
-- effective_io_concurrency = 200

-- Example OLTP tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '512MB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET checkpoint_timeout = '5min';
ALTER SYSTEM SET max_wal_size = '2GB';
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
```

### OLAP (Online Analytical Processing)

```sql
-- Characteristics: Complex queries, fewer concurrent users, large data

-- Memory settings (16GB RAM)
-- shared_buffers = 4GB
-- work_mem = 256MB  (fewer concurrent, complex queries)
-- maintenance_work_mem = 2GB  (large indexes, vacuums)
-- effective_cache_size = 12GB

-- Connection settings
-- max_connections = 50  (fewer concurrent)

-- Checkpoint settings
-- checkpoint_timeout = 30min  (less frequent)
-- max_wal_size = 8GB

-- Parallel query
-- max_parallel_workers_per_gather = 4
-- max_parallel_workers = 8

-- Other settings
-- random_page_cost = 1.1  (SSD)
-- effective_io_concurrency = 200

-- Example OLAP tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '256MB';
ALTER SYSTEM SET maintenance_work_mem = '2GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET max_connections = 50;
ALTER SYSTEM SET checkpoint_timeout = '30min';
ALTER SYSTEM SET max_wal_size = '8GB';
ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
ALTER SYSTEM SET max_parallel_workers = 8;
ALTER SYSTEM SET random_page_cost = 1.1;
ALTER SYSTEM SET effective_io_concurrency = 200;
```

### Mixed Workload

```sql
-- Balance between OLTP and OLAP

-- Memory settings (16GB RAM)
-- shared_buffers = 4GB
-- work_mem = 64MB  (moderate)
-- maintenance_work_mem = 1GB
-- effective_cache_size = 12GB

-- Connection settings
-- max_connections = 100 (with connection pooler)

-- Checkpoint settings
-- checkpoint_timeout = 15min
-- max_wal_size = 4GB

-- Parallel query (enabled but not aggressive)
-- max_parallel_workers_per_gather = 2
-- max_parallel_workers = 4

-- Example mixed workload tuning
ALTER SYSTEM SET shared_buffers = '4GB';
ALTER SYSTEM SET work_mem = '64MB';
ALTER SYSTEM SET maintenance_work_mem = '1GB';
ALTER SYSTEM SET effective_cache_size = '12GB';
ALTER SYSTEM SET max_connections = 100;
ALTER SYSTEM SET checkpoint_timeout = '15min';
ALTER SYSTEM SET max_wal_size = '4GB';
ALTER SYSTEM SET max_parallel_workers_per_gather = 2;
ALTER SYSTEM SET max_parallel_workers = 4;
```

## Hardware Considerations

### CPU

```sql
-- CPU cores affect:
-- - max_parallel_workers (should be <= CPU cores)
-- - max_worker_processes (should be >= max_parallel_workers)

-- Check CPU cores
-- $ nproc
-- or
-- $ lscpu

-- 4 cores:
-- max_parallel_workers = 4
-- max_worker_processes = 6

-- 8 cores:
-- max_parallel_workers = 8
-- max_worker_processes = 10

-- 16+ cores:
-- max_parallel_workers = 8-12  (diminishing returns beyond 8-12)
-- max_worker_processes = 16
```

### RAM

```sql
-- Memory allocation guidelines:

-- Total RAM: 4GB (small)
-- shared_buffers = 1GB (25%)
-- effective_cache_size = 3GB (75%)
-- OS/other = 1GB

-- Total RAM: 16GB (medium)
-- shared_buffers = 4GB (25%)
-- effective_cache_size = 12GB (75%)
-- OS/other = 4GB

-- Total RAM: 64GB (large)
-- shared_buffers = 16GB (25%)
-- effective_cache_size = 48GB (75%)
-- OS/other = 16GB

-- Total RAM: 128GB+ (very large)
-- shared_buffers = 16GB (not >25%, diminishing returns)
-- effective_cache_size = 96GB (75%)
-- OS/other = 32GB

-- Check system RAM (Linux)
-- $ free -h
-- $ cat /proc/meminfo | grep MemTotal
```

### Storage

```sql
-- HDD (spinning disk)
-- random_page_cost = 4.0
-- effective_io_concurrency = 2

-- SATA SSD
-- random_page_cost = 1.1
-- effective_io_concurrency = 200

-- NVMe SSD
-- random_page_cost = 1.0
-- effective_io_concurrency = 200

-- RAID configuration affects:
-- effective_io_concurrency (higher for RAID with many disks)

-- Separate WAL on different disk (reduces contention)
-- $ initdb -D /data/pgdata -X /wal/pgwal

-- Check disk I/O
-- $ iostat -x 1
-- Look for high await (I/O wait time)
-- High await = I/O bottleneck

-- Monitor disk usage
SELECT 
    pg_database.datname,
    pg_size_pretty(pg_database_size(pg_database.datname)) as size
FROM pg_database
ORDER BY pg_database_size(pg_database.datname) DESC;
```

## Summary

PostgreSQL performance tuning involves:
- **Memory Configuration**: shared_buffers, work_mem, effective_cache_size
- **Connection Management**: max_connections, connection pooling
- **Query Planner**: random_page_cost, effective_io_concurrency
- **WAL Configuration**: max_wal_size, checkpoint settings
- **Autovacuum**: Proper tuning prevents bloat
- **Workload-Specific**: OLTP vs OLAP vs mixed
- **Hardware**: Match settings to CPU, RAM, storage

Regular monitoring and adjustment are essential for optimal performance.

## Next Steps

- Study [Query Optimization](./20-query-optimization.md)
- Learn [Monitoring and Logging](./38-monitoring-and-logging.md)
- Explore [Backup and Recovery](./35-backup-and-recovery.md)
- Practice [Performance Troubleshooting](./39-performance-troubleshooting.md)
