# EXPLAIN and Query Plans

## Overview

Understanding query execution plans is essential for database performance optimization. PostgreSQL's EXPLAIN command reveals how the query planner will execute (or has executed) a query, showing operations, costs, and actual performance metrics.

## Table of Contents
- [EXPLAIN Basics](#explain-basics)
- [Understanding Plan Nodes](#understanding-plan-nodes)
- [Cost Model](#cost-model)
- [Reading Complex Plans](#reading-complex-plans)
- [EXPLAIN Options](#explain-options)
- [Analyzing Performance](#analyzing-performance)
- [Common Patterns](#common-patterns)
- [Troubleshooting Plans](#troubleshooting-plans)

## EXPLAIN Basics

### Basic EXPLAIN Syntax

```sql
-- Show estimated execution plan (doesn't run query)
EXPLAIN
SELECT * FROM orders WHERE customer_id = 100;

-- Output:
-- Index Scan using idx_customer on orders  (cost=0.42..8.44 rows=5 width=64)
--   Index Cond: (customer_id = 100)

-- Components explained:
-- - Operation: Index Scan
-- - Index used: idx_customer
-- - Table: orders
-- - cost=0.42..8.44 (startup cost .. total cost)
-- - rows=5 (estimated rows returned)
-- - width=64 (average row size in bytes)
```

### EXPLAIN ANALYZE

Actually executes the query:

```sql
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 100;

-- Output includes actual execution metrics:
-- Index Scan using idx_customer on orders  
--   (cost=0.42..8.44 rows=5 width=64) 
--   (actual time=0.025..0.028 rows=5 loops=1)
--   Index Cond: (customer_id = 100)
-- Planning Time: 0.123 ms
-- Execution Time: 0.052 ms

-- Key additions:
-- - actual time=0.025..0.028 (actual startup..total time in ms)
-- - rows=5 (actual rows returned)
-- - loops=1 (how many times node executed)
-- - Planning Time: time spent planning
-- - Execution Time: actual execution time
```

### Understanding Output Structure

```sql
-- Hierarchical structure (indentation shows nesting)
EXPLAIN ANALYZE
SELECT c.customer_name, COUNT(o.order_id)
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name;

-- Output structure:
-- HashAggregate  (outermost operation)
--   -> Hash Join  (nested under aggregate)
--        Hash Cond: (join condition)
--        -> Seq Scan on orders o  (left side of join)
--        -> Hash  (right side - build hash table)
--             -> Seq Scan on customers c
--
-- Read bottom-up: customers scanned, hash built, orders scanned, joined, aggregated
```

## Understanding Plan Nodes

### Scan Operations

```sql
-- 1. Sequential Scan (full table scan)
EXPLAIN ANALYZE
SELECT * FROM large_table;

-- Seq Scan on large_table  (cost=0.00..10000.00 rows=100000 width=100)
--   (actual time=0.010..45.123 rows=100000 loops=1)
-- When: No index available, or small table, or fetching most rows
-- Performance: O(n) - reads entire table

-- 2. Index Scan (uses index to find rows)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE order_id = 123;

-- Index Scan using orders_pkey on orders  (cost=0.42..8.44 rows=1 width=64)
--   (actual time=0.025..0.026 rows=1 loops=1)
--   Index Cond: (order_id = 123)
-- When: Selective query, index available
-- Performance: O(log n) - uses B-tree index

-- 3. Index Only Scan (reads only from index)
CREATE INDEX idx_customer_date ON orders(customer_id, order_date);

EXPLAIN ANALYZE
SELECT customer_id, order_date FROM orders WHERE customer_id = 100;

-- Index Only Scan using idx_customer_date on orders
--   (cost=0.42..4.44 rows=5 width=12)
--   (actual time=0.015..0.018 rows=5 loops=1)
--   Index Cond: (customer_id = 100)
--   Heap Fetches: 0  -- No table access needed!
-- When: All needed columns in index, visibility map current
-- Performance: Fastest - no table access

-- 4. Bitmap Index Scan (for multiple row retrieval)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id IN (1, 2, 3, 4, 5);

-- Bitmap Heap Scan on orders  (cost=20.42..100.00 rows=25 width=64)
--   (actual time=0.123..0.456 rows=25 loops=1)
--   Recheck Cond: (customer_id = ANY('{1,2,3,4,5}'::integer[]))
--   Heap Blocks: exact=20
--   -> Bitmap Index Scan on idx_customer  (cost=0.00..20.41 rows=25 width=0)
--         (actual time=0.089..0.089 rows=25 loops=1)
--         Index Cond: (customer_id = ANY('{1,2,3,4,5}'::integer[]))
-- When: Fetching multiple scattered rows
-- Process: 1) Build bitmap of matching rows, 2) Sort by physical location, 3) Read table

-- 5. TID Scan (by row identifier)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE ctid = '(0,1)';

-- Tid Scan on orders  (cost=0.00..4.01 rows=1 width=64)
--   TID Cond: (ctid = '(0,1)'::tid)
-- When: Direct row access by physical location (rare in application code)
```

### Join Operations

```sql
-- 1. Nested Loop Join
EXPLAIN ANALYZE
SELECT * FROM small_customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE c.country = 'USA';

-- Nested Loop  (cost=0.42..100.00 rows=50 width=128)
--   (actual time=0.050..1.234 rows=50 loops=1)
--   -> Index Scan on small_customers c  (cost=0.42..20.00 rows=10 width=64)
--         Filter: (country = 'USA'::text)
--   -> Index Scan on orders o  (cost=0.42..7.99 rows=5 width=64)
--         Index Cond: (customer_id = c.customer_id)
-- When: Small outer table, indexed inner table
-- Algorithm: For each row in outer, scan inner table
-- Cost: O(n * m) but efficient with indexes

-- 2. Hash Join
EXPLAIN ANALYZE
SELECT * FROM large_customers c
JOIN large_orders o ON c.customer_id = o.customer_id;

-- Hash Join  (cost=1000.00..10000.00 rows=10000 width=128)
--   (actual time=10.234..50.456 rows=10000 loops=1)
--   Hash Cond: (o.customer_id = c.customer_id)
--   -> Seq Scan on large_orders o  (cost=0.00..5000.00 rows=100000 width=64)
--   -> Hash  (cost=500.00..500.00 rows=10000 width=64)
--         (actual time=9.876..9.876 rows=10000 loops=1)
--         Buckets: 16384  Batches: 1  Memory Usage: 1234kB
--         -> Seq Scan on large_customers c  (cost=0.00..500.00 rows=10000 width=64)
-- When: Large tables, no useful indexes
-- Algorithm: 1) Build hash table from smaller side, 2) Probe with larger side
-- Cost: O(n + m) - linear in total rows
-- Memory: Needs work_mem for hash table

-- 3. Merge Join
CREATE INDEX idx_customers_id ON customers(customer_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);

EXPLAIN ANALYZE
SELECT * FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Merge Join  (cost=0.84..5000.00 rows=10000 width=128)
--   (actual time=0.050..25.678 rows=10000 loops=1)
--   Merge Cond: (c.customer_id = o.customer_id)
--   -> Index Scan on customers c  (cost=0.42..2000.00 rows=10000 width=64)
--   -> Index Scan on orders o  (cost=0.42..2500.00 rows=20000 width=64)
-- When: Both sides sorted on join key (or can be sorted cheaply)
-- Algorithm: Merge two sorted streams
-- Cost: O(n + m) - but requires sorted input
```

### Aggregate Operations

```sql
-- 1. HashAggregate
EXPLAIN ANALYZE
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;

-- HashAggregate  (cost=1000.00..1010.00 rows=10 width=16)
--   (actual time=15.234..15.245 rows=10 loops=1)
--   Group Key: department
--   Batches: 1  Memory Usage: 24kB
--   -> Seq Scan on employees  (cost=0.00..500.00 rows=10000 width=12)
-- When: GROUP BY with unsorted input, fits in work_mem
-- Memory: Needs work_mem for hash table

-- 2. GroupAggregate
CREATE INDEX idx_employees_dept ON employees(department);

EXPLAIN ANALYZE
SELECT department, COUNT(*), AVG(salary)
FROM employees
GROUP BY department;

-- GroupAggregate  (cost=0.42..1500.00 rows=10 width=16)
--   (actual time=0.050..12.345 rows=10 loops=1)
--   Group Key: department
--   -> Index Scan on employees using idx_employees_dept
--        (cost=0.42..1000.00 rows=10000 width=12)
-- When: Input already sorted on group key
-- More memory efficient than HashAggregate
```

### Sort Operations

```sql
-- Sort in memory (fast)
EXPLAIN ANALYZE
SELECT * FROM small_table ORDER BY created_at DESC LIMIT 10;

-- Limit  (cost=100.00..105.00 rows=10 width=64)
--   -> Sort  (cost=100.00..125.00 rows=1000 width=64)
--         (actual time=1.234..1.256 rows=10 loops=1)
--         Sort Key: created_at DESC
--         Sort Method: top-N heapsort  Memory: 25kB  -- In memory!
--         -> Seq Scan on small_table

-- Sort on disk (slow)
EXPLAIN ANALYZE
SELECT * FROM large_table ORDER BY created_at;

-- Sort  (cost=100000.00..125000.00 rows=100000 width=64)
--   (actual time=500.234..750.456 rows=100000 loops=1)
--   Sort Key: created_at
--   Sort Method: external merge  Disk: 12345kB  -- Spilled to disk!
--   -> Seq Scan on large_table
-- Solution: Increase work_mem or use index
```

## Cost Model

### Understanding Costs

```sql
-- Cost formula:
-- Total cost = startup_cost + (cpu_cost + io_cost) * rows

-- Cost parameters (from postgresql.conf):
-- seq_page_cost = 1.0        -- Cost to read sequential page
-- random_page_cost = 4.0     -- Cost to read random page
-- cpu_tuple_cost = 0.01      -- Cost to process one row
-- cpu_index_tuple_cost = 0.005  -- Cost to process index entry
-- cpu_operator_cost = 0.0025    -- Cost to process operator/function

-- Example cost calculation:
EXPLAIN
SELECT * FROM orders WHERE order_id = 123;

-- Index Scan using orders_pkey on orders  (cost=0.42..8.44 rows=1 width=64)
-- Breakdown:
-- 0.42 = startup cost (descend B-tree)
-- 8.44 = total cost (startup + fetch page + process row)
-- Difference: 8.44 - 0.42 = 8.02 = cost to fetch and return row
```

### Cost vs Actual Time

```sql
-- Cost is relative (unitless), actual time is milliseconds
EXPLAIN ANALYZE
SELECT * FROM orders WHERE customer_id = 100;

-- cost=0.42..8.44  -- Estimated cost (used by planner to choose plan)
-- actual time=0.025..0.028  -- Real milliseconds
-- rows=5 (estimated) vs rows=5 (actual)  -- Compare for accuracy

-- Large discrepancy indicates:
-- 1. Outdated statistics (run ANALYZE)
-- 2. Selectivity estimation issues
-- 3. Data skew not captured in statistics
```

## Reading Complex Plans

### Multi-Table Join Example

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    c.customer_name,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.quantity * p.price as line_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE c.country = 'USA'
  AND o.order_date >= '2024-01-01'
  AND p.category = 'Electronics'
ORDER BY o.order_date DESC
LIMIT 100;

-- Complex plan output (read from bottom to top, inside to outside):
/*
Limit  (cost=5000.00..5002.50 rows=100)
  (actual time=25.123..25.456 rows=100 loops=1)
  Buffers: shared hit=234 read=45
  -> Sort  (cost=5000.00..5500.00 rows=10000)
      (actual time=25.100..25.200 rows=100 loops=1)
      Sort Key: o.order_date DESC
      Sort Method: top-N heapsort  Memory: 50kB
      Buffers: shared hit=234 read=45
      -> Hash Join  (cost=3000.00..4500.00 rows=10000)
          (actual time=10.234..20.567 rows=10000 loops=1)
          Hash Cond: (oi.product_id = p.product_id)
          Buffers: shared hit=234 read=45
          -> Hash Join  (cost=2000.00..3000.00 rows=20000)
              (actual time=5.123..15.456 rows=20000 loops=1)
              Hash Cond: (oi.order_id = o.order_id)
              Buffers: shared hit=189 read=23
              -> Seq Scan on order_items oi
                  (cost=0.00..500.00 rows=50000)
                  (actual time=0.010..5.678 rows=50000 loops=1)
                  Buffers: shared hit=123
              -> Hash  (cost=1500.00..1500.00 rows=5000)
                  (actual time=5.000..5.000 rows=5000 loops=1)
                  Buckets: 8192  Batches: 1  Memory Usage: 789kB
                  Buffers: shared hit=66 read=23
                  -> Hash Join  (cost=500.00..1500.00 rows=5000)
                      (actual time=1.234..4.567 rows=5000 loops=1)
                      Hash Cond: (o.customer_id = c.customer_id)
                      Buffers: shared hit=66 read=23
                      -> Index Scan on orders o using idx_order_date
                          (cost=0.42..800.00 rows=10000)
                          (actual time=0.025..2.345 rows=10000 loops=1)
                          Index Cond: (order_date >= '2024-01-01')
                          Buffers: shared hit=45 read=12
                      -> Hash  (cost=400.00..400.00 rows=1000)
                          (actual time=1.123..1.123 rows=1000 loops=1)
                          Buckets: 1024  Batches: 1  Memory Usage: 123kB
                          Buffers: shared hit=21 read=11
                          -> Bitmap Heap Scan on customers c
                              (cost=20.00..400.00 rows=1000)
                              (actual time=0.234..0.987 rows=1000 loops=1)
                              Recheck Cond: (country = 'USA')
                              Heap Blocks: exact=32
                              Buffers: shared hit=21 read=11
                              -> Bitmap Index Scan on idx_country
                                  (cost=0.00..19.75 rows=1000)
                                  (actual time=0.123..0.123 rows=1000 loops=1)
                                  Index Cond: (country = 'USA')
                                  Buffers: shared read=11
          -> Hash  (cost=800.00..800.00 rows=2000)
              (actual time=4.567..4.567 rows=2000 loops=1)
              Buckets: 2048  Batches: 1  Memory Usage: 234kB
              Buffers: shared hit=45 read=22
              -> Bitmap Heap Scan on products p
                  (cost=50.00..800.00 rows=2000)
                  (actual time=0.456..3.789 rows=2000 loops=1)
                  Recheck Cond: (category = 'Electronics')
                  Heap Blocks: exact=67
                  Buffers: shared hit=45 read=22
                  -> Bitmap Index Scan on idx_category
                      (cost=0.00..49.50 rows=2000)
                      (actual time=0.345..0.345 rows=2000 loops=1)
                      Index Cond: (category = 'Electronics')
                      Buffers: shared read=22
Planning Time: 2.345 ms
Execution Time: 25.678 ms
*/

-- Reading strategy:
-- 1. Start at bottom: customers filtered by country
-- 2. Build hash from customers
-- 3. orders filtered by date, joined with customers
-- 4. Build hash from customer+orders
-- 5. Join with order_items
-- 6. Build hash from results
-- 7. Join with products filtered by category
-- 8. Sort results
-- 9. Return top 100 rows
```

## EXPLAIN Options

### All Available Options

```sql
-- Basic options
EXPLAIN (ANALYZE true)          -- Execute and show actual stats
SELECT * FROM orders;

EXPLAIN (VERBOSE true)          -- Show detailed column info
SELECT * FROM orders;

EXPLAIN (COSTS false)           -- Hide cost estimates
SELECT * FROM orders;

EXPLAIN (BUFFERS true)          -- Show buffer usage (with ANALYZE)
SELECT * FROM orders;

EXPLAIN (TIMING false)          -- Skip timing (faster ANALYZE)
SELECT * FROM orders;

EXPLAIN (SUMMARY true)          -- Show summary statistics
SELECT * FROM orders;

EXPLAIN (FORMAT JSON)           -- Output format
SELECT * FROM orders;

-- Combined options
EXPLAIN (
    ANALYZE true,
    VERBOSE true,
    BUFFERS true,
    COSTS true,
    TIMING true,
    SUMMARY true,
    FORMAT TEXT
)
SELECT * FROM orders WHERE customer_id = 100;
```

### Output Formats

```sql
-- TEXT format (default, human-readable)
EXPLAIN (FORMAT TEXT)
SELECT * FROM orders;

-- JSON format (machine-parseable)
EXPLAIN (ANALYZE, FORMAT JSON)
SELECT * FROM orders;
-- Returns: [{"Plan": {...}, "Planning Time": ..., "Execution Time": ...}]

-- XML format
EXPLAIN (FORMAT XML)
SELECT * FROM orders;

-- YAML format
EXPLAIN (FORMAT YAML)
SELECT * FROM orders;
```

### Buffer Statistics

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM large_table WHERE status = 'active';

-- Output includes:
-- Buffers: shared hit=1234 read=567 dirtied=0 written=0
--
-- shared hit: Pages found in shared buffer cache (fast - RAM)
-- shared read: Pages read from disk (slow)
-- shared dirtied: Pages modified
-- shared written: Pages written to disk
-- temp read/written: Temporary file I/O (sorts, hashes spilling to disk)
--
-- Good: High hit ratio (hit / (hit + read))
-- Bad: High read count or temp file usage
```

## Analyzing Performance

### Identifying Bottlenecks

```sql
-- Look for these issues:

-- 1. Sequential scans on large tables
EXPLAIN ANALYZE
SELECT * FROM large_table WHERE rarely_used_column = 'value';
-- Seq Scan on large_table  (cost=0.00..100000.00 rows=1)
-- Solution: Add index on rarely_used_column

-- 2. Actual rows >> estimated rows (bad statistics)
EXPLAIN ANALYZE
SELECT * FROM orders WHERE status = 'pending';
-- (cost=... rows=10 width=64)
-- (actual time=... rows=10000 loops=1)  -- 1000x more than estimated!
-- Solution: ANALYZE orders; or ALTER TABLE orders ALTER COLUMN status SET STATISTICS 1000;

-- 3. Nested loop with large outer table
EXPLAIN ANALYZE
SELECT * FROM huge_table h
JOIN small_table s ON h.id = s.id;
-- Nested Loop (actual time=... rows=... loops=100000)  -- Too many loops!
-- Solution: Rewrite to use hash join, or ensure index on join columns

-- 4. Sort spilling to disk
EXPLAIN ANALYZE
SELECT * FROM large_table ORDER BY created_at;
-- Sort Method: external merge  Disk: 123456kB  -- Using disk!
-- Solution: Increase work_mem, or use index for sorting

-- 5. Hash batches > 1 (memory exhausted)
EXPLAIN ANALYZE
SELECT * FROM large_a a JOIN large_b b ON a.id = b.id;
-- Hash  Buckets: 16384  Batches: 4  Memory Usage: 50000kB  -- Multiple batches!
-- Solution: Increase work_mem

-- 6. High buffer reads (cache misses)
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM orders;
-- Buffers: shared hit=10 read=10000  -- Low hit ratio!
-- Solution: Increase shared_buffers, or query during high-traffic period
```

### Comparing Plans

```sql
-- Test different approaches

-- Approach 1: Subquery
EXPLAIN ANALYZE
SELECT * FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders WHERE total_amount > 1000
);

-- Approach 2: JOIN
EXPLAIN ANALYZE
SELECT DISTINCT c.*
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
WHERE o.total_amount > 1000;

-- Approach 3: EXISTS
EXPLAIN ANALYZE
SELECT * FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.customer_id = c.customer_id 
    AND o.total_amount > 1000
);

-- Compare execution times and choose fastest
```

## Common Patterns

### Pattern Recognition

```sql
-- Good patterns:
-- ✓ Index Scan or Index Only Scan on large tables
-- ✓ Hash Join for large table joins
-- ✓ Top-N heapsort in memory
-- ✓ High buffer cache hit ratio
-- ✓ Actual rows ≈ estimated rows

-- Bad patterns:
-- ✗ Seq Scan on tables with millions of rows (when filtering)
-- ✗ Nested Loop with large outer table
-- ✗ External merge sort (spilling to disk)
-- ✗ Multiple hash batches
-- ✗ Actual rows >> estimated rows (outdated statistics)
-- ✗ Low buffer cache hit ratio
```

## Troubleshooting Plans

### Plan Not Using Index

```sql
-- Index exists but not used
CREATE INDEX idx_orders_status ON orders(status);

EXPLAIN
SELECT * FROM orders WHERE status = 'pending';
-- Still shows Seq Scan!

-- Possible reasons:

-- 1. Outdated statistics
ANALYZE orders;

-- 2. Too many matching rows (index not selective)
-- If >5-10% of rows match, seq scan might be faster
SELECT status, COUNT(*) FROM orders GROUP BY status;

-- 3. Function on indexed column
SELECT * FROM orders WHERE UPPER(status) = 'PENDING';  -- Can't use index
-- Solution: CREATE INDEX idx_upper_status ON orders(UPPER(status));

-- 4. Implicit type conversion
SELECT * FROM orders WHERE order_id = '123';  -- order_id is INTEGER
-- Solution: Use correct type: WHERE order_id = 123

-- 5. OR conditions on different columns
SELECT * FROM orders WHERE status = 'pending' OR customer_id = 100;
-- Solution: Use UNION or separate queries

-- 6. NOT, <>, != operators
SELECT * FROM orders WHERE status != 'completed';
-- Solution: Use IN for positive conditions if possible

-- 7. Cost settings favor seq scan
SET random_page_cost = 1.1;  -- For SSD storage
SET effective_cache_size = '8GB';  -- Adjust for available memory
```

### Forcing Plan Changes (Testing Only)

```sql
-- Disable scan types (for testing only, not production!)
SET enable_seqscan = off;
SET enable_indexscan = off;
SET enable_indexonlyscan = off;
SET enable_bitmapscan = off;

-- Disable join types
SET enable_nestloop = off;
SET enable_hashjoin = off;
SET enable_mergejoin = off;

-- Disable sort
SET enable_sort = off;

-- Reset to defaults
RESET enable_seqscan;
RESET ALL;
```

## Best Practices

1. **Always use EXPLAIN ANALYZE** for accurate performance data
2. **Include BUFFERS** to identify I/O bottlenecks
3. **Run ANALYZE** regularly to keep statistics current
4. **Compare estimated vs actual rows** to validate statistics
5. **Test with production-like data volumes**
6. **Focus on expensive operations first** (highest cost or time)
7. **Document query plans** for complex queries
8. **Use pg_stat_statements** to find slow queries automatically
9. **Baseline before optimizing** to measure improvement
10. **Consider query rewriting** before adding indexes

## Summary

EXPLAIN and query plans provide:
- **Visibility** into query execution strategy
- **Performance metrics** (estimated and actual)
- **Resource usage** (memory, I/O, CPU)
- **Optimization opportunities** through pattern recognition
- **Validation** of index usage and statistics accuracy

Master EXPLAIN to understand and optimize PostgreSQL query performance.

## Next Steps

- Learn about [Query Optimization](./20-query-optimization.md) techniques
- Explore [Index Optimization](./22-index-optimization.md) strategies
- Study [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [Performance Tuning](./34-configuration-and-tuning.md)
