# High Availability

## Overview

High Availability (HA) ensures database systems remain accessible with minimal downtime. This comprehensive guide covers HA architectures, automatic failover, load balancing, connection pooling, and disaster recovery strategies for PostgreSQL.

## Table of Contents
- [High Availability Basics](#high-availability-basics)
- [HA Architecture Patterns](#ha-architecture-patterns)
- [Automatic Failover](#automatic-failover)
- [Load Balancing](#load-balancing)
- [Connection Pooling](#connection-pooling)
- [Shared Storage](#shared-storage)
- [Health Checks](#health-checks)
- [Split-Brain Prevention](#split-brain-prevention)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [HA Best Practices](#ha-best-practices)

## High Availability Basics

### HA Terminology

```sql
-- Key HA concepts:

-- Availability: Percentage of time system is operational
-- 99.9% (Three Nines): 8.76 hours downtime/year
-- 99.99% (Four Nines): 52.56 minutes downtime/year
-- 99.999% (Five Nines): 5.26 minutes downtime/year

-- RTO (Recovery Time Objective): Max acceptable downtime
-- Example: RTO = 5 minutes

-- RPO (Recovery Point Objective): Max acceptable data loss
-- Example: RPO = 0 (zero data loss with sync replication)

-- Failover: Switching to standby when primary fails
-- Automatic: System detects failure and promotes standby
-- Manual: Human intervention required

-- Failback: Returning to original primary after recovery

-- Split-Brain: Both nodes think they're primary (dangerous!)

-- Fencing: Preventing failed primary from accepting writes

-- Quorum: Minimum number of nodes to make decisions
```

### HA Requirements

```sql
-- Components needed for HA:

-- 1. Redundancy: Multiple database servers
-- - Primary server
-- - One or more standby servers
-- - Streaming replication configured

-- 2. Monitoring: Detect failures
-- - Health checks (database connectivity, query response)
-- - Network monitoring
-- - Disk space monitoring
-- - Replication lag monitoring

-- 3. Automatic Failover: Promote standby on primary failure
-- - Patroni, repmgr, pg_auto_failover
-- - Consensus mechanism (etcd, Consul, ZooKeeper)

-- 4. Load Balancing: Distribute read traffic
-- - HAProxy, PgBouncer, Pgpool-II
-- - Application-level routing

-- 5. Connection Pooling: Manage connections efficiently
-- - PgBouncer, Pgpool-II
-- - Reduces connection overhead

-- 6. Virtual IP (VIP): Single connection point
-- - Moves to active primary
-- - Applications connect to VIP, not specific server
```

## HA Architecture Patterns

### Primary-Standby Architecture

```sql
-- Basic HA setup with one primary and one standby

-- Architecture:
-- ┌─────────────┐
-- │   Primary   │ ──streaming─→ │   Standby   │
-- └─────────────┘  replication   └─────────────┘
--       │                                │
--       └──────── Virtual IP ────────────┘
--            (points to active)

-- Configuration:

-- Primary:
ALTER SYSTEM SET wal_level = replica;
ALTER SYSTEM SET max_wal_senders = 5;
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET synchronous_standby_names = 'standby1';  -- For zero data loss

-- Standby:
-- Created with pg_basebackup
-- primary_conninfo = 'host=primary_host user=replicator ...'
-- hot_standby = on

-- Failover process:
-- 1. Detect primary failure
-- 2. Promote standby to primary
-- 3. Move VIP to new primary
-- 4. Applications reconnect (transparently via VIP)

-- Pros: Simple, proven, zero data loss (with sync replication)
-- Cons: Manual failover (without HA tools), one standby only
```

### Primary-Multi-Standby Architecture

```sql
-- HA setup with multiple standbys

-- Architecture:
--                  ┌─────────────┐
--         ┌────────│  Standby 1  │
--         │        └─────────────┘
-- ┌───────────┐   ┌─────────────┐
-- │  Primary  │───│  Standby 2  │
-- └───────────┘   └─────────────┘
--         │        ┌─────────────┐
--         └────────│  Standby 3  │
--                  └─────────────┘

-- Configuration:

-- Primary:
ALTER SYSTEM SET max_wal_senders = 10;  -- Support multiple standbys
ALTER SYSTEM SET synchronous_standby_names = 'FIRST 2 (standby1, standby2, standby3)';
-- Waits for 2 standbys before commit (high availability)

-- Multiple standbys provide:
-- - Higher availability (multiple failover targets)
-- - Read scaling (distribute read queries)
-- - Geographic distribution (standbys in different regions)
-- - Specialized standbys (one for backup, one for reporting)

-- Failover priority:
-- 1. Standby with least lag
-- 2. Synchronous standby (if configured)
-- 3. Standby with highest priority (configured in HA tool)
```

### Cascading Replication Architecture

```sql
-- Reduce load on primary by cascading replication

-- Architecture:
-- ┌─────────┐       ┌──────────┐       ┌──────────┐
-- │ Primary │ ────→ │ Standby1 │ ────→ │ Standby2 │
-- └─────────┘       └──────────┘       └──────────┘
--     │                   │                  │
--     │                   └──────────────────┤
--     │                  ┌──────────┐        │
--     │                  │ Standby3 │ ←──────┘
--     │                  └──────────┘
--     └── Geographic Boundary ──────────────→

-- Use case: Geographic distribution
-- Primary in US, Standby1 in US (sync), Standby2/3 in Europe (async)

-- Primary only replicates to Standby1
-- Standby1 cascades to Standby2 and Standby3

-- Configuration:

-- Standby1:
ALTER SYSTEM SET hot_standby = on;
ALTER SYSTEM SET max_wal_senders = 5;  -- Allow downstream standbys

-- Standby2/3:
-- primary_conninfo = 'host=standby1_host ...'  -- Connect to Standby1, not Primary

-- Pros: Reduces primary load, better geographic distribution
-- Cons: Increased complexity, higher lag for downstream standbys
```

### Multi-Master Architecture

```sql
-- Multi-master with logical replication (advanced)

-- Architecture:
-- ┌──────────┐  ←──logical──→  ┌──────────┐
-- │ Master A │    replication   │ Master B │
-- └──────────┘                  └──────────┘
--  (owns users)                 (owns orders)

-- Each master owns specific tables
-- Logical replication replicates to other masters

-- Master A:
CREATE PUBLICATION users_pub FOR TABLE users;
CREATE SUBSCRIPTION orders_sub 
CONNECTION 'host=masterB ...' 
PUBLICATION orders_pub;

-- Master B:
CREATE PUBLICATION orders_pub FOR TABLE orders;
CREATE SUBSCRIPTION users_sub 
CONNECTION 'host=masterA ...' 
PUBLICATION users_pub;

-- Application routes:
-- - User operations → Master A
-- - Order operations → Master B
-- - Both tables readable on both masters (eventual consistency)

-- Challenges:
-- - Conflict resolution (if same table written on multiple masters)
-- - Application complexity (routing logic)
-- - Eventual consistency (not immediately consistent)

-- Use cases:
-- - Geographic distribution (US users → US master, EU users → EU master)
-- - Service separation (user service → DB A, order service → DB B)
```

## Automatic Failover

### Patroni Setup

```sql
-- Patroni: HA solution with automatic failover
-- Uses etcd/Consul/ZooKeeper for distributed consensus

-- Architecture:
-- ┌─────────────┐
-- │    etcd     │  (Distributed configuration store)
-- └─────────────┘
--        ↕
-- ┌──────────────────────────────────┐
-- │  Patroni    Patroni    Patroni   │
-- │  Primary    Standby1   Standby2  │
-- │  (Leader)   (Replica)  (Replica) │
-- └──────────────────────────────────┘

-- Install Patroni and etcd
-- $ pip install patroni[etcd]
-- $ apt-get install etcd

-- Patroni configuration file (patroni.yml):
-- scope: postgres-cluster
-- name: node1
-- 
-- restapi:
--   listen: 0.0.0.0:8008
--   connect_address: node1:8008
-- 
-- etcd:
--   hosts: etcd1:2379,etcd2:2379,etcd3:2379
-- 
-- bootstrap:
--   dcs:
--     ttl: 30
--     loop_wait: 10
--     retry_timeout: 10
--     maximum_lag_on_failover: 1048576
--     postgresql:
--       parameters:
--         wal_level: replica
--         hot_standby: on
--         max_wal_senders: 5
--         max_replication_slots: 5
-- 
-- postgresql:
--   listen: 0.0.0.0:5432
--   connect_address: node1:5432
--   data_dir: /var/lib/postgresql/data
--   authentication:
--     replication:
--       username: replicator
--       password: repl_password
--     superuser:
--       username: postgres
--       password: postgres_password

-- Start Patroni
-- $ patroni /etc/patroni/patroni.yml

-- Patroni automatically:
-- - Monitors primary health
-- - Promotes standby on primary failure
-- - Manages replication configuration
-- - Provides REST API for status

-- Check cluster status
-- $ patronictl -c /etc/patroni/patroni.yml list
-- + Cluster: postgres-cluster -------+----+-----------+
-- | Member | Host      | Role    | State   | Lag in MB |
-- +--------+-----------+---------+---------+-----------+
-- | node1  | 10.0.1.1  | Leader  | running |           |
-- | node2  | 10.0.1.2  | Replica | running | 0         |
-- | node3  | 10.0.1.3  | Replica | running | 0         |
-- +--------+-----------+---------+---------+-----------+

-- Trigger failover manually
-- $ patronictl -c /etc/patroni/patroni.yml failover postgres-cluster
```

### repmgr Setup

```sql
-- repmgr: Replication manager for PostgreSQL

-- Install repmgr
-- $ apt-get install postgresql-14-repmgr

-- Configure repmgr.conf (on all nodes):
-- node_id=1
-- node_name='node1'
-- conninfo='host=node1 user=repmgr dbname=repmgr connect_timeout=2'
-- data_directory='/var/lib/postgresql/14/main'
-- replication_user='repmgr'
-- failover=automatic
-- promote_command='/usr/bin/repmgr standby promote -f /etc/repmgr.conf'
-- follow_command='/usr/bin/repmgr standby follow -f /etc/repmgr.conf --upstream-node-id=%n'

-- On Primary:
-- Create repmgr database and user
CREATE USER repmgr SUPERUSER LOGIN;
CREATE DATABASE repmgr OWNER repmgr;

-- Register primary
-- $ repmgr -f /etc/repmgr.conf primary register

-- On Standbys:
-- Clone from primary
-- $ repmgr -h node1 -U repmgr -d repmgr -f /etc/repmgr.conf standby clone
-- $ pg_ctl start

-- Register standby
-- $ repmgr -f /etc/repmgr.conf standby register

-- Start repmgrd (monitoring daemon)
-- $ repmgrd -f /etc/repmgr.conf

-- View cluster status
-- $ repmgr -f /etc/repmgr.conf cluster show

-- Manual failover
-- $ repmgr standby promote -f /etc/repmgr.conf
```

### pg_auto_failover

```sql
-- pg_auto_failover: Microsoft's automatic failover solution

-- Architecture:
-- ┌────────────┐
-- │  Monitor   │  (pg_auto_failover monitor node)
-- └────────────┘
--       ↕
-- ┌──────────────────┐
-- │  Primary  Standby│
-- └──────────────────┘

-- Install pg_auto_failover
-- $ apt-get install pg-auto-failover-cli

-- Create monitor node
-- $ pg_autoctl create monitor --pgdata /var/lib/postgresql/monitor --hostname monitor-host

-- Create primary node
-- $ pg_autoctl create postgres --pgdata /var/lib/postgresql/data --hostname primary-host --monitor postgres://autoctl_node@monitor-host/pg_auto_failover

-- Create standby node
-- $ pg_autoctl create postgres --pgdata /var/lib/postgresql/data --hostname standby-host --monitor postgres://autoctl_node@monitor-host/pg_auto_failover

-- Start nodes
-- $ pg_autoctl run --pgdata /var/lib/postgresql/data

-- View cluster state
-- $ pg_autoctl show state --pgdata /var/lib/postgresql/data

-- Manual failover
-- $ pg_autoctl perform failover --pgdata /var/lib/postgresql/data
```

## Load Balancing

### HAProxy Configuration

```sql
-- HAProxy: Load balancer for read/write splitting

-- HAProxy configuration (/etc/haproxy/haproxy.cfg):
-- 
-- global
--     maxconn 1000
-- 
-- defaults
--     mode tcp
--     timeout connect 10s
--     timeout client 30s
--     timeout server 30s
-- 
-- # Read-Write (Primary) Backend
-- frontend postgres_write
--     bind *:5000
--     default_backend postgres_primary
-- 
-- backend postgres_primary
--     option httpchk
--     http-check expect status 200
--     default-server inter 3s fall 3 rise 2
--     server primary1 10.0.1.1:5432 maxconn 100 check port 8008
--     server primary2 10.0.1.2:5432 maxconn 100 check port 8008 backup
-- 
-- # Read-Only (Standby) Backend
-- frontend postgres_read
--     bind *:5001
--     default_backend postgres_replicas
-- 
-- backend postgres_replicas
--     balance roundrobin
--     option httpchk
--     http-check expect status 200
--     default-server inter 3s fall 3 rise 2
--     server replica1 10.0.1.2:5432 maxconn 100 check port 8008
--     server replica2 10.0.1.3:5432 maxconn 100 check port 8008

-- Application connects to:
-- Write queries: haproxy_host:5000 (routes to primary)
-- Read queries: haproxy_host:5001 (routes to standbys, round-robin)

-- Health check endpoint (using Patroni REST API):
-- http://node:8008/health (returns 200 if healthy)

-- Benefits:
-- - Automatic routing to current primary
-- - Read load distribution across standbys
-- - Connection retry on failure
-- - Health-based routing
```

### Pgpool-II Configuration

```sql
-- Pgpool-II: Connection pooling and load balancing

-- Install Pgpool-II
-- $ apt-get install pgpool2

-- Configure pgpool.conf:
-- # Connection settings
-- listen_addresses = '*'
-- port = 9999
-- pcp_listen_addresses = '*'
-- pcp_port = 9898
-- 
-- # Backend nodes
-- backend_hostname0 = 'node1'
-- backend_port0 = 5432
-- backend_weight0 = 1
-- backend_flag0 = 'ALWAYS_PRIMARY'
-- 
-- backend_hostname1 = 'node2'
-- backend_port1 = 5432
-- backend_weight1 = 1
-- backend_flag1 = 'DISALLOW_TO_FAILOVER'
-- 
-- backend_hostname2 = 'node3'
-- backend_port2 = 5432
-- backend_weight2 = 1
-- backend_flag2 = 'DISALLOW_TO_FAILOVER'
-- 
-- # Load balancing
-- load_balance_mode = on
-- 
-- # Streaming replication
-- sr_check_period = 10
-- sr_check_user = 'repmgr'
-- sr_check_password = 'password'
-- 
-- # Health check
-- health_check_period = 10
-- health_check_user = 'repmgr'
-- health_check_password = 'password'
-- 
-- # Failover
-- failover_command = '/etc/pgpool2/failover.sh %d %h %p %D %m'
-- failback_command = '/etc/pgpool2/failback.sh %d %h %p %D %m'

-- Application connects to Pgpool-II port 9999
-- Pgpool-II handles:
-- - Read query load balancing
-- - Write query routing to primary
-- - Connection pooling
-- - Automatic failover

-- View Pgpool status
-- $ psql -h pgpool_host -p 9999 -c "show pool_nodes"
```

## Connection Pooling

### PgBouncer Setup

```sql
-- PgBouncer: Lightweight connection pooler

-- Install PgBouncer
-- $ apt-get install pgbouncer

-- Configure pgbouncer.ini:
-- [databases]
-- mydb = host=primary_host port=5432 dbname=mydb
-- mydb_readonly = host=standby_host port=5432 dbname=mydb
-- 
-- [pgbouncer]
-- listen_addr = 0.0.0.0
-- listen_port = 6432
-- auth_type = scram-sha-256
-- auth_file = /etc/pgbouncer/userlist.txt
-- pool_mode = transaction
-- max_client_conn = 10000
-- default_pool_size = 25
-- min_pool_size = 10
-- reserve_pool_size = 5
-- reserve_pool_timeout = 3
-- max_db_connections = 100
-- log_connections = 1
-- log_disconnections = 1

-- Pool modes:
-- - session: One server connection per client (safe, higher connections)
-- - transaction: Server connection released after transaction (efficient)
-- - statement: Server connection released after statement (most aggressive)

-- Application connects to:
-- postgres://user:pass@pgbouncer_host:6432/mydb

-- Benefits:
-- - Support 10,000 client connections with only 25 PostgreSQL connections
-- - Reduce connection overhead
-- - Fast connection reuse

-- View PgBouncer stats
-- $ psql -h pgbouncer_host -p 6432 -U admin -d pgbouncer -c "SHOW POOLS"
-- $ psql -h pgbouncer_host -p 6432 -U admin -d pgbouncer -c "SHOW STATS"

-- PgBouncer with HAProxy:
-- HAProxy routes to active primary
-- PgBouncer pools connections to primary
-- Application → HAProxy → PgBouncer → PostgreSQL
```

## Shared Storage

### Shared Disk Failover

```sql
-- Shared storage architecture (less common with streaming replication)

-- Architecture:
-- ┌──────────┐     ┌──────────┐
-- │ Primary  │     │ Standby  │
-- └────┬─────┘     └────┬─────┘
--      │                │
--      └────────┬───────┘
--           ┌───┴────┐
--           │ Shared │
--           │ Storage│
--           │ (SAN)  │
--           └────────┘

-- Only one node accesses storage at a time
-- Failover: Unmount from failed primary, mount on standby

-- Pros: Fast failover (no data copy needed)
-- Cons: Shared storage is single point of failure, complex, expensive

-- Modern approach: Streaming replication preferred
-- Shared storage still used in some enterprise environments
```

## Health Checks

### Database Health Check

```sql
-- Create health check function

CREATE OR REPLACE FUNCTION health_check()
RETURNS TABLE (
    check_name TEXT,
    status TEXT,
    details TEXT
) AS $$
BEGIN
    -- Check database connectivity
    RETURN QUERY SELECT 
        'Database Connection'::TEXT,
        'OK'::TEXT,
        'Connected successfully'::TEXT;
    
    -- Check if in recovery (standby)
    RETURN QUERY SELECT 
        'Role'::TEXT,
        CASE WHEN pg_is_in_recovery() THEN 'Standby' ELSE 'Primary' END,
        ''::TEXT;
    
    -- Check replication (if primary)
    IF NOT pg_is_in_recovery() THEN
        RETURN QUERY SELECT 
            'Replication Connections'::TEXT,
            count(*)::TEXT,
            string_agg(application_name, ', ')
        FROM pg_stat_replication;
    END IF;
    
    -- Check replication lag (if standby)
    IF pg_is_in_recovery() THEN
        RETURN QUERY SELECT 
            'Replication Lag'::TEXT,
            COALESCE(
                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()))::TEXT,
                '0'
            ) || ' seconds',
            ''::TEXT;
    END IF;
    
    -- Check table count (basic sanity)
    RETURN QUERY SELECT 
        'User Tables'::TEXT,
        count(*)::TEXT,
        ''::TEXT
    FROM pg_tables 
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
END;
$$ LANGUAGE plpgsql;

-- Run health check
SELECT * FROM health_check();

-- Simple HTTP health check endpoint (for HAProxy/load balancers)
-- Use Patroni REST API: http://node:8008/health
-- Or custom script checking query response time
```

### Application-Level Health Check

```sql
-- Application health check query (fast, minimal overhead)

SELECT 1;  -- Returns 1 if database responsive

-- More comprehensive check
SELECT 
    'OK' as status,
    pg_is_in_recovery() as is_standby,
    current_database() as database,
    version() as version,
    now() as timestamp;

-- Check write capability (fails on standby)
BEGIN;
CREATE TEMP TABLE health_check_write (id INT);
DROP TABLE health_check_write;
COMMIT;

-- Health check with timeout (application side)
-- Set statement_timeout to 5 seconds
-- If query exceeds 5s, consider database unhealthy
```

## Split-Brain Prevention

### Avoiding Split-Brain

```sql
-- Split-brain: Both primary and promoted standby accept writes simultaneously
-- Causes data divergence and conflicts

-- Prevention methods:

-- 1. Fencing: Prevent old primary from accepting writes
-- - STONITH (Shoot The Other Node In The Head)
-- - Network isolation (block old primary's ports)
-- - Disk I/O fencing (prevent disk writes)

-- 2. Consensus/Quorum: Use distributed consensus
-- - Patroni with etcd (requires quorum to promote)
-- - repmgr with witness server
-- - Minimum 3 nodes for quorum

-- 3. Virtual IP: Only active primary has VIP
-- - Applications connect to VIP
-- - VIP moves to new primary on failover
-- - Old primary without VIP can't receive connections

-- 4. Monitoring: Detect split-brain quickly
-- - Monitor pg_stat_replication on both nodes
-- - Alert if both nodes think they're primary
-- - Automated resolution script

-- Example: Check for split-brain condition
CREATE OR REPLACE FUNCTION detect_split_brain()
RETURNS BOOLEAN AS $$
DECLARE
    is_primary BOOLEAN;
    has_replicas BOOLEAN;
    dblink_result RECORD;
BEGIN
    -- Check if this node is primary
    is_primary := NOT pg_is_in_recovery();
    
    IF NOT is_primary THEN
        RETURN FALSE;  -- Standby can't have split-brain
    END IF;
    
    -- Check if other node also thinks it's primary
    -- Requires dblink extension and connection to other node
    -- FOR dblink_result IN 
    --     SELECT * FROM dblink('other_node_connection', 
    --                         'SELECT pg_is_in_recovery()') 
    --     AS t(is_recovery BOOLEAN)
    -- LOOP
    --     IF NOT dblink_result.is_recovery THEN
    --         RAISE WARNING 'SPLIT-BRAIN DETECTED!';
    --         RETURN TRUE;
    --     END IF;
    -- END LOOP;
    
    RETURN FALSE;
END;
$$ LANGUAGE plpgsql;
```

## Monitoring and Alerts

### HA Monitoring

```sql
-- Comprehensive HA monitoring

-- 1. Primary health
SELECT 
    'Primary Status' as check_type,
    CASE WHEN pg_is_in_recovery() THEN 'CRITICAL: Node is standby!' 
         ELSE 'OK' END as status;

-- 2. Replication connections
SELECT 
    'Replication' as check_type,
    CASE WHEN count(*) = 0 THEN 'CRITICAL: No standbys connected'
         WHEN count(*) < 2 THEN 'WARNING: Only ' || count(*) || ' standby'
         ELSE 'OK: ' || count(*) || ' standbys connected' END as status
FROM pg_stat_replication;

-- 3. Replication lag
SELECT 
    'Replication Lag' as check_type,
    application_name,
    CASE WHEN pg_wal_lsn_diff(sent_lsn, replay_lsn) > 104857600 
         THEN 'CRITICAL: Lag > 100MB'
         WHEN pg_wal_lsn_diff(sent_lsn, replay_lsn) > 10485760 
         THEN 'WARNING: Lag > 10MB'
         ELSE 'OK' END as status,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) as lag
FROM pg_stat_replication;

-- 4. Synchronous standby
SELECT 
    'Synchronous Replication' as check_type,
    CASE WHEN sync_state = 'sync' THEN 'OK: Synchronous standby active'
         ELSE 'WARNING: No synchronous standby' END as status
FROM pg_stat_replication
WHERE application_name = (SELECT setting FROM pg_settings WHERE name = 'synchronous_standby_names');

-- 5. Replication slots
SELECT 
    'Replication Slots' as check_type,
    slot_name,
    CASE WHEN NOT active THEN 'WARNING: Slot inactive'
         WHEN pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1073741824 
         THEN 'CRITICAL: Slot lag > 1GB'
         ELSE 'OK' END as status
FROM pg_replication_slots;

-- Create monitoring view
CREATE VIEW ha_health AS
SELECT * FROM (
    SELECT 'Primary Status' as metric, 
           CASE WHEN pg_is_in_recovery() THEN 'Standby' ELSE 'Primary' END as value
    UNION ALL
    SELECT 'Standby Count', count(*)::TEXT 
    FROM pg_stat_replication
    UNION ALL
    SELECT 'Max Replication Lag', 
           COALESCE(pg_size_pretty(max(pg_wal_lsn_diff(sent_lsn, replay_lsn))), '0 bytes')
    FROM pg_stat_replication
    UNION ALL
    SELECT 'Inactive Slots', count(*)::TEXT 
    FROM pg_replication_slots WHERE NOT active
) t;

SELECT * FROM ha_health;
```

## HA Best Practices

### Best Practices Checklist

```sql
-- [ ] Redundancy
--   [ ] Minimum 3 nodes (primary + 2 standbys) for quorum
--   [ ] Geographic distribution (multi-AZ or multi-region)
--   [ ] Dedicated network for replication

-- [ ] Automatic Failover
--   [ ] Use HA tool (Patroni, repmgr, pg_auto_failover)
--   [ ] Test failover regularly (monthly)
--   [ ] Document failover procedures
--   [ ] Measure actual RTO

-- [ ] Monitoring
--   [ ] Monitor primary health (connectivity, performance)
--   [ ] Monitor standby health and lag
--   [ ] Monitor replication slots
--   [ ] Alert on critical conditions
--   [ ] 24/7 on-call rotation

-- [ ] Split-Brain Prevention
--   [ ] Use consensus-based failover (etcd, Consul)
--   [ ] Implement fencing
--   [ ] Use virtual IP
--   [ ] Monitor for split-brain condition

-- [ ] Load Balancing
--   [ ] Use HAProxy or Pgpool-II
--   [ ] Separate read and write traffic
--   [ ] Health-based routing
--   [ ] Connection pooling (PgBouncer)

-- [ ] Data Consistency
--   [ ] Use synchronous replication for critical data
--   [ ] Balance between consistency and availability
--   [ ] Monitor and alert on replication lag
--   [ ] Regular consistency checks

-- [ ] Backup
--   [ ] Regular backups (replication ≠ backup)
--   [ ] Test restores monthly
--   [ ] Offsite backup storage
--   [ ] Encrypted backups

-- [ ] Documentation
--   [ ] Network topology diagram
--   [ ] Failover runbook
--   [ ] Contact lists
--   [ ] Post-incident review process

-- [ ] Testing
--   [ ] Monthly failover drills
--   [ ] Chaos engineering (controlled failures)
--   [ ] Load testing
--   [ ] Disaster recovery exercises

-- [ ] Security
--   [ ] SSL/TLS for replication
--   [ ] Secure replication user (limited privileges)
--   [ ] Network segmentation
--   [ ] Regular security audits
```

## Summary

PostgreSQL High Availability requires:
- **Redundancy**: Multiple database servers with replication
- **Automatic Failover**: Tools like Patroni, repmgr, pg_auto_failover
- **Load Balancing**: HAProxy, Pgpool-II for read/write splitting
- **Connection Pooling**: PgBouncer for efficient connection management
- **Monitoring**: Comprehensive health checks and alerts
- **Split-Brain Prevention**: Consensus, fencing, virtual IPs
- **Testing**: Regular failover drills and disaster recovery exercises

Proper HA setup ensures minimal downtime and business continuity.

## Next Steps

- Study [Replication](./36-replication.md)
- Learn [Backup and Recovery](./35-backup-and-recovery.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [Performance Troubleshooting](./39-performance-troubleshooting.md)
