# Hibernate / JPA — 50 Senior Interview Questions

**Bar:** Persistence context, flush, dirty checking, N+1, locking, caching. "I use Spring Data" is not enough.

---

### 1. Session vs EntityManager vs persistence context.

**Short answer:** JPA's `EntityManager` is the standard API; Hibernate's `Session` extends it. The persistence context (PC) is the first-level cache, identity map, and dirty-checking arena for one unit of work — typically aligned with a single database transaction in Spring.

#### What it is
The persistence context is where managed entities live between load and flush/commit. It ensures one Java object instance per database row within a unit of work.

#### How it works (internals)
`EntityManager` delegates to Hibernate `Session` internally. PC stores entities by id (identity map). `EntityManager.clear()` detaches all. In Spring `@Transactional`, the PC usually opens at TX begin and closes at commit/rollback.

#### When to use / when NOT to use
Inject `EntityManager`/`@PersistenceContext` in domain services when you need explicit control. Prefer repositories for simple CRUD. Avoid long-lived PC (OSIV abuse).

#### Production example
Order placement TX: load `Order`, add lines, flush at commit — one PC, one connection from Hikari for TX duration.

#### Common mistakes
Confusing Hibernate SessionFactory singleton with Session per TX; assuming PC spans multiple DBs; mixing `EntityManager` from two persistence units.

#### Interview follow-ups
- What is `PersistenceContextType.TRANSACTION` vs `EXTENDED`?
- How does Spring bind EM to thread?
- Difference `merge` identity in PC?

---

### 2. Entity states: transient, persistent, detached, removed.

**Short answer:** Transient entities are new with no persistent identity. Persistent entities are managed in the PC. Detached entities have identity but aren't managed. Removed entities are scheduled for deletion at flush.

#### What it is
JPA entity lifecycle states governing what operations are legal and how changes propagate to SQL.

#### How it works (internals)
`persist()` makes transient → persistent. `remove()` on managed → removed. Commit/close/detach → detached. `merge()` copies detached state into a managed instance — **always use the return value**. Accessing lazy associations on detached entities causes `LazyInitializationException`.

#### When to use / when NOT to use
Keep work inside one TX with small aggregates. Don't pass entities to the web layer — map to DTOs before detach.

#### Production example
REST client sends `OrderDto`; service loads managed `Order`, applies changes, commits — never merge client-provided detached graph blindly.

#### Common mistakes
Treating returned `merge()` reference as optional; `remove()` on detached without merge first; serializing entities to JSON then merging entire graph.

#### Interview follow-ups
- State diagram with operations?
- `EntityNotFoundException` on getReference?
- Spring Data `save()` state detection?

---

### 3. How does dirty checking work?

**Short answer:** Hibernate tracks entity changes by comparing current field values to a snapshot taken at load (or via bytecode enhancement). At flush, dirty fields generate UPDATE statements — entities you didn't call `save()` on still update.

#### What it is
Automatic change detection eliminating manual UPDATE calls for managed entities.

#### How it works (internals)
Default: snapshot per entity at load — memory cost. Bytecode enhancement tracks dirty flags on field access — lower memory, build-time plugin. `@DynamicUpdate` generates SQL updating only changed columns but still requires dirty detection.

#### When to use / when NOT to use
Rely on dirty checking in normal OLTP flows. Use bulk JPQL updates when you intentionally bypass PC. Enable enhancement on large domain models if profiling shows snapshot pressure.

#### Production example
Load `Customer`, set `email`, commit — Hibernate emits `UPDATE customer SET email=? WHERE id=?` without explicit save.

#### Common mistakes
Thinking `save()` is required for updates; modifying detached entity expecting auto-update; `@DynamicUpdate` misunderstood as skipping dirty check.

#### Interview follow-ups
- Enhancement vs snapshot trade-offs?
- Interaction with immutables?
- Dirty checking cost at scale?

---

### 4. Flush modes.

**Short answer:** Flush synchronizes persistence context to the database. `AUTO` (default) flushes before queries that might see stale data and at commit. `COMMIT` delays until commit — can read stale self-data. Unexpected flush mid-TX can cause deadlocks.

#### What it is
`FlushModeType` controlling when pending SQL is sent to the database within a transaction.

#### How it works (internals)
`AUTO`: before JPQL/Criteria that could conflict; at commit. `COMMIT`: only at commit — performance micro-optimization with consistency risk. `MANUAL`: explicit `flush()`. Hibernate `ALWAYS` flushes before every query — rarely used.

#### When to use / when NOT to use
Stay on AUTO unless measured need. COMMIT only with clear understanding of stale reads in same TX. Manual flush before native query needing visible writes.

#### Production example
Bulk insert loop with periodic `flush()` + `clear()` every 500 rows to avoid PC memory blow-up — still AUTO mode with explicit batch flush.

#### Common mistakes
Assuming `find()` never triggers flush (AUTO may flush first); flush before lock query causing write ordering deadlock.

#### Interview follow-ups
- `FlushModeType` per query hint?
- Relationship flush order FK constraints?
- `saveAndFlush` vs commit?

---

### 5. `persist` vs `merge` vs `save` (Hibernate) vs `save` (Spring Data).

**Short answer:** `persist` attaches new entities. `merge` reattaches detached state into a managed copy — use the returned instance. Spring Data `save()` chooses persist or merge heuristically — can cause extra SELECTs and broken collection merging.

#### What it is
Different API entry points for making entity state persistent, with subtly different semantics.

#### How it works (internals)
`persist`: illegal on detached (exception). `merge`: detached → managed copy; collections may replace by reference. Hibernate legacy `save`: may assign id before insert depending on generator. Spring Data `save`: `isNew()` detection via `Persistable`, `@Version`, or id null checks.

#### When to use / when NOT to use
Explicit `persist`/`merge` in domain services when graphs are complex. Spring Data `save` fine for simple aggregates. Never merge DTO-detached graphs with orphan collection surprises.

#### Production example
Create order: `em.persist(order)` with cascade on lines. Update from API: load managed entity, mutate fields — avoid merge entirely.

#### Common mistakes
Ignoring `merge` return value; `save()` on entity with null id but existing natural key; cascade merge pulling entire object graph.

#### Interview follow-ups
- Implement `Persistable` for assigned ids?
- `merge` and orphanRemoval interaction?
- `persist` on entity with generated id already set?

---

### 6. ID generation: IDENTITY vs SEQUENCE vs UUID.

**Short answer:** `IDENTITY` triggers insert-before-id-known — breaks JDBC batching. `SEQUENCE` with enhanced optimizers enables batch inserts. UUID avoids coordination but hurts B-tree locality unless time-ordered (UUIDv7).

#### What it is
Primary key generation strategy affecting insert performance, portability, and indexing.

#### How it works (internals)
`GenerationType.IDENTITY`: DB autoincrement — Hibernate can't batch inserts easily. `SEQUENCE`: `pooled`/`pooled-lo` optimizers reduce sequence roundtrips. UUID: `@UuidGenerator` or application-assigned; random UUIDs fragment indexes.

#### When to use / when NOT to use
SEQUENCE (or Postgres serial alternatives) for OLTP bulk inserts. UUID for distributed id generation without DB roundtrip — prefer UUIDv7 for index locality. IDENTITY acceptable at low volume.

#### Production example
Postgres orders table: `SEQUENCE` + `hibernate.jdbc.batch_size=50` + `order_inserts=true`. Public API exposes UUIDv7 as external id.

#### Common mistakes
IDENTITY with batch settings wondering why no batching; sharing sequence across high-insert tables causing contention.

#### Interview follow-ups
- `TABLE` generator why avoid?
- Hi/lo algorithm legacy?
- Composite keys `@EmbeddedId`?

#### Code / config (when useful)
```yaml
spring.jpa.properties.hibernate.jdbc.batch_size: 50
spring.jpa.properties.hibernate.order_inserts: true
```

---

### 7. Equals/hashCode for entities.

**Short answer:** Don't use database id in equals/hashCode before persist — id may be null or 0. Use stable business key, or identity (`==`) only within persistence context. Lombok `@Data` on entities breaks lazy loading and sets.

#### What it is
Correct equality semantics for JPA entities in collections and ORM identity map consistency.

#### How it works (internals)
Hibernate uses identity map — same id same instance in PC. `HashSet` of entities uses hashCode — changing id after persist breaks set contract. Business key (email, SKU) safe if immutable and unique.

#### When to use / when NOT to use
Business key equals for entities with natural keys. Id-based equals only in DTOs. Never include lazy collections in `toString`/`equals`.

#### Production example
`Product` equals by `sku` field; id assigned after insert doesn't change equals contract.

#### Common mistakes
Lombok `@EqualsAndHashCode(of = "id")` on new entities in sets; calling `hashCode()` triggering lazy load.

#### Interview follow-ups
- Hibernate `==` vs `equals` in PC?
- Equals for `@Embeddable` value types?
- Set of detached entities?

---

### 8. Associations: `mappedBy`, owning side.

**Short answer:** The owning side owns the foreign key or join table and is what Hibernate writes. `mappedBy` marks the inverse side. Bidirectional associations need sync helpers — updating only inverse side doesn't change FK.

#### What it is
JPA relationship mapping determining which entity's mapping controls database schema updates.

#### How it works (internals)
`@OneToMany(mappedBy="order")` — `OrderLine.order` owns FK. `@JoinColumn` on `@ManyToOne` side typically owns. Hibernate flush order respects FK dependencies.

#### When to use / when NOT to use
Prefer unidirectional `@ManyToOne` when you don't need parent→children navigation in domain. Bidirectional with `addLine()`/`removeLine()` helpers maintaining both sides.

#### Production example
```java
public void addLine(OrderLine line) {
    lines.add(line);
    line.setOrder(this);
}
```

#### Common mistakes
Setting only `order.getLines().add(line)` without `line.setOrder(this)` — FK null in DB.

#### Interview follow-ups
- `@JoinColumn` on both sides?
- Unidirectional `@OneToMany` with join table?
- Cascade direction best practice?

---

### 9. `CascadeType` vs orphanRemoval.

**Short answer:** Cascade propagates persist/merge/remove operations along associations. `orphanRemoval=true` deletes child rows when removed from parent's collection. `CascadeType.ALL` on large graphs can delete more than intended.

#### What it is
Rules for lifecycle operations propagating across entity relationships.

#### How it works (internals)
`CascadeType.PERSIST/MERGE/REMOVE/REFRESH/DETACH`. `orphanRemoval`: child no longer referenced by parent → DELETE. Distinct from `REMOVE` cascade on parent delete. Don't cascade from child to parent.

#### When to use / when NOT to use
Cascade PERSIST on composition (`Order` → `OrderLine`). orphanRemoval for true composition. Avoid ALL on `@ManyToMany`.

#### Production example
Remove line from order collection with orphanRemoval — line row deleted at flush. Parent order delete cascades remove lines.

#### Common mistakes
orphanRemoval with DTO merge replacing collection — accidental mass delete; cascade MERGE on `@ManyToOne` parent.

#### Interview follow-ups
- orphanRemoval vs `@OnDelete`?
- Cascade and `@OneToOne` optional?
- Soft delete vs orphanRemoval?

---

### 10. FetchType EAGER vs LAZY.

**Short answer:** EAGER loads associations immediately — global fetch plan you can't tune per use case. Default lazy for collections; `@ManyToOne` EAGER was common historically — still causes N+1. Explicit fetch per query wins.

#### What it is
JPA fetch strategy controlling when associated data is loaded from database.

#### How it works (internals)
LAZY: proxy or bytecode-enhanced lazy field until access. EAGER: join or secondary select at load time. Hibernate ignores global EAGER change without bytecode enhancement for field access in some cases.

#### When to use / when NOT to use
Default LAZY on collections always. Fetch join, entity graph, or batch size per use case. Never EAGER as blanket N+1 "fix."

#### Production example
`@ManyToOne(fetch=LAZY)` on `Order.customer`; checkout flow uses `@EntityGraph` loading customer name only via projection.

#### Common mistakes
EAGER on `@OneToMany` causing cartesian products; JSON serialization triggering lazy loads.

#### Interview follow-ups
- Hibernate `@LazyToOne`?
- Fetch profile?
- EAGER + `@BatchSize` interaction?

---

### 11. N+1: how you see it and how you kill it.

**Short answer:** One query for parents plus N queries for each child id — visible in SQL logs and Hibernate statistics. Fix with join fetch (watch cartesian product), `@EntityGraph`, `@BatchSize`, subselect fetch, or DTO projections — not global EAGER.

#### What it is
Performance anti-pattern where lazy associations trigger one SELECT per row in a loop or serialization.

#### How it works (internals)
Detect: `hibernate.generate_statistics=true`, datasource-proxy, p6spy. Fixes ranked: projection query best for read APIs; `@EntityGraph` for entity returns; `JOIN FETCH` for controlled graphs; `@BatchSize(size=20)` batches lazy loads into fewer IN queries.

#### When to use / when NOT to use
Measure first. Join fetch two bags — failure (multiple bag fetch exception). Two queries often beat one giant join.

#### Production example
List 100 orders: query 1 paginated ids; query 2 `WHERE order_id IN (...)` fetch lines — 2 queries total.

#### Common mistakes
Enabling EAGER globally; join fetch + Pageable broken pagination; ignoring N+1 in reporting jobs.

#### Interview follow-ups
- `@Fetch(SUBSELECT)` vs BATCH?
- Blaze-Persistence entity views?
- N+1 in GraphQL resolvers?

---

### 12. Multiple bags fetch exception.

**Short answer:** Hibernate cannot simultaneously JOIN FETCH two `List` collections without Cartesian product explosion — throws `MultipleBagFetchException` or causes memory blow-up.

#### What it is
Limitation of bag (`List`) semantics with multiple join fetch in one query.

#### How it works (internals)
Two bags multiply rows (10 lines × 10 payments = 100 rows per order). Hibernate 5+ refuses multiple bag fetch. `Set` avoids duplicate row issue but still cartesian risk.

#### When to use / when NOT to use
Use `Set` for uniqueness, or fetch collections in separate queries, or `@BatchSize`. `@OrderColumn` lists are not bags but have other costs.

#### Production example
Order with lines and payments: `@EntityGraph` one association + batch size on the other, or two sequential queries by order ids.

#### Common mistakes
Adding `distinct` thinking it fixes cartesian hydration cost; Hibernate 6 behavior differences untested.

#### Interview follow-ups
- List vs Set domain modeling?
- `@SqlRestriction` on collections?
- Multiple `@OneToMany` redesign?

---

### 13. Cartesian product with join fetch.

**Short answer:** Join fetching multiple collections multiplies result set rows — Hibernate hydrates duplicate parent entities (deduped in memory) but DB and network work still scales with product of child counts.

#### What it is
Relational join explosion when fetching multiple to-many associations in one SQL statement.

#### How it works (internals)
SQL returns M×N rows; Hibernate builds object graph with deduplication by id. Pagination (`setFirstResult`) with join fetch applies limit in memory in some cases — **broken pagination**.

#### When to use / when NOT to use
Paginate ids first, then fetch graph by id list. Prefer DTO queries for read models over entity join fetch at scale.

#### Production example
Admin order search: page 20 order ids sorted by date; second query fetch lines for those 20 ids only.

#### Common mistakes
`JOIN FETCH` on list endpoint with Pageable returning wrong counts; assuming `distinct` in JPQL fixes DB work.

#### Interview follow-ups
- Hibernate 6 DISTINCT semantics?
- Window functions for pagination?
- Read model denormalization?

---

### 14. `@OneToMany` default is lazy bag. Why `List` vs `Set` vs `@OrderColumn`?

**Short answer:** Bag (`List` without order column) allows duplicates, no index column. `List` + `@OrderColumn` maintains order with extra writable column. `Set` requires consistent equals/hashCode — no duplicate children.

#### What it is
Collection type choice affecting SQL shape, semantics, and Hibernate fetch behavior.

#### How it works (internals)
Bag: simple one-to-many FK on child table. `@OrderColumn`: position column updated on reorder — insert overhead. `Set`: typically no duplicates; may use join table or FK depending on mapping.

#### When to use / when NOT to use
Ordered lines: `List` with `@OrderBy("lineNumber")` often sufficient vs `@OrderColumn`. Set when uniqueness matters (tags). Avoid many-to-many bags.

#### Production example
Order lines as `List` ordered by `lineNumber` column — business order preserved without `@OrderColumn` fragility.

#### Common mistakes
`@OrderColumn` on large collections causing update storms on insert; HashSet with mutable entity equals bugs.

#### Interview follow-ups
- `@SortNatural`?
- Immutable collections mapping?
- Collection replacement vs diff?

---

### 15. `@ManyToMany` — why seniors avoid it.

**Short answer:** Pure many-to-many join table can't store relationship attributes (`assigned_at`, `role_expiry`). Cascades and fetch plans become footguns. Model an explicit join entity instead.

#### What it is
JPA shortcut mapping for many-to-many via join table without entity representing the association.

#### How it works (internals)
Hidden join table; both sides can map with `mappedBy`. Adding columns requires migration to entity anyway. Cascade ALL can delete unexpected join rows.

#### When to use / when NOT to use
Avoid in domain models. Use `UserRole`, `ProductCategory` entities with payload columns and explicit lifecycle.

#### Production example
Users and roles: `UserRole` entity with `userId`, `roleId`, `grantedAt`, `grantedBy` — queryable and auditable.

#### Common mistakes
ManyToMany cascade REMOVE wiping join data; unindexed join table full scan on authorization check.

#### Interview follow-ups
- Unidirectional ManyToMany?
- Replace with composite key entity?
- GraphQL many-to-many exposure?

---

### 16. Inheritance: SINGLE_TABLE vs JOINED vs TABLE_PER_CLASS.

**Short answer:** SINGLE_TABLE: one table, discriminator, nullable subtype columns — fast reads, wide sparse table. JOINED: normalized, joins per query. TABLE_PER_CLASS: union queries, poor polymorphic performance. Prefer composition over deep entity inheritance.

#### What it is
JPA strategies mapping class hierarchies to relational schema.

#### How it works (internals)
`SINGLE_TABLE`: `@DiscriminatorColumn`. JOINED: base + subclass tables. TABLE_PER_CLASS: each concrete class full table — polymorphic query unions all tables.

#### When to use / when NOT to use
SINGLE_TABLE for shallow hierarchy, few subtype fields. JOINED when normalization matters. Avoid TABLE_PER_CLASS. Often `@Embeddable` or `@MappedSuperclass` beats inheritance.

#### Production example
Payment types refactored from JOINED inheritance to `Payment` table with `type` enum + optional detail JSON column — simpler queries.

#### Common mistakes
Deep inheritance trees; discriminator string typos; querying root entity scanning huge single table.

#### Interview follow-ups
- `@MappedSuperclass` vs entity inheritance?
- Polymorphic `@Query` pitfalls?
- Hibernate `@DiscriminatorFormula`?

---

### 17. `@Embeddable` vs entity.

**Short answer:** Embeddables are value objects without identity — owned by parent entity, mapped to same table (typically). Good for Money, Address. No shared mutable embeddable instances across entities.

#### What it is
JPA composition mapping for types without standalone lifecycle.

#### How it works (internals)
Columns flattened into parent table (default) or `@AssociationOverride`. Equals by value. `@Embedded` on entity field. Cannot be queried as root entity (JPQL limitation without path).

#### When to use / when NOT to use
Money (`amount`, `currency`), Address, DateRange. Not for types needing independent repository.

#### Production example
```java
@Embeddable
public record Money(BigDecimal amount, Currency currency) {}
@Embedded private Money total;
```

#### Common mistakes
Mutating shared Address instance attached to two customers; null embeddable vs empty embeddable confusion.

#### Interview follow-ups
- `@AttributeOverride` column names?
- Embeddable collections?
- JSON embeddable mapping?

---

### 18. Second-level cache.

**Short answer:** Shared cache across persistence contexts/sessions — Ehcache, Infinispan, Redis (custom). Cache entities and collections with strict concurrency strategy. Best for read-mostly reference data; dangerous for frequently updated financial data without discipline.

#### What it is
Optional Hibernate cache region above the first-level PC, reducing DB reads for shared data.

#### How it works (internals)
`@Cache(usage = READ_WRITE)` entity regions; collection cache stores element ids. Invalidation on update. Cluster: invalidation vs replication latency. Requires `@EnableCaching` + JCache provider configuration.

#### When to use / when NOT to use
Countries, product categories, config tables. Not default for transactional hot entities. TTL + event invalidation for semi-static data.

#### Production example
Product metadata cached READ_ONLY; price changes `@CacheEvict` via Spring cache layer on admin service — dual cache layers need clear ownership.

#### Common mistakes
Caching entities with lazy unloaded collections; stale prices in cluster without invalidation; READ_ONLY on mutable data.

#### Interview follow-ups
- Query cache vs entity cache?
- `@NaturalId` cache?
- Redis as L2 provider trade-offs?

---

### 19. Query cache.

**Short answer:** Caches query result **identifiers**, not full entities — still hits entity cache/DB for hydration. Easy to make slower than no cache. Rarely enabled globally for good reason.

#### What it is
Hibernate cache storing mapping from query key + params to list of entity ids at a timestamp.

#### How it works (internals)
Invalidated when any table in query space updates (timestamp regions). Requires `@Cacheable` on query + global enable. Stale if invalidation misconfigured.

#### When to use / when NOT to use
Extremely stable repeated queries on reference data. Prefer explicit application cache with clear TTL for most cases.

#### Production example
Disabled after benchmark showed cache admin overhead exceeded savings on frequently updated catalog.

#### Common mistakes
Enabling query cache without entity cache; expecting cache to skip DB entirely.

#### Interview follow-ups
- `@QueryHints` CACHEABLE?
- Hibernate 6 query cache changes?
- vs Spring `@Cacheable` on repository?

---

### 20. Optimistic locking `@Version`.

**Short answer:** Version column in UPDATE WHERE clause — zero rows updated means concurrent modification → `OptimisticLockException`. Prevents silent lost updates. Expose version to clients via ETag/If-Match.

#### What it is
Lock-free concurrency control detecting conflicting writes at commit time.

#### How it works (internals)
`@Version` Long/Timestamp incremented on each successful update. JPA spec requires version check on merge/update. Retry or user conflict resolution on failure.

#### When to use / when NOT to use
Default for most OLTP entities with concurrent edits. Not for high-contention inventory without retry strategy — may need pessimistic or domain reservation.

#### Production example
PUT `/orders/{id}` requires `If-Match: "3"` matching `@Version`; 412 on conflict with current state payload.

#### Common mistakes
No version on hot entities; client never sends version — last write wins despite `@Version` if merge bypasses; bulk update skipping version increment.

#### Interview follow-ups
- `@OptimisticLocking` type TIMESTAMP?
- Retry with exponential backoff?
- Version on `@Embeddable`?

---

### 21. Pessimistic locking.

**Short answer:** `LockModeType.PESSIMISTIC_WRITE` maps to `SELECT FOR UPDATE` — holds row lock until TX ends. Use for scarce resources (inventory, seats), not every read. Configure lock timeout; expect deadlocks.

#### What it is
Database-level row locking via JPA lock modes on find/query.

#### How it works (internals)
`PESSIMISTIC_READ/WRITE`, `UPGRADE`, `PESSIMISTIC_FORCE_INCREMENT`. Timeout via `javax.persistence.lock.timeout` hint. DB-specific: NOWAIT, SKIP LOCKED for worker queues.

#### When to use / when NOT to use
Short TX reserving inventory row. SKIP LOCKED for job claiming. Not for report queries — blocks writers.

#### Production example
```java
@Lock(LockModeType.PESSIMISTIC_WRITE)
@Query("select i from Inventory i where i.sku = :sku")
Optional<Inventory> lockBySku(String sku);
```

#### Common mistakes
Long TX holding pessimistic lock; lock without index — table lock escalation; default infinite wait.

#### Interview follow-ups
- Pessimistic vs optimistic choice matrix?
- Oracle vs Postgres lock behavior?
- `@NamedEntityGraph` with lock?

---

### 22. `@Lock` vs DB isolation.

**Short answer:** Transaction isolation controls what rows/versions you **see**; explicit locks control who can **modify** rows. Repeatable read doesn't replace `FOR UPDATE` for inventory reservation.

#### What it is
Distinction between MVCC snapshot isolation and explicit row-level write locks.

#### How it works (internals)
Isolation prevents dirty reads; phantom behavior DB-dependent. `@Lock` issues SQL lock clauses independent of isolation level semantics. Serializable reduces anomalies but increases aborts.

#### When to use / when NOT to use
Combine READ COMMITTED + `@Version` for many apps. Pessimistic lock when business requires exclusive access to row during decision.

#### Production example
Transfer between accounts: pessimistic lock both rows in consistent id order to prevent deadlock.

#### Common mistakes
Assuming `@Transactional` isolation SERIALIZABLE fixes all race conditions; ignoring phantom inserts in inventory counts.

#### Interview follow-ups
- Snapshot isolation vs serializable?
- Lock ordering deadlock prevention?
- `@Formula` fields and locking?

---

### 23. Native queries and entities.

**Short answer:** Native SQL returning entities must include all mapped columns or use `@SqlResultSetMapping`. Schema-coupled and brittle — prefer JPQL/Criteria unless you need DB-specific features.

#### What it is
Executing raw SQL through JPA/Hibernate with optional entity mapping.

#### How it works (internals)
`createNativeQuery(sql, Entity.class)` requires column aliases matching mappings. `@SqlResultSetMapping` + `@EntityResult` for complex shapes. Hibernate 6 improved ad-hoc mapping.

#### When to use / when NOT to use
Window functions, CTEs, vendor hints, bulk reporting. DTO native for read-only reports. Not for portable CRUD.

#### Production example
Postgres `UPDATE ... RETURNING` native query mapping to DTO interface for upsert response.

#### Common mistakes
Partial column list silent wrong data; native query bypasses `@Where` soft delete filter.

#### Interview follow-ups
- `@NamedNativeQuery` maintenance?
- ResultSet mapping to constructor?
- Schema migration breaking natives?

---

### 24. JPQL vs Criteria vs Querydsl vs Spec.

**Short answer:** JPQL strings — simple, runtime errors. Criteria API — verbose type-safe. Querydsl/JOOQ — better complex dynamic SQL. Spring Data Specifications — composable predicates for repositories.

#### What it is
Query authoring options from strings to type-safe builders.

#### How it works (internals)
Criteria `CriteriaBuilder` predicates compile to JPQL. Specifications `toPredicate(Root, Query, CB)`. Never concatenate user input into JPQL — SQL injection via JPQL parameters still required.

#### When to use / when NOT to use
JPQL `@Query` for stable queries. Specifications for optional admin filters. Blaze-Persistence for advanced DTO queries on Hibernate.

#### Production example
Admin order search: `Specification` combining date range, status, customer id — reused in repository `findAll(spec, pageable)`.

#### Common mistakes
Dynamic JPQL string concat from request params; Criteria unreadable mega-methods.

#### Interview follow-ups
- Hibernate 6 Criteria changes?
- Type-safe query generators?
- Specification AND/OR composition?

---

### 25. Pagination: `Pageable` count query cost.

**Short answer:** `Page` runs data query plus `count(*)` — count often more expensive than page data on large tables. Use `Slice` when total unnecessary; keyset pagination for deep pages.

#### What it is
Spring Data pagination abstractions over JPA `setFirstResult/setMaxResults`.

#### How it works (internals)
`SimpleJpaRepository` derives count query from method — can be slow without matching indexes. Offset pagination degrades on large offsets (`OFFSET 1000000`).

#### When to use / when NOT to use
`Slice` for infinite scroll. Keyset (`WHERE id > :cursor ORDER BY id LIMIT 20`) for large datasets. Covering indexes on sort columns.

#### Production example
Order history UI uses cursor pagination by `(created_at, id)` tuple — stable under concurrent inserts.

#### Common mistakes
Count query on every scroll page; join fetch + Pageable returning wrong page size; missing index on ORDER BY column.

#### Interview follow-ups
- `@Query countQuery separate optimization?
- Hibernate `@PageableDefault`?
- Blaze-Pagination?

#### Code / config (when useful)
```java
Page<OrderSummary> findByCustomerId(Long customerId, Pageable pageable);
Slice<OrderSummary> findRecent(Pageable pageable);
```
