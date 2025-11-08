# Monitoring and Logging

## Overview

Effective monitoring and logging are essential for database performance, troubleshooting, and security. This comprehensive guide covers PostgreSQL monitoring tools, system views, logging configuration, query performance tracking, and alerting strategies.

## Table of Contents
- [Monitoring Basics](#monitoring-basics)
- [System Catalogs and Views](#system-catalogs-and-views)
- [pg_stat_statements](#pg_stat_statements)
- [Logging Configuration](#logging-configuration)
- [Query Performance Monitoring](#query-performance-monitoring)
- [System Metrics](#system-metrics)
- [Monitoring Tools](#monitoring-tools)
- [Alerting and Notifications](#alerting-and-notifications)
- [Log Analysis](#log-analysis)
- [Monitoring Best Practices](#monitoring-best-practices)

## Monitoring Basics

### What to Monitor

```sql
-- Key metrics to monitor:

-- 1. Performance Metrics
-- - Query execution time
-- - Throughput (queries per second)
-- - Transaction rate
-- - Cache hit ratio
-- - Index usage

-- 2. Resource Utilization
-- - CPU usage
-- - Memory usage
-- - Disk I/O
-- - Network I/O
-- - Connection count

-- 3. Database Health
-- - Database size
-- - Table/index bloat
-- - Replication lag
-- - Vacuum/autovacuum activity
-- - Lock contention

-- 4. Security
-- - Failed login attempts
-- - Unauthorized access attempts
-- - Privilege escalations
-- - Configuration changes

-- 5. Availability
-- - Database uptime
-- - Connection failures
-- - Backup success/failure
-- - Replication status
```

### Monitoring Strategy

```sql
-- Three levels of monitoring:

-- 1. Real-time (< 1 minute interval)
-- - Active connections
-- - Current query execution
-- - Lock contention
-- - Replication lag

-- 2. Short-term (1-5 minute interval)
-- - Query performance trends
-- - Cache hit ratio
-- - Transaction rate
-- - Resource utilization

-- 3. Long-term (hourly/daily)
-- - Database growth
-- - Capacity planning
-- - Performance trends
-- - Historical analysis
```

## System Catalogs and Views

### pg_stat_activity

```sql
-- Current database activity

SELECT 
    pid,
    usename,
    application_name,
    client_addr,
    state,
    query_start,
    state_change,
    wait_event_type,
    wait_event,
    query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY query_start;

-- Count connections by state
SELECT 
    state,
    count(*) as connection_count
FROM pg_stat_activity
GROUP BY state
ORDER BY connection_count DESC;

-- Find long-running queries
SELECT 
    pid,
    now() - query_start as duration,
    usename,
    state,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC;

-- Find idle in transaction
SELECT 
    pid,
    usename,
    application_name,
    now() - state_change as idle_duration,
    query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
  AND now() - state_change > interval '5 minutes'
ORDER BY idle_duration DESC;

-- Kill long-running query
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE pid = 12345;  -- Replace with actual PID
```

### pg_stat_database

```sql
-- Database-wide statistics

SELECT 
    datname,
    numbackends as active_connections,
    xact_commit as commits,
    xact_rollback as rollbacks,
    blks_read as disk_blocks_read,
    blks_hit as cache_blocks_hit,
    round(100.0 * blks_hit / nullif(blks_hit + blks_read, 0), 2) as cache_hit_ratio,
    tup_returned as rows_returned,
    tup_fetched as rows_fetched,
    tup_inserted as rows_inserted,
    tup_updated as rows_updated,
    tup_deleted as rows_deleted,
    conflicts,
    temp_files,
    temp_bytes,
    deadlocks,
    blk_read_time,
    blk_write_time
FROM pg_stat_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY datname;

-- Transaction rate
SELECT 
    datname,
    xact_commit + xact_rollback as total_transactions,
    round((xact_commit + xact_rollback) / 
          EXTRACT(EPOCH FROM (now() - stats_reset)), 2) as tps
FROM pg_stat_database
WHERE datname = current_database();

-- Cache hit ratio (should be > 95%)
SELECT 
    datname,
    round(100.0 * blks_hit / nullif(blks_hit + blks_read, 0), 2) as cache_hit_ratio
FROM pg_stat_database
WHERE datname = current_database();
```

### pg_stat_user_tables

```sql
-- Table-level statistics

SELECT 
    schemaname,
    relname as table_name,
    seq_scan as sequential_scans,
    seq_tup_read as seq_rows_read,
    idx_scan as index_scans,
    idx_tup_fetch as index_rows_fetched,
    n_tup_ins as rows_inserted,
    n_tup_upd as rows_updated,
    n_tup_del as rows_deleted,
    n_tup_hot_upd as hot_updates,
    n_live_tup as live_rows,
    n_dead_tup as dead_rows,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_row_percent,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- Tables needing vacuum
SELECT 
    schemaname,
    relname,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
  AND (n_dead_tup::float / nullif(n_live_tup + n_dead_tup, 0)) > 0.1
ORDER BY dead_ratio DESC;

-- Tables with high sequential scans (may need indexes)
SELECT 
    schemaname,
    relname,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / nullif(seq_scan, 0) as avg_seq_rows
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC
LIMIT 20;
```

### pg_stat_user_indexes

```sql
-- Index usage statistics

SELECT 
    schemaname,
    relname as table_name,
    indexrelname as index_name,
    idx_scan as index_scans,
    idx_tup_read as index_rows_read,
    idx_tup_fetch as index_rows_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan
LIMIT 20;

-- Unused indexes (candidates for removal)
SELECT 
    schemaname,
    relname as table_name,
    indexrelname as index_name,
    idx_scan as scans,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'  -- Exclude primary keys
  AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC;

-- Index hit ratio
SELECT 
    schemaname,
    relname,
    indexrelname,
    idx_scan,
    round(100.0 * idx_tup_fetch / nullif(idx_tup_read, 0), 2) as hit_ratio
FROM pg_stat_user_indexes
WHERE idx_scan > 0
ORDER BY idx_scan DESC
LIMIT 20;
```

### pg_locks

```sql
-- Lock monitoring

SELECT 
    l.locktype,
    l.database,
    l.relation::regclass as relation,
    l.page,
    l.tuple,
    l.transactionid,
    l.mode,
    l.granted,
    a.usename,
    a.query,
    a.pid
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE NOT l.granted
ORDER BY l.pid;

-- Blocking queries
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_query,
    blocking_activity.query AS blocking_query
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Lock wait times
SELECT 
    pid,
    usename,
    wait_event_type,
    wait_event,
    now() - query_start as wait_time,
    query
FROM pg_stat_activity
WHERE wait_event IS NOT NULL
  AND wait_event_type = 'Lock'
ORDER BY wait_time DESC;
```

## pg_stat_statements

### Installing pg_stat_statements

```sql
-- Enable pg_stat_statements extension

-- 1. Add to postgresql.conf
-- shared_preload_libraries = 'pg_stat_statements'
-- pg_stat_statements.max = 10000
-- pg_stat_statements.track = all

-- 2. Restart PostgreSQL
-- $ pg_ctl restart

-- 3. Create extension in database
CREATE EXTENSION pg_stat_statements;

-- Verify installation
SELECT * FROM pg_available_extensions WHERE name = 'pg_stat_statements';
```

### Query Performance Analysis

```sql
-- Top queries by total time
SELECT 
    queryid,
    substring(query, 1, 100) as query_snippet,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time,
    rows,
    100.0 * shared_blks_hit / nullif(shared_blks_hit + shared_blks_read, 0) as hit_ratio
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Slowest queries by average time
SELECT 
    queryid,
    substring(query, 1, 100) as query_snippet,
    calls,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
WHERE calls > 10  -- Only queries called multiple times
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Most frequently called queries
SELECT 
    queryid,
    substring(query, 1, 100) as query_snippet,
    calls,
    total_exec_time,
    mean_exec_time,
    rows / nullif(calls, 0) as avg_rows
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;

-- Queries with high variability (inconsistent performance)
SELECT 
    queryid,
    substring(query, 1, 100) as query_snippet,
    calls,
    mean_exec_time,
    stddev_exec_time,
    round(100.0 * stddev_exec_time / nullif(mean_exec_time, 0), 2) as variability_percent
FROM pg_stat_statements
WHERE calls > 100
  AND stddev_exec_time > 0
ORDER BY variability_percent DESC
LIMIT 20;

-- Queries causing most disk I/O
SELECT 
    queryid,
    substring(query, 1, 100) as query_snippet,
    calls,
    shared_blks_read + shared_blks_written as total_io,
    shared_blks_read,
    shared_blks_written,
    local_blks_read,
    local_blks_written,
    temp_blks_read,
    temp_blks_written
FROM pg_stat_statements
ORDER BY total_io DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

## Logging Configuration

### Logging Settings

```sql
-- Configure logging in postgresql.conf

-- Where to log
-- logging_collector = on
-- log_directory = 'log'
-- log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
-- log_file_mode = 0600

-- When to log
-- log_rotation_age = 1d
-- log_rotation_size = 100MB
-- log_truncate_on_rotation = off

-- What to log
-- log_connections = on
-- log_disconnections = on
-- log_duration = off  (use log_min_duration_statement instead)
-- log_statement = 'none'  ('none', 'ddl', 'mod', 'all')
-- log_min_duration_statement = 1000  (log queries > 1 second)

-- Log line format
-- log_line_prefix = '%m [%p] %u@%d %h '
-- %m: timestamp
-- %p: PID
-- %u: username
-- %d: database
-- %h: remote host
-- %a: application name
-- %i: command tag
-- %e: SQL state

-- Error severity
-- log_min_messages = warning
-- log_min_error_statement = error

-- Apply configuration
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_min_duration_statement = 1000;
ALTER SYSTEM SET log_line_prefix = '%m [%p] %u@%d %h ';
SELECT pg_reload_conf();

-- View current logging settings
SELECT name, setting, unit, context 
FROM pg_settings 
WHERE name LIKE 'log_%' 
   OR name = 'logging_collector'
ORDER BY name;
```

### Logging Slow Queries

```sql
-- Log queries exceeding duration threshold

-- Set globally
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- 1 second
SELECT pg_reload_conf();

-- Set per session
SET log_min_duration_statement = 500;  -- 500ms

-- Set per database
ALTER DATABASE mydb SET log_min_duration_statement = 1000;

-- Set per user
ALTER ROLE app_user SET log_min_duration_statement = 2000;

-- Set per function
ALTER FUNCTION expensive_function() SET log_min_duration_statement = 5000;

-- View slow query logs
-- $ grep "duration:" /var/log/postgresql/postgresql-*.log
-- Example output:
-- 2024-01-15 10:30:45 [12345] user@mydb 10.0.1.5 LOG: duration: 1234.567 ms statement: SELECT * FROM large_table WHERE ...
```

### Auto_explain

```sql
-- Automatically log query plans for slow queries

-- 1. Enable auto_explain
-- Add to postgresql.conf:
-- shared_preload_libraries = 'auto_explain'
-- auto_explain.log_min_duration = 1000  (log plans for queries > 1s)
-- auto_explain.log_analyze = true  (include actual execution stats)
-- auto_explain.log_buffers = true  (include buffer usage)
-- auto_explain.log_timing = true  (include timing information)
-- auto_explain.log_triggers = true  (include trigger execution)
-- auto_explain.log_verbose = false  (verbose output)
-- auto_explain.log_nested_statements = true  (log nested statements)

-- 2. Restart PostgreSQL
-- $ pg_ctl restart

-- 3. Set per session
LOAD 'auto_explain';
SET auto_explain.log_min_duration = 1000;
SET auto_explain.log_analyze = true;

-- Query plans will be logged automatically
-- Check logs:
-- $ grep "Query Text:" /var/log/postgresql/postgresql-*.log
```

## Query Performance Monitoring

### Real-Time Query Monitoring

```sql
-- Monitor currently executing queries

CREATE VIEW current_queries AS
SELECT 
    pid,
    now() - query_start as duration,
    usename,
    application_name,
    client_addr,
    state,
    wait_event_type,
    wait_event,
    substring(query, 1, 100) as query_snippet
FROM pg_stat_activity
WHERE state = 'active'
  AND pid != pg_backend_pid()
ORDER BY duration DESC;

SELECT * FROM current_queries;

-- Query execution progress (for some operations)
SELECT 
    pid,
    datname,
    relid::regclass as table_name,
    phase,
    round(100.0 * blocks_done / nullif(blocks_total, 0), 2) as percent_complete,
    blocks_done,
    blocks_total
FROM pg_stat_progress_vacuum;

-- Index creation progress
SELECT 
    pid,
    datname,
    relid::regclass as table_name,
    index_relid::regclass as index_name,
    phase,
    round(100.0 * blocks_done / nullif(blocks_total, 0), 2) as percent_complete,
    tuples_done,
    tuples_total
FROM pg_stat_progress_create_index;
```

### Query Performance Trends

```sql
-- Track query performance over time

-- Create performance history table
CREATE TABLE query_performance_history (
    recorded_at TIMESTAMP DEFAULT now(),
    queryid BIGINT,
    query TEXT,
    calls BIGINT,
    total_time DOUBLE PRECISION,
    mean_time DOUBLE PRECISION,
    max_time DOUBLE PRECISION,
    stddev_time DOUBLE PRECISION
);

-- Snapshot current performance
INSERT INTO query_performance_history (
    queryid, query, calls, total_time, mean_time, max_time, stddev_time
)
SELECT 
    queryid,
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    stddev_exec_time
FROM pg_stat_statements
WHERE calls > 10;

-- Compare performance over time
SELECT 
    h1.query,
    h1.mean_time as old_mean_time,
    h2.mean_time as new_mean_time,
    round(100.0 * (h2.mean_time - h1.mean_time) / h1.mean_time, 2) as percent_change
FROM query_performance_history h1
JOIN query_performance_history h2 ON h1.queryid = h2.queryid
WHERE h1.recorded_at = (SELECT min(recorded_at) FROM query_performance_history)
  AND h2.recorded_at = (SELECT max(recorded_at) FROM query_performance_history)
  AND abs(h2.mean_time - h1.mean_time) > 100  -- Significant change
ORDER BY percent_change DESC;
```

## System Metrics

### Database Size

```sql
-- Database sizes
SELECT 
    datname,
    pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
WHERE datname NOT IN ('template0', 'template1')
ORDER BY pg_database_size(datname) DESC;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - 
                   pg_relation_size(schemaname||'.'||tablename)) as index_size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- Index sizes
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(schemaname||'.'||indexname)) as size
FROM pg_indexes
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(schemaname||'.'||indexname) DESC
LIMIT 20;

-- Database growth rate
SELECT 
    current_database() as database,
    pg_size_pretty(pg_database_size(current_database())) as current_size;
-- Run periodically and compare
```

### Table Bloat

```sql
-- Estimate table bloat

SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
    round(100 * (pg_relation_size(schemaname||'.'||tablename) - 
                (n_live_tup * 
                 (current_setting('block_size')::integer / 
                  coalesce(nullif(n_live_tup, 0), 1)))) / 
          nullif(pg_relation_size(schemaname||'.'||tablename), 0), 2) as estimated_bloat_percent,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename) - 
                  (n_live_tup * 
                   (current_setting('block_size')::integer / 
                    coalesce(nullif(n_live_tup, 0), 1)))) as estimated_bloat_size
FROM pg_stat_user_tables
WHERE pg_relation_size(schemaname||'.'||tablename) > 10485760  -- > 10MB
ORDER BY pg_relation_size(schemaname||'.'||tablename) DESC
LIMIT 20;

-- Index bloat (simplified estimate)
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE pg_relation_size(indexrelid) > 10485760  -- > 10MB
  AND idx_scan = 0  -- Never used
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Vacuum and Autovacuum

```sql
-- Vacuum activity monitoring

SELECT 
    schemaname,
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count,
    n_dead_tup,
    n_live_tup,
    round(100.0 * n_dead_tup / nullif(n_live_tup + n_dead_tup, 0), 2) as dead_ratio
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC
LIMIT 20;

-- Current vacuum operations
SELECT 
    pid,
    datname,
    relid::regclass as table_name,
    phase,
    heap_blks_total,
    heap_blks_scanned,
    heap_blks_vacuumed,
    index_vacuum_count,
    max_dead_tuples,
    num_dead_tuples
FROM pg_stat_progress_vacuum;

-- Autovacuum configuration per table
SELECT 
    schemaname,
    tablename,
    reloptions
FROM pg_tables
WHERE reloptions IS NOT NULL;
```

## Monitoring Tools

### pgAdmin

```sql
-- pgAdmin: Web-based PostgreSQL management tool
-- Features:
-- - Dashboard with server statistics
-- - Query tool with explain plans
-- - Database object browser
-- - Backup/restore interface
-- - User management

-- Install pgAdmin:
-- $ pip install pgadmin4
-- Access via web browser: http://localhost:5050
```

### pg_top

```sql
-- pg_top: Real-time activity monitor (like Unix 'top')
-- Shows active queries, connections, locks

-- Install:
-- $ apt-get install pgtop

-- Run:
-- $ pg_top -h localhost -U postgres

-- Features:
-- - Real-time query monitoring
-- - Connection statistics
-- - Lock visualization
-- - Resource usage
```

### Prometheus and Grafana

```sql
-- Prometheus: Metrics collection
-- Grafana: Visualization and dashboards

-- 1. Install postgres_exporter
-- $ docker run -d -p 9187:9187 -e DATA_SOURCE_NAME="postgresql://user:pass@localhost:5432/postgres?sslmode=disable" prometheuscommunity/postgres-exporter

-- 2. Configure Prometheus to scrape postgres_exporter
-- prometheus.yml:
-- scrape_configs:
--   - job_name: 'postgresql'
--     static_configs:
--       - targets: ['localhost:9187']

-- 3. Import PostgreSQL dashboard in Grafana
-- Dashboard ID: 9628 (PostgreSQL Database)

-- Metrics exposed:
-- - pg_up: Database is up
-- - pg_stat_database_*: Database statistics
-- - pg_stat_bgwriter_*: Background writer statistics
-- - pg_replication_lag: Replication lag
-- - pg_locks_*: Lock statistics
```

### pgBadger

```sql
-- pgBadger: PostgreSQL log analyzer

-- Install:
-- $ apt-get install pgbadger

-- Generate report from logs:
-- $ pgbadger /var/log/postgresql/postgresql-*.log -o report.html

-- Features:
-- - Query performance analysis
-- - Connection statistics
-- - Error analysis
-- - Lock analysis
-- - Temporary file usage
-- - Checkpoints and WAL statistics

-- View report:
-- $ firefox report.html
```

## Alerting and Notifications

### Alert Conditions

```sql
-- Define alert thresholds

CREATE TABLE alert_thresholds (
    metric_name TEXT PRIMARY KEY,
    warning_threshold NUMERIC,
    critical_threshold NUMERIC,
    description TEXT
);

INSERT INTO alert_thresholds VALUES
    ('connection_usage_percent', 80, 95, 'Percentage of max_connections in use'),
    ('replication_lag_bytes', 10485760, 104857600, 'Replication lag in bytes (10MB, 100MB)'),
    ('cache_hit_ratio', 95, 90, 'Cache hit ratio percentage'),
    ('dead_tuple_ratio', 10, 20, 'Dead tuple percentage'),
    ('disk_usage_percent', 80, 90, 'Disk usage percentage'),
    ('query_duration_seconds', 5, 30, 'Long-running query duration'),
    ('lock_wait_seconds', 30, 300, 'Lock wait time');

-- Check function
CREATE OR REPLACE FUNCTION check_alerts()
RETURNS TABLE (
    metric TEXT,
    severity TEXT,
    current_value NUMERIC,
    threshold NUMERIC,
    message TEXT
) AS $$
BEGIN
    -- Connection usage
    RETURN QUERY
    WITH conn_stats AS (
        SELECT count(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as pct
        FROM pg_stat_activity
    )
    SELECT 
        'connection_usage_percent'::TEXT,
        CASE 
            WHEN pct >= critical_threshold THEN 'CRITICAL'
            WHEN pct >= warning_threshold THEN 'WARNING'
            ELSE 'OK'
        END,
        pct,
        warning_threshold,
        'Connection usage at ' || round(pct, 2) || '%'
    FROM conn_stats, alert_thresholds
    WHERE metric_name = 'connection_usage_percent'
      AND pct >= warning_threshold;
    
    -- Replication lag
    RETURN QUERY
    SELECT 
        'replication_lag_bytes'::TEXT,
        CASE 
            WHEN lag_bytes >= critical_threshold THEN 'CRITICAL'
            WHEN lag_bytes >= warning_threshold THEN 'WARNING'
            ELSE 'OK'
        END,
        lag_bytes,
        warning_threshold,
        'Replication lag: ' || pg_size_pretty(lag_bytes::bigint)
    FROM (
        SELECT pg_wal_lsn_diff(sent_lsn, replay_lsn)::numeric as lag_bytes
        FROM pg_stat_replication
    ) r, alert_thresholds
    WHERE metric_name = 'replication_lag_bytes'
      AND lag_bytes >= warning_threshold;
    
    -- Add more alert checks...
END;
$$ LANGUAGE plpgsql;

-- Run alert checks
SELECT * FROM check_alerts();
```

### Email Notifications

```sql
-- Send email alerts using external tools

-- 1. Create notification function (requires plpython3u)
CREATE EXTENSION plpython3u;

CREATE OR REPLACE FUNCTION send_email_alert(
    p_subject TEXT,
    p_body TEXT,
    p_to_email TEXT
) RETURNS void AS $$
    import smtplib
    from email.mime.text import MIMEText
    
    msg = MIMEText(p_body)
    msg['Subject'] = p_subject
    msg['From'] = 'alerts@example.com'
    msg['To'] = p_to_email
    
    s = smtplib.SMTP('localhost')
    s.send_message(msg)
    s.quit()
$$ LANGUAGE plpython3u;

-- 2. Check and send alerts
DO $$
DECLARE
    alert RECORD;
BEGIN
    FOR alert IN SELECT * FROM check_alerts() WHERE severity IN ('WARNING', 'CRITICAL')
    LOOP
        PERFORM send_email_alert(
            '[' || alert.severity || '] PostgreSQL Alert: ' || alert.metric,
            alert.message || E'\n\nCurrent value: ' || alert.current_value || E'\nThreshold: ' || alert.threshold,
            'dba@example.com'
        );
    END LOOP;
END $$;
```

## Log Analysis

### Parsing Logs

```sql
-- Create log table for analysis

CREATE TABLE postgres_logs (
    log_time TIMESTAMP,
    user_name TEXT,
    database_name TEXT,
    process_id INTEGER,
    connection_from TEXT,
    session_id TEXT,
    session_line_num BIGINT,
    command_tag TEXT,
    session_start_time TIMESTAMP,
    virtual_transaction_id TEXT,
    transaction_id BIGINT,
    error_severity TEXT,
    sql_state_code TEXT,
    message TEXT,
    detail TEXT,
    hint TEXT,
    internal_query TEXT,
    internal_query_pos INTEGER,
    context TEXT,
    query TEXT,
    query_pos INTEGER,
    location TEXT,
    application_name TEXT
);

-- Import logs (CSV format)
-- Requires log_destination = 'csvlog' in postgresql.conf
-- $ COPY postgres_logs FROM '/var/log/postgresql/postgresql-2024-01-15.csv' WITH CSV;

-- Analyze error patterns
SELECT 
    error_severity,
    count(*) as occurrence_count,
    count(DISTINCT message) as unique_messages
FROM postgres_logs
WHERE log_time > now() - interval '24 hours'
  AND error_severity IN ('ERROR', 'FATAL', 'PANIC')
GROUP BY error_severity
ORDER BY occurrence_count DESC;

-- Most common errors
SELECT 
    message,
    count(*) as count,
    min(log_time) as first_seen,
    max(log_time) as last_seen
FROM postgres_logs
WHERE error_severity = 'ERROR'
  AND log_time > now() - interval '24 hours'
GROUP BY message
ORDER BY count DESC
LIMIT 20;

-- Slow query analysis from logs
SELECT 
    user_name,
    database_name,
    substring(query, 1, 100) as query_snippet,
    count(*) as execution_count
FROM postgres_logs
WHERE message LIKE 'duration:%'
  AND log_time > now() - interval '24 hours'
GROUP BY user_name, database_name, query
ORDER BY execution_count DESC;
```

## Monitoring Best Practices

### Best Practices Checklist

```sql
-- [ ] Enable comprehensive logging
--   [ ] log_connections, log_disconnections
--   [ ] log_min_duration_statement for slow queries
--   [ ] auto_explain for query plans
--   [ ] CSV log format for analysis

-- [ ] Install monitoring extensions
--   [ ] pg_stat_statements for query performance
--   [ ] pg_stat_kcache for kernel statistics (if available)

-- [ ] Set up regular monitoring
--   [ ] Real-time dashboard (Grafana)
--   [ ] Hourly metric collection
--   [ ] Daily performance reports
--   [ ] Weekly capacity planning review

-- [ ] Configure alerts
--   [ ] Connection count approaching limit
--   [ ] Replication lag exceeding threshold
--   [ ] Cache hit ratio dropping
--   [ ] Long-running queries
--   [ ] Lock contention
--   [ ] Disk space running low
--   [ ] Backup failures

-- [ ] Baseline performance
--   [ ] Record normal operating metrics
--   [ ] Establish performance baselines
--   [ ] Define SLAs and SLOs

-- [ ] Regular log analysis
--   [ ] Review errors daily
--   [ ] Analyze slow queries weekly
--   [ ] Identify trends monthly

-- [ ] Capacity planning
--   [ ] Monitor database growth
--   [ ] Track resource utilization trends
--   [ ] Forecast capacity needs

-- [ ] Documentation
--   [ ] Document monitoring setup
--   [ ] Create runbooks for common issues
--   [ ] Maintain alert escalation procedures
```

## Summary

PostgreSQL monitoring and logging provides:
- **System Views**: pg_stat_activity, pg_stat_database, pg_stat_user_tables
- **Query Performance**: pg_stat_statements for detailed query analysis
- **Logging**: Comprehensive log configuration and analysis
- **Monitoring Tools**: pgAdmin, Prometheus/Grafana, pgBadger
- **Alerting**: Proactive notification of issues
- **Trends**: Historical analysis and capacity planning

Effective monitoring ensures optimal performance and rapid issue resolution.

## Next Steps

- Study [Performance Troubleshooting](./39-performance-troubleshooting.md)
- Learn [Configuration and Tuning](./34-configuration-and-tuning.md)
- Explore [Query Optimization](./20-query-optimization.md)
- Practice [High Availability](./37-high-availability.md)
