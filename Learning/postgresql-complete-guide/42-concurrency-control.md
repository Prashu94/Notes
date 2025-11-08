# Concurrency Control

## Overview

Concurrency control manages simultaneous database access by multiple users or processes, ensuring data consistency through locks, isolation levels, and Multi-Version Concurrency Control (MVCC). This comprehensive guide covers locking mechanisms, transaction isolation levels, deadlock prevention, MVCC internals, and best practices for high-concurrency applications.

## Table of Contents

- [Concurrency Challenges](#concurrency-challenges)
- [MVCC (Multi-Version Concurrency Control)](#mvcc-multi-version-concurrency-control)
- [Transaction Isolation Levels](#transaction-isolation-levels)
- [Locking Mechanisms](#locking-mechanisms)
- [Deadlocks](#deadlocks)
- [Advisory Locks](#advisory-locks)
- [Optimistic vs Pessimistic Locking](#optimistic-vs-pessimistic-locking)
- [Performance Tuning](#performance-tuning)
- [Best Practices](#best-practices)

## Concurrency Challenges

### Common Concurrency Problems

```sql
-- 1. Lost Update Problem
-- Two transactions update same row, one overwrites the other

-- Transaction 1
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000
UPDATE accounts SET balance = 1000 + 100 WHERE id = 1; -- balance = 1100
COMMIT;

-- Transaction 2 (concurrent)
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000 (before T1 commits)
UPDATE accounts SET balance = 1000 - 50 WHERE id = 1; -- balance = 950 (overwrites T1!)
COMMIT;

-- Result: balance = 950 (should be 1050!)
-- Solution: Use SELECT FOR UPDATE or higher isolation level

-- 2. Dirty Read
-- Transaction reads uncommitted changes from another transaction

-- Transaction 1
BEGIN;
UPDATE accounts SET balance = balance + 1000 WHERE id = 1;
-- Not committed yet

-- Transaction 2
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- Reads uncommitted value!
-- If T1 rolls back, this is a "dirty read"

-- Solution: Use READ COMMITTED or higher isolation level (PostgreSQL default)

-- 3. Non-Repeatable Read
-- Same query returns different results within same transaction

-- Transaction 1
BEGIN;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000

-- Transaction 2 (commits between T1's reads)
BEGIN;
UPDATE accounts SET balance = 2000 WHERE id = 1;
COMMIT;

-- Transaction 1 (continues)
SELECT balance FROM accounts WHERE id = 1; -- balance = 2000 (changed!)
COMMIT;

-- Solution: Use REPEATABLE READ isolation level

-- 4. Phantom Read
-- New rows appear in query results within same transaction

-- Transaction 1
BEGIN;
SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- count = 5

-- Transaction 2
BEGIN;
INSERT INTO accounts (id, balance) VALUES (100, 2000);
COMMIT;

-- Transaction 1 (continues)
SELECT COUNT(*) FROM accounts WHERE balance > 1000; -- count = 6 (phantom row!)
COMMIT;

-- Solution: Use SERIALIZABLE isolation level

-- 5. Write Skew
-- Two transactions read overlapping data and make decisions based on it

CREATE TABLE doctors_on_call (
    id SERIAL PRIMARY KEY,
    doctor_name VARCHAR(100),
    on_call BOOLEAN
);

INSERT INTO doctors_on_call (doctor_name, on_call) VALUES
('Dr. Smith', true),
('Dr. Jones', true);

-- Constraint: At least one doctor must be on call

-- Transaction 1 (Dr. Smith going off call)
BEGIN;
SELECT COUNT(*) FROM doctors_on_call WHERE on_call = true; -- count = 2 (safe to proceed)
UPDATE doctors_on_call SET on_call = false WHERE doctor_name = 'Dr. Smith';
COMMIT;

-- Transaction 2 (Dr. Jones going off call, concurrent)
BEGIN;
SELECT COUNT(*) FROM doctors_on_call WHERE on_call = true; -- count = 2 (safe to proceed)
UPDATE doctors_on_call SET on_call = false WHERE doctor_name = 'Dr. Jones';
COMMIT;

-- Result: Both doctors off call! Constraint violated.
-- Solution: Use SERIALIZABLE isolation level or explicit locking
```

## MVCC (Multi-Version Concurrency Control)

### How MVCC Works

```sql
-- PostgreSQL uses MVCC to handle concurrent transactions
-- Each transaction sees a "snapshot" of the database at transaction start
-- No read locks needed - readers don't block writers, writers don't block readers

-- MVCC Implementation:
-- - Each row has hidden columns: xmin (creating transaction ID), xmax (deleting transaction ID)
-- - Transaction IDs are sequential: 1, 2, 3, ...
-- - Transaction determines visibility based on xmin, xmax, and transaction snapshot

-- View transaction IDs
SELECT txid_current(); -- Current transaction ID

-- Create test table
CREATE TABLE mvcc_demo (
    id SERIAL PRIMARY KEY,
    value TEXT,
    xmin XID,  -- Creating transaction ID (hidden but can be selected)
    xmax XID   -- Deleting transaction ID (hidden)
);

INSERT INTO mvcc_demo (value) VALUES ('initial');

-- View row versions
SELECT
    id,
    value,
    xmin::TEXT AS created_by_txid,
    xmax::TEXT AS deleted_by_txid,
    CASE WHEN xmax = 0 THEN 'visible' ELSE 'deleted' END AS status
FROM mvcc_demo;

-- Update creates new row version
UPDATE mvcc_demo SET value = 'updated' WHERE id = 1;

-- Old version marked as deleted (xmax set), new version created (new xmin)
-- Old version kept for concurrent transactions that started before update

-- MVCC Benefits:
-- 1. Readers don't block writers
-- 2. Writers don't block readers
-- 3. High concurrency without read locks
-- 4. Consistent snapshots for each transaction

-- MVCC Costs:
-- 1. Dead tuples (old versions) must be cleaned up by VACUUM
-- 2. Increased storage for row versions
-- 3. Transaction ID wraparound must be prevented

-- Check dead tuples
SELECT
    schemaname,
    tablename,
    n_live_tup AS live_tuples,
    n_dead_tup AS dead_tuples,
    ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_tuple_percent,
    last_vacuum,
    last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 0
ORDER BY dead_tuple_percent DESC;

-- Manual vacuum to clean up dead tuples
VACUUM mvcc_demo;
```

### Transaction Snapshots

```sql
-- Each transaction gets a snapshot at BEGIN or first query (READ COMMITTED)
-- Snapshot determines which row versions are visible

-- Transaction 1
BEGIN;
SELECT txid_current_snapshot(); -- Shows snapshot: xmin:xmax:xip_list
-- Example: 1000:1005:1001,1003
-- - xmin (1000): All transactions < 1000 are committed
-- - xmax (1005): All transactions >= 1005 are not yet started
-- - xip_list (1001,1003): These transactions are in progress

SELECT * FROM accounts; -- Uses this snapshot
COMMIT;

-- Visibility rules:
-- Row is visible if:
-- 1. xmin is committed and < xmax in snapshot
-- 2. xmax is 0 (not deleted) OR xmax is not committed/in snapshot

-- Check transaction status
SELECT txid_status(1000); -- Returns: committed, aborted, or in progress
```

## Transaction Isolation Levels

### Isolation Levels Overview

```sql
-- PostgreSQL supports 4 isolation levels (SQL standard)
-- 1. READ UNCOMMITTED (treated as READ COMMITTED in PostgreSQL)
-- 2. READ COMMITTED (default)
-- 3. REPEATABLE READ
-- 4. SERIALIZABLE

-- View current isolation level
SHOW transaction_isolation;

-- Set isolation level for session
SET SESSION CHARACTERISTICS AS TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Set isolation level for transaction
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Comparison table:
/*
+-------------------+------------+------------------+--------------+-------------+
| Isolation Level   | Dirty Read | Non-Repeatable   | Phantom Read | Serialization |
|                   |            | Read             |              | Anomalies   |
+-------------------+------------+------------------+--------------+-------------+
| READ UNCOMMITTED  | Possible   | Possible         | Possible     | Possible    |
| READ COMMITTED    | Not        | Possible         | Possible     | Possible    |
| REPEATABLE READ   | Not        | Not Possible     | Not Possible | Possible    |
| SERIALIZABLE      | Not        | Not Possible     | Not Possible | Not Possible|
+-------------------+------------+------------------+--------------+-------------+
*/
```

### READ COMMITTED (Default)

```sql
-- READ COMMITTED: Transaction sees only committed changes
-- - New snapshot for each statement
-- - Prevents dirty reads
-- - Allows non-repeatable reads and phantom reads

-- Transaction 1
BEGIN; -- Uses READ COMMITTED by default
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000

-- Transaction 2
BEGIN;
UPDATE accounts SET balance = 2000 WHERE id = 1;
COMMIT;

-- Transaction 1 (continues)
SELECT balance FROM accounts WHERE id = 1; -- balance = 2000 (non-repeatable read)
COMMIT;

-- Use case: Most web applications (default choice)
```

### REPEATABLE READ

```sql
-- REPEATABLE READ: Transaction sees consistent snapshot throughout
-- - Single snapshot for entire transaction
-- - Prevents dirty reads and non-repeatable reads
-- - Prevents phantom reads in PostgreSQL (stronger than SQL standard)

-- Transaction 1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000

-- Transaction 2
BEGIN;
UPDATE accounts SET balance = 2000 WHERE id = 1;
COMMIT;

-- Transaction 1 (continues)
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000 (still sees old value)
COMMIT;

-- Update conflict detection
-- Transaction 1
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
SELECT balance FROM accounts WHERE id = 1; -- balance = 1000

-- Transaction 2
BEGIN TRANSACTION ISOLATION LEVEL REPEATABLE READ;
UPDATE accounts SET balance = 2000 WHERE id = 1;
COMMIT;

-- Transaction 1 (tries to update same row)
UPDATE accounts SET balance = 1500 WHERE id = 1;
-- ERROR: could not serialize access due to concurrent update
ROLLBACK;

-- Use case: Reports, batch processing, data consistency requirements
```

### SERIALIZABLE

```sql
-- SERIALIZABLE: Strongest isolation level
-- - Transactions execute as if serial (one after another)
-- - Prevents all anomalies including write skew
-- - Uses Serializable Snapshot Isolation (SSI)

-- Transaction 1
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts; -- sum = 10000

-- Transaction 2
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
INSERT INTO accounts (id, balance) VALUES (100, 1000);
COMMIT;

-- Transaction 1 (continues)
SELECT SUM(balance) FROM accounts; -- Still sees sum = 10000 (snapshot isolation)
INSERT INTO audit_log (total_balance) VALUES (10000);
COMMIT; -- ERROR: could not serialize access due to read/write dependencies

-- Must retry transaction
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(balance) FROM accounts; -- sum = 11000 (new snapshot)
INSERT INTO audit_log (total_balance) VALUES (11000);
COMMIT; -- Success

-- Write skew prevention
-- Transaction 1
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM doctors_on_call WHERE on_call = true; -- count = 2
UPDATE doctors_on_call SET on_call = false WHERE doctor_name = 'Dr. Smith';
COMMIT;

-- Transaction 2
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
SELECT COUNT(*) FROM doctors_on_call WHERE on_call = true; -- count = 2
UPDATE doctors_on_call SET on_call = false WHERE doctor_name = 'Dr. Jones';
COMMIT; -- ERROR: could not serialize access

-- Use case: Financial transactions, critical data integrity, concurrent writes to related data
```

## Locking Mechanisms

### Row-Level Locks

```sql
-- PostgreSQL row-level locks

-- 1. FOR UPDATE - Exclusive lock for update
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;
-- Blocks other SELECT FOR UPDATE, UPDATE, DELETE
-- Allows SELECT (without FOR UPDATE)
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- 2. FOR NO KEY UPDATE - Weaker exclusive lock
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;
-- Blocks UPDATE, DELETE
-- Allows SELECT FOR SHARE, foreign key checks
UPDATE accounts SET balance = balance + 100 WHERE id = 1; -- OK (not updating key)
COMMIT;

-- 3. FOR SHARE - Shared lock for read
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR SHARE;
-- Blocks UPDATE, DELETE, FOR UPDATE, FOR NO KEY UPDATE
-- Allows other FOR SHARE
COMMIT;

-- 4. FOR KEY SHARE - Weak shared lock
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR KEY SHARE;
-- Blocks UPDATE (if key columns), DELETE
-- Allows FOR SHARE, FOR NO KEY UPDATE
-- Used by foreign key references
COMMIT;

-- Lock options
-- NOWAIT: Don't wait for lock, return error immediately
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- ERROR: could not obtain lock on row (if locked)
ROLLBACK;

-- SKIP LOCKED: Skip locked rows
BEGIN;
SELECT * FROM queue WHERE processed = false
FOR UPDATE SKIP LOCKED
LIMIT 10;
-- Returns unlocked rows, skips locked ones
-- Useful for job queues
UPDATE queue SET processed = true WHERE id IN (...);
COMMIT;

-- Lock specific rows
BEGIN;
SELECT * FROM accounts WHERE id IN (1, 2, 3) FOR UPDATE;
-- Locks only rows with id 1, 2, 3
UPDATE accounts SET balance = balance + 100 WHERE id IN (1, 2, 3);
COMMIT;
```

### Table-Level Locks

```sql
-- Explicit table locks (rarely needed)

-- 1. ACCESS SHARE - Acquired by SELECT
BEGIN;
LOCK TABLE accounts IN ACCESS SHARE MODE;
-- Conflicts with: ACCESS EXCLUSIVE
SELECT * FROM accounts;
COMMIT;

-- 2. ROW SHARE - Acquired by SELECT FOR UPDATE
BEGIN;
LOCK TABLE accounts IN ROW SHARE MODE;
-- Conflicts with: EXCLUSIVE, ACCESS EXCLUSIVE
SELECT * FROM accounts FOR UPDATE;
COMMIT;

-- 3. ROW EXCLUSIVE - Acquired by UPDATE, DELETE, INSERT
BEGIN;
LOCK TABLE accounts IN ROW EXCLUSIVE MODE;
-- Conflicts with: SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE
UPDATE accounts SET balance = balance + 100;
COMMIT;

-- 4. SHARE UPDATE EXCLUSIVE - Prevents concurrent DDL
BEGIN;
LOCK TABLE accounts IN SHARE UPDATE EXCLUSIVE MODE;
-- Prevents ALTER TABLE, VACUUM, etc.
-- Used by VACUUM (non-FULL), CREATE INDEX CONCURRENTLY
COMMIT;

-- 5. SHARE - Allows concurrent reads, blocks writes
BEGIN;
LOCK TABLE accounts IN SHARE MODE;
-- Conflicts with: ROW EXCLUSIVE, SHARE UPDATE EXCLUSIVE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE
-- Multiple transactions can hold SHARE lock
SELECT * FROM accounts;
COMMIT;

-- 6. SHARE ROW EXCLUSIVE - Protects against concurrent changes
BEGIN;
LOCK TABLE accounts IN SHARE ROW EXCLUSIVE MODE;
-- Only one transaction can hold this lock
COMMIT;

-- 7. EXCLUSIVE - Allows concurrent reads only
BEGIN;
LOCK TABLE accounts IN EXCLUSIVE MODE;
-- Conflicts with: ROW SHARE, ROW EXCLUSIVE, SHARE UPDATE EXCLUSIVE, SHARE, SHARE ROW EXCLUSIVE, EXCLUSIVE, ACCESS EXCLUSIVE
COMMIT;

-- 8. ACCESS EXCLUSIVE - Most restrictive (used by most DDL)
BEGIN;
LOCK TABLE accounts IN ACCESS EXCLUSIVE MODE;
-- Blocks all access
-- Used by DROP TABLE, TRUNCATE, ALTER TABLE
COMMIT;

-- View table locks
SELECT
    locktype,
    database,
    relation::regclass AS table_name,
    mode,
    granted,
    pid,
    query
FROM pg_locks
JOIN pg_stat_activity USING (pid)
WHERE relation IS NOT NULL;
```

### Monitoring Locks

```sql
-- View current locks
SELECT
    locktype,
    database,
    relation::regclass AS table_name,
    page,
    tuple,
    virtualxid,
    transactionid,
    mode,
    granted,
    fastpath
FROM pg_locks;

-- Find blocking queries
SELECT
    blocked_locks.pid AS blocked_pid,
    blocked_activity.usename AS blocked_user,
    blocking_locks.pid AS blocking_pid,
    blocking_activity.usename AS blocking_user,
    blocked_activity.query AS blocked_statement,
    blocking_activity.query AS blocking_statement,
    blocked_activity.application_name AS blocked_application,
    blocking_activity.application_name AS blocking_application
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
    AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
    AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
    AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
    AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
    AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
    AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
    AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
    AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Kill blocking query (use with caution!)
SELECT pg_cancel_backend(blocking_pid); -- Try to cancel gracefully
SELECT pg_terminate_backend(blocking_pid); -- Force terminate
```

## Deadlocks

### Deadlock Detection

```sql
-- Deadlock: Two transactions waiting for each other

-- Transaction 1
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
-- Waiting to update id = 2

-- Transaction 2
BEGIN;
UPDATE accounts SET balance = balance - 50 WHERE id = 2;
-- Waiting to update id = 1

-- Transaction 1 (continues)
UPDATE accounts SET balance = balance + 100 WHERE id = 2; -- Waiting for T2

-- Transaction 2 (continues)
UPDATE accounts SET balance = balance - 50 WHERE id = 1; -- DEADLOCK!

-- PostgreSQL detects deadlock and aborts one transaction:
-- ERROR: deadlock detected
-- DETAIL: Process 12345 waits for ShareLock on transaction 67890; blocked by process 12346.

-- View deadlock timeout setting
SHOW deadlock_timeout; -- Default: 1s

-- Configure deadlock detection (postgresql.conf)
-- deadlock_timeout = 1s

-- Deadlock logs (postgresql.conf)
-- log_lock_waits = on
```

### Preventing Deadlocks

```sql
-- Strategy 1: Consistent lock ordering
-- Always lock rows in same order (e.g., by ID)

-- BAD: Random order
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT;

-- GOOD: Consistent order
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1; -- Always lock lower ID first
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Strategy 2: Use SELECT FOR UPDATE to acquire all locks upfront
BEGIN;
SELECT * FROM accounts WHERE id IN (1, 2) ORDER BY id FOR UPDATE;
-- Locks both rows immediately in order
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Strategy 3: Keep transactions short
BEGIN;
-- Do minimal work
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;
-- Don't hold locks longer than necessary

-- Strategy 4: Use NOWAIT or timeout
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE NOWAIT;
-- Immediately returns error if locked
-- Application can retry or handle gracefully
COMMIT;

-- Strategy 5: Use higher isolation level (SERIALIZABLE)
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- PostgreSQL will detect conflicts and abort one transaction
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

## Advisory Locks

### Advisory Lock Usage

```sql
-- Advisory locks: Application-controlled locks
-- - Not tied to database objects
-- - Must be explicitly acquired and released
-- - Useful for application-level coordination

-- Session-level advisory locks (released on session end)

-- Acquire exclusive lock
SELECT pg_advisory_lock(1234);
-- Blocks until lock acquired

-- Try to acquire lock (non-blocking)
SELECT pg_try_advisory_lock(1234);
-- Returns true if acquired, false if already locked

-- Release lock
SELECT pg_advisory_unlock(1234);

-- Transaction-level advisory locks (released on commit/rollback)

-- Acquire exclusive lock
SELECT pg_advisory_xact_lock(1234);

-- Try to acquire lock
SELECT pg_try_advisory_xact_lock(1234);

-- Shared advisory locks (multiple sessions can hold)

-- Acquire shared lock
SELECT pg_advisory_lock_shared(1234);

-- Release shared lock
SELECT pg_advisory_unlock_shared(1234);

-- Two-argument form (for namespace separation)
SELECT pg_advisory_lock(namespace_id, object_id);

-- Example: Job queue with advisory locks
CREATE TABLE jobs (
    id SERIAL PRIMARY KEY,
    status VARCHAR(20),
    data JSONB
);

-- Worker process acquiring job
BEGIN;
SELECT * FROM jobs
WHERE status = 'pending'
AND pg_try_advisory_xact_lock(id)
LIMIT 1;
-- Only one worker can lock each job
UPDATE jobs SET status = 'processing' WHERE id = ...;
-- Process job
UPDATE jobs SET status = 'completed' WHERE id = ...;
COMMIT; -- Lock automatically released

-- View advisory locks
SELECT
    locktype,
    classid,
    objid,
    mode,
    granted,
    pid
FROM pg_locks
WHERE locktype = 'advisory';
```

## Optimistic vs Pessimistic Locking

### Pessimistic Locking

```sql
-- Pessimistic locking: Lock rows before updating
-- Assumes conflicts are likely

BEGIN;
-- Lock row for update
SELECT * FROM products WHERE id = 1 FOR UPDATE;
-- Other transactions must wait

-- Check inventory
-- Update if available
UPDATE products SET quantity = quantity - 1 WHERE id = 1 AND quantity > 0;

COMMIT;

-- Pros:
-- - Prevents conflicts
-- - Consistent behavior

-- Cons:
-- - Reduces concurrency
-- - Can cause lock contention
-- - Risk of deadlocks

-- Use when: High likelihood of conflicts, critical consistency requirements
```

### Optimistic Locking

```sql
-- Optimistic locking: Don't lock, detect conflicts on update
-- Assumes conflicts are rare

-- Add version column
ALTER TABLE products ADD COLUMN version INTEGER DEFAULT 1;

-- Read without locking
BEGIN;
SELECT id, quantity, version FROM products WHERE id = 1;
-- version = 5, quantity = 10

-- Update with version check
UPDATE products
SET quantity = quantity - 1, version = version + 1
WHERE id = 1 AND version = 5;

-- Check if update succeeded
-- If no rows updated, version changed (conflict detected)
GET DIAGNOSTICS rows_updated = ROW_COUNT;

IF rows_updated = 0 THEN
    -- Conflict! Retry transaction
    ROLLBACK;
ELSE
    COMMIT;
END IF;

-- Pros:
-- - High concurrency
-- - No lock contention
-- - No deadlocks

-- Cons:
-- - Must handle conflicts in application
-- - Wasted work if conflict occurs

-- Use when: Low likelihood of conflicts, read-heavy workloads

-- Optimistic locking with timestamp
ALTER TABLE products ADD COLUMN updated_at TIMESTAMP DEFAULT NOW();

BEGIN;
SELECT id, quantity, updated_at FROM products WHERE id = 1;
-- updated_at = '2024-01-01 10:00:00'

UPDATE products
SET quantity = quantity - 1, updated_at = NOW()
WHERE id = 1 AND updated_at = '2024-01-01 10:00:00';

COMMIT;
```

## Performance Tuning

### Reducing Lock Contention

```sql
-- 1. Keep transactions short
BEGIN;
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;
-- Don't perform long computations inside transaction

-- 2. Batch updates efficiently
-- BAD: Many small transactions
FOR id IN 1..1000 LOOP
    BEGIN;
    UPDATE accounts SET balance = balance + 1 WHERE id = id;
    COMMIT;
END LOOP;

-- GOOD: Single transaction (if appropriate)
BEGIN;
UPDATE accounts SET balance = balance + 1 WHERE id BETWEEN 1 AND 1000;
COMMIT;

-- 3. Use appropriate lock levels
-- Use FOR NO KEY UPDATE instead of FOR UPDATE when possible
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR NO KEY UPDATE;
-- Allows foreign key checks, less restrictive
UPDATE accounts SET balance = balance + 100 WHERE id = 1;
COMMIT;

-- 4. Partition hot tables
CREATE TABLE accounts_partitioned (
    id SERIAL,
    balance NUMERIC,
    account_type VARCHAR(10)
) PARTITION BY HASH (id);

CREATE TABLE accounts_part_0 PARTITION OF accounts_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE accounts_part_1 PARTITION OF accounts_partitioned
    FOR VALUES WITH (MODULUS 4, REMAINDER 1);
-- etc.
-- Reduces contention by spreading rows across partitions

-- 5. Use SKIP LOCKED for queues
BEGIN;
SELECT * FROM job_queue
WHERE status = 'pending'
FOR UPDATE SKIP LOCKED
LIMIT 10;
-- Workers don't wait for locked rows
COMMIT;

-- 6. Monitor lock waits
-- Enable logging (postgresql.conf)
-- log_lock_waits = on
-- deadlock_timeout = 1s

-- Query to find lock waits
SELECT
    pid,
    usename,
    wait_event_type,
    wait_event,
    state,
    query
FROM pg_stat_activity
WHERE wait_event_type = 'Lock';
```

## Best Practices

### Best Practices Checklist

```text
Concurrency Control Best Practices:

1. Choose Appropriate Isolation Level
   ✓ READ COMMITTED: Default for web apps
   ✓ REPEATABLE READ: Reports, batch processing
   ✓ SERIALIZABLE: Financial transactions, critical integrity

2. Keep Transactions Short
   ✓ Minimize work inside transactions
   ✓ Don't wait for user input in transaction
   ✓ Commit as soon as possible

3. Lock in Consistent Order
   ✓ Always lock rows in same order (e.g., by ID)
   ✓ Use SELECT FOR UPDATE to acquire all locks upfront
   ✓ Prevents deadlocks

4. Use Appropriate Lock Levels
   ✓ FOR UPDATE: Exclusive update lock
   ✓ FOR NO KEY UPDATE: When not updating key columns
   ✓ FOR SHARE: Shared read lock
   ✓ FOR KEY SHARE: Weak shared lock

5. Handle Lock Timeouts
   ✓ Use NOWAIT for immediate error
   ✓ Use lock_timeout setting
   ✓ Implement retry logic with exponential backoff
   ✓ Log lock waits for monitoring

6. Use Optimistic Locking When Appropriate
   ✓ For low-conflict scenarios
   ✓ Add version or timestamp column
   ✓ Check version on update
   ✓ Retry on conflict

7. Monitor Lock Contention
   ✓ Enable log_lock_waits
   ✓ Monitor pg_locks and pg_stat_activity
   ✓ Alert on frequent deadlocks
   ✓ Identify hot tables

8. Use Advisory Locks for Application Logic
   ✓ Job queues with pg_try_advisory_xact_lock
   ✓ Application-level coordination
   ✓ Distributed locks across processes

9. Understand MVCC
   ✓ Readers don't block writers
   ✓ Writers don't block readers
   ✓ Dead tuples require VACUUM
   ✓ Transaction ID wraparound prevention

10. Test Under Load
    ✓ Simulate concurrent users
    ✓ Test deadlock scenarios
    ✓ Measure lock wait times
    ✓ Validate isolation level behavior

Common Mistakes to Avoid:
✗ Long-running transactions holding locks
✗ Locking rows in inconsistent order (causes deadlocks)
✗ Using SERIALIZABLE unnecessarily (reduces concurrency)
✗ Not handling lock timeout errors
✗ Not monitoring lock contention
✗ Performing I/O or external calls inside transactions
✗ Using table-level locks when row-level sufficient
✗ Not using connection pooling (increases lock contention)
```

## Summary

Concurrency control ensures data consistency in multi-user environments:

- **MVCC**: Multi-Version Concurrency Control enables high concurrency with readers not blocking writers
- **Isolation Levels**: READ COMMITTED (default, most web apps), REPEATABLE READ (reports), SERIALIZABLE (critical integrity)
- **Locks**: Row-level (FOR UPDATE, FOR SHARE) and table-level locks control concurrent access
- **Deadlocks**: Prevented by consistent lock ordering and short transactions
- **Advisory Locks**: Application-controlled locks for coordination (job queues, distributed locks)
- **Optimistic Locking**: Version-based conflict detection for low-conflict scenarios
- **Best Practices**: Short transactions, consistent lock ordering, appropriate isolation levels, monitor contention

Proper concurrency control is essential for data integrity and application performance.

## Next Steps

- Study [Transaction Management](./06-transactions.md)
- Learn [Performance Troubleshooting](./43-postgresql-administration.md)
- Explore [Monitoring and Logging](./38-monitoring-and-logging.md)
- Practice [High Availability](./37-high-availability.md)
