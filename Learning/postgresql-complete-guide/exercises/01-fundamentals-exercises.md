# Part 1: Fundamentals Exercises

## Topics Covered
- Basic SQL Operations (Chapter 5)
- Data Types (Chapter 4)
- Database and Schema Management

---

## Exercise 1.1: Database and Schema Setup 🟢

### Scenario
You're the lead database engineer starting the NeoBank project. Your first task is to create the initial database structure with proper organization using schemas.

### Requirements
1. Create the `neobank` database with UTF-8 encoding
2. Create schemas for different business domains
3. Set up a search path for convenient access

### Your Task
Write SQL to accomplish the above requirements.

### Solution

```sql
-- 1. Create the database (run as superuser)
CREATE DATABASE neobank
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TEMPLATE = template0
    CONNECTION LIMIT = 100;

-- Connect to the new database
\c neobank

-- 2. Create business domain schemas
CREATE SCHEMA IF NOT EXISTS banking
    AUTHORIZATION postgres;
COMMENT ON SCHEMA banking IS 'Core banking operations - accounts, transactions, transfers';

CREATE SCHEMA IF NOT EXISTS investments
    AUTHORIZATION postgres;
COMMENT ON SCHEMA investments IS 'Investment services - portfolios, trades, market data';

CREATE SCHEMA IF NOT EXISTS lending
    AUTHORIZATION postgres;
COMMENT ON SCHEMA lending IS 'Lending products - loans, credit cards, mortgages';

CREATE SCHEMA IF NOT EXISTS analytics
    AUTHORIZATION postgres;
COMMENT ON SCHEMA analytics IS 'Analytics and reporting data';

CREATE SCHEMA IF NOT EXISTS audit
    AUTHORIZATION postgres;
COMMENT ON SCHEMA audit IS 'Audit trails and compliance logs';

-- 3. Set the search path
ALTER DATABASE neobank SET search_path TO banking, investments, lending, analytics, audit, public;

-- Verify schemas
SELECT schema_name, schema_owner 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast');

-- Verify search path
SHOW search_path;
```

---

## Exercise 1.2: Customer Table with Proper Data Types 🟢

### Scenario
Design the core customers table that will store all NeoBank customer information. This includes personal details, contact information, and KYC (Know Your Customer) data required for regulatory compliance.

### Requirements
1. Unique customer identifier
2. Personal information (name, date of birth, SSN/Tax ID)
3. Contact details (email, phone, address)
4. Account status and type
5. KYC verification status
6. Timestamps for audit

### Your Task
Create the customers table with appropriate data types and constraints.

### Solution

```sql
-- Create ENUM types for status fields
CREATE TYPE banking.customer_status AS ENUM (
    'pending_verification',
    'active', 
    'suspended',
    'closed',
    'blocked'
);

CREATE TYPE banking.customer_type AS ENUM (
    'individual',
    'business',
    'joint'
);

CREATE TYPE banking.kyc_status AS ENUM (
    'not_started',
    'documents_pending',
    'under_review',
    'verified',
    'rejected',
    'expired'
);

-- Create the customers table
CREATE TABLE banking.customers (
    -- Primary identifier
    customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Alternative identifiers
    customer_number VARCHAR(20) UNIQUE NOT NULL,
    
    -- Personal information
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    
    -- Tax/Government ID (encrypted in real scenario)
    tax_id_hash VARCHAR(64),  -- Store hash, not actual SSN
    tax_id_last_four CHAR(4),
    
    -- Contact information
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_primary VARCHAR(20) NOT NULL,
    phone_secondary VARCHAR(20),
    
    -- Address (JSONB for flexibility with international formats)
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state_province VARCHAR(100),
    postal_code VARCHAR(20),
    country_code CHAR(2) DEFAULT 'US',
    
    -- Full address as JSONB for additional details
    address_details JSONB DEFAULT '{}',
    
    -- Account classification
    customer_type banking.customer_type DEFAULT 'individual',
    customer_status banking.customer_status DEFAULT 'pending_verification',
    
    -- KYC Information
    kyc_status banking.kyc_status DEFAULT 'not_started',
    kyc_verified_at TIMESTAMPTZ,
    kyc_expiry_date DATE,
    kyc_documents JSONB DEFAULT '[]',
    
    -- Risk and compliance
    risk_score SMALLINT CHECK (risk_score BETWEEN 0 AND 100),
    pep_status BOOLEAN DEFAULT FALSE,  -- Politically Exposed Person
    
    -- Preferences
    preferred_language CHAR(2) DEFAULT 'en',
    timezone VARCHAR(50) DEFAULT 'America/New_York',
    notification_preferences JSONB DEFAULT '{"email": true, "sms": true, "push": true}',
    
    -- Metadata
    referral_code VARCHAR(20),
    referred_by UUID REFERENCES banking.customers(customer_id),
    
    -- Audit timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT CURRENT_USER,
    
    -- Soft delete
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_at TIMESTAMPTZ
);

-- Create indexes for common queries
CREATE INDEX idx_customers_email ON banking.customers(email);
CREATE INDEX idx_customers_phone ON banking.customers(phone_primary);
CREATE INDEX idx_customers_status ON banking.customers(customer_status) WHERE customer_status = 'active';
CREATE INDEX idx_customers_kyc ON banking.customers(kyc_status) WHERE kyc_status != 'verified';
CREATE INDEX idx_customers_name ON banking.customers(last_name, first_name);

-- Add table comment
COMMENT ON TABLE banking.customers IS 'Core customer profiles for NeoBank - contains PII, handle with care';
COMMENT ON COLUMN banking.customers.tax_id_hash IS 'SHA-256 hash of SSN/Tax ID for verification without storing actual value';
COMMENT ON COLUMN banking.customers.pep_status IS 'Politically Exposed Person flag for enhanced due diligence';
```

---

## Exercise 1.3: Bank Accounts Table 🟢

### Scenario
Create the accounts table to store all bank accounts (checking, savings, money market, etc.). Each customer can have multiple accounts.

### Requirements
1. Support multiple account types
2. Track balance with proper precision for currency
3. Support multiple currencies
4. Track account status and limits
5. Link to customer

### Your Task
Design and create the accounts table.

### Solution

```sql
-- Create account type enum
CREATE TYPE banking.account_type AS ENUM (
    'checking',
    'savings', 
    'money_market',
    'certificate_of_deposit',
    'business_checking',
    'business_savings'
);

CREATE TYPE banking.account_status AS ENUM (
    'pending_activation',
    'active',
    'dormant',
    'frozen',
    'closed'
);

CREATE TYPE banking.currency_code AS ENUM (
    'USD', 'EUR', 'GBP', 'CAD', 'JPY', 'AUD', 'CHF'
);

-- Create accounts table
CREATE TABLE banking.accounts (
    -- Primary identifier
    account_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Human-readable account number (for display)
    account_number VARCHAR(20) UNIQUE NOT NULL,
    
    -- Routing number (for US banks)
    routing_number VARCHAR(9) DEFAULT '021000021',
    
    -- Owner reference
    customer_id UUID NOT NULL REFERENCES banking.customers(customer_id),
    
    -- Account classification
    account_type banking.account_type NOT NULL,
    account_status banking.account_status DEFAULT 'pending_activation',
    
    -- Account name/nickname
    account_name VARCHAR(100),
    
    -- Balance information
    currency banking.currency_code DEFAULT 'USD',
    current_balance NUMERIC(15, 2) DEFAULT 0.00,
    available_balance NUMERIC(15, 2) DEFAULT 0.00,
    pending_balance NUMERIC(15, 2) DEFAULT 0.00,
    
    -- Account limits
    daily_withdrawal_limit NUMERIC(10, 2) DEFAULT 5000.00,
    daily_transfer_limit NUMERIC(10, 2) DEFAULT 25000.00,
    monthly_transaction_limit INTEGER DEFAULT 500,
    
    -- Interest rates (for savings/CD)
    interest_rate NUMERIC(5, 4) DEFAULT 0.0000,  -- e.g., 0.0250 = 2.50%
    apy NUMERIC(5, 4) DEFAULT 0.0000,
    interest_accrued NUMERIC(15, 2) DEFAULT 0.00,
    last_interest_paid_at TIMESTAMPTZ,
    
    -- CD specific fields
    maturity_date DATE,
    term_months SMALLINT,
    
    -- Overdraft settings
    overdraft_enabled BOOLEAN DEFAULT FALSE,
    overdraft_limit NUMERIC(10, 2) DEFAULT 0.00,
    overdraft_linked_account_id UUID,
    
    -- Account features
    is_primary BOOLEAN DEFAULT FALSE,
    allows_wire_transfer BOOLEAN DEFAULT TRUE,
    allows_ach BOOLEAN DEFAULT TRUE,
    allows_check_writing BOOLEAN DEFAULT FALSE,
    
    -- Joint account support
    is_joint_account BOOLEAN DEFAULT FALSE,
    joint_holders UUID[] DEFAULT '{}',
    
    -- Timestamps
    opened_at TIMESTAMPTZ DEFAULT NOW(),
    activated_at TIMESTAMPTZ,
    closed_at TIMESTAMPTZ,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT positive_balance CHECK (
        current_balance >= -overdraft_limit
    ),
    CONSTRAINT valid_interest_rate CHECK (
        interest_rate >= 0 AND interest_rate <= 1
    ),
    CONSTRAINT cd_requires_maturity CHECK (
        (account_type = 'certificate_of_deposit' AND maturity_date IS NOT NULL) OR
        (account_type != 'certificate_of_deposit')
    )
);

-- Foreign key for overdraft linked account
ALTER TABLE banking.accounts
ADD CONSTRAINT fk_overdraft_account 
    FOREIGN KEY (overdraft_linked_account_id) 
    REFERENCES banking.accounts(account_id);

-- Indexes
CREATE INDEX idx_accounts_customer ON banking.accounts(customer_id);
CREATE INDEX idx_accounts_type_status ON banking.accounts(account_type, account_status);
CREATE INDEX idx_accounts_balance ON banking.accounts(current_balance) WHERE account_status = 'active';
CREATE UNIQUE INDEX idx_accounts_primary ON banking.accounts(customer_id) WHERE is_primary = TRUE;

-- Comments
COMMENT ON TABLE banking.accounts IS 'Bank accounts for all NeoBank customers';
COMMENT ON COLUMN banking.accounts.current_balance IS 'Actual balance including pending transactions';
COMMENT ON COLUMN banking.accounts.available_balance IS 'Balance available for withdrawal (excludes holds)';
```

---

## Exercise 1.4: Transactions Table with Partitioning Prep 🟡

### Scenario
Design the transactions table - the heart of the banking system. This table will grow to billions of rows and needs careful design for performance.

### Requirements
1. Record all financial movements (deposits, withdrawals, transfers, fees)
2. Support idempotency for duplicate detection
3. Include metadata for categorization and analytics
4. Design for future partitioning by date
5. Maintain referential integrity

### Your Task
Create a transactions table optimized for high volume.

### Solution

```sql
-- Transaction types
CREATE TYPE banking.transaction_type AS ENUM (
    'deposit',
    'withdrawal',
    'transfer_in',
    'transfer_out',
    'payment',
    'refund',
    'fee',
    'interest',
    'adjustment',
    'wire_in',
    'wire_out',
    'ach_in',
    'ach_out',
    'card_purchase',
    'card_refund',
    'atm_withdrawal',
    'atm_deposit'
);

CREATE TYPE banking.transaction_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'reversed'
);

CREATE TYPE banking.transaction_channel AS ENUM (
    'mobile_app',
    'web',
    'branch',
    'atm',
    'phone',
    'api',
    'scheduled',
    'system'
);

-- Transactions table (designed for partitioning)
CREATE TABLE banking.transactions (
    -- Primary identifier
    transaction_id UUID DEFAULT gen_random_uuid(),
    
    -- Idempotency key (for duplicate prevention)
    idempotency_key VARCHAR(64) NOT NULL,
    
    -- Reference number (human-readable)
    reference_number VARCHAR(30) NOT NULL,
    
    -- Account reference
    account_id UUID NOT NULL,
    
    -- Transaction details
    transaction_type banking.transaction_type NOT NULL,
    transaction_status banking.transaction_status DEFAULT 'pending',
    
    -- Amount (positive for credits, negative for debits)
    amount NUMERIC(15, 2) NOT NULL,
    currency banking.currency_code DEFAULT 'USD',
    
    -- Running balance after this transaction
    balance_after NUMERIC(15, 2),
    
    -- Related transaction (for transfers, reversals)
    related_transaction_id UUID,
    
    -- External references
    external_reference VARCHAR(100),
    
    -- Channel information
    channel banking.transaction_channel NOT NULL,
    
    -- Timestamps (transaction_date is partition key)
    transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    
    -- Description and categorization
    description VARCHAR(255),
    merchant_name VARCHAR(200),
    merchant_category_code VARCHAR(4),
    category VARCHAR(50),
    
    -- Location data (for card transactions)
    location_city VARCHAR(100),
    location_state VARCHAR(50),
    location_country CHAR(2),
    location_coordinates POINT,
    
    -- Metadata for analytics
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    
    -- Fraud detection
    risk_score SMALLINT,
    is_flagged BOOLEAN DEFAULT FALSE,
    flag_reason VARCHAR(255),
    
    -- Audit trail
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by VARCHAR(100) DEFAULT CURRENT_USER,
    
    -- Primary key includes partition key for partitioning
    PRIMARY KEY (transaction_id, transaction_date)
    
) PARTITION BY RANGE (transaction_date);

-- Create partitions for current and upcoming months
CREATE TABLE banking.transactions_2026_01 
    PARTITION OF banking.transactions
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE banking.transactions_2026_02 
    PARTITION OF banking.transactions
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE banking.transactions_2026_03 
    PARTITION OF banking.transactions
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Default partition for any other dates
CREATE TABLE banking.transactions_default 
    PARTITION OF banking.transactions
    DEFAULT;

-- Indexes on partitioned table (created on each partition automatically)
CREATE INDEX idx_transactions_account_date 
    ON banking.transactions(account_id, transaction_date DESC);

CREATE INDEX idx_transactions_status 
    ON banking.transactions(transaction_status) 
    WHERE transaction_status IN ('pending', 'processing');

CREATE INDEX idx_transactions_idempotency 
    ON banking.transactions(idempotency_key);

CREATE INDEX idx_transactions_type_date 
    ON banking.transactions(transaction_type, transaction_date);

CREATE INDEX idx_transactions_flagged 
    ON banking.transactions(is_flagged, transaction_date) 
    WHERE is_flagged = TRUE;

-- Unique constraint for idempotency
CREATE UNIQUE INDEX idx_transactions_idempotency_unique 
    ON banking.transactions(idempotency_key, transaction_date);

-- Comments
COMMENT ON TABLE banking.transactions IS 'All financial transactions - partitioned by transaction_date';
COMMENT ON COLUMN banking.transactions.idempotency_key IS 'Client-provided key to prevent duplicate transactions';
COMMENT ON COLUMN banking.transactions.balance_after IS 'Account balance immediately after this transaction posted';
```

---

## Exercise 1.5: Basic CRUD Operations 🟢

### Scenario
Now that the tables are created, perform basic CRUD operations to add initial data for testing.

### Tasks
1. Insert 5 sample customers
2. Create accounts for each customer
3. Insert some transactions
4. Update customer information
5. Query the data

### Solution

```sql
-- 1. Insert sample customers
INSERT INTO banking.customers (
    customer_number, first_name, last_name, date_of_birth,
    email, phone_primary, city, state_province, postal_code, country_code,
    customer_type, customer_status, kyc_status
) VALUES 
(
    'CUST-2026-00001',
    'John', 'Smith', '1985-03-15',
    'john.smith@email.com', '+1-555-0101',
    'New York', 'NY', '10001', 'US',
    'individual', 'active', 'verified'
),
(
    'CUST-2026-00002',
    'Sarah', 'Johnson', '1990-07-22',
    'sarah.j@email.com', '+1-555-0102',
    'Los Angeles', 'CA', '90001', 'US',
    'individual', 'active', 'verified'
),
(
    'CUST-2026-00003',
    'Michael', 'Chen', '1978-11-08',
    'mchen@email.com', '+1-555-0103',
    'Chicago', 'IL', '60601', 'US',
    'individual', 'active', 'verified'
),
(
    'CUST-2026-00004',
    'Tech Innovations', 'LLC', '2020-01-01',
    'finance@techinnovations.com', '+1-555-0104',
    'San Francisco', 'CA', '94102', 'US',
    'business', 'active', 'verified'
),
(
    'CUST-2026-00005',
    'Emily', 'Rodriguez', '1995-05-30',
    'emily.r@email.com', '+1-555-0105',
    'Miami', 'FL', '33101', 'US',
    'individual', 'pending_verification', 'documents_pending'
);

-- 2. Create accounts for customers
-- First, get customer IDs
WITH customer_ids AS (
    SELECT customer_id, customer_number
    FROM banking.customers
)
INSERT INTO banking.accounts (
    account_number, customer_id, account_type, account_status,
    account_name, current_balance, available_balance, is_primary
)
SELECT 
    'ACC' || SUBSTRING(customer_number FROM 6) || '-CHK',
    customer_id,
    'checking',
    'active',
    'Primary Checking',
    CASE customer_number
        WHEN 'CUST-2026-00001' THEN 5000.00
        WHEN 'CUST-2026-00002' THEN 12500.00
        WHEN 'CUST-2026-00003' THEN 8750.00
        WHEN 'CUST-2026-00004' THEN 150000.00
        WHEN 'CUST-2026-00005' THEN 500.00
    END,
    CASE customer_number
        WHEN 'CUST-2026-00001' THEN 4800.00
        WHEN 'CUST-2026-00002' THEN 12500.00
        WHEN 'CUST-2026-00003' THEN 8750.00
        WHEN 'CUST-2026-00004' THEN 148000.00
        WHEN 'CUST-2026-00005' THEN 500.00
    END,
    TRUE
FROM customer_ids;

-- Add savings accounts for some customers
INSERT INTO banking.accounts (
    account_number, customer_id, account_type, account_status,
    account_name, current_balance, available_balance, interest_rate, apy
)
SELECT 
    'ACC' || SUBSTRING(customer_number FROM 6) || '-SAV',
    customer_id,
    'savings',
    'active',
    'High-Yield Savings',
    CASE customer_number
        WHEN 'CUST-2026-00001' THEN 15000.00
        WHEN 'CUST-2026-00002' THEN 25000.00
        WHEN 'CUST-2026-00003' THEN 50000.00
    END,
    CASE customer_number
        WHEN 'CUST-2026-00001' THEN 15000.00
        WHEN 'CUST-2026-00002' THEN 25000.00
        WHEN 'CUST-2026-00003' THEN 50000.00
    END,
    0.0425,
    0.0434
FROM banking.customers
WHERE customer_number IN ('CUST-2026-00001', 'CUST-2026-00002', 'CUST-2026-00003');

-- 3. Insert transactions
INSERT INTO banking.transactions (
    idempotency_key, reference_number, account_id, transaction_type,
    transaction_status, amount, channel, description, transaction_date
)
SELECT 
    'TXN-' || gen_random_uuid()::text,
    'REF-2026-' || LPAD((ROW_NUMBER() OVER())::text, 6, '0'),
    a.account_id,
    t.txn_type,
    'completed',
    t.amount,
    t.channel,
    t.description,
    t.txn_date
FROM banking.accounts a
CROSS JOIN (
    VALUES 
        ('deposit'::banking.transaction_type, 1000.00, 'mobile_app'::banking.transaction_channel, 'Mobile deposit', '2026-01-15'::date),
        ('card_purchase'::banking.transaction_type, -45.99, 'mobile_app'::banking.transaction_channel, 'Amazon.com purchase', '2026-01-16'::date),
        ('transfer_out'::banking.transaction_type, -200.00, 'web'::banking.transaction_channel, 'Transfer to savings', '2026-01-17'::date),
        ('atm_withdrawal'::banking.transaction_type, -100.00, 'atm'::banking.transaction_channel, 'ATM Withdrawal', '2026-01-18'::date)
) AS t(txn_type, amount, channel, description, txn_date)
WHERE a.account_type = 'checking'
LIMIT 20;

-- 4. Update customer information
UPDATE banking.customers
SET 
    phone_secondary = '+1-555-9999',
    address_details = jsonb_build_object(
        'apartment', '4B',
        'building_name', 'Skyview Tower',
        'delivery_instructions', 'Leave with doorman'
    ),
    updated_at = NOW()
WHERE customer_number = 'CUST-2026-00001';

-- 5. Query the data
-- List all customers with their account counts
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS full_name,
    c.customer_status,
    c.kyc_status,
    COUNT(a.account_id) AS account_count,
    SUM(a.current_balance) AS total_balance
FROM banking.customers c
LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id
ORDER BY total_balance DESC NULLS LAST;

-- Recent transactions for a customer
SELECT 
    t.reference_number,
    t.transaction_type,
    t.amount,
    t.description,
    t.transaction_date,
    a.account_number
FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE c.customer_number = 'CUST-2026-00001'
ORDER BY t.transaction_date DESC, t.initiated_at DESC
LIMIT 10;
```

---

## Exercise 1.6: Data Validation Queries 🟢

### Scenario
Write queries to validate data integrity and find potential issues in the data.

### Tasks
1. Find customers without any accounts
2. Find accounts with negative available balance (potential overdraft)
3. Identify transactions without matching accounts
4. Check for duplicate customer emails

### Solution

```sql
-- 1. Customers without accounts
SELECT 
    c.customer_number,
    c.first_name || ' ' || c.last_name AS full_name,
    c.customer_status,
    c.created_at
FROM banking.customers c
LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
WHERE a.account_id IS NULL
ORDER BY c.created_at;

-- 2. Accounts with negative available balance
SELECT 
    a.account_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    a.account_type,
    a.current_balance,
    a.available_balance,
    a.overdraft_enabled,
    a.overdraft_limit,
    CASE 
        WHEN a.available_balance < 0 AND NOT a.overdraft_enabled 
        THEN 'ALERT: Negative balance without overdraft'
        WHEN a.available_balance < -a.overdraft_limit 
        THEN 'ALERT: Exceeded overdraft limit'
        ELSE 'OK'
    END AS status_check
FROM banking.accounts a
JOIN banking.customers c ON a.customer_id = c.customer_id
WHERE a.available_balance < 0
ORDER BY a.available_balance;

-- 3. Orphan transactions (shouldn't exist with FK, but good to check)
SELECT 
    t.transaction_id,
    t.reference_number,
    t.account_id,
    t.amount
FROM banking.transactions t
LEFT JOIN banking.accounts a ON t.account_id = a.account_id
WHERE a.account_id IS NULL;

-- 4. Duplicate emails (constraint should prevent, but validate)
SELECT 
    email,
    COUNT(*) as count,
    array_agg(customer_number) as customer_numbers
FROM banking.customers
GROUP BY email
HAVING COUNT(*) > 1;

-- 5. Data quality summary
SELECT 
    'Total Customers' as metric,
    COUNT(*)::text as value
FROM banking.customers
UNION ALL
SELECT 
    'Active Customers',
    COUNT(*)::text
FROM banking.customers
WHERE customer_status = 'active'
UNION ALL
SELECT 
    'Total Accounts',
    COUNT(*)::text
FROM banking.accounts
UNION ALL
SELECT 
    'Total Balance (USD)',
    TO_CHAR(SUM(current_balance), 'FM$999,999,999.00')
FROM banking.accounts
WHERE currency = 'USD'
UNION ALL
SELECT 
    'Total Transactions',
    COUNT(*)::text
FROM banking.transactions;
```

---

## 🎯 Practice Challenges

### Challenge 1.1
Create a table for `banking.cards` (debit/credit cards) linked to accounts with proper card number masking.

### Challenge 1.2
Write a query to generate the next sequential customer number in format `CUST-YYYY-NNNNN`.

### Challenge 1.3
Create a function that calculates the account balance from the sum of all transactions.

---

**Next: [Part 2 - Database Design Exercises](02-database-design-exercises.md)**
