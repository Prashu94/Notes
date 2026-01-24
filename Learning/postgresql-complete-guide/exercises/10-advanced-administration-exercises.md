# Part 10: Advanced Administration Exercises

## Topics Covered
- Tablespaces (Chapter 44)
- Schemas and Multi-Tenancy (Chapter 45)
- Logical Replication (Chapter 46)
- Point-in-Time Recovery (Chapter 47)
- PostgreSQL Internals (Chapter 48)

---

## Exercise 10.1: Tablespace Management 🔴

### Scenario
Design a tablespace strategy for NeoBank to optimize storage across different tiers (SSD, HDD, archive storage) based on data access patterns.

### Solution

```sql
-- Step 1: Create tablespace management schema
CREATE SCHEMA IF NOT EXISTS storage;

-- Step 2: Create tablespaces (requires OS-level directory setup)
-- These commands need to be run as superuser with proper directories created

/*
-- On the OS, first create directories:
mkdir -p /data/postgres/ssd_fast      # NVMe SSD for hot data
mkdir -p /data/postgres/ssd_standard  # Standard SSD for warm data
mkdir -p /data/postgres/hdd_archive   # HDD for cold/archive data
chown postgres:postgres /data/postgres/*
*/

-- Create tablespaces
CREATE TABLESPACE ts_hot_data 
    OWNER neobank_admin 
    LOCATION '/data/postgres/ssd_fast';

CREATE TABLESPACE ts_warm_data 
    OWNER neobank_admin 
    LOCATION '/data/postgres/ssd_standard';

CREATE TABLESPACE ts_archive 
    OWNER neobank_admin 
    LOCATION '/data/postgres/hdd_archive';

-- Step 3: Create tablespace allocation table
CREATE TABLE IF NOT EXISTS storage.tablespace_policy (
    policy_id SERIAL PRIMARY KEY,
    schema_name VARCHAR(100) NOT NULL,
    table_pattern VARCHAR(200) NOT NULL,  -- Supports wildcards
    data_tier VARCHAR(20) NOT NULL,       -- 'hot', 'warm', 'cold', 'archive'
    tablespace_name VARCHAR(100) NOT NULL,
    retention_days INTEGER,
    move_after_days INTEGER,              -- Days before moving to next tier
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Define tiering policies
INSERT INTO storage.tablespace_policy 
    (schema_name, table_pattern, data_tier, tablespace_name, move_after_days, notes)
VALUES 
    ('banking', 'transactions%', 'hot', 'ts_hot_data', 90, 
     'Active transactions - fast SSD'),
    ('banking', 'transactions_archive%', 'archive', 'ts_archive', NULL,
     'Historical transactions'),
    ('banking', 'accounts', 'hot', 'ts_hot_data', NULL,
     'Account data always hot'),
    ('banking', 'customers', 'hot', 'ts_hot_data', NULL,
     'Customer data always hot'),
    ('lending', 'loans', 'warm', 'ts_warm_data', NULL,
     'Loan data - moderate access'),
    ('analytics', '%_summary%', 'warm', 'ts_warm_data', NULL,
     'Summary tables - moderate access'),
    ('audit', '%', 'archive', 'ts_archive', NULL,
     'Audit logs - infrequent access');

-- Step 4: Function to move table to appropriate tablespace
CREATE OR REPLACE FUNCTION storage.apply_tablespace_policy(
    p_schema_name VARCHAR(100),
    p_table_name VARCHAR(200)
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_policy RECORD;
    v_current_ts TEXT;
    v_result TEXT;
BEGIN
    -- Find matching policy
    SELECT * INTO v_policy
    FROM storage.tablespace_policy
    WHERE schema_name = p_schema_name
      AND p_table_name LIKE REPLACE(REPLACE(table_pattern, '%', '%%'), '*', '%')
    ORDER BY LENGTH(table_pattern) DESC  -- Most specific match
    LIMIT 1;
    
    IF NOT FOUND THEN
        RETURN 'No policy found for ' || p_schema_name || '.' || p_table_name;
    END IF;
    
    -- Get current tablespace
    SELECT COALESCE(t.spcname, 'pg_default') INTO v_current_ts
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    LEFT JOIN pg_tablespace t ON c.reltablespace = t.oid
    WHERE n.nspname = p_schema_name AND c.relname = p_table_name;
    
    IF v_current_ts = v_policy.tablespace_name THEN
        RETURN 'Table already in correct tablespace: ' || v_policy.tablespace_name;
    END IF;
    
    -- Move table
    EXECUTE format(
        'ALTER TABLE %I.%I SET TABLESPACE %I',
        p_schema_name, p_table_name, v_policy.tablespace_name
    );
    
    v_result := format('Moved %I.%I from %s to %s',
        p_schema_name, p_table_name, v_current_ts, v_policy.tablespace_name);
    
    -- Log the move
    INSERT INTO audit.change_log (table_schema, table_name, operation, context)
    VALUES (p_schema_name, p_table_name, 'TABLESPACE_MOVE',
            jsonb_build_object('from', v_current_ts, 'to', v_policy.tablespace_name));
    
    RETURN v_result;
END;
$$;

-- Step 5: Tablespace usage monitoring view
CREATE OR REPLACE VIEW storage.v_tablespace_usage AS
SELECT 
    spcname AS tablespace_name,
    pg_size_pretty(pg_tablespace_size(spcname)) AS total_size,
    pg_tablespace_size(spcname) AS size_bytes,
    spclocation AS location,
    (SELECT COUNT(*) 
     FROM pg_class c 
     JOIN pg_tablespace t ON c.reltablespace = t.oid 
     WHERE t.spcname = ts.spcname) AS object_count
FROM pg_tablespace ts
WHERE spcname NOT LIKE 'pg_%'
ORDER BY pg_tablespace_size(spcname) DESC;

-- Step 6: Table distribution across tablespaces
CREATE OR REPLACE VIEW storage.v_table_tablespace_distribution AS
SELECT 
    n.nspname AS schema_name,
    c.relname AS table_name,
    COALESCE(t.spcname, 'pg_default') AS tablespace_name,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_total_relation_size(c.oid) AS size_bytes,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'i' THEN 'index'
        WHEN 't' THEN 'toast'
        WHEN 'm' THEN 'materialized view'
    END AS object_type
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN pg_tablespace t ON c.reltablespace = t.oid
WHERE n.nspname IN ('banking', 'lending', 'analytics', 'audit')
  AND c.relkind IN ('r', 'i', 'm')
ORDER BY pg_total_relation_size(c.oid) DESC;

-- Step 7: Index-specific tablespace management
CREATE OR REPLACE FUNCTION storage.move_indexes_to_tablespace(
    p_table_schema VARCHAR(100),
    p_table_name VARCHAR(200),
    p_tablespace VARCHAR(100)
)
RETURNS TABLE (index_name TEXT, result TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_index RECORD;
BEGIN
    FOR v_index IN 
        SELECT i.relname AS index_name
        FROM pg_index ix
        JOIN pg_class i ON ix.indexrelid = i.oid
        JOIN pg_class t ON ix.indrelid = t.oid
        JOIN pg_namespace n ON t.relnamespace = n.oid
        WHERE n.nspname = p_table_schema
          AND t.relname = p_table_name
    LOOP
        BEGIN
            EXECUTE format(
                'ALTER INDEX %I.%I SET TABLESPACE %I',
                p_table_schema, v_index.index_name, p_tablespace
            );
            index_name := v_index.index_name;
            result := 'Moved to ' || p_tablespace;
            RETURN NEXT;
        EXCEPTION WHEN OTHERS THEN
            index_name := v_index.index_name;
            result := 'Error: ' || SQLERRM;
            RETURN NEXT;
        END;
    END LOOP;
END;
$$;

-- Move all indexes for transactions table to fast storage
SELECT * FROM storage.move_indexes_to_tablespace('banking', 'transactions', 'ts_hot_data');
```

---

## Exercise 10.2: Multi-Tenant Schema Architecture 🔴

### Scenario
Design a multi-tenant architecture for NeoBank's white-label banking platform where different partner banks share the same PostgreSQL instance.

### Solution

```sql
-- Step 1: Create tenant management schema
CREATE SCHEMA IF NOT EXISTS tenant_mgmt;

-- Tenant registry
CREATE TABLE IF NOT EXISTS tenant_mgmt.tenants (
    tenant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_code VARCHAR(50) UNIQUE NOT NULL,
    tenant_name VARCHAR(200) NOT NULL,
    schema_name VARCHAR(63) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    config JSONB DEFAULT '{}',
    CONSTRAINT valid_schema_name CHECK (schema_name ~ '^[a-z][a-z0-9_]*$')
);

-- Step 2: Tenant provisioning function
CREATE OR REPLACE FUNCTION tenant_mgmt.provision_tenant(
    p_tenant_code VARCHAR(50),
    p_tenant_name VARCHAR(200),
    p_config JSONB DEFAULT '{}'
)
RETURNS UUID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_tenant_id UUID;
    v_schema_name VARCHAR(63);
BEGIN
    -- Generate schema name from tenant code
    v_schema_name := 'tenant_' || LOWER(REGEXP_REPLACE(p_tenant_code, '[^a-zA-Z0-9]', '_', 'g'));
    
    -- Create tenant record
    INSERT INTO tenant_mgmt.tenants (tenant_code, tenant_name, schema_name, config)
    VALUES (p_tenant_code, p_tenant_name, v_schema_name, p_config)
    RETURNING tenant_id INTO v_tenant_id;
    
    -- Create tenant schema
    EXECUTE format('CREATE SCHEMA IF NOT EXISTS %I', v_schema_name);
    
    -- Create tenant-specific tables (mirrors of main banking schema)
    EXECUTE format('
        CREATE TABLE %I.customers (
            customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL DEFAULT %L,
            customer_number VARCHAR(50) NOT NULL,
            first_name VARCHAR(100) NOT NULL,
            last_name VARCHAR(100) NOT NULL,
            email VARCHAR(255) NOT NULL,
            phone_primary VARCHAR(20),
            customer_type VARCHAR(20) DEFAULT ''individual'',
            customer_status VARCHAR(20) DEFAULT ''pending'',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (customer_number)
        )', v_schema_name, v_tenant_id);
    
    EXECUTE format('
        CREATE TABLE %I.accounts (
            account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL DEFAULT %L,
            customer_id UUID NOT NULL REFERENCES %I.customers(customer_id),
            account_number VARCHAR(50) NOT NULL,
            account_type VARCHAR(30) NOT NULL,
            currency_code CHAR(3) DEFAULT ''USD'',
            current_balance NUMERIC(18,2) DEFAULT 0,
            available_balance NUMERIC(18,2) DEFAULT 0,
            account_status VARCHAR(20) DEFAULT ''pending'',
            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),
            UNIQUE (account_number)
        )', v_schema_name, v_tenant_id, v_schema_name);
    
    EXECUTE format('
        CREATE TABLE %I.transactions (
            transaction_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            tenant_id UUID NOT NULL DEFAULT %L,
            account_id UUID NOT NULL REFERENCES %I.accounts(account_id),
            transaction_type VARCHAR(20) NOT NULL,
            amount NUMERIC(18,2) NOT NULL,
            currency_code CHAR(3) NOT NULL,
            running_balance NUMERIC(18,2),
            description TEXT,
            reference_number VARCHAR(50),
            transaction_date TIMESTAMPTZ DEFAULT NOW(),
            created_at TIMESTAMPTZ DEFAULT NOW()
        )', v_schema_name, v_tenant_id, v_schema_name);
    
    -- Create indexes
    EXECUTE format('CREATE INDEX ON %I.customers (email)', v_schema_name);
    EXECUTE format('CREATE INDEX ON %I.accounts (customer_id)', v_schema_name);
    EXECUTE format('CREATE INDEX ON %I.transactions (account_id, transaction_date DESC)', v_schema_name);
    
    -- Create tenant-specific role
    EXECUTE format('CREATE ROLE %I NOLOGIN', v_schema_name || '_role');
    EXECUTE format('GRANT USAGE ON SCHEMA %I TO %I', v_schema_name, v_schema_name || '_role');
    EXECUTE format('GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA %I TO %I', 
                   v_schema_name, v_schema_name || '_role');
    EXECUTE format('GRANT USAGE ON ALL SEQUENCES IN SCHEMA %I TO %I',
                   v_schema_name, v_schema_name || '_role');
    
    -- Log provisioning
    INSERT INTO audit.change_log (table_schema, table_name, operation, context)
    VALUES ('tenant_mgmt', 'tenants', 'TENANT_PROVISIONED',
            jsonb_build_object('tenant_id', v_tenant_id, 'schema', v_schema_name));
    
    RETURN v_tenant_id;
END;
$$;

-- Step 3: Tenant context management
CREATE OR REPLACE FUNCTION tenant_mgmt.set_tenant_context(p_tenant_code VARCHAR(50))
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_tenant RECORD;
BEGIN
    SELECT * INTO v_tenant
    FROM tenant_mgmt.tenants
    WHERE tenant_code = p_tenant_code AND status = 'active';
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tenant not found or inactive: %', p_tenant_code;
    END IF;
    
    -- Set session variables
    PERFORM set_config('app.tenant_id', v_tenant.tenant_id::TEXT, FALSE);
    PERFORM set_config('app.tenant_code', v_tenant.tenant_code, FALSE);
    PERFORM set_config('app.tenant_schema', v_tenant.schema_name, FALSE);
    
    -- Set search path to tenant schema
    EXECUTE format('SET search_path TO %I, public', v_tenant.schema_name);
END;
$$;

CREATE OR REPLACE FUNCTION tenant_mgmt.get_current_tenant_id()
RETURNS UUID
LANGUAGE SQL
STABLE
AS $$
    SELECT NULLIF(current_setting('app.tenant_id', TRUE), '')::UUID;
$$;

-- Step 4: Cross-tenant query (admin only)
CREATE OR REPLACE FUNCTION tenant_mgmt.cross_tenant_stats()
RETURNS TABLE (
    tenant_code VARCHAR(50),
    tenant_name VARCHAR(200),
    customer_count BIGINT,
    account_count BIGINT,
    total_balance NUMERIC(18,2)
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_tenant RECORD;
BEGIN
    FOR v_tenant IN SELECT * FROM tenant_mgmt.tenants WHERE status = 'active'
    LOOP
        RETURN QUERY EXECUTE format('
            SELECT 
                %L::VARCHAR(50) AS tenant_code,
                %L::VARCHAR(200) AS tenant_name,
                (SELECT COUNT(*) FROM %I.customers)::BIGINT,
                (SELECT COUNT(*) FROM %I.accounts)::BIGINT,
                (SELECT COALESCE(SUM(current_balance), 0) FROM %I.accounts)::NUMERIC(18,2)
        ', v_tenant.tenant_code, v_tenant.tenant_name, 
           v_tenant.schema_name, v_tenant.schema_name, v_tenant.schema_name);
    END LOOP;
END;
$$;

-- Step 5: Tenant RLS for shared tables (alternative approach)
-- For tables that are shared across tenants

CREATE TABLE IF NOT EXISTS tenant_mgmt.shared_config (
    config_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL REFERENCES tenant_mgmt.tenants(tenant_id),
    config_key VARCHAR(100) NOT NULL,
    config_value JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (tenant_id, config_key)
);

ALTER TABLE tenant_mgmt.shared_config ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON tenant_mgmt.shared_config
    FOR ALL
    USING (tenant_id = tenant_mgmt.get_current_tenant_id());

-- Step 6: Tenant deprovisioning (soft delete)
CREATE OR REPLACE FUNCTION tenant_mgmt.deprovision_tenant(
    p_tenant_code VARCHAR(50),
    p_hard_delete BOOLEAN DEFAULT FALSE
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_tenant RECORD;
BEGIN
    SELECT * INTO v_tenant
    FROM tenant_mgmt.tenants
    WHERE tenant_code = p_tenant_code;
    
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Tenant not found: %', p_tenant_code;
    END IF;
    
    IF p_hard_delete THEN
        -- Drop schema and all objects
        EXECUTE format('DROP SCHEMA IF EXISTS %I CASCADE', v_tenant.schema_name);
        -- Drop role
        EXECUTE format('DROP ROLE IF EXISTS %I', v_tenant.schema_name || '_role');
        -- Delete tenant record
        DELETE FROM tenant_mgmt.tenants WHERE tenant_id = v_tenant.tenant_id;
    ELSE
        -- Soft delete
        UPDATE tenant_mgmt.tenants
        SET status = 'deactivated',
            config = config || jsonb_build_object('deactivated_at', NOW())
        WHERE tenant_id = v_tenant.tenant_id;
    END IF;
    
    INSERT INTO audit.change_log (table_schema, table_name, operation, context)
    VALUES ('tenant_mgmt', 'tenants', 
            CASE WHEN p_hard_delete THEN 'TENANT_DELETED' ELSE 'TENANT_DEACTIVATED' END,
            jsonb_build_object('tenant_id', v_tenant.tenant_id));
    
    RETURN TRUE;
END;
$$;

-- Example: Provision a new tenant
SELECT tenant_mgmt.provision_tenant('PARTNER_BANK_A', 'Partner Bank Alpha');
SELECT tenant_mgmt.provision_tenant('PARTNER_BANK_B', 'Partner Bank Beta');

-- Set context and operate within tenant
SELECT tenant_mgmt.set_tenant_context('PARTNER_BANK_A');
-- Now all queries automatically use tenant_partner_bank_a schema
```

---

## Exercise 10.3: Logical Replication for Real-Time Analytics 🔴

### Scenario
Set up logical replication to stream NeoBank transaction data to an analytics database in real-time.

### Solution

```sql
-- =============================================================================
-- SOURCE DATABASE (Production)
-- =============================================================================

-- Step 1: Configure publication
-- Ensure wal_level = logical in postgresql.conf

-- Create publication for analytics-relevant tables
CREATE PUBLICATION analytics_feed FOR TABLE
    banking.customers,
    banking.accounts,
    banking.transactions
WITH (publish = 'insert, update, delete');

-- Add partitioned tables if needed
-- ALTER PUBLICATION analytics_feed ADD TABLE banking.transactions_2024_01;

-- Step 2: Create replication slot (optional - subscriber creates automatically)
-- SELECT pg_create_logical_replication_slot('analytics_slot', 'pgoutput');

-- Step 3: Monitor publication
CREATE OR REPLACE VIEW replication.v_publication_status AS
SELECT 
    p.pubname AS publication_name,
    p.puballtables AS all_tables,
    p.pubinsert AS publish_insert,
    p.pubupdate AS publish_update,
    p.pubdelete AS publish_delete,
    STRING_AGG(c.relname, ', ') AS tables
FROM pg_publication p
LEFT JOIN pg_publication_rel pr ON p.oid = pr.prpubid
LEFT JOIN pg_class c ON pr.prrelid = c.oid
GROUP BY p.pubname, p.puballtables, p.pubinsert, p.pubupdate, p.pubdelete;

-- =============================================================================
-- TARGET DATABASE (Analytics)
-- =============================================================================

-- Step 4: Create subscription on analytics database
/*
-- Run on analytics database:
CREATE SUBSCRIPTION analytics_sub
    CONNECTION 'host=prod-db.neobank.local port=5432 dbname=neobank user=replicator password=xxx'
    PUBLICATION analytics_feed
    WITH (
        copy_data = true,           -- Initial data sync
        create_slot = true,         -- Create replication slot
        enabled = true,             -- Start immediately
        synchronous_commit = 'off'  -- Async for performance
    );
*/

-- Step 5: Monitor subscription status
CREATE OR REPLACE VIEW replication.v_subscription_status AS
SELECT 
    s.subname AS subscription_name,
    s.subenabled AS enabled,
    st.received_lsn,
    st.latest_end_lsn,
    pg_wal_lsn_diff(st.latest_end_lsn, st.received_lsn) AS lag_bytes,
    pg_size_pretty(pg_wal_lsn_diff(st.latest_end_lsn, st.received_lsn)) AS lag_pretty,
    st.last_msg_send_time,
    st.last_msg_receipt_time,
    AGE(NOW(), st.last_msg_receipt_time) AS time_since_last_msg
FROM pg_subscription s
JOIN pg_stat_subscription st ON s.oid = st.subid;

-- Step 6: Logical replication monitoring on source
CREATE OR REPLACE VIEW replication.v_logical_replication_slots AS
SELECT 
    slot_name,
    plugin,
    slot_type,
    active,
    active_pid,
    restart_lsn,
    confirmed_flush_lsn,
    pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) AS retained_bytes,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS retained_pretty,
    CASE 
        WHEN NOT active AND pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn) > 1073741824
        THEN '🔴 CRITICAL - Inactive slot retaining > 1GB WAL'
        WHEN NOT active
        THEN '🟡 WARNING - Inactive slot'
        ELSE '🟢 OK'
    END AS status
FROM pg_replication_slots
WHERE slot_type = 'logical';

-- Step 7: Handle conflicts and apply errors
-- Create conflict resolution table
CREATE TABLE IF NOT EXISTS replication.apply_errors (
    error_id BIGSERIAL PRIMARY KEY,
    subscription_name TEXT,
    table_name TEXT,
    operation TEXT,
    error_message TEXT,
    row_data JSONB,
    occurred_at TIMESTAMPTZ DEFAULT NOW(),
    resolved BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT
);

-- Step 8: Selective replication with row filters (PostgreSQL 15+)
/*
-- Only replicate high-value transactions
CREATE PUBLICATION high_value_txn_feed
FOR TABLE banking.transactions
WHERE (amount > 10000)
WITH (publish = 'insert');
*/

-- Step 9: Table-level publication management
CREATE OR REPLACE FUNCTION replication.add_table_to_publication(
    p_publication TEXT,
    p_schema TEXT,
    p_table TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    EXECUTE format(
        'ALTER PUBLICATION %I ADD TABLE %I.%I',
        p_publication, p_schema, p_table
    );
    
    INSERT INTO audit.change_log (table_schema, table_name, operation, context)
    VALUES (p_schema, p_table, 'ADDED_TO_PUBLICATION',
            jsonb_build_object('publication', p_publication));
    
    RETURN TRUE;
EXCEPTION WHEN OTHERS THEN
    RAISE WARNING 'Failed to add table: %', SQLERRM;
    RETURN FALSE;
END;
$$;
```

---

## Exercise 10.4: Point-in-Time Recovery (PITR) 🔴

### Scenario
Implement PITR capability for NeoBank to recover from data corruption or accidental deletions.

### Solution

```sql
-- Step 1: PITR configuration and management schema
CREATE SCHEMA IF NOT EXISTS pitr;

-- Recovery point catalog
CREATE TABLE IF NOT EXISTS pitr.recovery_points (
    recovery_point_id SERIAL PRIMARY KEY,
    recovery_name VARCHAR(200) NOT NULL,
    recovery_type VARCHAR(20) NOT NULL,  -- 'named', 'scheduled', 'pre_deploy'
    wal_position PG_LSN NOT NULL,
    wal_filename TEXT,
    recovery_time TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    description TEXT,
    created_by TEXT DEFAULT CURRENT_USER,
    metadata JSONB DEFAULT '{}'
);

-- Step 2: Create named recovery point
CREATE OR REPLACE FUNCTION pitr.create_recovery_point(
    p_name VARCHAR(200),
    p_type VARCHAR(20) DEFAULT 'named',
    p_description TEXT DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_recovery_point_id INTEGER;
    v_lsn PG_LSN;
BEGIN
    -- Force a WAL switch to ensure recovery point is durable
    SELECT pg_switch_wal() INTO v_lsn;
    
    INSERT INTO pitr.recovery_points (
        recovery_name, recovery_type, wal_position, wal_filename, description
    ) VALUES (
        p_name,
        p_type,
        v_lsn,
        pg_walfile_name(v_lsn),
        p_description
    )
    RETURNING recovery_point_id INTO v_recovery_point_id;
    
    -- Log to audit
    INSERT INTO audit.change_log (table_schema, table_name, operation, context)
    VALUES ('pitr', 'recovery_points', 'RECOVERY_POINT_CREATED',
            jsonb_build_object(
                'recovery_point_id', v_recovery_point_id,
                'name', p_name,
                'lsn', v_lsn::TEXT
            ));
    
    RETURN v_recovery_point_id;
END;
$$;

-- Step 3: Recovery command generator
CREATE OR REPLACE FUNCTION pitr.generate_recovery_commands(
    p_recovery_point_id INTEGER DEFAULT NULL,
    p_target_time TIMESTAMPTZ DEFAULT NULL,
    p_target_lsn PG_LSN DEFAULT NULL
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_commands TEXT;
    v_rp RECORD;
    v_target TEXT;
BEGIN
    -- Validate inputs
    IF p_recovery_point_id IS NULL AND p_target_time IS NULL AND p_target_lsn IS NULL THEN
        RAISE EXCEPTION 'Must specify recovery_point_id, target_time, or target_lsn';
    END IF;
    
    -- Get recovery point info if specified
    IF p_recovery_point_id IS NOT NULL THEN
        SELECT * INTO v_rp FROM pitr.recovery_points WHERE recovery_point_id = p_recovery_point_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION 'Recovery point not found: %', p_recovery_point_id;
        END IF;
        v_target := 'recovery_target_lsn = ''' || v_rp.wal_position::TEXT || '''';
    ELSIF p_target_time IS NOT NULL THEN
        v_target := 'recovery_target_time = ''' || p_target_time::TEXT || '''';
    ELSE
        v_target := 'recovery_target_lsn = ''' || p_target_lsn::TEXT || '''';
    END IF;
    
    v_commands := E'-- PITR Recovery Commands for NeoBank\n';
    v_commands := v_commands || E'-- Generated: ' || NOW()::TEXT || E'\n\n';
    
    v_commands := v_commands || E'-- STEP 1: Stop PostgreSQL\n';
    v_commands := v_commands || E'sudo systemctl stop postgresql\n\n';
    
    v_commands := v_commands || E'-- STEP 2: Backup current data directory (safety)\n';
    v_commands := v_commands || E'sudo mv /var/lib/postgresql/16/main /var/lib/postgresql/16/main_backup_$(date +%Y%m%d_%H%M%S)\n\n';
    
    v_commands := v_commands || E'-- STEP 3: Restore base backup\n';
    v_commands := v_commands || E'pgbackrest --stanza=neobank restore\n\n';
    
    v_commands := v_commands || E'-- STEP 4: Configure recovery target\n';
    v_commands := v_commands || E'cat >> /var/lib/postgresql/16/main/postgresql.auto.conf << EOF\n';
    v_commands := v_commands || v_target || E'\n';
    v_commands := v_commands || E'recovery_target_action = ''pause''\n';
    v_commands := v_commands || E'EOF\n\n';
    
    v_commands := v_commands || E'-- STEP 5: Create recovery signal\n';
    v_commands := v_commands || E'touch /var/lib/postgresql/16/main/recovery.signal\n\n';
    
    v_commands := v_commands || E'-- STEP 6: Start PostgreSQL (will recover to target)\n';
    v_commands := v_commands || E'sudo systemctl start postgresql\n\n';
    
    v_commands := v_commands || E'-- STEP 7: Verify recovery and promote if satisfied\n';
    v_commands := v_commands || E'-- Check data, then run:\n';
    v_commands := v_commands || E'SELECT pg_wal_replay_resume();\n';
    
    RETURN v_commands;
END;
$$;

-- Step 4: Pre-deployment recovery point automation
CREATE OR REPLACE FUNCTION pitr.pre_deployment_checkpoint(p_deployment_name TEXT)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_rp_id INTEGER;
BEGIN
    -- Create CHECKPOINT for clean state
    CHECKPOINT;
    
    -- Create named recovery point
    v_rp_id := pitr.create_recovery_point(
        'pre_deploy_' || p_deployment_name || '_' || TO_CHAR(NOW(), 'YYYYMMDD_HH24MISS'),
        'pre_deploy',
        'Recovery point before deployment: ' || p_deployment_name
    );
    
    RETURN v_rp_id;
END;
$$;

-- Step 5: WAL archive monitoring
CREATE OR REPLACE VIEW pitr.v_wal_archive_health AS
SELECT 
    archived_count,
    failed_count,
    last_archived_wal,
    last_archived_time,
    last_failed_wal,
    last_failed_time,
    CASE 
        WHEN failed_count > 0 AND last_failed_time > COALESCE(last_archived_time, '1970-01-01'::TIMESTAMPTZ)
        THEN '🔴 CRITICAL - Recent archive failure'
        WHEN last_archived_time < NOW() - INTERVAL '5 minutes'
        THEN '🟡 WARNING - No recent archives'
        ELSE '🟢 OK'
    END AS status,
    AGE(NOW(), last_archived_time) AS time_since_archive
FROM pg_stat_archiver;

-- Step 6: Recovery testing schedule
CREATE TABLE IF NOT EXISTS pitr.recovery_tests (
    test_id SERIAL PRIMARY KEY,
    test_date TIMESTAMPTZ NOT NULL,
    recovery_point_used INTEGER REFERENCES pitr.recovery_points(recovery_point_id),
    target_time TIMESTAMPTZ,
    recovery_duration INTERVAL,
    data_verified BOOLEAN,
    test_result VARCHAR(20),  -- 'success', 'failed', 'partial'
    notes TEXT,
    performed_by TEXT
);

-- Function to record recovery test results
CREATE OR REPLACE FUNCTION pitr.record_recovery_test(
    p_recovery_point_id INTEGER,
    p_duration INTERVAL,
    p_verified BOOLEAN,
    p_result VARCHAR(20),
    p_notes TEXT DEFAULT NULL
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_test_id INTEGER;
BEGIN
    INSERT INTO pitr.recovery_tests (
        test_date, recovery_point_used, recovery_duration,
        data_verified, test_result, notes, performed_by
    ) VALUES (
        NOW(), p_recovery_point_id, p_duration,
        p_verified, p_result, p_notes, CURRENT_USER
    )
    RETURNING test_id INTO v_test_id;
    
    RETURN v_test_id;
END;
$$;

-- Step 7: Recovery point retention policy
CREATE OR REPLACE FUNCTION pitr.cleanup_old_recovery_points(p_retention_days INTEGER DEFAULT 30)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_deleted INTEGER;
BEGIN
    -- Keep named and pre_deploy points longer
    DELETE FROM pitr.recovery_points
    WHERE recovery_type = 'scheduled'
      AND recovery_time < NOW() - (p_retention_days || ' days')::INTERVAL;
    
    GET DIAGNOSTICS v_deleted = ROW_COUNT;
    
    RETURN v_deleted;
END;
$$;
```

---

## Exercise 10.5: PostgreSQL Internals Exploration ⚫

### Scenario
Deep dive into PostgreSQL internals to understand system behavior and optimize NeoBank's database.

### Solution

```sql
-- Step 1: Create internals exploration schema
CREATE SCHEMA IF NOT EXISTS pg_internals;

-- Step 2: Page header inspection
CREATE OR REPLACE FUNCTION pg_internals.inspect_page_header(
    p_relation TEXT,
    p_page_number INTEGER DEFAULT 0
)
RETURNS TABLE (
    attribute TEXT,
    value TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_page BYTEA;
BEGIN
    -- Get raw page data
    v_page := get_raw_page(p_relation, p_page_number);
    
    RETURN QUERY
    SELECT 'Page Size'::TEXT, octet_length(v_page)::TEXT
    UNION ALL
    SELECT 'LSN', page_header(v_page).lsn::TEXT
    UNION ALL
    SELECT 'Checksum', page_header(v_page).checksum::TEXT
    UNION ALL
    SELECT 'Flags', page_header(v_page).flags::TEXT
    UNION ALL
    SELECT 'Lower Offset', page_header(v_page).lower::TEXT
    UNION ALL
    SELECT 'Upper Offset', page_header(v_page).upper::TEXT
    UNION ALL
    SELECT 'Special', page_header(v_page).special::TEXT
    UNION ALL
    SELECT 'Free Space', (page_header(v_page).upper - page_header(v_page).lower)::TEXT;
END;
$$;

-- Step 3: Tuple header inspection
CREATE OR REPLACE FUNCTION pg_internals.inspect_tuple(
    p_relation TEXT,
    p_ctid TID
)
RETURNS TABLE (
    attribute TEXT,
    value TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_page_number INTEGER;
    v_tuple_number INTEGER;
    v_page BYTEA;
BEGIN
    v_page_number := (p_ctid::TEXT::point)[0]::INTEGER;
    v_tuple_number := (p_ctid::TEXT::point)[1]::INTEGER;
    
    v_page := get_raw_page(p_relation, v_page_number);
    
    RETURN QUERY
    SELECT 'CTID'::TEXT, p_ctid::TEXT
    UNION ALL
    SELECT 'Page Number', v_page_number::TEXT
    UNION ALL
    SELECT 'Tuple Number', v_tuple_number::TEXT
    UNION ALL
    SELECT 't_xmin', heap_tuple_infomask_flags(
        heap_page_items(v_page)
    )[v_tuple_number + 1].t_xmin::TEXT
    UNION ALL
    SELECT 't_xmax', heap_tuple_infomask_flags(
        heap_page_items(v_page)
    )[v_tuple_number + 1].t_xmax::TEXT;
END;
$$;

-- Step 4: Buffer cache analysis
CREATE EXTENSION IF NOT EXISTS pg_buffercache;

CREATE OR REPLACE VIEW pg_internals.v_buffer_cache_analysis AS
WITH buffer_stats AS (
    SELECT 
        c.relname,
        c.relnamespace::REGNAMESPACE::TEXT AS schema_name,
        COUNT(*) AS buffers,
        SUM(CASE WHEN b.isdirty THEN 1 ELSE 0 END) AS dirty_buffers,
        ROUND(100.0 * COUNT(*) / (
            SELECT setting::INTEGER FROM pg_settings WHERE name = 'shared_buffers'
        ), 2) AS pct_of_cache
    FROM pg_buffercache b
    JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
    WHERE b.reldatabase = (SELECT oid FROM pg_database WHERE datname = current_database())
    GROUP BY c.relname, c.relnamespace
)
SELECT 
    schema_name,
    relname AS table_name,
    buffers,
    pg_size_pretty(buffers * 8192) AS buffer_size,
    dirty_buffers,
    pct_of_cache
FROM buffer_stats
WHERE buffers > 10
ORDER BY buffers DESC;

-- Step 5: Transaction ID analysis
CREATE OR REPLACE VIEW pg_internals.v_transaction_id_status AS
SELECT 
    txid_current() AS current_txid,
    txid_current_snapshot() AS current_snapshot,
    age(datfrozenxid) AS database_age,
    datfrozenxid AS frozen_xid,
    CASE 
        WHEN age(datfrozenxid) > 1000000000 THEN '🔴 CRITICAL - XID wraparound imminent'
        WHEN age(datfrozenxid) > 500000000 THEN '🟡 WARNING - Consider aggressive vacuum'
        ELSE '🟢 OK'
    END AS status
FROM pg_database
WHERE datname = current_database();

-- Step 6: Checkpoint analysis
CREATE OR REPLACE VIEW pg_internals.v_checkpoint_analysis AS
SELECT 
    checkpoints_timed,
    checkpoints_req,
    ROUND(100.0 * checkpoints_req / NULLIF(checkpoints_timed + checkpoints_req, 0), 2) 
        AS pct_requested,
    checkpoint_write_time / 1000 AS write_time_seconds,
    checkpoint_sync_time / 1000 AS sync_time_seconds,
    buffers_checkpoint,
    buffers_clean,
    buffers_backend,
    ROUND(100.0 * buffers_backend / NULLIF(buffers_checkpoint + buffers_clean + buffers_backend, 0), 2)
        AS pct_backend_writes,
    maxwritten_clean,
    CASE 
        WHEN checkpoints_req > checkpoints_timed * 0.5 
        THEN '🟡 Too many requested checkpoints - increase max_wal_size'
        WHEN buffers_backend > buffers_checkpoint * 0.1
        THEN '🟡 Too many backend writes - tune bgwriter'
        ELSE '🟢 OK'
    END AS status
FROM pg_stat_bgwriter;

-- Step 7: WAL generation analysis
CREATE OR REPLACE FUNCTION pg_internals.analyze_wal_generation(
    p_interval_seconds INTEGER DEFAULT 60
)
RETURNS TABLE (
    start_lsn PG_LSN,
    end_lsn PG_LSN,
    wal_generated_bytes BIGINT,
    wal_generated_pretty TEXT,
    wal_rate_mb_per_sec NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_lsn PG_LSN;
    v_end_lsn PG_LSN;
    v_bytes BIGINT;
BEGIN
    v_start_lsn := pg_current_wal_lsn();
    PERFORM pg_sleep(p_interval_seconds);
    v_end_lsn := pg_current_wal_lsn();
    v_bytes := pg_wal_lsn_diff(v_end_lsn, v_start_lsn);
    
    RETURN QUERY SELECT 
        v_start_lsn,
        v_end_lsn,
        v_bytes,
        pg_size_pretty(v_bytes),
        ROUND((v_bytes::NUMERIC / 1024 / 1024) / p_interval_seconds, 2);
END;
$$;

-- Step 8: System catalog statistics
CREATE OR REPLACE VIEW pg_internals.v_catalog_stats AS
SELECT 
    'pg_class' AS catalog,
    COUNT(*) AS row_count,
    pg_size_pretty(pg_relation_size('pg_class')) AS size
FROM pg_class
UNION ALL
SELECT 'pg_attribute', COUNT(*), pg_size_pretty(pg_relation_size('pg_attribute'))
FROM pg_attribute
UNION ALL
SELECT 'pg_index', COUNT(*), pg_size_pretty(pg_relation_size('pg_index'))
FROM pg_index
UNION ALL
SELECT 'pg_statistic', COUNT(*), pg_size_pretty(pg_relation_size('pg_statistic'))
FROM pg_statistic
UNION ALL
SELECT 'pg_depend', COUNT(*), pg_size_pretty(pg_relation_size('pg_depend'))
FROM pg_depend
ORDER BY row_count DESC;

-- Step 9: Query execution internals
CREATE OR REPLACE FUNCTION pg_internals.explain_analyze_detailed(p_query TEXT)
RETURNS TABLE (
    plan_node TEXT,
    actual_time_ms NUMERIC,
    rows_estimate BIGINT,
    rows_actual BIGINT,
    accuracy_ratio NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_plan JSONB;
BEGIN
    EXECUTE 'EXPLAIN (ANALYZE, FORMAT JSON) ' || p_query INTO v_plan;
    
    RETURN QUERY
    WITH RECURSIVE plan_tree AS (
        SELECT 
            v_plan->0->'Plan' AS node,
            0 AS depth
        UNION ALL
        SELECT 
            child,
            depth + 1
        FROM plan_tree,
             LATERAL jsonb_array_elements(node->'Plans') AS child
        WHERE node->'Plans' IS NOT NULL
    )
    SELECT 
        REPEAT('  ', depth) || (node->>'Node Type')::TEXT,
        ((node->>'Actual Total Time')::NUMERIC),
        (node->>'Plan Rows')::BIGINT,
        (node->>'Actual Rows')::BIGINT,
        CASE 
            WHEN (node->>'Actual Rows')::BIGINT > 0 
            THEN ROUND((node->>'Plan Rows')::NUMERIC / (node->>'Actual Rows')::NUMERIC, 2)
            ELSE NULL
        END
    FROM plan_tree;
END;
$$;

-- Example usage
SELECT * FROM pg_internals.v_buffer_cache_analysis LIMIT 10;
SELECT * FROM pg_internals.v_transaction_id_status;
SELECT * FROM pg_internals.v_checkpoint_analysis;
```

---

## 🎯 Practice Challenges

### Challenge 10.1 🔴
Implement automated tablespace migration based on data age - move data older than X days to archive tablespace automatically.

### Challenge 10.2 ⚫
Create a tenant backup and restore system that can backup/restore individual tenants without affecting others.

### Challenge 10.3 ⚫
Build a custom MVCC visualization tool that shows tuple visibility across different transaction snapshots.

---

**Next: [Part 11 - Practical Applications Exercises](11-practical-applications-exercises.md)**
