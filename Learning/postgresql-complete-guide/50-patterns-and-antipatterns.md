# Common Patterns and Anti-Patterns

## Overview

This guide covers proven design patterns that lead to robust, performant PostgreSQL databases, as well as anti-patterns that cause problems. Learning to recognize both helps you make better architectural decisions.

## Table of Contents
- [Schema Design Patterns](#schema-design-patterns)
- [Schema Anti-Patterns](#schema-anti-patterns)
- [Query Patterns](#query-patterns)
- [Query Anti-Patterns](#query-anti-patterns)
- [Index Patterns](#index-patterns)
- [Index Anti-Patterns](#index-anti-patterns)
- [Transaction Patterns](#transaction-patterns)
- [Transaction Anti-Patterns](#transaction-anti-patterns)
- [Performance Patterns](#performance-patterns)
- [Performance Anti-Patterns](#performance-anti-patterns)
- [Security Patterns](#security-patterns)
- [Security Anti-Patterns](#security-anti-patterns)

---

## Schema Design Patterns

### ✅ Pattern: Proper Primary Keys

```sql
-- GOOD: UUID for distributed systems
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);

-- GOOD: Serial for simple applications
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- GOOD: Natural key when appropriate
CREATE TABLE countries (
    country_code CHAR(2) PRIMARY KEY,  -- ISO 3166-1 alpha-2
    name VARCHAR(100) NOT NULL
);
```

### ✅ Pattern: Soft Deletes with Status

```sql
-- Track deletion without losing data
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'active' NOT NULL,
    deleted_at TIMESTAMPTZ,
    CONSTRAINT valid_status CHECK (status IN ('active', 'inactive', 'suspended', 'deleted'))
);

-- Partial unique index for active records only
CREATE UNIQUE INDEX idx_users_email_active 
ON users(email) 
WHERE status != 'deleted';

-- View for convenience
CREATE VIEW active_users AS
SELECT * FROM users WHERE status != 'deleted';
```

### ✅ Pattern: Temporal Tables (History Tracking)

```sql
-- Main table
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- History table
CREATE TABLE products_history (
    history_id SERIAL PRIMARY KEY,
    product_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    valid_from TIMESTAMPTZ NOT NULL,
    valid_to TIMESTAMPTZ NOT NULL,
    operation VARCHAR(10) NOT NULL
);

-- Trigger to maintain history
CREATE OR REPLACE FUNCTION track_product_history()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO products_history (product_id, name, price, valid_from, valid_to, operation)
        VALUES (OLD.product_id, OLD.name, OLD.price, OLD.updated_at, NOW(), 'UPDATE');
        NEW.updated_at := NOW();
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO products_history (product_id, name, price, valid_from, valid_to, operation)
        VALUES (OLD.product_id, OLD.name, OLD.price, OLD.updated_at, NOW(), 'DELETE');
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER products_history_trigger
    BEFORE UPDATE OR DELETE ON products
    FOR EACH ROW EXECUTE FUNCTION track_product_history();
```

### ✅ Pattern: Polymorphic Associations with Proper Constraints

```sql
-- Instead of generic foreign keys, use junction tables
CREATE TABLE comments (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    author_id UUID NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Specific association tables
CREATE TABLE post_comments (
    comment_id UUID PRIMARY KEY REFERENCES comments(comment_id),
    post_id UUID NOT NULL REFERENCES posts(post_id)
);

CREATE TABLE product_comments (
    comment_id UUID PRIMARY KEY REFERENCES comments(comment_id),
    product_id UUID NOT NULL REFERENCES products(product_id)
);

-- Alternative: Single table with check constraint
CREATE TABLE comments_v2 (
    comment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    post_id UUID REFERENCES posts(post_id),
    product_id UUID REFERENCES products(product_id),
    -- Ensure exactly one parent
    CONSTRAINT one_parent CHECK (
        (post_id IS NOT NULL AND product_id IS NULL) OR
        (post_id IS NULL AND product_id IS NOT NULL)
    )
);
```

### ✅ Pattern: JSONB for Flexible Attributes

```sql
-- Structured core data + flexible attributes
CREATE TABLE products (
    product_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    -- Flexible attributes that vary by category
    attributes JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- GIN index for JSONB queries
CREATE INDEX idx_products_attributes ON products USING GIN(attributes);

-- Query specific attributes
SELECT * FROM products 
WHERE attributes @> '{"color": "red"}';

SELECT * FROM products 
WHERE attributes->>'size' = 'large';
```

### ✅ Pattern: Enum Types for Fixed Values

```sql
-- Create enum type
CREATE TYPE order_status AS ENUM (
    'pending', 'confirmed', 'processing', 
    'shipped', 'delivered', 'cancelled'
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    status order_status DEFAULT 'pending' NOT NULL
);

-- Benefits:
-- 1. Type safety
-- 2. Smaller storage than VARCHAR
-- 3. Automatic validation

-- Note: Adding values is easy, removing is hard
ALTER TYPE order_status ADD VALUE 'refunded' AFTER 'cancelled';
```

---

## Schema Anti-Patterns

### ❌ Anti-Pattern: Entity-Attribute-Value (EAV)

```sql
-- BAD: EAV pattern
CREATE TABLE entity_attributes (
    entity_id INTEGER,
    attribute_name VARCHAR(100),
    attribute_value TEXT,
    PRIMARY KEY (entity_id, attribute_name)
);

-- Problems:
-- 1. No type safety (everything is TEXT)
-- 2. Complex queries with many JOINs
-- 3. Cannot enforce constraints
-- 4. Poor query performance

-- Example of problematic query:
SELECT 
    e.entity_id,
    MAX(CASE WHEN a.attribute_name = 'name' THEN a.attribute_value END) AS name,
    MAX(CASE WHEN a.attribute_name = 'price' THEN a.attribute_value END) AS price
FROM entities e
JOIN entity_attributes a ON e.entity_id = a.entity_id
GROUP BY e.entity_id;

-- BETTER: Use JSONB or proper columns
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    attributes JSONB DEFAULT '{}'
);
```

### ❌ Anti-Pattern: One True Lookup Table (OTLT)

```sql
-- BAD: Single table for all lookups
CREATE TABLE lookups (
    lookup_id SERIAL PRIMARY KEY,
    lookup_type VARCHAR(50) NOT NULL,  -- 'status', 'category', etc.
    lookup_code VARCHAR(50) NOT NULL,
    lookup_value VARCHAR(255) NOT NULL
);

-- Problems:
-- 1. Cannot have proper foreign keys
-- 2. No referential integrity
-- 3. Complex queries

-- BETTER: Separate tables for each lookup
CREATE TABLE order_statuses (
    status_code VARCHAR(20) PRIMARY KEY,
    description VARCHAR(100)
);

CREATE TABLE categories (
    category_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);
```

### ❌ Anti-Pattern: Storing Comma-Separated Lists

```sql
-- BAD: Comma-separated values
CREATE TABLE users_bad (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    roles VARCHAR(500)  -- 'admin,editor,viewer'
);

-- Problems:
-- 1. Cannot use indexes efficiently
-- 2. No referential integrity
-- 3. Difficult to query
-- 4. Limited by column size

-- BETTER: Use arrays or junction tables
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE user_roles (
    user_id INTEGER REFERENCES users(user_id),
    role VARCHAR(50),
    PRIMARY KEY (user_id, role)
);

-- Or use arrays with GIN index
CREATE TABLE users_v2 (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    roles TEXT[]
);
CREATE INDEX idx_users_roles ON users_v2 USING GIN(roles);
```

### ❌ Anti-Pattern: Storing IP as VARCHAR

```sql
-- BAD: IP as string
CREATE TABLE access_log_bad (
    log_id SERIAL PRIMARY KEY,
    ip_address VARCHAR(45),  -- Supports IPv6
    accessed_at TIMESTAMPTZ
);

-- BETTER: Use INET type
CREATE TABLE access_log (
    log_id SERIAL PRIMARY KEY,
    ip_address INET NOT NULL,
    accessed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Benefits of INET:
-- 1. Validates format
-- 2. Efficient storage
-- 3. Network operations (subnet matching)
SELECT * FROM access_log 
WHERE ip_address << '192.168.1.0/24';  -- Subnet query
```

### ❌ Anti-Pattern: Premature Denormalization

```sql
-- BAD: Copying data everywhere
CREATE TABLE orders_bad (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    customer_name VARCHAR(100),     -- Duplicated!
    customer_email VARCHAR(255),    -- Duplicated!
    customer_phone VARCHAR(20),     -- Duplicated!
    total DECIMAL(10, 2)
);

-- Problems:
-- 1. Update anomalies (change in multiple places)
-- 2. Increased storage
-- 3. Data inconsistency risk

-- BETTER: Normalize first, denormalize only with evidence
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    total DECIMAL(10, 2)
);

-- If you need snapshot data (e.g., shipping address at order time)
CREATE TABLE orders_v2 (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    shipping_address JSONB NOT NULL,  -- Snapshot at order time
    total DECIMAL(10, 2)
);
```

---

## Query Patterns

### ✅ Pattern: Pagination with Keyset/Cursor

```sql
-- GOOD: Keyset pagination (efficient for large datasets)
SELECT * FROM products
WHERE (created_at, product_id) < ('2024-01-15 10:30:00', 'uuid-value')
ORDER BY created_at DESC, product_id DESC
LIMIT 20;

-- GOOD: Return cursor for next page
SELECT 
    *,
    created_at || ',' || product_id AS cursor
FROM products
ORDER BY created_at DESC, product_id DESC
LIMIT 20;

-- Function for cursor-based pagination
CREATE OR REPLACE FUNCTION get_products_page(
    p_cursor TEXT DEFAULT NULL,
    p_limit INTEGER DEFAULT 20
)
RETURNS TABLE (
    product_id UUID,
    name VARCHAR,
    created_at TIMESTAMPTZ,
    next_cursor TEXT
) AS $$
DECLARE
    v_cursor_time TIMESTAMPTZ;
    v_cursor_id UUID;
BEGIN
    IF p_cursor IS NOT NULL THEN
        v_cursor_time := split_part(p_cursor, ',', 1)::TIMESTAMPTZ;
        v_cursor_id := split_part(p_cursor, ',', 2)::UUID;
    END IF;
    
    RETURN QUERY
    SELECT 
        p.product_id,
        p.name,
        p.created_at,
        p.created_at::TEXT || ',' || p.product_id::TEXT AS next_cursor
    FROM products p
    WHERE p_cursor IS NULL 
        OR (p.created_at, p.product_id) < (v_cursor_time, v_cursor_id)
    ORDER BY p.created_at DESC, p.product_id DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;
```

### ✅ Pattern: Conditional Aggregation

```sql
-- Calculate multiple metrics in single scan
SELECT 
    COUNT(*) AS total_orders,
    COUNT(*) FILTER (WHERE status = 'completed') AS completed_orders,
    COUNT(*) FILTER (WHERE status = 'cancelled') AS cancelled_orders,
    SUM(total) FILTER (WHERE status = 'completed') AS total_revenue,
    AVG(total) FILTER (WHERE status = 'completed') AS avg_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers
FROM orders
WHERE created_at >= DATE_TRUNC('month', CURRENT_DATE);
```

### ✅ Pattern: Upsert with ON CONFLICT

```sql
-- Insert or update in one statement
INSERT INTO products (sku, name, price)
VALUES ('SKU-001', 'Widget', 29.99)
ON CONFLICT (sku) 
DO UPDATE SET 
    name = EXCLUDED.name,
    price = EXCLUDED.price,
    updated_at = NOW();

-- Conditional upsert (only update if price increased)
INSERT INTO products (sku, name, price)
VALUES ('SKU-001', 'Widget', 29.99)
ON CONFLICT (sku) 
DO UPDATE SET 
    price = EXCLUDED.price,
    updated_at = NOW()
WHERE products.price < EXCLUDED.price;

-- Insert and return whether it was insert or update
INSERT INTO products (sku, name, price)
VALUES ('SKU-001', 'Widget', 29.99)
ON CONFLICT (sku) DO UPDATE SET name = EXCLUDED.name
RETURNING *, (xmax = 0) AS was_inserted;
```

### ✅ Pattern: Recursive CTEs for Hierarchies

```sql
-- Employee hierarchy
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    manager_id INTEGER REFERENCES employees(employee_id)
);

-- Get full reporting chain
WITH RECURSIVE reporting_chain AS (
    -- Base case: the employee
    SELECT employee_id, name, manager_id, 1 AS level, 
           ARRAY[employee_id] AS path
    FROM employees
    WHERE employee_id = 100
    
    UNION ALL
    
    -- Recursive case: their reports
    SELECT e.employee_id, e.name, e.manager_id, rc.level + 1,
           rc.path || e.employee_id
    FROM employees e
    JOIN reporting_chain rc ON e.manager_id = rc.employee_id
    WHERE NOT e.employee_id = ANY(rc.path)  -- Prevent cycles
)
SELECT * FROM reporting_chain
ORDER BY level, name;
```

### ✅ Pattern: Lateral Joins for Top-N Per Group

```sql
-- Get top 3 orders per customer
SELECT 
    c.customer_id,
    c.name,
    recent_orders.*
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, total, created_at
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY created_at DESC
    LIMIT 3
) recent_orders;

-- With window functions (alternative)
SELECT * FROM (
    SELECT 
        o.*,
        ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
    FROM orders o
) ranked
WHERE rn <= 3;
```

---

## Query Anti-Patterns

### ❌ Anti-Pattern: SELECT *

```sql
-- BAD: Select all columns
SELECT * FROM orders;

-- Problems:
-- 1. Fetches unnecessary data
-- 2. Breaks when columns added
-- 3. Can't use covering indexes

-- BETTER: Explicit columns
SELECT order_id, customer_id, total, status, created_at
FROM orders;
```

### ❌ Anti-Pattern: OFFSET for Pagination

```sql
-- BAD: OFFSET pagination (slow for large offsets)
SELECT * FROM products
ORDER BY created_at DESC
OFFSET 100000 LIMIT 20;  -- Must scan 100,000 rows first!

-- BETTER: Keyset pagination
SELECT * FROM products
WHERE created_at < '2024-01-15'
ORDER BY created_at DESC
LIMIT 20;
```

### ❌ Anti-Pattern: NOT IN with NULLs

```sql
-- BAD: NOT IN can fail with NULLs
SELECT * FROM users
WHERE user_id NOT IN (SELECT user_id FROM banned_users);
-- If banned_users.user_id contains NULL, this returns NO ROWS!

-- BETTER: Use NOT EXISTS
SELECT * FROM users u
WHERE NOT EXISTS (
    SELECT 1 FROM banned_users b WHERE b.user_id = u.user_id
);

-- Or ensure no NULLs
SELECT * FROM users
WHERE user_id NOT IN (
    SELECT user_id FROM banned_users WHERE user_id IS NOT NULL
);
```

### ❌ Anti-Pattern: Using OR in JOIN Conditions

```sql
-- BAD: OR in JOIN (can't use indexes effectively)
SELECT * FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id 
    OR o.legacy_order_id = oi.order_id;

-- BETTER: Use UNION
SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
UNION
SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON o.legacy_order_id = oi.order_id;
```

### ❌ Anti-Pattern: Functions on Indexed Columns

```sql
-- BAD: Function prevents index use
SELECT * FROM orders
WHERE EXTRACT(YEAR FROM created_at) = 2024;

-- BETTER: Use range comparison
SELECT * FROM orders
WHERE created_at >= '2024-01-01' AND created_at < '2025-01-01';

-- Or create expression index if function is necessary
CREATE INDEX idx_orders_year ON orders (EXTRACT(YEAR FROM created_at));
```

### ❌ Anti-Pattern: Implicit Type Conversion

```sql
-- BAD: Comparing different types
SELECT * FROM products
WHERE product_id = '123';  -- product_id is INTEGER

-- This forces PostgreSQL to convert or may use wrong index
-- BETTER: Use correct type
SELECT * FROM products
WHERE product_id = 123;
```

---

## Index Patterns

### ✅ Pattern: Covering Indexes (Include)

```sql
-- Index covers the query completely
CREATE INDEX idx_orders_covering ON orders (customer_id, created_at)
INCLUDE (total, status);

-- This query uses Index Only Scan
SELECT customer_id, created_at, total, status
FROM orders
WHERE customer_id = 123
ORDER BY created_at DESC;
```

### ✅ Pattern: Partial Indexes

```sql
-- Index only active records
CREATE INDEX idx_users_active_email ON users (email)
WHERE status = 'active';

-- Index only recent data
CREATE INDEX idx_orders_recent ON orders (created_at)
WHERE created_at > '2024-01-01';

-- Index only NULL values (for finding missing data)
CREATE INDEX idx_products_missing_category ON products (product_id)
WHERE category_id IS NULL;
```

### ✅ Pattern: Expression Indexes

```sql
-- Case-insensitive search
CREATE INDEX idx_users_email_lower ON users (LOWER(email));

-- JSONB path
CREATE INDEX idx_products_brand ON products ((attributes->>'brand'));

-- Computed value
CREATE INDEX idx_orders_total_with_tax ON orders ((total * 1.1));
```

### ✅ Pattern: Composite Index Column Order

```sql
-- For queries filtering by status AND sorting by date
-- Status first (equality), then date (range/sort)
CREATE INDEX idx_orders_status_date ON orders (status, created_at DESC);

-- Supports:
-- WHERE status = 'pending' ORDER BY created_at DESC  ✓
-- WHERE status = 'pending'  ✓
-- WHERE status IN ('pending', 'processing') ORDER BY created_at DESC  ✓

-- Does NOT efficiently support:
-- ORDER BY created_at DESC  (without status filter)
```

---

## Index Anti-Patterns

### ❌ Anti-Pattern: Index on Every Column

```sql
-- BAD: Too many indexes
CREATE INDEX idx_1 ON orders(customer_id);
CREATE INDEX idx_2 ON orders(status);
CREATE INDEX idx_3 ON orders(created_at);
CREATE INDEX idx_4 ON orders(total);
CREATE INDEX idx_5 ON orders(customer_id, status);
CREATE INDEX idx_6 ON orders(status, created_at);
-- ... and more

-- Problems:
-- 1. Slow writes (each INSERT/UPDATE maintains all indexes)
-- 2. Wasted storage
-- 3. Planner confusion

-- BETTER: Create indexes based on actual query patterns
-- Analyze slow queries with EXPLAIN ANALYZE
```

### ❌ Anti-Pattern: Unused Indexes

```sql
-- Find unused indexes
SELECT 
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'
    AND indexrelname NOT LIKE '%_unique'
ORDER BY pg_relation_size(indexrelid) DESC;

-- Consider dropping indexes with 0 scans
-- (wait sufficient time to capture all query patterns)
```

### ❌ Anti-Pattern: Redundant Indexes

```sql
-- BAD: Redundant indexes
CREATE INDEX idx_a ON orders(customer_id);
CREATE INDEX idx_b ON orders(customer_id, created_at);  -- This covers idx_a's use case!

-- The composite index idx_b can serve queries that only filter by customer_id
-- idx_a is redundant
```

---

## Transaction Patterns

### ✅ Pattern: Advisory Locks for Application-Level Locking

```sql
-- Prevent concurrent processing of same entity
SELECT pg_try_advisory_lock(hashtext('order_' || order_id::text))
FROM orders WHERE order_id = 'uuid-value';

-- Process if lock acquired
-- ...

-- Release lock
SELECT pg_advisory_unlock(hashtext('order_' || 'uuid-value'));

-- Or use session-level lock that auto-releases
SELECT pg_advisory_lock(12345);  -- Blocks until available
-- ... do work ...
SELECT pg_advisory_unlock(12345);
```

### ✅ Pattern: Optimistic Locking

```sql
-- Add version column
CREATE TABLE accounts (
    account_id UUID PRIMARY KEY,
    balance DECIMAL(15, 2),
    version INTEGER DEFAULT 1
);

-- Update with version check
UPDATE accounts
SET balance = balance - 100,
    version = version + 1
WHERE account_id = 'uuid-value'
    AND version = 5;  -- Expected version

-- Check if update succeeded
-- If 0 rows affected, someone else modified the record
```

### ✅ Pattern: Idempotent Operations

```sql
-- Use unique request ID for idempotency
CREATE TABLE processed_requests (
    request_id UUID PRIMARY KEY,
    result JSONB,
    processed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Check before processing
INSERT INTO processed_requests (request_id, result)
VALUES ('request-uuid', '{"status": "processing"}')
ON CONFLICT (request_id) DO NOTHING
RETURNING request_id;

-- If nothing returned, request was already processed
-- Fetch previous result instead
```

---

## Transaction Anti-Patterns

### ❌ Anti-Pattern: Long-Running Transactions

```sql
-- BAD: Keeping transaction open
BEGIN;
SELECT * FROM large_table;  -- Start transaction
-- ... wait for user input or external service ...
-- ... transaction still open, blocking VACUUM ...
COMMIT;  -- Finally commits after minutes/hours

-- Problems:
-- 1. Prevents vacuum from reclaiming space
-- 2. Bloats tables with dead tuples
-- 3. Can cause transaction ID wraparound

-- BETTER: Keep transactions short
-- Fetch data, process outside transaction, then write
```

### ❌ Anti-Pattern: SELECT FOR UPDATE Without Timeout

```sql
-- BAD: Wait indefinitely
SELECT * FROM inventory 
WHERE product_id = 123 
FOR UPDATE;  -- Can block forever if another session holds lock

-- BETTER: Use timeout
SET lock_timeout = '5s';
SELECT * FROM inventory 
WHERE product_id = 123 
FOR UPDATE;

-- Or use NOWAIT to fail immediately
SELECT * FROM inventory 
WHERE product_id = 123 
FOR UPDATE NOWAIT;

-- Or SKIP LOCKED for queue-like processing
SELECT * FROM tasks 
WHERE status = 'pending'
FOR UPDATE SKIP LOCKED
LIMIT 1;
```

---

## Performance Patterns

### ✅ Pattern: Batch Operations

```sql
-- GOOD: Batch inserts
INSERT INTO log_entries (message, level, created_at)
VALUES 
    ('Message 1', 'INFO', NOW()),
    ('Message 2', 'WARN', NOW()),
    ('Message 3', 'ERROR', NOW());
    -- ... up to thousands of rows

-- GOOD: Batch updates with UNNEST
UPDATE products
SET price = data.new_price
FROM (
    SELECT unnest(ARRAY['sku1', 'sku2', 'sku3']) AS sku,
           unnest(ARRAY[10.99, 20.99, 30.99]) AS new_price
) AS data
WHERE products.sku = data.sku;

-- GOOD: Bulk delete with CTE
WITH to_delete AS (
    SELECT order_id FROM orders
    WHERE status = 'cancelled' AND created_at < NOW() - INTERVAL '1 year'
    LIMIT 10000
)
DELETE FROM orders
WHERE order_id IN (SELECT order_id FROM to_delete);
```

### ✅ Pattern: Materialized Views for Complex Reports

```sql
-- Create materialized view for dashboard
CREATE MATERIALIZED VIEW sales_summary AS
SELECT 
    DATE_TRUNC('day', o.created_at) AS date,
    p.category_id,
    COUNT(*) AS order_count,
    SUM(oi.quantity) AS units_sold,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY DATE_TRUNC('day', o.created_at), p.category_id;

-- Add unique index for concurrent refresh
CREATE UNIQUE INDEX idx_sales_summary ON sales_summary (date, category_id);

-- Refresh without blocking reads
REFRESH MATERIALIZED VIEW CONCURRENTLY sales_summary;
```

### ✅ Pattern: Connection Pooling Configuration

```sql
-- Application-side: Use PgBouncer
-- Settings in pgbouncer.ini:
-- pool_mode = transaction  (for most web apps)
-- default_pool_size = 20
-- max_client_conn = 1000

-- PostgreSQL-side settings for pooled connections
ALTER SYSTEM SET idle_in_transaction_session_timeout = '30s';
ALTER SYSTEM SET statement_timeout = '60s';
```

---

## Performance Anti-Patterns

### ❌ Anti-Pattern: N+1 Queries

```sql
-- BAD: N+1 queries
-- First query: Get all orders
SELECT * FROM orders WHERE customer_id = 123;

-- Then for EACH order (N queries):
SELECT * FROM order_items WHERE order_id = 'order-1';
SELECT * FROM order_items WHERE order_id = 'order-2';
-- ... repeated N times

-- BETTER: Single query with JOIN
SELECT o.*, oi.*
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.customer_id = 123;

-- Or use array aggregation
SELECT 
    o.*,
    array_agg(oi.*) AS items
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.customer_id = 123
GROUP BY o.order_id;
```

### ❌ Anti-Pattern: COUNT(*) for Existence Check

```sql
-- BAD: Count all matching rows
SELECT CASE WHEN COUNT(*) > 0 THEN true ELSE false END
FROM orders
WHERE customer_id = 123;  -- Counts ALL orders

-- BETTER: Use EXISTS (stops at first match)
SELECT EXISTS (
    SELECT 1 FROM orders WHERE customer_id = 123
);

-- Or LIMIT 1
SELECT 1 FROM orders WHERE customer_id = 123 LIMIT 1;
```

### ❌ Anti-Pattern: Storing Large BLOBs in Database

```sql
-- BAD: Large files in database
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY,
    file_data BYTEA,  -- Storing 100MB files
    metadata JSONB
);

-- Problems:
-- 1. Bloats database size
-- 2. Increases backup time
-- 3. Memory pressure during queries

-- BETTER: Store reference to external storage
CREATE TABLE documents (
    doc_id UUID PRIMARY KEY,
    storage_path TEXT NOT NULL,  -- S3, GCS, or filesystem path
    file_size BIGINT,
    mime_type VARCHAR(100),
    metadata JSONB
);
```

---

## Security Patterns

### ✅ Pattern: Parameterized Queries

```sql
-- ALWAYS use parameterized queries
-- In application code:
-- cursor.execute("SELECT * FROM users WHERE email = %s", [user_email])

-- NOT string concatenation:
-- cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}'")  -- SQL INJECTION RISK!
```

### ✅ Pattern: Least Privilege Roles

```sql
-- Create specific roles
CREATE ROLE app_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;

CREATE ROLE app_readwrite;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;

-- Application user inherits appropriate role
CREATE USER webapp_user WITH PASSWORD 'secure_password';
GRANT app_readwrite TO webapp_user;
```

### ✅ Pattern: Row-Level Security

```sql
-- Enable RLS
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Users see only their documents
CREATE POLICY user_documents ON documents
    USING (owner_id = current_setting('app.user_id')::UUID);

-- Admins see everything
CREATE POLICY admin_all ON documents
    USING (current_setting('app.is_admin')::BOOLEAN = TRUE);

-- Set context before queries
SET app.user_id = 'user-uuid';
SET app.is_admin = 'false';
```

---

## Security Anti-Patterns

### ❌ Anti-Pattern: Storing Plaintext Passwords

```sql
-- BAD: Never do this
CREATE TABLE users_bad (
    user_id INTEGER PRIMARY KEY,
    password VARCHAR(100)  -- Plaintext password!
);

-- BETTER: Use pgcrypto for hashing
CREATE EXTENSION pgcrypto;

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    password_hash TEXT NOT NULL
);

-- Store hashed password
INSERT INTO users (user_id, password_hash)
VALUES (1, crypt('user_password', gen_salt('bf', 10)));

-- Verify password
SELECT user_id FROM users
WHERE user_id = 1 AND password_hash = crypt('input_password', password_hash);
```

### ❌ Anti-Pattern: Excessive Privileges

```sql
-- BAD: Application using superuser
-- webapp connects as postgres (superuser)

-- BAD: Granting too much
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO webapp_user;

-- BETTER: Minimal required privileges
GRANT SELECT, INSERT, UPDATE ON specific_tables TO webapp_user;
REVOKE DELETE ON sensitive_tables FROM webapp_user;
```

---

## Summary

### Pattern Checklist

| Category | ✅ Do | ❌ Avoid |
|----------|-------|---------|
| Schema | Proper PKs, JSONB for flex data | EAV, comma-separated lists |
| Queries | Keyset pagination, EXISTS | OFFSET, SELECT *, N+1 |
| Indexes | Partial, covering, expression | Over-indexing, redundant |
| Transactions | Short, idempotent | Long-running, no timeout |
| Security | Parameterized, RLS, least privilege | Plaintext passwords, superuser |

---

## Next Steps

- [Migration Strategies](51-migration-strategies.md)
- [Troubleshooting Guide](52-troubleshooting-guide.md)
