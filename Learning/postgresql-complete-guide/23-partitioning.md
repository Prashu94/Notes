# Partitioning

## Overview

Table partitioning divides large tables into smaller, more manageable pieces called partitions. PostgreSQL supports declarative partitioning (PostgreSQL 10+) which improves query performance, simplifies maintenance, and enables efficient data archival.

## Table of Contents
- [Partitioning Basics](#partitioning-basics)
- [Partition Types](#partition-types)
- [Creating Partitions](#creating-partitions)
- [Partition Management](#partition-management)
- [Query Optimization](#query-optimization)
- [Maintenance Operations](#maintenance-operations)
- [Best Practices](#best-practices)
- [Migration Strategies](#migration-strategies)

## Partitioning Basics

### What is Partitioning?

```sql
-- Instead of one large table:
CREATE TABLE orders (
    order_id SERIAL,
    order_date DATE,
    customer_id INTEGER,
    total_amount NUMERIC
);
-- 100 million rows

-- Create partitioned table:
CREATE TABLE orders (
    order_id SERIAL,
    order_date DATE,
    customer_id INTEGER,
    total_amount NUMERIC
) PARTITION BY RANGE (order_date);

-- Create individual partitions:
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Benefits:
-- 1. Faster queries (partition pruning)
-- 2. Easier maintenance (drop old partitions)
-- 3. Better index performance (smaller indexes)
-- 4. Parallel operations per partition
-- 5. Efficient archival (detach partitions)
```

### When to Use Partitioning

```sql
-- Good candidates:
-- 1. Very large tables (100+ GB, millions of rows)
-- 2. Time-series data (logs, events, transactions)
-- 3. Data with natural partitioning key (date, region, category)
-- 4. Regular data archival/deletion needs
-- 5. Queries that filter on partition key

-- Example: Order history
-- - 100 million orders
-- - Queries mostly for recent orders
-- - Partition by year/quarter/month
-- - Drop old partitions after retention period

-- Not good candidates:
-- 1. Small tables (< 100 GB)
-- 2. Queries don't filter on partition key
-- 3. Uniform data distribution (no natural partition key)
-- 4. Very frequent partition creation/deletion
```

## Partition Types

### Range Partitioning

Most common - partition by value ranges:

```sql
-- By date ranges
CREATE TABLE measurements (
    measurement_id BIGSERIAL,
    sensor_id INTEGER,
    measured_at TIMESTAMP,
    temperature NUMERIC,
    humidity NUMERIC
) PARTITION BY RANGE (measured_at);

-- Monthly partitions
CREATE TABLE measurements_2024_01 PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE measurements_2024_02 PARTITION OF measurements
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

CREATE TABLE measurements_2024_03 PARTITION OF measurements
    FOR VALUES FROM ('2024-03-01') TO ('2024-04-01');

-- By numeric ranges
CREATE TABLE sales (
    sale_id BIGSERIAL,
    sale_amount NUMERIC,
    sale_date DATE
) PARTITION BY RANGE (sale_amount);

CREATE TABLE sales_small PARTITION OF sales
    FOR VALUES FROM (0) TO (1000);

CREATE TABLE sales_medium PARTITION OF sales
    FOR VALUES FROM (1000) TO (10000);

CREATE TABLE sales_large PARTITION OF sales
    FOR VALUES FROM (10000) TO (100000);

CREATE TABLE sales_xlarge PARTITION OF sales
    FOR VALUES FROM (100000) TO (MAXVALUE);
```

### List Partitioning

Partition by discrete values:

```sql
-- By country/region
CREATE TABLE customers (
    customer_id SERIAL,
    customer_name TEXT,
    country TEXT,
    email TEXT
) PARTITION BY LIST (country);

CREATE TABLE customers_usa PARTITION OF customers
    FOR VALUES IN ('USA');

CREATE TABLE customers_canada PARTITION OF customers
    FOR VALUES IN ('Canada');

CREATE TABLE customers_uk PARTITION OF customers
    FOR VALUES IN ('UK', 'GB');

CREATE TABLE customers_eu PARTITION OF customers
    FOR VALUES IN ('Germany', 'France', 'Spain', 'Italy');

CREATE TABLE customers_other PARTITION OF customers
    DEFAULT;  -- Catch-all for unlisted values

-- By status
CREATE TABLE orders (
    order_id SERIAL,
    status TEXT,
    order_date DATE,
    total_amount NUMERIC
) PARTITION BY LIST (status);

CREATE TABLE orders_active PARTITION OF orders
    FOR VALUES IN ('pending', 'processing', 'shipped');

CREATE TABLE orders_completed PARTITION OF orders
    FOR VALUES IN ('delivered', 'completed');

CREATE TABLE orders_cancelled PARTITION OF orders
    FOR VALUES IN ('cancelled', 'refunded');
```

### Hash Partitioning

Distribute data evenly:

```sql
-- By customer ID (for load distribution)
CREATE TABLE user_sessions (
    session_id UUID,
    user_id INTEGER,
    created_at TIMESTAMP,
    data JSONB
) PARTITION BY HASH (user_id);

-- Create 4 partitions
CREATE TABLE user_sessions_0 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);

CREATE TABLE user_sessions_1 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);

CREATE TABLE user_sessions_2 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 2);

CREATE TABLE user_sessions_3 PARTITION OF user_sessions
    FOR VALUES WITH (MODULUS 4, REMAINDER 3);

-- Benefits:
-- - Even data distribution
-- - Parallel query processing
-- - Load balancing

-- Drawbacks:
-- - Can't easily add/remove partitions
-- - No partition pruning for range queries
-- - Use only when even distribution is primary goal
```

### Multi-Level Partitioning (Sub-partitioning)

```sql
-- Partition by year, then by month
CREATE TABLE events (
    event_id BIGSERIAL,
    event_type TEXT,
    event_date DATE,
    user_id INTEGER,
    data JSONB
) PARTITION BY RANGE (event_date);

-- Year partitions
CREATE TABLE events_2024 PARTITION OF events
    FOR VALUES FROM ('2024-01-01') TO ('2025-01-01')
    PARTITION BY RANGE (event_date);

-- Month partitions within 2024
CREATE TABLE events_2024_01 PARTITION OF events_2024
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events_2024
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Alternatively: Partition by date, then by region
CREATE TABLE sales (
    sale_id BIGSERIAL,
    sale_date DATE,
    region TEXT,
    amount NUMERIC
) PARTITION BY RANGE (sale_date);

CREATE TABLE sales_2024_q1 PARTITION OF sales
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01')
    PARTITION BY LIST (region);

CREATE TABLE sales_2024_q1_north PARTITION OF sales_2024_q1
    FOR VALUES IN ('North', 'Northeast', 'Northwest');

CREATE TABLE sales_2024_q1_south PARTITION OF sales_2024_q1
    FOR VALUES IN ('South', 'Southeast', 'Southwest');
```

## Creating Partitions

### Automatic Partition Creation

```sql
-- PostgreSQL doesn't auto-create partitions, but you can:

-- 1. Using pg_partman extension
CREATE EXTENSION pg_partman;

SELECT partman.create_parent(
    p_parent_table := 'public.measurements',
    p_control := 'measured_at',
    p_type := 'native',
    p_interval := 'monthly',
    p_premake := 3
);

-- 2. Using function
CREATE OR REPLACE FUNCTION create_monthly_partition(
    table_name TEXT,
    start_date DATE
) RETURNS VOID AS $$
DECLARE
    partition_name TEXT;
    end_date DATE;
BEGIN
    partition_name := table_name || '_' || TO_CHAR(start_date, 'YYYY_MM');
    end_date := start_date + INTERVAL '1 month';
    
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF %I
         FOR VALUES FROM (%L) TO (%L)',
        partition_name, table_name, start_date, end_date
    );
    
    RAISE NOTICE 'Created partition: %', partition_name;
END;
$$ LANGUAGE plpgsql;

-- Create partitions for next 12 months
DO $$
DECLARE
    start_date DATE := DATE_TRUNC('month', CURRENT_DATE);
    i INTEGER;
BEGIN
    FOR i IN 0..11 LOOP
        PERFORM create_monthly_partition('measurements', start_date + (i || ' months')::INTERVAL);
    END LOOP;
END $$;

-- 3. Using cron job
-- Schedule daily/weekly job to create future partitions
-- psql -d database -c "SELECT create_monthly_partition('measurements', CURRENT_DATE + INTERVAL '2 months');"
```

### Indexes on Partitioned Tables

```sql
-- Create index on parent table (applies to all partitions)
CREATE TABLE orders (
    order_id SERIAL,
    order_date DATE,
    customer_id INTEGER,
    status TEXT
) PARTITION BY RANGE (order_date);

-- Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- Index on parent creates indexes on all partitions
CREATE INDEX idx_orders_customer ON orders(customer_id);
-- Creates: idx_orders_customer_orders_2024_q1, idx_orders_customer_orders_2024_q2, etc.

CREATE INDEX idx_orders_status ON orders(status);

-- Index on partition key (usually redundant)
CREATE INDEX idx_orders_date ON orders(order_date);
-- Not needed if queries always filter by partition key

-- Partial index example
CREATE INDEX idx_orders_pending ON orders(order_date)
WHERE status = 'pending';

-- Unique constraints require partition key
-- GOOD: Includes partition key
CREATE UNIQUE INDEX idx_orders_unique ON orders(order_id, order_date);

-- BAD: Doesn't include partition key
-- CREATE UNIQUE INDEX idx_orders_id ON orders(order_id);  -- ERROR!

-- Primary key must include partition key
ALTER TABLE orders ADD PRIMARY KEY (order_id, order_date);
```

## Partition Management

### Attaching Partitions

```sql
-- Create standalone table
CREATE TABLE orders_2024_q3 (
    order_id SERIAL,
    order_date DATE,
    customer_id INTEGER,
    status TEXT,
    CHECK (order_date >= '2024-07-01' AND order_date < '2024-10-01')
);

-- Populate data
INSERT INTO orders_2024_q3 SELECT * FROM staging_table;

-- Validate data
-- ALTER TABLE orders_2024_q3 VALIDATE CONSTRAINT ...;

-- Attach to partitioned table
ALTER TABLE orders ATTACH PARTITION orders_2024_q3
    FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

-- Fast operation - no data movement
```

### Detaching Partitions

```sql
-- Detach partition (for archival/maintenance)
ALTER TABLE orders DETACH PARTITION orders_2023_q1;

-- Concurrent detach (PostgreSQL 14+, doesn't block queries)
ALTER TABLE orders DETACH PARTITION orders_2023_q1 CONCURRENTLY;

-- Now orders_2023_q1 is a regular table
-- Can be:
-- 1. Archived
pg_dump -t orders_2023_q1 database > orders_2023_q1.sql

-- 2. Moved to different tablespace
ALTER TABLE orders_2023_q1 SET TABLESPACE archive_tablespace;

-- 3. Dropped
DROP TABLE orders_2023_q1;

-- 4. Exported
COPY orders_2023_q1 TO '/archive/orders_2023_q1.csv' WITH CSV HEADER;
DROP TABLE orders_2023_q1;
```

### Moving Partitions

```sql
-- Move partition to different tablespace
ALTER TABLE orders_2024_q1 SET TABLESPACE ssd_tablespace;

-- Move old partitions to slow storage
ALTER TABLE orders_2022_q1 SET TABLESPACE hdd_tablespace;
ALTER TABLE orders_2022_q2 SET TABLESPACE hdd_tablespace;
```

### Splitting and Merging Partitions

```sql
-- Split yearly partition into quarterly partitions

-- 1. Create new partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
    FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

-- 2. Detach old partition
ALTER TABLE orders DETACH PARTITION orders_2024;

-- 3. Move data
INSERT INTO orders_2024_q1 SELECT * FROM orders_2024 
WHERE order_date >= '2024-01-01' AND order_date < '2024-04-01';

INSERT INTO orders_2024_q2 SELECT * FROM orders_2024 
WHERE order_date >= '2024-04-01' AND order_date < '2024-07-01';

-- 4. Drop old partition
DROP TABLE orders_2024;

-- Merge partitions (reverse process)
-- Create new larger partition, copy data, drop old partitions
```

## Query Optimization

### Partition Pruning

PostgreSQL automatically eliminates partitions that don't match query conditions:

```sql
-- Enable partition pruning (default: on)
SET enable_partition_pruning = on;

-- Example: Query only one partition
EXPLAIN SELECT * FROM orders WHERE order_date = '2024-06-15';

-- Output shows:
-- Append
--   -> Seq Scan on orders_2024_q2
--         Filter: (order_date = '2024-06-15')
-- Only scans orders_2024_q2 partition!

-- Query multiple partitions
EXPLAIN SELECT * FROM orders 
WHERE order_date BETWEEN '2024-03-15' AND '2024-08-15';

-- Output shows:
-- Append
--   -> Seq Scan on orders_2024_q1
--   -> Seq Scan on orders_2024_q2
--   -> Seq Scan on orders_2024_q3
-- Scans only relevant partitions

-- Query without partition key (scans all partitions)
EXPLAIN SELECT * FROM orders WHERE customer_id = 100;

-- Output shows:
-- Append
--   -> Seq Scan on orders_2024_q1
--   -> Seq Scan on orders_2024_q2
--   -> Seq Scan on orders_2024_q3
--   -> Seq Scan on orders_2024_q4
-- Must scan all partitions (no pruning)
```

### Partition-Wise Joins

```sql
-- Enable partition-wise joins (PostgreSQL 11+)
SET enable_partitionwise_join = on;
SET enable_partitionwise_aggregate = on;

-- Both tables partitioned identically
CREATE TABLE orders (...) PARTITION BY RANGE (order_date);
CREATE TABLE order_items (...) PARTITION BY RANGE (order_date);

-- Join on partition key
EXPLAIN SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date BETWEEN '2024-01-01' AND '2024-03-31';

-- With partition-wise join:
-- Append
--   -> Hash Join
--         -> Seq Scan on orders_2024_q1
--         -> Hash
--               -> Seq Scan on order_items_2024_q1
-- Joins partition-by-partition (more efficient)
```

### Constraint Exclusion (Legacy)

```sql
-- For inheritance-based partitioning (pre-PostgreSQL 10)
SET constraint_exclusion = partition;

-- Not needed for declarative partitioning
```

## Maintenance Operations

### VACUUM and ANALYZE

```sql
-- Vacuum parent table (vacuums all partitions)
VACUUM orders;

-- Vacuum specific partition
VACUUM orders_2024_q1;

-- Analyze for statistics
ANALYZE orders;
ANALYZE orders_2024_q1;

-- Autovacuum works per partition
ALTER TABLE orders_2024_q1 SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);
```

### REINDEX

```sql
-- Reindex parent (reindexes all partition indexes)
REINDEX TABLE orders;

-- Reindex specific partition
REINDEX TABLE orders_2024_q1;

-- Concurrent reindex
REINDEX INDEX CONCURRENTLY idx_orders_customer_orders_2024_q1;
```

### Statistics

```sql
-- View partition sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) AS indexes_size
FROM pg_tables
WHERE tablename LIKE 'orders_%'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check partition row counts
SELECT
    schemaname,
    tablename,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE tablename LIKE 'orders_%'
ORDER BY tablename;
```

## Best Practices

### 1. Choose Appropriate Partition Size

```sql
-- Too many partitions (< 1GB each):
-- - High overhead
-- - Slow partition pruning
-- - Many small indexes

-- Too few partitions (> 100GB each):
-- - Limited pruning benefit
-- - Large maintenance operations
-- - Slow partition drops

-- Recommended: 10-50GB per partition
-- For time-series: monthly or quarterly partitions often work well
```

### 2. Always Include Partition Key in Queries

```sql
-- GOOD: Includes partition key
SELECT * FROM orders 
WHERE order_date = '2024-06-15' AND customer_id = 100;

-- BAD: Missing partition key (scans all partitions)
SELECT * FROM orders WHERE customer_id = 100;

-- Solution: Add index on non-partition columns
CREATE INDEX idx_orders_customer ON orders(customer_id);
```

### 3. Pre-create Future Partitions

```sql
-- Avoid runtime errors for new data
-- Create partitions for next 3 months in advance

-- Schedule monthly job:
SELECT create_monthly_partition('orders', CURRENT_DATE + INTERVAL '2 months');
SELECT create_monthly_partition('orders', CURRENT_DATE + INTERVAL '3 months');
```

### 4. Monitor Partition Growth

```sql
-- Alert when partition reaches size limit
CREATE OR REPLACE FUNCTION check_partition_size(
    table_pattern TEXT,
    max_size_gb NUMERIC
) RETURNS TABLE(tablename TEXT, size_gb NUMERIC) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.tablename::TEXT,
        (pg_total_relation_size(t.schemaname||'.'||t.tablename) / 1024.0^3)::NUMERIC as size_gb
    FROM pg_tables t
    WHERE t.tablename LIKE table_pattern
      AND pg_total_relation_size(t.schemaname||'.'||t.tablename) / 1024.0^3 > max_size_gb;
END;
$$ LANGUAGE plpgsql;

-- Check for oversized partitions
SELECT * FROM check_partition_size('orders_%', 50);
```

### 5. Regular Archival

```sql
-- Archive old partitions quarterly
DO $$
DECLARE
    cutoff_date DATE := CURRENT_DATE - INTERVAL '2 years';
    partition_record RECORD;
BEGIN
    FOR partition_record IN 
        SELECT tablename 
        FROM pg_tables 
        WHERE tablename LIKE 'orders_%'
          AND tablename < 'orders_' || TO_CHAR(cutoff_date, 'YYYY_MM')
    LOOP
        -- Detach partition
        EXECUTE format('ALTER TABLE orders DETACH PARTITION %I', partition_record.tablename);
        
        -- Archive to file
        EXECUTE format('COPY %I TO ''/archive/%I.csv'' WITH CSV HEADER', 
                      partition_record.tablename, partition_record.tablename);
        
        -- Drop partition
        EXECUTE format('DROP TABLE %I', partition_record.tablename);
        
        RAISE NOTICE 'Archived and dropped: %', partition_record.tablename;
    END LOOP;
END $$;
```

## Migration Strategies

### Converting Existing Table to Partitioned

```sql
-- 1. Create partitioned table
CREATE TABLE orders_partitioned (
    LIKE orders INCLUDING ALL
) PARTITION BY RANGE (order_date);

-- 2. Create partitions
CREATE TABLE orders_2024_q1 PARTITION OF orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');
-- ... create all needed partitions

-- 3. Copy data (can be done in batches)
INSERT INTO orders_partitioned 
SELECT * FROM orders 
WHERE order_date >= '2024-01-01' AND order_date < '2024-04-01';

-- 4. Verify data
SELECT COUNT(*) FROM orders;
SELECT COUNT(*) FROM orders_partitioned;

-- 5. Switch tables (in transaction)
BEGIN;
    ALTER TABLE orders RENAME TO orders_old;
    ALTER TABLE orders_partitioned RENAME TO orders;
    -- Update sequences, grants, etc.
COMMIT;

-- 6. Drop old table
DROP TABLE orders_old;
```

### Zero-Downtime Migration

```sql
-- Use logical replication or triggers to keep tables in sync
-- Then switch atomically
```

## Common Pitfalls

1. **Not including partition key in unique constraints**: Causes error
2. **Too many small partitions**: High overhead
3. **Forgetting to create future partitions**: Runtime errors
4. **Not pruning old partitions**: Unbounded growth
5. **Missing indexes on partitions**: Slow queries
6. **Querying without partition key**: No pruning benefit
7. **Using wrong partition type**: Hash when range would be better
8. **Not monitoring partition sizes**: Performance degradation

## Summary

PostgreSQL partitioning provides:
- **Performance**: Faster queries through partition pruning
- **Maintainability**: Easy archival and deletion of old data
- **Scalability**: Distribute large tables across multiple physical partitions
- **Flexibility**: Range, list, hash, and multi-level partitioning

Use partitioning for large tables with natural partition keys and time-series data.

## Next Steps

- Learn about [Query Optimization](./20-query-optimization.md)
- Explore [Index Optimization](./22-index-optimization.md)
- Study [Vacuuming and Maintenance](./24-vacuuming-and-maintenance.md)
- Practice [Tablespaces](./44-tablespaces.md) for partition placement
