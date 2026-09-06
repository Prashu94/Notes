# SQL, Oracle, PL/SQL & Sybase — 50 Senior Interview Questions

**Bar:** Plans, indexes, isolation, set-based thinking. Application developers who "just use JPA" fail this loop at banks.

---

### 1. What does an index actually store?

**Short answer:** An index is a separate, ordered data structure — usually a B+ tree — that maps indexed column values to row locators (Oracle ROWID, InnoDB PK leaf, Postgres heap TID). It lets the engine seek a narrow range instead of scanning the whole table, at the cost of extra storage and slower writes on every DML. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

An index is not a copy of the table; it is a lookup side structure. The optimizer chooses between index range scan, index-only scan, or full table scan based on selectivity, statistics, and cost model. Each additional index is a write amplifier.

#### How it works (internals)

B+ tree leaves hold sorted keys plus pointers to rows. Oracle heap tables store ROWIDs; InnoDB clustered PK stores the row in the leaf; Postgres stores heap TIDs that may need follow-up if the row moved (HOT updates help). A **covering index** includes all columns the query needs, enabling index-only access without touching the table block.

#### When to use / when NOT to use

Index columns used in selective `WHERE`, join keys, and FK columns. Avoid indexing low-cardinality flags alone, over-indexing write-heavy tables, or duplicating the same leading prefix across six indexes. Measure with actual plans, not guesswork.

#### Production example

Payments table `(customer_id, created_at)` composite index serves `WHERE customer_id = ? ORDER BY created_at DESC` for statement history. A separate index on `status` alone is dropped after AWR shows it is never used and slows nightly batch inserts.

#### Common mistakes

"Add an index on every column in the WHERE clause." Ignoring write-path cost on high-insert ledgers. Assuming an index is used because it exists — check `access` predicates in the plan, not just `INDEX RANGE SCAN` label. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** What is a function-based index and when would you use one?
**A:** For «What does an index actually store?», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Bitmap vs B-tree in Oracle — trade-offs?
**A:** On «Bitmap vs B-tree in Oracle — trade-offs», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** How does index clustering factor affect NL joins?
**A:** Trade-off answer for «How does index clustering factor affect NL joins»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «What does an index actually store?» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Payments table `(customer_id, created_at)` composite index serves `WHERE customer_id = ? ORDER BY created_at DESC` for statement history. A separate index on `status` alone is dropped after AWR shows . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
-- Covering index for a hot read path
CREATE INDEX ix_pay_cust_created ON payments (customer_id, created_at DESC)
  INCLUDE (amount, currency);  -- SQL Server syntax; Oracle: put cols in index
```

---

### 2. Clustered vs non-clustered (Oracle vs SQL Server vs Postgres).

**Short answer:** "Clustered" means the table's physical row order follows an index key — SQL Server and InnoDB cluster on the PK. Oracle defaults to heap tables; Postgres is heap plus separate indexes. Oracle **Index-Organized Tables** and the unrelated **CLUSTER** object are different beasts — speak the dialect of the job. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Clustering controls how rows are stored on disk relative to an index. It affects range scans, insert patterns, and fragmentation. Non-clustered indexes always require a lookup step to fetch the row (except covering cases).

#### How it works (internals)

**SQL Server / InnoDB:** PK is the clustered index — the table is the leaf of that B-tree. Secondary indexes point to clustered key. **Oracle:** heap by default; rows land wherever space exists; PK creates a unique index but not clustering unless IOT. **Postgres:** heap storage; `CLUSTER` command reorders once (not maintained). Oracle **CLUSTER** (old feature) co-locates rows from joined tables by cluster key — rare in modern designs.

#### When to use / when NOT to use

Clustered PK on monotonic insert keys (identity, sequence) can cause hot right-edge contention in some engines — consider hash partitioning or reverse key indexes in Oracle. IOT when table is mostly accessed via PK range and wide rows are acceptable overhead in the index leaf. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

Migrating Sybase ASE shop to Oracle: developers expect "clustered index on order_date" — in Oracle you use partitioning by month plus local indexes, not SQL Server-style clustering. Hibernate entity `@Id` maps to sequence; no clustered index concept in the ORM layer. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Using "cluster" terminology interchangeably across vendors. Rebuilding clustered indexes nightly on billion-row fact tables without online options. Assuming Postgres `CLUSTER` stays sorted after updates — it does not.

#### Interview follow-ups (with model answers)

**Q:** What is an Index-Organized Table in Oracle?
**A:** For «Clustered vs non-clustered (Oracle vs SQL Server vs Postgres).», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does heap vs clustered affect `ORDER BY` on PK?
**A:** On «How does heap vs clustered affect `ORDER BY` on PK», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Fragmentation symptoms and remediation per engine?
**A:** Trade-off answer for «Fragmentation symptoms and remediation per engine»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Clustered vs non-clustered (Oracle vs SQL Server vs Postgres).» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Migrating Sybase ASE shop to Oracle: developers expect "clustered index on order_date" — in Oracle you use partitioning by month plus local indexes, not SQL Server-style clustering. Hibernate entity `. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 3. Cardinality, selectivity, histograms.

**Short answer:** The optimizer estimates how many rows each predicate returns using table/index statistics: **cardinality** (distinct values), **selectivity** (fraction matching), and **histograms** for skewed columns. Wrong estimates pick nested loops on millions of rows or hash joins that spill to temp — disaster at scale. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Cost-based optimization depends on statistics, not magic. A column with two values (`ACTIVE`/`CLOSED`) may have 99% closed — equality on `OPEN` is highly selective; on `CLOSED` it is not. Without a histogram the optimizer assumes uniform distribution.

#### How it works (internals)

`DBMS_STATS.GATHER_TABLE_STATS` collects NDV, min/max, and histogram buckets (height-balanced or hybrid). Bind variable peeking (first execution value) and adaptive cursor sharing / adaptive plans adjust when estimates diverge from reality. Extended statistics capture column group correlations `(status, region)`.

#### When to use / when NOT to use

Gather stats after bulk load, partition exchange, or major data shape change. Use histograms on skewed non-uniform columns — not on every column (noise). For known skew, consider separate SQL for hot vs cold values instead of fighting the optimizer.

#### Production example

`orders.status` has 98% `SHIPPED`. Dashboard query `WHERE status = 'PENDING'` gets a frequency histogram; plan uses index range scan. Batch job `WHERE status = 'SHIPPED'` uses parallel full scan — two SQL IDs, not one bind-fits-all.

#### Common mistakes

Locking stats (`METHOD_OPT => 'FOR ALL COLUMNS SIZE 1'`) then wondering why plans are stale. Deleting stats to "force re-optimization." Ignoring E-Rows vs A-Rows mismatch in `DBMS_XPLAN` actuals. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** Bind peeking vs adaptive cursor sharing?
**A:** For «Cardinality, selectivity, histograms.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** When would you use a SQL profile or baseline?
**A:** On «When would you use a SQL profile or baseline», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Extended stats for correlated columns?
**A:** Trade-off answer for «Extended stats for correlated columns»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Cardinality, selectivity, histograms.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: `orders.status` has 98% `SHIPPED`. Dashboard query `WHERE status = 'PENDING'` gets a frequency histogram; plan uses index range scan. Batch job `WHERE status = 'SHIPPED'` uses parallel full scan — two. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
EXEC DBMS_STATS.GATHER_TABLE_STATS(
  ownname => 'APP', tabname => 'ORDERS',
  method_opt => 'FOR COLUMNS status SIZE AUTO'
);
```

---

### 4. Nested loop vs hash vs merge join.

**Short answer:** **Nested loop (NL)** drives from a small outer set and probes the inner via index — great for OLTP point lookups. **Hash join** builds a hash table on the smaller side — best for large equijoins without useful indexes. **Merge join** needs sorted inputs — efficient when both sides are already ordered or sort cost is acceptable. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. PL/SQL belongs where set-based SQL cannot express the rule or where you must keep logic colocated with data for performance.

#### What it is

Join algorithms are the heart of relational execution. The optimizer picks based on cardinality estimates, available indexes, memory (`pga_aggregate_target`), and hints. Wrong join method is the #1 cause of "query worked in dev, died in prod."

#### How it works (internals)

NL: for each outer row, index seek on inner — O(outer × log inner) with index; catastrophic without index (inner full scan per outer row). Hash: probe/build sides; spills to temp if memory insufficient (`TEMP TABLESPACE` growth). Merge: sort-merge on join keys; often appears with index full scan producing ordered output.

#### When to use / when NOT to use

NL when outer cardinality is small ( tens–thousands ) and inner is indexed. Hash for star-schema fact joins, ETL, large staging sets. Merge when both inputs pre-sorted on join key. Never accept NL with E-Rows outer=50 and A-Rows outer=5M without investigation.

#### Production example

Nightly reconciliation joins 20M staging rows to `accounts` on `account_no`. Hash join with parallel query completes in minutes. Accidental NL after stats loss runs 18 hours — fix: refresh stats, index on `account_no`, or `USE_HASH` hint while root-causing stats job.

#### Common mistakes

Adding an index "to help the join" that the optimizer ignores due to skew. Increasing PGA without fixing cartesian products. Using merge join hints on unsorted heap scans forcing expensive sorts.

#### Interview follow-ups (with model answers)

**Q:** What is a cartesian join and how does it appear in plans?
**A:** For «Nested loop vs hash vs merge join.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Hash join spill to disk — what wait events?
**A:** On «Hash join spill to disk — what wait events», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** When does Oracle pick NL vs hash for anti-joins?
**A:** Trade-off answer for «When does Oracle pick NL vs hash for anti-joins»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Nested loop vs hash vs merge join.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Nightly reconciliation joins 20M staging rows to `accounts` on `account_no`. Hash join with parallel query completes in minutes. Accidental NL after stats loss runs 18 hours — fix: refresh stats, inde. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 5. How to read an Oracle execution plan.

**Short answer:** Start with **actual** plans (`DBMS_XPLAN.DISPLAY_CURSOR` with `ALLSTATS LAST`), compare **A-Rows vs E-Rows** at each step, then trace join order, join method, access vs filter predicates, and expensive operations (full scans, sorts, temp). Estimated plans from `EXPLAIN PLAN` alone lie about cardinality and timing. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

The execution plan is a tree of operations the optimizer chose. Reading it is a core senior skill — not decorative DBA trivia. It connects SQL text to wait events and I/O.

#### How it works (internals)

Operations: `TABLE ACCESS FULL`, `INDEX RANGE SCAN`, `NESTED LOOPS`, `HASH JOIN`, etc. **Access predicates** use index structure; **filter predicates** discard rows after retrieval (often bad sign). `Starts`/`A-Rows`/`E-Rows` show per-execution iteration counts. `LAST` stats require `STATISTICS_LEVEL=ALL` or `GATHER_PLAN_STATISTICS` hint for the run.

#### When to use / when NOT to use

Always fetch actuals for production troubleshooting. Use `EXPLAIN PLAN` only for quick syntax checks or when you cannot run the query. Pair plan reading with ASH/AWR for wait class (`db file sequential read`, `direct path read temp`).

#### Production example

Slow API query: `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(:sql_id, NULL, 'ALLSTATS LAST'))`. Step 4 shows `HASH JOIN` E-Rows 1K A-Rows 2.3M — stats on `line_items` stale. `GATHER_TABLE_STATS` fixes plan; API p99 drops from 8s to 40ms.

#### Common mistakes

Reading top-to-bottom as execution order (it's a tree — inner/child operations first). Ignoring filter predicates on indexed columns. Stopping at "INDEX RANGE SCAN" without checking if most rows are filtered out afterward.

#### Interview follow-ups (with model answers)

**Q:** Difference between `EXPLAIN PLAN` and `V$SQL_PLAN`?
**A:** For «How to read an Oracle execution plan.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** What does `BUFFER SORT` in a plan mean?
**A:** On «What does `BUFFER SORT` in a plan mean», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «How to read an Oracle execution plan.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Slow API query: `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(:sql_id, NULL, 'ALLSTATS LAST'))`. Step 4 shows `HASH JOIN` E-Rows 1K A-Rows 2.3M — stats on `line_items` stale. `GATHER_TABLE_STATS` fix. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY_CURSOR(
  :sql_id, NULL, 'ALLSTATS LAST +PEEKED_BINDS'
));
```

---

### 6. Bind variables vs literals.

**Short answer:** **Bind variables** enable cursor sharing, reduce parse CPU, and prevent SQL injection — Hibernate uses them by default. **Literals** expose each value to the optimizer for better skew plans but cause parse storms and cache bloat. Production systems mix both: binds for OLTP volume, literal variants or adaptive features for skewed admin queries. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

A bind is a placeholder (`:status`) filled at execute time; a literal embeds the value in SQL text (`status = 'OPEN'`). This choice affects security, performance, and plan stability across Oracle, Sybase, and JDBC stacks. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle shared pool stores parent/child cursors. Identical SQL text shares; binds differ per execution. Bind peeking uses first bind values for plan; adaptive cursor sharing may keep multiple plans. `CURSOR_SHARING=FORCE` replaces literals with binds (blunt instrument). JDBC `PreparedStatement` binds; dynamic string concat in app code defeats this.

#### When to use / when NOT to use

Binds for all user-facing OLTP paths. Consider literal SQL or SQL plan baselines for known skew (reporting on one status value). Never concatenate user input — binds or strict validation only.

#### Production example

Banking portal: 10K TPS on `SELECT ... WHERE account_id = :id` — single shared cursor. Monthly compliance report runs `WHERE region = 'EMEA'` as literal with its own plan and baseline — documented exception, not the default pattern.

#### Common mistakes

`cursor_sharing=force` masking app bugs that generate thousands of literal SQL variants. Disabling binds in Hibernate for "better plans" globally. Not logging bind values in trace (use `sql_trace`, ASH) when debugging skew.

#### Interview follow-ups (with model answers)

**Q:** Adaptive cursor sharing vs SQL plan baselines?
**A:** For «Bind variables vs literals.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does bind peeking interact with histograms?
**A:** On «How does bind peeking interact with histograms», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Sybase/jConnect prepared statement behavior?
**A:** Trade-off answer for «Sybase/jConnect prepared statement behavior»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Bind variables vs literals.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Banking portal: 10K TPS on `SELECT ... WHERE account_id = :id` — single shared cursor. Monthly compliance report runs `WHERE region = 'EMEA'` as literal with its own plan and baseline — documented exc. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 7. `WHERE` on a leading column of a composite index.

**Short answer:** Composite index `(a, b, c)` is usable when the predicate provides a leading prefix: `a = ?` works; `a = ? AND b = ?` works; `b = ?` alone generally does not (index skip scan is rare and costly). Design indexes with equality columns first, then range columns, then columns needed for `ORDER BY`. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

B-tree indexes are sorted lexicographically on `(col1, col2, ...)`. The left-prefix rule determines whether the index can narrow the search or whether the engine must scan a wide portion / skip to table. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`WHERE a = 1 AND b > 10 AND c = 5` uses `a` for range start, `b` for range within `a`, but typically cannot use `c` for index access (filter only). `ORDER BY b` may avoid sort if `a` is equality and `b` matches index order. Index skip scan (Oracle) probes each distinct leading value — viable only with very few distinct `a` values.

#### When to use / when NOT to use

Put highest-selectivity equality filters leftmost. Avoid one mega-index `(a,b,c,d,e)` that serves every report — write amplification kills OLTP. Sometimes two targeted indexes beat one "god index."

#### Production example

Index `(customer_id, status, created_at DESC)` serves `WHERE customer_id = ? AND status = 'OPEN' ORDER BY created_at DESC` without sort. Query filtering only `status = 'OPEN'` across all customers cannot use this index efficiently — needs different access path or materialized view.

#### Common mistakes

Reversing column order because "status is more selective" without checking query shapes. Creating `(created_at, customer_id)` when every query filters `customer_id` first. Expecting index use for `OR` across non-leading columns.

#### Interview follow-ups (with model answers)

**Q:** Index merge/intersection vs composite index?
**A:** For «`WHERE` on a leading column of a composite index.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does a trailing `ORDER BY` interact with range predicates?
**A:** On «How does a trailing `ORDER BY` interact with range predicates», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Partial indexes (Postgres) vs function-based (Oracle)?
**A:** Trade-off answer for «Partial indexes (Postgres) vs function-based (Oracle)»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`WHERE` on a leading column of a composite index.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Index `(customer_id, status, created_at DESC)` serves `WHERE customer_id = ? AND status = 'OPEN' ORDER BY created_at DESC` without sort. Query filtering only `status = 'OPEN'` across all customers can. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 8. Functions on columns kill indexes.

**Short answer:** Wrapping an indexed column in a function (`UPPER(name)`, `TRUNC(created_at)`) prevents a normal index seek unless you add a **function-based index** or **virtual column** indexed on the expression. Same trap for implicit conversions (`WHERE varchar_col = 123`). Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Indexes are keyed on stored column values. Applying a function at query time changes the search key, so the B-tree on the raw column no longer applies. This is one of the most common accidental full-scan causes in enterprise apps.

#### How it works (internals)

Oracle function-based indexes store `UPPER(name)` in the index tree. Virtual columns (`name_upper GENERATED ALWAYS AS (UPPER(name))`) keep app SQL readable. Postgres expression indexes serve the same role. Range on dates: prefer `created_at >= :d AND created_at < :d+1` over `TRUNC(created_at) = :d`.

#### When to use / when NOT to use

Function-based index when the expression is selective and query volume justifies write cost. Prefer sargable rewrite first (range instead of truncate). Avoid indexing `LOWER(email)` when app can normalize on insert.

#### Production example

Login lookup used `WHERE LOWER(email) = LOWER(:email)` — full scan on 50M users. Fix: persist `email_normalized` with unique index; app writes uppercase on insert. Removed FBI after migration; simpler stats and constraints.

#### Common mistakes

FBI on non-deterministic functions (not allowed / unstable). Indexing `TO_CHAR(date)` for reporting instead of partitioning by date. Java-side formatting dates into strings in SQL strings.

#### Interview follow-ups (with model answers)

**Q:** Implicit conversion between VARCHAR2 and NUMBER in Oracle?
**A:** For «Functions on columns kill indexes.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Virtual column vs FBI maintenance?
**A:** On «Virtual column vs FBI maintenance», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Case-insensitive search alternatives (CI collations)?
**A:** Trade-off answer for «Case-insensitive search alternatives (CI collations)»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Functions on columns kill indexes.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Login lookup used `WHERE LOWER(email) = LOWER(:email)` — full scan on 50M users. Fix: persist `email_normalized` with unique index; app writes uppercase on insert. Removed FBI after migration; simpler. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
CREATE INDEX ix_cust_email_upper ON customers (UPPER(email));
-- or
ALTER TABLE customers ADD (email_upper AS (UPPER(email)) VIRTUAL);
CREATE UNIQUE INDEX ux_cust_email_upper ON customers (email_upper);
```

---

### 9. SARGability.

**Short answer:** **SARGable** (Search ARGument able) predicates let the optimizer use an index: `col =`, `col >`, `col LIKE 'ABC%'`. Non-sargable patterns — `%ABC` wildcards, `col + 1 = 5`, functions on columns — force scans or filter-after-read. Write SQL the index can seek, not SQL that looks clever. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

SARGability is the bridge between SQL you write and physical access paths. ORMs often generate non-sargable SQL via `DATE(created)` functions or `LIKE '%' || :term || '%'` search boxes. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

The optimizer's index range scan needs a bounded prefix of the search key. Leading wildcard LIKE breaks prefix. Arithmetic on column side (`amount + fee > 100`) prevents index use on `amount`. Rewriting to `amount > 100 - fee` is sargable if `fee` is constant/bind.

#### When to use / when NOT to use

Design search UX knowing `%term%` needs Full Text / Oracle Text / Elasticsearch — not B-tree index hope. For datetime boundaries use half-open ranges. Document non-sargable report queries as batch/warehouse paths.

#### Production example

Product search MVP used `LIKE '%phone%'` — p95 12s. Moved fuzzy search to OpenSearch; SQL keeps sargable filters `category_id = ? AND price BETWEEN ? AND ?` on indexed columns only.

#### Common mistakes

" We'll add Elasticsearch later" while burning DB CPU on `%like%`. Using `NVL(col, 'X') = 'Y'` instead of `(col = 'Y' OR col IS NULL)` with separate plan consideration. COALESCE on indexed column in WHERE.

#### Interview follow-ups (with model answers)

**Q:** Is `IN (list)` sargable?
**A:** For «SARGability.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** OR expansion and index merge costs?
**A:** On «OR expansion and index merge costs», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** How do histograms interact with non-sargable filters?
**A:** Trade-off answer for «How do histograms interact with non-sargable filters»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «SARGability.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Product search MVP used `LIKE '%phone%'` — p95 12s. Moved fuzzy search to OpenSearch; SQL keeps sargable filters `category_id = ? AND price BETWEEN ? AND ?` on indexed columns only. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 10. Isolation levels and anomalies.

**Short answer:** Isolation levels trade concurrency for consistency. **Read Committed** (Oracle default) prevents dirty reads but allows non-repeatable reads and phantoms. **Serializable** prevents anomalies but increases blocking/retries. Oracle implements RC via MVCC (undo); Sybase/SQL Server historically used more locking — know your engine's real behavior, not the textbook chart alone. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Anomalies: **dirty read** (see uncommitted), **non-repeatable read** (same row changes between reads in TX), **phantom** (new rows appear in range). Isolation level names are standardized; implementations differ — especially Oracle vs Sybase. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

| Level | Dirty read | Non-repeatable | Phantom |
|-------|------------|----------------|---------|
| Read Uncommitted | yes | yes | yes |
| Read Committed | no | yes | yes |
| Repeatable Read | no | no | depends |
| Serializable | no | no | no |

Oracle: statement-level read consistency in RC; each statement sees snapshot as of statement start. Writers generate undo; readers don't block writers. Sybase ASE / SQL Server: locking readers/writers unless **RCSI** (row versioning). `SET TRANSACTION ISOLATION LEVEL` in JDBC changes behavior — test, don't assume.

#### When to use / when NOT to use

RC for most OLTP. RR/Serializable for financial invariants where phantom must be prevented — expect `ORA-08177` / deadlocks / retries. Never use Sybase `NOLOCK` as a "isolation level" for money (see Q43).

#### Production example

Transfer between accounts: `@Transactional` + `SELECT ... FOR UPDATE` on both rows in consistent order — app-level pattern on Oracle RC. Reporting replica uses read-only connection with snapshot export, not `NOLOCK` on primary.

#### Common mistakes

Believing Oracle RR equals ANSI RR (it uses SCN snapshots differently). Running long reports on primary with default isolation holding undo. Mixing isolation levels across connection pool without documentation.

#### Interview follow-ups (with model answers)

**Q:** Oracle vs Postgres MVCC implementation?
**A:** For «Isolation levels and anomalies.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** What is RCSI in SQL Server?
**A:** On «What is RCSI in SQL Server», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Isolation levels and anomalies.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Transfer between accounts: `@Transactional` + `SELECT ... FOR UPDATE` on both rows in consistent order — app-level pattern on Oracle RC. Reporting replica uses read-only connection with snapshot expor. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 11. Oracle MVCC / undo / "snapshot too old".

**Short answer:** Oracle readers don't lock writers; they reconstruct past block images from **undo** (rollback segments) to present a consistent snapshot. Long-running queries plus heavy DML exhaust undo or discard needed versions → **ORA-01555 snapshot too old**. Fix undo sizing, shorten transactions, fetch faster, or use read-only replicas — not "just retry." Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Multi-Version Concurrency Control in Oracle is undo-based, not row-version storage like Postgres. Undo retention must cover the longest snapshot any session needs — including open cursors slowly fetching in JDBC. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

DML replaces row pieces and stores old values in undo segments. A query's SCN determines which version to assemble. `UNDO_RETENTION` is a target; space pressure causes undo to be overwritten early. `v$undostat`, AWR undo reports show contention. Active undo from long TX blocks reuse.

#### When to use / when NOT to use

Size undo for peak DML + longest report (or move reports to standby). Use `@Transactional(readOnly=true)` with fetch size tuned — but read-only TX still holds snapshot. For ETL, use direct-path or partition exchange to reduce undo volume.

#### Production example

Nightly batch updates 10M `transactions` while finance runs 2-hour JDBC report with default fetch size 10 — ORA-01555 at hour 1.5. Fix: increase undo tablespace, `setFetchSize(1000)`, run report on Active Data Guard standby. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Blaming ORA-01555 on "Oracle bug" when app holds ResultSet open across user think time. Setting absurd `UNDO_RETENTION` without disk space. Not monitoring `long running` SQL in ASH.

#### Interview follow-ups (with model answers)

**Q:** Difference between undo and redo?
**A:** For «Oracle MVCC / undo / "snapshot too old".», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does flashback query relate to undo?
**A:** On «How does flashback query relate to undo», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Read consistency at statement vs transaction level?
**A:** Trade-off answer for «Read consistency at statement vs transaction level»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Oracle MVCC / undo / "snapshot too old".» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Nightly batch updates 10M `transactions` while finance runs 2-hour JDBC report with default fetch size 10 — ORA-01555 at hour 1.5. Fix: increase undo tablespace, `setFetchSize(1000)`, run report on Ac. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 12. Lost update.

**Short answer:** Two sessions read the same value, both increment, both write — one update is lost. **Read Committed does not prevent lost updates** by itself. Fix with optimistic locking (`version` column), atomic `UPDATE ... SET bal = bal + :delta`, or pessimistic `SELECT FOR UPDATE`. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Lost update is a write-write conflict invisible to isolation level names alone. It is rampant in REST APIs that do read-modify-write without concurrency control — especially under load. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Session A: `SELECT balance → 100`. Session B: `SELECT balance → 100`. A: `UPDATE SET balance=120`. B: `UPDATE SET balance=120` (should be 140). Optimistic: `UPDATE ... SET balance=120, version=6 WHERE id=1 AND version=5` — zero rows updated triggers retry. Pessimistic: lock row on read.

#### When to use / when NOT to use

Optimistic for low contention user edits. Pessimistic for ledger postings, inventory deduction, seat booking. Never rely on "we're single threaded" in clustered app servers.

#### Production example

Wallet service uses `UPDATE wallets SET balance = balance - :amt, version = version + 1 WHERE id = :id AND version = :expected`. JPA `@Version` maps column; conflict → `OptimisticLockException` → UI retry. Zero lost updates at 2K TPS.

#### Common mistakes

Read-modify-write in Java without version check. `SELECT FOR UPDATE` forgotten on one code path in saga. Caching entity in session across long user forms then blind save.

#### Interview follow-ups (with model answers)

**Q:** Compare optimistic vs pessimistic in Spring `@Transactional`?
**A:** For «Lost update.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does lost update differ from write skew?
**A:** On «How does lost update differ from write skew», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Idempotent updates with natural keys?
**A:** Trade-off answer for «Idempotent updates with natural keys»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Lost update.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Wallet service uses `UPDATE wallets SET balance = balance - :amt, version = version + 1 WHERE id = :id AND version = :expected`. JPA `@Version` maps column; conflict → `OptimisticLockException` → UI r. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
UPDATE accounts
   SET balance = balance + :delta, version = version + 1
 WHERE account_id = :id AND version = :expected;
-- rows updated = 0 → conflict
```

---

### 13. `SELECT FOR UPDATE` vs `SKIP LOCKED` vs `NOWAIT`.

**Short answer:** **`FOR UPDATE`** locks selected rows for the transaction — queue behavior when contended. **`NOWAIT`** fails immediately if lock held (`ORA-00054`). **`SKIP LOCKED`** (Oracle 11g+, Postgres) skips locked rows — ideal for work-queue workers competing for jobs without blocking. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. PL/SQL belongs where set-based SQL cannot express the rule or where you must keep logic colocated with data for performance.

#### What it is

Row-locking clauses implement pessimistic concurrency patterns at the database. They are the correct primitive for job queues, inventory holds, and serializing updates — not ad hoc `sleep` in Java. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`SELECT ... FOR UPDATE` takes TX locks; others wait (or timeout with `WAIT n`). `SKIP LOCKED` returns only unlocked rows — multiple workers dequeue different jobs safely in one statement. `NOWAIT` for fail-fast UX ("account busy"). Lock on indexed PK — or you lock more rows than intended.

#### When to use / when NOT to use

SKIP LOCKED for async worker pools (`job_queue` pattern). FOR UPDATE when business requires all-or-nothing row set (transfer both legs). NOWAIT for interactive "try lock" flows. Don't FOR UPDATE in read-only reports.

#### Production example

Payment reconciliation workers: `SELECT id FROM jobs WHERE status='PENDING' ORDER BY created_at FETCH FIRST 1 ROW ONLY FOR UPDATE SKIP LOCKED`. Each pod grabs distinct rows; no `ORA-00054` storm. Completed jobs commit status update in same TX.

#### Common mistakes

FOR UPDATE without index → table lock escalation risk on some engines. Holding locks while calling external HTTP inside `@Transactional`. SKIP LOCKED without `ORDER BY` → starvation.

#### Interview follow-ups (with model answers)

**Q:** `FOR UPDATE OF` column semantics?
**A:** For «`SELECT FOR UPDATE` vs `SKIP LOCKED` vs `NOWAIT`.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does this interact with connection pool and lock timeout?
**A:** On «How does this interact with connection pool and lock timeout», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Queue implementation vs Kafka for work distribution?
**A:** Trade-off answer for «Queue implementation vs Kafka for work distribution»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`SELECT FOR UPDATE` vs `SKIP LOCKED` vs `NOWAIT`.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Payment reconciliation workers: `SELECT id FROM jobs WHERE status='PENDING' ORDER BY created_at FETCH FIRST 1 ROW ONLY FOR UPDATE SKIP LOCKED`. Each pod grabs distinct rows; no `ORA-00054` storm. Comp. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
SELECT id FROM job_queue
 WHERE status = 'READY'
 ORDER BY priority, id
 FETCH FIRST 10 ROWS ONLY
 FOR UPDATE SKIP LOCKED;
```

---

### 14. Deadlocks.

**Short answer:** Deadlock is circular wait — session A locks row 1 waits for row 2 while B locks row 2 waits for row 1. Oracle detects and kills one session (`ORA-00060`). Prevention: **consistent lock ordering**, shorter transactions, index rows so you lock only what you need, and **app-level retry** on deadlock. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Deadlocks are a normal outcome of concurrent locking, not necessarily a "bug" — but predictable patterns are fixable. Trace files and ASH show the cycle; juniors blame Oracle instead of lock order. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle's deadlock detector runs periodically; victim session gets ORA-00060 and rollback. Lock modes escalate with `FOR UPDATE`, FK checks, unindexed FK on parent delete. Sybase/SQL Server similar with different error codes. Graph: who waits on whom in `v$session` / `dba_blockers`.

#### When to use / when NOT to use

Always acquire locks in global order (parent account before child ledger entries). Split hot rows to reduce contention. Retry with exponential backoff in service layer for transient deadlocks — idempotent operations only.

#### Production example

Two transfers A→B and B→A concurrently deadlocked when code locked accounts by insertion order. Fix: `ORDER BY account_id` before `FOR UPDATE` in both code paths — deadlocks drop to zero in load test. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Random lock order across microservices touching same rows. Long TX holding locks while publishing to Kafka. Ignoring unindexed FK causing table-level lock surprises (Oracle parent delete).

#### Interview follow-ups (with model answers)

**Q:** How to read Oracle deadlock trace (deadlock graph)?
**A:** For «Deadlocks.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Difference between deadlock and lock timeout?
**A:** On «Difference between deadlock and lock timeout», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Does index column order affect row lock granularity?
**A:** Trade-off answer for «Does index column order affect row lock granularity»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Deadlocks.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Two transfers A→B and B→A concurrently deadlocked when code locked accounts by insertion order. Fix: `ORDER BY account_id` before `FOR UPDATE` in both code paths — deadlocks drop to zero in load test. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 15. Transactions: commit, rollback, autocommit.

**Short answer:** A transaction groups DML into one atomic unit — **commit** makes changes visible and releases locks; **rollback** undoes. JDBC **autocommit=true** (default) makes every statement its own transaction — death for multi-step business ops. Spring `@Transactional` defines boundaries; Oracle **DDL auto-commits** — a footgun in migration scripts. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Transaction boundaries define consistency and durability guarantees with redo/undo. Misaligned boundaries cause partial updates, connection pool leaks, and "it worked in the debugger" failures under load. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle: implicit commit on DDL (`CREATE`, `ALTER`, some `TRUNCATE`). Sybase: explicit `BEGIN TRAN` / `COMMIT` / `ROLLBACK`; batch separators `GO`. Spring: proxy wraps service method; rollback on runtime exceptions by default (not checked). Propagation `REQUIRES_NEW` spawns separate TX — know nested commit semantics.

#### When to use / when NOT to use

One `@Transactional` per business use case on the service layer. Never commit in a loop (log sync flush per row). Read-only TX for queries that must be consistent snapshot. Split long batch into chunks with commit between — but design idempotency.

#### Production example

Order placement: single `@Transactional` inserts order, lines, inventory hold, outbox row — one commit or full rollback. Removed `@Transactional` from repository layer that accidentally opened nested transactions and partial commits on failure. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Autocommit left on in batch jobs. Swallowing exception without rollback. Running DDL in flyway/Liquibase mid-app TX expecting rollback. Chatty commits on high-TPS API (redo log flood).

#### Interview follow-ups (with model answers)

**Q:** Spring propagation and isolation defaults?
**A:** For «Transactions: commit, rollback, autocommit.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Savepoints — when useful?
**A:** On «Savepoints — when useful», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Transactions: commit, rollback, autocommit.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Order placement: single `@Transactional` inserts order, lines, inventory hold, outbox row — one commit or full rollback. Removed `@Transactional` from repository layer that accidentally opened nested . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 16. Normalization vs denormalization.

**Short answer:** **Normalization** (typically 3NF) eliminates redundancy and update anomalies — one fact, one place. **Denormalization** duplicates data for read performance but requires a defined update path. Denormalize deliberately for read models (projections, reporting), not lazily because JOINs feel hard. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Schema design balances write correctness vs read speed. Banks often have normalized OLTP cores plus denormalized reporting marts fed by ETL or events — not random duplicate columns without ownership. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

3NF: non-key attributes depend on key, not on other non-keys. Denormalized `order_total` on header avoids summing lines — but who updates it when line changes? Triggers (risky), app service, or materialized view refresh. Event-driven read models duplicate `customerName` on orders — bounded consistency.

#### When to use / when NOT to use

Normalize money paths and regulatory data. Denormalize read-heavy dashboards with clear refresh SLA. Never denormalize without measuring JOIN cost — SSD and hash joins solve many "problems."

#### Production example

OLTP `orders` + `order_lines` normalized. Reporting star schema nightly load denormalizes dimensions. API read model table `order_summary` updated from outbox consumer — not trigger-maintained copy on OLTP row.

#### Common mistakes

Denormalizing every FK into wide tables "for Hibernate." No strategy when duplicate copies diverge. 1NF violations storing CSV in a column because normalization is "slow." Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** BCNF and when it matters?
**A:** For «Normalization vs denormalization.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Materialized view vs denormalized column?
**A:** On «Materialized view vs denormalized column», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** CQRS read model ownership?
**A:** Trade-off answer for «CQRS read model ownership»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Normalization vs denormalization.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: OLTP `orders` + `order_lines` normalized. Reporting star schema nightly load denormalizes dimensions. API read model table `order_summary` updated from outbox consumer — not trigger-maintained copy on. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 17. Surrogate vs natural keys.

**Short answer:** **Surrogate keys** (sequence, UUID) are stable, narrow FKs with no business meaning. **Natural keys** (ISBN, country code) encode domain identity but can change or be composite-fat. Best practice: surrogate PK plus **unique constraint** on natural business key. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Primary key choice affects every FK index, JOIN width, and ORM mapping. Composite natural PKs `(tenant_id, legacy_code)` propagate to child tables — painful at scale. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Surrogate: `NUMBER` sequence / `IDENTITY` / UUID — immutable. Natural: meaningful, may need update (`email` change) cascading FKs. Oracle sequences gap on rollback — acceptable. UUID as PK causes index fragmentation — consider `SYS_GUID()` vs sequential IDs for hot inserts.

#### When to use / when NOT to use

Surrogate for internal entities and high-volume OLTP. Expose natural keys in APIs (`orderNumber`) without using them as PK unless domain demands. Global UUID when merging distributed writes — else sequence + shard prefix.

#### Production example

`customers.id` sequence PK; `UNIQUE (tenant_id, external_crm_id)` for integration. Hibernate `@Id @GeneratedValue` on surrogate; business lookups use natural unique index — email change updates one row, FKs untouched. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Using email as PK. UUID v4 random clustering on B-tree (insert hot spot mitigation: sequential UUID or IDENTITY). No unique constraint on natural key → duplicate business rows.

#### Interview follow-ups (with model answers)

**Q:** UUID vs sequence in microservices?
**A:** For «Surrogate vs natural keys.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Composite keys in JPA — pain points?
**A:** On «Composite keys in JPA — pain points», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Surrogate key exposure in REST — security?
**A:** Trade-off answer for «Surrogate key exposure in REST — security»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Surrogate vs natural keys.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: `customers.id` sequence PK; `UNIQUE (tenant_id, external_crm_id)` for integration. Hibernate `@Id @GeneratedValue` on surrogate; business lookups use natural unique index — email change updates one ro. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 18. Nulls: three-valued logic.

**Short answer:** SQL uses **TRUE, FALSE, UNKNOWN** — any comparison with `NULL` yields UNKNOWN, filtered out by `WHERE`. Write `IS NULL`, not `= NULL`. **`NOT IN (subquery)`** fails if subquery returns NULL. Oracle unique indexes allow multiple NULLs (version-dependent nuances) — know your rules. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

NULL means missing/unknown, not zero or empty string. Three-valued logic breaks boolean intuition from Java — especially combined with `NOT`, `AND`, `OR`, and outer joins. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`WHERE col = NULL` never true. `UNKNOWN AND TRUE` is UNKNOWN. `NOT IN (1,2,NULL)` → UNKNOWN for all rows — empty result set surprise. Oracle: empty string `''` is NULL historically — unique constraint pain vs other DBs. `COALESCE`, `NVL` convert NULL to value for display, not always for index use.

#### When to use / when NOT to use

Explicit `IS NULL` / `IS NOT NULL`. Prefer `NOT EXISTS` over `NOT IN` when NULLs possible. Use `NOT NULL` constraints on required business fields at schema level — don't rely on app validation alone.

#### Production example

Blacklist query rewritten from `id NOT IN (SELECT blocked_id FROM blocks)` to `NOT EXISTS (SELECT 1 FROM blocks b WHERE b.blocked_id = u.id)` after NULL `blocked_id` rows caused "nobody matches" production incident. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

`= NULL` in legacy SQL. Aggregates: `COUNT(*)` vs `COUNT(col)` — NULLs excluded in latter. JPA `Optional` mapping confusion with primitive wrappers.

#### Interview follow-ups (with model answers)

**Q:** Oracle empty string vs NULL?
**A:** For «Nulls: three-valued logic.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How do outer joins generate NULL-related bugs?
**A:** On «How do outer joins generate NULL-related bugs», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Filtered/partial unique indexes with NULL?
**A:** Trade-off answer for «Filtered/partial unique indexes with NULL»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Nulls: three-valued logic.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Blacklist query rewritten from `id NOT IN (SELECT blocked_id FROM blocks)` to `NOT EXISTS (SELECT 1 FROM blocks b WHERE b.blocked_id = u.id)` after NULL `blocked_id` rows caused "nobody matches" produ. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 19. `NOT IN` vs `NOT EXISTS` vs anti-join.

**Short answer:** Semantically similar for non-null sets, but **`NOT IN` breaks on NULL** in the subquery list. **`NOT EXISTS`** is NULL-safe and usually preferred. Optimizer often rewrites to **hash anti-join** (`ANTI`) — same performance when written correctly. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Anti-join patterns answer "rows in A with no match in B." Choice affects correctness first, performance second — a fast wrong answer is still wrong. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`NOT IN`: compares to each subquery value; one NULL → entire predicate UNKNOWN. `NOT EXISTS`: correlated semijoin negation — stops at first match, NULL-safe. Oracle may produce `HASH JOIN ANTI NA` or `NESTED LOOPS ANTI`. `LEFT JOIN ... WHERE b.key IS NULL` equivalent — sometimes clearer in analytics SQL.

#### When to use / when NOT to use

Default to `NOT EXISTS` or explicit `NOT IN` only with `NOT NULL` constraint on subquery column. Anti-join rewrite for large fact tables with stats. Avoid correlated `NOT EXISTS` without index on inner join key.

#### Production example

Find active customers with no orders in 90 days: `NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.created_at > SYSDATE - 90)` — indexed on `(customer_id, created_at)`. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Copy-paste `NOT IN` from Stack Overflow without NULL audit. Assuming `NOT IN` and `NOT EXISTS` always same plan — check actuals. Using `!= ALL` (same NULL trap).

#### Interview follow-ups (with model answers)

**Q:** Semi-join vs anti-join in execution plans?
**A:** For «`NOT IN` vs `NOT EXISTS` vs anti-join.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Rewrite NOT EXISTS to LEFT JOIN — when?
**A:** On «Rewrite NOT EXISTS to LEFT JOIN — when», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** NULL-safe `<>` patterns?
**A:** Trade-off answer for «NULL-safe `<>` patterns»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`NOT IN` vs `NOT EXISTS` vs anti-join.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Find active customers with no orders in 90 days: `NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.created_at > SYSDATE - 90)` — indexed on `(customer_id, created_at)`. Capture AWR/. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 20. Window functions.

**Short answer:** Window functions compute aggregates/rankings **over a partition without collapsing rows** — `ROW_NUMBER() OVER (PARTITION BY customer ORDER BY created DESC)` picks latest per group in one pass. Replace Java "fetch all then pick max" with set-based SQL — fewer round trips, correct semantics. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Analytics and OLTP both use windows: running totals, moving averages, deduplication, gap detection. Oracle supports rich window framing (`ROWS BETWEEN`, `RANGE BETWEEN`). This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`OVER (PARTITION BY ... ORDER BY ...)` defines window; `ROW_NUMBER`, `RANK`, `DENSE_RANK`, `LAG`, `LEAD`, `SUM() OVER`. Filter via subquery `WHERE rn = 1` (Oracle 12c+ qualify clause in some engines). Unlike `GROUP BY`, input row count preserved until outer filter.

#### When to use / when NOT to use

Latest-per-partition, cumulative balances, sessionization. Prefer windows over correlated subqueries when readability and single-scan matter. For huge partitions, ensure supporting index on `(partition_key, order_key)`.

#### Production example

Duplicate detection: `ROW_NUMBER() OVER (PARTITION BY external_id ORDER BY updated_at DESC) rn` → delete where rn > 1 in batch job. API "latest status per account" uses same pattern instead of N+1 per account in Java. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Forgetting `ORDER BY` in window → random row numbered 1. Confusing `RANK` ties vs `ROW_NUMBER`. Selecting `*` with window in view without filtering — perf surprise.

#### Interview follow-ups (with model answers)

**Q:** Frame clause ROWS vs RANGE?
**A:** For «Window functions.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Window functions vs `KEEP (DENSE_RANK FIRST ORDER BY ...)`?
**A:** On «Window functions vs `KEEP (DENSE_RANK FIRST ORDER BY ...)`», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Window functions.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Duplicate detection: `ROW_NUMBER() OVER (PARTITION BY external_id ORDER BY updated_at DESC) rn` → delete where rn > 1 in batch job. API "latest status per account" uses same pattern instead of N+1 per. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
SELECT customer_id, order_id, total
  FROM (
    SELECT o.*, ROW_NUMBER() OVER (
      PARTITION BY customer_id ORDER BY created_at DESC
    ) rn FROM orders o
  ) WHERE rn = 1;
```

---

### 21. `GROUP BY` and `HAVING`.

**Short answer:** **`WHERE`** filters rows before aggregation; **`HAVING`** filters groups after `GROUP BY`. Select list must contain grouped columns or aggregates (Oracle/MySQL strict modes vary). Putting non-aggregated columns in SELECT without grouping is a logic bug masked by deprecated permissive modes. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Aggregation collapses many rows to groups — `COUNT`, `SUM`, `AVG`. `HAVING COUNT(*) > 10` answers questions about group properties, not row properties (`WHERE status = 'OPEN'` first). This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Optimizer may rewrite to hash aggregation or sort group by. Filter early in `WHERE` reduces rows aggregated — cheaper than `HAVING` on same predicate when possible (`WHERE status='OPEN'` not `HAVING MAX(status)='OPEN'` unless needed). `ROLLUP`, `CUBE`, `GROUPING SETS` for report subtotals.

#### When to use / when NOT to use

`HAVING` for conditions on aggregates (`SUM(amount) > 1000`). Move static filters to `WHERE`. For distinct counts on huge sets, consider approximate algorithms or pre-aggregates.

#### Production example

Daily fraud alert: `SELECT merchant_id, SUM(amount) total FROM tx WHERE tx_date = TRUNC(SYSDATE) GROUP BY merchant_id HAVING SUM(amount) > :threshold` — index on `(tx_date, merchant_id)` feeds aggregation. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Filtering with `HAVING column = 'X'` when `WHERE` suffices. `SELECT customer_id, status, COUNT(*)` without grouping `status` — ambiguous which status shown. Confusing `COUNT(*)` with `COUNT(DISTINCT ...)`.

#### Interview follow-ups (with model answers)

**Q:** DISTINCT vs GROUP BY equivalence?
**A:** For «`GROUP BY` and `HAVING`.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Group by on indexed columns — sort avoidance?
**A:** On «Group by on indexed columns — sort avoidance», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Filtered aggregates in Oracle 12c+?
**A:** Trade-off answer for «Filtered aggregates in Oracle 12c+»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`GROUP BY` and `HAVING`.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Daily fraud alert: `SELECT merchant_id, SUM(amount) total FROM tx WHERE tx_date = TRUNC(SYSDATE) GROUP BY merchant_id HAVING SUM(amount) > :threshold` — index on `(tx_date, merchant_id)` feeds aggrega. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 22. CTE vs subquery vs temp table.

**Short answer:** **CTEs** (`WITH`) improve readability; Oracle may inline or materialize (`MATERIALIZE` hint). **Subqueries** in FROM/WHERE are often equivalent after rewrite. **Global temp / `#temp` tables** (Sybase/SQL Server) or GTT (Oracle) help when you need stats, indexes, or multi-step reuse on large intermediates — don't stack 12 CTEs each scanning the fact table. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. PL/SQL belongs where set-based SQL cannot express the rule or where you must keep logic colocated with data for performance.

#### What it is

Choice of SQL structure affects optimizer visibility, temp space, and maintainability. Recursive CTEs (`CONNECT BY` legacy in Oracle) express hierarchies. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle 12c+: inline CTE by default unless `MATERIALIZE` hint or optimizer choice — materialization writes temp, can help or hurt. Postgres CTE optimization improved (not always optimization fence). Sybase `#temp` in tempdb with optional indexes and stats updates.

#### When to use / when NOT to use

CTE for readable multi-step reports. Temp table when intermediate is large, reused, or needs index for join. Avoid deep CTE chains that obscure one full scan per level — flatten or stage.

#### Production example

Risk report stages 5M eligible trades into `GTT_STAGING` with index on `account_id`, then joins to dimensions — one scan of fact. Replacing earlier 8-CTE query cut runtime 70% after `DBMS_XPLAN` showed repeated full scans. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Assuming CTE always runs once (Oracle inlines and rescans). No stats on GTT leading to hash join disasters. Permanent temp tables never truncated — tempdb bloat.

#### Interview follow-ups (with model answers)

**Q:** Recursive CTE vs Oracle CONNECT BY?
**A:** For «CTE vs subquery vs temp table.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** When does Oracle materialize WITH clauses?
**A:** On «When does Oracle materialize WITH clauses», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Temp table transaction visibility?
**A:** Trade-off answer for «Temp table transaction visibility»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «CTE vs subquery vs temp table.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Risk report stages 5M eligible trades into `GTT_STAGING` with index on `account_id`, then joins to dimensions — one scan of fact. Replacing earlier 8-CTE query cut runtime 70% after `DBMS_XPLAN` showe. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 23. Pagination: `OFFSET` vs keyset.

**Short answer:** **`OFFSET n`** skips n rows — cost grows linearly (page 10000 still reads 100000 rows). **Keyset (seek) pagination** uses last-seen key: `WHERE (created_at, id) < (:c, :i) ORDER BY created_at DESC, id DESC FETCH FIRST 20 ROWS ONLY` — constant time per page. Oracle 12c+: `FETCH FIRST n ROWS ONLY`. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Pagination pattern for APIs and UIs. OFFSET is simple but does not scale; keyset requires stable sort keys and handles duplicates via tie-breaker column (usually PK). This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

OFFSET implemented as count-and-discard in most engines. Keyset uses index range on `(sort_col, id)` — no rescan of prior pages. `ROWNUM` wrapper pattern pre-12c; watch **ROWNUM before ORDER BY** trap (Q rapid-fire). Keyset breaks if sort column mutates during paging — document contract.

#### When to use / when NOT to use

Keyset for infinite scroll on large tables. OFFSET acceptable for admin screens page 1–5 only. Never `OFFSET` million-row exports — use keyset batch or parallel partition scan.

#### Production example

Transaction history API: clients send `cursor=base64(created_at|id)`; SQL seeks from cursor. Removed `OFFSET ?` after page 500 queries timed out — p99 stable at 15ms. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Keyset without unique tie-breaker → skipped/duplicate rows across pages. OFFSET with unstable `ORDER BY name` (names change). Using `COUNT(*)` over full table for total on every page load.

#### Interview follow-ups (with model answers)

**Q:** How to paginate with filters on multiple columns?
**A:** For «Pagination: `OFFSET` vs keyset.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Hibernate `setFirstResult` / `setMaxResults` implications?
**A:** On «Hibernate `setFirstResult` / `setMaxResults` implications», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Keyset vs search-after in Elasticsearch — analogy?
**A:** Trade-off answer for «Keyset vs search-after in Elasticsearch — analogy»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Pagination: `OFFSET` vs keyset.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Transaction history API: clients send `cursor=base64(created_at|id)`; SQL seeks from cursor. Removed `OFFSET ?` after page 500 queries timed out — p99 stable at 15ms. Capture AWR/ASH SQL_ID, baseline . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
SELECT id, created_at, amount
  FROM payments
 WHERE (created_at, id) < (:last_created, :last_id)
 ORDER BY created_at DESC, id DESC
 FETCH FIRST 20 ROWS ONLY;
```

---

### 24. Prepared statements and cursor sharing.

**Short answer:** **Prepared statements** parse once, bind many — essential for OLTP throughput and SQL injection defense. Oracle **cursor sharing** reuses plans in shared pool; watch `open_cursors` limit and **ResultSet/Statement leaks** that exhaust cursors per session. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

JDBC `PreparedStatement`, JPA native queries with parameters, PL/SQL binds — all the same principle. Literal-heavy ORMs (dynamic sort columns) defeat sharing. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle: soft parse vs hard parse; `V$SQL` shows executions vs parses. `session_cached_cursors` reduces reopen cost. Sybase jConnect prepared statements similar. Hibernate batching (`jdbc.batch_size`) batches DML binds — separate from read cursor sharing.

#### When to use / when NOT to use

Always parameterize user input. Pool statements at framework level; don't create new `PreparedStatement` per loop iteration without batch. Monitor `ORA-01000 maximum open cursors exceeded`.

#### Production example

Connection leak hunt: `V$SESSION` shows 800 open cursors for app user — unclosed streams in legacy DAO. Try-with-resources fix + Hikari `leakDetectionThreshold` — cursors drop to <20 per session. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

String concatenation in JPQL/native SQL. Closing Connection but not ResultSet (driver-dependent leak). Disabling prepared statements "for debugging."

#### Interview follow-ups (with model answers)

**Q:** Hard parse storm symptoms in AWR?
**A:** For «Prepared statements and cursor sharing.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Statement caching in Hikari + Oracle implicit caching?
**A:** On «Statement caching in Hikari + Oracle implicit caching», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Literal SQL from Hibernate `Criteria` — still an issue?
**A:** Trade-off answer for «Literal SQL from Hibernate `Criteria` — still an issue»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Prepared statements and cursor sharing.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Connection leak hunt: `V$SESSION` shows 800 open cursors for app user — unclosed streams in legacy DAO. Try-with-resources fix + Hikari `leakDetectionThreshold` — cursors drop to <20 per session. Capt. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 25. N+1 in SQL (not just ORM).

**Short answer:** N+1 is executing one query per row in a loop — `SELECT * FROM order_line WHERE order_id = ?` × 500 orders. Fix with **`WHERE order_id IN (...)`** in bounded chunks, or a single JOIN fetching parent+child. ORM lazy loading triggers the same pattern; raw JDBC is not immune. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Chatty database access dominates latency when RTT to DB is milliseconds and row count is thousands. Set-based thinking is the senior fix — in SQL or ORM fetch joins. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Loop in Java service calls repository 500 times — 500 round trips even if indexed. Batch `IN` lists (Oracle 1000 bind limit — chunk with UNION ALL or temp table of ids). JOIN returns wide result — map in app or use DTO projection. Hibernate `@EntityGraph`, `JOIN FETCH`, or `@BatchSize`.

#### When to use / when NOT to use

JOIN when you always need child rows. Batch IN when child load is conditional. Cursor/stream for huge exports — not N+1 but single query with fetch size tuning.

#### Production example

Invoice PDF job loaded headers then looped lines — 40 min. Replaced with `SELECT h.*, l.* FROM invoice h JOIN line l ON ... WHERE batch_id = :batch` — 90 seconds. Hibernate path uses `@BatchSize(size=50)` on collections as interim fix.

#### Common mistakes

Assuming JPA `@OneToMany` default is safe. `IN` clause with 50K binds — parse errors. Cartesian product from joining two collections without distinct.

#### Interview follow-ups (with model answers)

**Q:** `@BatchSize` vs `JOIN FETCH` trade-offs?
**A:** For «N+1 in SQL (not just ORM).», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How to detect N+1 in AWR / p6spy?
**A:** On «How to detect N+1 in AWR / p6spy», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «N+1 in SQL (not just ORM).» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Invoice PDF job loaded headers then looped lines — 40 min. Replaced with `SELECT h.*, l.* FROM invoice h JOIN line l ON ... WHERE batch_id = :batch` — 90 seconds. Hibernate path uses `@BatchSize(size=. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 26. Execution plan instability.

**Short answer:** Same SQL text, different plans over time — caused by stale stats, bind peeking, data volume shifts, histogram gaps, or upgrade. Oracle **SQL Plan Management** (baselines) and controlled stats jobs stabilize critical SQL. Never accept "Tuesday it's fast, Wednesday it's slow" without AWR diff and bind capture. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Plan instability is production poison for SLAs. Apps don't change but optimizer cost model or statistics do — p99 latency spikes mysteriously. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Adaptive plans, cardinality feedback, reoptimization on first few executions. `DBMS_STATS` auto job vs manual post-ETL. SQL baselines capture accepted plan; new plans evolve only if verified better. `OPTIMIZER_USE_PENDING_STATISTICS` — dangerous if unreviewed.

#### When to use / when NOT to use

Baselines for top 20 revenue-critical SQL IDs from AWR. Refresh stats after partition load with `GRANULARITY => 'PARTITION'`. Avoid locking bad plans forever — review quarterly.

#### Production example

Post-holiday data skew broke checkout SQL — NL join returned. SPM baseline from pre-holiday plan restored SLA; parallel root cause fix: extended stats on `(promo_flag, category_id)`. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

`DBMS_STATS` with `estimate_percent => 1` on huge tables — wild NDV errors. Deleting all baselines during upgrade panic. Hinting every query instead of fixing stats.

#### Interview follow-ups (with model answers)

**Q:** SQL profile vs baseline vs patch?
**A:** For «Execution plan instability.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Bind-aware baseline capture?
**A:** On «Bind-aware baseline capture», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** 12c adaptive plans — friend or foe?
**A:** Trade-off answer for «12c adaptive plans — friend or foe»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Execution plan instability.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Post-holiday data skew broke checkout SQL — NL join returned. SPM baseline from pre-holiday plan restored SLA; parallel root cause fix: extended stats on `(promo_flag, category_id)`. Capture AWR/ASH S. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 27. Partitioning.

**Short answer:** **Partitioning** splits large tables by key (range, list, hash) for prune-able scans, easier retention (drop partition), and partition-wise joins. Wrong key — every query scans all partitions. **Local indexes** follow partition; **global** span all — trade maintenance and availability. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Partitioning is a manageability and performance feature, not a substitute for indexing. Oracle interval partitioning auto-creates monthly partitions; Sybase/SQL Server have similar schemes. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Partition pruning: `WHERE tx_date BETWEEN ...` touches only relevant segments. `EXPLAIN PLAN` shows `PARTITION RANGE` iterator. Exchange partition loads data without DML on live table. Hash spreads hot inserts; list for region codes; range for time series.

#### When to use / when NOT to use

Fact tables by date with retention policy. Tables > tens of GB where queries always filter on partition key. Avoid partitioning small tables — metadata overhead. Align partition key with query filters — not arbitrary.

#### Production example

`transactions` range by month, 24 online partitions, drop >7 years via `ALTER TABLE DROP PARTITION` — seconds vs DELETE hours. Local index on `(account_id, tx_date)` prune + seek. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Partition key not in WHERE — full scan all partitions. Global index maintenance after drop partition (invalid until rebuild). 10K partitions — DDL and dictionary bloat. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** Interval vs manual partition creation?
**A:** For «Partitioning.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Partition-wise join requirements?
**A:** On «Partition-wise join requirements», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Subpartitioning use case?
**A:** Trade-off answer for «Subpartitioning use case»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Partitioning.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: `transactions` range by month, 24 online partitions, drop >7 years via `ALTER TABLE DROP PARTITION` — seconds vs DELETE hours. Local index on `(account_id, tx_date)` prune + seek. Capture AWR/ASH SQL_. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 28. Indexing for `ORDER BY` + `WHERE`.

**Short answer:** Composite index `(filter_col, sort_col DESC)` lets Oracle satisfy `WHERE filter_col = ? ORDER BY sort_col DESC` via index range scan **without separate SORT** operation. Match index column order to equality filters first, then sort direction in index definition. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Avoiding sorts saves temp and CPU on high-volume list endpoints. `EXPLAIN PLAN` `SORT ORDER BY` disappearing is the win signal. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Index leaf keys are ordered; descending index columns (Oracle) match `ORDER BY ... DESC`. Mixed ASC/DESC in SQL may need adjusted index or sort anyway. Filter on non-leading index column → sort may still occur after table access.

#### When to use / when NOT to use

Index when API paginates sorted filtered lists at scale. Skip when result sets are tiny or sort column updated constantly (index maintenance). Covering index avoids table hop after sort elimination.

#### Production example

Open tickets queue: index `(assignee_id, priority DESC, created_at DESC)` for `WHERE assignee_id = :me AND status = 'OPEN' ORDER BY priority DESC, created_at DESC` — list API 3ms vs 400ms with filesort. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Index `(created_at)` only when every query filters `status`. Wrong DESC marker in index vs SQL ASC mismatch. Assuming elimination of sort without checking actual plan.

#### Interview follow-ups (with model answers)

**Q:** Index-only access plus ORDER BY?
**A:** For «Indexing for `ORDER BY` + `WHERE`.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Sort elimination with JOIN queries?
**A:** On «Sort elimination with JOIN queries», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Functional index on expression in ORDER BY?
**A:** Trade-off answer for «Functional index on expression in ORDER BY»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Indexing for `ORDER BY` + `WHERE`.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Open tickets queue: index `(assignee_id, priority DESC, created_at DESC)` for `WHERE assignee_id = :me AND status = 'OPEN' ORDER BY priority DESC, created_at DESC` — list API 3ms vs 400ms with filesor. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 29. Covering vs lookup.

**Short answer:** **Covering index** includes all columns the query needs — index-only scan, no table lookup by ROWID. **Non-covering** index seek plus **table access by index ROWID** (extra I/O). Wide covering indexes speed reads but slow writes and consume space — measure both paths. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Covering is the read optimization capstone for hot queries. Oracle doesn't have SQL Server `INCLUDE` columns identically — put columns in index or use IOT/over-indexing consciously. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Index-only scan when all selected/filtered columns present in index leaf (including PK for heap tables). Lookup: for each index entry, fetch table block — random I/O multiplier on wide result sets. Bitmap indexes (Oracle DW) different trade-offs — not OLTP default.

#### When to use / when NOT to use

Covering for top 5 read-heavy queries on write-moderate tables. Avoid 15-column indexes "just in case." Postgres `INCLUDE` columns for non-key payload — pattern worth knowing cross-vendor. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

Account list API selects `(id, name, status)` only — index `(customer_id, status, name)` serves query index-only; dropped redundant index on `(customer_id)` alone after verification. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Covering index on CLOB column (not possible / useless). Duplicate indexes differing only by trailing column — confusing optimizer. Ignoring index clustering / row scattering — many lookups still slow.

#### Interview follow-ups (with model answers)

**Q:** Index-only scan vs fast full index scan?
**A:** For «Covering vs lookup.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** When does Oracle choose lookup despite covering?
**A:** On «When does Oracle choose lookup despite covering», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Write amplification quantification?
**A:** Trade-off answer for «Write amplification quantification»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Covering vs lookup.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Account list API selects `(id, name, status)` only — index `(customer_id, status, name)` serves query index-only; dropped redundant index on `(customer_id)` alone after verification. Capture AWR/ASH S. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 30. Locking: row vs table vs TX.

**Short answer:** Oracle excels at **row-level locking** for DML; readers usually don't block writers (MVCC). **Table locks** (`LOCK TABLE`, unindexed FK on parent delete) are rare but catastrophic when they appear. **Transaction locks** held until commit — keep TX short; consistent lock order prevents deadlocks. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. PL/SQL belongs where set-based SQL cannot express the rule or where you must keep logic colocated with data for performance.

#### What it is

Lock granularity determines concurrency. Seniors know when app design forces table locks — especially FK and DDL — not just "Oracle locks rows." This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

DML locks rows touched; DDL may lock table (exclusive during alter). `TM` enqueue on DML; `TX` transaction lock. `SELECT FOR UPDATE` row locks. Sybase historically more table-lock prone on heap tables; `HOLDLOCK` range locks. Lock escalation in SQL Server — different from Oracle.

#### When to use / when NOT to use

Design FKs with indexes on child side (Oracle locks parent on unindexed FK child delete/update). Avoid long `@Transactional` spanning user input. Online rebuild uses `ONLINE` redefinition — not blind `ALTER` in peak.

#### Production example

Parent `accounts` delete blocked all child inserts — missing index on `transactions.account_id` FK caused share lock on parent table. Added index — inserts concurrent again. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Running batch delete without chunking holding millions of row locks. DDL during business hours. Ignoring `v$locked_object` in incident response.

#### Interview follow-ups (with model answers)

**Q:** Lock modes SS, SX, X in Oracle?
**A:** For «Locking: row vs table vs TX.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How does MVCC avoid reader-writer blocking?
**A:** On «How does MVCC avoid reader-writer blocking», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Locking: row vs table vs TX.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Parent `accounts` delete blocked all child inserts — missing index on `transactions.account_id` FK caused share lock on parent table. Added index — inserts concurrent again. Capture AWR/ASH SQL_ID, ba. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 31. Foreign keys and performance.

**Short answer:** FKs enforce referential integrity — every child insert/update checks parent; parent delete/update locks/affects children. **Unindexed FK columns** on child table cause full table scans on cascade checks and **table-level locks on parent** in Oracle. Always index FK columns; understand delete rules (`ON DELETE CASCADE` vs restrict). Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

FK is not free — it's correctness with DML cost. Banks keep FKs; startups sometimes drop them and regret data orphans — senior answer balances integrity vs perf. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle: unindexed FK on child → DML on parent acquires share lock on child table (full scan). Indexed FK → row-level checks only. Sybase/SQL Server similar themes. ORM `@ManyToOne` doesn't auto-create FK index — DBA must.

#### When to use / when NOT to use

Always FK + index on high-volume OLTP. `ON DELETE CASCADE` for pure composition; restrict for financial links. Deferrable FKs rare in apps — batch loads may use `DISABLE VALIDATE`.

#### Production example

Schema review checklist: every FK column has matching index — automated query against `dba_constraints` / `dba_ind_columns`. Found 12 missing — fixed before go-live, prevented production lock incident. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Assuming JPA creates FK index. CASCADE delete on shared reference data — accidental mass delete. Disabling FK for "speed" without replacement validation job.

#### Interview follow-ups (with model answers)

**Q:** Deferred constraint checking?
**A:** For «Foreign keys and performance.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** FK vs application-enforced integrity in microservices?
**A:** On «FK vs application-enforced integrity in microservices», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Impact of FK on partition exchange?
**A:** Trade-off answer for «Impact of FK on partition exchange»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Foreign keys and performance.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Schema review checklist: every FK column has matching index — automated query against `dba_constraints` / `dba_ind_columns`. Found 12 missing — fixed before go-live, prevented production lock incident. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 32. Sequences vs identity (Oracle).

**Short answer:** Oracle traditionally used **`SEQUENCE.NEXTVAL`** (via trigger or default) for surrogate keys; **IDENTITY columns** (12c+) simplify syntax. Sequences **gap on rollback** — normal. Set **`CACHE`** size for throughput (`CACHE 20` default may cause RAC gaps / latch contention — tune with Hibernate `pooled-lo`). Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

ID generation strategy affects insert rate, gaps in business-visible numbers, and ORM config. Not the same as UUID — sequences are ordered-ish and narrow. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`CREATE SEQUENCE ord_seq CACHE 1000` pre-allocates in SGA — restart loses unused → gaps. `NOCACHE` serializable IDs, slower. IDENTITY: `GENERATED ALWAYS AS IDENTITY`. RAC: each instance caches — larger gaps. Sybase: `@@identity` after insert — session scope.

#### When to use / when NOT to use

Sequence + Hibernate `SequenceStyleGenerator` with alignment to cache size. IDENTITY for simple apps; harder batch insert optimization in some ORMs. Never use sequence for security tokens (predictable).

#### Production example

Order IDs must be monotonic-ish but gaps OK on rollback — `ord_seq CACHE 500` with Hibernate `pooled-lo` optimizer matches DB cache — insert TPS 8K vs 800 with `NOCACHE`. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Expecting gapless IDs for audit numbering — use separate ledger sequence. `ORDER` keyword on sequence (12c) for strict ordering — perf hit. Copying sequence cache mismatch with ORM pool.

#### Interview follow-ups (with model answers)

**Q:** UUID vs sequence in sharded Oracle?
**A:** For «Sequences vs identity (Oracle).», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Trigger-based vs default ON NULL sequence?
**A:** On «Trigger-based vs default ON NULL sequence», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Sybase `@@identity` vs sequence?
**A:** Trade-off answer for «Sybase `@@identity` vs sequence»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Sequences vs identity (Oracle).» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Order IDs must be monotonic-ish but gaps OK on rollback — `ord_seq CACHE 500` with Hibernate `pooled-lo` optimizer matches DB cache — insert TPS 8K vs 800 with `NOCACHE`. Capture AWR/ASH SQL_ID, basel. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
CREATE SEQUENCE ord_seq START WITH 1 INCREMENT BY 1 CACHE 500;
-- Hibernate: pooled-lo with allocationSize matching cache
```

---

### 33. PL/SQL: when it belongs.

**Short answer:** PL/SQL belongs **close to data** for set-based batch, validation that must be DB-enforced, security definer APIs, and reducing round trips — not as a substitute for all domain logic in Java. Banks run massive PL/SQL estates — you must read packages; greenfield splits **invariants in DB (constraints)** vs **orchestration in services**. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

PL/SQL is Oracle's procedural extension — procedures, packages, triggers. Strategic placement avoids chatty Java loops and leverages SQL engine; misuse creates undeployable monolith logic DBAs own forever. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Procedures run in DB server process — no network per row. Packages group spec (public API) and body (implementation). `AUTHID DEFINER` runs with owner privileges — controlled elevation. Sybase T-SQL stored procs analogous for ASE migrations.

#### When to use / when NOT to use

Bulk ETL steps, interest calculation batch, centralized audit logging API. Avoid core product rules only in PL/SQL if Java team can't test/version — hybrid: expose package proc called from service for heavy set ops. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

End-of-day interest accrual: 50M accounts in PL/SQL `FORALL` batch — 12 minutes. Prior Java row loop 4 hours. Domain rules for "what is interest" still owned by Java module generating config tables PL/SQL reads.

#### Common mistakes

Business logic in triggers (hidden). PL/SQL calling HTTP (UTL_HTTP) for orchestration — wrong layer. No source control for package bodies.

#### Interview follow-ups (with model answers)

**Q:** Package spec vs body deployment?
**A:** For «PL/SQL: when it belongs.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Testing PL/SQL in CI?
**A:** On «Testing PL/SQL in CI», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** When to prefer Java JDBC batch vs PL/SQL?
**A:** Trade-off answer for «When to prefer Java JDBC batch vs PL/SQL»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «PL/SQL: when it belongs.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: End-of-day interest accrual: 50M accounts in PL/SQL `FORALL` batch — 12 minutes. Prior Java row loop 4 hours. Domain rules for "what is interest" still owned by Java module generating config tables PL. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 34. PL/SQL cursor FOR vs bulk `FORALL` / `BULK COLLECT`.

**Short answer:** Row-by-row **`FOR rec IN cur LOOP`** causes context switches — slow at scale. **`BULK COLLECT LIMIT n`** fetches arrays; **`FORALL`** drives array DML in one engine call. Watch **PGA memory** with huge limits; handle **`SAVE EXCEPTIONS`** for partial failure in batch loads. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Bulk binding is the PL/SQL performance baseline senior code must use for batch jobs — same conceptual win as JDBC batch, inside the server. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`BULK COLLECT INTO l_ids LIMIT 1000` — fetches 1000 at a time. `FORALL i IN 1..l_ids.COUNT INSERT ... VALUES l_ids(i)` — array insert. `%ROWTYPE` collections. Exceptions: one bad row aborts whole FORALL unless `SAVE EXCEPTIONS` + `SQL%BULK_EXCEPTIONS`.

#### When to use / when NOT to use

Bulk for ETL, reconciliation, mass updates. Simple single-row CRUD — plain SQL or ORM fine. Limit 500–5000 tuned to PGA and undo — not `LIMIT 1000000`.

#### Production example

Nightly status flip on 2M rows: ref cursor bulk collect 2000 + FORALL update — 8 min, 40MB PGA peak. Row loop prototype timed out at 2 hours. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

`SELECT * BULK COLLECT` wide rows into memory. No exception handling in FORALL — silent partial apply. Mixing bulk fetch with row triggers firing per row still slow.

#### Interview follow-ups (with model answers)

**Q:** pipelined table functions?
**A:** For «PL/SQL cursor FOR vs bulk `FORALL` / `BULK COLLECT`.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Comparing FORALL vs executemany in JDBC?
**A:** On «Comparing FORALL vs executemany in JDBC», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Collection types `TABLE OF` memory?
**A:** Trade-off answer for «Collection types `TABLE OF` memory»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «PL/SQL cursor FOR vs bulk `FORALL` / `BULK COLLECT`.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Nightly status flip on 2M rows: ref cursor bulk collect 2000 + FORALL update — 8 min, 40MB PGA peak. Row loop prototype timed out at 2 hours. Capture AWR/ASH SQL_ID, baseline the good plan, and schedu. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
OPEN c; LOOP
  FETCH c BULK COLLECT INTO l_ids LIMIT 2000;
  EXIT WHEN l_ids.COUNT = 0;
  FORALL i IN 1..l_ids.COUNT
    UPDATE jobs SET status = 'DONE' WHERE id = l_ids(i);
  COMMIT;
END LOOP;
```

---

### 35. Packages, spec vs body, grants.

**Short answer:** **Package spec** is the public API — procedures/functions signatures. **Body** holds implementation; can be recompiled without changing callers if spec unchanged. **`AUTHID DEFINER`** vs **`CURRENT_USER`** controls privilege context. **Synonyms** simplify cross-schema access; **WRAP** obfuscates — not security. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. PL/SQL belongs where set-based SQL cannot express the rule or where you must keep logic colocated with data for performance.

#### What it is

Packages are Oracle's module system for PL/SQL — encapsulation, overloading, private procedures in body only. Grant `EXECUTE` on spec; hide body from dependency churn. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Spec stored in data dictionary first; body depends on spec. `AUTHID DEFINER`: runs as owner — app user executes with definer rights (controlled). `AUTHID CURRENT_USER`: invoker rights — resolves tables as caller. Breakable grants: grant on procedure in spec, not internal helpers.

#### When to use / when NOT to use

Package related procs (billing package, audit package). Definer rights for tightly controlled API on schema-owner tables. Invoker when multi-tenant table synonyms per user — rare in app-user models.

#### Production example

`APP_API` package spec exposed to JDBC callable statement; body in `SCHEMA_OWNER`. App user has no direct table SELECT — only `EXECUTE ON APP_API`. Security audit passes least privilege.

#### Common mistakes

Granting SELECT on all tables to app user "because easier." WRAP thinking it hides secrets. Spec change breaks dependent Java without coordination. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** Dependency tracking and invalidation?
**A:** For «Packages, spec vs body, grants.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Edition-based redefinition?
**A:** On «Edition-based redefinition», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Packages, spec vs body, grants.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: `APP_API` package spec exposed to JDBC callable statement; body in `SCHEMA_OWNER`. App user has no direct table SELECT — only `EXECUTE ON APP_API`. Security audit passes least privilege. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 36. Triggers: why seniors fear them.

**Short answer:** Triggers hide side effects — audit, replication, derived columns — invisible to app code and Hibernate. Cause **mutating table errors**, ordering surprises, double-fire on ORM flush, hard-to-test behavior. Prefer **constraints + explicit service logic**; if triggers exist, document in entity/runbook. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Row/statement triggers fire on DML timing (BEFORE/AFTER, INSERT/UPDATE/DELETE). Banks have legacy audit triggers everywhere — you maintain, not always choose. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

BEFORE row trigger can mutate `:NEW`. AFTER statement trigger sees committed changes in same TX. Hibernate single save may UPDATE twice → trigger twice. `WHEN` clause filters. Compound triggers (11g+) unify row/statement — still complexity.

#### When to use / when NOT to use

Acceptable: uniform audit trail, immutable history table, simple `updated_at` if team standard. Avoid: business rules, calling external systems, cascading updates across tables. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

Removed `BEFORE INSERT` trigger assigning sequence — replaced with IDENTITY and Hibernate — eliminated ORA-04091 interaction with batch insert job. Kept AFTER INSERT audit trigger — documented in architecture decision record. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Trigger calling Java via queue table unknowingly twice. Recursive trigger loops. `@Transactional` rollback leaving audit trigger committed via autonomous transaction (integrity lie).

#### Interview follow-ups (with model answers)

**Q:** Compound trigger structure?
**A:** For «Triggers: why seniors fear them.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Trigger vs Flashback/archive?
**A:** On «Trigger vs Flashback/archive», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Testing triggers in Flyway migrations?
**A:** Trade-off answer for «Testing triggers in Flyway migrations»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Triggers: why seniors fear them.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Removed `BEFORE INSERT` trigger assigning sequence — replaced with IDENTITY and Hibernate — eliminated ORA-04091 interaction with batch insert job. Kept AFTER INSERT audit trigger — documented in arch. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 37. Mutating table and compound triggers.

**Short answer:** **`ORA-04091` mutating table** — row trigger on table T cannot query or DML T because it's in mutation. Workarounds: **compound triggers**, **AFTER STATEMENT** timing, temporary staging tables, or redesign. Usually signals trigger belongs elsewhere. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Classic Oracle footgun when trigger tries to validate against same table mid-DML. Hibernate bulk operations trigger it more than manual SQL in dev. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Row trigger fires per row while table is mutating — consistency protection. Compound trigger defines sections: BEFORE STATEMENT, BEFORE EACH ROW, AFTER EACH ROW, AFTER STATEMENT — share state via PL/SQL variables. Statement section runs when mutation complete — safe for aggregate checks on same table.

#### When to use / when NOT to use

Compound trigger for complex audit needing row + statement phases. Better: move validation to materialized constraint check job or app layer. Autonomous transaction workaround for mutating — smell (Q38).

#### Production example

Line-item total validation trigger failed on bulk load ORA-04091. Refactored to AFTER STATEMENT compound comparing sum to header in same TX — works for batch; still flagged for move to service layer. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Autonomous transaction log "fix" while parent rolls back. `@Transactional` test doesn't cover bulk JDBC path. Querying same table in BEFORE ROW trigger.

#### Interview follow-ups (with model answers)

**Q:** Temporary table workaround pattern?
**A:** For «Mutating table and compound triggers.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Mutating vs constraining table?
**A:** On «Mutating vs constraining table», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Replace trigger with constraint (check deferred)?
**A:** Trade-off answer for «Replace trigger with constraint (check deferred)»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Mutating table and compound triggers.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Line-item total validation trigger failed on bulk load ORA-04091. Refactored to AFTER STATEMENT compound comparing sum to header in same TX — works for batch; still flagged for move to service layer. . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 38. Autonomous transactions.

**Short answer:** **`PRAGMA AUTONOMOUS_TRANSACTION`** starts independent TX — commits/rollbacks separately from caller. Useful for **audit/error logging** that must survive parent rollback. Dangerous as habitual mutating-table fix — you can log success while business TX rolls back (**lying audit**). Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Separate transaction scope in same session — rare, sharp tool. Commits in autonomous proc don't commit parent; parent rollback doesn't undo autonomous commit. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Enter autonomous proc → implicit commit of parent? No — parent suspended; autonomous has own TX. Must COMMIT/ROLLBACK inside autonomous before return. Often used in log tables `err_log`. Sybase has no direct equivalent — nested tran different semantics.

#### When to use / when NOT to use

Error logging where failure must persist. Avoid business data writes autonomous unless audit semantics explicitly require out-of-band commit. Never chain autonomous to "fix" data integrity.

#### Production example

Global exception handler in batch PL/SQL calls `log_error_autonomous(msg)` — ops sees failure reason even when main batch rolls back. Business rows not written autonomously — only diagnostic row. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Autonomous insert of business fact then parent fails — inconsistent state. Forgetting COMMIT in autonomous → ORA-06519. Overuse → debugging nightmare.

#### Interview follow-ups (with model answers)

**Q:** Compare to Java REQUIRES_NEW?
**A:** For «Autonomous transactions.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Audit trigger autonomous — compliance implications?
**A:** On «Audit trigger autonomous — compliance implications», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Lock interaction with parent TX?
**A:** Trade-off answer for «Lock interaction with parent TX»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Autonomous transactions.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Global exception handler in batch PL/SQL calls `log_error_autonomous(msg)` — ops sees failure reason even when main batch rolls back. Business rows not written autonomously — only diagnostic row. Capt. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
CREATE PROCEDURE log_err(p_msg VARCHAR2) AS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO err_log(msg, ts) VALUES (p_msg, SYSTIMESTAMP);
  COMMIT;
END;
```

---

### 39. Exception handling in PL/SQL.

**Short answer:** **`WHEN OTHERS THEN NULL`** swallows failures — production incident fuel. Log context, **`RAISE`** or **`RAISE_APPLICATION_ERROR`** to caller. **`SELECT INTO`** raises **`NO_DATA_FOUND`** / **`TOO_MANY_ROWS`** — handle explicitly; don't treat as generic OTHERS silently. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

PL/SQL exception block controls failure visibility to Java/JDBC caller. Spring maps to `UncategorizedSQLException` — still need correct error propagation from DB layer. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Predefined exceptions; user-defined; `RAISE_APPLICATION_ERROR(-20001, 'msg')`. `SQLCODE`, `SQLERRM`, `DBMS_UTILITY.FORMAT_ERROR_BACKTRACE`. In bulk ops, `%BULK_EXCEPTIONS`. Java must map known error codes for retry vs fail.

#### When to use / when NOT to use

Catch specific exceptions; OTHERS only at boundary with log+re-raise. Use application error codes contract between PL/SQL and service tier. Don't hide constraint violations Hibernate should surface to user.

#### Production example

Payment package maps insufficient funds to `-20001` — Java catches and returns 402. Unknown errors re-raised — not swallowed. Removed blank OTHERS handlers from 1990s legacy — incidents now debuggable.

#### Common mistakes

OTHERS without RAISE. Wrong exception order (OTHERS first — unreachable). Logging without correlation id from Java.

#### Interview follow-ups (with model answers)

**Q:** Exception propagation across JDBC callableStatement?
**A:** For «Exception handling in PL/SQL.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Retry on ORA-00060 in caller?
**A:** On «Retry on ORA-00060 in caller», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Unit testing exceptions with utPLSQL?
**A:** Trade-off answer for «Unit testing exceptions with utPLSQL»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Exception handling in PL/SQL.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Payment package maps insufficient funds to `-20001` — Java catches and returns 402. Unknown errors re-raised — not swallowed. Removed blank OTHERS handlers from 1990s legacy — incidents now debuggable. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 40. `SELECT INTO` vs cursor.

**Short answer:** **`SELECT ... INTO`** expects **exactly one row** — `NO_DATA_FOUND` if zero, `TOO_MANY_ROWS` if multiple. Fine for singleton lookups. **Explicit cursor** or **`CURSOR FOR`** for controlled iteration; bulk collect for batches. Never use INTO assuming "maybe one row" without handling both exceptions.

#### What it is

PL/SQL data retrieval patterns — simplicity vs control. Anti-pattern: SELECT INTO in loop without bulk — performance and exception chaos. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Implicit query in INTO runs once; exceptions propagate unless handled. Cursor: OPEN/FETCH/CLOSE lifecycle; `%NOTFOUND`. Ref cursors for dynamic result sets returned to Java. FOR rec IN (SELECT ...) simplifies read-only iteration.

#### When to use / when NOT to use

INTO for config key lookup guaranteed unique. Cursor for streaming large sets with bulk fetch. Ref cursor from proc to JDBC ResultSet for report procedures.

#### Production example

Settings lookup: `SELECT value INTO v FROM app_config WHERE key = 'MAX_RETRY'` — handles NO_DATA_FOUND with default. Report proc returns SYS_REFCURSOR to Java — no INTO. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

INTO in trigger assuming single row — multi-row data causes ORA-01422. Not closing cursor on exception path — leak. Using COUNT(*) then INTO — two queries wasteful.

#### Interview follow-ups (with model answers)

**Q:** Ref cursor vs JDBC ResultSet typing?
**A:** For «`SELECT INTO` vs cursor.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** BULK COLLECT from implicit cursor?
**A:** On «BULK COLLECT from implicit cursor», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`SELECT INTO` vs cursor.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Settings lookup: `SELECT value INTO v FROM app_config WHERE key = 'MAX_RETRY'` — handles NO_DATA_FOUND with default. Report proc returns SYS_REFCURSOR to Java — no INTO. Capture AWR/ASH SQL_ID, baseli. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 41. Dynamic SQL (`EXECUTE IMMEDIATE`).

**Short answer:** **`EXECUTE IMMEDIATE`** and **`DBMS_SQL`** build SQL at runtime — mandatory for DDL, pivot tables, optional filters. **Always bind** user values — never concatenate. Consider **cursor sharing**, **SQL injection**, and **privilege** (`AUTHID CURRENT_USER` invoker resolution). Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Dynamic SQL when table/column names aren't known at compile time — or generic utility procedures. High risk surface if concatenated from UI input. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`EXECUTE IMMEDIATE '... :b' INTO ... USING val;` — binds safe. `USING` for IN, `INTO` for OUT. `DBMS_SQL` parse/bind/execute for older complex patterns. Whitelist table names in app — binds can't parameterize identifiers.

#### When to use / when NOT to use

Dynamic for admin packages, partition maintenance, generic search with fixed column whitelist. Static SQL for all OLTP hot paths — optimizer friendlier. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

Reporting proc accepts sort column from whitelist `(amount, date, status)` — builds SQL with identifier from case statement, filters bound. Security review passes; concat version rejected. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

`:table_name` bind for identifier — doesn't work. SQL injection in search box passed to dynamic SQL. No exception handling — opaque ORA errors to user.

#### Interview follow-ups (with model answers)

**Q:** DBMS_ASSERT.SIMPLE_SQL_NAME?
**A:** For «Dynamic SQL (`EXECUTE IMMEDIATE`).», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Dynamic SQL and SQL injection in Hibernate native?
**A:** On «Dynamic SQL and SQL injection in Hibernate native», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Parse once execute many with DBMS_SQL?
**A:** Trade-off answer for «Parse once execute many with DBMS_SQL»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Dynamic SQL (`EXECUTE IMMEDIATE`).» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Reporting proc accepts sort column from whitelist `(amount, date, status)` — builds SQL with identifier from case statement, filters bound. Security review passes; concat version rejected. Capture AWR. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

#### Code / config (when useful)
```sql
EXECUTE IMMEDIATE
  'UPDATE accounts SET status = :st WHERE id = :id'
  USING p_status, p_id;
```

---

### 42. Sybase ASE vs Oracle (interview for mixed estates).

**Short answer:** **Sybase ASE** uses T-SQL dialect, **`GO`** batches, **`@@identity`**, **`#temp`** tables, historically heavier **table locking**, **`HOLDLOCK`**, infamous **`NOLOCK`**. JDBC via **jConnect**. Many estates migrated ASE → SQL Server or Oracle — you'll maintain/read legacy T-SQL and know isolation/locking differs from Oracle MVCC. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Cross-vendor literacy for brownfield banks and telcos. Interview tests whether you panic at `GO` or map concepts to Oracle equivalents. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

ASE: tempdb `#temp` vs `@table` variable; lock manager; `SET CHAINED` transaction mode; procedures with `@params`. Oracle: PL/SQL, sequences, undo MVCC. Migration projects often run dual-write or read replicas — SQL portability illusion breaks on hints and types.

#### When to use / when NOT to use

Know Sybase when job mentions ASE, IQ (analytics), or Sybase-to-Oracle migration. Don't assume Oracle hints work on Sybase. Map `GETDATE()` → `SYSDATE`, `ISNULL` → `NVL`.

#### Production example

Team migrating 400 ASE procs to Oracle packages — categorize: pure SQL rewrite, cursor→bulk, identity→sequence, remove `NOLOCK` reads to Oracle consistent read on ADG standby. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Running ASE scripts with `GO` in SQL*Plus. Expecting identical isolation behavior without test. Ignoring jConnect charset/TDS settings.

#### Interview follow-ups (with model answers)

**Q:** Sybase IQ vs ASE workload split?
**A:** For «Sybase ASE vs Oracle (interview for mixed estates).», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Migration tooling (SAP SQLOnly, custom)?
**A:** On «Migration tooling (SAP SQLOnly, custom)», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Lock escalation differences?
**A:** Trade-off answer for «Lock escalation differences»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Sybase ASE vs Oracle (interview for mixed estates).» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Team migrating 400 ASE procs to Oracle packages — categorize: pure SQL rewrite, cursor→bulk, identity→sequence, remove `NOLOCK` reads to Oracle consistent read on ADG standby. Capture AWR/ASH SQL_ID, . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 43. `NOLOCK` / dirty read.

**Short answer:** **`NOLOCK` (Sybase/SQL Server)** or **`READ UNCOMMITTED`** reads uncommitted rows — **dirty reads, phantom rows, duplicates** in reports. Never for money, balances, or compliance. Prefer **RCSI**, **snapshot isolation**, or **read replica** with proper lag disclosure — not wrong answers for convenience. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

A hint born of blocking frustration on locking engines — technical debt masquerading as performance fix. Oracle doesn't have NOLOCK; readers use undo — different world. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Reader skips shared locks — sees in-flight uncommitted changes that may rollback. Report sums wrong during bulk update. Duplicate/missed rows if page splits during scan — documented SQL Server behaviors under NOLOCK.

#### When to use / when NOT to use

Essentially never in financial OLTP read paths. Historical misguided reporting only — replace architecture. Oracle: use read-only standby; Sybase: fix blocking root cause (indexes, TX length).

#### Production example

Legacy ASE report `FROM transactions WITH (NOLOCK)` showed $2M phantom revenue during failed batch rollback. Removed hint; enabled RCSI on SQL Server migration path; reports read AG replica. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

"Reports don't need accuracy." Copying NOLOCK pattern into Oracle docs (irrelevant). Using NOLOCK on tables being updated by same report's ETL. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** RCSI vs snapshot isolation?
**A:** For «`NOLOCK` / dirty read.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Oracle read consistency without NOLOCK equivalent?
**A:** On «Oracle read consistency without NOLOCK equivalent», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Blocking diagnosis on ASE?
**A:** Trade-off answer for «Blocking diagnosis on ASE»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «`NOLOCK` / dirty read.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Legacy ASE report `FROM transactions WITH (NOLOCK)` showed $2M phantom revenue during failed batch rollback. Removed hint; enabled RCSI on SQL Server migration path; reports read AG replica. Capture A. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 44. Temp tables vs CTEs in Sybase/SQL Server.

**Short answer:** **`#temp`** tables live in tempdb — can have **indexes, stats, explicit cardinality** — optimizer plans better for large intermediates. **`@table` variables** often lack stats (older versions) → bad plans on big sets. **CTEs** readable but may be inlined/recomputed. Choose by size and reuse, not fashion. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Sybase/SQL Server-specific intermediate data patterns — Oracle analog: **GTT (GLOBAL TEMPORARY TABLE)** and CTE materialization hints. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`CREATE TABLE #stage (...); CREATE INDEX ...; INSERT...; UPDATE STATISTICS`. Table variable: scope, fewer recompiles on small sets. CTE referenced multiple times may scan twice unless materialized (SQL Server 2019+ optimizations vary).

#### When to use / when NOT to use

#temp for ETL staging millions of rows. @variable for small TVP parameter patterns. CTE for short readable queries — not repeated fact scans. Pick patterns that survive batch windows, ETL loads, and peak OLTP without requiring heroic hints forever.

#### Production example

Reconciliation sproc: stage 3M keys in `#keys` with clustered index, join to fact — 2 min. @variable version estimated 1 row — nested loop disaster 45 min. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

@table variable for large heap — always slow. #temp without index on join column. Leaving #temp in nested proc — tempdb churn. Juniors often optimize SELECT latency while ignoring INSERT/UPDATE cost, lock duration, or ORA- errors during month-end jobs.

#### Interview follow-ups (with model answers)

**Q:** Oracle GTT vs SQL Server #temp?
**A:** For «Temp tables vs CTEs in Sybase/SQL Server.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Table variable statistics fixes in modern SQL Server?
**A:** On «Table variable statistics fixes in modern SQL Server», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Tempdb contention monitoring?
**A:** Trade-off answer for «Tempdb contention monitoring»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Temp tables vs CTEs in Sybase/SQL Server.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Reconciliation sproc: stage 3M keys in `#keys` with clustered index, join to fact — 2 min. @variable version estimated 1 row — nested loop disaster 45 min. Capture AWR/ASH SQL_ID, baseline the good pl. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 45. Explain a slow query methodology.

**Short answer:** Structured triage: **(1) reproduce** with binds **(2) actual execution plan** **(3) A-Rows vs E-Rows** at each step **(4) wait events** (ASH, `v$session`) **(5) index/rewrite/stats fix** **(6) bind peeking check** **(7) app layer** — N+1, fetch size, chatty commits. Document before/after; don't hint-and-pray permanently. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

The senior interview answer is a **process**, not a single trick. Shows you won't randomly add indexes at 2 a.m. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Identify SQL_ID from AWR/ASH/JDBC trace. `DBMS_XPLAN.DISPLAY_CURSOR` actuals. Top wait: `db file sequential read` (index lookup), `direct path read temp` (sort/hash spill), `enq: TX` (locking). Compare stats last_analyzed. Check bind values vs histogram.

#### When to use / when NOT to use

Always for prod regressions. Skip deep dive if obvious full scan on new query — still verify with actuals once. Escalate to DBA for system-wide latch/IO if single-query fix insufficient.

#### Production example

API regression: ASH shows SQL_ID hot, plan flip to FULL scan, stats stale after partition exchange. `GATHER_PARTITION_STATS` + baseline — restored. Secondary find: fetch size 10 → 500 reduced round trips 40%.

#### Common mistakes

Adding index without measuring write impact. Sharing estimated plan only in ticket. Fixing DB while N+1 in Java still burns 80% time.

#### Interview follow-ups (with model answers)

**Q:** AWR vs Real-Time ADDM?
**A:** For «Explain a slow query methodology.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How to baseline before release?
**A:** On «How to baseline before release», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Explain a slow query methodology.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: API regression: ASH shows SQL_ID hot, plan flip to FULL scan, stats stale after partition exchange. `GATHER_PARTITION_STATS` + baseline — restored. Secondary find: fetch size 10 → 500 reduced round tr. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 46. Hibernate + Oracle specifics.

**Short answer:** Map **`Dialect`**, **`NVARCHAR2`**, **`CLOB`** vs **`VARCHAR2(4000)`**, Oracle **empty string = NULL**, **`TIMESTAMP WITH TIME ZONE`**, **sequence/IDENTITY** generators, **`ROWNUM` vs FETCH FIRST**, boolean as **`NUMBER(1)`** historically. Test `GenerationType` batch inserts and FK indexes — JPA won't save you from Oracle semantics. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

ORM abstraction leaks at scale — especially Oracle types, pagination, and identity. Senior devs configure Hibernate explicitly, not defaults from Postgres dev laptop. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

`Oracle12cDialect` / `OracleDialect` pagination (`OFFSET/FETCH` vs `ROWNUM` wrapper). `@Lob` CLOB streaming — don't materialize 10MB in heap. `@Nationalized` for NVARCHAR2. `hibernate.jdbc.batch_size` + `order_inserts` for bulk. Unique on nullable column — multiple NULLs allowed.

#### When to use / when NOT to use

Explicit dialect and type mapping in entity design review. Avoid native queries with ROWNUM traps — use JPQL/Criteria pagination API. Sequence alignment with CACHE for inserts.

#### Production example

Bug: `@Column(unique=true)` on optional email — multiple NULL rows OK in Oracle but product assumed one — fixed with partial unique index pattern via filtered `email IS NOT NULL` unique constraint in migration. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Boolean `@Column` without converter — Oracle no native BOOLEAN. Using `GenerationType.IDENTITY` without testing batch perf. CLOB in equals/hashCode.

#### Interview follow-ups (with model answers)

**Q:** `Dialect` customization for 19c vs 21c?
**A:** For «Hibernate + Oracle specifics.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** UCP vs Hikari with Oracle?
**A:** On «UCP vs Hikari with Oracle», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** JSON type mapping in 21c?
**A:** Trade-off answer for «JSON type mapping in 21c»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Hibernate + Oracle specifics.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Bug: `@Column(unique=true)` on optional email — multiple NULL rows OK in Oracle but product assumed one — fixed with partial unique index pattern via filtered `email IS NOT NULL` unique constraint in . If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 47. Security: least privilege, views, VPD.

**Short answer:** App DB user should **`EXECUTE`** procs / **`SELECT`** views — not own tables or **`DBA`**. **Views** restrict columns/rows; **VPD (`DBMS_RLS`)** adds tenant predicate automatically — still test **IDOR** in app. Never concatenate SQL; binds always; audit definer-rights packages. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Database security layer complements app auth — especially multi-tenant banks. Schema owner vs application executor split is standard hardening. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

VPD policy adds `WHERE tenant_id = SYS_CONTEXT('ctx','tenant')` transparently. Synonyms point app user to API views. `AUTHID DEFINER` procedures gate DML. Column privileges rare but exist. Audit unified auditing (12c+) tracks access.

#### When to use / when NOT to use

VPD when many ad hoc SQL tools must not cross tenants. Views for hiding PII columns from reporting user. Don't rely on VPD alone — app must validate tenant on every request parameter.

#### Production example

App user `APP_RW` has SELECT on `V_CUSTOMER_SAFE` (no SSN column), EXECUTE on `PKG_PAYMENTS`. Direct table access revoked — SQL injection blast radius reduced. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

App connects as schema owner because "Flyway needs it" — separate migration user. VPD policy bypass via direct synonym to base table. Granting `SELECT ANY TABLE`.

#### Interview follow-ups (with model answers)

**Q:** Real Application Security ( RAS ) vs VPD?
**A:** For «Security: least privilege, views, VPD.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Redaction vs view?
**A:** On «Redaction vs view», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Credential rotation with UCP?
**A:** Trade-off answer for «Credential rotation with UCP»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Security: least privilege, views, VPD.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: App user `APP_RW` has SELECT on `V_CUSTOMER_SAFE` (no SSN column), EXECUTE on `PKG_PAYMENTS`. Direct table access revoked — SQL injection blast radius reduced. Capture AWR/ASH SQL_ID, baseline the goo. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 48. Migrations without downtime.

**Short answer:** **Expand/contract** pattern: add nullable column → deploy app writing both → backfill batched → switch reads → add NOT NULL/constraints → drop old. **`CREATE INDEX ONLINE`** (Oracle Enterprise). Avoid single TX **`UPDATE` 100M rows** — undo/redo/log sync kills system; batch with sleep and idempotent chunks. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses.

#### What it is

Zero-downtime schema change is choreography between DDL, app versions, and data backfill — Liquibase/Flyway scripts alone aren't enough without deployment strategy. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Oracle online redefinition (`DBMS_REDEFINITION`), online index build, incremental add partition. Backfill: `WHERE id BETWEEN :lo AND :hi` commits between chunks. Feature flags read new column when populated. Contract phase removes old only after traffic at zero on old path.

#### When to use / when NOT to use

Always plan expand/contract for breaking schema changes in 24/7 systems. Maintenance window for non-online Enterprise features — know license. Sybase/SQL Server online index variations differ.

#### Production example

Rename column flow: add `new_status`, app dual-write, backfill 10M rows in 5K batches off-peak, flip read flag v2.3, drop `old_status` v2.4 — zero downtime, no `ALTER COLUMN RENAME` instant break. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Blocking `ALTER TABLE MODIFY` on huge table. Backfill without index on filter — full scan lock. Dropping old column before all app instances upgraded.

#### Interview follow-ups (with model answers)

**Q:** gh-ost vs Oracle online redefinition?
**A:** For «Migrations without downtime.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Long-running DDL monitoring?
**A:** On «Long-running DDL monitoring», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** Rollback strategy if backfill wrong?
**A:** Trade-off answer for «Rollback strategy if backfill wrong»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Migrations without downtime.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Rename column flow: add `new_status`, app dual-write, backfill 10M rows in 5K batches off-peak, flip read flag v2.3, drop `old_status` v2.4 — zero downtime, no `ALTER COLUMN RENAME` instant break. Cap. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 49. Statistics and stale plans after a release.

**Short answer:** New release introduces **new SQL**, **changed binds**, **data volume growth**, or **missing indexes** — plans regress. Compare **AWR / SQL Monitor** before/after; run targeted **`DBMS_STATS`**; have **SQL baselines** or **rollback** (prior app version) ready. Treat stats job failure as release blocker for major deployments. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Post-release perf incidents often blamed on "bad code" when root cause is optimizer + stats + data shape. Senior release checklist includes DB verification. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

New ORM query shape → new SQL_ID. Auto stats job skipped on partition. Histogram not recreated after load. Bind selectivity change. SQL plan baseline not evolved — or evolved badly. Query store / AWR SQL baseline comparison.

#### When to use / when NOT to use

Pre-prod load test with production-like stats (clone + mask). Post-deploy smoke on top 20 SQL from AWR. Scheduled stats after ETL before business open.

#### Production example

Release Tuesday: p95 up 3×. Diff AWR: new SQL full scanning `events`. Missing index on `(user_id, created_at)` in migration script — hotfix index online + stats — p95 normalized in 1 hour.

#### Common mistakes

Deploy Friday without AWR baseline. Assuming dev plan equals prod. Locking stale bad plan as baseline permanently.

#### Interview follow-ups (with model answers)

**Q:** SQL regression testing in CI?
**A:** For «Statistics and stale plans after a release.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** Pending statistics adoption process?
**A:** On «Pending statistics adoption process», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

**Q:** When to flush shared pool (almost never)?
**A:** Trade-off answer for «When to flush shared pool (almost never)»: the smallest fix that restores SLO without hiding tomorrow's incident. Sometimes that is an online index rebuild on the leading predicate column; sometimes it is rewriting ORM N+1 into one join fetch or a covering index for a dashboard. I communicate write amplification to the app team before adding a fourth index on a ledger table. In interviews I narrate the loop: symptom → SQL_ID → plan diff → waits/locks → rewrite or stats → verify A-Rows → guardrail (baseline, monitor, runbook). That is the bank-grade bar for mixed Oracle/Sybase estates.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Statistics and stale plans after a release.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Release Tuesday: p95 up 3×. Diff AWR: new SQL full scanning `events`. Missing index on `(user_id, created_at)` in migration script — hotfix index online + stats — p95 normalized in 1 hour. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

### 50. Senior SQL answer shape.

**Short answer:** In the interview, narrate a **method**, not magic: reproduce → **actual plan** → **A-Rows vs E-Rows** → join method and **access vs filter** predicates → **wait events/locks** → rewrite set-based with right **index/pagination** → measure write cost before index sprawl. Show trade-off awareness — "I'd baseline this SQL and fix stats before hinting." Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory. In Oracle estates, undo, redo, and latch contention often explain latency better than 'add RAM' guesses. Always verify with an actual execution plan and compare E-Rows to A-Rows before declaring victory.

#### What it is

Meta-question testing communication under pressure — panel listens for structured thinking applicable to their Oracle/Sybase estate, not trivia recitation. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production. This concept bridges the optimizer cost model, storage layout, and how JDBC/Hibernate issues SQL in production.

#### How it works (internals)

Demonstrate loop: symptom (p99 latency) → evidence (ASH SQL_ID) → plan anomaly (NL on millions) → root cause (stale stats / missing index / N+1) → fix + verify → guardrail (baseline, monitor, runbook). Mention app layer when JDBC chatty. Oracle's CBO chooses access paths using statistics, histograms, and bind peeking; locks and MVCC govern concurrent readers and writers.

#### When to use / when NOT to use

Use this narrative for "how would you debug slow query" and design questions. Tailor dialect (Oracle MVCC vs Sybase locking) to interviewer. Don't monologue — pause for constraints (Enterprise Edition, downtime window).

#### Production example

Candidate walks through real incident: ORA-01555 during report — undo, fetch size, standby redirect — not "add RAM." Panel hears senior bar: data + app + ops. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL. Capture AWR/ASH SQL_ID, baseline the good plan, and schedule stats jobs so releases do not regress top SQL.

#### Common mistakes

Jumping to "add index" in ten seconds. Ignoring DML/write path. Claiming expertise without mentioning actual plans. Dismissing PL/SQL/triggers in bank context.

#### Interview follow-ups (with model answers)

**Q:** Design index strategy for new feature under write load?
**A:** For «Senior SQL answer shape.», I start with `DBMS_XPLAN.DISPLAY_CURSOR` actuals — E-Rows vs A-Rows on the driving operation tells me if statistics or bind peeking lied. I check `v$session`/`v$locked_object` for blockers, ASH wait events (db file sequential read, enq: TX-row lock contention, direct path read temp), and whether the SQL_ID changed after last night's stats job. PL/SQL paths get `%SQL%` line profiling when logic is row-by-row. I never hint until I understand plan regression root cause: stale stats, new bind volume, missing index, or cartesian from an ORM-generated join.

**Q:** How would you mentor junior on EXPLAIN PLAN?
**A:** On «How would you mentor junior on EXPLAIN PLAN», production tuning means measuring both read latency and DML cost. I compare AWR before/after release, verify partition pruning, confirm bind variables are shared (not literal flood), and watch undo/retention if long reports hit ORA-01555. For lock-heavy flows I shorten transactions, order `FOR UPDATE` consistently, or switch hot counters to `MERGE` with minimal hold time. PL/SQL bulk `FORALL`/`BULK COLLECT` replaces nested loops when batch jobs must finish inside the batch window. Document the fix with a SQL baseline or extended stats — not a permanent hint nobody remembers.

#### Scenario probe

**Situation:** Month-end batch plus OLTP on «Senior SQL answer shape.» triggers p99 spikes; AWR shows new top SQL_ID, sessions waiting on `enq: TX-row lock contention` or temp tablespace growth; app team blames 'the database'.

**Model answer:** I refuse the blame game — I reproduce with `DBMS_SQLTUNE` or SQL Monitor, pull actual plan with A-Rows, and compare to pre-release baseline. Context: Candidate walks through real incident: ORA-01555 during report — undo, fetch size, standby redirect — not "add RAM." Panel hears senior bar: data + app + ops. Capture AWR/ASH SQL_ID, baseline the good. If nested loops exploded, I check stats and bind selectivity; if hash join spills, I watch `temp` and PGA; if locks dominate, I map blockers in `v$session` and shorten transactions holding `FOR UPDATE`. PL/SQL jobs get bulk operations instead of row-by-row commits. I fix root cause (stats, index, rewrite) before hinting, document in runbook, and add a lightweight regression check in CI against explain plans for the top ten SQL statements.

---

## Deep-dive additions (Q51–Q58)

Oracle upserts, analytics SQL, PL/SQL performance, RAC, cross-dialect migration, and temporal data.

---

### 51. Oracle MERGE statement and upsert patterns

**Short answer:** Oracle **`MERGE`** (upsert) joins target and source on a key, then **WHEN MATCHED UPDATE** and **WHEN NOT MATCHED INSERT** in one statement — atomic per row, avoids race between separate SELECT/INSERT/UPDATE. Prefer `MERGE` over `INSERT ... ON CONFLICT` (PostgreSQL) when on Oracle; watch for **mutating table** triggers and **direct-path** restrictions. For high-volume staging loads, use `FORALL` bulk merge or external tables. Trade-off: single-statement clarity versus harder debugging when `MERGE` matches multiple source rows (ORA-30926).

#### What it is
`MERGE INTO target t USING source s ON (t.id = s.id)` is the standard idempotent sync from staging (`etl_staging_orders`) to production (`orders`). Common in nightly batch and Kafka consumer JDBC upserts. Java apps via JPA often use native query or Spring `JdbcTemplate` for merge performance — Hibernate merge is ORM concept, different from SQL MERGE.

#### How it works (internals)
Optimizer chooses join plan between target and source; unique index on merge key required for predictable behavior. `WHEN MATCHED THEN UPDATE SET ... WHERE <optional filter>` skips updates. `DELETE WHERE` clause on matched branch for sync-delete patterns. One source row must match at most one target row — duplicate source keys cause ORA-30926. Hints: `/*+ USE_HASH(t s) */` on large merges. Logging: full redo on row-by-row merge; consider direct-path insert into staging then merge off-peak.

#### When to use / when NOT to use
Use for CDC upsert, dimension sync, consumer idempotency (`event_id` in staging). Avoid row-by-row merge in tight OLTP loop — batch instead. For simple single-row upsert from Java, `MERGE` or `INSERT ... SELECT ... WHERE NOT EXISTS` — benchmark both. On PostgreSQL migrations, translate to `ON CONFLICT DO UPDATE`.

#### Production example
Kafka consumer lands rows in `payment_events_staging`; job runs `MERGE INTO payments p USING staging s ON (p.payment_id = s.payment_id) WHEN MATCHED THEN UPDATE SET status = s.status WHEN NOT MATCHED THEN INSERT (...)`. Duplicate staging keys from replay caught by pre-merge `GROUP BY` validation — prevented ORA-30926 during Black Friday replay.

#### Common mistakes
- Source query returns duplicate keys — merge fails or updates unpredictably.
- `WHEN MATCHED` updates columns in ON clause — infinite loop risk with triggers.
- Missing index on merge key — full table scan on billion-row target.
- Using MERGE when only INSERT needed — unnecessary lock footprint.

#### Interview follow-ups (with model answers)

**Q:** MERGE vs INSERT + exception handler in PL/SQL?
**A:** `MERGE` is declarative and often faster in set-based ETL. PL/SQL row-by-row with `DUP_VAL_ON_INDEX` exception suits low-volume API path. For 100k+ rows, bulk MERGE or `FORALL` wins; for single-row REST upsert, native MERGE or JDBC `merge` one-liner is fine.

**Q:** How do you make Kafka consumer merge idempotent?
**A:** Merge on natural key (`event_id` or `payment_id`); include `processed_at` and ignore older event versions via `WHERE s.event_version > t.event_version` in UPDATE clause. Inbox table with UNIQUE on `event_id` before merge is belt-and-suspenders.

#### Scenario probe
Merge job fails ORA-30926 during staging load after upstream duplicate fix lagged.

**Model answer:** Dedupe staging: `DELETE FROM staging s WHERE rowid NOT IN (SELECT MIN(rowid) FROM staging GROUP BY payment_id)` or reject file in validation step. Add constraint on staging temp table. Alert on duplicate count in pre-merge QA query.

#### Code / config (when useful)

```sql
MERGE INTO orders o
USING (SELECT :id AS id, :total AS total FROM dual) s
ON (o.order_id = s.id)
WHEN MATCHED THEN
  UPDATE SET o.total = s.total, o.updated_at = SYSTIMESTAMP
WHEN NOT MATCHED THEN
  INSERT (order_id, total, created_at)
  VALUES (s.id, s.total, SYSTIMESTAMP);
```

---

### 52. Analytic/window functions: `ROW_NUMBER`, `LAG`, `LEAD`, running totals

**Short answer:** **Window functions** compute per-row metrics over a partition without collapsing rows like `GROUP BY`. `ROW_NUMBER()` dedupes or ranks; `LAG`/`LEAD` access previous/next row for sessionization and gap detection; `SUM() OVER (ORDER BY ...)` gives running totals. Oracle optimizes with **window sorting** — index on `(partition_key, order_key)` helps. Trade-off: expressive SQL versus plan complexity and temp spills on huge partitions.

#### What it is
Analytics in SQL without exporting to Excel — common in reporting, fraud (time-between-transactions), inventory snapshots, and leaderboard queries. Oracle 12c+ syntax: `OVER (PARTITION BY customer_id ORDER BY txn_time)`. Java apps often push this to SQL rather than loading lists into memory — JDBC returns result set.

#### How it works (internals)
Window buffer sorts partition rows (often `SORT ORDER BY` in plan). `ROW_NUMBER` assigns unique sequence; tie-break with extra sort keys. `LAG(col, 1, default) OVER (...)` reads prior row in partition — NULL for first row. Frame clauses `ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` control running aggregate scope. Parallel query can parallelize full table scan but window sort may be single-threaded bottleneck.

#### When to use / when NOT to use
Use for rankings, YoY comparisons, running balances, dedupe (`WHERE rn = 1`). Avoid nested windows on unfiltered billion-row tables in OLTP path — move to materialized view or batch. Prefer analytic SQL over self-joins for readability when performance acceptable.

#### Production example
Fraud rule: flag if `txn_amount > 3 * AVG(amount) OVER (PARTITION BY customer_id ORDER BY txn_time ROWS BETWEEN 10 PRECEDING AND 1 PRECEDING)`. Batch job writes alerts table nightly; OLTP unchanged. `LAG(status)` detects `SHIPPED → CANCELLED` illegal transitions in audit report.

#### Common mistakes
- Forgetting `ORDER BY` in window — nondeterministic `ROW_NUMBER`.
- `SELECT *` with window in view — accidental perf hit on OLTP.
- Duplicate rows in partition break `LAG` logic.
- Running totals without frame clause — wrong cumulative scope.

#### Interview follow-ups (with model answers)

**Q:** `ROW_NUMBER` vs `RANK` vs `DENSE_RANK`?
**A:** `ROW_NUMBER` always unique (1,2,3); `RANK` skips after ties (1,2,2,4); `DENSE_RANK` no gaps (1,2,2,3). Pick `ROW_NUMBER` for dedupe; `RANK` for olympic-style leaderboards.

**Q:** How optimize window on 500M rows?
**A:** Partition pruning (filter `txn_date` last 90 days), index on `(customer_id, txn_time)`, materialized view refresh off-peak, or pre-aggregate to daily grain then window on smaller set. Check SQL Monitor for temp usage.

#### Scenario probe
Report needs each customer's latest order per region — developers use correlated subquery, runtime 40 minutes.

**Model answer:** Rewrite with `ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC)` filter `rn = 1` — often single pass sort. Verify plan uses partition pruning on `order_date`. Consider `KEEP (DENSE_RANK LAST ...)` alternative for one row per group.

#### Code / config (when useful)

```sql
SELECT customer_id, order_id, order_total,
       SUM(order_total) OVER (
         PARTITION BY customer_id
         ORDER BY order_date
         ROWS UNBOUNDED PRECEDING) AS running_total
FROM orders
WHERE order_date >= TRUNC(SYSDATE) - 90;
```

---

### 53. Oracle autonomous transactions — when and why dangerous

**Short answer:** **`PRAGMA AUTONOMOUS_TRANSACTION`** lets a PL/SQL block commit independently of the caller's transaction — useful for **audit logging** when parent rolls back. Dangerous when used for business data: breaks atomicity, causes **partial commits**, orphan rows, and reconciliation nightmares. Interview answer: only for non-business side effects (error log, audit trail); never for money movement. Trade-off: observability of failures versus transactional integrity.

#### What it is
Autonomous procedure starts separate transaction; `COMMIT` inside commits only that work. Caller may still `ROLLBACK` — audit row persists while order insert rolled back. Pattern: `log_error_autonomous(msg)` in exception handlers. Rare in Java — PL/SQL-specific; know for legacy Oracle estates and DBA interviews.

#### How it works (internals)
Compiler marks unit autonomous; runtime gets separate transaction context. Must `COMMIT` or `ROLLBACK` before exit — else ORA-06519. Nesting: autonomous cannot see uncommitted parent changes (read consistency isolation). Triggers cannot be fully autonomous in all versions — check docs. Performance: extra commit round-trip per call.

#### When to use / when NOT to use
Use: audit, application log table, `DBMS_JOB` error capture when parent must roll back. Never: update inventory, post payment, dual-write to second table "so it survives rollback." If Java service needs audit on failure, use separate transactional datasource or async outbox — not autonomous PL/SQL hidden in trigger.

#### Production example
Legacy trigger `AFTER INSERT ON orders` autonomous-writes `order_audit` — seemed fine until finance found orders rolled back for fraud still showing in audit — compliance report wrong. Fix: move audit to same transaction or event outbox; autonomous only for `error_log` table.

#### Common mistakes
- Autonomous update of business entities "for resilience."
- Hidden autonomous triggers — developers unaware of commit side effects.
- Forgetting COMMIT in autonomous proc — ORA-06519.
- Autonomous + mutating table trigger combinations.

#### Interview follow-ups (with model answers)

**Q:** Alternative to autonomous audit in modern Java + Oracle?
**A:** Same-transaction insert to `audit` table; or transactional outbox event consumed by audit service; or `SYS_CONTEXT` + flashback query for forensics. Autonomous last resort for error logger only.

**Q:** Can autonomous procedure call non-autonomous?
**A:** Yes, but called proc runs in autonomous transaction context — understand commit boundaries. Debugging requires explicit documentation in package header.

#### Scenario probe
Developer adds autonomous transaction to save payment on failure "so we don't lose it." Your review?

**Model answer:** Reject — payment must roll back with failed order. Use idempotent retry, outbox, or saga compensation. Autonomous payment creates duplicate charge risk and breaks ACID story to auditors.

#### Code / config (when useful)

```sql
CREATE OR REPLACE PROCEDURE log_error(p_msg VARCHAR2) AS
  PRAGMA AUTONOMOUS_TRANSACTION;
BEGIN
  INSERT INTO error_log (msg, logged_at) VALUES (p_msg, SYSTIMESTAMP);
  COMMIT;
END;
/
```

---

### 54. PL/SQL collections (`TABLE`, `VARRAY`, nested tables) and bulk bind

**Short answer:** PL/SQL **collections** hold arrays in memory — **associative arrays** (`TABLE OF` indexed by PLS_INTEGER), **nested tables**, **VARRAYs**. **`FORALL`** and **`BULK COLLECT`** reduce context switches between SQL and PL/SQL — 10–100× faster than row-by-row loops. Java batch JDBC (`addBatch`/`executeBatch`) is the app-layer equivalent. Trade-off: memory for large `BULK COLLECT LIMIT` versus speed; always use `LIMIT` to avoid PGA blow-up.

#### What it is
Oracle PL/SQL performance foundation for ETL jobs, package procedures called from Java, and legacy batch. `FORALL i IN 1..arr.COUNT INSERT ... VALUES arr(i)` issues one array DML. Collections passed as bind variables to JDBC via `OracleConnection.createOracleArray`.

#### How it works (internals)
Row-by-row loop: PL/SQL ↔ SQL context switch per iteration. `BULK COLLECT INTO arr LIMIT 10000` fetches 10k rows per round trip. `FORALL` generates array insert/update; `SAVE EXCEPTIONS` continues on dup key collecting `%BULK_EXCEPTIONS`. Nested table stored in DB can be column type; VARRAY fixed max size. Associative array index can be string (`INDEX BY VARCHAR2`).

#### When to use / when NOT to use
Use bulk for any loop >100 iterations touching SQL. Avoid unbounded `BULK COLLECT` without `LIMIT` — ORA-04036 PGA. For Java services, prefer JDBC batch unless logic lives in PL/SQL package already.

#### Production example
Nightly job processed 2M price updates in row loop — 3 hours. Rewrote with `FORALL` batch 5000 + `SAVE EXCEPTIONS` logging bad SKUs — 8 minutes. Java caller unchanged — still `CallableStatement` calling package.

#### Common mistakes
- No `LIMIT` on cursor bulk collect — memory exhaustion.
- Assuming `FORALL` row count equals array count when `%ROWCOUNT` differs with exceptions.
- Mixing `FORALL` indices after deleting from collection.
- Reimplementing bulk in Java row loop calling single-row proc.

#### Interview follow-ups (with model answers)

**Q:** `FORALL` vs executemany in JDBC?
**A:** Same performance idea — minimize round trips. If logic in PL/SQL, `FORALL` inside package; if in Java service, `JdbcTemplate.batchUpdate`. Do not row-loop across network from Java to PL/SQL.

**Q:** What does `SAVE EXCEPTIONS` do?
**A:** `FORALL ... SAVE EXCEPTIONS` continues DML on remaining rows; query `SQL%BULK_EXCEPTIONS` for failed indices and error codes — ideal for staging loads with few bad rows.

#### Scenario probe
AWR shows PL/SQL procedure `update_prices` with 2M executions — one per SKU.

**Model answer:** Refactor to bulk: load SKUs into collection, `FORALL` update, or merge from staging table. Measure PGA with `LIMIT` tuning; add job monitoring on rows/sec metric.

#### Code / config (when useful)

```sql
DECLARE
  TYPE sku_list IS TABLE OF VARCHAR2(32);
  skus sku_list := sku_list('A','B','C');
BEGIN
  FORALL i IN 1..skus.COUNT
    UPDATE products SET price = price * 1.1 WHERE sku = skus(i);
  COMMIT;
END;
/
```

---

### 55. Oracle RAC basics: cache fusion, global locks

**Short answer:** **Oracle RAC** (Real Application Clusters) is multiple instances on shared storage (ASM) presenting one database. **Cache fusion** transfers data blocks between instances via private interconnect instead of disk — maintains consistency. **Global cache locks** (GC enqueue waits) coordinate block ownership across nodes. Java apps use SCAN hostname and TAF/FCF for failover. Trade-off: horizontal DB scale versus cluster licensing cost and interconnect latency sensitivity.

#### What it is
Enterprise Oracle HA/scale pattern — two+ nodes in cluster; JDBC thin driver connects to SCAN VIP. Relevant for senior roles on bank/telecom Oracle estates. Not Exadata-specific but often paired. Understand for interview: why `gc cr grant` waits appear in AWR.

#### How it works (internals)
Instance A modifies block; instance B needs it — resource mastering node grants block via interconnect (cache fusion). Excessive cross-instance block ping causes `gc buffer busy` waits — wrong partitioning or hot index on RAC. **GV$** views (`GV$SESSION`) cluster-wide. Undo and redo per instance; shared datafiles on ASM. DML on same hot block from many nodes → serialization.

#### When to use / when NOT to use
RAC when need HA + scale-out OLTP on Oracle stack with budget. Alternative: Data Guard standby for HA without scale-out writes. Application design: partition workload by key to reduce block ping (`customer_id` hash to service name).

#### Production example
Java payroll batch and OLTP shared hot index on `employees(status)` — RAC node 2 showed 40% `gc cr` waits. Fix: reverse key index, partition table by `dept_id`, route batch job to single service with `SERVICE_NAME=batch_svc`. p99 improved 3×.

#### Common mistakes
- Treating RAC like two independent databases — shared blocks matter.
- No SERVICE_NAME separation for batch vs OLTP.
- Ignoring interconnect bandwidth — fusion slower than local cache.
- Sequence hot block on RAC — use `CACHE` size or ordered sequences awareness.

#### Interview follow-ups (with model answers)

**Q:** RAC vs Active Data Guard?
**A:** RAC: multiple instances, one DB, scale reads/writes with coordination cost. ADG: primary + standby, failover for DR, reads on standby lagging. Many use both — RAC for local HA, ADG for DR site.

**Q:** What JDBC URL pattern for RAC?
**A:** `jdbc:oracle:thin:@(DESCRIPTION=(ADDRESS_LIST=(ADDRESS=(PROTOCOL=TCP)(HOST=scan)(PORT=1521)))(CONNECT_DATA=(SERVICE_NAME=app_svc)))` — SCAN resolves all nodes; use `oracle.jdbc.fanEnabled` for FCF with UCP pool.

#### Scenario probe
AWR after RAC expansion shows increased `gc buffer busy` — app team says "add node."

**Model answer:** More nodes can worsen block ping if workload not partitioned. Analyze hot objects in ASH, affinity by service, partition hot tables, review index design. Scale-out is not free on RAC.

#### Code / config (when useful)

```properties
spring.datasource.url=jdbc:oracle:thin:@//scan.example.com:1521/orders_svc
oracle.jdbc.fanEnabled=true
```

---

### 56. SQL Server vs Oracle: `TOP` vs `FETCH`, `IDENTITY` vs `SEQUENCE`

**Short answer:** SQL Server **`TOP n`** / **`OFFSET-FETCH`** maps to Oracle **`FETCH FIRST n ROWS ONLY`** (12c+) or `ROWNUM` wrapper pre-12c. SQL Server **`IDENTITY`** column auto-increment differs from Oracle **`SEQUENCE` + trigger** or **`GENERATED AS IDENTITY`** (12c+). Migration pitfall: `TOP` without `ORDER BY` is nondeterministic on both; Oracle sequences gap on rollback while IDENTITY gaps too but semantics differ in bulk insert. Know both for JD migrations and polyglot teams.

#### What it is
Cross-dialect fluency for teams moving Sybase/SQL Server workloads to Oracle or maintaining hybrid reporting. Java JPA `@GeneratedValue` abstracts some differences — native SQL in reports does not.

#### How it works (internals)
SQL Server: `SELECT TOP 10 * FROM t ORDER BY id DESC`; paging `ORDER BY id OFFSET 20 ROWS FETCH NEXT 10 ONLY`. Oracle 12c+: same `OFFSET n ROWS FETCH NEXT m ROWS ONLY`; legacy `SELECT * FROM (SELECT ... ORDER BY id) WHERE ROWNUM <= 10`. Identity: SQL Server `INT IDENTITY(1,1)`; Oracle `GENERATED BY DEFAULT AS IDENTITY` or `sequence.NEXTVAL` in trigger (older pattern). Hibernate `GenerationType.SEQUENCE` with `allocationSize` on Oracle.

#### When to use / when NOT to use
Always specify `ORDER BY` with limit queries. On Oracle new apps prefer identity or sequence with default — avoid trigger overhead. In migration scripts, mechanical translation tools miss `TOP` in subqueries — manual review.

#### Production example
Report migrated from SQL Server used `SELECT TOP 1` without ORDER BY — Oracle rewrite returned random row daily. Fix: explicit `ORDER BY created_at DESC FETCH FIRST 1 ROW ONLY`. IDENTITY insert in SSIS package replaced with Oracle sequence in JDBC batch — gaps accepted per audit.

#### Common mistakes
- `ROWNUM` applied before ORDER BY in Oracle subquery mistake.
- Assuming IDENTITY insert rules identical in bulk load tools.
- `TOP 100 PERCENT` nonsense in SQL Server carried to Oracle.
- Sequence cache 20 on RAC causing gaps — document as normal.

#### Interview follow-ups (with model answers)

**Q:** Oracle `ROWNUM` vs `FETCH FIRST`?
**A:** `FETCH FIRST` is SQL standard and respects ORDER BY in same query level. `ROWNUM` assigned before sort unless subquery wrapper — legacy pattern error-prone. Use `FETCH FIRST` on 12c+.

**Q:** JPA on Oracle — IDENTITY or SEQUENCE?
**A:** `IDENTITY` simpler; `SEQUENCE` with `allocationSize=50` reduces round trips on bulk insert. Match DBA preference and existing schema; never mix two generators on same table.

#### Scenario probe
Migrate paging API from SQL Server `OFFSET/FETCH` to Oracle 11g — approach?

**Model answer:** Wrapper subquery with `ROWNUM` between bounds or upgrade to 12c+ for native OFFSET-FETCH. Test stable sort key; expose same API contract. Add integration test comparing page contents cross-dialect if dual-run period.

#### Code / config (when useful)

```sql
-- Oracle 12c+
SELECT order_id, total
FROM orders
ORDER BY created_at DESC
FETCH FIRST 20 ROWS ONLY
OFFSET 40 ROWS;
```

---

### 57. Sybase ASE → Oracle migration pitfalls (JD-relevant)

**Short answer:** **Sybase ASE** to **Oracle** migrations hit: different **NULL** and empty string semantics, **`IDENTITY`** vs sequence, **`TOP`** vs `ROWNUM`/`FETCH`, **T-SQL vs PL/SQL** procedural differences, **`datetime` precision**, **`text/image`** to LOB, and **locking** (page vs row, `HOLDLOCK` vs `FOR UPDATE`). Java JDBC apps may embed Sybase-specific SQL — grep for `TOP`, `@@identity`, `getdate()`. Trade-off: migration window versus parallel run with dual-write validation.

#### What it is
Common in banking/enterprise JDs — legacy Sybase cores moving to Oracle Exadata or RDS Custom. Senior engineer validates ETL, stored proc rewrite, and Hibernate dialect change (`SybaseDialect` → `Oracle12cDialect`). Data type mapping documents are critical deliverable.

#### How it works (internals)
Sybase `''` often equals single space in VARCHAR; Oracle treats `''` as NULL. `SELECT TOP` → `FETCH FIRST`. `GETDATE()` → `SYSDATE`/`CURRENT_TIMESTAMP`. `ISNULL` → `NVL`/`COALESCE`. Temp tables `#t` → `GLOBAL TEMPORARY TABLE`. Procs: T-SQL cursors and `@@rowcount` rewrite to PL/SQL implicit cursors. JDBC: `jdbc:sybase` URLs to thin Oracle; test `setBoolean` mapping. Charset UTF-8 migration for international data.

#### When to use / when NOT to use
Plan phased migration: read-only reports first, then OLTP cutover with rollback script. Parallel run compares row counts and hash sums per table. Do not big-bang without proc compilation validation in CI.

#### Production example
Trade capture system: 400 Sybase procs, Java Spring with native queries containing `TOP 1`. Team built automated scanner flagging Sybase idioms; proc rewrite factory with unit tests on ref cursor results. Cutover weekend: 2-hour rollback window unused; post-migration ORA-12899 caught oversized VARCHAR2 — Sybase allowed longer implicit truncate.

#### Common mistakes
- Assuming Hibernate fixes all SQL — native queries break.
- Missing `TO_DATE` format masks on string literals.
- Lock escalation differences causing deadlock pattern changes.
- Not regression-testing `MONEY`/`NUMERIC` scale precision.

#### Interview follow-ups (with model answers)

**Q:** How validate migration correctness?
**A:** Table-level row count + checksum hash, sample business scenario E2E tests, parallel run shadow reads comparing API responses, replay production read traffic on Oracle replica. Finance sign-off on penny totals.

**Q:** Sybase `HOLDLOCK` equivalent in Oracle?
**A:** `SELECT ... FOR UPDATE` or serializable isolation — semantics differ; review transaction boundaries in Java `@Transactional` boundaries. Load test lock duration.

#### Scenario probe
Java app works on Sybase; first Oracle deploy fails on `SELECT TOP 10 * FROM trades`.

**Model answer:** Replace with `FETCH FIRST 10 ROWS ONLY` and mandatory `ORDER BY trade_time DESC`. Add CI rule banning `TOP ` in SQL files. Retest pagination endpoints.

#### Code / config (when useful)

```sql
-- Sybase
SELECT TOP 10 trade_id FROM trades ORDER BY trade_time DESC;
-- Oracle
SELECT trade_id FROM trades ORDER BY trade_time DESC FETCH FIRST 10 ROWS ONLY;
```

---

### 58. Temporal tables and system-versioned rows (Oracle/SQL Server)

**Short answer:** **Temporal tables** (SQL Server **system-versioned**, Oracle **Flashback** / **Temporal Validity** / 23ai **SQL temporal**) store row **history** with `ValidFrom`/`ValidTo` or transaction time — query "as of" prior state for audit and compliance. SQL Server: `FOR SYSTEM_TIME AS OF`. Oracle: `FLASHBACK QUERY AS OF TIMESTAMP` or application-maintained history table. Trade-off: storage growth and query complexity versus regulator-ready audit trail without bespoke triggers.

#### What it is
Regulated industries need "what was account balance on March 1?" — temporal features answer without restoring backup. Java: Hibernate Envers for app-level history; database temporal for tamper-evident DBA-managed history. Know both SQL Server native temporal and Oracle flashback for JD interviews.

#### How it works (internals)
SQL Server: current table + `history` table auto-populated on UPDATE/DELETE; system time columns `GENERATED ALWAYS`. Queries append `FOR SYSTEM_TIME AS OF @t`. Oracle Flashback uses undo — retention limited by `undo_retention`; long audit needs **Flashback Archive** (FDA) or physical history table. Oracle 23ai adds standard temporal period definitions. Index current table normally; history table partitioned by time.

#### When to use / when NOT to use
Use when auditors require point-in-time row state and ORM Envers insufficient (direct SQL changes). Avoid on ultra-high churn tables without partition purge policy — storage explodes. Define retention (7 years) and archive job.

#### Production example
SQL Server `accounts` system-versioned; compliance query `SELECT * FROM accounts FOR SYSTEM_TIME AS OF '2024-06-01' WHERE id = 5` for dispute. Oracle equivalent: FDA on `accounts` with `VERSIONS BETWEEN TIMESTAMP` query. Java report service parameterizes `asOf` timestamp — read-only route.

#### Common mistakes
- Flashback query beyond undo retention — ORA-01555.
- Forgetting history table indexes for as-of queries.
- App bypassing temporal with direct JDBC update on history table.
- Mixing business effective dating with system versioning concepts.

#### Interview follow-ups (with model answers)

**Q:** Envers vs database temporal?
**A:** Envers: JPA entity audit, easy in Java, misses ad-hoc SQL. Database temporal: captures all changes, DBA governance, better for compliance. Use both: Envers for app debug, temporal for legal record.

**Q:** How purge old history?
**A:** SQL Server: partition switch out old history partitions. Oracle FDA: archive tablespace move + drop partition. Legal holds may block purge — workflow required.

#### Scenario probe
Auditor asks account balance on date 2 years ago; undo retention is 24 hours.

**Model answer:** Flashback Query insufficient — should have Flashback Archive or system-versioned history table from go-live. Emergency: restore backup to clone DB and query — painful. Proposal: enable FDA or SQL Server temporal with 7-year retention policy.

#### Code / config (when useful)

```sql
-- SQL Server system-versioned
CREATE TABLE dbo.accounts (
  id INT PRIMARY KEY,
  balance DECIMAL(18,2),
  SysStartTime DATETIME2 GENERATED ALWAYS AS ROW START HIDDEN,
  SysEndTime   DATETIME2 GENERATED ALWAYS AS ROW END HIDDEN,
  PERIOD FOR SYSTEM_TIME (SysStartTime, SysEndTime)
) WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.accounts_history));

SELECT * FROM dbo.accounts FOR SYSTEM_TIME AS OF '2023-01-15T00:00:00' WHERE id = 42;
```

---

## Scenario-based interview drills

### S1. Plan regression after Tuesday release

**Situation:** Order search p95 jumps from 120ms to 4s after Hibernate upgrade. AWR shows new SQL_ID doing full table scan on `orders` (80M rows). App team insists 'no SQL changed'.

**What they're testing:** Execution plan analysis, ORM vs SQL, statistics, AWR comparison.

**How to structure your answer:**
- Compare SQL_ID before/after
- Actual plan vs estimated rows
- Stats and bind variables
- Fix without permanent hint

**Model answer:** ORM generated different SQL — common after fetch or join changes. I pull last known good plan from AWR baseline or SQL plan history, run `DBMS_XPLAN.DISPLAY_CURSOR` with `+peeked_binds` on prod-like data. If E-Rows 1000 but A-Rows 8M, stats or bind peeking failed. Check `DBMS_STATS` job logs; histogram on `status` may be stale after weekend bulk update. Fix: gather stats on `orders`, create composite index matching `WHERE tenant_id = ? AND status = ? ORDER BY created_at DESC` — leading columns matter. Avoid emergency `INDEX` hint without ticket — add SQL baseline after verification. Hibernate: add `@EntityGraph` or explicit join fetch instead of accidental cartesian. CI: capture explain for top queries. Communicate write cost if new index added. Senior loop: evidence before index; measure DML impact. Post-fix SQL Monitor proves p95 restored under peak bind values.

**Common weak answers:** 'Flush shared pool.' 'Add RAM.' Hint forever without stats fix.

**Follow-up probes (with answers):**

**Q:** When SQL baseline?
**A:** After confirming good plan on representative binds — not as first knee-jerk.

**Q:** Bind peeking issue?
**A:** Adaptive cursor sharing or separate SQL for skewed status values.

---

### S2. ORA-01555 on month-end report

**Situation:** Finance report runs 90 minutes via JDBC default fetch; fails with ORA-01555 snapshot too old. Undo tablespace is AUTOEXTEND ON but storage team is nervous.

**What they're testing:** Oracle MVCC, undo retention, fetch size, long-running read strategy.

**How to structure your answer:**
- Explain ORA-01555 mechanism
- Short-term report options
- Undo/retention tuning
- Architectural fix

**Model answer:** ORA-01555 means undo needed to construct consistent read block was overwritten — long cursor held open while DML churned undo. Short-term: rerun with larger fetch size to reduce round trips, or run during quiet window, or use `FLASHBACK` query snapshot if acceptable. Tune `undo_retention` and ensure undo tablespace sized for peak DML — not just AUTOEXTEND panic. Architectural: materialized view or summary table refreshed nightly for finance; report reads MV not live ledger. JDBC: `setFetchSize` aligned with memory; avoid ORM scrolling infinite stream without commit boundaries. For ADG, redirect heavy read to standby with lag awareness. Never 'just increase undo' without understanding DML rate during report. Document in runbook: max report duration vs undo retention. Senior answer names MVCC, not generic reboot. Partition pruning on `posted_month` cuts report scope dramatically.

**Common weak answers:** 'Restart database.' 'Use NOLOCK.' No undo/MVCC explanation.

**Follow-up probes (with answers):**

**Q:** Fetch size trade-off?
**A:** Larger fetch reduces calls but increases client memory — balance per row width.

**Q:** MV vs live query?
**A:** MV for regulatory snapshots; live only when intraday accuracy mandatory.

---

### S3. Deadlock between batch and OLTP

**Situation:** Nightly pricing batch updates `products` while checkout updates `order_lines` referencing products. ORA-00060 deadlocks spike at 02:00; checkout fails for customers.

**What they're testing:** Deadlock graphs, lock ordering, batch scheduling, transaction scope.

**How to structure your answer:**
- Read deadlock trace
- Consistent lock order
- Shrink transaction scope
- Schedule or redesign batch

**Model answer:** Deadlock means cyclic wait — Oracle picks victim and rolls back one session. I pull `ORA-00060` trace or `v$session` blocker chain: batch likely locks `products` then touches `order_lines` while checkout does reverse order. Fix: standardize lock order — always lock parent `products` before child rows, or batch uses `MERGE` in small commits ordered by `product_id`. Shrink batch transactions — 5K row commits with `FORALL` instead of one giant update. Schedule batch outside checkout peak or use online rebuild pattern on staging table swap. OLTP: `SELECT FOR UPDATE NOWAIT` fail fast with retry UX vs hanging. Monitor `enq: TX-row lock contention` in ASH. Senior teams redesign so batch does not share hot rows with OLTP — versioned price table effective-dated instead of in-place overwrite during night. Application retry on deadlock must be idempotent — unique keys on orders.

**Common weak answers:** 'Kill batch job.' 'Increase deadlock detector.' No lock order analysis.

**Follow-up probes (with answers):**

**Q:** NOWAIT vs SKIP LOCKED?
**A:** NOWAIT fails fast for user-facing; SKIP LOCKED for queue workers grabbing work.

**Q:** Detect in AWR?
**A:** Deadlock count in `dba_hist_active_sess_history` and alert log mining.

---

### S4. Missing index discovered in AWR top SQL

**Situation:** AWR shows `SELECT * FROM payments WHERE customer_id = ? ORDER BY created_at DESC` at 40% DB time; plan is full table scan. Table has 200M rows; product wants feature live tomorrow.

**What they're testing:** Index design, write amplification, online DDL, covering indexes.

**How to structure your answer:**
- Validate selectivity
- Composite index column order
- Online build plan
- Measure DML impact

**Model answer:** High DB time + filter on `customer_id` screams composite index `(customer_id, created_at DESC)`. Verify selectivity with stats — if `customer_id` always returns millions, index may not help. Use `DBMS_ONLINE_INDEX` or Enterprise online rebuild; in Standard Edition, build `UNUSABLE` then rebuild off-peak. Include `amount, currency` in index only if query is covering — Oracle include syntax via index-only columns strategy. Before deploy: measure insert rate on `payments` — each index slows writes. Hibernate: ensure query uses bind not literal. After index: confirm `INDEX RANGE SCAN DESC` in plan, A-Rows match expectation. Add monitoring on index usage `v$object_usage`. Senior refusal: no six indexes on every WHERE column — one purposeful composite. Document rollback: drop index online if regression. Keyset pagination in app matches index sort direction.

**Common weak answers:** 'Index every column.' Offline rebuild during peak. No write-cost mention.

**Follow-up probes (with answers):**

**Q:** INCLUDE columns?
**A:** Covering index avoids table lookup when all selected cols are in index leaf.

**Q:** Reverse key index?
**A:** Only for monotonic insert hot right-edge contention — rare fix.

---

### S5. Row lock contention on order status

**Situation:** Warehouse scanners call `UPDATE orders SET status = 'PICKED' WHERE id = ?` ; p99 spikes; ASH shows `enq: TX-row lock contention` on a few hot `orders` rows during flash sale.

**What they're testing:** Row locks, transaction length, design alternatives to hot-row updates.

**How to structure your answer:**
- Confirm hot row pattern
- Shorten transactions
- Queue or shard pattern
- Avoid unnecessary FOR UPDATE

**Model answer:** Flash sales create hot rows when everyone updates same inventory or order header. I confirm blockers in `v$session`: many sessions waiting on same `rowid`. Shorten TX — update status only, no remote HTTP inside transaction. Remove accidental `SELECT FOR UPDATE` on parent order when child line update suffices. Pattern change: status transitions via `order_events` append-only table — no single hot row; readers join latest event. Or shard inventory counters per SKU partition. Retry with exponential backoff on `ORA-00054 resource busy` with NOWAIT. PL/SQL: bulk updates ordered by primary key reduce deadlock probability. Never hold locks across user think time. Senior design moves contention from one row to partitioned queue — architectural, not just `INITRANS` tweak. Metrics on lock wait time per endpoint guide capacity decisions.

**Common weak answers:** 'Raise INITRANS to 100.' Long TX with external API calls inside.

**Follow-up probes (with answers):**

**Q:** Optimistic vs pessimistic?
**A:** Optimistic versioning for admin edits; short pessimistic only when inventory must be exact.

**Q:** Event table trade-off?
**A:** More rows but fewer hot updates — queries need latest-event pattern or MV.

---

### S6. Mutating trigger ORA-04091

**Situation:** New `BEFORE INSERT` trigger on `orders` updates `customer_stats`; batch load fails with ORA-04091 table is mutating. Developer says 'it works in unit test with one row'.

**What they're testing:** PL/SQL triggers, mutating table constraint, compound triggers, design smell.

**How to structure your answer:**
- Explain mutating trigger error
- Why single-row test lied
- Safer patterns
- When to remove trigger

**Model answer:** ORA-04091 occurs when row trigger queries or updates the same table that fired it — classic PL/SQL trap. Single-row unit test passes; bulk insert or cascade fails. Fixes ranked: (1) move aggregation to materialized view or scheduled job — best; (2) compound trigger with collection buffering flush after statement; (3) autonomous transaction for audit only — not for business invariants; (4) replace trigger with explicit service-layer SQL in batch job. I read trigger in `DBA_SOURCE`, map to calling paths including Hibernate batch inserts. Bank interview: seniors distrust triggers for business rules — hidden, untested in CI, surprise latency. If trigger must stay, document and add integration test with 500-row bulk. Never stack triggers on triggers. Post-fix: SQL% rowcount validation in batch job. Code review rule: new triggers need DBA sign-off and perf test.

**Common weak answers:** 'Use autonomous transaction for everything.' 'Disable trigger in prod.'

**Follow-up probes (with answers):**

**Q:** Compound trigger?
**A:** Buffers row-level changes, processes in AFTER STATEMENT — avoids mutating read.

**Q:** Trigger vs app logic?
**A:** App logic versioned in Git; triggers opaque to most Java devs — prefer app for rules.

---

### S7. PL/SQL row-by-row nightly job overrun

**Situation:** Nightly settlement PL/SQL loops cursor updating 5M `ledger_entries` one row at a time; job missed SLA three nights; undo and redo generation alarms fire.

**What they're testing:** Bulk COLLECT/FORALL, set-based SQL, redo/undo, job scheduling.

**How to structure your answer:**
- Profile current PL/SQL
- Convert to bulk or set SQL
- Commit batching
- Verify redo impact

**Model answer:** Row-by-row PL/SQL in a loop is a performance anti-pattern at millions of rows. I rewrite with `BULK COLLECT LIMIT 10000` into array, `FORALL` update, commit every N batches to cap undo — or single set-based `MERGE`/`UPDATE` if rule allows. Measure before/after with `SQL%` and redo size from `v$sesstat`. Enable `PLSQL_CODE_TYPE=NATIVE` only after profiling — minor gain vs algorithm fix. Parallel DML if Enterprise and table partitioned — coordinate with DBAs. Schedule job when OLTP low; use `DBMS_SCHEDULER` chains with max duration alert. Hibernate apps should not fight this — settlement belongs in PL/SQL or ETL, not scattered in Java loops. Senior answer quantifies rows/sec improvement and redo reduction, not 'we added parallelism' blindly. Idempotent batch keys let safe rerun after failure without double-settlement.

**Common weak answers:** 'Increase commit frequency only.' Keep cursor loop. No BULK COLLECT.

**Follow-up probes (with answers):**

**Q:** FORALL errors?
**A:** SAVE EXCEPTIONS collects failures — log bad rows without aborting entire batch.

**Q:** Pure SQL vs PL/SQL?
**A:** Set-based SQL first; PL/SQL for procedural exceptions per row.

---

### S8. Stale stats after partition exchange

**Situation:** ETL exchanges daily partition into `facts` table; Monday morning dashboards slow; plans show full scans; stats job ran before exchange completed.

**What they're testing:** Statistics lifecycle, partition exchange, extended stats, plan stability.

**How to structure your answer:**
- Timeline stats vs exchange
- Gather partition stats
- Verify plan per partition
- Automate post-ETL gather

**Model answer:** Partition exchange swaps data quickly but statistics may be missing or wrong for new partition — optimizer defaults to bad cardinality. Fix: `DBMS_STATS.GATHER_TABLE_STATS` with `granularity => 'PARTITION'` immediately after exchange; include extended stats if correlated columns. Check `pending` stats adoption if using incremental stats. Compare SQL plan before/after on dashboard SQL_ID. AWR diff Monday vs Sunday. Automate: ETL last step calls gather stats job; failure pages DBA before business open. Consider locked stats on historical partitions with stable shape. Hibernate `@PartitionKey` queries must include partition key in WHERE for pruning — stats useless if pruning fails. Senior ops: stats job failure is release blocker for ETL-heavy nights. SQL plan baselines protect critical dashboard SQL after verified good plan.

**Common weak answers:** 'Lock stats forever on first good plan.' No post-exchange gather.

**Follow-up probes (with answers):**

**Q:** Incremental stats?
**A:** Helps large tables — ensure exchange marks partition needing gather.

**Q:** Extended stats?
**A:** For correlated `(region, status)` filters common in BI queries.

---

### S9. Zero-downtime column rename migration

**Situation:** Regulatory label change requires renaming `customer.ssn` to `tax_identifier` across Oracle DB, Sybase legacy, and three Hibernate services. Downtime window is zero.

**What they're testing:** Expand-contract migration, dual-write, backfill, ORM compatibility.

**How to structure your answer:**
- Expand: add new column
- Dual-write and backfill
- Switch reads
- Contract: drop old

**Model answer:** Never `ALTER TABLE RENAME` on live column in one shot for multi-service estates. Expand: add `tax_identifier` nullable; deploy app v1 writing both columns; backfill in batches with `ROWNUM`/keyset chunks and low parallel degree monitoring redo. Switch reads to new column in v2; verify Hibernate `@Column` mapping and native queries. Sybase leg gets same pattern — dialect differences in batch scripts. Contract: stop writing old column v3, drop after traffic zero — use `DBMS_REDEFINITION` or online rebuild if needed. Feature flag controls read path. Rollback: keep old column until bake period ends. Document in migration ticket: batch size, undo estimate, verification queries. Senior bar: coordinates app and DBA timelines — schema-only change without app deploy is fantasy. Partial unique indexes apply only after backfill completes on nullable transition.

**Common weak answers:** 'Big bang rename Friday night.' Single service deploy assumption.

**Follow-up probes (with answers):**

**Q:** gh-ost vs Oracle redefinition?
**A:** Oracle online redefinition or add-column pattern; gh-ost for MySQL family.

**Q:** Backfill throttle?
**A:** Parallel 5 with `LOG ERRORS` — watch undo and archivelog.

---

### S10. Senior slow-query war room

**Situation:** CEO dashboard blank; `order_summary_mv` refresh failed; ad-hoc query on base `orders` runs 25 minutes; app pool exhausted. VP asks 'what is wrong with Oracle' in all-hands channel.

**What they're testing:** Structured methodology, communication, plan/lock/stats triage, senior composure.

**How to structure your answer:**
- Stabilize blast radius
- Evidence gathering loop
- Smallest fix first
- Communicate and prevent recurrence

**Model answer:** I calm the room with facts, not defensiveness. Stabilize: kill runaway session if needed, redirect traffic to cached read replica or stale MV with banner 'data as of T-1h', increase pool temporarily only with timeout caps. Evidence: SQL_ID from ASH, SQL Monitor report, plan with A-Rows, blocker checks, stats last gather time. Likely story: MV broken so app hits raw 80M row table with NL join due to stale stats. Fix path: refresh stats on `orders`, restore MV job, add missing index if plan proves it, rewrite query to prune partitions. Communicate ETA and workaround to CEO staff — not technical jargon. Post-incident: guardrail query timeout in app, alert on MV refresh failure, top-10 SQL regression monitor in CI. Interview gold: narrate method calmly — reproduce, plan, waits, locks, fix, verify — with one production war story detail. That beats reciting B-tree theory. Runbook links SQL_ID to owner service and on-call rotation.

**Common weak answers:** 'Database is slow.' 'Add CPU.' No method, no communication plan.

**Follow-up probes (with answers):**

**Q:** Kill session criteria?
**A:** After identifying serial offender with DBA approval — capture SQL Monitor first.

**Q:** Mentor junior on EXPLAIN?
**A:** Teach E-Rows vs A-Rows on real incident, not abstract diagrams only.

---

## Oracle rapid-fire

- `DUAL`
- `NVL` vs `COALESCE` vs `NVL2`
- `DECODE` vs `CASE`
- `MERGE` (upsert)
- `CONNECT BY` vs recursive CTE
- `ROWNUM` filter before `ORDER BY` trap
- `dbms_metadata.get_ddl`
- `v$session`, `v$sql`, `v$locked_object`
- `ORA-00054` resource busy
- `ORA-00942` synonym/grant
