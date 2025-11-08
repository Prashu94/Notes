# Tablespaces

## Overview

Tablespaces in PostgreSQL allow administrators to define storage locations for database objects on the file system, enabling storage optimization across different physical devices (SSDs, HDDs), I/O distribution, and capacity management. This comprehensive guide covers tablespace creation, management, best practices, performance optimization, and real-world usage scenarios.

## Table of Contents

- [Tablespace Fundamentals](#tablespace-fundamentals)
- [Creating Tablespaces](#creating-tablespaces)
- [Managing Database Objects](#managing-database-objects)
- [Default Tablespaces](#default-tablespaces)
- [Moving Objects Between Tablespaces](#moving-objects-between-tablespaces)
- [Tablespace Permissions](#tablespace-permissions)
- [Monitoring Tablespaces](#monitoring-tablespaces)
- [Performance Optimization](#performance-optimization)
- [Best Practices](#best-practices)

## Tablespace Fundamentals

### What Are Tablespaces?

```sql
-- Tablespaces: Named locations on file system where PostgreSQL stores data files
-- Benefits:
-- 1. Storage flexibility: Place data on different disks
-- 2. Performance: Put hot data on fast SSD, cold data on slower HDD
-- 3. Capacity management: Distribute data across multiple volumes
-- 4. I/O distribution: Spread I/O load across devices

-- Default tablespaces:
-- pg_default: Default tablespace for user data
-- pg_global: System catalog tables (shared across all databases)

-- View existing tablespaces
SELECT
    spcname AS tablespace_name,
    pg_catalog.pg_get_userbyid(spcowner) AS owner,
    pg_catalog.pg_tablespace_location(oid) AS location,
    spcacl AS access_privileges,
    spcoptions AS options
FROM pg_tablespace
ORDER BY spcname;

-- Example output:
-- tablespace_name | owner    | location                           | access_privileges | options
-- ----------------|----------|---------------------------------------|-------------------|--------
-- pg_default      | postgres |                                       | NULL              | NULL
-- pg_global       | postgres |                                       | NULL              | NULL

-- Check current tablespace
SELECT current_setting('default_tablespace');

-- Tablespace use cases:
-- 1. Separate indexes from tables (fast SSD for indexes, regular storage for tables)
-- 2. Archive old data to slower/cheaper storage
-- 3. Place temporary tablespace on fast storage
-- 4. Distribute large tables across multiple disks
-- 5. Meet storage capacity requirements
```

### Tablespace Architecture

```text
PostgreSQL Data Directory Structure:

$PGDATA/
├── base/                    # Default tablespace (pg_default)
│   ├── 1/                  # template1 database
│   ├── 13000/              # template0 database
│   └── 16384/              # User database
│       ├── 16385          # Table file (relation)
│       ├── 16385_fsm      # Free Space Map
│       ├── 16385_vm       # Visibility Map
│       └── ...
├── global/                  # pg_global tablespace (cluster-wide tables)
│   ├── 1260               # pg_authid
│   ├── 1261               # pg_database
│   └── ...
└── pg_tblspc/              # Symbolic links to custom tablespaces
    ├── 16388 -> /mnt/ssd1/postgres/fast_tblspc
    └── 16389 -> /mnt/hdd1/postgres/archive_tblspc

Custom Tablespace Directory:
/mnt/ssd1/postgres/fast_tblspc/
└── PG_14_202107181/        # PostgreSQL version identifier
    └── 16384/              # Database OID
        ├── 16400          # Table/index file
        └── ...

Symbolic Link Flow:
Database Object -> pg_tblspc/16388 -> /mnt/ssd1/postgres/fast_tblspc/PG_14_202107181/16384/16400
```

## Creating Tablespaces

### Basic Tablespace Creation

```sql
-- Create directory on file system (as OS user with appropriate permissions)
-- Linux/macOS:
-- sudo mkdir -p /mnt/ssd1/postgres/fast_tblspc
-- sudo chown postgres:postgres /mnt/ssd1/postgres/fast_tblspc
-- sudo chmod 700 /mnt/ssd1/postgres/fast_tblspc

-- Create tablespace
CREATE TABLESPACE fast_storage
    LOCATION '/mnt/ssd1/postgres/fast_tblspc';

-- Create tablespace with owner
CREATE TABLESPACE archive_storage
    OWNER archive_user
    LOCATION '/mnt/hdd1/postgres/archive_tblspc';

-- Verify creation
SELECT * FROM pg_tablespace WHERE spcname = 'fast_storage';

-- View tablespace location
SELECT pg_tablespace_location(oid) AS location
FROM pg_tablespace
WHERE spcname = 'fast_storage';

-- Important notes:
-- 1. Directory must exist and be empty
-- 2. Directory must be owned by postgres user
-- 3. Directory permissions should be 700 (drwx------)
-- 4. Path must be absolute (not relative)
-- 5. Tablespace location is stored in symbolic link (pg_tblspc/)
```

### Tablespace Options

```sql
-- Create tablespace with options
CREATE TABLESPACE temp_storage
    LOCATION '/mnt/ssd2/postgres/temp_tblspc'
    WITH (
        seq_page_cost = 0.5,     -- Sequential page cost (default: 1.0)
        random_page_cost = 0.1    -- Random page cost (default: 4.0 for HDD, lower for SSD)
    );

-- Set tablespace parameters (affects query planner)
-- For SSD storage (faster random access)
ALTER TABLESPACE fast_storage SET (
    seq_page_cost = 0.5,
    random_page_cost = 0.5
);

-- For HDD storage (slower random access)
ALTER TABLESPACE archive_storage SET (
    seq_page_cost = 1.0,
    random_page_cost = 4.0
);

-- Reset to defaults
ALTER TABLESPACE fast_storage RESET (seq_page_cost, random_page_cost);

-- View tablespace options
SELECT spcname, spcoptions
FROM pg_tablespace
WHERE spcoptions IS NOT NULL;
```

## Managing Database Objects

### Creating Objects in Tablespaces

```sql
-- Create table in specific tablespace
CREATE TABLE hot_data (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
) TABLESPACE fast_storage;

-- Create index in specific tablespace
CREATE INDEX idx_hot_data_created
    ON hot_data (created_at)
    TABLESPACE fast_storage;

-- Create table with index in different tablespace
CREATE TABLE mixed_storage (
    id SERIAL PRIMARY KEY,
    data TEXT,
    archived BOOLEAN DEFAULT FALSE
) TABLESPACE pg_default;

CREATE INDEX idx_mixed_archived
    ON mixed_storage (archived)
    TABLESPACE fast_storage;  -- Index on fast storage

-- Create entire database in tablespace
CREATE DATABASE archive_db
    TABLESPACE archive_storage;

-- Check object tablespace
SELECT
    schemaname,
    tablename,
    tablespace
FROM pg_tables
WHERE tablespace IS NOT NULL;

-- Check index tablespace
SELECT
    schemaname,
    tablename,
    indexname,
    tablespace
FROM pg_indexes
WHERE tablespace IS NOT NULL;

-- Create temporary tables in temp tablespace
SET temp_tablespaces = 'temp_storage';

CREATE TEMP TABLE temp_data (
    id INT,
    value TEXT
);
-- Will use temp_storage tablespace
```

### Partitioned Tables and Tablespaces

```sql
-- Create partitioned table with partitions in different tablespaces
CREATE TABLE sales (
    id SERIAL,
    sale_date DATE NOT NULL,
    amount NUMERIC,
    region VARCHAR(50)
) PARTITION BY RANGE (sale_date);

-- Recent partition on fast SSD
CREATE TABLE sales_2024_q4 PARTITION OF sales
    FOR VALUES FROM ('2024-10-01') TO ('2025-01-01')
    TABLESPACE fast_storage;

-- Older partition on slower storage
CREATE TABLE sales_2024_q3 PARTITION OF sales
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01')
    TABLESPACE archive_storage;

-- Archive partition on cheapest storage
CREATE TABLE sales_2023 PARTITION OF sales
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01')
    TABLESPACE archive_storage;

-- Query uses appropriate storage automatically
SELECT * FROM sales WHERE sale_date >= '2024-10-01';
-- Accesses fast_storage

SELECT * FROM sales WHERE sale_date >= '2023-06-01' AND sale_date < '2023-07-01';
-- Accesses archive_storage

-- View partition tablespaces
SELECT
    nmsp_parent.nspname AS schema,
    parent.relname AS table_name,
    child.relname AS partition_name,
    ts.spcname AS tablespace
FROM pg_inherits
    JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
    JOIN pg_class child ON pg_inherits.inhrelid = child.oid
    JOIN pg_namespace nmsp_parent ON nmsp_parent.oid = parent.relnamespace
    LEFT JOIN pg_tablespace ts ON ts.oid = child.reltablespace
WHERE parent.relname = 'sales'
ORDER BY partition_name;
```

## Default Tablespaces

### Setting Default Tablespaces

```sql
-- System-wide default (postgresql.conf)
-- default_tablespace = 'fast_storage'

-- Session-level default
SET default_tablespace = 'fast_storage';

-- All new tables/indexes in this session use fast_storage
CREATE TABLE auto_fast (id INT);
-- Uses fast_storage tablespace

-- Reset to system default
RESET default_tablespace;

-- Database-level default
ALTER DATABASE mydb SET default_tablespace = 'fast_storage';

-- User-level default
ALTER ROLE myuser SET default_tablespace = 'fast_storage';

-- Temporary tablespace (for temp tables and work files)
SET temp_tablespaces = 'temp_storage';

-- Multiple temp tablespaces (load balancing)
SET temp_tablespaces = 'temp_storage1, temp_storage2, temp_storage3';
-- PostgreSQL distributes temp files across these tablespaces

-- View current defaults
SELECT
    current_setting('default_tablespace') AS default_tblspc,
    current_setting('temp_tablespaces') AS temp_tblspcs;

-- Check database default tablespace
SELECT
    datname,
    ts.spcname AS default_tablespace
FROM pg_database d
LEFT JOIN pg_tablespace ts ON ts.oid = d.dattablespace;
```

## Moving Objects Between Tablespaces

### Moving Tables and Indexes

```sql
-- Move table to different tablespace
ALTER TABLE hot_data SET TABLESPACE archive_storage;
-- Rewrites entire table, may take long time
-- Requires ACCESS EXCLUSIVE lock (blocks all access)

-- Move index to different tablespace
ALTER INDEX idx_hot_data_created SET TABLESPACE fast_storage;

-- Move all tables in schema to tablespace
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ALTER TABLE %I SET TABLESPACE %I', tbl.tablename, 'archive_storage');
    END LOOP;
END $$;

-- Move all indexes in tablespace to another
DO $$
DECLARE
    idx RECORD;
BEGIN
    FOR idx IN
        SELECT schemaname, indexname
        FROM pg_indexes
        WHERE tablespace = 'pg_default'
    LOOP
        EXECUTE format('ALTER INDEX %I.%I SET TABLESPACE %I',
            idx.schemaname, idx.indexname, 'fast_storage');
    END LOOP;
END $$;

-- Move database to different tablespace
ALTER DATABASE archive_db SET TABLESPACE archive_storage;
-- Moves all objects in database
-- Database must have no active connections

-- Check progress (for large tables, use pg_stat_progress_create_index for indexes)
SELECT
    pid,
    datname,
    relid::regclass AS table_name,
    phase,
    blocks_total,
    blocks_done,
    ROUND(100.0 * blocks_done / NULLIF(blocks_total, 0), 2) AS pct_done
FROM pg_stat_progress_cluster
WHERE command = 'CLUSTER'; -- Similar for tablespace moves
```

### Moving with Minimal Downtime

```sql
-- Strategy 1: Create new table, copy data, swap names
BEGIN;
-- Create new table in target tablespace
CREATE TABLE hot_data_new (LIKE hot_data INCLUDING ALL)
    TABLESPACE archive_storage;

-- Copy data
INSERT INTO hot_data_new SELECT * FROM hot_data;

-- Swap names
ALTER TABLE hot_data RENAME TO hot_data_old;
ALTER TABLE hot_data_new RENAME TO hot_data;

-- Drop old table
DROP TABLE hot_data_old;
COMMIT;

-- Strategy 2: Use pg_repack (requires extension)
-- Moves table/index to different tablespace without blocking
-- pg_repack -t hot_data --tablespace archive_storage

-- Strategy 3: For partitioned tables, move partitions individually
ALTER TABLE sales_2024_q4 SET TABLESPACE archive_storage;
-- Only locks one partition, not entire table
```

## Tablespace Permissions

### Managing Access

```sql
-- Grant CREATE permission on tablespace
GRANT CREATE ON TABLESPACE fast_storage TO app_user;

-- Revoke permission
REVOKE CREATE ON TABLESPACE fast_storage FROM app_user;

-- Grant to multiple users
GRANT CREATE ON TABLESPACE fast_storage TO app_user1, app_user2, app_user3;

-- Grant to role
GRANT CREATE ON TABLESPACE fast_storage TO app_role;

-- View tablespace permissions
SELECT
    spcname AS tablespace,
    pg_catalog.pg_get_userbyid(spcowner) AS owner,
    spcacl AS access_privileges
FROM pg_tablespace;

-- Check if user can create in tablespace
SELECT has_tablespace_privilege('app_user', 'fast_storage', 'CREATE');

-- Change tablespace owner
ALTER TABLESPACE fast_storage OWNER TO new_owner;

-- Grant all permissions
GRANT ALL ON TABLESPACE fast_storage TO admin_user;
```

## Monitoring Tablespaces

### Tablespace Usage

```sql
-- View tablespace size
SELECT
    spcname AS tablespace_name,
    pg_size_pretty(pg_tablespace_size(spcname)) AS size
FROM pg_tablespace
ORDER BY pg_tablespace_size(spcname) DESC;

-- Detailed tablespace usage by database
SELECT
    ts.spcname AS tablespace,
    d.datname AS database,
    pg_size_pretty(SUM(pg_relation_size(c.oid))) AS size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_database d ON d.datname = current_database()
JOIN pg_tablespace ts ON ts.oid = COALESCE(c.reltablespace, 0)
WHERE c.relkind IN ('r', 'i', 'm')
GROUP BY ts.spcname, d.datname
ORDER BY SUM(pg_relation_size(c.oid)) DESC;

-- Objects per tablespace
SELECT
    ts.spcname AS tablespace,
    COUNT(*) AS object_count,
    pg_size_pretty(SUM(pg_relation_size(c.oid))) AS total_size
FROM pg_class c
JOIN pg_tablespace ts ON ts.oid = COALESCE(c.reltablespace, 0)
WHERE c.relkind IN ('r', 'i', 'm')
GROUP BY ts.spcname
ORDER BY SUM(pg_relation_size(c.oid)) DESC;

-- Largest tables per tablespace
SELECT
    ts.spcname AS tablespace,
    n.nspname AS schema,
    c.relname AS table_name,
    pg_size_pretty(pg_relation_size(c.oid)) AS size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
JOIN pg_tablespace ts ON ts.oid = COALESCE(c.reltablespace, 0)
WHERE c.relkind = 'r'
ORDER BY pg_relation_size(c.oid) DESC
LIMIT 20;

-- Monitor disk space (requires file system access)
-- Linux: df -h /mnt/ssd1/postgres/fast_tblspc
-- Check available space on tablespace mount points

-- Alert if tablespace > 80% full
-- Requires external monitoring (shell script, monitoring tool)
```

### Tablespace I/O Statistics

```sql
-- Enable track_io_timing for accurate I/O stats (postgresql.conf)
-- track_io_timing = on

-- View I/O statistics per tablespace
SELECT
    ts.spcname AS tablespace,
    SUM(heap_blks_read) AS heap_blocks_read,
    SUM(heap_blks_hit) AS heap_blocks_hit,
    ROUND(100.0 * SUM(heap_blks_hit) / NULLIF(SUM(heap_blks_hit) + SUM(heap_blks_read), 0), 2) AS cache_hit_ratio,
    SUM(idx_blks_read) AS index_blocks_read,
    SUM(idx_blks_hit) AS index_blocks_hit
FROM pg_statio_user_tables st
JOIN pg_class c ON c.oid = st.relid
JOIN pg_tablespace ts ON ts.oid = COALESCE(c.reltablespace, 0)
GROUP BY ts.spcname;

-- Tablespace I/O wait times (requires pg_stat_statements)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

SELECT
    ts.spcname AS tablespace,
    COUNT(*) AS query_count,
    ROUND(AVG(total_time)::NUMERIC, 2) AS avg_time_ms,
    ROUND(SUM(blk_read_time)::NUMERIC, 2) AS total_read_time_ms,
    ROUND(SUM(blk_write_time)::NUMERIC, 2) AS total_write_time_ms
FROM pg_stat_statements pss
JOIN pg_class c ON c.relname = ANY(string_to_array(pss.query, ' '))
JOIN pg_tablespace ts ON ts.oid = COALESCE(c.reltablespace, 0)
WHERE pss.query NOT LIKE '%pg_%'
GROUP BY ts.spcname;
```

## Performance Optimization

### Optimizing with Tablespaces

```sql
-- Strategy 1: Hot/Cold Data Separation
-- Hot data (frequently accessed) -> SSD tablespace
-- Cold data (rarely accessed) -> HDD tablespace

-- Example: E-commerce orders
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT,
    order_date DATE,
    status VARCHAR(20),
    total NUMERIC
) PARTITION BY RANGE (order_date);

-- Recent orders on SSD (hot)
CREATE TABLE orders_2024 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    TABLESPACE fast_storage;

-- Old orders on HDD (cold)
CREATE TABLE orders_2023 PARTITION OF orders
    FOR VALUES FROM ('2023-01-01') TO ('2024-01-01')
    TABLESPACE archive_storage;

-- Strategy 2: Index Separation
-- Place indexes on faster storage than tables
CREATE TABLE large_table (
    id SERIAL PRIMARY KEY,
    data TEXT
) TABLESPACE pg_default;

CREATE INDEX idx_large_table_data ON large_table (data)
    TABLESPACE fast_storage;  -- Index on SSD

-- Strategy 3: Temporary Tablespace Optimization
-- Place temp tablespace on fastest storage (SSD with high IOPS)
SET temp_tablespaces = 'temp_storage';

-- Large sorts/joins use temp tablespace
SELECT * FROM large_table1 t1
JOIN large_table2 t2 ON t1.id = t2.id
ORDER BY t1.data;  -- Temp files written to temp_storage

-- Strategy 4: I/O Load Distribution
-- Distribute high-traffic tables across multiple tablespaces on different disks

CREATE TABLESPACE disk1_tblspc LOCATION '/mnt/disk1/postgres';
CREATE TABLESPACE disk2_tblspc LOCATION '/mnt/disk2/postgres';
CREATE TABLESPACE disk3_tblspc LOCATION '/mnt/disk3/postgres';

-- Distribute tables
CREATE TABLE high_traffic_1 (...) TABLESPACE disk1_tblspc;
CREATE TABLE high_traffic_2 (...) TABLESPACE disk2_tblspc;
CREATE TABLE high_traffic_3 (...) TABLESPACE disk3_tblspc;

-- Strategy 5: Adjust Cost Parameters
-- Fine-tune query planner for different storage types

-- SSD tablespace (fast random access)
ALTER TABLESPACE fast_storage SET (
    random_page_cost = 1.1,  -- Low random access cost
    seq_page_cost = 1.0
);

-- HDD tablespace (slow random access)
ALTER TABLESPACE archive_storage SET (
    random_page_cost = 4.0,  -- High random access cost
    seq_page_cost = 1.0
);

-- Planner chooses appropriate access methods based on costs
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;
-- Uses index scan on SSD, seq scan on HDD
```

### Benchmarking Tablespaces

```sql
-- Test sequential read performance
CREATE TABLE seq_read_test (id INT, data TEXT) TABLESPACE fast_storage;
INSERT INTO seq_read_test SELECT generate_series(1, 1000000), md5(random()::TEXT);

\timing on
SELECT COUNT(*) FROM seq_read_test;
\timing off
-- Record time

-- Test random read performance
CREATE INDEX idx_seq_read_test ON seq_read_test(id) TABLESPACE fast_storage;

\timing on
SELECT * FROM seq_read_test WHERE id = floor(random() * 1000000)::INT;
\timing off
-- Run multiple times, record average

-- Compare with different tablespace
CREATE TABLE seq_read_test_hdd (id INT, data TEXT) TABLESPACE archive_storage;
INSERT INTO seq_read_test_hdd SELECT generate_series(1, 1000000), md5(random()::TEXT);

\timing on
SELECT COUNT(*) FROM seq_read_test_hdd;
\timing off
-- Compare with SSD version

-- Test write performance
\timing on
INSERT INTO seq_read_test SELECT generate_series(1000001, 1100000), md5(random()::TEXT);
\timing off

-- Cleanup
DROP TABLE seq_read_test, seq_read_test_hdd;
```

## Best Practices

### Best Practices Checklist

```text
Tablespace Best Practices:

1. Strategic Placement
   ✓ Hot data (frequently accessed) on fast SSD
   ✓ Cold data (archived, rarely accessed) on slower HDD
   ✓ Indexes on fast storage (high I/O benefit)
   ✓ Temporary tablespace on fastest storage

2. Partitioning Strategy
   ✓ Recent partitions on fast storage
   ✓ Old partitions on archive storage
   ✓ Move partitions as they age
   ✓ Automate partition migration

3. I/O Distribution
   ✓ Distribute high-traffic tables across multiple disks
   ✓ Use multiple temp tablespaces for parallel queries
   ✓ Balance load across storage devices
   ✓ Monitor I/O utilization per tablespace

4. Capacity Planning
   ✓ Monitor tablespace disk usage (alert at 80%)
   ✓ Plan for data growth
   ✓ Reserve space for emergency (10-20%)
   ✓ Regular cleanup of old data

5. Cost Parameters
   ✓ Set random_page_cost appropriately per storage type
   ✓ SSD: random_page_cost = 1.1
   ✓ HDD: random_page_cost = 4.0
   ✓ Benchmark to validate settings

6. Permissions
   ✓ Grant CREATE only to necessary users
   ✓ Review permissions regularly
   ✓ Use roles for permission management
   ✓ Document tablespace ownership

7. Maintenance
   ✓ Regular VACUUM of tables in all tablespaces
   ✓ Monitor bloat per tablespace
   ✓ Schedule maintenance during off-peak hours
   ✓ Test tablespace migrations in dev first

8. Monitoring
   ✓ Track tablespace size growth
   ✓ Monitor I/O statistics per tablespace
   ✓ Alert on low disk space (< 20% free)
   ✓ Log tablespace moves and changes

9. Backup and Recovery
   ✓ Backup all tablespace locations
   ✓ Document tablespace directory structure
   ✓ Test restore procedures
   ✓ Include tablespaces in DR plan

10. Documentation
    ✓ Document tablespace purpose
    ✓ Document storage device specifications
    ✓ Document cost parameter rationale
    ✓ Maintain inventory of objects per tablespace

Common Mistakes to Avoid:
✗ Not setting appropriate cost parameters for storage type
✗ Placing all data in one tablespace (no benefit)
✗ Not monitoring disk space on tablespace volumes
✗ Moving large tables during peak hours (locks table)
✗ Not testing tablespace performance before production
✗ Forgetting to backup tablespace directories
✗ Not documenting tablespace strategy
✗ Using tablespaces without clear performance benefit
✗ Creating too many tablespaces (management overhead)
✗ Not aligning tablespace with physical storage boundaries
```

## Summary

Tablespaces enable flexible storage management in PostgreSQL:

- **Purpose**: Define storage locations for database objects on file system
- **Benefits**: Storage optimization, I/O distribution, capacity management, performance tuning
- **Default Tablespaces**: pg_default (user data), pg_global (system catalog)
- **Creation**: CREATE TABLESPACE with absolute path, proper permissions required
- **Object Placement**: Tables, indexes, partitions can reside in different tablespaces
- **Performance**: Hot data on SSD, cold data on HDD, separate indexes from tables
- **Cost Parameters**: random_page_cost and seq_page_cost guide query planner
- **Monitoring**: Track size, I/O statistics, disk space utilization
- **Best Practices**: Strategic placement, capacity planning, appropriate cost parameters, regular monitoring

Use tablespaces strategically for performance optimization and storage management.

## Next Steps

- Study [Configuration and Tuning](./34-configuration-and-tuning.md)
- Learn [Performance Troubleshooting](./45-cloud-deployments.md)
- Explore [Backup and Recovery](./35-backup-and-recovery.md)
- Practice [Partitioning](./13-partitioning.md)
