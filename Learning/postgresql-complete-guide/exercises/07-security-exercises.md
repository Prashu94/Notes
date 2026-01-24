# Part 7: Security Exercises

## Topics Covered
- Authentication and Authorization (Chapter 30)
- Row-Level Security (Chapter 31)
- SSL and Encryption (Chapter 32)
- Security Best Practices (Chapter 33)

---

## Exercise 7.1: Role-Based Access Control (RBAC) 🟡

### Scenario
Implement a comprehensive role-based access control system for NeoBank that supports different user types with varying permission levels.

### Requirements
1. Define roles for different job functions
2. Implement principle of least privilege
3. Support role inheritance
4. Create audit capabilities

### Solution

```sql
-- Step 1: Create role hierarchy
-- Base roles (no login - for grouping permissions)
CREATE ROLE neobank_base NOLOGIN;
CREATE ROLE neobank_read NOLOGIN;
CREATE ROLE neobank_write NOLOGIN;
CREATE ROLE neobank_admin NOLOGIN;

-- Job function roles
CREATE ROLE teller NOLOGIN;           -- Branch tellers
CREATE ROLE customer_service NOLOGIN;  -- Customer service reps
CREATE ROLE loan_officer NOLOGIN;      -- Loan processing
CREATE ROLE analyst NOLOGIN;           -- Business analysts
CREATE ROLE compliance NOLOGIN;        -- Compliance officers
CREATE ROLE developer NOLOGIN;         -- Application developers
CREATE ROLE dba NOLOGIN;               -- Database administrators

-- Step 2: Define permission hierarchy
-- neobank_read: Basic read access
GRANT USAGE ON SCHEMA banking, lending, analytics TO neobank_read;
GRANT SELECT ON ALL TABLES IN SCHEMA banking TO neobank_read;
GRANT SELECT ON ALL TABLES IN SCHEMA lending TO neobank_read;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO neobank_read;

-- neobank_write: Read + write access
GRANT neobank_read TO neobank_write;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA banking TO neobank_write;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA lending TO neobank_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA banking TO neobank_write;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA lending TO neobank_write;

-- neobank_admin: Full access except security changes
GRANT neobank_write TO neobank_admin;
GRANT DELETE ON ALL TABLES IN SCHEMA banking TO neobank_admin;
GRANT DELETE ON ALL TABLES IN SCHEMA lending TO neobank_admin;
GRANT TRUNCATE ON ALL TABLES IN SCHEMA analytics TO neobank_admin;
GRANT USAGE ON SCHEMA audit TO neobank_admin;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO neobank_admin;

-- Step 3: Assign permissions to job roles
-- Teller: View and create transactions, view accounts
GRANT neobank_read TO teller;
GRANT INSERT ON banking.transactions TO teller;
GRANT UPDATE ON banking.accounts TO teller;  -- For balance updates
GRANT EXECUTE ON FUNCTION banking.execute_transfer TO teller;

-- Customer service: Broader read, limited updates
GRANT neobank_read TO customer_service;
GRANT UPDATE (phone_primary, phone_secondary, address_line1, address_line2, 
              city, state_province, postal_code, notification_preferences) 
    ON banking.customers TO customer_service;

-- Loan officer: Full lending access
GRANT neobank_read TO loan_officer;
GRANT INSERT, UPDATE ON ALL TABLES IN SCHEMA lending TO loan_officer;
GRANT EXECUTE ON PROCEDURE lending.submit_loan_application TO loan_officer;
GRANT EXECUTE ON PROCEDURE lending.process_loan_decision TO loan_officer;
GRANT EXECUTE ON PROCEDURE lending.disburse_loan TO loan_officer;

-- Analyst: Read-only including analytics
GRANT neobank_read TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO analyst;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA analytics TO analyst;
-- No access to PII
REVOKE SELECT ON banking.customers FROM analyst;
-- Create a view with masked data
GRANT SELECT ON banking.v_customers_masked TO analyst;

-- Compliance: Read all including audit
GRANT neobank_read TO compliance;
GRANT USAGE ON SCHEMA audit TO compliance;
GRANT SELECT ON ALL TABLES IN SCHEMA audit TO compliance;
-- Cannot modify anything

-- Developer: Schema access for development
GRANT neobank_read TO developer;
GRANT CREATE ON SCHEMA banking, lending, analytics TO developer;
-- No direct data modification in production

-- DBA: Full access
GRANT neobank_admin TO dba;
GRANT ALL ON SCHEMA banking, lending, analytics, audit TO dba;

-- Step 4: Create login users with role assignments
CREATE USER alice_teller WITH LOGIN PASSWORD 'secure_pwd_1' VALID UNTIL '2027-01-01';
GRANT teller TO alice_teller;

CREATE USER bob_loan_officer WITH LOGIN PASSWORD 'secure_pwd_2' VALID UNTIL '2027-01-01';
GRANT loan_officer TO bob_loan_officer;

CREATE USER charlie_analyst WITH LOGIN PASSWORD 'secure_pwd_3' VALID UNTIL '2027-01-01';
GRANT analyst TO charlie_analyst;

CREATE USER diana_compliance WITH LOGIN PASSWORD 'secure_pwd_4' VALID UNTIL '2027-01-01';
GRANT compliance TO diana_compliance;

-- Step 5: Create masked view for analysts
CREATE OR REPLACE VIEW banking.v_customers_masked AS
SELECT 
    customer_id,
    customer_number,
    -- Mask name: Show first letter and last name initial
    LEFT(first_name, 1) || '***' AS first_name,
    LEFT(last_name, 1) || '***' AS last_name,
    -- Mask email: Show first 3 chars and domain
    LEFT(email, 3) || '***@' || SPLIT_PART(email, '@', 2) AS email,
    -- Mask phone: Show last 4 digits
    '***-***-' || RIGHT(phone_primary, 4) AS phone_primary,
    -- Demographics (aggregatable but not identifiable)
    EXTRACT(YEAR FROM AGE(date_of_birth))::INTEGER AS age,
    city,
    state_province,
    country_code,
    customer_type,
    customer_status,
    kyc_status,
    created_at
FROM banking.customers;

-- Step 6: Function to check user permissions
CREATE OR REPLACE FUNCTION audit.check_user_permissions(p_username TEXT)
RETURNS TABLE (
    role_name TEXT,
    schema_name TEXT,
    table_name TEXT,
    privilege TEXT
)
LANGUAGE SQL
SECURITY DEFINER
AS $$
    WITH user_roles AS (
        SELECT rolname
        FROM pg_roles
        WHERE pg_has_role(p_username, oid, 'member')
    )
    SELECT 
        grantee::TEXT AS role_name,
        table_schema::TEXT AS schema_name,
        table_name::TEXT,
        privilege_type::TEXT AS privilege
    FROM information_schema.table_privileges
    WHERE grantee IN (SELECT rolname FROM user_roles)
      AND table_schema IN ('banking', 'lending', 'analytics', 'audit')
    ORDER BY table_schema, table_name, privilege_type;
$$;

-- Check permissions for a user
SELECT * FROM audit.check_user_permissions('alice_teller');
```

---

## Exercise 7.2: Row-Level Security for Multi-Tenant Data 🔴

### Scenario
Implement row-level security to ensure customers can only see their own data, while allowing different levels of access for staff roles.

### Requirements
1. Customers see only their own data
2. Tellers see customers assigned to their branch
3. Managers see all customers in their region
4. Compliance sees everything but cannot modify

### Solution

```sql
-- Step 1: Add branch/region context to tables
ALTER TABLE banking.customers 
ADD COLUMN IF NOT EXISTS branch_id INTEGER,
ADD COLUMN IF NOT EXISTS region_id INTEGER;

-- Step 2: Create session context table for application use
CREATE TABLE IF NOT EXISTS banking.session_context (
    session_id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::TEXT,
    user_id UUID,
    customer_id UUID,
    employee_id UUID,
    branch_id INTEGER,
    region_id INTEGER,
    role_type TEXT,  -- 'customer', 'teller', 'manager', 'compliance', 'admin'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '8 hours'
);

-- Step 3: Functions to set and get session context
CREATE OR REPLACE FUNCTION banking.set_session_context(
    p_role_type TEXT,
    p_customer_id UUID DEFAULT NULL,
    p_employee_id UUID DEFAULT NULL,
    p_branch_id INTEGER DEFAULT NULL,
    p_region_id INTEGER DEFAULT NULL
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_session_id TEXT;
BEGIN
    v_session_id := gen_random_uuid()::TEXT;
    
    INSERT INTO banking.session_context (
        session_id, customer_id, employee_id, branch_id, region_id, role_type
    ) VALUES (
        v_session_id, p_customer_id, p_employee_id, p_branch_id, p_region_id, p_role_type
    );
    
    -- Set session variable
    PERFORM set_config('app.session_id', v_session_id, FALSE);
    PERFORM set_config('app.role_type', p_role_type, FALSE);
    PERFORM set_config('app.customer_id', COALESCE(p_customer_id::TEXT, ''), FALSE);
    PERFORM set_config('app.branch_id', COALESCE(p_branch_id::TEXT, ''), FALSE);
    PERFORM set_config('app.region_id', COALESCE(p_region_id::TEXT, ''), FALSE);
    
    RETURN v_session_id;
END;
$$;

CREATE OR REPLACE FUNCTION banking.get_current_customer_id()
RETURNS UUID
LANGUAGE SQL
STABLE
AS $$
    SELECT NULLIF(current_setting('app.customer_id', TRUE), '')::UUID;
$$;

CREATE OR REPLACE FUNCTION banking.get_current_branch_id()
RETURNS INTEGER
LANGUAGE SQL
STABLE
AS $$
    SELECT NULLIF(current_setting('app.branch_id', TRUE), '')::INTEGER;
$$;

CREATE OR REPLACE FUNCTION banking.get_current_role_type()
RETURNS TEXT
LANGUAGE SQL
STABLE
AS $$
    SELECT COALESCE(current_setting('app.role_type', TRUE), 'none');
$$;

-- Step 4: Enable RLS on tables
ALTER TABLE banking.customers ENABLE ROW LEVEL SECURITY;
ALTER TABLE banking.accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE banking.transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE lending.loans ENABLE ROW LEVEL SECURITY;

-- Step 5: Create RLS policies for customers table

-- Policy: Customers can only see themselves
CREATE POLICY customer_self_access ON banking.customers
    FOR ALL
    TO PUBLIC
    USING (
        banking.get_current_role_type() = 'customer'
        AND customer_id = banking.get_current_customer_id()
    )
    WITH CHECK (
        banking.get_current_role_type() = 'customer'
        AND customer_id = banking.get_current_customer_id()
    );

-- Policy: Tellers can see customers in their branch
CREATE POLICY teller_branch_access ON banking.customers
    FOR SELECT
    TO teller
    USING (
        banking.get_current_role_type() = 'teller'
        AND branch_id = banking.get_current_branch_id()
    );

-- Policy: Tellers can update limited fields for their branch customers
CREATE POLICY teller_branch_update ON banking.customers
    FOR UPDATE
    TO teller
    USING (branch_id = banking.get_current_branch_id())
    WITH CHECK (branch_id = banking.get_current_branch_id());

-- Policy: Managers can see all customers in their region
CREATE POLICY manager_region_access ON banking.customers
    FOR SELECT
    TO neobank_admin
    USING (
        banking.get_current_role_type() = 'manager'
        AND region_id = NULLIF(current_setting('app.region_id', TRUE), '')::INTEGER
    );

-- Policy: Compliance can see everything
CREATE POLICY compliance_full_read ON banking.customers
    FOR SELECT
    TO compliance
    USING (banking.get_current_role_type() = 'compliance');

-- Policy: DBAs bypass RLS
ALTER TABLE banking.customers FORCE ROW LEVEL SECURITY;
CREATE POLICY dba_bypass ON banking.customers
    FOR ALL
    TO dba
    USING (TRUE)
    WITH CHECK (TRUE);

-- Step 6: RLS for accounts table
CREATE POLICY customer_accounts ON banking.accounts
    FOR ALL
    TO PUBLIC
    USING (
        banking.get_current_role_type() = 'customer'
        AND customer_id = banking.get_current_customer_id()
    );

CREATE POLICY staff_accounts ON banking.accounts
    FOR SELECT
    TO teller, customer_service, loan_officer
    USING (
        banking.get_current_role_type() IN ('teller', 'customer_service', 'loan_officer')
    );

-- Step 7: RLS for transactions table
CREATE POLICY customer_transactions ON banking.transactions
    FOR SELECT
    TO PUBLIC
    USING (
        banking.get_current_role_type() = 'customer'
        AND account_id IN (
            SELECT account_id FROM banking.accounts 
            WHERE customer_id = banking.get_current_customer_id()
        )
    );

CREATE POLICY staff_transactions ON banking.transactions
    FOR SELECT
    TO teller, customer_service, compliance
    USING (TRUE);  -- Staff can see all transactions

-- Step 8: Test RLS

-- Simulate customer login
SELECT banking.set_session_context(
    'customer',
    (SELECT customer_id FROM banking.customers WHERE customer_number = 'CUST-2026-00001')
);

-- This should only return the logged-in customer's data
SELECT * FROM banking.customers;  -- Should see only their own record
SELECT * FROM banking.accounts;   -- Should see only their own accounts

-- Simulate teller login
SELECT banking.set_session_context('teller', NULL, NULL, 1, 1);

-- Teller should see all customers in branch 1
SELECT customer_number, first_name, last_name FROM banking.customers;

-- Step 9: RLS for sensitive operations audit
CREATE OR REPLACE FUNCTION audit.log_rls_access()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO audit.change_log (
        table_schema,
        table_name,
        record_id,
        operation,
        context
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        CASE TG_OP 
            WHEN 'DELETE' THEN OLD.customer_id::TEXT
            ELSE NEW.customer_id::TEXT
        END,
        TG_OP,
        jsonb_build_object(
            'role_type', banking.get_current_role_type(),
            'session_id', current_setting('app.session_id', TRUE),
            'timestamp', NOW()
        )
    );
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;
```

---

## Exercise 7.3: Data Encryption and Masking 🔴

### Scenario
Implement encryption for sensitive data at rest and create data masking functions for different user contexts.

### Solution

```sql
-- Enable pgcrypto extension
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Step 1: Create encryption key management (simplified - use proper KMS in production)
CREATE TABLE IF NOT EXISTS audit.encryption_keys (
    key_id SERIAL PRIMARY KEY,
    key_name VARCHAR(100) UNIQUE NOT NULL,
    key_value BYTEA NOT NULL,  -- In production, this would be in a KMS
    algorithm VARCHAR(50) DEFAULT 'aes256',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    rotated_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- Store encryption key (in production, use AWS KMS, HashiCorp Vault, etc.)
INSERT INTO audit.encryption_keys (key_name, key_value) 
VALUES ('pii_key', pgp_sym_encrypt('master-encryption-key-32bytes!!', 'key-encryption-key'));

-- Step 2: Create encryption/decryption functions
CREATE OR REPLACE FUNCTION banking.encrypt_pii(
    p_data TEXT,
    p_key_name VARCHAR(100) DEFAULT 'pii_key'
)
RETURNS BYTEA
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_key TEXT;
BEGIN
    -- Get the encryption key
    SELECT pgp_sym_decrypt(key_value, 'key-encryption-key')
    INTO v_key
    FROM audit.encryption_keys
    WHERE key_name = p_key_name AND is_active;
    
    IF v_key IS NULL THEN
        RAISE EXCEPTION 'Encryption key not found or inactive';
    END IF;
    
    RETURN pgp_sym_encrypt(p_data, v_key);
END;
$$;

CREATE OR REPLACE FUNCTION banking.decrypt_pii(
    p_encrypted BYTEA,
    p_key_name VARCHAR(100) DEFAULT 'pii_key'
)
RETURNS TEXT
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_key TEXT;
BEGIN
    -- Check if user has permission to decrypt
    IF NOT (
        banking.get_current_role_type() IN ('admin', 'compliance', 'customer_service')
        OR pg_has_role(CURRENT_USER, 'dba', 'member')
    ) THEN
        RAISE EXCEPTION 'Insufficient privileges to decrypt PII';
    END IF;
    
    -- Get the encryption key
    SELECT pgp_sym_decrypt(key_value, 'key-encryption-key')
    INTO v_key
    FROM audit.encryption_keys
    WHERE key_name = p_key_name AND is_active;
    
    IF v_key IS NULL THEN
        RAISE EXCEPTION 'Encryption key not found or inactive';
    END IF;
    
    RETURN pgp_sym_decrypt(p_encrypted, v_key);
EXCEPTION
    WHEN OTHERS THEN
        -- Log decryption attempt
        INSERT INTO audit.change_log (table_schema, table_name, operation, context)
        VALUES ('banking', 'pii_decryption', 'DECRYPT_FAILED', 
                jsonb_build_object('user', CURRENT_USER, 'error', SQLERRM));
        RAISE;
END;
$$;

-- Step 3: Create table with encrypted columns
CREATE TABLE IF NOT EXISTS banking.customer_sensitive_data (
    customer_id UUID PRIMARY KEY REFERENCES banking.customers(customer_id),
    ssn_encrypted BYTEA,
    ssn_last_four CHAR(4),  -- For display/verification
    drivers_license_encrypted BYTEA,
    passport_encrypted BYTEA,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 4: Functions to store and retrieve encrypted data
CREATE OR REPLACE FUNCTION banking.store_ssn(
    p_customer_id UUID,
    p_ssn TEXT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Validate SSN format
    IF NOT p_ssn ~ '^\d{3}-\d{2}-\d{4}$' THEN
        RAISE EXCEPTION 'Invalid SSN format';
    END IF;
    
    INSERT INTO banking.customer_sensitive_data (
        customer_id,
        ssn_encrypted,
        ssn_last_four
    ) VALUES (
        p_customer_id,
        banking.encrypt_pii(p_ssn),
        RIGHT(REPLACE(p_ssn, '-', ''), 4)
    )
    ON CONFLICT (customer_id) DO UPDATE SET
        ssn_encrypted = banking.encrypt_pii(p_ssn),
        ssn_last_four = RIGHT(REPLACE(p_ssn, '-', ''), 4),
        updated_at = NOW();
    
    -- Audit log
    INSERT INTO audit.change_log (table_schema, table_name, record_id, operation, context)
    VALUES ('banking', 'customer_sensitive_data', p_customer_id::TEXT, 'SSN_UPDATED',
            jsonb_build_object('user', CURRENT_USER, 'last_four', RIGHT(REPLACE(p_ssn, '-', ''), 4)));
    
    RETURN TRUE;
END;
$$;

-- Step 5: Data masking functions
CREATE OR REPLACE FUNCTION banking.mask_ssn(p_ssn TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT '***-**-' || RIGHT(REPLACE(p_ssn, '-', ''), 4);
$$;

CREATE OR REPLACE FUNCTION banking.mask_email(p_email TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT 
        CASE 
            WHEN p_email IS NULL THEN NULL
            WHEN LENGTH(SPLIT_PART(p_email, '@', 1)) <= 3 THEN '***@' || SPLIT_PART(p_email, '@', 2)
            ELSE LEFT(SPLIT_PART(p_email, '@', 1), 3) || '***@' || SPLIT_PART(p_email, '@', 2)
        END;
$$;

CREATE OR REPLACE FUNCTION banking.mask_phone(p_phone TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT 
        CASE 
            WHEN p_phone IS NULL THEN NULL
            ELSE '(***) ***-' || RIGHT(REGEXP_REPLACE(p_phone, '[^0-9]', '', 'g'), 4)
        END;
$$;

CREATE OR REPLACE FUNCTION banking.mask_account_number(p_account TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT 
        CASE 
            WHEN p_account IS NULL THEN NULL
            ELSE '****' || RIGHT(p_account, 4)
        END;
$$;

CREATE OR REPLACE FUNCTION banking.mask_card_number(p_card TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT 
        CASE 
            WHEN p_card IS NULL THEN NULL
            ELSE '**** **** **** ' || RIGHT(REGEXP_REPLACE(p_card, '[^0-9]', '', 'g'), 4)
        END;
$$;

-- Step 6: Create role-aware masking view
CREATE OR REPLACE VIEW banking.v_customer_data AS
SELECT 
    c.customer_id,
    c.customer_number,
    -- Name: Show full to authorized roles, partial to others
    CASE 
        WHEN banking.get_current_role_type() IN ('compliance', 'admin', 'customer_service')
            OR c.customer_id = banking.get_current_customer_id()
        THEN c.first_name
        ELSE LEFT(c.first_name, 1) || '***'
    END AS first_name,
    CASE 
        WHEN banking.get_current_role_type() IN ('compliance', 'admin', 'customer_service')
            OR c.customer_id = banking.get_current_customer_id()
        THEN c.last_name
        ELSE LEFT(c.last_name, 1) || '***'
    END AS last_name,
    -- Email: Masked except for authorized roles
    CASE 
        WHEN banking.get_current_role_type() IN ('compliance', 'admin', 'customer_service')
            OR c.customer_id = banking.get_current_customer_id()
        THEN c.email
        ELSE banking.mask_email(c.email)
    END AS email,
    -- Phone: Masked
    CASE 
        WHEN banking.get_current_role_type() IN ('compliance', 'admin')
            OR c.customer_id = banking.get_current_customer_id()
        THEN c.phone_primary
        ELSE banking.mask_phone(c.phone_primary)
    END AS phone_primary,
    -- SSN: Only last 4 shown
    COALESCE(csd.ssn_last_four, '****') AS ssn_last_four,
    -- Other non-sensitive fields
    c.customer_type,
    c.customer_status,
    c.kyc_status,
    c.city,
    c.state_province,
    c.country_code,
    c.created_at
FROM banking.customers c
LEFT JOIN banking.customer_sensitive_data csd ON c.customer_id = csd.customer_id;

-- Step 7: Password hashing functions
CREATE OR REPLACE FUNCTION banking.hash_password(p_password TEXT)
RETURNS TEXT
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT crypt(p_password, gen_salt('bf', 12));  -- bcrypt with cost 12
$$;

CREATE OR REPLACE FUNCTION banking.verify_password(p_password TEXT, p_hash TEXT)
RETURNS BOOLEAN
LANGUAGE SQL
IMMUTABLE
AS $$
    SELECT crypt(p_password, p_hash) = p_hash;
$$;
```

---

## Exercise 7.4: Security Audit and Monitoring 🟡

### Scenario
Implement comprehensive security auditing to track access attempts, privilege changes, and suspicious activities.

### Solution

```sql
-- Step 1: Create security audit tables
CREATE TABLE IF NOT EXISTS audit.security_events (
    event_id BIGSERIAL PRIMARY KEY,
    event_type VARCHAR(50) NOT NULL,
    event_severity VARCHAR(20) DEFAULT 'INFO',
    username TEXT,
    client_ip INET,
    database_name TEXT DEFAULT current_database(),
    schema_name TEXT,
    object_name TEXT,
    object_type TEXT,
    command TEXT,
    query_text TEXT,
    success BOOLEAN,
    error_message TEXT,
    event_timestamp TIMESTAMPTZ DEFAULT NOW(),
    session_info JSONB DEFAULT '{}'
);

CREATE INDEX idx_security_events_timestamp ON audit.security_events (event_timestamp DESC);
CREATE INDEX idx_security_events_type ON audit.security_events (event_type);
CREATE INDEX idx_security_events_user ON audit.security_events (username);

-- Step 2: Create event logging functions
CREATE OR REPLACE FUNCTION audit.log_security_event(
    p_event_type VARCHAR(50),
    p_severity VARCHAR(20),
    p_object_name TEXT DEFAULT NULL,
    p_command TEXT DEFAULT NULL,
    p_success BOOLEAN DEFAULT TRUE,
    p_error TEXT DEFAULT NULL,
    p_additional JSONB DEFAULT '{}'
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO audit.security_events (
        event_type,
        event_severity,
        username,
        client_ip,
        object_name,
        command,
        success,
        error_message,
        session_info
    ) VALUES (
        p_event_type,
        p_severity,
        CURRENT_USER,
        inet_client_addr(),
        p_object_name,
        p_command,
        p_success,
        p_error,
        p_additional || jsonb_build_object(
            'session_user', SESSION_USER,
            'application_name', current_setting('application_name', TRUE),
            'session_id', current_setting('app.session_id', TRUE)
        )
    );
END;
$$;

-- Step 3: Create DDL event trigger for privilege changes
CREATE OR REPLACE FUNCTION audit.log_ddl_events()
RETURNS event_trigger
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_obj RECORD;
BEGIN
    FOR v_obj IN SELECT * FROM pg_event_trigger_ddl_commands()
    LOOP
        INSERT INTO audit.security_events (
            event_type,
            event_severity,
            username,
            client_ip,
            schema_name,
            object_name,
            object_type,
            command,
            success
        ) VALUES (
            'DDL_COMMAND',
            CASE 
                WHEN v_obj.command_tag IN ('GRANT', 'REVOKE', 'CREATE ROLE', 'DROP ROLE', 'ALTER ROLE')
                THEN 'WARNING'
                ELSE 'INFO'
            END,
            CURRENT_USER,
            inet_client_addr(),
            v_obj.schema_name,
            v_obj.object_identity,
            v_obj.object_type,
            v_obj.command_tag,
            TRUE
        );
    END LOOP;
END;
$$;

CREATE EVENT TRIGGER audit_ddl_events ON ddl_command_end
    EXECUTE FUNCTION audit.log_ddl_events();

-- Step 4: Login attempt tracking (requires connection pool or application integration)
CREATE TABLE IF NOT EXISTS audit.login_attempts (
    attempt_id BIGSERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    client_ip INET,
    success BOOLEAN NOT NULL,
    failure_reason TEXT,
    attempt_timestamp TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_login_attempts_user ON audit.login_attempts (username, attempt_timestamp DESC);

-- Function to check for brute force attacks
CREATE OR REPLACE FUNCTION audit.check_brute_force(
    p_username TEXT,
    p_max_attempts INTEGER DEFAULT 5,
    p_window_minutes INTEGER DEFAULT 15
)
RETURNS BOOLEAN
LANGUAGE SQL
STABLE
AS $$
    SELECT COUNT(*) >= p_max_attempts
    FROM audit.login_attempts
    WHERE username = p_username
      AND success = FALSE
      AND attempt_timestamp > NOW() - (p_window_minutes || ' minutes')::INTERVAL;
$$;

-- Step 5: Suspicious activity detection
CREATE OR REPLACE VIEW audit.v_suspicious_activities AS
WITH 
-- Multiple failed logins
failed_logins AS (
    SELECT 
        username,
        client_ip,
        COUNT(*) AS failure_count,
        'MULTIPLE_FAILED_LOGINS' AS alert_type,
        'HIGH' AS severity
    FROM audit.login_attempts
    WHERE success = FALSE
      AND attempt_timestamp > NOW() - INTERVAL '1 hour'
    GROUP BY username, client_ip
    HAVING COUNT(*) >= 3
),
-- After-hours access
after_hours AS (
    SELECT DISTINCT
        username,
        client_ip,
        1 AS failure_count,
        'AFTER_HOURS_ACCESS' AS alert_type,
        'MEDIUM' AS severity
    FROM audit.security_events
    WHERE event_timestamp > NOW() - INTERVAL '24 hours'
      AND EXTRACT(HOUR FROM event_timestamp) NOT BETWEEN 6 AND 22
      AND event_type NOT IN ('SCHEDULED_JOB')
),
-- Privilege escalation attempts
priv_escalation AS (
    SELECT 
        username,
        client_ip,
        COUNT(*) AS failure_count,
        'PRIVILEGE_ESCALATION_ATTEMPT' AS alert_type,
        'CRITICAL' AS severity
    FROM audit.security_events
    WHERE event_timestamp > NOW() - INTERVAL '24 hours'
      AND success = FALSE
      AND error_message LIKE '%permission denied%'
    GROUP BY username, client_ip
    HAVING COUNT(*) >= 2
),
-- Mass data access
mass_access AS (
    SELECT 
        username,
        client_ip,
        COUNT(*) AS failure_count,
        'MASS_DATA_ACCESS' AS alert_type,
        'HIGH' AS severity
    FROM audit.security_events
    WHERE event_timestamp > NOW() - INTERVAL '1 hour'
      AND command IN ('SELECT', 'COPY')
    GROUP BY username, client_ip
    HAVING COUNT(*) >= 100
)
SELECT * FROM failed_logins
UNION ALL SELECT * FROM after_hours
UNION ALL SELECT * FROM priv_escalation
UNION ALL SELECT * FROM mass_access;

-- Step 6: Security compliance report
CREATE OR REPLACE FUNCTION audit.generate_security_report(
    p_start_date TIMESTAMPTZ DEFAULT NOW() - INTERVAL '7 days',
    p_end_date TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    report_section TEXT,
    metric_name TEXT,
    metric_value TEXT,
    status TEXT
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Login Statistics
    RETURN QUERY
    SELECT 
        'Login Activity'::TEXT,
        'Total Login Attempts'::TEXT,
        COUNT(*)::TEXT,
        'INFO'::TEXT
    FROM audit.login_attempts
    WHERE attempt_timestamp BETWEEN p_start_date AND p_end_date;
    
    RETURN QUERY
    SELECT 
        'Login Activity',
        'Failed Login Attempts',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 100 THEN 'WARNING' ELSE 'OK' END
    FROM audit.login_attempts
    WHERE attempt_timestamp BETWEEN p_start_date AND p_end_date
      AND success = FALSE;
    
    -- DDL Activity
    RETURN QUERY
    SELECT 
        'Schema Changes',
        'DDL Commands Executed',
        COUNT(*)::TEXT,
        'INFO'
    FROM audit.security_events
    WHERE event_timestamp BETWEEN p_start_date AND p_end_date
      AND event_type = 'DDL_COMMAND';
    
    -- Permission Changes
    RETURN QUERY
    SELECT 
        'Permission Changes',
        'GRANT/REVOKE Operations',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 10 THEN 'REVIEW' ELSE 'OK' END
    FROM audit.security_events
    WHERE event_timestamp BETWEEN p_start_date AND p_end_date
      AND command IN ('GRANT', 'REVOKE');
    
    -- Suspicious Activities
    RETURN QUERY
    SELECT 
        'Alerts',
        'Suspicious Activities Detected',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'ALERT' ELSE 'OK' END
    FROM audit.v_suspicious_activities;
    
    -- Password expiring
    RETURN QUERY
    SELECT 
        'User Management',
        'Users with Expiring Passwords (30 days)',
        COUNT(*)::TEXT,
        CASE WHEN COUNT(*) > 0 THEN 'WARNING' ELSE 'OK' END
    FROM pg_roles
    WHERE rolvaliduntil IS NOT NULL
      AND rolvaliduntil < NOW() + INTERVAL '30 days';
END;
$$;

-- Generate report
SELECT * FROM audit.generate_security_report();
```

---

## 🎯 Practice Challenges

### Challenge 7.1 🟡
Implement a password policy enforcement function that checks password complexity, history, and expiration.

### Challenge 7.2 🔴
Create a dynamic data masking system that automatically masks sensitive data based on the calling user's role.

### Challenge 7.3 ⚫
Implement a complete audit trail system that captures before/after values for all changes with tamper-evident logging.

---

**Next: [Part 8 - Administration Exercises](08-administration-exercises.md)**
