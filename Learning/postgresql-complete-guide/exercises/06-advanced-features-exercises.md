# Part 6: Advanced Features Exercises

## Topics Covered
- Full-Text Search (Chapter 25)
- JSON and JSONB (Chapter 26)
- Arrays and Composite Types (Chapter 27)
- Extensions (Chapter 28)
- Foreign Data Wrappers (Chapter 29)

---

## Exercise 6.1: Full-Text Search for Transaction Search 🟡

### Scenario
Build a powerful search feature that allows customers to search their transactions using natural language queries like "coffee shop last week" or "amazon purchase electronics".

### Requirements
1. Create searchable text from transaction descriptions
2. Support weighted search (merchant name more important than description)
3. Handle typos and variations
4. Rank results by relevance

### Solution

```sql
-- Step 1: Add tsvector column for search
ALTER TABLE banking.transactions 
ADD COLUMN IF NOT EXISTS search_vector tsvector;

-- Step 2: Create function to generate search vector
CREATE OR REPLACE FUNCTION banking.generate_transaction_search_vector()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.merchant_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.description, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.category, '')), 'C');
    RETURN NEW;
END;
$$;

-- Step 3: Create trigger
CREATE TRIGGER trg_transaction_search_vector
    BEFORE INSERT OR UPDATE OF merchant_name, description, category
    ON banking.transactions
    FOR EACH ROW
    EXECUTE FUNCTION banking.generate_transaction_search_vector();

-- Step 4: Update existing rows
UPDATE banking.transactions
SET search_vector = 
    setweight(to_tsvector('english', COALESCE(merchant_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(description, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(category, '')), 'C');

-- Step 5: Create GIN index for fast searches
CREATE INDEX CONCURRENTLY idx_transactions_search 
ON banking.transactions USING GIN (search_vector);

-- Step 6: Search function with relevance ranking
CREATE OR REPLACE FUNCTION banking.search_transactions(
    p_customer_id UUID,
    p_query TEXT,
    p_start_date DATE DEFAULT NULL,
    p_end_date DATE DEFAULT NULL,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    transaction_id UUID,
    transaction_date DATE,
    account_number VARCHAR(20),
    amount NUMERIC(15, 2),
    merchant_name VARCHAR(200),
    description VARCHAR(255),
    category VARCHAR(50),
    relevance_score REAL,
    headline TEXT
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_tsquery tsquery;
BEGIN
    -- Parse the query with prefix matching for partial words
    v_tsquery := websearch_to_tsquery('english', p_query);
    
    -- If that fails, try plainto_tsquery
    IF v_tsquery IS NULL THEN
        v_tsquery := plainto_tsquery('english', p_query);
    END IF;
    
    RETURN QUERY
    SELECT 
        t.transaction_id,
        t.transaction_date,
        a.account_number,
        t.amount,
        t.merchant_name,
        t.description,
        t.category,
        ts_rank_cd(t.search_vector, v_tsquery) AS relevance_score,
        ts_headline('english', 
            COALESCE(t.merchant_name, '') || ' - ' || COALESCE(t.description, ''),
            v_tsquery,
            'StartSel=<mark>, StopSel=</mark>, MaxWords=50, MinWords=20'
        ) AS headline
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = p_customer_id
      AND t.search_vector @@ v_tsquery
      AND (p_start_date IS NULL OR t.transaction_date >= p_start_date)
      AND (p_end_date IS NULL OR t.transaction_date <= p_end_date)
    ORDER BY ts_rank_cd(t.search_vector, v_tsquery) DESC, t.transaction_date DESC
    LIMIT p_limit;
END;
$$;

-- Step 7: Fuzzy search with trigrams for typo tolerance
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Combined search: Full-text + fuzzy matching
CREATE OR REPLACE FUNCTION banking.smart_search_transactions(
    p_customer_id UUID,
    p_query TEXT,
    p_limit INTEGER DEFAULT 50
)
RETURNS TABLE (
    transaction_id UUID,
    transaction_date DATE,
    amount NUMERIC(15, 2),
    merchant_name VARCHAR(200),
    description VARCHAR(255),
    match_type TEXT,
    score REAL
)
LANGUAGE plpgsql
STABLE
AS $$
BEGIN
    RETURN QUERY
    -- Full-text search results
    SELECT 
        t.transaction_id,
        t.transaction_date,
        t.amount,
        t.merchant_name,
        t.description,
        'full_text'::TEXT AS match_type,
        ts_rank_cd(t.search_vector, websearch_to_tsquery('english', p_query)) AS score
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = p_customer_id
      AND t.search_vector @@ websearch_to_tsquery('english', p_query)
    
    UNION ALL
    
    -- Fuzzy trigram matches (for typos)
    SELECT 
        t.transaction_id,
        t.transaction_date,
        t.amount,
        t.merchant_name,
        t.description,
        'fuzzy'::TEXT AS match_type,
        similarity(LOWER(COALESCE(t.merchant_name, '') || ' ' || COALESCE(t.description, '')), LOWER(p_query)) AS score
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE a.customer_id = p_customer_id
      AND (
        t.merchant_name % p_query OR
        t.description % p_query
      )
      AND NOT t.search_vector @@ websearch_to_tsquery('english', p_query)  -- Exclude FTS matches
    
    ORDER BY score DESC
    LIMIT p_limit;
END;
$$;

-- Test searches
-- SELECT * FROM banking.search_transactions(
--     (SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001'),
--     'coffee shop',
--     '2025-01-01',
--     '2026-12-31'
-- );

-- Custom dictionary for banking terms
-- CREATE TEXT SEARCH DICTIONARY banking_synonyms (
--     TEMPLATE = synonym,
--     SYNONYMS = banking_syn
-- );
-- Would need a file: $SHAREDIR/tsearch_data/banking_syn.syn
-- Example content:
-- atm cash
-- pos purchase
-- xfer transfer
```

---

## Exercise 6.2: JSONB for Flexible Customer Preferences 🟡

### Scenario
Store and query complex, flexible customer preferences and settings that vary by customer without schema changes.

### Requirements
1. Store notification preferences
2. Store UI customization settings
3. Store feature flags per customer
4. Query and update nested JSON efficiently

### Solution

```sql
-- Create preferences table with JSONB
CREATE TABLE banking.customer_preferences (
    preference_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL REFERENCES banking.customers(customer_id),
    
    -- Different preference categories as JSONB
    notifications JSONB DEFAULT '{
        "email": {
            "enabled": true,
            "frequency": "daily",
            "types": ["transactions", "statements", "security"]
        },
        "push": {
            "enabled": true,
            "quiet_hours": {"start": "22:00", "end": "08:00"}
        },
        "sms": {
            "enabled": false,
            "phone": null
        }
    }',
    
    ui_settings JSONB DEFAULT '{
        "theme": "light",
        "language": "en",
        "timezone": "America/New_York",
        "dashboard": {
            "widgets": ["balance", "spending", "transactions"],
            "default_account": null
        },
        "accessibility": {
            "high_contrast": false,
            "font_size": "medium"
        }
    }',
    
    feature_flags JSONB DEFAULT '{
        "beta_features": false,
        "new_dashboard": false,
        "ai_insights": true,
        "crypto_trading": false
    }',
    
    custom_data JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_customer_preferences UNIQUE (customer_id)
);

-- Create GIN indexes for JSONB queries
CREATE INDEX idx_preferences_notifications 
ON banking.customer_preferences USING GIN (notifications jsonb_path_ops);

CREATE INDEX idx_preferences_features 
ON banking.customer_preferences USING GIN (feature_flags);

-- Function to get preference with default fallback
CREATE OR REPLACE FUNCTION banking.get_preference(
    p_customer_id UUID,
    p_path TEXT[],
    p_default JSONB DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_result JSONB;
    v_full_data JSONB;
BEGIN
    -- Build the full preferences object
    SELECT 
        jsonb_build_object(
            'notifications', notifications,
            'ui_settings', ui_settings,
            'feature_flags', feature_flags,
            'custom_data', custom_data
        )
    INTO v_full_data
    FROM banking.customer_preferences
    WHERE customer_id = p_customer_id;
    
    IF v_full_data IS NULL THEN
        RETURN p_default;
    END IF;
    
    -- Navigate the path
    v_result := v_full_data;
    FOR i IN 1..array_length(p_path, 1) LOOP
        v_result := v_result -> p_path[i];
        IF v_result IS NULL THEN
            RETURN p_default;
        END IF;
    END LOOP;
    
    RETURN v_result;
END;
$$;

-- Function to update nested preference
CREATE OR REPLACE FUNCTION banking.set_preference(
    p_customer_id UUID,
    p_category TEXT,  -- 'notifications', 'ui_settings', 'feature_flags', 'custom_data'
    p_path TEXT[],
    p_value JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_column_name TEXT;
    v_current JSONB;
    v_updated JSONB;
BEGIN
    -- Validate category
    IF p_category NOT IN ('notifications', 'ui_settings', 'feature_flags', 'custom_data') THEN
        RAISE EXCEPTION 'Invalid category: %', p_category;
    END IF;
    
    -- Ensure preferences exist
    INSERT INTO banking.customer_preferences (customer_id)
    VALUES (p_customer_id)
    ON CONFLICT (customer_id) DO NOTHING;
    
    -- Get current value
    EXECUTE FORMAT(
        'SELECT %I FROM banking.customer_preferences WHERE customer_id = $1',
        p_category
    ) INTO v_current USING p_customer_id;
    
    -- Build path and update
    v_updated := jsonb_set(
        v_current,
        p_path,
        p_value,
        TRUE  -- Create if missing
    );
    
    -- Update the column
    EXECUTE FORMAT(
        'UPDATE banking.customer_preferences SET %I = $1, updated_at = NOW() WHERE customer_id = $2',
        p_category
    ) USING v_updated, p_customer_id;
    
    RETURN v_updated;
END;
$$;

-- Query examples

-- Find all customers with email notifications enabled
SELECT 
    c.customer_number,
    c.email,
    p.notifications->'email'->>'frequency' AS email_frequency
FROM banking.customers c
JOIN banking.customer_preferences p ON c.customer_id = p.customer_id
WHERE p.notifications->'email'->>'enabled' = 'true';

-- Find customers with specific feature flag
SELECT 
    c.customer_number,
    p.feature_flags
FROM banking.customers c
JOIN banking.customer_preferences p ON c.customer_id = p.customer_id
WHERE p.feature_flags @> '{"beta_features": true}';

-- Aggregate preferences statistics
SELECT 
    notifications->'email'->>'frequency' AS email_frequency,
    COUNT(*) AS customer_count
FROM banking.customer_preferences
WHERE notifications->'email'->>'enabled' = 'true'
GROUP BY notifications->'email'->>'frequency';

-- Update preference example
SELECT banking.set_preference(
    (SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001'),
    'notifications',
    ARRAY['email', 'frequency'],
    '"weekly"'::jsonb
);

-- Complex JSONB query: Find customers who can receive push notifications now
SELECT 
    c.customer_number,
    c.email
FROM banking.customers c
JOIN banking.customer_preferences p ON c.customer_id = p.customer_id
WHERE p.notifications->'push'->>'enabled' = 'true'
  AND (
    p.notifications->'push'->'quiet_hours' IS NULL
    OR NOT (
        CURRENT_TIME >= (p.notifications->'push'->'quiet_hours'->>'start')::TIME
        AND CURRENT_TIME <= (p.notifications->'push'->'quiet_hours'->>'end')::TIME
    )
  );

-- JSONB analytics: Most common dashboard widget combinations
SELECT 
    ui_settings->'dashboard'->'widgets' AS widget_config,
    COUNT(*) AS usage_count
FROM banking.customer_preferences
WHERE ui_settings->'dashboard'->'widgets' IS NOT NULL
GROUP BY ui_settings->'dashboard'->'widgets'
ORDER BY usage_count DESC
LIMIT 10;
```

---

## Exercise 6.3: Arrays for Transaction Tags and Categories 🟡

### Scenario
Implement a flexible tagging system for transactions that allows multiple tags per transaction and efficient querying.

### Solution

```sql
-- Add tags array to transactions (if not exists)
ALTER TABLE banking.transactions 
ADD COLUMN IF NOT EXISTS tags TEXT[] DEFAULT '{}';

-- Create GIN index for array operations
CREATE INDEX CONCURRENTLY idx_transactions_tags 
ON banking.transactions USING GIN (tags);

-- Function to add tags to transaction
CREATE OR REPLACE FUNCTION banking.add_transaction_tags(
    p_transaction_id UUID,
    p_transaction_date DATE,
    p_tags TEXT[]
)
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    v_result TEXT[];
BEGIN
    UPDATE banking.transactions
    SET tags = array_cat(
        tags,
        ARRAY(SELECT DISTINCT LOWER(TRIM(t)) FROM unnest(p_tags) t WHERE TRIM(t) != '')
    )
    WHERE transaction_id = p_transaction_id
      AND transaction_date = p_transaction_date
    RETURNING tags INTO v_result;
    
    -- Remove duplicates
    UPDATE banking.transactions
    SET tags = ARRAY(SELECT DISTINCT unnest(tags) ORDER BY 1)
    WHERE transaction_id = p_transaction_id
      AND transaction_date = p_transaction_date
    RETURNING tags INTO v_result;
    
    RETURN v_result;
END;
$$;

-- Function to remove tags
CREATE OR REPLACE FUNCTION banking.remove_transaction_tags(
    p_transaction_id UUID,
    p_transaction_date DATE,
    p_tags TEXT[]
)
RETURNS TEXT[]
LANGUAGE plpgsql
AS $$
DECLARE
    v_result TEXT[];
BEGIN
    UPDATE banking.transactions
    SET tags = array_remove_all(tags, p_tags)
    WHERE transaction_id = p_transaction_id
      AND transaction_date = p_transaction_date
    RETURNING tags INTO v_result;
    
    RETURN v_result;
END;
$$;

-- Helper function to remove multiple elements from array
CREATE OR REPLACE FUNCTION array_remove_all(arr TEXT[], remove_items TEXT[])
RETURNS TEXT[]
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT ARRAY(
        SELECT elem
        FROM unnest(arr) elem
        WHERE elem != ALL(remove_items)
    );
$$;

-- Query: Find transactions with ANY of the specified tags
SELECT 
    t.reference_number,
    t.transaction_date,
    t.amount,
    t.description,
    t.tags
FROM banking.transactions t
WHERE t.tags && ARRAY['business', 'tax-deductible']
ORDER BY t.transaction_date DESC
LIMIT 20;

-- Query: Find transactions with ALL specified tags
SELECT 
    t.reference_number,
    t.transaction_date,
    t.amount,
    t.description,
    t.tags
FROM banking.transactions t
WHERE t.tags @> ARRAY['business', 'travel']
ORDER BY t.transaction_date DESC;

-- Tag analytics
SELECT 
    tag,
    COUNT(*) AS transaction_count,
    SUM(ABS(amount)) AS total_amount,
    AVG(ABS(amount))::NUMERIC(10,2) AS avg_amount
FROM banking.transactions,
     unnest(tags) AS tag
WHERE transaction_date >= CURRENT_DATE - 90
GROUP BY tag
ORDER BY transaction_count DESC
LIMIT 20;

-- Co-occurring tags analysis
WITH tag_pairs AS (
    SELECT 
        t1.tag AS tag1,
        t2.tag AS tag2,
        COUNT(*) AS co_occurrence
    FROM banking.transactions txn,
         unnest(txn.tags) AS t1(tag),
         unnest(txn.tags) AS t2(tag)
    WHERE t1.tag < t2.tag  -- Avoid duplicates
    GROUP BY t1.tag, t2.tag
    HAVING COUNT(*) > 5
)
SELECT * FROM tag_pairs
ORDER BY co_occurrence DESC
LIMIT 20;

-- Auto-tagging function based on merchant/category
CREATE OR REPLACE FUNCTION banking.auto_tag_transaction()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_auto_tags TEXT[] := '{}';
BEGIN
    -- Tag based on amount
    IF ABS(NEW.amount) > 1000 THEN
        v_auto_tags := array_append(v_auto_tags, 'large-purchase');
    END IF;
    
    -- Tag based on category
    CASE NEW.category
        WHEN 'dining' THEN v_auto_tags := array_append(v_auto_tags, 'meals');
        WHEN 'transportation' THEN v_auto_tags := array_append(v_auto_tags, 'travel');
        WHEN 'utilities' THEN v_auto_tags := array_append(v_auto_tags, 'bills');
        ELSE NULL;
    END CASE;
    
    -- Tag based on merchant patterns
    IF NEW.merchant_name ~* '(uber|lyft|taxi)' THEN
        v_auto_tags := array_cat(v_auto_tags, ARRAY['rideshare', 'transportation']);
    ELSIF NEW.merchant_name ~* '(amazon|walmart|target)' THEN
        v_auto_tags := array_append(v_auto_tags, 'retail');
    ELSIF NEW.merchant_name ~* '(starbucks|dunkin|coffee)' THEN
        v_auto_tags := array_append(v_auto_tags, 'coffee');
    END IF;
    
    -- Tag recurring transactions
    IF EXISTS (
        SELECT 1 FROM banking.transactions
        WHERE account_id = NEW.account_id
          AND merchant_name = NEW.merchant_name
          AND ABS(amount - NEW.amount) < 1
          AND transaction_date BETWEEN NEW.transaction_date - 35 AND NEW.transaction_date - 25
    ) THEN
        v_auto_tags := array_append(v_auto_tags, 'recurring');
    END IF;
    
    -- Merge with existing tags
    NEW.tags := ARRAY(
        SELECT DISTINCT unnest(array_cat(COALESCE(NEW.tags, '{}'), v_auto_tags))
    );
    
    RETURN NEW;
END;
$$;

CREATE TRIGGER trg_auto_tag_transaction
    BEFORE INSERT ON banking.transactions
    FOR EACH ROW
    EXECUTE FUNCTION banking.auto_tag_transaction();
```

---

## Exercise 6.4: Using Extensions for Advanced Analytics 🔴

### Scenario
Leverage PostgreSQL extensions to add advanced capabilities for analytics, geospatial queries, and data analysis.

### Solution

```sql
-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;  -- Query performance
CREATE EXTENSION IF NOT EXISTS pgcrypto;            -- Encryption
CREATE EXTENSION IF NOT EXISTS uuid-ossp;           -- UUID generation
CREATE EXTENSION IF NOT EXISTS tablefunc;           -- Pivot tables
CREATE EXTENSION IF NOT EXISTS pg_trgm;             -- Fuzzy matching
CREATE EXTENSION IF NOT EXISTS btree_gist;          -- GiST for exclusion

-- 1. Using tablefunc for pivot reports
-- Monthly spending by category pivot table

-- First, create the crosstab query
SELECT * FROM crosstab(
    $$
    SELECT 
        DATE_TRUNC('month', t.transaction_date)::DATE AS month,
        t.category,
        SUM(ABS(t.amount))::NUMERIC(12,2) AS total
    FROM banking.transactions t
    WHERE t.amount < 0
      AND t.category IS NOT NULL
      AND t.transaction_date >= '2025-01-01'
    GROUP BY DATE_TRUNC('month', t.transaction_date), t.category
    ORDER BY 1, 2
    $$,
    $$
    SELECT DISTINCT category 
    FROM banking.transactions 
    WHERE category IS NOT NULL 
    ORDER BY 1
    $$
) AS pivot(
    month DATE,
    dining NUMERIC,
    groceries NUMERIC,
    shopping NUMERIC,
    transportation NUMERIC,
    utilities NUMERIC
);

-- 2. Using pgcrypto for sensitive data
-- Encrypt SSN/Tax ID before storage
CREATE OR REPLACE FUNCTION banking.encrypt_sensitive_data(
    p_data TEXT,
    p_key TEXT DEFAULT 'your-encryption-key-here'
)
RETURNS BYTEA
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT pgp_sym_encrypt(p_data, p_key);
$$;

CREATE OR REPLACE FUNCTION banking.decrypt_sensitive_data(
    p_encrypted BYTEA,
    p_key TEXT DEFAULT 'your-encryption-key-here'
)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT pgp_sym_decrypt(p_encrypted, p_key);
$$;

-- 3. Statistical functions for analytics
-- Percentile analysis of transaction amounts
SELECT 
    category,
    COUNT(*) AS txn_count,
    ROUND(AVG(ABS(amount))::numeric, 2) AS mean,
    ROUND(STDDEV(ABS(amount))::numeric, 2) AS std_dev,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY ABS(amount)) AS p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY ABS(amount)) AS median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY ABS(amount)) AS p75,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY ABS(amount)) AS p95,
    MODE() WITHIN GROUP (ORDER BY ROUND(ABS(amount), -1)) AS mode_rounded
FROM banking.transactions
WHERE amount < 0 AND category IS NOT NULL
GROUP BY category
ORDER BY txn_count DESC;

-- 4. Time series analysis helpers
-- Create time buckets for analysis
CREATE OR REPLACE FUNCTION analytics.time_bucket(
    p_interval INTERVAL,
    p_timestamp TIMESTAMPTZ
)
RETURNS TIMESTAMPTZ
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT 
        DATE_TRUNC('second', 
            TO_TIMESTAMP(
                FLOOR(EXTRACT(EPOCH FROM p_timestamp) / EXTRACT(EPOCH FROM p_interval)) 
                * EXTRACT(EPOCH FROM p_interval)
            )
        );
$$;

-- Transactions per 15-minute bucket
SELECT 
    analytics.time_bucket('15 minutes', initiated_at) AS time_bucket,
    COUNT(*) AS transaction_count,
    SUM(ABS(amount)) AS total_volume
FROM banking.transactions
WHERE transaction_date = CURRENT_DATE
GROUP BY 1
ORDER BY 1;

-- 5. pg_stat_statements for query analysis
-- Top slow queries
SELECT 
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(total_exec_time::numeric / 1000, 2) AS total_time_sec,
    ROUND(mean_exec_time::numeric, 2) AS avg_time_ms,
    rows,
    ROUND((100 * total_exec_time / SUM(total_exec_time) OVER())::numeric, 2) AS pct_total_time
FROM pg_stat_statements
WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
ORDER BY total_exec_time DESC
LIMIT 20;

-- 6. Window functions for running statistics
SELECT 
    transaction_date,
    amount,
    -- Running stats
    AVG(amount) OVER w AS running_avg,
    STDDEV(amount) OVER w AS running_stddev,
    -- Percentile rank
    PERCENT_RANK() OVER (ORDER BY ABS(amount)) AS percentile,
    -- Z-score (how many std devs from mean)
    (amount - AVG(amount) OVER w) / NULLIF(STDDEV(amount) OVER w, 0) AS z_score
FROM banking.transactions
WHERE account_id = (SELECT account_id FROM banking.accounts WHERE account_number = 'ACC2026-00001-CHK')
  AND transaction_date >= CURRENT_DATE - 30
WINDOW w AS (ORDER BY transaction_date ROWS BETWEEN 29 PRECEDING AND CURRENT ROW);
```

---

## Exercise 6.5: Foreign Data Wrapper for Legacy System Integration 🔴

### Scenario
NeoBank needs to integrate with a legacy core banking system that runs on a separate PostgreSQL instance. Use FDW to query data across systems.

### Solution

```sql
-- Enable postgres_fdw extension
CREATE EXTENSION IF NOT EXISTS postgres_fdw;

-- Create server connection to legacy system
CREATE SERVER legacy_core_banking
    FOREIGN DATA WRAPPER postgres_fdw
    OPTIONS (
        host 'legacy-db.internal',
        port '5432',
        dbname 'core_banking',
        fetch_size '10000'
    );

-- Create user mapping
CREATE USER MAPPING FOR neobank_app
    SERVER legacy_core_banking
    OPTIONS (
        user 'readonly_user',
        password 'secure_password'  -- In production, use .pgpass or secrets manager
    );

-- Import foreign schema
IMPORT FOREIGN SCHEMA legacy 
    LIMIT TO (customers, accounts, transactions)
    FROM SERVER legacy_core_banking
    INTO banking_legacy;

-- Or create specific foreign tables
CREATE FOREIGN TABLE banking.legacy_customers (
    customer_id INTEGER,
    account_number VARCHAR(20),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    created_date DATE
)
SERVER legacy_core_banking
OPTIONS (
    schema_name 'public',
    table_name 'customers'
);

CREATE FOREIGN TABLE banking.legacy_transactions (
    transaction_id BIGINT,
    account_number VARCHAR(20),
    transaction_date DATE,
    amount NUMERIC(12,2),
    description VARCHAR(200),
    status VARCHAR(20)
)
SERVER legacy_core_banking
OPTIONS (
    schema_name 'public',
    table_name 'transactions'
);

-- Query combining local and legacy data
-- Customer migration verification
SELECT 
    l.customer_id AS legacy_id,
    l.email AS legacy_email,
    n.customer_id AS neobank_id,
    n.email AS neobank_email,
    CASE 
        WHEN n.customer_id IS NULL THEN 'Not Migrated'
        WHEN l.email != n.email THEN 'Email Mismatch'
        ELSE 'OK'
    END AS migration_status
FROM banking.legacy_customers l
LEFT JOIN banking.customers n ON l.email = n.email
ORDER BY migration_status, l.customer_id
LIMIT 100;

-- Transaction reconciliation
WITH legacy_totals AS (
    SELECT 
        account_number,
        DATE_TRUNC('day', transaction_date) AS txn_date,
        COUNT(*) AS legacy_count,
        SUM(amount) AS legacy_total
    FROM banking.legacy_transactions
    WHERE transaction_date >= '2025-01-01'
    GROUP BY account_number, DATE_TRUNC('day', transaction_date)
),
neobank_totals AS (
    SELECT 
        a.account_number,
        t.transaction_date AS txn_date,
        COUNT(*) AS neobank_count,
        SUM(t.amount) AS neobank_total
    FROM banking.transactions t
    JOIN banking.accounts a ON t.account_id = a.account_id
    WHERE t.transaction_date >= '2025-01-01'
    GROUP BY a.account_number, t.transaction_date
)
SELECT 
    COALESCE(l.account_number, n.account_number) AS account_number,
    COALESCE(l.txn_date, n.txn_date) AS date,
    l.legacy_count,
    n.neobank_count,
    l.legacy_total,
    n.neobank_total,
    CASE 
        WHEN l.legacy_count IS NULL THEN 'Only in NeoBank'
        WHEN n.neobank_count IS NULL THEN 'Only in Legacy'
        WHEN l.legacy_count != n.neobank_count THEN 'Count Mismatch'
        WHEN l.legacy_total != n.neobank_total THEN 'Amount Mismatch'
        ELSE 'Reconciled'
    END AS status
FROM legacy_totals l
FULL OUTER JOIN neobank_totals n 
    ON l.account_number = n.account_number 
    AND l.txn_date = n.txn_date
WHERE l.legacy_count != n.neobank_count 
   OR l.legacy_total != n.neobank_total
   OR l.account_number IS NULL 
   OR n.account_number IS NULL
ORDER BY date DESC, account_number;

-- Materialized view for frequently accessed legacy data
CREATE MATERIALIZED VIEW banking.mv_legacy_customer_summary AS
SELECT 
    lc.customer_id AS legacy_id,
    lc.account_number AS legacy_account,
    lc.first_name || ' ' || lc.last_name AS legacy_name,
    lc.email AS legacy_email,
    COUNT(lt.transaction_id) AS total_transactions,
    SUM(lt.amount) AS total_amount,
    MAX(lt.transaction_date) AS last_transaction
FROM banking.legacy_customers lc
LEFT JOIN banking.legacy_transactions lt ON lc.account_number = lt.account_number
GROUP BY lc.customer_id, lc.account_number, lc.first_name, lc.last_name, lc.email
WITH DATA;

-- Refresh periodically
-- REFRESH MATERIALIZED VIEW CONCURRENTLY banking.mv_legacy_customer_summary;
```

---

## 🎯 Practice Challenges

### Challenge 6.1 🟡
Implement a search feature that allows searching across customers, accounts, and transactions using a single search box.

### Challenge 6.2 🔴
Create a JSONB-based audit trail that captures the complete before/after state for any table change.

### Challenge 6.3 ⚫
Build a recommendation engine using arrays to suggest merchants based on spending patterns ("Customers who spent here also spent at...").

---

**Next: [Part 7 - Security Exercises](07-security-exercises.md)**
