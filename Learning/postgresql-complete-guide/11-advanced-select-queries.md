# Advanced SELECT Queries

## Overview

Advanced SELECT queries in PostgreSQL allow you to perform complex data retrieval operations including DISTINCT operations, LIMIT/OFFSET pagination, UNION/INTERSECT/EXCEPT set operations, CASE expressions, and pattern matching. These techniques are essential for real-world applications.

## Table of Contents
- [DISTINCT and DISTINCT ON](#distinct-and-distinct-on)
- [LIMIT and OFFSET](#limit-and-offset)
- [Set Operations](#set-operations)
- [CASE Expressions](#case-expressions)
- [Pattern Matching](#pattern-matching)
- [Array Operations in Queries](#array-operations)
- [JSON Queries](#json-queries)
- [Lateral Joins](#lateral-joins)

## DISTINCT and DISTINCT ON

### Basic DISTINCT

Remove duplicate rows from result sets:

```sql
-- Remove duplicate values
SELECT DISTINCT department 
FROM employees;

-- DISTINCT on multiple columns
SELECT DISTINCT department, job_title 
FROM employees;

-- Count distinct values
SELECT COUNT(DISTINCT department) as dept_count 
FROM employees;
```

### DISTINCT ON

PostgreSQL-specific feature to get first row per group:

```sql
-- Get most recent order per customer
SELECT DISTINCT ON (customer_id) 
    customer_id, 
    order_date, 
    total_amount
FROM orders
ORDER BY customer_id, order_date DESC;

-- Get highest paid employee per department
SELECT DISTINCT ON (department) 
    department, 
    employee_name, 
    salary
FROM employees
ORDER BY department, salary DESC;

-- Multiple DISTINCT ON columns
SELECT DISTINCT ON (year, month) 
    year, 
    month, 
    product_id, 
    sales
FROM monthly_sales
ORDER BY year, month, sales DESC;
```

**Important**: DISTINCT ON expressions must match leftmost ORDER BY expressions.

## LIMIT and OFFSET

### Basic Pagination

```sql
-- Get first 10 rows
SELECT * FROM products 
ORDER BY product_id 
LIMIT 10;

-- Skip first 10, get next 10 (page 2)
SELECT * FROM products 
ORDER BY product_id 
LIMIT 10 OFFSET 10;

-- Using variables for dynamic pagination
SELECT * FROM products 
ORDER BY product_id 
LIMIT :page_size OFFSET (:page_number - 1) * :page_size;
```

### Performance Considerations

```sql
-- BAD: Large OFFSET is slow
SELECT * FROM orders 
ORDER BY order_date 
LIMIT 10 OFFSET 1000000;  -- Scans 1M+ rows!

-- GOOD: Keyset pagination (cursor-based)
SELECT * FROM orders 
WHERE order_id > :last_seen_id 
ORDER BY order_id 
LIMIT 10;

-- For timestamp-based pagination
SELECT * FROM orders 
WHERE order_date > :last_seen_date 
   OR (order_date = :last_seen_date AND order_id > :last_seen_id)
ORDER BY order_date, order_id 
LIMIT 10;
```

### FETCH Clause (SQL Standard)

```sql
-- Standard SQL syntax (same as LIMIT)
SELECT * FROM products 
ORDER BY price 
FETCH FIRST 10 ROWS ONLY;

-- With OFFSET
SELECT * FROM products 
ORDER BY price 
OFFSET 5 ROWS 
FETCH NEXT 10 ROWS ONLY;

-- With ties (includes tied values)
SELECT * FROM products 
ORDER BY price 
FETCH FIRST 10 ROWS WITH TIES;
```

## Set Operations

### UNION

Combine results from multiple queries:

```sql
-- UNION removes duplicates
SELECT product_id, product_name FROM products_2023
UNION
SELECT product_id, product_name FROM products_2024;

-- UNION ALL keeps duplicates (faster)
SELECT customer_id, order_date FROM online_orders
UNION ALL
SELECT customer_id, order_date FROM store_orders;

-- With ORDER BY
SELECT 'customer' as type, name FROM customers
UNION ALL
SELECT 'supplier' as type, name FROM suppliers
ORDER BY name;
```

### INTERSECT

Find common rows:

```sql
-- Customers who made purchases in both years
SELECT customer_id FROM orders_2023
INTERSECT
SELECT customer_id FROM orders_2024;

-- Products in both warehouses
SELECT product_id, product_name FROM warehouse_a_inventory
INTERSECT
SELECT product_id, product_name FROM warehouse_b_inventory;
```

### EXCEPT

Find rows in first query but not in second:

```sql
-- Customers who haven't made recent purchases
SELECT customer_id FROM all_customers
EXCEPT
SELECT customer_id FROM orders 
WHERE order_date > CURRENT_DATE - INTERVAL '1 year';

-- Products not in any orders
SELECT product_id FROM products
EXCEPT
SELECT DISTINCT product_id FROM order_items;
```

### Combining Set Operations

```sql
-- Complex set operations
(SELECT customer_id FROM premium_customers
 UNION
 SELECT customer_id FROM vip_customers)
EXCEPT
SELECT customer_id FROM cancelled_customers
ORDER BY customer_id;
```

## CASE Expressions

### Simple CASE

```sql
-- Categorize based on value
SELECT 
    product_name,
    price,
    CASE category
        WHEN 'electronics' THEN 'Tech'
        WHEN 'clothing' THEN 'Fashion'
        WHEN 'food' THEN 'Grocery'
        ELSE 'Other'
    END as category_group
FROM products;
```

### Searched CASE

More flexible with conditions:

```sql
-- Price ranges
SELECT 
    product_name,
    price,
    CASE 
        WHEN price < 10 THEN 'Budget'
        WHEN price BETWEEN 10 AND 50 THEN 'Mid-range'
        WHEN price BETWEEN 50 AND 200 THEN 'Premium'
        ELSE 'Luxury'
    END as price_category
FROM products;

-- Multiple conditions
SELECT 
    employee_name,
    salary,
    performance_score,
    CASE 
        WHEN performance_score >= 9 AND salary < 100000 THEN 'Raise Recommended'
        WHEN performance_score < 5 THEN 'Performance Review'
        WHEN salary > 150000 THEN 'Executive Level'
        ELSE 'Standard'
    END as employee_status
FROM employees;
```

### CASE in Aggregations

```sql
-- Conditional counting
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(CASE WHEN salary > 100000 THEN 1 END) as high_earners,
    COUNT(CASE WHEN hire_date > '2023-01-01' THEN 1 END) as recent_hires,
    AVG(CASE WHEN performance_score >= 8 THEN salary END) as avg_top_performer_salary
FROM employees
GROUP BY department;

-- Pivot-like queries
SELECT 
    product_category,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 1 THEN amount ELSE 0 END) as jan_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 2 THEN amount ELSE 0 END) as feb_sales,
    SUM(CASE WHEN EXTRACT(MONTH FROM order_date) = 3 THEN amount ELSE 0 END) as mar_sales
FROM orders
GROUP BY product_category;
```

### Nested CASE

```sql
SELECT 
    customer_name,
    total_purchases,
    CASE 
        WHEN total_purchases > 1000 THEN 
            CASE 
                WHEN last_purchase_date > CURRENT_DATE - INTERVAL '30 days' THEN 'VIP Active'
                ELSE 'VIP Inactive'
            END
        WHEN total_purchases > 500 THEN 'Regular'
        ELSE 'New'
    END as customer_tier
FROM customer_summary;
```

## Pattern Matching

### LIKE and ILIKE

```sql
-- Basic pattern matching
SELECT * FROM products 
WHERE product_name LIKE 'Samsung%';  -- Starts with Samsung

SELECT * FROM customers 
WHERE email LIKE '%@gmail.com';  -- Ends with @gmail.com

SELECT * FROM products 
WHERE product_name LIKE '%phone%';  -- Contains 'phone'

-- Case-insensitive (PostgreSQL specific)
SELECT * FROM products 
WHERE product_name ILIKE '%IPHONE%';

-- Underscore for single character
SELECT * FROM products 
WHERE product_code LIKE 'A_C%';  -- A, any char, C, then anything
```

### SIMILAR TO (SQL Standard)

```sql
-- Regular expression-like patterns
SELECT * FROM products 
WHERE product_code SIMILAR TO '[A-Z]{3}[0-9]{4}';

SELECT * FROM emails 
WHERE email SIMILAR TO '%@(gmail|yahoo|hotmail).com';
```

### Regular Expressions (~)

PostgreSQL's powerful regex support:

```sql
-- Match pattern
SELECT * FROM products 
WHERE product_name ~ '^[A-Z]';  -- Starts with uppercase letter

-- Case-insensitive regex
SELECT * FROM products 
WHERE product_name ~* 'phone|tablet|laptop';

-- Not matching
SELECT * FROM products 
WHERE product_name !~ '[0-9]';  -- No digits

-- Extract matches
SELECT 
    product_name,
    (regexp_match(product_name, '(\d+)GB'))[1] as storage_gb
FROM products;

-- Multiple matches
SELECT 
    description,
    regexp_matches(description, '[A-Z][a-z]+', 'g') as words
FROM products;

-- Replace with regex
SELECT 
    regexp_replace(phone_number, '[^0-9]', '', 'g') as cleaned_phone
FROM contacts;
```

## Array Operations in Queries

```sql
-- Query array columns
SELECT * FROM articles 
WHERE 'postgresql' = ANY(tags);

SELECT * FROM articles 
WHERE tags @> ARRAY['postgresql', 'database'];  -- Contains all

SELECT * FROM articles 
WHERE tags && ARRAY['python', 'java'];  -- Overlaps

-- Unnest arrays
SELECT 
    article_id,
    unnest(tags) as tag
FROM articles;

-- Array aggregation
SELECT 
    author_id,
    array_agg(article_title ORDER BY published_date) as articles
FROM articles
GROUP BY author_id;
```

## JSON Queries

```sql
-- Query JSON columns
SELECT * FROM orders 
WHERE metadata->>'status' = 'completed';

SELECT * FROM orders 
WHERE (metadata->'customer'->>'vip')::boolean = true;

-- Extract JSON values
SELECT 
    order_id,
    metadata->>'status' as status,
    (metadata->>'total')::numeric as total
FROM orders;

-- JSON array elements
SELECT 
    order_id,
    jsonb_array_elements(items) as item
FROM orders;

-- JSON aggregation
SELECT 
    customer_id,
    jsonb_agg(
        jsonb_build_object(
            'order_id', order_id,
            'total', total_amount,
            'date', order_date
        )
    ) as orders
FROM orders
GROUP BY customer_id;
```

## Lateral Joins

Allows subqueries to reference previous FROM items:

```sql
-- Get top 3 products per category
SELECT 
    c.category_name,
    p.product_name,
    p.sales
FROM categories c
CROSS JOIN LATERAL (
    SELECT product_name, sales
    FROM products
    WHERE category_id = c.category_id
    ORDER BY sales DESC
    LIMIT 3
) p;

-- Complex calculations per row
SELECT 
    e.employee_name,
    e.salary,
    stats.avg_dept_salary,
    stats.rank_in_dept
FROM employees e
CROSS JOIN LATERAL (
    SELECT 
        AVG(salary) as avg_dept_salary,
        (SELECT COUNT(*) + 1 
         FROM employees e2 
         WHERE e2.department_id = e.department_id 
           AND e2.salary > e.salary) as rank_in_dept
    FROM employees
    WHERE department_id = e.department_id
) stats;
```

## Best Practices

### 1. Use Appropriate Indexing
```sql
-- For DISTINCT queries
CREATE INDEX idx_dept ON employees(department);

-- For pattern matching
CREATE INDEX idx_name_trgm ON products USING gin(product_name gin_trgm_ops);

-- For JSON queries
CREATE INDEX idx_metadata ON orders USING gin(metadata);
```

### 2. Optimize Set Operations
- Use UNION ALL instead of UNION when duplicates don't matter (faster)
- Ensure indexes on columns used in set operations
- Consider materialized views for complex unions

### 3. CASE Expression Tips
- Put most common conditions first
- Use CASE in indexes for conditional indexes
- Avoid complex CASE in WHERE clauses (hurt performance)

### 4. Pattern Matching Performance
```sql
-- GOOD: Can use index
SELECT * FROM products WHERE product_name LIKE 'Samsung%';

-- BAD: Cannot use regular index
SELECT * FROM products WHERE product_name LIKE '%phone%';

-- Solution: Use trigram index for contains searches
CREATE EXTENSION pg_trgm;
CREATE INDEX idx_name_trgm ON products USING gin(product_name gin_trgm_ops);
```

### 5. Pagination Best Practices
```sql
-- Avoid large OFFSET values
-- Use keyset pagination for large datasets
SELECT * FROM orders 
WHERE (order_date, order_id) > (:last_date, :last_id)
ORDER BY order_date, order_id 
LIMIT 20;
```

## Common Pitfalls

### 1. DISTINCT Performance
```sql
-- BAD: DISTINCT on large table without index
SELECT DISTINCT expensive_column FROM huge_table;

-- GOOD: Use indexes or GROUP BY
CREATE INDEX idx_exp_col ON huge_table(expensive_column);
SELECT expensive_column FROM huge_table GROUP BY expensive_column;
```

### 2. UNION vs UNION ALL
```sql
-- Don't use UNION when you know there are no duplicates
-- UNION adds expensive deduplication step
SELECT id FROM table1 WHERE condition1
UNION ALL  -- Use ALL if duplicates impossible or acceptable
SELECT id FROM table2 WHERE condition2;
```

### 3. NULL Handling in CASE
```sql
-- Remember: NULL doesn't equal NULL
SELECT CASE status 
    WHEN NULL THEN 'No status'  -- This never matches!
    ELSE 'Has status'
END;

-- Correct way
SELECT CASE 
    WHEN status IS NULL THEN 'No status'
    ELSE 'Has status'
END;
```

### 4. Pattern Matching Edge Cases
```sql
-- Escaping special characters
SELECT * FROM products 
WHERE product_name LIKE '50\% off%' ESCAPE '\';

-- Case sensitivity
SELECT * FROM products 
WHERE product_name ILIKE '%iphone%';  -- PostgreSQL specific
```

## Performance Tips

### 1. Analyze Query Plans
```sql
EXPLAIN ANALYZE
SELECT DISTINCT department FROM employees;

EXPLAIN ANALYZE
SELECT * FROM orders LIMIT 10 OFFSET 10000;
```

### 2. Use Covering Indexes
```sql
-- Index includes all columns needed
CREATE INDEX idx_covering ON products(category_id) 
INCLUDE (product_name, price);
```

### 3. Materialized Views for Complex Queries
```sql
CREATE MATERIALIZED VIEW product_stats AS
SELECT 
    category,
    COUNT(*) as product_count,
    AVG(price) as avg_price
FROM products
GROUP BY category;

CREATE INDEX ON product_stats(category);
```

## Summary

Advanced SELECT queries in PostgreSQL provide powerful tools for:
- **DISTINCT operations** for unique values
- **LIMIT/OFFSET** for pagination (prefer keyset for large offsets)
- **Set operations** (UNION, INTERSECT, EXCEPT) for combining queries
- **CASE expressions** for conditional logic
- **Pattern matching** with LIKE, SIMILAR TO, and regex
- **LATERAL joins** for correlated subqueries

Master these techniques to write efficient, readable SQL queries.

## Next Steps

- Learn about [Common Table Expressions (CTEs)](./14-common-table-expressions.md)
- Explore [Window Functions](./13-window-functions.md)
- Study [Query Optimization](./20-query-optimization.md)
- Practice with [Aggregation and Grouping](./15-aggregation-and-grouping.md)
