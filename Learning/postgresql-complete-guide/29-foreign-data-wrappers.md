# Foreign Data Wrappers

## Overview

Foreign Data Wrappers (FDW) enable PostgreSQL to access data from external sources as if they were local tables. FDWs allow querying remote databases, files, web services, and other data sources using standard SQL.

## Table of Contents
- [FDW Basics](#fdw-basics)
- [postgres_fdw](#postgres_fdw)
- [file_fdw](#file_fdw)
- [Other Popular FDWs](#other-popular-fdws)
- [Creating Foreign Tables](#creating-foreign-tables)
- [Querying Foreign Data](#querying-foreign-data)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Best Practices](#best-practices)

## FDW Basics

### Understanding Foreign Data Wrappers

```sql
-- Foreign Data Wrapper architecture:
-- 1. FDW Extension: Handles communication protocol
-- 2. Foreign Server: Connection to external data source
-- 3. User Mapping: Authentication credentials
-- 4. Foreign Table: Schema definition for external data

-- List available FDWs
SELECT * FROM pg_foreign_data_wrapper;

-- List installed foreign servers
SELECT * FROM pg_foreign_server;

-- List foreign tables
SELECT 
    ft.foreign_table_schema,
    ft.foreign_table_name,
    fs.srvname as server_name
FROM information_schema.foreign_tables ft
JOIN pg_foreign_table pft ON pft.ftrelid = (ft.foreign_table_schema || '.' || ft.foreign_table_name)::regclass
JOIN pg_foreign_server fs ON fs.oid = pft.ftserver;
```

### Basic FDW Setup Steps

```sql
-- Step 1: Install FDW extension
CREATE EXTENSION postgres_fdw;

-- Step 2: Create foreign server
CREATE SERVER remote_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote-host.com', port '5432', dbname 'remote_db');

-- Step 3: Create user mapping
CREATE USER MAPPING FOR local_user
SERVER remote_server
OPTIONS (user 'remote_user', password 'remote_password');

-- Step 4: Create foreign table
CREATE FOREIGN TABLE remote_users (
    id INTEGER,
    username TEXT,
    email TEXT
)
SERVER remote_server
OPTIONS (schema_name 'public', table_name 'users');

-- Step 5: Query foreign data
SELECT * FROM remote_users;
```

## postgres_fdw

### Connecting to Remote PostgreSQL

```sql
-- Install extension
CREATE EXTENSION postgres_fdw;

-- Create server for remote PostgreSQL database
CREATE SERVER production_db
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    host 'prod-db.example.com',
    port '5432',
    dbname 'production',
    fetch_size '1000',        -- Rows per fetch
    use_remote_estimate 'true' -- Use remote stats for planning
);

-- Create user mapping (per local user)
CREATE USER MAPPING FOR current_user
SERVER production_db
OPTIONS (user 'prod_readonly', password 'secret');

-- Or map all local users
CREATE USER MAPPING FOR PUBLIC
SERVER production_db
OPTIONS (user 'shared_user', password 'shared_pass');

-- Import entire foreign schema
IMPORT FOREIGN SCHEMA public
FROM SERVER production_db
INTO local_schema;

-- Import specific tables only
IMPORT FOREIGN SCHEMA public
LIMIT TO (users, orders, products)
FROM SERVER production_db
INTO local_schema;

-- Import except specific tables
IMPORT FOREIGN SCHEMA public
EXCEPT (sensitive_table, temp_data)
FROM SERVER production_db
INTO local_schema;
```

### Manual Foreign Table Creation

```sql
-- Create foreign table manually
CREATE FOREIGN TABLE production_orders (
    order_id INTEGER NOT NULL,
    customer_id INTEGER,
    order_date DATE,
    total NUMERIC(10,2),
    status TEXT
)
SERVER production_db
OPTIONS (
    schema_name 'public',
    table_name 'orders',
    updatable 'false'  -- Read-only
);

-- Query foreign table
SELECT * FROM production_orders WHERE order_date >= CURRENT_DATE - 7;

-- Join local and foreign tables
SELECT 
    l.name,
    f.order_date,
    f.total
FROM local_customers l
JOIN production_orders f ON f.customer_id = l.id
WHERE f.order_date >= '2024-01-01';
```

### Writable Foreign Tables

```sql
-- Create writable foreign table
CREATE FOREIGN TABLE remote_logs (
    id SERIAL,
    log_level TEXT,
    message TEXT,
    created_at TIMESTAMP DEFAULT now()
)
SERVER production_db
OPTIONS (schema_name 'public', table_name 'logs');

-- Insert into remote table
INSERT INTO remote_logs (log_level, message)
VALUES ('INFO', 'Log from local database');

-- Update remote data
UPDATE remote_logs
SET log_level = 'WARNING'
WHERE id = 123;

-- Delete from remote table
DELETE FROM remote_logs WHERE created_at < CURRENT_DATE - 90;
```

### Advanced postgres_fdw Options

```sql
-- Server options
CREATE SERVER advanced_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    host 'remote.example.com',
    port '5432',
    dbname 'mydb',
    use_remote_estimate 'true',  -- Use remote stats
    fetch_size '1000',            -- Batch size
    extensions 'postgres_fdw',    -- Extensions available
    keep_connections 'on',        -- Keep connections open
    truncatable 'true',           -- Allow TRUNCATE
    async_capable 'true'          -- Async query execution (PG 14+)
);

-- Table-level options
CREATE FOREIGN TABLE advanced_table (
    id INTEGER,
    data TEXT
)
SERVER advanced_server
OPTIONS (
    schema_name 'public',
    table_name 'remote_table',
    fetch_size '5000',            -- Override server setting
    use_remote_estimate 'false',  -- Override server setting
    updatable 'true'              -- Allow DML operations
);

-- Column-level options
CREATE FOREIGN TABLE column_options (
    id INTEGER OPTIONS (column_name 'remote_id'),
    name TEXT OPTIONS (column_name 'full_name')
)
SERVER advanced_server
OPTIONS (schema_name 'public', table_name 'people');
```

## file_fdw

### Reading CSV Files

```sql
-- Install extension
CREATE EXTENSION file_fdw;

-- Create server
CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;

-- Create foreign table for CSV
CREATE FOREIGN TABLE sales_data (
    date DATE,
    product_id INTEGER,
    quantity INTEGER,
    revenue NUMERIC(10,2)
)
SERVER file_server
OPTIONS (
    filename '/data/sales.csv',
    format 'csv',
    header 'true',
    delimiter ',',
    null ''
);

-- Query CSV file
SELECT 
    date,
    sum(revenue) as daily_revenue
FROM sales_data
GROUP BY date
ORDER BY date DESC;

-- Join CSV with database table
SELECT 
    p.name,
    s.quantity,
    s.revenue
FROM sales_data s
JOIN products p ON p.id = s.product_id;
```

### Reading Text Files

```sql
-- Foreign table for log files
CREATE FOREIGN TABLE server_logs (
    log_line TEXT
)
SERVER file_server
OPTIONS (
    filename '/var/log/application.log',
    format 'text'
);

-- Parse log lines
SELECT 
    substring(log_line from '^\[(.*?)\]') as timestamp,
    substring(log_line from '\[(.*?)\] ([A-Z]+)') as level,
    substring(log_line from '\] [A-Z]+ (.*)$') as message
FROM server_logs
WHERE log_line ~ 'ERROR'
LIMIT 100;
```

### Multiple Files with PROGRAM

```sql
-- Read from program output
CREATE FOREIGN TABLE dynamic_data (
    data TEXT
)
SERVER file_server
OPTIONS (
    program 'cat /data/*.csv',  -- Shell command
    format 'text'
);

-- Or use gzip
CREATE FOREIGN TABLE compressed_data (
    data TEXT
)
SERVER file_server
OPTIONS (
    program 'gzip -dc /data/archive.csv.gz',
    format 'csv',
    header 'true'
);
```

## Other Popular FDWs

### mysql_fdw

Connect to MySQL databases:

```sql
-- Install mysql_fdw (requires compilation)
CREATE EXTENSION mysql_fdw;

-- Create server
CREATE SERVER mysql_server
FOREIGN DATA WRAPPER mysql_fdw
OPTIONS (
    host '127.0.0.1',
    port '3306'
);

-- User mapping
CREATE USER MAPPING FOR postgres
SERVER mysql_server
OPTIONS (username 'mysql_user', password 'mysql_pass');

-- Import MySQL tables
IMPORT FOREIGN SCHEMA mysql_database
FROM SERVER mysql_server
INTO public;

-- Or create manually
CREATE FOREIGN TABLE mysql_products (
    id INT,
    name TEXT,
    price DECIMAL
)
SERVER mysql_server
OPTIONS (dbname 'shop', table_name 'products');
```

### oracle_fdw

Connect to Oracle databases:

```sql
-- Install oracle_fdw
CREATE EXTENSION oracle_fdw;

-- Create server
CREATE SERVER oracle_server
FOREIGN DATA WRAPPER oracle_fdw
OPTIONS (dbserver '//oracle-host:1521/ORCL');

-- User mapping
CREATE USER MAPPING FOR postgres
SERVER oracle_server
OPTIONS (user 'oracle_user', password 'oracle_pass');

-- Create foreign table
CREATE FOREIGN TABLE oracle_employees (
    employee_id NUMBER,
    first_name VARCHAR2,
    last_name VARCHAR2,
    hire_date DATE
)
SERVER oracle_server
OPTIONS (schema 'HR', table 'EMPLOYEES');
```

### mongo_fdw

Connect to MongoDB:

```sql
-- Install mongo_fdw
CREATE EXTENSION mongo_fdw;

-- Create server
CREATE SERVER mongo_server
FOREIGN DATA WRAPPER mongo_fdw
OPTIONS (address '127.0.0.1', port '27017');

-- User mapping
CREATE USER MAPPING FOR postgres
SERVER mongo_server
OPTIONS (username 'mongo_user', password 'mongo_pass');

-- Create foreign table
CREATE FOREIGN TABLE mongo_users (
    _id NAME,
    name TEXT,
    email TEXT,
    age INT
)
SERVER mongo_server
OPTIONS (database 'mydb', collection 'users');
```

### redis_fdw

Connect to Redis:

```sql
-- Install redis_fdw
CREATE EXTENSION redis_fdw;

-- Create server
CREATE SERVER redis_server
FOREIGN DATA WRAPPER redis_fdw
OPTIONS (
    address '127.0.0.1',
    port '6379'
);

-- Foreign table for Redis keys
CREATE FOREIGN TABLE redis_cache (
    key TEXT,
    value TEXT
)
SERVER redis_server
OPTIONS (database '0');

-- Query Redis data
SELECT * FROM redis_cache WHERE key LIKE 'user:%';
```

## Creating Foreign Tables

### Automatic Schema Import

```sql
-- Import all tables from foreign schema
IMPORT FOREIGN SCHEMA remote_schema
FROM SERVER remote_server
INTO local_schema;

-- Import with options
IMPORT FOREIGN SCHEMA remote_schema
LIMIT TO (table1, table2, table3)
FROM SERVER remote_server
INTO local_schema
OPTIONS (import_default 'true', import_not_null 'true');

-- Check imported tables
SELECT 
    foreign_table_schema,
    foreign_table_name,
    foreign_server_name
FROM information_schema.foreign_tables;
```

### Manual Creation with Type Mapping

```sql
-- Map PostgreSQL types to foreign types
CREATE FOREIGN TABLE type_mapping (
    id INTEGER,
    bigint_col BIGINT,
    text_col TEXT,
    json_col JSONB,
    date_col DATE,
    timestamp_col TIMESTAMP,
    boolean_col BOOLEAN,
    array_col INTEGER[]
)
SERVER remote_server
OPTIONS (schema_name 'public', table_name 'remote_table');
```

### Partitioned Foreign Tables

```sql
-- Create partitioned table with foreign partitions
CREATE TABLE orders (
    order_id INTEGER,
    order_date DATE,
    total NUMERIC
) PARTITION BY RANGE (order_date);

-- Local partition
CREATE TABLE orders_2023 PARTITION OF orders
FOR VALUES FROM ('2023-01-01') TO ('2024-01-01');

-- Foreign partition
CREATE FOREIGN TABLE orders_2022 PARTITION OF orders
FOR VALUES FROM ('2022-01-01') TO ('2023-01-01')
SERVER archive_server
OPTIONS (schema_name 'public', table_name 'orders_2022');

-- Query seamlessly spans local and remote
SELECT * FROM orders WHERE order_date >= '2022-06-01';
```

## Querying Foreign Data

### Basic Queries

```sql
-- Simple SELECT
SELECT * FROM foreign_table WHERE id > 1000;

-- Aggregations (pushed to remote if possible)
SELECT 
    status,
    count(*) as count,
    avg(total) as avg_total
FROM foreign_orders
GROUP BY status;

-- Joins (local execution)
SELECT 
    l.name,
    f.total
FROM local_customers l
JOIN foreign_orders f ON f.customer_id = l.id;
```

### EXPLAIN Analysis

```sql
-- See query execution plan
EXPLAIN (VERBOSE, COSTS) 
SELECT * FROM foreign_table WHERE status = 'active';

-- Shows:
-- Foreign Scan on foreign_table
--   Remote SQL: SELECT id, name, status FROM remote_schema.remote_table WHERE status = 'active'

-- Check if predicates are pushed down
EXPLAIN (VERBOSE)
SELECT * FROM foreign_orders 
WHERE order_date >= '2024-01-01' 
  AND total > 100;
-- Look for filters in "Remote SQL"
```

### Combining Multiple Foreign Servers

```sql
-- Query data from multiple remote databases
SELECT 
    'Server A' as source,
    count(*) as order_count
FROM server_a_orders
UNION ALL
SELECT 
    'Server B' as source,
    count(*) as order_count
FROM server_b_orders;

-- Join data from different remote sources
SELECT 
    a.customer_name,
    b.order_count
FROM server_a_customers a
JOIN (
    SELECT customer_id, count(*) as order_count
    FROM server_b_orders
    GROUP BY customer_id
) b ON a.id = b.customer_id;
```

## Performance Optimization

### Pushdown Optimization

```sql
-- PostgreSQL pushes down:
-- - WHERE clauses
-- - Column selection
-- - Aggregations
-- - Sorting
-- - Joins (postgres_fdw 9.6+)

-- Good: WHERE pushed to remote
SELECT * FROM foreign_table WHERE status = 'active';
-- Remote SQL: SELECT ... WHERE status = 'active'

-- Good: Aggregation pushed to remote
SELECT status, count(*) FROM foreign_table GROUP BY status;
-- Remote SQL: SELECT status, count(*) FROM ... GROUP BY status

-- Bad: Function not pushable
SELECT * FROM foreign_table WHERE custom_function(status) = 'x';
-- Fetches all rows, filters locally

-- Check pushdown with EXPLAIN
EXPLAIN (VERBOSE) SELECT ...;
```

### Batch Fetching

```sql
-- Adjust fetch_size for better performance
ALTER SERVER remote_server OPTIONS (SET fetch_size '10000');

-- Or per table
ALTER FOREIGN TABLE large_table OPTIONS (SET fetch_size '50000');

-- Larger fetch_size:
-- + Fewer round trips
-- + Better for large result sets
-- - More memory usage
-- - Higher latency for first row
```

### Using Indexes on Remote

```sql
-- Remote indexes are used automatically
-- Create indexes on remote server for better performance

-- On remote server:
-- CREATE INDEX idx_orders_date ON orders(order_date);
-- CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Local queries benefit:
SELECT * FROM foreign_orders WHERE order_date >= '2024-01-01';
-- Uses remote index

-- Check with EXPLAIN
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM foreign_orders WHERE customer_id = 123;
-- Should show index usage in Remote SQL
```

### Parallel Query Execution

```sql
-- PostgreSQL 14+ supports async execution
ALTER SERVER remote_server OPTIONS (ADD async_capable 'true');

-- Enable parallel append
SET enable_parallel_append = on;

-- Query partitioned table with foreign partitions in parallel
EXPLAIN (ANALYZE)
SELECT * FROM partitioned_table WHERE date >= '2024-01-01';
-- Shows parallel foreign scans
```

### Materialized Views

```sql
-- Cache foreign data locally
CREATE MATERIALIZED VIEW mv_foreign_summary AS
SELECT 
    customer_id,
    count(*) as order_count,
    sum(total) as total_revenue
FROM foreign_orders
GROUP BY customer_id;

CREATE INDEX ON mv_foreign_summary(customer_id);

-- Refresh periodically
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_foreign_summary;

-- Query local materialized view (fast)
SELECT * FROM mv_foreign_summary WHERE customer_id = 123;
```

## Security Considerations

### User Mapping Security

```sql
-- Store credentials securely
-- Option 1: Per-user mapping
CREATE USER MAPPING FOR app_user
SERVER remote_server
OPTIONS (user 'remote_user', password 'secret');

-- Option 2: Use password file (.pgpass)
-- Don't store passwords in database
CREATE USER MAPPING FOR app_user
SERVER remote_server
OPTIONS (user 'remote_user');
-- .pgpass: remote-host:5432:dbname:remote_user:secret

-- Option 3: Use SSL certificates
CREATE SERVER secure_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (
    host 'remote-host',
    dbname 'mydb',
    sslmode 'require',
    sslcert '/path/to/client-cert.pem',
    sslkey '/path/to/client-key.pem',
    sslrootcert '/path/to/ca-cert.pem'
);
```

### Access Control

```sql
-- Grant access to foreign tables
GRANT SELECT ON foreign_table TO app_user;
GRANT INSERT, UPDATE, DELETE ON foreign_table TO admin_user;

-- Revoke access
REVOKE ALL ON foreign_table FROM app_user;

-- Grant access to foreign server (for creating tables)
GRANT USAGE ON FOREIGN SERVER remote_server TO developer;

-- Create read-only user mapping
CREATE USER MAPPING FOR readonly_user
SERVER remote_server
OPTIONS (user 'remote_readonly', password 'pass');
```

### Row-Level Security

```sql
-- Apply RLS on foreign tables (PostgreSQL 14+)
ALTER FOREIGN TABLE foreign_orders ENABLE ROW LEVEL SECURITY;

CREATE POLICY user_orders ON foreign_orders
FOR SELECT
USING (customer_id = current_user_id());

-- Users only see their own orders
SELECT * FROM foreign_orders;  -- Filtered by policy
```

## Best Practices

### 1. Connection Pooling

```sql
-- Keep connections open
ALTER SERVER remote_server OPTIONS (ADD keep_connections 'on');

-- Monitor connections
SELECT 
    srvname,
    usename,
    pg_stat_get_activity(pid)
FROM pg_stat_activity
WHERE application_name LIKE '%fdw%';
```

### 2. Error Handling

```sql
-- Handle connection errors
DO $$
BEGIN
    PERFORM * FROM foreign_table LIMIT 1;
EXCEPTION
    WHEN OTHERS THEN
        RAISE NOTICE 'Foreign table unavailable: %', SQLERRM;
END;
$$;

-- Set statement timeout
SET statement_timeout = '30s';
SELECT * FROM foreign_table;
```

### 3. Monitoring

```sql
-- Check FDW performance
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE tablename LIKE 'foreign_%';

-- Monitor foreign server connections
SELECT * FROM pg_stat_activity
WHERE backend_type = 'background worker'
  AND application_name LIKE '%fdw%';
```

### 4. Documentation

```sql
-- Document foreign dependencies
COMMENT ON FOREIGN TABLE foreign_orders IS 
'Connects to production database: prod-db.example.com
Updated in real-time via postgres_fdw
Contact: dba@example.com';

COMMENT ON SERVER remote_server IS
'Production database server
Connection: prod-db.example.com:5432
Purpose: Real-time order data access';
```

### 5. Testing

```sql
-- Test foreign table access
SELECT 
    COUNT(*) as total_rows,
    MAX(updated_at) as last_update
FROM foreign_table;

-- Verify data freshness
SELECT 
    'foreign' as source,
    count(*) as count
FROM foreign_orders
UNION ALL
SELECT 
    'expected' as source,
    1000 as count;

-- Test write operations
BEGIN;
INSERT INTO foreign_table VALUES (...);
SELECT * FROM foreign_table WHERE ...;
ROLLBACK;  -- Test without committing
```

## Summary

Foreign Data Wrappers enable:
- **Remote Access**: Query data from other PostgreSQL instances, MySQL, Oracle, MongoDB, files
- **Integration**: Join local and remote data seamlessly
- **Pushdown**: Filters and aggregations executed on remote server
- **Security**: User mappings, SSL, access control
- **Performance**: Batch fetching, async execution, materialized views

FDWs turn PostgreSQL into a powerful data integration platform.

## Next Steps

- Learn about [Extensions](./28-extensions.md)
- Explore [Partitioning](./23-partitioning.md)
- Study [Performance Optimization](./20-query-optimization.md)
- Practice [Data Import/Export](./19-data-import-export.md)
