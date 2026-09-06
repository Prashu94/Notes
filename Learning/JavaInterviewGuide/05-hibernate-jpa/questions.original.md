# Hibernate / JPA — 50 Senior Interview Questions

**Bar:** Persistence context, flush, dirty checking, N+1, locking, caching. "I use Spring Data" is not enough.

---

### 1. Session vs EntityManager vs persistence context.

**Short answer:** `EntityManager` is the JPA facade; Hibernate's `Session` extends the same contract. The persistence context (PC) is the in-memory scope where entities are managed — identity map, dirty checking, and lazy proxies. In Spring, one thread-bound `EntityManager` per transaction is the norm.

#### What it is
JPA standardizes persistence via `EntityManager`; Hibernate implements it with `Session`. The persistence context is not a separate API object you hold — it is the logical first-level cache and lifecycle manager behind the `EntityManager`. Spring's `SharedEntityManagerCreator` wraps a container-managed `EntityManager` that delegates to the underlying Hibernate `Session`.

#### How it works (internals)
When a transaction starts, Spring binds an `EntityManager` to the thread (`TransactionSynchronizationManager`). `em.find()` loads entities into the PC keyed by `(entityType, id)`. Subsequent loads in the same TX return the same instance (identity guarantee). `em.clear()` evicts the PC; `em.detach()` removes one entity. Hibernate's `Session` adds methods like `save`, `update`, `getReference` — prefer JPA APIs in portable code.

#### When to use / when NOT to use
Use `EntityManager`/`@PersistenceContext` when you need explicit control: bulk operations, `getReference` for FK-only inserts, native queries with entity results. Avoid injecting `Session` unless you need Hibernate-specific APIs. Do not create multiple PCs per request without understanding isolation.

#### Production example
An order placement service runs in `@Transactional`. `OrderRepository.save()` and `em.find(Customer.class, id)` share the same PC — updating the customer address on the loaded instance is flushed at commit without an explicit `save()` on Customer if the association is managed.

#### Common mistakes
Confusing `EntityManager` (API) with persistence context (state); opening a new `EntityManager` per query in non-Spring code and losing identity; calling `em.close()` in managed environments; assuming `@Transactional(readOnly=true)` clears the PC (it does not).

#### Interview follow-ups
- What is the difference between `EntityManagerFactory` and `EntityManager`?
- How does Open Session In View extend the PC lifecycle?
- Is the PC the same as the first-level cache?

#### Code / config (when useful)
```java
@Service
public class OrderService {
    @PersistenceContext
    private EntityManager em;

    @Transactional
    public void placeOrder(Long customerId) {
        Customer c = em.find(Customer.class, customerId);
        Order o = new Order(c);
        em.persist(o); // same PC, same TX
    }
}
```

---

### 2. Entity states: transient, persistent, detached, removed.

**Short answer:** Transient entities are new with no persistent identity. Persistent entities are managed in the PC. Detached entities have identity but are outside the PC. Removed entities are scheduled for DELETE at flush. State transitions are driven by `persist`, `merge`, `remove`, `clear`, and transaction boundaries.

#### What it is
JPA defines four entity lifecycle states. Understanding them explains why `merge` returns a different instance, why lazy collections fail after commit, and why `save` in Spring Data sometimes issues extra SELECTs.

#### How it works (internals)
`persist(entity)` — transient → persistent; INSERT at flush. `remove(entity)` — persistent → removed; DELETE at flush. Transaction commit/rollback or `em.clear()` — persistent → detached. `merge(detached)` — copies state onto a managed copy (or loads existing); detached instance stays detached. Hibernate tracks state in `EntityEntry` (status: MANAGED, DELETED, etc.).

#### When to use / when NOT to use
Design services so entities entering the TX are transient (create) or loaded inside the TX (update). Avoid passing detached entities across REST boundaries without DTOs. Use `merge` only when reattaching detached graphs is intentional.

#### Production example
A PUT endpoint receives `OrderDto` with `orderId`. Loading `em.find(Order.class, id)` inside the TX is safer than mapping DTO → detached `Order` and calling `repository.save()`, which may `merge` and mishandle collection orphans.

#### Common mistakes
Using the argument of `merge` after the call (still detached); assuming `save` always persists (Spring Data merges when `isNew` is false); treating removed entities as deleted in DB before flush; serializing persistent entities to JSON inside a TX (lazy surprises).

#### Interview follow-ups
- What happens to a detached entity's lazy collection?
- Difference between `em.remove` and `DELETE` JPQL?
- How does `Persistable` affect Spring Data `save`?

#### Code / config (when useful)
```java
Order o = new Order();           // TRANSIENT
em.persist(o);                   // PERSISTENT
em.detach(o);                    // DETACHED
Order managed = em.merge(o);       // o still DETACHED; managed is PERSISTENT
em.remove(managed);              // REMOVED (DELETE on flush)
```

---

### 3. How does dirty checking work?

**Short answer:** Hibernate tracks managed entity field changes and generates UPDATE statements at flush time without explicit `save`. It compares current state to a snapshot taken at load (or uses bytecode-enhanced dirty tracking). Only changed columns are included unless `@DynamicUpdate` is off.

#### What it is
Dirty checking is automatic change detection for persistent entities. It is the reason you can `find` an entity, mutate a setter, and commit — no `repository.save()` required in a transactional service.

#### How it works (internals)
On load, Hibernate stores a snapshot (array of field values) in `EntityEntry`. At flush, `DefaultFlushEntityEventListener` compares snapshot to current state field-by-field. Changed fields populate the UPDATE SET clause. With bytecode enhancement (`enableLazyInitialization`, `enableDirtyTracking`), Hibernate can track dirty flags on the entity itself, avoiding snapshot memory. Collections are dirty-tracked separately; replacing a collection reference vs modifying in place matters.

#### When to use / when NOT to use
Rely on dirty checking for in-TX updates of managed entities. Use explicit `save`/`merge` when entities are detached. Enable `@DynamicUpdate` on wide tables (audit columns, large VARCHAR) to shrink UPDATE statements. Do not depend on dirty checking across transaction boundaries.

#### Production example
`CustomerService.updateEmail(id, email)` loads the customer, calls `setEmail`, returns. One `UPDATE customer SET email=? WHERE id=?` at commit. With `@DynamicUpdate` on `Customer`, unchanged columns are omitted — important for Oracle row chaining and trigger-heavy tables.

#### Common mistakes
Mutating a detached entity and expecting DB update; modifying entities after `em.clear()`; assuming `readOnly=true` prevents flush (it sets flush mode but loaded entities can still flush on commit in some configs); using `field` access with inconsistent getter side effects.

#### Interview follow-ups
- Does dirty checking run on every query or only at flush?
- How do embeddables participate in dirty checking?
- Impact of `FlushMode.COMMIT` on dirty checking visibility?

#### Code / config (when useful)
```java
@Entity
@DynamicUpdate
public class Customer {
    @Id private Long id;
    private String email;
    // setEmail() on managed instance → dirty at flush
}
```

---

### 4. Flush modes.

**Short answer:** Flush synchronizes the persistence context to the database. `AUTO` (default) flushes before queries that need fresh data and at commit. `COMMIT` delays flush until commit. `MANUAL` requires explicit `flush()`. Wrong flush timing causes stale reads, surprise UPDATEs mid-request, or constraint violations late in the TX.

#### What it is
Flush mode controls when pending INSERT/UPDATE/DELETE statements execute. Flush is not commit — you can flush without committing, but commit always flushes.

#### How it works (internals)
`FlushModeType.AUTO`: before JPQL/Criteria that might conflict with PC state; at transaction commit. Hibernate may flush before native queries depending on settings. `COMMIT`: only at TX end — same-TX queries can return stale DB rows while PC has newer state. `MANUAL`: developer calls `em.flush()`. `FlushMode.ALWAYS` flushes before every query (rare, performance hit). Spring `@Transactional(readOnly=true)` sets `FlushMode.MANUAL` on the Session to reduce writes.

#### When to use / when NOT to use
Stay on AUTO for most OLTP services. Use COMMIT sparingly when you understand stale-read trade-offs inside long transactions. MANUAL for bulk ETL steps where you flush in batches. Never mix unaware native queries with unflushed PC changes.

#### Production example
Batch import: `for (item : items) { em.persist(item); if (++i % 50 == 0) em.flush(); em.clear(); }` — MANUAL-style batching with periodic flush/clear to avoid huge PC memory.

#### Common mistakes
Assuming `flush()` commits; running a native `SELECT` expecting to see unflushed inserts; `AUTO` flush before a validation query triggering premature FK violations; deadlocks from flush reordering under concurrent updates.

#### Interview follow-ups
- Difference between `flush()` and `saveAndFlush()`?
- How does flush interact with IDENTITY generators?
- What is `FlushModeType` default in read-only transactions?

#### Code / config (when useful)
```java
em.setFlushMode(FlushModeType.COMMIT);
em.persist(order);
// JPQL may not see order until commit
```

---

### 5. `persist` vs `merge` vs `save` (Hibernate) vs `save` (Spring Data).

**Short answer:** `persist` attaches a new entity and throws if detached. `merge` copies detached state into the PC and returns the managed instance. Hibernate `save` is legacy (saveOrUpdate semantics). Spring Data `save` calls `persist` or `merge` based on `isNew()` — convenient but can hide extra SELECTs and collection merge bugs.

#### What it is
These APIs are the main entry points for persisting object graphs. Confusing them causes duplicate rows, lost updates, and orphan collection issues.

#### How it works (internals)
`em.persist(x)`: x must be transient; becomes persistent; INSERT at flush; returns void. `em.merge(x)`: x can be detached; loads or copies into managed entity; returns managed copy; x unchanged. Hibernate `session.save()`: assigns identifier early depending on generator; prefer `persist` in JPA. Spring `SimpleJpaRepository.save`: `entityInformation.isNew(entity)` → `em.persist` else `em.merge`. Override with `Persistable.getId()` or `@Version` null checks.

#### When to use / when NOT to use
Use `persist` for creates inside the TX. Use `merge` when reattaching a detached graph is unavoidable. Prefer loading + mutate for updates. Avoid Spring `save` for partial updates on detached DTO-mapped entities — use dedicated queries or load-merge intentionally.

#### Production example
Creating an order: `em.persist(new Order(...))`. Receiving a detached `Product` from a cache layer: `Product managed = em.merge(cachedProduct)` — always use the return value for further associations.

#### Common mistakes
Ignoring `merge` return value; `save` on entity with id=0 treated as new on some DBs; merging entities with `LAZY` collections initialized to empty (wipes DB children); calling `persist` on detached entity (`EntityExistsException`).

#### Interview follow-ups
- How does `saveAll` differ from repeated `save`?
- What is `EntityManager.getReference` vs `merge`?
- Custom `isNew` with `AbstractAggregateRoot`?

#### Code / config (when useful)
```java
// WRONG
Order detached = dtoMapper.toEntity(dto);
repository.save(detached); // merge — may orphan line items

// BETTER
Order order = repository.findById(dto.getId()).orElseThrow();
dtoMapper.updateEntity(dto, order);
```

---

### 6. ID generation: IDENTITY vs SEQUENCE vs UUID.

**Short answer:** `IDENTITY` delegates to DB auto-increment — simple but disables JDBC batch inserts until Hibernate 5+/dialect fixes. `SEQUENCE` with pooled optimizer (`pooled-lo`) scales on Oracle/Postgres. UUID avoids coordination but hurts B-tree locality unless time-ordered (UUIDv7). Pick per table traffic and sharding needs.

#### What it is
Primary key generation strategy affects insert performance, batching, replication, and index fragmentation.

#### How it works (internals)
`GenerationType.IDENTITY`: Hibernate must execute INSERT immediately to read id — breaks batching unless `hibernate.jdbc.batch_versioned_data` and dialect support insert-delayed id retrieval. `SEQUENCE`: separate `nextval` call; `allocationSize` must match optimizer (`pooled-lo` recommended); misconfigured `allocationSize=1` causes round-trip per row. `UUID`: `@GeneratedValue` with generator or `@UuidGenerator`; stored as CHAR(36) or native `uuid` type in Postgres.

#### When to use / when NOT to use
IDENTITY for low-volume tables, simplicity on MySQL/SQL Server. SEQUENCE for Oracle enterprise OLTP with batch inserts. UUID for public APIs, offline clients, multi-region writes without a central id broker. Avoid random UUID as clustered PK on huge Postgres tables without BRIN/partitioning strategy.

#### Production example
Postgres order table: `@SequenceGenerator(name="ord_seq", sequenceName="order_seq", allocationSize=50)` with `pooled-lo`. Event outbox table: UUIDv7 for roughly time-ordered inserts and safe consumer dedup.

#### Common mistakes
`allocationSize=50` in JPA but sequence `INCREMENT BY 1` in DB (gaps and errors); assuming IDs are gapless; exposing sequential IDs publicly (enumeration attacks); IDENTITY + `saveAll` wondering why batching is off.

#### Interview follow-ups
- What is `hibernate.id.new_generator_mappings`?
- Table generator vs sequence on Oracle?
- How does `@GeneratedValue(strategy=AUTO)` pick?

#### Code / config (when useful)
```java
@Id
@GeneratedValue(strategy = GenerationType.SEQUENCE, generator = "order_gen")
@SequenceGenerator(name = "order_gen", sequenceName = "order_seq", allocationSize = 50)
private Long id;
```

---

### 7. Equals/hashCode for entities.

**Short answer:** Never use database-generated id in `equals`/`hashCode` before persist — id can be null or change. Use a stable business key, or accept identity (`==`) within a persistence context. Broken equals breaks `Set` associations and second-level cache keys.

#### What it is
Entities are reference types with lifecycle-dependent identity. `equals`/`hashCode` must align with how you use them in collections and caches.

#### How it works (internals)
Hibernate does not require overriding `equals`/`hashCode`. For entities in a `Set` mapping, equals must be consistent with DB uniqueness. Lombok `@Data` generates `equals`/`hashCode` including all fields — triggers lazy loads and `LazyInitializationException`. Common pattern: business key (`tenantId + code`) if immutable; or Hibernate class + id when id is assigned and non-null.

#### When to use / when NOT to use
Override when entities go in `HashSet`/`HashMap` or dedup logic. Do not override with `getId()` alone if id is null pre-flush. For DTOs and records, use natural value equality. Inside one PC, reference equality often suffices.

#### Production example
`Product` keyed by `(sku, tenantId)` in a `Set<Channel>` mapping — equals/hashCode on those two fields only, never on lazy `categories` collection.

#### Common mistakes
Lombok `@EqualsAndHashCode` on `@Entity`; including `@OneToMany` in equals; using `instanceof` across inheritance hierarchies with SINGLE_TABLE; changing hashCode after insert into a `HashSet`.

#### Interview follow-ups
- Should equals be symmetric for Hibernate proxies?
- How does Envers handle equals?
- Difference between entity and embeddable equals?

#### Code / config (when useful)
```java
@Override
public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Product p)) return false;
    return sku != null && sku.equals(p.sku) && tenantId.equals(p.tenantId);
}
```

---

### 8. Associations: `mappedBy`, owning side.

**Short answer:** The owning side has the foreign key column and is what you persist to update the relationship. `mappedBy` marks the inverse side — updates ignored unless you sync both sides or rely on owning side only. Always set the owning side in code.

#### What it is
Bidirectional associations split responsibility: one side maps the FK (`@JoinColumn`, `@ManyToOne`), the other references it with `mappedBy`.

#### How it works (internals)
`@ManyToOne` is always owning (FK in child table). `@OneToMany(mappedBy="order")` is inverse — Hibernate ignores FK changes from inverse only. `mappedBy` value is the field name on the owning entity. Unidirectional `@OneToMany` without `mappedBy` uses join table or FK column (avoid FK in child via `@JoinColumn` on OneToMany — breaks portability). Synchronizing both sides in domain methods (`order.addLine(line)`) prevents inconsistent object graphs.

#### When to use / when NOT to use
Prefer unidirectional `@ManyToOne` when you never navigate parent → children in domain. Bidirectional when aggregate behavior requires it — maintain sync helpers. Owning side is source of truth for FK writes.

#### Production example
`Order` ↔ `OrderLine`: `OrderLine.order` is `@ManyToOne` owning; `Order.lines` is `@OneToMany(mappedBy="order")`. `order.addLine(line)` sets `line.setOrder(this)` and adds to list — FK written on flush.

#### Common mistakes
Updating only inverse side; `mappedBy` typo; mixing `@JoinColumn` on both sides; cascade PERSIST from parent without setting child owning reference.

#### Interview follow-ups
- Can you have bidirectional `@ManyToMany`?
- What SQL does unidirectional `@OneToMany` generate?
- How does `orphanRemoval` interact with owning side?

#### Code / config (when useful)
```java
public void addLine(OrderLine line) {
    lines.add(line);
    line.setOrder(this); // owning side
}
```

---

### 9. `CascadeType` vs orphanRemoval.

**Short answer:** Cascade propagates persistence operations to associated entities (`PERSIST`, `MERGE`, `REMOVE`, etc.). `orphanRemoval=true` deletes children removed from the parent's collection when the parent is managed. They solve different problems — cascade is not orphan removal.

#### What it is
Cascade defines which operations flow across association boundaries. Orphan removal deletes rows when the association link is broken in the object model.

#### How it works (internals)
`CascadeType.PERSIST`: `em.persist(parent)` persists children. `REMOVE`: deleting parent deletes children (dangerous on `@ManyToOne`). `MERGE`: merges entire graph. `orphanRemoval`: when child is removed from `@OneToMany` collection or parent deleted, child row deleted at flush — only for `@OneToMany`/`@OneToOne` with single-valued. Replacing collection reference without orphanRemoval leaves old rows (FK null or orphan depending on mapping).

#### When to use / when NOT to use
`CascadeType.PERSIST` on parent→children composition (order lines). `orphanRemoval` when children have no meaning without parent. Never cascade `REMOVE` to `@ManyToOne` shared references (Product on many OrderLines). Avoid `CascadeType.ALL` lazily — explicit cascades document intent.

#### Production example
`Order` with `lines`: `cascade = PERSIST, MERGE`, `orphanRemoval = true`. Removing a line from `order.getLines()` schedules DELETE for that line at flush.

#### Common mistakes
Expecting orphanRemoval when clearing and re-adding collection (can DELETE all then INSERT); cascade MERGE wiping children; `REMOVE` cascade deleting shared `Category`; orphanRemoval on `@ManyToMany`.

#### Interview follow-ups
- Difference between `DELETE` JPQL and `REMOVE` cascade?
- Does `orphanRemoval` work on detached collections?
- Safe cascade for aggregate roots in DDD?

#### Code / config (when useful)
```java
@OneToMany(mappedBy = "order", cascade = CascadeType.PERSIST, orphanRemoval = true)
private List<OrderLine> lines = new ArrayList<>();
```

---

### 10. FetchType EAGER vs LAZY.

**Short answer:** `LAZY` loads associations on first access (proxy or batch). `EAGER` loads with the owner — often via join or secondary select. Default: `@ManyToOne` EAGER, `@OneToMany` LAZY. Prefer LAZY everywhere and fetch explicitly in queries; EAGER on collections causes Cartesian products and surprise queries.

#### What it is
Fetch type defines when associated data is loaded relative to the owner entity. It is a hint overridden by fetch joins in JPQL.

#### How it works (internals)
`LAZY`: Hibernate returns proxy (`PersistentCollection` for collections) — initializes on access inside open Session. `EAGER`: `select` fetch (N+1) or `join` fetch depending on `hibernate.enable_lazy_load_no_trans` and mapping. `@ManyToOne(fetch=EAGER)` is JPA default — senior teams set `LAZY` globally via `hibernate.default_lazy=true` or bytecode enhancement. `FetchType` on field is static; dynamic fetching uses entity graphs or JOIN FETCH.

#### When to use / when NOT to use
Default LAZY; use `JOIN FETCH` or `@EntityGraph` per use case. EAGER only for tiny, always-needed associations (rare). Never EAGER on large collections. For read models, use projections instead of tuning fetch types.

#### Production example
`Order` with lazy `lines`: list endpoint uses `SELECT o FROM Order o JOIN FETCH o.lines WHERE o.customerId = :id` — one query, no LazyInitializationException, no global EAGER.

#### Common mistakes
`EAGER` on `@OneToMany`; JSON serialization touching lazy fields outside TX; assuming `FetchType.LAZY` on `@ManyToOne` without changing default; `OpenEntityManagerInView` masking design problems.

#### Interview follow-ups
- Can you make `@ManyToOne` lazy in JPA without Hibernate property?
- What is `FetchMode` vs `FetchType` in Hibernate?
- How do `@EntityGraph` attribute paths work?

#### Code / config (when useful)
```java
@ManyToOne(fetch = FetchType.LAZY)
@JoinColumn(name = "customer_id")
private Customer customer;
```

---

<!-- BATCH_2 -->
