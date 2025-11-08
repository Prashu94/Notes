# Joins and Subqueries

## Overview

Joins combine rows from two or more tables based on related columns. Subqueries are nested queries used within other queries.

## Sample Data Setup

```sql
-- Create sample tables
CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(255),
    country VARCHAR(50)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date DATE,
    total DECIMAL(10, 2)
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE order_items (
    order_item_id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    unit_price DECIMAL(10, 2)
);

-- Insert sample data
INSERT INTO customers (name, email, country) VALUES
    ('John Doe', 'john@example.com', 'USA'),
    ('Jane Smith', 'jane@example.com', 'UK'),
    ('Bob Johnson', 'bob@example.com', 'Canada'),
    ('Alice Williams', 'alice@example.com', 'USA');

INSERT INTO orders (customer_id, order_date, total) VALUES
    (1, '2024-01-15', 150.00),
    (1, '2024-02-20', 200.00),
    (2, '2024-01-10', 300.00),
    (3, '2024-03-05', 100.00);

INSERT INTO products (product_name, category, price) VALUES
    ('Laptop', 'Electronics', 999.99),
    ('Mouse', 'Electronics', 29.99),
    ('Keyboard', 'Electronics', 79.99),
    ('Desk', 'Furniture', 299.99);

INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES
    (1, 2, 2, 29.99),
    (1, 3, 1, 79.99),
    (2, 1, 1, 999.99),
    (3, 4, 1, 299.99);
```

## INNER JOIN

### Basic INNER JOIN

Returns rows that have matching values in both tables.

```sql
-- Get orders with customer names
SELECT 
    o.order_id,
    c.name AS customer_name,
    o.order_date,
    o.total
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;

-- Explicit INNER keyword (same as above)
SELECT 
    o.order_id,
    c.name,
    o.total
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- Multiple conditions
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id 
    AND c.country = 'USA';
```

### Multi-Table INNER JOIN

```sql
-- Join three tables
SELECT 
    c.name AS customer_name,
    o.order_id,
    o.order_date,
    p.product_name,
    oi.quantity,
    oi.unit_price,
    (oi.quantity * oi.unit_price) AS line_total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Four or more tables
SELECT 
    c.name,
    o.order_id,
    p.product_name,
    p.category,
    oi.quantity
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE p.category = 'Electronics'
ORDER BY c.name, o.order_date;
```

## LEFT JOIN (LEFT OUTER JOIN)

### Basic LEFT JOIN

Returns all rows from the left table and matched rows from the right table. NULL for non-matching right rows.

```sql
-- All customers and their orders (including customers with no orders)
SELECT 
    c.customer_id,
    c.name,
    o.order_id,
    o.total
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id;

-- Find customers with no orders
SELECT 
    c.customer_id,
    c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- Count orders per customer (including zero)
SELECT 
    c.name,
    COUNT(o.order_id) AS order_count,
    COALESCE(SUM(o.total), 0) AS total_spent
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name
ORDER BY total_spent DESC;
```

### Multiple LEFT JOINs

```sql
-- All customers with their orders and order items
SELECT 
    c.name,
    o.order_id,
    o.order_date,
    oi.product_id,
    oi.quantity
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id;

-- Complex reporting query
SELECT 
    c.name AS customer_name,
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(oi.order_item_id) AS total_items,
    COALESCE(SUM(o.total), 0) AS total_revenue
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
LEFT JOIN order_items oi ON o.order_id = oi.order_id
GROUP BY c.customer_id, c.name;
```

## RIGHT JOIN (RIGHT OUTER JOIN)

### Basic RIGHT JOIN

Returns all rows from the right table and matched rows from the left table. NULL for non-matching left rows.

```sql
-- All orders and their customers
SELECT 
    c.name,
    o.order_id,
    o.total
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id;

-- Find orders without customers (orphaned records)
SELECT 
    o.order_id,
    o.total
FROM customers c
RIGHT JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL;

-- Note: RIGHT JOIN is less common; usually rewritten as LEFT JOIN
-- This RIGHT JOIN:
SELECT * FROM customers c RIGHT JOIN orders o ON c.customer_id = o.customer_id;

-- Can be rewritten as LEFT JOIN:
SELECT * FROM orders o LEFT JOIN customers c ON o.customer_id = c.customer_id;
```

## FULL OUTER JOIN

### Basic FULL OUTER JOIN

Returns all rows from both tables, with NULL for non-matching rows.

```sql
-- All customers and all orders, matched where possible
SELECT 
    c.customer_id,
    c.name,
    o.order_id,
    o.total
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;

-- Find unmatched records in either table
SELECT 
    c.name,
    o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id
WHERE c.customer_id IS NULL OR o.order_id IS NULL;

-- Data quality check: Find orphaned records
SELECT 
    CASE 
        WHEN c.customer_id IS NULL THEN 'Orphaned Order'
        WHEN o.order_id IS NULL THEN 'Customer Without Orders'
        ELSE 'Matched'
    END AS status,
    c.name,
    o.order_id
FROM customers c
FULL OUTER JOIN orders o ON c.customer_id = o.customer_id;
```

## CROSS JOIN

### Basic CROSS JOIN

Returns the Cartesian product of both tables (every combination).

```sql
-- All possible combinations
SELECT 
    c.name,
    p.product_name
FROM customers c
CROSS JOIN products p;

-- Useful for generating combinations
SELECT 
    d.date,
    s.store_id
FROM generate_series('2024-01-01'::date, '2024-01-31'::date, '1 day'::interval) AS d(date)
CROSS JOIN stores s;

-- Alternative syntax (implicit cross join)
SELECT 
    c.name,
    p.product_name
FROM customers c, products p;

-- Practical example: Sales matrix
SELECT 
    p.product_name,
    m.month,
    COALESCE(SUM(s.quantity), 0) AS total_sold
FROM products p
CROSS JOIN (SELECT generate_series(1, 12) AS month) m
LEFT JOIN sales s ON p.product_id = s.product_id 
    AND EXTRACT(MONTH FROM s.sale_date) = m.month
GROUP BY p.product_name, m.month
ORDER BY p.product_name, m.month;
```

## SELF JOIN

### Basic SELF JOIN

Joining a table to itself.

```sql
-- Employee hierarchy
CREATE TABLE employees (
    emp_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    manager_id INTEGER REFERENCES employees(emp_id)
);

INSERT INTO employees (name, manager_id) VALUES
    ('CEO', NULL),
    ('VP Sales', 1),
    ('VP Engineering', 1),
    ('Sales Rep 1', 2),
    ('Sales Rep 2', 2),
    ('Engineer 1', 3);

-- Find employees and their managers
SELECT 
    e.name AS employee,
    m.name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.emp_id;

-- Find all employees reporting to VP Sales
SELECT 
    e.name AS employee
FROM employees e
JOIN employees m ON e.manager_id = m.emp_id
WHERE m.name = 'VP Sales';

-- Find pairs of employees with same manager
SELECT 
    e1.name AS employee1,
    e2.name AS employee2,
    m.name AS shared_manager
FROM employees e1
JOIN employees e2 ON e1.manager_id = e2.manager_id 
    AND e1.emp_id < e2.emp_id  -- Avoid duplicates
JOIN employees m ON e1.manager_id = m.emp_id;
```

## USING Clause

### Simplified JOIN Syntax

When join columns have the same name.

```sql
-- Instead of ON clause
SELECT *
FROM orders
JOIN customers USING (customer_id);

-- Multiple columns
SELECT *
FROM order_items
JOIN orders USING (order_id);

-- Equivalent to:
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- USING automatically removes duplicate column
SELECT *
FROM orders
JOIN customers USING (customer_id);
-- customer_id appears once

SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;
-- customer_id appears twice (o.customer_id and c.customer_id)
```

## NATURAL JOIN

### Automatic JOIN on Common Columns

**Warning**: Rarely used, can be unpredictable.

```sql
-- Joins on all columns with same name
SELECT *
FROM orders
NATURAL JOIN customers;

-- Equivalent to:
SELECT *
FROM orders
JOIN customers USING (customer_id);  -- Assumes only customer_id is common

-- Dangerous if tables have multiple common column names
-- Avoid in production code!
```

## Subqueries in WHERE

### Scalar Subqueries

```sql
-- Find products more expensive than average
SELECT product_name, price
FROM products
WHERE price > (SELECT AVG(price) FROM products);

-- Customers who spent more than average
SELECT name
FROM customers c
WHERE (
    SELECT COALESCE(SUM(total), 0)
    FROM orders o
    WHERE o.customer_id = c.customer_id
) > (
    SELECT AVG(total)
    FROM orders
);
```

### IN Subqueries

```sql
-- Customers who placed orders
SELECT name
FROM customers
WHERE customer_id IN (
    SELECT customer_id 
    FROM orders
);

-- Products never ordered
SELECT product_name
FROM products
WHERE product_id NOT IN (
    SELECT product_id 
    FROM order_items
    WHERE product_id IS NOT NULL
);

-- Customers from countries with orders
SELECT *
FROM customers
WHERE country IN (
    SELECT DISTINCT c.country
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
);
```

### EXISTS Subqueries

```sql
-- Customers with orders (more efficient than IN for large datasets)
SELECT name
FROM customers c
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- Customers without orders
SELECT name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- Products ordered more than once
SELECT product_name
FROM products p
WHERE EXISTS (
    SELECT 1
    FROM order_items oi
    WHERE oi.product_id = p.product_id
    GROUP BY oi.product_id
    HAVING SUM(quantity) > 1
);
```

### ANY/ALL Subqueries

```sql
-- Products more expensive than any electronic item
SELECT product_name, price
FROM products
WHERE price > ANY (
    SELECT price 
    FROM products 
    WHERE category = 'Electronics'
);

-- Products more expensive than all furniture items
SELECT product_name, price
FROM products
WHERE price > ALL (
    SELECT price 
    FROM products 
    WHERE category = 'Furniture'
);

-- Customers with any order above $200
SELECT name
FROM customers c
WHERE 200 < ANY (
    SELECT total 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);
```

## Subqueries in SELECT

### Correlated Subqueries

```sql
-- Show each customer with their total spent
SELECT 
    name,
    (SELECT COUNT(*) 
     FROM orders o 
     WHERE o.customer_id = c.customer_id) AS order_count,
    (SELECT COALESCE(SUM(total), 0) 
     FROM orders o 
     WHERE o.customer_id = c.customer_id) AS total_spent
FROM customers c;

-- Product with its category average
SELECT 
    product_name,
    price,
    (SELECT AVG(price) 
     FROM products p2 
     WHERE p2.category = p1.category) AS category_avg,
    price - (SELECT AVG(price) 
             FROM products p2 
             WHERE p2.category = p1.category) AS price_diff
FROM products p1;
```

### Window Functions Alternative

```sql
-- Instead of correlated subquery
SELECT 
    product_name,
    price,
    AVG(price) OVER (PARTITION BY category) AS category_avg
FROM products;
-- Much more efficient than subquery for this purpose
```

## Subqueries in FROM

### Derived Tables

```sql
-- Query a subquery result
SELECT 
    category,
    avg_price
FROM (
    SELECT 
        category,
        AVG(price) AS avg_price
    FROM products
    GROUP BY category
) AS category_stats
WHERE avg_price > 100;

-- Complex aggregation
SELECT 
    customer_summary.name,
    customer_summary.order_count,
    customer_summary.total_spent
FROM (
    SELECT 
        c.name,
        COUNT(o.order_id) AS order_count,
        SUM(o.total) AS total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
) AS customer_summary
WHERE order_count > 1;

-- Multi-level aggregation
SELECT 
    AVG(order_count) AS avg_orders_per_customer
FROM (
    SELECT 
        customer_id,
        COUNT(*) AS order_count
    FROM orders
    GROUP BY customer_id
) AS customer_orders;
```

## Common Table Expressions (CTEs)

### Basic CTE

```sql
-- Cleaner alternative to subqueries in FROM
WITH customer_stats AS (
    SELECT 
        c.customer_id,
        c.name,
        COUNT(o.order_id) AS order_count,
        COALESCE(SUM(o.total), 0) AS total_spent
    FROM customers c
    LEFT JOIN orders o ON c.customer_id = o.customer_id
    GROUP BY c.customer_id, c.name
)
SELECT *
FROM customer_stats
WHERE order_count > 1
ORDER BY total_spent DESC;

-- Multiple CTEs
WITH 
product_sales AS (
    SELECT 
        p.product_id,
        p.product_name,
        COALESCE(SUM(oi.quantity), 0) AS total_sold
    FROM products p
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    GROUP BY p.product_id, p.product_name
),
category_sales AS (
    SELECT 
        p.category,
        SUM(ps.total_sold) AS category_total
    FROM products p
    JOIN product_sales ps ON p.product_id = ps.product_id
    GROUP BY p.category
)
SELECT *
FROM category_sales
ORDER BY category_total DESC;
```

## LATERAL Joins

### Overview

LATERAL allows subqueries to reference columns from preceding tables.

```sql
-- Top 2 orders per customer
SELECT 
    c.name,
    top_orders.order_id,
    top_orders.total
FROM customers c
LEFT JOIN LATERAL (
    SELECT order_id, total
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY total DESC
    LIMIT 2
) AS top_orders ON TRUE;

-- Recent order for each customer
SELECT 
    c.name,
    recent.order_date,
    recent.total
FROM customers c
LEFT JOIN LATERAL (
    SELECT order_date, total
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY order_date DESC
    LIMIT 1
) AS recent ON TRUE;

-- Calculate running total
SELECT 
    o1.order_id,
    o1.total,
    running_total.sum
FROM orders o1
CROSS JOIN LATERAL (
    SELECT SUM(total) AS sum
    FROM orders o2
    WHERE o2.order_id <= o1.order_id
) AS running_total
ORDER BY o1.order_id;
```

## JOIN Performance Tips

### 1. Index Join Columns

```sql
-- Always index foreign keys
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
```

### 2. JOIN Order Matters

```sql
-- Start with smallest table or most filtered
-- Good:
SELECT *
FROM small_filtered_table s
JOIN large_table l ON s.id = l.small_id;

-- Less efficient:
SELECT *
FROM large_table l
JOIN small_filtered_table s ON l.small_id = s.id;

-- PostgreSQL query planner usually optimizes this automatically
```

### 3. Avoid SELECT *

```sql
-- Bad: Fetches all columns
SELECT *
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;

-- Good: Select only needed columns
SELECT 
    c.name,
    o.order_id,
    o.total
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id;
```

### 4. Use EXISTS Instead of IN for Large Sets

```sql
-- Less efficient with large subquery results
SELECT name
FROM customers
WHERE customer_id IN (
    SELECT customer_id FROM orders  -- Could be millions
);

-- More efficient
SELECT name
FROM customers c
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```

## Common Patterns

### Find Records Without Match

```sql
-- LEFT JOIN with WHERE IS NULL
SELECT c.name
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
WHERE o.order_id IS NULL;

-- NOT EXISTS (usually more efficient)
SELECT c.name
FROM customers c
WHERE NOT EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.customer_id
);
```

### Top N per Group

```sql
-- Using LATERAL
SELECT 
    c.name,
    top3.order_id,
    top3.total
FROM customers c
CROSS JOIN LATERAL (
    SELECT order_id, total
    FROM orders o
    WHERE o.customer_id = c.customer_id
    ORDER BY total DESC
    LIMIT 3
) AS top3;

-- Using window functions (usually better)
WITH ranked_orders AS (
    SELECT 
        c.name,
        o.order_id,
        o.total,
        ROW_NUMBER() OVER (PARTITION BY c.customer_id ORDER BY o.total DESC) AS rn
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
)
SELECT name, order_id, total
FROM ranked_orders
WHERE rn <= 3;
```

## Summary

**JOIN Types**:
- **INNER JOIN**: Matching rows only
- **LEFT JOIN**: All left rows + matches
- **RIGHT JOIN**: All right rows + matches  
- **FULL OUTER JOIN**: All rows from both
- **CROSS JOIN**: Cartesian product
- **SELF JOIN**: Table joined to itself

**Subquery Types**:
- **Scalar**: Returns single value
- **Row**: Returns single row
- **Table**: Returns multiple rows
- **Correlated**: References outer query

**Subquery Locations**:
- **WHERE**: Filtering
- **SELECT**: Calculated columns
- **FROM**: Derived tables
- **HAVING**: Group filtering

**Best Practices**:
- Index join columns
- Use EXISTS over IN for large sets
- Prefer CTEs over nested subqueries
- Use LATERAL for top-N-per-group
- Avoid SELECT *

**Next Topics**:
- [Window Functions](13-window-functions.md)
- [Common Table Expressions](14-common-table-expressions.md)
- [Query Optimization](20-query-optimization.md)
