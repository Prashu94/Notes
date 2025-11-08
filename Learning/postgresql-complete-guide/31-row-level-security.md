# Row-Level Security

## Overview

Row-Level Security (RLS) in PostgreSQL allows you to restrict which rows users can access or modify based on security policies. This provides fine-grained access control at the row level, complementing traditional table-level permissions.

## Table of Contents
- [RLS Basics](#rls-basics)
- [Creating Policies](#creating-policies)
- [Policy Types](#policy-types)
- [Using Policies](#using-policies)
- [Advanced Policies](#advanced-policies)
- [Performance Considerations](#performance-considerations)
- [Multi-Tenancy with RLS](#multi-tenancy-with-rls)
- [Debugging RLS](#debugging-rls)
- [Best Practices](#best-practices)

## RLS Basics

### Enabling Row-Level Security

```sql
-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    owner_id INTEGER NOT NULL,
    department TEXT,
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now()
);

-- Enable RLS on table
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Check if RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity
FROM pg_tables
WHERE tablename = 'documents';

-- Disable RLS
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- Force RLS (applies to table owner too)
ALTER TABLE documents FORCE ROW LEVEL SECURITY;
-- Without FORCE, table owner bypasses RLS by default
```

### How RLS Works

```sql
-- RLS flow:
-- 1. User queries table
-- 2. PostgreSQL checks applicable policies
-- 3. Adds policy conditions to WHERE clause
-- 4. Returns only matching rows

-- Without RLS:
SELECT * FROM documents;
-- Returns all rows

-- With RLS enabled (and policy):
SELECT * FROM documents;
-- Effectively becomes:
-- SELECT * FROM documents WHERE owner_id = current_user_id;

-- RLS is transparent to application
-- No query changes needed
```

## Creating Policies

### Basic Policy Syntax

```sql
-- CREATE POLICY syntax:
CREATE POLICY policy_name ON table_name
[FOR operation]
[TO roles]
[USING (condition)]
[WITH CHECK (condition)];

-- Simple SELECT policy
CREATE POLICY user_documents ON documents
FOR SELECT
USING (owner_id = current_user_id());

-- USING: determines which rows are visible
-- WITH CHECK: determines which rows can be modified
```

### Policy for All Operations

```sql
-- Policy applying to all operations
CREATE POLICY user_access ON documents
FOR ALL
USING (owner_id = current_user_id())
WITH CHECK (owner_id = current_user_id());

-- Equivalent to separate policies for SELECT, INSERT, UPDATE, DELETE
```

### User Context Functions

```sql
-- Set up user context
CREATE FUNCTION current_user_id() RETURNS INTEGER AS $$
BEGIN
    RETURN current_setting('app.user_id', true)::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;

-- Set user ID in session
SET app.user_id = '123';

-- Or use current_user (PostgreSQL role name)
CREATE POLICY by_username ON documents
FOR SELECT
USING (owner_name = current_user);

-- Or use custom configuration
SET app.department = 'engineering';
CREATE POLICY dept_access ON documents
FOR SELECT
USING (department = current_setting('app.department'));
```

## Policy Types

### SELECT Policies

```sql
-- Users see only their documents
CREATE POLICY select_own ON documents
FOR SELECT
USING (owner_id = current_user_id());

-- Users see own + public documents
CREATE POLICY select_visible ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR is_public = true
);

-- Department-based access
CREATE POLICY select_dept ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR department = current_setting('app.department')
);
```

### INSERT Policies

```sql
-- Users can only insert with their user_id
CREATE POLICY insert_own ON documents
FOR INSERT
WITH CHECK (owner_id = current_user_id());

-- Prevent inserting public documents
CREATE POLICY insert_private ON documents
FOR INSERT
WITH CHECK (is_public = false);

-- Department restriction
CREATE POLICY insert_dept ON documents
FOR INSERT
WITH CHECK (department = current_setting('app.department'));
```

### UPDATE Policies

```sql
-- Users can update only their documents
CREATE POLICY update_own ON documents
FOR UPDATE
USING (owner_id = current_user_id())
WITH CHECK (owner_id = current_user_id());

-- USING: which rows can be selected for update
-- WITH CHECK: what the new values must satisfy

-- Allow updating content but not ownership
CREATE POLICY update_content ON documents
FOR UPDATE
USING (owner_id = current_user_id())
WITH CHECK (
    owner_id = current_user_id()
    AND owner_id = OLD.owner_id  -- Can't change owner
);

-- Managers can update department documents
CREATE POLICY update_manager ON documents
FOR UPDATE
USING (
    department = current_setting('app.department')
    AND is_manager()
);
```

### DELETE Policies

```sql
-- Users can delete only their documents
CREATE POLICY delete_own ON documents
FOR DELETE
USING (owner_id = current_user_id());

-- Prevent deleting public documents
CREATE POLICY delete_non_public ON documents
FOR DELETE
USING (
    owner_id = current_user_id()
    AND is_public = false
);

-- Soft delete based on age
CREATE POLICY delete_recent ON documents
FOR DELETE
USING (
    owner_id = current_user_id()
    AND created_at > now() - interval '7 days'
);
```

## Using Policies

### Multiple Policies

```sql
-- Multiple policies are combined with OR
CREATE POLICY see_own ON documents
FOR SELECT
USING (owner_id = current_user_id());

CREATE POLICY see_public ON documents
FOR SELECT
USING (is_public = true);

-- Effective condition: (owner_id = X) OR (is_public = true)

-- To require ALL policies (AND), use single policy:
CREATE POLICY restricted ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    AND department = current_setting('app.department')
    AND is_active = true
);
```

### Role-Specific Policies

```sql
-- Different policies for different roles
CREATE POLICY user_read ON documents
FOR SELECT
TO app_user
USING (owner_id = current_user_id());

CREATE POLICY admin_read ON documents
FOR SELECT
TO app_admin
USING (true);  -- Admins see everything

CREATE POLICY manager_read ON documents
FOR SELECT
TO app_manager
USING (department = current_setting('app.department'));

-- User inherits policies from all granted roles
```

### Permissive vs Restrictive Policies

```sql
-- Permissive (default): combined with OR
CREATE POLICY permissive_own ON documents
AS PERMISSIVE  -- default
FOR SELECT
USING (owner_id = current_user_id());

CREATE POLICY permissive_public ON documents
AS PERMISSIVE
FOR SELECT
USING (is_public = true);
-- Result: can see own OR public

-- Restrictive: combined with AND
CREATE POLICY restrictive_active ON documents
AS RESTRICTIVE
FOR SELECT
USING (is_active = true);

CREATE POLICY restrictive_dept ON documents
AS RESTRICTIVE
FOR SELECT
USING (department IN ('eng', 'sales'));

-- Final: (own OR public) AND active AND dept_check
-- All restrictive policies must be satisfied
```

## Advanced Policies

### Policies with Subqueries

```sql
-- Access shared documents
CREATE TABLE document_shares (
    document_id INTEGER,
    user_id INTEGER,
    PRIMARY KEY (document_id, user_id)
);

CREATE POLICY see_shared ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR is_public = true
    OR EXISTS (
        SELECT 1 FROM document_shares
        WHERE document_id = documents.id
          AND user_id = current_user_id()
    )
);

-- Performance note: Ensure indexes on subquery tables
CREATE INDEX idx_shares_user_doc ON document_shares(user_id, document_id);
```

### Policies with Functions

```sql
-- Check if user is admin
CREATE FUNCTION is_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_setting('app.role', true) = 'admin';
END;
$$ LANGUAGE plpgsql STABLE;

-- Check if user is in department
CREATE FUNCTION in_department(dept TEXT) RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_setting('app.department', true) = dept;
END;
$$ LANGUAGE plpgsql STABLE;

-- Use in policies
CREATE POLICY admin_access ON documents
FOR ALL
USING (is_admin() OR owner_id = current_user_id());

CREATE POLICY dept_access ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR in_department(department)
);

-- Mark functions as STABLE or IMMUTABLE for performance
```

### Time-Based Policies

```sql
-- Documents visible only during business hours
CREATE POLICY business_hours ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR (
        is_public = true
        AND extract(hour from now()) BETWEEN 9 AND 17
        AND extract(dow from now()) BETWEEN 1 AND 5
    )
);

-- Expire access after certain date
CREATE TABLE document_access (
    document_id INTEGER,
    user_id INTEGER,
    expires_at TIMESTAMP,
    PRIMARY KEY (document_id, user_id)
);

CREATE POLICY time_limited_access ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR EXISTS (
        SELECT 1 FROM document_access
        WHERE document_id = documents.id
          AND user_id = current_user_id()
          AND expires_at > now()
    )
);
```

### Hierarchical Access

```sql
-- Organization hierarchy
CREATE TABLE org_hierarchy (
    employee_id INTEGER PRIMARY KEY,
    manager_id INTEGER REFERENCES org_hierarchy(employee_id),
    department TEXT
);

-- Function to check if user is manager
CREATE FUNCTION is_manager_of(emp_id INTEGER) RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM org_hierarchy
        WHERE employee_id = emp_id
          AND manager_id = current_user_id()
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- Policy: see own and subordinates' documents
CREATE POLICY hierarchical_access ON documents
FOR SELECT
USING (
    owner_id = current_user_id()
    OR is_manager_of(owner_id)
);
```

## Performance Considerations

### Indexing for RLS

```sql
-- Index columns used in policies
CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_documents_dept ON documents(department);
CREATE INDEX idx_documents_public ON documents(is_public) WHERE is_public = true;

-- Composite indexes for multiple conditions
CREATE INDEX idx_documents_owner_dept ON documents(owner_id, department);

-- Partial index for policy conditions
CREATE INDEX idx_documents_active ON documents(owner_id)
WHERE is_active = true;
```

### Query Performance

```sql
-- Check query plan with RLS
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM documents WHERE title LIKE '%test%';
-- Look for policy conditions in Filter

-- Policies add WHERE clauses, impacting performance
-- Optimize policies like any WHERE condition

-- Bad: function call per row
CREATE POLICY slow_policy ON documents
FOR SELECT
USING (expensive_function(owner_id));

-- Good: use indexed columns
CREATE POLICY fast_policy ON documents
FOR SELECT
USING (owner_id = current_user_id());

-- Use STABLE functions (can be optimized)
CREATE FUNCTION current_user_id() RETURNS INTEGER AS $$
BEGIN
    RETURN current_setting('app.user_id')::INTEGER;
END;
$$ LANGUAGE plpgsql STABLE;  -- Not VOLATILE
```

### Caching User Context

```sql
-- Cache user context at connection start
-- Application sets once per session:
SET app.user_id = '123';
SET app.department = 'engineering';
SET app.role = 'user';

-- Policies use these settings (fast)
CREATE POLICY cached_access ON documents
FOR SELECT
USING (
    owner_id = current_setting('app.user_id')::INTEGER
    OR department = current_setting('app.department')
);

-- Avoid per-query user lookups
```

## Multi-Tenancy with RLS

### Tenant Isolation

```sql
-- Multi-tenant application
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    username TEXT NOT NULL,
    UNIQUE (tenant_id, username)
);

CREATE TABLE tenant_data (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    user_id INTEGER REFERENCES users(id),
    data JSONB,
    created_at TIMESTAMP DEFAULT now()
);

-- Enable RLS
ALTER TABLE tenant_data ENABLE ROW LEVEL SECURITY;

-- Policy: users see only their tenant's data
CREATE POLICY tenant_isolation ON tenant_data
FOR ALL
USING (tenant_id = current_setting('app.tenant_id')::INTEGER)
WITH CHECK (tenant_id = current_setting('app.tenant_id')::INTEGER);

-- Application sets tenant_id at connection:
SET app.tenant_id = '42';

-- All queries automatically filtered by tenant
SELECT * FROM tenant_data;  -- Only tenant 42's data
```

### Complete Multi-Tenant Setup

```sql
-- 1. Create schemas per tenant (optional)
CREATE SCHEMA tenant_1;
CREATE SCHEMA tenant_2;

-- 2. Or use shared tables with RLS
CREATE TABLE shared_orders (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER NOT NULL,
    customer_name TEXT,
    total NUMERIC,
    created_at TIMESTAMP DEFAULT now()
);

-- 3. Enable RLS
ALTER TABLE shared_orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE shared_orders FORCE ROW LEVEL SECURITY;  -- Even for owner

-- 4. Create tenant isolation policy
CREATE POLICY tenant_orders ON shared_orders
FOR ALL
USING (tenant_id = current_setting('app.tenant_id')::INTEGER)
WITH CHECK (tenant_id = current_setting('app.tenant_id')::INTEGER);

-- 5. Create indexes
CREATE INDEX idx_orders_tenant ON shared_orders(tenant_id);
CREATE INDEX idx_orders_tenant_date ON shared_orders(tenant_id, created_at);

-- 6. Application code
-- conn.execute("SET app.tenant_id = %s", [tenant_id])
-- All subsequent queries are tenant-isolated
```

### Preventing Tenant Leakage

```sql
-- Ensure tenant_id can't be changed mid-session
CREATE FUNCTION set_tenant_id(tid INTEGER) RETURNS VOID AS $$
BEGIN
    IF current_setting('app.tenant_id', true) IS NOT NULL THEN
        RAISE EXCEPTION 'Tenant ID already set';
    END IF;
    PERFORM set_config('app.tenant_id', tid::TEXT, false);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Application calls once per connection:
SELECT set_tenant_id(42);

-- Subsequent SET commands fail
SET app.tenant_id = '99';  -- Raises exception
```

## Debugging RLS

### Checking Policies

```sql
-- List all policies
SELECT 
    schemaname,
    tablename,
    policyname,
    permissive,
    roles,
    cmd,
    qual,
    with_check
FROM pg_policies
WHERE tablename = 'documents';

-- Check if RLS is enabled
SELECT 
    schemaname,
    tablename,
    rowsecurity,
    forcerowsecurity
FROM pg_tables
WHERE tablename = 'documents';
```

### Testing Policies

```sql
-- Test as specific user
SET ROLE app_user;
SET app.user_id = '123';
SELECT * FROM documents;  -- See what this user sees
RESET ROLE;

-- Bypass RLS for testing (as superuser)
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;
SELECT * FROM documents;  -- See all rows
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Or grant BYPASSRLS to role
ALTER ROLE test_user BYPASSRLS;
```

### Debugging Policy Filters

```sql
-- See actual query with policy
EXPLAIN (VERBOSE, COSTS OFF)
SELECT * FROM documents WHERE title LIKE '%test%';

-- Output shows policy conditions:
-- Filter: ((owner_id = current_user_id()) OR is_public)
--     AND (title ~~ '%test%')

-- Use EXPLAIN ANALYZE to see row counts
EXPLAIN (ANALYZE, VERBOSE)
SELECT * FROM documents;
-- Shows how many rows filtered by policy
```

### Common Issues

```sql
-- Issue 1: No rows returned
-- Check: Is RLS enabled?
SELECT rowsecurity FROM pg_tables WHERE tablename = 'documents';

-- Check: Are there policies?
SELECT count(*) FROM pg_policies WHERE tablename = 'documents';

-- Check: Is user context set?
SELECT current_setting('app.user_id', true);

-- Issue 2: Wrong rows returned
-- Check policy logic
SELECT 
    policyname,
    qual as using_clause,
    with_check
FROM pg_policies
WHERE tablename = 'documents';

-- Issue 3: Performance problems
-- Check indexes on policy columns
SELECT indexname, indexdef
FROM pg_indexes
WHERE tablename = 'documents';
```

## Best Practices

### 1. Always Set User Context

```sql
-- At connection start:
-- conn.execute("SET app.user_id = %s", [user_id])
-- conn.execute("SET app.tenant_id = %s", [tenant_id])

-- Validate context is set before queries
CREATE FUNCTION require_user_context() RETURNS BOOLEAN AS $$
BEGIN
    IF current_setting('app.user_id', true) IS NULL THEN
        RAISE EXCEPTION 'User context not set';
    END IF;
    RETURN true;
END;
$$ LANGUAGE plpgsql STABLE;

-- Use in policies
CREATE POLICY requires_context ON documents
FOR ALL
USING (require_user_context() AND owner_id = current_user_id()::INTEGER);
```

### 2. Use FORCE ROW LEVEL SECURITY

```sql
-- Ensure table owner also subject to RLS
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Without FORCE, table owner bypasses RLS
-- This can lead to data leaks if app connects as owner
```

### 3. Index Policy Columns

```sql
-- Always index columns used in policies
CREATE INDEX idx_documents_owner ON documents(owner_id);
CREATE INDEX idx_documents_tenant ON documents(tenant_id);

-- Composite indexes for multi-column policies
CREATE INDEX idx_documents_tenant_owner ON documents(tenant_id, owner_id);
```

### 4. Test Policies Thoroughly

```sql
-- Test each role
SET ROLE regular_user;
-- Verify only appropriate rows visible

SET ROLE admin_user;
-- Verify admin sees more/all rows

SET ROLE other_user;
-- Verify no access to wrong tenant
```

### 5. Monitor Performance

```sql
-- Log slow queries
SET log_min_duration_statement = 1000;

-- Check query plans regularly
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM documents WHERE ...;

-- Monitor policy overhead
SELECT 
    schemaname,
    tablename,
    seq_scan,
    idx_scan,
    seq_tup_read
FROM pg_stat_user_tables
WHERE tablename = 'documents';
```

### 6. Document Policies

```sql
-- Comment policies
COMMENT ON POLICY tenant_isolation ON tenant_data IS
'Ensures users only access their tenant data. Requires app.tenant_id to be set.';

COMMENT ON POLICY user_documents ON documents IS
'Users can access their own documents and public documents.';

-- Document required context
COMMENT ON TABLE documents IS
'Requires RLS context: app.user_id, app.tenant_id';
```

## Summary

Row-Level Security in PostgreSQL provides:
- **Fine-Grained Control**: Restrict access at the row level
- **Transparent**: No application query changes needed
- **Flexible Policies**: Multiple conditions, subqueries, functions
- **Multi-Tenancy**: Complete tenant isolation with shared tables
- **Performance**: Optimizable with proper indexing
- **Security**: Combine with traditional privileges for defense-in-depth

RLS is essential for multi-tenant applications and fine-grained access control.

## Next Steps

- Learn about [Authentication and Authorization](./30-authentication-authorization.md)
- Explore [Database Security](./33-database-security.md)
- Study [Performance Optimization](./20-query-optimization.md)
- Practice [User Management](./32-user-management-and-security.md)
