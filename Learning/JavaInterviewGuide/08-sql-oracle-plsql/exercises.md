# SQL / Oracle / PL/SQL — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**Stack:** Oracle XE 21c in Docker (preferred for JD), or Postgres with dialect notes.

```bash
docker run -d --name oracle-xe -p 1521:1521 -e ORACLE_PASSWORD=oracle \
  gvenzl/oracle-xe:21-slim
sqlplus system/oracle@//localhost:1521/XEPDB1
```

---

# Part A — Basic (10)

## Exercise 1 — `SELECT` with `WHERE` and `ORDER BY`

**Task:** Return the 5 most recent orders for customer `C100`.

**Solution:**

```sql
CREATE TABLE customers (
  id          VARCHAR2(36) PRIMARY KEY,
  email       VARCHAR2(255) NOT NULL,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

CREATE TABLE orders (
  id          VARCHAR2(36) PRIMARY KEY,
  customer_id VARCHAR2(36) NOT NULL REFERENCES customers(id),
  status      VARCHAR2(20) NOT NULL,
  amount      NUMBER(12,2) NOT NULL,
  created_at  TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL
);

INSERT INTO customers VALUES ('C100', 'alice@example.com', SYSTIMESTAMP);
INSERT INTO orders VALUES ('O1', 'C100', 'PENDING',  99.00, SYSTIMESTAMP - INTERVAL '1' DAY);
INSERT INTO orders VALUES ('O2', 'C100', 'SHIPPED', 150.00, SYSTIMESTAMP);

SELECT id, status, amount, created_at
  FROM orders
 WHERE customer_id = 'C100'
 ORDER BY created_at DESC
 FETCH FIRST 5 ROWS ONLY;
```

---

## Exercise 2 — `INNER JOIN` customers and orders

**Task:** List order id, customer email, amount for all `SHIPPED` orders.

**Solution:**

```sql
SELECT o.id AS order_id, c.email, o.amount
  FROM orders o
 INNER JOIN customers c ON c.id = o.customer_id
 WHERE o.status = 'SHIPPED';
```

**Explain:** `INNER JOIN` drops orders with missing customers (should not happen with FK) and customers with no orders.

---

## Exercise 3 — `LEFT JOIN` to find customers with zero orders

**Task:** Return all customers and a count of their orders (including zero).

**Solution:**

```sql
SELECT c.id, c.email, COUNT(o.id) AS order_count
  FROM customers c
  LEFT JOIN orders o ON o.customer_id = c.id
 GROUP BY c.id, c.email
 ORDER BY order_count DESC;
```

---

## Exercise 4 — `GROUP BY` / `HAVING`

**Task:** Customers who spent more than $500 total.

**Solution:**

```sql
SELECT c.id, c.email, SUM(o.amount) AS total_spent
  FROM customers c
  JOIN orders o ON o.customer_id = c.id
 GROUP BY c.id, c.email
HAVING SUM(o.amount) > 500;
```

---

## Exercise 5 — The `ROWNUM` trap

**Task:** Explain why this is **not** “top 10 newest orders” and fix it.

**Broken:**

```sql
SELECT * FROM orders WHERE ROWNUM <= 10 ORDER BY created_at DESC;
```

**Solution:**

```sql
-- Oracle 12c+ (preferred)
SELECT * FROM orders ORDER BY created_at DESC FETCH FIRST 10 ROWS ONLY;

-- Pre-12c
SELECT * FROM (
  SELECT * FROM orders ORDER BY created_at DESC
) WHERE ROWNUM <= 10;
```

`ROWNUM` is assigned **before** `ORDER BY` in the outer query — you get 10 arbitrary rows, then sorted.

---

## Exercise 6 — `INSERT`, `UPDATE`, `COMMIT`

**Task:** Insert a new order, update status to `CONFIRMED`, verify with `SELECT`.

**Solution:**

```sql
INSERT INTO orders (id, customer_id, status, amount)
VALUES ('O3', 'C100', 'PENDING', 75.50);

UPDATE orders SET status = 'CONFIRMED' WHERE id = 'O3';

SELECT status FROM orders WHERE id = 'O3';  -- CONFIRMED
COMMIT;
```

---

## Exercise 7 — `NOT IN` with NULL (three-valued logic)

**Task:** Show why `NOT IN` returns empty when the subquery contains NULL.

**Solution:**

```sql
CREATE TABLE t (id NUMBER);
INSERT INTO t VALUES (1);
INSERT INTO t VALUES (NULL);

SELECT * FROM dual WHERE 1 NOT IN (SELECT id FROM t);
-- empty!  1 NOT IN (1, NULL) → UNKNOWN → filtered out

SELECT * FROM dual WHERE NOT EXISTS (SELECT 1 FROM t WHERE id = 1);
-- one row — prefer NOT EXISTS or NOT IN with NOT NULL filter

SELECT * FROM dual WHERE 1 NOT IN (SELECT id FROM t WHERE id IS NOT NULL);
-- works
```

---

## Exercise 8 — Scalar subquery

**Task:** Select each order with the customer's email via subquery (no join).

**Solution:**

```sql
SELECT o.id,
       o.amount,
       (SELECT c.email FROM customers c WHERE c.id = o.customer_id) AS email
  FROM orders o;
```

Compare plan to `JOIN` — usually join is faster; subquery fine for one-off reports.

---

## Exercise 9 — `NULL` handling with `NVL` / `COALESCE`

**Task:** Display `discount` as `0` when NULL in a report.

**Solution:**

```sql
ALTER TABLE orders ADD discount NUMBER(12,2);

UPDATE orders SET discount = NULL WHERE id = 'O1';
UPDATE orders SET discount = 10    WHERE id = 'O2';

SELECT id, amount, NVL(discount, 0) AS discount,
       amount - NVL(discount, 0) AS net
  FROM orders;
```

**Postgres note:** Use `COALESCE(discount, 0)` — same semantics.

---

## Exercise 10 — Basic data types and constraints

**Task:** Create `accounts` with non-negative balance and unique email.

**Solution:**

```sql
CREATE TABLE accounts (
  id       VARCHAR2(36) PRIMARY KEY,
  email    VARCHAR2(255) NOT NULL UNIQUE,
  balance  NUMBER(12,2) DEFAULT 0 NOT NULL,
  CONSTRAINT ck_balance_nonneg CHECK (balance >= 0)
);

INSERT INTO accounts VALUES ('A1', 'bob@example.com', 100);
INSERT INTO accounts VALUES ('A2', 'bob@example.com', 50);  -- ORA-00001 unique
INSERT INTO accounts VALUES ('A3', 'carol@example.com', -1); -- ORA-02290 check
```

---

# Part B — Intermediate (10)

## Exercise 11 — Lost update (read-modify-write race)

**Task:** Two sessions each add to balance; final should be 150, not 120 or 130.

**Broken pattern:**

```sql
-- Session 1
SELECT balance FROM accounts WHERE id = 'A1';  -- 100
-- Session 2: SELECT → 100, UPDATE to 130, COMMIT
UPDATE accounts SET balance = 100 + 20 WHERE id = 'A1';  -- overwrites 130
COMMIT;  -- final 120
```

**Solution:**

```sql
-- Atomic increment (best)
UPDATE accounts SET balance = balance + 20 WHERE id = 'A1';

-- Or pessimistic lock
SELECT balance FROM accounts WHERE id = 'A1' FOR UPDATE;
-- compute new balance, UPDATE, COMMIT
```

---

## Exercise 12 — Job worker with `FOR UPDATE SKIP LOCKED`

**Task:** Two workers dequeue jobs without double-claiming.

**Solution:**

```sql
CREATE TABLE jobs (
  id         NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  payload    VARCHAR2(4000),
  status     VARCHAR2(20) DEFAULT 'NEW',
  locked_by  VARCHAR2(64),
  created_at TIMESTAMP DEFAULT SYSTIMESTAMP
);

INSERT INTO jobs (payload) SELECT 'job-' || LEVEL FROM dual CONNECT BY LEVEL <= 20;
COMMIT;

-- Worker SQL (run in two sessions)
UPDATE jobs
   SET status = 'RUNNING', locked_by = :worker_id
 WHERE id IN (
   SELECT id FROM jobs
    WHERE status = 'NEW'
    ORDER BY created_at
    FETCH FIRST 10 ROWS ONLY
    FOR UPDATE SKIP LOCKED
 )
RETURNING id, payload INTO :ids, :payloads;
COMMIT;
```

Session A and B each get disjoint id sets.

---

## Exercise 13 — Window function: latest order per customer

**Task:** One row per customer — their most recent order.

**Solution:**

```sql
SELECT id, customer_id, status, amount, created_at
  FROM (
    SELECT o.*,
           ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn
      FROM orders o
  )
 WHERE rn = 1;
```

**Correlated alternative (usually slower):**

```sql
SELECT o.*
  FROM orders o
 WHERE o.created_at = (
   SELECT MAX(o2.created_at) FROM orders o2 WHERE o2.customer_id = o.customer_id
 );
```

Run `EXPLAIN PLAN` on both; compare cost.

---

## Exercise 14 — Read an execution plan

**Task:** Index `customers.email` and `orders(customer_id, created_at)` until the plan is efficient.

**Solution:**

```sql
EXPLAIN PLAN FOR
SELECT o.*
  FROM orders o
  JOIN customers c ON c.id = o.customer_id
 WHERE c.email = :email
 ORDER BY o.created_at DESC
 FETCH FIRST 20 ROWS ONLY;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);

CREATE INDEX ix_customers_email ON customers (email);
CREATE INDEX ix_orders_cust_created ON orders (customer_id, created_at DESC);

-- Re-run EXPLAIN — expect INDEX RANGE SCAN on customers, NESTED LOOPS or HASH JOIN,
-- INDEX RANGE SCAN on orders, possibly no SORT if index order matches.
```

---

## Exercise 15 — Unindexed foreign key → table lock on parent delete

**Task:** Observe lock waits when deleting a customer while child inserts run.

**Solution:**

```sql
-- Drop index if present
DROP INDEX ix_orders_customer;

-- Session 1
DELETE FROM customers WHERE id = 'C100';  -- blocks on child rows

-- Session 2 (concurrent)
INSERT INTO orders VALUES ('OX', 'C100', 'PENDING', 10, SYSTIMESTAMP);
-- waits — FK check locks child table

-- Fix
CREATE INDEX ix_orders_customer ON orders (customer_id);
-- Deletes still lock rows but child inserts on other customers proceed
```

---

## Exercise 16 — Keyset pagination

**Task:** Page through a customer's orders without `OFFSET`.

**Solution:**

```sql
SELECT *
  FROM orders
 WHERE customer_id = :cid
   AND (created_at, id) < (:cursor_ts, :cursor_id)
 ORDER BY created_at DESC, id DESC
 FETCH FIRST 20 ROWS ONLY;

CREATE INDEX ix_orders_cust_keyset ON orders (customer_id, created_at DESC, id DESC);
```

First page: pass `NULL` for cursor or use a sentinel wrapper in application code.

---

## Exercise 17 — Function-based index

**Task:** Query by `UPPER(email)` without full table scan.

**Solution:**

```sql
-- Without index: TABLE ACCESS FULL
SELECT * FROM customers WHERE UPPER(email) = UPPER(:e);

CREATE INDEX ix_cust_email_upper ON customers (UPPER(email));

-- Plan should show INDEX RANGE SCAN
EXPLAIN PLAN FOR
SELECT * FROM customers WHERE UPPER(email) = UPPER(:e);
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

**Senior takeaway:** Prefer storing normalized `email_lower` if that's the only access pattern — function index still works but adds write overhead.

---

## Exercise 18 — PL/SQL `BULK COLLECT` + `FORALL`

**Task:** Batch-update 1000 orders from `NEW` to `BATCH` faster than row-by-row.

**Solution:**

```sql
DECLARE
  TYPE t_ids IS TABLE OF orders.id%TYPE;
  l_ids t_ids;
BEGIN
  SELECT id BULK COLLECT INTO l_ids
    FROM orders
   WHERE status = 'NEW'
     FETCH FIRST 1000 ROWS ONLY;

  FORALL i IN 1 .. l_ids.COUNT
    UPDATE orders SET status = 'BATCH' WHERE id = l_ids(i);

  DBMS_OUTPUT.PUT_LINE('Updated: ' || SQL%ROWCOUNT);
  COMMIT;
END;
/
```

Compare elapsed time vs:

```sql
FOR r IN (SELECT id FROM orders WHERE status = 'NEW' FETCH FIRST 1000 ROWS ONLY) LOOP
  UPDATE orders SET status = 'BATCH' WHERE id = r.id;
END LOOP;
```

---

## Exercise 19 — `MERGE` (upsert)

**Task:** Sync staging rows into `customers`.

**Solution:**

```sql
CREATE TABLE customers_staging (
  id    VARCHAR2(36),
  email VARCHAR2(255)
);

INSERT INTO customers_staging VALUES ('C100', 'alice-new@example.com');
INSERT INTO customers_staging VALUES ('C200', 'dave@example.com');

MERGE INTO customers c
USING customers_staging s ON (c.id = s.id)
WHEN MATCHED THEN
  UPDATE SET c.email = s.email
WHEN NOT MATCHED THEN
  INSERT (id, email) VALUES (s.id, s.email);

COMMIT;
```

**Postgres:** `INSERT ... ON CONFLICT (id) DO UPDATE SET email = EXCLUDED.email`.

---

## Exercise 20 — Isolation: `READ COMMITTED` vs phantom reads

**Task:** Demonstrate non-repeatable read in Session 1; fix with `FOR UPDATE` or higher isolation.

**Solution:**

```sql
-- Session 1
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM accounts WHERE id = 'A1';  -- 100

-- Session 2
UPDATE accounts SET balance = 200 WHERE id = 'A1';
COMMIT;

-- Session 1
SELECT balance FROM accounts WHERE id = 'A1';  -- 200 (different read)

-- Fix for report consistency in one TX:
SELECT balance FROM accounts WHERE id = 'A1' FOR UPDATE;  -- holds lock until commit
```

Oracle default is READ COMMITTED; no standard `REPEATABLE READ` without serializable or locking.

---

# Part C — Hard (8)

## Exercise 21 — Deadlock with circular FK updates

**Task:** Create a deadlock, read trace, document fix.

**Solution:**

```sql
-- Session 1
UPDATE accounts SET balance = balance + 1 WHERE id = 'A1';  -- locks A1
-- Session 2
UPDATE accounts SET balance = balance + 1 WHERE id = 'A2';  -- locks A2
-- Session 1
UPDATE accounts SET balance = balance + 1 WHERE id = 'A2';  -- waits for S2
-- Session 2
UPDATE accounts SET balance = balance + 1 WHERE id = 'A1';  -- ORA-00060 deadlock

SELECT * FROM v$session WHERE blocking_session IS NOT NULL;
```

**Fix:** Consistent lock ordering (always lock A1 before A2), shorter transactions, retry on `ORA-00060`.

---

## Exercise 22 — Composite index design for a reporting query

**Task:** Optimize this query with the smallest useful index set.

```sql
SELECT customer_id, SUM(amount)
  FROM orders
 WHERE status = 'SHIPPED'
   AND created_at >= DATE '2026-01-01'
   AND created_at <  DATE '2026-02-01'
 GROUP BY customer_id;
```

**Solution:**

```sql
-- Leading column: most selective filter that matches equality first
CREATE INDEX ix_orders_status_created_cust
  ON orders (status, created_at, customer_id);

EXPLAIN PLAN FOR
SELECT customer_id, SUM(amount) FROM orders
 WHERE status = 'SHIPPED'
   AND created_at >= DATE '2026-01-01' AND created_at < DATE '2026-02-01'
 GROUP BY customer_id;

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- Ideal: INDEX RANGE SCAN + no sort if GROUP BY columns in index
```

If `status` has low cardinality, consider `(created_at, status, customer_id)` based on actual selectivity stats.

---

## Exercise 23 — PL/SQL procedure with exception handling

**Task:** `transfer_funds(from_id, to_id, amount)` — rollback on insufficient funds.

**Solution:**

```sql
CREATE OR REPLACE PROCEDURE transfer_funds(
  p_from VARCHAR2, p_to VARCHAR2, p_amount NUMBER
) AS
  l_balance NUMBER;
BEGIN
  IF p_amount <= 0 THEN
    RAISE_APPLICATION_ERROR(-20001, 'Amount must be positive');
  END IF;

  SELECT balance INTO l_balance FROM accounts WHERE id = p_from FOR UPDATE;
  IF l_balance < p_amount THEN
    RAISE_APPLICATION_ERROR(-20002, 'Insufficient funds');
  END IF;

  UPDATE accounts SET balance = balance - p_amount WHERE id = p_from;
  UPDATE accounts SET balance = balance + p_amount WHERE id = p_to;
  COMMIT;
EXCEPTION
  WHEN NO_DATA_FOUND THEN
    ROLLBACK;
    RAISE_APPLICATION_ERROR(-20003, 'Account not found');
  WHEN OTHERS THEN
    ROLLBACK;
    RAISE;
END;
/

BEGIN transfer_funds('A1', 'A2', 50); END;
/
```

---

## Exercise 24 — Mutating trigger (`ORA-04091`)

**Task:** Hit the error, then rewrite as statement-level or move logic to Java.

**Broken:**

```sql
CREATE OR REPLACE TRIGGER trg_order_limit
AFTER INSERT ON orders
FOR EACH ROW
DECLARE
  l_cnt NUMBER;
BEGIN
  SELECT COUNT(*) INTO l_cnt FROM orders WHERE customer_id = :NEW.customer_id;
  IF l_cnt > 100 THEN
    RAISE_APPLICATION_ERROR(-20010, 'Too many orders');
  END IF;
END;
/
-- INSERT → ORA-04091: table ORDERS is mutating
```

**Solution (statement-level):**

```sql
CREATE OR REPLACE TRIGGER trg_order_limit_stmt
AFTER INSERT ON orders
DECLARE
  l_cnt NUMBER;
BEGIN
  FOR r IN (SELECT DISTINCT customer_id FROM orders WHERE ROWNUM = 1) LOOP
    SELECT COUNT(*) INTO l_cnt FROM orders WHERE customer_id = r.customer_id;
    IF l_cnt > 100 THEN
      RAISE_APPLICATION_ERROR(-20010, 'Too many orders');
    END IF;
  END LOOP;
END;
/
```

**Better:** enforce in service layer + optional materialized count column.

---

## Exercise 25 — Partition pruning

**Task:** Range-partition `orders` by month; prove partition elimination in plan.

**Solution:**

```sql
CREATE TABLE orders_part (
  id          VARCHAR2(36),
  customer_id VARCHAR2(36),
  amount      NUMBER(12,2),
  created_at  DATE NOT NULL
)
PARTITION BY RANGE (created_at) (
  PARTITION p202601 VALUES LESS THAN (DATE '2026-02-01'),
  PARTITION p202602 VALUES LESS THAN (DATE '2026-03-01'),
  PARTITION pmax    VALUES LESS THAN (MAXVALUE)
);

INSERT INTO orders_part SELECT id, customer_id, amount, TRUNC(created_at) FROM orders;

EXPLAIN PLAN FOR
SELECT SUM(amount) FROM orders_part
 WHERE created_at >= DATE '2026-01-01' AND created_at < DATE '2026-02-01';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
-- Pstart/Pstop show single partition access
```

---

## Exercise 26 — Lock modes: `FOR UPDATE NOWAIT` vs `SKIP LOCKED`

**Task:** Show `NOWAIT` fails immediately when row is locked.

**Solution:**

```sql
-- Session 1
SELECT * FROM accounts WHERE id = 'A1' FOR UPDATE;

-- Session 2
SELECT * FROM accounts WHERE id = 'A1' FOR UPDATE NOWAIT;
-- ORA-00054: resource busy

-- Session 2 with SKIP LOCKED (on a queue table) returns empty instead of waiting
```

Use `NOWAIT` for user-facing "someone else is editing"; `SKIP LOCKED` for work queues.

---

## Exercise 27 — Materialized view for dashboard aggregate

**Task:** Fast `SUM(amount) BY customer_id` for shipped orders.

**Solution:**

```sql
CREATE MATERIALIZED VIEW mv_customer_spend
BUILD IMMEDIATE
REFRESH FAST ON COMMIT
AS
SELECT customer_id, SUM(amount) AS total_spent, COUNT(*) AS order_count
  FROM orders
 WHERE status = 'SHIPPED'
 GROUP BY customer_id;

CREATE INDEX ix_mv_spend ON mv_customer_spend (total_spent DESC);

SELECT * FROM mv_customer_spend WHERE total_spent > 500;

-- Manual refresh (if not ON COMMIT)
BEGIN DBMS_MVIEW.REFRESH('MV_CUSTOMER_SPEND'); END;
/
```

---

## Exercise 28 — Hibernate empty string → Oracle `NULL`

**Task:** Insert `""` via JPA; observe `NULL` in DB; fix validation.

**Solution:**

```java
@Entity
class Customer {
    @Id String id;
    @Column(nullable = false)
    String nickname;  // @NotBlank in DTO
}
```

```sql
-- After persist with nickname = ""
SELECT nickname, CASE WHEN nickname IS NULL THEN 'IS NULL' ELSE nickname END
  FROM customers WHERE id = 'C100';
-- IS NULL
```

**Fix:** `@NotBlank` on API layer; never rely on `""` for "unset" in Oracle VARCHAR2. Unique index on `nickname` treats all empty strings as one NULL (Oracle allows multiple NULLs in unique).

---

## Exercise 29 — MERGE upsert from staging table

**Difficulty:** Intermediate

**Task:** Create `orders_staging` and `orders`. Write `MERGE` syncing staging → orders on `order_id`. Run twice with same data — row count unchanged.

**Solution:**

```sql
MERGE INTO orders o
USING orders_staging s ON (o.order_id = s.order_id)
WHEN MATCHED THEN UPDATE SET o.total = s.total
WHEN NOT MATCHED THEN INSERT (order_id, total) VALUES (s.order_id, s.total);
```

**Senior takeaway:** MERGE is the Oracle idempotent sync primitive — dedupe staging first to avoid ORA-30926.

---

## Exercise 30 — Running total with window function

**Difficulty:** Basic

**Task:** For one `customer_id`, compute running sum of `order_total` ordered by `order_date`.

**Solution:**

```sql
SELECT order_id, order_total,
       SUM(order_total) OVER (
         PARTITION BY customer_id ORDER BY order_date
         ROWS UNBOUNDED PRECEDING) AS running_total
FROM orders WHERE customer_id = :cid;
```

**Senior takeaway:** Window functions replace slow correlated subqueries for analytics in SQL.

---

## Exercise 31 — FORALL bulk price update

**Difficulty:** Intermediate

**Task:** PL/SQL: update 1000 SKUs using `FORALL` with `LIMIT` bulk collect from cursor — compare timing to row loop.

**Solution:**

```sql
DECLARE
  CURSOR c IS SELECT sku, new_price FROM price_staging;
  TYPE t IS TABLE OF c%ROWTYPE;
  arr t;
BEGIN
  OPEN c;
  LOOP
    FETCH c BULK COLLECT INTO arr LIMIT 5000;
    EXIT WHEN arr.COUNT = 0;
    FORALL i IN 1..arr.COUNT
      UPDATE products SET price = arr(i).new_price WHERE sku = arr(i).sku;
    COMMIT;
  END LOOP;
END;
/
```

**Senior takeaway:** Bulk bind is mandatory for large PL/SQL ETL — row loops are a top AWR offender.

---

## Exercise 32 — Translate SQL Server TOP to Oracle FETCH

**Difficulty:** Basic

**Task:** Rewrite `SELECT TOP 20 * FROM trades ORDER BY trade_time DESC` for Oracle 12c+ and add integration test asserting stable ordering.

**Solution:**

```sql
SELECT * FROM trades ORDER BY trade_time DESC FETCH FIRST 20 ROWS ONLY;
```

**Senior takeaway:** Migration projects fail on dialect trivia — automate grep for `TOP ` and `@@identity` in repos.

---

## Exercise 33 — System-versioned query (SQL Server or Oracle FDA sketch)

**Difficulty:** Hard

**Task:** Enable system-versioning on `accounts` (SQL Server) OR document Flashback Archive setup. Query balance `AS OF` yesterday.

**Solution:**

```sql
-- SQL Server
SELECT balance FROM accounts
FOR SYSTEM_TIME AS OF DATEADD(day, -1, SYSUTCDATETIME())
WHERE id = 1001;

-- Oracle Flashback Query (short undo window)
SELECT balance FROM accounts AS OF TIMESTAMP (SYSTIMESTAMP - INTERVAL '1' DAY)
WHERE id = 1001;
```

**Senior takeaway:** Point-in-time queries need history storage beyond undo — plan retention at design time.

---

# Weekend challenge

1. Take the slowest query in a sample schema, capture **actual** execution plan (`DBMS_XPLAN.DISPLAY_CURSOR` after `ALTER SESSION SET STATISTICS_LEVEL = ALL`), write a 5-line RCA.
2. Add a Flyway script: expand-only migration — add nullable column, backfill in batches of 1000 with `COMMIT` between batches, then add `NOT NULL` in a follow-up script.
3. Draw undo vs redo tablespace flow from memory (Oracle). Label: when does a long-running query need undo?
4. Run two `SKIP LOCKED` workers against 10,000 jobs; prove zero duplicate claims with a `claimed_by` audit column.
