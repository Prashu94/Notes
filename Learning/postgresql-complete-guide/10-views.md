# Views

## Overview

Views are virtual tables based on SQL queries. They don't store data themselves but provide a way to:
- Simplify complex queries
- Provide data abstraction
- Implement security (show only certain columns/rows)
- Maintain backward compatibility

## Simple Views

### Creating Views

```sql
-- Basic view
CREATE VIEW active_customers AS
SELECT 
    customer_id,
    name,
    email,
    created_at
FROM customers
WHERE is_active = TRUE;

-- Query the view
SELECT * FROM active_customers;

-- View with joins
CREATE VIEW order_summary AS
SELECT 
    o.order_id,
    c.name AS customer_name,
    o.order_date,
    o.total,
    o.status
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id;

-- View with aggregation
CREATE VIEW customer_stats AS
SELECT 
    c.customer_id,
    c.name,
    COUNT(o.order_id) AS total_orders,
    COALESCE(SUM(o.total), 0) AS lifetime_value,
    MAX(o.order_date) AS last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name;
```

### View Information

```sql
-- List all views
\dv

-- View definition
\d+ view_name

-- Get view definition
SELECT definition FROM pg_views WHERE viewname = 'active_customers';

-- All views in schema
SELECT 
    schemaname,
    viewname,
    viewowner
FROM pg_views
WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
```

### Modifying Views

```sql
-- Replace view (OR REPLACE)
CREATE OR REPLACE VIEW active_customers AS
SELECT 
    customer_id,
    name,
    email,
    phone,  -- Added column
    created_at
FROM customers
WHERE is_active = TRUE AND deleted_at IS NULL;

-- Rename view
ALTER VIEW active_customers RENAME TO current_customers;

-- Change owner
ALTER VIEW active_customers OWNER TO new_owner;

-- Drop view
DROP VIEW active_customers;
DROP VIEW IF EXISTS active_customers;
DROP VIEW IF EXISTS view1, view2, view3;

-- Drop with CASCADE (also drop dependent views)
DROP VIEW active_customers CASCADE;
```

## Updatable Views

### INSERT, UPDATE, DELETE on Views

```sql
-- Simple updatable view
CREATE VIEW active_users AS
SELECT user_id, username, email
FROM users
WHERE is_active = TRUE;

-- These work automatically if view is simple enough
INSERT INTO active_users (username, email) VALUES ('john', 'john@example.com');
UPDATE active_users SET email = 'newemail@example.com' WHERE user_id = 1;
DELETE FROM active_users WHERE user_id = 1;

-- View must meet conditions:
-- - FROM one table only
-- - No DISTINCT, GROUP BY, HAVING, LIMIT, OFFSET
-- - No set operations (UNION, INTERSECT, EXCEPT)
-- - No aggregate or window functions
```

### WITH CHECK OPTION

```sql
-- Prevent inserts/updates that don't match view condition
CREATE VIEW active_users AS
SELECT user_id, username, email, is_active
FROM users
WHERE is_active = TRUE
WITH CHECK OPTION;

-- This fails: is_active = FALSE doesn't match view condition
INSERT INTO active_users VALUES (1, 'john', 'john@example.com', FALSE);
-- ERROR: new row violates check option

-- WITH LOCAL CHECK OPTION vs WITH CASCADED CHECK OPTION
CREATE VIEW high_value_customers AS
SELECT * FROM active_customers  -- Base view has WHERE condition
WHERE lifetime_value > 10000
WITH LOCAL CHECK OPTION;  -- Only checks this view's condition

CREATE VIEW high_value_customers AS
SELECT * FROM active_customers
WHERE lifetime_value > 10000
WITH CASCADED CHECK OPTION;  -- Checks all view conditions in hierarchy
```

### Instead-Of Triggers

```sql
-- Make complex views updatable with triggers
CREATE VIEW order_details AS
SELECT 
    o.order_id,
    c.name AS customer_name,
    p.product_name,
    oi.quantity
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id;

-- Create INSTEAD OF trigger
CREATE OR REPLACE FUNCTION update_order_details()
RETURNS TRIGGER AS $$
BEGIN
    -- Update logic here
    UPDATE order_items
    SET quantity = NEW.quantity
    WHERE order_id = NEW.order_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_order_details
INSTEAD OF UPDATE ON order_details
FOR EACH ROW EXECUTE FUNCTION update_order_details();
```

## Materialized Views

### Overview

Materialized views store query results physically, unlike regular views.

```sql
-- Create materialized view
CREATE MATERIALIZED VIEW customer_monthly_sales AS
SELECT 
    customer_id,
    DATE_TRUNC('month', order_date) AS month,
    COUNT(*) AS order_count,
    SUM(total) AS total_sales
FROM orders
GROUP BY customer_id, DATE_TRUNC('month', order_date);

-- Create index on materialized view
CREATE INDEX idx_customer_monthly_sales_customer 
ON customer_monthly_sales(customer_id);

CREATE INDEX idx_customer_monthly_sales_month 
ON customer_monthly_sales(month);

-- Query materialized view (fast - data is pre-computed)
SELECT * FROM customer_monthly_sales
WHERE customer_id = 1;
```

### Refreshing Materialized Views

```sql
-- Full refresh (locks view)
REFRESH MATERIALIZED VIEW customer_monthly_sales;

-- Concurrent refresh (requires UNIQUE index, no lock)
CREATE UNIQUE INDEX idx_customer_monthly_pk 
ON customer_monthly_sales(customer_id, month);

REFRESH MATERIALIZED VIEW CONCURRENTLY customer_monthly_sales;

-- Automated refresh with cron/pg_cron
CREATE EXTENSION pg_cron;

-- Refresh daily at 2 AM
SELECT cron.schedule('refresh-customer-sales', '0 2 * * *', 
    'REFRESH MATERIALIZED VIEW CONCURRENTLY customer_monthly_sales');
```

### Drop Materialized View

```sql
DROP MATERIALIZED VIEW customer_monthly_sales;
DROP MATERIALIZED VIEW IF EXISTS customer_monthly_sales;
```

## Recursive Views

```sql
-- Recursive CTE in view
CREATE VIEW employee_hierarchy AS
WITH RECURSIVE emp_tree AS (
    -- Base case: top-level employees
    SELECT employee_id, name, manager_id, 0 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- Recursive case
    SELECT e.employee_id, e.name, e.manager_id, et.level + 1
    FROM employees e
    JOIN emp_tree et ON e.manager_id = et.employee_id
)
SELECT * FROM emp_tree;

-- Query hierarchy
SELECT * FROM employee_hierarchy ORDER BY level, name;
```

## Security with Views

```sql
-- Hide sensitive columns
CREATE VIEW public_user_info AS
SELECT 
    user_id,
    username,
    email,
    created_at
    -- password_hash is hidden
FROM users;

-- Row-level security through views
CREATE VIEW my_orders AS
SELECT *
FROM orders
WHERE user_id = current_setting('app.current_user_id')::INTEGER;

-- Grant access to view, not base table
REVOKE ALL ON users FROM public;
GRANT SELECT ON public_user_info TO public;
```

## Best Practices

```sql
-- 1. Name views clearly
CREATE VIEW vw_active_customers AS ...  -- Prefix with vw_
CREATE VIEW active_customers_view AS ...  -- Suffix with _view

-- 2. Add comments
COMMENT ON VIEW active_customers IS 
'Contains only active customers (is_active = TRUE and deleted_at IS NULL)';

-- 3. Use for complex, repeated queries
CREATE VIEW order_fulfillment_status AS
SELECT 
    o.order_id,
    o.order_date,
    o.status AS order_status,
    s.shipped_date,
    s.carrier,
    s.tracking_number,
    d.delivered_date,
    CASE 
        WHEN d.delivered_date IS NOT NULL THEN 'Delivered'
        WHEN s.shipped_date IS NOT NULL THEN 'In Transit'
        WHEN o.status = 'processing' THEN 'Processing'
        ELSE 'Pending'
    END AS fulfillment_status
FROM orders o
LEFT JOIN shipments s ON o.order_id = s.order_id
LEFT JOIN deliveries d ON s.shipment_id = d.shipment_id;

-- 4. Index materialized views
-- 5. Refresh materialized views regularly
-- 6. Monitor view performance

SELECT 
    schemaname,
    viewname,
    pg_size_pretty(pg_relation_size(schemaname||'.'||viewname)) AS size
FROM pg_views
WHERE schemaname = 'public';
```

## Summary

- **Regular Views**: Virtual tables, no storage
- **Materialized Views**: Physical storage, requires refresh
- **Updatable Views**: Can INSERT/UPDATE/DELETE  
- **Security**: Hide columns/rows, implement access control
- Use views for abstraction and simplification
