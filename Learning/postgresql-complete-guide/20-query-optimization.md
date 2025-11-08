# Query Optimization

## Overview

Query optimization is critical for database performance. PostgreSQL's query planner automatically optimizes queries, but understanding how it works and how to influence it can dramatically improve performance. This guide covers query analysis, optimization techniques, and performance tuning.

## Table of Contents
- [Query Execution Process](#query-execution-process)
- [EXPLAIN and EXPLAIN ANALYZE](#explain-and-explain-analyze)
- [Index Optimization](#index-optimization)
- [Query Rewriting](#query-rewriting)
- [Join Optimization](#join-optimization)
- [Subquery Optimization](#subquery-optimization)
- [Statistics and Planner](#statistics-and-planner)
- [Configuration Tuning](#configuration-tuning)

## Query Execution Process

### How PostgreSQL Executes Queries

1. **Parsing**: SQL text → parse tree
2. **Analysis**: Validate syntax, resolve names
3. **Rewriting**: Apply rules (views, etc.)
4. **Planning**: Generate optimal execution plan
5. **Execution**: Execute the plan, return results

```sql
-- Simple query execution
SELECT customer_name, total_amount
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_date > '2024-01-01'
ORDER BY total_amount DESC
LIMIT 10;

-- Planner considers:
-- - Available indexes
-- - Table statistics
-- - Join methods (nested loop, hash, merge)
-- - Sort methods
-- - Cost estimates
```

## EXPLAIN and EXPLAIN ANALYZE

### Basic EXPLAIN

```sql
-- Show execution plan (doesn't run query)
EXPLAIN
SELECT * FROM orders WHERE customer_id = 100;

-- Output:
-- Seq Scan on orders  (cost=0.00..1806.00 rows=500 width=64)
--   Filter: (customer_id = 100)

-- Components:
-- - Operation type (Seq Scan, Index Scan, etc.)
-- - cost=startup_cost..total_cost
-- - rows=estimated rows returned
-- - width=average row size in bytes
```

### EXPLAIN ANALYZE

Actually runs the query and shows real timing:

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 100;

-- Output includes actual timing:
-- Index Scan using idx_customer on orders  (cost=0.42..8.44 rows=5 width=64) 
--   (actual time=0.025..0.028 rows=5 loops=1)
--   Index Cond: (customer_id = 100)
-- Planning Time: 0.123 ms
-- Execution Time: 0.052 ms
```

### EXPLAIN Options

```sql
-- Detailed output
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM orders WHERE customer_id = 100;

-- Show buffer usage
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders WHERE customer_id = 100;
-- Shows:
-- - Shared blocks hit (from cache)
-- - Shared blocks read (from disk)
-- - Shared blocks written

-- All options
EXPLAIN (
    ANALYZE true,      -- Execute and show actual times
    VERBOSE true,      -- Show detailed info
    BUFFERS true,      -- Show buffer usage
    COSTS true,        -- Show cost estimates (default)
    TIMING true,       -- Show actual timing (default with ANALYZE)
    SUMMARY true,      -- Show summary stats
    FORMAT JSON        -- Output format: TEXT, JSON, XML, YAML
)
SELECT * FROM large_table WHERE condition;

-- JSON format for programmatic parsing
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM orders;
```

### Reading EXPLAIN Output

```sql
-- Example query with complex plan
EXPLAIN ANALYZE
SELECT 
    c.customer_name,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.created_at > '2023-01-01'
GROUP BY c.customer_id, c.customer_name
HAVING SUM(o.total_amount) > 1000
ORDER BY total_spent DESC
LIMIT 10;

-- Output interpretation:
-- Limit  (cost=X..Y rows=10)
--   -> Sort  (cost=X..Y rows=N)
--         Sort Key: (sum(o.total_amount)) DESC
--         -> HashAggregate  (cost=X..Y rows=N)
--               Group Key: c.customer_id
--               Filter: (sum(o.total_amount) > 1000)
--               -> Hash Left Join  (cost=X..Y rows=N)
--                     Hash Cond: (o.customer_id = c.customer_id)
--                     -> Seq Scan on orders o
--                     -> Hash
--                           -> Index Scan on customers c
--                                 Filter: (created_at > '2023-01-01')

-- Key things to look for:
-- 1. Seq Scan on large tables (consider adding index)
-- 2. High cost operations
-- 3. Large row count estimates
-- 4. Nested loops with large outer tables
-- 5. Sorts that spill to disk
```

### Common Plan Nodes

```sql
-- Sequential Scan (bad for large tables)
EXPLAIN SELECT * FROM large_table WHERE status = 'active';
-- Seq Scan on large_table  (cost=0.00..100000.00 rows=1000)

-- Index Scan (good)
EXPLAIN SELECT * FROM orders WHERE order_id = 123;
-- Index Scan using orders_pkey on orders  (cost=0.42..8.44 rows=1)

-- Index Only Scan (best - doesn't need table)
EXPLAIN SELECT customer_id FROM orders WHERE customer_id = 100;
-- Index Only Scan using idx_customer on orders  (cost=0.42..8.44 rows=5)

-- Bitmap Heap Scan (for multiple rows)
EXPLAIN SELECT * FROM orders WHERE customer_id IN (1,2,3,4,5);
-- Bitmap Heap Scan on orders
--   -> Bitmap Index Scan on idx_customer

-- Nested Loop (good for small tables)
EXPLAIN SELECT * FROM small_table a JOIN another_small b ON a.id = b.id;
-- Nested Loop
--   -> Seq Scan on small_table a
--   -> Index Scan on another_small b

-- Hash Join (good for large tables)
EXPLAIN SELECT * FROM large_table a JOIN large_table b ON a.id = b.id;
-- Hash Join
--   Hash Cond: (a.id = b.id)
--   -> Seq Scan on large_table a
--   -> Hash
--         -> Seq Scan on large_table b

-- Merge Join (for sorted data)
EXPLAIN SELECT * FROM sorted_a a JOIN sorted_b b ON a.id = b.id;
-- Merge Join
--   Merge Cond: (a.id = b.id)
--   -> Index Scan on sorted_a a
--   -> Index Scan on sorted_b b
```

## Index Optimization

### Index Selection Strategy

```sql
-- 1. Identify slow queries
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- 2. Check missing indexes
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
-- If shows "Seq Scan", consider index

-- 3. Create appropriate index
CREATE INDEX idx_orders_status ON orders(status);

-- 4. Verify improvement
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
-- Should now show "Index Scan" or "Bitmap Index Scan"
```

### Index Types and Use Cases

```sql
-- B-tree (default, most common)
CREATE INDEX idx_orders_date ON orders(order_date);
-- Use for: =, <, <=, >, >=, BETWEEN, IN, IS NULL

-- Hash (for equality only)
CREATE INDEX idx_products_code ON products USING hash(product_code);
-- Use for: = only (rarely needed, B-tree usually better)

-- GiST (for geometric, full-text search)
CREATE INDEX idx_locations ON stores USING gist(location);
CREATE INDEX idx_documents ON documents USING gist(to_tsvector('english', content));

-- GIN (for arrays, JSONB, full-text)
CREATE INDEX idx_tags ON articles USING gin(tags);
CREATE INDEX idx_metadata ON orders USING gin(metadata jsonb_path_ops);

-- BRIN (for large sequential data)
CREATE INDEX idx_logs_timestamp ON logs USING brin(created_at);
-- Use for: time-series data, append-only tables

-- Partial indexes
CREATE INDEX idx_active_customers ON customers(last_login) 
WHERE status = 'active';

-- Expression indexes
CREATE INDEX idx_lower_email ON customers(LOWER(email));

-- Multi-column indexes
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
-- Column order matters! Use most selective first
```

### Index Maintenance

```sql
-- Check index usage
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan ASC;

-- Find unused indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey';

-- Check index size
SELECT
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Rebuild bloated indexes
REINDEX INDEX idx_name;
REINDEX TABLE table_name;
-- Or concurrent (doesn't lock)
REINDEX INDEX CONCURRENTLY idx_name;

-- Drop unused indexes
DROP INDEX IF EXISTS idx_unused;
```

## Query Rewriting

### Inefficient vs Efficient Queries

```sql
-- BAD: Using OR with different columns
SELECT * FROM orders 
WHERE customer_id = 100 OR status = 'pending';
-- Can't use indexes efficiently

-- GOOD: Rewrite using UNION
SELECT * FROM orders WHERE customer_id = 100
UNION
SELECT * FROM orders WHERE status = 'pending';

-- BAD: Negation prevents index usage
SELECT * FROM products WHERE name NOT LIKE 'A%';

-- GOOD: Use positive condition if possible
SELECT * FROM products WHERE name >= 'B' AND name < 'z';

-- BAD: Function on indexed column
SELECT * FROM customers WHERE LOWER(email) = 'john@example.com';

-- GOOD: Use expression index or compare directly
CREATE INDEX idx_lower_email ON customers(LOWER(email));
-- Or store lowercase version

-- BAD: Implicit type conversion
SELECT * FROM orders WHERE order_id = '123';  -- order_id is INTEGER

-- GOOD: Explicit type
SELECT * FROM orders WHERE order_id = 123;

-- BAD: SELECT *
SELECT * FROM large_table WHERE condition;

-- GOOD: Select only needed columns
SELECT id, name, created_at FROM large_table WHERE condition;
```

### Avoiding Common Pitfalls

```sql
-- BAD: Multiple OR conditions
SELECT * FROM orders 
WHERE status = 'pending' OR status = 'processing' OR status = 'shipped';

-- GOOD: Use IN
SELECT * FROM orders 
WHERE status IN ('pending', 'processing', 'shipped');

-- BAD: Correlated subquery in SELECT
SELECT 
    c.customer_name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id) as order_count
FROM customers c;

-- GOOD: Use JOIN or window function
SELECT 
    c.customer_name,
    COUNT(o.order_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;

-- BAD: NOT IN with nullable column
SELECT * FROM customers 
WHERE customer_id NOT IN (SELECT customer_id FROM orders);
-- Returns no rows if any order has NULL customer_id!

-- GOOD: Use NOT EXISTS
SELECT * FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);

-- Or use LEFT JOIN with NULL check
SELECT c.* FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.customer_id IS NULL;
```

## Join Optimization

### Join Order Matters

```sql
-- PostgreSQL automatically reorders joins, but you can help

-- BAD: Large table first
SELECT * FROM large_table l
JOIN small_table s ON l.id = s.id
WHERE s.category = 'specific';

-- GOOD: Filter early, small table first
SELECT * FROM small_table s
JOIN large_table l ON s.id = l.id
WHERE s.category = 'specific';

-- Use CTEs to materialize filtered results
WITH filtered_small AS (
    SELECT * FROM small_table WHERE category = 'specific'
)
SELECT * FROM filtered_small s
JOIN large_table l ON s.id = l.id;
```

### Join Methods

```sql
-- Nested Loop Join (small tables)
-- For each row in outer, scan inner table
-- Good when: Small tables, indexed join column
SET enable_hashjoin = off;
SET enable_mergejoin = off;
EXPLAIN SELECT * FROM small_a a JOIN small_b b ON a.id = b.id;

-- Hash Join (large tables)
-- Build hash table from smaller side, probe from larger
-- Good when: Large tables, no index, lots of memory
SET enable_nestloop = off;
SET enable_mergejoin = off;
EXPLAIN SELECT * FROM large_a a JOIN large_b b ON a.id = b.id;

-- Merge Join (sorted data)
-- Both tables sorted on join key, merge sorted streams
-- Good when: Both sides sorted/indexed on join column
SET enable_nestloop = off;
SET enable_hashjoin = off;
EXPLAIN SELECT * FROM sorted_a a JOIN sorted_b b ON a.id = b.id;

-- Reset to defaults
RESET enable_nestloop;
RESET enable_hashjoin;
RESET enable_mergejoin;
```

### Join Hints (Indirect)

```sql
-- Increase work_mem for better hash joins
SET work_mem = '256MB';

-- Adjust join cost parameters
SET random_page_cost = 1.1;  -- For SSD storage
SET cpu_tuple_cost = 0.01;

-- Force planner reconsideration
SET join_collapse_limit = 8;  -- Default, increase for complex queries
SET from_collapse_limit = 8;

-- Materialize subqueries
WITH important_data AS MATERIALIZED (
    SELECT expensive_calculation FROM large_table
)
SELECT * FROM important_data JOIN other_table;
```

## Subquery Optimization

### Subquery vs JOIN

```sql
-- BAD: Correlated subquery
SELECT customer_id, customer_name,
    (SELECT COUNT(*) FROM orders o WHERE o.customer_id = c.customer_id)
FROM customers c;

-- GOOD: JOIN with GROUP BY
SELECT c.customer_id, c.customer_name, COUNT(o.order_id)
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;

-- GOOD: Window function
SELECT DISTINCT ON (c.customer_id)
    c.customer_id,
    c.customer_name,
    COUNT(*) OVER (PARTITION BY c.customer_id) as order_count
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;
```

### EXISTS vs IN

```sql
-- For existence checks, EXISTS is often faster
-- BAD: IN with subquery
SELECT * FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE total_amount > 1000
);

-- GOOD: EXISTS
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.total_amount > 1000
);

-- Note: PostgreSQL often optimizes these similarly,
-- but EXISTS is semantically clearer for existence checks
```

### Common Table Expressions (CTEs)

```sql
-- CTEs can help or hurt performance

-- Optimization fence (materialized by default in PostgreSQL < 12)
WITH stats AS (
    SELECT department, AVG(salary) as avg_sal
    FROM employees
    GROUP BY department
)
SELECT * FROM stats WHERE avg_sal > 50000;

-- Force inline (PostgreSQL 12+)
WITH stats AS NOT MATERIALIZED (
    SELECT department, AVG(salary) as avg_sal
    FROM employees
    GROUP BY department
)
SELECT * FROM stats WHERE avg_sal > 50000;

-- Force materialization (PostgreSQL 12+)
WITH stats AS MATERIALIZED (
    SELECT expensive_calculation() as result
    FROM large_table
)
SELECT * FROM stats s1
JOIN stats s2 ON s1.result = s2.result;  -- Computed once, used twice
```

## Statistics and Planner

### Table Statistics

```sql
-- Update statistics (crucial for good plans)
ANALYZE;                    -- All tables
ANALYZE table_name;         -- Specific table
ANALYZE table_name (column1, column2);  -- Specific columns

-- Check when last analyzed
SELECT 
    schemaname,
    tablename,
    last_analyze,
    last_autoanalyze,
    n_live_tup,
    n_dead_tup
FROM pg_stat_user_tables
ORDER BY last_analyze NULLS FIRST;

-- Auto-vacuum and analyze settings
ALTER TABLE large_table SET (
    autovacuum_analyze_threshold = 50,
    autovacuum_analyze_scale_factor = 0.1
);
```

### Statistics Targets

```sql
-- Increase statistics detail for selective columns
ALTER TABLE orders ALTER COLUMN status SET STATISTICS 1000;
-- Default is 100, max is 10000
-- More statistics = better plans, but slower ANALYZE

-- Check column statistics
SELECT 
    tablename,
    attname,
    n_distinct,
    correlation
FROM pg_stats
WHERE tablename = 'orders';

-- View histogram bounds
SELECT 
    attname,
    histogram_bounds
FROM pg_stats
WHERE tablename = 'orders' AND attname = 'order_date';
```

### Planner Configuration

```sql
-- Cost constants (tune for your hardware)
SET seq_page_cost = 1.0;        -- Sequential page read cost
SET random_page_cost = 4.0;     -- Random page read (SSD: 1.1-1.5)
SET cpu_tuple_cost = 0.01;      -- CPU cost per row
SET cpu_index_tuple_cost = 0.005;  -- CPU cost per index entry
SET cpu_operator_cost = 0.0025;  -- CPU cost per operator

-- For SSD storage
ALTER DATABASE mydb SET random_page_cost = 1.1;

-- Memory settings
SET work_mem = '64MB';          -- Per operation (sort, hash)
SET maintenance_work_mem = '512MB';  -- For VACUUM, CREATE INDEX
SET effective_cache_size = '4GB';  -- OS + PostgreSQL cache

-- Parallel query settings
SET max_parallel_workers_per_gather = 4;
SET parallel_setup_cost = 1000;
SET parallel_tuple_cost = 0.1;
```

## Configuration Tuning

### Memory Configuration

```sql
-- postgresql.conf settings

-- Shared buffers (25% of RAM, max 8GB on dedicated server)
shared_buffers = 2GB

-- Work memory (per operation, be conservative)
work_mem = 64MB

-- Maintenance operations
maintenance_work_mem = 512MB

-- Effective cache (OS + PostgreSQL, ~75% of RAM)
effective_cache_size = 8GB

-- Check current settings
SHOW shared_buffers;
SHOW work_mem;
SHOW maintenance_work_mem;
SHOW effective_cache_size;
```

### Query Timeout Settings

```sql
-- Prevent runaway queries
SET statement_timeout = '5min';
SET lock_timeout = '10s';
SET idle_in_transaction_session_timeout = '1min';

-- Per-user limits
ALTER ROLE app_user SET statement_timeout = '30s';

-- Per-database limits
ALTER DATABASE app_db SET statement_timeout = '1min';
```

### Monitoring Queries

```sql
-- Install pg_stat_statements extension
CREATE EXTENSION pg_stat_statements;

-- View slowest queries
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time,
    rows
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Reset statistics
SELECT pg_stat_statements_reset();

-- View currently running queries
SELECT 
    pid,
    now() - query_start as duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- Kill long-running query
SELECT pg_cancel_backend(pid);  -- Graceful
SELECT pg_terminate_backend(pid);  -- Forceful
```

## Best Practices

1. **Always ANALYZE after bulk data changes**
2. **Create indexes on foreign keys**
3. **Use covering indexes when possible**
4. **Avoid SELECT *** - specify columns
5. **Use connection pooling** to reduce overhead
6. **Monitor query performance** regularly
7. **Keep PostgreSQL updated** for planner improvements
8. **Set appropriate statistics targets** for selective columns
9. **Use EXPLAIN ANALYZE** before optimizing
10. **Test with production-like data volumes**

## Common Optimization Patterns

### Pagination

```sql
-- BAD: Large OFFSET
SELECT * FROM orders 
ORDER BY order_date 
LIMIT 10 OFFSET 100000;  -- Slow!

-- GOOD: Keyset pagination
SELECT * FROM orders 
WHERE order_date < :last_seen_date
   OR (order_date = :last_seen_date AND order_id < :last_seen_id)
ORDER BY order_date DESC, order_id DESC
LIMIT 10;
```

### Counting Rows

```sql
-- BAD: COUNT(*) on large table
SELECT COUNT(*) FROM huge_table;  -- Can be slow

-- GOOD: Estimate for approximate count
SELECT reltuples::bigint AS estimate
FROM pg_class
WHERE relname = 'huge_table';

-- GOOD: Cache counts
CREATE MATERIALIZED VIEW table_counts AS
SELECT 'huge_table' as table_name, COUNT(*) as row_count
FROM huge_table;

REFRESH MATERIALIZED VIEW CONCURRENTLY table_counts;
```

### Distinct Values

```sql
-- BAD: DISTINCT on large result set
SELECT DISTINCT customer_id FROM orders;

-- GOOD: Use GROUP BY
SELECT customer_id FROM orders GROUP BY customer_id;

-- BETTER: Use an index
CREATE INDEX idx_orders_customer ON orders(customer_id);
SELECT customer_id FROM orders GROUP BY customer_id;
```

## Summary

Query optimization in PostgreSQL involves:
- **Understanding EXPLAIN output** to identify bottlenecks
- **Creating appropriate indexes** for query patterns
- **Rewriting queries** for better performance
- **Maintaining statistics** for accurate planning
- **Tuning configuration** for your workload
- **Monitoring performance** continuously

Master these techniques to build high-performance applications.

## Next Steps

- Learn about [EXPLAIN and Query Plans](./21-explain-and-query-plans.md) in detail
- Explore [Index Optimization](./22-index-optimization.md)
- Study [Partitioning](./23-partitioning.md) for large tables
- Practice [Monitoring and Logging](./38-monitoring-and-logging.md)
