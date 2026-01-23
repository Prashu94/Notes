# PostgreSQL Troubleshooting Guide

## Overview

This comprehensive guide covers common PostgreSQL errors, performance issues, and their solutions. Learn to diagnose and resolve problems efficiently with practical examples and debugging techniques.

## Table of Contents
- [Connection Issues](#connection-issues)
- [Authentication Errors](#authentication-errors)
- [Performance Problems](#performance-problems)
- [Lock and Deadlock Issues](#lock-and-deadlock-issues)
- [Replication Problems](#replication-problems)
- [Storage and Disk Issues](#storage-and-disk-issues)
- [Memory Problems](#memory-problems)
- [Query Errors](#query-errors)
- [Data Corruption](#data-corruption)
- [Backup and Recovery Issues](#backup-and-recovery-issues)
- [Monitoring and Diagnostics](#monitoring-and-diagnostics)

---

## Connection Issues

### Error: "could not connect to server: Connection refused"

```
psql: error: could not connect to server: Connection refused
    Is the server running on host "localhost" (127.0.0.1) and accepting
    TCP/IP connections on port 5432?
```

**Causes:**
1. PostgreSQL not running
2. Wrong host/port
3. Firewall blocking connection
4. PostgreSQL not configured for TCP/IP

**Solutions:**

```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql
# or
pg_isready -h localhost -p 5432

# Start PostgreSQL
sudo systemctl start postgresql

# Check listening ports
ss -tlnp | grep 5432
netstat -an | grep 5432

# Check postgresql.conf
# Ensure listen_addresses includes your host
listen_addresses = '*'  # or specific IP

# Check pg_hba.conf for connection permissions
# Add line for your network
host    all    all    192.168.1.0/24    scram-sha-256
```

### Error: "too many connections"

```
FATAL: too many connections for role "myuser"
-- or --
FATAL: sorry, too many clients already
```

**Diagnosis:**

```sql
-- Check current connections
SELECT count(*) FROM pg_stat_activity;

-- Check connections by state
SELECT state, count(*) 
FROM pg_stat_activity 
GROUP BY state;

-- Check connections by user
SELECT usename, count(*) 
FROM pg_stat_activity 
GROUP BY usename
ORDER BY count DESC;

-- Find idle connections
SELECT pid, usename, application_name, client_addr, 
       state, query_start, query
FROM pg_stat_activity
WHERE state = 'idle'
ORDER BY query_start;
```

**Solutions:**

```sql
-- Increase max_connections (requires restart)
-- In postgresql.conf:
max_connections = 200

-- Terminate idle connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND query_start < NOW() - INTERVAL '10 minutes'
AND pid <> pg_backend_pid();

-- Set connection limits per user
ALTER ROLE myuser CONNECTION LIMIT 20;

-- Use connection pooling (PgBouncer)
-- pgbouncer.ini:
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 50
```

### Connection Timeout

```
FATAL: connection timed out
```

**Solutions:**

```bash
# Check network connectivity
ping postgres-server
telnet postgres-server 5432

# Check server-side timeout settings (postgresql.conf)
tcp_keepalives_idle = 60
tcp_keepalives_interval = 10
tcp_keepalives_count = 6

# Client-side timeout
export PGCONNECT_TIMEOUT=30
psql "host=server connect_timeout=30"
```

---

## Authentication Errors

### Error: "password authentication failed"

```
FATAL: password authentication failed for user "myuser"
```

**Diagnosis:**

```bash
# Check pg_hba.conf authentication method
cat /etc/postgresql/14/main/pg_hba.conf | grep -v "^#" | grep -v "^$"
```

**Solutions:**

```bash
# Reset user password
sudo -u postgres psql -c "ALTER USER myuser PASSWORD 'newpassword';"

# Check password encryption method
# postgresql.conf
password_encryption = scram-sha-256

# Ensure pg_hba.conf matches
# host all all 0.0.0.0/0 scram-sha-256

# Reload configuration
sudo systemctl reload postgresql
```

### Error: "peer authentication failed"

```
FATAL: Peer authentication failed for user "myuser"
```

**Solution:**

```bash
# pg_hba.conf - change peer to md5 or scram-sha-256 for local connections
# Before:
local   all   all   peer
# After:
local   all   all   scram-sha-256

# Or connect with matching OS user
sudo -u myuser psql
```

### Error: "no pg_hba.conf entry"

```
FATAL: no pg_hba.conf entry for host "192.168.1.100", user "myuser", database "mydb"
```

**Solution:**

```bash
# Add appropriate entry to pg_hba.conf
# Format: TYPE  DATABASE  USER  ADDRESS  METHOD

# Allow specific IP
host    mydb    myuser    192.168.1.100/32    scram-sha-256

# Allow subnet
host    all     all       192.168.1.0/24      scram-sha-256

# Reload
sudo systemctl reload postgresql
```

---

## Performance Problems

### Slow Queries

**Diagnosis:**

```sql
-- Enable query logging
-- postgresql.conf
log_min_duration_statement = 1000  -- Log queries taking > 1 second

-- Find slow queries
SELECT pid, now() - pg_stat_activity.query_start AS duration, query, state
FROM pg_stat_activity
WHERE state != 'idle'
AND now() - pg_stat_activity.query_start > interval '5 seconds'
ORDER BY duration DESC;

-- Check query plan
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM orders WHERE customer_id = 123;

-- Identify slow query patterns
SELECT 
    substring(query, 1, 50) AS short_query,
    round(total_exec_time::numeric, 2) AS total_time,
    calls,
    round(mean_exec_time::numeric, 2) AS mean_time,
    round((100 * total_exec_time / sum(total_exec_time) OVER ())::numeric, 2) AS percentage
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

**Solutions:**

```sql
-- Add missing indexes
CREATE INDEX CONCURRENTLY idx_orders_customer 
ON orders(customer_id);

-- Update statistics
ANALYZE orders;

-- Rewrite query to use indexes
-- Before (can't use index):
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';
-- After (can use functional index):
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
SELECT * FROM users WHERE LOWER(email) = 'user@example.com';

-- Or use expression index with ILIKE:
CREATE INDEX idx_users_email_pattern ON users(email varchar_pattern_ops);
SELECT * FROM users WHERE email ILIKE 'user%';
```

### High CPU Usage

```sql
-- Find CPU-intensive queries
SELECT pid, usename, client_addr, 
       now() - query_start AS duration,
       state, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC;

-- Check for missing indexes causing sequential scans
SELECT 
    schemaname,
    relname AS table_name,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    CASE WHEN seq_scan > 0 
         THEN round(seq_tup_read::numeric / seq_scan, 2) 
         ELSE 0 
    END AS avg_seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 100
ORDER BY seq_tup_read DESC;

-- Terminate runaway query
SELECT pg_cancel_backend(pid);  -- Graceful
SELECT pg_terminate_backend(pid);  -- Force
```

### High Memory Usage

```sql
-- Check shared buffer usage
SELECT 
    c.relname,
    pg_size_pretty(count(*) * 8192) AS buffered,
    round(100.0 * count(*) / 
          (SELECT setting FROM pg_settings WHERE name = 'shared_buffers')::integer, 1) 
          AS buffer_percent
FROM pg_class c
INNER JOIN pg_buffercache b ON b.relfilenode = c.relfilenode
INNER JOIN pg_database d ON b.reldatabase = d.oid AND d.datname = current_database()
GROUP BY c.relname
ORDER BY count(*) DESC
LIMIT 20;

-- Find memory-hungry queries
SELECT pid, usename, 
       pg_size_pretty(temp_files_bytes) AS temp_size,
       query
FROM pg_stat_activity
WHERE temp_files_bytes > 0
ORDER BY temp_files_bytes DESC;
```

**Configuration Tuning:**

```ini
# postgresql.conf - Memory settings

# Shared memory (25% of RAM)
shared_buffers = 4GB

# Working memory per operation
work_mem = 256MB

# Maintenance operations
maintenance_work_mem = 1GB

# Effective cache size (50-75% of RAM)
effective_cache_size = 12GB
```

---

## Lock and Deadlock Issues

### Finding Locks

```sql
-- View current locks
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity 
    ON blocked_activity.pid = blocked_locks.pid
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
JOIN pg_catalog.pg_stat_activity blocking_activity 
    ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Simpler lock view
SELECT 
    l.pid,
    l.locktype,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.query_start
FROM pg_locks l
JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.relation IS NOT NULL
ORDER BY l.pid;
```

### Deadlock Resolution

```sql
-- Error: deadlock detected
-- DETAIL: Process 1234 waits for ShareLock on transaction 5678;
--         blocked by process 9012.
--         Process 9012 waits for ShareLock on transaction 1234;
--         blocked by process 1234.

-- Enable deadlock logging
-- postgresql.conf
log_lock_waits = on
deadlock_timeout = 1s

-- View deadlock information in logs
-- Check PostgreSQL logs for detailed deadlock info

-- Prevent deadlocks by consistent ordering
-- Always access tables/rows in the same order

-- Before (potential deadlock):
-- Session 1: UPDATE accounts SET balance = balance - 100 WHERE id = 1;
--            UPDATE accounts SET balance = balance + 100 WHERE id = 2;
-- Session 2: UPDATE accounts SET balance = balance - 50 WHERE id = 2;
--            UPDATE accounts SET balance = balance + 50 WHERE id = 1;

-- After (consistent ordering):
-- Always update lower ID first
UPDATE accounts SET balance = balance + 
    CASE id WHEN 1 THEN -100 WHEN 2 THEN 100 END
WHERE id IN (1, 2);
```

### Long-Running Transactions

```sql
-- Find long-running transactions
SELECT 
    pid,
    now() - xact_start AS transaction_duration,
    now() - query_start AS query_duration,
    state,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
AND state != 'idle'
ORDER BY xact_start;

-- Set statement timeout
SET statement_timeout = '30s';

-- Set idle transaction timeout (PostgreSQL 14+)
SET idle_in_transaction_session_timeout = '5min';

-- Or globally in postgresql.conf
statement_timeout = 30000  -- 30 seconds
idle_in_transaction_session_timeout = 300000  -- 5 minutes
```

---

## Replication Problems

### Replication Lag

```sql
-- On primary: Check replication status
SELECT 
    client_addr,
    state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS lag_size,
    EXTRACT(EPOCH FROM (now() - reply_time))::int AS lag_seconds
FROM pg_stat_replication;

-- On replica: Check lag
SELECT 
    now() - pg_last_xact_replay_timestamp() AS replication_lag,
    pg_is_in_recovery() AS is_replica,
    pg_last_wal_receive_lsn() AS receive_lsn,
    pg_last_wal_replay_lsn() AS replay_lsn;
```

**Solutions:**

```bash
# Increase wal_keep_size if replicas fall behind
# postgresql.conf (primary)
wal_keep_size = 2GB

# Use replication slots (prevents WAL removal)
SELECT pg_create_physical_replication_slot('replica1_slot');

# In replica's recovery.conf/postgresql.conf
primary_slot_name = 'replica1_slot'
```

### Replica Not Connecting

```
FATAL: could not connect to the primary server: connection refused
```

**Diagnosis:**

```bash
# On replica, check recovery status
SELECT pg_is_in_recovery();

# Check primary_conninfo in postgresql.conf or recovery.conf
primary_conninfo = 'host=primary-host port=5432 user=replicator password=secret'

# Check replication user permissions on primary
SELECT * FROM pg_user WHERE usename = 'replicator';

# Check pg_hba.conf on primary
host    replication    replicator    replica-ip/32    scram-sha-256
```

### WAL Archiving Failures

```sql
-- Check archive status
SELECT * FROM pg_stat_archiver;

-- Common error: archive_command failing
-- Check archive_command in postgresql.conf
archive_command = 'cp %p /var/lib/postgresql/archive/%f'

-- Test archive command manually
cp /var/lib/postgresql/14/main/pg_wal/000000010000000000000001 /var/lib/postgresql/archive/

-- Check disk space on archive destination
df -h /var/lib/postgresql/archive/
```

---

## Storage and Disk Issues

### Error: "No space left on device"

```
ERROR: could not extend file "base/16384/16385": No space left on device
```

**Immediate Actions:**

```bash
# Check disk usage
df -h

# Find large files
du -sh /var/lib/postgresql/*
du -sh /var/lib/postgresql/14/main/*

# Check WAL size
du -sh /var/lib/postgresql/14/main/pg_wal/

# Check for bloated tables
```

```sql
-- Find largest tables
SELECT 
    nspname || '.' || relname AS table,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
    pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE relkind = 'r'
ORDER BY pg_total_relation_size(c.oid) DESC
LIMIT 20;

-- Find tables with bloat
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname || '.' || tablename)) AS total_size,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_percentage
FROM pg_stat_user_tables
WHERE n_dead_tup > 10000
ORDER BY n_dead_tup DESC;
```

**Solutions:**

```sql
-- Clean up dead tuples
VACUUM FULL large_table;  -- Caution: locks table

-- Or run regular vacuum (less aggressive)
VACUUM VERBOSE large_table;

-- Delete old data
DELETE FROM logs WHERE created_at < NOW() - INTERVAL '90 days';
VACUUM logs;

-- Clean up WAL files (if using slots)
SELECT pg_drop_replication_slot('unused_slot');

-- Archive and remove old backups
```

### Table Bloat

```sql
-- Estimate table bloat using pgstattuple extension
CREATE EXTENSION pgstattuple;

SELECT * FROM pgstattuple('large_table');

-- Check bloat ratio
SELECT 
    table_len,
    tuple_count,
    dead_tuple_count,
    dead_tuple_len,
    free_space,
    round(100.0 * dead_tuple_len / table_len, 2) AS dead_percent
FROM pgstattuple('large_table');

-- Fix bloat
-- Option 1: VACUUM FULL (locks table)
VACUUM FULL large_table;

-- Option 2: pg_repack (minimal locking)
-- Install pg_repack extension
pg_repack -d mydb -t large_table

-- Option 3: Create new table and swap
CREATE TABLE large_table_new AS SELECT * FROM large_table;
-- Add indexes, constraints
BEGIN;
ALTER TABLE large_table RENAME TO large_table_old;
ALTER TABLE large_table_new RENAME TO large_table;
COMMIT;
DROP TABLE large_table_old;
```

---

## Memory Problems

### Out of Memory Errors

```
ERROR: out of memory
DETAIL: Failed on request of size 12345678
```

**Solutions:**

```sql
-- Reduce work_mem for specific sessions
SET work_mem = '64MB';

-- Check for memory-heavy queries
SELECT pid, usename, 
       pg_size_pretty(temp_files_bytes) AS temp_disk,
       query
FROM pg_stat_activity
WHERE temp_files_bytes > 0;

-- Limit hash operations memory
SET hash_mem_multiplier = 1.0;  -- PostgreSQL 13+

-- Check current memory settings
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
```

**Configuration:**

```ini
# postgresql.conf
# Don't exceed available RAM
shared_buffers = 4GB  # ~25% of RAM
work_mem = 128MB       # Per operation
maintenance_work_mem = 1GB
effective_cache_size = 12GB  # ~75% of RAM

# Limit connections to prevent memory exhaustion
max_connections = 100

# Per-connection memory = work_mem * operations
# Total memory = shared_buffers + (max_connections * work_mem * operations)
```

### Shared Memory Errors

```
FATAL: could not map anonymous shared memory: Cannot allocate memory
```

**Solutions:**

```bash
# Check system shared memory limits
sysctl -a | grep shm
cat /proc/sys/kernel/shmmax

# Increase limits (Linux)
sudo sysctl -w kernel.shmmax=8589934592
sudo sysctl -w kernel.shmall=2097152

# Make permanent in /etc/sysctl.conf
kernel.shmmax = 8589934592
kernel.shmall = 2097152

# For huge pages
sudo sysctl -w vm.nr_hugepages=2200

# In postgresql.conf
huge_pages = try  # or 'on'
```

---

## Query Errors

### Syntax Errors

```sql
-- ERROR: syntax error at or near "..."

-- Common causes:
-- 1. Reserved keywords as identifiers
-- Wrong:
SELECT from, to FROM flights;
-- Fix:
SELECT "from", "to" FROM flights;

-- 2. Missing quotes
-- Wrong:
SELECT * FROM users WHERE name = John;
-- Fix:
SELECT * FROM users WHERE name = 'John';

-- 3. Wrong string concatenation
-- Wrong:
SELECT first_name + last_name FROM users;
-- Fix:
SELECT first_name || last_name FROM users;
```

### Type Mismatch Errors

```sql
-- ERROR: operator does not exist: integer = text
-- Fix with explicit cast:
SELECT * FROM orders WHERE order_id = '123'::integer;

-- ERROR: cannot cast type boolean to integer
-- Fix:
SELECT CASE WHEN is_active THEN 1 ELSE 0 END FROM users;

-- Type conversion functions
SELECT 
    '123'::integer AS to_int,
    123::text AS to_text,
    '2024-01-15'::date AS to_date,
    '{"a":1}'::jsonb AS to_jsonb;
```

### NULL Handling Errors

```sql
-- Wrong: NULL comparisons
SELECT * FROM users WHERE middle_name = NULL;  -- Always returns 0 rows!

-- Fix:
SELECT * FROM users WHERE middle_name IS NULL;

-- NULL in NOT IN
-- This returns no rows even if values exist!
SELECT * FROM orders WHERE customer_id NOT IN (SELECT id FROM inactive_customers);
-- If inactive_customers has NULL values, entire result is empty

-- Fix:
SELECT * FROM orders o
WHERE NOT EXISTS (
    SELECT 1 FROM inactive_customers ic WHERE ic.id = o.customer_id
);

-- Or exclude NULLs explicitly:
SELECT * FROM orders 
WHERE customer_id NOT IN (
    SELECT id FROM inactive_customers WHERE id IS NOT NULL
);
```

---

## Data Corruption

### Detecting Corruption

```sql
-- Check for index corruption
SELECT schemaname, tablename, indexname
FROM pg_indexes
WHERE indexdef IS NULL;

-- Verify table integrity
-- Using amcheck extension (PostgreSQL 10+)
CREATE EXTENSION amcheck;

-- Check B-tree index structure
SELECT bt_index_check('idx_users_email');

-- Check with parent verification
SELECT bt_index_parent_check('idx_users_email');

-- Checksum verification (if enabled)
SHOW data_checksums;  -- Must be 'on'
```

### Recovery from Corruption

```sql
-- Rebuild corrupted index
REINDEX INDEX idx_users_email;

-- Rebuild all indexes in table
REINDEX TABLE users;

-- Rebuild all indexes in database
REINDEX DATABASE mydb;

-- If table data is corrupted
-- 1. Try to dump what you can
pg_dump -t table_name dbname > table_backup.sql

-- 2. Set zero_damaged_pages to skip bad pages
SET zero_damaged_pages = on;
SELECT * FROM damaged_table;  -- Will skip corrupted pages

-- 3. Restore from backup
pg_restore -d mydb backup.dump
```

---

## Backup and Recovery Issues

### pg_dump Failures

```bash
# Error: pg_dump: error: connection to database failed
pg_dump -h localhost -U postgres mydb > backup.sql

# Check connection
psql -h localhost -U postgres -d mydb

# Error: permission denied
# Fix: Ensure user has SELECT privileges
GRANT SELECT ON ALL TABLES IN SCHEMA public TO backup_user;

# Error: out of memory during dump
# Use directory format with parallel jobs
pg_dump -Fd -j 4 -f backup_dir mydb

# Error: table is locked
# Use --lock-timeout
pg_dump --lock-timeout=60000 mydb > backup.sql
```

### Point-in-Time Recovery (PITR)

```bash
# Prerequisites:
# - archive_mode = on
# - archive_command configured
# - Base backup available

# 1. Stop PostgreSQL
sudo systemctl stop postgresql

# 2. Clear data directory (backup first!)
mv /var/lib/postgresql/14/main /var/lib/postgresql/14/main_old
mkdir /var/lib/postgresql/14/main

# 3. Restore base backup
tar -xf base_backup.tar -C /var/lib/postgresql/14/main

# 4. Configure recovery
cat > /var/lib/postgresql/14/main/postgresql.auto.conf << EOF
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
recovery_target_time = '2024-01-15 14:30:00'
recovery_target_action = 'promote'
EOF

# 5. Create recovery signal file
touch /var/lib/postgresql/14/main/recovery.signal

# 6. Fix permissions
chown -R postgres:postgres /var/lib/postgresql/14/main

# 7. Start PostgreSQL
sudo systemctl start postgresql

# 8. Verify recovery
psql -c "SELECT pg_is_in_recovery();"
```

---

## Monitoring and Diagnostics

### Essential Monitoring Queries

```sql
-- Database size
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) AS size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;

-- Connection status
SELECT 
    state,
    count(*) AS connections,
    max(now() - query_start) AS max_duration
FROM pg_stat_activity
GROUP BY state;

-- Cache hit ratio (should be > 99%)
SELECT 
    sum(heap_blks_hit) AS hits,
    sum(heap_blks_read) AS reads,
    round(100.0 * sum(heap_blks_hit) / 
          NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) AS ratio
FROM pg_statio_user_tables;

-- Transaction rate
SELECT 
    xact_commit + xact_rollback AS total_transactions,
    xact_commit AS commits,
    xact_rollback AS rollbacks
FROM pg_stat_database
WHERE datname = current_database();

-- Checkpoint activity
SELECT 
    checkpoints_timed,
    checkpoints_req,
    checkpoint_write_time,
    checkpoint_sync_time,
    buffers_checkpoint
FROM pg_stat_bgwriter;
```

### Setting Up pg_stat_statements

```sql
-- Enable extension
CREATE EXTENSION pg_stat_statements;

-- Add to postgresql.conf
shared_preload_libraries = 'pg_stat_statements'
pg_stat_statements.track = all

-- Query slow statements
SELECT 
    substring(query, 1, 80) AS query,
    calls,
    round(total_exec_time::numeric / 1000, 2) AS total_sec,
    round(mean_exec_time::numeric, 2) AS mean_ms,
    round(stddev_exec_time::numeric, 2) AS stddev_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

### Log Analysis

```bash
# Key log settings in postgresql.conf
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_min_duration_statement = 1000  # Log slow queries (ms)
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on
log_temp_files = 0  # Log all temp files

# Analyze logs with pgBadger
pgbadger /var/log/postgresql/postgresql-*.log -o report.html

# Search for errors
grep -i "error\|fatal\|panic" /var/log/postgresql/*.log

# Find slow queries
grep "duration:" /var/log/postgresql/*.log | awk -F'duration: ' '{print $2}' | sort -rn | head -20
```

---

## Quick Reference

### Emergency Commands

```sql
-- Kill all connections to a database
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE datname = 'mydb' AND pid <> pg_backend_pid();

-- Cancel running query (graceful)
SELECT pg_cancel_backend(pid);

-- Terminate connection (force)
SELECT pg_terminate_backend(pid);

-- Force checkpoint
CHECKPOINT;

-- Switch to new WAL file
SELECT pg_switch_wal();

-- Reload configuration without restart
SELECT pg_reload_conf();
```

### Common Error Messages Quick Fix

| Error | Quick Fix |
|-------|-----------|
| Connection refused | Check PostgreSQL is running, check port |
| Password authentication failed | Reset password, check pg_hba.conf |
| Permission denied | GRANT appropriate privileges |
| Relation does not exist | Check schema search_path |
| Deadlock detected | Retry transaction, fix query order |
| Out of disk space | VACUUM, delete old data, add storage |
| Too many connections | Use connection pooler, increase limit |
| Query timeout | Optimize query, increase timeout |

---

## Summary

Effective troubleshooting requires:
1. **Good monitoring** - Know your baseline
2. **Proper logging** - Capture relevant information
3. **Systematic approach** - Diagnose before fixing
4. **Regular maintenance** - Prevent issues proactively

---

## Next Steps

- [PostgreSQL Internals](48-postgresql-internals.md)
- [Performance Tuning](39-performance-analysis.md)
- [Backup and Recovery](40-backup-recovery.md)
