# Part 8: Administration Exercises

## Topics Covered
- Configuration and Tuning (Chapter 34)
- Backup and Recovery (Chapter 35)
- Replication (Chapter 36)
- High Availability (Chapter 37)
- Monitoring and Logging (Chapter 38)

---

## Exercise 8.1: Performance Configuration and Tuning 🔴

### Scenario
Configure PostgreSQL for NeoBank's production workload: high transaction volume, complex reporting queries, and strict performance SLAs.

### Requirements
1. Memory configuration for 64GB RAM server
2. Connection pooling settings
3. Write-ahead logging optimization
4. Query planner tuning

### Solution

```sql
-- Step 1: Create configuration management table
CREATE TABLE IF NOT EXISTS admin.config_settings (
    setting_id SERIAL PRIMARY KEY,
    setting_name VARCHAR(100) NOT NULL,
    current_value TEXT,
    recommended_value TEXT,
    category VARCHAR(50),
    description TEXT,
    requires_restart BOOLEAN DEFAULT FALSE,
    applied_at TIMESTAMPTZ,
    applied_by TEXT
);

-- Step 2: Memory Configuration (for 64GB RAM server)
-- Document current vs recommended settings

INSERT INTO admin.config_settings (setting_name, current_value, recommended_value, category, description, requires_restart)
VALUES 
-- Memory Settings
('shared_buffers', current_setting('shared_buffers'), '16GB', 'memory', 
 '25% of RAM for dedicated DB server', TRUE),
('effective_cache_size', current_setting('effective_cache_size'), '48GB',
 'memory', '75% of RAM - OS cache estimation', FALSE),
('work_mem', current_setting('work_mem'), '256MB', 'memory',
 'Per-operation memory for sorts/hashes. Careful with concurrent connections', FALSE),
('maintenance_work_mem', current_setting('maintenance_work_mem'), '2GB', 'memory',
 'Memory for VACUUM, CREATE INDEX, etc.', FALSE),
('wal_buffers', current_setting('wal_buffers'), '64MB', 'memory',
 'WAL buffer size, -1 for auto (3% of shared_buffers)', TRUE),

-- Connection Settings
('max_connections', current_setting('max_connections'), '200', 'connections',
 'Use connection pooler for more connections', TRUE),

-- WAL Settings
('wal_level', current_setting('wal_level'), 'replica', 'wal',
 'Enable logical for CDC, replica for streaming replication', TRUE),
('max_wal_size', current_setting('max_wal_size'), '4GB', 'wal',
 'Max WAL size before checkpoint', FALSE),
('min_wal_size', current_setting('min_wal_size'), '1GB', 'wal',
 'Min WAL to keep', FALSE),
('checkpoint_completion_target', current_setting('checkpoint_completion_target'), '0.9', 'wal',
 'Spread checkpoint writes over this fraction of interval', FALSE),

-- Query Planner
('random_page_cost', current_setting('random_page_cost'), '1.1', 'planner',
 'Lower for SSD (closer to seq_page_cost)', FALSE),
('effective_io_concurrency', current_setting('effective_io_concurrency'), '200', 'planner',
 'Concurrent I/O operations for SSD', FALSE),
('default_statistics_target', current_setting('default_statistics_target'), '200', 'planner',
 'More statistics for better plans', FALSE),

-- Parallelism
('max_worker_processes', current_setting('max_worker_processes'), '8', 'parallel',
 'Total background workers', TRUE),
('max_parallel_workers_per_gather', current_setting('max_parallel_workers_per_gather'), '4', 'parallel',
 'Workers per parallel query', FALSE),
('max_parallel_workers', current_setting('max_parallel_workers'), '8', 'parallel',
 'Total parallel query workers', FALSE),
('max_parallel_maintenance_workers', current_setting('max_parallel_maintenance_workers'), '4', 'parallel',
 'Workers for VACUUM, CREATE INDEX', FALSE);

-- Step 3: Function to generate ALTER SYSTEM commands
CREATE OR REPLACE FUNCTION admin.generate_config_script()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_script TEXT := '';
    v_rec RECORD;
BEGIN
    v_script := '-- PostgreSQL Configuration Script for NeoBank Production' || E'\n';
    v_script := v_script || '-- Generated: ' || NOW()::TEXT || E'\n\n';
    
    FOR v_rec IN 
        SELECT * FROM admin.config_settings 
        ORDER BY requires_restart DESC, category
    LOOP
        v_script := v_script || format(
            '-- %s: %s%sALTER SYSTEM SET %s = ''%s'';%s',
            v_rec.category,
            v_rec.description,
            E'\n',
            v_rec.setting_name,
            v_rec.recommended_value,
            E'\n\n'
        );
    END LOOP;
    
    v_script := v_script || E'\n-- Apply changes:\n';
    v_script := v_script || '-- For runtime changes: SELECT pg_reload_conf();' || E'\n';
    v_script := v_script || '-- For restart-required changes: Restart PostgreSQL service' || E'\n';
    
    RETURN v_script;
END;
$$;

-- Generate the script
SELECT admin.generate_config_script();

-- Step 4: Workload-specific configurations

-- OLTP-optimized settings (high transaction volume)
CREATE OR REPLACE FUNCTION admin.apply_oltp_profile()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Smaller work_mem for many concurrent simple queries
    ALTER SYSTEM SET work_mem = '64MB';
    
    -- More connections for transaction processing
    ALTER SYSTEM SET max_connections = 300;
    
    -- Faster commits (synchronous_commit can be 'off' for non-critical)
    ALTER SYSTEM SET synchronous_commit = 'on';
    
    -- Frequent checkpoints for faster recovery
    ALTER SYSTEM SET checkpoint_completion_target = 0.9;
    ALTER SYSTEM SET max_wal_size = '2GB';
    
    -- Less aggressive autovacuum (don't compete with transactions)
    ALTER SYSTEM SET autovacuum_vacuum_cost_delay = '20ms';
    
    PERFORM pg_reload_conf();
    
    INSERT INTO admin.config_settings (setting_name, current_value, category, applied_at, applied_by)
    VALUES ('PROFILE', 'OLTP', 'profile', NOW(), CURRENT_USER);
END;
$$;

-- Analytics/Reporting optimized settings
CREATE OR REPLACE FUNCTION admin.apply_analytics_profile()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Larger work_mem for complex queries
    ALTER SYSTEM SET work_mem = '1GB';
    
    -- Enable more parallelism
    ALTER SYSTEM SET max_parallel_workers_per_gather = 4;
    
    -- Larger hash joins
    ALTER SYSTEM SET hash_mem_multiplier = 2.0;
    
    -- More statistics for better plans
    ALTER SYSTEM SET default_statistics_target = 500;
    
    -- JIT compilation for complex queries
    ALTER SYSTEM SET jit = 'on';
    ALTER SYSTEM SET jit_above_cost = 100000;
    
    PERFORM pg_reload_conf();
    
    INSERT INTO admin.config_settings (setting_name, current_value, category, applied_at, applied_by)
    VALUES ('PROFILE', 'Analytics', 'profile', NOW(), CURRENT_USER);
END;
$$;

-- Step 5: Monitor configuration effectiveness
CREATE OR REPLACE VIEW admin.v_buffer_effectiveness AS
SELECT 
    'Shared Buffers' AS metric,
    pg_size_pretty(setting::BIGINT * 8192) AS size,
    ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2) AS hit_ratio_pct
FROM pg_settings, pg_stat_database
WHERE name = 'shared_buffers'
  AND datname = current_database()

UNION ALL

SELECT 
    'Effective Cache',
    current_setting('effective_cache_size'),
    NULL;

-- Step 6: Query to identify configuration issues
CREATE OR REPLACE FUNCTION admin.check_configuration_health()
RETURNS TABLE (
    check_name TEXT,
    current_value TEXT,
    status TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check buffer hit ratio
    RETURN QUERY
    SELECT 
        'Buffer Hit Ratio'::TEXT,
        ROUND(100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0), 2)::TEXT || '%',
        CASE 
            WHEN 100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0) > 99 THEN 'OK'
            WHEN 100.0 * blks_hit / NULLIF(blks_hit + blks_read, 0) > 95 THEN 'WARNING'
            ELSE 'CRITICAL'
        END,
        'Should be > 99% for OLTP workloads'
    FROM pg_stat_database
    WHERE datname = current_database();
    
    -- Check checkpoint frequency
    RETURN QUERY
    SELECT 
        'Checkpoint Frequency',
        checkpoints_req::TEXT || ' requested, ' || checkpoints_timed::TEXT || ' timed',
        CASE 
            WHEN checkpoints_req > checkpoints_timed * 0.1 THEN 'WARNING'
            ELSE 'OK'
        END,
        'Too many requested checkpoints - increase max_wal_size'
    FROM pg_stat_bgwriter;
    
    -- Check connection utilization
    RETURN QUERY
    SELECT 
        'Connection Utilization',
        COUNT(*)::TEXT || ' of ' || current_setting('max_connections'),
        CASE 
            WHEN COUNT(*)::FLOAT / current_setting('max_connections')::FLOAT > 0.9 THEN 'CRITICAL'
            WHEN COUNT(*)::FLOAT / current_setting('max_connections')::FLOAT > 0.7 THEN 'WARNING'
            ELSE 'OK'
        END,
        'Consider connection pooler if > 70%'
    FROM pg_stat_activity
    WHERE backend_type = 'client backend';
    
    -- Check temp file usage
    RETURN QUERY
    SELECT 
        'Temp File Usage',
        pg_size_pretty(temp_bytes),
        CASE 
            WHEN temp_bytes > 1073741824 THEN 'WARNING'  -- > 1GB
            ELSE 'OK'
        END,
        'High temp usage - consider increasing work_mem'
    FROM pg_stat_database
    WHERE datname = current_database();
END;
$$;

SELECT * FROM admin.check_configuration_health();
```

---

## Exercise 8.2: Backup and Recovery Strategy 🔴

### Scenario
Implement a comprehensive backup strategy for NeoBank with different recovery point objectives (RPO) for different data tiers.

### Solution

```sql
-- Step 1: Create backup management schema
CREATE SCHEMA IF NOT EXISTS backup;

-- Backup catalog table
CREATE TABLE IF NOT EXISTS backup.backup_catalog (
    backup_id SERIAL PRIMARY KEY,
    backup_type VARCHAR(20) NOT NULL,  -- 'full', 'incremental', 'wal'
    backup_method VARCHAR(20) NOT NULL, -- 'pg_dump', 'pg_basebackup', 'pgbackrest'
    start_time TIMESTAMPTZ NOT NULL,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) DEFAULT 'running',
    size_bytes BIGINT,
    backup_path TEXT,
    wal_start_lsn PG_LSN,
    wal_end_lsn PG_LSN,
    retention_days INTEGER DEFAULT 30,
    verified BOOLEAN DEFAULT FALSE,
    verification_time TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}'
);

-- Step 2: Logical backup function using pg_dump
CREATE OR REPLACE FUNCTION backup.create_logical_backup(
    p_backup_path TEXT,
    p_schema TEXT DEFAULT NULL,
    p_tables TEXT[] DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_backup_id INTEGER;
    v_filename TEXT;
    v_command TEXT;
BEGIN
    -- Create backup record
    INSERT INTO backup.backup_catalog (backup_type, backup_method, start_time, backup_path)
    VALUES ('full', 'pg_dump', NOW(), p_backup_path)
    RETURNING backup_id INTO v_backup_id;
    
    -- Generate filename
    v_filename := p_backup_path || '/neobank_' || 
                  TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS') || '.dump';
    
    -- Build pg_dump command (would be executed via shell)
    v_command := format(
        'pg_dump -Fc -d %s -f %s',
        current_database(),
        v_filename
    );
    
    IF p_schema IS NOT NULL THEN
        v_command := v_command || ' -n ' || p_schema;
    END IF;
    
    -- Store command for reference
    UPDATE backup.backup_catalog
    SET metadata = jsonb_build_object(
        'command', v_command,
        'filename', v_filename,
        'schema', p_schema,
        'tables', p_tables
    )
    WHERE backup_id = v_backup_id;
    
    RETURN v_backup_id;
END;
$$;

-- Step 3: Function to track WAL archiving status
CREATE OR REPLACE VIEW backup.v_wal_archive_status AS
SELECT 
    archived_count,
    last_archived_wal,
    last_archived_time,
    failed_count,
    last_failed_wal,
    last_failed_time,
    CASE 
        WHEN failed_count > 0 AND last_failed_time > last_archived_time 
        THEN 'ALERT: Recent archive failure'
        WHEN last_archived_time < NOW() - INTERVAL '10 minutes'
        THEN 'WARNING: No recent archives'
        ELSE 'OK'
    END AS status
FROM pg_stat_archiver;

-- Step 4: PITR recovery planning
CREATE TABLE IF NOT EXISTS backup.recovery_points (
    recovery_point_id SERIAL PRIMARY KEY,
    label TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    lsn PG_LSN,
    wal_file TEXT,
    description TEXT,
    created_by TEXT DEFAULT CURRENT_USER
);

-- Create named recovery point
CREATE OR REPLACE FUNCTION backup.create_recovery_point(
    p_label TEXT,
    p_description TEXT DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_recovery_point_id INTEGER;
BEGIN
    -- Create checkpoint for clean recovery point
    CHECKPOINT;
    
    INSERT INTO backup.recovery_points (label, lsn, wal_file, description)
    VALUES (
        p_label,
        pg_current_wal_lsn(),
        pg_walfile_name(pg_current_wal_lsn()),
        p_description
    )
    RETURNING recovery_point_id INTO v_recovery_point_id;
    
    RETURN v_recovery_point_id;
END;
$$;

-- Step 5: Backup verification function
CREATE OR REPLACE FUNCTION backup.verify_backup(p_backup_id INTEGER)
RETURNS TABLE (
    check_name TEXT,
    status TEXT,
    details TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_backup RECORD;
BEGIN
    SELECT * INTO v_backup FROM backup.backup_catalog WHERE backup_id = p_backup_id;
    
    IF NOT FOUND THEN
        RETURN QUERY SELECT 'Backup Exists'::TEXT, 'FAIL'::TEXT, 'Backup not found'::TEXT;
        RETURN;
    END IF;
    
    -- Check 1: Backup completed
    RETURN QUERY
    SELECT 
        'Backup Completed',
        CASE WHEN v_backup.status = 'completed' THEN 'PASS' ELSE 'FAIL' END,
        'Status: ' || v_backup.status;
    
    -- Check 2: Backup size reasonable
    RETURN QUERY
    SELECT 
        'Backup Size',
        CASE 
            WHEN v_backup.size_bytes > 0 THEN 'PASS'
            WHEN v_backup.size_bytes IS NULL THEN 'UNKNOWN'
            ELSE 'FAIL'
        END,
        COALESCE(pg_size_pretty(v_backup.size_bytes), 'Unknown');
    
    -- Check 3: Backup age
    RETURN QUERY
    SELECT 
        'Backup Age',
        CASE 
            WHEN v_backup.start_time > NOW() - INTERVAL '1 day' THEN 'PASS'
            WHEN v_backup.start_time > NOW() - INTERVAL '7 days' THEN 'WARNING'
            ELSE 'FAIL'
        END,
        AGE(NOW(), v_backup.start_time)::TEXT;
    
    -- Update verification timestamp
    UPDATE backup.backup_catalog
    SET verified = TRUE, verification_time = NOW()
    WHERE backup_id = p_backup_id;
END;
$$;

-- Step 6: Retention policy enforcement
CREATE OR REPLACE FUNCTION backup.enforce_retention_policy()
RETURNS TABLE (
    action TEXT,
    backup_id INTEGER,
    backup_time TIMESTAMPTZ,
    age_days INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Mark expired backups
    RETURN QUERY
    UPDATE backup.backup_catalog
    SET status = 'expired'
    WHERE status = 'completed'
      AND start_time < NOW() - (retention_days || ' days')::INTERVAL
    RETURNING 
        'EXPIRED'::TEXT,
        backup_catalog.backup_id,
        start_time,
        EXTRACT(DAY FROM AGE(NOW(), start_time))::INTEGER;
END;
$$;

-- Step 7: Backup monitoring view
CREATE OR REPLACE VIEW backup.v_backup_health AS
WITH backup_stats AS (
    SELECT 
        backup_type,
        MAX(start_time) AS last_backup,
        COUNT(*) FILTER (WHERE start_time > NOW() - INTERVAL '24 hours') AS backups_24h,
        COUNT(*) FILTER (WHERE status = 'completed') AS successful,
        COUNT(*) FILTER (WHERE status = 'failed') AS failed
    FROM backup.backup_catalog
    WHERE start_time > NOW() - INTERVAL '7 days'
    GROUP BY backup_type
)
SELECT 
    backup_type,
    last_backup,
    AGE(NOW(), last_backup) AS time_since_backup,
    backups_24h,
    successful,
    failed,
    CASE 
        WHEN last_backup IS NULL THEN 'CRITICAL: No backups'
        WHEN last_backup < NOW() - INTERVAL '24 hours' THEN 'WARNING: No recent backup'
        WHEN failed > successful THEN 'WARNING: High failure rate'
        ELSE 'OK'
    END AS status
FROM backup_stats;

-- Step 8: Sample pgBackRest configuration generator
CREATE OR REPLACE FUNCTION backup.generate_pgbackrest_config()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_config TEXT;
BEGIN
    v_config := E'# pgBackRest Configuration for NeoBank\n\n';
    v_config := v_config || E'[global]\n';
    v_config := v_config || E'repo1-path=/backup/pgbackrest\n';
    v_config := v_config || E'repo1-retention-full=2\n';
    v_config := v_config || E'repo1-retention-diff=7\n';
    v_config := v_config || E'log-level-console=info\n';
    v_config := v_config || E'log-level-file=detail\n';
    v_config := v_config || E'compress-type=zst\n';
    v_config := v_config || E'compress-level=3\n\n';
    
    v_config := v_config || E'[neobank]\n';
    v_config := v_config || format(E'pg1-path=%s\n', current_setting('data_directory'));
    v_config := v_config || E'pg1-port=5432\n';
    
    RETURN v_config;
END;
$$;

SELECT backup.generate_pgbackrest_config();
```

---

## Exercise 8.3: Streaming Replication Setup 🔴

### Scenario
Configure streaming replication for NeoBank with one synchronous and one asynchronous replica for high availability and read scaling.

### Solution

```sql
-- Step 1: Replication monitoring schema
CREATE SCHEMA IF NOT EXISTS replication;

-- Step 2: Create replication slot management
CREATE OR REPLACE FUNCTION replication.create_replication_slot(
    p_slot_name TEXT,
    p_slot_type TEXT DEFAULT 'physical'
)
RETURNS TABLE (
    slot_name TEXT,
    slot_type TEXT,
    restart_lsn PG_LSN
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    IF p_slot_type = 'physical' THEN
        RETURN QUERY
        SELECT * FROM pg_create_physical_replication_slot(p_slot_name);
    ELSE
        RETURN QUERY
        SELECT * FROM pg_create_logical_replication_slot(p_slot_name, 'pgoutput');
    END IF;
END;
$$;

-- Step 3: Replication lag monitoring view
CREATE OR REPLACE VIEW replication.v_replica_status AS
SELECT 
    client_addr,
    usename,
    application_name,
    state,
    sync_state,
    sent_lsn,
    write_lsn,
    flush_lsn,
    replay_lsn,
    -- Calculate lag in bytes
    pg_wal_lsn_diff(sent_lsn, replay_lsn) AS replay_lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(sent_lsn, replay_lsn)) AS replay_lag_pretty,
    -- Calculate lag in time (approximate)
    CASE 
        WHEN replay_lag IS NOT NULL THEN replay_lag
        ELSE '0 seconds'::INTERVAL
    END AS replay_lag_time,
    -- Health status
    CASE 
        WHEN state != 'streaming' THEN 'CRITICAL: Not streaming'
        WHEN pg_wal_lsn_diff(sent_lsn, replay_lsn) > 100 * 1024 * 1024 THEN 'WARNING: Lag > 100MB'
        ELSE 'OK'
    END AS status
FROM pg_stat_replication;

-- Step 4: Replication slot monitoring
CREATE OR REPLACE VIEW replication.v_slot_status AS
SELECT 
    slot_name,
    slot_type,
    active,
    restart_lsn,
    -- Calculate retained WAL
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_pretty,
    -- Warning if too much WAL retained
    CASE 
        WHEN NOT active AND pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1073741824 
        THEN 'WARNING: Inactive slot retaining > 1GB'
        WHEN NOT active 
        THEN 'WARNING: Slot inactive'
        ELSE 'OK'
    END AS status
FROM pg_replication_slots;

-- Step 5: Function to check replication health
CREATE OR REPLACE FUNCTION replication.check_replication_health()
RETURNS TABLE (
    check_name TEXT,
    value TEXT,
    status TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check 1: Number of replicas
    RETURN QUERY
    SELECT 
        'Active Replicas'::TEXT,
        COUNT(*)::TEXT,
        CASE 
            WHEN COUNT(*) >= 2 THEN 'OK'
            WHEN COUNT(*) = 1 THEN 'WARNING'
            ELSE 'CRITICAL'
        END,
        'Should have at least 2 replicas for HA'
    FROM pg_stat_replication
    WHERE state = 'streaming';
    
    -- Check 2: Synchronous replication
    RETURN QUERY
    SELECT 
        'Synchronous Replicas',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) >= 1 THEN 'OK' ELSE 'WARNING' END,
        'At least one sync replica recommended for zero data loss'
    FROM pg_stat_replication
    WHERE sync_state = 'sync';
    
    -- Check 3: Max replication lag
    RETURN QUERY
    SELECT 
        'Max Replication Lag',
        COALESCE(pg_size_pretty(MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn))), '0 bytes'),
        CASE 
            WHEN MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn)) > 100 * 1024 * 1024 THEN 'WARNING'
            ELSE 'OK'
        END,
        'Lag should be < 100MB for read scaling'
    FROM pg_stat_replication;
    
    -- Check 4: Inactive replication slots
    RETURN QUERY
    SELECT 
        'Inactive Slots',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'WARNING' ELSE 'OK' END,
        'Inactive slots prevent WAL cleanup'
    FROM pg_replication_slots
    WHERE NOT active;
    
    -- Check 5: WAL sender processes
    RETURN QUERY
    SELECT 
        'WAL Sender Processes',
        COUNT(*)::TEXT || ' of ' || current_setting('max_wal_senders'),
        CASE 
            WHEN COUNT(*)::FLOAT / current_setting('max_wal_senders')::FLOAT > 0.8 
            THEN 'WARNING'
            ELSE 'OK'
        END,
        'May need to increase max_wal_senders'
    FROM pg_stat_replication;
END;
$$;

SELECT * FROM replication.check_replication_health();

-- Step 6: Configuration generator for primary
CREATE OR REPLACE FUNCTION replication.generate_primary_config()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_config TEXT;
BEGIN
    v_config := E'# Primary Server Configuration for Streaming Replication\n\n';
    v_config := v_config || E'# Replication Settings\n';
    v_config := v_config || E'wal_level = replica\n';
    v_config := v_config || E'max_wal_senders = 10\n';
    v_config := v_config || E'max_replication_slots = 10\n';
    v_config := v_config || E'wal_keep_size = 1GB\n\n';
    
    v_config := v_config || E'# Synchronous Replication\n';
    v_config := v_config || E'# For one sync replica:\n';
    v_config := v_config || E'synchronous_standby_names = ''FIRST 1 (replica1, replica2)''\n';
    v_config := v_config || E'synchronous_commit = on\n\n';
    
    v_config := v_config || E'# Archive Settings (for PITR)\n';
    v_config := v_config || E'archive_mode = on\n';
    v_config := v_config || E'archive_command = ''pgbackrest --stanza=neobank archive-push %p''\n';
    
    RETURN v_config;
END;
$$;

-- Step 7: Configuration generator for replica
CREATE OR REPLACE FUNCTION replication.generate_replica_config()
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_config TEXT;
BEGIN
    v_config := E'# Replica Server Configuration\n\n';
    v_config := v_config || E'# Connection to Primary\n';
    v_config := v_config || E'primary_conninfo = ''host=primary.neobank.local port=5432 ';
    v_config := v_config || E'user=replicator password=<password> application_name=replica1''\n';
    v_config := v_config || E'primary_slot_name = ''replica1_slot''\n\n';
    
    v_config := v_config || E'# Recovery Settings\n';
    v_config := v_config || E'hot_standby = on\n';
    v_config := v_config || E'hot_standby_feedback = on\n';
    v_config := v_config || E'max_standby_streaming_delay = 30s\n';
    v_config := v_config || E'max_standby_archive_delay = 60s\n\n';
    
    v_config := v_config || E'# Archive Recovery (if needed)\n';
    v_config := v_config || E'restore_command = ''pgbackrest --stanza=neobank archive-get %f %p''\n';
    
    RETURN v_config;
END;
$$;

-- Step 8: Replication lag alert function
CREATE OR REPLACE FUNCTION replication.check_and_alert_lag()
RETURNS TABLE (
    replica TEXT,
    lag_bytes BIGINT,
    lag_time INTERVAL,
    alert_level TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        r.application_name::TEXT,
        pg_wal_lsn_diff(r.sent_lsn, r.replay_lsn),
        r.replay_lag,
        CASE 
            WHEN pg_wal_lsn_diff(r.sent_lsn, r.replay_lsn) > 500 * 1024 * 1024 
            THEN 'CRITICAL'
            WHEN pg_wal_lsn_diff(r.sent_lsn, r.replay_lsn) > 100 * 1024 * 1024 
            THEN 'WARNING'
            ELSE 'OK'
        END
    FROM pg_stat_replication r;
END;
$$;
```

---

## Exercise 8.4: Monitoring and Alerting System 🟡

### Scenario
Build a comprehensive monitoring dashboard for NeoBank's database operations.

### Solution

```sql
-- Step 1: Create monitoring schema and tables
CREATE SCHEMA IF NOT EXISTS monitoring;

-- Metric collection table
CREATE TABLE IF NOT EXISTS monitoring.metrics (
    metric_id BIGSERIAL PRIMARY KEY,
    metric_name VARCHAR(100) NOT NULL,
    metric_value NUMERIC,
    metric_unit VARCHAR(20),
    tags JSONB DEFAULT '{}',
    collected_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_metrics_name_time ON monitoring.metrics (metric_name, collected_at DESC);

-- Step 2: System metrics collection function
CREATE OR REPLACE FUNCTION monitoring.collect_system_metrics()
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_db_stats RECORD;
    v_bg_stats RECORD;
BEGIN
    -- Database statistics
    SELECT * INTO v_db_stats FROM pg_stat_database WHERE datname = current_database();
    
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    VALUES 
        ('database.connections', v_db_stats.numbackends, 'count', '{"type":"gauge"}'),
        ('database.transactions_committed', v_db_stats.xact_commit, 'count', '{"type":"counter"}'),
        ('database.transactions_rolledback', v_db_stats.xact_rollback, 'count', '{"type":"counter"}'),
        ('database.blocks_read', v_db_stats.blks_read, 'count', '{"type":"counter"}'),
        ('database.blocks_hit', v_db_stats.blks_hit, 'count', '{"type":"counter"}'),
        ('database.tuples_returned', v_db_stats.tup_returned, 'count', '{"type":"counter"}'),
        ('database.tuples_fetched', v_db_stats.tup_fetched, 'count', '{"type":"counter"}'),
        ('database.tuples_inserted', v_db_stats.tup_inserted, 'count', '{"type":"counter"}'),
        ('database.tuples_updated', v_db_stats.tup_updated, 'count', '{"type":"counter"}'),
        ('database.tuples_deleted', v_db_stats.tup_deleted, 'count', '{"type":"counter"}'),
        ('database.temp_files', v_db_stats.temp_files, 'count', '{"type":"counter"}'),
        ('database.temp_bytes', v_db_stats.temp_bytes, 'bytes', '{"type":"counter"}'),
        ('database.deadlocks', v_db_stats.deadlocks, 'count', '{"type":"counter"}');
    
    -- Background writer statistics
    SELECT * INTO v_bg_stats FROM pg_stat_bgwriter;
    
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    VALUES 
        ('bgwriter.checkpoints_timed', v_bg_stats.checkpoints_timed, 'count', '{"type":"counter"}'),
        ('bgwriter.checkpoints_requested', v_bg_stats.checkpoints_req, 'count', '{"type":"counter"}'),
        ('bgwriter.buffers_written', v_bg_stats.buffers_checkpoint, 'count', '{"type":"counter"}'),
        ('bgwriter.buffers_clean', v_bg_stats.buffers_clean, 'count', '{"type":"counter"}');
    
    -- Connection counts by state
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    SELECT 
        'connections.by_state',
        COUNT(*),
        'count',
        jsonb_build_object('state', COALESCE(state, 'unknown'))
    FROM pg_stat_activity
    GROUP BY state;
    
    -- Table sizes
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    SELECT 
        'table.size',
        pg_total_relation_size(schemaname || '.' || relname),
        'bytes',
        jsonb_build_object('schema', schemaname, 'table', relname)
    FROM pg_stat_user_tables
    WHERE schemaname IN ('banking', 'lending', 'analytics');
END;
$$;

-- Step 3: Query performance metrics
CREATE OR REPLACE FUNCTION monitoring.collect_query_metrics()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Requires pg_stat_statements extension
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    SELECT 
        'query.total_time',
        total_exec_time,
        'ms',
        jsonb_build_object(
            'query_id', queryid::TEXT,
            'query', LEFT(query, 100)
        )
    FROM pg_stat_statements
    ORDER BY total_exec_time DESC
    LIMIT 20;
    
    INSERT INTO monitoring.metrics (metric_name, metric_value, metric_unit, tags)
    SELECT 
        'query.calls',
        calls,
        'count',
        jsonb_build_object(
            'query_id', queryid::TEXT,
            'query', LEFT(query, 100)
        )
    FROM pg_stat_statements
    ORDER BY calls DESC
    LIMIT 20;
END;
$$;

-- Step 4: Health check dashboard view
CREATE OR REPLACE VIEW monitoring.v_health_dashboard AS
WITH 
current_metrics AS (
    SELECT DISTINCT ON (metric_name, tags)
        metric_name,
        metric_value,
        metric_unit,
        tags,
        collected_at
    FROM monitoring.metrics
    ORDER BY metric_name, tags, collected_at DESC
),
health_checks AS (
    -- Buffer hit ratio
    SELECT 
        'Buffer Hit Ratio' AS check_name,
        ROUND(
            100.0 * (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') /
            NULLIF(
                (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') +
                (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_read'), 
                0
            ), 2
        ) AS value,
        '%' AS unit,
        CASE 
            WHEN ROUND(
                100.0 * (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') /
                NULLIF(
                    (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') +
                    (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_read'), 
                    0
                ), 2
            ) > 99 THEN '🟢'
            WHEN ROUND(
                100.0 * (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') /
                NULLIF(
                    (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_hit') +
                    (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.blocks_read'), 
                    0
                ), 2
            ) > 95 THEN '🟡'
            ELSE '🔴'
        END AS status
    
    UNION ALL
    
    -- Connection utilization
    SELECT 
        'Connection Utilization',
        ROUND(
            100.0 * (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.connections') /
            current_setting('max_connections')::NUMERIC, 
            2
        ),
        '%',
        CASE 
            WHEN (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.connections') /
                 current_setting('max_connections')::NUMERIC < 0.7 THEN '🟢'
            WHEN (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.connections') /
                 current_setting('max_connections')::NUMERIC < 0.9 THEN '🟡'
            ELSE '🔴'
        END
    
    UNION ALL
    
    -- Deadlocks
    SELECT 
        'Deadlocks (24h)',
        (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.deadlocks'),
        'count',
        CASE 
            WHEN (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.deadlocks') = 0 THEN '🟢'
            WHEN (SELECT metric_value FROM current_metrics WHERE metric_name = 'database.deadlocks') < 10 THEN '🟡'
            ELSE '🔴'
        END
)
SELECT * FROM health_checks;

-- Step 5: Alert rules table
CREATE TABLE IF NOT EXISTS monitoring.alert_rules (
    rule_id SERIAL PRIMARY KEY,
    rule_name VARCHAR(100) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    condition VARCHAR(20) NOT NULL,  -- 'gt', 'lt', 'eq', 'ne'
    threshold NUMERIC NOT NULL,
    severity VARCHAR(20) DEFAULT 'warning',
    notification_channel VARCHAR(50),
    enabled BOOLEAN DEFAULT TRUE,
    cooldown_minutes INTEGER DEFAULT 15,
    last_triggered TIMESTAMPTZ
);

-- Step 6: Alert evaluation function
CREATE OR REPLACE FUNCTION monitoring.evaluate_alerts()
RETURNS TABLE (
    rule_name TEXT,
    severity TEXT,
    current_value NUMERIC,
    threshold NUMERIC,
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_rule RECORD;
    v_value NUMERIC;
    v_triggered BOOLEAN;
BEGIN
    FOR v_rule IN 
        SELECT * FROM monitoring.alert_rules 
        WHERE enabled 
          AND (last_triggered IS NULL OR last_triggered < NOW() - (cooldown_minutes || ' minutes')::INTERVAL)
    LOOP
        -- Get current value
        SELECT metric_value INTO v_value
        FROM monitoring.metrics
        WHERE metric_name = v_rule.metric_name
        ORDER BY collected_at DESC
        LIMIT 1;
        
        -- Evaluate condition
        v_triggered := CASE v_rule.condition
            WHEN 'gt' THEN v_value > v_rule.threshold
            WHEN 'lt' THEN v_value < v_rule.threshold
            WHEN 'eq' THEN v_value = v_rule.threshold
            WHEN 'ne' THEN v_value != v_rule.threshold
            ELSE FALSE
        END;
        
        IF v_triggered THEN
            -- Update last triggered
            UPDATE monitoring.alert_rules 
            SET last_triggered = NOW() 
            WHERE rule_id = v_rule.rule_id;
            
            -- Return alert
            rule_name := v_rule.rule_name;
            severity := v_rule.severity;
            current_value := v_value;
            threshold := v_rule.threshold;
            message := format('Alert: %s - Current: %s, Threshold: %s %s',
                v_rule.rule_name, v_value, v_rule.condition, v_rule.threshold);
            RETURN NEXT;
        END IF;
    END LOOP;
END;
$$;

-- Step 7: Configure default alert rules
INSERT INTO monitoring.alert_rules (rule_name, metric_name, condition, threshold, severity, notification_channel)
VALUES 
    ('High Connection Usage', 'database.connections', 'gt', 180, 'warning', 'slack'),
    ('Deadlock Detected', 'database.deadlocks', 'gt', 0, 'critical', 'pagerduty'),
    ('High Temp File Usage', 'database.temp_bytes', 'gt', 1073741824, 'warning', 'slack'),
    ('Low Buffer Hit Ratio', 'database.blocks_hit', 'lt', 99, 'warning', 'email');

-- Step 8: Metric retention cleanup
CREATE OR REPLACE FUNCTION monitoring.cleanup_old_metrics(p_retention_days INTEGER DEFAULT 30)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    DELETE FROM monitoring.metrics
    WHERE collected_at < NOW() - (p_retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    RETURN v_deleted;
END;
$$;
```

---

## 🎯 Practice Challenges

### Challenge 8.1 🟡
Create a scheduled job system using pg_cron to run metric collection every minute and cleanup every day.

### Challenge 8.2 🔴
Implement a failover test procedure that safely verifies standby can be promoted and measures RTO.

### Challenge 8.3 ⚫
Build a capacity planning system that projects when storage, connections, or other resources will be exhausted based on trend analysis.

---

**Next: [Part 9 - Special Topics Exercises](09-special-topics-exercises.md)**
