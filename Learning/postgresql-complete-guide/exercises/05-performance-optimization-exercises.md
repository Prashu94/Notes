# Part 5: Performance & Optimization Exercises

## Topics Covered
- Query Optimization (Chapter 20)
- EXPLAIN and Query Plans (Chapter 21)
- Index Optimization (Chapter 22)
- Partitioning (Chapter 23)
- Vacuuming and Maintenance (Chapter 24)

---

## Exercise 5.1: Query Plan Analysis 🟡

### Scenario
The transaction search feature is slow. Analyze the query plans and optimize the queries.

### Tasks
1. Analyze slow queries using EXPLAIN
2. Identify missing indexes
3. Rewrite queries for better performance
4. Measure improvements

### Solution

```sql
-- Enable timing and analyze
\timing on

-- Problem Query 1: Slow transaction search
-- Original query (likely doing sequential scan)
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    t.reference_number,
    t.transaction_date,
    t.amount,
    t.description,
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE t.merchant_name ILIKE '%amazon%'
  AND t.transaction_date BETWEEN '2025-01-01' AND '2025-12-31'
ORDER BY t.transaction_date DESC
LIMIT 100;

-- Analysis: Check what indexes exist
SELECT 
    indexname,
    indexdef
FROM pg_indexes
WHERE tablename = 'transactions'
  AND schemaname = 'banking';

-- Check if merchant_name has index
-- If not, create optimized index for ILIKE searches
CREATE INDEX CONCURRENTLY idx_transactions_merchant_lower
ON banking.transactions (LOWER(merchant_name) varchar_pattern_ops)
WHERE merchant_name IS NOT NULL;

-- For ILIKE, we need trigram index
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX CONCURRENTLY idx_transactions_merchant_trgm
ON banking.transactions USING GIN (merchant_name gin_trgm_ops)
WHERE merchant_name IS NOT NULL;

-- Rewritten optimized query
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT 
    t.reference_number,
    t.transaction_date,
    t.amount,
    t.description,
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE t.merchant_name ILIKE '%amazon%'
  AND t.transaction_date >= '2025-01-01'::date  -- Partition pruning friendly
  AND t.transaction_date < '2026-01-01'::date
ORDER BY t.transaction_date DESC
LIMIT 100;

-- Problem Query 2: Customer account summary
-- Original slow query
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS name,
    (SELECT COUNT(*) FROM banking.accounts WHERE customer_id = c.customer_id) AS account_count,
    (SELECT SUM(current_balance) FROM banking.accounts WHERE customer_id = c.customer_id) AS total_balance,
    (SELECT COUNT(*) FROM banking.transactions t 
     JOIN banking.accounts a ON t.account_id = a.account_id 
     WHERE a.customer_id = c.customer_id 
       AND t.transaction_date >= CURRENT_DATE - 30) AS recent_txn_count
FROM banking.customers c
WHERE c.customer_status = 'active';

-- Optimized: Replace correlated subqueries with JOINs
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS name,
    COALESCE(acc.account_count, 0) AS account_count,
    COALESCE(acc.total_balance, 0) AS total_balance,
    COALESCE(txn.recent_txn_count, 0) AS recent_txn_count
FROM banking.customers c
LEFT JOIN LATERAL (
    SELECT 
        COUNT(*) AS account_count,
        SUM(current_balance) AS total_balance
    FROM banking.accounts
    WHERE customer_id = c.customer_id
) acc ON TRUE
LEFT JOIN LATERAL (
    SELECT COUNT(*) AS recent_txn_count
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = c.customer_id
      AND t.transaction_date >= CURRENT_DATE - 30
) txn ON TRUE
WHERE c.customer_status = 'active';

-- Even better with single aggregation
EXPLAIN (ANALYZE, BUFFERS)
WITH customer_stats AS (
    SELECT 
        a.customer_id,
        COUNT(DISTINCT a.account_id) AS account_count,
        SUM(a.current_balance) AS total_balance,
        COUNT(t.transaction_id) FILTER (
            WHERE t.transaction_date >= CURRENT_DATE - 30
        ) AS recent_txn_count
    FROM banking.accounts a
    LEFT JOIN banking.transactions t ON a.account_id = t.account_id
    GROUP BY a.customer_id
)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS name,
    COALESCE(cs.account_count, 0) AS account_count,
    COALESCE(cs.total_balance, 0) AS total_balance,
    COALESCE(cs.recent_txn_count, 0) AS recent_txn_count
FROM banking.customers c
LEFT JOIN customer_stats cs ON c.customer_id = cs.customer_id
WHERE c.customer_status = 'active';

-- Query Plan Analysis Helper Function
CREATE OR REPLACE FUNCTION analytics.analyze_query_plan(p_query TEXT)
RETURNS TABLE (
    node_type TEXT,
    relation_name TEXT,
    startup_cost NUMERIC,
    total_cost NUMERIC,
    plan_rows BIGINT,
    actual_rows BIGINT,
    actual_time_ms NUMERIC,
    loops BIGINT,
    index_name TEXT,
    filter TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_plan JSONB;
    v_node JSONB;
BEGIN
    -- Get the execution plan
    EXECUTE 'EXPLAIN (ANALYZE, FORMAT JSON) ' || p_query INTO v_plan;
    
    -- Parse plan nodes (simplified - real implementation would be recursive)
    FOR v_node IN SELECT jsonb_array_elements(v_plan->0->'Plan'->'Plans')
    LOOP
        node_type := v_node->>'Node Type';
        relation_name := v_node->>'Relation Name';
        startup_cost := (v_node->>'Startup Cost')::NUMERIC;
        total_cost := (v_node->>'Total Cost')::NUMERIC;
        plan_rows := (v_node->>'Plan Rows')::BIGINT;
        actual_rows := (v_node->>'Actual Rows')::BIGINT;
        actual_time_ms := (v_node->>'Actual Total Time')::NUMERIC;
        loops := (v_node->>'Actual Loops')::BIGINT;
        index_name := v_node->>'Index Name';
        filter := v_node->>'Filter';
        
        -- Generate recommendations
        recommendation := CASE
            WHEN node_type = 'Seq Scan' AND plan_rows > 10000 
                THEN 'Consider adding index for filter: ' || COALESCE(filter, 'N/A')
            WHEN actual_rows > plan_rows * 10 
                THEN 'Statistics may be outdated - run ANALYZE'
            WHEN node_type = 'Nested Loop' AND actual_rows > 10000 
                THEN 'Consider rewriting with hash join'
            ELSE 'OK'
        END;
        
        RETURN NEXT;
    END LOOP;
END;
$$;
```

---

## Exercise 5.2: Index Strategy for High-Volume Tables 🔴

### Scenario
Design an optimal indexing strategy for the transactions table that handles millions of rows with various query patterns.

### Requirements
1. Support account-based queries
2. Support date range queries
3. Support merchant/category searches
4. Support fraud detection queries
5. Minimize index bloat and maintenance overhead

### Solution

```sql
-- Audit existing indexes
SELECT 
    indexrelid::regclass AS index_name,
    relid::regclass AS table_name,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'banking'
  AND relid = 'banking.transactions'::regclass
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
    indexrelid::regclass AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE schemaname = 'banking'
  AND relid = 'banking.transactions'::regclass
  AND idx_scan = 0;

-- Index Strategy Implementation

-- 1. Primary access pattern: Account + Date (covering index)
-- This is the most common query - get transactions for an account in date range
DROP INDEX IF EXISTS banking.idx_transactions_account_date_desc;
CREATE INDEX CONCURRENTLY idx_txn_account_date_covering
ON banking.transactions (account_id, transaction_date DESC)
INCLUDE (amount, transaction_type, description, balance_after)
WHERE transaction_status = 'completed';

-- 2. Date-based queries for reporting (partition-aligned)
CREATE INDEX CONCURRENTLY idx_txn_date_type
ON banking.transactions (transaction_date, transaction_type)
INCLUDE (amount)
WHERE transaction_status = 'completed';

-- 3. Pending/Processing transactions (small, hot data)
CREATE INDEX CONCURRENTLY idx_txn_pending
ON banking.transactions (transaction_status, initiated_at)
WHERE transaction_status IN ('pending', 'processing');

-- 4. Fraud detection - flagged transactions
CREATE INDEX CONCURRENTLY idx_txn_flagged
ON banking.transactions (is_flagged, risk_score DESC, transaction_date DESC)
WHERE is_flagged = TRUE;

-- 5. Merchant search with trigrams (already created)
-- CREATE INDEX CONCURRENTLY idx_txn_merchant_trgm ...

-- 6. Category-based analytics
CREATE INDEX CONCURRENTLY idx_txn_category_date
ON banking.transactions (category, transaction_date)
INCLUDE (amount)
WHERE category IS NOT NULL;

-- 7. Expression index for amount ranges (useful for alerts)
CREATE INDEX CONCURRENTLY idx_txn_large_amounts
ON banking.transactions (account_id, transaction_date)
WHERE ABS(amount) > 10000;

-- Index maintenance function
CREATE OR REPLACE FUNCTION banking.maintain_transaction_indexes()
RETURNS TABLE (
    index_name TEXT,
    action TEXT,
    details TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_idx RECORD;
BEGIN
    -- Check for bloated indexes
    FOR v_idx IN 
        SELECT 
            indexrelid::regclass::text AS idx_name,
            pg_relation_size(indexrelid) AS size,
            idx_scan
        FROM pg_stat_user_indexes
        WHERE schemaname = 'banking'
          AND relid = 'banking.transactions'::regclass
    LOOP
        -- Check if index needs rebuild
        IF v_idx.size > 1024*1024*100 THEN  -- > 100MB
            index_name := v_idx.idx_name;
            action := 'REINDEX RECOMMENDED';
            details := FORMAT('Size: %s, Scans: %s', 
                pg_size_pretty(v_idx.size), v_idx.idx_scan);
            RETURN NEXT;
        END IF;
        
        -- Check for unused indexes
        IF v_idx.idx_scan = 0 THEN
            index_name := v_idx.idx_name;
            action := 'DROP CANDIDATE';
            details := 'Zero scans since stats reset';
            RETURN NEXT;
        END IF;
    END LOOP;
    
    -- Suggest missing indexes based on common queries
    -- (This would analyze pg_stat_statements in real implementation)
    
    RETURN;
END;
$$;

-- Run maintenance check
SELECT * FROM banking.maintain_transaction_indexes();

-- Index effectiveness query
WITH index_stats AS (
    SELECT 
        indexrelid::regclass AS index_name,
        idx_scan,
        idx_tup_read,
        idx_tup_fetch,
        pg_relation_size(indexrelid) AS size_bytes
    FROM pg_stat_user_indexes
    WHERE schemaname = 'banking'
      AND relid = 'banking.transactions'::regclass
),
table_stats AS (
    SELECT 
        seq_scan,
        seq_tup_read,
        idx_scan AS total_idx_scan,
        n_tup_ins,
        n_tup_upd,
        n_tup_del
    FROM pg_stat_user_tables
    WHERE schemaname = 'banking'
      AND relname = 'transactions'
)
SELECT 
    i.index_name,
    i.idx_scan AS scans,
    i.idx_tup_read AS rows_read,
    i.idx_tup_fetch AS rows_fetched,
    pg_size_pretty(i.size_bytes) AS size,
    ROUND(i.idx_scan::numeric / NULLIF(t.total_idx_scan + t.seq_scan, 0) * 100, 2) AS pct_of_queries,
    ROUND(i.size_bytes::numeric / 1024 / 1024 / NULLIF(i.idx_scan, 0), 4) AS mb_per_scan
FROM index_stats i
CROSS JOIN table_stats t
ORDER BY i.idx_scan DESC;
```

---

## Exercise 5.3: Table Partitioning Implementation 🔴

### Scenario
The transactions table has grown to 500 million rows. Implement partitioning to improve query performance and simplify data retention.

### Requirements
1. Partition by month
2. Automate partition creation
3. Implement data retention (drop partitions older than 7 years)
4. Handle partition pruning optimization

### Solution

```sql
-- Note: If table already has data, we need a migration approach
-- Here's the complete implementation

-- Step 1: Create new partitioned table (if starting fresh)
CREATE TABLE banking.transactions_partitioned (
    transaction_id UUID DEFAULT gen_random_uuid(),
    idempotency_key VARCHAR(64) NOT NULL,
    reference_number VARCHAR(30) NOT NULL,
    account_id UUID NOT NULL,
    transaction_type banking.transaction_type NOT NULL,
    transaction_status banking.transaction_status DEFAULT 'pending',
    amount NUMERIC(15, 2) NOT NULL,
    currency banking.currency_code DEFAULT 'USD',
    balance_after NUMERIC(15, 2),
    related_transaction_id UUID,
    external_reference VARCHAR(100),
    channel banking.transaction_channel NOT NULL,
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    description VARCHAR(255),
    merchant_name VARCHAR(200),
    merchant_category_code VARCHAR(4),
    category VARCHAR(50),
    location_city VARCHAR(100),
    location_state VARCHAR(50),
    location_country CHAR(2),
    metadata JSONB DEFAULT '{}',
    risk_score SMALLINT,
    is_flagged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (transaction_id, transaction_date)
) PARTITION BY RANGE (transaction_date);

-- Step 2: Create function to generate partitions
CREATE OR REPLACE FUNCTION banking.create_transaction_partition(
    p_year INTEGER,
    p_month INTEGER
)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    v_partition_name TEXT;
    v_start_date DATE;
    v_end_date DATE;
BEGIN
    v_partition_name := FORMAT('transactions_%s_%s', 
        p_year, LPAD(p_month::TEXT, 2, '0'));
    v_start_date := make_date(p_year, p_month, 1);
    v_end_date := v_start_date + INTERVAL '1 month';
    
    -- Check if partition exists
    IF EXISTS (
        SELECT 1 FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname = 'banking'
          AND c.relname = v_partition_name
    ) THEN
        RETURN 'EXISTS: ' || v_partition_name;
    END IF;
    
    -- Create partition
    EXECUTE FORMAT(
        'CREATE TABLE banking.%I PARTITION OF banking.transactions_partitioned
         FOR VALUES FROM (%L) TO (%L)',
        v_partition_name,
        v_start_date,
        v_end_date
    );
    
    -- Create indexes on new partition
    EXECUTE FORMAT(
        'CREATE INDEX %I ON banking.%I (account_id, transaction_date DESC)',
        'idx_' || v_partition_name || '_account',
        v_partition_name
    );
    
    EXECUTE FORMAT(
        'CREATE INDEX %I ON banking.%I (transaction_status) WHERE transaction_status IN (''pending'', ''processing'')',
        'idx_' || v_partition_name || '_pending',
        v_partition_name
    );
    
    RETURN 'CREATED: ' || v_partition_name;
END;
$$;

-- Step 3: Create partitions for historical data and future
DO $$
DECLARE
    v_year INTEGER;
    v_month INTEGER;
    v_result TEXT;
BEGIN
    -- Create partitions from 2020 to 2027
    FOR v_year IN 2020..2027 LOOP
        FOR v_month IN 1..12 LOOP
            SELECT banking.create_transaction_partition(v_year, v_month) INTO v_result;
            RAISE NOTICE '%', v_result;
        END LOOP;
    END LOOP;
END;
$$;

-- Step 4: Create default partition for safety
CREATE TABLE banking.transactions_default 
    PARTITION OF banking.transactions_partitioned DEFAULT;

-- Step 5: Automated partition management procedure
CREATE OR REPLACE PROCEDURE banking.manage_partitions()
LANGUAGE plpgsql
AS $$
DECLARE
    v_future_date DATE;
    v_retention_date DATE;
    v_partition RECORD;
    v_year INTEGER;
    v_month INTEGER;
BEGIN
    -- Create partitions for next 3 months
    v_future_date := CURRENT_DATE + INTERVAL '3 months';
    v_year := EXTRACT(YEAR FROM v_future_date);
    v_month := EXTRACT(MONTH FROM v_future_date);
    
    PERFORM banking.create_transaction_partition(v_year, v_month);
    
    -- Drop partitions older than 7 years (regulatory retention)
    v_retention_date := CURRENT_DATE - INTERVAL '7 years';
    
    FOR v_partition IN 
        SELECT 
            c.relname AS partition_name,
            pg_get_expr(c.relpartbound, c.oid) AS bounds
        FROM pg_class c
        JOIN pg_inherits i ON c.oid = i.inhrelid
        JOIN pg_class p ON i.inhparent = p.oid
        WHERE p.relname = 'transactions_partitioned'
          AND c.relname != 'transactions_default'
    LOOP
        -- Parse bounds and check date
        IF v_partition.bounds ~ 'TO \(''(\d{4}-\d{2}-\d{2})' THEN
            IF (regexp_match(v_partition.bounds, 'TO \(''(\d{4}-\d{2}-\d{2})'))[1]::DATE < v_retention_date THEN
                -- Archive before drop (in real scenario)
                RAISE NOTICE 'Dropping old partition: %', v_partition.partition_name;
                EXECUTE FORMAT('DROP TABLE banking.%I', v_partition.partition_name);
            END IF;
        END IF;
    END LOOP;
    
    COMMIT;
END;
$$;

-- Step 6: Schedule partition management (run monthly via pg_cron or external scheduler)
-- SELECT cron.schedule('manage-partitions', '0 1 1 * *', 'CALL banking.manage_partitions()');

-- Step 7: Migrate existing data (if applicable)
-- This should be done in batches during low-traffic periods
CREATE OR REPLACE PROCEDURE banking.migrate_transactions_to_partitioned(
    p_batch_size INTEGER DEFAULT 100000,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_migrated INTEGER := 0;
    v_batch INTEGER;
    v_date DATE;
BEGIN
    v_start_date := COALESCE(p_start_date, (SELECT MIN(transaction_date) FROM banking.transactions));
    v_end_date := COALESCE(p_end_date, CURRENT_DATE);
    
    FOR v_date IN SELECT generate_series(v_start_date, v_end_date, '1 day'::interval)::date
    LOOP
        -- Ensure partition exists
        PERFORM banking.create_transaction_partition(
            EXTRACT(YEAR FROM v_date)::INTEGER,
            EXTRACT(MONTH FROM v_date)::INTEGER
        );
        
        -- Migrate day's data
        INSERT INTO banking.transactions_partitioned
        SELECT * FROM banking.transactions
        WHERE transaction_date = v_date
        ON CONFLICT DO NOTHING;
        
        GET DIAGNOSTICS v_batch = ROW_COUNT;
        v_migrated := v_migrated + v_batch;
        
        IF v_migrated % 1000000 = 0 THEN
            RAISE NOTICE 'Migrated % rows through %', v_migrated, v_date;
            COMMIT;
        END IF;
    END LOOP;
    
    RAISE NOTICE 'Migration complete. Total rows: %', v_migrated;
    COMMIT;
END;
$$;

-- Step 8: Query showing partition pruning
EXPLAIN (ANALYZE, COSTS OFF)
SELECT COUNT(*), SUM(amount)
FROM banking.transactions_partitioned
WHERE transaction_date BETWEEN '2026-01-01' AND '2026-01-31'
  AND account_id = 'some-uuid-here';

-- Verify partition pruning
SELECT 
    parent.relname AS parent,
    child.relname AS partition,
    pg_get_expr(child.relpartbound, child.oid) AS bounds,
    pg_size_pretty(pg_relation_size(child.oid)) AS size,
    (SELECT COUNT(*) FROM pg_stat_user_tables WHERE relname = child.relname)
FROM pg_inherits
JOIN pg_class parent ON pg_inherits.inhparent = parent.oid
JOIN pg_class child ON pg_inherits.inhrelid = child.oid
WHERE parent.relname = 'transactions_partitioned'
ORDER BY child.relname;
```

---

## Exercise 5.4: Vacuum and Maintenance Strategy 🟡

### Scenario
Design a comprehensive maintenance strategy for the NeoBank database to prevent bloat and maintain performance.

### Solution

```sql
-- Check current bloat and dead tuples
SELECT 
    schemaname,
    relname AS table_name,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(n_dead_tup::numeric / NULLIF(n_live_tup + n_dead_tup, 0) * 100, 2) AS dead_pct,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE schemaname IN ('banking', 'lending', 'audit')
ORDER BY n_dead_tup DESC;

-- Check table bloat estimate
WITH constants AS (
    SELECT current_setting('block_size')::numeric AS bs
),
table_stats AS (
    SELECT 
        schemaname,
        tablename,
        (SELECT bs FROM constants) * relpages AS table_bytes,
        CASE WHEN reltuples > 0
            THEN (SELECT bs FROM constants) * relpages / reltuples
            ELSE 0
        END AS avg_row_size,
        reltuples AS row_count
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    JOIN pg_stat_user_tables t ON c.relname = t.relname AND n.nspname = t.schemaname
    WHERE c.relkind = 'r'
)
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(table_bytes) AS table_size,
    row_count::bigint,
    ROUND(avg_row_size::numeric, 2) AS avg_row_bytes
FROM table_stats
WHERE schemaname IN ('banking', 'lending')
ORDER BY table_bytes DESC;

-- Autovacuum tuning for high-transaction tables
-- These settings can be applied per-table

-- For transactions table (high write volume)
ALTER TABLE banking.transactions SET (
    autovacuum_vacuum_scale_factor = 0.01,      -- Vacuum when 1% dead (default 20%)
    autovacuum_vacuum_threshold = 10000,         -- Minimum 10k dead tuples
    autovacuum_analyze_scale_factor = 0.005,     -- Analyze when 0.5% changed
    autovacuum_analyze_threshold = 5000,         -- Minimum 5k changed
    autovacuum_vacuum_cost_delay = 2,            -- Faster vacuum (default 2ms)
    autovacuum_vacuum_cost_limit = 1000,         -- More aggressive (default 200)
    fillfactor = 90                              -- Leave 10% for HOT updates
);

-- For accounts table (moderate writes, frequent reads)
ALTER TABLE banking.accounts SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02,
    fillfactor = 95
);

-- For audit log (append-only, rarely updated)
ALTER TABLE audit.change_log SET (
    autovacuum_enabled = true,
    autovacuum_vacuum_scale_factor = 0.1,       -- Less aggressive
    autovacuum_freeze_max_age = 500000000       -- Prevent wraparound
);

-- Create maintenance monitoring view
CREATE OR REPLACE VIEW analytics.v_maintenance_status AS
SELECT 
    schemaname || '.' || relname AS table_name,
    pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
    pg_size_pretty(pg_relation_size(relid)) AS table_size,
    pg_size_pretty(pg_indexes_size(relid)) AS index_size,
    n_live_tup AS live_rows,
    n_dead_tup AS dead_rows,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct,
    
    -- Last maintenance
    last_vacuum,
    last_autovacuum,
    last_analyze,
    
    -- Activity since last vacuum
    COALESCE(n_tup_ins, 0) AS inserts_since_vacuum,
    COALESCE(n_tup_upd, 0) AS updates_since_vacuum,
    COALESCE(n_tup_del, 0) AS deletes_since_vacuum,
    
    -- Health indicators
    CASE 
        WHEN n_dead_tup > 100000 AND ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 2) > 10 
            THEN 'VACUUM NEEDED'
        WHEN last_analyze < NOW() - INTERVAL '7 days' 
            THEN 'ANALYZE NEEDED'
        WHEN last_vacuum < NOW() - INTERVAL '1 day' AND n_dead_tup > 10000
            THEN 'VACUUM RECOMMENDED'
        ELSE 'OK'
    END AS health_status

FROM pg_stat_user_tables
WHERE schemaname IN ('banking', 'lending', 'analytics', 'audit')
ORDER BY n_dead_tup DESC;

-- Maintenance procedure
CREATE OR REPLACE PROCEDURE banking.perform_maintenance(
    p_aggressive BOOLEAN DEFAULT FALSE
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_table RECORD;
BEGIN
    -- Update statistics first
    FOR v_table IN 
        SELECT schemaname, relname
        FROM pg_stat_user_tables
        WHERE schemaname IN ('banking', 'lending')
          AND (last_analyze IS NULL OR last_analyze < NOW() - INTERVAL '1 day')
    LOOP
        EXECUTE FORMAT('ANALYZE %I.%I', v_table.schemaname, v_table.relname);
        RAISE NOTICE 'Analyzed %.%', v_table.schemaname, v_table.relname;
    END LOOP;
    
    -- Vacuum tables with significant dead tuples
    FOR v_table IN 
        SELECT schemaname, relname, n_dead_tup
        FROM pg_stat_user_tables
        WHERE schemaname IN ('banking', 'lending')
          AND n_dead_tup > 10000
        ORDER BY n_dead_tup DESC
    LOOP
        IF p_aggressive THEN
            EXECUTE FORMAT('VACUUM (ANALYZE, VERBOSE) %I.%I', 
                v_table.schemaname, v_table.relname);
        ELSE
            EXECUTE FORMAT('VACUUM ANALYZE %I.%I', 
                v_table.schemaname, v_table.relname);
        END IF;
        RAISE NOTICE 'Vacuumed %.% (% dead tuples)', 
            v_table.schemaname, v_table.relname, v_table.n_dead_tup;
        
        COMMIT;  -- Commit after each table
    END LOOP;
    
    -- Reindex bloated indexes
    IF p_aggressive THEN
        FOR v_table IN 
            SELECT 
                schemaname,
                indexname,
                pg_relation_size(indexrelid) AS size
            FROM pg_stat_user_indexes
            WHERE schemaname IN ('banking', 'lending')
              AND pg_relation_size(indexrelid) > 100 * 1024 * 1024  -- > 100MB
        LOOP
            EXECUTE FORMAT('REINDEX INDEX CONCURRENTLY %I.%I', 
                v_table.schemaname, v_table.indexname);
            RAISE NOTICE 'Reindexed %.%', v_table.schemaname, v_table.indexname;
        END LOOP;
    END IF;
END;
$$;

-- Check maintenance status
SELECT * FROM analytics.v_maintenance_status;

-- Run maintenance
CALL banking.perform_maintenance(FALSE);  -- Regular maintenance
-- CALL banking.perform_maintenance(TRUE);   -- Aggressive maintenance (weekend)
```

---

## Exercise 5.5: Query Performance Tuning Workshop 🔴

### Scenario
Optimize a set of slow queries identified in production monitoring.

### Solution

```sql
-- Slow Query 1: Monthly spending report by category
-- Original (slow - sequential scan, bad join order)
EXPLAIN (ANALYZE, BUFFERS, TIMING)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    t.category,
    DATE_TRUNC('month', t.transaction_date) AS month,
    COUNT(*) AS transaction_count,
    SUM(ABS(t.amount)) AS total_spent
FROM banking.customers c
JOIN banking.accounts a ON c.customer_id = a.customer_id
JOIN banking.transactions t ON a.account_id = t.account_id
WHERE t.amount < 0
  AND t.transaction_date >= '2025-01-01'
  AND t.transaction_date < '2026-01-01'
GROUP BY c.customer_id, c.customer_number, c.first_name, c.last_name, t.category, DATE_TRUNC('month', t.transaction_date)
ORDER BY customer_name, month, total_spent DESC;

-- Optimized version
EXPLAIN (ANALYZE, BUFFERS, TIMING)
WITH monthly_spending AS (
    SELECT 
        a.customer_id,
        t.category,
        DATE_TRUNC('month', t.transaction_date) AS month,
        COUNT(*) AS transaction_count,
        SUM(ABS(t.amount)) AS total_spent
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE t.amount < 0
      AND t.transaction_date >= '2025-01-01'
      AND t.transaction_date < '2026-01-01'
    GROUP BY a.customer_id, t.category, DATE_TRUNC('month', t.transaction_date)
)
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    ms.category,
    ms.month,
    ms.transaction_count,
    ms.total_spent
FROM monthly_spending ms
JOIN banking.customers c ON ms.customer_id = c.customer_id
ORDER BY customer_name, month, total_spent DESC;

-- Slow Query 2: Find duplicate transactions (fraud detection)
-- Original (expensive self-join)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    t1.reference_number,
    t1.account_id,
    t1.amount,
    t1.transaction_date,
    t2.reference_number AS duplicate_ref
FROM banking.transactions t1
JOIN banking.transactions t2 
    ON t1.account_id = t2.account_id
    AND t1.amount = t2.amount
    AND t1.transaction_date = t2.transaction_date
    AND t1.transaction_id != t2.transaction_id
WHERE t1.transaction_date >= CURRENT_DATE - 7;

-- Optimized using window function
EXPLAIN (ANALYZE, BUFFERS)
WITH potential_duplicates AS (
    SELECT 
        transaction_id,
        reference_number,
        account_id,
        amount,
        transaction_date,
        initiated_at,
        COUNT(*) OVER (
            PARTITION BY account_id, amount, transaction_date
        ) AS duplicate_count,
        ROW_NUMBER() OVER (
            PARTITION BY account_id, amount, transaction_date 
            ORDER BY initiated_at
        ) AS rn
    FROM banking.transactions
    WHERE transaction_date >= CURRENT_DATE - 7
)
SELECT 
    reference_number,
    account_id,
    amount,
    transaction_date,
    duplicate_count
FROM potential_duplicates
WHERE duplicate_count > 1
ORDER BY transaction_date DESC, account_id, rn;

-- Slow Query 3: Customer lifetime value
-- Original (multiple correlated subqueries)
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.customer_id,
    c.customer_number,
    (SELECT SUM(ABS(amount)) FROM banking.transactions t 
     JOIN banking.accounts a ON t.account_id = a.account_id 
     WHERE a.customer_id = c.customer_id AND amount < 0) AS total_spent,
    (SELECT COUNT(*) FROM banking.transactions t 
     JOIN banking.accounts a ON t.account_id = a.account_id 
     WHERE a.customer_id = c.customer_id) AS total_transactions,
    (SELECT AVG(current_balance) FROM banking.accounts 
     WHERE customer_id = c.customer_id) AS avg_balance
FROM banking.customers c
WHERE c.customer_status = 'active';

-- Optimized with single aggregation pass
EXPLAIN (ANALYZE, BUFFERS)
WITH customer_metrics AS (
    SELECT 
        a.customer_id,
        SUM(ABS(t.amount)) FILTER (WHERE t.amount < 0) AS total_spent,
        COUNT(t.transaction_id) AS total_transactions,
        AVG(a.current_balance) AS avg_balance
    FROM banking.accounts a
    LEFT JOIN banking.transactions t ON a.account_id = t.account_id
    GROUP BY a.customer_id
)
SELECT 
    c.customer_id,
    c.customer_number,
    COALESCE(cm.total_spent, 0) AS total_spent,
    COALESCE(cm.total_transactions, 0) AS total_transactions,
    COALESCE(cm.avg_balance, 0) AS avg_balance
FROM banking.customers c
LEFT JOIN customer_metrics cm ON c.customer_id = cm.customer_id
WHERE c.customer_status = 'active';

-- Performance comparison helper
CREATE OR REPLACE FUNCTION analytics.compare_query_performance(
    p_query1 TEXT,
    p_query2 TEXT,
    p_iterations INTEGER DEFAULT 5
)
RETURNS TABLE (
    query_number INTEGER,
    iteration INTEGER,
    execution_time_ms NUMERIC,
    rows_returned BIGINT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_start TIMESTAMPTZ;
    v_end TIMESTAMPTZ;
    v_rows BIGINT;
    v_i INTEGER;
BEGIN
    -- Warm up cache
    EXECUTE 'SELECT COUNT(*) FROM (' || p_query1 || ') q';
    EXECUTE 'SELECT COUNT(*) FROM (' || p_query2 || ') q';
    
    -- Test query 1
    FOR v_i IN 1..p_iterations LOOP
        v_start := clock_timestamp();
        EXECUTE 'SELECT COUNT(*) FROM (' || p_query1 || ') q' INTO v_rows;
        v_end := clock_timestamp();
        
        query_number := 1;
        iteration := v_i;
        execution_time_ms := EXTRACT(MILLISECONDS FROM (v_end - v_start));
        rows_returned := v_rows;
        RETURN NEXT;
    END LOOP;
    
    -- Test query 2
    FOR v_i IN 1..p_iterations LOOP
        v_start := clock_timestamp();
        EXECUTE 'SELECT COUNT(*) FROM (' || p_query2 || ') q' INTO v_rows;
        v_end := clock_timestamp();
        
        query_number := 2;
        iteration := v_i;
        execution_time_ms := EXTRACT(MILLISECONDS FROM (v_end - v_start));
        rows_returned := v_rows;
        RETURN NEXT;
    END LOOP;
END;
$$;
```

---

## 🎯 Practice Challenges

### Challenge 5.1 🔴
Create a query that identifies the top 10 slowest queries from `pg_stat_statements` and suggests optimizations.

### Challenge 5.2 ⚫
Implement a connection pooling strategy using PgBouncer configuration recommendations based on workload analysis.

### Challenge 5.3 ⚫
Design a read replica query routing strategy that directs analytics queries to replicas while keeping transactions on primary.

---

**Next: [Part 6 - Advanced Features Exercises](06-advanced-features-exercises.md)**
