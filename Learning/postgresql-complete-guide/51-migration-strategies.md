# Migration Strategies

## Overview

Migrating to PostgreSQL from other database systems requires careful planning, execution, and validation. This guide covers migration strategies from popular databases including MySQL, Oracle, SQL Server, and MongoDB, with practical tools, scripts, and best practices.

## Table of Contents
- [Migration Planning](#migration-planning)
- [MySQL to PostgreSQL](#mysql-to-postgresql)
- [Oracle to PostgreSQL](#oracle-to-postgresql)
- [SQL Server to PostgreSQL](#sql-server-to-postgresql)
- [MongoDB to PostgreSQL](#mongodb-to-postgresql)
- [Migration Tools](#migration-tools)
- [Data Validation](#data-validation)
- [Cutover Strategies](#cutover-strategies)
- [Post-Migration Tasks](#post-migration-tasks)

---

## Migration Planning

### Assessment Phase

```sql
-- Questions to answer before migration:

-- 1. Database Size Assessment
-- Source database size
-- Number of tables, indexes, constraints
-- Largest tables by row count and size

-- 2. Feature Usage Analysis
-- Stored procedures and functions
-- Triggers
-- Database-specific features
-- Custom data types

-- 3. Application Dependencies
-- Connection strings
-- ORM compatibility
-- SQL dialect differences
-- Transaction handling
```

### Migration Checklist

```markdown
## Pre-Migration
- [ ] Inventory all database objects
- [ ] Document schema including all constraints
- [ ] Identify database-specific features
- [ ] Analyze application SQL queries
- [ ] Plan for downtime window
- [ ] Set up target PostgreSQL environment
- [ ] Create migration test environment

## Schema Migration
- [ ] Convert data types
- [ ] Migrate tables
- [ ] Create indexes
- [ ] Add constraints (primary, foreign, unique, check)
- [ ] Migrate sequences/auto-increment
- [ ] Convert views
- [ ] Convert stored procedures
- [ ] Convert triggers
- [ ] Set up schemas/namespaces

## Data Migration
- [ ] Export data from source
- [ ] Transform data (encoding, format)
- [ ] Load data into PostgreSQL
- [ ] Verify row counts
- [ ] Validate data integrity

## Application Migration
- [ ] Update connection strings
- [ ] Modify SQL queries
- [ ] Test all CRUD operations
- [ ] Update ORM configurations
- [ ] Performance testing

## Post-Migration
- [ ] Run ANALYZE on all tables
- [ ] Configure autovacuum
- [ ] Set up monitoring
- [ ] Validate backup procedures
- [ ] Document changes
```

---

## MySQL to PostgreSQL

### Data Type Mapping

| MySQL Type | PostgreSQL Type | Notes |
|------------|-----------------|-------|
| TINYINT | SMALLINT | Or BOOLEAN for TINYINT(1) |
| SMALLINT | SMALLINT | |
| MEDIUMINT | INTEGER | |
| INT/INTEGER | INTEGER | |
| BIGINT | BIGINT | |
| FLOAT | REAL | |
| DOUBLE | DOUBLE PRECISION | |
| DECIMAL(m,n) | DECIMAL(m,n) | |
| CHAR(n) | CHAR(n) | |
| VARCHAR(n) | VARCHAR(n) | |
| TINYTEXT | TEXT | |
| TEXT | TEXT | |
| MEDIUMTEXT | TEXT | |
| LONGTEXT | TEXT | |
| TINYBLOB | BYTEA | |
| BLOB | BYTEA | |
| MEDIUMBLOB | BYTEA | |
| LONGBLOB | BYTEA | |
| DATE | DATE | |
| TIME | TIME | |
| DATETIME | TIMESTAMP | |
| TIMESTAMP | TIMESTAMPTZ | |
| YEAR | SMALLINT | Or use CHECK constraint |
| ENUM | VARCHAR + CHECK | Or CREATE TYPE |
| SET | TEXT[] | Or junction table |
| JSON | JSONB | Preferred for indexing |
| AUTO_INCREMENT | SERIAL/BIGSERIAL | Or IDENTITY |

### Schema Conversion

```sql
-- MySQL Schema
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status ENUM('active', 'inactive', 'banned') DEFAULT 'active',
    data JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- PostgreSQL Equivalent
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'inactive', 'banned')),
    data JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create trigger for updated_at (MySQL ON UPDATE equivalent)
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
```

### Query Syntax Differences

```sql
-- MySQL vs PostgreSQL differences

-- 1. String concatenation
-- MySQL:
SELECT CONCAT(first_name, ' ', last_name) FROM users;
-- PostgreSQL (both work):
SELECT first_name || ' ' || last_name FROM users;
SELECT CONCAT(first_name, ' ', last_name) FROM users;

-- 2. LIMIT with OFFSET
-- MySQL:
SELECT * FROM products LIMIT 10, 20;  -- OFFSET 10, LIMIT 20
-- PostgreSQL:
SELECT * FROM products LIMIT 20 OFFSET 10;

-- 3. Case sensitivity
-- MySQL: Case-insensitive by default
-- PostgreSQL: Case-sensitive
-- Solution:
SELECT * FROM users WHERE LOWER(email) = LOWER('User@Example.com');
-- Or use ILIKE:
SELECT * FROM users WHERE email ILIKE 'user@example.com';

-- 4. GROUP BY
-- MySQL: Allows non-aggregated columns in SELECT
-- PostgreSQL: All non-aggregated columns must be in GROUP BY
SELECT category, product_name, SUM(quantity)  -- This fails in PG
FROM order_items
GROUP BY category;
-- Fix:
SELECT category, MIN(product_name), SUM(quantity)
FROM order_items
GROUP BY category;

-- 5. Boolean handling
-- MySQL: 0/1, TRUE/FALSE
-- PostgreSQL: TRUE/FALSE, 't'/'f'
SELECT * FROM users WHERE is_active = TRUE;  -- Works in both
SELECT * FROM users WHERE is_active;         -- PostgreSQL shorthand

-- 6. IFNULL vs COALESCE
-- MySQL:
SELECT IFNULL(middle_name, '') FROM users;
-- PostgreSQL:
SELECT COALESCE(middle_name, '') FROM users;

-- 7. NOW() vs CURRENT_TIMESTAMP
-- Both work in PostgreSQL, NOW() returns TIMESTAMPTZ

-- 8. Date formatting
-- MySQL:
SELECT DATE_FORMAT(created_at, '%Y-%m-%d') FROM orders;
-- PostgreSQL:
SELECT TO_CHAR(created_at, 'YYYY-MM-DD') FROM orders;

-- 9. Auto-increment reset
-- MySQL:
ALTER TABLE users AUTO_INCREMENT = 1000;
-- PostgreSQL:
ALTER SEQUENCE users_id_seq RESTART WITH 1000;
```

### Using pgloader

```bash
# Install pgloader
# macOS: brew install pgloader
# Ubuntu: apt-get install pgloader

# Basic migration
pgloader mysql://user:password@localhost/mydb \
         postgresql://user:password@localhost/pgdb

# With configuration file
cat > migration.load << 'EOF'
LOAD DATABASE
    FROM mysql://root:password@localhost/mysql_db
    INTO postgresql://postgres:password@localhost/pg_db

WITH include drop, create tables, create indexes, reset sequences,
     workers = 4, concurrency = 1

SET maintenance_work_mem to '512MB',
    work_mem to '48MB'

CAST type datetime to timestamptz drop default drop not null using zero-dates-to-null,
     type date to date drop default drop not null using zero-dates-to-null,
     type tinyint to boolean using tinyint-to-boolean

EXCLUDING TABLE NAMES MATCHING 'temp_', 'backup_'

BEFORE LOAD DO
     $$ DROP SCHEMA IF EXISTS public CASCADE; $$,
     $$ CREATE SCHEMA public; $$;
EOF

pgloader migration.load
```

### Stored Procedure Conversion

```sql
-- MySQL Stored Procedure
DELIMITER //
CREATE PROCEDURE GetUserOrders(IN userId INT)
BEGIN
    SELECT o.*, u.name
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.user_id = userId
    ORDER BY o.created_at DESC;
END //
DELIMITER ;

-- PostgreSQL Function
CREATE OR REPLACE FUNCTION get_user_orders(p_user_id INTEGER)
RETURNS TABLE (
    order_id INTEGER,
    total DECIMAL,
    status VARCHAR,
    created_at TIMESTAMPTZ,
    user_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.order_id, o.total, o.status, o.created_at, u.name
    FROM orders o
    JOIN users u ON o.user_id = u.id
    WHERE o.user_id = p_user_id
    ORDER BY o.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Call the function
SELECT * FROM get_user_orders(123);
```

---

## Oracle to PostgreSQL

### Data Type Mapping

| Oracle Type | PostgreSQL Type | Notes |
|-------------|-----------------|-------|
| NUMBER | NUMERIC/INTEGER/BIGINT | Based on precision |
| NUMBER(p,0) | INTEGER/BIGINT | Based on size |
| VARCHAR2(n) | VARCHAR(n) | |
| CHAR(n) | CHAR(n) | |
| NVARCHAR2(n) | VARCHAR(n) | UTF-8 native |
| NCHAR(n) | CHAR(n) | |
| CLOB | TEXT | |
| NCLOB | TEXT | |
| BLOB | BYTEA | |
| RAW | BYTEA | |
| LONG | TEXT | Deprecated in Oracle |
| LONG RAW | BYTEA | |
| DATE | TIMESTAMP | Oracle DATE includes time |
| TIMESTAMP | TIMESTAMP | |
| TIMESTAMP WITH TIME ZONE | TIMESTAMPTZ | |
| INTERVAL YEAR TO MONTH | INTERVAL | |
| INTERVAL DAY TO SECOND | INTERVAL | |
| ROWID | OID | Limited support |
| BINARY_FLOAT | REAL | |
| BINARY_DOUBLE | DOUBLE PRECISION | |
| XMLType | XML | |

### Oracle to PostgreSQL Syntax

```sql
-- 1. Sequences
-- Oracle:
CREATE SEQUENCE order_seq START WITH 1 INCREMENT BY 1;
SELECT order_seq.NEXTVAL FROM dual;
-- PostgreSQL:
CREATE SEQUENCE order_seq START WITH 1 INCREMENT BY 1;
SELECT nextval('order_seq');

-- 2. String functions
-- Oracle SUBSTR:
SELECT SUBSTR(name, 1, 10) FROM users;
-- PostgreSQL (both work):
SELECT SUBSTR(name, 1, 10) FROM users;
SELECT SUBSTRING(name FROM 1 FOR 10) FROM users;

-- 3. NVL vs COALESCE
-- Oracle:
SELECT NVL(middle_name, 'N/A') FROM users;
-- PostgreSQL:
SELECT COALESCE(middle_name, 'N/A') FROM users;

-- 4. DECODE vs CASE
-- Oracle:
SELECT DECODE(status, 1, 'Active', 2, 'Inactive', 'Unknown') FROM users;
-- PostgreSQL:
SELECT CASE status 
    WHEN 1 THEN 'Active' 
    WHEN 2 THEN 'Inactive' 
    ELSE 'Unknown' 
END FROM users;

-- 5. SYSDATE vs NOW()
-- Oracle:
SELECT SYSDATE FROM dual;
-- PostgreSQL:
SELECT NOW();
SELECT CURRENT_TIMESTAMP;

-- 6. Date arithmetic
-- Oracle:
SELECT created_at + 7 FROM orders;  -- Add 7 days
-- PostgreSQL:
SELECT created_at + INTERVAL '7 days' FROM orders;

-- 7. TO_DATE/TO_CHAR
-- Oracle:
SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD') FROM dual;
SELECT TO_CHAR(created_at, 'YYYY-MM-DD') FROM orders;
-- PostgreSQL (same syntax mostly works):
SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD');
SELECT TO_CHAR(created_at, 'YYYY-MM-DD') FROM orders;

-- 8. ROWNUM vs ROW_NUMBER
-- Oracle:
SELECT * FROM orders WHERE ROWNUM <= 10;
-- PostgreSQL:
SELECT * FROM orders LIMIT 10;
-- Or with ROW_NUMBER:
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (ORDER BY created_at) AS rn 
    FROM orders
) t WHERE rn <= 10;

-- 9. (+) outer join syntax
-- Oracle:
SELECT * FROM orders o, customers c WHERE o.customer_id = c.id(+);
-- PostgreSQL:
SELECT * FROM orders o LEFT JOIN customers c ON o.customer_id = c.id;

-- 10. Hierarchical queries
-- Oracle CONNECT BY:
SELECT employee_id, manager_id, LEVEL
FROM employees
START WITH manager_id IS NULL
CONNECT BY PRIOR employee_id = manager_id;

-- PostgreSQL (recursive CTE):
WITH RECURSIVE emp_hierarchy AS (
    SELECT employee_id, manager_id, 1 AS level
    FROM employees
    WHERE manager_id IS NULL
    
    UNION ALL
    
    SELECT e.employee_id, e.manager_id, eh.level + 1
    FROM employees e
    JOIN emp_hierarchy eh ON e.manager_id = eh.employee_id
)
SELECT * FROM emp_hierarchy;
```

### PL/SQL to PL/pgSQL Conversion

```sql
-- Oracle PL/SQL Package
CREATE OR REPLACE PACKAGE order_pkg AS
    PROCEDURE create_order(
        p_customer_id IN NUMBER,
        p_total IN NUMBER,
        p_order_id OUT NUMBER
    );
    FUNCTION get_order_count(p_customer_id NUMBER) RETURN NUMBER;
END order_pkg;
/

CREATE OR REPLACE PACKAGE BODY order_pkg AS
    PROCEDURE create_order(
        p_customer_id IN NUMBER,
        p_total IN NUMBER,
        p_order_id OUT NUMBER
    ) IS
    BEGIN
        INSERT INTO orders (customer_id, total)
        VALUES (p_customer_id, p_total)
        RETURNING order_id INTO p_order_id;
        COMMIT;
    EXCEPTION
        WHEN OTHERS THEN
            ROLLBACK;
            RAISE;
    END create_order;
    
    FUNCTION get_order_count(p_customer_id NUMBER) RETURN NUMBER IS
        v_count NUMBER;
    BEGIN
        SELECT COUNT(*) INTO v_count
        FROM orders
        WHERE customer_id = p_customer_id;
        RETURN v_count;
    END get_order_count;
END order_pkg;
/

-- PostgreSQL equivalent (schema as namespace)
CREATE SCHEMA order_pkg;

CREATE OR REPLACE FUNCTION order_pkg.create_order(
    p_customer_id INTEGER,
    p_total DECIMAL
)
RETURNS INTEGER AS $$
DECLARE
    v_order_id INTEGER;
BEGIN
    INSERT INTO orders (customer_id, total)
    VALUES (p_customer_id, p_total)
    RETURNING order_id INTO v_order_id;
    
    RETURN v_order_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION order_pkg.get_order_count(p_customer_id INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_count
    FROM orders
    WHERE customer_id = p_customer_id;
    
    RETURN v_count;
END;
$$ LANGUAGE plpgsql;

-- Note: Transaction control (COMMIT/ROLLBACK) in PostgreSQL
-- functions doesn't work the same way - handle at application level
```

### Using Ora2Pg

```bash
# Install ora2pg
# Download from https://ora2pg.darold.net/

# Generate configuration file
ora2pg --init_project my_migration

# Edit ora2pg.conf
# Set ORACLE_DSN, ORACLE_USER, ORACLE_PWD
# Set PG_DSN, PG_USER, PG_PWD

# Export schema
ora2pg -t TABLE -o tables.sql
ora2pg -t SEQUENCE -o sequences.sql
ora2pg -t VIEW -o views.sql
ora2pg -t FUNCTION -o functions.sql
ora2pg -t PROCEDURE -o procedures.sql
ora2pg -t TRIGGER -o triggers.sql
ora2pg -t PACKAGE -o packages.sql

# Export data
ora2pg -t COPY -o data.sql

# Or export to files for parallel loading
ora2pg -t COPY -j 4 -o data/

# Full migration report
ora2pg -t SHOW_REPORT --estimate_cost

# Import to PostgreSQL
psql -h localhost -U postgres -d target_db -f tables.sql
psql -h localhost -U postgres -d target_db -f data.sql
```

---

## SQL Server to PostgreSQL

### Data Type Mapping

| SQL Server Type | PostgreSQL Type | Notes |
|-----------------|-----------------|-------|
| BIT | BOOLEAN | |
| TINYINT | SMALLINT | |
| SMALLINT | SMALLINT | |
| INT | INTEGER | |
| BIGINT | BIGINT | |
| DECIMAL/NUMERIC | DECIMAL/NUMERIC | |
| MONEY | DECIMAL(19,4) | |
| SMALLMONEY | DECIMAL(10,4) | |
| FLOAT | DOUBLE PRECISION | |
| REAL | REAL | |
| CHAR(n) | CHAR(n) | |
| VARCHAR(n) | VARCHAR(n) | |
| VARCHAR(MAX) | TEXT | |
| NCHAR(n) | CHAR(n) | UTF-8 native |
| NVARCHAR(n) | VARCHAR(n) | UTF-8 native |
| NVARCHAR(MAX) | TEXT | |
| TEXT | TEXT | |
| NTEXT | TEXT | |
| BINARY(n) | BYTEA | |
| VARBINARY(n) | BYTEA | |
| IMAGE | BYTEA | |
| DATE | DATE | |
| TIME | TIME | |
| DATETIME | TIMESTAMP | |
| DATETIME2 | TIMESTAMP | |
| SMALLDATETIME | TIMESTAMP | |
| DATETIMEOFFSET | TIMESTAMPTZ | |
| UNIQUEIDENTIFIER | UUID | |
| XML | XML | |
| GEOGRAPHY | GEOGRAPHY | PostGIS |
| GEOMETRY | GEOMETRY | PostGIS |
| HIERARCHYID | LTREE | Extension |

### T-SQL to PostgreSQL

```sql
-- 1. Identity columns
-- SQL Server:
CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100)
);
-- PostgreSQL:
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);
-- Or (PostgreSQL 10+):
CREATE TABLE users (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(100)
);

-- 2. TOP vs LIMIT
-- SQL Server:
SELECT TOP 10 * FROM orders ORDER BY created_at DESC;
-- PostgreSQL:
SELECT * FROM orders ORDER BY created_at DESC LIMIT 10;

-- 3. String concatenation
-- SQL Server:
SELECT first_name + ' ' + last_name FROM users;
-- PostgreSQL:
SELECT first_name || ' ' || last_name FROM users;

-- 4. ISNULL vs COALESCE
-- SQL Server:
SELECT ISNULL(middle_name, '') FROM users;
-- PostgreSQL:
SELECT COALESCE(middle_name, '') FROM users;

-- 5. GETDATE() vs NOW()
-- SQL Server:
SELECT GETDATE();
-- PostgreSQL:
SELECT NOW();

-- 6. DATEADD/DATEDIFF
-- SQL Server:
SELECT DATEADD(day, 7, created_at) FROM orders;
SELECT DATEDIFF(day, created_at, GETDATE()) FROM orders;
-- PostgreSQL:
SELECT created_at + INTERVAL '7 days' FROM orders;
SELECT EXTRACT(DAY FROM NOW() - created_at) FROM orders;
-- Or use AGE function:
SELECT AGE(NOW(), created_at) FROM orders;

-- 7. CONVERT/CAST
-- SQL Server:
SELECT CONVERT(VARCHAR, created_at, 120) FROM orders;
-- PostgreSQL:
SELECT TO_CHAR(created_at, 'YYYY-MM-DD HH24:MI:SS') FROM orders;

-- 8. Temp tables
-- SQL Server:
SELECT * INTO #temp_table FROM orders WHERE status = 'pending';
-- PostgreSQL:
CREATE TEMP TABLE temp_table AS 
SELECT * FROM orders WHERE status = 'pending';

-- 9. Table variables
-- SQL Server:
DECLARE @t TABLE (id INT, name VARCHAR(100));
INSERT INTO @t VALUES (1, 'test');
-- PostgreSQL (use CTEs or temp tables):
WITH t AS (
    SELECT 1 AS id, 'test' AS name
)
SELECT * FROM t;

-- 10. OUTPUT clause
-- SQL Server:
DELETE FROM orders 
OUTPUT deleted.order_id, deleted.total
WHERE status = 'cancelled';
-- PostgreSQL:
DELETE FROM orders 
WHERE status = 'cancelled'
RETURNING order_id, total;
```

### Stored Procedure Conversion

```sql
-- SQL Server Procedure
CREATE PROCEDURE usp_GetOrdersByStatus
    @Status VARCHAR(20),
    @StartDate DATETIME = NULL,
    @EndDate DATETIME = NULL
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT o.*, c.name AS customer_name
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.status = @Status
      AND (@StartDate IS NULL OR o.created_at >= @StartDate)
      AND (@EndDate IS NULL OR o.created_at <= @EndDate)
    ORDER BY o.created_at DESC;
END;

-- PostgreSQL Function
CREATE OR REPLACE FUNCTION get_orders_by_status(
    p_status VARCHAR(20),
    p_start_date TIMESTAMP DEFAULT NULL,
    p_end_date TIMESTAMP DEFAULT NULL
)
RETURNS TABLE (
    order_id INTEGER,
    customer_id INTEGER,
    total DECIMAL,
    status VARCHAR,
    created_at TIMESTAMP,
    customer_name VARCHAR
) AS $$
BEGIN
    RETURN QUERY
    SELECT o.order_id, o.customer_id, o.total, o.status, o.created_at, c.name
    FROM orders o
    INNER JOIN customers c ON o.customer_id = c.id
    WHERE o.status = p_status
      AND (p_start_date IS NULL OR o.created_at >= p_start_date)
      AND (p_end_date IS NULL OR o.created_at <= p_end_date)
    ORDER BY o.created_at DESC;
END;
$$ LANGUAGE plpgsql;
```

---

## MongoDB to PostgreSQL

### Document to Relational Mapping

```javascript
// MongoDB Document
{
    "_id": ObjectId("..."),
    "name": "John Doe",
    "email": "john@example.com",
    "addresses": [
        {
            "type": "home",
            "street": "123 Main St",
            "city": "New York",
            "zip": "10001"
        },
        {
            "type": "work",
            "street": "456 Office Ave",
            "city": "New York",
            "zip": "10002"
        }
    ],
    "orders": [
        {
            "order_id": "ORD-001",
            "total": 99.99,
            "items": [
                {"product": "Widget", "qty": 2, "price": 29.99},
                {"product": "Gadget", "qty": 1, "price": 40.01}
            ]
        }
    ],
    "preferences": {
        "newsletter": true,
        "notifications": {
            "email": true,
            "sms": false
        }
    }
}
```

### Option 1: Normalized Schema

```sql
-- Fully normalized PostgreSQL schema
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL
);

CREATE TABLE addresses (
    address_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id) ON DELETE CASCADE,
    address_type VARCHAR(20) NOT NULL,
    street VARCHAR(255),
    city VARCHAR(100),
    zip VARCHAR(20)
);

CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    order_number VARCHAR(20) UNIQUE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_items (
    item_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    product VARCHAR(100) NOT NULL,
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);

CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    newsletter BOOLEAN DEFAULT FALSE,
    email_notifications BOOLEAN DEFAULT TRUE,
    sms_notifications BOOLEAN DEFAULT FALSE
);
```

### Option 2: Hybrid with JSONB

```sql
-- Hybrid approach: Normalize important relationships, JSONB for flexible data
CREATE TABLE users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    -- Embed addresses as JSONB (not queried independently often)
    addresses JSONB DEFAULT '[]',
    -- Flexible preferences
    preferences JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Normalize orders (important for querying and reporting)
CREATE TABLE orders (
    order_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(user_id),
    order_number VARCHAR(20) UNIQUE NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    -- Embed items as JSONB (if always accessed with order)
    items JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for JSONB queries
CREATE INDEX idx_users_addresses ON users USING GIN(addresses);
CREATE INDEX idx_orders_items ON orders USING GIN(items);

-- Query examples
-- Find users in New York
SELECT * FROM users 
WHERE addresses @> '[{"city": "New York"}]';

-- Find orders containing Widget
SELECT * FROM orders 
WHERE items @> '[{"product": "Widget"}]';
```

### Migration Script

```python
# Python script to migrate MongoDB to PostgreSQL
import pymongo
import psycopg2
from psycopg2.extras import execute_values
import json

# MongoDB connection
mongo_client = pymongo.MongoClient("mongodb://localhost:27017")
mongo_db = mongo_client["source_db"]

# PostgreSQL connection
pg_conn = psycopg2.connect(
    host="localhost",
    database="target_db",
    user="postgres",
    password="password"
)
pg_cursor = pg_conn.cursor()

def migrate_users():
    """Migrate users collection with hybrid approach"""
    users = mongo_db.users.find()
    
    user_data = []
    for user in users:
        user_data.append((
            str(user['_id']),  # Convert ObjectId to string
            user['name'],
            user['email'],
            json.dumps(user.get('addresses', [])),
            json.dumps(user.get('preferences', {}))
        ))
    
    execute_values(
        pg_cursor,
        """
        INSERT INTO users (user_id, name, email, addresses, preferences)
        VALUES %s
        ON CONFLICT (email) DO UPDATE SET
            name = EXCLUDED.name,
            addresses = EXCLUDED.addresses,
            preferences = EXCLUDED.preferences
        """,
        user_data,
        template="(%s::uuid, %s, %s, %s::jsonb, %s::jsonb)"
    )
    pg_conn.commit()
    print(f"Migrated {len(user_data)} users")

def migrate_orders():
    """Migrate orders with normalized items"""
    orders = mongo_db.orders.find()
    
    for order in orders:
        # Insert order
        pg_cursor.execute(
            """
            INSERT INTO orders (order_id, user_id, order_number, total, items)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                str(order['_id']),
                str(order['user_id']),
                order['order_number'],
                order['total'],
                json.dumps(order.get('items', []))
            )
        )
    
    pg_conn.commit()
    print("Orders migrated")

if __name__ == "__main__":
    migrate_users()
    migrate_orders()
    pg_cursor.close()
    pg_conn.close()
```

---

## Migration Tools

### Tool Comparison

| Tool | Source | Best For |
|------|--------|----------|
| pgloader | MySQL, SQLite | Automated MySQL migration |
| ora2pg | Oracle | Complete Oracle migration |
| AWS DMS | Any | Cloud migrations |
| Striim | Any | Real-time, zero-downtime |
| pgAdmin | CSV/Files | Manual imports |
| Foreign Data Wrappers | Any | Live queries during transition |

### Using Foreign Data Wrappers for Migration

```sql
-- Install MySQL FDW
CREATE EXTENSION mysql_fdw;

-- Create server
CREATE SERVER mysql_server
    FOREIGN DATA WRAPPER mysql_fdw
    OPTIONS (host 'mysql-host', port '3306');

-- Create user mapping
CREATE USER MAPPING FOR postgres
    SERVER mysql_server
    OPTIONS (username 'mysql_user', password 'mysql_pass');

-- Create foreign table
CREATE FOREIGN TABLE mysql_users (
    id INTEGER,
    name VARCHAR(100),
    email VARCHAR(255),
    created_at TIMESTAMP
)
SERVER mysql_server
OPTIONS (dbname 'mysql_db', table_name 'users');

-- Copy data
INSERT INTO users (id, name, email, created_at)
SELECT id, name, email, created_at FROM mysql_users;

-- Keep in sync during transition
INSERT INTO users (id, name, email, created_at)
SELECT id, name, email, created_at 
FROM mysql_users mu
WHERE NOT EXISTS (
    SELECT 1 FROM users u WHERE u.id = mu.id
);
```

---

## Data Validation

### Row Count Validation

```sql
-- Create validation table
CREATE TABLE migration_validation (
    table_name VARCHAR(100) PRIMARY KEY,
    source_count BIGINT,
    target_count BIGINT,
    validated_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20)
);

-- Populate (run after migration)
INSERT INTO migration_validation (table_name, source_count, target_count, status)
VALUES 
    ('users', 
     (SELECT count FROM dblink('source_db', 'SELECT COUNT(*) FROM users') AS t(count BIGINT)),
     (SELECT COUNT(*) FROM users),
     CASE WHEN source_count = target_count THEN 'PASS' ELSE 'FAIL' END
    );
```

### Data Integrity Checks

```sql
-- Check for NULL values in NOT NULL columns
SELECT 'users' AS table_name, 
       COUNT(*) FILTER (WHERE email IS NULL) AS null_emails,
       COUNT(*) FILTER (WHERE name IS NULL) AS null_names
FROM users;

-- Check referential integrity
SELECT 'orphan_orders' AS check_type, COUNT(*) AS count
FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM users u WHERE u.user_id = o.user_id);

-- Check data ranges
SELECT 
    'orders' AS table_name,
    MIN(total) AS min_total,
    MAX(total) AS max_total,
    COUNT(*) FILTER (WHERE total < 0) AS negative_totals
FROM orders;

-- Compare checksums (simplified)
SELECT 
    'users' AS table_name,
    md5(string_agg(user_id::text || email || name, ',' ORDER BY user_id)) AS checksum
FROM users;
```

### Automated Validation Script

```python
import psycopg2
import pymysql

def validate_migration():
    """Compare source and target databases"""
    # Connect to both databases
    mysql_conn = pymysql.connect(host='mysql-host', user='user', password='pass', db='source_db')
    pg_conn = psycopg2.connect(host='pg-host', user='user', password='pass', dbname='target_db')
    
    tables = ['users', 'orders', 'products', 'order_items']
    
    results = []
    for table in tables:
        # Get counts
        with mysql_conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            mysql_count = cursor.fetchone()[0]
        
        with pg_conn.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            pg_count = cursor.fetchone()[0]
        
        status = 'PASS' if mysql_count == pg_count else 'FAIL'
        results.append({
            'table': table,
            'source_count': mysql_count,
            'target_count': pg_count,
            'status': status
        })
    
    return results
```

---

## Cutover Strategies

### Big Bang Migration

```markdown
## Big Bang Approach
1. Schedule downtime window
2. Stop all application writes
3. Run final data sync
4. Validate data
5. Switch application to PostgreSQL
6. Monitor closely
7. Keep source as fallback

Pros:
- Simple approach
- Clean cutover

Cons:
- Requires downtime
- Higher risk
```

### Parallel Running

```markdown
## Parallel Running
1. Set up dual-write from application
2. Sync historical data
3. Run both databases in parallel
4. Compare results
5. Gradually shift reads to PostgreSQL
6. Stop writes to source
7. Decommission source

Pros:
- Lower risk
- Can compare results

Cons:
- More complex
- Potential data inconsistency
```

### Strangler Pattern

```markdown
## Strangler Pattern (Microservices)
1. Identify bounded contexts
2. Migrate one service/feature at a time
3. Route traffic to new service
4. Repeat for other services
5. Eventually decompose monolith

Pros:
- Gradual migration
- Can stop if issues arise

Cons:
- Longer timeline
- Temporary increased complexity
```

---

## Post-Migration Tasks

### Performance Optimization

```sql
-- Run ANALYZE on all tables
ANALYZE;

-- Or specific tables
ANALYZE users;
ANALYZE orders;

-- Check for missing indexes
SELECT 
    schemaname,
    relname,
    seq_scan,
    idx_scan,
    seq_tup_read
FROM pg_stat_user_tables
WHERE seq_scan > 0
ORDER BY seq_tup_read DESC;

-- Create indexes based on query patterns
CREATE INDEX CONCURRENTLY idx_orders_customer ON orders(customer_id);
CREATE INDEX CONCURRENTLY idx_orders_status_date ON orders(status, created_at DESC);
```

### Configure Autovacuum

```sql
-- Adjust autovacuum for large tables
ALTER TABLE large_table SET (
    autovacuum_vacuum_scale_factor = 0.05,
    autovacuum_analyze_scale_factor = 0.02
);

-- Monitor vacuum
SELECT 
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;
```

---

## Summary

### Migration Checklist Summary

| Phase | Key Activities |
|-------|----------------|
| Assessment | Inventory, feature analysis, complexity estimation |
| Planning | Timeline, resources, rollback plan |
| Schema | Type mapping, constraint conversion |
| Data | Export, transform, load, validate |
| Application | Query updates, connection changes |
| Testing | Functional, performance, integration |
| Cutover | Execute migration, switch traffic |
| Post-migration | Optimize, monitor, document |

---

## Next Steps

- [Troubleshooting Guide](52-troubleshooting-guide.md)
