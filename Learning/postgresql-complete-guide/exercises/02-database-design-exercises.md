# Part 2: Database Design Exercises

## Topics Covered
- Database Design Principles (Chapter 6)
- Normalization (Chapter 7)
- Constraints and Keys (Chapter 8)
- Indexes (Chapter 9)
- Views (Chapter 10)

---

## Exercise 2.1: Normalize the Lending Schema 🟡

### Scenario
The lending team has provided a denormalized spreadsheet of loan data. Your task is to normalize this into a proper relational structure that follows 3NF.

### Current Denormalized Data (What they gave you)
```
loan_id | customer_name | customer_email | loan_type | loan_type_desc | rate | term | amount | payment | payment_date | payment_amount | collateral_type | collateral_value
```

### Requirements
1. Normalize to Third Normal Form (3NF)
2. Create appropriate lookup/reference tables
3. Support multiple payments per loan
4. Support multiple collaterals per loan
5. Track loan status changes over time

### Solution

```sql
-- Step 1: Create reference/lookup tables (eliminates transitive dependencies)

-- Loan types (1NF violation fix - repeating loan_type_desc for same loan_type)
CREATE TABLE lending.loan_types (
    loan_type_id SERIAL PRIMARY KEY,
    loan_type_code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(200) NOT NULL,
    min_term_months SMALLINT NOT NULL,
    max_term_months SMALLINT NOT NULL,
    min_amount NUMERIC(12, 2) NOT NULL,
    max_amount NUMERIC(12, 2) NOT NULL,
    base_rate NUMERIC(5, 4) NOT NULL,
    requires_collateral BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Insert loan types
INSERT INTO lending.loan_types (
    loan_type_code, description, min_term_months, max_term_months,
    min_amount, max_amount, base_rate, requires_collateral
) VALUES
    ('PERSONAL', 'Personal Loan', 12, 60, 1000, 50000, 0.0899, FALSE),
    ('AUTO', 'Auto Loan', 24, 84, 5000, 100000, 0.0599, TRUE),
    ('MORTGAGE', 'Home Mortgage', 180, 360, 50000, 2000000, 0.0649, TRUE),
    ('HOME_EQUITY', 'Home Equity Line of Credit', 60, 240, 10000, 500000, 0.0749, TRUE),
    ('BUSINESS', 'Small Business Loan', 12, 120, 10000, 500000, 0.0799, FALSE),
    ('STUDENT', 'Student Loan', 60, 240, 1000, 150000, 0.0499, FALSE);

-- Collateral types
CREATE TABLE lending.collateral_types (
    collateral_type_id SERIAL PRIMARY KEY,
    type_code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL,
    valuation_frequency_months SMALLINT DEFAULT 12,
    ltv_max_percent NUMERIC(5, 2) DEFAULT 80.00
);

INSERT INTO lending.collateral_types (type_code, description, ltv_max_percent) VALUES
    ('VEHICLE', 'Motor Vehicle', 85.00),
    ('REAL_ESTATE', 'Real Estate Property', 80.00),
    ('SECURITIES', 'Stocks and Bonds', 70.00),
    ('EQUIPMENT', 'Business Equipment', 75.00),
    ('INVENTORY', 'Business Inventory', 50.00),
    ('CASH', 'Cash/CD Collateral', 100.00);

-- Loan statuses
CREATE TABLE lending.loan_statuses (
    status_id SERIAL PRIMARY KEY,
    status_code VARCHAR(20) UNIQUE NOT NULL,
    description VARCHAR(100) NOT NULL,
    is_active_loan BOOLEAN DEFAULT TRUE,
    allows_payments BOOLEAN DEFAULT TRUE
);

INSERT INTO lending.loan_statuses (status_code, description, is_active_loan, allows_payments) VALUES
    ('APPLIED', 'Application Submitted', FALSE, FALSE),
    ('UNDER_REVIEW', 'Under Review', FALSE, FALSE),
    ('APPROVED', 'Approved - Pending Disbursement', FALSE, FALSE),
    ('ACTIVE', 'Active Loan', TRUE, TRUE),
    ('DELINQUENT', 'Payment Delinquent', TRUE, TRUE),
    ('DEFAULT', 'In Default', TRUE, TRUE),
    ('PAID_OFF', 'Paid in Full', FALSE, FALSE),
    ('CLOSED', 'Closed', FALSE, FALSE),
    ('REJECTED', 'Application Rejected', FALSE, FALSE);

-- Step 2: Create the normalized loans table (2NF - remove partial dependencies)

CREATE TABLE lending.loans (
    loan_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_number VARCHAR(20) UNIQUE NOT NULL,
    
    -- Customer reference (FK to banking.customers)
    customer_id UUID NOT NULL REFERENCES banking.customers(customer_id),
    
    -- Loan type reference (normalized - no more loan_type_desc in this table)
    loan_type_id INTEGER NOT NULL REFERENCES lending.loan_types(loan_type_id),
    
    -- Current status
    status_id INTEGER NOT NULL REFERENCES lending.loan_statuses(status_id),
    
    -- Loan terms
    principal_amount NUMERIC(12, 2) NOT NULL,
    interest_rate NUMERIC(5, 4) NOT NULL,
    term_months SMALLINT NOT NULL,
    
    -- Calculated fields (stored for performance)
    monthly_payment NUMERIC(10, 2) NOT NULL,
    total_interest NUMERIC(12, 2),
    
    -- Outstanding balances
    principal_balance NUMERIC(12, 2),
    interest_balance NUMERIC(12, 2),
    fees_balance NUMERIC(10, 2) DEFAULT 0,
    
    -- Important dates
    application_date DATE NOT NULL DEFAULT CURRENT_DATE,
    approval_date DATE,
    disbursement_date DATE,
    first_payment_date DATE,
    maturity_date DATE,
    
    -- Payment tracking
    next_payment_date DATE,
    last_payment_date DATE,
    payments_made INTEGER DEFAULT 0,
    payments_remaining INTEGER,
    
    -- Delinquency tracking
    days_past_due SMALLINT DEFAULT 0,
    times_delinquent SMALLINT DEFAULT 0,
    
    -- Disbursement details
    disbursement_account_id UUID REFERENCES banking.accounts(account_id),
    payment_account_id UUID REFERENCES banking.accounts(account_id),
    
    -- Metadata
    purpose VARCHAR(200),
    notes TEXT,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    CONSTRAINT valid_rate CHECK (interest_rate >= 0 AND interest_rate < 1),
    CONSTRAINT valid_term CHECK (term_months > 0),
    CONSTRAINT valid_amount CHECK (principal_amount > 0)
);

-- Step 3: Loan payments table (fixes 1NF - no repeating payment groups)

CREATE TYPE lending.payment_type AS ENUM (
    'regular',
    'extra_principal',
    'payoff',
    'late_fee',
    'nsf_fee',
    'refund'
);

CREATE TYPE lending.payment_status AS ENUM (
    'scheduled',
    'pending',
    'processing',
    'completed',
    'failed',
    'reversed'
);

CREATE TABLE lending.loan_payments (
    payment_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES lending.loans(loan_id),
    
    -- Payment details
    payment_number INTEGER NOT NULL,
    payment_type lending.payment_type DEFAULT 'regular',
    payment_status lending.payment_status DEFAULT 'pending',
    
    -- Amounts
    payment_amount NUMERIC(10, 2) NOT NULL,
    principal_amount NUMERIC(10, 2) NOT NULL,
    interest_amount NUMERIC(10, 2) NOT NULL,
    fees_amount NUMERIC(10, 2) DEFAULT 0,
    
    -- Balances after payment
    principal_balance_after NUMERIC(12, 2),
    
    -- Dates
    due_date DATE NOT NULL,
    scheduled_date DATE,
    paid_date TIMESTAMPTZ,
    
    -- Payment method
    payment_method VARCHAR(20),
    source_account_id UUID REFERENCES banking.accounts(account_id),
    transaction_id UUID,
    
    -- Late payment tracking
    days_late SMALLINT DEFAULT 0,
    late_fee_applied NUMERIC(10, 2) DEFAULT 0,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    CONSTRAINT unique_loan_payment UNIQUE (loan_id, payment_number)
);

-- Step 4: Collateral table (fixes 1NF - multiple collaterals per loan)

CREATE TABLE lending.loan_collateral (
    collateral_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    loan_id UUID NOT NULL REFERENCES lending.loans(loan_id),
    collateral_type_id INTEGER NOT NULL REFERENCES lending.collateral_types(collateral_type_id),
    
    -- Collateral details
    description TEXT NOT NULL,
    
    -- Valuation
    original_value NUMERIC(12, 2) NOT NULL,
    current_value NUMERIC(12, 2) NOT NULL,
    last_valuation_date DATE DEFAULT CURRENT_DATE,
    next_valuation_date DATE,
    
    -- For vehicles
    vin VARCHAR(17),
    make VARCHAR(50),
    model VARCHAR(50),
    year SMALLINT,
    
    -- For real estate
    property_address TEXT,
    parcel_number VARCHAR(50),
    
    -- For securities
    security_type VARCHAR(50),
    cusip VARCHAR(9),
    shares NUMERIC(15, 4),
    
    -- Status
    is_primary BOOLEAN DEFAULT TRUE,
    is_released BOOLEAN DEFAULT FALSE,
    released_date DATE,
    
    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Step 5: Loan status history (temporal tracking)

CREATE TABLE lending.loan_status_history (
    history_id SERIAL PRIMARY KEY,
    loan_id UUID NOT NULL REFERENCES lending.loans(loan_id),
    
    old_status_id INTEGER REFERENCES lending.loan_statuses(status_id),
    new_status_id INTEGER NOT NULL REFERENCES lending.loan_statuses(status_id),
    
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,
    reason VARCHAR(500),
    
    CONSTRAINT status_change CHECK (
        old_status_id IS NULL OR old_status_id != new_status_id
    )
);

-- Indexes for the lending schema
CREATE INDEX idx_loans_customer ON lending.loans(customer_id);
CREATE INDEX idx_loans_status ON lending.loans(status_id);
CREATE INDEX idx_loans_type ON lending.loans(loan_type_id);
CREATE INDEX idx_loans_next_payment ON lending.loans(next_payment_date) WHERE status_id IN (SELECT status_id FROM lending.loan_statuses WHERE is_active_loan);
CREATE INDEX idx_loans_delinquent ON lending.loans(days_past_due) WHERE days_past_due > 0;

CREATE INDEX idx_payments_loan ON lending.loan_payments(loan_id);
CREATE INDEX idx_payments_due_date ON lending.loan_payments(due_date);
CREATE INDEX idx_payments_status ON lending.loan_payments(payment_status) WHERE payment_status IN ('scheduled', 'pending');

CREATE INDEX idx_collateral_loan ON lending.loan_collateral(loan_id);
CREATE INDEX idx_status_history_loan ON lending.loan_status_history(loan_id);
```

---

## Exercise 2.2: Design Constraints for Data Integrity 🟡

### Scenario
Add comprehensive constraints to ensure data integrity across the NeoBank database. These constraints should catch business rule violations at the database level.

### Requirements
1. Ensure loan amounts are within product limits
2. Prevent accounts from going below overdraft limits
3. Ensure transaction dates are not in the future
4. Validate email and phone formats
5. Create domain types for reusable constraints

### Solution

```sql
-- Create reusable domains with constraints

-- Email domain
CREATE DOMAIN banking.email_address AS VARCHAR(255)
    CHECK (VALUE ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$');

-- Phone domain (E.164 format)
CREATE DOMAIN banking.phone_number AS VARCHAR(20)
    CHECK (VALUE ~ '^\+?[1-9]\d{1,14}$');

-- Positive money domain
CREATE DOMAIN banking.positive_money AS NUMERIC(15, 2)
    CHECK (VALUE >= 0);

-- Percentage domain (0-100)
CREATE DOMAIN banking.percentage AS NUMERIC(5, 2)
    CHECK (VALUE >= 0 AND VALUE <= 100);

-- Interest rate domain (0-1 as decimal)
CREATE DOMAIN banking.interest_rate AS NUMERIC(6, 5)
    CHECK (VALUE >= 0 AND VALUE <= 1);

-- Complex constraint function: Validate loan against product limits
CREATE OR REPLACE FUNCTION lending.validate_loan_limits()
RETURNS TRIGGER AS $$
DECLARE
    v_loan_type lending.loan_types%ROWTYPE;
BEGIN
    -- Get loan type configuration
    SELECT * INTO v_loan_type
    FROM lending.loan_types
    WHERE loan_type_id = NEW.loan_type_id;
    
    -- Check amount limits
    IF NEW.principal_amount < v_loan_type.min_amount THEN
        RAISE EXCEPTION 'Loan amount % is below minimum % for loan type %',
            NEW.principal_amount, v_loan_type.min_amount, v_loan_type.loan_type_code;
    END IF;
    
    IF NEW.principal_amount > v_loan_type.max_amount THEN
        RAISE EXCEPTION 'Loan amount % exceeds maximum % for loan type %',
            NEW.principal_amount, v_loan_type.max_amount, v_loan_type.loan_type_code;
    END IF;
    
    -- Check term limits
    IF NEW.term_months < v_loan_type.min_term_months THEN
        RAISE EXCEPTION 'Loan term % months is below minimum % for loan type %',
            NEW.term_months, v_loan_type.min_term_months, v_loan_type.loan_type_code;
    END IF;
    
    IF NEW.term_months > v_loan_type.max_term_months THEN
        RAISE EXCEPTION 'Loan term % months exceeds maximum % for loan type %',
            NEW.term_months, v_loan_type.max_term_months, v_loan_type.loan_type_code;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_loan_limits
    BEFORE INSERT OR UPDATE ON lending.loans
    FOR EACH ROW
    EXECUTE FUNCTION lending.validate_loan_limits();

-- Constraint function: Prevent future transaction dates
CREATE OR REPLACE FUNCTION banking.check_transaction_date()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.transaction_date > CURRENT_DATE THEN
        RAISE EXCEPTION 'Transaction date % cannot be in the future', NEW.transaction_date;
    END IF;
    
    -- Don't allow transactions more than 7 days in the past for new entries
    IF TG_OP = 'INSERT' AND NEW.transaction_date < CURRENT_DATE - INTERVAL '7 days' THEN
        RAISE EXCEPTION 'Transaction date % is too far in the past. Max backdating is 7 days.', 
            NEW.transaction_date;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_transaction_date
    BEFORE INSERT OR UPDATE ON banking.transactions
    FOR EACH ROW
    EXECUTE FUNCTION banking.check_transaction_date();

-- Constraint: Account balance with overdraft
ALTER TABLE banking.accounts
    ADD CONSTRAINT chk_balance_overdraft 
    CHECK (
        current_balance >= -overdraft_limit
    );

-- Constraint: Transfer must have valid source and destination
CREATE OR REPLACE FUNCTION banking.validate_transfer()
RETURNS TRIGGER AS $$
BEGIN
    -- For transfer_out, there should be a corresponding transfer_in
    IF NEW.transaction_type = 'transfer_out' AND NEW.related_transaction_id IS NULL THEN
        RAISE WARNING 'Transfer out % should have a related transaction', NEW.transaction_id;
    END IF;
    
    -- Cannot transfer to same account
    IF NEW.related_transaction_id IS NOT NULL THEN
        DECLARE
            v_related_account_id UUID;
        BEGIN
            SELECT account_id INTO v_related_account_id
            FROM banking.transactions
            WHERE transaction_id = NEW.related_transaction_id;
            
            IF v_related_account_id = NEW.account_id THEN
                RAISE EXCEPTION 'Cannot transfer to the same account';
            END IF;
        EXCEPTION
            WHEN NO_DATA_FOUND THEN
                -- Related transaction doesn't exist yet, skip validation
                NULL;
        END;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Constraint: Ensure collateral value meets LTV requirements
CREATE OR REPLACE FUNCTION lending.validate_collateral_ltv()
RETURNS TRIGGER AS $$
DECLARE
    v_loan_amount NUMERIC;
    v_total_collateral_value NUMERIC;
    v_required_ltv NUMERIC;
    v_actual_ltv NUMERIC;
BEGIN
    -- Get loan amount
    SELECT principal_amount INTO v_loan_amount
    FROM lending.loans
    WHERE loan_id = NEW.loan_id;
    
    -- Get total collateral value including this one
    SELECT COALESCE(SUM(current_value), 0) + NEW.current_value
    INTO v_total_collateral_value
    FROM lending.loan_collateral
    WHERE loan_id = NEW.loan_id
      AND collateral_id != COALESCE(NEW.collateral_id, gen_random_uuid());
    
    -- Get required LTV for this collateral type
    SELECT ltv_max_percent INTO v_required_ltv
    FROM lending.collateral_types
    WHERE collateral_type_id = NEW.collateral_type_id;
    
    -- Calculate actual LTV
    v_actual_ltv := (v_loan_amount / NULLIF(v_total_collateral_value, 0)) * 100;
    
    -- Warn if LTV exceeds limit (but don't prevent - might have multiple collaterals)
    IF v_actual_ltv > v_required_ltv THEN
        RAISE WARNING 'Current LTV of %.2f%% exceeds limit of %.2f%% for collateral type. Consider additional collateral.',
            v_actual_ltv, v_required_ltv;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_validate_collateral_ltv
    AFTER INSERT OR UPDATE ON lending.loan_collateral
    FOR EACH ROW
    EXECUTE FUNCTION lending.validate_collateral_ltv();

-- Add exclusion constraint: No overlapping active loans of same type per customer
-- (Customer can't have two active personal loans simultaneously)
ALTER TABLE lending.loans
    ADD CONSTRAINT excl_one_active_loan_per_type
    EXCLUDE USING gist (
        customer_id WITH =,
        loan_type_id WITH =,
        tsrange(disbursement_date::timestamp, COALESCE(maturity_date::timestamp, 'infinity')) WITH &&
    )
    WHERE (status_id IN (SELECT status_id FROM lending.loan_statuses WHERE is_active_loan));

-- Note: Requires btree_gist extension
-- CREATE EXTENSION IF NOT EXISTS btree_gist;
```

---

## Exercise 2.3: Create Strategic Indexes 🟡

### Scenario
The NeoBank application is experiencing slow queries. Analyze common query patterns and create appropriate indexes.

### Common Query Patterns
1. Find customer by email or phone
2. Get all transactions for an account in date range
3. Find delinquent loans with customer info
4. Search transactions by merchant name
5. Get account balance history

### Solution

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- For text search
CREATE EXTENSION IF NOT EXISTS btree_gist;  -- For exclusion constraints

-- 1. Customer lookup indexes
-- Email lookup (already exists, ensure it's optimal)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_customers_email_lower 
    ON banking.customers (LOWER(email));

-- Phone lookup with partial index for active customers
CREATE INDEX CONCURRENTLY idx_customers_phone_active 
    ON banking.customers (phone_primary)
    WHERE customer_status = 'active' AND is_deleted = FALSE;

-- Name search with trigram for fuzzy matching
CREATE INDEX CONCURRENTLY idx_customers_name_trgm 
    ON banking.customers 
    USING GIN ((first_name || ' ' || last_name) gin_trgm_ops);

-- 2. Transaction indexes for account queries
-- Composite index for account + date range (most common query)
CREATE INDEX CONCURRENTLY idx_transactions_account_date_desc
    ON banking.transactions (account_id, transaction_date DESC, initiated_at DESC)
    INCLUDE (amount, transaction_type, description);

-- Covering index for transaction summaries
CREATE INDEX CONCURRENTLY idx_transactions_summary
    ON banking.transactions (account_id, transaction_type)
    INCLUDE (amount, transaction_status)
    WHERE transaction_status = 'completed';

-- 3. Loan delinquency indexes
CREATE INDEX CONCURRENTLY idx_loans_delinquent_with_customer
    ON lending.loans (customer_id, days_past_due DESC)
    WHERE days_past_due > 0;

-- Index for loan status with common statuses partial indexed
CREATE INDEX CONCURRENTLY idx_loans_active_status
    ON lending.loans (status_id, next_payment_date)
    WHERE status_id IN (4, 5);  -- ACTIVE, DELINQUENT

-- 4. Merchant search for transactions
CREATE INDEX CONCURRENTLY idx_transactions_merchant_trgm
    ON banking.transactions
    USING GIN (merchant_name gin_trgm_ops)
    WHERE merchant_name IS NOT NULL;

-- Category search
CREATE INDEX CONCURRENTLY idx_transactions_category
    ON banking.transactions (category)
    WHERE category IS NOT NULL;

-- 5. Balance history (using transaction balance_after)
CREATE INDEX CONCURRENTLY idx_transactions_balance_history
    ON banking.transactions (account_id, transaction_date, initiated_at)
    INCLUDE (balance_after)
    WHERE balance_after IS NOT NULL;

-- Additional strategic indexes

-- Pending transactions (hot data)
CREATE INDEX CONCURRENTLY idx_transactions_pending
    ON banking.transactions (transaction_status, initiated_at)
    WHERE transaction_status IN ('pending', 'processing');

-- Flagged transactions for fraud review
CREATE INDEX CONCURRENTLY idx_transactions_flagged_review
    ON banking.transactions (risk_score DESC, initiated_at DESC)
    WHERE is_flagged = TRUE;

-- Payment due dates for loan servicing
CREATE INDEX CONCURRENTLY idx_payments_upcoming
    ON lending.loan_payments (due_date)
    INCLUDE (loan_id, payment_amount)
    WHERE payment_status = 'scheduled' 
      AND due_date >= CURRENT_DATE;

-- Expression index for age-based queries
CREATE INDEX CONCURRENTLY idx_customers_age
    ON banking.customers (
        EXTRACT(YEAR FROM AGE(CURRENT_DATE, date_of_birth))
    );

-- JSONB index for notification preferences
CREATE INDEX CONCURRENTLY idx_customers_notifications
    ON banking.customers 
    USING GIN (notification_preferences jsonb_path_ops);

-- Analyze index usage query
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch,
    pg_size_pretty(pg_relation_size(indexrelid)) as index_size
FROM pg_stat_user_indexes
WHERE schemaname IN ('banking', 'lending')
ORDER BY idx_scan DESC;

-- Find unused indexes
SELECT 
    schemaname || '.' || tablename as table,
    indexname,
    idx_scan,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND schemaname IN ('banking', 'lending')
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Exercise 2.4: Create Useful Views 🟡

### Scenario
Create views to simplify common queries and provide abstraction layers for the application.

### Requirements
1. Customer summary view with account totals
2. Transaction history view with readable formats
3. Loan portfolio view with calculated fields
4. Delinquent accounts view for collections

### Solution

```sql
-- 1. Customer Summary View
CREATE OR REPLACE VIEW banking.v_customer_summary AS
SELECT 
    c.customer_id,
    c.customer_number,
    c.first_name || ' ' || c.last_name AS full_name,
    c.email,
    c.phone_primary,
    c.customer_type,
    c.customer_status,
    c.kyc_status,
    c.created_at AS member_since,
    
    -- Account statistics
    COUNT(DISTINCT a.account_id) AS total_accounts,
    COUNT(DISTINCT a.account_id) FILTER (WHERE a.account_status = 'active') AS active_accounts,
    
    -- Balance summary
    COALESCE(SUM(a.current_balance) FILTER (WHERE a.account_type IN ('checking', 'savings', 'money_market')), 0) AS total_deposits,
    COALESCE(SUM(a.current_balance) FILTER (WHERE a.account_type = 'checking'), 0) AS checking_balance,
    COALESCE(SUM(a.current_balance) FILTER (WHERE a.account_type = 'savings'), 0) AS savings_balance,
    
    -- Loan summary
    COUNT(DISTINCT l.loan_id) AS total_loans,
    COALESCE(SUM(l.principal_balance), 0) AS total_loan_balance,
    
    -- Activity
    MAX(t.initiated_at) AS last_transaction_date,
    COUNT(DISTINCT t.transaction_id) FILTER (
        WHERE t.transaction_date >= CURRENT_DATE - INTERVAL '30 days'
    ) AS transactions_last_30_days

FROM banking.customers c
LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
LEFT JOIN lending.loans l ON c.customer_id = l.customer_id 
    AND l.status_id IN (SELECT status_id FROM lending.loan_statuses WHERE is_active_loan)
LEFT JOIN banking.transactions t ON a.account_id = t.account_id
WHERE c.is_deleted = FALSE
GROUP BY c.customer_id;

COMMENT ON VIEW banking.v_customer_summary IS 'Comprehensive customer view with account and loan summaries';

-- 2. Transaction History View (human-readable)
CREATE OR REPLACE VIEW banking.v_transaction_history AS
SELECT 
    t.transaction_id,
    t.reference_number,
    t.transaction_date,
    t.initiated_at,
    
    -- Account info
    a.account_number,
    a.account_type::text AS account_type,
    
    -- Customer info
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    
    -- Transaction details
    t.transaction_type::text AS transaction_type,
    CASE t.transaction_type
        WHEN 'deposit' THEN 'Deposit'
        WHEN 'withdrawal' THEN 'Withdrawal'
        WHEN 'transfer_in' THEN 'Transfer Received'
        WHEN 'transfer_out' THEN 'Transfer Sent'
        WHEN 'card_purchase' THEN 'Card Purchase'
        WHEN 'atm_withdrawal' THEN 'ATM Withdrawal'
        WHEN 'fee' THEN 'Fee'
        WHEN 'interest' THEN 'Interest Credit'
        ELSE INITCAP(REPLACE(t.transaction_type::text, '_', ' '))
    END AS transaction_type_display,
    
    t.transaction_status::text AS status,
    
    -- Amounts with formatting
    t.amount,
    t.currency::text AS currency,
    CASE 
        WHEN t.amount >= 0 THEN '+' || TO_CHAR(t.amount, 'FM$999,999,999.00')
        ELSE TO_CHAR(t.amount, 'FM$999,999,999.00')
    END AS amount_display,
    t.balance_after,
    
    -- Description
    COALESCE(t.description, t.merchant_name, t.transaction_type::text) AS description,
    t.merchant_name,
    t.category,
    
    -- Channel
    t.channel::text AS channel,
    
    -- Location
    CASE 
        WHEN t.location_city IS NOT NULL 
        THEN t.location_city || ', ' || COALESCE(t.location_state, t.location_country)
        ELSE NULL
    END AS location,
    
    -- Flags
    t.is_flagged,
    t.risk_score

FROM banking.transactions t
JOIN banking.accounts a ON t.account_id = a.account_id
JOIN banking.customers c ON a.customer_id = c.customer_id
ORDER BY t.transaction_date DESC, t.initiated_at DESC;

-- 3. Loan Portfolio View
CREATE OR REPLACE VIEW lending.v_loan_portfolio AS
SELECT 
    l.loan_id,
    l.loan_number,
    
    -- Customer
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.email AS customer_email,
    
    -- Loan type
    lt.loan_type_code,
    lt.description AS loan_type_description,
    
    -- Status
    ls.status_code AS loan_status,
    ls.description AS status_description,
    ls.is_active_loan,
    
    -- Amounts
    l.principal_amount AS original_principal,
    l.interest_rate,
    l.interest_rate * 100 AS interest_rate_percent,
    l.term_months,
    l.monthly_payment,
    
    -- Current balances
    l.principal_balance,
    l.interest_balance,
    l.fees_balance,
    l.principal_balance + COALESCE(l.interest_balance, 0) + COALESCE(l.fees_balance, 0) AS total_balance_due,
    
    -- Progress
    ROUND(
        ((l.principal_amount - COALESCE(l.principal_balance, 0)) / NULLIF(l.principal_amount, 0)) * 100, 
        2
    ) AS percent_paid_off,
    l.payments_made,
    l.payments_remaining,
    
    -- Dates
    l.application_date,
    l.approval_date,
    l.disbursement_date,
    l.maturity_date,
    l.next_payment_date,
    l.last_payment_date,
    
    -- Delinquency
    l.days_past_due,
    l.times_delinquent,
    CASE 
        WHEN l.days_past_due = 0 THEN 'Current'
        WHEN l.days_past_due BETWEEN 1 AND 30 THEN '1-30 Days Past Due'
        WHEN l.days_past_due BETWEEN 31 AND 60 THEN '31-60 Days Past Due'
        WHEN l.days_past_due BETWEEN 61 AND 90 THEN '61-90 Days Past Due'
        ELSE '90+ Days Past Due'
    END AS delinquency_bucket,
    
    -- Collateral (if any)
    (
        SELECT COALESCE(SUM(current_value), 0)
        FROM lending.loan_collateral lc
        WHERE lc.loan_id = l.loan_id AND NOT lc.is_released
    ) AS total_collateral_value,
    
    -- Calculated LTV
    CASE 
        WHEN EXISTS (SELECT 1 FROM lending.loan_collateral lc WHERE lc.loan_id = l.loan_id)
        THEN ROUND(
            (l.principal_balance / NULLIF(
                (SELECT SUM(current_value) FROM lending.loan_collateral lc 
                 WHERE lc.loan_id = l.loan_id AND NOT lc.is_released), 0
            )) * 100, 2
        )
        ELSE NULL
    END AS current_ltv

FROM lending.loans l
JOIN banking.customers c ON l.customer_id = c.customer_id
JOIN lending.loan_types lt ON l.loan_type_id = lt.loan_type_id
JOIN lending.loan_statuses ls ON l.status_id = ls.status_id;

-- 4. Collections View (Delinquent Accounts)
CREATE OR REPLACE VIEW lending.v_collections_queue AS
SELECT 
    l.loan_id,
    l.loan_number,
    
    -- Customer contact info
    c.customer_number,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.phone_primary,
    c.phone_secondary,
    c.email,
    
    -- Address
    c.address_line1 || COALESCE(', ' || c.address_line2, '') AS street_address,
    c.city || ', ' || c.state_province || ' ' || c.postal_code AS city_state_zip,
    
    -- Loan info
    lt.loan_type_code,
    l.monthly_payment,
    
    -- Delinquency details
    l.days_past_due,
    CASE 
        WHEN l.days_past_due BETWEEN 1 AND 30 THEN 1
        WHEN l.days_past_due BETWEEN 31 AND 60 THEN 2
        WHEN l.days_past_due BETWEEN 61 AND 90 THEN 3
        ELSE 4
    END AS collection_priority,
    
    -- Amount past due (simplified - actual would calculate missed payments)
    CEIL(l.days_past_due / 30.0) * l.monthly_payment AS estimated_past_due_amount,
    
    l.principal_balance + COALESCE(l.interest_balance, 0) + COALESCE(l.fees_balance, 0) AS total_balance,
    
    -- Payment history
    l.last_payment_date,
    l.times_delinquent AS historical_delinquencies,
    
    -- Risk assessment
    c.risk_score AS customer_risk_score,
    
    -- Collateral for secured loans
    (
        SELECT STRING_AGG(
            ct.description || ': $' || TO_CHAR(lc.current_value, 'FM999,999,999'), 
            '; '
        )
        FROM lending.loan_collateral lc
        JOIN lending.collateral_types ct ON lc.collateral_type_id = ct.collateral_type_id
        WHERE lc.loan_id = l.loan_id AND NOT lc.is_released
    ) AS collateral_summary

FROM lending.loans l
JOIN banking.customers c ON l.customer_id = c.customer_id
JOIN lending.loan_types lt ON l.loan_type_id = lt.loan_type_id
WHERE l.days_past_due > 0
  AND l.status_id IN (SELECT status_id FROM lending.loan_statuses WHERE is_active_loan)
ORDER BY l.days_past_due DESC, l.principal_balance DESC;

COMMENT ON VIEW lending.v_collections_queue IS 'Active delinquent loans prioritized for collections';

-- 5. Materialized view for account daily balances (performance optimization)
CREATE MATERIALIZED VIEW banking.mv_daily_account_balances AS
SELECT 
    a.account_id,
    a.account_number,
    d.date AS balance_date,
    COALESCE(
        (
            SELECT t.balance_after
            FROM banking.transactions t
            WHERE t.account_id = a.account_id
              AND t.transaction_date <= d.date
              AND t.balance_after IS NOT NULL
            ORDER BY t.transaction_date DESC, t.initiated_at DESC
            LIMIT 1
        ),
        a.current_balance
    ) AS end_of_day_balance
FROM banking.accounts a
CROSS JOIN generate_series(
    CURRENT_DATE - INTERVAL '90 days',
    CURRENT_DATE,
    INTERVAL '1 day'
) AS d(date)
WHERE a.account_status = 'active';

CREATE UNIQUE INDEX ON banking.mv_daily_account_balances (account_id, balance_date);

-- Refresh function for the materialized view
CREATE OR REPLACE FUNCTION banking.refresh_daily_balances()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY banking.mv_daily_account_balances;
END;
$$ LANGUAGE plpgsql;
```

---

## 🎯 Practice Challenges

### Challenge 2.1 🟡
Design a normalized schema for the investments domain including portfolios, holdings, and trades.

### Challenge 2.2 🔴
Create a partial unique index that enforces "only one primary account per customer" business rule.

### Challenge 2.3 🔴
Design a temporal table structure to track all changes to customer information for regulatory compliance.

---

**Next: [Part 3 - Advanced Querying Exercises](03-advanced-querying-exercises.md)**
