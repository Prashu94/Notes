# Logical Replication

## Overview

Logical replication in PostgreSQL replicates data at a higher level than physical replication, enabling selective replication of tables, schema changes during replication, cross-version replication, and multi-directional replication. This comprehensive guide covers logical replication setup, publications, subscriptions, conflict resolution, monitoring, and advanced use cases.

## Table of Contents

- [Logical vs Physical Replication](#logical-vs-physical-replication)
- [Publications](#publications)
- [Subscriptions](#subscriptions)
- [Setting Up Logical Replication](#setting-up-logical-replication)
- [Conflict Resolution](#conflict-resolution)
- [Monitoring Logical Replication](#monitoring-logical-replication)
- [Advanced Use Cases](#advanced-use-cases)
- [Performance Tuning](#performance-tuning)
- [Best Practices](#best-practices)

## Logical vs Physical Replication

### Comparison

```sql
-- Physical Replication (Streaming Replication)
-- - Replicates entire database cluster (all databases)
-- - Block-level replication (WAL shipping)
-- - Standby is exact copy of primary
-- - Read-only standby (hot standby)
-- - Same PostgreSQL version required
-- - Cannot write to standby
-- - Use case: High availability, disaster recovery

-- Logical Replication
-- - Replicates specific tables/databases
-- - Row-level replication (logical decoding)
-- - Subscriber can have different schema
-- - Subscriber is read-write (can have own data)
-- - Different PostgreSQL versions supported (upgrade path)
-- - Bi-directional replication possible
-- - Use case: Selective replication, data distribution, upgrades

/*
+------------------------+-------------------------+------------------------+
| Feature                | Physical Replication   | Logical Replication    |
+------------------------+-------------------------+------------------------+
| Granularity            | Entire cluster         | Individual tables      |
| Replication Level      | Block-level (WAL)      | Row-level (SQL)        |
| Standby Writable       | No (read-only)         | Yes (read-write)       |
| Cross-Version          | No                     | Yes                    |
| Schema Changes         | Automatic              | Manual (DDL not replic)|
| Selective Tables       | No                     | Yes                    |
| Conflict Detection     | N/A                    | Manual handling needed |
| Performance            | Faster                 | Slower                 |
| Network Bandwidth      | Higher                 | Lower                  |
| Use Cases              | HA, DR                 | Data distribution,     |
|                        |                        | upgrades, analytics    |
+------------------------+-------------------------+------------------------+
*/

-- Architecture differences:

-- Physical Replication:
-- Primary --> WAL Files --> Standby
-- (All databases, all tables, all changes)

-- Logical Replication:
-- Publisher (Primary) --> Logical Decoding --> Replication Slot --> Subscriber
-- (Selected tables only, row-level changes)
```

### Logical Replication Features

```sql
-- Key features of logical replication:

-- 1. Table-level granularity
-- Replicate specific tables, not entire database

-- 2. Multiple publishers to one subscriber
-- Consolidate data from multiple sources

-- 3. Multiple subscribers to one publisher
-- Distribute data to multiple targets

-- 4. Bi-directional replication (with conflict handling)
-- Write to both nodes

-- 5. Cross-version support
-- Upgrade PostgreSQL with minimal downtime

-- 6. Filtering
-- Replicate subset of rows (WHERE clause)

-- 7. Column filtering (PostgreSQL 15+)
-- Replicate specific columns only

-- 8. Initial data synchronization
-- Automatic initial table copy

-- 9. DDL not replicated automatically
-- Schema changes must be applied manually

-- 10. Subscriber is writable
-- Can have additional tables, indexes, etc.
```

## Publications

### Creating Publications

```sql
-- Publications: Define what to replicate from publisher (source)

-- Check configuration (postgresql.conf)
-- wal_level = logical (required for logical replication)
-- max_replication_slots = 10 (at least number of subscribers)
-- max_wal_senders = 10 (at least number of subscribers)

SHOW wal_level;  -- Should be 'logical'

-- Create publication for all tables
CREATE PUBLICATION all_tables_pub FOR ALL TABLES;

-- Create publication for specific tables
CREATE PUBLICATION users_orders_pub FOR TABLE users, orders;

-- Create publication with WHERE clause (row filtering)
CREATE PUBLICATION active_users_pub FOR TABLE users WHERE (active = true);

-- Create publication with column list (PostgreSQL 15+)
CREATE PUBLICATION users_basic_pub FOR TABLE users (id, username, email);
-- Only replicates specified columns

-- Create publication for partitioned table
CREATE PUBLICATION sales_pub FOR TABLE sales;
-- Replicates all partitions automatically

-- Create publication with specific operations
CREATE PUBLICATION insert_only_pub FOR TABLE logs
    WITH (publish = 'insert');
-- Only INSERT operations replicated

CREATE PUBLICATION updates_deletes_pub FOR TABLE products
    WITH (publish = 'update, delete');
-- Only UPDATE and DELETE operations

-- Default: publish = 'insert, update, delete, truncate'

-- View publications
SELECT * FROM pg_publication;

-- View publication tables
SELECT * FROM pg_publication_tables;

-- View publication details
\dRp+  -- In psql

-- Check publication for specific table
SELECT pubname
FROM pg_publication_tables
WHERE tablename = 'users';
```

### Managing Publications

```sql
-- Add table to publication
ALTER PUBLICATION users_orders_pub ADD TABLE products;

-- Remove table from publication
ALTER PUBLICATION users_orders_pub DROP TABLE products;

-- Change publication options
ALTER PUBLICATION users_orders_pub SET (publish = 'insert, update');

-- Add table with WHERE clause
ALTER PUBLICATION active_users_pub
    SET TABLE users WHERE (active = true AND created_at > '2024-01-01');

-- Rename publication
ALTER PUBLICATION users_orders_pub RENAME TO main_pub;

-- Change owner
ALTER PUBLICATION main_pub OWNER TO new_owner;

-- Drop publication
DROP PUBLICATION main_pub;

-- Drop with cascade (removes subscriber dependencies)
DROP PUBLICATION main_pub CASCADE;

-- View publication details with table list
SELECT
    p.pubname,
    p.pubowner::regrole AS owner,
    p.puballtables,
    p.pubinsert,
    p.pubupdate,
    p.pubdelete,
    p.pubtruncate,
    COALESCE(
        (SELECT string_agg(tablename, ', ')
         FROM pg_publication_tables pt
         WHERE pt.pubname = p.pubname),
        'ALL TABLES'
    ) AS tables
FROM pg_publication p
ORDER BY p.pubname;
```

## Subscriptions

### Creating Subscriptions

```sql
-- Subscriptions: Define what to receive on subscriber (target)

-- On subscriber database:

-- Create subscription
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser password=secret'
    PUBLICATION all_tables_pub;

-- Create subscription with options
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser'
    PUBLICATION users_orders_pub
    WITH (
        copy_data = true,          -- Copy initial data (default: true)
        create_slot = true,        -- Create replication slot (default: true)
        enabled = true,            -- Enable immediately (default: true)
        slot_name = 'my_slot',     -- Custom slot name
        synchronous_commit = off   -- Async commit for better performance
    );

-- Create subscription without initial data copy
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser'
    PUBLICATION users_orders_pub
    WITH (copy_data = false);

-- Create disabled subscription (enable later)
CREATE SUBSCRIPTION my_subscription
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser'
    PUBLICATION users_orders_pub
    WITH (enabled = false);

-- Enable subscription
ALTER SUBSCRIPTION my_subscription ENABLE;

-- Subscribe to multiple publications
CREATE SUBSCRIPTION multi_pub_sub
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser'
    PUBLICATION pub1, pub2, pub3;

-- View subscriptions
SELECT * FROM pg_subscription;

-- View subscription details
\dRs+  -- In psql

-- Check subscription state
SELECT
    subname AS subscription_name,
    subenabled AS enabled,
    subconninfo AS connection_info,
    subpublications AS publications,
    subslotname AS slot_name
FROM pg_subscription;
```

### Managing Subscriptions

```sql
-- Disable subscription (stops replication)
ALTER SUBSCRIPTION my_subscription DISABLE;

-- Re-enable subscription
ALTER SUBSCRIPTION my_subscription ENABLE;

-- Refresh subscription (resync table list from publication)
ALTER SUBSCRIPTION my_subscription REFRESH PUBLICATION;

-- Change connection string
ALTER SUBSCRIPTION my_subscription
    CONNECTION 'host=new_publisher_host port=5432 dbname=sourcedb user=repuser';

-- Change publications
ALTER SUBSCRIPTION my_subscription
    SET PUBLICATION new_pub1, new_pub2;

-- Skip transaction (if replication stuck on error)
ALTER SUBSCRIPTION my_subscription SKIP (lsn = '0/12345678');

-- Drop subscription
DROP SUBSCRIPTION my_subscription;

-- Drop subscription but keep slot on publisher (manual cleanup needed)
ALTER SUBSCRIPTION my_subscription SET (slot_name = NONE);
DROP SUBSCRIPTION my_subscription;

-- View subscription workers
SELECT
    subname,
    pid,
    leader_pid,
    relid::regclass AS table_name,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time
FROM pg_stat_subscription;

-- Check subscription lag
SELECT
    subname,
    pg_wal_lsn_diff(latest_end_lsn, received_lsn) AS lag_bytes,
    EXTRACT(EPOCH FROM (NOW() - last_msg_receipt_time)) AS lag_seconds
FROM pg_stat_subscription;
```

## Setting Up Logical Replication

### Step-by-Step Setup

```sql
-- === PUBLISHER SETUP ===

-- 1. Configure postgresql.conf on publisher
-- wal_level = logical
-- max_replication_slots = 10
-- max_wal_senders = 10

-- Restart PostgreSQL after config change
-- sudo systemctl restart postgresql

-- 2. Create replication user on publisher
CREATE USER repuser WITH REPLICATION PASSWORD 'secure_password';

-- 3. Configure pg_hba.conf on publisher to allow subscriber connection
-- host    all    repuser    subscriber_ip/32    md5

-- Reload PostgreSQL
-- SELECT pg_reload_conf();

-- 4. Grant permissions to replication user
GRANT SELECT ON ALL TABLES IN SCHEMA public TO repuser;
GRANT USAGE ON SCHEMA public TO repuser;

-- For future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT ON TABLES TO repuser;

-- 5. Create publication
CREATE PUBLICATION my_pub FOR TABLE users, orders;

-- Verify publication
SELECT * FROM pg_publication WHERE pubname = 'my_pub';
SELECT * FROM pg_publication_tables WHERE pubname = 'my_pub';

-- === SUBSCRIBER SETUP ===

-- 1. Create database on subscriber (if needed)
CREATE DATABASE targetdb;

-- 2. Create tables with same structure as publisher
-- Option A: Use pg_dump to copy schema
-- On publisher:
-- pg_dump -s -t users -t orders sourcedb > schema.sql
-- On subscriber:
-- psql targetdb < schema.sql

-- Option B: Manually create tables
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100)
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT,
    order_date DATE,
    total NUMERIC
);

-- 3. Create subscription
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=publisher_host port=5432 dbname=sourcedb user=repuser password=secure_password'
    PUBLICATION my_pub;

-- 4. Verify subscription
SELECT * FROM pg_subscription WHERE subname = 'my_sub';

-- 5. Check replication status
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_receipt_time
FROM pg_stat_subscription;

-- 6. Check replication slot on publisher
SELECT
    slot_name,
    plugin,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn
FROM pg_replication_slots;

-- === TEST REPLICATION ===

-- On publisher, insert data
INSERT INTO users (username, email) VALUES ('alice', 'alice@example.com');
INSERT INTO orders (user_id, order_date, total) VALUES (1, '2024-01-01', 100);

-- On subscriber, verify data appears
SELECT * FROM users;
SELECT * FROM orders;
-- Data should replicate within seconds
```

### Troubleshooting Setup

```sql
-- Check if wal_level is logical
SHOW wal_level;
-- If not 'logical', update postgresql.conf and restart

-- Check replication slots
SELECT * FROM pg_replication_slots;
-- Should see slot for each subscription

-- Check subscription state
SELECT
    subname,
    subenabled,
    subconninfo,
    subslotname
FROM pg_subscription;

-- Check subscription worker processes
SELECT * FROM pg_stat_subscription;
-- Should see active workers

-- Check for replication errors
SELECT * FROM pg_stat_subscription WHERE last_msg_receipt_time < NOW() - INTERVAL '5 minutes';
-- Indicates potential issue if lag is high

-- View subscription worker logs
-- Check PostgreSQL logs for errors like:
-- "logical replication worker for subscription ... has started"
-- "could not connect to publisher"

-- Common issues:
-- 1. wal_level not set to logical
-- 2. pg_hba.conf doesn't allow connection
-- 3. Replication user lacks permissions
-- 4. Tables don't exist on subscriber
-- 5. Network connectivity issues
-- 6. Firewall blocking connection
```

## Conflict Resolution

### Handling Conflicts

```sql
-- Conflicts occur when same row modified on publisher and subscriber
-- (only possible with bi-directional replication or manual changes on subscriber)

-- Conflict types:
-- 1. INSERT conflict: Row with same primary key exists
-- 2. UPDATE conflict: Row to update doesn't exist
-- 3. DELETE conflict: Row to delete doesn't exist

-- Default conflict resolution: Last write wins (timestamp-based)

-- Conflict handling strategies:

-- Strategy 1: Prevent conflicts (recommended)
-- - Don't write to subscriber tables that are replicated
-- - Use triggers to prevent writes
CREATE OR REPLACE FUNCTION prevent_direct_writes()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Direct writes to replicated table not allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER prevent_writes_trigger
    BEFORE INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW
    WHEN (current_setting('session_replication_role') = 'origin')
    EXECUTE FUNCTION prevent_direct_writes();

-- Strategy 2: Detect conflicts
-- Add timestamp column for conflict detection
ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();

CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_timestamp_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_timestamp();

-- Strategy 3: Log conflicts
CREATE TABLE replication_conflicts (
    id SERIAL PRIMARY KEY,
    table_name TEXT,
    conflict_type TEXT,
    detected_at TIMESTAMP DEFAULT NOW(),
    details JSONB
);

-- Strategy 4: Manual conflict resolution
-- When conflict detected, subscription stops
-- Check pg_stat_subscription for errors
SELECT
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time
FROM pg_stat_subscription;

-- View conflict in logs
-- PostgreSQL logs will show: "duplicate key value violates unique constraint"

-- Resolve conflict manually:
-- Option A: Fix data on subscriber
DELETE FROM users WHERE id = 123;  -- Remove conflicting row

-- Option B: Skip conflicting transaction
ALTER SUBSCRIPTION my_sub SKIP (lsn = 'X/XXXXXXXX');
-- Get LSN from error message in logs

-- Subscription resumes automatically after resolution

-- Strategy 5: Bi-directional replication conflicts
-- Use conflict detection columns
ALTER TABLE users ADD COLUMN node_id INT DEFAULT 1;
ALTER TABLE users ADD COLUMN version INT DEFAULT 1;

-- On each write, increment version
UPDATE users SET data = 'new', version = version + 1 WHERE id = 1;

-- Conflict resolution: Higher version wins
-- Requires custom conflict resolution logic
```

### Conflict Detection Queries

```sql
-- Find INSERT conflicts (duplicate keys)
-- Run on subscriber
SELECT
    schemaname,
    tablename,
    indexname
FROM pg_stat_user_tables t
JOIN pg_stat_user_indexes i USING (relid)
WHERE idx_scan = 0  -- Index never used for scan
AND indexrelname LIKE '%_pkey';

-- Detect stuck subscriptions (potential conflicts)
SELECT
    subname,
    EXTRACT(EPOCH FROM (NOW() - last_msg_receipt_time)) AS seconds_since_last_msg
FROM pg_stat_subscription
WHERE EXTRACT(EPOCH FROM (NOW() - last_msg_receipt_time)) > 60;
-- If > 60 seconds with no message, investigate

-- Monitor subscription state
SELECT
    s.subname,
    s.subenabled,
    ss.pid,
    ss.received_lsn,
    ss.latest_end_lsn,
    pg_wal_lsn_diff(ss.latest_end_lsn, ss.received_lsn) AS lag_bytes
FROM pg_subscription s
LEFT JOIN pg_stat_subscription ss ON s.oid = ss.subid;

-- Check for replication errors in logs
-- grep "ERROR" /var/log/postgresql/postgresql-*.log | grep "logical replication"
```

## Monitoring Logical Replication

### Monitoring Queries

```sql
-- Monitor publications
SELECT
    p.pubname,
    p.pubowner::regrole AS owner,
    p.puballtables,
    COUNT(pt.tablename) AS table_count
FROM pg_publication p
LEFT JOIN pg_publication_tables pt ON p.pubname = pt.pubname
GROUP BY p.pubname, p.pubowner, p.puballtables;

-- Monitor subscriptions
SELECT
    s.subname,
    s.subenabled AS enabled,
    s.subconninfo AS connection,
    array_to_string(s.subpublications, ', ') AS publications,
    s.subslotname AS slot_name
FROM pg_subscription s;

-- Monitor replication lag (on subscriber)
SELECT
    subname AS subscription,
    pg_size_pretty(pg_wal_lsn_diff(latest_end_lsn, received_lsn)) AS lag_size,
    EXTRACT(EPOCH FROM (NOW() - last_msg_receipt_time)) AS lag_seconds,
    last_msg_receipt_time
FROM pg_stat_subscription;

-- Monitor replication slots (on publisher)
SELECT
    slot_name,
    plugin,
    slot_type,
    active,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_wal,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), confirmed_flush_lsn)) AS pending_wal
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- Monitor subscription workers (on subscriber)
SELECT
    subname,
    pid,
    relid::regclass AS table_name,
    received_lsn,
    latest_end_lsn,
    last_msg_send_time,
    last_msg_receipt_time
FROM pg_stat_subscription;

-- Check WAL sender processes (on publisher)
SELECT
    pid,
    usename,
    application_name,
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    sync_state
FROM pg_stat_replication
WHERE application_name LIKE '%subscription%';

-- Alert on high lag
SELECT
    subname,
    pg_wal_lsn_diff(latest_end_lsn, received_lsn) AS lag_bytes
FROM pg_stat_subscription
WHERE pg_wal_lsn_diff(latest_end_lsn, received_lsn) > 10485760;  -- > 10 MB
-- Alert if lag exceeds threshold

-- Monitor replication throughput
SELECT
    subname,
    relid::regclass AS table_name,
    received_lsn,
    latest_end_lsn
FROM pg_stat_subscription;
-- Track LSN changes over time to measure throughput
```

### Performance Metrics

```sql
-- Create monitoring table
CREATE TABLE logical_replication_metrics (
    recorded_at TIMESTAMP DEFAULT NOW(),
    subscription_name TEXT,
    lag_bytes BIGINT,
    lag_seconds NUMERIC,
    received_lsn PG_LSN,
    latest_end_lsn PG_LSN
);

-- Collect metrics periodically (e.g., every minute via cron)
INSERT INTO logical_replication_metrics (subscription_name, lag_bytes, lag_seconds, received_lsn, latest_end_lsn)
SELECT
    subname,
    pg_wal_lsn_diff(latest_end_lsn, received_lsn),
    EXTRACT(EPOCH FROM (NOW() - last_msg_receipt_time)),
    received_lsn,
    latest_end_lsn
FROM pg_stat_subscription;

-- Analyze lag trends
SELECT
    subscription_name,
    DATE_TRUNC('hour', recorded_at) AS hour,
    AVG(lag_bytes) AS avg_lag_bytes,
    MAX(lag_bytes) AS max_lag_bytes,
    AVG(lag_seconds) AS avg_lag_seconds
FROM logical_replication_metrics
WHERE recorded_at > NOW() - INTERVAL '24 hours'
GROUP BY subscription_name, hour
ORDER BY hour DESC;
```

## Advanced Use Cases

### Multi-Master Replication

```sql
-- Bi-directional replication (multi-master)
-- Warning: Requires careful conflict handling!

-- === NODE 1 (Master 1) ===
-- Create publication
CREATE PUBLICATION node1_pub FOR TABLE shared_table;

-- Create subscription to Node 2
CREATE SUBSCRIPTION node1_sub
    CONNECTION 'host=node2_host port=5432 dbname=db user=repuser'
    PUBLICATION node2_pub;

-- === NODE 2 (Master 2) ===
-- Create publication
CREATE PUBLICATION node2_pub FOR TABLE shared_table;

-- Create subscription to Node 1
CREATE SUBSCRIPTION node2_sub
    CONNECTION 'host=node1_host port=5432 dbname=db user=repuser'
    PUBLICATION node1_pub;

-- Conflict prevention: Add node_id to identify origin
ALTER TABLE shared_table ADD COLUMN origin_node INT;

-- On Node 1, set origin_node = 1 for all writes
-- On Node 2, set origin_node = 2 for all writes

-- Conflict resolution: Use application logic or timestamps
ALTER TABLE shared_table ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();
ALTER TABLE shared_table ADD COLUMN updated_by_node INT;

-- Note: PostgreSQL doesn't automatically resolve conflicts
-- Requires custom conflict detection and resolution logic
```

### Consolidation Pattern

```sql
-- Multiple publishers to single subscriber
-- Use case: Data warehousing, analytics

-- === PUBLISHER 1 (Region: US) ===
CREATE PUBLICATION us_sales_pub FOR TABLE sales;

-- === PUBLISHER 2 (Region: EU) ===
CREATE PUBLICATION eu_sales_pub FOR TABLE sales;

-- === PUBLISHER 3 (Region: ASIA) ===
CREATE PUBLICATION asia_sales_pub FOR TABLE sales;

-- === SUBSCRIBER (Data Warehouse) ===
-- Create partitioned table
CREATE TABLE sales (
    id SERIAL,
    region VARCHAR(10),
    amount NUMERIC,
    sale_date DATE
) PARTITION BY LIST (region);

CREATE TABLE sales_us PARTITION OF sales FOR VALUES IN ('US');
CREATE TABLE sales_eu PARTITION OF sales FOR VALUES IN ('EU');
CREATE TABLE sales_asia PARTITION OF sales FOR VALUES IN ('ASIA');

-- Subscribe to all regions
CREATE SUBSCRIPTION us_sales_sub
    CONNECTION 'host=us_publisher port=5432 dbname=salesdb user=repuser'
    PUBLICATION us_sales_pub
    WITH (copy_data = true, create_slot = true, enabled = true);

CREATE SUBSCRIPTION eu_sales_sub
    CONNECTION 'host=eu_publisher port=5432 dbname=salesdb user=repuser'
    PUBLICATION eu_sales_pub
    WITH (copy_data = true, create_slot = true, enabled = true);

CREATE SUBSCRIPTION asia_sales_sub
    CONNECTION 'host=asia_publisher port=5432 dbname=salesdb user=repuser'
    PUBLICATION asia_sales_pub
    WITH (copy_data = true, create_slot = true, enabled = true);

-- Data from all regions consolidated into single data warehouse
```

### Distribution Pattern

```sql
-- Single publisher to multiple subscribers
-- Use case: Data distribution, caching, read replicas

-- === PUBLISHER (Central Database) ===
CREATE PUBLICATION central_pub FOR TABLE products, inventory;

-- === SUBSCRIBER 1 (Region: US) ===
CREATE SUBSCRIPTION us_replica_sub
    CONNECTION 'host=central_host port=5432 dbname=centraldb user=repuser'
    PUBLICATION central_pub;

-- === SUBSCRIBER 2 (Region: EU) ===
CREATE SUBSCRIPTION eu_replica_sub
    CONNECTION 'host=central_host port=5432 dbname=centraldb user=repuser'
    PUBLICATION central_pub;

-- === SUBSCRIBER 3 (Region: ASIA) ===
CREATE SUBSCRIPTION asia_replica_sub
    CONNECTION 'host=central_host port=5432 dbname=centraldb user=repuser'
    PUBLICATION central_pub;

-- All regions have synchronized copy of central data
-- Can serve reads locally, reducing latency
```

## Performance Tuning

### Optimizing Logical Replication

```sql
-- 1. Tune max_replication_slots and max_wal_senders
-- postgresql.conf on publisher
-- max_replication_slots = 20  -- At least one per subscriber
-- max_wal_senders = 20         -- At least one per subscriber

-- 2. Tune wal_sender_timeout
-- wal_sender_timeout = 60s     -- Timeout for WAL sender

-- 3. Use asynchronous commit on subscriber
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=publisher port=5432 dbname=sourcedb user=repuser'
    PUBLICATION my_pub
    WITH (synchronous_commit = off);
-- Improves throughput, slight durability tradeoff

-- 4. Optimize initial data copy
-- For large tables, consider manual initial copy
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=publisher port=5432 dbname=sourcedb user=repuser'
    PUBLICATION my_pub
    WITH (copy_data = false);  -- Skip automatic copy

-- Then manually copy data (faster):
-- pg_dump -t users sourcedb | psql targetdb

-- 5. Monitor and cleanup old replication slots
SELECT
    slot_name,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_wal_bytes
FROM pg_replication_slots
WHERE NOT active;

-- Drop inactive slots to free WAL
SELECT pg_drop_replication_slot('unused_slot');

-- 6. Tune parallel workers (PostgreSQL 16+)
-- ALTER SUBSCRIPTION my_sub SET (streaming = parallel);

-- 7. Optimize network
-- Use compression for remote subscribers
-- ALTER SUBSCRIPTION my_sub CONNECTION 'host=... sslcompression=1';

-- 8. Batch changes when possible
-- Instead of: INSERT INTO users VALUES (1, 'Alice'); (repeated 1000 times)
-- Use: INSERT INTO users SELECT * FROM source_data;
-- Reduces replication overhead

-- 9. Monitor replication lag and adjust
SELECT
    subname,
    pg_wal_lsn_diff(latest_end_lsn, received_lsn) AS lag_bytes
FROM pg_stat_subscription
WHERE pg_wal_lsn_diff(latest_end_lsn, received_lsn) > 10485760;
-- If lag consistently high, investigate bottleneck
```

## Best Practices

### Best Practices Checklist

```text
Logical Replication Best Practices:

1. Planning
   ✓ Define replication topology (publisher/subscriber, bi-directional)
   ✓ Identify tables to replicate
   ✓ Plan conflict resolution strategy
   ✓ Document architecture

2. Setup
   ✓ Set wal_level = logical on publisher
   ✓ Configure max_replication_slots and max_wal_senders
   ✓ Create dedicated replication user
   ✓ Configure pg_hba.conf for replication connections

3. Security
   ✓ Use strong passwords for replication users
   ✓ Use SSL for replication connections
   ✓ Grant minimal permissions (SELECT only for replicated tables)
   ✓ Regularly rotate credentials

4. Schema Management
   ✓ Apply DDL changes to subscriber manually (not automatic)
   ✓ Test schema changes in dev environment first
   ✓ Coordinate DDL changes with replication maintenance window
   ✓ Document schema change procedures

5. Conflict Handling
   ✓ Prevent conflicts when possible (read-only subscriber)
   ✓ Add timestamps and version columns for detection
   ✓ Monitor for conflicts regularly
   ✓ Have manual resolution procedures documented

6. Monitoring
   ✓ Monitor replication lag (lag_bytes, lag_seconds)
   ✓ Alert on high lag or stopped replication
   ✓ Monitor WAL disk usage on publisher
   ✓ Track subscription state

7. Performance
   ✓ Use asynchronous commit on subscriber
   ✓ Optimize initial data copy for large tables
   ✓ Clean up inactive replication slots
   ✓ Monitor network bandwidth

8. Maintenance
   ✓ Regular backups of both publisher and subscriber
   ✓ Test failover procedures
   ✓ Monitor disk space (WAL files can accumulate)
   ✓ Schedule maintenance windows for schema changes

9. Disaster Recovery
   ✓ Document recovery procedures
   ✓ Test restoring subscriber from backup
   ✓ Have rollback plan for replication setup
   ✓ Monitor replication health continuously

10. Testing
    ✓ Test replication in dev/staging before production
    ✓ Test conflict scenarios
    ✓ Test failover and recovery
    ✓ Load test to ensure adequate performance

Common Mistakes to Avoid:
✗ Not setting wal_level to logical
✗ Forgetting to apply DDL changes to subscriber
✗ Not monitoring replication lag
✗ Not cleaning up inactive replication slots
✗ Writing to subscriber tables without conflict handling
✗ Not testing failover procedures
✗ Insufficient monitoring and alerting
✗ Not planning for conflicts in bi-directional setups
✗ Not documenting replication topology
✗ Ignoring WAL disk space consumption
```

## Summary

Logical replication enables flexible, selective data replication:

- **Purpose**: Replicate specific tables, cross-version upgrades, data distribution, multi-master
- **Publications**: Define what to replicate (tables, operations, row filters)
- **Subscriptions**: Define what to receive and from where
- **Setup**: wal_level=logical, publications on publisher, subscriptions on subscriber
- **Conflicts**: Occur in bi-directional replication, requires manual resolution
- **Monitoring**: Track lag (bytes, seconds), subscription state, replication slots
- **Use Cases**: Data warehousing, read replicas, cross-region distribution, upgrades
- **Best Practices**: Plan topology, prevent conflicts, monitor lag, coordinate DDL changes

Logical replication complements physical replication for advanced replication scenarios.

## Next Steps

- Study [Physical Replication](./36-replication.md)
- Learn [High Availability](./37-high-availability.md)
- Explore [Backup and Recovery](./35-backup-and-recovery.md)
- Practice [Performance Tuning](./34-configuration-and-tuning.md)
