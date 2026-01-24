# Part 11: Practical Applications Exercises

## Topics Covered
- Real-World Use Cases (Chapter 49)
- Design Patterns and Anti-Patterns (Chapter 50)
- Migration Strategies (Chapter 51)
- Troubleshooting Guide (Chapter 52)

---

## Exercise 11.1: Complete Banking Transaction System 🔴

### Scenario
Build a production-ready transaction processing system for NeoBank that handles high-volume payments, transfers, and settlements.

### Requirements
1. Support multiple transaction types
2. Handle concurrent operations safely
3. Provide real-time balance updates
4. Maintain complete audit trail
5. Support reversals and disputes

### Solution

```sql
-- Step 1: Transaction processing core schema
CREATE SCHEMA IF NOT EXISTS txn_processing;

-- Transaction types and statuses
CREATE TYPE txn_processing.txn_type AS ENUM (
    'deposit', 'withdrawal', 'transfer', 'payment',
    'fee', 'interest', 'refund', 'reversal', 'adjustment'
);

CREATE TYPE txn_processing.txn_status AS ENUM (
    'pending', 'processing', 'completed', 'failed',
    'reversed', 'disputed', 'on_hold'
);

-- Main transaction ledger
CREATE TABLE IF NOT EXISTS txn_processing.ledger (
    ledger_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_id UUID NOT NULL,  -- Groups related entries
    account_id UUID NOT NULL REFERENCES banking.accounts(account_id),
    entry_type VARCHAR(10) NOT NULL CHECK (entry_type IN ('debit', 'credit')),
    amount NUMERIC(18,2) NOT NULL CHECK (amount > 0),
    currency_code CHAR(3) NOT NULL DEFAULT 'USD',
    running_balance NUMERIC(18,2) NOT NULL,
    transaction_type txn_processing.txn_type NOT NULL,
    status txn_processing.txn_status DEFAULT 'pending',
    reference_number VARCHAR(50) NOT NULL,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    reversed_at TIMESTAMPTZ,
    reversed_by UUID,  -- Reference to reversal transaction
    CONSTRAINT positive_balance CHECK (running_balance >= 0 OR transaction_type IN ('fee', 'adjustment'))
);

CREATE INDEX idx_ledger_account_date ON txn_processing.ledger (account_id, created_at DESC);
CREATE INDEX idx_ledger_transaction ON txn_processing.ledger (transaction_id);
CREATE INDEX idx_ledger_reference ON txn_processing.ledger (reference_number);
CREATE INDEX idx_ledger_status ON txn_processing.ledger (status) WHERE status != 'completed';

-- Step 2: Transaction request queue
CREATE TABLE IF NOT EXISTS txn_processing.transaction_queue (
    request_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    transaction_type txn_processing.txn_type NOT NULL,
    source_account_id UUID,
    destination_account_id UUID,
    amount NUMERIC(18,2) NOT NULL,
    currency_code CHAR(3) DEFAULT 'USD',
    priority INTEGER DEFAULT 5,  -- 1=highest, 10=lowest
    idempotency_key VARCHAR(100) UNIQUE,
    request_data JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'queued',
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    error_message TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 hour'
);

CREATE INDEX idx_queue_status_priority ON txn_processing.transaction_queue (status, priority, created_at)
WHERE status = 'queued';

-- Step 3: Core transaction processing function
CREATE OR REPLACE FUNCTION txn_processing.process_transaction(
    p_request_id UUID
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_request RECORD;
    v_transaction_id UUID;
    v_reference VARCHAR(50);
    v_result JSONB;
BEGIN
    -- Get and lock the request
    SELECT * INTO v_request
    FROM txn_processing.transaction_queue
    WHERE request_id = p_request_id
    FOR UPDATE SKIP LOCKED;
    
    IF NOT FOUND THEN
        RETURN jsonb_build_object('error', 'Request not found or already processing');
    END IF;
    
    IF v_request.status != 'queued' THEN
        RETURN jsonb_build_object('error', 'Request already processed', 'status', v_request.status);
    END IF;
    
    -- Mark as processing
    UPDATE txn_processing.transaction_queue
    SET status = 'processing'
    WHERE request_id = p_request_id;
    
    -- Generate identifiers
    v_transaction_id := gen_random_uuid();
    v_reference := 'TXN-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' || 
                   UPPER(SUBSTRING(v_transaction_id::TEXT, 1, 8));
    
    -- Route to appropriate handler
    CASE v_request.transaction_type
        WHEN 'transfer' THEN
            v_result := txn_processing.execute_transfer(
                v_transaction_id,
                v_reference,
                v_request.source_account_id,
                v_request.destination_account_id,
                v_request.amount,
                v_request.currency_code,
                v_request.request_data
            );
        WHEN 'deposit' THEN
            v_result := txn_processing.execute_deposit(
                v_transaction_id,
                v_reference,
                v_request.destination_account_id,
                v_request.amount,
                v_request.currency_code,
                v_request.request_data
            );
        WHEN 'withdrawal' THEN
            v_result := txn_processing.execute_withdrawal(
                v_transaction_id,
                v_reference,
                v_request.source_account_id,
                v_request.amount,
                v_request.currency_code,
                v_request.request_data
            );
        WHEN 'payment' THEN
            v_result := txn_processing.execute_payment(
                v_transaction_id,
                v_reference,
                v_request.source_account_id,
                v_request.amount,
                v_request.currency_code,
                v_request.request_data
            );
        ELSE
            v_result := jsonb_build_object('error', 'Unsupported transaction type');
    END CASE;
    
    -- Update request status
    IF v_result->>'error' IS NULL THEN
        UPDATE txn_processing.transaction_queue
        SET status = 'completed',
            processed_at = NOW()
        WHERE request_id = p_request_id;
    ELSE
        UPDATE txn_processing.transaction_queue
        SET status = 'failed',
            error_message = v_result->>'error',
            retry_count = retry_count + 1
        WHERE request_id = p_request_id;
    END IF;
    
    RETURN v_result || jsonb_build_object(
        'request_id', p_request_id,
        'transaction_id', v_transaction_id,
        'reference', v_reference
    );
END;
$$;

-- Step 4: Transfer execution
CREATE OR REPLACE FUNCTION txn_processing.execute_transfer(
    p_transaction_id UUID,
    p_reference VARCHAR(50),
    p_from_account UUID,
    p_to_account UUID,
    p_amount NUMERIC(18,2),
    p_currency CHAR(3),
    p_metadata JSONB
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_from_account RECORD;
    v_to_account RECORD;
    v_from_new_balance NUMERIC(18,2);
    v_to_new_balance NUMERIC(18,2);
BEGIN
    -- Lock accounts in consistent order
    SELECT * INTO v_from_account
    FROM banking.accounts
    WHERE account_id = p_from_account
    FOR UPDATE;
    
    SELECT * INTO v_to_account
    FROM banking.accounts
    WHERE account_id = p_to_account
    FOR UPDATE;
    
    -- Validations
    IF v_from_account IS NULL OR v_to_account IS NULL THEN
        RETURN jsonb_build_object('error', 'Account not found');
    END IF;
    
    IF v_from_account.account_status != 'active' THEN
        RETURN jsonb_build_object('error', 'Source account not active');
    END IF;
    
    IF v_to_account.account_status NOT IN ('active', 'dormant') THEN
        RETURN jsonb_build_object('error', 'Destination account not available');
    END IF;
    
    IF v_from_account.available_balance < p_amount THEN
        RETURN jsonb_build_object('error', 'Insufficient funds',
            'available', v_from_account.available_balance,
            'requested', p_amount);
    END IF;
    
    -- Debit source account
    UPDATE banking.accounts
    SET current_balance = current_balance - p_amount,
        available_balance = available_balance - p_amount,
        updated_at = NOW()
    WHERE account_id = p_from_account
    RETURNING current_balance INTO v_from_new_balance;
    
    -- Create debit ledger entry
    INSERT INTO txn_processing.ledger (
        transaction_id, account_id, entry_type, amount, currency_code,
        running_balance, transaction_type, status, reference_number,
        description, metadata, processed_at
    ) VALUES (
        p_transaction_id, p_from_account, 'debit', p_amount, p_currency,
        v_from_new_balance, 'transfer', 'completed', p_reference,
        'Transfer to ' || v_to_account.account_number,
        p_metadata || jsonb_build_object('to_account', p_to_account),
        NOW()
    );
    
    -- Credit destination account
    UPDATE banking.accounts
    SET current_balance = current_balance + p_amount,
        available_balance = available_balance + p_amount,
        updated_at = NOW()
    WHERE account_id = p_to_account
    RETURNING current_balance INTO v_to_new_balance;
    
    -- Create credit ledger entry
    INSERT INTO txn_processing.ledger (
        transaction_id, account_id, entry_type, amount, currency_code,
        running_balance, transaction_type, status, reference_number,
        description, metadata, processed_at
    ) VALUES (
        p_transaction_id, p_to_account, 'credit', p_amount, p_currency,
        v_to_new_balance, 'transfer', 'completed', p_reference,
        'Transfer from ' || v_from_account.account_number,
        p_metadata || jsonb_build_object('from_account', p_from_account),
        NOW()
    );
    
    RETURN jsonb_build_object(
        'success', TRUE,
        'from_balance', v_from_new_balance,
        'to_balance', v_to_new_balance
    );
END;
$$;

-- Step 5: Transaction reversal
CREATE OR REPLACE FUNCTION txn_processing.reverse_transaction(
    p_transaction_id UUID,
    p_reason TEXT,
    p_reversed_by TEXT DEFAULT CURRENT_USER
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_entry RECORD;
    v_reversal_txn_id UUID;
    v_reference VARCHAR(50);
    v_new_balance NUMERIC(18,2);
BEGIN
    v_reversal_txn_id := gen_random_uuid();
    v_reference := 'REV-' || TO_CHAR(NOW(), 'YYYYMMDD') || '-' ||
                   UPPER(SUBSTRING(v_reversal_txn_id::TEXT, 1, 8));
    
    -- Process each entry in the original transaction
    FOR v_entry IN
        SELECT * FROM txn_processing.ledger
        WHERE transaction_id = p_transaction_id
          AND status = 'completed'
        ORDER BY created_at
        FOR UPDATE
    LOOP
        -- Create opposite entry
        IF v_entry.entry_type = 'debit' THEN
            -- Reverse debit = credit
            UPDATE banking.accounts
            SET current_balance = current_balance + v_entry.amount,
                available_balance = available_balance + v_entry.amount,
                updated_at = NOW()
            WHERE account_id = v_entry.account_id
            RETURNING current_balance INTO v_new_balance;
            
            INSERT INTO txn_processing.ledger (
                transaction_id, account_id, entry_type, amount, currency_code,
                running_balance, transaction_type, status, reference_number,
                description, metadata, processed_at
            ) VALUES (
                v_reversal_txn_id, v_entry.account_id, 'credit', v_entry.amount,
                v_entry.currency_code, v_new_balance, 'reversal', 'completed',
                v_reference, 'Reversal: ' || p_reason,
                jsonb_build_object('original_txn', p_transaction_id, 'reason', p_reason),
                NOW()
            );
        ELSE
            -- Reverse credit = debit
            UPDATE banking.accounts
            SET current_balance = current_balance - v_entry.amount,
                available_balance = available_balance - v_entry.amount,
                updated_at = NOW()
            WHERE account_id = v_entry.account_id
            RETURNING current_balance INTO v_new_balance;
            
            INSERT INTO txn_processing.ledger (
                transaction_id, account_id, entry_type, amount, currency_code,
                running_balance, transaction_type, status, reference_number,
                description, metadata, processed_at
            ) VALUES (
                v_reversal_txn_id, v_entry.account_id, 'debit', v_entry.amount,
                v_entry.currency_code, v_new_balance, 'reversal', 'completed',
                v_reference, 'Reversal: ' || p_reason,
                jsonb_build_object('original_txn', p_transaction_id, 'reason', p_reason),
                NOW()
            );
        END IF;
        
        -- Mark original as reversed
        UPDATE txn_processing.ledger
        SET status = 'reversed',
            reversed_at = NOW(),
            reversed_by = v_reversal_txn_id
        WHERE ledger_id = v_entry.ledger_id;
    END LOOP;
    
    RETURN jsonb_build_object(
        'success', TRUE,
        'reversal_transaction_id', v_reversal_txn_id,
        'reference', v_reference
    );
END;
$$;

-- Step 6: Daily reconciliation
CREATE OR REPLACE FUNCTION txn_processing.daily_reconciliation(p_date DATE DEFAULT CURRENT_DATE)
RETURNS TABLE (
    account_id UUID,
    account_number VARCHAR(50),
    ledger_balance NUMERIC(18,2),
    account_balance NUMERIC(18,2),
    difference NUMERIC(18,2),
    status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH ledger_balances AS (
        SELECT 
            l.account_id,
            SUM(CASE WHEN entry_type = 'credit' THEN amount ELSE -amount END) AS calculated_balance
        FROM txn_processing.ledger l
        WHERE l.status = 'completed'
          AND l.created_at::DATE <= p_date
        GROUP BY l.account_id
    )
    SELECT 
        a.account_id,
        a.account_number,
        COALESCE(lb.calculated_balance, 0),
        a.current_balance,
        COALESCE(lb.calculated_balance, 0) - a.current_balance,
        CASE 
            WHEN ABS(COALESCE(lb.calculated_balance, 0) - a.current_balance) < 0.01 THEN '✅ Balanced'
            ELSE '❌ Discrepancy'
        END
    FROM banking.accounts a
    LEFT JOIN ledger_balances lb ON a.account_id = lb.account_id
    WHERE a.account_status = 'active'
    ORDER BY ABS(COALESCE(lb.calculated_balance, 0) - a.current_balance) DESC;
END;
$$;
```

---

## Exercise 11.2: Design Patterns Implementation 🟡

### Scenario
Implement common database design patterns used in financial applications.

### Solution

```sql
-- =============================================================================
-- Pattern 1: Event Sourcing
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS event_store;

-- Event store table
CREATE TABLE IF NOT EXISTS event_store.events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_type VARCHAR(100) NOT NULL,  -- e.g., 'Account', 'Customer'
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,      -- e.g., 'AccountOpened', 'FundsDeposited'
    event_version INTEGER NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT DEFAULT CURRENT_USER,
    UNIQUE (aggregate_id, event_version)
);

CREATE INDEX idx_events_aggregate ON event_store.events (aggregate_type, aggregate_id, event_version);

-- Append event function
CREATE OR REPLACE FUNCTION event_store.append_event(
    p_aggregate_type VARCHAR(100),
    p_aggregate_id UUID,
    p_event_type VARCHAR(100),
    p_event_data JSONB,
    p_expected_version INTEGER DEFAULT NULL
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_version INTEGER;
    v_new_version INTEGER;
    v_event_id UUID;
BEGIN
    -- Get current version with lock
    SELECT COALESCE(MAX(event_version), 0) INTO v_current_version
    FROM event_store.events
    WHERE aggregate_id = p_aggregate_id
    FOR UPDATE;
    
    -- Optimistic concurrency check
    IF p_expected_version IS NOT NULL AND v_current_version != p_expected_version THEN
        RAISE EXCEPTION 'Concurrency conflict: expected version %, found %',
            p_expected_version, v_current_version;
    END IF;
    
    v_new_version := v_current_version + 1;
    
    INSERT INTO event_store.events (
        aggregate_type, aggregate_id, event_type, event_version, event_data
    ) VALUES (
        p_aggregate_type, p_aggregate_id, p_event_type, v_new_version, p_event_data
    )
    RETURNING event_id INTO v_event_id;
    
    RETURN v_event_id;
END;
$$;

-- Rebuild aggregate from events
CREATE OR REPLACE FUNCTION event_store.get_aggregate_state(
    p_aggregate_id UUID,
    p_up_to_version INTEGER DEFAULT NULL
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_state JSONB := '{}';
    v_event RECORD;
BEGIN
    FOR v_event IN
        SELECT * FROM event_store.events
        WHERE aggregate_id = p_aggregate_id
          AND (p_up_to_version IS NULL OR event_version <= p_up_to_version)
        ORDER BY event_version
    LOOP
        -- Apply event to state based on type
        CASE v_event.event_type
            WHEN 'AccountOpened' THEN
                v_state := v_event.event_data;
            WHEN 'FundsDeposited' THEN
                v_state := jsonb_set(
                    v_state,
                    '{balance}',
                    to_jsonb((v_state->>'balance')::NUMERIC + (v_event.event_data->>'amount')::NUMERIC)
                );
            WHEN 'FundsWithdrawn' THEN
                v_state := jsonb_set(
                    v_state,
                    '{balance}',
                    to_jsonb((v_state->>'balance')::NUMERIC - (v_event.event_data->>'amount')::NUMERIC)
                );
            WHEN 'AccountClosed' THEN
                v_state := jsonb_set(v_state, '{status}', '"closed"');
            ELSE
                -- Unknown event, merge data
                v_state := v_state || v_event.event_data;
        END CASE;
        
        v_state := jsonb_set(v_state, '{version}', to_jsonb(v_event.event_version));
    END LOOP;
    
    RETURN v_state;
END;
$$;

-- =============================================================================
-- Pattern 2: Saga Pattern for Distributed Transactions
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS saga;

CREATE TYPE saga.saga_status AS ENUM (
    'started', 'running', 'completed', 'compensating', 'failed'
);

CREATE TABLE IF NOT EXISTS saga.sagas (
    saga_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saga_type VARCHAR(100) NOT NULL,
    status saga.saga_status DEFAULT 'started',
    current_step INTEGER DEFAULT 0,
    context JSONB NOT NULL DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT
);

CREATE TABLE IF NOT EXISTS saga.saga_steps (
    step_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    saga_id UUID NOT NULL REFERENCES saga.sagas(saga_id),
    step_number INTEGER NOT NULL,
    step_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    compensation_needed BOOLEAN DEFAULT FALSE,
    compensated_at TIMESTAMPTZ,
    UNIQUE (saga_id, step_number)
);

-- Create saga with steps
CREATE OR REPLACE FUNCTION saga.create_saga(
    p_saga_type VARCHAR(100),
    p_steps TEXT[],
    p_context JSONB DEFAULT '{}'
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_saga_id UUID;
    v_step TEXT;
    v_step_num INTEGER := 1;
BEGIN
    INSERT INTO saga.sagas (saga_type, context)
    VALUES (p_saga_type, p_context)
    RETURNING saga_id INTO v_saga_id;
    
    FOREACH v_step IN ARRAY p_steps
    LOOP
        INSERT INTO saga.saga_steps (saga_id, step_number, step_name)
        VALUES (v_saga_id, v_step_num, v_step);
        v_step_num := v_step_num + 1;
    END LOOP;
    
    RETURN v_saga_id;
END;
$$;

-- Execute next step
CREATE OR REPLACE FUNCTION saga.execute_step(
    p_saga_id UUID,
    p_output JSONB DEFAULT '{}'
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_saga RECORD;
    v_step RECORD;
BEGIN
    SELECT * INTO v_saga FROM saga.sagas WHERE saga_id = p_saga_id FOR UPDATE;
    
    IF v_saga.status NOT IN ('started', 'running') THEN
        RETURN jsonb_build_object('error', 'Saga not in executable state');
    END IF;
    
    -- Get current step
    SELECT * INTO v_step
    FROM saga.saga_steps
    WHERE saga_id = p_saga_id AND step_number = v_saga.current_step + 1;
    
    IF NOT FOUND THEN
        -- All steps completed
        UPDATE saga.sagas
        SET status = 'completed', completed_at = NOW()
        WHERE saga_id = p_saga_id;
        RETURN jsonb_build_object('status', 'completed');
    END IF;
    
    -- Mark step as running
    UPDATE saga.saga_steps
    SET status = 'running', started_at = NOW(), input_data = p_output
    WHERE step_id = v_step.step_id;
    
    UPDATE saga.sagas
    SET status = 'running', current_step = v_step.step_number
    WHERE saga_id = p_saga_id;
    
    RETURN jsonb_build_object(
        'step_id', v_step.step_id,
        'step_name', v_step.step_name,
        'step_number', v_step.step_number
    );
END;
$$;

-- =============================================================================
-- Pattern 3: Temporal Tables (Bi-temporal)
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS temporal;

-- Create temporal version of accounts table
CREATE TABLE IF NOT EXISTS temporal.accounts_history (
    history_id BIGSERIAL PRIMARY KEY,
    account_id UUID NOT NULL,
    -- Business data
    customer_id UUID NOT NULL,
    account_number VARCHAR(50) NOT NULL,
    account_type VARCHAR(30) NOT NULL,
    current_balance NUMERIC(18,2),
    account_status VARCHAR(20),
    -- Temporal columns
    valid_from TIMESTAMPTZ NOT NULL,      -- Business time start
    valid_to TIMESTAMPTZ,                  -- Business time end
    transaction_from TIMESTAMPTZ NOT NULL, -- System time start
    transaction_to TIMESTAMPTZ,            -- System time end
    -- Metadata
    changed_by TEXT DEFAULT CURRENT_USER,
    change_reason TEXT
);

CREATE INDEX idx_accounts_history_id ON temporal.accounts_history (account_id, valid_from, transaction_from);

-- Function to get account state at a point in time
CREATE OR REPLACE FUNCTION temporal.get_account_as_of(
    p_account_id UUID,
    p_as_of_time TIMESTAMPTZ DEFAULT NOW(),
    p_transaction_time TIMESTAMPTZ DEFAULT NOW()
)
RETURNS TABLE (
    account_id UUID,
    customer_id UUID,
    account_number VARCHAR(50),
    current_balance NUMERIC(18,2),
    account_status VARCHAR(20),
    valid_from TIMESTAMPTZ,
    valid_to TIMESTAMPTZ
)
LANGUAGE SQL
AS $$
    SELECT 
        account_id, customer_id, account_number, current_balance, account_status,
        valid_from, valid_to
    FROM temporal.accounts_history
    WHERE account_id = p_account_id
      AND valid_from <= p_as_of_time
      AND (valid_to IS NULL OR valid_to > p_as_of_time)
      AND transaction_from <= p_transaction_time
      AND (transaction_to IS NULL OR transaction_to > p_transaction_time)
    ORDER BY valid_from DESC, transaction_from DESC
    LIMIT 1;
$$;

-- =============================================================================
-- Pattern 4: CQRS - Command Query Responsibility Segregation
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS cqrs;

-- Command side - write operations go through commands
CREATE TABLE IF NOT EXISTS cqrs.commands (
    command_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    command_type VARCHAR(100) NOT NULL,
    aggregate_type VARCHAR(100) NOT NULL,
    aggregate_id UUID,
    payload JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    result JSONB
);

-- Query side - optimized read models
CREATE TABLE IF NOT EXISTS cqrs.customer_summary (
    customer_id UUID PRIMARY KEY,
    customer_name TEXT,
    total_accounts INTEGER DEFAULT 0,
    total_balance NUMERIC(18,2) DEFAULT 0,
    last_transaction_date TIMESTAMPTZ,
    risk_score INTEGER,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cqrs.account_activity (
    account_id UUID PRIMARY KEY,
    account_number VARCHAR(50),
    customer_name TEXT,
    current_balance NUMERIC(18,2),
    available_balance NUMERIC(18,2),
    transaction_count_30d INTEGER DEFAULT 0,
    average_transaction_amount NUMERIC(18,2),
    last_activity TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Projection updater (would be triggered by events)
CREATE OR REPLACE FUNCTION cqrs.update_customer_summary(p_customer_id UUID)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO cqrs.customer_summary (
        customer_id, customer_name, total_accounts, total_balance, 
        last_transaction_date, updated_at
    )
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name,
        COUNT(a.account_id),
        COALESCE(SUM(a.current_balance), 0),
        MAX(t.transaction_date),
        NOW()
    FROM banking.customers c
    LEFT JOIN banking.accounts a ON c.customer_id = a.customer_id
    LEFT JOIN banking.transactions t ON a.account_id = t.account_id
    WHERE c.customer_id = p_customer_id
    GROUP BY c.customer_id, c.first_name, c.last_name
    ON CONFLICT (customer_id) DO UPDATE SET
        customer_name = EXCLUDED.customer_name,
        total_accounts = EXCLUDED.total_accounts,
        total_balance = EXCLUDED.total_balance,
        last_transaction_date = EXCLUDED.last_transaction_date,
        updated_at = NOW();
END;
$$;
```

---

## Exercise 11.3: Database Migration Strategy 🔴

### Scenario
Plan and execute a zero-downtime migration from an old schema to a new optimized schema for NeoBank.

### Solution

```sql
-- =============================================================================
-- Migration Framework
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS migrations;

-- Migration tracking table
CREATE TABLE IF NOT EXISTS migrations.migration_history (
    migration_id SERIAL PRIMARY KEY,
    version VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    script_checksum VARCHAR(64),
    applied_at TIMESTAMPTZ DEFAULT NOW(),
    applied_by TEXT DEFAULT CURRENT_USER,
    execution_time_ms INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    rollback_script TEXT
);

-- Migration execution function
CREATE OR REPLACE FUNCTION migrations.execute_migration(
    p_version VARCHAR(20),
    p_name VARCHAR(200),
    p_up_script TEXT,
    p_down_script TEXT DEFAULT NULL,
    p_description TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_start_time TIMESTAMPTZ;
    v_migration_id INTEGER;
BEGIN
    -- Check if already applied
    IF EXISTS (SELECT 1 FROM migrations.migration_history WHERE version = p_version) THEN
        RAISE NOTICE 'Migration % already applied', p_version;
        RETURN FALSE;
    END IF;
    
    v_start_time := clock_timestamp();
    
    -- Record migration start
    INSERT INTO migrations.migration_history (version, name, description, rollback_script, status)
    VALUES (p_version, p_name, p_description, p_down_script, 'running')
    RETURNING migration_id INTO v_migration_id;
    
    -- Execute migration
    BEGIN
        EXECUTE p_up_script;
        
        -- Update status
        UPDATE migrations.migration_history
        SET status = 'completed',
            execution_time_ms = EXTRACT(MILLISECOND FROM clock_timestamp() - v_start_time)::INTEGER
        WHERE migration_id = v_migration_id;
        
        RETURN TRUE;
    EXCEPTION WHEN OTHERS THEN
        -- Record failure
        UPDATE migrations.migration_history
        SET status = 'failed',
            description = COALESCE(description, '') || E'\nError: ' || SQLERRM
        WHERE migration_id = v_migration_id;
        
        RAISE;
    END;
END;
$$;

-- =============================================================================
-- Zero-Downtime Migration Pattern: Expand-Contract
-- =============================================================================

-- Phase 1: EXPAND - Add new columns, keep old ones
CREATE OR REPLACE FUNCTION migrations.phase1_expand()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Add new columns (nullable)
    ALTER TABLE banking.customers
    ADD COLUMN IF NOT EXISTS full_name TEXT,
    ADD COLUMN IF NOT EXISTS contact_info JSONB,
    ADD COLUMN IF NOT EXISTS address JSONB;
    
    -- Create new optimized table structure
    CREATE TABLE IF NOT EXISTS banking.customers_v2 (
        customer_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        customer_number VARCHAR(50) NOT NULL,
        -- Consolidated name
        full_name TEXT NOT NULL,
        -- Consolidated contact
        contact_info JSONB NOT NULL DEFAULT '{}',
        -- Consolidated address
        address JSONB NOT NULL DEFAULT '{}',
        -- Other fields
        customer_type VARCHAR(20) DEFAULT 'individual',
        customer_status VARCHAR(20) DEFAULT 'pending',
        kyc_status VARCHAR(20) DEFAULT 'pending',
        created_at TIMESTAMPTZ DEFAULT NOW(),
        updated_at TIMESTAMPTZ DEFAULT NOW()
    );
    
    RAISE NOTICE 'Phase 1: EXPAND completed - new columns and tables added';
END;
$$;

-- Phase 2: MIGRATE - Copy data to new structure
CREATE OR REPLACE FUNCTION migrations.phase2_migrate_batch(
    p_batch_size INTEGER DEFAULT 1000
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_migrated INTEGER := 0;
BEGIN
    -- Migrate in batches to avoid long locks
    WITH batch AS (
        SELECT customer_id
        FROM banking.customers c
        WHERE NOT EXISTS (
            SELECT 1 FROM banking.customers_v2 v2 
            WHERE v2.customer_id = c.customer_id
        )
        LIMIT p_batch_size
        FOR UPDATE SKIP LOCKED
    ),
    migrated AS (
        INSERT INTO banking.customers_v2 (
            customer_id,
            customer_number,
            full_name,
            contact_info,
            address,
            customer_type,
            customer_status,
            kyc_status,
            created_at
        )
        SELECT 
            c.customer_id,
            c.customer_number,
            COALESCE(c.full_name, c.first_name || ' ' || c.last_name),
            COALESCE(c.contact_info, jsonb_build_object(
                'email', c.email,
                'phone_primary', c.phone_primary,
                'phone_secondary', c.phone_secondary
            )),
            COALESCE(c.address, jsonb_build_object(
                'line1', c.address_line1,
                'line2', c.address_line2,
                'city', c.city,
                'state', c.state_province,
                'postal_code', c.postal_code,
                'country', c.country_code
            )),
            c.customer_type,
            c.customer_status,
            c.kyc_status,
            c.created_at
        FROM banking.customers c
        JOIN batch b ON c.customer_id = b.customer_id
        ON CONFLICT (customer_id) DO NOTHING
        RETURNING 1
    )
    SELECT COUNT(*) INTO v_migrated FROM migrated;
    
    -- Also update old table with consolidated data
    UPDATE banking.customers c
    SET full_name = c.first_name || ' ' || c.last_name,
        contact_info = jsonb_build_object(
            'email', c.email,
            'phone_primary', c.phone_primary,
            'phone_secondary', c.phone_secondary
        ),
        address = jsonb_build_object(
            'line1', c.address_line1,
            'line2', c.address_line2,
            'city', c.city,
            'state', c.state_province,
            'postal_code', c.postal_code,
            'country', c.country_code
        )
    WHERE full_name IS NULL
      AND customer_id IN (SELECT customer_id FROM batch);
    
    RETURN v_migrated;
END;
$$;

-- Phase 3: DUAL WRITE - Write to both tables
CREATE OR REPLACE FUNCTION migrations.dual_write_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO banking.customers_v2 (
            customer_id, customer_number, full_name, contact_info, address,
            customer_type, customer_status, kyc_status, created_at
        ) VALUES (
            NEW.customer_id,
            NEW.customer_number,
            COALESCE(NEW.full_name, NEW.first_name || ' ' || NEW.last_name),
            COALESCE(NEW.contact_info, jsonb_build_object(
                'email', NEW.email,
                'phone_primary', NEW.phone_primary
            )),
            COALESCE(NEW.address, jsonb_build_object(
                'city', NEW.city,
                'country', NEW.country_code
            )),
            NEW.customer_type,
            NEW.customer_status,
            NEW.kyc_status,
            NEW.created_at
        )
        ON CONFLICT (customer_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            contact_info = EXCLUDED.contact_info,
            address = EXCLUDED.address,
            customer_status = EXCLUDED.customer_status,
            updated_at = NOW();
    ELSIF TG_OP = 'UPDATE' THEN
        UPDATE banking.customers_v2
        SET full_name = COALESCE(NEW.full_name, NEW.first_name || ' ' || NEW.last_name),
            contact_info = COALESCE(NEW.contact_info, jsonb_build_object(
                'email', NEW.email,
                'phone_primary', NEW.phone_primary
            )),
            customer_status = NEW.customer_status,
            updated_at = NOW()
        WHERE customer_id = NEW.customer_id;
    ELSIF TG_OP = 'DELETE' THEN
        DELETE FROM banking.customers_v2 WHERE customer_id = OLD.customer_id;
    END IF;
    
    RETURN NEW;
END;
$$;

-- Apply dual-write trigger
-- CREATE TRIGGER trg_dual_write_customers
-- AFTER INSERT OR UPDATE OR DELETE ON banking.customers
-- FOR EACH ROW EXECUTE FUNCTION migrations.dual_write_trigger();

-- Phase 4: CONTRACT - Remove old structure
CREATE OR REPLACE FUNCTION migrations.phase4_contract()
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN
    -- Verify migration complete
    IF EXISTS (
        SELECT 1 FROM banking.customers c
        WHERE NOT EXISTS (
            SELECT 1 FROM banking.customers_v2 v2 
            WHERE v2.customer_id = c.customer_id
        )
    ) THEN
        RAISE EXCEPTION 'Migration incomplete - some records not migrated';
    END IF;
    
    -- Drop old columns (optional, can be done later)
    -- ALTER TABLE banking.customers DROP COLUMN first_name CASCADE;
    -- ALTER TABLE banking.customers DROP COLUMN last_name CASCADE;
    
    RAISE NOTICE 'Phase 4: CONTRACT completed - ready to drop old columns';
END;
$$;
```

---

## Exercise 11.4: Troubleshooting Toolkit 🟡

### Scenario
Build a comprehensive troubleshooting toolkit for NeoBank's database operations team.

### Solution

```sql
-- =============================================================================
-- Troubleshooting Schema and Tools
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS troubleshoot;

-- =============================================================================
-- Performance Diagnostics
-- =============================================================================

-- Slow query identifier
CREATE OR REPLACE VIEW troubleshoot.v_slow_queries AS
SELECT 
    queryid,
    LEFT(query, 100) AS query_preview,
    calls,
    ROUND(total_exec_time::NUMERIC, 2) AS total_time_ms,
    ROUND(mean_exec_time::NUMERIC, 2) AS avg_time_ms,
    ROUND(stddev_exec_time::NUMERIC, 2) AS stddev_ms,
    rows,
    ROUND(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) AS cache_hit_pct
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Table health check
CREATE OR REPLACE FUNCTION troubleshoot.check_table_health(p_schema TEXT DEFAULT 'banking')
RETURNS TABLE (
    table_name TEXT,
    issue_type TEXT,
    severity TEXT,
    details TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Check for bloated tables
    RETURN QUERY
    SELECT 
        schemaname || '.' || relname,
        'Table Bloat'::TEXT,
        CASE 
            WHEN n_dead_tup > n_live_tup THEN 'CRITICAL'
            WHEN n_dead_tup::FLOAT / NULLIF(n_live_tup, 0) > 0.2 THEN 'WARNING'
            ELSE 'INFO'
        END,
        'Dead tuples: ' || n_dead_tup || ', Live tuples: ' || n_live_tup,
        'Run VACUUM ANALYZE ' || schemaname || '.' || relname
    FROM pg_stat_user_tables
    WHERE schemaname = p_schema
      AND n_dead_tup > n_live_tup * 0.1;
    
    -- Check for missing indexes (sequential scans on large tables)
    RETURN QUERY
    SELECT 
        schemaname || '.' || relname,
        'Missing Index',
        CASE 
            WHEN seq_scan > idx_scan * 10 AND n_live_tup > 10000 THEN 'WARNING'
            ELSE 'INFO'
        END,
        'Seq scans: ' || seq_scan || ', Index scans: ' || idx_scan,
        'Consider adding indexes based on query patterns'
    FROM pg_stat_user_tables
    WHERE schemaname = p_schema
      AND seq_scan > idx_scan * 5
      AND n_live_tup > 1000;
    
    -- Check for unused indexes
    RETURN QUERY
    SELECT 
        schemaname || '.' || indexrelname,
        'Unused Index',
        'INFO'::TEXT,
        'Index scans: ' || idx_scan || ', Size: ' || pg_size_pretty(pg_relation_size(indexrelid)),
        'Consider dropping if truly unused'
    FROM pg_stat_user_indexes
    WHERE schemaname = p_schema
      AND idx_scan = 0
      AND pg_relation_size(indexrelid) > 1024 * 1024;  -- > 1MB
END;
$$;

-- =============================================================================
-- Lock and Blocking Analysis
-- =============================================================================

CREATE OR REPLACE VIEW troubleshoot.v_blocking_chains AS
WITH RECURSIVE lock_tree AS (
    -- Base: blocked processes
    SELECT 
        blocked.pid AS blocked_pid,
        blocked.usename AS blocked_user,
        blocked.query AS blocked_query,
        blocking.pid AS blocking_pid,
        blocking.usename AS blocking_user,
        blocking.query AS blocking_query,
        1 AS depth,
        ARRAY[blocking.pid] AS path
    FROM pg_stat_activity blocked
    JOIN pg_locks blocked_locks ON blocked.pid = blocked_locks.pid
    JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
        AND blocked_locks.relation = blocking_locks.relation
        AND blocked_locks.pid != blocking_locks.pid
    JOIN pg_stat_activity blocking ON blocking_locks.pid = blocking.pid
    WHERE NOT blocked_locks.granted
      AND blocking_locks.granted
    
    UNION ALL
    
    -- Recursive: find blockers of blockers
    SELECT 
        lt.blocked_pid,
        lt.blocked_user,
        lt.blocked_query,
        blocking.pid,
        blocking.usename,
        blocking.query,
        lt.depth + 1,
        lt.path || blocking.pid
    FROM lock_tree lt
    JOIN pg_locks blocked_locks ON lt.blocking_pid = blocked_locks.pid
    JOIN pg_locks blocking_locks ON blocked_locks.locktype = blocking_locks.locktype
        AND blocked_locks.relation = blocking_locks.relation
        AND blocked_locks.pid != blocking_locks.pid
    JOIN pg_stat_activity blocking ON blocking_locks.pid = blocking.pid
    WHERE NOT blocked_locks.granted
      AND blocking_locks.granted
      AND NOT blocking.pid = ANY(lt.path)
      AND lt.depth < 10
)
SELECT * FROM lock_tree
ORDER BY depth DESC, blocked_pid;

-- =============================================================================
-- Connection Diagnostics
-- =============================================================================

CREATE OR REPLACE FUNCTION troubleshoot.connection_analysis()
RETURNS TABLE (
    metric TEXT,
    value TEXT,
    status TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_max_conn INTEGER;
    v_current_conn INTEGER;
    v_idle_conn INTEGER;
    v_active_conn INTEGER;
    v_idle_in_txn INTEGER;
BEGIN
    v_max_conn := current_setting('max_connections')::INTEGER;
    
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE state = 'idle'),
        COUNT(*) FILTER (WHERE state = 'active'),
        COUNT(*) FILTER (WHERE state = 'idle in transaction')
    INTO v_current_conn, v_idle_conn, v_active_conn, v_idle_in_txn
    FROM pg_stat_activity
    WHERE backend_type = 'client backend';
    
    RETURN QUERY VALUES
        ('Max Connections', v_max_conn::TEXT, 'INFO'),
        ('Current Connections', v_current_conn::TEXT, 
         CASE WHEN v_current_conn > v_max_conn * 0.8 THEN 'WARNING' ELSE 'OK' END),
        ('Active Connections', v_active_conn::TEXT, 'INFO'),
        ('Idle Connections', v_idle_conn::TEXT,
         CASE WHEN v_idle_conn > v_current_conn * 0.7 THEN 'WARNING' ELSE 'OK' END),
        ('Idle in Transaction', v_idle_in_txn::TEXT,
         CASE WHEN v_idle_in_txn > 5 THEN 'WARNING' ELSE 'OK' END),
        ('Connection Utilization', 
         ROUND(100.0 * v_current_conn / v_max_conn, 1) || '%',
         CASE WHEN v_current_conn > v_max_conn * 0.9 THEN 'CRITICAL'
              WHEN v_current_conn > v_max_conn * 0.7 THEN 'WARNING'
              ELSE 'OK' END);
END;
$$;

-- =============================================================================
-- Emergency Response Procedures
-- =============================================================================

-- Kill long-running queries
CREATE OR REPLACE FUNCTION troubleshoot.kill_long_queries(
    p_max_duration INTERVAL DEFAULT '5 minutes',
    p_dry_run BOOLEAN DEFAULT TRUE
)
RETURNS TABLE (
    pid INTEGER,
    duration INTERVAL,
    query TEXT,
    action TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_proc RECORD;
BEGIN
    FOR v_proc IN
        SELECT 
            a.pid,
            NOW() - a.query_start AS duration,
            LEFT(a.query, 200) AS query
        FROM pg_stat_activity a
        WHERE a.state = 'active'
          AND a.pid != pg_backend_pid()
          AND NOW() - a.query_start > p_max_duration
    LOOP
        pid := v_proc.pid;
        duration := v_proc.duration;
        query := v_proc.query;
        
        IF p_dry_run THEN
            action := 'WOULD TERMINATE (dry run)';
        ELSE
            PERFORM pg_terminate_backend(v_proc.pid);
            action := 'TERMINATED';
            
            INSERT INTO audit.change_log (table_schema, table_name, operation, context)
            VALUES ('troubleshoot', 'long_queries', 'KILL',
                    jsonb_build_object('pid', v_proc.pid, 'query', v_proc.query));
        END IF;
        
        RETURN NEXT;
    END LOOP;
END;
$$;

-- Emergency: Clear all idle in transaction
CREATE OR REPLACE FUNCTION troubleshoot.clear_idle_transactions(
    p_older_than INTERVAL DEFAULT '10 minutes',
    p_dry_run BOOLEAN DEFAULT TRUE
)
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER := 0;
    v_proc RECORD;
BEGIN
    FOR v_proc IN
        SELECT pid
        FROM pg_stat_activity
        WHERE state = 'idle in transaction'
          AND NOW() - state_change > p_older_than
          AND pid != pg_backend_pid()
    LOOP
        IF NOT p_dry_run THEN
            PERFORM pg_terminate_backend(v_proc.pid);
        END IF;
        v_count := v_count + 1;
    END LOOP;
    
    RETURN v_count;
END;
$$;

-- =============================================================================
-- Health Check Dashboard
-- =============================================================================

CREATE OR REPLACE FUNCTION troubleshoot.full_health_check()
RETURNS TABLE (
    category TEXT,
    check_name TEXT,
    status TEXT,
    value TEXT,
    recommendation TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    -- Database size
    RETURN QUERY
    SELECT 
        'Storage'::TEXT,
        'Database Size',
        'INFO',
        pg_size_pretty(pg_database_size(current_database())),
        NULL::TEXT;
    
    -- Connection health
    RETURN QUERY
    SELECT 
        'Connections',
        metric,
        status,
        value,
        NULL
    FROM troubleshoot.connection_analysis();
    
    -- Replication status
    RETURN QUERY
    SELECT 
        'Replication',
        'Replica Lag',
        CASE 
            WHEN MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn)) > 100*1024*1024 THEN 'WARNING'
            ELSE 'OK'
        END,
        COALESCE(pg_size_pretty(MAX(pg_wal_lsn_diff(sent_lsn, replay_lsn))), 'No replicas'),
        NULL
    FROM pg_stat_replication;
    
    -- Cache performance
    RETURN QUERY
    SELECT 
        'Performance',
        'Buffer Cache Hit Ratio',
        CASE 
            WHEN ROUND(100.0 * SUM(blks_hit) / NULLIF(SUM(blks_hit + blks_read), 0), 2) > 99 THEN 'OK'
            WHEN ROUND(100.0 * SUM(blks_hit) / NULLIF(SUM(blks_hit + blks_read), 0), 2) > 95 THEN 'WARNING'
            ELSE 'CRITICAL'
        END,
        ROUND(100.0 * SUM(blks_hit) / NULLIF(SUM(blks_hit + blks_read), 0), 2) || '%',
        CASE WHEN ROUND(100.0 * SUM(blks_hit) / NULLIF(SUM(blks_hit + blks_read), 0), 2) < 95 
             THEN 'Consider increasing shared_buffers' ELSE NULL END
    FROM pg_stat_database
    WHERE datname = current_database();
    
    -- Transaction ID age
    RETURN QUERY
    SELECT 
        'Maintenance',
        'Transaction ID Age',
        CASE 
            WHEN age(datfrozenxid) > 1000000000 THEN 'CRITICAL'
            WHEN age(datfrozenxid) > 500000000 THEN 'WARNING'
            ELSE 'OK'
        END,
        age(datfrozenxid)::TEXT,
        CASE WHEN age(datfrozenxid) > 500000000 
             THEN 'Run VACUUM FREEZE on large tables' ELSE NULL END
    FROM pg_database
    WHERE datname = current_database();
END;
$$;

-- Run full health check
SELECT * FROM troubleshoot.full_health_check();
```

---

## 🎯 Practice Challenges

### Challenge 11.1 🔴
Implement a complete batch payment processing system with retry logic, idempotency, and detailed error tracking.

### Challenge 11.2 ⚫
Design and implement a real-time fraud detection system using PostgreSQL triggers, materialized views, and temporal pattern analysis.

### Challenge 11.3 ⚫
Create a complete disaster recovery runbook with automated failover procedures and validation scripts.

### Challenge 11.4 🔴
Build a database performance baseline tool that captures metrics, identifies deviations, and generates alerts.

---

## 🎓 Capstone Project

### NeoBank Production Readiness Assessment

Combine all exercises to create a production-ready NeoBank database with:

1. **Complete Schema** - All tables with proper constraints and indexes
2. **Security Implementation** - RBAC, RLS, encryption, and audit logging
3. **High Availability** - Replication, failover procedures, and monitoring
4. **Performance Optimization** - Query tuning, partitioning, and caching strategies
5. **Operational Tools** - Backup, recovery, troubleshooting, and health checks
6. **Documentation** - Schema documentation, runbooks, and procedures

---

**🎉 Congratulations! You've completed all PostgreSQL exercises!**

Return to: [Exercise Overview](00-exercise-setup.md)
