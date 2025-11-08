# Common Table Expressions (CTEs)

## Overview

Common Table Expressions (CTEs) are temporary named result sets that exist only during query execution. They make complex queries more readable, enable recursive queries, and can improve query organization. CTEs are defined using the `WITH` clause.

## Table of Contents
- [Basic CTE Syntax](#basic-cte-syntax)
- [Multiple CTEs](#multiple-ctes)
- [Recursive CTEs](#recursive-ctes)
- [CTE Performance Considerations](#cte-performance-considerations)
- [Writeable CTEs](#writeable-ctes)
- [Advanced CTE Patterns](#advanced-cte-patterns)

## Basic CTE Syntax

### Simple CTE

```sql
-- Basic CTE structure
WITH high_earners AS (
    SELECT employee_id, employee_name, salary, department_id
    FROM employees
    WHERE salary > 100000
)
SELECT * FROM high_earners
ORDER BY salary DESC;

-- CTE with aggregation
WITH department_stats AS (
    SELECT 
        department_id,
        COUNT(*) as employee_count,
        AVG(salary) as avg_salary,
        MAX(salary) as max_salary
    FROM employees
    GROUP BY department_id
)
SELECT 
    d.department_name,
    ds.employee_count,
    ds.avg_salary,
    ds.max_salary
FROM department_stats ds
JOIN departments d ON ds.department_id = d.department_id
WHERE ds.employee_count > 10;
```

### Benefits Over Subqueries

```sql
-- Without CTE (harder to read)
SELECT 
    e.employee_name,
    e.salary,
    e.salary - dept_avg.avg_sal as diff_from_avg
FROM employees e
JOIN (
    SELECT department_id, AVG(salary) as avg_sal
    FROM employees
    GROUP BY department_id
) dept_avg ON e.department_id = dept_avg.department_id
WHERE e.salary > dept_avg.avg_sal * 1.2;

-- With CTE (clearer intent)
WITH department_averages AS (
    SELECT 
        department_id, 
        AVG(salary) as avg_salary
    FROM employees
    GROUP BY department_id
)
SELECT 
    e.employee_name,
    e.salary,
    e.salary - da.avg_salary as diff_from_avg
FROM employees e
JOIN department_averages da ON e.department_id = da.department_id
WHERE e.salary > da.avg_salary * 1.2;
```

## Multiple CTEs

Chain multiple CTEs together:

```sql
-- Multiple CTEs separated by commas
WITH 
-- First CTE: Calculate monthly sales
monthly_sales AS (
    SELECT 
        EXTRACT(YEAR FROM order_date) as year,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(total_amount) as total_sales,
        COUNT(DISTINCT customer_id) as unique_customers
    FROM orders
    WHERE order_date >= '2024-01-01'
    GROUP BY year, month
),
-- Second CTE: Calculate running totals
sales_with_running_total AS (
    SELECT 
        year,
        month,
        total_sales,
        unique_customers,
        SUM(total_sales) OVER (ORDER BY year, month) as running_total
    FROM monthly_sales
),
-- Third CTE: Calculate month-over-month change
sales_with_change AS (
    SELECT 
        year,
        month,
        total_sales,
        unique_customers,
        running_total,
        LAG(total_sales) OVER (ORDER BY year, month) as prev_month_sales,
        total_sales - LAG(total_sales) OVER (ORDER BY year, month) as sales_change
    FROM sales_with_running_total
)
-- Final query
SELECT 
    year,
    month,
    total_sales,
    unique_customers,
    running_total,
    prev_month_sales,
    sales_change,
    ROUND(100.0 * sales_change / NULLIF(prev_month_sales, 0), 2) as pct_change
FROM sales_with_change
ORDER BY year, month;
```

### CTEs Referencing Other CTEs

```sql
WITH 
-- Get active customers
active_customers AS (
    SELECT DISTINCT customer_id
    FROM orders
    WHERE order_date > CURRENT_DATE - INTERVAL '6 months'
),
-- Get customer lifetime value (using first CTE)
customer_ltv AS (
    SELECT 
        o.customer_id,
        COUNT(*) as order_count,
        SUM(o.total_amount) as lifetime_value
    FROM orders o
    JOIN active_customers ac ON o.customer_id = ac.customer_id
    GROUP BY o.customer_id
),
-- Classify customers (using second CTE)
customer_segments AS (
    SELECT 
        customer_id,
        order_count,
        lifetime_value,
        CASE 
            WHEN lifetime_value > 10000 THEN 'VIP'
            WHEN lifetime_value > 5000 THEN 'Premium'
            WHEN lifetime_value > 1000 THEN 'Regular'
            ELSE 'New'
        END as segment
    FROM customer_ltv
)
SELECT 
    segment,
    COUNT(*) as customer_count,
    AVG(lifetime_value) as avg_ltv,
    AVG(order_count) as avg_orders
FROM customer_segments
GROUP BY segment
ORDER BY avg_ltv DESC;
```

## Recursive CTEs

### Basic Recursive CTE Structure

```sql
WITH RECURSIVE cte_name AS (
    -- Base case (non-recursive term)
    SELECT ...
    
    UNION [ALL]
    
    -- Recursive term
    SELECT ...
    FROM cte_name
    WHERE termination_condition
)
SELECT * FROM cte_name;
```

### Number Series Generation

```sql
-- Generate numbers 1 to 10
WITH RECURSIVE numbers AS (
    SELECT 1 as n  -- Base case
    UNION ALL
    SELECT n + 1   -- Recursive case
    FROM numbers
    WHERE n < 10   -- Termination
)
SELECT * FROM numbers;

-- Generate date series
WITH RECURSIVE date_series AS (
    SELECT DATE '2024-01-01' as date
    UNION ALL
    SELECT date + INTERVAL '1 day'
    FROM date_series
    WHERE date < DATE '2024-12-31'
)
SELECT date, EXTRACT(DOW FROM date) as day_of_week
FROM date_series
WHERE EXTRACT(DOW FROM date) IN (0, 6); -- Weekends only
```

### Hierarchical Data Traversal

```sql
-- Organization hierarchy
CREATE TABLE employees (
    employee_id INT PRIMARY KEY,
    employee_name VARCHAR(100),
    manager_id INT,
    salary NUMERIC
);

-- Find all subordinates of a manager
WITH RECURSIVE subordinates AS (
    -- Base case: direct reports
    SELECT 
        employee_id,
        employee_name,
        manager_id,
        salary,
        1 as level,
        employee_name as path
    FROM employees
    WHERE manager_id = 100  -- Starting manager
    
    UNION ALL
    
    -- Recursive case: employees reporting to subordinates
    SELECT 
        e.employee_id,
        e.employee_name,
        e.manager_id,
        e.salary,
        s.level + 1,
        s.path || ' > ' || e.employee_name
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.employee_id
    WHERE s.level < 10  -- Prevent infinite recursion
)
SELECT 
    employee_id,
    REPEAT('  ', level - 1) || employee_name as employee_hierarchy,
    level,
    salary,
    path
FROM subordinates
ORDER BY level, employee_name;

-- Find management chain (upward traversal)
WITH RECURSIVE management_chain AS (
    -- Base case: starting employee
    SELECT 
        employee_id,
        employee_name,
        manager_id,
        1 as level
    FROM employees
    WHERE employee_id = 500  -- Starting employee
    
    UNION ALL
    
    -- Recursive case: managers
    SELECT 
        e.employee_id,
        e.employee_name,
        e.manager_id,
        mc.level + 1
    FROM employees e
    JOIN management_chain mc ON e.employee_id = mc.manager_id
)
SELECT * FROM management_chain
ORDER BY level DESC;
```

### Tree/Graph Traversal

```sql
-- Category tree (product categories)
CREATE TABLE categories (
    category_id INT PRIMARY KEY,
    category_name VARCHAR(100),
    parent_category_id INT
);

-- Get all subcategories
WITH RECURSIVE category_tree AS (
    -- Root categories
    SELECT 
        category_id,
        category_name,
        parent_category_id,
        1 as depth,
        ARRAY[category_id] as path,
        category_name as full_path
    FROM categories
    WHERE parent_category_id IS NULL
    
    UNION ALL
    
    -- Child categories
    SELECT 
        c.category_id,
        c.category_name,
        c.parent_category_id,
        ct.depth + 1,
        ct.path || c.category_id,
        ct.full_path || ' > ' || c.category_name
    FROM categories c
    JOIN category_tree ct ON c.parent_category_id = ct.category_id
    WHERE NOT c.category_id = ANY(ct.path)  -- Prevent cycles
)
SELECT 
    REPEAT('  ', depth - 1) || category_name as category_hierarchy,
    depth,
    full_path,
    array_length(path, 1) as level_count
FROM category_tree
ORDER BY full_path;
```

### Bill of Materials (BOM)

```sql
-- Parts and assemblies
CREATE TABLE parts (
    part_id INT PRIMARY KEY,
    part_name VARCHAR(100),
    cost NUMERIC
);

CREATE TABLE assembly (
    assembly_id INT,
    part_id INT,
    quantity INT,
    PRIMARY KEY (assembly_id, part_id)
);

-- Calculate total cost including all subcomponents
WITH RECURSIVE part_explosion AS (
    -- Top-level assembly
    SELECT 
        a.part_id,
        p.part_name,
        a.quantity,
        p.cost,
        a.quantity * p.cost as total_cost,
        1 as level
    FROM assembly a
    JOIN parts p ON a.part_id = p.part_id
    WHERE a.assembly_id = 1000  -- Product we're costing
    
    UNION ALL
    
    -- Subcomponents
    SELECT 
        a.part_id,
        p.part_name,
        pe.quantity * a.quantity,
        p.cost,
        pe.quantity * a.quantity * p.cost,
        pe.level + 1
    FROM assembly a
    JOIN parts p ON a.part_id = p.part_id
    JOIN part_explosion pe ON a.assembly_id = pe.part_id
    WHERE pe.level < 20
)
SELECT 
    part_id,
    REPEAT('  ', level - 1) || part_name as component,
    quantity,
    cost,
    total_cost,
    level
FROM part_explosion
ORDER BY level, part_name;

-- Total BOM cost
WITH RECURSIVE part_explosion AS (
    -- ... same as above ...
)
SELECT 
    'Total Cost' as description,
    SUM(total_cost) as total_bom_cost
FROM part_explosion;
```

### Graph Traversal (Finding Paths)

```sql
-- Road network
CREATE TABLE roads (
    from_city VARCHAR(50),
    to_city VARCHAR(50),
    distance INT
);

-- Find all paths between two cities
WITH RECURSIVE routes AS (
    -- Starting point
    SELECT 
        from_city,
        to_city,
        distance,
        ARRAY[from_city, to_city] as path,
        distance as total_distance
    FROM roads
    WHERE from_city = 'New York'
    
    UNION ALL
    
    -- Add connected cities
    SELECT 
        r.from_city,
        rd.to_city,
        rd.distance,
        r.path || rd.to_city,
        r.total_distance + rd.distance
    FROM routes r
    JOIN roads rd ON r.to_city = rd.from_city
    WHERE rd.to_city <> ALL(r.path)  -- Avoid cycles
      AND array_length(r.path, 1) < 10  -- Limit path length
)
SELECT 
    path,
    total_distance
FROM routes
WHERE to_city = 'Los Angeles'
ORDER BY total_distance
LIMIT 5;
```

## CTE Performance Considerations

### Materialization vs Inline

PostgreSQL 12+ has optimization fence behavior:

```sql
-- CTE is materialized (optimization fence)
WITH regional_sales AS (
    SELECT region, SUM(amount) as total_sales
    FROM orders
    GROUP BY region
)
SELECT * FROM regional_sales
WHERE total_sales > 10000;

-- Force inline behavior (PostgreSQL 12+)
WITH regional_sales AS NOT MATERIALIZED (
    SELECT region, SUM(amount) as total_sales
    FROM orders
    GROUP BY region
)
SELECT * FROM regional_sales
WHERE total_sales > 10000;

-- Force materialization
WITH regional_sales AS MATERIALIZED (
    SELECT region, SUM(amount) as total_sales
    FROM orders
    GROUP BY region
)
SELECT * FROM regional_sales
WHERE total_sales > 10000;
```

### When CTEs Help Performance

```sql
-- CTE used multiple times - prevents redundant computation
WITH expensive_calc AS (
    SELECT 
        product_id,
        AVG(price) as avg_price,
        STDDEV(price) as price_stddev
    FROM price_history
    WHERE date > CURRENT_DATE - INTERVAL '1 year'
    GROUP BY product_id
)
SELECT 
    p.product_name,
    ec1.avg_price as current_avg,
    ec2.avg_price as competitor_avg,
    ec1.avg_price - ec2.avg_price as price_difference
FROM products p
JOIN expensive_calc ec1 ON p.product_id = ec1.product_id
JOIN expensive_calc ec2 ON p.competitor_id = ec2.product_id;
```

### Recursive CTE Optimization

```sql
-- Add termination conditions
WITH RECURSIVE hierarchy AS (
    SELECT id, parent_id, 1 as level
    FROM nodes
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT n.id, n.parent_id, h.level + 1
    FROM nodes n
    JOIN hierarchy h ON n.parent_id = h.id
    WHERE h.level < 100  -- IMPORTANT: Prevent infinite recursion
)
SELECT * FROM hierarchy;

-- Use indexes on recursive join columns
CREATE INDEX idx_nodes_parent ON nodes(parent_id);
```

## Writeable CTEs

Modify data and return results:

```sql
-- Insert and return
WITH inserted_orders AS (
    INSERT INTO orders (customer_id, order_date, total_amount)
    VALUES (100, CURRENT_DATE, 500.00)
    RETURNING order_id, customer_id, total_amount
)
INSERT INTO order_audit (order_id, action, timestamp)
SELECT order_id, 'CREATED', CURRENT_TIMESTAMP
FROM inserted_orders;

-- Update with CTE
WITH updated_prices AS (
    UPDATE products
    SET price = price * 1.10
    WHERE category = 'electronics'
    RETURNING product_id, product_name, price as new_price
)
SELECT * FROM updated_prices;

-- Complex multi-table modification
WITH moved_orders AS (
    DELETE FROM pending_orders
    WHERE order_date < CURRENT_DATE - INTERVAL '7 days'
    RETURNING *
),
archived AS (
    INSERT INTO archived_orders
    SELECT * FROM moved_orders
    RETURNING order_id
)
SELECT COUNT(*) as archived_count FROM archived;

-- Conditional updates with CTEs
WITH customer_stats AS (
    SELECT 
        customer_id,
        COUNT(*) as order_count,
        SUM(total_amount) as total_spent
    FROM orders
    WHERE order_date > CURRENT_DATE - INTERVAL '1 year'
    GROUP BY customer_id
),
tier_updates AS (
    UPDATE customers c
    SET 
        customer_tier = CASE 
            WHEN cs.total_spent > 10000 THEN 'VIP'
            WHEN cs.total_spent > 5000 THEN 'Premium'
            ELSE 'Regular'
        END,
        updated_at = CURRENT_TIMESTAMP
    FROM customer_stats cs
    WHERE c.customer_id = cs.customer_id
    RETURNING c.customer_id, c.customer_tier
)
SELECT customer_tier, COUNT(*) as customer_count
FROM tier_updates
GROUP BY customer_tier;
```

## Advanced CTE Patterns

### Moving Averages with CTEs

```sql
WITH daily_sales AS (
    SELECT 
        order_date::DATE as date,
        SUM(total_amount) as daily_total
    FROM orders
    GROUP BY order_date::DATE
),
sales_with_ma AS (
    SELECT 
        date,
        daily_total,
        AVG(daily_total) OVER (
            ORDER BY date 
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) as moving_avg_7day
    FROM daily_sales
)
SELECT * FROM sales_with_ma
WHERE date > CURRENT_DATE - INTERVAL '30 days'
ORDER BY date;
```

### Gaps and Islands

```sql
-- Find consecutive date ranges
WITH numbered_dates AS (
    SELECT 
        login_date,
        ROW_NUMBER() OVER (ORDER BY login_date) as rn,
        login_date - (ROW_NUMBER() OVER (ORDER BY login_date))::INT as grp
    FROM user_logins
    WHERE user_id = 100
),
consecutive_ranges AS (
    SELECT 
        MIN(login_date) as range_start,
        MAX(login_date) as range_end,
        COUNT(*) as consecutive_days
    FROM numbered_dates
    GROUP BY grp
)
SELECT * FROM consecutive_ranges
ORDER BY range_start;
```

### Pivot with CTEs

```sql
WITH monthly_data AS (
    SELECT 
        product_id,
        EXTRACT(MONTH FROM order_date) as month,
        SUM(quantity) as total_quantity
    FROM order_items oi
    JOIN orders o ON oi.order_id = o.order_id
    WHERE EXTRACT(YEAR FROM order_date) = 2024
    GROUP BY product_id, month
)
SELECT 
    product_id,
    SUM(CASE WHEN month = 1 THEN total_quantity ELSE 0 END) as jan,
    SUM(CASE WHEN month = 2 THEN total_quantity ELSE 0 END) as feb,
    SUM(CASE WHEN month = 3 THEN total_quantity ELSE 0 END) as mar,
    SUM(CASE WHEN month = 4 THEN total_quantity ELSE 0 END) as apr,
    SUM(CASE WHEN month = 5 THEN total_quantity ELSE 0 END) as may,
    SUM(CASE WHEN month = 6 THEN total_quantity ELSE 0 END) as jun
FROM monthly_data
GROUP BY product_id;
```

## Best Practices

1. **Use CTEs for Readability**: Break complex queries into logical steps
2. **Name CTEs Descriptively**: Use clear, intention-revealing names
3. **Consider Materialization**: Use MATERIALIZED/NOT MATERIALIZED hints when needed
4. **Add Recursion Limits**: Always include termination conditions in recursive CTEs
5. **Index Join Columns**: Ensure columns used in recursive joins are indexed
6. **Avoid Overuse**: Don't use CTEs when simple subqueries are clearer
7. **Monitor Performance**: Use EXPLAIN ANALYZE to verify CTE performance

## Common Pitfalls

### 1. Infinite Recursion
```sql
-- BAD: No termination condition
WITH RECURSIVE bad_cte AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM bad_cte  -- Never stops!
)
SELECT * FROM bad_cte;

-- GOOD: Always add termination
WITH RECURSIVE good_cte AS (
    SELECT 1 as n
    UNION ALL
    SELECT n + 1 FROM bad_cte WHERE n < 100
)
SELECT * FROM good_cte;
```

### 2. Circular References
```sql
-- Detect cycles in hierarchical data
WITH RECURSIVE hierarchy AS (
    SELECT id, parent_id, ARRAY[id] as path
    FROM nodes
    WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT n.id, n.parent_id, h.path || n.id
    FROM nodes n
    JOIN hierarchy h ON n.parent_id = h.id
    WHERE NOT n.id = ANY(h.path)  -- Prevent cycles
)
SELECT * FROM hierarchy;
```

### 3. Performance Issues
```sql
-- Monitor CTE execution
EXPLAIN (ANALYZE, BUFFERS)
WITH large_cte AS (
    SELECT * FROM huge_table WHERE condition
)
SELECT * FROM large_cte
WHERE another_condition;
```

## Summary

Common Table Expressions (CTEs) provide:
- **Improved readability** through named subqueries
- **Recursive capabilities** for hierarchical and graph data
- **Data modification** with RETURNING clauses
- **Query organization** for complex multi-step operations

Use CTEs to make SQL more maintainable and express complex logic clearly.

## Next Steps

- Learn about [Window Functions](./13-window-functions.md)
- Explore [Advanced SELECT Queries](./11-advanced-select-queries.md)
- Study [Query Optimization](./20-query-optimization.md)
- Practice [Aggregation and Grouping](./15-aggregation-and-grouping.md)
