# Replication

## Overview

PostgreSQL replication provides database redundancy, high availability, and load distribution. This comprehensive guide covers streaming replication, logical replication, synchronous/asynchronous modes, cascading replication, and monitoring replication health.

## Table of Contents
- [Replication Basics](#replication-basics)
- [Streaming Replication](#streaming-replication)
- [Logical Replication](#logical-replication)
- [Synchronous Replication](#synchronous-replication)
- [Cascading Replication](#cascading-replication)
- [Replication Slots](#replication-slots)
- [Monitoring Replication](#monitoring-replication)
- [Failover and Switchover](#failover-and-switchover)
- [Conflict Resolution](#conflict-resolution)
- [Replication Best Practices](#replication-best-practices)

## Replication Basics

### Types of Replication

```sql
-- PostgreSQL replication types:

-- 1. Physical Replication (Streaming Replication)
-- - Byte-by-byte copy of data files
-- - Entire cluster replication
-- - Read-only standby
-- - Very fast, low overhead
-- - All databases replicated

-- 2. Logical Replication
-- - Row-level replication
-- - Selective (specific tables/databases)
-- - Standby can accept writes (to different tables)
-- - Higher overhead
-- - Requires primary key on tables

-- 3. File-Based Log Shipping
-- - Archive WAL files to standby
-- - Restore WAL files on standby
-- - Higher latency
-- - Simpler setup

-- Comparison table
CREATE TABLE replication_comparison (
    feature TEXT,
    physical_replication TEXT,
    logical_replication TEXT
);

INSERT INTO replication_comparison VALUES
    ('Granularity', 'Entire cluster', 'Per table/database'),
    ('Standby writes', 'Read-only', 'Allowed (different tables)'),
    ('Performance', 'Very fast', 'Moderate'),
    ('Version compatibility', 'Same major version', 'Cross-version supported'),
    ('DDL replication', 'Yes', 'No (manual)'),
    ('Use case', 'HA, read replicas', 'Partial replication, upgrades');

SELECT * FROM replication_comparison;
```

### Replication Terminology

```sql
-- Key terms:

-- Primary (Master): Source database accepting writes
-- Standby (Replica, Secondary): Copy receiving changes
-- WAL: Write-Ahead Log containing all changes
-- Streaming: Real-time WAL transmission
-- Hot Standby: Standby accepting read queries
-- Warm Standby: Standby not accepting queries
-- Cascading: Standby replicating to another standby
-- Replication Lag: Time/data difference between primary and standby
-- Failover: Promote standby to primary (unplanned)
-- Switchover: Planned failover
-- Synchronous: Wait for standby confirmation
-- Asynchronous: Don't wait for standby
```

## Streaming Replication

### Setting Up Streaming Replication

```sql
-- Primary Server Configuration:

-- 1. Create replication user
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'strong_replication_password';

-- 2. Configure postgresql.conf
ALTER SYSTEM SET wal_level = replica;  -- Or 'logical' for logical replication
ALTER SYSTEM SET max_wal_senders = 10;  -- Max concurrent replication connections
ALTER SYSTEM SET wal_keep_size = '1GB';  -- Keep WAL for lagging standbys (optional)
ALTER SYSTEM SET max_replication_slots = 10;  -- For replication slots (recommended)
ALTER SYSTEM SET hot_standby = on;  -- Allow queries on standby

-- Restart required
-- $ pg_ctl restart

-- 3. Configure pg_hba.conf (allow replication connections)
-- Add line:
-- host replication replicator 10.0.1.0/24 scram-sha-256
-- Or for specific standby:
-- host replication replicator 10.0.1.50/32 scram-sha-256

-- Reload pg_hba.conf
SELECT pg_reload_conf();

-- 4. Create replication slot (recommended)
SELECT pg_create_physical_replication_slot('standby_slot1');

-- Verify configuration
SHOW wal_level;
SHOW max_wal_senders;
SHOW hot_standby;

-- View replication slots
SELECT slot_name, slot_type, active FROM pg_replication_slots;
```

### Standby Server Setup

```sql
-- Standby Server Configuration:

-- Method 1: Using pg_basebackup (recommended)

-- 1. On standby server, create base backup from primary
-- $ pg_basebackup -h primary_host -D /var/lib/postgresql/data -U replicator -P -v -R -X stream -C -S standby_slot1

-- Options explained:
-- -h primary_host: Primary server hostname
-- -D /var/lib/postgresql/data: Data directory
-- -U replicator: Replication user
-- -P: Show progress
-- -v: Verbose
-- -R: Write standby.signal and minimal recovery config
-- -X stream: Include WAL files
-- -C: Create replication slot
-- -S standby_slot1: Replication slot name

-- 2. pg_basebackup automatically creates:
-- - standby.signal file (marks server as standby)
-- - postgresql.auto.conf with primary_conninfo

-- 3. If needed, customize postgresql.conf
-- ALTER SYSTEM SET hot_standby = on;
-- ALTER SYSTEM SET primary_conninfo = 'host=primary_host port=5432 user=replicator password=strong_password application_name=standby1';
-- ALTER SYSTEM SET primary_slot_name = 'standby_slot1';

-- 4. Start standby
-- $ pg_ctl start

-- Method 2: Manual setup

-- 1. Stop standby if running
-- $ pg_ctl stop

-- 2. Remove existing data
-- $ rm -rf /var/lib/postgresql/data/*

-- 3. Create base backup
-- $ pg_basebackup -h primary_host -D /var/lib/postgresql/data -U replicator -X stream

-- 4. Create standby.signal
-- $ touch /var/lib/postgresql/data/standby.signal

-- 5. Configure replication in postgresql.auto.conf
-- $ echo "primary_conninfo = 'host=primary_host port=5432 user=replicator password=password'" >> /var/lib/postgresql/data/postgresql.auto.conf
-- $ echo "primary_slot_name = 'standby_slot1'" >> /var/lib/postgresql/data/postgresql.auto.conf

-- 6. Start standby
-- $ pg_ctl start

-- Verify standby is in recovery mode
SELECT pg_is_in_recovery();  -- Should return true
```

### Testing Replication

```sql
-- On Primary:

-- Create test data
CREATE TABLE replication_test (
    id SERIAL PRIMARY KEY,
    data TEXT,
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO replication_test (data) VALUES ('Test data 1'), ('Test data 2');

-- Check current WAL position
SELECT pg_current_wal_lsn();

-- View active replication connections
SELECT 
    client_addr,
    application_name,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes
FROM pg_stat_replication;

-- On Standby:

-- Verify data replicated
SELECT * FROM replication_test;

-- Check replay position
SELECT pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();

-- Check replication lag
SELECT 
    now() - pg_last_xact_replay_timestamp() AS replication_lag_time,
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as lag_bytes;

-- Standby should be read-only
-- This should fail:
INSERT INTO replication_test (data) VALUES ('This will fail');
-- ERROR: cannot execute INSERT in a read-only transaction
```

## Logical Replication

### Setting Up Logical Replication

```sql
-- Logical replication allows selective table replication

-- On Publisher (Primary):

-- 1. Set wal_level to logical
ALTER SYSTEM SET wal_level = logical;
-- Restart required
-- $ pg_ctl restart

-- 2. Create publication for specific tables
CREATE PUBLICATION my_publication FOR TABLE users, orders;

-- Or for all tables in database
CREATE PUBLICATION all_tables_pub FOR ALL TABLES;

-- Or for specific schema
CREATE PUBLICATION schema_pub FOR ALL TABLES IN SCHEMA public;

-- Or with WHERE clause (filtered replication)
CREATE PUBLICATION active_users_pub FOR TABLE users WHERE (active = true);

-- View publications
SELECT * FROM pg_publication;

-- View tables in publication
SELECT * FROM pg_publication_tables WHERE pubname = 'my_publication';

-- On Subscriber (Standby):

-- 1. Create matching table structure
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    email TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    total NUMERIC(10,2),
    created_at TIMESTAMP DEFAULT now()
);

-- 2. Create subscription
CREATE SUBSCRIPTION my_subscription
CONNECTION 'host=publisher_host port=5432 dbname=mydb user=replication_user password=password'
PUBLICATION my_publication;

-- View subscriptions
SELECT * FROM pg_subscription;

-- View subscription status
SELECT * FROM pg_stat_subscription;

-- 3. Subscription automatically creates replication slot on publisher
-- Check on publisher:
SELECT slot_name, slot_type, active FROM pg_replication_slots;
```

### Managing Logical Replication

```sql
-- Add table to existing publication (on publisher)
ALTER PUBLICATION my_publication ADD TABLE products;

-- Remove table from publication
ALTER PUBLICATION my_publication DROP TABLE products;

-- Refresh subscription (on subscriber, after publication changes)
ALTER SUBSCRIPTION my_subscription REFRESH PUBLICATION;

-- Disable subscription temporarily
ALTER SUBSCRIPTION my_subscription DISABLE;

-- Enable subscription
ALTER SUBSCRIPTION my_subscription ENABLE;

-- Change subscription connection string
ALTER SUBSCRIPTION my_subscription CONNECTION 'host=new_publisher port=5432 dbname=mydb user=repl password=pass';

-- Drop subscription (on subscriber)
DROP SUBSCRIPTION my_subscription;

-- Drop publication (on publisher)
DROP PUBLICATION my_publication;

-- Monitor logical replication lag
SELECT 
    subname,
    pid,
    received_lsn,
    latest_end_lsn,
    pg_wal_lsn_diff(latest_end_lsn, received_lsn) as lag_bytes
FROM pg_stat_subscription;
```

### Logical Replication Use Cases

```sql
-- Use Case 1: Partial database replication
-- Replicate only critical tables

CREATE PUBLICATION critical_data FOR TABLE users, orders, payments;

-- Use Case 2: Cross-version upgrades
-- Replicate from PostgreSQL 13 to PostgreSQL 15
-- Logical replication works across major versions

-- Use Case 3: Multi-master (with caution)
-- Replicate different tables in different directions

-- On Server A: Publish users, Subscribe to orders
CREATE PUBLICATION users_pub FOR TABLE users;
CREATE SUBSCRIPTION orders_sub 
CONNECTION 'host=serverB ...' 
PUBLICATION orders_pub;

-- On Server B: Publish orders, Subscribe to users
CREATE PUBLICATION orders_pub FOR TABLE orders;
CREATE SUBSCRIPTION users_sub 
CONNECTION 'host=serverA ...' 
PUBLICATION users_pub;

-- Use Case 4: Data aggregation
-- Consolidate data from multiple databases

-- On Data Warehouse:
CREATE SUBSCRIPTION sales_east_sub 
CONNECTION 'host=east_server ...' 
PUBLICATION sales_pub;

CREATE SUBSCRIPTION sales_west_sub 
CONNECTION 'host=west_server ...' 
PUBLICATION sales_pub;

-- Use Case 5: Filtered replication
-- Replicate only specific rows

CREATE PUBLICATION premium_users_pub 
FOR TABLE users WHERE (subscription_tier = 'premium');
```

## Synchronous Replication

### Configuring Synchronous Replication

```sql
-- Synchronous replication waits for standby confirmation before commit
-- Ensures zero data loss but adds latency

-- On Primary:

-- 1. Configure synchronous standby names
ALTER SYSTEM SET synchronous_standby_names = 'standby1';
-- Or multiple standbys (FIRST 1 means wait for any 1 standby)
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 1 (standby1, standby2)';
-- Or ALL standbys
ALTER SYSTEM SET synchronous_standby_names = 'ANY 1 (standby1, standby2, standby3)';

-- Reload configuration
SELECT pg_reload_conf();

-- 2. Standby must set application_name in primary_conninfo
-- On Standby:
ALTER SYSTEM SET primary_conninfo = 'host=primary_host port=5432 user=replicator password=password application_name=standby1';
-- Restart standby
-- $ pg_ctl restart

-- Verify synchronous replication active
SELECT 
    application_name,
    client_addr,
    state,
    sync_state,  -- Should be 'sync' for synchronous
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn
FROM pg_stat_replication;

-- Test synchronous commit
-- On Primary:
INSERT INTO replication_test (data) VALUES ('Synchronous test');
-- This INSERT waits for standby confirmation before returning

-- Check sync state
SELECT sync_state FROM pg_stat_replication WHERE application_name = 'standby1';
-- Should show 'sync'
```

### Synchronous Commit Modes

```sql
-- Different synchronous commit levels

-- 1. synchronous_commit = off
-- Don't wait for WAL write (fastest, data loss on crash)
SET synchronous_commit = off;
INSERT INTO test VALUES (1);  -- Returns immediately

-- 2. synchronous_commit = local
-- Wait for local WAL write (default, crash-safe)
SET synchronous_commit = local;
INSERT INTO test VALUES (2);  -- Waits for local disk write

-- 3. synchronous_commit = remote_write
-- Wait for standby to write to OS (not flushed to disk)
SET synchronous_commit = remote_write;
INSERT INTO test VALUES (3);  -- Waits for standby OS write

-- 4. synchronous_commit = on (or remote_flush)
-- Wait for standby to flush to disk (safest)
SET synchronous_commit = on;
INSERT INTO test VALUES (4);  -- Waits for standby disk flush

-- 5. synchronous_commit = remote_apply
-- Wait for standby to apply changes (read-after-write consistency)
SET synchronous_commit = remote_apply;
INSERT INTO test VALUES (5);  -- Waits for standby to apply

-- View current setting
SHOW synchronous_commit;

-- Set per transaction
BEGIN;
SET LOCAL synchronous_commit = off;
INSERT INTO bulk_load VALUES (...);  -- Fast insert
COMMIT;
```

## Cascading Replication

### Setting Up Cascading Replication

```sql
-- Cascading: Standby replicates to another standby
-- Reduces load on primary

-- Topology:
-- Primary -> Standby1 -> Standby2

-- On Primary:
-- Standard setup (already configured)

-- On Standby1:
-- 1. Ensure standby can act as replication source
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET max_wal_senders = 5;  -- Allow downstream standbys

-- 2. Create replication slot for Standby2
SELECT pg_create_physical_replication_slot('standby2_slot');

-- Restart Standby1
-- $ pg_ctl restart

-- On Standby2:
-- 1. Create base backup from Standby1 (not Primary!)
-- $ pg_basebackup -h standby1_host -D /var/lib/postgresql/data -U replicator -P -R -X stream -C -S standby2_slot

-- 2. Start Standby2
-- $ pg_ctl start

-- Verify cascading replication
-- On Primary:
SELECT 
    application_name,
    client_addr,
    state
FROM pg_stat_replication;
-- Should show Standby1

-- On Standby1:
SELECT 
    application_name,
    client_addr,
    state
FROM pg_stat_replication;
-- Should show Standby2

-- Benefits of cascading:
-- - Reduces network/CPU load on primary
-- - Geographic distribution (Primary in US, Standby1 in EU, Standby2 in Asia)
-- - Isolate backup load (Standby2 for backups, doesn't impact primary)
```

## Replication Slots

### Physical Replication Slots

```sql
-- Replication slots prevent WAL deletion until consumed by standby

-- Create replication slot (on primary)
SELECT pg_create_physical_replication_slot('standby1_slot');

-- View replication slots
SELECT 
    slot_name,
    slot_type,
    active,
    restart_lsn,
    confirmed_flush_lsn,
    wal_status,
    safe_wal_size
FROM pg_replication_slots;

-- Configure standby to use slot
-- On Standby:
ALTER SYSTEM SET primary_slot_name = 'standby1_slot';
-- Restart standby

-- Drop replication slot (when standby removed)
SELECT pg_drop_replication_slot('standby1_slot');

-- Warning: Inactive slots can cause WAL accumulation
-- Monitor slot usage and drop unused slots
SELECT 
    slot_name,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) as lag_size
FROM pg_replication_slots
WHERE active = false;
```

### Logical Replication Slots

```sql
-- Logical replication automatically creates slots

-- View logical replication slots
SELECT 
    slot_name,
    slot_type,
    database,
    active,
    confirmed_flush_lsn
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- Manually create logical replication slot
SELECT pg_create_logical_replication_slot('manual_slot', 'pgoutput');

-- Drop logical replication slot
SELECT pg_drop_replication_slot('manual_slot');

-- Advance slot (skip data, useful for resolving conflicts)
SELECT pg_replication_slot_advance('my_slot', '0/3000000');
```

## Monitoring Replication

### Replication Health

```sql
-- Monitor replication status on Primary

SELECT 
    application_name,
    client_addr,
    client_hostname,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as replay_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as replay_lag_size,
    write_lag,
    flush_lag,
    replay_lag
FROM pg_stat_replication;

-- Check for disconnected standbys
SELECT 
    slot_name,
    active,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) as bytes_behind
FROM pg_replication_slots
WHERE active = false;

-- Alert if lag exceeds threshold
SELECT 
    application_name,
    pg_wal_lsn_diff(sent_lsn, replay_lsn) as lag_bytes
FROM pg_stat_replication
WHERE pg_wal_lsn_diff(sent_lsn, replay_lsn) > 10485760  -- 10MB
ORDER BY lag_bytes DESC;
```

### Standby Monitoring

```sql
-- Monitor replication on Standby

-- Check if in recovery mode
SELECT pg_is_in_recovery();  -- Should be true

-- Check last received and replayed WAL
SELECT 
    pg_last_wal_receive_lsn() as receive_lsn,
    pg_last_wal_replay_lsn() as replay_lsn,
    pg_wal_lsn_diff(pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn()) as lag_bytes;

-- Check replication lag time
SELECT 
    now() - pg_last_xact_replay_timestamp() AS replication_lag_time;

-- If lag is NULL, standby is fully caught up or no recent activity

-- View recovery status
SELECT 
    pg_is_in_recovery() as in_recovery,
    pg_is_wal_replay_paused() as replay_paused,
    pg_last_wal_receive_lsn() as receive_lsn,
    pg_last_wal_replay_lsn() as replay_lsn,
    pg_last_xact_replay_timestamp() as last_replay_time;
```

### Replication Alerts

```sql
-- Create monitoring function for alerts

CREATE OR REPLACE FUNCTION check_replication_health()
RETURNS TABLE (
    alert_type TEXT,
    severity TEXT,
    message TEXT
) AS $$
BEGIN
    -- Check if replication is active
    IF NOT EXISTS (SELECT 1 FROM pg_stat_replication) THEN
        RETURN QUERY SELECT 
            'No Active Replication'::TEXT,
            'CRITICAL'::TEXT,
            'No standby servers connected'::TEXT;
    END IF;
    
    -- Check replication lag
    RETURN QUERY
    SELECT 
        'Replication Lag'::TEXT,
        CASE 
            WHEN pg_wal_lsn_diff(sent_lsn, replay_lsn) > 104857600 THEN 'CRITICAL'  -- 100MB
            WHEN pg_wal_lsn_diff(sent_lsn, replay_lsn) > 10485760 THEN 'WARNING'   -- 10MB
            ELSE 'OK'
        END,
        'Standby ' || application_name || ' lag: ' || 
        pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn))
    FROM pg_stat_replication
    WHERE pg_wal_lsn_diff(sent_lsn, replay_lsn) > 10485760;
    
    -- Check for inactive replication slots
    RETURN QUERY
    SELECT 
        'Inactive Slot'::TEXT,
        'WARNING'::TEXT,
        'Replication slot ' || slot_name || ' is inactive'
    FROM pg_replication_slots
    WHERE active = false;
END;
$$ LANGUAGE plpgsql;

-- Run health check
SELECT * FROM check_replication_health();
```

## Failover and Switchover

### Promoting Standby

```sql
-- Promote standby to primary (failover)

-- On Standby:

-- Method 1: Using SQL function (PostgreSQL 12+)
SELECT pg_promote();

-- Method 2: Using pg_ctl
-- $ pg_ctl promote -D /var/lib/postgresql/data

-- Method 3: Using trigger file (older method)
-- $ touch /tmp/postgresql.trigger.5432

-- Verify promotion
SELECT pg_is_in_recovery();  -- Should return false

-- After promotion:
-- 1. Update application connection strings to new primary
-- 2. Reconfigure old primary as new standby (if coming back online)
-- 3. Update DNS/load balancer
-- 4. Verify all applications connected to new primary
```

### Planned Switchover

```sql
-- Planned switchover (zero data loss)

-- 1. On Old Primary: Stop accepting new writes
ALTER SYSTEM SET default_transaction_read_only = on;
SELECT pg_reload_conf();

-- Verify no writes occurring
SELECT count(*) FROM pg_stat_activity 
WHERE state = 'active' AND query NOT ILIKE '%pg_stat_activity%';

-- 2. On Old Primary: Check current WAL position
SELECT pg_current_wal_lsn();
-- Example: 0/15000000

-- 3. On Standby: Wait for replication to catch up
SELECT pg_last_wal_replay_lsn();
-- Wait until this matches primary's pg_current_wal_lsn()

-- Check replication lag
SELECT 
    pg_wal_lsn_diff(
        (SELECT pg_current_wal_lsn() FROM dblink('primary_connection', 'SELECT pg_current_wal_lsn()') AS t(lsn pg_lsn)),
        pg_last_wal_replay_lsn()
    ) as lag_bytes;

-- 4. On Standby: Promote to primary
SELECT pg_promote();

-- 5. On Old Primary: Shut down
-- $ pg_ctl stop -m fast

-- 6. Reconfigure Old Primary as Standby:
-- Create standby.signal
-- $ touch /var/lib/postgresql/data/standby.signal

-- Configure primary_conninfo (point to new primary)
ALTER SYSTEM SET primary_conninfo = 'host=new_primary_host port=5432 user=replicator password=password application_name=old_primary_standby';
ALTER SYSTEM SET primary_slot_name = 'old_primary_slot';

-- Remove read-only restriction
ALTER SYSTEM RESET default_transaction_read_only;

-- 7. On New Primary: Create replication slot for old primary
SELECT pg_create_physical_replication_slot('old_primary_slot');

-- 8. Start old primary (now as standby)
-- $ pg_ctl start

-- Verify configuration
-- On New Primary:
SELECT application_name, state FROM pg_stat_replication;
-- Should show old_primary_standby
```

## Conflict Resolution

### Logical Replication Conflicts

```sql
-- Logical replication can have conflicts when subscriber allows writes

-- Types of conflicts:
-- 1. INSERT conflict (duplicate key)
-- 2. UPDATE conflict (row doesn't exist)
-- 3. DELETE conflict (row doesn't exist)

-- View replication errors
SELECT * FROM pg_stat_subscription;
-- Check subworkercount and last_msg_send_time

-- Example conflict scenario:
-- On Publisher:
INSERT INTO users (id, username) VALUES (1, 'alice');

-- On Subscriber (if writes allowed):
INSERT INTO users (id, username) VALUES (1, 'bob');

-- Replication will fail with conflict

-- Resolve conflicts:

-- Method 1: Delete conflicting row on subscriber
DELETE FROM users WHERE id = 1;

-- Method 2: Update subscriber row
UPDATE users SET username = 'alice' WHERE id = 1;

-- Method 3: Skip conflict (dangerous)
-- On subscriber, alter subscription to skip errors (not recommended)

-- Best practice: Prevent conflicts
-- - Don't allow writes to replicated tables on subscriber
-- - Use different primary key ranges on different nodes
-- - Partition data (each node owns different data)
```

## Replication Best Practices

### Best Practices Checklist

```sql
-- [ ] Use replication slots
--   Prevents WAL deletion before standby consumes it
SELECT pg_create_physical_replication_slot('standby1');

-- [ ] Monitor replication lag
--   Alert when lag exceeds threshold
SELECT pg_wal_lsn_diff(sent_lsn, replay_lsn) FROM pg_stat_replication;

-- [ ] Use synchronous replication for critical data
--   Ensures zero data loss (with latency cost)
ALTER SYSTEM SET synchronous_standby_names = 'standby1';

-- [ ] Test failover regularly
--   Practice failover procedures
--   Measure actual RTO/RPO

-- [ ] Document topology
--   Maintain diagram of replication setup
--   Document failover procedures

-- [ ] Monitor disk space on primary
--   WAL files can accumulate if standby disconnected
SELECT pg_size_pretty(sum(size)) FROM pg_ls_waldir();

-- [ ] Set appropriate wal_keep_size
--   Balance between disk space and standby catch-up
ALTER SYSTEM SET wal_keep_size = '2GB';

-- [ ] Use cascading for geographic distribution
--   Reduces load on primary
--   Improves cross-region performance

-- [ ] Regular backup of primary
--   Replication is NOT a backup
--   Corruption/deletion replicates to standbys

-- [ ] Network security
--   Use SSL for replication connections
--   Restrict replication user privileges
ALTER SYSTEM SET primary_conninfo = 'host=primary sslmode=require ...';

-- [ ] Application-level read distribution
--   Direct read-only queries to standbys
--   Requires application awareness of topology
```

## Summary

PostgreSQL replication provides:
- **High Availability**: Automatic failover with minimal downtime
- **Read Scalability**: Distribute read queries across standbys
- **Geographic Distribution**: Standbys in different regions
- **Zero Data Loss**: Synchronous replication option
- **Flexibility**: Physical (full cluster) or logical (selective) replication
- **Monitoring**: Comprehensive replication health metrics

Proper replication setup ensures data availability and business continuity.

## Next Steps

- Study [Backup and Recovery](./35-backup-and-recovery.md)
- Learn [High Availability Architecture](./37-high-availability.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [Disaster Recovery](./37-disaster-recovery.md)
