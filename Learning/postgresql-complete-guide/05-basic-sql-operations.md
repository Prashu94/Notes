# Basic SQL Operations

## Database Operations

### Creating Databases

```sql
-- Create a simple database
CREATE DATABASE mydb;

-- Create database with options
CREATE DATABASE sales_db
    WITH
    OWNER = sales_user
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = 100;

-- Create database from template
CREATE DATABASE test_db TEMPLATE template0;

-- List all databases
\l
-- Or
SELECT datname FROM pg_database;
```

### Managing Databases

```sql
-- Connect to database
\c mydb
-- Or
\connect mydb

-- Rename database
ALTER DATABASE mydb RENAME TO new_db_name;

-- Change database owner
ALTER DATABASE mydb OWNER TO new_owner;

-- Drop database
DROP DATABASE mydb;

-- Drop if exists
DROP DATABASE IF EXISTS mydb;

-- Show current database
SELECT current_database();
```

## Schema Operations

```sql
-- Create schema
CREATE SCHEMA sales;
CREATE SCHEMA IF NOT EXISTS hr;
CREATE SCHEMA inventory AUTHORIZATION inventory_user;

-- List schemas
\dn
-- Or
SELECT schema_name FROM information_schema.schemata;

-- Set search path
SET search_path TO sales, public;
SHOW search_path;

-- Create table in specific schema
CREATE TABLE sales.orders (
    id SERIAL PRIMARY KEY,
    amount DECIMAL(10, 2)
);

-- Drop schema
DROP SCHEMA sales;
DROP SCHEMA sales CASCADE;  -- Drop with all objects
```

## Table Operations

### Creating Tables

```sql
-- Basic table creation
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Table with various constraints
CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(50),
    price NUMERIC(10, 2) CHECK (price > 0),
    stock_quantity INTEGER DEFAULT 0 CHECK (stock_quantity >= 0),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT unique_product_name UNIQUE (product_name),
    CONSTRAINT price_range CHECK (price BETWEEN 0.01 AND 999999.99)
);

-- Create table from query
CREATE TABLE high_value_products AS
SELECT * FROM products WHERE price > 1000;

-- Create table like another
CREATE TABLE products_backup (LIKE products INCLUDING ALL);

-- Temporary table (session-specific)
CREATE TEMP TABLE temp_data (
    id SERIAL,
    value TEXT
);

-- Unlogged table (faster but not crash-safe)
CREATE UNLOGGED TABLE cache_data (
    key TEXT PRIMARY KEY,
    value JSONB
);
```

### Table Information

```sql
-- List tables
\dt
\dt+  -- With size information

-- Describe table structure
\d users
\d+ users  -- Detailed info

-- Show table definition
\d+ products

-- Query information schema
SELECT 
    table_schema,
    table_name,
    table_type
FROM information_schema.tables
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_name;

-- Get table columns
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### Altering Tables

```sql
-- Add column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS middle_name TEXT;

-- Drop column
ALTER TABLE users DROP COLUMN phone;
ALTER TABLE users DROP COLUMN IF EXISTS middle_name;

-- Rename column
ALTER TABLE users RENAME COLUMN username TO user_name;

-- Change column type
ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(255);

-- Set/drop default
ALTER TABLE users ALTER COLUMN created_at SET DEFAULT NOW();
ALTER TABLE users ALTER COLUMN created_at DROP DEFAULT;

-- Set/drop NOT NULL
ALTER TABLE users ALTER COLUMN email SET NOT NULL;
ALTER TABLE users ALTER COLUMN email DROP NOT NULL;

-- Rename table
ALTER TABLE users RENAME TO app_users;

-- Change table owner
ALTER TABLE users OWNER TO new_owner;

-- Add constraint
ALTER TABLE products 
ADD CONSTRAINT check_price CHECK (price > 0);

-- Drop constraint
ALTER TABLE products 
DROP CONSTRAINT check_price;
```

### Dropping Tables

```sql
-- Drop single table
DROP TABLE users;

-- Drop if exists
DROP TABLE IF EXISTS users;

-- Drop multiple tables
DROP TABLE IF EXISTS users, products, orders;

-- Drop with CASCADE (also drops dependent objects)
DROP TABLE users CASCADE;

-- Truncate (delete all rows but keep table)
TRUNCATE TABLE users;
TRUNCATE TABLE users RESTART IDENTITY;  -- Reset serial columns
TRUNCATE TABLE users, products CASCADE;  -- Multiple tables
```

## INSERT Operations

### Basic INSERT

```sql
-- Insert single row
INSERT INTO users (username, email) 
VALUES ('john_doe', 'john@example.com');

-- Insert multiple rows
INSERT INTO users (username, email) VALUES 
    ('alice', 'alice@example.com'),
    ('bob', 'bob@example.com'),
    ('charlie', 'charlie@example.com');

-- Insert with all columns (not recommended)
INSERT INTO users VALUES 
    (DEFAULT, 'dave', 'dave@example.com', DEFAULT);

-- Insert with subquery
INSERT INTO products_archive 
SELECT * FROM products WHERE is_active = FALSE;
```

### INSERT with RETURNING

```sql
-- Return inserted row
INSERT INTO users (username, email) 
VALUES ('eve', 'eve@example.com')
RETURNING *;

-- Return specific columns
INSERT INTO products (product_name, price) 
VALUES ('New Product', 99.99)
RETURNING product_id, created_at;

-- Return multiple rows
INSERT INTO orders (user_id, total) VALUES 
    (1, 100.00),
    (2, 150.00)
RETURNING order_id, total;
```

### INSERT with ON CONFLICT (UPSERT)

```sql
-- Ignore conflicts
INSERT INTO users (username, email) 
VALUES ('john_doe', 'newemail@example.com')
ON CONFLICT (username) DO NOTHING;

-- Update on conflict
INSERT INTO users (username, email, updated_at) 
VALUES ('john_doe', 'updated@example.com', NOW())
ON CONFLICT (username) 
DO UPDATE SET 
    email = EXCLUDED.email,
    updated_at = EXCLUDED.updated_at;

-- Complex upsert with WHERE clause
INSERT INTO products (product_name, price, stock_quantity) 
VALUES ('Widget', 29.99, 100)
ON CONFLICT (product_name) 
DO UPDATE SET 
    price = EXCLUDED.price,
    stock_quantity = products.stock_quantity + EXCLUDED.stock_quantity,
    updated_at = NOW()
WHERE products.price != EXCLUDED.price;
```

### INSERT DEFAULT VALUES

```sql
-- Insert with all defaults
INSERT INTO users DEFAULT VALUES;

-- Insert specific defaults
INSERT INTO products (product_name, price) 
VALUES ('Item', DEFAULT);
```

## SELECT Operations

### Basic SELECT

```sql
-- Select all columns
SELECT * FROM users;

-- Select specific columns
SELECT username, email FROM users;

-- Select with alias
SELECT 
    username AS user,
    email AS email_address,
    created_at AS registration_date
FROM users;

-- Select distinct values
SELECT DISTINCT category FROM products;

-- Select with LIMIT
SELECT * FROM users LIMIT 10;

-- Select with OFFSET (pagination)
SELECT * FROM users LIMIT 10 OFFSET 20;

-- Better pagination (use WHERE with index)
SELECT * FROM users 
WHERE id > 20 
ORDER BY id 
LIMIT 10;
```

### WHERE Clause

```sql
-- Basic conditions
SELECT * FROM products WHERE price > 50;
SELECT * FROM products WHERE category = 'Electronics';
SELECT * FROM users WHERE created_at >= '2024-01-01';

-- Multiple conditions (AND)
SELECT * FROM products 
WHERE category = 'Electronics' 
  AND price BETWEEN 100 AND 500
  AND stock_quantity > 0;

-- Multiple conditions (OR)
SELECT * FROM users 
WHERE username = 'john' 
   OR email LIKE '%@example.com';

-- NOT condition
SELECT * FROM products WHERE NOT category = 'Electronics';

-- IN clause
SELECT * FROM products 
WHERE category IN ('Electronics', 'Computers', 'Phones');

-- BETWEEN
SELECT * FROM orders 
WHERE order_date BETWEEN '2024-01-01' AND '2024-12-31';

-- LIKE (pattern matching)
SELECT * FROM users WHERE email LIKE '%@gmail.com';
SELECT * FROM products WHERE product_name LIKE 'A%';     -- Starts with A
SELECT * FROM products WHERE product_name LIKE '%Pro%';  -- Contains Pro
SELECT * FROM products WHERE product_name LIKE '_Phone'; -- One char + Phone

-- ILIKE (case-insensitive)
SELECT * FROM users WHERE username ILIKE 'john%';

-- Regular expressions
SELECT * FROM users WHERE email ~ '^[a-z]+@[a-z]+\.[a-z]+$';
SELECT * FROM users WHERE email ~* '^admin';  -- Case-insensitive

-- NULL checks
SELECT * FROM products WHERE description IS NULL;
SELECT * FROM products WHERE description IS NOT NULL;

-- Boolean checks
SELECT * FROM products WHERE is_active;
SELECT * FROM products WHERE NOT is_active;
```

### ORDER BY

```sql
-- Ascending order (default)
SELECT * FROM products ORDER BY price;
SELECT * FROM products ORDER BY price ASC;

-- Descending order
SELECT * FROM products ORDER BY price DESC;

-- Multiple columns
SELECT * FROM products 
ORDER BY category ASC, price DESC;

-- Order by expression
SELECT * FROM users 
ORDER BY LENGTH(username);

-- Order with NULLS FIRST/LAST
SELECT * FROM products 
ORDER BY description NULLS LAST;
```

### LIMIT and OFFSET

```sql
-- First 10 rows
SELECT * FROM users LIMIT 10;

-- Skip first 10, get next 10
SELECT * FROM users LIMIT 10 OFFSET 10;

-- Page 3 (rows 21-30)
SELECT * FROM users LIMIT 10 OFFSET 20;

-- FETCH (SQL standard)
SELECT * FROM users 
OFFSET 10 ROWS 
FETCH NEXT 10 ROWS ONLY;
```

## UPDATE Operations

### Basic UPDATE

```sql
-- Update single column
UPDATE users 
SET email = 'newemail@example.com'
WHERE username = 'john_doe';

-- Update multiple columns
UPDATE products 
SET 
    price = 99.99,
    stock_quantity = 50,
    updated_at = NOW()
WHERE product_id = 1;

-- Update all rows (dangerous!)
UPDATE products SET is_active = TRUE;

-- Update with calculation
UPDATE products 
SET price = price * 1.1  -- 10% increase
WHERE category = 'Electronics';

-- Update with subquery
UPDATE users 
SET email = (
    SELECT email FROM users_backup 
    WHERE users_backup.id = users.id
)
WHERE email IS NULL;
```

### UPDATE with FROM

```sql
-- Update using another table
UPDATE products p
SET category = c.new_category
FROM category_mappings c
WHERE p.category = c.old_category;

-- Update with join
UPDATE orders o
SET total = (
    SELECT SUM(quantity * price)
    FROM order_items oi
    WHERE oi.order_id = o.order_id
);
```

### UPDATE with RETURNING

```sql
-- Return updated rows
UPDATE products 
SET price = price * 0.9
WHERE category = 'Clearance'
RETURNING product_id, product_name, price;

-- Return count of updated rows
WITH updated AS (
    UPDATE products 
    SET stock_quantity = 0
    WHERE stock_quantity < 0
    RETURNING *
)
SELECT COUNT(*) FROM updated;
```

## DELETE Operations

### Basic DELETE

```sql
-- Delete specific rows
DELETE FROM users 
WHERE username = 'john_doe';

-- Delete with multiple conditions
DELETE FROM products 
WHERE category = 'Discontinued' 
  AND stock_quantity = 0;

-- Delete all rows (dangerous!)
DELETE FROM temp_table;

-- Delete with subquery
DELETE FROM orders 
WHERE user_id IN (
    SELECT user_id FROM users WHERE is_active = FALSE
);
```

### DELETE with USING

```sql
-- Delete using another table
DELETE FROM orders o
USING users u
WHERE o.user_id = u.user_id 
  AND u.is_deleted = TRUE;
```

### DELETE with RETURNING

```sql
-- Return deleted rows
DELETE FROM products 
WHERE is_active = FALSE
RETURNING *;

-- Log deleted rows
WITH deleted AS (
    DELETE FROM old_orders 
    WHERE created_at < NOW() - INTERVAL '1 year'
    RETURNING *
)
INSERT INTO archived_orders 
SELECT * FROM deleted;
```

## Aggregate Functions

```sql
-- Common aggregates
SELECT 
    COUNT(*) AS total_users,
    COUNT(DISTINCT email) AS unique_emails,
    MIN(created_at) AS first_registration,
    MAX(created_at) AS last_registration
FROM users;

-- Numeric aggregates
SELECT 
    AVG(price) AS average_price,
    SUM(stock_quantity) AS total_stock,
    MIN(price) AS cheapest,
    MAX(price) AS most_expensive
FROM products;

-- String aggregates
SELECT 
    string_agg(username, ', ') AS all_users,
    string_agg(username, ', ' ORDER BY created_at) AS users_ordered
FROM users;

-- Array aggregate
SELECT array_agg(product_name) AS all_products
FROM products;

-- JSON aggregate
SELECT jsonb_agg(
    jsonb_build_object('name', product_name, 'price', price)
) AS products_json
FROM products;
```

## GROUP BY

```sql
-- Basic grouping
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(price) AS average_price
FROM products
GROUP BY category;

-- Multiple columns
SELECT 
    category,
    is_active,
    COUNT(*) AS count,
    SUM(stock_quantity) AS total_stock
FROM products
GROUP BY category, is_active;

-- Grouping with HAVING
SELECT 
    category,
    COUNT(*) AS product_count,
    AVG(price) AS avg_price
FROM products
GROUP BY category
HAVING COUNT(*) > 5 AND AVG(price) > 100;

-- GROUP BY with expressions
SELECT 
    DATE_TRUNC('month', created_at) AS month,
    COUNT(*) AS registrations
FROM users
GROUP BY DATE_TRUNC('month', created_at)
ORDER BY month;
```

## DISTINCT and DISTINCT ON

```sql
-- Get unique values
SELECT DISTINCT category FROM products;

-- DISTINCT ON (PostgreSQL specific)
SELECT DISTINCT ON (user_id)
    user_id,
    order_date,
    total
FROM orders
ORDER BY user_id, order_date DESC;  -- Latest order per user

-- Multiple DISTINCT ON columns
SELECT DISTINCT ON (category, brand)
    category,
    brand,
    product_name,
    price
FROM products
ORDER BY category, brand, price DESC;
```

## Common Table Expressions (CTEs)

```sql
-- Basic CTE
WITH expensive_products AS (
    SELECT * FROM products WHERE price > 1000
)
SELECT category, COUNT(*) 
FROM expensive_products 
GROUP BY category;

-- Multiple CTEs
WITH 
active_users AS (
    SELECT * FROM users WHERE is_active = TRUE
),
recent_orders AS (
    SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '30 days'
)
SELECT 
    u.username,
    COUNT(o.order_id) AS order_count
FROM active_users u
LEFT JOIN recent_orders o ON u.user_id = o.user_id
GROUP BY u.username;

-- Recursive CTE (covered in advanced section)
```

## Subqueries

```sql
-- Subquery in WHERE
SELECT * FROM products 
WHERE price > (SELECT AVG(price) FROM products);

-- Subquery in SELECT
SELECT 
    product_name,
    price,
    (SELECT AVG(price) FROM products) AS avg_price,
    price - (SELECT AVG(price) FROM products) AS price_diff
FROM products;

-- Subquery with IN
SELECT * FROM users 
WHERE user_id IN (
    SELECT user_id FROM orders WHERE total > 1000
);

-- Subquery with EXISTS
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM orders o 
    WHERE o.user_id = u.user_id 
    AND o.total > 1000
);

-- Subquery in FROM
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
```

## CASE Expressions

```sql
-- Simple CASE
SELECT 
    product_name,
    price,
    CASE 
        WHEN price < 50 THEN 'Budget'
        WHEN price < 200 THEN 'Mid-Range'
        ELSE 'Premium'
    END AS price_category
FROM products;

-- Searched CASE
SELECT 
    username,
    CASE 
        WHEN created_at > NOW() - INTERVAL '1 month' THEN 'New'
        WHEN created_at > NOW() - INTERVAL '1 year' THEN 'Active'
        ELSE 'Long-time'
    END AS user_type
FROM users;

-- CASE in aggregation
SELECT 
    category,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE price < 100) AS budget_count,
    COUNT(CASE WHEN price < 100 THEN 1 END) AS budget_count_alt,
    SUM(CASE WHEN is_active THEN 1 ELSE 0 END) AS active_count
FROM products
GROUP BY category;
```

## COALESCE and NULLIF

```sql
-- COALESCE (return first non-null)
SELECT 
    username,
    COALESCE(email, phone, 'No contact') AS contact_method
FROM users;

-- NULLIF (return NULL if equal)
SELECT 
    product_name,
    price,
    NULLIF(discount, 0) AS discount  -- NULL if discount is 0
FROM products;

-- Practical example
SELECT 
    category,
    COUNT(*) AS count,
    AVG(price) AS avg_price,
    COALESCE(AVG(NULLIF(discount, 0)), 0) AS avg_discount
FROM products
GROUP BY category;
```

## Practical Examples

### User Registration and Activity

```sql
-- Create users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Register new user
INSERT INTO users (username, email, password_hash) 
VALUES ('john_doe', 'john@example.com', 'hashed_password')
RETURNING user_id, username, created_at;

-- Update last login
UPDATE users 
SET last_login = NOW() 
WHERE username = 'john_doe';

-- Find inactive users
SELECT * FROM users 
WHERE is_active = FALSE 
   OR last_login < NOW() - INTERVAL '90 days';
```

### E-commerce Orders

```sql
-- Create orders table
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    total DECIMAL(10, 2) NOT NULL CHECK (total >= 0),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Place order
INSERT INTO orders (user_id, total) 
VALUES (1, 299.99)
RETURNING order_id;

-- Update order status
UPDATE orders 
SET status = 'shipped' 
WHERE order_id = 1;

-- Get user's orders
SELECT 
    order_id,
    total,
    status,
    created_at
FROM orders
WHERE user_id = 1
ORDER BY created_at DESC;

-- Calculate total sales
SELECT 
    COUNT(*) AS total_orders,
    SUM(total) AS total_revenue,
    AVG(total) AS average_order_value
FROM orders
WHERE status = 'completed';
```

## Summary

**Key Operations**:
- **CREATE**: Create databases, schemas, tables
- **INSERT**: Add data with RETURNING and ON CONFLICT
- **SELECT**: Query data with WHERE, ORDER BY, LIMIT
- **UPDATE**: Modify existing data
- **DELETE**: Remove data
- **Aggregates**: COUNT, SUM, AVG, MIN, MAX
- **GROUP BY**: Aggregate by groups
- **Subqueries**: Nested queries
- **CASE**: Conditional logic

**Next Steps**:
- [Joins and Subqueries](12-joins-and-subqueries.md)
- [Indexes](09-indexes.md)
- [Constraints and Keys](08-constraints-and-keys.md)
