# Extensions

## Overview

PostgreSQL extensions are add-on modules that provide additional functionality beyond the core database system. Extensions enable features like full-text search, geographic data support, additional data types, foreign data wrappers, and much more.

## Table of Contents
- [Extension Basics](#extension-basics)
- [Popular Extensions](#popular-extensions)
- [Full-Text Search Extensions](#full-text-search-extensions)
- [Data Type Extensions](#data-type-extensions)
- [Foreign Data Wrappers](#foreign-data-wrappers)
- [Utility Extensions](#utility-extensions)
- [Performance Extensions](#performance-extensions)
- [Security Extensions](#security-extensions)
- [Custom Extensions](#custom-extensions)
- [Best Practices](#best-practices)

## Extension Basics

### Managing Extensions

```sql
-- List available extensions
SELECT * FROM pg_available_extensions ORDER BY name;

-- List installed extensions
SELECT * FROM pg_extension ORDER BY extname;

-- Get extension details
SELECT 
    e.extname,
    e.extversion,
    n.nspname as schema,
    c.description
FROM pg_extension e
LEFT JOIN pg_namespace n ON n.oid = e.extnamespace
LEFT JOIN pg_description c ON c.objoid = e.oid;

-- Install extension
CREATE EXTENSION IF NOT EXISTS extension_name;

-- Install in specific schema
CREATE EXTENSION extension_name SCHEMA schema_name;

-- Update extension
ALTER EXTENSION extension_name UPDATE;
ALTER EXTENSION extension_name UPDATE TO '2.0';

-- Drop extension
DROP EXTENSION extension_name;
DROP EXTENSION IF EXISTS extension_name CASCADE;

-- Check extension version
SELECT extversion FROM pg_extension WHERE extname = 'pg_trgm';
```

### Extension Dependencies

```sql
-- Some extensions require others
CREATE EXTENSION postgis;  -- May require postgis_topology

-- View extension dependencies
SELECT 
    e1.extname as extension,
    e2.extname as depends_on
FROM pg_depend d
JOIN pg_extension e1 ON e1.oid = d.objid
JOIN pg_extension e2 ON e2.oid = d.refobjid
WHERE d.deptype = 'e';
```

## Popular Extensions

### pg_trgm (Trigram Similarity)

Text similarity and fuzzy matching:

```sql
-- Install
CREATE EXTENSION pg_trgm;

-- Similarity matching
SELECT similarity('hello', 'hallo');  -- Returns: 0.5

-- Find similar strings
CREATE TABLE products (name TEXT);
INSERT INTO products VALUES ('PostgreSQL'), ('MySQL'), ('Oracle'), ('MongoDB');

SELECT name, similarity(name, 'postgres') as sim
FROM products
ORDER BY sim DESC;

-- Fuzzy search operator (%)
SELECT * FROM products WHERE name % 'postgres';

-- Create trigram index
CREATE INDEX idx_products_name_trgm ON products USING GIN (name gin_trgm_ops);

-- Or GiST index
CREATE INDEX idx_products_name_gist ON products USING GIST (name gist_trgm_ops);

-- Regular expression search with index support
SELECT * FROM products WHERE name ~ 'Post.*SQL';
-- Uses trigram index if available

-- Word similarity (PostgreSQL 9.6+)
SELECT word_similarity('postgres', 'PostgreSQL database');
SELECT strict_word_similarity('postgres', 'PostgreSQL database');
```

### uuid-ossp (UUID Generation)

Generate universally unique identifiers:

```sql
-- Install
CREATE EXTENSION "uuid-ossp";

-- Generate UUIDs
SELECT uuid_generate_v1();  -- Time-based UUID
SELECT uuid_generate_v4();  -- Random UUID

-- Use in table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

INSERT INTO users (username) VALUES ('john_doe');
SELECT * FROM users;

-- Other UUID functions
SELECT uuid_nil();  -- 00000000-0000-0000-0000-000000000000
SELECT uuid_ns_dns();  -- Namespace for DNS
SELECT uuid_ns_url();  -- Namespace for URLs
```

### hstore (Key-Value Store)

Store sets of key-value pairs:

```sql
-- Install
CREATE EXTENSION hstore;

-- Create table with hstore
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name TEXT,
    attributes HSTORE
);

-- Insert data
INSERT INTO products (name, attributes) VALUES
    ('Widget', 'color=>red, size=>large, material=>plastic'),
    ('Gadget', 'color=>blue, weight=>500g, battery=>lithium');

-- Query hstore
SELECT name, attributes->'color' as color FROM products;

-- Check key existence
SELECT * FROM products WHERE attributes ? 'battery';

-- Check multiple keys
SELECT * FROM products WHERE attributes ?& ARRAY['color', 'size'];

-- Get all keys
SELECT name, akeys(attributes) FROM products;

-- Get all values
SELECT name, avals(attributes) FROM products;

-- Convert to JSON
SELECT name, hstore_to_json(attributes) FROM products;

-- Update hstore
UPDATE products 
SET attributes = attributes || 'warranty=>2years'
WHERE name = 'Widget';

-- Delete key
UPDATE products 
SET attributes = delete(attributes, 'weight')
WHERE name = 'Gadget';

-- Create GIN index
CREATE INDEX idx_products_attributes ON products USING GIN(attributes);

-- Query with index
SELECT * FROM products WHERE attributes @> 'color=>red';
```

## Full-Text Search Extensions

### unaccent

Remove accents from text:

```sql
-- Install
CREATE EXTENSION unaccent;

-- Remove accents
SELECT unaccent('Héllo Wörld');  -- Result: Hello World
SELECT unaccent('São Paulo');     -- Result: Sao Paulo
SELECT unaccent('café');          -- Result: cafe

-- Use with full-text search
SELECT * FROM articles
WHERE to_tsvector('simple', unaccent(content)) @@ 
      to_tsquery('simple', unaccent('café'));

-- Create functional index
CREATE INDEX idx_articles_content_unaccent 
ON articles USING GIN (to_tsvector('simple', unaccent(content)));
```

### pg_trgm (for Full-Text)

Already covered, but useful for text search:

```sql
-- Fuzzy text search
SELECT * FROM articles 
WHERE title % 'postgress';  -- Matches 'PostgreSQL'

-- Pattern matching with index
SELECT * FROM articles 
WHERE content ~ 'data.*base';
```

## Data Type Extensions

### postgis (Geographic Data)

Spatial and geographic data support:

```sql
-- Install
CREATE EXTENSION postgis;

-- Create table with geography
CREATE TABLE locations (
    id SERIAL PRIMARY KEY,
    name TEXT,
    location GEOGRAPHY(POINT, 4326)
);

-- Insert data (longitude, latitude)
INSERT INTO locations (name, location) VALUES
    ('New York', ST_GeogFromText('POINT(-74.006 40.7128)')),
    ('Los Angeles', ST_GeogFromText('POINT(-118.2437 34.0522)')),
    ('Chicago', ST_GeogFromText('POINT(-87.6298 41.8781)'));

-- Calculate distance (in meters)
SELECT 
    l1.name as city1,
    l2.name as city2,
    ST_Distance(l1.location, l2.location) / 1000 as distance_km
FROM locations l1, locations l2
WHERE l1.name = 'New York' AND l2.name = 'Los Angeles';

-- Find nearby locations (within 1000km)
SELECT name
FROM locations
WHERE ST_DWithin(
    location,
    ST_GeogFromText('POINT(-74.006 40.7128)'),  -- New York
    1000000  -- 1000km in meters
);

-- Create spatial index
CREATE INDEX idx_locations_location ON locations USING GIST(location);
```

### citext (Case-Insensitive Text)

Case-insensitive text type:

```sql
-- Install
CREATE EXTENSION citext;

-- Create table with citext
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email CITEXT UNIQUE,
    username CITEXT UNIQUE
);

-- Case-insensitive operations
INSERT INTO users (email, username) VALUES 
    ('user@EXAMPLE.com', 'JohnDoe');

-- These all match
SELECT * FROM users WHERE email = 'user@example.com';
SELECT * FROM users WHERE email = 'USER@EXAMPLE.COM';
SELECT * FROM users WHERE username = 'johndoe';

-- Prevents case-variant duplicates
-- This will fail (duplicate):
-- INSERT INTO users (email) VALUES ('USER@example.com');
```

### ltree (Hierarchical Tree Structures)

Tree-like structures:

```sql
-- Install
CREATE EXTENSION ltree;

-- Create table
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT,
    path LTREE
);

-- Insert hierarchical data
INSERT INTO categories (name, path) VALUES
    ('Electronics', 'electronics'),
    ('Computers', 'electronics.computers'),
    ('Laptops', 'electronics.computers.laptops'),
    ('Desktops', 'electronics.computers.desktops'),
    ('Phones', 'electronics.phones'),
    ('Smartphones', 'electronics.phones.smartphones');

-- Query descendants
SELECT * FROM categories WHERE path <@ 'electronics.computers';

-- Query ancestors
SELECT * FROM categories WHERE path @> 'electronics.computers.laptops';

-- Match pattern
SELECT * FROM categories WHERE path ~ '*.computers.*';

-- Get all subcategories
SELECT * FROM categories WHERE path ~ 'electronics.computers.*';

-- Create index
CREATE INDEX idx_categories_path ON categories USING GIST(path);
```

## Foreign Data Wrappers

### postgres_fdw (Foreign PostgreSQL)

Connect to other PostgreSQL databases:

```sql
-- Install
CREATE EXTENSION postgres_fdw;

-- Create foreign server
CREATE SERVER foreign_db
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host 'remote-host.com', port '5432', dbname 'remote_db');

-- Create user mapping
CREATE USER MAPPING FOR CURRENT_USER
SERVER foreign_db
OPTIONS (user 'remote_user', password 'remote_password');

-- Import foreign schema
IMPORT FOREIGN SCHEMA public
FROM SERVER foreign_db
INTO local_schema;

-- Or create foreign table manually
CREATE FOREIGN TABLE foreign_users (
    id INTEGER,
    username TEXT,
    email TEXT
)
SERVER foreign_db
OPTIONS (schema_name 'public', table_name 'users');

-- Query foreign table
SELECT * FROM foreign_users;

-- Join local and foreign tables
SELECT 
    l.name,
    f.email
FROM local_table l
JOIN foreign_users f ON l.user_id = f.id;
```

### file_fdw (File Access)

Read CSV and text files:

```sql
-- Install
CREATE EXTENSION file_fdw;

-- Create server
CREATE SERVER file_server
FOREIGN DATA WRAPPER file_fdw;

-- Create foreign table
CREATE FOREIGN TABLE csv_data (
    id INTEGER,
    name TEXT,
    value NUMERIC
)
SERVER file_server
OPTIONS (filename '/path/to/file.csv', format 'csv', header 'true');

-- Query CSV file
SELECT * FROM csv_data;

-- Aggregate data from file
SELECT name, sum(value) FROM csv_data GROUP BY name;
```

## Utility Extensions

### pgcrypto (Cryptography)

Cryptographic functions:

```sql
-- Install
CREATE EXTENSION pgcrypto;

-- Hash functions
SELECT md5('password');
SELECT digest('password', 'sha256');
SELECT digest('password', 'sha512');

-- Generate random values
SELECT gen_random_uuid();
SELECT gen_random_bytes(16);

-- Password hashing (bcrypt)
SELECT crypt('my_password', gen_salt('bf'));

-- Verify password
SELECT crypt('my_password', '$2a$06$...') = '$2a$06$...';

-- Store hashed passwords
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT
);

INSERT INTO users (username, password_hash)
VALUES ('john', crypt('secret123', gen_salt('bf')));

-- Authenticate
SELECT * FROM users
WHERE username = 'john'
  AND password_hash = crypt('secret123', password_hash);

-- Encryption/Decryption
SELECT pgp_sym_encrypt('sensitive data', 'encryption_key');
SELECT pgp_sym_decrypt(
    pgp_sym_encrypt('sensitive data', 'encryption_key'),
    'encryption_key'
);
```

### tablefunc (Pivot Tables)

Cross-tabulation and pivot:

```sql
-- Install
CREATE EXTENSION tablefunc;

-- Crosstab example
CREATE TABLE sales (
    year INTEGER,
    quarter INTEGER,
    amount NUMERIC
);

INSERT INTO sales VALUES
    (2023, 1, 1000), (2023, 2, 1500), (2023, 3, 1200), (2023, 4, 1800),
    (2024, 1, 1100), (2024, 2, 1600);

-- Pivot data
SELECT * FROM crosstab(
    'SELECT year, quarter, amount FROM sales ORDER BY 1, 2',
    'SELECT generate_series(1, 4)'
) AS ct(year INTEGER, q1 NUMERIC, q2 NUMERIC, q3 NUMERIC, q4 NUMERIC);

-- Generate series
SELECT * FROM generate_series(1, 10);
SELECT * FROM generate_series('2024-01-01'::date, '2024-12-31'::date, '1 month');
```

### pg_stat_statements (Query Statistics)

Track query performance:

```sql
-- Install
CREATE EXTENSION pg_stat_statements;

-- Must also add to postgresql.conf:
-- shared_preload_libraries = 'pg_stat_statements'

-- View query statistics
SELECT 
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;

-- Find slow queries
SELECT 
    query,
    mean_exec_time,
    calls
FROM pg_stat_statements
WHERE mean_exec_time > 1000  -- > 1 second
ORDER BY mean_exec_time DESC;

-- Reset statistics
SELECT pg_stat_statements_reset();
```

## Performance Extensions

### pg_prewarm

Preload tables into cache:

```sql
-- Install
CREATE EXTENSION pg_prewarm;

-- Preload table into buffer cache
SELECT pg_prewarm('large_table');

-- Preload specific blocks
SELECT pg_prewarm('large_table', 'buffer', 'main', 0, 1000);

-- Use on startup (postgresql.conf):
-- shared_preload_libraries = 'pg_prewarm'
-- pg_prewarm.autoprewarm = true
```

### pg_buffercache

Inspect buffer cache:

```sql
-- Install
CREATE EXTENSION pg_buffercache;

-- View buffer cache contents
SELECT 
    c.relname,
    count(*) as buffers,
    pg_size_pretty(count(*) * 8192) as cached_size
FROM pg_buffercache b
JOIN pg_class c ON b.relfilenode = pg_relation_filenode(c.oid)
WHERE b.reldatabase = (SELECT oid FROM pg_database WHERE datname = current_database())
GROUP BY c.relname
ORDER BY buffers DESC
LIMIT 10;
```

## Security Extensions

### pgaudit

Audit logging:

```sql
-- Install
CREATE EXTENSION pgaudit;

-- Must configure in postgresql.conf:
-- shared_preload_libraries = 'pgaudit'
-- pgaudit.log = 'read, write, ddl'

-- Audit specific database
ALTER DATABASE mydb SET pgaudit.log = 'all';

-- Audit specific user
ALTER ROLE myuser SET pgaudit.log = 'write';

-- Session logging
SET pgaudit.log = 'ddl';
CREATE TABLE test (id INT);  -- This will be logged
```

### pgcrypto (covered above)

Additional security features:

```sql
-- Secure random token generation
SELECT encode(gen_random_bytes(32), 'hex') as token;

-- HMAC
SELECT encode(hmac('message', 'secret_key', 'sha256'), 'hex');
```

## Custom Extensions

### Creating Simple Extension

```sql
-- Create extension files

-- my_extension--1.0.sql:
CREATE FUNCTION hello(name TEXT) RETURNS TEXT AS $$
BEGIN
    RETURN 'Hello, ' || name || '!';
END;
$$ LANGUAGE plpgsql;

-- my_extension.control:
-- comment = 'My custom extension'
-- default_version = '1.0'
-- relocatable = true

-- Install
CREATE EXTENSION my_extension;

-- Use
SELECT hello('World');  -- Returns: Hello, World!
```

## Best Practices

### 1. Install Extensions Carefully

```sql
-- Always use IF NOT EXISTS
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Install in specific schema (not public)
CREATE SCHEMA extensions;
CREATE EXTENSION pg_trgm SCHEMA extensions;

-- Check before installing
SELECT * FROM pg_available_extensions 
WHERE name = 'desired_extension';
```

### 2. Manage Extension Updates

```sql
-- Check for updates
SELECT 
    extname,
    extversion as installed,
    default_version as available
FROM pg_extension e
JOIN pg_available_extensions ae ON e.extname = ae.name
WHERE extversion != default_version;

-- Update extension
ALTER EXTENSION pg_trgm UPDATE;

-- Or update to specific version
ALTER EXTENSION pg_trgm UPDATE TO '1.5';
```

### 3. Document Extension Dependencies

```sql
-- Document in migration scripts
-- Required extensions:
-- - pg_trgm (fuzzy text search)
-- - uuid-ossp (UUID generation)
-- - postgis (geographic data)

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

### 4. Monitor Extension Usage

```sql
-- Check installed extensions
SELECT 
    e.extname,
    e.extversion,
    n.nspname as schema,
    pg_size_pretty(pg_total_relation_size(n.nspname||'.'||e.extname)) as size
FROM pg_extension e
JOIN pg_namespace n ON e.extnamespace = n.oid;

-- Find unused extensions (manual review needed)
SELECT extname FROM pg_extension
WHERE extname NOT IN (
    -- List extensions you know are used
    'plpgsql', 'pg_trgm', 'uuid-ossp'
);
```

### 5. Security Considerations

```sql
-- Grant extension usage carefully
GRANT USAGE ON SCHEMA extensions TO app_user;

-- Some extensions require superuser
-- Create extensions in separate database/schema

-- Avoid installing extensions in production without testing
-- Test extensions in dev/staging first

-- Review extension code before installation
-- Extensions have full database access
```

## Summary

PostgreSQL extensions provide:
- **Text Processing**: pg_trgm (fuzzy search), unaccent (accent removal)
- **Data Types**: postgis (geographic), hstore (key-value), ltree (hierarchical)
- **Utilities**: uuid-ossp (UUID), pgcrypto (encryption), tablefunc (pivot)
- **Foreign Data**: postgres_fdw, file_fdw for external data access
- **Performance**: pg_stat_statements, pg_prewarm, pg_buffercache
- **Security**: pgaudit (audit logging), pgcrypto (encryption)

Extensions greatly extend PostgreSQL's capabilities beyond core features.

## Next Steps

- Learn about [Custom Functions](./17-stored-procedures-and-functions.md)
- Explore [Foreign Data Wrappers](./45-foreign-data-wrappers.md)
- Study [Performance Tuning](./34-configuration-and-tuning.md)
- Practice [Security](./32-user-management-and-security.md)
