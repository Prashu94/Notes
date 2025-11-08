# Aggregation and Grouping

## Overview

Aggregation functions perform calculations on sets of rows and return single values. Combined with GROUP BY, HAVING, and advanced grouping features like ROLLUP, CUBE, and GROUPING SETS, PostgreSQL provides powerful tools for data analysis and reporting.

## Table of Contents
- [Aggregate Functions](#aggregate-functions)
- [GROUP BY Basics](#group-by-basics)
- [HAVING Clause](#having-clause)
- [Advanced Grouping](#advanced-grouping)
- [FILTER Clause](#filter-clause)
- [Ordered-Set Aggregates](#ordered-set-aggregates)
- [Statistical Aggregates](#statistical-aggregates)
- [Custom Aggregates](#custom-aggregates)

## Aggregate Functions

### Common Aggregate Functions

```sql
-- COUNT: Number of rows
SELECT COUNT(*) FROM orders;  -- All rows including NULLs
SELECT COUNT(customer_id) FROM orders;  -- Non-NULL values only
SELECT COUNT(DISTINCT customer_id) FROM orders;  -- Unique customers

-- SUM: Total of numeric values
SELECT SUM(total_amount) as total_revenue FROM orders;
SELECT SUM(CASE WHEN status = 'completed' THEN total_amount ELSE 0 END) as completed_revenue
FROM orders;

-- AVG: Average (mean) value
SELECT AVG(salary) as avg_salary FROM employees;
SELECT AVG(salary) FILTER (WHERE department = 'Engineering') as eng_avg_salary
FROM employees;

-- MIN and MAX: Smallest and largest values
SELECT 
    MIN(order_date) as first_order,
    MAX(order_date) as last_order,
    MIN(total_amount) as smallest_order,
    MAX(total_amount) as largest_order
FROM orders;

-- STRING_AGG: Concatenate strings
SELECT 
    department,
    STRING_AGG(employee_name, ', ' ORDER BY employee_name) as employees
FROM employees
GROUP BY department;

-- ARRAY_AGG: Collect values into array
SELECT 
    customer_id,
    ARRAY_AGG(order_id ORDER BY order_date DESC) as order_ids
FROM orders
GROUP BY customer_id;

-- JSON aggregates
SELECT 
    department,
    JSON_AGG(
        JSON_BUILD_OBJECT(
            'name', employee_name,
            'salary', salary
        ) ORDER BY salary DESC
    ) as employees
FROM employees
GROUP BY department;
```

### Boolean Aggregates

```sql
-- BOOL_AND: True if all values are true
SELECT 
    department,
    BOOL_AND(salary > 50000) as all_above_50k
FROM employees
GROUP BY department;

-- BOOL_OR: True if any value is true
SELECT 
    department,
    BOOL_OR(salary > 100000) as has_high_earner
FROM employees
GROUP BY department;

-- EVERY: Synonym for BOOL_AND
SELECT 
    product_category,
    EVERY(in_stock) as all_in_stock
FROM products
GROUP BY product_category;
```

### Bitwise Aggregates

```sql
-- BIT_AND, BIT_OR: Bitwise operations
SELECT 
    category,
    BIT_AND(flags) as common_flags,
    BIT_OR(flags) as any_flags
FROM items
GROUP BY category;
```

## GROUP BY Basics

### Simple Grouping

```sql
-- Group by single column
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    SUM(salary) as total_salary
FROM employees
GROUP BY department;

-- Group by multiple columns
SELECT 
    department,
    job_title,
    COUNT(*) as count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department, job_title
ORDER BY department, job_title;

-- Group by expressions
SELECT 
    EXTRACT(YEAR FROM order_date) as year,
    EXTRACT(MONTH FROM order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue
FROM orders
GROUP BY 
    EXTRACT(YEAR FROM order_date),
    EXTRACT(MONTH FROM order_date)
ORDER BY year, month;

-- Using column positions (not recommended for maintenance)
SELECT 
    department,
    COUNT(*) as employee_count
FROM employees
GROUP BY 1;  -- References first column in SELECT
```

### GROUP BY with JOINs

```sql
SELECT 
    c.customer_name,
    c.customer_tier,
    COUNT(o.order_id) as order_count,
    SUM(o.total_amount) as total_spent,
    AVG(o.total_amount) as avg_order_value,
    MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name, c.customer_tier
HAVING COUNT(o.order_id) > 0
ORDER BY total_spent DESC;
```

### Grouping by Date/Time

```sql
-- Group by day
SELECT 
    order_date::DATE as order_day,
    COUNT(*) as order_count,
    SUM(total_amount) as daily_revenue
FROM orders
GROUP BY order_date::DATE
ORDER BY order_day;

-- Group by week
SELECT 
    DATE_TRUNC('week', order_date) as week_start,
    COUNT(*) as order_count,
    SUM(total_amount) as weekly_revenue
FROM orders
GROUP BY DATE_TRUNC('week', order_date)
ORDER BY week_start;

-- Group by month
SELECT 
    DATE_TRUNC('month', order_date) as month,
    COUNT(*) as order_count,
    SUM(total_amount) as monthly_revenue
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;

-- Group by quarter and year
SELECT 
    EXTRACT(YEAR FROM order_date) as year,
    EXTRACT(QUARTER FROM order_date) as quarter,
    COUNT(*) as order_count,
    SUM(total_amount) as revenue
FROM orders
GROUP BY 
    EXTRACT(YEAR FROM order_date),
    EXTRACT(QUARTER FROM order_date)
ORDER BY year, quarter;

-- Group by hour of day (time patterns)
SELECT 
    EXTRACT(HOUR FROM created_at) as hour_of_day,
    COUNT(*) as transaction_count
FROM transactions
GROUP BY EXTRACT(HOUR FROM created_at)
ORDER BY hour_of_day;

-- Group by day of week
SELECT 
    TO_CHAR(order_date, 'Day') as day_name,
    EXTRACT(DOW FROM order_date) as day_num,
    COUNT(*) as order_count,
    AVG(total_amount) as avg_order_value
FROM orders
GROUP BY 
    TO_CHAR(order_date, 'Day'),
    EXTRACT(DOW FROM order_date)
ORDER BY day_num;
```

## HAVING Clause

Filter groups after aggregation:

```sql
-- Basic HAVING
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) >= 5;  -- Only departments with 5+ employees

-- Multiple HAVING conditions
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
GROUP BY department
HAVING COUNT(*) >= 5 
   AND AVG(salary) > 60000;

-- HAVING with aggregates not in SELECT
SELECT 
    customer_id,
    COUNT(*) as order_count
FROM orders
WHERE order_date > '2024-01-01'
GROUP BY customer_id
HAVING SUM(total_amount) > 10000  -- Filter by total spent
   AND MAX(order_date) > CURRENT_DATE - INTERVAL '30 days';

-- WHERE vs HAVING
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary
FROM employees
WHERE hire_date > '2020-01-01'  -- Filter BEFORE grouping
GROUP BY department
HAVING COUNT(*) >= 3;  -- Filter AFTER grouping
```

### Complex HAVING Examples

```sql
-- Find customers with inconsistent order patterns
SELECT 
    customer_id,
    COUNT(*) as order_count,
    STDDEV(total_amount) as order_stddev,
    AVG(total_amount) as avg_order
FROM orders
GROUP BY customer_id
HAVING STDDEV(total_amount) > AVG(total_amount) * 0.5  -- High variance
   AND COUNT(*) >= 10;

-- Find products popular in multiple categories
SELECT 
    product_name,
    COUNT(DISTINCT category_id) as category_count,
    SUM(quantity_sold) as total_sold
FROM product_sales
GROUP BY product_name
HAVING COUNT(DISTINCT category_id) >= 3;

-- Identify seasonal products
SELECT 
    product_id,
    COUNT(DISTINCT EXTRACT(QUARTER FROM order_date)) as quarters_sold,
    AVG(quantity) as avg_quantity
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
GROUP BY product_id
HAVING COUNT(DISTINCT EXTRACT(QUARTER FROM order_date)) <= 2
   AND AVG(quantity) > 100;
```

## Advanced Grouping

### GROUPING SETS

Specify multiple grouping levels in one query:

```sql
-- Multiple grouping levels
SELECT 
    region,
    product_category,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY GROUPING SETS (
    (region, product_category),  -- Group by both
    (region),                     -- Group by region only
    (product_category),           -- Group by category only
    ()                            -- Grand total
)
ORDER BY region NULLS FIRST, product_category NULLS FIRST;

-- With GROUPING() function to identify aggregation level
SELECT 
    region,
    product_category,
    SUM(sales_amount) as total_sales,
    GROUPING(region) as is_region_total,
    GROUPING(product_category) as is_category_total,
    CASE 
        WHEN GROUPING(region) = 1 AND GROUPING(product_category) = 1 
            THEN 'Grand Total'
        WHEN GROUPING(region) = 1 
            THEN 'Category Total'
        WHEN GROUPING(product_category) = 1 
            THEN 'Region Total'
        ELSE 'Detail'
    END as aggregation_level
FROM sales
GROUP BY GROUPING SETS (
    (region, product_category),
    (region),
    (product_category),
    ()
);
```

### ROLLUP

Hierarchical subtotals (right-to-left):

```sql
-- Basic ROLLUP
SELECT 
    year,
    quarter,
    month,
    SUM(revenue) as total_revenue
FROM monthly_sales
GROUP BY ROLLUP (year, quarter, month)
ORDER BY year, quarter, month;

-- Produces groupings:
-- (year, quarter, month)  - Most detailed
-- (year, quarter)         - Quarterly totals
-- (year)                  - Yearly totals
-- ()                      - Grand total

-- Partial ROLLUP
SELECT 
    region,
    year,
    month,
    SUM(sales) as total_sales
FROM sales
GROUP BY region, ROLLUP (year, month);
-- Keeps region ungrouped, rolls up year and month

-- ROLLUP with GROUPING for labels
SELECT 
    COALESCE(region, 'ALL REGIONS') as region,
    COALESCE(product_type, 'ALL TYPES') as product_type,
    SUM(sales_amount) as total_sales,
    GROUPING(region) as is_region_rollup,
    GROUPING(product_type) as is_type_rollup
FROM sales
GROUP BY ROLLUP (region, product_type)
ORDER BY region NULLS LAST, product_type NULLS LAST;
```

### CUBE

All possible combinations:

```sql
-- Basic CUBE
SELECT 
    region,
    product_category,
    sales_channel,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY CUBE (region, product_category, sales_channel);

-- Produces 2^3 = 8 grouping combinations:
-- (region, product_category, sales_channel)
-- (region, product_category)
-- (region, sales_channel)
-- (region)
-- (product_category, sales_channel)
-- (product_category)
-- (sales_channel)
-- ()  - Grand total

-- Partial CUBE
SELECT 
    year,
    region,
    product_category,
    SUM(sales_amount) as total_sales
FROM sales
GROUP BY year, CUBE (region, product_category);
-- Year is not cubed, only region and category

-- CUBE with useful labels
SELECT 
    COALESCE(region, 'Total') as region,
    COALESCE(product_category, 'Total') as category,
    COALESCE(quarter::TEXT, 'Total') as quarter,
    SUM(sales_amount) as total_sales,
    COUNT(*) as transaction_count
FROM sales
WHERE year = 2024
GROUP BY CUBE (region, product_category, quarter)
ORDER BY 
    GROUPING(region),
    GROUPING(product_category),
    GROUPING(quarter),
    region,
    product_category,
    quarter;
```

### Combining ROLLUP, CUBE, and GROUPING SETS

```sql
-- Complex grouping combinations
SELECT 
    year,
    quarter,
    region,
    product_line,
    SUM(revenue) as total_revenue,
    COUNT(*) as sale_count
FROM sales
GROUP BY GROUPING SETS (
    ROLLUP(year, quarter),           -- Time hierarchy
    ROLLUP(region, product_line),    -- Geographic/product hierarchy
    (year, region),                   -- Specific combination
    ()                                -- Grand total
)
ORDER BY year, quarter, region, product_line;
```

## FILTER Clause

Apply conditions to specific aggregates:

```sql
-- Multiple filtered aggregates
SELECT 
    department,
    COUNT(*) as total_employees,
    COUNT(*) FILTER (WHERE salary > 100000) as high_earners,
    COUNT(*) FILTER (WHERE hire_date > '2023-01-01') as recent_hires,
    AVG(salary) as avg_salary,
    AVG(salary) FILTER (WHERE performance_score >= 8) as avg_top_performer_salary
FROM employees
GROUP BY department;

-- Compare different time periods
SELECT 
    product_id,
    product_name,
    SUM(quantity) FILTER (
        WHERE order_date >= '2024-01-01' 
        AND order_date < '2024-04-01'
    ) as q1_sales,
    SUM(quantity) FILTER (
        WHERE order_date >= '2024-04-01' 
        AND order_date < '2024-07-01'
    ) as q2_sales,
    SUM(quantity) FILTER (
        WHERE order_date >= '2024-07-01' 
        AND order_date < '2024-10-01'
    ) as q3_sales,
    SUM(quantity) FILTER (
        WHERE order_date >= '2024-10-01' 
        AND order_date < '2025-01-01'
    ) as q4_sales
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE EXTRACT(YEAR FROM order_date) = 2024
GROUP BY product_id, product_name;

-- FILTER vs CASE expression
-- These are equivalent:
SELECT 
    department,
    COUNT(*) FILTER (WHERE salary > 100000) as method1,
    SUM(CASE WHEN salary > 100000 THEN 1 ELSE 0 END) as method2
FROM employees
GROUP BY department;
-- FILTER is more readable and potentially faster
```

## Ordered-Set Aggregates

### Percentile Functions

```sql
-- Median (50th percentile)
SELECT 
    department,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY salary) as median_salary,
    PERCENTILE_DISC(0.5) WITHIN GROUP (ORDER BY salary) as median_salary_discrete
FROM employees
GROUP BY department;

-- Multiple percentiles
SELECT 
    department,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY salary) as p25,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY salary) as p50_median,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY salary) as p75,
    PERCENTILE_CONT(0.90) WITHIN GROUP (ORDER BY salary) as p90
FROM employees
GROUP BY department;

-- Array of percentiles
SELECT 
    department,
    PERCENTILE_CONT(ARRAY[0.25, 0.5, 0.75, 0.95]) 
        WITHIN GROUP (ORDER BY salary) as quartiles
FROM employees
GROUP BY department;
```

### MODE

```sql
-- Most common value
SELECT 
    department,
    MODE() WITHIN GROUP (ORDER BY job_title) as most_common_title
FROM employees
GROUP BY department;

-- Most common order amount
SELECT 
    customer_tier,
    MODE() WITHIN GROUP (ORDER BY total_amount) as typical_order_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
GROUP BY customer_tier;
```

## Statistical Aggregates

```sql
-- Variance and Standard Deviation
SELECT 
    department,
    COUNT(*) as employee_count,
    AVG(salary) as avg_salary,
    STDDEV(salary) as salary_stddev,           -- Sample std dev
    STDDEV_POP(salary) as salary_stddev_pop,   -- Population std dev
    VARIANCE(salary) as salary_variance,        -- Sample variance
    VAR_POP(salary) as salary_var_pop          -- Population variance
FROM employees
GROUP BY department;

-- Coefficient of variation (relative variability)
SELECT 
    product_category,
    AVG(price) as avg_price,
    STDDEV(price) as price_stddev,
    STDDEV(price) / NULLIF(AVG(price), 0) as coefficient_of_variation
FROM products
GROUP BY product_category;

-- Correlation
SELECT 
    CORR(temperature, ice_cream_sales) as temp_sales_correlation,
    REGR_R2(ice_cream_sales, temperature) as r_squared
FROM daily_sales;

-- Linear regression
SELECT 
    REGR_SLOPE(y, x) as slope,
    REGR_INTERCEPT(y, x) as intercept,
    REGR_R2(y, x) as r_squared,
    REGR_COUNT(y, x) as point_count
FROM data_points;

-- Covariance
SELECT 
    department,
    COVAR_POP(years_experience, salary) as experience_salary_covar
FROM employees
GROUP BY department;
```

## Custom Aggregates

### Creating Custom Aggregate Functions

```sql
-- Create a custom aggregate for geometric mean
CREATE AGGREGATE geometric_mean (float8) (
    SFUNC = float8mul,          -- State transition function
    STYPE = float8,             -- State data type
    FINALFUNC = exp,            -- Final calculation
    INITCOND = '0'             -- Initial condition
);

-- Usage
SELECT 
    product_category,
    geometric_mean(growth_rate) as avg_growth_rate
FROM product_growth
GROUP BY product_category;

-- Custom aggregate with multiple columns
CREATE TYPE median_state AS (
    values float8[],
    count int
);

-- More complex custom aggregates require writing functions
```

## Performance Optimization

### Indexing for GROUP BY

```sql
-- Create index on GROUP BY columns
CREATE INDEX idx_employees_dept_salary 
ON employees(department, salary);

-- Covering index for better performance
CREATE INDEX idx_orders_customer_amount 
ON orders(customer_id) 
INCLUDE (total_amount, order_date);

-- Partial index for filtered aggregates
CREATE INDEX idx_recent_orders 
ON orders(customer_id, total_amount)
WHERE order_date > '2024-01-01';
```

### Materialized Views for Heavy Aggregations

```sql
-- Create materialized view for expensive aggregations
CREATE MATERIALIZED VIEW monthly_sales_summary AS
SELECT 
    DATE_TRUNC('month', order_date) as month,
    product_category,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue,
    AVG(total_amount) as avg_order_value,
    COUNT(DISTINCT customer_id) as unique_customers
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY DATE_TRUNC('month', order_date), product_category;

-- Create indexes on materialized view
CREATE INDEX idx_monthly_summary_month 
ON monthly_sales_summary(month);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales_summary;
```

### Parallel Aggregation

```sql
-- Enable parallel aggregation
SET max_parallel_workers_per_gather = 4;

-- Check if query uses parallel aggregation
EXPLAIN (ANALYZE, BUFFERS)
SELECT 
    department,
    COUNT(*),
    AVG(salary)
FROM large_employee_table
GROUP BY department;
```

## Best Practices

1. **Use Appropriate Aggregates**: Choose FILTER over CASE when possible for readability
2. **Index GROUP BY Columns**: Essential for performance on large tables
3. **Consider Materialized Views**: For expensive aggregations run frequently
4. **Use HAVING Wisely**: Filter after grouping, use WHERE for row filtering
5. **Leverage GROUPING SETS**: Instead of UNION ALL for multiple grouping levels
6. **Handle NULLs**: Remember COUNT(column) excludes NULLs, COUNT(*) includes them
7. **Use DISTINCT Carefully**: COUNT(DISTINCT) can be expensive on large datasets

## Common Pitfalls

### 1. Mixing Aggregated and Non-Aggregated Columns

```sql
-- ERROR: column must appear in GROUP BY or aggregate
SELECT department, employee_name, AVG(salary)
FROM employees
GROUP BY department;

-- CORRECT: Include all non-aggregated columns in GROUP BY
SELECT department, employee_name, AVG(salary)
FROM employees
GROUP BY department, employee_name;
```

### 2. NULL Handling

```sql
-- COUNT(*) includes rows with NULL values
-- COUNT(column) excludes NULLs
SELECT 
    COUNT(*) as total_rows,            -- Includes NULL emails
    COUNT(email) as rows_with_email,   -- Excludes NULL emails
    COUNT(DISTINCT email) as unique_emails
FROM customers;

-- Use COALESCE for NULL replacement
SELECT 
    COALESCE(region, 'Unknown') as region,
    COUNT(*) as customer_count
FROM customers
GROUP BY region;
```

### 3. HAVING vs WHERE

```sql
-- WRONG: Can't use aggregate in WHERE
SELECT department, AVG(salary) as avg_sal
FROM employees
WHERE AVG(salary) > 50000  -- ERROR!
GROUP BY department;

-- CORRECT: Use HAVING for aggregate conditions
SELECT department, AVG(salary) as avg_sal
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;
```

### 4. String Aggregation Order

```sql
-- Order matters for STRING_AGG
SELECT 
    department,
    STRING_AGG(employee_name, ', ' ORDER BY employee_name) as employees
FROM employees
GROUP BY department;
-- Always specify ORDER BY for predictable results
```

## Summary

PostgreSQL aggregation and grouping provides:
- **Aggregate functions**: COUNT, SUM, AVG, MIN, MAX, and many more
- **GROUP BY**: Organize data into groups for aggregation
- **HAVING**: Filter groups after aggregation
- **Advanced grouping**: ROLLUP, CUBE, GROUPING SETS for multi-level analysis
- **FILTER clause**: Conditional aggregation
- **Statistical functions**: Percentiles, variance, correlation
- **Performance options**: Indexes, materialized views, parallel execution

## Next Steps

- Learn about [Window Functions](./13-window-functions.md) for advanced analytics
- Explore [Common Table Expressions](./14-common-table-expressions.md) for complex queries
- Study [Query Optimization](./20-query-optimization.md) for performance tuning
- Practice [Advanced SELECT Queries](./11-advanced-select-queries.md)
