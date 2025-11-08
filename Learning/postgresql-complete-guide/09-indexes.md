# Indexes

## Overview

Indexes are special database objects that speed up data retrieval. They work like a book's index, allowing PostgreSQL to quickly locate rows without scanning the entire table.

## Why Use Indexes?

### Performance Impact

```sql
-- Without index: Full table scan
-- With 1 million rows, might scan all rows

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    email TEXT,
    created_at TIMESTAMPTZ
);

-- Insert sample data
INSERT INTO users (email, created_at)
SELECT 
    'user' || generate_series || '@example.com',
    NOW() - (random() * INTERVAL '365 days')
FROM generate_series(1, 1000000);

-- Query without index (slow)
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user50000@example.com';
-- Seq Scan on users  (cost=0.00..20834.00 rows=1 width=45) (actual time=150.234..150.234 rows=1)

-- Create index
CREATE INDEX idx_users_email ON users(email);

-- Query with index (fast)
EXPLAIN ANALYZE
SELECT * FROM users WHERE email = 'user50000@example.com';
-- Index Scan using idx_users_email  (cost=0.42..8.44 rows=1 width=45) (actual time=0.034..0.036 rows=1)
```

### Trade-offs

**Benefits**:
- ✅ Faster SELECT queries
- ✅ Faster JOIN operations
- ✅ Faster WHERE clauses
- ✅ Faster ORDER BY
- ✅ Enforce uniqueness

**Costs**:
- ❌ Slower INSERT operations
- ❌ Slower UPDATE operations
- ❌ Slower DELETE operations
- ❌ Additional disk space
- ❌ Maintenance overhead

## B-Tree Indexes (Default)

### Overview

B-Tree is the default and most commonly used index type, suitable for most scenarios.

### Creating B-Tree Indexes

```sql
-- Simple index
CREATE INDEX idx_users_email ON users(email);

-- Named explicitly
CREATE INDEX CONCURRENTLY idx_users_email ON users USING BTREE (email);

-- Composite index (multiple columns)
CREATE INDEX idx_users_name_email ON users(last_name, first_name, email);

-- Partial index (conditional)
CREATE INDEX idx_active_users ON users(email) WHERE is_active = TRUE;

-- Expression index
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- DESC index for ORDER BY DESC
CREATE INDEX idx_users_created_desc ON users(created_at DESC);

-- NULLS FIRST/LAST
CREATE INDEX idx_users_last_login ON users(last_login DESC NULLS LAST);
```

### When to Use B-Tree

```sql
-- Equality comparisons
SELECT * FROM users WHERE user_id = 100;

-- Range queries
SELECT * FROM users WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31';

-- Sorting
SELECT * FROM users ORDER BY created_at;

-- Pattern matching (prefix only)
SELECT * FROM users WHERE email LIKE 'john%';  -- Uses index
SELECT * FROM users WHERE email LIKE '%john%'; -- Doesn't use index

-- IN clauses
SELECT * FROM users WHERE user_id IN (1, 2, 3, 4, 5);

-- MIN/MAX
SELECT MIN(created_at) FROM users;
```

### Composite Index Column Order

```sql
-- Index on (last_name, first_name)
CREATE INDEX idx_users_name ON users(last_name, first_name);

-- Can use index for:
SELECT * FROM users WHERE last_name = 'Smith';                    -- ✅
SELECT * FROM users WHERE last_name = 'Smith' AND first_name = 'John'; -- ✅
SELECT * FROM users WHERE last_name LIKE 'Sm%';                   -- ✅

-- Cannot use index for:
SELECT * FROM users WHERE first_name = 'John';                    -- ❌
SELECT * FROM users WHERE first_name LIKE 'Jo%';                  -- ❌

-- Rule: Index helps with leftmost columns only
```

## Hash Indexes

### Overview

Hash indexes are for simple equality comparisons only.

```sql
-- Create hash index
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- Good for equality
SELECT * FROM users WHERE email = 'john@example.com';  -- Uses hash index

-- Not for ranges or patterns
SELECT * FROM users WHERE email LIKE 'john%';          -- Doesn't use hash
SELECT * FROM users WHERE email > 'a@example.com';     -- Doesn't use hash
```

### When to Use Hash

- ✅ Only equality comparisons
- ✅ Large tables with many duplicates
- ❌ Rarely needed (B-Tree usually better)
- ❌ Can't be used for sorting
- ❌ Can't be used for range queries

## GiST Indexes (Generalized Search Tree)

### Overview

GiST indexes support various data types including geometric, full-text, and range types.

```sql
-- Full-text search
CREATE INDEX idx_documents_search ON documents USING GIST (search_vector);

-- Range types (prevent overlaps)
CREATE INDEX idx_bookings_range ON room_bookings USING GIST (during);

-- Geometric data
CREATE INDEX idx_locations_point ON locations USING GIST (coordinates);

-- Array containment
CREATE INDEX idx_posts_tags ON posts USING GIST (tags);
```

### Full-Text Search Example

```sql
CREATE TABLE articles (
    article_id SERIAL PRIMARY KEY,
    title TEXT,
    body TEXT,
    search_vector TSVECTOR
);

-- Update search vector
UPDATE articles 
SET search_vector = to_tsvector('english', title || ' ' || body);

-- Create GiST index
CREATE INDEX idx_articles_search ON articles USING GIST (search_vector);

-- Search
SELECT * FROM articles 
WHERE search_vector @@ to_tsquery('english', 'postgresql & performance');
```

### Range Type Example

```sql
-- Prevent overlapping bookings
CREATE TABLE bookings (
    booking_id SERIAL PRIMARY KEY,
    room_id INTEGER,
    during TSTZRANGE
);

CREATE INDEX idx_bookings_room_time ON bookings USING GIST (room_id, during);

-- Find overlapping bookings
SELECT * FROM bookings 
WHERE room_id = 101 
  AND during && tstzrange('2024-12-20', '2024-12-22');
```

## GIN Indexes (Generalized Inverted Index)

### Overview

GIN indexes are ideal for indexing composite values like arrays, JSONB, and full-text search.

```sql
-- JSONB indexing
CREATE INDEX idx_products_attributes ON products USING GIN (attributes);

-- Array indexing
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- Full-text search (usually better than GiST)
CREATE INDEX idx_documents_search ON documents USING GIN (search_vector);

-- Trigram similarity
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);
```

### JSONB Indexing

```sql
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    name TEXT,
    attributes JSONB
);

-- Standard GIN index
CREATE INDEX idx_products_attrs ON products USING GIN (attributes);

-- Query with GIN index
SELECT * FROM products 
WHERE attributes @> '{"brand": "Apple"}';

SELECT * FROM products 
WHERE attributes ? 'color';

SELECT * FROM products 
WHERE attributes ?| ARRAY['bluetooth', 'wifi'];

-- jsonb_path_ops (more efficient, but only for @> operator)
CREATE INDEX idx_products_attrs_path ON products 
USING GIN (attributes jsonb_path_ops);
```

### Array Indexing

```sql
CREATE TABLE posts (
    post_id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[]
);

-- GIN index on array
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- Queries that use the index
SELECT * FROM posts WHERE tags @> ARRAY['postgresql'];
SELECT * FROM posts WHERE tags && ARRAY['database', 'sql'];
SELECT * FROM posts WHERE 'postgresql' = ANY(tags);
```

### Full-Text Search with GIN

```sql
-- GIN is usually better than GiST for full-text
CREATE TABLE documents (
    doc_id SERIAL PRIMARY KEY,
    content TEXT,
    search_vector TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', content)) STORED
);

CREATE INDEX idx_docs_search ON documents USING GIN (search_vector);

-- Fast full-text queries
SELECT * FROM documents 
WHERE search_vector @@ to_tsquery('english', 'postgresql & database');
```

## BRIN Indexes (Block Range Index)

### Overview

BRIN indexes are very small and efficient for large, naturally ordered tables.

```sql
-- Time-series data
CREATE TABLE sensor_data (
    sensor_id INTEGER,
    reading_time TIMESTAMPTZ,
    temperature DECIMAL(5,2)
);

-- BRIN index (much smaller than B-Tree)
CREATE INDEX idx_sensor_time ON sensor_data USING BRIN (reading_time);

-- Efficient for range queries on ordered data
SELECT * FROM sensor_data 
WHERE reading_time BETWEEN '2024-01-01' AND '2024-01-31';
```

### When to Use BRIN

**Good for**:
- ✅ Very large tables (billions of rows)
- ✅ Naturally ordered data (timestamps, sequences)
- ✅ Append-only tables
- ✅ When index size is a concern
- ✅ Data warehouse queries

**Not good for**:
- ❌ Small tables
- ❌ Randomly ordered data
- ❌ Frequent updates
- ❌ High selectivity queries

```sql
-- Example: Log data
CREATE TABLE access_logs (
    log_id BIGSERIAL,
    log_time TIMESTAMPTZ DEFAULT NOW(),
    user_id INTEGER,
    action TEXT
);

-- BRIN index on timestamp
CREATE INDEX idx_logs_time ON access_logs USING BRIN (log_time);

-- Compare index sizes
SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes
WHERE tablename = 'access_logs';
```

## SP-GiST Indexes (Space-Partitioned GiST)

### Overview

SP-GiST supports partitioned search trees for specialized data types.

```sql
-- Phone numbers, IP addresses
CREATE INDEX idx_ips ON network_logs USING SPGIST (ip_address);

-- Quad-tree for points
CREATE INDEX idx_locations ON stores USING SPGIST (location);

-- Text prefix searches
CREATE INDEX idx_names ON users USING SPGIST (name text_ops);
```

## Partial Indexes

### Overview

Index only rows that match a condition, saving space and improving performance.

```sql
-- Index only active users
CREATE INDEX idx_active_users_email ON users(email) 
WHERE is_active = TRUE;

-- Index only recent orders
CREATE INDEX idx_recent_orders ON orders(created_at) 
WHERE created_at > NOW() - INTERVAL '90 days';

-- Index only high-value orders
CREATE INDEX idx_high_value_orders ON orders(total) 
WHERE total > 1000;

-- Index only NULL values
CREATE INDEX idx_users_no_email ON users(user_id) 
WHERE email IS NULL;

-- Multiple conditions
CREATE INDEX idx_premium_active_users ON users(email) 
WHERE is_active = TRUE AND subscription_type = 'premium';
```

### Query Must Match Condition

```sql
-- This uses the index
SELECT * FROM users 
WHERE is_active = TRUE AND email = 'john@example.com';

-- This doesn't use the index
SELECT * FROM users 
WHERE email = 'john@example.com';  -- Missing is_active condition
```

## Expression Indexes

### Overview

Index the result of an expression or function.

```sql
-- Case-insensitive search
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

SELECT * FROM users WHERE LOWER(email) = 'john@example.com';

-- Date extraction
CREATE INDEX idx_orders_month ON orders(EXTRACT(MONTH FROM created_at));

SELECT * FROM orders WHERE EXTRACT(MONTH FROM created_at) = 12;

-- Computed column
CREATE INDEX idx_full_name ON users((first_name || ' ' || last_name));

SELECT * FROM users WHERE (first_name || ' ' || last_name) = 'John Doe';

-- JSON extraction
CREATE INDEX idx_products_brand ON products((attributes->>'brand'));

SELECT * FROM products WHERE attributes->>'brand' = 'Apple';

-- Trigram for fuzzy search
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_users_name_trgm ON users USING GIN (name gin_trgm_ops);

SELECT * FROM users WHERE name % 'Jon Doe';  -- Similarity search
```

## Unique Indexes

```sql
-- Unique index (same as UNIQUE constraint)
CREATE UNIQUE INDEX idx_users_email_unique ON users(email);

-- Unique composite index
CREATE UNIQUE INDEX idx_users_username_email ON users(username, email);

-- Partial unique index (unique only for active users)
CREATE UNIQUE INDEX idx_active_users_email ON users(email) 
WHERE is_active = TRUE;

-- Case-insensitive unique
CREATE UNIQUE INDEX idx_users_email_lower ON users(LOWER(email));

-- Unique with NULL handling (NULL values don't conflict)
CREATE UNIQUE INDEX idx_users_phone ON users(phone) 
WHERE phone IS NOT NULL;
```

## Index Management

### Creating Indexes

```sql
-- Standard creation (locks table)
CREATE INDEX idx_users_email ON users(email);

-- Concurrent creation (no lock, slower)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- If not exists
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);

-- With tablespace
CREATE INDEX idx_users_email ON users(email) TABLESPACE fast_storage;
```

### Dropping Indexes

```sql
-- Drop index
DROP INDEX idx_users_email;

-- Concurrent drop (no lock)
DROP INDEX CONCURRENTLY idx_users_email;

-- Drop if exists
DROP INDEX IF EXISTS idx_users_email;

-- Drop cascade (also drop dependent objects)
DROP INDEX idx_users_email CASCADE;
```

### Reindexing

```sql
-- Rebuild single index
REINDEX INDEX idx_users_email;

-- Rebuild all indexes on table
REINDEX TABLE users;

-- Rebuild all indexes in database
REINDEX DATABASE mydb;

-- Concurrent reindex (PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY idx_users_email;

-- Why reindex?
-- - Reduce index bloat
-- - Fix corrupted indexes
-- - Improve performance after bulk operations
```

### Monitoring Indexes

```sql
-- List all indexes
\di

-- List indexes for a table
\d users

-- Index size
SELECT 
    indexname,
    tablename,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY pg_relation_size(indexname::regclass) DESC;

-- Index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan AS index_scans,
    idx_tup_read AS tuples_read,
    idx_tup_fetch AS tuples_fetched
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;

-- Unused indexes (potential candidates for removal)
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexname::regclass)) AS index_size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexname::regclass) DESC;

-- Index bloat
CREATE EXTENSION IF NOT EXISTS pgstattuple;

SELECT 
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    round(100 * (1 - avg_leaf_density/100),2) AS bloat_pct
FROM pg_index
JOIN pg_class ON pg_class.oid = pg_index.indexrelid
JOIN pg_stat_user_indexes ON pg_stat_user_indexes.indexrelid = pg_index.indexrelid
CROSS JOIN LATERAL pgstatindex(pg_class.oid) AS pgsi
WHERE schemaname = 'public'
ORDER BY bloat_pct DESC;
```

## Index Design Strategies

### 1. Identify Query Patterns

```sql
-- Enable query logging
ALTER DATABASE mydb SET log_min_duration_statement = 100;  -- Log queries > 100ms

-- Analyze slow queries
SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;

-- Create indexes based on WHERE clauses and JOINs
```

### 2. Covering Indexes

```sql
-- Query needs user_id and email
CREATE INDEX idx_users_id_email ON users(user_id, email);

-- Index-only scan (faster)
EXPLAIN (ANALYZE, BUFFERS) 
SELECT user_id, email FROM users WHERE user_id > 1000;
```

### 3. Composite Index Guidelines

```sql
-- Order by cardinality (high to low)
CREATE INDEX idx_orders_status_user ON orders(status, user_id);
-- Not: CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Order by query patterns
-- If you often query: WHERE user_id = ? AND status = ?
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- If you often query: WHERE status = ?
CREATE INDEX idx_orders_status ON orders(status);
```

### 4. Avoid Over-Indexing

```sql
-- Bad: Too many indexes
CREATE INDEX idx1 ON users(email);
CREATE INDEX idx2 ON users(username);
CREATE INDEX idx3 ON users(email, username);  -- Redundant
CREATE INDEX idx4 ON users(username, email);  -- Redundant

-- Good: Necessary indexes only
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
```

## Best Practices

### 1. When to Create Indexes

```sql
-- ✅ DO: Index foreign keys
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- ✅ DO: Index columns in WHERE clauses
CREATE INDEX idx_users_created_at ON users(created_at);

-- ✅ DO: Index columns in JOIN conditions
CREATE INDEX idx_order_items_product_id ON order_items(product_id);

-- ✅ DO: Index columns in ORDER BY
CREATE INDEX idx_products_price ON products(price);

-- ✅ DO: Index columns in GROUP BY
CREATE INDEX idx_sales_category ON sales(category);
```

### 2. When NOT to Create Indexes

```sql
-- ❌ DON'T: Index small tables
-- (< 1000 rows, sequential scan is faster)

-- ❌ DON'T: Index frequently updated columns
-- (Unless read-heavy workload)

-- ❌ DON'T: Index low-cardinality columns
CREATE INDEX idx_users_gender ON users(gender);  -- Only 2-3 values

-- ❌ DON'T: Create redundant indexes
-- If you have idx(a,b), you don't need idx(a)
```

### 3. Maintenance

```sql
-- Monitor index bloat
SELECT * FROM pgstatindex('idx_users_email');

-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_users_email;

-- Remove unused indexes
-- Check idx_scan in pg_stat_user_indexes

-- Update statistics regularly
ANALYZE users;
```

## Summary

**Index Types**:
- **B-Tree**: Default, most common use cases
- **Hash**: Equality only (rarely needed)
- **GiST**: Full-text, geometric, ranges
- **GIN**: JSONB, arrays, full-text (best for full-text)
- **BRIN**: Very large, ordered tables
- **SP-GiST**: Specialized partitioned searches

**Special Indexes**:
- **Partial**: Index subset of rows
- **Expression**: Index computed values
- **Unique**: Enforce uniqueness
- **Covering**: Include extra columns

**Best Practices**:
- Index foreign keys
- Index WHERE clause columns
- Use composite indexes wisely
- Monitor usage and bloat
- Create indexes concurrently in production
- Don't over-index

**Next Topics**:
- [Query Optimization](20-query-optimization.md)
- [EXPLAIN and Query Plans](21-explain-and-query-plans.md)
- [Index Optimization](22-index-optimization.md)
