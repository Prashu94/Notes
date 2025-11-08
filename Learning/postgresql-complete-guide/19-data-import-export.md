# Data Import and Export

## Overview

PostgreSQL provides multiple methods for importing and exporting data, including COPY command, pg_dump/pg_restore utilities, CSV files, JSON data, and foreign data wrappers. Choosing the right method depends on data volume, format requirements, and performance needs.

## Table of Contents
- [COPY Command](#copy-command)
- [CSV Import/Export](#csv-importexport)
- [pg_dump and pg_restore](#pg_dump-and-pg_restore)
- [Bulk Loading](#bulk-loading)
- [JSON Import/Export](#json-importexport)
- [Foreign Data Wrappers](#foreign-data-wrappers)
- [Data Migration Strategies](#data-migration-strategies)
- [Performance Optimization](#performance-optimization)

## COPY Command

The fastest way to import/export large amounts of data.

### Basic COPY Syntax

```sql
-- Export table to file
COPY employees TO '/tmp/employees.csv' WITH (FORMAT CSV, HEADER);

-- Export query results
COPY (
    SELECT employee_id, employee_name, salary
    FROM employees
    WHERE department = 'Engineering'
) TO '/tmp/engineering_employees.csv' WITH CSV HEADER;

-- Import from file
COPY employees FROM '/tmp/employees.csv' WITH (FORMAT CSV, HEADER);

-- Import specific columns
COPY employees (employee_id, employee_name, salary)
FROM '/tmp/employees.csv'
WITH (FORMAT CSV, HEADER);
```

### COPY Options

```sql
-- Full option syntax
COPY table_name [ ( column_list ) ]
FROM '/path/to/file'
WITH (
    FORMAT format_name,           -- CSV, TEXT, BINARY
    DELIMITER 'delimiter_char',   -- Field separator (default: comma for CSV)
    NULL 'null_string',           -- String representing NULL (default: empty)
    HEADER [ boolean ],           -- First line is header
    QUOTE 'quote_char',          -- Quote character (default: ")
    ESCAPE 'escape_char',        -- Escape character (default: same as QUOTE)
    ENCODING 'encoding_name',    -- File encoding (e.g., UTF8, LATIN1)
    FREEZE [ boolean ]           -- Optimize for bulk loading
);

-- Example with all options
COPY products FROM '/tmp/products.csv' WITH (
    FORMAT CSV,
    DELIMITER ',',
    NULL 'NULL',
    HEADER true,
    QUOTE '"',
    ESCAPE '\',
    ENCODING 'UTF8'
);

-- Tab-delimited files
COPY employees FROM '/tmp/employees.tsv' WITH (
    DELIMITER E'\t',
    NULL 'NULL'
);

-- Custom delimiter
COPY data FROM '/tmp/data.txt' WITH (
    DELIMITER '|',
    NULL 'N/A'
);
```

### COPY with STDIN/STDOUT

```sql
-- From standard input (useful in scripts)
COPY employees FROM STDIN WITH CSV HEADER;
1,John Doe,50000
2,Jane Smith,60000
3,Bob Johnson,55000
\.

-- To standard output
COPY employees TO STDOUT WITH CSV HEADER;

-- Using psql \copy for client-side files
\copy employees FROM '/local/path/employees.csv' WITH CSV HEADER
\copy employees TO '/local/path/employees.csv' WITH CSV HEADER

-- Difference: COPY runs on server, \copy runs on client
```

### Handling Errors in COPY

```sql
-- COPY stops on first error by default
-- Use transactions for safety
BEGIN;
COPY employees FROM '/tmp/employees.csv' WITH CSV HEADER;
-- Check if import looks correct
SELECT COUNT(*) FROM employees;
ROLLBACK; -- or COMMIT if satisfied

-- Import into staging table first
CREATE TABLE employees_staging (LIKE employees);

COPY employees_staging FROM '/tmp/employees.csv' WITH CSV HEADER;

-- Validate data
SELECT * FROM employees_staging WHERE salary < 0;

-- Insert valid data
INSERT INTO employees
SELECT * FROM employees_staging
WHERE salary >= 0 AND email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z]{2,}$';

DROP TABLE employees_staging;
```

## CSV Import/Export

### Exporting to CSV

```sql
-- Basic CSV export
COPY customers TO '/tmp/customers.csv' 
WITH (FORMAT CSV, HEADER true);

-- Export with custom options
COPY orders TO '/tmp/orders.csv' WITH (
    FORMAT CSV,
    HEADER true,
    DELIMITER ',',
    QUOTE '"',
    FORCE_QUOTE (customer_name, notes),  -- Always quote these columns
    NULL 'NULL'
);

-- Export query results
COPY (
    SELECT 
        o.order_id,
        c.customer_name,
        o.order_date,
        o.total_amount,
        CASE 
            WHEN o.status = 'completed' THEN 'Complete'
            WHEN o.status = 'pending' THEN 'Pending'
            ELSE 'Unknown'
        END as status_description
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    WHERE o.order_date >= '2024-01-01'
    ORDER BY o.order_date DESC
) TO '/tmp/orders_2024.csv' WITH CSV HEADER;

-- Export with UTF-8 BOM (for Excel)
COPY (
    SELECT E'\uFEFF' || column1::text as column1, column2, column3
    FROM my_table
    LIMIT 1
    UNION ALL
    SELECT column1, column2, column3
    FROM my_table
) TO '/tmp/excel_friendly.csv' WITH CSV;
```

### Importing from CSV

```sql
-- Basic import
COPY products FROM '/tmp/products.csv' WITH CSV HEADER;

-- Import with data transformation
CREATE TEMP TABLE products_temp AS SELECT * FROM products LIMIT 0;

COPY products_temp FROM '/tmp/products.csv' WITH CSV HEADER;

INSERT INTO products (product_name, price, category)
SELECT 
    TRIM(product_name),
    ROUND(price::numeric, 2),
    LOWER(category)
FROM products_temp;

-- Import with constraints handling
-- Disable triggers during import
ALTER TABLE products DISABLE TRIGGER ALL;

COPY products FROM '/tmp/products.csv' WITH CSV HEADER;

-- Re-enable triggers
ALTER TABLE products ENABLE TRIGGER ALL;

-- Handle duplicate keys
CREATE TABLE products_import (LIKE products);

COPY products_import FROM '/tmp/products.csv' WITH CSV HEADER;

INSERT INTO products
SELECT * FROM products_import
ON CONFLICT (product_id) DO UPDATE SET
    product_name = EXCLUDED.product_name,
    price = EXCLUDED.price,
    updated_at = CURRENT_TIMESTAMP;
```

### Working with Excel Files

```sql
-- Excel saves as CSV with specific characteristics
COPY data FROM '/tmp/excel_export.csv' WITH (
    FORMAT CSV,
    HEADER true,
    DELIMITER ',',
    QUOTE '"',
    ENCODING 'UTF8'
);

-- Handle Excel's date format
CREATE TABLE temp_import (
    id INTEGER,
    name TEXT,
    date_text TEXT  -- Import as text first
);

COPY temp_import FROM '/tmp/excel_dates.csv' WITH CSV HEADER;

-- Convert Excel dates (days since 1900-01-01)
INSERT INTO final_table (id, name, date_column)
SELECT 
    id,
    name,
    DATE '1900-01-01' + (date_text::integer - 2) -- Excel has leap year bug
FROM temp_import;
```

## pg_dump and pg_restore

### pg_dump - Database Backup

```bash
# Full database dump (SQL format)
pg_dump dbname > backup.sql

# Compressed custom format (recommended)
pg_dump -Fc dbname > backup.dump

# Directory format (parallel restore)
pg_dump -Fd dbname -f backup_dir

# Specific schemas
pg_dump -n schema_name dbname > schema_backup.sql

# Specific tables
pg_dump -t table_name dbname > table_backup.sql
pg_dump -t 'schema.table*' dbname > tables_backup.sql  # Pattern matching

# Exclude tables
pg_dump --exclude-table=logs --exclude-table=temp_* dbname > backup.sql

# Data only (no schema)
pg_dump --data-only dbname > data.sql

# Schema only (no data)
pg_dump --schema-only dbname > schema.sql

# Include/exclude specific objects
pg_dump --exclude-table-data=audit_logs \
        --no-owner \
        --no-privileges \
        dbname > backup.sql

# Dump to remote server
pg_dump -h remote_host -U username dbname > backup.sql

# Split large dumps
pg_dump dbname | gzip > backup.sql.gz
pg_dump dbname | split -b 1000m - backup.sql.part_
```

### pg_restore - Restore from Backup

```bash
# Restore from custom format
pg_restore -d dbname backup.dump

# Restore from directory format
pg_restore -d dbname backup_dir

# Parallel restore (faster)
pg_restore -j 4 -d dbname backup.dump  # 4 parallel jobs

# Restore specific table
pg_restore -t table_name -d dbname backup.dump

# Restore specific schema
pg_restore -n schema_name -d dbname backup.dump

# Create new database and restore
createdb new_database
pg_restore -d new_database backup.dump

# Restore with options
pg_restore --clean \          # Drop objects before recreating
           --if-exists \      # Use IF EXISTS when dropping
           --no-owner \       # Don't restore ownership
           --no-privileges \  # Don't restore access privileges
           -d dbname backup.dump

# List contents without restoring
pg_restore -l backup.dump > contents.txt

# Selective restore using list
pg_restore -L contents.txt -d dbname backup.dump
```

### SQL Format Backup and Restore

```bash
# Create SQL backup
pg_dump dbname > backup.sql

# Restore SQL backup
psql dbname < backup.sql

# With connection options
psql -h localhost -U postgres dbname < backup.sql

# Compressed SQL backup
pg_dump dbname | gzip > backup.sql.gz
gunzip -c backup.sql.gz | psql dbname

# View SQL backup contents
less backup.sql
grep "CREATE TABLE" backup.sql
```

## Bulk Loading

### Optimizing Bulk Inserts

```sql
-- 1. Drop indexes before loading
DROP INDEX IF EXISTS idx_employees_department;
DROP INDEX IF EXISTS idx_employees_salary;

-- 2. Disable triggers
ALTER TABLE employees DISABLE TRIGGER ALL;

-- 3. Use COPY with FREEZE
COPY employees FROM '/tmp/employees.csv' WITH (FORMAT CSV, HEADER, FREEZE true);

-- 4. Recreate indexes
CREATE INDEX idx_employees_department ON employees(department);
CREATE INDEX idx_employees_salary ON employees(salary);

-- 5. Re-enable triggers
ALTER TABLE employees ENABLE TRIGGER ALL;

-- 6. Update statistics
ANALYZE employees;

-- Alternative: Use UNLOGGED table for staging
CREATE UNLOGGED TABLE employees_stage (LIKE employees);

COPY employees_stage FROM '/tmp/employees.csv' WITH CSV HEADER;

-- Convert to logged and move data
ALTER TABLE employees_stage SET LOGGED;

INSERT INTO employees SELECT * FROM employees_stage;

DROP TABLE employees_stage;
```

### Parallel Loading

```bash
# Split large file
split -l 100000 large_file.csv part_

# Load in parallel (separate connections)
# Terminal 1
\copy table FROM 'part_aa' WITH CSV HEADER

# Terminal 2
\copy table FROM 'part_ab' WITH CSV HEADER

# Terminal 3
\copy table FROM 'part_ac' WITH CSV HEADER

# Or use GNU parallel
parallel psql -c "COPY table FROM STDIN WITH CSV HEADER" < {} ::: part_*
```

### Using COPY with Program

```sql
-- Import from compressed file
COPY employees FROM PROGRAM 'gunzip -c /tmp/employees.csv.gz'
WITH CSV HEADER;

-- Import from URL (requires curl)
COPY products FROM PROGRAM 'curl -s https://example.com/products.csv'
WITH CSV HEADER;

-- Export to compressed file
COPY employees TO PROGRAM 'gzip > /tmp/employees.csv.gz'
WITH CSV HEADER;

-- Export to S3 (with AWS CLI)
COPY large_table TO PROGRAM 'aws s3 cp - s3://bucket/backup.csv'
WITH CSV HEADER;
```

## JSON Import/Export

### Exporting to JSON

```sql
-- Export table as JSON
COPY (
    SELECT json_agg(row_to_json(customers)) 
    FROM customers
) TO '/tmp/customers.json';

-- Export with custom JSON structure
COPY (
    SELECT json_agg(
        json_build_object(
            'id', customer_id,
            'name', customer_name,
            'email', email,
            'orders', (
                SELECT json_agg(
                    json_build_object(
                        'order_id', order_id,
                        'date', order_date,
                        'total', total_amount
                    )
                )
                FROM orders
                WHERE orders.customer_id = customers.customer_id
            )
        )
    )
    FROM customers
) TO '/tmp/customers_with_orders.json';

-- Export as JSONL (JSON Lines - one object per line)
COPY (
    SELECT row_to_json(products)
    FROM products
) TO '/tmp/products.jsonl';

-- Pretty-printed JSON
COPY (
    SELECT jsonb_pretty(jsonb_agg(row_to_json(t)))
    FROM (SELECT * FROM customers LIMIT 10) t
) TO '/tmp/customers_pretty.json';
```

### Importing from JSON

```sql
-- Create table to hold JSON
CREATE TABLE json_import (data JSONB);

-- Import JSON file
COPY json_import FROM '/tmp/data.json';

-- Extract data from JSONB
INSERT INTO customers (customer_id, customer_name, email)
SELECT 
    (item->>'id')::INTEGER,
    item->>'name',
    item->>'email'
FROM json_import, jsonb_array_elements(data) AS item;

-- Import JSONL (one JSON object per line)
CREATE TABLE jsonl_import (data JSONB);

COPY jsonl_import FROM '/tmp/data.jsonl';

INSERT INTO products (product_id, product_name, price)
SELECT 
    (data->>'id')::INTEGER,
    data->>'name',
    (data->>'price')::NUMERIC
FROM jsonl_import;
```

### Working with JSON APIs

```sql
-- Import from REST API
CREATE EXTENSION IF NOT EXISTS http;

-- Fetch and import JSON data
WITH api_data AS (
    SELECT content::jsonb as data
    FROM http_get('https://api.example.com/products')
)
INSERT INTO products (product_id, product_name, price)
SELECT 
    (item->>'id')::INTEGER,
    item->>'name',
    (item->>'price')::NUMERIC
FROM api_data, jsonb_array_elements(data->'products') AS item;
```

## Foreign Data Wrappers

### file_fdw - Access CSV Files as Tables

```sql
-- Install extension
CREATE EXTENSION file_fdw;

-- Create foreign server
CREATE SERVER file_server FOREIGN DATA WRAPPER file_fdw;

-- Create foreign table
CREATE FOREIGN TABLE employees_csv (
    employee_id INTEGER,
    employee_name TEXT,
    department TEXT,
    salary NUMERIC
) SERVER file_server
OPTIONS (
    filename '/tmp/employees.csv',
    format 'csv',
    header 'true',
    delimiter ',',
    null ''
);

-- Query CSV file directly
SELECT * FROM employees_csv WHERE department = 'Engineering';

-- Import from foreign table
INSERT INTO employees 
SELECT * FROM employees_csv;
```

### postgres_fdw - Access Remote PostgreSQL

```sql
-- Install extension
CREATE EXTENSION postgres_fdw;

-- Create server connection
CREATE SERVER remote_db
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote.example.com', port '5432', dbname 'remote_database');

-- Create user mapping
CREATE USER MAPPING FOR CURRENT_USER
SERVER remote_db
OPTIONS (user 'remote_user', password 'remote_password');

-- Import foreign schema
IMPORT FOREIGN SCHEMA public
FROM SERVER remote_db
INTO local_schema;

-- Query remote table
SELECT * FROM local_schema.remote_table;

-- Join local and remote tables
SELECT l.*, r.data
FROM local_table l
JOIN local_schema.remote_table r ON l.id = r.id;

-- Copy data from remote
INSERT INTO local_table
SELECT * FROM local_schema.remote_table
WHERE created_at > '2024-01-01';
```

## Data Migration Strategies

### Zero-Downtime Migration

```sql
-- 1. Create new table with desired structure
CREATE TABLE employees_new (
    employee_id SERIAL PRIMARY KEY,
    employee_name TEXT NOT NULL,
    email TEXT UNIQUE,
    salary NUMERIC(10,2),
    department_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Initial data copy
INSERT INTO employees_new (employee_id, employee_name, email, salary, department_id)
SELECT employee_id, name, email, salary, dept_id
FROM employees_old;

-- 3. Create trigger to keep in sync
CREATE OR REPLACE FUNCTION sync_employees()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO employees_new (employee_id, employee_name, email, salary, department_id)
        VALUES (NEW.employee_id, NEW.name, NEW.email, NEW.salary, NEW.dept_id);
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE employees_new
        SET employee_name = NEW.name,
            email = NEW.email,
            salary = NEW.salary,
            department_id = NEW.dept_id
        WHERE employee_id = NEW.employee_id;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM employees_new WHERE employee_id = OLD.employee_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sync_trigger
AFTER INSERT OR UPDATE OR DELETE ON employees_old
FOR EACH ROW EXECUTE FUNCTION sync_employees();

-- 4. Verify data
SELECT COUNT(*) FROM employees_old;
SELECT COUNT(*) FROM employees_new;

-- 5. Switch tables (in transaction)
BEGIN;
    ALTER TABLE employees_old RENAME TO employees_backup;
    ALTER TABLE employees_new RENAME TO employees;
    DROP TRIGGER sync_trigger ON employees_backup;
COMMIT;
```

### Cross-Database Migration

```bash
# Direct pipe (same PostgreSQL version)
pg_dump -h source_host source_db | psql -h dest_host dest_db

# With transformation
pg_dump -h source_host source_db | \
    sed 's/old_schema/new_schema/g' | \
    psql -h dest_host dest_db

# Using intermediate file
pg_dump -Fc -h source_host source_db > backup.dump
pg_restore -d dest_db -h dest_host backup.dump

# Table-by-table migration
pg_dump -t table_name source_db | psql dest_db
```

## Performance Optimization

### Import Performance Tips

```sql
-- 1. Increase maintenance_work_mem
SET maintenance_work_mem = '1GB';

-- 2. Disable autovacuum during import
ALTER TABLE employees SET (autovacuum_enabled = false);

-- 3. Use COPY instead of INSERT
-- COPY is 10-100x faster than individual INSERTs

-- 4. Batch inserts if not using COPY
INSERT INTO employees (name, salary)
SELECT name, salary FROM unnest(
    ARRAY['John', 'Jane', 'Bob'],
    ARRAY[50000, 60000, 55000]
) AS t(name, salary);

-- 5. Drop foreign keys during import
ALTER TABLE orders DROP CONSTRAINT fk_customer;
-- Import data
ALTER TABLE orders ADD CONSTRAINT fk_customer 
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id);

-- 6. Use UNLOGGED tables for staging
CREATE UNLOGGED TABLE staging_table (...);
-- Load data into staging
-- Transform and load to final table
ALTER TABLE staging_table SET LOGGED;

-- 7. Increase checkpoint_timeout
-- In postgresql.conf: checkpoint_timeout = 30min

-- 8. Use parallel operations
SET max_parallel_workers_per_gather = 4;
```

### Export Performance Tips

```sql
-- Use COPY instead of SELECT
-- COPY is much faster for large datasets

-- Compress output on the fly
COPY large_table TO PROGRAM 'gzip > /tmp/large_table.csv.gz' WITH CSV HEADER;

-- Export in parallel (split by partition or range)
-- Terminal 1
COPY (SELECT * FROM large_table WHERE id < 1000000) 
TO '/tmp/part1.csv' WITH CSV HEADER;

-- Terminal 2
COPY (SELECT * FROM large_table WHERE id >= 1000000 AND id < 2000000)
TO '/tmp/part2.csv' WITH CSV HEADER;

-- Use binary format for speed (not human-readable)
COPY table_name TO '/tmp/data.bin' WITH BINARY;
```

## Best Practices

1. **Always use transactions** for imports
2. **Validate data** in staging table before final insert
3. **Use COPY** instead of INSERT for bulk operations
4. **Drop indexes/constraints** before large imports
5. **Use UNLOGGED tables** for temporary staging
6. **Compress large exports** to save space
7. **Test restore process** regularly
8. **Document schema changes** in migration scripts
9. **Use pg_dump custom format** for flexibility
10. **Monitor disk space** during operations

## Common Pitfalls

1. **Character encoding mismatches**: Always specify encoding
2. **Missing HEADER option**: Leads to header row as data
3. **Wrong delimiter**: CSV vs TSV confusion
4. **File permissions**: Server needs read/write access
5. **Path issues**: COPY uses server paths, \copy uses client paths
6. **Memory limits**: Large transactions can exhaust memory
7. **Lock contention**: Bulk operations lock tables
8. **Forgot to re-enable triggers**: Data integrity issues

## Summary

PostgreSQL data import/export provides:
- **COPY command**: Fastest bulk data transfer
- **pg_dump/pg_restore**: Complete database backups
- **CSV support**: Universal data exchange format
- **JSON handling**: Modern data interchange
- **Foreign Data Wrappers**: Access external data sources
- **Parallel operations**: Scale for large datasets

Choose the right tool based on data volume, format, and performance requirements.

## Next Steps

- Learn about [Backup and Recovery](./35-backup-and-recovery.md) strategies
- Explore [Performance Optimization](./20-query-optimization.md)
- Study [Foreign Data Wrappers](./29-foreign-data-wrappers.md) in detail
- Practice [Migration Strategies](./51-migration-strategies.md)
