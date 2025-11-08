# Index Optimization

## Overview

Indexes are crucial for database performance, but they must be carefully designed and maintained. This guide covers index types, optimization strategies, monitoring, maintenance, and best practices for PostgreSQL indexes.

## Table of Contents
- [Index Types and Use Cases](#index-types-and-use-cases)
- [Index Selection Strategy](#index-selection-strategy)
- [Multi-Column Indexes](#multi-column-indexes)
- [Partial Indexes](#partial-indexes)
- [Expression Indexes](#expression-indexes)
- [Covering Indexes](#covering-indexes)
- [Index Maintenance](#index-maintenance)
- [Advanced Techniques](#advanced-techniques)

## Index Types and Use Cases

### B-tree Indexes (Default)

Most common and versatile index type:

```sql
-- Basic B-tree index
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Supports operators: <, <=, =, >=, >, BETWEEN, IN, IS NULL, IS NOT NULL

-- Use cases:
-- 1. Equality searches
SELECT * FROM orders WHERE customer_id = 100;

-- 2. Range queries
SELECT * FROM orders WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- 3. Sorting
SELECT * FROM orders ORDER BY order_date DESC;

-- 4. Pattern matching (prefix only)
SELECT * FROM customers WHERE email LIKE 'john%';  -- Uses index
SELECT * FROM customers WHERE email LIKE '%@gmail.com';  -- Doesn't use index

-- 5. MIN/MAX optimization
SELECT MIN(order_date), MAX(order_date) FROM orders;  -- Fast with index
```

### Hash Indexes

Equality-only comparisons:

```sql
-- Hash index (rarely needed, B-tree usually better)
CREATE INDEX idx_products_code ON products USING hash(product_code);

-- Only supports: =
SELECT * FROM products WHERE product_code = 'ABC123';

-- Doesn't support:
-- - Range queries (<, >, BETWEEN)
-- - Pattern matching (LIKE)
-- - Sorting (ORDER BY)

-- When to use:
-- - Very large tables with equality-only queries
-- - WAL logging available since PostgreSQL 10
-- - Generally, stick with B-tree unless you have specific benchmarks showing benefit
```

### GiST Indexes (Generalized Search Tree)

For geometric types, full-text search, and more:

```sql
-- 1. Geometric data
CREATE TABLE stores (
    store_id SERIAL PRIMARY KEY,
    store_name TEXT,
    location POINT
);

CREATE INDEX idx_stores_location ON stores USING gist(location);

-- Find nearby stores
SELECT * FROM stores 
WHERE location <-> point(40.7128, -74.0060) < 10;

-- 2. Full-text search
CREATE INDEX idx_documents_content ON documents 
USING gist(to_tsvector('english', content));

SELECT * FROM documents 
WHERE to_tsvector('english', content) @@ to_tsquery('postgresql & performance');

-- 3. Range types
CREATE TABLE reservations (
    room_id INTEGER,
    during TSRANGE
);

CREATE INDEX idx_reservations_during ON reservations USING gist(during);

-- Find overlapping reservations
SELECT * FROM reservations 
WHERE during && '[2024-01-01, 2024-01-07)'::tsrange;

-- 4. Exclusion constraints
CREATE TABLE room_bookings (
    room_id INTEGER,
    during TSRANGE,
    EXCLUDE USING gist (room_id WITH =, during WITH &&)
);
-- Prevents overlapping bookings for same room
```

### GIN Indexes (Generalized Inverted Index)

For array, JSONB, and full-text search:

```sql
-- 1. Array columns
CREATE TABLE articles (
    article_id SERIAL PRIMARY KEY,
    title TEXT,
    tags TEXT[]
);

CREATE INDEX idx_articles_tags ON articles USING gin(tags);

-- Find articles with specific tag
SELECT * FROM articles WHERE tags @> ARRAY['postgresql'];

-- Find articles with any of these tags
SELECT * FROM articles WHERE tags && ARRAY['postgresql', 'database'];

-- 2. JSONB columns
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_data JSONB
);

CREATE INDEX idx_orders_customer_data ON orders USING gin(customer_data);

-- Query JSONB
SELECT * FROM orders WHERE customer_data @> '{"vip": true}';
SELECT * FROM orders WHERE customer_data ? 'email';

-- jsonb_path_ops (faster, fewer operations)
CREATE INDEX idx_orders_customer_jsonb ON orders 
USING gin(customer_data jsonb_path_ops);
-- Supports @>, but not ?, ?&, ?|, @?

-- 3. Full-text search (better than GiST for text)
CREATE INDEX idx_documents_search ON documents 
USING gin(to_tsvector('english', content));

SELECT * FROM documents 
WHERE to_tsvector('english', content) @@ to_tsquery('postgresql & optimization');

-- 4. Multiple columns (composite)
CREATE INDEX idx_products_search ON products 
USING gin(to_tsvector('english', name || ' ' || description));
```

### BRIN Indexes (Block Range Index)

For large, naturally ordered tables:

```sql
-- Time-series data
CREATE TABLE sensor_data (
    sensor_id INTEGER,
    recorded_at TIMESTAMP,
    temperature NUMERIC,
    humidity NUMERIC
);

-- BRIN index on time column
CREATE INDEX idx_sensor_data_time ON sensor_data USING brin(recorded_at);

-- Characteristics:
-- - Very small index size (1-2 orders of magnitude smaller than B-tree)
-- - Best for append-only or naturally ordered data
-- - Stores min/max values per block range
-- - Good for: time series, sequential IDs, append-only logs

-- Example: 100 million rows, B-tree index = 2GB, BRIN index = 2MB

-- Query performance:
SELECT AVG(temperature) 
FROM sensor_data 
WHERE recorded_at BETWEEN '2024-01-01' AND '2024-01-31';

-- BRIN is efficient because data is ordered by time

-- Configure pages per range (default: 128)
CREATE INDEX idx_sensor_data_time ON sensor_data 
USING brin(recorded_at) WITH (pages_per_range = 64);

-- Smaller pages_per_range = larger index, more precise, better selectivity
-- Larger pages_per_range = smaller index, less precise, lower selectivity
```

### SP-GiST Indexes (Space-Partitioned GiST)

For partitioned search spaces:

```sql
-- 1. IP addresses
CREATE TABLE access_logs (
    ip_address INET,
    access_time TIMESTAMP
);

CREATE INDEX idx_logs_ip ON access_logs USING spgist(ip_address);

-- Efficient for network queries
SELECT * FROM access_logs WHERE ip_address << '192.168.1.0/24';

-- 2. Text with prefix searches
CREATE INDEX idx_customers_email ON customers USING spgist(email);

-- Good for prefix matching
SELECT * FROM customers WHERE email ^@ 'admin';  -- Starts with 'admin'

-- 3. Geometric data (alternative to GiST)
CREATE INDEX idx_points ON locations USING spgist(location);
```

## Index Selection Strategy

### Identifying Missing Indexes

```sql
-- 1. Analyze slow queries
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
-- If shows "Seq Scan", consider index

-- 2. Use pg_stat_statements
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
WHERE query LIKE '%WHERE%'
ORDER BY mean_exec_time DESC
LIMIT 20;

-- 3. Check for sequential scans
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    seq_tup_read / NULLIF(seq_scan, 0) as avg_seq_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- High seq_scan with large avg_seq_read suggests missing index

-- 4. Missing index on foreign keys
SELECT
    tc.table_name,
    kcu.column_name,
    tc.constraint_name
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu 
    ON tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND NOT EXISTS (
      SELECT 1 FROM pg_indexes pi
      WHERE pi.tablename = tc.table_name
        AND pi.indexdef LIKE '%' || kcu.column_name || '%'
  );
```

### Index Selection Criteria

```sql
-- Create index if:
-- 1. Column used in WHERE clauses frequently
CREATE INDEX idx_orders_status ON orders(status);

-- 2. Column used in JOIN conditions
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_product ON order_items(product_id);

-- 3. Column used in ORDER BY
CREATE INDEX idx_orders_date ON orders(order_date DESC);

-- 4. Column has high cardinality (many distinct values)
SELECT COUNT(DISTINCT customer_id) FROM orders;  -- High cardinality
SELECT COUNT(DISTINCT status) FROM orders;       -- Low cardinality

-- 5. Table is large (small tables don't benefit much)
SELECT pg_size_pretty(pg_relation_size('orders'));

-- DON'T create index if:
-- 1. Column has low cardinality (few distinct values)
-- Example: status column with only 3 values ('pending', 'completed', 'cancelled')

-- 2. Table is small (< 10,000 rows)
-- Sequential scan is faster than index scan for small tables

-- 3. Column updated frequently
-- Index maintenance overhead > query performance gain

-- 4. Query returns large percentage of rows (> 5-10%)
-- Sequential scan is more efficient
```

## Multi-Column Indexes

### Column Order Matters

```sql
-- Index: (customer_id, order_date)
CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date);

-- Can efficiently support:
SELECT * FROM orders WHERE customer_id = 100;  -- Uses index
SELECT * FROM orders WHERE customer_id = 100 AND order_date > '2024-01-01';  -- Uses index
SELECT * FROM orders WHERE customer_id = 100 ORDER BY order_date;  -- Uses index

-- Cannot efficiently support:
SELECT * FROM orders WHERE order_date > '2024-01-01';  -- Doesn't use index (no customer_id)

-- Rule: Index is useful when query has leftmost columns
-- (customer_id) → uses index
-- (customer_id, order_date) → uses index
-- (order_date) → doesn't use index

-- Ordering by selectivity
-- Put most selective (most unique) column first
CREATE INDEX idx_orders_selective ON orders(
    customer_id,    -- High cardinality (many customers)
    status,         -- Low cardinality (few statuses)
    order_date
);

-- But also consider query patterns!
-- If you frequently query by status alone, create separate index
CREATE INDEX idx_orders_status ON orders(status);
```

### Multiple Index Strategies

```sql
-- Strategy 1: Multiple single-column indexes
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
CREATE INDEX idx_orders_status ON orders(status);

-- PostgreSQL can combine indexes using bitmap scans
SELECT * FROM orders 
WHERE customer_id = 100 AND order_date > '2024-01-01';
-- Uses both indexes with Bitmap Index Scan

-- Strategy 2: Composite indexes for specific queries
CREATE INDEX idx_orders_cust_date ON orders(customer_id, order_date);
-- Faster than combining single indexes, but less flexible

-- Strategy 3: Hybrid approach
CREATE INDEX idx_orders_customer ON orders(customer_id);  -- For customer-only queries
CREATE INDEX idx_orders_cust_date_status ON orders(customer_id, order_date, status);  -- For complex queries

-- Verify with EXPLAIN
EXPLAIN SELECT * FROM orders WHERE customer_id = 100 AND order_date > '2024-01-01';
```

## Partial Indexes

Smaller, more efficient indexes:

```sql
-- 1. Index only active records
CREATE INDEX idx_active_customers ON customers(last_login)
WHERE status = 'active';

-- Queries must include the WHERE condition
SELECT * FROM customers 
WHERE status = 'active' AND last_login > '2024-01-01';  -- Uses index

SELECT * FROM customers 
WHERE last_login > '2024-01-01';  -- Doesn't use partial index

-- 2. Index only recent data
CREATE INDEX idx_recent_orders ON orders(customer_id)
WHERE order_date > '2024-01-01';

-- Much smaller index for recent order queries
SELECT * FROM orders 
WHERE customer_id = 100 AND order_date > '2024-01-01';

-- 3. Index non-NULL values
CREATE INDEX idx_customers_email ON customers(email)
WHERE email IS NOT NULL;

-- Useful when column is frequently NULL
SELECT * FROM customers WHERE email = 'john@example.com';

-- 4. Index specific statuses
CREATE INDEX idx_pending_orders ON orders(created_at, customer_id)
WHERE status IN ('pending', 'processing');

-- Efficient for queries on in-progress orders
SELECT * FROM orders 
WHERE status = 'pending' AND created_at < NOW() - INTERVAL '1 day';

-- Benefits:
-- - Smaller index size → faster updates
-- - Reduced maintenance overhead
-- - More cache-efficient
-- - Better for frequently updated tables
```

## Expression Indexes

Index computed values:

```sql
-- 1. Case-insensitive searches
CREATE INDEX idx_customers_lower_email ON customers(LOWER(email));

SELECT * FROM customers WHERE LOWER(email) = 'john@example.com';
-- Uses index

-- 2. Computed columns
CREATE INDEX idx_orders_total ON orders((quantity * unit_price));

SELECT * FROM orders WHERE quantity * unit_price > 1000;
-- Uses index

-- 3. Date extractions
CREATE INDEX idx_orders_year_month ON orders(
    EXTRACT(YEAR FROM order_date),
    EXTRACT(MONTH FROM order_date)
);

SELECT * FROM orders 
WHERE EXTRACT(YEAR FROM order_date) = 2024 
  AND EXTRACT(MONTH FROM order_date) = 6;

-- 4. String operations
CREATE INDEX idx_products_name_trimmed ON products(TRIM(LOWER(name)));

SELECT * FROM products WHERE TRIM(LOWER(name)) = 'widget';

-- 5. JSON path extraction
CREATE INDEX idx_orders_customer_email ON orders((customer_data->>'email'));

SELECT * FROM orders WHERE customer_data->>'email' = 'john@example.com';

-- Important: Query must match index expression exactly
-- This WON'T use the LOWER(email) index:
SELECT * FROM customers WHERE email = 'john@example.com';  -- No LOWER()

-- This WILL use it:
SELECT * FROM customers WHERE LOWER(email) = 'john@example.com';
```

## Covering Indexes

Include all columns needed by query:

```sql
-- Without covering index
CREATE INDEX idx_orders_customer ON orders(customer_id);

SELECT customer_id, order_date, total_amount 
FROM orders 
WHERE customer_id = 100;

-- Execution: Index scan + table lookup for order_date and total_amount

-- With covering index (PostgreSQL 11+)
CREATE INDEX idx_orders_customer_covering ON orders(customer_id)
INCLUDE (order_date, total_amount);

SELECT customer_id, order_date, total_amount 
FROM orders 
WHERE customer_id = 100;

-- Execution: Index Only Scan (no table access!)

-- Verify with EXPLAIN
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id, order_date, total_amount 
FROM orders 
WHERE customer_id = 100;

-- Output should show:
-- Index Only Scan using idx_orders_customer_covering
-- Heap Fetches: 0  -- No table access!

-- Use cases:
-- 1. Frequently run queries with specific column sets
CREATE INDEX idx_users_email_covering ON users(email)
INCLUDE (name, created_at);

-- 2. Avoiding table lookups in joins
CREATE INDEX idx_products_category_covering ON products(category_id)
INCLUDE (product_name, price);

-- Benefits:
-- - Faster queries (no table access)
-- - Reduced I/O
-- - Better cache utilization

-- Tradeoffs:
-- - Larger index size
-- - Slower writes (more index maintenance)
-- - Use judiciously for critical queries only
```

## Index Maintenance

### Monitoring Index Usage

```sql
-- 1. Check index usage statistics
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- idx_scan = 0 means index is never used (consider dropping)

-- 2. Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'  -- Exclude primary keys
  AND indexrelname NOT LIKE '%_key'   -- Exclude unique constraints
ORDER BY pg_relation_size(indexrelid) DESC;

-- 3. Index bloat detection
SELECT
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    ROUND(100 * idx_scan::NUMERIC / NULLIF(idx_tup_read, 0), 2) as hit_rate
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- 4. Index cache hit ratio
SELECT 
    indexrelname,
    idx_blks_read,
    idx_blks_hit,
    ROUND(100.0 * idx_blks_hit / NULLIF(idx_blks_hit + idx_blks_read, 0), 2) as cache_hit_ratio
FROM pg_statio_user_indexes
WHERE idx_blks_read + idx_blks_hit > 0
ORDER BY cache_hit_ratio ASC;

-- Low ratio means index not in cache often (may indicate too many indexes)
```

### Rebuilding Indexes

```sql
-- 1. Reindex single index (locks table)
REINDEX INDEX idx_orders_customer;

-- 2. Reindex table (all indexes)
REINDEX TABLE orders;

-- 3. Concurrent reindex (no locks, PostgreSQL 12+)
REINDEX INDEX CONCURRENTLY idx_orders_customer;

-- 4. Rebuild with new definition
CREATE INDEX CONCURRENTLY idx_orders_customer_new ON orders(customer_id);
DROP INDEX CONCURRENTLY idx_orders_customer;
ALTER INDEX idx_orders_customer_new RENAME TO idx_orders_customer;

-- 5. Schedule regular maintenance
-- In cron or scheduled job:
-- psql -d database -c "REINDEX INDEX CONCURRENTLY idx_name;"

-- When to reindex:
-- - After major data changes (bulk inserts/updates/deletes)
-- - Index bloat (detected via pgstattuple extension)
-- - Performance degradation
-- - After VACUUM FULL

-- Check index bloat
CREATE EXTENSION pgstattuple;

SELECT 
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    round(100 * (1 - avg_leaf_density / 100), 2) as bloat_pct
FROM pg_stat_user_indexes
CROSS JOIN LATERAL pgstatindex(indexrelid)
WHERE avg_leaf_density IS NOT NULL
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Index Maintenance Best Practices

```sql
-- 1. Autovacuum configuration
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,  -- Vacuum at 5% changes
    autovacuum_analyze_scale_factor = 0.02  -- Analyze at 2% changes
);

-- 2. Fillfactor for frequently updated tables
CREATE INDEX idx_orders_customer ON orders(customer_id)
WITH (fillfactor = 70);
-- Leaves 30% space per page for updates, reduces page splits

-- 3. Drop duplicate/redundant indexes
-- Index on (a, b) makes index on (a) redundant
DROP INDEX IF EXISTS idx_redundant;

-- 4. Monitor index creation progress (PostgreSQL 12+)
SELECT 
    pid,
    now() - query_start as duration,
    query,
    state
FROM pg_stat_activity
WHERE query LIKE '%CREATE INDEX%'
  AND state = 'active';

-- 5. Estimate index size before creation
SELECT pg_size_pretty(
    pg_relation_size('table_name') * 0.1  -- Rough estimate: 10% of table size
);
```

## Advanced Techniques

### Conditional Index Use

```sql
-- Force index usage (for testing)
SET enable_seqscan = off;
EXPLAIN SELECT * FROM orders WHERE customer_id = 100;
RESET enable_seqscan;

-- Disable specific index
DROP INDEX idx_orders_customer;
-- Or update statistics to make planner choose different plan
ANALYZE orders;
```

### Index-Only Scans Optimization

```sql
-- Ensure visibility map is up to date
VACUUM orders;

-- Check visibility map coverage
SELECT 
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE relname = 'orders';

-- Verify index-only scan
EXPLAIN (ANALYZE, BUFFERS)
SELECT customer_id FROM orders WHERE customer_id > 100;

-- Should show:
-- Index Only Scan
-- Heap Fetches: 0  (or very low number)

-- If Heap Fetches > 0, table needs vacuum
```

### Parallel Index Creation

```sql
-- Use multiple workers (PostgreSQL 11+)
SET max_parallel_maintenance_workers = 4;

CREATE INDEX CONCURRENTLY idx_large_table ON large_table(column_name);

-- Monitor progress
SELECT 
    pid,
    phase,
    blocks_total,
    blocks_done,
    tuples_total,
    tuples_done
FROM pg_stat_progress_create_index;
```

### Partial Index Optimization

```sql
-- Combine with statistics
CREATE INDEX idx_hot_customers ON customers(last_login)
WHERE last_login > CURRENT_DATE - INTERVAL '90 days';

-- Set statistics target
ALTER TABLE customers ALTER COLUMN last_login SET STATISTICS 1000;

ANALYZE customers;

-- Query must match WHERE condition
SELECT * FROM customers 
WHERE last_login > CURRENT_DATE - INTERVAL '30 days'  -- Within 90 days
  AND status = 'active';
```

## Best Practices Checklist

1. **Index Selection**
   - Index columns in WHERE, JOIN, ORDER BY
   - Index foreign keys
   - Avoid over-indexing (3-5 indexes per table typical)

2. **Index Design**
   - Use appropriate index type
   - Consider column order in composite indexes
   - Use partial indexes for filtered queries
   - Use expression indexes for computed values

3. **Maintenance**
   - Monitor index usage regularly
   - Drop unused indexes
   - Reindex bloated indexes
   - Keep statistics current with ANALYZE

4. **Performance**
   - Test with EXPLAIN ANALYZE
   - Measure before and after
   - Consider covering indexes for hot queries
   - Use BRIN for time-series data

5. **Operations**
   - Use CONCURRENTLY for production
   - Schedule maintenance during low-traffic
   - Monitor disk space before creating indexes
   - Document index purpose and queries served

## Common Pitfalls

1. **Over-indexing**: Too many indexes slow down writes
2. **Wrong column order**: Leftmost columns must match query patterns
3. **Ignoring index maintenance**: Bloated indexes hurt performance
4. **Indexing low-cardinality columns**: Status flags rarely benefit
5. **Forgetting partial indexes**: Full indexes on filtered data waste space
6. **Not using CONCURRENTLY**: Locks table during creation/rebuild
7. **Expression mismatch**: Query must exactly match index expression
8. **Ignoring statistics**: Outdated stats lead to poor plans

## Summary

Index optimization in PostgreSQL requires:
- **Understanding index types** and their appropriate use cases
- **Strategic index selection** based on query patterns
- **Regular monitoring** of index usage and performance
- **Proper maintenance** to prevent bloat and degradation
- **Careful design** of composite, partial, and covering indexes

Effective indexing dramatically improves query performance while balancing write overhead.

## Next Steps

- Learn about [Query Optimization](./20-query-optimization.md)
- Explore [EXPLAIN and Query Plans](./21-explain-and-query-plans.md)
- Study [Partitioning](./23-partitioning.md) for large tables
- Practice [Monitoring and Logging](./38-monitoring-and-logging.md)
