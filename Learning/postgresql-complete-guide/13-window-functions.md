# Window Functions

## Overview

Window functions perform calculations across rows related to the current row, without grouping rows into a single output row like aggregate functions.

## Basic Syntax

```sql
function_name([expression]) OVER (
    [PARTITION BY partition_expression]
    [ORDER BY sort_expression [ASC | DESC]]
    [frame_clause]
)
```

## Sample Data

```sql
CREATE TABLE sales (
    sale_id SERIAL PRIMARY KEY,
    employee_id INTEGER,
    department VARCHAR(50),
    sale_date DATE,
    amount DECIMAL(10, 2)
);

INSERT INTO sales (employee_id, department, sale_date, amount) VALUES
    (1, 'Electronics', '2024-01-01', 1500),
    (1, 'Electronics', '2024-01-15', 2000),
    (2, 'Electronics', '2024-01-10', 1800),
    (2, 'Electronics', '2024-01-20', 2200),
    (3, 'Clothing', '2024-01-05', 800),
    (3, 'Clothing', '2024-01-25', 1200),
    (4, 'Clothing', '2024-01-12', 950),
    (4, 'Clothing', '2024-01-28', 1100);
```

## Ranking Functions

### ROW_NUMBER()

```sql
-- Assign unique number to each row
SELECT 
    employee_id,
    sale_date,
    amount,
    ROW_NUMBER() OVER (ORDER BY amount DESC) AS row_num
FROM sales;

-- Row number per partition
SELECT 
    employee_id,
    department,
    amount,
    ROW_NUMBER() OVER (
        PARTITION BY department 
        ORDER BY amount DESC
    ) AS dept_rank
FROM sales;
```

### RANK()

```sql
-- Rank with gaps for ties
SELECT 
    employee_id,
    amount,
    RANK() OVER (ORDER BY amount DESC) AS rank
FROM sales;

-- Department ranking
SELECT 
    employee_id,
    department,
    amount,
    RANK() OVER (
        PARTITION BY department 
        ORDER BY amount DESC
    ) AS dept_rank
FROM sales;
```

### DENSE_RANK()

```sql
-- Rank without gaps
SELECT 
    employee_id,
    amount,
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank
FROM sales;
```

### NTILE()

```sql
-- Divide rows into N groups
SELECT 
    employee_id,
    amount,
    NTILE(4) OVER (ORDER BY amount) AS quartile
FROM sales;

-- Top 25% of sales
SELECT *
FROM (
    SELECT 
        *,
        NTILE(4) OVER (ORDER BY amount DESC) AS quartile
    FROM sales
) sub
WHERE quartile = 1;
```

## Aggregate Window Functions

### Running Totals

```sql
-- Cumulative sum
SELECT 
    sale_date,
    amount,
    SUM(amount) OVER (
        ORDER BY sale_date
    ) AS running_total
FROM sales;

-- Running total per department
SELECT 
    department,
    sale_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY department
        ORDER BY sale_date
    ) AS dept_running_total
FROM sales;
```

### Moving Averages

```sql
-- 3-day moving average
SELECT 
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS moving_avg_3day
FROM sales;

-- 7-day moving average
SELECT 
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7day
FROM sales;
```

### MIN, MAX, COUNT

```sql
SELECT 
    employee_id,
    sale_date,
    amount,
    MIN(amount) OVER (PARTITION BY employee_id) AS min_sale,
    MAX(amount) OVER (PARTITION BY employee_id) AS max_sale,
    AVG(amount) OVER (PARTITION BY employee_id) AS avg_sale,
    COUNT(*) OVER (PARTITION BY employee_id) AS total_sales
FROM sales;
```

## Value Functions

### LEAD()

```sql
-- Get next row's value
SELECT 
    sale_date,
    amount,
    LEAD(amount) OVER (ORDER BY sale_date) AS next_amount,
    LEAD(amount, 2) OVER (ORDER BY sale_date) AS amount_2_ahead
FROM sales;

-- Calculate change from previous
SELECT 
    sale_date,
    amount,
    LEAD(amount) OVER (ORDER BY sale_date) AS next_amount,
    LEAD(amount) OVER (ORDER BY sale_date) - amount AS change
FROM sales;
```

### LAG()

```sql
-- Get previous row's value
SELECT 
    sale_date,
    amount,
    LAG(amount) OVER (ORDER BY sale_date) AS prev_amount,
    amount - LAG(amount) OVER (ORDER BY sale_date) AS change
FROM sales;

-- Month-over-month growth
SELECT 
    DATE_TRUNC('month', sale_date) AS month,
    SUM(amount) AS monthly_total,
    LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', sale_date)) AS prev_month,
    SUM(amount) - LAG(SUM(amount)) OVER (ORDER BY DATE_TRUNC('month', sale_date)) AS growth
FROM sales
GROUP BY DATE_TRUNC('month', sale_date);
```

### FIRST_VALUE() and LAST_VALUE()

```sql
-- First and last values in window
SELECT 
    employee_id,
    sale_date,
    amount,
    FIRST_VALUE(amount) OVER (
        PARTITION BY employee_id 
        ORDER BY sale_date
    ) AS first_sale,
    LAST_VALUE(amount) OVER (
        PARTITION BY employee_id 
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_sale
FROM sales;
```

### NTH_VALUE()

```sql
-- Get nth value in window
SELECT 
    employee_id,
    sale_date,
    amount,
    NTH_VALUE(amount, 2) OVER (
        PARTITION BY employee_id 
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS second_sale
FROM sales;
```

## Frame Clause

### ROWS vs RANGE

```sql
-- ROWS: Physical rows
SELECT 
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 1 PRECEDING AND 1 FOLLOWING
    ) AS avg_3rows
FROM sales;

-- RANGE: Logical range based on value
SELECT 
    sale_date,
    amount,
    AVG(amount) OVER (
        ORDER BY amount
        RANGE BETWEEN 100 PRECEDING AND 100 FOLLOWING
    ) AS avg_similar_amounts
FROM sales;
```

### Frame Specifications

```sql
-- Various frame specifications
SELECT 
    sale_date,
    amount,
    
    -- From start to current
    SUM(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_sum,
    
    -- Previous 3 rows
    AVG(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN 3 PRECEDING AND 1 PRECEDING
    ) AS prev_3_avg,
    
    -- Current and next 2
    MAX(amount) OVER (
        ORDER BY sale_date
        ROWS BETWEEN CURRENT ROW AND 2 FOLLOWING
    ) AS max_next_3,
    
    -- All rows in partition
    COUNT(*) OVER (
        PARTITION BY department
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS dept_total_count
FROM sales;
```

## Practical Examples

### Top N per Group

```sql
-- Top 3 sales per department
SELECT *
FROM (
    SELECT 
        department,
        employee_id,
        amount,
        ROW_NUMBER() OVER (
            PARTITION BY department 
            ORDER BY amount DESC
        ) AS rn
    FROM sales
) sub
WHERE rn <= 3;
```

### Deduplication

```sql
-- Keep only latest record per employee
DELETE FROM sales
WHERE sale_id IN (
    SELECT sale_id
    FROM (
        SELECT 
            sale_id,
            ROW_NUMBER() OVER (
                PARTITION BY employee_id 
                ORDER BY sale_date DESC
            ) AS rn
        FROM sales
    ) sub
    WHERE rn > 1
);
```

### Percentile Calculation

```sql
SELECT 
    employee_id,
    amount,
    PERCENT_RANK() OVER (ORDER BY amount) AS percent_rank,
    CUME_DIST() OVER (ORDER BY amount) AS cumulative_dist,
    NTILE(100) OVER (ORDER BY amount) AS percentile
FROM sales;
```

### Gap Detection

```sql
-- Find gaps in dates
SELECT 
    sale_date,
    LEAD(sale_date) OVER (ORDER BY sale_date) AS next_date,
    LEAD(sale_date) OVER (ORDER BY sale_date) - sale_date AS gap_days
FROM sales
WHERE LEAD(sale_date) OVER (ORDER BY sale_date) - sale_date > 1;
```

## Best Practices

1. Use appropriate window function for the task
2. PARTITION BY for grouping without collapsing rows
3. ORDER BY determines calculation order
4. Specify frame clause explicitly when needed
5. Index columns used in PARTITION BY and ORDER BY

## Summary

- **Ranking**: ROW_NUMBER, RANK, DENSE_RANK, NTILE
- **Aggregates**: SUM, AVG, MIN, MAX, COUNT  
- **Value**: LEAD, LAG, FIRST_VALUE, LAST_VALUE, NTH_VALUE
- **Frame**: Control which rows are included in calculation
- Powerful for analytics without self-joins
