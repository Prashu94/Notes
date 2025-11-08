# Schemas and Namespaces

## Overview

Schemas in PostgreSQL provide logical namespaces for organizing database objects, enabling multi-tenant applications, permission management, and name collision avoidance. This comprehensive guide covers schema creation, search paths, permissions, multi-tenant architectures, and best practices for schema design.

## Table of Contents

- [Schema Fundamentals](#schema-fundamentals)
- [Creating and Managing Schemas](#creating-and-managing-schemas)
- [Search Path](#search-path)
- [Schema Permissions](#schema-permissions)
- [Multi-Tenant Architecture](#multi-tenant-architecture)
- [Schema Organization Patterns](#schema-organization-patterns)
- [Schema Management](#schema-management)
- [Best Practices](#best-practices)

## Schema Fundamentals

### What Are Schemas?

```sql
-- Schemas: Logical namespaces within a database
-- Benefits:
-- 1. Organization: Group related objects
-- 2. Permissions: Grant/revoke access per schema
-- 3. Multi-tenancy: Isolate tenant data
-- 4. Name collision: Same object name in different schemas
-- 5. Modularity: Separate application components

-- Default schemas:
-- public: Default schema for user objects
-- pg_catalog: System catalog (built-in objects)
-- information_schema: SQL standard views

-- View existing schemas
SELECT
    nspname AS schema_name,
    pg_catalog.pg_get_userbyid(nspowner) AS owner,
    nspacl AS access_privileges
FROM pg_namespace
WHERE nspname NOT LIKE 'pg_%'
AND nspname != 'information_schema'
ORDER BY nspname;

-- Check current schema
SELECT current_schema();

-- Fully qualified object name
-- schema_name.object_name
SELECT * FROM public.users;
SELECT * FROM app_schema.orders;

-- Schema hierarchy: Database -> Schema -> Table
-- Example structure:
-- mydb (database)
--   ├── public (schema)
--   │   ├── users (table)
--   │   └── products (table)
--   ├── accounting (schema)
--   │   ├── invoices (table)
--   │   └── payments (table)
--   └── reporting (schema)
--       ├── sales_summary (view)
--       └── customer_stats (materialized view)
```

### Schema Use Cases

```sql
-- Use Case 1: Application Modularity
-- Separate schemas for different modules
CREATE SCHEMA auth;        -- Authentication/authorization
CREATE SCHEMA inventory;   -- Inventory management
CREATE SCHEMA billing;     -- Billing system
CREATE SCHEMA reporting;   -- Reports and analytics

CREATE TABLE auth.users (id SERIAL PRIMARY KEY, username VARCHAR(50));
CREATE TABLE inventory.products (id SERIAL PRIMARY KEY, name VARCHAR(100));
CREATE TABLE billing.invoices (id SERIAL PRIMARY KEY, amount NUMERIC);

-- Use Case 2: Multi-Tenant Applications
-- One schema per tenant
CREATE SCHEMA tenant_acme;
CREATE SCHEMA tenant_globex;

CREATE TABLE tenant_acme.customers (id SERIAL PRIMARY KEY, name VARCHAR(100));
CREATE TABLE tenant_globex.customers (id SERIAL PRIMARY KEY, name VARCHAR(100));
-- Same table name, different schemas (isolation)

-- Use Case 3: Development Environments
-- Separate schemas for dev, test, prod
CREATE SCHEMA dev;
CREATE SCHEMA test;
CREATE SCHEMA prod;

-- Deploy same structure to each
CREATE TABLE dev.users (id INT, name VARCHAR(100));
CREATE TABLE test.users (id INT, name VARCHAR(100));
CREATE TABLE prod.users (id INT, name VARCHAR(100));

-- Use Case 4: Versioning
-- Multiple API versions
CREATE SCHEMA api_v1;
CREATE SCHEMA api_v2;

CREATE VIEW api_v1.user_list AS SELECT id, name FROM users;
CREATE VIEW api_v2.user_list AS SELECT id, name, email FROM users; -- New field

-- Use Case 5: Permissions Management
-- Separate read-only and read-write schemas
CREATE SCHEMA data_read;    -- Read-only views
CREATE SCHEMA data_write;   -- Editable tables

CREATE VIEW data_read.customers AS SELECT * FROM data_write.customers;
GRANT SELECT ON ALL TABLES IN SCHEMA data_read TO readonly_role;
```

## Creating and Managing Schemas

### Creating Schemas

```sql
-- Create basic schema
CREATE SCHEMA app_schema;

-- Create schema with owner
CREATE SCHEMA app_schema AUTHORIZATION app_user;

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS app_schema;

-- Create schema and objects in one statement
CREATE SCHEMA hr AUTHORIZATION hr_admin
    CREATE TABLE employees (
        id SERIAL PRIMARY KEY,
        name VARCHAR(100),
        department VARCHAR(50)
    )
    CREATE TABLE departments (
        id SERIAL PRIMARY KEY,
        name VARCHAR(50)
    );

-- Verify creation
SELECT nspname FROM pg_namespace WHERE nspname = 'app_schema';

-- Create multiple schemas
DO $$
BEGIN
    FOR i IN 1..5 LOOP
        EXECUTE format('CREATE SCHEMA IF NOT EXISTS tenant_%s', i);
    END LOOP;
END $$;
```

### Modifying Schemas

```sql
-- Rename schema
ALTER SCHEMA app_schema RENAME TO application_schema;

-- Change schema owner
ALTER SCHEMA application_schema OWNER TO new_owner;

-- Drop schema (must be empty)
DROP SCHEMA application_schema;

-- Drop schema and all objects
DROP SCHEMA application_schema CASCADE;
-- WARNING: Deletes all tables, views, functions, etc. in schema

-- Drop only if exists
DROP SCHEMA IF EXISTS application_schema CASCADE;

-- Move object between schemas
ALTER TABLE public.users SET SCHEMA app_schema;
-- Now accessible as app_schema.users

ALTER VIEW public.user_stats SET SCHEMA reporting;

ALTER FUNCTION public.calculate_total() SET SCHEMA utils;

-- Move all tables from one schema to another
DO $$
DECLARE
    tbl RECORD;
BEGIN
    FOR tbl IN
        SELECT tablename
        FROM pg_tables
        WHERE schemaname = 'public'
    LOOP
        EXECUTE format('ALTER TABLE public.%I SET SCHEMA app_schema', tbl.tablename);
    END LOOP;
END $$;
```

## Search Path

### Understanding Search Path

```sql
-- Search path: Order of schemas PostgreSQL searches for unqualified object names
-- Default: "$user", public

-- View current search path
SHOW search_path;
-- Default output: "$user", public
-- "$user" means schema with same name as current user (if exists)

-- How search path works:
-- Query: SELECT * FROM users;
-- PostgreSQL searches:
-- 1. Schema named after current user (if exists)
-- 2. public schema
-- 3. Error if not found: relation "users" does not exist

-- Set search path for session
SET search_path TO app_schema, public;

-- Now unqualified names search app_schema first
SELECT * FROM users;  -- Finds app_schema.users if exists, else public.users

-- Set multiple schemas in search path
SET search_path TO app_schema, reporting, utils, public;

-- Set search path permanently for user
ALTER USER myuser SET search_path = app_schema, public;

-- Set search path for database
ALTER DATABASE mydb SET search_path = app_schema, public;

-- Include pg_catalog explicitly (usually implicit)
SET search_path TO app_schema, pg_catalog, public;

-- Reset to default
RESET search_path;

-- Example: Search path in action
CREATE SCHEMA schema1;
CREATE SCHEMA schema2;

CREATE TABLE schema1.products (id INT, name VARCHAR(50));
CREATE TABLE schema2.products (id INT, name VARCHAR(50));

INSERT INTO schema1.products VALUES (1, 'Product A');
INSERT INTO schema2.products VALUES (2, 'Product B');

-- Set search path to schema1
SET search_path TO schema1, public;
SELECT * FROM products;  -- Returns schema1.products (Product A)

-- Set search path to schema2
SET search_path TO schema2, public;
SELECT * FROM products;  -- Returns schema2.products (Product B)

-- Always use fully qualified names to avoid ambiguity
SELECT * FROM schema1.products;  -- Explicit, clear
```

### Search Path Security

```sql
-- Security risk: Search path hijacking
-- Malicious user creates function in public schema
-- If public is in search path, might execute unintended function

-- Secure configuration: Remove public from search path
ALTER DATABASE mydb SET search_path = "$user";

-- Per-user search path (secure)
ALTER USER app_user SET search_path = app_schema, pg_catalog;

-- Function search_path (secure functions)
CREATE FUNCTION secure_function()
RETURNS INT
LANGUAGE SQL
SECURITY DEFINER
SET search_path = app_schema, pg_catalog
AS $$
    SELECT COUNT(*)::INT FROM users;
$$;
-- Function uses fixed search path, not caller's

-- Check functions with unsafe search_path
SELECT
    n.nspname AS schema,
    p.proname AS function_name,
    pg_get_functiondef(p.oid) AS definition
FROM pg_proc p
JOIN pg_namespace n ON n.oid = p.pronamespace
WHERE NOT prosecdef  -- Not security definer
OR prosecdef AND proconfig IS NULL  -- Security definer but no fixed search_path
ORDER BY n.nspname, p.proname;

-- Best practice: Always set search_path for SECURITY DEFINER functions
CREATE OR REPLACE FUNCTION safe_function()
RETURNS INT
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = app_schema, pg_catalog
AS $$
BEGIN
    RETURN (SELECT COUNT(*)::INT FROM users);
END;
$$;
```

## Schema Permissions

### Granting Schema Access

```sql
-- Grant USAGE (allows access to schema)
GRANT USAGE ON SCHEMA app_schema TO app_user;
-- User can see objects in schema

-- Grant CREATE (allows creating objects in schema)
GRANT CREATE ON SCHEMA app_schema TO app_user;
-- User can create tables, views, etc. in schema

-- Grant both USAGE and CREATE
GRANT USAGE, CREATE ON SCHEMA app_schema TO app_user;

-- Grant to multiple users
GRANT USAGE ON SCHEMA app_schema TO user1, user2, user3;

-- Grant to role
GRANT USAGE ON SCHEMA app_schema TO app_role;

-- Grant all permissions
GRANT ALL ON SCHEMA app_schema TO admin_user;

-- Revoke permissions
REVOKE CREATE ON SCHEMA app_schema FROM app_user;
REVOKE ALL ON SCHEMA app_schema FROM app_user;

-- Grant permissions on all tables in schema
GRANT SELECT ON ALL TABLES IN SCHEMA app_schema TO readonly_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA app_schema TO readwrite_user;

-- Grant permissions on future tables (for existing users)
ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema
GRANT SELECT ON TABLES TO readonly_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA app_schema
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO readwrite_user;

-- Check schema permissions
SELECT
    nspname AS schema_name,
    nspacl AS access_privileges
FROM pg_namespace
WHERE nspname = 'app_schema';

-- Check if user has permission
SELECT has_schema_privilege('app_user', 'app_schema', 'USAGE');
SELECT has_schema_privilege('app_user', 'app_schema', 'CREATE');

-- View all schema permissions
SELECT
    n.nspname AS schema,
    r.rolname AS grantee,
    privilege_type
FROM information_schema.role_usage_grants rug
JOIN pg_namespace n ON n.nspname = rug.object_schema
JOIN pg_roles r ON r.rolname = rug.grantee
WHERE rug.object_type = 'SCHEMA'
ORDER BY n.nspname, r.rolname;
```

### Schema Isolation

```sql
-- Complete isolation: Each user has own schema
CREATE USER alice PASSWORD 'password123';
CREATE USER bob PASSWORD 'password123';

CREATE SCHEMA AUTHORIZATION alice;
CREATE SCHEMA AUTHORIZATION bob;

-- Set default search path for each user
ALTER USER alice SET search_path = alice;
ALTER USER bob SET search_path = bob;

-- Each user creates tables in own schema
-- As alice:
CREATE TABLE users (id INT, name VARCHAR(50));  -- Creates alice.users

-- As bob:
CREATE TABLE users (id INT, name VARCHAR(50));  -- Creates bob.users

-- No conflicts, complete isolation

-- Shared read access to common schema
CREATE SCHEMA shared;
CREATE TABLE shared.reference_data (id INT, value TEXT);

GRANT USAGE ON SCHEMA shared TO alice, bob;
GRANT SELECT ON ALL TABLES IN SCHEMA shared TO alice, bob;

ALTER USER alice SET search_path = alice, shared;
ALTER USER bob SET search_path = bob, shared;

-- Now alice and bob can read shared.reference_data
```

## Multi-Tenant Architecture

### Schema-Based Multi-Tenancy

```sql
-- Multi-tenancy pattern: One schema per tenant
-- Advantages:
-- - Strong data isolation
-- - Per-tenant backups
-- - Easy tenant deletion
-- Disadvantages:
-- - Schema proliferation (PostgreSQL handles thousands well)
-- - Cross-tenant queries more complex

-- Create tenant schema
CREATE OR REPLACE FUNCTION create_tenant_schema(tenant_name TEXT)
RETURNS VOID AS $$
BEGIN
    -- Create schema
    EXECUTE format('CREATE SCHEMA %I', tenant_name);
    
    -- Create tables
    EXECUTE format('
        CREATE TABLE %I.customers (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            email VARCHAR(100)
        )', tenant_name);
    
    EXECUTE format('
        CREATE TABLE %I.orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES %I.customers(id),
            order_date DATE,
            total NUMERIC
        )', tenant_name, tenant_name);
    
    -- Create indexes
    EXECUTE format('CREATE INDEX idx_customers_email ON %I.customers(email)', tenant_name);
    
    RAISE NOTICE 'Tenant schema % created successfully', tenant_name;
END;
$$ LANGUAGE plpgsql;

-- Create tenants
SELECT create_tenant_schema('tenant_acme');
SELECT create_tenant_schema('tenant_globex');
SELECT create_tenant_schema('tenant_initech');

-- Tenant-specific user
CREATE USER acme_user PASSWORD 'secure_password';
GRANT USAGE ON SCHEMA tenant_acme TO acme_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA tenant_acme TO acme_user;
ALTER USER acme_user SET search_path = tenant_acme;

-- Application sets search path based on tenant
-- Example: SET search_path TO tenant_acme;
-- Then queries use unqualified names:
SELECT * FROM customers;  -- Accesses tenant_acme.customers

-- Cross-tenant query (admin only)
SELECT 'acme' AS tenant, COUNT(*) FROM tenant_acme.customers
UNION ALL
SELECT 'globex' AS tenant, COUNT(*) FROM tenant_globex.customers
UNION ALL
SELECT 'initech' AS tenant, COUNT(*) FROM tenant_initech.customers;

-- Delete tenant
DROP SCHEMA tenant_initech CASCADE;
```

### Row-Level Security Multi-Tenancy

```sql
-- Alternative: Single schema with RLS (Row-Level Security)
-- Advantages:
-- - Single schema (simpler)
-- - Easier cross-tenant queries
-- - Better for large number of tenants
-- Disadvantages:
-- - Requires tenant_id in every table
-- - More complex RLS policies

CREATE SCHEMA app;

CREATE TABLE app.customers (
    id SERIAL PRIMARY KEY,
    tenant_id INT NOT NULL,
    name VARCHAR(100),
    email VARCHAR(100)
);

CREATE INDEX idx_customers_tenant ON app.customers(tenant_id);

-- Enable RLS
ALTER TABLE app.customers ENABLE ROW LEVEL SECURITY;

-- RLS policy: Users see only their tenant's data
CREATE POLICY tenant_isolation ON app.customers
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::INT);

-- Application sets tenant context
-- SET app.tenant_id = '1';  -- For tenant 1
-- SET app.tenant_id = '2';  -- For tenant 2

-- Test RLS
INSERT INTO app.customers (tenant_id, name, email) VALUES
(1, 'Alice', 'alice@acme.com'),
(2, 'Bob', 'bob@globex.com');

-- Set tenant context
SET app.tenant_id = '1';
SELECT * FROM app.customers;  -- Sees only tenant_id = 1 (Alice)

SET app.tenant_id = '2';
SELECT * FROM app.customers;  -- Sees only tenant_id = 2 (Bob)

-- Compare: Schema-based vs RLS-based multi-tenancy
/*
Schema-Based:
✓ Stronger isolation
✓ Easier per-tenant operations (backup, delete)
✓ Simpler queries (no tenant_id filter)
✗ More schemas (management overhead)
✗ Cross-tenant queries harder

RLS-Based:
✓ Single schema (simpler structure)
✓ Easier cross-tenant queries
✓ Scales to more tenants
✗ Requires tenant_id everywhere
✗ RLS policy complexity
*/
```

## Schema Organization Patterns

### Application Module Pattern

```sql
-- Organize by application domain/module
CREATE SCHEMA auth;          -- Authentication
CREATE SCHEMA user_mgmt;     -- User management
CREATE SCHEMA products;      -- Product catalog
CREATE SCHEMA orders;        -- Order processing
CREATE SCHEMA payments;      -- Payment processing
CREATE SCHEMA notifications; -- Notification system
CREATE SCHEMA reporting;     -- Reports and analytics

-- Auth schema
CREATE TABLE auth.users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255)
);

CREATE TABLE auth.roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50)
);

CREATE TABLE auth.user_roles (
    user_id INT REFERENCES auth.users(id),
    role_id INT REFERENCES auth.roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- Products schema
CREATE TABLE products.categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100)
);

CREATE TABLE products.items (
    id SERIAL PRIMARY KEY,
    category_id INT REFERENCES products.categories(id),
    name VARCHAR(100),
    price NUMERIC
);

-- Orders schema (references other schemas)
CREATE TABLE orders.orders (
    id SERIAL PRIMARY KEY,
    user_id INT,  -- References auth.users(id)
    order_date DATE,
    status VARCHAR(20)
);

CREATE TABLE orders.order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders.orders(id),
    product_id INT,  -- References products.items(id)
    quantity INT,
    price NUMERIC
);

-- Add foreign key constraints across schemas
ALTER TABLE orders.orders
    ADD CONSTRAINT fk_orders_user
    FOREIGN KEY (user_id) REFERENCES auth.users(id);

ALTER TABLE orders.order_items
    ADD CONSTRAINT fk_order_items_product
    FOREIGN KEY (product_id) REFERENCES products.items(id);

-- Set appropriate permissions
GRANT USAGE ON SCHEMA auth TO app_user;
GRANT SELECT ON ALL TABLES IN SCHEMA auth TO app_user;

GRANT USAGE ON SCHEMA products, orders TO app_user;
GRANT ALL ON ALL TABLES IN SCHEMA products, orders TO app_user;
```

### Environment Pattern

```sql
-- Separate schemas for different environments
CREATE SCHEMA dev;
CREATE SCHEMA test;
CREATE SCHEMA staging;
CREATE SCHEMA prod;

-- Deploy same structure to each
CREATE OR REPLACE FUNCTION create_schema_tables(schema_name TEXT)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('
        CREATE TABLE %I.users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50)
        )', schema_name);
    
    EXECUTE format('
        CREATE TABLE %I.orders (
            id SERIAL PRIMARY KEY,
            user_id INT REFERENCES %I.users(id)
        )', schema_name, schema_name);
END;
$$ LANGUAGE plpgsql;

SELECT create_schema_tables('dev');
SELECT create_schema_tables('test');
SELECT create_schema_tables('staging');
SELECT create_schema_tables('prod');

-- Users access specific environment
ALTER USER dev_user SET search_path = dev;
ALTER USER test_user SET search_path = test;
ALTER USER prod_user SET search_path = prod;

-- Promote from dev to test
INSERT INTO test.users SELECT * FROM dev.users;
INSERT INTO test.orders SELECT * FROM dev.orders;
```

## Schema Management

### Schema Maintenance

```sql
-- List all schemas with sizes
SELECT
    nspname AS schema_name,
    pg_size_pretty(SUM(pg_total_relation_size(c.oid))) AS size
FROM pg_namespace n
LEFT JOIN pg_class c ON n.oid = c.relnamespace
WHERE nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
GROUP BY nspname
ORDER BY SUM(pg_total_relation_size(c.oid)) DESC;

-- List objects in schema
SELECT
    n.nspname AS schema,
    c.relname AS object_name,
    CASE c.relkind
        WHEN 'r' THEN 'table'
        WHEN 'i' THEN 'index'
        WHEN 'v' THEN 'view'
        WHEN 'm' THEN 'materialized view'
        WHEN 'S' THEN 'sequence'
        WHEN 'f' THEN 'foreign table'
    END AS object_type,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS size
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = 'app_schema'
AND c.relkind IN ('r', 'i', 'v', 'm', 'S', 'f')
ORDER BY pg_total_relation_size(c.oid) DESC;

-- Clone schema (structure only)
CREATE OR REPLACE FUNCTION clone_schema(source_schema TEXT, dest_schema TEXT)
RETURNS VOID AS $$
DECLARE
    object RECORD;
BEGIN
    EXECUTE format('CREATE SCHEMA %I', dest_schema);
    
    FOR object IN
        SELECT tablename FROM pg_tables WHERE schemaname = source_schema
    LOOP
        EXECUTE format('CREATE TABLE %I.%I (LIKE %I.%I INCLUDING ALL)',
            dest_schema, object.tablename, source_schema, object.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Clone schema (structure + data)
CREATE OR REPLACE FUNCTION clone_schema_with_data(source_schema TEXT, dest_schema TEXT)
RETURNS VOID AS $$
DECLARE
    object RECORD;
BEGIN
    EXECUTE format('CREATE SCHEMA %I', dest_schema);
    
    FOR object IN
        SELECT tablename FROM pg_tables WHERE schemaname = source_schema
    LOOP
        EXECUTE format('CREATE TABLE %I.%I AS SELECT * FROM %I.%I',
            dest_schema, object.tablename, source_schema, object.tablename);
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Backup schema
-- pg_dump --schema=app_schema --file=app_schema_backup.sql mydb

-- Restore schema
-- psql mydb < app_schema_backup.sql
```

### Schema Dependencies

```sql
-- View dependencies between schemas
SELECT DISTINCT
    n1.nspname AS source_schema,
    n2.nspname AS dependent_schema
FROM pg_depend d
JOIN pg_class c1 ON d.objid = c1.oid
JOIN pg_namespace n1 ON c1.relnamespace = n1.oid
JOIN pg_class c2 ON d.refobjid = c2.oid
JOIN pg_namespace n2 ON c2.relnamespace = n2.oid
WHERE n1.nspname != n2.nspname
AND n1.nspname NOT LIKE 'pg_%'
AND n2.nspname NOT LIKE 'pg_%'
ORDER BY n1.nspname, n2.nspname;

-- Find foreign keys across schemas
SELECT
    tc.table_schema AS source_schema,
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    ccu.table_schema AS target_schema,
    ccu.table_name AS target_table,
    ccu.column_name AS target_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
AND tc.table_schema != ccu.table_schema
ORDER BY tc.table_schema, tc.table_name;
```

## Best Practices

### Best Practices Checklist

```text
Schema Best Practices:

1. Schema Organization
   ✓ Use schemas for logical grouping (modules, tenants, environments)
   ✓ Keep related objects in same schema
   ✓ Avoid too many schemas (management overhead)
   ✓ Document schema purpose and organization

2. Naming Conventions
   ✓ Use descriptive schema names (auth, products, reporting)
   ✓ Avoid special characters and spaces
   ✓ Use lowercase names
   ✓ Consistent naming across project

3. Search Path
   ✓ Set explicit search_path per user/database
   ✓ Remove 'public' from search path for security
   ✓ Always include pg_catalog
   ✓ Document expected search_path

4. Permissions
   ✓ Grant USAGE before other permissions
   ✓ Use ALTER DEFAULT PRIVILEGES for future objects
   ✓ Principle of least privilege
   ✓ Regular permission audits

5. Multi-Tenancy
   ✓ Schema-based: For strong isolation, fewer tenants
   ✓ RLS-based: For many tenants, shared resources
   ✓ Hybrid: Schema-based with RLS for sub-tenants
   ✓ Benchmark before production

6. Security
   ✓ Remove public schema from search_path
   ✓ Set search_path for SECURITY DEFINER functions
   ✓ Grant permissions to roles, not individual users
   ✓ Monitor for privilege escalation

7. Maintenance
   ✓ Regular backups per schema
   ✓ Monitor schema sizes
   ✓ Document schema dependencies
   ✓ Clean up unused schemas

8. Cross-Schema References
   ✓ Minimize cross-schema foreign keys
   ✓ Document dependencies
   ✓ Consider impact on schema deletion
   ✓ Use views for cross-schema queries

9. Development Workflow
   ✓ Separate dev/test/prod schemas in same DB (if appropriate)
   ✓ Migration scripts schema-aware
   ✓ CI/CD schema deployment automation
   ✓ Version control schema definitions

10. Performance
    ✓ Indexes on frequently queried columns (all schemas)
    ✓ Monitor query performance per schema
    ✓ Partition large tables (schema-aware)
    ✓ VACUUM and ANALYZE all schemas

Common Mistakes to Avoid:
✗ Using public schema without securing it
✗ Not setting explicit search_path
✗ Granting permissions to 'public' role
✗ Creating too many schemas (management burden)
✗ Not documenting schema organization
✗ Ignoring cross-schema dependencies
✗ Not backing up all schemas
✗ Using different structures in tenant schemas
✗ Not testing schema isolation
✗ Hardcoding schema names in application
```

## Summary

Schemas provide powerful namespace organization in PostgreSQL:

- **Purpose**: Logical grouping, permissions management, multi-tenancy, name collision avoidance
- **Default Schemas**: public (user objects), pg_catalog (system), information_schema (SQL standard)
- **Search Path**: Defines schema lookup order for unqualified names
- **Permissions**: USAGE (access) and CREATE (create objects) per schema
- **Multi-Tenancy**: Schema-based (strong isolation) vs RLS-based (scalability)
- **Organization Patterns**: Application modules, environments, versioning
- **Security**: Remove public from search_path, use roles, set search_path for functions
- **Best Practices**: Logical organization, explicit search_path, least privilege, regular audits

Use schemas strategically for organization, security, and multi-tenancy.

## Next Steps

- Study [Permissions and Security](./27-authorization-and-permissions.md)
- Learn [Row-Level Security](./29-row-level-security.md)
- Explore [Multi-Tenant Architectures](./46-postgresql-internals.md)
- Practice [Database Design](./04-database-design-and-normalization.md)
