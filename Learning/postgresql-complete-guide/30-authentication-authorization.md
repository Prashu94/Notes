# Authentication and Authorization

## Overview

PostgreSQL provides comprehensive security through authentication (verifying identity) and authorization (controlling access). This includes user management, role-based access control, row-level security, and various authentication methods.

## Table of Contents
- [Users and Roles](#users-and-roles)
- [Authentication Methods](#authentication-methods)
- [Password Management](#password-management)
- [Privileges and Permissions](#privileges-and-permissions)
- [Database Access Control](#database-access-control)
- [Row-Level Security](#row-level-security)
- [Column-Level Security](#column-level-security)
- [Schema Permissions](#schema-permissions)
- [Best Practices](#best-practices)

## Users and Roles

### Creating Roles

```sql
-- Create role (cannot login by default)
CREATE ROLE readonly;

-- Create user (can login)
CREATE USER app_user WITH PASSWORD 'secure_password';

-- Create role with login
CREATE ROLE admin WITH LOGIN PASSWORD 'admin_pass';

-- Role with attributes
CREATE ROLE developer WITH
    LOGIN
    PASSWORD 'dev_pass'
    VALID UNTIL '2025-12-31'
    CONNECTION LIMIT 10
    CREATEDB
    CREATEROLE;

-- Create superuser (full privileges)
CREATE ROLE superadmin WITH SUPERUSER LOGIN PASSWORD 'super_pass';

-- List all roles
SELECT rolname, rolsuper, rolcreaterole, rolcreatedb, rolcanlogin
FROM pg_roles
ORDER BY rolname;

-- Alternative:
\du  -- psql command
```

### Role Attributes

```sql
-- SUPERUSER: Full access (bypass all checks)
ALTER ROLE username SUPERUSER;

-- CREATEDB: Can create databases
ALTER ROLE username CREATEDB;

-- CREATEROLE: Can create/alter/drop roles
ALTER ROLE username CREATEROLE;

-- REPLICATION: Can initiate streaming replication
ALTER ROLE username REPLICATION;

-- BYPASSRLS: Can bypass row-level security
ALTER ROLE username BYPASSRLS;

-- CONNECTION LIMIT: Max concurrent connections
ALTER ROLE username CONNECTION LIMIT 5;

-- VALID UNTIL: Account expiration
ALTER ROLE username VALID UNTIL '2025-12-31';

-- Remove attribute
ALTER ROLE username NOCREATEDB;
ALTER ROLE username NOSUPERUSER;
```

### Role Membership (Groups)

```sql
-- Create group roles
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_admin;

-- Grant role membership
GRANT app_readonly TO user1;
GRANT app_readwrite TO user2;
GRANT app_admin TO user3;

-- User inherits group permissions
GRANT app_readonly TO user1;  -- user1 gets readonly permissions

-- Multiple role membership
GRANT app_readonly, app_readwrite TO user4;

-- Hierarchical roles
GRANT app_readonly TO app_readwrite;
GRANT app_readwrite TO app_admin;
-- app_admin inherits from app_readwrite and app_readonly

-- Revoke role membership
REVOKE app_readonly FROM user1;

-- View role memberships
SELECT 
    r.rolname as role,
    m.rolname as member
FROM pg_roles r
JOIN pg_auth_members am ON r.oid = am.roleid
JOIN pg_roles m ON m.oid = am.member
ORDER BY r.rolname, m.rolname;
```

### Role Management

```sql
-- Rename role
ALTER ROLE old_name RENAME TO new_name;

-- Change password
ALTER ROLE username PASSWORD 'new_password';

-- Drop role
DROP ROLE IF EXISTS username;

-- Drop role with dependencies
DROP OWNED BY username;  -- Drop owned objects first
DROP ROLE username;

-- Transfer ownership before dropping
REASSIGN OWNED BY old_user TO new_user;
DROP ROLE old_user;

-- Current role
SELECT current_role;
SELECT current_user;
SELECT session_user;

-- Switch role (if member)
SET ROLE app_readonly;
SELECT current_role;  -- app_readonly

-- Switch back
RESET ROLE;
SELECT current_role;  -- original user
```

## Authentication Methods

### pg_hba.conf Configuration

```sql
-- pg_hba.conf format:
-- TYPE  DATABASE  USER  ADDRESS  METHOD

-- Examples:

-- Trust (no password - local only)
-- local   all       all              trust

-- MD5 password authentication
-- host    all       all   0.0.0.0/0  md5

-- SCRAM-SHA-256 (recommended)
-- host    all       all   0.0.0.0/0  scram-sha-256

-- Peer authentication (Unix socket, username match)
-- local   all       all              peer

-- Specific database and user
-- host    mydb      myuser  192.168.1.0/24  scram-sha-256

-- Reject connections
-- host    all       all     10.0.0.0/8      reject

-- After modifying pg_hba.conf:
SELECT pg_reload_conf();  -- Reload configuration
```

### Authentication Methods

```sql
-- 1. TRUST: No authentication (dangerous)
--    Use only for local development

-- 2. PASSWORD: Plain text password (not recommended)
--    Sends password in clear text

-- 3. MD5: MD5 hashed password
--    Better than plain text, but outdated

-- 4. SCRAM-SHA-256: Modern password hashing (recommended)
--    Most secure password method
--    Set in postgresql.conf:
--    password_encryption = scram-sha-256

-- 5. PEER: OS username must match PostgreSQL username
--    Unix socket connections only

-- 6. IDENT: Use ident server to verify username
--    Similar to peer, but works over TCP

-- 7. CERT: SSL certificate authentication
--    Requires SSL client certificates

-- 8. LDAP: External LDAP server authentication
--    Integrates with Active Directory

-- 9. PAM: Pluggable Authentication Modules
--    OS-level authentication

-- 10. RADIUS: RADIUS server authentication
--     Enterprise authentication
```

### SSL/TLS Configuration

```sql
-- Enable SSL in postgresql.conf:
-- ssl = on
-- ssl_cert_file = 'server.crt'
-- ssl_key_file = 'server.key'
-- ssl_ca_file = 'root.crt'

-- Require SSL in pg_hba.conf:
-- hostssl  all  all  0.0.0.0/0  scram-sha-256

-- SSL modes:
-- disable: No SSL
-- allow: Try non-SSL, then SSL
-- prefer: Try SSL, then non-SSL (default)
-- require: SSL required
-- verify-ca: SSL with CA verification
-- verify-full: SSL with full verification

-- Connect with SSL:
-- psql "postgresql://user@host/db?sslmode=require"

-- Check SSL status
SELECT * FROM pg_stat_ssl;

-- Force SSL for specific user
ALTER ROLE username SET ssl = true;
```

## Password Management

### Password Policies

```sql
-- Set password
ALTER ROLE username PASSWORD 'secure_password';

-- Password expiration
ALTER ROLE username VALID UNTIL '2025-12-31';

-- Force password change on next login
ALTER ROLE username PASSWORD 'temp_pass' VALID UNTIL 'now';

-- Check password encryption
SHOW password_encryption;  -- Should be scram-sha-256

-- Set password encryption method
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

-- Password strength extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Hash password with bcrypt
SELECT crypt('my_password', gen_salt('bf', 10));

-- Verify password
SELECT crypt('my_password', stored_hash) = stored_hash;
```

### Password Complexity

```sql
-- Enforce password complexity with check constraint
CREATE TABLE user_accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    CONSTRAINT password_complexity CHECK (
        length(password_hash) >= 60  -- bcrypt hash length
    )
);

-- Password validation function
CREATE OR REPLACE FUNCTION validate_password(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Minimum 8 characters
    IF length(password) < 8 THEN
        RAISE EXCEPTION 'Password must be at least 8 characters';
    END IF;
    
    -- Require uppercase
    IF password !~ '[A-Z]' THEN
        RAISE EXCEPTION 'Password must contain uppercase letter';
    END IF;
    
    -- Require lowercase
    IF password !~ '[a-z]' THEN
        RAISE EXCEPTION 'Password must contain lowercase letter';
    END IF;
    
    -- Require digit
    IF password !~ '[0-9]' THEN
        RAISE EXCEPTION 'Password must contain digit';
    END IF;
    
    -- Require special character
    IF password !~ '[^A-Za-z0-9]' THEN
        RAISE EXCEPTION 'Password must contain special character';
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- Use in application
SELECT validate_password('MyPass123!');
```

### .pgpass File

```sql
-- Store passwords securely in ~/.pgpass
-- Format: hostname:port:database:username:password
-- Example:
-- localhost:5432:mydb:myuser:mypassword
-- *.example.com:5432:*:myuser:mypassword

-- File permissions: chmod 0600 ~/.pgpass

-- Connect without password prompt:
-- psql -h localhost -U myuser -d mydb
```

## Privileges and Permissions

### Database Privileges

```sql
-- Grant database access
GRANT CONNECT ON DATABASE mydb TO app_user;

-- Grant create schema privilege
GRANT CREATE ON DATABASE mydb TO developer;

-- Grant temporary table privilege
GRANT TEMP ON DATABASE mydb TO app_user;

-- Grant all database privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO admin;

-- Revoke privileges
REVOKE CONNECT ON DATABASE mydb FROM app_user;

-- View database privileges
SELECT 
    datname,
    datacl
FROM pg_database
WHERE datname = 'mydb';
```

### Table Privileges

```sql
-- Grant SELECT
GRANT SELECT ON users TO readonly_user;

-- Grant INSERT
GRANT INSERT ON users TO app_user;

-- Grant UPDATE
GRANT UPDATE ON users TO app_user;

-- Grant DELETE
GRANT DELETE ON users TO app_user;

-- Grant multiple privileges
GRANT SELECT, INSERT, UPDATE ON users TO app_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON users TO admin;

-- Grant on all tables in schema
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly_user;

-- Grant for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO readonly_user;

-- Column-specific privileges
GRANT SELECT (id, username) ON users TO limited_user;
GRANT UPDATE (email, updated_at) ON users TO app_user;

-- Revoke privileges
REVOKE INSERT ON users FROM app_user;
REVOKE ALL ON users FROM app_user;

-- View table privileges
SELECT 
    grantee,
    privilege_type
FROM information_schema.table_privileges
WHERE table_name = 'users';
```

### Schema Privileges

```sql
-- Grant usage on schema
GRANT USAGE ON SCHEMA public TO app_user;

-- Grant create on schema
GRANT CREATE ON SCHEMA public TO developer;

-- Grant all schema privileges
GRANT ALL ON SCHEMA public TO admin;

-- Grant on all schemas
GRANT USAGE ON ALL SCHEMAS TO app_user;

-- Revoke schema access
REVOKE ALL ON SCHEMA private FROM app_user;
```

### Sequence Privileges

```sql
-- Grant sequence usage
GRANT USAGE ON SEQUENCE users_id_seq TO app_user;

-- Grant all sequence operations
GRANT ALL ON SEQUENCE users_id_seq TO admin;

-- Grant for all sequences
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- Default privileges for future sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE ON SEQUENCES TO app_user;
```

### Function Privileges

```sql
-- Grant execute on function
GRANT EXECUTE ON FUNCTION calculate_total(INTEGER) TO app_user;

-- Grant on all functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;

-- Default privileges for future functions
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT EXECUTE ON FUNCTIONS TO app_user;

-- Revoke execute
REVOKE EXECUTE ON FUNCTION sensitive_function() FROM app_user;
```

## Database Access Control

### Complete Access Setup

```sql
-- 1. Create database
CREATE DATABASE app_db;

-- 2. Create roles
CREATE ROLE app_readonly;
CREATE ROLE app_readwrite;
CREATE ROLE app_admin;

-- 3. Grant database access
GRANT CONNECT ON DATABASE app_db TO app_readonly, app_readwrite, app_admin;

-- 4. Grant schema usage
\c app_db
GRANT USAGE ON SCHEMA public TO app_readonly, app_readwrite, app_admin;

-- 5. Grant table privileges
GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_readonly;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_readwrite;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_admin;

-- 6. Grant sequence privileges
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_readwrite;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO app_admin;

-- 7. Default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT ON TABLES TO app_readonly;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_readwrite;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT USAGE ON SEQUENCES TO app_readwrite;

-- 8. Create users and assign roles
CREATE USER readonly_user WITH PASSWORD 'pass1';
CREATE USER readwrite_user WITH PASSWORD 'pass2';
CREATE USER admin_user WITH PASSWORD 'pass3';

GRANT app_readonly TO readonly_user;
GRANT app_readwrite TO readwrite_user;
GRANT app_admin TO admin_user;
```

### Revoking All Access

```sql
-- Revoke all from user
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM app_user;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM app_user;
REVOKE ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public FROM app_user;
REVOKE ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public FROM app_user;

-- Revoke from public (all users)
REVOKE ALL ON DATABASE mydb FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
```

## Row-Level Security

### Enabling RLS

```sql
-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    title TEXT,
    content TEXT,
    owner_id INTEGER,
    department TEXT,
    created_at TIMESTAMP DEFAULT now()
);

-- Enable row-level security
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Create policy: users see only their documents
CREATE POLICY user_documents ON documents
FOR SELECT
USING (owner_id = current_setting('app.user_id')::INTEGER);

-- Create policy: users modify only their documents
CREATE POLICY user_modify ON documents
FOR ALL
USING (owner_id = current_setting('app.user_id')::INTEGER);

-- Set user context
SET app.user_id = '123';

-- Query returns only user's documents
SELECT * FROM documents;  -- Filtered by policy

-- Separate policies for different operations
CREATE POLICY doc_select ON documents FOR SELECT
USING (owner_id = current_setting('app.user_id')::INTEGER);

CREATE POLICY doc_insert ON documents FOR INSERT
WITH CHECK (owner_id = current_setting('app.user_id')::INTEGER);

CREATE POLICY doc_update ON documents FOR UPDATE
USING (owner_id = current_setting('app.user_id')::INTEGER)
WITH CHECK (owner_id = current_setting('app.user_id')::INTEGER);

CREATE POLICY doc_delete ON documents FOR DELETE
USING (owner_id = current_setting('app.user_id')::INTEGER);
```

### Advanced RLS Policies

```sql
-- Policy with OR conditions
CREATE POLICY dept_access ON documents
FOR SELECT
USING (
    owner_id = current_setting('app.user_id')::INTEGER
    OR department = current_setting('app.department')::TEXT
);

-- Policy using function
CREATE FUNCTION is_admin() RETURNS BOOLEAN AS $$
BEGIN
    RETURN current_setting('app.role')::TEXT = 'admin';
END;
$$ LANGUAGE plpgsql STABLE;

CREATE POLICY admin_access ON documents
FOR ALL
USING (is_admin() OR owner_id = current_setting('app.user_id')::INTEGER);

-- Policy with joins
CREATE POLICY shared_docs ON documents
FOR SELECT
USING (
    owner_id = current_setting('app.user_id')::INTEGER
    OR EXISTS (
        SELECT 1 FROM document_shares
        WHERE document_id = documents.id
          AND user_id = current_setting('app.user_id')::INTEGER
    )
);

-- Role-based policy
CREATE POLICY role_based ON documents
FOR SELECT
USING (
    CASE current_setting('app.role')
        WHEN 'admin' THEN TRUE
        WHEN 'manager' THEN department = current_setting('app.department')
        ELSE owner_id = current_setting('app.user_id')::INTEGER
    END
);
```

### Managing RLS Policies

```sql
-- List policies
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

-- Drop policy
DROP POLICY user_documents ON documents;

-- Disable RLS
ALTER TABLE documents DISABLE ROW LEVEL SECURITY;

-- Force RLS for table owner too
ALTER TABLE documents FORCE ROW LEVEL SECURITY;

-- Bypass RLS (requires BYPASSRLS attribute)
ALTER ROLE admin BYPASSRLS;
```

## Column-Level Security

### Column Privileges

```sql
-- Grant SELECT on specific columns
GRANT SELECT (id, username, email) ON users TO app_user;

-- Grant UPDATE on specific columns
GRANT UPDATE (email, phone, updated_at) ON users TO app_user;

-- Revoke column access
REVOKE SELECT (email) ON users FROM public_user;

-- View column privileges
SELECT 
    grantee,
    table_name,
    column_name,
    privilege_type
FROM information_schema.column_privileges
WHERE table_name = 'users';
```

### Hiding Sensitive Columns

```sql
-- Create view without sensitive columns
CREATE VIEW public_users AS
SELECT id, username, created_at
FROM users;

GRANT SELECT ON public_users TO public_user;
REVOKE SELECT ON users FROM public_user;

-- Masked view for sensitive data
CREATE VIEW masked_users AS
SELECT 
    id,
    username,
    substring(email from 1 for 3) || '***@' || substring(email from position('@' in email)) as email_masked,
    '***-***-' || right(phone, 4) as phone_masked
FROM users;

GRANT SELECT ON masked_users TO limited_user;
```

## Schema Permissions

### Schema-Based Security

```sql
-- Create schemas for different access levels
CREATE SCHEMA app_public;
CREATE SCHEMA app_private;
CREATE SCHEMA app_admin;

-- Grant appropriate access
GRANT USAGE ON SCHEMA app_public TO PUBLIC;
GRANT USAGE ON SCHEMA app_private TO app_user;
GRANT ALL ON SCHEMA app_admin TO admin;

-- Create tables in schemas
CREATE TABLE app_public.products (...);
CREATE TABLE app_private.orders (...);
CREATE TABLE app_admin.audit_logs (...);

-- Grant privileges
GRANT SELECT ON ALL TABLES IN SCHEMA app_public TO PUBLIC;
GRANT ALL ON ALL TABLES IN SCHEMA app_private TO app_user;
```

### Search Path Security

```sql
-- Set search path
ALTER ROLE app_user SET search_path = app_public, app_private, public;

-- Secure search path (prevent function hijacking)
ALTER DATABASE mydb SET search_path = "$user", public;

-- Check current search path
SHOW search_path;

-- Temporary search path
SET search_path = app_public, app_private;
```

## Best Practices

### 1. Principle of Least Privilege

```sql
-- Grant only necessary permissions
CREATE ROLE app_reader;
GRANT CONNECT ON DATABASE mydb TO app_reader;
GRANT USAGE ON SCHEMA public TO app_reader;
GRANT SELECT ON specific_tables TO app_reader;
-- Don't grant ALL or superuser unless absolutely necessary

-- Use role hierarchy
CREATE ROLE base_user;
GRANT CONNECT ON DATABASE mydb TO base_user;

CREATE ROLE reader;
GRANT base_user TO reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO reader;

CREATE ROLE writer;
GRANT reader TO writer;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO writer;
```

### 2. Separate Application and Admin Access

```sql
-- Application role (limited)
CREATE ROLE app_role WITH LOGIN PASSWORD 'app_pass';
GRANT CONNECT ON DATABASE app_db TO app_role;
GRANT USAGE ON SCHEMA public TO app_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;

-- Admin role (full access)
CREATE ROLE admin_role WITH LOGIN PASSWORD 'admin_pass' CREATEDB CREATEROLE;
GRANT ALL PRIVILEGES ON DATABASE app_db TO admin_role;

-- Never use superuser for applications
```

### 3. Regular Auditing

```sql
-- Audit roles and permissions
SELECT 
    r.rolname,
    r.rolsuper,
    r.rolcreaterole,
    r.rolcreatedb,
    r.rolcanlogin,
    r.rolconnlimit,
    r.rolvaliduntil
FROM pg_roles r
ORDER BY r.rolname;

-- Audit table privileges
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY grantee, table_name;

-- Find users with excessive privileges
SELECT rolname
FROM pg_roles
WHERE rolsuper = true
   OR rolcreaterole = true
ORDER BY rolname;
```

### 4. Secure Password Management

```sql
-- Use SCRAM-SHA-256
ALTER SYSTEM SET password_encryption = 'scram-sha-256';

-- Enforce password expiration
ALTER ROLE app_user VALID UNTIL '2025-12-31';

-- Use external authentication when possible
-- Configure LDAP, Kerberos, or OAuth

-- Never store passwords in application code
-- Use environment variables or secret management
```

### 5. Network Security

```sql
-- Restrict connections in pg_hba.conf
-- Only allow specific IPs
-- host  all  all  192.168.1.0/24  scram-sha-256

-- Require SSL
-- hostssl  all  all  0.0.0.0/0  scram-sha-256

-- Reject unauthorized networks
-- host  all  all  10.0.0.0/8  reject

-- Monitor connections
SELECT 
    datname,
    usename,
    application_name,
    client_addr,
    state,
    query_start
FROM pg_stat_activity
WHERE datname IS NOT NULL
ORDER BY query_start DESC;
```

## Summary

PostgreSQL authentication and authorization includes:
- **Users and Roles**: Role-based access control with inheritance
- **Authentication**: Multiple methods (SCRAM-SHA-256, SSL, LDAP, etc.)
- **Privileges**: Granular control at database, schema, table, column, row levels
- **Row-Level Security**: Filter rows based on user context
- **Password Management**: Secure hashing, expiration, complexity requirements
- **Best Practices**: Least privilege, separation of duties, regular auditing

Proper security configuration is essential for protecting database assets.

## Next Steps

- Learn about [Backup and Recovery](./35-backup-and-recovery.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Study [Database Security](./33-database-security.md)
- Practice [Connection Pooling](./37-connection-pooling.md)
