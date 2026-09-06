# Hibernate / JPA — 58 Senior Interview Questions

**Bar:** Persistence context, flush, dirty checking, N+1, locking, caching. "I use Spring Data" is not enough.

---

### 1. Session vs EntityManager vs persistence context.

**Short answer:** JPA's `EntityManager` is the standard API; Hibernate's `Session` extends it. The persistence context (PC) is the first-level cache, identity map, and dirty-checking arena for one unit of work — typically aligned with a single database transaction in Spring. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
The persistence context is where managed entities live between load and flush/commit. It ensures one Java object instance per database row within a unit of work. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`EntityManager` delegates to Hibernate `Session` internally. PC stores entities by id (identity map). `EntityManager.clear()` detaches all. In Spring `@Transactional`, the PC usually opens at TX begin and closes at commit/rollback.

#### When to use / when NOT to use
Inject `EntityManager`/`@PersistenceContext` in domain services when you need explicit control. Prefer repositories for simple CRUD. Avoid long-lived PC (OSIV abuse). Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Order placement TX: load `Order`, add lines, flush at commit — one PC, one connection from Hikari for TX duration. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Confusing Hibernate SessionFactory singleton with Session per TX; assuming PC spans multiple DBs; mixing `EntityManager` from two persistence units.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** What is `PersistenceContextType.TRANSACTION` vs `EXTENDED`?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. JPA's `EntityManager` is the standard API; Hibernate's `Session` extends it. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How does Spring bind EM to thread?
**A:** Senior answer to 'How does Spring bind EM to thread': tie mechanism to production SQL, transaction scope, and one metric you watch. The persistence context is where managed entities live between load and flush/commit. Order placement TX: load `Order`, add lines, flush at commit — one PC, one connection from Hikari for TX duration. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Difference `merge` identity in PC?
**A:** 'Difference `merge` identity in PC' — know entity state and who owns the transaction boundary. `EntityManager` delegates to Hibernate `Session` internally. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving session vs entitymanager vs persistence context. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. JPA's `EntityManager` is the standard API; Hibernate's `Session` extends it. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Order placement TX: load `Order`, add lines, flush at commit — one PC, one connection from Hikari for TX duration.

---

### 2. Entity states: transient, persistent, detached, removed.

**Short answer:** Transient entities are new with no persistent identity. Persistent entities are managed in the PC. Detached entities have identity but aren't managed. Removed entities are scheduled for deletion at flush.

#### What it is
JPA entity lifecycle states governing what operations are legal and how changes propagate to SQL. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`persist()` makes transient → persistent. `remove()` on managed → removed. Commit/close/detach → detached. `merge()` copies detached state into a managed instance — **always use the return value**. Accessing lazy associations on detached entities causes `LazyInitializationException`.

#### When to use / when NOT to use
Keep work inside one TX with small aggregates. Don't pass entities to the web layer — map to DTOs before detach. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
REST client sends `OrderDto`; service loads managed `Order`, applies changes, commits — never merge client-provided detached graph blindly. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Treating returned `merge()` reference as optional; `remove()` on detached without merge first; serializing entities to JSON then merging entire graph.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** State diagram with operations?
**A:** 'State diagram with operations' — know entity state and who owns the transaction boundary. `persist()` makes transient → persistent. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `EntityNotFoundException` on getReference?
**A:** Senior answer to '`EntityNotFoundException` on getReference': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA entity lifecycle states governing what operations are legal and how changes propagate to SQL. REST client sends `OrderDto`; service loads managed `Order`, applies changes, commits — never merge client-provided detached graph blindly. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Spring Data `save()` state detection?
**A:** 'Spring Data `save()` state detection' — know entity state and who owns the transaction boundary. `persist()` makes transient → persistent. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving entity states: transient, persistent, detached, removed. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Transient entities are new with no persistent identity. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. REST client sends `OrderDto`; service loads managed `Order`, applies changes, commits — never merge client-provided detached graph blindly.

---

### 3. How does dirty checking work?

**Short answer:** Hibernate tracks entity changes by comparing current field values to a snapshot taken at load (or via bytecode enhancement). At flush, dirty fields generate UPDATE statements — entities you didn't call `save()` on still update. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Automatic change detection eliminating manual UPDATE calls for managed entities. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Default: snapshot per entity at load — memory cost. Bytecode enhancement tracks dirty flags on field access — lower memory, build-time plugin. `@DynamicUpdate` generates SQL updating only changed columns but still requires dirty detection. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Rely on dirty checking in normal OLTP flows. Use bulk JPQL updates when you intentionally bypass PC. Enable enhancement on large domain models if profiling shows snapshot pressure. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=? WHERE id=?` without explicit save. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- Thinking `save()` is required for updates; modifying detached entity expecting auto-update; `@DynamicUpdate` misunderstood as skipping dirty check.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Enhancement vs snapshot trade-offs?
**A:** Senior answer to 'Enhancement vs snapshot trade-offs': tie mechanism to production SQL, transaction scope, and one metric you watch. Automatic change detection eliminating manual UPDATE calls for managed entities. Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=? Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Interaction with immutables?
**A:** Senior answer to 'Interaction with immutables': tie mechanism to production SQL, transaction scope, and one metric you watch. Automatic change detection eliminating manual UPDATE calls for managed entities. Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=? Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Dirty checking cost at scale?
**A:** Senior answer to 'Dirty checking cost at scale': tie mechanism to production SQL, transaction scope, and one metric you watch. Automatic change detection eliminating manual UPDATE calls for managed entities. Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=? Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving how does dirty checking work? shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Hibernate tracks entity changes by comparing current field values to a snapshot taken at load (or via bytecode enhancement). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=?

---

### 4. Flush modes.

**Short answer:** Flush synchronizes persistence context to the database. `AUTO` (default) flushes before queries that might see stale data and at commit. `COMMIT` delays until commit — can read stale self-data. Unexpected flush mid-TX can cause deadlocks.

#### What it is
`FlushModeType` controlling when pending SQL is sent to the database within a transaction. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`AUTO`: before JPQL/Criteria that could conflict; at commit. `COMMIT`: only at commit — performance micro-optimization with consistency risk. `MANUAL`: explicit `flush()`. Hibernate `ALWAYS` flushes before every query — rarely used.

#### When to use / when NOT to use
Stay on AUTO unless measured need. COMMIT only with clear understanding of stale reads in same TX. Manual flush before native query needing visible writes. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Bulk insert loop with periodic `flush()` + `clear()` every 500 rows to avoid PC memory blow-up — still AUTO mode with explicit batch flush. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Assuming `find()` never triggers flush (AUTO may flush first); flush before lock query causing write ordering deadlock.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `FlushModeType` per query hint?
**A:** '`FlushModeType` per query hint' — know entity state and who owns the transaction boundary. `AUTO`: before JPQL/Criteria that could conflict; at commit. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Relationship flush order FK constraints?
**A:** 'Relationship flush order FK constraints' — know entity state and who owns the transaction boundary. `AUTO`: before JPQL/Criteria that could conflict; at commit. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `saveAndFlush` vs commit?
**A:** '`saveAndFlush` vs commit' — know entity state and who owns the transaction boundary. `AUTO`: before JPQL/Criteria that could conflict; at commit. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving flush modes. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Flush synchronizes persistence context to the database. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Bulk insert loop with periodic `flush()` + `clear()` every 500 rows to avoid PC memory blow-up — still AUTO mode with explicit batch flush.

---

### 5. `persist` vs `merge` vs `save` (Hibernate) vs `save` (Spring Data).

**Short answer:** `persist` attaches new entities. `merge` reattaches detached state into a managed copy — use the returned instance. Spring Data `save()` chooses persist or merge heuristically — can cause extra SELECTs and broken collection merging. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Different API entry points for making entity state persistent, with subtly different semantics. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`persist`: illegal on detached (exception). `merge`: detached → managed copy; collections may replace by reference. Hibernate legacy `save`: may assign id before insert depending on generator. Spring Data `save`: `isNew()` detection via `Persistable`, `@Version`, or id null checks.

#### When to use / when NOT to use
Explicit `persist`/`merge` in domain services when graphs are complex. Spring Data `save` fine for simple aggregates. Never merge DTO-detached graphs with orphan collection surprises. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Create order: `em.persist(order)` with cascade on lines. Update from API: load managed entity, mutate fields — avoid merge entirely. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- Ignoring `merge` return value; `save()` on entity with null id but existing natural key; cascade merge pulling entire object graph.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Implement `Persistable` for assigned ids?
**A:** 'Implement `Persistable` for assigned ids' — know entity state and who owns the transaction boundary. `persist`: illegal on detached (exception). merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `merge` and orphanRemoval interaction?
**A:** '`merge` and orphanRemoval interaction' — know entity state and who owns the transaction boundary. `persist`: illegal on detached (exception). merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `persist` on entity with generated id already set?
**A:** '`persist` on entity with generated id already set' — know entity state and who owns the transaction boundary. `persist`: illegal on detached (exception). merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `persist` vs `merge` vs `save` (hibernate) vs `save` (spring data). shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `persist` attaches new entities. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Create order: `em.persist(order)` with cascade on lines.

---

### 6. ID generation: IDENTITY vs SEQUENCE vs UUID.

**Short answer:** `IDENTITY` triggers insert-before-id-known — breaks JDBC batching. `SEQUENCE` with enhanced optimizers enables batch inserts. UUID avoids coordination but hurts B-tree locality unless time-ordered (UUIDv7). The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Primary key generation strategy affecting insert performance, portability, and indexing. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`GenerationType.IDENTITY`: DB autoincrement — Hibernate can't batch inserts easily. `SEQUENCE`: `pooled`/`pooled-lo` optimizers reduce sequence roundtrips. UUID: `@UuidGenerator` or application-assigned; random UUIDs fragment indexes. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
SEQUENCE (or Postgres serial alternatives) for OLTP bulk inserts. UUID for distributed id generation without DB roundtrip — prefer UUIDv7 for index locality. IDENTITY acceptable at low volume. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`. Public API exposes UUIDv7 as external id. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- IDENTITY with batch settings wondering why no batching; sharing sequence across high-insert tables causing contention.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `TABLE` generator why avoid?
**A:** Senior answer to '`TABLE` generator why avoid': tie mechanism to production SQL, transaction scope, and one metric you watch. Primary key generation strategy affecting insert performance, portability, and indexing. Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hi/lo algorithm legacy?
**A:** Senior answer to 'Hi/lo algorithm legacy': tie mechanism to production SQL, transaction scope, and one metric you watch. Primary key generation strategy affecting insert performance, portability, and indexing. Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Composite keys `@EmbeddedId`?
**A:** Senior answer to 'Composite keys `@EmbeddedId`': tie mechanism to production SQL, transaction scope, and one metric you watch. Primary key generation strategy affecting insert performance, portability, and indexing. Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving id generation: identity vs sequence vs uuid. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `IDENTITY` triggers insert-before-id-known — breaks JDBC batching. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`.

#### Code / config (when useful)

```yaml
spring.jpa.properties.hibernate.jdbc.batch_size: 50
spring.jpa.properties.hibernate.order_inserts: true
```

---

### 7. Equals/hashCode for entities.

**Short answer:** Don't use database id in equals/hashCode before persist — id may be null or 0. Use stable business key, or identity (`==`) only within persistence context. Lombok `@Data` on entities breaks lazy loading and sets. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Correct equality semantics for JPA entities in collections and ORM identity map consistency. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Hibernate uses identity map — same id same instance in PC. `HashSet` of entities uses hashCode — changing id after persist breaks set contract. Business key (email, SKU) safe if immutable and unique. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Business key equals for entities with natural keys. Id-based equals only in DTOs. Never include lazy collections in `toString`/`equals`. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
`Product` equals by `sku` field; id assigned after insert doesn't change equals contract. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Lombok `@EqualsAndHashCode(of = "id")` on new entities in sets; calling `hashCode()` triggering lazy load.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Hibernate `==` vs `equals` in PC?
**A:** Senior answer to 'Hibernate `==` vs `equals` in PC': tie mechanism to production SQL, transaction scope, and one metric you watch. Correct equality semantics for JPA entities in collections and ORM identity map consistency. `Product` equals by `sku` field; id assigned after insert doesn't change equals contract. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Equals for `@Embeddable` value types?
**A:** Senior answer to 'Equals for `@Embeddable` value types': tie mechanism to production SQL, transaction scope, and one metric you watch. Correct equality semantics for JPA entities in collections and ORM identity map consistency. `Product` equals by `sku` field; id assigned after insert doesn't change equals contract. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Set of detached entities?
**A:** 'Set of detached entities' — know entity state and who owns the transaction boundary. Hibernate uses identity map — same id same instance in PC. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving equals/hashcode for entities. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Don't use database id in equals/hashCode before persist — id may be null or 0. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. `Product` equals by `sku` field; id assigned after insert doesn't change equals contract.

---

### 8. Associations: `mappedBy`, owning side.

**Short answer:** The owning side owns the foreign key or join table and is what Hibernate writes. `mappedBy` marks the inverse side. Bidirectional associations need sync helpers — updating only inverse side doesn't change FK. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
JPA relationship mapping determining which entity's mapping controls database schema updates. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@OneToMany(mappedBy="order")` — `OrderLine.order` owns FK. `@JoinColumn` on `@ManyToOne` side typically owns. Hibernate flush order respects FK dependencies. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Prefer unidirectional `@ManyToOne` when you don't need parent→children navigation in domain. Bidirectional with `addLine()`/`removeLine()` helpers maintaining both sides. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
```java public void addLine(OrderLine line) { lines.add(line); line.setOrder(this); } ``` Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Setting only `order.getLines().add(line)` without `line.setOrder(this)` — FK null in DB.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@JoinColumn` on both sides?
**A:** On '`@JoinColumn` on both sides': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `@OneToMany(mappedBy="order")` — `OrderLine.order` owns FK. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Unidirectional `@OneToMany` with join table?
**A:** On 'Unidirectional `@OneToMany` with join table': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `@OneToMany(mappedBy="order")` — `OrderLine.order` owns FK. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Cascade direction best practice?
**A:** Senior answer to 'Cascade direction best practice': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA relationship mapping determining which entity's mapping controls database schema updates. ```java public void addLine(OrderLine line) { lines.add(line); line.setOrder(this); } ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving associations: `mappedby`, owning side. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. The owning side owns the foreign key or join table and is what Hibernate writes. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. ```java public void addLine(OrderLine line) { lines.add(line); line.setOrder(this); } ```

---

### 9. `CascadeType` vs orphanRemoval.

**Short answer:** Cascade propagates persist/merge/remove operations along associations. `orphanRemoval=true` deletes child rows when removed from parent's collection. `CascadeType.ALL` on large graphs can delete more than intended. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Rules for lifecycle operations propagating across entity relationships. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`CascadeType.PERSIST/MERGE/REMOVE/REFRESH/DETACH`. `orphanRemoval`: child no longer referenced by parent → DELETE. Distinct from `REMOVE` cascade on parent delete. Don't cascade from child to parent.

#### When to use / when NOT to use
Cascade PERSIST on composition (`Order` → `OrderLine`). orphanRemoval for true composition. Avoid ALL on `@ManyToMany`. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Remove line from order collection with orphanRemoval — line row deleted at flush. Parent order delete cascades remove lines. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- orphanRemoval with DTO merge replacing collection — accidental mass delete; cascade MERGE on `@ManyToOne` parent.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** orphanRemoval vs `@OnDelete`?
**A:** Senior answer to 'orphanRemoval vs `@OnDelete`': tie mechanism to production SQL, transaction scope, and one metric you watch. Rules for lifecycle operations propagating across entity relationships. Remove line from order collection with orphanRemoval — line row deleted at flush. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Cascade and `@OneToOne` optional?
**A:** Senior answer to 'Cascade and `@OneToOne` optional': tie mechanism to production SQL, transaction scope, and one metric you watch. Rules for lifecycle operations propagating across entity relationships. Remove line from order collection with orphanRemoval — line row deleted at flush. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Soft delete vs orphanRemoval?
**A:** Senior answer to 'Soft delete vs orphanRemoval': tie mechanism to production SQL, transaction scope, and one metric you watch. Rules for lifecycle operations propagating across entity relationships. Remove line from order collection with orphanRemoval — line row deleted at flush. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `cascadetype` vs orphanremoval. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Cascade propagates persist/merge/remove operations along associations. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Remove line from order collection with orphanRemoval — line row deleted at flush.

---

### 10. FetchType EAGER vs LAZY.

**Short answer:** EAGER loads associations immediately — global fetch plan you can't tune per use case. Default lazy for collections; `@ManyToOne` EAGER was common historically — still causes N+1. Explicit fetch per query wins. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
JPA fetch strategy controlling when associated data is loaded from database. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
LAZY: proxy or bytecode-enhanced lazy field until access. EAGER: join or secondary select at load time. Hibernate ignores global EAGER change without bytecode enhancement for field access in some cases. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Default LAZY on collections always. Fetch join, entity graph, or batch size per use case. Never EAGER as blanket N+1 "fix." Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
`@ManyToOne(fetch=LAZY)` on `Order.customer`; checkout flow uses `@EntityGraph` loading customer name only via projection. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- EAGER on `@OneToMany` causing cartesian products; JSON serialization triggering lazy loads.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Hibernate `@LazyToOne`?
**A:** On 'Hibernate `@LazyToOne`': measure SQL count per endpoint first using APM or Hibernate statistics in staging. LAZY: proxy or bytecode-enhanced lazy field until access. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Fetch profile?
**A:** On 'Fetch profile': measure SQL count per endpoint first using APM or Hibernate statistics in staging. LAZY: proxy or bytecode-enhanced lazy field until access. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** EAGER + `@BatchSize` interaction?
**A:** On 'EAGER + `@BatchSize` interaction': measure SQL count per endpoint first using APM or Hibernate statistics in staging. LAZY: proxy or bytecode-enhanced lazy field until access. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving fetchtype eager vs lazy. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. EAGER loads associations immediately — global fetch plan you can't tune per use case. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. `@ManyToOne(fetch=LAZY)` on `Order.customer`; checkout flow uses `@EntityGraph` loading customer name only via projection.

---

### 11. N+1: how you see it and how you kill it.

**Short answer:** One query for parents plus N queries for each child id — visible in SQL logs and Hibernate statistics. Fix with join fetch (watch cartesian product), `@EntityGraph`, `@BatchSize`, subselect fetch, or DTO projections — not global EAGER. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Performance anti-pattern where lazy associations trigger one SELECT per row in a loop or serialization. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Detect: `hibernate.generate_statistics=true`, datasource-proxy, p6spy. Fixes ranked: projection query best for read APIs; `@EntityGraph` for entity returns; `JOIN FETCH` for controlled graphs; `@BatchSize(size=20)` batches lazy loads into fewer IN queries. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Measure first. Join fetch two bags — failure (multiple bag fetch exception). Two queries often beat one giant join. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
List 100 orders: query 1 paginated ids; query 2 `WHERE order_id IN (...)` fetch lines — 2 queries total. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Enabling EAGER globally; join fetch + Pageable broken pagination; ignoring N+1 in reporting jobs.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@Fetch(SUBSELECT)` vs BATCH?
**A:** On '`@Fetch(SUBSELECT)` vs BATCH': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Detect: `hibernate.generate_statistics=true`, datasource-proxy, p6spy. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Blaze-Persistence entity views?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. One query for parents plus N queries for each child id — visible in SQL logs and Hibernate statistics. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** N+1 in GraphQL resolvers?
**A:** On 'N+1 in GraphQL resolvers': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Detect: `hibernate.generate_statistics=true`, datasource-proxy, p6spy. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving n+1: how you see it and how you kill it. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. One query for parents plus N queries for each child id — visible in SQL logs and Hibernate statistics. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. List 100 orders: query 1 paginated ids; query 2 `WHERE order_id IN (...)` fetch lines — 2 queries total.

---

### 12. Multiple bags fetch exception.

**Short answer:** Hibernate cannot simultaneously JOIN FETCH two `List` collections without Cartesian product explosion — throws `MultipleBagFetchException` or causes memory blow-up. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Limitation of bag (`List`) semantics with multiple join fetch in one query. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Two bags multiply rows (10 lines × 10 payments = 100 rows per order). Hibernate 5+ refuses multiple bag fetch. `Set` avoids duplicate row issue but still cartesian risk. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Use `Set` for uniqueness, or fetch collections in separate queries, or `@BatchSize`. `@OrderColumn` lists are not bags but have other costs. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Adding `distinct` thinking it fixes cartesian hydration cost; Hibernate 6 behavior differences untested.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** List vs Set domain modeling?
**A:** Senior answer to 'List vs Set domain modeling': tie mechanism to production SQL, transaction scope, and one metric you watch. Limitation of bag (`List`) semantics with multiple join fetch in one query. Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@SqlRestriction` on collections?
**A:** Senior answer to '`@SqlRestriction` on collections': tie mechanism to production SQL, transaction scope, and one metric you watch. Limitation of bag (`List`) semantics with multiple join fetch in one query. Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Multiple `@OneToMany` redesign?
**A:** Senior answer to 'Multiple `@OneToMany` redesign': tie mechanism to production SQL, transaction scope, and one metric you watch. Limitation of bag (`List`) semantics with multiple join fetch in one query. Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving multiple bags fetch exception. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Hibernate cannot simultaneously JOIN FETCH two `List` collections without Cartesian product explosion — throws `MultipleBagFetchException` or causes memory blow-up. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids.

---

### 13. Cartesian product with join fetch.

**Short answer:** Join fetching multiple collections multiplies result set rows — Hibernate hydrates duplicate parent entities (deduped in memory) but DB and network work still scales with product of child counts. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Relational join explosion when fetching multiple to-many associations in one SQL statement. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
SQL returns M×N rows; Hibernate builds object graph with deduplication by id. Pagination (`setFirstResult`) with join fetch applies limit in memory in some cases — **broken pagination**. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Paginate ids first, then fetch graph by id list. Prefer DTO queries for read models over entity join fetch at scale. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- `JOIN FETCH` on list endpoint with Pageable returning wrong counts; assuming `distinct` in JPQL fixes DB work.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Hibernate 6 DISTINCT semantics?
**A:** Senior answer to 'Hibernate 6 DISTINCT semantics': tie mechanism to production SQL, transaction scope, and one metric you watch. Relational join explosion when fetching multiple to-many associations in one SQL statement. Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Window functions for pagination?
**A:** Senior answer to 'Window functions for pagination': tie mechanism to production SQL, transaction scope, and one metric you watch. Relational join explosion when fetching multiple to-many associations in one SQL statement. Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Read model denormalization?
**A:** Senior answer to 'Read model denormalization': tie mechanism to production SQL, transaction scope, and one metric you watch. Relational join explosion when fetching multiple to-many associations in one SQL statement. Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving cartesian product with join fetch. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Join fetching multiple collections multiplies result set rows — Hibernate hydrates duplicate parent entities (deduped in memory) but DB and network work still scales with product of child counts. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only.

---

### 14. `@OneToMany` default is lazy bag. Why `List` vs `Set` vs `@OrderColumn`?

**Short answer:** Bag (`List` without order column) allows duplicates, no index column. `List` + `@OrderColumn` maintains order with extra writable column. `Set` requires consistent equals/hashCode — no duplicate children. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Collection type choice affecting SQL shape, semantics, and Hibernate fetch behavior. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Bag: simple one-to-many FK on child table. `@OrderColumn`: position column updated on reorder — insert overhead. `Set`: typically no duplicates; may use join table or FK depending on mapping. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Ordered lines: `List` with `@OrderBy("lineNumber")` often sufficient vs `@OrderColumn`. Set when uniqueness matters (tags). Avoid many-to-many bags. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- `@OrderColumn` on large collections causing update storms on insert; HashSet with mutable entity equals bugs.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@SortNatural`?
**A:** Senior answer to '`@SortNatural`': tie mechanism to production SQL, transaction scope, and one metric you watch. Collection type choice affecting SQL shape, semantics, and Hibernate fetch behavior. Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Immutable collections mapping?
**A:** Senior answer to 'Immutable collections mapping': tie mechanism to production SQL, transaction scope, and one metric you watch. Collection type choice affecting SQL shape, semantics, and Hibernate fetch behavior. Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Collection replacement vs diff?
**A:** Senior answer to 'Collection replacement vs diff': tie mechanism to production SQL, transaction scope, and one metric you watch. Collection type choice affecting SQL shape, semantics, and Hibernate fetch behavior. Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `@onetomany` default is lazy bag. why `list` vs `set` vs `@ordercolumn`? shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Bag (`List` without order column) allows duplicates, no index column. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility.

---

### 15. `@ManyToMany` — why seniors avoid it.

**Short answer:** Pure many-to-many join table can't store relationship attributes (`assigned_at`, `role_expiry`). Cascades and fetch plans become footguns. Model an explicit join entity instead. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
JPA shortcut mapping for many-to-many via join table without entity representing the association. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Hidden join table; both sides can map with `mappedBy`. Adding columns requires migration to entity anyway. Cascade ALL can delete unexpected join rows. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Avoid in domain models. Use `UserRole`, `ProductCategory` entities with payload columns and explicit lifecycle. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Users and roles: `UserRole` entity with `userId`, `roleId`, `grantedAt`, `grantedBy` — queryable and auditable. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- ManyToMany cascade REMOVE wiping join data; unindexed join table full scan on authorization check.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Unidirectional ManyToMany?
**A:** Senior answer to 'Unidirectional ManyToMany': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA shortcut mapping for many-to-many via join table without entity representing the association. Users and roles: `UserRole` entity with `userId`, `roleId`, `grantedAt`, `grantedBy` — queryable and auditable. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Replace with composite key entity?
**A:** Senior answer to 'Replace with composite key entity': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA shortcut mapping for many-to-many via join table without entity representing the association. Users and roles: `UserRole` entity with `userId`, `roleId`, `grantedAt`, `grantedBy` — queryable and auditable. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** GraphQL many-to-many exposure?
**A:** On 'GraphQL many-to-many exposure': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Hidden join table; both sides can map with `mappedBy`. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `@manytomany` shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Pure many-to-many join table can't store relationship attributes (`assigned_at`, `role_expiry`). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Users and roles: `UserRole` entity with `userId`, `roleId`, `grantedAt`, `grantedBy` — queryable and auditable.

---

### 16. Inheritance: SINGLE_TABLE vs JOINED vs TABLE_PER_CLASS.

**Short answer:** SINGLE_TABLE: one table, discriminator, nullable subtype columns — fast reads, wide sparse table. JOINED: normalized, joins per query. TABLE_PER_CLASS: union queries, poor polymorphic performance. Prefer composition over deep entity inheritance.

#### What it is
JPA strategies mapping class hierarchies to relational schema. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`SINGLE_TABLE`: `@DiscriminatorColumn`. JOINED: base + subclass tables. TABLE_PER_CLASS: each concrete class full table — polymorphic query unions all tables. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
SINGLE_TABLE for shallow hierarchy, few subtype fields. JOINED when normalization matters. Avoid TABLE_PER_CLASS. Often `@Embeddable` or `@MappedSuperclass` beats inheritance.

#### Production example
Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Deep inheritance trees; discriminator string typos; querying root entity scanning huge single table.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@MappedSuperclass` vs entity inheritance?
**A:** Senior answer to '`@MappedSuperclass` vs entity inheritance': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA strategies mapping class hierarchies to relational schema. Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Polymorphic `@Query` pitfalls?
**A:** Senior answer to 'Polymorphic `@Query` pitfalls': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA strategies mapping class hierarchies to relational schema. Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate `@DiscriminatorFormula`?
**A:** Senior answer to 'Hibernate `@DiscriminatorFormula`': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA strategies mapping class hierarchies to relational schema. Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving inheritance: single_table vs joined vs table_per_class. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. SINGLE_TABLE: one table, discriminator, nullable subtype columns — fast reads, wide sparse table. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries.

---

### 17. `@Embeddable` vs entity.

**Short answer:** Embeddables are value objects without identity — owned by parent entity, mapped to same table (typically). Good for Money, Address. No shared mutable embeddable instances across entities. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
JPA composition mapping for types without standalone lifecycle. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Columns flattened into parent table (default) or `@AssociationOverride`. Equals by value. `@Embedded` on entity field. Cannot be queried as root entity (JPQL limitation without path).

#### When to use / when NOT to use
Money (`amount`, `currency`), Address, DateRange. Not for types needing independent repository. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
```java @Embeddable public record Money(BigDecimal amount, Currency currency) {} @Embedded private Money total; ``` Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Mutating shared Address instance attached to two customers; null embeddable vs empty embeddable confusion.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@AttributeOverride` column names?
**A:** Senior answer to '`@AttributeOverride` column names': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA composition mapping for types without standalone lifecycle. ```java @Embeddable public record Money(BigDecimal amount, Currency currency) {} @Embedded private Money total; ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Embeddable collections?
**A:** Senior answer to 'Embeddable collections': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA composition mapping for types without standalone lifecycle. ```java @Embeddable public record Money(BigDecimal amount, Currency currency) {} @Embedded private Money total; ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** JSON embeddable mapping?
**A:** Senior answer to 'JSON embeddable mapping': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA composition mapping for types without standalone lifecycle. ```java @Embeddable public record Money(BigDecimal amount, Currency currency) {} @Embedded private Money total; ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `@embeddable` vs entity. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Embeddables are value objects without identity — owned by parent entity, mapped to same table (typically). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. ```java @Embeddable public record Money(BigDecimal amount, Currency currency) {} @Embedded private Money total; ```

---

### 18. Second-level cache.

**Short answer:** Shared cache across persistence contexts/sessions — Ehcache, Infinispan, Redis (custom). Cache entities and collections with strict concurrency strategy. Best for read-mostly reference data; dangerous for frequently updated financial data without discipline. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Optional Hibernate cache region above the first-level PC, reducing DB reads for shared data. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@Cache(usage = READ_WRITE)` entity regions; collection cache stores element ids. Invalidation on update. Cluster: invalidation vs replication latency. Requires `@EnableCaching` + JCache provider configuration.

#### When to use / when NOT to use
Countries, product categories, config tables. Not default for transactional hot entities. TTL + event invalidation for semi-static data. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Caching entities with lazy unloaded collections; stale prices in cluster without invalidation; READ_ONLY on mutable data.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Query cache vs entity cache?
**A:** Senior answer to 'Query cache vs entity cache': tie mechanism to production SQL, transaction scope, and one metric you watch. Optional Hibernate cache region above the first-level PC, reducing DB reads for shared data. Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@NaturalId` cache?
**A:** Senior answer to '`@NaturalId` cache': tie mechanism to production SQL, transaction scope, and one metric you watch. Optional Hibernate cache region above the first-level PC, reducing DB reads for shared data. Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Redis as L2 provider trade-offs?
**A:** Senior answer to 'Redis as L2 provider trade-offs': tie mechanism to production SQL, transaction scope, and one metric you watch. Optional Hibernate cache region above the first-level PC, reducing DB reads for shared data. Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving second-level cache. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Shared cache across persistence contexts/sessions — Ehcache, Infinispan, Redis (custom). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership.

---

### 19. Query cache.

**Short answer:** Caches query result **identifiers**, not full entities — still hits entity cache/DB for hydration. Easy to make slower than no cache. Rarely enabled globally for good reason. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Hibernate cache storing mapping from query key + params to list of entity ids at a timestamp. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Invalidated when any table in query space updates (timestamp regions). Requires `@Cacheable` on query + global enable. Stale if invalidation misconfigured. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Extremely stable repeated queries on reference data. Prefer explicit application cache with clear TTL for most cases. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Enabling query cache without entity cache; expecting cache to skip DB entirely.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@QueryHints` CACHEABLE?
**A:** Senior answer to '`@QueryHints` CACHEABLE': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate cache storing mapping from query key + params to list of entity ids at a timestamp. Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate 6 query cache changes?
**A:** Senior answer to 'Hibernate 6 query cache changes': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate cache storing mapping from query key + params to list of entity ids at a timestamp. Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** vs Spring `@Cacheable` on repository?
**A:** Senior answer to 'vs Spring `@Cacheable` on repository': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate cache storing mapping from query key + params to list of entity ids at a timestamp. Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving query cache. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Caches query result **identifiers**, not full entities — still hits entity cache/DB for hydration. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog.

---

### 20. Optimistic locking `@Version`.

**Short answer:** Version column in UPDATE WHERE clause — zero rows updated means concurrent modification → `OptimisticLockException`. Prevents silent lost updates. Expose version to clients via ETag/If-Match. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Lock-free concurrency control detecting conflicting writes at commit time. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@Version` Long/Timestamp incremented on each successful update. JPA spec requires version check on merge/update. Retry or user conflict resolution on failure. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Default for most OLTP entities with concurrent edits. Not for high-contention inventory without retry strategy — may need pessimistic or domain reservation. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
PUT `/orders/{id}` requires `If-Match: "3"` matching `@Version`; 412 on conflict with current state payload. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- No version on hot entities; client never sends version — last write wins despite `@Version` if merge bypasses; bulk update skipping version increment.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@OptimisticLocking` type TIMESTAMP?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Version column in UPDATE WHERE clause — zero rows updated means concurrent modification → `OptimisticLockException`. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Retry with exponential backoff?
**A:** Senior answer to 'Retry with exponential backoff': tie mechanism to production SQL, transaction scope, and one metric you watch. Lock-free concurrency control detecting conflicting writes at commit time. PUT `/orders/{id}` requires `If-Match: "3"` matching `@Version`; 412 on conflict with current state payload. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Version on `@Embeddable`?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Version column in UPDATE WHERE clause — zero rows updated means concurrent modification → `OptimisticLockException`. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving optimistic locking `@version`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Version column in UPDATE WHERE clause — zero rows updated means concurrent modification → `OptimisticLockException`. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. PUT `/orders/{id}` requires `If-Match: "3"` matching `@Version`; 412 on conflict with current state payload.

---

### 21. Pessimistic locking.

**Short answer:** `LockModeType.PESSIMISTIC_WRITE` maps to `SELECT FOR UPDATE` — holds row lock until TX ends. Use for scarce resources (inventory, seats), not every read. Configure lock timeout; expect deadlocks. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Database-level row locking via JPA lock modes on find/query. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`PESSIMISTIC_READ/WRITE`, `UPGRADE`, `PESSIMISTIC_FORCE_INCREMENT`. Timeout via `javax.persistence.lock.timeout` hint. DB-specific: NOWAIT, SKIP LOCKED for worker queues. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Short TX reserving inventory row. SKIP LOCKED for job claiming. Not for report queries — blocks writers. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
```java @Lock(LockModeType.PESSIMISTIC_WRITE) @Query("select i from Inventory i where i.sku = :sku") Optional<Inventory> lockBySku(String sku); ``` Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Long TX holding pessimistic lock; lock without index — table lock escalation; default infinite wait.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Pessimistic vs optimistic choice matrix?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. `LockModeType.PESSIMISTIC_WRITE` maps to `SELECT FOR UPDATE` — holds row lock until TX ends. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Oracle vs Postgres lock behavior?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. `LockModeType.PESSIMISTIC_WRITE` maps to `SELECT FOR UPDATE` — holds row lock until TX ends. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@NamedEntityGraph` with lock?
**A:** On '`@NamedEntityGraph` with lock': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `PESSIMISTIC_READ/WRITE`, `UPGRADE`, `PESSIMISTIC_FORCE_INCREMENT`. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving pessimistic locking. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `LockModeType.PESSIMISTIC_WRITE` maps to `SELECT FOR UPDATE` — holds row lock until TX ends. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. ```java @Lock(LockModeType.PESSIMISTIC_WRITE) @Query("select i from Inventory i where i.sku = :sku") Optional<Inventory> lockBySku(String sku); ```

---

### 22. `@Lock` vs DB isolation.

**Short answer:** Transaction isolation controls what rows/versions you **see**; explicit locks control who can **modify** rows. Repeatable read doesn't replace `FOR UPDATE` for inventory reservation. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Distinction between MVCC snapshot isolation and explicit row-level write locks. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Isolation prevents dirty reads; phantom behavior DB-dependent. `@Lock` issues SQL lock clauses independent of isolation level semantics. Serializable reduces anomalies but increases aborts. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Combine READ COMMITTED + `@Version` for many apps. Pessimistic lock when business requires exclusive access to row during decision. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Transfer between accounts: pessimistic lock both rows in consistent id order to prevent deadlock. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Assuming `@Transactional` isolation SERIALIZABLE fixes all race conditions; ignoring phantom inserts in inventory counts.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Snapshot isolation vs serializable?
**A:** Senior answer to 'Snapshot isolation vs serializable': tie mechanism to production SQL, transaction scope, and one metric you watch. Distinction between MVCC snapshot isolation and explicit row-level write locks. Transfer between accounts: pessimistic lock both rows in consistent id order to prevent deadlock. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Lock ordering deadlock prevention?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Transaction isolation controls what rows/versions you **see**; explicit locks control who can **modify** rows. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@Formula` fields and locking?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Transaction isolation controls what rows/versions you **see**; explicit locks control who can **modify** rows. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `@lock` vs db isolation. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Transaction isolation controls what rows/versions you **see**; explicit locks control who can **modify** rows. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Transfer between accounts: pessimistic lock both rows in consistent id order to prevent deadlock.

---

### 23. Native queries and entities.

**Short answer:** Native SQL returning entities must include all mapped columns or use `@SqlResultSetMapping`. Schema-coupled and brittle — prefer JPQL/Criteria unless you need DB-specific features. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Executing raw SQL through JPA/Hibernate with optional entity mapping. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`createNativeQuery(sql, Entity.class)` requires column aliases matching mappings. `@SqlResultSetMapping` + `@EntityResult` for complex shapes. Hibernate 6 improved ad-hoc mapping. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Window functions, CTEs, vendor hints, bulk reporting. DTO native for read-only reports. Not for portable CRUD. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Postgres `UPDATE ... RETURNING` native query mapping to DTO interface for upsert response. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- Partial column list silent wrong data; native query bypasses `@Where` soft delete filter.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@NamedNativeQuery` maintenance?
**A:** Senior answer to '`@NamedNativeQuery` maintenance': tie mechanism to production SQL, transaction scope, and one metric you watch. Executing raw SQL through JPA/Hibernate with optional entity mapping. Postgres `UPDATE ... Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** ResultSet mapping to constructor?
**A:** Senior answer to 'ResultSet mapping to constructor': tie mechanism to production SQL, transaction scope, and one metric you watch. Executing raw SQL through JPA/Hibernate with optional entity mapping. Postgres `UPDATE ... Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Schema migration breaking natives?
**A:** Senior answer to 'Schema migration breaking natives': tie mechanism to production SQL, transaction scope, and one metric you watch. Executing raw SQL through JPA/Hibernate with optional entity mapping. Postgres `UPDATE ... Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving native queries and entities. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Native SQL returning entities must include all mapped columns or use `@SqlResultSetMapping`. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Postgres `UPDATE ...

---

### 24. JPQL vs Criteria vs Querydsl vs Spec.

**Short answer:** JPQL strings — simple, runtime errors. Criteria API — verbose type-safe. Querydsl/JOOQ — better complex dynamic SQL. Spring Data Specifications — composable predicates for repositories.

#### What it is
Query authoring options from strings to type-safe builders. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Criteria `CriteriaBuilder` predicates compile to JPQL. Specifications `toPredicate(Root, Query, CB)`. Never concatenate user input into JPQL — SQL injection via JPQL parameters still required. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
JPQL `@Query` for stable queries. Specifications for optional admin filters. Blaze-Persistence for advanced DTO queries on Hibernate. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Dynamic JPQL string concat from request params; Criteria unreadable mega-methods.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Hibernate 6 Criteria changes?
**A:** Senior answer to 'Hibernate 6 Criteria changes': tie mechanism to production SQL, transaction scope, and one metric you watch. Query authoring options from strings to type-safe builders. Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Type-safe query generators?
**A:** Senior answer to 'Type-safe query generators': tie mechanism to production SQL, transaction scope, and one metric you watch. Query authoring options from strings to type-safe builders. Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Specification AND/OR composition?
**A:** Senior answer to 'Specification AND/OR composition': tie mechanism to production SQL, transaction scope, and one metric you watch. Query authoring options from strings to type-safe builders. Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving jpql vs criteria vs querydsl vs spec. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. JPQL strings — simple, runtime errors. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`.

---

### 25. Pagination: `Pageable` count query cost.

**Short answer:** `Page` runs data query plus `count(*)` — count often more expensive than page data on large tables. Use `Slice` when total unnecessary; keyset pagination for deep pages. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Spring Data pagination abstractions over JPA `setFirstResult/setMaxResults`. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`SimpleJpaRepository` derives count query from method — can be slow without matching indexes. Offset pagination degrades on large offsets (`OFFSET 1000000`). Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
`Slice` for infinite scroll. Keyset (`WHERE id > :cursor ORDER BY id LIMIT 20`) for large datasets. Covering indexes on sort columns. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Count query on every scroll page; join fetch + Pageable returning wrong page size; missing index on ORDER BY column.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@Query countQuery separate optimization?
**A:** Senior answer to '`@Query countQuery separate optimization': tie mechanism to production SQL, transaction scope, and one metric you watch. Spring Data pagination abstractions over JPA `setFirstResult/setMaxResults`. Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate `@PageableDefault`?
**A:** Senior answer to 'Hibernate `@PageableDefault`': tie mechanism to production SQL, transaction scope, and one metric you watch. Spring Data pagination abstractions over JPA `setFirstResult/setMaxResults`. Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Blaze-Pagination?
**A:** Senior answer to 'Blaze-Pagination': tie mechanism to production SQL, transaction scope, and one metric you watch. Spring Data pagination abstractions over JPA `setFirstResult/setMaxResults`. Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving pagination: `pageable` count query cost. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `Page` runs data query plus `count(*)` — count often more expensive than page data on large tables. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts.

#### Code / config (when useful)

```java
Page<OrderSummary> findByCustomerId(Long customerId, Pageable pageable);
Slice<OrderSummary> findRecent(Pageable pageable);
```

---

### 26. Batch inserts.

**Short answer:** Enable `hibernate.jdbc.batch_size`, order inserts/updates, avoid IDENTITY generator, and periodically `flush()`/`clear()` in bulk loops. For massive loads use JDBC COPY/SQL*Loader — Hibernate isn't the right tool. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
JDBC batching grouping INSERT statements for fewer roundtrips to the database. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Settings: `batch_size`, `order_inserts`, `order_updates`, Postgres `reWriteBatchedInserts=true`. IDENTITY prevents effective batching. PC holds all entities until flush — memory risk in million-row import. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Batch ORM inserts for moderate bulk (thousands). StatelessSession or raw JDBC for ETL millions. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Import 50k products: batch_size=50, flush/clear every 500 entities, SEQUENCE id generator, monitor duration vs JDBC COPY baseline. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- IDENTITY + batch_size wondering why no improvement; never clearing PC in loop OOM.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** StatelessSession bulk pattern?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. Enable `hibernate.jdbc.batch_size`, order inserts/updates, avoid IDENTITY generator, and periodically `flush()`/`clear()` in bulk loops. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@JdbcBatchSize` annotation?
**A:** On '`@JdbcBatchSize` annotation': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Settings: `batch_size`, `order_inserts`, `order_updates`, Postgres `reWriteBatchedInserts=true`. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Spring Batch chunk sizing?
**A:** On 'Spring Batch chunk sizing': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Settings: `batch_size`, `order_inserts`, `order_updates`, Postgres `reWriteBatchedInserts=true`. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving batch inserts. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Enable `hibernate.jdbc.batch_size`, order inserts/updates, avoid IDENTITY generator, and periodically `flush()`/`clear()` in bulk loops. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Import 50k products: batch_size=50, flush/clear every 500 entities, SEQUENCE id generator, monitor duration vs JDBC COPY baseline.

---

### 27. `hibernate.order_updates` and deadlock reduction.

**Short answer:** Ordering UPDATEs by primary key reduces deadlock probability when multiple transactions update overlapping rows in different orders — helpful but not substitute for consistent business lock ordering. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Hibernate setting sorting update statements for predictable lock acquisition order. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`hibernate.order_updates=true` sorts by entity type and id before issuing SQL. Deadlocks still possible with gap locks and inserts. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Enable in high-contention OLTP as low-cost mitigation. Primary fix: lock resources in consistent order in code. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Concurrent order line quantity updates on same order — ordered updates plus `@Version` reduce deadlock rate measured in prod metrics. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Assuming setting eliminates all deadlocks; ignoring insert lock ordering.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Deadlock graph reading in Postgres?
**A:** On 'Deadlock graph reading in Postgres': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `hibernate.order_updates=true` sorts by entity type and id before issuing SQL. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Retry on `PessimisticLockException`?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Ordering UPDATEs by primary key reduces deadlock probability when multiple transactions update overlapping rows in different orders — helpful but not substitute for consistent business lock ordering. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@DynamicUpdate` lock interaction?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. Ordering UPDATEs by primary key reduces deadlock probability when multiple transactions update overlapping rows in different orders — helpful but not substitute for consistent business lock ordering. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `hibernate.order_updates` and deadlock reduction. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Ordering UPDATEs by primary key reduces deadlock probability when multiple transactions update overlapping rows in different orders — helpful but not substitute for consistent business lock ordering. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Concurrent order line quantity updates on same order — ordered updates plus `@Version` reduce deadlock rate measured in prod metrics.

---

### 28. LazyInitializationException.

**Short answer:** Accessing uninitialized lazy association outside an open persistence context throws this exception. Fix by fetching inside TX (join fetch, entity graph, projection), not by enabling OSIV as permanent crutch. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Runtime error when Hibernate proxy has no session to load association. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Lazy association is proxy; first access triggers SELECT if session open. After session closes, no loader available. `Hibernate.initialize()` forces load still requires open session. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
DTO mapping inside `@Transactional` service method. Open-in-view only if consciously accepted. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Controller called `order.getLines().size()` after service returned — exception with OSIV disabled. Fixed with `OrderDto` built in service using `@EntityGraph`. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- OSIV masking until production; `@JsonIgnoreProperties` hiding missing fetch; `FetchType.EAGER` blanket fix.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Bytecode lazy attributes?
**A:** On 'Bytecode lazy attributes': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Lazy association is proxy; first access triggers SELECT if session open. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** MapStruct lazy mapping?
**A:** On 'MapStruct lazy mapping': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Lazy association is proxy; first access triggers SELECT if session open. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** WebFlux and LazyInitialization?
**A:** On 'WebFlux and LazyInitialization': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Lazy association is proxy; first access triggers SELECT if session open. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving lazyinitializationexception. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Accessing uninitialized lazy association outside an open persistence context throws this exception. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Controller called `order.getLines().size()` after service returned — exception with OSIV disabled.

---

### 29. `n+1` with `@ManyToOne` in a list endpoint.

**Short answer:** Loading N entities each with lazy `@ManyToOne` triggers N additional SELECTs when parent field accessed. Fix with join fetch, batch fetching, or projection query selecting both columns. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Common N+1 variant on to-one side in list views. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`findAll()` users then loop `user.getDepartment().getName()` — 1 + N queries. `@BatchSize(size=20)` on Department batches IN queries. Projection `select u.name, d.name from User u join u.department d` — one query. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Projection for read APIs; entity graph when need full entity graph in service. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency. When read shapes diverge from writes, DTO projections or CQRS read models beat tuning entity graphs for list endpoints.

#### Production example
User list API returns DTO with department name — single JPQL constructor expression query. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Join fetch to-one on paginated list multiplying rows when to-many also present.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@FetchProfile`?
**A:** On '`@FetchProfile`': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `findAll()` users then loop `user.getDepartment().getName()` — 1 + N queries. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate statistics interpretation?
**A:** Senior answer to 'Hibernate statistics interpretation': tie mechanism to production SQL, transaction scope, and one metric you watch. Common N+1 variant on to-one side in list views. User list API returns DTO with department name — single JPQL constructor expression query. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** GraphQL DataLoader pattern?
**A:** On 'GraphQL DataLoader pattern': measure SQL count per endpoint first using APM or Hibernate statistics in staging. `findAll()` users then loop `user.getDepartment().getName()` — 1 + N queries. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `n+1` with `@manytoone` in a list endpoint. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Loading N entities each with lazy `@ManyToOne` triggers N additional SELECTs when parent field accessed. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. User list API returns DTO with department name — single JPQL constructor expression query.

---

### 30. Projections: interface, class, record.

**Short answer:** Interface projections may use closed projection (single query) or open (N+1 risk). Class/record constructor expressions (`select new`) guarantee one query with explicit columns. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Spring Data JPA mechanism returning subset of entity data without full entity hydration. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Closed interface projection: derived query selects needed columns. Open projection with `@Value` SpEL may trigger lazy loads. DTO class/record in `@Query` constructor expression preferred for clarity. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Record DTO for API read models. Interface projection for simple Spring Data derived queries with verified SQL. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
```java @Query("select new com.acme.OrderSummary(o.id, o.status, c.name) " + "from Order o join o.customer c where o.id = :id") Optional<OrderSummary> summaryById(Long id); ``` Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Nested interface projection causing extra queries; native query + interface mapping surprises.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Dynamic projections?
**A:** Senior answer to 'Dynamic projections': tie mechanism to production SQL, transaction scope, and one metric you watch. Spring Data JPA mechanism returning subset of entity data without full entity hydration. ```java @Query("select new com.acme.OrderSummary(o.id, o.status, c.name) " + "from Order o join o.customer c where o.id = :id") Optional<OrderSummary> summaryById(Long id); ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Blaze-Persistence entity views?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. Interface projections may use closed projection (single query) or open (N+1 risk). The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** MapStruct vs projection?
**A:** Senior answer to 'MapStruct vs projection': tie mechanism to production SQL, transaction scope, and one metric you watch. Spring Data JPA mechanism returning subset of entity data without full entity hydration. ```java @Query("select new com.acme.OrderSummary(o.id, o.status, c.name) " + "from Order o join o.customer c where o.id = :id") Optional<OrderSummary> summaryById(Long id); ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone.

#### Scenario probe
After a release, an endpoint involving projections: interface, class, record. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Interface projections may use closed projection (single query) or open (N+1 risk). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. ```java @Query("select new com.acme.OrderSummary(o.id, o.status, c.name) " + "from Order o join o.customer c where o.id = :id") Optional<OrderSummary> summaryById(Long id); ```

---

### 31. Hibernate 6 / Jakarta changes.

**Short answer:** Hibernate 6 aligns with Jakarta Persistence 3.1, improves type system, query semantics, and performance. Migration requires `javax` → `jakarta` packages, dialect updates, and retesting fetch/pagination behavior. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Major Hibernate revision used by Spring Boot 3.x stack. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
New SQM query engine; improved JSON/`Instant` support; `@JdbcTypeCode` for types; changed `NullPrecedence`, DISTINCT handling. Removed legacy criteria paths. Integration with bytecode enhancement. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Plan migration testing around native queries, custom dialect extensions, and Envers compatibility. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency. When read shapes diverge from writes, DTO projections or CQRS read models beat tuning entity graphs for list endpoints.

#### Production example
Upgrade regression: pagination with join fetch returned duplicate roots — fixed by query rewrite per Hibernate 6 DISTINCT rules. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Copying Hibernate 5 `@Type` annotations; assuming identical SQL generation; missing `hibernate.orm.jdbc.time_zone=UTC`.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Spring Boot 3 migration checklist?
**A:** Senior answer to 'Spring Boot 3 migration checklist': tie mechanism to production SQL, transaction scope, and one metric you watch. Major Hibernate revision used by Spring Boot 3.x stack. Upgrade regression: pagination with join fetch returned duplicate roots — fixed by query rewrite per Hibernate 6 DISTINCT rules. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@Incubating` APIs?
**A:** Senior answer to '`@Incubating` APIs': tie mechanism to production SQL, transaction scope, and one metric you watch. Major Hibernate revision used by Spring Boot 3.x stack. Upgrade regression: pagination with join fetch returned duplicate roots — fixed by query rewrite per Hibernate 6 DISTINCT rules. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate Reactive vs classic?
**A:** Senior answer to 'Hibernate Reactive vs classic': tie mechanism to production SQL, transaction scope, and one metric you watch. Major Hibernate revision used by Spring Boot 3.x stack. Upgrade regression: pagination with join fetch returned duplicate roots — fixed by query rewrite per Hibernate 6 DISTINCT rules. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving hibernate 6 / jakarta changes. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Hibernate 6 aligns with Jakarta Persistence 3.1, improves type system, query semantics, and performance. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Upgrade regression: pagination with join fetch returned duplicate roots — fixed by query rewrite per Hibernate 6 DISTINCT rules.

---

### 32. `@Formula`, `@Where`, `@Filter`.

**Short answer:** `@Formula` embeds SQL fragment (non-portable, not indexed). `@Where` adds static SQL condition (soft delete) — easy to miss in native queries. `@Filter` enables parametric session filters. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Hibernate extensions for computed properties and row-level visibility rules. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@Where(clause="deleted = false")` on entity. `@FilterDef` + `@Filter` activated on session with parameters (tenant). `@Formula` read-only computed column subselect. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Soft delete via `@Where` + partial unique index `(email) WHERE deleted=false`. Filters for multi-tenant row scoping. Avoid `@Formula` on hot query paths. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Tenant id filter enabled at request start in interceptor — all queries scoped without repeating `tenant_id = ?`. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Native SQL bypassing `@Where`; forgetting to enable filter in batch jobs; formula preventing index use.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Soft delete vs `@SQLDelete`?
**A:** Senior answer to 'Soft delete vs `@SQLDelete`': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate extensions for computed properties and row-level visibility rules. Tenant id filter enabled at request start in interceptor — all queries scoped without repeating `tenant_id = ?`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Discriminator + soft delete?
**A:** Senior answer to 'Discriminator + soft delete': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate extensions for computed properties and row-level visibility rules. Tenant id filter enabled at request start in interceptor — all queries scoped without repeating `tenant_id = ?`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Filter on collections?
**A:** Senior answer to 'Filter on collections': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate extensions for computed properties and row-level visibility rules. Tenant id filter enabled at request start in interceptor — all queries scoped without repeating `tenant_id = ?`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `@formula`, `@where`, `@filter`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `@Formula` embeds SQL fragment (non-portable, not indexed). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Tenant id filter enabled at request start in interceptor — all queries scoped without repeating `tenant_id = ?`.

---

### 33. Envers vs application-level audit.

**Short answer:** Hibernate Envers auto-maintains history tables — easy but heavy and couples audit to ORM. Application audit columns + domain events often suffice; regulatory needs may require append-only external store. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Envers provides automatic versioning of entity changes into `_AUD` tables. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@Audited` entities tracked on flush; revision numbers and timestamps. Queries via Envers API. Storage growth and write amplification significant on hot tables. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Envers for moderate entities needing point-in-time reconstruction. Prefer `created_by/updated_at` columns + Kafka audit events for business audit trail. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Financial ledger uses immutable append-only event store; operational entities use simple audit columns — Envers rejected after storage projection. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Auditing entire graph including collections; Envers on high-write tables without archival strategy.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Envers performance tuning?
**A:** Senior answer to 'Envers performance tuning': tie mechanism to production SQL, transaction scope, and one metric you watch. Envers provides automatic versioning of entity changes into `_AUD` tables. Financial ledger uses immutable append-only event store; operational entities use simple audit columns — Envers rejected after storage projection. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** CDC vs Envers?
**A:** Senior answer to 'CDC vs Envers': tie mechanism to production SQL, transaction scope, and one metric you watch. Envers provides automatic versioning of entity changes into `_AUD` tables. Financial ledger uses immutable append-only event store; operational entities use simple audit columns — Envers rejected after storage projection. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** GDPR delete in Envers?
**A:** Senior answer to 'GDPR delete in Envers': tie mechanism to production SQL, transaction scope, and one metric you watch. Envers provides automatic versioning of entity changes into `_AUD` tables. Financial ledger uses immutable append-only event store; operational entities use simple audit columns — Envers rejected after storage projection. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving envers vs application-level audit. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Hibernate Envers auto-maintains history tables — easy but heavy and couples audit to ORM. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Financial ledger uses immutable append-only event store; operational entities use simple audit columns — Envers rejected after storage projection.

---

### 34. Multi-tenancy.

**Short answer:** Strategies: discriminator column, separate schema, separate database. Hibernate `CurrentTenantIdentifierResolver` + `MultiTenantConnectionProvider` route connections. Pool sizing per tenant vs shared pool is operational challenge. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Isolating tenant data in shared or separate database structures. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
DISCRIMINATOR: `tenant_id` column + filter. SCHEMA: `SET search_path` or equivalent. DATABASE: separate datasource per tenant. Migrations multiply with schema/database per tenant.

#### When to use / when NOT to use
Discriminator for many small tenants. Separate DB for largest enterprise tenants. Never query without tenant predicate. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
SaaS app: discriminator default; `@PrePersist` sets tenant from security context; integration tests verify cross-tenant leak impossible. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Missing tenant filter in native query; connection pool exhaustion with per-tenant datasources.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Spring `@Async` tenant context?
**A:** Senior answer to 'Spring `@Async` tenant context': tie mechanism to production SQL, transaction scope, and one metric you watch. Isolating tenant data in shared or separate database structures. SaaS app: discriminator default; `@PrePersist` sets tenant from security context; integration tests verify cross-tenant leak impossible. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Row-level security vs Hibernate filter?
**A:** Senior answer to 'Row-level security vs Hibernate filter': tie mechanism to production SQL, transaction scope, and one metric you watch. Isolating tenant data in shared or separate database structures. SaaS app: discriminator default; `@PrePersist` sets tenant from security context; integration tests verify cross-tenant leak impossible. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Tenant in cache keys?
**A:** Senior answer to 'Tenant in cache keys': tie mechanism to production SQL, transaction scope, and one metric you watch. Isolating tenant data in shared or separate database structures. SaaS app: discriminator default; `@PrePersist` sets tenant from security context; integration tests verify cross-tenant leak impossible. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving multi-tenancy. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Strategies: discriminator column, separate schema, separate database. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. SaaS app: discriminator default; `@PrePersist` sets tenant from security context; integration tests verify cross-tenant leak impossible.

---

### 35. Connection provider vs persistence context.

**Short answer:** HikariCP pools physical connections; persistence context holds logical session state and typically binds one connection for transaction duration. Long transactions starve the pool — don't do HTTP calls inside `@Transactional`. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Distinction between connection pooling infrastructure and JPA session lifecycle. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Connection acquired at TX start (or first access), released at TX end. OSIV extends EM lifetime → longer connection hold. Pool `maximumPoolSize` must align with Tomcat threads and TX length. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Keep TX short. Read-only TX still holds connection until complete. Use async messaging for slow external work outside TX. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Pool exhaustion traced to 30s TX including external payment API — moved API call after commit via outbox pattern. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Assuming read-only releases connection mid-request with OSIV; leak detection ignored in staging.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `connection.release_mode`?
**A:** Senior answer to '`connection.release_mode`': tie mechanism to production SQL, transaction scope, and one metric you watch. Distinction between connection pooling infrastructure and JPA session lifecycle. Pool exhaustion traced to 30s TX including external payment API — moved API call after commit via outbox pattern. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Reactive Hibernate connection model?
**A:** Senior answer to 'Reactive Hibernate connection model': tie mechanism to production SQL, transaction scope, and one metric you watch. Distinction between connection pooling infrastructure and JPA session lifecycle. Pool exhaustion traced to 30s TX including external payment API — moved API call after commit via outbox pattern. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Pool sizing formula?
**A:** Senior answer to 'Pool sizing formula': tie mechanism to production SQL, transaction scope, and one metric you watch. Distinction between connection pooling infrastructure and JPA session lifecycle. Pool exhaustion traced to 30s TX including external payment API — moved API call after commit via outbox pattern. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving connection provider vs persistence context. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. HikariCP pools physical connections; persistence context holds logical session state and typically binds one connection for transaction duration. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Pool exhaustion traced to 30s TX including external payment API — moved API call after commit via outbox pattern.

---

### 36. Read replica routing.

**Short answer:** Route read-only transactions to replica via `AbstractRoutingDataSource` and `@Transactional(readOnly=true)`. Handle replica lag — read-your-writes after mutation requires primary pin or synchronous replication awareness. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Scaling read load by directing SELECT traffic to database replicas. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Routing datasource key from transaction readOnly flag or explicit aspect. Lag: user updates profile, immediate read from replica stale — pin to primary post-write or delay UI refresh. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Eventual consistency acceptable for dashboards. Strong read-after-write on same request → primary. CQRS read models alternative. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Product catalog browse from replica; checkout validation reads inventory from primary. Thread-local "sticky primary" for 2s after write. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- Routing writes accidentally to replica; assuming replica lag zero in tests.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** AWS Aurora reader endpoints?
**A:** Senior answer to 'AWS Aurora reader endpoints': tie mechanism to production SQL, transaction scope, and one metric you watch. Scaling read load by directing SELECT traffic to database replicas. Product catalog browse from replica; checkout validation reads inventory from primary. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate `@Transactional` routing AOP?
**A:** Senior answer to 'Hibernate `@Transactional` routing AOP': tie mechanism to production SQL, transaction scope, and one metric you watch. Scaling read load by directing SELECT traffic to database replicas. Product catalog browse from replica; checkout validation reads inventory from primary. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** CQRS vs replica routing?
**A:** Senior answer to 'CQRS vs replica routing': tie mechanism to production SQL, transaction scope, and one metric you watch. Scaling read load by directing SELECT traffic to database replicas. Product catalog browse from replica; checkout validation reads inventory from primary. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving read replica routing. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Route read-only transactions to replica via `AbstractRoutingDataSource` and `@Transactional(readOnly=true)`. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Product catalog browse from replica; checkout validation reads inventory from primary.

---

### 37. Schema generation: `ddl-auto`.

**Short answer:** Never `update` or `create` in production — unreviewed schema drift and data loss risk. Use `none` or `validate`; Flyway/Liquibase for all changes. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Hibernate automatic DDL generation from entity mappings. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`validate`: compare schema to mappings — fail startup on mismatch. `update`: alter schema at runtime — unpredictable. `create-drop`: dev only. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
`validate` in prod CI/staging smoke. Local dev may use Testcontainers + Flyway instead of ddl-auto. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Startup fails validate when developer forgot migration — catches drift before serving traffic. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- `update` in prod "temporarily"; relying on ddl-auto in multi-service shared DB.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Flyway baseline existing DB?
**A:** Senior answer to 'Flyway baseline existing DB': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate automatic DDL generation from entity mappings. Startup fails validate when developer forgot migration — catches drift before serving traffic. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate `@Column` vs migration source of truth?
**A:** Senior answer to 'Hibernate `@Column` vs migration source of truth': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate automatic DDL generation from entity mappings. Startup fails validate when developer forgot migration — catches drift before serving traffic. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Testcontainers migration strategy?
**A:** Senior answer to 'Testcontainers migration strategy': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate automatic DDL generation from entity mappings. Startup fails validate when developer forgot migration — catches drift before serving traffic. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving schema generation: `ddl-auto`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Never `update` or `create` in production — unreviewed schema drift and data loss risk. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Startup fails validate when developer forgot migration — catches drift before serving traffic.

---

### 38. Mapping enums.

**Short answer:** Map enums as `STRING` — never `ORDINAL` (reordering constants corrupts data). PostgreSQL native enum types possible with extra migration care. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
JPA `@Enumerated` mapping Java enums to database columns. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
ORDINAL stores 0,1,2 — fragile. STRING stores name — renames need migration. `@JdbcTypeCode(SqlTypes.NAMED_ENUM)` for Postgres enum type. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
STRING default. Postgres enum when DB-level constraint desired. Document enum additions as expand-only migrations. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
`OrderStatus` stored as VARCHAR; new status `PENDING_PAYMENT` added — backward compatible read; old code ignores unknown with defensive parsing if needed. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- ORDINAL after inserting new constant in middle; renaming enum without DB update.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** AttributeConverter for enum?
**A:** Senior answer to 'AttributeConverter for enum': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA `@Enumerated` mapping Java enums to database columns. `OrderStatus` stored as VARCHAR; new status `PENDING_PAYMENT` added — backward compatible read; old code ignores unknown with defensive parsing if needed. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** JSON enum unknown values?
**A:** Senior answer to 'JSON enum unknown values': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA `@Enumerated` mapping Java enums to database columns. `OrderStatus` stored as VARCHAR; new status `PENDING_PAYMENT` added — backward compatible read; old code ignores unknown with defensive parsing if needed. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Check constraint vs enum type?
**A:** Senior answer to 'Check constraint vs enum type': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA `@Enumerated` mapping Java enums to database columns. `OrderStatus` stored as VARCHAR; new status `PENDING_PAYMENT` added — backward compatible read; old code ignores unknown with defensive parsing if needed. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving mapping enums. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Map enums as `STRING` — never `ORDINAL` (reordering constants corrupts data). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. `OrderStatus` stored as VARCHAR; new status `PENDING_PAYMENT` added — backward compatible read; old code ignores unknown with defensive parsing if needed.

---

### 39. JSON columns (`@JdbcTypeCode(SqlTypes.JSON)`).

**Short answer:** JSON columns flexible for semi-structured attributes — weak DB constraints, indexing DB-specific. Don't dump core queryable fields into JSON to avoid schema migration discipline. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Mapping JSON documents to Java Map, JsonNode, or typed objects in relational columns. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Hibernate 6 `@JdbcTypeCode(SqlTypes.JSON)` with Jackson serialization. Postgres JSONB GIN indexes; Oracle JSON binary. Schema evolution via application versioning inside JSON. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Extension attributes, metadata, feature-varying payloads. Keep filter/sort fields as columns. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Product `attributes` JSONB for color/size; price and sku remain columns with indexes. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- JSON query without index full table scan; storing PII unencrypted in JSON blob.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** JSON schema validation?
**A:** Senior answer to 'JSON schema validation': tie mechanism to production SQL, transaction scope, and one metric you watch. Mapping JSON documents to Java Map, JsonNode, or typed objects in relational columns. Product `attributes` JSONB for color/size; price and sku remain columns with indexes. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** `@ColumnTransformer`?
**A:** Senior answer to '`@ColumnTransformer`': tie mechanism to production SQL, transaction scope, and one metric you watch. Mapping JSON documents to Java Map, JsonNode, or typed objects in relational columns. Product `attributes` JSONB for color/size; price and sku remain columns with indexes. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Migration JSON shape versions?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. JSON columns flexible for semi-structured attributes — weak DB constraints, indexing DB-specific. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving json columns (`@jdbctypecode(sqltypes.json)`). shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. JSON columns flexible for semi-structured attributes — weak DB constraints, indexing DB-specific. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Product `attributes` JSONB for color/size; price and sku remain columns with indexes.

---

### 40. Time zones.

**Short answer:** Store instants in UTC (`Instant`, `timestamptz`). `LocalDateTime` has no zone — bugs around DST and global users. Align JVM, JDBC, and Hibernate `jdbc.time_zone=UTC`. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Correct temporal type selection and timezone configuration across JVM, JDBC, and database. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`Instant` → UTC storage. `OffsetDateTime` preserves offset. Oracle `TIMESTAMP WITH TIME ZONE`. Hibernate 6 time zone storage settings. Server `user.timezone=UTC` in containers.

#### When to use / when NOT to use
Instant for events (created_at). LocalDate for birth date (no time). ZonedDateTime at UI boundary only. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
Promo ends at instant UTC; frontend converts with `Intl.DateTimeFormat`. Tests use fixed Clock. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates.

#### Common mistakes
- `LocalDateTime.now()` for global expiry; mixing TIMESTAMP WITHOUT TIME ZONE columns.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@TimeZoneStorage` options?
**A:** Senior answer to '`@TimeZoneStorage` options': tie mechanism to production SQL, transaction scope, and one metric you watch. Correct temporal type selection and timezone configuration across JVM, JDBC, and database. Promo ends at instant UTC; frontend converts with `Intl.DateTimeFormat`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** JPA 2.2 temporal types?
**A:** Senior answer to 'JPA 2.2 temporal types': tie mechanism to production SQL, transaction scope, and one metric you watch. Correct temporal type selection and timezone configuration across JVM, JDBC, and database. Promo ends at instant UTC; frontend converts with `Intl.DateTimeFormat`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Scheduling with DST gaps?
**A:** Senior answer to 'Scheduling with DST gaps': tie mechanism to production SQL, transaction scope, and one metric you watch. Correct temporal type selection and timezone configuration across JVM, JDBC, and database. Promo ends at instant UTC; frontend converts with `Intl.DateTimeFormat`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving time zones. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Store instants in UTC (`Instant`, `timestamptz`). Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Promo ends at instant UTC; frontend converts with `Intl.DateTimeFormat`.

---

### 41. `PersistenceContextType.EXTENDED`.

**Short answer:** Extended PC spans multiple transactions — conversation pattern like long JSF conversations or OSIV. Rare in stateless REST; invites stale data and memory leaks. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
JPA persistence context scope longer than a single transaction. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Stateful session bean pattern (legacy): EM open across requests with manual flush. OSIV mimics extended-like behavior for web request. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Avoid in REST microservices. Consider only for stateful desktop or specialized workflow UIs with clear lifecycle. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Legacy app migration: replaced extended EM conversation with explicit service methods + DTO per request. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Confusing EXTENDED with OSIV; detached entities accumulating in long conversation.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@ConversationScoped` legacy?
**A:** Senior answer to '`@ConversationScoped` legacy': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA persistence context scope longer than a single transaction. Legacy app migration: replaced extended EM conversation with explicit service methods + DTO per request. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Spring `@Scope` session vs EXTENDED?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. Extended PC spans multiple transactions — conversation pattern like long JSF conversations or OSIV. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Testing extended context?
**A:** Senior answer to 'Testing extended context': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA persistence context scope longer than a single transaction. Legacy app migration: replaced extended EM conversation with explicit service methods + DTO per request. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `persistencecontexttype.extended`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Extended PC spans multiple transactions — conversation pattern like long JSF conversations or OSIV. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Legacy app migration: replaced extended EM conversation with explicit service methods + DTO per request.

---

### 42. StatelessSession.

**Short answer:** No persistence context, no dirty checking, no cascade lifecycle — you manage SQL and identity explicitly. Ideal for bulk ETL reads/writes where ORM overhead isn't justified. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Hibernate API bypassing first-level cache for high-throughput bulk operations. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`session.insert/update/delete/get` directly. No lazy loading. No automatic dirty detection. Close session frequently.

#### When to use / when NOT to use
Millions of rows import/export. Not for interactive OLTP domain logic. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Nightly archive job: StatelessSession reads ids batch, inserts to archive table, deletes source — 10x faster than default Session in benchmark. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Using StatelessSession like normal Session expecting cascade; memory leak not clearing batches.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** StateSession vs JDBC?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. No persistence context, no dirty checking, no cascade lifecycle — you manage SQL and identity explicitly. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Spring integration pattern?
**A:** Senior answer to 'Spring integration pattern': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate API bypassing first-level cache for high-throughput bulk operations. Nightly archive job: StatelessSession reads ids batch, inserts to archive table, deletes source — 10x faster than default Session in benchmark. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Batch delete with StatelessSession?
**A:** EntityManagerFactory is expensive and thread-safe — one per application. EntityManager/Session is lightweight, bound per transaction in Spring. No persistence context, no dirty checking, no cascade lifecycle — you manage SQL and identity explicitly. The persistence context is the first-level cache behind the EM — identity map, dirty checking, lazy proxies. OSIV extends EM until view render; prefer open-in-view: false with explicit fetch in the service layer. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving statelesssession. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. No persistence context, no dirty checking, no cascade lifecycle — you manage SQL and identity explicitly. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Nightly archive job: StatelessSession reads ids batch, inserts to archive table, deletes source — 10x faster than default Session in benchmark.

---

### 43. Bulk JPQL update/delete bypass PC.

**Short answer:** `UPDATE Entity e SET ...` executes SQL directly — entities in persistence context remain stale until refreshed or cleared. Version columns may not auto-increment unless included in UPDATE. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Bulk operations circumventing Hibernate dirty checking and entity state sync. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`@Modifying` Spring Data queries call `executeUpdate()`. PC entities with same ids show old values until `em.refresh()` or `clear()`. Second-level cache may need eviction. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Mass status updates, purge jobs. Follow with `clear()` or avoid loading affected entities in same TX. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Expire stale carts: `@Modifying @Query("update Cart c set c.status = EXPIRED where ...")` then `entityManager.clear()`. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Bulk update then returning managed entities with stale state to API; optimistic lock bypass.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@Modifying(flushAutomatically)`?
**A:** '`@Modifying(flushAutomatically)`' — know entity state and who owns the transaction boundary. `@Modifying` Spring Data queries call `executeUpdate()`. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Bulk delete orphan constraints?
**A:** Senior answer to 'Bulk delete orphan constraints': tie mechanism to production SQL, transaction scope, and one metric you watch. Bulk operations circumventing Hibernate dirty checking and entity state sync. Expire stale carts: `@Modifying @Query("update Cart c set c.status = EXPIRED where ...")` then `entityManager.clear()`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** CDC seeing bulk changes?
**A:** Senior answer to 'CDC seeing bulk changes': tie mechanism to production SQL, transaction scope, and one metric you watch. Bulk operations circumventing Hibernate dirty checking and entity state sync. Expire stale carts: `@Modifying @Query("update Cart c set c.status = EXPIRED where ...")` then `entityManager.clear()`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving bulk jpql update/delete bypass pc. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `UPDATE Entity e SET ...` executes SQL directly — entities in persistence context remain stale until refreshed or cleared. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Expire stale carts: `@Modifying @Query("update Cart c set c.status = EXPIRED where ...")` then `entityManager.clear()`.

---

### 44. Hibernate types and `AttributeConverter`.

**Short answer:** `AttributeConverter` maps custom Java types to JDBC columns — Money to minor units bigint, encrypted strings. `@Converter(autoApply=true)` applies globally — verify scope. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
JPA standard extension for custom type persistence without Hibernate UserType (legacy). This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
`convertToDatabaseColumn` / `convertToEntityAttribute`. Registered via `@Converter` or `@Convert`. Hibernate `@JdbcTypeCode` for built-in advanced types. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Money, Email value types, encryption at rest layer. autoApply carefully — may affect unintended columns of same type. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency. When read shapes diverge from writes, DTO projections or CQRS read models beat tuning entity graphs for list endpoints.

#### Production example
```java @Converter public class MoneyConverter implements AttributeConverter<Money, Long> { public Long convertToDatabaseColumn(Money m) { return m.minorUnits(); } public Money convertToEntityAttribute(Long db) { return Money.ofMinor(db); } } ``` Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Null handling forgotten; converter applied to `@Embeddable` fields unexpectedly with autoApply.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@CompositeUserType` legacy?
**A:** Senior answer to '`@CompositeUserType` legacy': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA standard extension for custom type persistence without Hibernate UserType (legacy). ```java @Converter public class MoneyConverter implements AttributeConverter<Money, Long> { public Long convertToDatabaseColumn(Money m) { return m.minorUnits(); } public Money convertToEntityAttribute(Long db) { return Money.ofMinor(db); } } ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** JSON converter vs `@JdbcTypeCode(JSON)`?
**A:** Senior answer to 'JSON converter vs `@JdbcTypeCode(JSON)`': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA standard extension for custom type persistence without Hibernate UserType (legacy). ```java @Converter public class MoneyConverter implements AttributeConverter<Money, Long> { public Long convertToDatabaseColumn(Money m) { return m.minorUnits(); } public Money convertToEntityAttribute(Long db) { return Money.ofMinor(db); } } ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Encryption key rotation?
**A:** Senior answer to 'Encryption key rotation': tie mechanism to production SQL, transaction scope, and one metric you watch. JPA standard extension for custom type persistence without Hibernate UserType (legacy). ```java @Converter public class MoneyConverter implements AttributeConverter<Money, Long> { public Long convertToDatabaseColumn(Money m) { return m.minorUnits(); } public Money convertToEntityAttribute(Long db) { return Money.ofMinor(db); } } ``` Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving hibernate types and `attributeconverter`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `AttributeConverter` maps custom Java types to JDBC columns — Money to minor units bigint, encrypted strings. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. ```java @Converter public class MoneyConverter implements AttributeConverter<Money, Long> { public Long convertToDatabaseColumn(Money m) { return m.minorUnits(); } public Money convertToEntityAttribute(Long db) { return Money.ofMinor(db); } } ```

---

### 45. Testing JPA.

**Short answer:** `@DataJpaTest` fast but H2 differs from prod Postgres/Oracle. Use Testcontainers matching prod engine. Assert SQL count with datasource-proxy; test optimistic lock with two EntityManagers. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
Testing strategy validating ORM mappings, queries, and concurrency behavior realistically. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Testcontainers starts real DB in Docker. `@DataJpaTest` slices JPA + `@AutoConfigureTestDatabase(replace=NONE)`. Two EMs simulate concurrent update for `@Version`. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Unit test domain without DB when possible. Integration test repositories against Testcontainers. Never rely on H2 for SQL dialect features used in prod. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests.

#### Production example
CI runs `@DataJpaTest` with Postgres 16 Testcontainer; p6spy fails test if order list query exceeds 3 SQL statements. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- `@Transactional` test rollback hiding constraint violations; shared Testcontainer without isolation.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@Sql` scripts vs Flyway in tests?
**A:** Senior answer to '`@Sql` scripts vs Flyway in tests': tie mechanism to production SQL, transaction scope, and one metric you watch. Testing strategy validating ORM mappings, queries, and concurrency behavior realistically. CI runs `@DataJpaTest` with Postgres 16 Testcontainer; p6spy fails test if order list query exceeds 3 SQL statements. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Test entity builders?
**A:** Senior answer to 'Test entity builders': tie mechanism to production SQL, transaction scope, and one metric you watch. Testing strategy validating ORM mappings, queries, and concurrency behavior realistically. CI runs `@DataJpaTest` with Postgres 16 Testcontainer; p6spy fails test if order list query exceeds 3 SQL statements. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** ArchUnit JPA rules?
**A:** Senior answer to 'ArchUnit JPA rules': tie mechanism to production SQL, transaction scope, and one metric you watch. Testing strategy validating ORM mappings, queries, and concurrency behavior realistically. CI runs `@DataJpaTest` with Postgres 16 Testcontainer; p6spy fails test if order list query exceeds 3 SQL statements. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving testing jpa. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `@DataJpaTest` fast but H2 differs from prod Postgres/Oracle. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. CI runs `@DataJpaTest` with Postgres 16 Testcontainer; p6spy fails test if order list query exceeds 3 SQL statements.

---

### 46. `saveAndFlush` vs `flush`.

**Short answer:** `saveAndFlush` persists then immediately flushes to DB — surfaces constraint violations early in same TX. Raw `flush()` without batching in loop kills performance. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Spring Data JPA convenience forcing synchronization to database mid-transaction. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Flush sends SQL; still committable or rollbackable in same TX. Useful before native query needing visible rows or getting generated id from trigger. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer. Hibernate orders batched INSERT/UPDATE statements by entity type and primary key when order_inserts and order_updates are enabled.

#### When to use / when NOT to use
Validate unique constraint before external call in same TX. Batch jobs: periodic flush+clear, not every row `saveAndFlush`. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Create user then call external ID verification requiring user row exists — `saveAndFlush` before HTTP call still inside TX cautiously. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- `saveAndFlush` in import loop disabling batching; assuming flush equals commit.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Trigger-generated id after flush?
**A:** 'Trigger-generated id after flush' — know entity state and who owns the transaction boundary. Flush sends SQL; still committable or rollbackable in same TX. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Flush and `@Version` increment?
**A:** Optimistic (@Version) suits read-heavy OLTP; pessimistic FOR UPDATE suits scarce resources — keep transactions short with consistent lock ordering. `saveAndFlush` persists then immediately flushes to DB — surfaces constraint violations early in same TX. SKIP LOCKED / NOWAIT for queue workers; enable order_updates to reduce deadlock probability. Bulk JPQL bypasses version increment unless you clearAutomatically. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Repository `flush()` explicit?
**A:** 'Repository `flush()` explicit' — know entity state and who owns the transaction boundary. Flush sends SQL; still committable or rollbackable in same TX. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving `saveandflush` vs `flush`. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. `saveAndFlush` persists then immediately flushes to DB — surfaces constraint violations early in same TX. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Create user then call external ID verification requiring user row exists — `saveAndFlush` before HTTP call still inside TX cautiously.

---

### 47. Constraint violations mapping.

**Short answer:** Unique/FK violations become `DataIntegrityViolationException` — map to HTTP 409 at API layer. Hibernate Validator uniqueness annotations don't prevent race — DB constraint is source of truth. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Translating database constraint failures to user-meaningful API errors. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Spring `SQLExceptionTranslator` wraps vendor error codes. Parse message fragile — prefer constraint name mapping table. Catch at service boundary, not repository everywhere. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Global `@ControllerAdvice` handler for integrity violations. Business duplicate checks plus DB unique index defense in depth. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Duplicate email registration: Postgres unique violation → 409 Problem Detail type `duplicate-email`. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Relying only on `@Column(unique=true)` without handling exception; leaking raw SQL in error message.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** `@SQLState` portable handling?
**A:** '`@SQLState` portable handling' — know entity state and who owns the transaction boundary. Spring `SQLExceptionTranslator` wraps vendor error codes. merge returns the managed instance; the argument stays detached. Spring save uses isNew to choose persist or merge — detached DTO-mapped entities cause orphan collection bugs. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Partial unique index violations?
**A:** Senior answer to 'Partial unique index violations': tie mechanism to production SQL, transaction scope, and one metric you watch. Translating database constraint failures to user-meaningful API errors. Duplicate email registration: Postgres unique violation → 409 Problem Detail type `duplicate-email`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Retry on serialization failure?
**A:** Senior answer to 'Retry on serialization failure': tie mechanism to production SQL, transaction scope, and one metric you watch. Translating database constraint failures to user-meaningful API errors. Duplicate email registration: Postgres unique violation → 409 Problem Detail type `duplicate-email`. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving constraint violations mapping. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Unique/FK violations become `DataIntegrityViolationException` — map to HTTP 409 at API layer. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Duplicate email registration: Postgres unique violation → 409 Problem Detail type `duplicate-email`.

---

### 48. Second-level cache with `@Cache` on collections.

**Short answer:** Collection cache stores element ids — entity cache must also cache elements. Any collection mutation invalidates cache entry — cluster invalidation latency causes brief inconsistency. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Caching `@OneToMany`/`@ManyToMany` collection regions in second-level cache. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Collection region stores keys of entities; elements loaded from entity regions. Adding/removing element invalidates parent's collection cache. READ_WRITE strategy uses soft locks. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Rare — prefer query cache off, application cache of DTOs, or denormalized read model. If used, limit to stable reference relationships. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Disabled collection cache after incident showing stale membership list in cluster for 200ms after update. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Caching collection without caching entity type; expecting collection cache to skip all DB reads.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Cache concurrency strategies table?
**A:** Senior answer to 'Cache concurrency strategies table': tie mechanism to production SQL, transaction scope, and one metric you watch. Caching `@OneToMany`/`@ManyToMany` collection regions in second-level cache. Disabled collection cache after incident showing stale membership list in cluster for 200ms after update. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Natural id region?
**A:** Senior answer to 'Natural id region': tie mechanism to production SQL, transaction scope, and one metric you watch. Caching `@OneToMany`/`@ManyToMany` collection regions in second-level cache. Disabled collection cache after incident showing stale membership list in cluster for 200ms after update. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Metrics on cache hit ratio?
**A:** Senior answer to 'Metrics on cache hit ratio': tie mechanism to production SQL, transaction scope, and one metric you watch. Caching `@OneToMany`/`@ManyToMany` collection regions in second-level cache. Disabled collection cache after incident showing stale membership list in cluster for 200ms after update. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving second-level cache with `@cache` on collections. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Collection cache stores element ids — entity cache must also cache elements. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Disabled collection cache after incident showing stale membership list in cluster for 200ms after update.

---

### 49. Hibernate bytecode enhancement.

**Short answer:** Build-time enhancement enables lazy basic attributes, dirty tracking without snapshots, and better association lazy loading. Worth it on large models; debugging stack traces slightly harder. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load. Production failures often surface as query storms, stale second-level cache entries, or transactions held open across remote calls.

#### What it is
Hibernate agent modifying entity bytecode at build time for performance features. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Maven/Gradle `hibernate-enhance-maven-plugin`. Features: `enableLazyInitialization`, `enableDirtyTracking`, `enableAssociationManagement`. Required for some lazy field patterns without field access violation. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Enable when profiling shows snapshot memory or need lazy basic fields. Ensure CI runs enhancement consistently. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Large insurance policy graph: enhancement reduced heap per request 30% in load test by eliminating deep snapshots. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- Enhanced entities in dev without plugin — works differently prod; mixing enhanced and non-enhanced modules.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Enhancement vs MapStruct compile order?
**A:** Senior answer to 'Enhancement vs MapStruct compile order': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate agent modifying entity bytecode at build time for performance features. Large insurance policy graph: enhancement reduced heap per request 30% in load test by eliminating deep snapshots. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Quarkus default enhancement?
**A:** Senior answer to 'Quarkus default enhancement': tie mechanism to production SQL, transaction scope, and one metric you watch. Hibernate agent modifying entity bytecode at build time for performance features. Large insurance policy graph: enhancement reduced heap per request 30% in load test by eliminating deep snapshots. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Lazy collection without enhancement?
**A:** On 'Lazy collection without enhancement': measure SQL count per endpoint first using APM or Hibernate statistics in staging. Maven/Gradle `hibernate-enhance-maven-plugin`. JOIN FETCH and @EntityGraph for bounded graphs; @BatchSize or default_batch_fetch_size as safer global tuning; DTO projections are best for list APIs. Never paginate with collection fetch join; avoid two bag JOIN FETCH — use Set, separate queries, or batch fetch. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving hibernate bytecode enhancement. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Build-time enhancement enables lazy basic attributes, dirty tracking without snapshots, and better association lazy loading. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Large insurance policy graph: enhancement reduced heap per request 30% in load test by eliminating deep snapshots.

---

### 50. Senior mental model.

**Short answer:** Treat Hibernate as a unit-of-work mapper, not a graph navigation toolkit. Open TX, load small aggregate, mutate, flush, commit. Fetch deliberately, version hot rows, measure SQL, use outbox for side effects — draw PC lifecycle on whiteboard. The senior trade-off is developer ergonomics versus predictable SQL, lock duration, and connection pool usage under concurrent load.

#### What it is
The integrated mindset tying persistence context, transactions, fetch planning, locking, and messaging. This sits at the intersection of the JPA specification, Hibernate Session implementation, and Spring declarative transaction management. Interviewers expect mechanism and production failure modes — not annotation names without naming flush timing or transaction scope.

#### How it works (internals)
Request → `@Transactional` service → load aggregate with planned fetch → business logic → flush dirty check → commit → connection released. Side effects via outbox same TX. Read APIs use projections bypassing entity graph entirely. Spring binds the EntityManager to the transaction synchronization manager, so flush and commit follow @Transactional boundaries on the service layer.

#### When to use / when NOT to use
Apply rigor in all production persistence paths. Prototypes may cut corners temporarily with explicit tech debt ticket. Prefer explicit fetch plans per endpoint over global EAGER mappings that hide N+1 until load tests. Do not treat Open Session In View as permanent architecture — it masks missing fetch joins and ties pool connections to HTTP latency.

#### Production example
Incident postmortem: N+1 in list endpoint caused DB CPU spike — fixed projection query, disabled OSIV, added SQL assertion test, documented aggregate boundaries in ADR. Catch regressions with integration tests that assert query count per endpoint against Testcontainers on the production database dialect. On-call runbooks document expected SQL shape, transaction propagation, and whether the path uses pessimistic locks or bulk updates. After incidents, add a regression test so the same flush, fetch, or cache invalidation bug cannot ship silently again.

#### Common mistakes
- "Spring Data handles it"; walking lazy graph in loop; no `@Version` on concurrent entity; bulk update with stale PC.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.
- Fixing symptoms with global defaults instead of per-endpoint fetch plans or service boundaries.
- Skipping integration tests on the production database dialect before shipping.

#### Interview follow-ups (with model answers)

**Q:** Whiteboard order flow with PC and Kafka outbox?
**A:** Senior answer to 'Whiteboard order flow with PC and Kafka outbox': tie mechanism to production SQL, transaction scope, and one metric you watch. The integrated mindset tying persistence context, transactions, fetch planning, locking, and messaging. Incident postmortem: N+1 in list endpoint caused DB CPU spike — fixed projection query, disabled OSIV, added SQL assertion test, documented aggregate boundaries in ADR. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone.

**Q:** When to abandon ORM for read path?
**A:** Senior answer to 'When to abandon ORM for read path': tie mechanism to production SQL, transaction scope, and one metric you watch. The integrated mindset tying persistence context, transactions, fetch planning, locking, and messaging. Incident postmortem: N+1 in list endpoint caused DB CPU spike — fixed projection query, disabled OSIV, added SQL assertion test, documented aggregate boundaries in ADR. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Hibernate vs jOOQ division of labor?
**A:** Senior answer to 'Hibernate vs jOOQ division of labor': tie mechanism to production SQL, transaction scope, and one metric you watch. The integrated mindset tying persistence context, transactions, fetch planning, locking, and messaging. Incident postmortem: N+1 in list endpoint caused DB CPU spike — fixed projection query, disabled OSIV, added SQL assertion test, documented aggregate boundaries in ADR. Validate with SQL logging, query-count assertions per endpoint, and integration tests on Postgres or Oracle — not H2 assumptions alone. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
After a release, an endpoint involving senior mental model. shows rising p95 latency; APM reports many similar JDBC statements or Hikari pool wait time increasing.

**Model answer:** I confirm query count and transaction length: N+1, missing FK index, OSIV, long @Transactional spanning remote calls, or stale L2 cache. Treat Hibernate as a unit-of-work mapper, not a graph navigation toolkit. Reproduce in staging with SQL logging; fix with fetch join, projection, batch size, or cache eviction. Incident postmortem: N+1 in list endpoint caused DB CPU spike — fixed projection query, disabled OSIV, added SQL assertion test, documented aggregate boundaries in ADR.

#### Code / config (when useful)

```yaml
spring.jpa.open-in-view: false
spring.jpa.properties.hibernate.generate_statistics: false  # true only when profiling
spring.jpa.properties.hibernate.jdbc.time_zone: UTC
```

---

### 51. `@SQLRestriction` and `@SQLDelete` soft delete (Hibernate 6.3+).

**Short answer:** `@SQLDelete` replaces DELETE with UPDATE setting deleted flag; `@SQLRestriction` (replaces deprecated `@Where`) appends `deleted = false` to all entity queries automatically. Together they implement transparent soft delete without filtering in every JPQL string. Trade-off: unique constraints must include deleted flag or use partial index; native SQL bypasses restriction unless you remember manual filter.

#### What it is
Hibernate entity-level soft delete annotations — SQL customization on lifecycle and global query predicate.

#### How it works (internals)
On `remove(entity)`, Hibernate executes `@SQLDelete(sql="UPDATE orders SET deleted=true WHERE id=?")` instead of DELETE. `@SQLRestriction("deleted = false")` adds predicate to loads, joins, and collections referencing entity. Hibernate 6.3 renamed `@Where` to `@SQLRestriction` for clarity.

#### When to use / when NOT to use
Audit/compliance domains needing recoverable deletes — soft delete. Hard delete for GDPR erasure — override with native delete or dedicated purge job bypassing restriction. High-volume purge — batch UPDATE then archive, not per-entity remove().

#### Production example
Orders soft-deleted retain FK history for invoices; list API never sees deleted rows without `@Where` on every query. Unique on `(customer_id, order_number, deleted)` allows re-order same number after soft delete. Incident: native cleanup script hard-deleted rows breaking audit — runbook updated.

#### Common mistakes
Unique constraint on `(email)` only — second signup fails after soft delete. Forgetting `@SQLRestriction` on associated entity — orphan deleted rows visible via join workaround. Calling `delete()` expecting row gone from DB — disk growth.

#### Interview follow-ups (with model answers)

**Q:** `@SQLDelete` vs `@SoftDelete` (Hibernate 6.5+)?
**A:** Newer `@SoftDelete` API integrates strategy enum (ACTIVE, DELETED timestamps) with less boilerplate SQL strings. `@SQLDelete` + `@SQLRestriction` still common in codebases on 6.3–6.4. Migration path documented in Hibernate migration guide — know both in interview.

**Q:** Does soft delete affect second-level cache?
**A:** Evict entity region on soft remove; cached entity may resurrect if not invalidated. `@Cache` on soft-deleted entity needs careful invalidation or disable cache for that type. Test cache hit after delete returns null/absent.

#### Scenario probe

Customer cannot re-register same email after account "deleted" — unique violation on email column.

**Model answer:** Soft delete leaves row with deleted=true; unique on email blocks insert. Fix partial unique index `WHERE deleted=false` (Postgres) or compound unique `(email, deleted)`. Product decision: allow email reuse vs permanent block. Document in API that delete is soft.

---

### 52. `@NaturalId` and natural id caching.

**Short answer:** `@NaturalId` marks business-stable identifier (SKU, SSN hash) separate from surrogate `@Id`. Hibernate provides `Session.byNaturalId()` API with optional `@NaturalIdCache` region for read-heavy lookups by natural key without hitting DB every time. Invalidate natural id cache on updates to natural key fields — rare but must be transactional. Prefer surrogate PK for joins; natural id for human-meaningful lookups.

#### What it is
Hibernate extension for immutable or slow-changing business keys with dedicated loading API and L2 cache integration.

#### How it works (internals)
`session.byNaturalId(Product.class).using("sku", sku).load()` generates optimized query; cache stores naturalId → pk mapping. Changing natural id field requires cache eviction — Hibernate handles on flush if configured. Not part of JPA standard — Hibernate-specific.

#### When to use / when NOT to use
Lookup product by SKU millions of times daily — natural id cache. Natural key changes frequently — avoid caching. Cross-vendor portability requirement — document Hibernate dependency.

#### Production example
Catalog service: `@NaturalId(mutable=false) sku` with `@NaturalIdCache` — 95% cache hit on SKU resolution in cart flow. DB load drops; watch cache miss spike after bulk SKU import requiring region clear.

#### Common mistakes
Mutable natural id without cache strategy — stale reads. Using natural id as `@Id` complicating FK migrations — surrogate + unique natural id cleaner. Exposing natural id loader without authorization — enumeration risk.

#### Interview follow-ups (with model answers)

**Q:** Natural id vs unique column + repository method?
**A:** Repository `findBySku` always hits query cache/L2 only if annotated `@Cacheable` on method — separate concern. `@NaturalId` integrates with persistence context and dedicated cache region optimized for id→entity resolution. Choose for Hibernate-centric apps with heavy natural key reads.

**Q:** Cluster invalidation?
**A:** `@NaturalIdCache` uses same L2 provider (Infinispan, Redis) — cluster invalidation follows entity region policies. Bulk import: call `session.getSessionFactory().getCache().evictEntityData(Product.class)` in job.

#### Scenario probe

Price update by SKU sees stale price intermittently after enabling natural id cache without understanding mutability.

**Model answer:** Cached entity snapshot stale if price on same row updated via bulk SQL bypassing Hibernate. Fix: evict after bulk job; do not mark volatile fields as part of natural id cache entity without `@Cache` concurrency strategy read-write. Prefer cache natural id mapping only, load fresh entity for price in TX.

---

### 53. `@JoinFormula` and derived associations.

**Short answer:** `@JoinFormula` defines association join condition via SQL formula instead of simple `@JoinColumn` — e.g., join latest version row, polymorphic discriminator match, or effective-dated relationship. Powerful for legacy schemas without clean FKs; fragile across databases and breaks schema-agnostic JPQL assumptions. Use sparingly with integration tests on target dialect; prefer views or database FK refactor long-term.

#### What it is
Hibernate mapping for read-only or computed joins using SQL expression in ON clause.

#### How it works (internals)
`@ManyToOne @JoinFormula("(SELECT id FROM dept d WHERE d.code = emp.dept_code AND d.active = true)")` — Hibernate embeds subselect in joins. Often read-only (`insertable=false, updatable=false`). Generated SQL complex — explain plan critical.

#### When to use / when NOT to use
Legacy ERP schema where FK missing but business join rule exists — bridge with `@JoinFormula`. Greenfield — proper FK and `@JoinColumn`. Multi-tenant effective dating where FK points to header not line — maybe formula or `@JoinColumnOrFormula`.

#### Production example
Employee to "current department" via formula picking row where `effective_to IS NULL` — avoids duplicate `@ManyToOne` columns. Oracle plan review adds index on `(dept_code, effective_to)` — without it list employees N+1 subselect disaster.

#### Common mistakes
Portable JPQL join fetch on formula association — dialect-specific failure. Writable association via formula — updates wrong row. Omitting `insertable/updatable false` — Hibernate generates invalid INSERT.

#### Interview follow-ups (with model answers)

**Q:** `@JoinFormula` vs database view mapped as entity?
**A:** View entity read-only clean separation — DBA owns view definition. `@JoinFormula` hides complexity in annotation — harder for ops to discover. Prefer view for team boundaries; formula for quick legacy bridge with deprecation ticket.

**Q:** Performance?
**A:** Subselect per join row — correlated subquery risk. EXPLAIN on worst query; materialized view if hot path. `@BatchSize` on collection still helps but formula join may defeat index nested loop.

#### Scenario probe

Hibernate 6 upgrade changes formula join SQL — Oracle plan regressions 10x latency.

**Model answer:** Regression test with SQL capture comparing 5.x vs 6.x plans on staging Oracle Testcontainers. Fix: rewrite formula to `@JoinColumn` after schema migration adding surrogate FK; or hint/index tuning. Pin Hibernate minor until fix — document formula as high-risk mapping in ADR.

---

### 54. Hibernate Search 7 + Elasticsearch integration.

**Short answer:** Hibernate Search maps entities to Elasticsearch/OpenSearch indexes via `@Indexed`, `@FullTextField`, `@KeywordField` — automatic index updates on persist/flush (outbox or sync). Version 7 aligns with Hibernate ORM 6 and Jakarta. Use for full-text search, faceted catalog browse — not replacement for transactional DB. Eventual consistency between DB and index requires outbox or failure reconciliation job.

#### What it is
Full-text search bridge: ORM lifecycle triggers index document updates; Search DSL queries Elasticsearch without hand-rolled REST clients for CRUD sync.

#### How it works (internals)
`@IndexedEntity` registers entity; MassIndexer for bulk reindex. `@IndexingPlan` executes on transaction commit (sync) or async backend. Hibernate Search 7 uses Elasticsearch Java client 8.x; configuration `spring.jpa.properties.hibernate.search.backend.hosts`.

#### When to use / when NOT to use
Product search, autocomplete, log-like faceting — Search. Simple `LIKE` on indexed column — DB index enough. Strong consistency read-your-writes — need sync indexing or read DB until index caught up.

#### Production example
Catalog `@FullTextField(name="title")` + `@KeywordField brand`; user search sub-50ms on ES cluster; DB remains source of truth. Reindex job nightly verifies drift count; outbox pattern on index failure during peak.

#### Common mistakes
Indexing lazy associations without `@IndexedEmbedded` plan — N+1 index writes. Full cluster reindex on deploy without blue-green index alias swap. Searching before MassIndexer completes — empty results.

#### Interview follow-ups (with model answers)

**Q:** Sync vs async indexing?
**A:** Sync on commit adds latency to TX — acceptable for low-volume admin edits. Async (`backend.scheduled.delay`) decouples but risks stale search until worker runs. Kafka outbox + indexer consumer for reliable async at scale.

**Q:** Hibernate Search vs Spring Data Elasticsearch?
**A:** Search keeps mapping on entity co-located with ORM — single model. Spring Data ES separate repository layer — good if search schema diverges heavily from ORM. Hybrid: Search for entity-driven sync, custom REST for aggregations.

#### Scenario probe

Product saved in DB but missing in search for 30 minutes after ES cluster yellow.

**Model answer:** Async indexing backlog; yellow shards delayed writes. Monitor index lag metric; pause bulk imports until cluster green. Temporary read fallback query DB with `LIKE` degraded mode flag. Long-term: outbox with retry DLQ and lag alert >60s.

---

### 55. Spring Data JPA auditing (`@CreatedDate`, `@LastModifiedBy`).

**Short answer:** `@EnableJpaAuditing` + `@EntityListeners(AuditingEntityListener.class)` auto-populates `@CreatedDate`, `@LastModifiedDate`, `@CreatedBy`, `@LastModifiedBy` on persist/update. `AuditorAware<String>` bean supplies current user from SecurityContext. Works only through Spring Data save/merge paths — bulk JPQL bypasses listeners. Immutable created fields should set `updatable=false`.

#### What it is
Cross-cutting audit metadata on entities without manual setter calls in every service method.

#### How it works (internals)
AuditingEntityListener callbacks on `@PrePersist`/`@PreUpdate`; dates use `Optional` `DateTimeProvider` bean for test clock. `@CreatedBy` needs authenticated context — batch jobs use `@AuthenticationPrincipal` substitute or system auditor in AuditorAware.

#### When to use / when NOT to use
Standard CRUD entities needing who/when — auditing. High-volume append-only events — DB default `now()` may suffice. Compliance requiring tamper-proof audit — DB triggers or event store, not only JPA fields.

#### Production example
`Order` entity `@CreatedDate Instant createdAt` populated automatically; support searches by date range. Batch import sets AuditorAware to `system-import` via `@BeforeStep` context holder — traceable ownership.

#### Common mistakes
Auditing disabled in test slice — null dates fail assertions. `@Modifying` bulk update skips `@LastModifiedDate` — stale audit. Mutable `@CreatedBy` allowing overwrite on update.

#### Interview follow-ups (with model answers)

**Q:** AuditorAware in async thread?
**A:** SecurityContext not propagated — TaskDecorator copies principal or AuditorAware reads MDC/scoped value. Batch: ThreadLocal holder set in job listener before repository calls.

**Q:** `@CreatedDate` with `@Version`?
**A:** Complementary — version for optimistic lock, dates for audit. Both work with same listener order; test concurrent update bumps version and lastModified together.

#### Scenario probe

Compliance audit finds orders with null `created_by` during peak — Kafka consumer persisted without security context.

**Model answer:** Consumer thread lacks AuditorAware user — returns empty Optional. Fix: propagate user from event payload into `AuditorAware` scoped holder at listener entry; reject events missing actor. Backfill job sets `unknown-migration` for historical nulls with ticket reference.

---

### 56. Batch fetching (`@BatchSize`) vs `@Fetch(FetchMode.SUBSELECT)`.

**Short answer:** `@BatchSize(n)` on entity/collection batches lazy loads — Hibernate groups `WHERE id IN (...)` up to n ids, reducing N+1. `@Fetch(SUBSELECT)` loads collection via subselect `WHERE owner_id IN (SELECT id FROM owners WHERE ...)` — one extra query per entity type per query tree, can over-fetch. Prefer `@BatchSize` for predictable query count; SUBSELECT when collections large and batch IN list would exceed parameter limits.

#### What it is
Fetch tuning annotations controlling how Hibernate loads lazy associations beyond default N+1 behavior.

#### How it works (internals)
`@BatchSize(16)` on `Order.items` — loading 100 orders triggers ceil(100/16) batch queries for items not one per order. SUBSELECT generates `where items.order_id in (select id from orders where ...)` — single query for all items of all orders in persistence context query — can pull huge graphs.

#### When to use / when NOT to use
List endpoints with lazy collections occasionally accessed — `@BatchSize` global default via `hibernate.default_batch_fetch_size=16`. SUBSELECT rare — deep graphs with moderate collection sizes. Best: fetch join or DTO projection for hot paths — annotations are safety net.

#### Production example
Admin order list adds `@BatchSize(32)` on `OrderLine` — query count drops 201→7 in stats. SUBSELECT on `Category.products` caused 50MB result when only category names needed — replaced with projection query.

#### Common mistakes
SUBSELECT on large bag collections — memory spike. `@BatchSize` too large — Oracle IN list limits (1000). Relying on batch fetch instead of fixing API returning entity graphs.

#### Interview follow-ups (with model answers)

**Q:** Default batch fetch size property?
**A:** `spring.jpa.properties.hibernate.default_batch_fetch_size=16` applies to all lazy loads — good baseline. Entity-level `@BatchSize` overrides. Verify with `statistics` or datasource-proxy query count test.

**Q:** `@BatchSize` vs join fetch in JPQL?
**A:** Join fetch in query plan explicit for that use case — best for known hot path. Batch size helps when code path unpredictable or legacy traversal. Join fetch duplicates parent rows with multiple bags — MultipleBagFetchException — batch size safer for bags.

#### Scenario probe

Enable SUBSELECT on `Author.books` — library search page loads all books for all authors in result page — heap GC pause.

**Model answer:** SUBSELECT over-fetched entire collection table slice. Switch to `@BatchSize`, pagination on authors, DTO with `COUNT` subquery for book count only. Hibernate stats showed single query returning 200k rows — fixed before prod canary.

---

### 57. `@NamedEntityGraph` vs entity graph API dynamic graphs.

**Short answer:** `@NamedEntityGraph` declares fetch plan on entity (attribute nodes, subgraphs) invoked by name in repository `@EntityGraph` or `EntityManager.createEntityGraph`. Dynamic graphs built at runtime via `em.createEntityGraph(Order.class)` add subgraph nodes per use case without proliferating annotations. Both generate LEFT JOIN FETCH or batch fetch plan depending on attributes — override global EAGER mistakes with per-query plan.

#### What it is
JPA 2.1+ mechanism to define which associations to initialize in a query without changing fetch type mapping globally.

#### How it works (internals)
Named graph on entity: `@NamedEntityGraph(name="Order.withLines", attributeNodes=@NamedAttributeNode("lines"))`. Repository: `@EntityGraph("Order.withLines") List<Order> findByCustomerId(Long id);`. Dynamic: `EntityGraph<Order> g = em.createEntityGraph(Order.class); g.addAttributeNodes("lines", "customer");` pass as hint to query.

#### When to use / when NOT to use
Multiple read use cases same aggregate different depths — named + dynamic graphs. Single hot path — explicit JPQL `join fetch` clearer in code review. Graph on wrong aggregate root — still N+1 on nested paths without subgraph.

#### Production example
Order API: `findById` uses graph `order-summary` (customer only); `findForFulfillment` uses dynamic graph adding lines + inventory subgraph — same entity, no EAGER on mapping. Query count regression test per graph name in CI.

#### Common mistakes
Graph name typo — silent fallback to lazy N+1. `@EntityGraph` on `Page` without fetch join limit — duplicates with Page sort. Assuming graph applies to write operations — load only.

#### Interview follow-ups (with model answers)

**Q:** Entity graph vs `@SqlResultSetMapping`?
**A:** Graph loads managed entities with planned associations — ORM lifecycle applies. SqlResultSetMapping/DTO projection read-only flat rows — better for read-heavy list screens. Graph when need entity mutation in same TX; projection for API response.

**Q:** Subgraphs?
**A:** `@NamedSubgraph` on nested association fetch plan — `lines` subgraph includes `product` node. Dynamic API: `g.addSubgraph("lines").addAttributeNodes("product")`. Required for multi-level without fetching entire object graph.

#### Scenario probe

Developer added `@EntityGraph("Order.detail")` to paginated list — duplicate orders in page content, wrong total count.

**Model answer:** Join fetch + pagination known JPA issue — Hibernate may duplicate rows in result; use `@EntityGraph(type=LOAD)` with batch size instead of JOIN fetch mode, or projection query. Fix: separate count query; or `@EntityGraph` with `LOAD` fetch type (default) not `FETCH` join for Page queries per Spring Data docs.

---

### 58. Hibernate bytecode enhancement: lazy initialization without session.

**Short answer:** Build-time enhancement (`hibernate-enhance-maven-plugin`) weaves lazy field initialization, dirty tracking, and association management bytecode — enables lazy basic attribute loading without open session and reduces snapshot memory. Required for `@LazyToOne(LazyRelation.NO_PROXY)` patterns and optimal dirty checking at scale. Trade-off: build complexity, debugger confusion, must run enhancer in CI same as local.

#### What it is
Hibernate agent modifies entity bytecode at build time (preferred) or runtime `-javaagent` for features beyond standard JPA proxies.

#### How it works (internals)
Enhancer adds `$hibernate_read_*` methods loading fields on first access if session available; without session throws `LazyInitializationException` still unless no-proxy configured with active session elsewhere. Dirty tracking avoids full field snapshot compare on flush — faster for wide entities.

#### When to use / when NOT to use
Large entities with many nullable fields rarely read — enhancement + lazy basics. Small CRUD entities — skip enhancer simplicity. Already disabled OSIV and use DTOs — enhancement less critical but still helps flush performance.

#### Production example
Insurance `Policy` 200 fields, 10 read per request — enhancement lazy-loads only accessed fields; heap per request down 30% in load test. CI runs enhance goal before package; missing enhancement fails startup validation test comparing `@LazyGroup` behavior.

#### Common mistakes
Enhancement in IDE not run in CI — prod behaves differently. Expecting lazy basics without enhancement — fields eager loaded. Mixing enhanced and non-enhanced entities in same module — inconsistent behavior.

#### Interview follow-ups (with model answers)

**Q:** Enhancement vs standard JDK proxy?
**A:** JDK proxy only for interfaces; bytecode subclass for concrete entities. Enhancement goes further — inline lazy field access, bidirectional association management. Hibernate 6 enables enhancement by default in some Boot configs — verify `hibernate.enhancer.enabled`.

**Q:** Debugging enhanced entities?
**A:** Stack traces show synthetic methods — step-through harder. Reproduce issues with enhancement off in local profile comparing SQL. Document enhancer version locked to Hibernate ORM version.

#### Scenario probe

Local dev works; CI tests fail LazyInitializationException on same code — enhancement not run in test compile phase.

**Model answer:** Maven enhancer plugin bound to wrong phase — test classpath uses unenhanced classes. Fix plugin execution on `process-classes` and test dependency on enhanced output. Add assertion test verifying enhanced bytecode marker interface present. Align Boot parent Hibernate version with enhancer version.

#### Code / config (when useful)

```xml
<plugin>
  <groupId>org.hibernate.orm.tooling</groupId>
  <artifactId>hibernate-enhance-maven-plugin</artifactId>
  <executions><execution><goals><goal>enhance</goal></goals></execution></executions>
</plugin>
```

---

## Scenario-based interview drills

### S1. Order API p95 latency spike after Spring Boot upgrade

**Situation:** E-commerce `order-service` on Spring Boot 3 / Hibernate 6; `GET /api/orders` p95 jumps from 180ms to 2.1s after upgrade. APM shows 250+ JDBC calls per request. Team blames "Hibernate 6 regression." Pool size 20, Tomcat threads 200, `open-in-view: true`.

**What they're testing:** N+1 diagnosis, OSIV, fetch plans, production debugging without panic-refactoring.

**How to structure your answer:** Symptom → measure SQL count → identify lazy access pattern → short-term mitigation → durable fix → prevention.

**Model answer:** I would not roll back blindly. First, capture one trace and enable SQL logging in staging with the same dataset size. The pattern 1 + N strongly suggests lazy `@OneToMany` or `@ManyToOne` accessed during JSON serialization after the service method returns — OSIV keeps the session open, so the failure is architectural, not a Hibernate 6 bug. Confirm by setting `spring.jpa.open-in-view: false` in staging: the endpoint should fail fast with `LazyInitializationException`, pinpointing the layer (controller or mapper) touching associations. The durable fix is per-endpoint fetch strategy: `@EntityGraph`, `JOIN FETCH` in JPQL, or a DTO projection for list endpoints — never global EAGER. For `GET /orders`, I want one query with a join or a two-step batch fetch (`WHERE id IN (:ids)` + `@BatchSize`). Short-term mitigation: add `@BatchSize` on the child entity and cap page size. Long-term: ArchUnit rule forbidding entity return types from controllers on list APIs; CI assertion `assertThat(queryCount).isLessThan(5)` on integration test. I also verify indexes on foreign keys — missing indexes inflate join cost. Document in runbook: list endpoints return projections; detail endpoint may fetch graph intentionally inside `@Transactional` service.

**Common weak answers:** "Set everything to EAGER." "Increase pool to 200." "Hibernate 6 is broken — downgrade." No mention of query count or OSIV.

**Follow-up probes (with answers):**

**Q:** Would you keep OSIV enabled with a larger pool?
**A:** Only as a temporary bridge while migrating endpoints — not as the fix. OSIV ties connection hold time to HTTP latency including slow clients, multiplying pool demand under load. Larger pools mask the symptom until the database runs out of connections globally. The correct fix is fetch plans inside the service transaction boundary.

**Q:** How do you prevent regression?
**A:** Integration test with `Statistics` or datasource-proxy query counting per endpoint, plus code review rule: list APIs return DTOs. Optional P6Spy or `datasource-proxy` in staging continuously tracks query count dashboards.

---

### S2. Double charge on payment retry

**Situation:** Mobile clients retry `POST /payments` on timeout. Two pods process the same `Idempotency-Key` concurrently; customer charged twice. Payment provider supports idempotency but your service does not persist keys durably.

**What they're testing:** Idempotency, concurrency, saga boundaries, exactly-once semantics for side effects.

**How to structure your answer:** Root cause → correct idempotency store → concurrency control → provider alignment → observability.

**Model answer:** Duplicate charges mean the idempotency check was not atomic or not durable. I implement server-side idempotency with a unique constraint on `(tenant_id, idempotency_key)` in the payment service database — not an in-memory map. Flow: begin transaction, `INSERT INTO idempotency_record (key, request_hash, status) VALUES (...)` — duplicate key catches concurrent requests; one thread proceeds, the other waits or reads existing result. Alternatively `SELECT ... FOR UPDATE` on the key row before processing. Store response snapshot and return it for duplicates with same HTTP status. Processing and idempotency insert must be one transaction or use outbox ordering so crash mid-flight does not lose state. Align with payment gateway's own idempotency key forwarding. For Kafka consumers, separate `processed_events` table with `event_id` unique constraint in same TX as side effect. Alert on idempotency collision rate spike. Runbook: support searches by key, verifies single capture in provider dashboard. Never reuse keys across different amounts or endpoints.

**Common weak answers:** "Use Redis only." "Retry is client's problem." No mention of unique constraint or race between pods.

**Follow-up probes (with answers):**

**Q:** TTL for idempotency keys?
**A:** Typically 24–72 hours for HTTP POST — long enough for client retries and mobile background replay, short enough to limit table growth. Archive to cold storage if audit requires longer retention of outcomes, not necessarily the full request body.

---

### S3. Optimistic lock storm on hot inventory row

**Situation:** Flash sale on single SKU; `OptimisticLockException` rate 40% on `Product` entity. Service retries blindly, amplifying load. Stock oversell near zero.

**What they're testing:** Locking strategy, contention, atomic SQL, transaction length.

**How to structure your answer:** Why optimistic fails → pessimistic or atomic update → retry policy → UX → metrics.

**Model answer:** High contention on one row makes `@Version` optimistic locking a lottery — many transactions fail at flush with zero rows updated. For scarce inventory I switch to atomic SQL: `UPDATE stock SET qty = qty - :n WHERE sku = :sku AND qty >= :n` and check `rowsUpdated == 1`. Alternatively short `PESSIMISTIC_WRITE` transaction: load row `FOR UPDATE`, validate, decrement, commit in under 50ms — never hold lock across HTTP to payment. Retries must be exponential backoff with jitter and capped attempts; return 409 to client when sold out. Do not retry optimistic lock failures infinitely. Consider partitioning inventory per warehouse to shrink hot row. Measure `rowsUpdated` failures vs successes; dashboard on lock wait time if pessimistic. UX: show "only 2 left" from cached approximate stock but authoritative decrement at checkout only.

**Common weak answers:** "Add more `@Retry`." "Cache stock in Redis without invalidation." Long transactions with pessimistic locks.

**Follow-up probes (with answers):**

**Q:** Pessimistic vs atomic UPDATE?
**A:** Atomic UPDATE is often best for single-row decrement — one round-trip, no entity load, no version column needed. Pessimistic helps when multiple columns and business rules must be validated before write, but keep the transaction minimal.

---

### S4. Bulk JPQL update leaves stale L2 cache

**Situation:** Admin runs `@Modifying` query deactivating 50k promotions. API still shows active prices for 10 minutes. No errors in logs.

**What they're testing:** Bulk operations vs persistence context, second-level cache, query cache invalidation.

**How to structure your answer:** Bulk bypasses PC → stale entities in L1/L2 → eviction strategy → safer pattern.

**Model answer:** Bulk JPQL `executeUpdate` hits the database directly — managed entities in any open persistence context and second-level cache entries are not updated automatically. Hibernate does not magically refresh `Promotion` instances still in memory. Fix: `@Modifying(clearAutomatically = true, flushAutomatically = true)` on the repository method so subsequent reads in the same TX reload from DB. After bulk job, evict L2 region: `sessionFactory.getCache().evictEntityData(Promotion.class)` and evict query cache regions if `Promotion` queries were cached. If admin UI and API share L2 READ_WRITE, stale reads persist until eviction or TTL. For large batch jobs, consider disabling L2 for that entity during job or run job in maintenance window with cache clear endpoint. Long-term: treat bulk admin ops as separate pipeline publishing `PromotionDeactivated` events so read models and edge caches invalidate. Test: after bulk update, assert `findById` returns inactive without restart.

**Common weak answers:** "Restart pods." "JPA should auto-update cache." Only `clearAutomatically` without L2 eviction.

**Follow-up probes (with answers):**

**Q:** Does `@Version` increment on bulk update?
**A:** No — unless your JPQL explicitly sets `version = version + 1`. Subsequent optimistic updates on stale in-memory entities can behave unexpectedly; prefer `clearAutomatically` or avoid loading entities before bulk in same TX.

---

### S5. Multi-tenant data leak via missing filter

**Situation:** SaaS app uses Hibernate `@Filter` for `tenant_id`. New `ReportRepository` native query returns documents from all tenants. Security audit finding.

**What they're testing:** Multi-tenancy, `@Filter` vs explicit predicates, native SQL bypass.

**How to structure your answer:** How leak happened → defense in depth → test strategy → incident response.

**Model answer:** Hibernate `@Filter` applies only when enabled on the session and only to entity loads/HQL — native SQL bypasses it entirely unless you duplicate the predicate. Every repository path needs review: JPQL should include `tenantId` parameter from `TenantContext`; native queries must append `AND tenant_id = :tenantId` from trusted JWT claim, never from client body. Enable filter in a servlet filter or Spring `HandlerInterceptor` at request start: `session.enableFilter("tenantFilter").setParameter("tenantId", ctx.getId())`. Defense in depth: row-level security in Postgres optional for enterprise tier. Integration tests: create two tenants, assert cross-tenant `findById` returns empty. ArchUnit or custom lint on `@NativeQuery` without tenant parameter. For admin support "break glass", separate role disables filter with audit log. Incident: identify affected queries, notify customers per GDPR, rotate credentials if exports occurred.

**Common weak answers:** "Filters catch everything." "Only happens in dev." No native query mention.

**Follow-up probes (with answers):**

**Q:** `@TenantId` (Hibernate 6.2+) vs manual filter?
**A:** `@TenantId` auto-populates on insert and can simplify discriminator-style tenancy, but native SQL and JDBC still require explicit predicates — automatic tenant injection is not universal across all access paths.

---

### S6. Replication lag causes read-your-writes failure

**Situation:** User updates profile, immediate `GET` shows old email. Read replica routing via `@Transactional(readOnly=true)` on all queries.

**What they're testing:** Read replica routing, consistency guarantees, read-your-writes patterns.

**How to structure your answer:** Lag mechanism → user expectation → routing fix → document SLA.

**Model answer:** After write to primary, replica may lag milliseconds to seconds. If read-only transactions always route to replica, the user sees stale data immediately after their own mutation — classic read-your-writes violation. Fixes: route session's reads to primary for a short window after write (sticky token in cookie), or key reads by user id to primary for N seconds, or client polls until version matches. `Transactional(readOnly=true)` on class level is dangerous without nuanced router — split read services: `ProfileCommandService` writes primary, `ProfileQueryService` reads replica with `version` or `updatedAt` in response so client detects staleness. Document: "profile may take up to 5s to propagate." For financial balances after transfer, never use replica — primary only. Implementation: `AbstractRoutingDataSource` keys off `ThreadLocal` flag set after write in same request thread, or use Aurora writer endpoint for recent mutations.

**Common weak answers:** "Replicas are always consistent." "Turn off replicas." No UX or routing strategy.

**Follow-up probes (with answers):**

**Q:** Is `readOnly=true` enough for routing?
**A:** No — it is only a hint unless your routing datasource explicitly checks `TransactionSynchronizationManager.isCurrentTransactionReadOnly()`. You must implement the router and define exceptions for read-your-writes paths.

---

### S7. Flyway migration + Envers audit table drift

**Situation:** Deploy fails: Hibernate `ddl-auto=validate` reports `product_aud` missing column added to `product`. Developer changed entity only, Flyway script updated main table, forgot Envers audit table.

**What they're testing:** Schema discipline, Envers, validate mode, CI gates.

**How to structure your answer:** Validate caught it → Envers mirrors → migration checklist → CI.

**Model answer:** `@Audited` entities have companion `_AUD` tables mirroring audited columns plus `REV` and `REVTYPE`. Any column add/rename on `Product` requires parallel Flyway change on `product_aud` unless field marked `@NotAudited`. `ddl-auto=validate` in staging/prod catches mapping drift before bad deploy — keep it. Checklist on PR: entity diff → Flyway for base table → Flyway for audit table → update `@Audited` targets. CI: Testcontainers Postgres, Flyway migrate, Spring context start with `validate`. For high-churn tables, reconsider full auditing — audit only compliance fields. Envers schema is not auto-managed by Flyway unless you generate scripts from Hibernate schema tool in dev and review. Rollback plan: backward-compatible migrations only (add column nullable first).

**Common weak answers:** "Use ddl-auto=update in prod." "Disable Envers." Skip audit table in migration review.

**Follow-up probes (with answers):**

**Q:** Performance of auditing high-churn tables?
**A:** Each update doubles write volume to audit tables — partition or sample, audit only required fields, or use CDC to warehouse for analytics instead of Envers for hot paths.

---

### S8. StatelessSession bulk import OOM vs EntityManager

**Situation:** Nightly import of 2M rows via `saveAll` in loop OOMs heap at 600k rows. Job must finish in 30 minutes.

**What they're testing:** Persistence context memory, batching, StatelessSession, JDBC alternatives.

**How to structure your answer:** Why PC grows → flush/clear → batch settings → StatelessSession/COPY → outcome.

**Model answer:** Each `persist` adds entity to persistence context with snapshot for dirty checking — without `flush()` and `clear()` every chunk, memory grows linearly with row count. First tuning: `hibernate.jdbc.batch_size=50`, `order_inserts=true`, SEQUENCE not IDENTITY, loop with `if (i % 50 == 0) { em.flush(); em.clear(); }`. If still too slow or memory heavy, `StatelessSession` from `SessionFactory`: no first-level cache, no cascade — explicit `insert` per row, still batch JDBC. For Postgres million-row loads, `COPY` via `PgConnection` or Spring Batch `JdbcBatchItemWriter` may beat ORM entirely. Monitor GC and row throughput; single long transaction bloats undo logs — commit every 10k rows. Validate duplicate handling and error row quarantine. Never use `findAll` on staging table.

**Common weak answers:** "Increase heap to 32GB." "Parallel streams on saveAll." IDENTITY keys with batching expectations.

**Follow-up probes (with answers):**

**Q:** When is ORM wrong for import?
**A:** When you do not need managed entities, associations, or dirty checking — plain JDBC, COPY, or bulk loader tools are faster and predictable. ORM import is for moderate volume with domain validation per row.

---

### S9. Pessimistic lock deadlock between order and payment

**Situation:** Deadlocks between services updating `account` and `order` tables in different lock order. Postgres logs show cyclic waits.

**What they're testing:** Deadlock avoidance, lock ordering, transaction scope, distributed vs local locks.

**How to structure your answer:** Local deadlock → consistent ordering → shorten TX → retry → avoid cross-service locks.

**Model answer:** Within one service, always acquire pessimistic locks in deterministic order — e.g., lower `account_id` first. Enable `hibernate.order_updates=true` so flush batches updates by PK. Keep transactions short: never call payment HTTP inside a transaction holding `FOR UPDATE` on account rows. Cross-service "locks" are not real locks — sagas with compensations instead of locking remote state. On `deadlock detected`, retry idempotent operation with jitter, max 3 attempts. Analyze `pg_locks` and deadlock graphs; fix code paths that lock parent then child in one TX and child then parent in another. Consider splitting hot row — wallet per currency. Alert on deadlock rate; runbook documents retry-safe endpoints.

**Common weak answers:** "Use distributed Redis lock everywhere." Long TX with external calls. No lock ordering convention.

**Follow-up probes (with answers):**

**Q:** Does optimistic locking prevent deadlocks?
**A:** It reduces row lock hold time but does not eliminate deadlocks if you still use `FOR UPDATE`. It changes failure mode to optimistic lock exception instead of deadlock.

---

### S10. Senior design review: new marketplace listing API

**Situation:** Team proposes returning full `Listing` entity with lazy `images`, `seller`, `reviews` from new `@RestController`. Expected 5k RPS read traffic.

**What they're testing:** Holistic JPA mental model, boundaries, projections, caching, operability.

**How to structure your answer:** Requirements → TX boundary → query design → cache → failure modes → checklist.

**Model answer:** I reject returning entities at 5k RPS. Define `ListingCardDto` with fields the mobile app needs; repository method with JPQL constructor expression or interface projection — one query, maybe join seller name only. Transaction on service method read-only, `open-in-view: false`. If images are S3 URLs, store URLs in listing table or join single `primary_image` — do not lazy-load 20 images per row. For hot SKUs, READ_ONLY L2 or Caffeine cache with TTL + Kafka invalidation on `ListingUpdated`. Pagination via keyset on `id`, not offset 10000. Indexes on filter columns. Load test in CI: p95 < 100ms, < 5 queries. Document consistency: search index eventual. Security: no lazy traversal exposing internal associations. This is the senior mental model: ORM inside TX, DTOs outside, SQL measured, cache explicit, DB enforces invariants.

**Common weak answers:** "Spring Data makes it easy — return entity." OSIV + EAGER all associations. No load test or query budget.

**Follow-up probes (with answers):**

**Q:** When would you use entity graph on this API?
**A:** Only on a detail endpoint with low QPS where the client truly needs a bounded graph — still inside service TX, with explicit path and query count test. Not on list/card endpoints.

---
