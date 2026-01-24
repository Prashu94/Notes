# Part 4: Data Manipulation Exercises

## Topics Covered
- Transactions and ACID (Chapter 16)
- Stored Procedures and Functions (Chapter 17)
- Triggers (Chapter 18)
- Data Import/Export (Chapter 19)

---

## Exercise 4.1: Transaction Management for Money Transfers 🔴

### Scenario
Implement a secure money transfer system that ensures ACID compliance. A transfer must debit one account and credit another atomically - if either fails, both must rollback.

### Requirements
1. Create a transfer function with proper transaction handling
2. Validate sufficient balance
3. Check transfer limits
4. Create audit trail
5. Handle concurrent transfers safely

### Solution

```sql
-- Create transfer status enum
CREATE TYPE banking.transfer_status AS ENUM (
    'pending',
    'processing',
    'completed',
    'failed',
    'cancelled',
    'reversed'
);

-- Create transfers table
CREATE TABLE IF NOT EXISTS banking.transfers (
    transfer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transfer_number VARCHAR(30) UNIQUE NOT NULL,
    
    -- Source and destination
    source_account_id UUID NOT NULL REFERENCES banking.accounts(account_id),
    destination_account_id UUID NOT NULL REFERENCES banking.accounts(account_id),
    
    -- Amount
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    currency banking.currency_code DEFAULT 'USD',
    
    -- Status tracking
    status banking.transfer_status DEFAULT 'pending',
    
    -- Transaction references
    debit_transaction_id UUID,
    credit_transaction_id UUID,
    
    -- Metadata
    memo VARCHAR(255),
    initiated_by VARCHAR(100) DEFAULT CURRENT_USER,
    
    -- Timestamps
    initiated_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    failed_at TIMESTAMPTZ,
    failure_reason TEXT,
    
    -- Constraints
    CONSTRAINT different_accounts CHECK (source_account_id != destination_account_id)
);

-- Main transfer function with full ACID compliance
CREATE OR REPLACE FUNCTION banking.execute_transfer(
    p_source_account_number VARCHAR(20),
    p_destination_account_number VARCHAR(20),
    p_amount NUMERIC(15, 2),
    p_memo VARCHAR(255) DEFAULT NULL,
    p_idempotency_key VARCHAR(64) DEFAULT NULL
)
RETURNS TABLE (
    success BOOLEAN,
    transfer_id UUID,
    transfer_number VARCHAR(30),
    message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_source_account_id UUID;
    v_dest_account_id UUID;
    v_source_balance NUMERIC(15, 2);
    v_source_available NUMERIC(15, 2);
    v_daily_transfer_limit NUMERIC(10, 2);
    v_daily_transferred NUMERIC(15, 2);
    v_transfer_id UUID;
    v_transfer_number VARCHAR(30);
    v_debit_txn_id UUID;
    v_credit_txn_id UUID;
    v_source_new_balance NUMERIC(15, 2);
    v_dest_new_balance NUMERIC(15, 2);
    v_existing_transfer_id UUID;
BEGIN
    -- Check idempotency (prevent duplicate transfers)
    IF p_idempotency_key IS NOT NULL THEN
        SELECT t.transfer_id INTO v_existing_transfer_id
        FROM banking.transfers t
        JOIN banking.transactions txn ON t.debit_transaction_id = txn.transaction_id
        WHERE txn.idempotency_key = p_idempotency_key
        LIMIT 1;
        
        IF v_existing_transfer_id IS NOT NULL THEN
            RETURN QUERY SELECT 
                TRUE, 
                v_existing_transfer_id, 
                (SELECT transfer_number FROM banking.transfers WHERE transfer_id = v_existing_transfer_id),
                'Transfer already processed (idempotent)'::TEXT;
            RETURN;
        END IF;
    END IF;

    -- Validate amount
    IF p_amount <= 0 THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 'Transfer amount must be positive'::TEXT;
        RETURN;
    END IF;

    -- Get source account (with lock to prevent race conditions)
    SELECT 
        account_id, 
        current_balance, 
        available_balance,
        daily_transfer_limit
    INTO 
        v_source_account_id, 
        v_source_balance, 
        v_source_available,
        v_daily_transfer_limit
    FROM banking.accounts
    WHERE account_number = p_source_account_number
      AND account_status = 'active'
    FOR UPDATE;  -- Lock the row
    
    IF v_source_account_id IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 'Source account not found or not active'::TEXT;
        RETURN;
    END IF;

    -- Get destination account
    SELECT account_id INTO v_dest_account_id
    FROM banking.accounts
    WHERE account_number = p_destination_account_number
      AND account_status = 'active'
    FOR UPDATE;  -- Lock the row
    
    IF v_dest_account_id IS NULL THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 'Destination account not found or not active'::TEXT;
        RETURN;
    END IF;

    -- Check same account
    IF v_source_account_id = v_dest_account_id THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 'Cannot transfer to the same account'::TEXT;
        RETURN;
    END IF;

    -- Check sufficient balance
    IF v_source_available < p_amount THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 
            FORMAT('Insufficient funds. Available: %s, Requested: %s', v_source_available, p_amount)::TEXT;
        RETURN;
    END IF;

    -- Check daily transfer limit
    SELECT COALESCE(SUM(amount), 0) INTO v_daily_transferred
    FROM banking.transfers
    WHERE source_account_id = v_source_account_id
      AND DATE(initiated_at) = CURRENT_DATE
      AND status IN ('completed', 'processing', 'pending');
    
    IF (v_daily_transferred + p_amount) > v_daily_transfer_limit THEN
        RETURN QUERY SELECT FALSE, NULL::UUID, NULL::VARCHAR(30), 
            FORMAT('Daily transfer limit exceeded. Limit: %s, Used: %s, Requested: %s', 
                v_daily_transfer_limit, v_daily_transferred, p_amount)::TEXT;
        RETURN;
    END IF;

    -- Generate transfer number
    v_transfer_number := 'TRF-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || 
                         LPAD(NEXTVAL('banking.transfer_seq')::TEXT, 6, '0');

    -- Create transfer record
    INSERT INTO banking.transfers (
        transfer_number,
        source_account_id,
        destination_account_id,
        amount,
        memo,
        status
    ) VALUES (
        v_transfer_number,
        v_source_account_id,
        v_dest_account_id,
        p_amount,
        p_memo,
        'processing'
    ) RETURNING transfer_id INTO v_transfer_id;

    -- Debit source account
    UPDATE banking.accounts
    SET 
        current_balance = current_balance - p_amount,
        available_balance = available_balance - p_amount,
        last_activity_at = NOW(),
        updated_at = NOW()
    WHERE account_id = v_source_account_id
    RETURNING current_balance INTO v_source_new_balance;

    -- Create debit transaction
    INSERT INTO banking.transactions (
        idempotency_key,
        reference_number,
        account_id,
        transaction_type,
        transaction_status,
        amount,
        balance_after,
        channel,
        description,
        related_transaction_id,
        transaction_date
    ) VALUES (
        COALESCE(p_idempotency_key, gen_random_uuid()::text) || '-DEBIT',
        v_transfer_number || '-D',
        v_source_account_id,
        'transfer_out',
        'completed',
        -p_amount,
        v_source_new_balance,
        'api',
        COALESCE(p_memo, 'Transfer to ' || p_destination_account_number),
        NULL,
        CURRENT_DATE
    ) RETURNING transaction_id INTO v_debit_txn_id;

    -- Credit destination account
    UPDATE banking.accounts
    SET 
        current_balance = current_balance + p_amount,
        available_balance = available_balance + p_amount,
        last_activity_at = NOW(),
        updated_at = NOW()
    WHERE account_id = v_dest_account_id
    RETURNING current_balance INTO v_dest_new_balance;

    -- Create credit transaction
    INSERT INTO banking.transactions (
        idempotency_key,
        reference_number,
        account_id,
        transaction_type,
        transaction_status,
        amount,
        balance_after,
        channel,
        description,
        related_transaction_id,
        transaction_date
    ) VALUES (
        COALESCE(p_idempotency_key, gen_random_uuid()::text) || '-CREDIT',
        v_transfer_number || '-C',
        v_dest_account_id,
        'transfer_in',
        'completed',
        p_amount,
        v_dest_new_balance,
        'api',
        COALESCE(p_memo, 'Transfer from ' || p_source_account_number),
        v_debit_txn_id,
        CURRENT_DATE
    ) RETURNING transaction_id INTO v_credit_txn_id;

    -- Update debit transaction with related transaction
    UPDATE banking.transactions
    SET related_transaction_id = v_credit_txn_id
    WHERE transaction_id = v_debit_txn_id;

    -- Complete transfer record
    UPDATE banking.transfers
    SET 
        status = 'completed',
        debit_transaction_id = v_debit_txn_id,
        credit_transaction_id = v_credit_txn_id,
        completed_at = NOW()
    WHERE transfer_id = v_transfer_id;

    -- Return success
    RETURN QUERY SELECT TRUE, v_transfer_id, v_transfer_number, 'Transfer completed successfully'::TEXT;

EXCEPTION
    WHEN OTHERS THEN
        -- Log the error (in real system, would log to error table)
        RAISE WARNING 'Transfer failed: %', SQLERRM;
        
        -- Update transfer status if it was created
        IF v_transfer_id IS NOT NULL THEN
            UPDATE banking.transfers
            SET 
                status = 'failed',
                failed_at = NOW(),
                failure_reason = SQLERRM
            WHERE transfer_id = v_transfer_id;
        END IF;
        
        -- Re-raise to trigger rollback
        RAISE;
END;
$$;

-- Create sequence for transfer numbers
CREATE SEQUENCE IF NOT EXISTS banking.transfer_seq START 1;

-- Test the transfer function
SELECT * FROM banking.execute_transfer(
    'ACC2026-00001-CHK',
    'ACC2026-00002-CHK',
    250.00,
    'Test transfer'
);

-- Verify balances and transactions
SELECT account_number, current_balance, available_balance
FROM banking.accounts
WHERE account_number IN ('ACC2026-00001-CHK', 'ACC2026-00002-CHK');
```

---

## Exercise 4.2: Audit Triggers for Compliance 🟡

### Scenario
Implement comprehensive audit logging for all sensitive operations. Banking regulations require tracking who changed what, when, and the before/after values.

### Requirements
1. Create audit log table
2. Trigger for customer changes
3. Trigger for account changes
4. Trigger for transaction modifications
5. Audit query functions

### Solution

```sql
-- Create comprehensive audit log table
CREATE TABLE audit.change_log (
    log_id BIGSERIAL PRIMARY KEY,
    
    -- What changed
    table_schema VARCHAR(63) NOT NULL,
    table_name VARCHAR(63) NOT NULL,
    record_id TEXT NOT NULL,  -- Primary key value(s)
    
    -- Type of change
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    
    -- Change details
    old_values JSONB,
    new_values JSONB,
    changed_columns TEXT[],
    
    -- Who and when
    changed_at TIMESTAMPTZ DEFAULT NOW(),
    changed_by VARCHAR(100) DEFAULT CURRENT_USER,
    session_user VARCHAR(100) DEFAULT SESSION_USER,
    
    -- Context
    application_name VARCHAR(100) DEFAULT current_setting('application_name', TRUE),
    client_ip INET DEFAULT inet_client_addr(),
    client_port INTEGER DEFAULT inet_client_port(),
    
    -- Transaction info
    transaction_id BIGINT DEFAULT txid_current(),
    
    -- Additional context (can be set by application)
    context JSONB DEFAULT '{}'
);

-- Create index for common queries
CREATE INDEX idx_audit_table_record ON audit.change_log (table_schema, table_name, record_id);
CREATE INDEX idx_audit_timestamp ON audit.change_log (changed_at DESC);
CREATE INDEX idx_audit_user ON audit.change_log (changed_by, changed_at DESC);

-- Generic audit trigger function
CREATE OR REPLACE FUNCTION audit.log_changes()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER  -- Run with definer's privileges
AS $$
DECLARE
    v_old_values JSONB;
    v_new_values JSONB;
    v_record_id TEXT;
    v_changed_columns TEXT[];
    v_key TEXT;
BEGIN
    -- Determine the record ID (assumes 'id' or table_name_id pattern)
    IF TG_OP = 'DELETE' THEN
        v_record_id := COALESCE(
            OLD.customer_id::TEXT,
            OLD.account_id::TEXT,
            OLD.transaction_id::TEXT,
            OLD.loan_id::TEXT,
            (row_to_json(OLD)->>'id')::TEXT
        );
        v_old_values := to_jsonb(OLD);
        v_new_values := NULL;
    ELSIF TG_OP = 'INSERT' THEN
        v_record_id := COALESCE(
            NEW.customer_id::TEXT,
            NEW.account_id::TEXT,
            NEW.transaction_id::TEXT,
            NEW.loan_id::TEXT,
            (row_to_json(NEW)->>'id')::TEXT
        );
        v_old_values := NULL;
        v_new_values := to_jsonb(NEW);
    ELSE  -- UPDATE
        v_record_id := COALESCE(
            NEW.customer_id::TEXT,
            NEW.account_id::TEXT,
            NEW.transaction_id::TEXT,
            NEW.loan_id::TEXT,
            (row_to_json(NEW)->>'id')::TEXT
        );
        v_old_values := to_jsonb(OLD);
        v_new_values := to_jsonb(NEW);
        
        -- Find changed columns
        SELECT array_agg(key)
        INTO v_changed_columns
        FROM jsonb_each(v_new_values) AS n(key, value)
        WHERE v_old_values->key IS DISTINCT FROM v_new_values->key;
    END IF;
    
    -- Skip if nothing actually changed in UPDATE
    IF TG_OP = 'UPDATE' AND v_changed_columns IS NULL THEN
        RETURN NEW;
    END IF;
    
    -- Remove sensitive fields from audit (or mask them)
    IF v_old_values IS NOT NULL THEN
        v_old_values := v_old_values - ARRAY['tax_id_hash', 'password_hash'];
        -- Mask last 4 of SSN
        IF v_old_values ? 'tax_id_last_four' THEN
            v_old_values := jsonb_set(v_old_values, '{tax_id_last_four}', '"****"');
        END IF;
    END IF;
    
    IF v_new_values IS NOT NULL THEN
        v_new_values := v_new_values - ARRAY['tax_id_hash', 'password_hash'];
        IF v_new_values ? 'tax_id_last_four' THEN
            v_new_values := jsonb_set(v_new_values, '{tax_id_last_four}', '"****"');
        END IF;
    END IF;
    
    -- Insert audit record
    INSERT INTO audit.change_log (
        table_schema,
        table_name,
        record_id,
        operation,
        old_values,
        new_values,
        changed_columns
    ) VALUES (
        TG_TABLE_SCHEMA,
        TG_TABLE_NAME,
        v_record_id,
        TG_OP,
        v_old_values,
        v_new_values,
        v_changed_columns
    );
    
    -- Return appropriate value
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$;

-- Apply audit triggers to sensitive tables
CREATE TRIGGER audit_customers
    AFTER INSERT OR UPDATE OR DELETE ON banking.customers
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER audit_accounts
    AFTER INSERT OR UPDATE OR DELETE ON banking.accounts
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

CREATE TRIGGER audit_loans
    AFTER INSERT OR UPDATE OR DELETE ON lending.loans
    FOR EACH ROW EXECUTE FUNCTION audit.log_changes();

-- Audit query functions

-- Get history for a specific record
CREATE OR REPLACE FUNCTION audit.get_record_history(
    p_schema VARCHAR(63),
    p_table VARCHAR(63),
    p_record_id TEXT,
    p_limit INTEGER DEFAULT 100
)
RETURNS TABLE (
    log_id BIGINT,
    operation VARCHAR(10),
    changed_at TIMESTAMPTZ,
    changed_by VARCHAR(100),
    changed_columns TEXT[],
    old_values JSONB,
    new_values JSONB
)
LANGUAGE SQL
STABLE
AS $$
    SELECT 
        log_id,
        operation,
        changed_at,
        changed_by,
        changed_columns,
        old_values,
        new_values
    FROM audit.change_log
    WHERE table_schema = p_schema
      AND table_name = p_table
      AND record_id = p_record_id
    ORDER BY changed_at DESC
    LIMIT p_limit;
$$;

-- Get all changes by user
CREATE OR REPLACE FUNCTION audit.get_user_activity(
    p_username VARCHAR(100),
    p_start_date TIMESTAMPTZ DEFAULT NOW() - INTERVAL '24 hours',
    p_end_date TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    log_id BIGINT,
    table_schema VARCHAR(63),
    table_name VARCHAR(63),
    record_id TEXT,
    operation VARCHAR(10),
    changed_at TIMESTAMPTZ,
    summary TEXT
)
LANGUAGE SQL
STABLE
AS $$
    SELECT 
        log_id,
        table_schema,
        table_name,
        record_id,
        operation,
        changed_at,
        CASE operation
            WHEN 'INSERT' THEN 'Created new ' || table_name || ' record'
            WHEN 'UPDATE' THEN 'Updated ' || array_to_string(changed_columns, ', ') || ' in ' || table_name
            WHEN 'DELETE' THEN 'Deleted ' || table_name || ' record'
        END AS summary
    FROM audit.change_log
    WHERE changed_by = p_username
      AND changed_at BETWEEN p_start_date AND p_end_date
    ORDER BY changed_at DESC;
$$;

-- Test the audit triggers
UPDATE banking.customers
SET phone_secondary = '+1-555-8888'
WHERE customer_number = 'CUST-2026-00001';

-- View the audit log
SELECT * FROM audit.get_record_history(
    'banking', 
    'customers', 
    (SELECT customer_id::text FROM banking.customers WHERE customer_number = 'CUST-2026-00001')
);
```

---

## Exercise 4.3: Stored Procedures for Loan Processing 🟡

### Scenario
Create stored procedures to handle the loan application lifecycle - from application through approval to disbursement.

### Requirements
1. Submit loan application
2. Process credit check
3. Approve/reject loan
4. Disburse loan funds
5. Calculate monthly payment

### Solution

```sql
-- Helper function: Calculate monthly payment (PMT formula)
CREATE OR REPLACE FUNCTION lending.calculate_monthly_payment(
    p_principal NUMERIC,
    p_annual_rate NUMERIC,
    p_term_months INTEGER
)
RETURNS NUMERIC
LANGUAGE plpgsql
IMMUTABLE
AS $$
DECLARE
    v_monthly_rate NUMERIC;
BEGIN
    IF p_annual_rate = 0 THEN
        RETURN ROUND(p_principal / p_term_months, 2);
    END IF;
    
    v_monthly_rate := p_annual_rate / 12;
    
    RETURN ROUND(
        p_principal * (v_monthly_rate * POWER(1 + v_monthly_rate, p_term_months)) / 
        (POWER(1 + v_monthly_rate, p_term_months) - 1),
        2
    );
END;
$$;

-- Procedure: Submit loan application
CREATE OR REPLACE PROCEDURE lending.submit_loan_application(
    p_customer_number VARCHAR(20),
    p_loan_type_code VARCHAR(20),
    p_amount NUMERIC(12, 2),
    p_term_months SMALLINT,
    p_purpose VARCHAR(200),
    OUT p_loan_number VARCHAR(20),
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_customer_id UUID;
    v_loan_type_id INTEGER;
    v_loan_type lending.loan_types%ROWTYPE;
    v_status_id INTEGER;
    v_interest_rate NUMERIC(5, 4);
    v_monthly_payment NUMERIC(10, 2);
    v_loan_id UUID;
BEGIN
    -- Get customer
    SELECT customer_id INTO v_customer_id
    FROM banking.customers
    WHERE customer_number = p_customer_number
      AND customer_status = 'active'
      AND kyc_status = 'verified';
    
    IF v_customer_id IS NULL THEN
        p_loan_number := NULL;
        p_message := 'Customer not found, not active, or KYC not verified';
        RETURN;
    END IF;
    
    -- Get loan type and validate
    SELECT * INTO v_loan_type
    FROM lending.loan_types
    WHERE loan_type_code = p_loan_type_code
      AND is_active = TRUE;
    
    IF v_loan_type.loan_type_id IS NULL THEN
        p_loan_number := NULL;
        p_message := 'Invalid or inactive loan type';
        RETURN;
    END IF;
    
    -- Validate amount
    IF p_amount < v_loan_type.min_amount OR p_amount > v_loan_type.max_amount THEN
        p_loan_number := NULL;
        p_message := FORMAT('Amount must be between %s and %s for %s', 
            v_loan_type.min_amount, v_loan_type.max_amount, p_loan_type_code);
        RETURN;
    END IF;
    
    -- Validate term
    IF p_term_months < v_loan_type.min_term_months OR p_term_months > v_loan_type.max_term_months THEN
        p_loan_number := NULL;
        p_message := FORMAT('Term must be between %s and %s months for %s', 
            v_loan_type.min_term_months, v_loan_type.max_term_months, p_loan_type_code);
        RETURN;
    END IF;
    
    -- Get application status
    SELECT status_id INTO v_status_id
    FROM lending.loan_statuses
    WHERE status_code = 'APPLIED';
    
    -- Calculate interest rate (base rate + customer risk adjustment)
    v_interest_rate := v_loan_type.base_rate + 
        COALESCE((SELECT risk_score FROM banking.customers WHERE customer_id = v_customer_id), 50) * 0.0001;
    
    -- Calculate monthly payment
    v_monthly_payment := lending.calculate_monthly_payment(p_amount, v_interest_rate, p_term_months);
    
    -- Generate loan number
    p_loan_number := 'LOAN-' || TO_CHAR(NOW(), 'YYYY') || '-' || 
                     LPAD(NEXTVAL('lending.loan_number_seq')::TEXT, 5, '0');
    
    -- Create loan application
    INSERT INTO lending.loans (
        loan_number,
        customer_id,
        loan_type_id,
        status_id,
        principal_amount,
        interest_rate,
        term_months,
        monthly_payment,
        total_interest,
        principal_balance,
        application_date,
        payments_remaining,
        purpose
    ) VALUES (
        p_loan_number,
        v_customer_id,
        v_loan_type.loan_type_id,
        v_status_id,
        p_amount,
        v_interest_rate,
        p_term_months,
        v_monthly_payment,
        (v_monthly_payment * p_term_months) - p_amount,
        p_amount,
        CURRENT_DATE,
        p_term_months,
        p_purpose
    ) RETURNING loan_id INTO v_loan_id;
    
    -- Record status history
    INSERT INTO lending.loan_status_history (loan_id, new_status_id, reason)
    VALUES (v_loan_id, v_status_id, 'Initial application submitted');
    
    p_message := FORMAT('Loan application submitted. Monthly payment: $%s', v_monthly_payment);
    
    COMMIT;
END;
$$;

-- Create sequence for loan numbers
CREATE SEQUENCE IF NOT EXISTS lending.loan_number_seq START 1;

-- Procedure: Process loan decision
CREATE OR REPLACE PROCEDURE lending.process_loan_decision(
    p_loan_number VARCHAR(20),
    p_decision VARCHAR(10),  -- 'APPROVE' or 'REJECT'
    p_reason TEXT,
    p_adjusted_rate NUMERIC(5, 4) DEFAULT NULL,
    OUT p_success BOOLEAN,
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_loan lending.loans%ROWTYPE;
    v_new_status_id INTEGER;
    v_old_status_id INTEGER;
BEGIN
    -- Get loan
    SELECT * INTO v_loan
    FROM lending.loans
    WHERE loan_number = p_loan_number
    FOR UPDATE;
    
    IF v_loan.loan_id IS NULL THEN
        p_success := FALSE;
        p_message := 'Loan not found';
        RETURN;
    END IF;
    
    -- Verify loan is in reviewable state
    IF v_loan.status_id NOT IN (
        SELECT status_id FROM lending.loan_statuses WHERE status_code IN ('APPLIED', 'UNDER_REVIEW')
    ) THEN
        p_success := FALSE;
        p_message := 'Loan is not in a reviewable state';
        RETURN;
    END IF;
    
    v_old_status_id := v_loan.status_id;
    
    IF UPPER(p_decision) = 'APPROVE' THEN
        SELECT status_id INTO v_new_status_id
        FROM lending.loan_statuses WHERE status_code = 'APPROVED';
        
        -- Update loan with approval
        UPDATE lending.loans
        SET 
            status_id = v_new_status_id,
            interest_rate = COALESCE(p_adjusted_rate, interest_rate),
            monthly_payment = lending.calculate_monthly_payment(
                principal_amount,
                COALESCE(p_adjusted_rate, interest_rate),
                term_months
            ),
            approval_date = CURRENT_DATE,
            updated_at = NOW()
        WHERE loan_id = v_loan.loan_id;
        
        p_message := 'Loan approved. Ready for disbursement.';
        
    ELSIF UPPER(p_decision) = 'REJECT' THEN
        SELECT status_id INTO v_new_status_id
        FROM lending.loan_statuses WHERE status_code = 'REJECTED';
        
        UPDATE lending.loans
        SET 
            status_id = v_new_status_id,
            updated_at = NOW()
        WHERE loan_id = v_loan.loan_id;
        
        p_message := 'Loan rejected.';
        
    ELSE
        p_success := FALSE;
        p_message := 'Invalid decision. Use APPROVE or REJECT';
        RETURN;
    END IF;
    
    -- Record status change
    INSERT INTO lending.loan_status_history (loan_id, old_status_id, new_status_id, reason)
    VALUES (v_loan.loan_id, v_old_status_id, v_new_status_id, p_reason);
    
    p_success := TRUE;
    
    COMMIT;
END;
$$;

-- Procedure: Disburse loan funds
CREATE OR REPLACE PROCEDURE lending.disburse_loan(
    p_loan_number VARCHAR(20),
    p_disbursement_account_number VARCHAR(20),
    OUT p_success BOOLEAN,
    OUT p_transaction_ref VARCHAR(30),
    OUT p_message TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_loan lending.loans%ROWTYPE;
    v_account banking.accounts%ROWTYPE;
    v_new_status_id INTEGER;
    v_transaction_id UUID;
    v_new_balance NUMERIC(15, 2);
BEGIN
    -- Get loan
    SELECT * INTO v_loan
    FROM lending.loans
    WHERE loan_number = p_loan_number
    FOR UPDATE;
    
    IF v_loan.loan_id IS NULL THEN
        p_success := FALSE;
        p_message := 'Loan not found';
        RETURN;
    END IF;
    
    -- Verify loan is approved
    IF v_loan.status_id != (SELECT status_id FROM lending.loan_statuses WHERE status_code = 'APPROVED') THEN
        p_success := FALSE;
        p_message := 'Loan must be approved before disbursement';
        RETURN;
    END IF;
    
    -- Get disbursement account
    SELECT * INTO v_account
    FROM banking.accounts
    WHERE account_number = p_disbursement_account_number
      AND account_status = 'active'
    FOR UPDATE;
    
    IF v_account.account_id IS NULL THEN
        p_success := FALSE;
        p_message := 'Disbursement account not found or not active';
        RETURN;
    END IF;
    
    -- Verify account belongs to loan customer
    IF v_account.customer_id != v_loan.customer_id THEN
        p_success := FALSE;
        p_message := 'Disbursement account must belong to the loan applicant';
        RETURN;
    END IF;
    
    -- Generate transaction reference
    p_transaction_ref := 'DISB-' || p_loan_number;
    
    -- Credit the account
    UPDATE banking.accounts
    SET 
        current_balance = current_balance + v_loan.principal_amount,
        available_balance = available_balance + v_loan.principal_amount,
        last_activity_at = NOW(),
        updated_at = NOW()
    WHERE account_id = v_account.account_id
    RETURNING current_balance INTO v_new_balance;
    
    -- Create disbursement transaction
    INSERT INTO banking.transactions (
        idempotency_key,
        reference_number,
        account_id,
        transaction_type,
        transaction_status,
        amount,
        balance_after,
        channel,
        description,
        transaction_date
    ) VALUES (
        'LOAN-DISB-' || v_loan.loan_id::text,
        p_transaction_ref,
        v_account.account_id,
        'deposit',
        'completed',
        v_loan.principal_amount,
        v_new_balance,
        'system',
        'Loan disbursement - ' || p_loan_number,
        CURRENT_DATE
    ) RETURNING transaction_id INTO v_transaction_id;
    
    -- Update loan status
    SELECT status_id INTO v_new_status_id
    FROM lending.loan_statuses WHERE status_code = 'ACTIVE';
    
    UPDATE lending.loans
    SET 
        status_id = v_new_status_id,
        disbursement_date = CURRENT_DATE,
        disbursement_account_id = v_account.account_id,
        first_payment_date = (CURRENT_DATE + INTERVAL '1 month')::DATE,
        next_payment_date = (CURRENT_DATE + INTERVAL '1 month')::DATE,
        maturity_date = (CURRENT_DATE + (term_months || ' months')::INTERVAL)::DATE,
        updated_at = NOW()
    WHERE loan_id = v_loan.loan_id;
    
    -- Record status change
    INSERT INTO lending.loan_status_history (loan_id, old_status_id, new_status_id, reason)
    VALUES (v_loan.loan_id, v_loan.status_id, v_new_status_id, 
            'Loan disbursed to account ' || p_disbursement_account_number);
    
    -- Generate payment schedule
    CALL lending.generate_payment_schedule(v_loan.loan_id);
    
    p_success := TRUE;
    p_message := FORMAT('Loan of $%s disbursed to account %s', 
                        v_loan.principal_amount, p_disbursement_account_number);
    
    COMMIT;
END;
$$;

-- Procedure: Generate payment schedule
CREATE OR REPLACE PROCEDURE lending.generate_payment_schedule(
    p_loan_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_loan lending.loans%ROWTYPE;
    v_payment_date DATE;
    v_remaining_balance NUMERIC(12, 2);
    v_monthly_rate NUMERIC(10, 8);
    v_interest_payment NUMERIC(10, 2);
    v_principal_payment NUMERIC(10, 2);
    v_payment_number INTEGER := 0;
BEGIN
    SELECT * INTO v_loan FROM lending.loans WHERE loan_id = p_loan_id;
    
    v_payment_date := v_loan.first_payment_date;
    v_remaining_balance := v_loan.principal_amount;
    v_monthly_rate := v_loan.interest_rate / 12;
    
    WHILE v_payment_number < v_loan.term_months AND v_remaining_balance > 0 LOOP
        v_payment_number := v_payment_number + 1;
        
        -- Calculate interest and principal portions
        v_interest_payment := ROUND(v_remaining_balance * v_monthly_rate, 2);
        
        IF v_payment_number = v_loan.term_months THEN
            -- Last payment - pay off remaining balance
            v_principal_payment := v_remaining_balance;
        ELSE
            v_principal_payment := v_loan.monthly_payment - v_interest_payment;
        END IF;
        
        v_remaining_balance := GREATEST(0, v_remaining_balance - v_principal_payment);
        
        -- Insert payment schedule
        INSERT INTO lending.loan_payments (
            loan_id,
            payment_number,
            payment_type,
            payment_status,
            payment_amount,
            principal_amount,
            interest_amount,
            principal_balance_after,
            due_date,
            scheduled_date
        ) VALUES (
            p_loan_id,
            v_payment_number,
            'regular',
            'scheduled',
            CASE WHEN v_payment_number = v_loan.term_months 
                 THEN v_principal_payment + v_interest_payment 
                 ELSE v_loan.monthly_payment 
            END,
            v_principal_payment,
            v_interest_payment,
            v_remaining_balance,
            v_payment_date,
            v_payment_date
        );
        
        v_payment_date := v_payment_date + INTERVAL '1 month';
    END LOOP;
END;
$$;

-- Test the loan procedures
DO $$
DECLARE
    v_loan_number VARCHAR(20);
    v_message TEXT;
    v_success BOOLEAN;
    v_txn_ref VARCHAR(30);
BEGIN
    -- Submit application
    CALL lending.submit_loan_application(
        'CUST-2026-00001',
        'PERSONAL',
        10000.00,
        36,
        'Home improvement',
        v_loan_number,
        v_message
    );
    RAISE NOTICE 'Application: % - %', v_loan_number, v_message;
    
    -- Approve loan
    CALL lending.process_loan_decision(
        v_loan_number,
        'APPROVE',
        'Good credit history, stable income',
        NULL,
        v_success,
        v_message
    );
    RAISE NOTICE 'Decision: % - %', v_success, v_message;
    
    -- Disburse loan
    CALL lending.disburse_loan(
        v_loan_number,
        'ACC2026-00001-CHK',
        v_success,
        v_txn_ref,
        v_message
    );
    RAISE NOTICE 'Disbursement: % - % - %', v_success, v_txn_ref, v_message;
END;
$$;
```

---

## Exercise 4.4: Data Import/Export for Batch Processing 🟡

### Scenario
Create procedures to handle batch operations - importing transactions from external systems and exporting reports.

### Solution

```sql
-- Create staging table for imports
CREATE TABLE banking.transaction_import_staging (
    import_id SERIAL PRIMARY KEY,
    batch_id UUID NOT NULL,
    row_number INTEGER NOT NULL,
    
    -- Raw data
    account_number VARCHAR(20),
    transaction_date VARCHAR(20),
    amount VARCHAR(30),
    description VARCHAR(255),
    merchant_name VARCHAR(200),
    category VARCHAR(50),
    
    -- Processing status
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    
    -- Result
    transaction_id UUID,
    
    -- Timestamps
    imported_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ
);

-- Function to process staged imports
CREATE OR REPLACE FUNCTION banking.process_transaction_imports(
    p_batch_id UUID
)
RETURNS TABLE (
    total_rows INTEGER,
    successful INTEGER,
    failed INTEGER,
    errors JSONB
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_row RECORD;
    v_account_id UUID;
    v_transaction_id UUID;
    v_amount NUMERIC(15, 2);
    v_txn_date DATE;
    v_error TEXT;
    v_total INTEGER := 0;
    v_success INTEGER := 0;
    v_failed INTEGER := 0;
    v_errors JSONB := '[]'::JSONB;
BEGIN
    FOR v_row IN 
        SELECT * FROM banking.transaction_import_staging
        WHERE batch_id = p_batch_id AND status = 'pending'
        ORDER BY row_number
    LOOP
        v_total := v_total + 1;
        v_error := NULL;
        
        BEGIN
            -- Validate and convert data
            -- Account lookup
            SELECT account_id INTO v_account_id
            FROM banking.accounts
            WHERE account_number = v_row.account_number
              AND account_status = 'active';
            
            IF v_account_id IS NULL THEN
                RAISE EXCEPTION 'Account not found: %', v_row.account_number;
            END IF;
            
            -- Parse amount
            BEGIN
                v_amount := v_row.amount::NUMERIC(15, 2);
            EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION 'Invalid amount: %', v_row.amount;
            END;
            
            -- Parse date
            BEGIN
                v_txn_date := v_row.transaction_date::DATE;
            EXCEPTION WHEN OTHERS THEN
                RAISE EXCEPTION 'Invalid date: %', v_row.transaction_date;
            END;
            
            -- Insert transaction
            INSERT INTO banking.transactions (
                idempotency_key,
                reference_number,
                account_id,
                transaction_type,
                transaction_status,
                amount,
                channel,
                description,
                merchant_name,
                category,
                transaction_date
            ) VALUES (
                'IMPORT-' || p_batch_id::TEXT || '-' || v_row.row_number,
                'IMP-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || LPAD(v_row.row_number::TEXT, 6, '0'),
                v_account_id,
                CASE WHEN v_amount >= 0 THEN 'deposit' ELSE 'card_purchase' END::banking.transaction_type,
                'completed',
                v_amount,
                'api'::banking.transaction_channel,
                v_row.description,
                v_row.merchant_name,
                v_row.category,
                v_txn_date
            ) RETURNING transaction_id INTO v_transaction_id;
            
            -- Update staging record
            UPDATE banking.transaction_import_staging
            SET 
                status = 'processed',
                transaction_id = v_transaction_id,
                processed_at = NOW()
            WHERE import_id = v_row.import_id;
            
            v_success := v_success + 1;
            
        EXCEPTION WHEN OTHERS THEN
            v_error := SQLERRM;
            
            UPDATE banking.transaction_import_staging
            SET 
                status = 'error',
                error_message = v_error,
                processed_at = NOW()
            WHERE import_id = v_row.import_id;
            
            v_failed := v_failed + 1;
            v_errors := v_errors || jsonb_build_object(
                'row', v_row.row_number,
                'error', v_error
            );
        END;
    END LOOP;
    
    RETURN QUERY SELECT v_total, v_success, v_failed, v_errors;
END;
$$;

-- Function to export account statements
CREATE OR REPLACE FUNCTION banking.export_account_statement(
    p_account_number VARCHAR(20),
    p_start_date DATE,
    p_end_date DATE
)
RETURNS TABLE (
    statement_json JSONB
)
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_account banking.accounts%ROWTYPE;
    v_customer banking.customers%ROWTYPE;
BEGIN
    -- Get account and customer
    SELECT a.*, c.*
    INTO v_account, v_customer
    FROM banking.accounts a
    JOIN banking.customers c ON a.customer_id = c.customer_id
    WHERE a.account_number = p_account_number;
    
    RETURN QUERY
    SELECT jsonb_build_object(
        'statement_date', NOW(),
        'period', jsonb_build_object(
            'start', p_start_date,
            'end', p_end_date
        ),
        'account', jsonb_build_object(
            'number', v_account.account_number,
            'type', v_account.account_type,
            'currency', v_account.currency
        ),
        'customer', jsonb_build_object(
            'name', v_customer.first_name || ' ' || v_customer.last_name,
            'address', v_customer.address_line1 || ', ' || 
                       v_customer.city || ', ' || v_customer.state_province
        ),
        'opening_balance', (
            SELECT COALESCE(balance_after, 0)
            FROM banking.transactions
            WHERE account_id = v_account.account_id
              AND transaction_date < p_start_date
            ORDER BY transaction_date DESC, initiated_at DESC
            LIMIT 1
        ),
        'closing_balance', v_account.current_balance,
        'total_deposits', (
            SELECT COALESCE(SUM(amount), 0)
            FROM banking.transactions
            WHERE account_id = v_account.account_id
              AND transaction_date BETWEEN p_start_date AND p_end_date
              AND amount > 0
        ),
        'total_withdrawals', (
            SELECT COALESCE(ABS(SUM(amount)), 0)
            FROM banking.transactions
            WHERE account_id = v_account.account_id
              AND transaction_date BETWEEN p_start_date AND p_end_date
              AND amount < 0
        ),
        'transactions', (
            SELECT jsonb_agg(
                jsonb_build_object(
                    'date', transaction_date,
                    'reference', reference_number,
                    'description', description,
                    'amount', amount,
                    'balance', balance_after,
                    'type', transaction_type
                ) ORDER BY transaction_date, initiated_at
            )
            FROM banking.transactions
            WHERE account_id = v_account.account_id
              AND transaction_date BETWEEN p_start_date AND p_end_date
        )
    );
END;
$$;

-- Test export
SELECT * FROM banking.export_account_statement(
    'ACC2026-00001-CHK',
    '2026-01-01',
    '2026-01-31'
);
```

---

## 🎯 Practice Challenges

### Challenge 4.1 🔴
Create a procedure that handles loan payment processing, including partial payments, overpayments, and late fee assessment.

### Challenge 4.2 🔴
Implement a trigger that prevents account balance from going below a configurable minimum balance threshold.

### Challenge 4.3 ⚫
Create a saga pattern implementation for handling distributed transactions across the banking and lending schemas with compensating transactions.

---

**Next: [Part 5 - Performance & Optimization Exercises](05-performance-optimization-exercises.md)**
