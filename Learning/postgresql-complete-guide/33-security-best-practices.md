# Security Best Practices

## Overview

Database security is critical for protecting sensitive data, ensuring compliance, and maintaining system integrity. This comprehensive guide covers PostgreSQL security best practices including hardening, access control, auditing, compliance, and incident response.

## Table of Contents
- [Security Principles](#security-principles)
- [Network Security](#network-security)
- [Authentication Security](#authentication-security)
- [Authorization and Access Control](#authorization-and-access-control)
- [Data Protection](#data-protection)
- [Auditing and Monitoring](#auditing-and-monitoring)
- [Compliance](#compliance)
- [Incident Response](#incident-response)
- [Security Checklist](#security-checklist)

## Security Principles

### Defense in Depth

```sql
-- Multiple layers of security:

-- Layer 1: Network (firewall, VPC)
-- Allow only necessary ports and IP ranges

-- Layer 2: Authentication (strong passwords, MFA)
-- Require SCRAM-SHA-256, certificate authentication

-- Layer 3: Authorization (least privilege)
-- Grant minimal required permissions

-- Layer 4: Data encryption (SSL, column encryption)
-- Encrypt data in transit and at rest

-- Layer 5: Auditing (logging, monitoring)
-- Track all access and modifications

-- Layer 6: Backup (encrypted, tested)
-- Regular backups stored securely offsite

-- Example: Multi-layer protection for sensitive table
CREATE TABLE sensitive_data (
    id SERIAL PRIMARY KEY,
    data_encrypted BYTEA  -- Encrypted at column level
);

-- Enable RLS (row-level security)
ALTER TABLE sensitive_data ENABLE ROW LEVEL SECURITY;

-- Create policy (authorization layer)
CREATE POLICY sensitive_access ON sensitive_data
FOR ALL TO app_user
USING (user_id = current_user_id());

-- Require SSL (network layer)
-- pg_hba.conf: hostssl all all 0.0.0.0/0 scram-sha-256

-- Enable audit logging (monitoring layer)
-- postgresql.conf: log_statement = 'all'
```

### Principle of Least Privilege

```sql
-- Grant only necessary permissions

-- Bad: Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE mydb TO app_user;  -- Too broad!

-- Good: Grant specific needed privileges
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE ON orders TO app_user;
GRANT SELECT ON products TO app_user;  -- Read-only
GRANT USAGE ON SEQUENCE orders_id_seq TO app_user;

-- Even better: Use role hierarchy
CREATE ROLE readonly;
GRANT CONNECT ON DATABASE mydb TO readonly;
GRANT USAGE ON SCHEMA public TO readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;

CREATE ROLE readwrite;
GRANT readonly TO readwrite;  -- Inherit readonly permissions
GRANT INSERT, UPDATE, DELETE ON orders, order_items TO readwrite;

-- Application user inherits from readwrite
CREATE USER app_user WITH PASSWORD 'secure_password';
GRANT readwrite TO app_user;

-- Regularly review granted privileges
SELECT 
    grantee,
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'app_user'
ORDER BY table_name, privilege_type;
```

### Separation of Duties

```sql
-- Different roles for different responsibilities

-- Database Administrator: Schema management
CREATE ROLE dba_role WITH SUPERUSER LOGIN;

-- Application Owner: Object ownership
CREATE ROLE app_owner WITH CREATEDB LOGIN;
GRANT CREATE ON DATABASE mydb TO app_owner;

-- Application User: Runtime operations
CREATE ROLE app_runtime WITH LOGIN;
GRANT CONNECT ON DATABASE mydb TO app_runtime;
GRANT USAGE ON SCHEMA public TO app_runtime;

-- Read-Only Analyst: Reporting
CREATE ROLE analyst WITH LOGIN;
GRANT CONNECT ON DATABASE mydb TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;

-- Audit User: Monitor logs only
CREATE ROLE auditor WITH LOGIN;
GRANT pg_read_all_stats TO auditor;
-- Grant access to audit tables only

-- Example workflow:
-- 1. DBA creates database and schemas
SET ROLE dba_role;
CREATE DATABASE mydb;
\c mydb
CREATE SCHEMA app_schema;

-- 2. App owner creates tables
SET ROLE app_owner;
CREATE TABLE app_schema.orders (...);

-- 3. App owner grants runtime privileges
GRANT SELECT, INSERT, UPDATE, DELETE ON app_schema.orders TO app_runtime;

-- 4. Analyst can only read
SET ROLE analyst;
SELECT * FROM app_schema.orders;  -- OK
INSERT INTO app_schema.orders VALUES (...);  -- ERROR: permission denied
```

## Network Security

### PostgreSQL Network Configuration

```sql
-- postgresql.conf network settings

-- 1. Bind to specific interface (not all)
-- listen_addresses = 'localhost'  -- Local only
-- listen_addresses = '10.0.1.5'  -- Specific IP
-- listen_addresses = 'localhost,10.0.1.5'  -- Multiple
-- listen_addresses = '*'  -- All (use with firewall!)

-- 2. Specific port (change from default 5432)
-- port = 15432

-- 3. Maximum connections (limit resource exhaustion)
-- max_connections = 100
-- superuser_reserved_connections = 3

-- 4. Connection timeouts
-- authentication_timeout = 60s
-- tcp_keepalives_idle = 60
-- tcp_keepalives_interval = 10
-- tcp_keepalives_count = 3

-- Check current listen addresses
SHOW listen_addresses;

-- View active connections by source
SELECT 
    client_addr,
    count(*) as connection_count,
    array_agg(DISTINCT usename) as users,
    array_agg(DISTINCT application_name) as applications
FROM pg_stat_activity
WHERE client_addr IS NOT NULL
GROUP BY client_addr
ORDER BY connection_count DESC;
```

### pg_hba.conf Hardening

```sql
-- pg_hba.conf (Host-Based Authentication) best practices:

-- 1. Order matters (first match wins)
-- 2. Be specific (narrow IP ranges)
-- 3. Require SSL for remote connections
-- 4. Use strong authentication methods

-- Good pg_hba.conf configuration:

-- Local connections (Unix socket)
local   all             postgres                                peer
local   all             all                                     scram-sha-256

-- Localhost TCP connections
host    all             all             127.0.0.1/32            scram-sha-256
host    all             all             ::1/128                 scram-sha-256

-- Remote connections (require SSL)
hostssl mydb            app_user        10.0.1.0/24            scram-sha-256
hostssl mydb            readonly        10.0.2.0/24            scram-sha-256

-- Admin from specific IP only
hostssl all             admin           203.0.113.50/32        cert clientcert=verify-full

-- Reject all non-SSL remote
hostnossl all           all             0.0.0.0/0              reject
hostnossl all           all             ::/0                   reject

-- After changes, reload configuration
SELECT pg_reload_conf();

-- Audit pg_hba.conf rules
SELECT * FROM pg_hba_file_rules;
```

### Firewall Configuration

```sql
-- Configure OS firewall (outside PostgreSQL)

-- Linux iptables example:
-- $ iptables -A INPUT -p tcp --dport 5432 -s 10.0.1.0/24 -j ACCEPT
-- $ iptables -A INPUT -p tcp --dport 5432 -j DROP

-- Linux firewalld example:
-- $ firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="10.0.1.0/24" port port="5432" protocol="tcp" accept'
-- $ firewall-cmd --reload

-- AWS Security Group example:
-- Type: PostgreSQL (5432)
-- Protocol: TCP
-- Port: 5432
-- Source: 10.0.1.0/24 (VPC CIDR)

-- Monitor rejected connections
-- Check system logs:
-- $ grep "refused" /var/log/postgresql/postgresql-*.log
```

## Authentication Security

### Strong Password Policies

```sql
-- Require strong passwords

-- 1. Set password encryption method
ALTER SYSTEM SET password_encryption = 'scram-sha-256';
SELECT pg_reload_conf();

-- 2. Create password complexity function
CREATE OR REPLACE FUNCTION validate_password(password TEXT)
RETURNS BOOLEAN AS $$
BEGIN
    -- Minimum 12 characters
    IF length(password) < 12 THEN
        RAISE EXCEPTION 'Password must be at least 12 characters';
    END IF;
    
    -- Must contain uppercase
    IF password !~ '[A-Z]' THEN
        RAISE EXCEPTION 'Password must contain uppercase letter';
    END IF;
    
    -- Must contain lowercase
    IF password !~ '[a-z]' THEN
        RAISE EXCEPTION 'Password must contain lowercase letter';
    END IF;
    
    -- Must contain digit
    IF password !~ '[0-9]' THEN
        RAISE EXCEPTION 'Password must contain digit';
    END IF;
    
    -- Must contain special character
    IF password !~ '[!@#$%^&*()_+\-=\[\]{};:,.<>?]' THEN
        RAISE EXCEPTION 'Password must contain special character';
    END IF;
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- 3. Create user with strong password
DO $$
DECLARE
    pwd TEXT := 'Str0ng!P@ssw0rd#2024';
BEGIN
    IF validate_password(pwd) THEN
        EXECUTE format('CREATE USER new_user WITH PASSWORD %L', pwd);
    END IF;
END $$;

-- 4. Set password expiration
ALTER ROLE new_user VALID UNTIL '2024-12-31';

-- 5. Check expiring passwords
SELECT 
    rolname,
    rolvaliduntil,
    CASE 
        WHEN rolvaliduntil IS NULL THEN 'Never expires'
        WHEN rolvaliduntil < now() THEN 'EXPIRED'
        WHEN rolvaliduntil < now() + interval '30 days' THEN 'Expiring soon'
        ELSE 'Valid'
    END as status
FROM pg_roles
WHERE rolcanlogin
ORDER BY rolvaliduntil NULLS LAST;
```

### Multi-Factor Authentication

```sql
-- PostgreSQL doesn't have built-in MFA
-- Implement using:

-- 1. PAM (Pluggable Authentication Modules)
-- Configure pg_hba.conf:
-- host  all  all  0.0.0.0/0  pam pamservice=postgresql

-- 2. LDAP with MFA provider
-- host  all  all  0.0.0.0/0  ldap ldapserver=ldap.example.com ldapbasedn="dc=example,dc=com"

-- 3. Client certificates (additional factor)
-- hostssl  all  all  0.0.0.0/0  cert clientcert=verify-full

-- 4. Application-level MFA
-- Application requests token before database connection

-- 5. Connection pooler with MFA (e.g., PgBouncer + auth service)

-- Monitor authentication attempts
SELECT 
    datname,
    usename,
    client_addr,
    backend_start,
    state
FROM pg_stat_activity
WHERE backend_start > now() - interval '1 hour'
ORDER BY backend_start DESC;
```

### Failed Login Monitoring

```sql
-- Enable connection logging
-- postgresql.conf:
-- log_connections = on
-- log_disconnections = on
-- log_line_prefix = '%m [%p] %u@%d %h '

-- Create function to parse auth failures from logs
CREATE TABLE auth_failures (
    timestamp TIMESTAMP,
    username TEXT,
    database TEXT,
    client_addr INET,
    message TEXT
);

-- Parse PostgreSQL logs (external script or tool)
-- INSERT INTO auth_failures VALUES (...);

-- Query recent failures
SELECT 
    client_addr,
    username,
    count(*) as failure_count,
    max(timestamp) as last_attempt
FROM auth_failures
WHERE timestamp > now() - interval '1 hour'
GROUP BY client_addr, username
HAVING count(*) > 3  -- More than 3 failures
ORDER BY failure_count DESC;

-- Alert on brute force attempts
CREATE OR REPLACE FUNCTION alert_brute_force()
RETURNS void AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN 
        SELECT client_addr, username, count(*) as cnt
        FROM auth_failures
        WHERE timestamp > now() - interval '5 minutes'
        GROUP BY client_addr, username
        HAVING count(*) > 5
    LOOP
        RAISE WARNING 'Possible brute force: % attempts from % for user %',
            r.cnt, r.client_addr, r.username;
        -- Send alert (integrate with monitoring system)
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

## Authorization and Access Control

### Regular Permission Audits

```sql
-- Audit all user privileges

-- 1. Database privileges
SELECT 
    datname,
    array_agg(DISTINCT rolname) as users_with_access
FROM pg_database d
CROSS JOIN pg_roles r
WHERE has_database_privilege(r.rolname, d.datname, 'CONNECT')
  AND d.datname NOT IN ('template0', 'template1')
  AND r.rolcanlogin
GROUP BY datname;

-- 2. Schema privileges
SELECT 
    schema_name,
    grantee,
    string_agg(privilege_type, ', ') as privileges
FROM information_schema.schema_privileges
WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
GROUP BY schema_name, grantee
ORDER BY schema_name, grantee;

-- 3. Table privileges
SELECT 
    table_schema,
    table_name,
    grantee,
    string_agg(privilege_type, ', ') as privileges
FROM information_schema.table_privileges
WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
GROUP BY table_schema, table_name, grantee
ORDER BY table_name, grantee;

-- 4. Superusers (should be minimal)
SELECT rolname, rolsuper, rolcreatedb, rolcreaterole
FROM pg_roles
WHERE rolsuper = true;

-- 5. Users with dangerous privileges
SELECT 
    rolname,
    rolsuper,
    rolcreaterole,
    rolcreatedb,
    rolreplication,
    rolbypassrls
FROM pg_roles
WHERE (rolsuper OR rolcreaterole OR rolreplication OR rolbypassrls)
  AND rolname != 'postgres'
ORDER BY rolsuper DESC, rolcreaterole DESC;
```

### Revoking Unnecessary Privileges

```sql
-- Remove privileges that shouldn't exist

-- 1. Revoke public access (common security issue)
REVOKE ALL ON SCHEMA public FROM public;
REVOKE CREATE ON SCHEMA public FROM public;

-- 2. Revoke function execution from public
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM public;

-- 3. Remove old user access
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM old_user;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM old_user;
DROP USER old_user;

-- 4. Downgrade user privileges
-- User had UPDATE but should only have SELECT
REVOKE UPDATE ON orders FROM app_user;

-- 5. Review and clean up default privileges
SELECT 
    defaclrole::regrole,
    defaclnamespace::regnamespace,
    defaclobjtype,
    defaclacl
FROM pg_default_acl;

-- Remove unnecessary defaults
ALTER DEFAULT PRIVILEGES FOR ROLE app_owner REVOKE ALL ON TABLES FROM public;
```

## Data Protection

### Encryption Best Practices

```sql
-- 1. Always use SSL/TLS
-- pg_hba.conf: hostssl all all 0.0.0.0/0 scram-sha-256

-- 2. Encrypt sensitive columns
CREATE EXTENSION pgcrypto;

CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    ssn_encrypted BYTEA,
    credit_card_encrypted BYTEA
);

INSERT INTO customers (name, ssn_encrypted, credit_card_encrypted)
VALUES (
    'John Doe',
    pgp_sym_encrypt('123-45-6789', current_setting('app.encryption_key')),
    pgp_sym_encrypt('1234-5678-9012-3456', current_setting('app.encryption_key'))
);

-- 3. Encrypt backups
-- $ pg_dump mydb | gpg --encrypt --recipient admin@example.com > backup.sql.gpg

-- 4. Use filesystem encryption for data directory
-- LUKS (Linux), BitLocker (Windows), FileVault (macOS)

-- 5. Secure key management
-- Never hardcode keys
-- Use key management service (AWS KMS, HashiCorp Vault)
-- Rotate keys regularly
```

### Data Masking

```sql
-- Mask sensitive data in non-production environments

-- Function to mask credit card
CREATE OR REPLACE FUNCTION mask_credit_card(cc TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN '****-****-****-' || right(cc, 4);
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to mask email
CREATE OR REPLACE FUNCTION mask_email(email TEXT)
RETURNS TEXT AS $$
DECLARE
    parts TEXT[];
BEGIN
    parts := string_to_array(email, '@');
    RETURN left(parts[1], 1) || '***@' || parts[2];
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Masked view for non-production
CREATE VIEW customers_masked AS
SELECT 
    id,
    name,
    mask_email(email) as email,
    mask_credit_card(credit_card) as credit_card,
    created_at
FROM customers;

-- Grant access to masked view
GRANT SELECT ON customers_masked TO reporting_user;
REVOKE ALL ON customers FROM reporting_user;
```

### Preventing SQL Injection

```sql
-- 1. Always use parameterized queries

-- Bad (vulnerable to SQL injection)
CREATE FUNCTION get_user_bad(p_username TEXT)
RETURNS TABLE(id INT, username TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE 'SELECT id, username FROM users WHERE username = ''' || p_username || '''';
    -- Vulnerable: p_username = "admin'; DROP TABLE users; --"
END;
$$ LANGUAGE plpgsql;

-- Good (safe with parameters)
CREATE FUNCTION get_user_safe(p_username TEXT)
RETURNS TABLE(id INT, username TEXT) AS $$
BEGIN
    RETURN QUERY EXECUTE 'SELECT id, username FROM users WHERE username = $1'
    USING p_username;
END;
$$ LANGUAGE plpgsql;

-- Better (use static SQL when possible)
CREATE FUNCTION get_user_best(p_username TEXT)
RETURNS TABLE(id INT, username TEXT) AS $$
BEGIN
    RETURN QUERY 
    SELECT u.id, u.username FROM users u WHERE u.username = p_username;
END;
$$ LANGUAGE plpgsql;

-- 2. Use quote_literal for dynamic SQL
CREATE FUNCTION safe_dynamic_table(p_table TEXT)
RETURNS void AS $$
BEGIN
    -- Validate table name first
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = p_table
    ) THEN
        RAISE EXCEPTION 'Invalid table name';
    END IF;
    
    EXECUTE 'SELECT * FROM ' || quote_ident(p_table);
END;
$$ LANGUAGE plpgsql;
```

## Auditing and Monitoring

### Comprehensive Audit Logging

```sql
-- postgresql.conf logging configuration:

-- What to log
-- log_connections = on
-- log_disconnections = on
-- log_duration = on
-- log_statement = 'all'  -- Or 'ddl', 'mod'
-- log_line_prefix = '%m [%p] %u@%d %h '

-- Log destination
-- logging_collector = on
-- log_directory = 'log'
-- log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
-- log_rotation_age = 1d
-- log_rotation_size = 100MB

-- Create audit log table
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    username TEXT,
    table_name TEXT,
    operation TEXT,
    old_data JSONB,
    new_data JSONB,
    client_addr INET,
    application_name TEXT
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger()
RETURNS TRIGGER AS $$
DECLARE
    client_addr INET;
    app_name TEXT;
BEGIN
    -- Get client info
    SELECT client_addr, application_name
    INTO client_addr, app_name
    FROM pg_stat_activity
    WHERE pid = pg_backend_pid();
    
    IF TG_OP = 'DELETE' THEN
        INSERT INTO audit_log (username, table_name, operation, old_data, client_addr, application_name)
        VALUES (current_user, TG_TABLE_NAME, 'DELETE', row_to_json(OLD), client_addr, app_name);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_log (username, table_name, operation, old_data, new_data, client_addr, application_name)
        VALUES (current_user, TG_TABLE_NAME, 'UPDATE', row_to_json(OLD), row_to_json(NEW), client_addr, app_name);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO audit_log (username, table_name, operation, new_data, client_addr, application_name)
        VALUES (current_user, TG_TABLE_NAME, 'INSERT', row_to_json(NEW), client_addr, app_name);
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Apply to sensitive tables
CREATE TRIGGER orders_audit
AFTER INSERT OR UPDATE OR DELETE ON orders
FOR EACH ROW EXECUTE FUNCTION audit_trigger();

-- Query audit log
SELECT 
    timestamp,
    username,
    table_name,
    operation,
    client_addr
FROM audit_log
WHERE timestamp > now() - interval '1 day'
ORDER BY timestamp DESC
LIMIT 100;
```

### Security Monitoring

```sql
-- Monitor suspicious activities

-- 1. Unusual query patterns
SELECT 
    usename,
    count(*) as query_count,
    count(DISTINCT client_addr) as unique_ips
FROM pg_stat_statements
JOIN pg_stat_activity USING (userid)
WHERE calls > 1000  -- High frequency
GROUP BY usename
HAVING count(DISTINCT client_addr) > 5;  -- Multiple sources

-- 2. Long-running queries (potential DoS)
SELECT 
    pid,
    now() - query_start as duration,
    usename,
    query
FROM pg_stat_activity
WHERE state = 'active'
  AND now() - query_start > interval '5 minutes'
ORDER BY duration DESC;

-- 3. Failed authentication attempts
-- Parse from PostgreSQL logs

-- 4. Privilege escalation attempts
CREATE TABLE privilege_changes (
    timestamp TIMESTAMP DEFAULT now(),
    changed_by TEXT,
    target_role TEXT,
    privilege TEXT
);

-- Log privilege grants
CREATE EVENT TRIGGER log_grant
ON ddl_command_end
WHEN TAG IN ('GRANT', 'REVOKE')
EXECUTE FUNCTION log_privilege_change();

-- 5. DDL changes (schema modifications)
CREATE TABLE ddl_audit (
    timestamp TIMESTAMP DEFAULT now(),
    username TEXT,
    command_tag TEXT,
    object_type TEXT,
    object_name TEXT,
    query TEXT
);

CREATE OR REPLACE FUNCTION audit_ddl()
RETURNS event_trigger AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        INSERT INTO ddl_audit (username, command_tag, object_type, object_name, query)
        VALUES (current_user, r.command_tag, r.object_type, r.object_identity, current_query());
    END LOOP;
END;
$$ LANGUAGE plpgsql;

CREATE EVENT TRIGGER ddl_audit_trigger
ON ddl_command_end
EXECUTE FUNCTION audit_ddl();
```

## Compliance

### GDPR Compliance

```sql
-- Right to Access: User can request their data
CREATE FUNCTION get_user_data(p_user_id INTEGER)
RETURNS TABLE (
    table_name TEXT,
    data JSONB
) AS $$
BEGIN
    -- Return all user data across tables
    RETURN QUERY
    SELECT 'users'::TEXT, row_to_json(u)::JSONB
    FROM users u WHERE u.id = p_user_id
    UNION ALL
    SELECT 'orders'::TEXT, row_to_json(o)::JSONB
    FROM orders o WHERE o.user_id = p_user_id
    UNION ALL
    SELECT 'addresses'::TEXT, row_to_json(a)::JSONB
    FROM addresses a WHERE a.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Right to Erasure: Delete user data
CREATE FUNCTION delete_user_data(p_user_id INTEGER)
RETURNS void AS $$
BEGIN
    DELETE FROM order_items WHERE order_id IN (SELECT id FROM orders WHERE user_id = p_user_id);
    DELETE FROM orders WHERE user_id = p_user_id;
    DELETE FROM addresses WHERE user_id = p_user_id;
    DELETE FROM users WHERE id = p_user_id;
    
    INSERT INTO gdpr_deletions (user_id, deleted_at)
    VALUES (p_user_id, now());
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Data retention policy
CREATE TABLE data_retention (
    table_name TEXT PRIMARY KEY,
    retention_days INTEGER NOT NULL
);

INSERT INTO data_retention VALUES
    ('audit_log', 2555),  -- 7 years
    ('sessions', 30),
    ('temp_data', 7);

-- Cleanup old data
CREATE FUNCTION cleanup_old_data()
RETURNS void AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN SELECT * FROM data_retention LOOP
        EXECUTE format(
            'DELETE FROM %I WHERE created_at < now() - interval ''%s days''',
            r.table_name, r.retention_days
        );
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### PCI DSS Compliance

```sql
-- Payment Card Industry Data Security Standard

-- 1. Encrypt cardholder data
CREATE TABLE payment_cards (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    pan_encrypted BYTEA NOT NULL,  -- Encrypted PAN (card number)
    pan_hash TEXT NOT NULL UNIQUE,  -- For duplicate detection
    last_four TEXT,  -- Can store last 4 digits unencrypted
    expiry_encrypted BYTEA,
    cvv_encrypted BYTEA,  -- Don't store CVV after auth!
    created_at TIMESTAMP DEFAULT now()
);

-- 2. Restrict access to cardholder data
REVOKE ALL ON payment_cards FROM public;
GRANT SELECT (id, user_id, last_four) ON payment_cards TO app_user;
GRANT INSERT, UPDATE, DELETE ON payment_cards TO payment_processor;

-- 3. Audit all access
CREATE TRIGGER payment_cards_audit
AFTER SELECT OR INSERT OR UPDATE OR DELETE ON payment_cards
FOR EACH STATEMENT EXECUTE FUNCTION audit_payment_access();

-- 4. Log and monitor
CREATE TABLE pci_access_log (
    timestamp TIMESTAMP DEFAULT now(),
    username TEXT,
    operation TEXT,
    record_count INTEGER,
    client_addr INET,
    INDEX idx_pci_timestamp (timestamp)
);

-- 5. Implement strong access control
-- Use RLS for multi-tenant
ALTER TABLE payment_cards ENABLE ROW LEVEL SECURITY;

CREATE POLICY payment_cards_policy ON payment_cards
FOR ALL TO app_user
USING (user_id = current_user_id());
```

### HIPAA Compliance

```sql
-- Health Insurance Portability and Accountability Act

-- 1. Encrypt PHI (Protected Health Information)
CREATE TABLE patient_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER,
    medical_record_encrypted BYTEA,  -- Encrypted PHI
    diagnosis_encrypted BYTEA,
    created_at TIMESTAMP,
    created_by TEXT
);

-- 2. Access controls and audit trail
CREATE TABLE hipaa_audit (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    user_id TEXT,
    patient_id INTEGER,
    action TEXT,
    reason TEXT,
    client_addr INET,
    CONSTRAINT require_reason CHECK (char_length(reason) > 0)
);

-- Require reason for access
CREATE FUNCTION access_patient_record(
    p_patient_id INTEGER,
    p_reason TEXT
) RETURNS TABLE (
    id INTEGER,
    medical_record TEXT
) AS $$
BEGIN
    -- Log access
    INSERT INTO hipaa_audit (user_id, patient_id, action, reason, client_addr)
    SELECT current_user, p_patient_id, 'ACCESS', p_reason, client_addr
    FROM pg_stat_activity WHERE pid = pg_backend_pid();
    
    -- Return data
    RETURN QUERY
    SELECT 
        pr.id,
        pgp_sym_decrypt(pr.medical_record_encrypted, current_setting('app.encryption_key'))::TEXT
    FROM patient_records pr
    WHERE pr.patient_id = p_patient_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 3. Minimum necessary access
GRANT EXECUTE ON FUNCTION access_patient_record TO doctor_role;
REVOKE ALL ON patient_records FROM doctor_role;
```

## Incident Response

### Security Incident Detection

```sql
-- Detect and alert on security incidents

-- 1. Unauthorized access attempts
CREATE FUNCTION detect_unauthorized_access()
RETURNS TABLE (
    timestamp TIMESTAMP,
    username TEXT,
    table_name TEXT,
    client_addr INET
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        al.timestamp,
        al.username,
        al.table_name,
        al.client_addr
    FROM audit_log al
    WHERE al.timestamp > now() - interval '1 hour'
      AND al.table_name IN ('payment_cards', 'patient_records', 'sensitive_data')
      AND al.username NOT IN (
          SELECT rolname FROM pg_roles WHERE rolname IN ('authorized_user_1', 'authorized_user_2')
      );
END;
$$ LANGUAGE plpgsql;

-- 2. Data exfiltration detection
SELECT 
    usename,
    count(*) as query_count,
    sum(rows) as total_rows
FROM pg_stat_statements
JOIN pg_roles ON (userid = oid)
WHERE query ILIKE '%SELECT%'
  AND calls > 100
GROUP BY usename
HAVING sum(rows) > 100000  -- Large data extraction
ORDER BY total_rows DESC;

-- 3. Privilege escalation
SELECT 
    timestamp,
    username,
    command_tag,
    query
FROM ddl_audit
WHERE command_tag IN ('GRANT', 'ALTER ROLE')
  AND timestamp > now() - interval '24 hours'
ORDER BY timestamp DESC;
```

### Incident Response Procedures

```sql
-- Immediate response to security incident

-- 1. Terminate suspicious connections
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE usename = 'suspicious_user'
  OR client_addr = '203.0.113.10';

-- 2. Revoke privileges
REVOKE ALL PRIVILEGES ON DATABASE mydb FROM suspicious_user;
REVOKE ALL PRIVILEGES ON ALL TABLES IN SCHEMA public FROM suspicious_user;

-- 3. Disable user account
ALTER ROLE suspicious_user NOLOGIN;

-- 4. Preserve evidence
CREATE TABLE incident_evidence AS
SELECT * FROM audit_log
WHERE username = 'suspicious_user'
  AND timestamp BETWEEN '2024-01-01' AND '2024-01-02';

-- 5. Analyze impact
SELECT 
    table_name,
    operation,
    count(*) as operation_count
FROM audit_log
WHERE username = 'suspicious_user'
  AND timestamp BETWEEN '2024-01-01' AND '2024-01-02'
GROUP BY table_name, operation;

-- 6. Restore from backup if needed
-- $ pg_restore -d mydb backup_file.dump

-- 7. Change passwords
ALTER ROLE app_user PASSWORD 'new_secure_password';

-- 8. Document incident
CREATE TABLE security_incidents (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT now(),
    incident_type TEXT,
    description TEXT,
    affected_users TEXT[],
    affected_tables TEXT[],
    actions_taken TEXT,
    resolved_at TIMESTAMP
);

INSERT INTO security_incidents (incident_type, description, affected_users, actions_taken)
VALUES (
    'Unauthorized Access',
    'Suspicious activity detected from user suspicious_user',
    ARRAY['suspicious_user'],
    'Terminated connections, revoked privileges, disabled account'
);
```

## Security Checklist

### Deployment Checklist

```sql
-- Pre-production security checklist

-- [ ] Network Security
--   [ ] Firewall configured (only necessary ports)
--   [ ] listen_addresses restricted
--   [ ] pg_hba.conf hardened
--   [ ] SSL/TLS enabled and required
--   [ ] Certificates from trusted CA

-- [ ] Authentication
--   [ ] Strong password policy enforced
--   [ ] password_encryption = 'scram-sha-256'
--   [ ] No default passwords
--   [ ] Password expiration configured
--   [ ] Failed login monitoring enabled

-- [ ] Authorization
--   [ ] Principle of least privilege applied
--   [ ] Public schema access revoked
--   [ ] Superuser accounts minimized
--   [ ] Role hierarchy implemented
--   [ ] Regular permission audits scheduled

-- [ ] Data Protection
--   [ ] Sensitive columns encrypted
--   [ ] Backups encrypted
--   [ ] Filesystem encryption enabled
--   [ ] Key management solution implemented
--   [ ] Data retention policies defined

-- [ ] Auditing and Monitoring
--   [ ] Comprehensive logging enabled
--   [ ] Audit triggers on sensitive tables
--   [ ] Log rotation configured
--   [ ] Security monitoring tools deployed
--   [ ] Alert rules configured

-- [ ] Compliance
--   [ ] GDPR/PCI/HIPAA requirements met (if applicable)
--   [ ] Data classification documented
--   [ ] Privacy policies implemented
--   [ ] Compliance audits scheduled

-- [ ] Incident Response
--   [ ] Incident response plan documented
--   [ ] Security contacts defined
--   [ ] Backup and recovery tested
--   [ ] Monitoring and alerting validated

-- Query to verify some checks
SELECT 
    'SSL Enabled' as check_item,
    CASE WHEN setting = 'on' THEN '✓' ELSE '✗' END as status
FROM pg_settings WHERE name = 'ssl'
UNION ALL
SELECT 
    'Password Encryption',
    CASE WHEN setting = 'scram-sha-256' THEN '✓' ELSE '✗' END
FROM pg_settings WHERE name = 'password_encryption'
UNION ALL
SELECT 
    'Logging Enabled',
    CASE WHEN setting = 'on' THEN '✓' ELSE '✗' END
FROM pg_settings WHERE name = 'logging_collector';
```

## Summary

PostgreSQL security requires:
- **Defense in Depth**: Multiple security layers
- **Strong Authentication**: SCRAM-SHA-256, SSL certificates
- **Least Privilege**: Minimal necessary permissions
- **Encryption**: SSL/TLS, column encryption, filesystem encryption
- **Auditing**: Comprehensive logging and monitoring
- **Compliance**: GDPR, PCI DSS, HIPAA requirements
- **Incident Response**: Detection, response, and recovery procedures

Security is an ongoing process requiring regular audits and updates.

## Next Steps

- Review [Authentication and Authorization](./30-authentication-authorization.md)
- Study [SSL and Encryption](./32-ssl-and-encryption.md)
- Learn [Monitoring and Logging](./38-monitoring-and-logging.md)
- Explore [Backup and Recovery](./35-backup-and-recovery.md)
