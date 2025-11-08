# Transactions and ACID

## Overview

A transaction is a sequence of database operations that are treated as a single unit of work. Transactions ensure data integrity through ACID properties.

## ACID Properties

### Atomicity

**Definition**: All operations in a transaction succeed or all fail (all-or-nothing).

```sql
-- Both operations must succeed
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- If second UPDATE fails, first is rolled back automatically
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE account_id = 999;  -- Fails
COMMIT;  -- Transaction is rolled back
```

### Consistency

**Definition**: Database moves from one valid state to another valid state.

```sql
-- Constraints ensure consistency
CREATE TABLE accounts (
    account_id SERIAL PRIMARY KEY,
    balance DECIMAL(10, 2) CHECK (balance >= 0)  -- Can't go negative
);

BEGIN;
    UPDATE accounts SET balance = balance - 200 WHERE account_id = 1;
    -- If balance would go negative, transaction fails
COMMIT;
```

### Isolation

**Definition**: Concurrent transactions don't interfere with each other.

```sql
-- Transaction 1
BEGIN;
    UPDATE products SET stock = stock - 5 WHERE product_id = 1;
    -- Transaction 2 sees original stock until COMMIT
COMMIT;

-- Transaction 2
BEGIN;
    SELECT stock FROM products WHERE product_id = 1;
COMMIT;
```

### Durability

**Definition**: Once committed, changes persist even if system crashes.

```sql
BEGIN;
    INSERT INTO orders (customer_id, total) VALUES (1, 500.00);
COMMIT;  -- Data is written to WAL and persisted to disk
```

## Transaction Control

### BEGIN/START TRANSACTION

```sql
-- Start transaction
BEGIN;
-- Or
START TRANSACTION;

-- Start with specific isolation level
BEGIN ISOLATION LEVEL SERIALIZABLE;
START TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

### COMMIT

```sql
BEGIN;
    INSERT INTO users (name) VALUES ('Alice');
    INSERT INTO orders (user_id, total) VALUES (1, 100);
COMMIT;  -- Save all changes
```

### ROLLBACK

```sql
BEGIN;
    DELETE FROM users WHERE user_id = 1;
    -- Oops, wrong user!
ROLLBACK;  -- Undo all changes
```

### SAVEPOINT

```sql
BEGIN;
    INSERT INTO orders (user_id, total) VALUES (1, 100);
    SAVEPOINT order_created;
    
    INSERT INTO order_items (order_id, product_id) VALUES (1, 5);
    -- Error in order items
    ROLLBACK TO SAVEPOINT order_created;  -- Only rollback items
    
    -- Fix and retry
    INSERT INTO order_items (order_id, product_id) VALUES (1, 6);
COMMIT;  -- Commit order and corrected items
```

## Isolation Levels

### Read Uncommitted

**PostgreSQL doesn't support true Read Uncommitted** (behaves like Read Committed)

### Read Committed (Default)

```sql
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;

-- Transaction 1
BEGIN;
    SELECT * FROM products WHERE product_id = 1;  -- stock = 100
    -- Transaction 2 updates stock to 95
    SELECT * FROM products WHERE product_id = 1;  -- stock = 95 (non-repeatable read)
COMMIT;
```

**Problems**: Non-repeatable reads

### Repeatable Read

```sql
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Transaction 1
BEGIN;
    SELECT * FROM products WHERE product_id = 1;  -- stock = 100
    -- Transaction 2 updates stock to 95 and commits
    SELECT * FROM products WHERE product_id = 1;  -- Still 100 (repeatable)
COMMIT;
```

**Problems**: Phantom reads (in theory, but PostgreSQL prevents them)

### Serializable

```sql
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Strictest isolation
-- Prevents all concurrency anomalies
-- May cause serialization failures that require retry
```

### Comparison

```sql
-- Read Committed: See committed changes from other transactions
-- Repeatable Read: Snapshot of data at transaction start
-- Serializable: As if transactions ran one at a time

-- Set default for session
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Set for single transaction
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

## Concurrency Issues

### Dirty Reads

Reading uncommitted changes from another transaction.
**PostgreSQL prevents dirty reads** at all isolation levels.

### Non-Repeatable Reads

Same query returns different results within transaction.

```sql
-- Transaction 1
BEGIN ISOLATION LEVEL READ COMMITTED;
    SELECT balance FROM accounts WHERE account_id = 1;  -- 1000
    -- Transaction 2 updates balance to 1500
    SELECT balance FROM accounts WHERE account_id = 1;  -- 1500 (different!)
COMMIT;
```

**Solution**: Use REPEATABLE READ or SERIALIZABLE

### Phantom Reads

New rows appear in result set within transaction.

```sql
-- Transaction 1
BEGIN ISOLATION LEVEL READ COMMITTED;
    SELECT COUNT(*) FROM orders WHERE status = 'pending';  -- 5
    -- Transaction 2 inserts new pending order
    SELECT COUNT(*) FROM orders WHERE status = 'pending';  -- 6 (phantom!)
COMMIT;
```

**Solution**: Use REPEATABLE READ or SERIALIZABLE

### Lost Updates

Two transactions read same value, then both update it.

```sql
-- Transaction 1
BEGIN;
    SELECT balance FROM accounts WHERE account_id = 1;  -- 1000
    -- Calculate new balance: 1000 + 100 = 1100
    -- Transaction 2 does same: reads 1000, calculates 1000 - 50 = 950
    UPDATE accounts SET balance = 1100 WHERE account_id = 1;
COMMIT;

-- Transaction 2
BEGIN;
    UPDATE accounts SET balance = 950 WHERE account_id = 1;  -- Overwrites!
COMMIT;
-- Lost update: +100 is lost, final balance is 950 instead of 1050
```

**Solution**: Use SELECT FOR UPDATE or UPDATE with WHERE condition

## Locking

### Explicit Locking

```sql
-- SELECT FOR UPDATE: Lock rows for update
BEGIN;
    SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE;
    -- Other transactions block on this row
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
COMMIT;

-- SELECT FOR SHARE: Lock rows for read
BEGIN;
    SELECT * FROM products WHERE product_id = 1 FOR SHARE;
    -- Other SELECT FOR SHARE allowed
    -- UPDATE/DELETE blocked
COMMIT;

-- FOR UPDATE NOWAIT: Don't wait for lock
BEGIN;
    SELECT * FROM accounts WHERE account_id = 1 FOR UPDATE NOWAIT;
    -- If locked, error immediately
COMMIT;

-- FOR UPDATE SKIP LOCKED: Skip locked rows
SELECT * FROM jobs WHERE status = 'pending' 
ORDER BY created_at 
LIMIT 10 
FOR UPDATE SKIP LOCKED;
```

### Table-Level Locking

```sql
-- Explicit table locks (rarely needed)
BEGIN;
    LOCK TABLE orders IN EXCLUSIVE MODE;
    -- Prevents concurrent modifications
    INSERT INTO orders VALUES (...);
COMMIT;

-- Lock modes:
-- ACCESS SHARE, ROW SHARE, ROW EXCLUSIVE, SHARE UPDATE EXCLUSIVE,
-- SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE
```

## Transaction Best Practices

### 1. Keep Transactions Short

```sql
-- Bad: Long transaction
BEGIN;
    SELECT * FROM large_table;  -- Slow query
    -- User thinks for 5 minutes
    UPDATE orders SET status = 'confirmed';
COMMIT;

-- Good: Short transaction
BEGIN;
    UPDATE orders SET status = 'confirmed';
COMMIT;
```

### 2. Handle Serialization Failures

```sql
-- Retry logic for serializable transactions
CREATE OR REPLACE FUNCTION transfer_money(from_id INT, to_id INT, amt DECIMAL)
RETURNS BOOLEAN AS $$
DECLARE
    max_attempts INT := 3;
    attempt INT := 0;
BEGIN
    LOOP
        BEGIN
            BEGIN ISOLATION LEVEL SERIALIZABLE;
                UPDATE accounts SET balance = balance - amt WHERE account_id = from_id;
                UPDATE accounts SET balance = balance + amt WHERE account_id = to_id;
            COMMIT;
            RETURN TRUE;
        EXCEPTION
            WHEN serialization_failure THEN
                attempt := attempt + 1;
                IF attempt >= max_attempts THEN
                    RAISE;
                END IF;
        END;
    END LOOP;
END;
$$ LANGUAGE plpgsql;
```

### 3. Use Appropriate Isolation Level

```sql
-- Read Committed: Most workloads (default)
-- Repeatable Read: Consistent reports
-- Serializable: Critical financial transactions
```

### 4. Avoid Deadlocks

```sql
-- Bad: Different lock order
-- Transaction 1
BEGIN;
    UPDATE accounts SET balance = balance - 100 WHERE account_id = 1;
    UPDATE accounts SET balance = balance + 100 WHERE account_id = 2;
COMMIT;

-- Transaction 2
BEGIN;
    UPDATE accounts SET balance = balance - 50 WHERE account_id = 2;  -- Waits for T1
    UPDATE accounts SET balance = balance + 50 WHERE account_id = 1;  -- Deadlock!
COMMIT;

-- Good: Same lock order
-- Both transactions lock accounts in same order (by ID)
```

## Monitoring Transactions

```sql
-- View active transactions
SELECT 
    pid,
    usename,
    state,
    query,
    xact_start,
    NOW() - xact_start AS duration
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY xact_start;

-- View locks
SELECT 
    locktype,
    relation::regclass,
    mode,
    granted,
    pid
FROM pg_locks
WHERE NOT granted;

-- Kill long-running transaction
SELECT pg_terminate_backend(pid);
SELECT pg_cancel_backend(pid);  -- Gentler cancel
```

## Summary

**ACID Properties**:
- **A**tomicity: All or nothing
- **C**onsistency: Valid state to valid state
- **I**solation: Concurrent transactions isolated
- **D**urability: Committed changes persist

**Commands**:
- BEGIN/START TRANSACTION
- COMMIT
- ROLLBACK
- SAVEPOINT

**Isolation Levels**:
- Read Committed (default)
- Repeatable Read
- Serializable

**Locking**:
- FOR UPDATE
- FOR SHARE
- Table locks

**Best Practices**:
- Keep transactions short
- Handle serialization failures
- Use appropriate isolation level
- Avoid deadlocks (consistent lock order)
