# Microservices — 50 Senior Interview Questions

**Bar:** Boundaries, data ownership, failure, consistency. "We use Kubernetes" is not a microservice.

---

### 1. When should you *not* split a monolith?

**Short answer:** Do not split when the domain is still fuzzy, the team is small (<8 engineers), operational maturity is low, or the workflow is inherently one transactional unit with heavy cross-entity joins. Microservices multiply failure modes, deployment overhead, and coordination cost. Split when you have a clear bounded context, a team ready to own runtime + data, and a concrete pain (deploy cadence, scale, blast radius) that boundaries solve. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
A **monolith** is one deployable with in-process calls and usually one database. **Microservices** are independently deployable services with explicit integration and **data ownership**. The decision is organizational and architectural — not a Kubernetes checkbox. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate.

#### How it works (internals)
Splitting introduces network hops, partial failures, distributed tracing needs, contract testing, and independent schema evolution. You trade compile-time coupling for runtime coupling. Without clear boundaries, you get a **distributed monolith**: same entanglement, worse latency. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Split when | Stay monolith when |
|------------|-------------------|
| Team can own service + DB + on-call | One team owns everything anyway |
| Different scale profiles (search vs checkout) | All paths scale together |
| Clear bounded context (payments vs catalog) | Model changes weekly across "services" |
| Need independent deploy after CI maturity | No automated tests, no observability |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
A 12-person startup runs a Spring Boot monolith with modules (`order`, `catalog`, `billing`). They defer extraction until billing needs PCI isolation and a dedicated 4-person team. They extract `payment-service` with its own Postgres schema — not three services because someone read a blog post. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Splitting along technical layers (`user-dao-service`, `user-api-service`).
- "We'll share one database temporarily" — temporary lasts years.
- Measuring success by service count instead of deploy frequency and incident blast radius.
- No strangler plan: big-bang rewrite while features stall.

#### Interview follow-ups (with model answers)

**Q:** What signals tell you a boundary is wrong?
**A:** 'What signals tell you a boundary is wrong' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. A **monolith** is one deployable with in-process calls and usually one database. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How would you strangler-extract the first service?
**A:** 'How would you strangler-extract the first service' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. A **monolith** is one deployable with in-process calls and usually one database. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What ops prerequisites do you need before service #2?
**A:** Senior answer to 'What ops prerequisites do you need before service #2': tie to ownership, timeouts, and observable failure modes. A **monolith** is one deployable with in-process calls and usually one database. A 12-person startup runs a Spring Boot monolith with modules (`order`, `catalog`, `billing`). Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving when should you *not* split a monolith? shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. Do not split when the domain is still fuzzy, the team is small (<8 engineers), operational maturity is low, or the workflow is inherently one transactional unit with heavy cross-entity joins. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. A 12-person startup runs a Spring Boot monolith with modules (`order`, `catalog`, `billing`).

---

### 2. Bounded context vs service vs module.

**Short answer:** A **bounded context** is a linguistic and model boundary (ubiquitous language, invariants). A **module** is a compile-time package boundary inside one deployable. A **service** is a deployable runtime unit that owns its data and release cadence. You can — and often should — model multiple contexts as modules in a monolith before promoting one to a service.

#### What it is
From DDD: contexts define **what terms mean** (`Order` in fulfillment vs `Order` in billing). Modules enforce **encapsulation** via packages and package-private APIs. Services add **network, versioning, and operational ownership**. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate.

#### How it works (internals)
In a modular monolith, `catalog` module exposes `CatalogFacade`; `order` calls it in-process. When extracted, the facade becomes an HTTP/gRPC client; the **context boundary** stays the same — only the integration mechanism changes. Confusion arises when teams draw service lines on org charts instead of domain language. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Construct | Use for |
|-----------|---------|
| Bounded context | Modeling workshops, API/event design |
| Module | Enforcing dependencies in one repo (`archunit` rules) |
| Service | Independent deploy, scale, failure domain, team ownership |

Do not create a service per entity (`CustomerService`, `AddressService`) unless each has distinct lifecycle and team.

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
E-commerce: `Pricing` context computes discounts; `Checkout` context totals the cart. Both live in one repo as Gradle modules with ArchUnit forbidding `checkout → pricing` except through `PricingPort`. Later, `pricing-service` ships with Kafka events `PriceListUpdated` — same boundary, new transport. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Renaming packages to microservices without changing data ownership.
- One giant "shared-kernel" module everyone depends on.
- Service boundaries that split a single aggregate across two databases.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you discover bounded contexts in a legacy monolith?
**A:** 'How do you discover bounded contexts in a legacy monolith' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. From DDD: contexts define **what terms mean** (`Order` in fulfillment vs `Order` in billing). Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Can two contexts share one database schema?
**A:** 'Can two contexts share one database schema' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. From DDD: contexts define **what terms mean** (`Order` in fulfillment vs `Order` in billing). Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What is an anti-corruption layer and when do you need it?
**A:** Senior answer to 'What is an anti-corruption layer and when do you need it': tie to ownership, timeouts, and observable failure modes. From DDD: contexts define **what terms mean** (`Order` in fulfillment vs `Order` in billing). E-commerce: `Pricing` context computes discounts; `Checkout` context totals the cart. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving bounded context vs service vs module. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **bounded context** is a linguistic and model boundary (ubiquitous language, invariants). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. E-commerce: `Pricing` context computes discounts; `Checkout` context totals the cart.

#### Code / config (when useful)

```java
// Modular monolith — only cross-module via port
package com.shop.checkout;

public interface PricingPort {
    Money applyDiscounts(Cart cart);
}
```

---

### 3. Data ownership: the rule that matters.

**Short answer:** Each piece of mutable data has **one writer** — one service owns the schema and all writes. Other services read via that service's API or events, never by querying its database. Shared writable tables are the fastest path to inconsistent state and undeployable coupling. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
**Data ownership** means the owning team controls schema migrations, backup/restore, retention, and consistency guarantees for that data. Consumers hold **derived copies** or call synchronously — they do not become co-owners. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
When Service B writes to Service A's table, deploy order matters: A's migration can break B. Transactions cannot span services cleanly. Reporting needs **CQRS projections** or an analytics pipeline — not cross-service SQL joins in production OLTP paths. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| OK | Not OK |
|----|--------|
| Read replica of **your** service's DB for reporting | Service B INSERT into Service A's `orders` |
| Event-sourced read models you own | "Shared library" that writes to common tables |
| Cached copy with TTL and invalidation | Dual writes to two DBs without outbox |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`inventory-service` owns `stock_levels`. `order-service` reserves stock via `POST /reservations` (sync) or publishes `OrderPlaced` consumed by inventory (async). Warehouse dashboard reads from `inventory_read_model` fed by CDC — not live joins to `order_db`. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Read-only access to another service's DB "just for reporting" that becomes write paths via triggers.
- Passing primary keys across services as if schemas are stable forever.
- No deletion/retention story — GDPR requests become archaeology.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you handle reporting across services?
**A:** Senior answer to 'How do you handle reporting across services': tie to ownership, timeouts, and observable failure modes. **Data ownership** means the owning team controls schema migrations, backup/restore, retention, and consistency guarantees for that data. `inventory-service` owns `stock_levels`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What breaks when two services share a Mongo collection?
**A:** Senior answer to 'What breaks when two services share a Mongo collection': tie to ownership, timeouts, and observable failure modes. **Data ownership** means the owning team controls schema migrations, backup/restore, retention, and consistency guarantees for that data. `inventory-service` owns `stock_levels`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you migrate ownership from monolith table to new service?
**A:** 'How do you migrate ownership from monolith table to new service' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. **Data ownership** means the owning team controls schema migrations, backup/restore, retention, and consistency guarantees for that data. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving data ownership: the rule that matters. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. Each piece of mutable data has **one writer** — one service owns the schema and all writes. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `inventory-service` owns `stock_levels`.

---

### 4. Synchronous vs asynchronous integration.

**Short answer:** **Synchronous** (HTTP/gRPC) couples caller and callee in time: you need an answer now, and failures propagate as errors to the user. **Asynchronous** (message bus) decouples in time: publish facts, consumers react later; UX becomes eventual unless you add polling/WebSockets. Use sync for queries and commit decisions the user waits on; use async for side effects and cross-context notifications. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Sync: request/response, timeouts, retries with care. Async: topics/queues, at-least-once delivery, consumer groups, dead-letter queues. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Sync chains latency: p99_total ≈ sum(p99_i). Circuit breakers and bulkheads limit cascade. Async adds **ordering**, **duplication**, and **lag** concerns; consumers must be idempotent. Hybrid is common: HTTP creates order, Kafka notifies fulfillment and analytics.

#### When to use / when NOT to use
| Sync | Async |
|------|-------|
| "Is this SKU in stock?" now | Send email, update search index |
| Payment authorization | Notify 5 downstream systems |
| Strong UX: show error immediately | Peak buffering (Black Friday) |

Avoid sync call chains deeper than 2–3 hops for user-facing paths.

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Checkout: `order-service` calls `payment-service` synchronously (user sees decline). On success, publishes `OrderPaid` to Kafka; `shipping`, `loyalty`, and `data-warehouse` consumers process independently. If email consumer is down, order still completes. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Kafka as a synchronous RPC bus with request-reply hacks everywhere.
- No timeout on HTTP client — threads pile up during outage.
- Fire-and-forget async without monitoring consumer lag.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you show order status when fulfillment is async?
**A:** Senior answer to 'How do you show order status when fulfillment is async': tie to ownership, timeouts, and observable failure modes. Sync: request/response, timeouts, retries with care. Checkout: `order-service` calls `payment-service` synchronously (user sees decline). Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Sync vs async for saga steps?
**A:** For 'Sync vs async for saga steps': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Sync chains latency: p99_total ≈ sum(p99_i). Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What happens when the message broker is slower than HTTP?
**A:** Senior answer to 'What happens when the message broker is slower than HTTP': tie to ownership, timeouts, and observable failure modes. Sync: request/response, timeouts, retries with care. Checkout: `order-service` calls `payment-service` synchronously (user sees decline). Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving synchronous vs asynchronous integration. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Synchronous** (HTTP/gRPC) couples caller and callee in time: you need an answer now, and failures propagate as errors to the user. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Checkout: `order-service` calls `payment-service` synchronously (user sees decline).

---

### 5. Orchestration vs choreography.

**Short answer:** **Orchestration** uses a central coordinator that tells each service what to do next — visible process, easier debugging, single place for timeouts/compensation. **Choreography** has services react to events without a central brain — loose coupling, but hard to answer "where is order #12345?". Production systems often **hybrid**: orchestrate the money path, choreograph notifications. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Orchestrator: saga manager, Temporal/Camunda workflow, or dedicated `order-orchestrator` service. Choreography: `OrderPlaced` → inventory reserves → `StockReserved` → payment captures. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Orchestration stores workflow state (step, correlation ID, deadlines). Failures trigger compensating commands. Choreography relies on event contracts; a missing event stalls the flow silently unless you build **process monitoring** from event logs. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Orchestration | Choreography |
|---------------|--------------|
| Strict ordering, compensations, SLAs | Simple fan-out side effects |
| Regulated audit trail | Few steps, stable contracts |
| Many branches / human tasks | Team wants zero coordinator SPOF |

Pure choreography for 8-step checkout becomes "event soup."

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`order-saga` (Temporal workflow) calls payment and inventory activities with retries. On payment failure, runs `ReleaseReservation`. Meanwhile, `OrderPaid` events trigger choreographed email and analytics — no orchestrator needed there. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Hidden orchestration in the API gateway (untestable business logic).
- Choreography without correlation IDs or saga timeout sweeps.
- Two orchestrators for the same business process.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you debug a stuck choreography?
**A:** For 'How do you debug a stuck choreography': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Orchestration stores workflow state (step, correlation ID, deadlines). Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Temporal vs hand-rolled saga table?
**A:** For 'Temporal vs hand-rolled saga table': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Orchestration stores workflow state (step, correlation ID, deadlines). Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Who owns the orchestrator team?
**A:** For 'Who owns the orchestrator team': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Orchestration stores workflow state (step, correlation ID, deadlines). Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving orchestration vs choreography. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Orchestration** uses a central coordinator that tells each service what to do next — visible process, easier debugging, single place for timeouts/compensation. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `order-saga` (Temporal workflow) calls payment and inventory activities with retries.

---

### 6. Saga: compensation is not rollback.

**Short answer:** In a distributed saga there is no global `ROLLBACK`. Each step commits locally; **compensating transactions** are new business operations that undo or offset prior effects (refund, release reservation, cancel shipment). Compensations can fail, arrive late, or run twice — design them **idempotent** and operable from support tools. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
A **saga** is a sequence of local transactions with defined forward and compensating actions. Patterns: orchestrated (central) or choreographed (events). The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Forward: `CreateOrder` → `ReserveStock` → `ChargeCard` → `Ship`. Failure after charge triggers `Refund` + `ReleaseStock`. State machine tracks `COMPENSATING`. Unlike 2PC, intermediate states are visible — users may see "payment taken, fulfillment pending."

#### When to use / when NOT to use
Use sagas for multi-service business processes that cannot be one DB transaction. Do not use sagas when a single monolith transaction suffices — you are paying complexity tax. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Payment captured but warehouse API times out. Saga marks order `FULFILLMENT_FAILED`, runs `RefundPayment` with idempotency key `order-9f2-refund`. Support UI shows compensation status; alerts if refund stuck > 15 minutes. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Treating compensation as `DELETE FROM orders` — refunds are financial events with audit.
- No idempotency on compensate — double refund.
- Compensating out of order (release stock before cancel payment).
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** What is the pivot transaction in a saga?
**A:** For 'What is the pivot transaction in a saga': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Forward: `CreateOrder` → `ReserveStock` → `ChargeCard` → `Ship`. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you test compensation paths?
**A:** For 'How do you test compensation paths': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Forward: `CreateOrder` → `ReserveStock` → `ChargeCard` → `Ship`. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What do you show the customer mid-saga?
**A:** For 'What do you show the customer mid-saga': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Forward: `CreateOrder` → `ReserveStock` → `ChargeCard` → `Ship`. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving saga: compensation is not rollback. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. In a distributed saga there is no global `ROLLBACK`. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Payment captured but warehouse API times out.

#### Code / config (when useful)

```java
// Compensating action — idempotent refund
public RefundResult refund(String orderId, String idempotencyKey) {
    return paymentClient.refund(orderId, idempotencyKey); // 409 = already refunded → success
}
```

---

### 7. 2PC / XA across services.

**Short answer:** **Two-phase commit (2PC/XA)** across microservices is almost always the wrong tool: blocking locks, coordinator failure modes, poor latency, and fragile heuristics when a participant crashes. Industry practice is **sagas + outbox** for cross-service consistency, and ordinary local transactions inside each service. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
2PC: prepare phase (all vote commit) → commit phase. XA ties JDBC + JMS resources in one global transaction — rare in cloud-native stacks. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
During prepare, resources hold locks. If coordinator dies, participants block until timeout/recovery. HTTP services are not XA participants. Kubernetes pods make lock duration unpredictable.

#### When to use / when NOT to use
| Acceptable | Avoid |
|------------|-------|
| Single service, single DB transaction | Payment + inventory + shipping in one XA |
| Some legacy mainframe bridges | "Strong consistency everywhere" default |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Team considered XA between `order-db` and IBM MQ; p99 checkout latency doubled and stuck transactions required DBA intervention weekly. Replaced with outbox → Kafka + saga; incidents dropped. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Confusing "I need consistency" with "I need 2PC."
- XA in Spring `@Transactional` across DB + broker without understanding recovery.
- Interview answer "we use eventual consistency" without naming the business tolerance.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** What consistency does the business actually need for checkout?
**A:** Senior answer to 'What consistency does the business actually need for checkout': tie to ownership, timeouts, and observable failure modes. 2PC: prepare phase (all vote commit) → commit phase. Team considered XA between `order-db` and IBM MQ; p99 checkout latency doubled and stuck transactions required DBA intervention weekly. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How does outbox differ from 2PC guarantees?
**A:** Senior answer to 'How does outbox differ from 2PC guarantees': tie to ownership, timeouts, and observable failure modes. 2PC: prepare phase (all vote commit) → commit phase. Team considered XA between `order-db` and IBM MQ; p99 checkout latency doubled and stuck transactions required DBA intervention weekly. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** When is single-service local transaction enough?
**A:** Senior answer to 'When is single-service local transaction enough': tie to ownership, timeouts, and observable failure modes. 2PC: prepare phase (all vote commit) → commit phase. Team considered XA between `order-db` and IBM MQ; p99 checkout latency doubled and stuck transactions required DBA intervention weekly. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving 2pc / xa across services. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Two-phase commit (2PC/XA)** across microservices is almost always the wrong tool: blocking locks, coordinator failure modes, poor latency, and fragile heuristics when a participant crashes. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Team considered XA between `order-db` and IBM MQ; p99 checkout latency doubled and stuck transactions required DBA intervention weekly.

---

### 8. Idempotency keys.

**Short answer:** An **idempotency key** (client-supplied or server-generated) lets a service recognize duplicate requests and return the same outcome without double-charging or double-shipping. Essential for retries, at-least-once messaging, and mobile clients that tap "Pay" twice. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Typically a UUID sent in header (`Idempotency-Key`) or body; stored with request fingerprint and response snapshot for 24–72 hours. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
First request: process, persist `(key, hash, response, status)`. Duplicate: return stored response (HTTP 200/409) without re-executing side effects. Keys must scope to **tenant + operation** (`POST /payments` not global). Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
Required for: payments, reservations, create-style POSTs with side effects. Less critical for idempotent PUTs with natural keys. Message consumers should use **business id** (`orderId`) as dedup key. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve.

#### Production example
Mobile app sends `Idempotency-Key: 7b3e...` on `POST /v1/payments`. Network retry hits load balancer twice; second request returns original `201` body from idempotency store. Kafka consumer stores `processed_events(eventId)` before side effects. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Key only in memory — lost on pod restart → double charge.
- Same key reused for different amounts.
- Idempotency without locking — two threads both pass check.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Idempotency key TTL — how long and why?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. An **idempotency key** (client-supplied or server-generated) lets a service recognize duplicate requests and return the same outcome without double-charging or double-shipping. Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Difference vs Kafka exactly-once semantics?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. An **idempotency key** (client-supplied or server-generated) lets a service recognize duplicate requests and return the same outcome without double-charging or double-shipping. Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you key saga compensations?
**A:** For 'How do you key saga compensations': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. First request: process, persist `(key, hash, response, status)`. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving idempotency keys. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. An **idempotency key** (client-supplied or server-generated) lets a service recognize duplicate requests and return the same outcome without double-charging or double-shipping. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Mobile app sends `Idempotency-Key: 7b3e...` on `POST /v1/payments`.

#### Code / config (when useful)

```java
@PostMapping("/payments")
public ResponseEntity<Payment> pay(@RequestHeader("Idempotency-Key") String key,
                                   @RequestBody PaymentRequest req) {
    return idempotencyStore.execute(key, req, () -> paymentService.charge(req));
}
```

---

### 9. API versioning vs event versioning.

**Short answer:** **API versioning** (URL `/v2`, header, content negotiation) controls synchronous contract evolution — clients choose when to migrate. **Event versioning** must tolerate **multiple schema versions in flight** because you cannot upgrade all consumers simultaneously. Events favor backward-compatible additive changes, schema registry rules, and upcasters — not "breaking v2 topic" without a plan. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
APIs: request/response, often fewer producers. Events: many consumers at different speeds, log retention, replay. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
API: deprecate v1 with sunset date; gateway routes by path. Events: Avro/Protobuf with **FULL_TRANSITIVE** compatibility; new optional fields; `schema_version` field; dual-write or dual-read during migration. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| API break | Event break |
|-----------|-------------|
| Coordinated mobile release | Never casually — replay breaks |
| BFF shields clients | Use new event type + deprecate old |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`OrderCreated` v1 has `customerId`; v2 adds `customerSegment` optional. Consumers ignore unknown fields. Breaking rename `customerId` → `buyerId` ships as new event `OrderCreatedV2` on topic `orders.v2`; old topic drained before decommission. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Breaking JSON events without schema registry enforcement.
- Versioning only in topic name (`orders-v47`) with no compatibility policy.
- API v2 that changes error codes silently.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Expand/contract for events?
**A:** Senior answer to 'Expand/contract for events': tie to ownership, timeouts, and observable failure modes. APIs: request/response, often fewer producers. `OrderCreated` v1 has `customerId`; v2 adds `customerSegment` optional. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How long do you run dual API versions?
**A:** Senior answer to 'How long do you run dual API versions': tie to ownership, timeouts, and observable failure modes. APIs: request/response, often fewer producers. `OrderCreated` v1 has `customerId`; v2 adds `customerSegment` optional. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Pact vs schema registry responsibilities?
**A:** Senior answer to 'Pact vs schema registry responsibilities': tie to ownership, timeouts, and observable failure modes. APIs: request/response, often fewer producers. `OrderCreated` v1 has `customerId`; v2 adds `customerSegment` optional. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving api versioning vs event versioning. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **API versioning** (URL `/v2`, header, content negotiation) controls synchronous contract evolution — clients choose when to migrate. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `OrderCreated` v1 has `customerId`; v2 adds `customerSegment` optional.

---

### 10. Contract testing (Pact) vs E2E.

**Short answer:** **Contract tests** verify provider meets consumer expectations in isolation — fast, precise failures at the breaking change. **E2E** tests full journeys in near-prod — slow, flaky, few in number. Seniors pyramid: many unit, some integration (Testcontainers), contract tests at boundaries, handful of smoke E2E. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Pact: consumer defines expected request/response; provider verification job fails CI if broken. E2E: Playwright/Cypress against staging with all services up. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Consumer test generates pact JSON → published to broker → provider `verify-pacts` in pipeline. E2E requires data seeding, env stability, and debug time when red. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Contract | E2E |
|----------|-----|
| Every service boundary | Critical revenue paths (checkout smoke) |
| Event schema consumer-driven | Cross-team release confidence |

Do not replace contract tests with 200 Selenium tests.

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`mobile-bff` pact expects `GET /products/{id}` returns `sku` string. `catalog-service` CI verifies all pacts before deploy. One nightly E2E buys a $0 test SKU in staging. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Pact only on happy path — no error contracts.
- Provider verification skipped on "small" PRs.
- E2E testing third-party payment sandbox in every PR.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Consumer-driven vs provider-driven contracts?
**A:** Senior answer to 'Consumer-driven vs provider-driven contracts': tie to ownership, timeouts, and observable failure modes. Pact: consumer defines expected request/response; provider verification job fails CI if broken. `mobile-bff` pact expects `GET /products/{id}` returns `sku` string. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you contract-test Kafka events?
**A:** Senior answer to 'How do you contract-test Kafka events': tie to ownership, timeouts, and observable failure modes. Pact: consumer defines expected request/response; provider verification job fails CI if broken. `mobile-bff` pact expects `GET /products/{id}` returns `sku` string. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** What belongs in Testcontainers vs pact?
**A:** Senior answer to 'What belongs in Testcontainers vs pact': tie to ownership, timeouts, and observable failure modes. Pact: consumer defines expected request/response; provider verification job fails CI if broken. `mobile-bff` pact expects `GET /products/{id}` returns `sku` string. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving contract testing (pact) vs e2e. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Contract tests** verify provider meets consumer expectations in isolation — fast, precise failures at the breaking change. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `mobile-bff` pact expects `GET /products/{id}` returns `sku` string.

---

### 11. Service discovery.

**Short answer:** **Service discovery** lets callers find healthy instances without hard-coded IPs — register on startup, deregister on shutdown, health-check periodically. In Kubernetes, DNS + Endpoints + kube-proxy/Envoy often replace bespoke Consul/Eureka; understand both models for interviews and brownfield. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Client-side discovery (Eureka + Ribbon): client queries registry, picks instance. Server-side (K8s Service, mesh): stable DNS name → load-balanced backends. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Registry stores `(serviceName, host, port, metadata, health)`. Cache + refresh intervals cause brief stale routing after deploy. Headless services for StatefulSets; ClusterIP for stateless. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| K8s-native DNS | Eureka/Consul |
|----------------|---------------|
| Greenfield on K8s | VMs, multi-cloud without mesh |
| Platform team owns networking | Spring Cloud Netflix legacy |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`order-service` Deployment registers as `order-service.default.svc.cluster.local`. `payment-service` uses `http://payment-service:8080` — no config change on scale-out. Readiness probe gates Endpoints until DB migration completes. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Liveness flapping removes all replicas from discovery.
- Relying on pod IP in config.
- No grace period on shutdown — in-flight requests killed.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Client-side vs server-side discovery trade-offs?
**A:** Senior answer to 'Client-side vs server-side discovery trade-offs': tie to ownership, timeouts, and observable failure modes. Client-side discovery (Eureka + Ribbon): client queries registry, picks instance. `order-service` Deployment registers as `order-service.default.svc.cluster.local`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How does Istio service entry differ?
**A:** Senior answer to 'How does Istio service entry differ': tie to ownership, timeouts, and observable failure modes. Client-side discovery (Eureka + Ribbon): client queries registry, picks instance. `order-service` Deployment registers as `order-service.default.svc.cluster.local`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Eureka in K8s — still worth it?
**A:** Senior answer to 'Eureka in K8s — still worth it': tie to ownership, timeouts, and observable failure modes. Client-side discovery (Eureka + Ribbon): client queries registry, picks instance. `order-service` Deployment registers as `order-service.default.svc.cluster.local`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving service discovery. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Service discovery** lets callers find healthy instances without hard-coded IPs — register on startup, deregister on shutdown, health-check periodically. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `order-service` Deployment registers as `order-service.default.svc.cluster.local`.

---

### 12. Load balancing L4 vs L7.

**Short answer:** **L4** balances TCP connections to instances — fast, protocol-agnostic, no URL routing. **L7** understands HTTP/gRPC: path-based routing, TLS termination, retries, rate limits, header-based canary. Microservices on Kubernetes typically use L7 Ingress/gateway for north-south traffic and L4 kube-proxy or mesh for east-west. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
L4: IP:port → backend pool (NLB, kube-proxy). L7: Host, path, headers → service/version (ALB, NGINX Ingress, Envoy). The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
L7 can inject tracing headers, enforce JWT validation, and weight 90/10 canary. L4 preserves source IP with PROXY protocol; connection stickiness without app awareness. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| L4 | L7 |
|----|-----|
| Non-HTTP (Redis, custom TCP) | REST/gRPC APIs, BFF routing |
| Maximum throughput simplicity | Path-based monolith strangler |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
ALB terminates TLS, routes `/api/orders/*` → `order-service`, `/api/catalog/*` → `catalog-service`. Internal gRPC uses mesh L7 retries with `retryOn: unavailable` limited to idempotent methods. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- L7 balancer with no idle timeout alignment → 502 mid-request.
- Canary by DNS only — sticky clients bypass split.
- Retry storms at L7 without idempotency downstream.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Where does TLS terminate?
**A:** Senior answer to 'Where does TLS terminate': tie to ownership, timeouts, and observable failure modes. L4: IP:port → backend pool (NLB, kube-proxy). ALB terminates TLS, routes `/api/orders/*` → `order-service`, `/api/catalog/*` → `catalog-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** gRPC load balancing — why L7 matters?
**A:** Senior answer to 'gRPC load balancing — why L7 matters': tie to ownership, timeouts, and observable failure modes. L4: IP:port → backend pool (NLB, kube-proxy). ALB terminates TLS, routes `/api/orders/*` → `order-service`, `/api/catalog/*` → `catalog-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Connection pooling through gateway?
**A:** Senior answer to 'Connection pooling through gateway': tie to ownership, timeouts, and observable failure modes. L4: IP:port → backend pool (NLB, kube-proxy). ALB terminates TLS, routes `/api/orders/*` → `order-service`, `/api/catalog/*` → `catalog-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving load balancing l4 vs l7. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **L4** balances TCP connections to instances — fast, protocol-agnostic, no URL routing. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. ALB terminates TLS, routes `/api/orders/*` → `order-service`, `/api/catalog/*` → `catalog-service`.

---

### 13. Circuit breaker, retry, timeout, bulkhead — the four horsemen.

**Short answer:** **Timeouts** cap wait — fail fast. **Retries** handle transient errors with backoff+jitter on idempotent ops only. **Circuit breakers** stop calling a failing dependency to let it recover. **Bulkheads** isolate thread pools/connections so one slow dependency cannot exhaust the service. Together they prevent cascade failures; misconfigured retries are often worse than no retries.

#### What it is
Resilience4j / Istio policies implement these patterns. Defaults without tuning are dangerous. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Breaker states: CLOSED → OPEN (fail fast) → HALF_OPEN (probe). Bulkhead: separate executor for `paymentClient` vs `catalogClient`. Retry budget: max attempts × instances can DDOS a recovering service. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Apply | Avoid |
|-------|-------|
| Every outbound sync call gets timeout | Retry POST /charge without idempotency |
| Breaker on payment, inventory | Infinite retries |
| Bulkhead when fan-out to N services | Shared unbounded thread pool |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`order-service`: 2s timeout on inventory, 3 retries with 100ms–1s jitter on `GET` availability only; breaker opens after 50% errors in 10s window; bulkhead max 20 concurrent payment calls. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- Retry on 500 for non-idempotent create.
- Global breaker — catalog outage blocks checkout unnecessarily.
- Timeout longer than gateway timeout — client sees 504 while server still working.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you choose timeout values?
**A:** Senior answer to 'How do you choose timeout values': tie to ownership, timeouts, and observable failure modes. Resilience4j / Istio policies implement these patterns. `order-service`: 2s timeout on inventory, 3 retries with 100ms–1s jitter on `GET` availability only; breaker opens after 50% errors in 10s window; bulkhead max 20 concurrent payment calls. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Half-open probe rate?
**A:** Senior answer to 'Half-open probe rate': tie to ownership, timeouts, and observable failure modes. Resilience4j / Istio policies implement these patterns. `order-service`: 2s timeout on inventory, 3 retries with 100ms–1s jitter on `GET` availability only; breaker opens after 50% errors in 10s window; bulkhead max 20 concurrent payment calls. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Bulkhead vs rate limit difference?
**A:** Senior answer to 'Bulkhead vs rate limit difference': tie to ownership, timeouts, and observable failure modes. Resilience4j / Istio policies implement these patterns. `order-service`: 2s timeout on inventory, 3 retries with 100ms–1s jitter on `GET` availability only; breaker opens after 50% errors in 10s window; bulkhead max 20 concurrent payment calls. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving circuit breaker, retry, timeout, bulkhead shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Timeouts** cap wait — fail fast. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `order-service`: 2s timeout on inventory, 3 retries with 100ms–1s jitter on `GET` availability only; breaker opens after 50% errors in 10s window; bulkhead max 20 concurrent payment calls.

#### Code / config (when useful)

```java
@CircuitBreaker(name = "inventory")
@Retry(name = "inventory", fallbackMethod = "inventoryFallback")
@TimeLimiter(name = "inventory")
public Stock checkStock(String sku) { ... }
```

---

### 14. Distributed tracing.

**Short answer:** **Distributed tracing** correlates one user request across services via a **trace ID** propagated in headers (`traceparent`, B3, W3C). Spans show latency per hop — essential when p99 explodes and logs alone cannot tell which downstream call stalled. Pair traces with structured logs sharing `traceId`. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
OpenTelemetry SDK → collector → Jaeger/Tempo/Datadog. Each service creates spans for inbound HTTP, DB, Kafka publish/consume. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Trace: tree of spans with parent span ID. Sampling: head-based (1%) or tail-based (keep errors/slow). Baggage propagates business context (tenant) — use sparingly (PII risk). Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
Mandatory for microservices with sync chains >2 deep. Monolith with one DB — logs may suffice initially. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Checkout trace shows 1.2s in `payment-service` JDBC pool wait — not network. Fix: increase pool + index on `payments(idempotency_key)`. Alert on span `kafka.publish` lag > 500ms. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Broken context propagation in async `@Async` or reactive chains.
- 100% trace sampling in prod — cost explosion.
- Traces without linking Kafka consumer to producer trace.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** W3C tracecontext vs B3?
**A:** 'W3C tracecontext vs B3' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. OpenTelemetry SDK → collector → Jaeger/Tempo/Datadog. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to trace scheduled jobs?
**A:** Senior answer to 'How to trace scheduled jobs': tie to ownership, timeouts, and observable failure modes. OpenTelemetry SDK → collector → Jaeger/Tempo/Datadog. Checkout trace shows 1.2s in `payment-service` JDBC pool wait — not network. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Tail-based sampling benefits?
**A:** Senior answer to 'Tail-based sampling benefits': tie to ownership, timeouts, and observable failure modes. OpenTelemetry SDK → collector → Jaeger/Tempo/Datadog. Checkout trace shows 1.2s in `payment-service` JDBC pool wait — not network. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving distributed tracing. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Distributed tracing** correlates one user request across services via a **trace ID** propagated in headers (`traceparent`, B3, W3C). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Checkout trace shows 1.2s in `payment-service` JDBC pool wait — not network.

---

### 15. Correlation vs causation in events.

**Short answer:** **Correlation ID** ties related messages about one business case (`orderId`, `checkoutId`) — many events, one story. **Causation ID** points to the specific parent event/command that triggered this one — reconstruct chains for debugging and audit. Use both: correlation for dashboards, causation for "why did this refund fire?" The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Fields in event envelope: `correlationId`, `causationId`, `eventId`, `occurredAt`. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
`OrderPlaced` (id=e1) → inventory emits `StockReserved` (correlation=order-1, causation=e1). Support tool walks causation chain. Distinct from distributed tracing `traceId` — business vs technical correlation. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
Always in event-driven systems. Skip only for fire-and-forget metrics with no business linkage. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Fraud service subscribes to payments; each `PaymentDeclined` carries causation from `PaymentAuthorized` attempt. Analysts trace promotion bug: bad `DiscountApplied` caused downstream `RefundIssued`. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Reusing correlation ID across unrelated customer sessions.
- Only UUID in logs, not in Kafka headers.
- No causation — cannot distinguish retry from new business action.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Correlation ID vs trace ID?
**A:** Senior answer to 'Correlation ID vs trace ID': tie to ownership, timeouts, and observable failure modes. Fields in event envelope: `correlationId`, `causationId`, `eventId`, `occurredAt`. Fraud service subscribes to payments; each `PaymentDeclined` carries causation from `PaymentAuthorized` attempt. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Propagate through saga orchestrator?
**A:** For 'Propagate through saga orchestrator': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. `OrderPlaced` (id=e1) → inventory emits `StockReserved` (correlation=order-1, causation=e1). Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Event sourcing and causation streams?
**A:** Senior answer to 'Event sourcing and causation streams': tie to ownership, timeouts, and observable failure modes. Fields in event envelope: `correlationId`, `causationId`, `eventId`, `occurredAt`. Fraud service subscribes to payments; each `PaymentDeclined` carries causation from `PaymentAuthorized` attempt. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving correlation vs causation in events. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Correlation ID** ties related messages about one business case (`orderId`, `checkoutId`) — many events, one story. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Fraud service subscribes to payments; each `PaymentDeclined` carries causation from `PaymentAuthorized` attempt.

---

### 16. BFF (Backend for Frontend).

**Short answer:** A **BFF** is a dedicated API layer per client experience (mobile, web, partner) that aggregates microservices, shapes DTOs, and handles client-specific auth and caching — keeping core domain services free of `if (iOS)` logic. Not every app needs one; avoid N BFFs duplicating business rules. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Thin orchestration + presentation API; usually no owned database (cache exception). The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Mobile BFF parallel-calls `catalog` + `pricing` + `inventory`, returns one payload. GraphQL BFF resolves fields via dataloaders to avoid N+1 HTTP. Token exchange: public OAuth at edge, service tokens inside. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| BFF yes | BFF no |
|---------|--------|
| Distinct mobile/web payloads | Single API consumers |
| Client-specific aggregation | Business logic creep in BFF |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`mobile-bff` exposes `GET /home-feed` — 4 backend calls, 200ms budget, cached hero products. `web-bff` returns richer CMS blocks. `order-service` stays canonical for `Order` model. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- BFF becomes second monolith with business rules.
- Six BFFs with copy-paste aggregation code.
- BFF writes to another service's DB "for speed."
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** BFF vs API Gateway — overlap?
**A:** Senior answer to 'BFF vs API Gateway — overlap': tie to ownership, timeouts, and observable failure modes. Thin orchestration + presentation API; usually no owned database (cache exception). `mobile-bff` exposes `GET /home-feed` — 4 backend calls, 200ms budget, cached hero products. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** GraphQL as BFF — pitfalls?
**A:** Senior answer to 'GraphQL as BFF — pitfalls': tie to ownership, timeouts, and observable failure modes. Thin orchestration + presentation API; usually no owned database (cache exception). `mobile-bff` exposes `GET /home-feed` — 4 backend calls, 200ms budget, cached hero products. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to prevent logic duplication across BFFs?
**A:** Senior answer to 'How to prevent logic duplication across BFFs': tie to ownership, timeouts, and observable failure modes. Thin orchestration + presentation API; usually no owned database (cache exception). `mobile-bff` exposes `GET /home-feed` — 4 backend calls, 200ms budget, cached hero products. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving bff (backend for frontend). shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **BFF** is a dedicated API layer per client experience (mobile, web, partner) that aggregates microservices, shapes DTOs, and handles client-specific auth and caching — keeping core domain services free of `if (iOS)` logic. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `mobile-bff` exposes `GET /home-feed` — 4 backend calls, 200ms budget, cached hero products.

---

### 17. API Gateway responsibilities.

**Short answer:** An **API Gateway** is the north-south front door: TLS termination, authentication, rate limiting, routing to services, request/response transformation, and sometimes WAF. It should not own core business workflows — those belong in domain services or a dedicated orchestrator. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Kong, Apigee, AWS API Gateway, NGINX, Envoy Gateway — policy enforcement at the edge. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Plugins/middleware chain: JWT validate → extract claims → route `/v1/orders` → add `X-Request-Id` → forward to K8s Ingress. Centralized API keys for partners; mTLS for internal optional. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Gateway | Not gateway |
|---------|-------------|
| Cross-cutting edge policies | Saga compensation |
| Public multi-tenant APIs | Deep domain validation |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Partner API: gateway enforces 1000 req/min per API key, validates OAuth scope `orders:read`, routes to `order-service`. Internal admin traffic uses separate gateway with IP allowlist. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- 500-line Lua in gateway implementing pricing rules.
- Gateway as only rate limit — no per-service limits behind it.
- Double body parsing — gateway + service both read stream.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Gateway vs service mesh ingress?
**A:** Senior answer to 'Gateway vs service mesh ingress': tie to ownership, timeouts, and observable failure modes. Kong, Apigee, AWS API Gateway, NGINX, Envoy Gateway — policy enforcement at the edge. Partner API: gateway enforces 1000 req/min per API key, validates OAuth scope `orders:read`, routes to `order-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you version routes at gateway?
**A:** Senior answer to 'How do you version routes at gateway': tie to ownership, timeouts, and observable failure modes. Kong, Apigee, AWS API Gateway, NGINX, Envoy Gateway — policy enforcement at the edge. Partner API: gateway enforces 1000 req/min per API key, validates OAuth scope `orders:read`, routes to `order-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Zero-trust: gateway enough?
**A:** Senior answer to 'Zero-trust: gateway enough': tie to ownership, timeouts, and observable failure modes. Kong, Apigee, AWS API Gateway, NGINX, Envoy Gateway — policy enforcement at the edge. Partner API: gateway enforces 1000 req/min per API key, validates OAuth scope `orders:read`, routes to `order-service`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving api gateway responsibilities. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. An **API Gateway** is the north-south front door: TLS termination, authentication, rate limiting, routing to services, request/response transformation, and sometimes WAF. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Partner API: gateway enforces 1000 req/min per API key, validates OAuth scope `orders:read`, routes to `order-service`.

---

### 18. Authentication in a mesh.

**Short answer:** **Edge authentication** validates user/partner tokens (OAuth2/OIDC). **Service-to-service** uses short-lived tokens (JWT with audience, mTLS SPIFFE IDs) — never long-lived shared secrets in config. A mesh can enforce mTLS and RBAC; it does not replace identity for end users. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Layers: user JWT at gateway → internal service identity (K8s SA token, Istio peer identity) → optional per-request authorization (OPA, Cedar). The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Gateway validates external JWT, forwards `Authorization` or exchanges for internal token. Mesh `PeerAuthentication` STRICT mTLS; `AuthorizationPolicy` allows `order-service` → `payment-service` only. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| mTLS mesh | Shared API key between all services |
|-----------|-------------------------------------|
| Zero-trust east-west | Never in prod |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Keycloak issues user JWT; `order-service` validates via JWKS cache. Calls `payment-service` with K8s projected SA token; Istio ensures only `order-service` identity reaches payment pods. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Passing user JWT to every internal service — bloated, hard to revoke.
- `disable TLS verify` in dev becoming prod config.
- Authorization only at gateway — attacker inside cluster has free rein.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** SPIFFE/SPIRE vs K8s SA tokens?
**A:** Senior answer to 'SPIFFE/SPIRE vs K8s SA tokens': tie to ownership, timeouts, and observable failure modes. Layers: user JWT at gateway → internal service identity (K8s SA token, Istio peer identity) → optional per-request authorization (OPA, Cedar). Keycloak issues user JWT; `order-service` validates via JWKS cache. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to propagate user identity to audit logs?
**A:** Senior answer to 'How to propagate user identity to audit logs': tie to ownership, timeouts, and observable failure modes. Layers: user JWT at gateway → internal service identity (K8s SA token, Istio peer identity) → optional per-request authorization (OPA, Cedar). Keycloak issues user JWT; `order-service` validates via JWKS cache. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Service account key in Git — incident story?
**A:** Senior answer to 'Service account key in Git — incident story': tie to ownership, timeouts, and observable failure modes. Layers: user JWT at gateway → internal service identity (K8s SA token, Istio peer identity) → optional per-request authorization (OPA, Cedar). Keycloak issues user JWT; `order-service` validates via JWKS cache. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving authentication in a mesh. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Edge authentication** validates user/partner tokens (OAuth2/OIDC). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Keycloak issues user JWT; `order-service` validates via JWKS cache.

---

### 19. Distributed monolith symptoms.

**Short answer:** A **distributed monolith** looks like microservices but behaves like one tightly coupled app: shared databases, synchronized deploys, chatty sync chains, and breaking one service requires changing three others. Symptoms include "we can't deploy catalog without deploying order" and p99 latency that sums across five HTTP calls for one screen. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Architecture anti-pattern: network boundaries without domain or data boundaries. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Teams retain monolith mental model — cross-service transactions, shared ORM entities, circular dependencies. CI pipelines deploy "the stack" together. Incidents require war rooms across all teams. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
Recognition triggers refactor: introduce data ownership, async boundaries, or **re-merge** services if boundaries were wrong (yes, merge is valid). Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
Four services, one Postgres schema, Flyway migrations coordinated in Slack. Extract failed; team merged `shipping` back into `fulfillment` monolith module and kept one deployable — latency and deploy frequency improved. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Ignoring symptoms because "we have 40 pods."
- Blaming Kafka instead of fixing shared DB.
- Conway's law ignored — five teams, one database.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** How do you diagnose vs healthy microservices?
**A:** Senior answer to 'How do you diagnose vs healthy microservices': tie to ownership, timeouts, and observable failure modes. Architecture anti-pattern: network boundaries without domain or data boundaries. Four services, one Postgres schema, Flyway migrations coordinated in Slack. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** When would you merge services back?
**A:** Senior answer to 'When would you merge services back': tie to ownership, timeouts, and observable failure modes. Architecture anti-pattern: network boundaries without domain or data boundaries. Four services, one Postgres schema, Flyway migrations coordinated in Slack. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Metrics that expose distributed monolith?
**A:** 'Metrics that expose distributed monolith' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. Architecture anti-pattern: network boundaries without domain or data boundaries. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving distributed monolith symptoms. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **distributed monolith** looks like microservices but behaves like one tightly coupled app: shared databases, synchronized deploys, chatty sync chains, and breaking one service requires changing three others. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Four services, one Postgres schema, Flyway migrations coordinated in Slack.

---

### 20. Shared libraries: OK vs not.

**Short answer:** **OK to share:** pure utilities, observability bootstrap, auth client SDKs, DTOs for **published API contracts** (with versioning discipline). **Not OK:** shared domain entities with JPA annotations, "common-service" business logic, shared DB access layer — those create hidden coupling and synchronized releases. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Internal Maven/Gradle artifacts (`platform-observability`, `payments-api-contract`) vs `common-everything.jar`. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Every shared domain class change forces N service releases. Binary coupling beats network coupling for frequency of breakage. Prefer copy-small-value-objects or codegen from OpenAPI/Avro over fat shared models. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Share | Don't share |
|-------|-------------|
| Resilience4j wrappers, trace propagators | `OrderEntity` with Hibernate mappings |
| Generated API client from OpenAPI | Business policy engine in library |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`payments-api` module contains only OpenAPI-generated interfaces + DTOs versioned `2.1.0`. Services pin different versions during migration. Deleted `common-domain` jar that caused monthly "bump common" PRs across 12 repos. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- SNAPSHOT dependencies in prod builds.
- Shared library performs DB queries.
- One repo to rule them all without release tags.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Duplicate code vs shared library trade-off?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. **OK to share:** pure utilities, observability bootstrap, auth client SDKs, DTOs for **published API contracts** (with versioning discipline). Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to version internal libraries?
**A:** Senior answer to 'How to version internal libraries': tie to ownership, timeouts, and observable failure modes. Internal Maven/Gradle artifacts (`platform-observability`, `payments-api-contract`) vs `common-everything.jar`. `payments-api` module contains only OpenAPI-generated interfaces + DTOs versioned `2.1.0`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Monorepo vs multirepo for libraries?
**A:** Senior answer to 'Monorepo vs multirepo for libraries': tie to ownership, timeouts, and observable failure modes. Internal Maven/Gradle artifacts (`platform-observability`, `payments-api-contract`) vs `common-everything.jar`. `payments-api` module contains only OpenAPI-generated interfaces + DTOs versioned `2.1.0`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving shared libraries: ok vs not. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **OK to share:** pure utilities, observability bootstrap, auth client SDKs, DTOs for **published API contracts** (with versioning discipline). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `payments-api` module contains only OpenAPI-generated interfaces + DTOs versioned `2.1.0`.

---

### 21. Schema registry for events.

**Short answer:** A **schema registry** (Confluent, Apicurio) stores Avro/Protobuf/JSON Schema versions with **compatibility rules** — producers register schema ID in message payload; consumers deserialize safely. It prevents "someone added a field Friday" production outages and enables replay with schema evolution. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Central contract store for async boundaries; CI checks compatibility on PR. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Wire format: magic byte + schema ID + payload. Registry returns schema for ID. Rules: BACKWARD (new consumer, old producer), FORWARD, FULL. Incompatible change fails CI `mvn schema-registry:test`.

#### When to use / when NOT to use
| Registry | Skip |
|----------|------|
| Kafka with many event types | One internal topic, one team, JSON blobs |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`OrderCreated` Avro schema adds optional `loyaltyTier`; registry validates BACKWARD compat; old consumers continue. Breaking change requires new subject `order-created-v2` and migration playbook. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- JSON without schema enforcement in prod.
- Deleting old schema versions while Kafka retention still has old messages.
- `auto.register.schemas=true` in prod producers — bypasses review.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** BACKWARD vs FULL transitive?
**A:** Senior answer to 'BACKWARD vs FULL transitive': tie to ownership, timeouts, and observable failure modes. Central contract store for async boundaries; CI checks compatibility on PR. `OrderCreated` Avro schema adds optional `loyaltyTier`; registry validates BACKWARD compat; old consumers continue. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Schema registry HA and Kafka outage?
**A:** Senior answer to 'Schema registry HA and Kafka outage': tie to ownership, timeouts, and observable failure modes. Central contract store for async boundaries; CI checks compatibility on PR. `OrderCreated` Avro schema adds optional `loyaltyTier`; registry validates BACKWARD compat; old consumers continue. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Protobuf vs Avro in Java?
**A:** Senior answer to 'Protobuf vs Avro in Java': tie to ownership, timeouts, and observable failure modes. Central contract store for async boundaries; CI checks compatibility on PR. `OrderCreated` Avro schema adds optional `loyaltyTier`; registry validates BACKWARD compat; old consumers continue. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving schema registry for events. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **schema registry** (Confluent, Apicurio) stores Avro/Protobuf/JSON Schema versions with **compatibility rules** — producers register schema ID in message payload; consumers deserialize safely. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `OrderCreated` Avro schema adds optional `loyaltyTier`; registry validates BACKWARD compat; old consumers continue.

---

### 22. Fan-out and the N+1 of microservices.

**Short answer:** **Fan-out** is one request triggering many downstream calls — the microservices version of N+1 queries. A single `GET /product-page` that serially calls 12 services multiplies latency and failure risk. Fix with parallel calls, aggregation (BFF), materialized read models, or batch APIs. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Structural problem: graph depth and breadth without caching or denormalization. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Serial: L_total = Σ L_i. Parallel: L_total ≈ max(L_i) + overhead. Each hop adds timeout/retry policy risk. Event-driven read models pre-join data for display.

#### When to use / when NOT to use
| Fix fan-out | Accept fan-out |
|-------------|----------------|
| User-facing read paths | Rare admin ops |
| High QPS endpoints | Strong consistency across reads |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Product page moved from 8 sync calls to `product-read-service` serving denormalized document updated by `ProductUpdated` events. p95 dropped 400ms → 80ms. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- GraphQL resolver calling HTTP per field without DataLoader.
- No bulkhead — one slow recommendation service stalls page.
- "We'll cache later" without invalidation design.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** BFF aggregation vs CQRS read model?
**A:** Senior answer to 'BFF aggregation vs CQRS read model': tie to ownership, timeouts, and observable failure modes. Structural problem: graph depth and breadth without caching or denormalization. Product page moved from 8 sync calls to `product-read-service` serving denormalized document updated by `ProductUpdated` events. p95 dropped 400ms → 80ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to bulkhead fan-out?
**A:** Senior answer to 'How to bulkhead fan-out': tie to ownership, timeouts, and observable failure modes. Structural problem: graph depth and breadth without caching or denormalization. Product page moved from 8 sync calls to `product-read-service` serving denormalized document updated by `ProductUpdated` events. p95 dropped 400ms → 80ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** GraphQL N+1 in microservices?
**A:** Senior answer to 'GraphQL N+1 in microservices': tie to ownership, timeouts, and observable failure modes. Structural problem: graph depth and breadth without caching or denormalization. Product page moved from 8 sync calls to `product-read-service` serving denormalized document updated by `ProductUpdated` events. p95 dropped 400ms → 80ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving fan-out and the n+1 of microservices. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Fan-out** is one request triggering many downstream calls — the microservices version of N+1 queries. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Product page moved from 8 sync calls to `product-read-service` serving denormalized document updated by `ProductUpdated` events. p95 dropped 400ms → 80ms.

---

### 23. Caching in distributed systems.

**Short answer:** Caches trade consistency for speed — **cache-aside** (app manages Redis) is common; **TTL** alone is not invalidation. In microservices, each service caches **its own** data or explicitly subscribed projections; never cache another service's mutable state without an invalidation contract (events, version headers). The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Layers: CDN (static), gateway (rate limit counters), app Redis, local Caffeine, DB query cache. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Cache-aside: read Redis → miss → DB → set with TTL. Write-through/on-write-invalidate for hot keys. Stale reads acceptable? Define business SLO. Thundering herd: singleflight or probabilistic early expiration.

#### When to use / when NOT to use
| Cache | Don't cache |
|-------|-------------|
| Catalog, config, idempotent GETs | Stock levels without invalidation |
| JWT JWKS (short TTL) | Personalized prices without version key |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`catalog-service` caches product by SKU in Redis, 5m TTL + invalidates on `ProductUpdated` Kafka event. `order-service` does not cache inventory — always calls inventory or uses reservation hold. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Shared Redis key namespace across services — collision and stale cross-talk.
- No cache stampede protection on hot keys.
- Caching POST responses.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Cache invalidation vs TTL for pricing?
**A:** Senior answer to 'Cache invalidation vs TTL for pricing': tie to ownership, timeouts, and observable failure modes. Layers: CDN (static), gateway (rate limit counters), app Redis, local Caffeine, DB query cache. `catalog-service` caches product by SKU in Redis, 5m TTL + invalidates on `ProductUpdated` Kafka event. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Local cache per pod — consistency?
**A:** Senior answer to 'Local cache per pod — consistency': tie to ownership, timeouts, and observable failure modes. Layers: CDN (static), gateway (rate limit counters), app Redis, local Caffeine, DB query cache. `catalog-service` caches product by SKU in Redis, 5m TTL + invalidates on `ProductUpdated` Kafka event. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Redis cluster failure mode?
**A:** Senior answer to 'Redis cluster failure mode': tie to ownership, timeouts, and observable failure modes. Layers: CDN (static), gateway (rate limit counters), app Redis, local Caffeine, DB query cache. `catalog-service` caches product by SKU in Redis, 5m TTL + invalidates on `ProductUpdated` Kafka event. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving caching in distributed systems. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. Caches trade consistency for speed — **cache-aside** (app manages Redis) is common; **TTL** alone is not invalidation. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `catalog-service` caches product by SKU in Redis, 5m TTL + invalidates on `ProductUpdated` Kafka event.

---

### 24. Consistency models you'll actually use.

**Short answer:** In production microservices you mostly use **strong consistency inside one service** (single DB transaction) and **eventual consistency across services** with explicit business tolerances. **Read-your-writes** via routing or short sync wait; **causal** via version vectors rarely outside specialized systems. Name the user-visible guarantee, not CAP buzzwords. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Models: linearizable (single leader DB), eventual (replicas lag), sequential (per-session), bounded staleness. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Checkout: order row + outbox in one TX = strong local. Search index updates seconds later = eventual. Payment status polled until `CAPTURED` or timeout = UX consistency pattern. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Strong cross-service | Eventual |
|----------------------|----------|
| Almost never (saga instead) | Notifications, analytics, search |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Customer sees "Payment pending" for up to 30s while webhook confirms — documented SLA. Inventory dashboard may lag 10s from OLTP — banner shows "last updated." Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- "We need strong consistency" without defining which read.
- Hiding eventual lag — double-submit orders.
- Using distributed cache as source of truth.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** CAP in one sentence for this system?
**A:** Senior answer to 'CAP in one sentence for this system': tie to ownership, timeouts, and observable failure modes. Models: linearizable (single leader DB), eventual (replicas lag), sequential (per-session), bounded staleness. Customer sees "Payment pending" for up to 30s while webhook confirms — documented SLA. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Read-your-writes after profile update?
**A:** Senior answer to 'Read-your-writes after profile update': tie to ownership, timeouts, and observable failure modes. Models: linearizable (single leader DB), eventual (replicas lag), sequential (per-session), bounded staleness. Customer sees "Payment pending" for up to 30s while webhook confirms — documented SLA. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Monotonic reads for feed?
**A:** Senior answer to 'Monotonic reads for feed': tie to ownership, timeouts, and observable failure modes. Models: linearizable (single leader DB), eventual (replicas lag), sequential (per-session), bounded staleness. Customer sees "Payment pending" for up to 30s while webhook confirms — documented SLA. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving consistency models you'll actually use. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. In production microservices you mostly use **strong consistency inside one service** (single DB transaction) and **eventual consistency across services** with explicit business tolerances. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Customer sees "Payment pending" for up to 30s while webhook confirms — documented SLA.

---

### 25. Outbox vs CDC vs dual write.

**Short answer:** **Dual write** (DB + Kafka in app code) risks orphan states — avoid. **Transactional outbox** writes event row in same DB TX as business data; relay publishes to Kafka — reliable, app-controlled. **CDC** (Debezium) tails DB WAL — no app code, captures all changes, harder to shape event semantics. Pick outbox for explicit domain events; CDC for analytics/integration when event shape = row shape is OK.

#### What it is
Patterns for **atomic publish** of state change + message. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Outbox: `INSERT order` + `INSERT outbox` → poller/LogTape relay → Kafka. CDC: connector reads binlog → topic per table. Dual write: commit DB then publish — crash between = inconsistency. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Outbox | CDC |
|--------|-----|
| Rich domain events | Warehouse sync, audit stream |
| Control payload | Legacy DB you can't change |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`order-service` outbox table relayed by Debezium Outbox Event Router to `orders` topic with aggregate id partition key. Reporting uses raw CDC `orders_table` topic separately. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Outbox relay without idempotent publish keys.
- CDC exposing internal columns (PII) to all consumers.
- Deleting outbox rows before Kafka ack.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Polling vs log-based relay latency?
**A:** Senior answer to 'Polling vs log-based relay latency': tie to ownership, timeouts, and observable failure modes. Patterns for **atomic publish** of state change + message. `order-service` outbox table relayed by Debezium Outbox Event Router to `orders` topic with aggregate id partition key. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** CDC ordering per partition?
**A:** Senior answer to 'CDC ordering per partition': tie to ownership, timeouts, and observable failure modes. Patterns for **atomic publish** of state change + message. `order-service` outbox table relayed by Debezium Outbox Event Router to `orders` topic with aggregate id partition key. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Exactly-once with outbox?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. **Dual write** (DB + Kafka in app code) risks orphan states — avoid. Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving outbox vs cdc vs dual write. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Dual write** (DB + Kafka in app code) risks orphan states — avoid. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `order-service` outbox table relayed by Debezium Outbox Event Router to `orders` topic with aggregate id partition key.

#### Code / config (when useful)

```sql
-- Same transaction as business write
INSERT INTO outbox (aggregate_id, type, payload) VALUES (...);
```

---

### 26. Exactly-once in microservices.

**Short answer:** True **end-to-end exactly-once** across services is impractical; what teams implement is **effectively-once**: idempotent consumers + dedup store + transactional outbox + Kafka idempotent producer (per partition). Interview answer: define **exactly-once semantics for side effects**, not Kafka marketing slides. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Layers: broker dedup (producer id + sequence), consumer offset commit with processing, business idempotency table. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Kafka EOS: transactional producer + `read_committed` consumers in stream app — scope is one consume-process-produce topology, not your whole enterprise. Cross-service needs idempotency keys at boundaries. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Target effectively-once | Chase EOS everywhere |
|-------------------------|----------------------|
| Payments, inventory | Theoretical purity |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Consumer processes `OrderPaid`: `INSERT INTO processed(event_id)` in same TX as `UPDATE shipment_queue` — duplicate delivery no-ops. Payment gateway idempotency handles HTTP retries. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Assuming `@KafkaListener` exactly-once without TX boundary.
- Offset commit before side effect completes.
- Ignoring poison messages in "exactly-once" design.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Kafka transactions scope limits?
**A:** Senior answer to 'Kafka transactions scope limits': tie to ownership, timeouts, and observable failure modes. Layers: broker dedup (producer id + sequence), consumer offset commit with processing, business idempotency table. Consumer processes `OrderPaid`: `INSERT INTO processed(event_id)` in same TX as `UPDATE shipment_queue` — duplicate delivery no-ops. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Outbox + dedup vs Kafka EOS?
**A:** Senior answer to 'Outbox + dedup vs Kafka EOS': tie to ownership, timeouts, and observable failure modes. Layers: broker dedup (producer id + sequence), consumer offset commit with processing, business idempotency table. Consumer processes `OrderPaid`: `INSERT INTO processed(event_id)` in same TX as `UPDATE shipment_queue` — duplicate delivery no-ops. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How long keep dedup table?
**A:** Senior answer to 'How long keep dedup table': tie to ownership, timeouts, and observable failure modes. Layers: broker dedup (producer id + sequence), consumer offset commit with processing, business idempotency table. Consumer processes `OrderPaid`: `INSERT INTO processed(event_id)` in same TX as `UPDATE shipment_queue` — duplicate delivery no-ops. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving exactly-once in microservices. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. True **end-to-end exactly-once** across services is impractical; what teams implement is **effectively-once**: idempotent consumers + dedup store + transactional outbox + Kafka idempotent producer (per partition). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Consumer processes `OrderPaid`: `INSERT INTO processed(event_id)` in same TX as `UPDATE shipment_queue` — duplicate delivery no-ops.

---

### 27. Versioned deploy: expand/contract.

**Short answer:** **Expand/contract** (parallel change) lets you evolve schema and APIs without big-bang downtime: **expand** — add new column/API alongside old; **migrate** — dual-write or backfill; **contract** — remove old after consumers upgraded. Applies to DB migrations, REST fields, and event schemas. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Also called **parallel change** or Martin Fowler's expand-contract migrations. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Phase 1: add nullable `email_v2` column. Phase 2: app writes both. Phase 3: backfill job. Phase 4: read from v2. Phase 5: drop v1. Same for API: ship optional field, migrate clients, deprecate old endpoint.

#### When to use / when NOT to use
Always for shared contracts in microservices. Skip only for internal tables with zero consumers and instant deploy. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Rename `customer_id` → `buyer_id` in events: expand by publishing both fields for 2 releases; consumers switch; contract removes `customer_id` after dashboard team confirms. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- Contract before all consumers migrated — production 500s.
- Non-null column add without default on huge table — lock.
- Feature flag off but migration already contracted.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Blue/green vs expand/contract?
**A:** Senior answer to 'Blue/green vs expand/contract': tie to ownership, timeouts, and observable failure modes. Also called **parallel change** or Martin Fowler's expand-contract migrations. Rename `customer_id` → `buyer_id` in events: expand by publishing both fields for 2 releases; consumers switch; contract removes `customer_id` after dashboard team confirms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Flyway in multi-service same DB legacy?
**A:** Senior answer to 'Flyway in multi-service same DB legacy': tie to ownership, timeouts, and observable failure modes. Also called **parallel change** or Martin Fowler's expand-contract migrations. Rename `customer_id` → `buyer_id` in events: expand by publishing both fields for 2 releases; consumers switch; contract removes `customer_id` after dashboard team confirms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Event dual-publish duration?
**A:** Senior answer to 'Event dual-publish duration': tie to ownership, timeouts, and observable failure modes. Also called **parallel change** or Martin Fowler's expand-contract migrations. Rename `customer_id` → `buyer_id` in events: expand by publishing both fields for 2 releases; consumers switch; contract removes `customer_id` after dashboard team confirms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving versioned deploy: expand/contract. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Expand/contract** (parallel change) lets you evolve schema and APIs without big-bang downtime: **expand** — add new column/API alongside old; **migrate** — dual-write or backfill; **contract** — remove old after consumers upgraded. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Rename `customer_id` → `buyer_id` in events: expand by publishing both fields for 2 releases; consumers switch; contract removes `customer_id` after dashboard team confirms.

---

### 28. Database per service and reporting.

**Short answer:** **Database per service** isolates schema evolution and failure domains but breaks ad-hoc SQL reports across domains. Reporting uses **read replicas**, **CDC to warehouse**, **CQRS projections**, or **data mesh** curated datasets — not cross-service JOINs in OLTP. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Each service owns Postgres/MySQL/etc. Analytics lives in Snowflake/BigQuery fed by pipelines. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Debezium → Kafka → dbt → star schema. Operational queries use denormalized read models. GDPR: delete commands propagated or crypto-shredding in warehouse. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Per-service DB | Shared reporting DB |
|----------------|---------------------|
| Microservices default | Legacy transitional only |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Nightly Airflow syncs `order`, `customer`, `payment` CDC streams into warehouse `fct_orders` — CEO dashboard reads warehouse only; OLTP never scanned for BI. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- BI tool connected directly to `order-service` prod DB.
- No ownership of warehouse PII masking.
- Real-time report requirements without stream pipeline budget.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** CQRS read store vs warehouse?
**A:** Senior answer to 'CQRS read store vs warehouse': tie to ownership, timeouts, and observable failure modes. Each service owns Postgres/MySQL/etc. Nightly Airflow syncs `order`, `customer`, `payment` CDC streams into warehouse `fct_orders` — CEO dashboard reads warehouse only; OLTP never scanned for BI. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Event sourcing for analytics?
**A:** Senior answer to 'Event sourcing for analytics': tie to ownership, timeouts, and observable failure modes. Each service owns Postgres/MySQL/etc. Nightly Airflow syncs `order`, `customer`, `payment` CDC streams into warehouse `fct_orders` — CEO dashboard reads warehouse only; OLTP never scanned for BI. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to delete user across DBs?
**A:** Senior answer to 'How to delete user across DBs': tie to ownership, timeouts, and observable failure modes. Each service owns Postgres/MySQL/etc. Nightly Airflow syncs `order`, `customer`, `payment` CDC streams into warehouse `fct_orders` — CEO dashboard reads warehouse only; OLTP never scanned for BI. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving database per service and reporting. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Database per service** isolates schema evolution and failure domains but breaks ad-hoc SQL reports across domains. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Nightly Airflow syncs `order`, `customer`, `payment` CDC streams into warehouse `fct_orders` — CEO dashboard reads warehouse only; OLTP never scanned for BI.

---

### 29. Distributed transactions in interviews: the order/payment/inventory example.

**Short answer:** Classic scenario: place order, reserve inventory, charge card — **cannot** be one XA transaction across three services. Walk through **saga**: reserve → pay → confirm; on pay failure release reserve; idempotency on each step; user sees explicit states. Shows you understand failure, not just happy path. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Standard senior loop question testing saga, consistency, and UX honesty. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
``` CREATE order PENDING → reserve (sync/async) → charge → CONFIRMED ↘ fail → release reserve, order CANCELLED ``` Outbox emits `OrderConfirmed` after local commit. Inventory uses reservation TTL to auto-release stuck holds. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
Use this example to discuss trade-offs — orchestration vs choreography, sync inventory check vs oversell risk. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
Flash sale: optimistic reserve with version column; payment breaker open → queue orders for retry rather than blocking catalog. Support tool manually compensates edge cases. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- "Use 2PC" without acknowledging ops reality.
- No story for payment success + order DB down.
- Ignoring duplicate submit on mobile.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Overselling inventory under race?
**A:** Senior answer to 'Overselling inventory under race': tie to ownership, timeouts, and observable failure modes. Standard senior loop question testing saga, consistency, and UX honesty. Flash sale: optimistic reserve with version column; payment breaker open → queue orders for retry rather than blocking catalog. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Sync vs async reserve?
**A:** Senior answer to 'Sync vs async reserve': tie to ownership, timeouts, and observable failure modes. Standard senior loop question testing saga, consistency, and UX honesty. Flash sale: optimistic reserve with version column; payment breaker open → queue orders for retry rather than blocking catalog. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How long reservation TTL?
**A:** Senior answer to 'How long reservation TTL': tie to ownership, timeouts, and observable failure modes. Standard senior loop question testing saga, consistency, and UX honesty. Flash sale: optimistic reserve with version column; payment breaker open → queue orders for retry rather than blocking catalog. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving distributed transactions in interviews: the order/payment/inventory example. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. Classic scenario: place order, reserve inventory, charge card — **cannot** be one XA transaction across three services. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Flash sale: optimistic reserve with version column; payment breaker open → queue orders for retry rather than blocking catalog.

---

### 30. gRPC vs REST vs GraphQL vs queues.

**Short answer:** **REST/HTTP JSON** — universal, cache-friendly, human-debuggable. **gRPC** — binary, HTTP/2, strong contracts, best internal east-west high-QPS. **GraphQL** — flexible client queries, risk of N+1 and server complexity at BFF. **Queues** — async facts, buffering, no immediate response. Public APIs often REST; internal hot paths gRPC; async domain events Kafka.

#### What it is
Sync protocols vs async messaging — different jobs. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
gRPC: protobuf, streaming, deadline propagation built-in. GraphQL: single endpoint, resolver graph. Kafka: log, consumer groups, replay. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| REST | gRPC | GraphQL | Queue |
|------|------|---------|-------|
| Public, browser | Service-to-service | Mobile BFF aggregation | Side effects |
| Webhooks | Bi-di streaming | — | Peak load smoothing |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Public partner API: OpenAPI REST. Internal `pricing` ↔ `cart`: gRPC with 50ms deadline. `OrderPlaced` → Kafka. Admin portal GraphQL BFF over REST microservices.

#### Common mistakes
- gRPC to browser without grpc-web gateway plan.
- GraphQL exposing entire microservice graph publicly.
- Queue used for query workloads.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** REST error model vs gRPC status?
**A:** Senior answer to 'REST error model vs gRPC status': tie to ownership, timeouts, and observable failure modes. Sync protocols vs async messaging — different jobs. Public partner API: OpenAPI REST. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Kafka vs RabbitMQ for events?
**A:** Senior answer to 'Kafka vs RabbitMQ for events': tie to ownership, timeouts, and observable failure modes. Sync protocols vs async messaging — different jobs. Public partner API: OpenAPI REST. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Versioning protobuf breaking changes?
**A:** Senior answer to 'Versioning protobuf breaking changes': tie to ownership, timeouts, and observable failure modes. Sync protocols vs async messaging — different jobs. Public partner API: OpenAPI REST. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving grpc vs rest vs graphql vs queues. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **REST/HTTP JSON** — universal, cache-friendly, human-debuggable. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Public partner API: OpenAPI REST.

---

### 31. Service mesh (Istio/Linkerd) value.

**Short answer:** A **service mesh** adds uniform **mTLS**, observability, retries, timeouts, and traffic splitting as infrastructure — without baking Resilience4j into every service. Value rises with many languages/teams; cost is operational complexity and latency overhead. For homogeneous Java + good libraries, mesh is optional; for polyglot at scale, often worth it. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Data plane (Envoy sidecars or eBPF) + control plane (Istiod). L7 policy without app code changes. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Sidecar intercepts outbound/inbound traffic; applies VirtualService (routing), DestinationRule (LB), PeerAuthentication (mTLS). Wasm filters for custom auth. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Mesh | Skip mesh |
|------|-----------|
| Polyglot, strict zero-trust | 3 services, one language |
| Canary at L7 without app change | Team lacks K8s maturity |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Istio sends 5% traffic to `order-service-v2` canary; automatic retries only on `idempotent=true` header; Grafana shows golden metrics per service pair without SDK in Ruby legacy app. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- Mesh without observability stack to use metrics.
- Retry policies duplicating app retries — amplification.
- Sidecar resource limits too low — OOM during spike.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Sidecar vs ambient mesh (Istio)?
**A:** Senior answer to 'Sidecar vs ambient mesh (Istio)': tie to ownership, timeouts, and observable failure modes. Data plane (Envoy sidecars or eBPF) + control plane (Istiod). Istio sends 5% traffic to `order-service-v2` canary; automatic retries only on `idempotent=true` header; Grafana shows golden metrics per service pair without SDK in Ruby legacy app. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Mesh vs ingress gateway overlap?
**A:** Senior answer to 'Mesh vs ingress gateway overlap': tie to ownership, timeouts, and observable failure modes. Data plane (Envoy sidecars or eBPF) + control plane (Istiod). Istio sends 5% traffic to `order-service-v2` canary; automatic retries only on `idempotent=true` header; Grafana shows golden metrics per service pair without SDK in Ruby legacy app. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Debugging 403 from AuthorizationPolicy?
**A:** Senior answer to 'Debugging 403 from AuthorizationPolicy': tie to ownership, timeouts, and observable failure modes. Data plane (Envoy sidecars or eBPF) + control plane (Istiod). Istio sends 5% traffic to `order-service-v2` canary; automatic retries only on `idempotent=true` header; Grafana shows golden metrics per service pair without SDK in Ruby legacy app. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving service mesh (istio/linkerd) value. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **service mesh** adds uniform **mTLS**, observability, retries, timeouts, and traffic splitting as infrastructure — without baking Resilience4j into every service. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Istio sends 5% traffic to `order-service-v2` canary; automatic retries only on `idempotent=true` header; Grafana shows golden metrics per service pair without SDK in Ruby legacy app.

---

### 32. Config and secret distribution.

**Short answer:** **Config** (feature toggles, URLs, pool sizes) belongs in ConfigMaps/parameter store with env-specific values and git review where possible. **Secrets** (DB passwords, API keys) live in Vault/Secrets Manager/K8s Secrets with rotation, never in images or git. Services fetch at startup or via mounted volumes; hot reload for config, not always for secrets. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Separation: config changes often; secrets leak impact is catastrophic. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
External Secrets Operator syncs Vault → K8s Secret. Spring Cloud Config vs K8s-native env injection. Immutable secrets: rotate → rolling restart. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Vault + ESO | .env in repo |
|-------------|--------------|
| Prod always | Never |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Helm values `qa.yaml` / `prod.yaml` in git; DB password from AWS Secrets Manager referenced in ExternalSecret; Spring reads `SPRING_DATASOURCE_PASSWORD` from env. Config refresh via Spring Cloud Kubernetes reload for log levels. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Secrets in application.properties committed to git.
- Same prod/qa credentials "for simplicity."
- Logging config at DEBUG prints connection strings.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Secret rotation without downtime?
**A:** Senior answer to 'Secret rotation without downtime': tie to ownership, timeouts, and observable failure modes. Separation: config changes often; secrets leak impact is catastrophic. Helm values `qa.yaml` / `prod.yaml` in git; DB password from AWS Secrets Manager referenced in ExternalSecret; Spring reads `SPRING_DATASOURCE_PASSWORD` from env. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Config vs secret in feature flags?
**A:** Senior answer to 'Config vs secret in feature flags': tie to ownership, timeouts, and observable failure modes. Separation: config changes often; secrets leak impact is catastrophic. Helm values `qa.yaml` / `prod.yaml` in git; DB password from AWS Secrets Manager referenced in ExternalSecret; Spring reads `SPRING_DATASOURCE_PASSWORD` from env. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Blast radius of compromised K8s Secret?
**A:** Senior answer to 'Blast radius of compromised K8s Secret': tie to ownership, timeouts, and observable failure modes. Separation: config changes often; secrets leak impact is catastrophic. Helm values `qa.yaml` / `prod.yaml` in git; DB password from AWS Secrets Manager referenced in ExternalSecret; Spring reads `SPRING_DATASOURCE_PASSWORD` from env. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving config and secret distribution. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Config** (feature toggles, URLs, pool sizes) belongs in ConfigMaps/parameter store with env-specific values and git review where possible. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Helm values `qa.yaml` / `prod.yaml` in git; DB password from AWS Secrets Manager referenced in ExternalSecret; Spring reads `SPRING_DATASOURCE_PASSWORD` from env.

---

### 33. Multi-region.

**Short answer:** **Multi-region** improves availability and latency but introduces hard problems: data replication lag, split-brain, conflict resolution, and regulatory residency. Patterns: active-passive (failover), active-active with **partitioned tenancy**, or global DB (Spanner/Cockroach) with cost trade-offs. Most teams are single-region until SLO demands otherwise. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Geographic distribution of compute and data with defined RPO/RTO. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Route 53/Geo DNS → nearest region. Postgres logical replication lag → stale reads or conflict writes. Kafka MirrorMaker 2 for cross-region events. Writes often home-region per tenant (`eu-customers` → `eu-west`).

#### When to use / when NOT to use
| Multi-region | Single region |
|--------------|---------------|
| 99.99+ uptime mandate | Team < 20 ops |
| Data residency law | No DR budget |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Active-passive: `us-east` primary, `us-west` warm standby with async replication RPO 30s; failover runbook quarterly tested. EU shard for GDPR — no US replication of PII. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Active-active same SKU inventory without conflict strategy — oversell.
- DNS TTL too high on failover day.
- Cross-region sync calls — latency death.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** CAP during region partition?
**A:** Senior answer to 'CAP during region partition': tie to ownership, timeouts, and observable failure modes. Geographic distribution of compute and data with defined RPO/RTO. Active-passive: `us-east` primary, `us-west` warm standby with async replication RPO 30s; failover runbook quarterly tested. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Kafka multi-region ordering?
**A:** Senior answer to 'Kafka multi-region ordering': tie to ownership, timeouts, and observable failure modes. Geographic distribution of compute and data with defined RPO/RTO. Active-passive: `us-east` primary, `us-west` warm standby with async replication RPO 30s; failover runbook quarterly tested. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Global vs regional sagas?
**A:** For 'Global vs regional sagas': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Route 53/Geo DNS → nearest region. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving multi-region. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Multi-region** improves availability and latency but introduces hard problems: data replication lag, split-brain, conflict resolution, and regulatory residency. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Active-passive: `us-east` primary, `us-west` warm standby with async replication RPO 30s; failover runbook quarterly tested.

---

### 34. Rate limiting and quotas.

**Short answer:** **Rate limiting** protects services from overload and enforces fairness (per API key, IP, tenant). Implement at **gateway** (coarse) and **service** (fine-grained) with token bucket or leaky bucket; return `429` + `Retry-After`. **Quotas** cap daily/monthly usage for billing tiers — often async counted. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Defense against abuse, noisy neighbors, and cascade during incidents. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Redis sliding window counters; Envoy local vs global rate limit; priority queues for premium tenants. Coordinated limiting needs shared store; per-pod limits are uneven under LB. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Limit | Don't |
|-------|-------|
| Public APIs, auth endpoints | Internal service-to-service default throttle |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Partner tier: 100 req/s burst 200 at gateway; `order-service` enforces 10 creates/min per `customerId` to block bot checkout. Dashboard shows quota consumption via Redis + nightly reconcile to billing. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Only gateway limit — attacker bypasses via internal network.
- 429 without Retry-After — client hammers harder.
- Rate limit on health checks blocking orchestrator.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Fairness across tenants?
**A:** Senior answer to 'Fairness across tenants': tie to ownership, timeouts, and observable failure modes. Defense against abuse, noisy neighbors, and cascade during incidents. Partner tier: 100 req/s burst 200 at gateway; `order-service` enforces 10 creates/min per `customerId` to block bot checkout. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Limit vs bulkhead?
**A:** Senior answer to 'Limit vs bulkhead': tie to ownership, timeouts, and observable failure modes. Defense against abuse, noisy neighbors, and cascade during incidents. Partner tier: 100 req/s burst 200 at gateway; `order-service` enforces 10 creates/min per `customerId` to block bot checkout. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Distributed counter consistency?
**A:** Senior answer to 'Distributed counter consistency': tie to ownership, timeouts, and observable failure modes. Defense against abuse, noisy neighbors, and cascade during incidents. Partner tier: 100 req/s burst 200 at gateway; `order-service` enforces 10 creates/min per `customerId` to block bot checkout. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving rate limiting and quotas. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Rate limiting** protects services from overload and enforces fairness (per API key, IP, tenant). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Partner tier: 100 req/s burst 200 at gateway; `order-service` enforces 10 creates/min per `customerId` to block bot checkout.

---

### 35. Poison messages and parking lot.

**Short answer:** A **poison message** fails processing repeatedly (bad schema, bug, toxic data) and blocks partition processing. After N retries, move to **DLQ** (dead-letter queue) or **parking lot** for manual triage — alert, fix, replay. Never infinite retry the same message in production. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Operational pattern for at-least-once consumers. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Kafka: `max.poll.interval`, retry topic, DLT with header `original-topic`. SQS redrive policy. Parking lot DB table for inspection UI. Replay tooling with idempotent consumers.

#### When to use / when NOT to use
Mandatory for any async consumer with side effects. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
`PaymentWebhook` consumer fails on unknown `currency=XXX`; after 3 tries message goes to `payments.DLT`; PagerDuty fires; engineer fixes mapping, replays from DLT with script verifying `eventId` dedup. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- DLQ with no monitoring — silent data loss.
- Replaying without fixing root cause — infinite loop.
- Same retry delay for all errors — no distinction transient vs permanent.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** DLQ vs parking lot naming?
**A:** Senior answer to 'DLQ vs parking lot naming': tie to ownership, timeouts, and observable failure modes. Operational pattern for at-least-once consumers. `PaymentWebhook` consumer fails on unknown `currency=XXX`; after 3 tries message goes to `payments.DLT`; PagerDuty fires; engineer fixes mapping, replays from DLT with script verifying `eventId` dedup. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Who can replay prod messages?
**A:** Senior answer to 'Who can replay prod messages': tie to ownership, timeouts, and observable failure modes. Operational pattern for at-least-once consumers. `PaymentWebhook` consumer fails on unknown `currency=XXX`; after 3 tries message goes to `payments.DLT`; PagerDuty fires; engineer fixes mapping, replays from DLT with script verifying `eventId` dedup. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Schema poison pill detection?
**A:** Senior answer to 'Schema poison pill detection': tie to ownership, timeouts, and observable failure modes. Operational pattern for at-least-once consumers. `PaymentWebhook` consumer fails on unknown `currency=XXX`; after 3 tries message goes to `payments.DLT`; PagerDuty fires; engineer fixes mapping, replays from DLT with script verifying `eventId` dedup. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving poison messages and parking lot. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. A **poison message** fails processing repeatedly (bad schema, bug, toxic data) and blocks partition processing. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `PaymentWebhook` consumer fails on unknown `currency=XXX`; after 3 tries message goes to `payments.DLT`; PagerDuty fires; engineer fixes mapping, replays from DLT with script verifying `eventId` dedup.

---

### 36. Testing strategy pyramid for services.

**Short answer:** **Many** fast unit tests; **some** integration tests with Testcontainers (real DB/Kafka); **contract tests** at each boundary; **few** E2E smokes in staging; **chaos/resilience** tests in non-prod. Per-service CI must not require full ecosystem up — that's why contracts exist. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Test pyramid adapted for distributed systems — inverted pyramid is CI bankruptcy. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Unit: domain logic, saga state machine. Integration: `@SpringBootTest` + Postgres container, Kafka test topic. Pact verify in provider pipeline. E2E: 3–5 golden paths. Synthetic probes in prod optional.

#### When to use / when NOT to use
| Invest in contracts | Skip |
|---------------------|------|
| 10+ services | Solo monolith |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`inventory-service` CI: 800 unit, 40 Testcontainers tests for reservation concurrency, pact verify from `order-service` consumer, no full E2E in PR — nightly pipeline only. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- E2E as only safety net — flaky, slow, ignored reds.
- Mocking Kafka entirely — rebalance bugs slip through.
- No test for compensation/refund paths.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Testcontainers vs embedded Kafka?
**A:** Senior answer to 'Testcontainers vs embedded Kafka': tie to ownership, timeouts, and observable failure modes. Test pyramid adapted for distributed systems — inverted pyramid is CI bankruptcy. `inventory-service` CI: 800 unit, 40 Testcontainers tests for reservation concurrency, pact verify from `order-service` consumer, no full E2E in PR — nightly pipeline only. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to test idempotency?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. **Many** fast unit tests; **some** integration tests with Testcontainers (real DB/Kafka); **contract tests** at each boundary; **few** E2E smokes in staging; **chaos/resilience** tests in non-prod. Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Consumer contract for events?
**A:** Senior answer to 'Consumer contract for events': tie to ownership, timeouts, and observable failure modes. Test pyramid adapted for distributed systems — inverted pyramid is CI bankruptcy. `inventory-service` CI: 800 unit, 40 Testcontainers tests for reservation concurrency, pact verify from `order-service` consumer, no full E2E in PR — nightly pipeline only. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving testing strategy pyramid for services. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Many** fast unit tests; **some** integration tests with Testcontainers (real DB/Kafka); **contract tests** at each boundary; **few** E2E smokes in staging; **chaos/resilience** tests in non-prod. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `inventory-service` CI: 800 unit, 40 Testcontainers tests for reservation concurrency, pact verify from `order-service` consumer, no full E2E in PR — nightly pipeline only.

---

### 37. Observability three pillars + profiling.

**Short answer:** **Metrics** (RED/USE, SLO dashboards), **logs** (structured, correlated traceId), **traces** (distributed latency) — plus **profiling** (CPU, heap, async stalls) when metrics show symptom not cause. Seniors define SLOs per service and runbooks linked from alerts. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Pillars: Prometheus/Datadog metrics, ELK/Loki logs, Jaeger/Tempo traces. Continuous profiling: Pyroscope, async-profiler in JVM. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
RED: Rate, Errors, Duration per endpoint. USE for nodes. Log JSON: `traceId`, `spanId`, `tenantId`. Profile on high CPU pod during incident — often GC or lock contention, not "network."

#### When to use / when NOT to use
Observability is not optional at service #3. Profiling is targeted — not always-on 100% CPU overhead. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
SLO: 99% `POST /orders` < 500ms. Burn rate alert pages on-call. Trace shows DB migration missing index; async profiler confirms not CPU — fix index, not scale pods. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- String logs only — cannot correlate.
- Metrics without labels cardinality control — Prometheus OOM.
- Alert on every error — fatigue, miss real outage.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** RED vs USE?
**A:** Senior answer to 'RED vs USE': tie to ownership, timeouts, and observable failure modes. Pillars: Prometheus/Datadog metrics, ELK/Loki logs, Jaeger/Tempo traces. SLO: 99% `POST /orders` < 500ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Golden signals for Kafka consumer?
**A:** Senior answer to 'Golden signals for Kafka consumer': tie to ownership, timeouts, and observable failure modes. Pillars: Prometheus/Datadog metrics, ELK/Loki logs, Jaeger/Tempo traces. SLO: 99% `POST /orders` < 500ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** When to enable continuous profiling?
**A:** Senior answer to 'When to enable continuous profiling': tie to ownership, timeouts, and observable failure modes. Pillars: Prometheus/Datadog metrics, ELK/Loki logs, Jaeger/Tempo traces. SLO: 99% `POST /orders` < 500ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving observability three pillars + profiling. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Metrics** (RED/USE, SLO dashboards), **logs** (structured, correlated traceId), **traces** (distributed latency) — plus **profiling** (CPU, heap, async stalls) when metrics show symptom not cause. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. SLO: 99% `POST /orders` < 500ms.

---

### 38. SLO vs SLA vs SLI.

**Short answer:** **SLI** is the measured metric (availability, latency p99). **SLO** is internal target (99.9% availability / 30d). **SLA** is contractual promise to customers with remedies — usually stricter SLO buffer. Error budgets from SLO drive release velocity vs reliability trade-offs.

#### What it is
Language for reliability engineering — not interchangeable acronyms. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
SLI: successful requests / total. SLO: SLI ≥ target over window. Error budget = 1 - SLO — when exhausted, freeze features, fix reliability. SLA penalty clause only if SLA breached (often looser than SLO).

#### When to use / when NOT to use
Every production service needs SLOs; SLAs only when legally/commercially required. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
`payment-service` SLO: 99.95% success, p99 < 800ms. Monthly error budget 21 minutes downtime. Burn alert at 2% budget in 1 hour. Customer SLA 99.9% — never triggered because SLO is tighter.

#### Common mistakes
- SLO on CPU not user journeys.
- No multi-window burn alerts — slow leak unnoticed.
- Promising SLA without measuring SLI.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Error budget policy when exhausted?
**A:** Senior answer to 'Error budget policy when exhausted': tie to ownership, timeouts, and observable failure modes. Language for reliability engineering — not interchangeable acronyms. `payment-service` SLO: 99.95% success, p99 < 800ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** SLO for async processing lag?
**A:** Senior answer to 'SLO for async processing lag': tie to ownership, timeouts, and observable failure modes. Language for reliability engineering — not interchangeable acronyms. `payment-service` SLO: 99.95% success, p99 < 800ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Who approves SLO changes?
**A:** Senior answer to 'Who approves SLO changes': tie to ownership, timeouts, and observable failure modes. Language for reliability engineering — not interchangeable acronyms. `payment-service` SLO: 99.95% success, p99 < 800ms. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving slo vs sla vs sli. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **SLI** is the measured metric (availability, latency p99). Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `payment-service` SLO: 99.95% success, p99 < 800ms.

---

### 39. Team topology.

**Short answer:** **Team Topologies** maps teams to architecture: **stream-aligned** teams own features end-to-end; **platform** enables self-service infra; **complicated-subsystem** for ML/fraud; **enabling** coaches adoption. Microservices only work when **Conway's law** is intentional — service boundaries align with team boundaries and cognitive load. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Organizational design for fast flow and clear ownership. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Two-pizza team owns 2–4 services max (rule of thumb). Platform provides golden paths (CI template, K8s namespace, observability). Enabling team helps strangler migration — not permanent staff aug. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Align team/service | Split team across 10 services |
|--------------------|-------------------------------|
| Clear on-call rotation | Everyone on-call for everything |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`Checkout` stream team owns `order`, `cart`, `checkout-bff` — 8 engineers, one PagerDuty rotation. Platform team ships IDP (see Q45). Fraud is complicated-subsystem consulted via API. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy.

#### Common mistakes
- Component teams (DB team, API team) — handoffs kill velocity.
- 3 engineers, 25 services — ownership theater.
- Platform team as ticket queue without self-service.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Inverse Conway maneuver?
**A:** Senior answer to 'Inverse Conway maneuver': tie to ownership, timeouts, and observable failure modes. Organizational design for fast flow and clear ownership. `Checkout` stream team owns `order`, `cart`, `checkout-bff` — 8 engineers, one PagerDuty rotation. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Shared on-call across teams?
**A:** Senior answer to 'Shared on-call across teams': tie to ownership, timeouts, and observable failure modes. Organizational design for fast flow and clear ownership. `Checkout` stream team owns `order`, `cart`, `checkout-bff` — 8 engineers, one PagerDuty rotation. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** When to split a team?
**A:** 'When to split a team' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. Organizational design for fast flow and clear ownership. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving team topology. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Team Topologies** maps teams to architecture: **stream-aligned** teams own features end-to-end; **platform** enables self-service infra; **complicated-subsystem** for ML/fraud; **enabling** coaches adoption. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `Checkout` stream team owns `order`, `cart`, `checkout-bff` — 8 engineers, one PagerDuty rotation.

---

### 40. Strangler: routing layer.

**Short answer:** The **strangler fig** migrates monolith incrementally: a **routing layer** (gateway, proxy, feature flag) sends some routes to new service, rest to legacy. Grow new paths until monolith is hollow, then decommission. Routing is the control surface — get it right before extracting code. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Pattern for incremental modernization without big-bang rewrite. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
NGINX/Envoy rules: `/api/v2/orders` → `order-service`; `/api/v1/*` → monolith. Session affinity if needed. Dual-write period with reconciliation job. Metrics compare error rates old vs new path.

#### When to use / when NOT to use
| Strangler | Big-bang rewrite |
|-----------|------------------|
| Revenue system running | Greenfield with no users |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
10% traffic `createOrder` routed to new service via header `X-Route: new` for internal testers, then 50/50 canary, then 100% over 6 weeks. Monolith code path deleted when Kafka consumer lag zero for backfill. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Extract service without routing — parallel APIs confuse clients.
- No parity metrics — silent data divergence.
- Strangler without data migration plan.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Dual-write vs read from new write to old?
**A:** Senior answer to 'Dual-write vs read from new write to old': tie to ownership, timeouts, and observable failure modes. Pattern for incremental modernization without big-bang rewrite. 10% traffic `createOrder` routed to new service via header `X-Route: new` for internal testers, then 50/50 canary, then 100% over 6 weeks. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to route authenticated sessions?
**A:** Senior answer to 'How to route authenticated sessions': tie to ownership, timeouts, and observable failure modes. Pattern for incremental modernization without big-bang rewrite. 10% traffic `createOrder` routed to new service via header `X-Route: new` for internal testers, then 50/50 canary, then 100% over 6 weeks. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Rollback strategy during canary?
**A:** Senior answer to 'Rollback strategy during canary': tie to ownership, timeouts, and observable failure modes. Pattern for incremental modernization without big-bang rewrite. 10% traffic `createOrder` routed to new service via header `X-Route: new` for internal testers, then 50/50 canary, then 100% over 6 weeks. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving strangler: routing layer. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. The **strangler fig** migrates monolith incrementally: a **routing layer** (gateway, proxy, feature flag) sends some routes to new service, rest to legacy. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. 10% traffic `createOrder` routed to new service via header `X-Route: new` for internal testers, then 50/50 canary, then 100% over 6 weeks.

---

### 41. Backpressure across services.

**Short answer:** **Backpressure** signals upstream to slow down when downstream is saturated — bounded queues, HTTP 503 with retry, reactive `request(n)`, Kafka consumer pause. Without it, slow services accumulate memory, threads, and timeouts that amplify outages. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Flow control in distributed pipelines — not only reactive programming buzzword. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Thread pool full → reject fast. Kafka: `pause()` partitions when DB write lag high. gRPC streaming flow control windows. Caller respects `Retry-After`. Bulkhead prevents one pipeline from starving others.

#### When to use / when NOT to use
| Bounded queues | Unbounded LinkedBlockingQueue |
|----------------|-------------------------------|
| Always for async workers | Never |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`notification-service` pauses Kafka consumption when SendGrid rate limit hit; lag grows safely vs OOM. Upstream `order-service` sees growing lag alert and sheds non-critical marketing sends. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Infinite queue "to never drop messages" — drops whole JVM instead.
- No signal to upstream — retry storm.
- Blocking calls on event loop thread.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Backpressure vs rate limit?
**A:** Senior answer to 'Backpressure vs rate limit': tie to ownership, timeouts, and observable failure modes. Flow control in distributed pipelines — not only reactive programming buzzword. `notification-service` pauses Kafka consumption when SendGrid rate limit hit; lag grows safely vs OOM. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Kafka consumer lag as pressure signal?
**A:** Senior answer to 'Kafka consumer lag as pressure signal': tie to ownership, timeouts, and observable failure modes. Flow control in distributed pipelines — not only reactive programming buzzword. `notification-service` pauses Kafka consumption when SendGrid rate limit hit; lag grows safely vs OOM. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Project Reactor `onBackpressureBuffer` risks?
**A:** Senior answer to 'Project Reactor `onBackpressureBuffer` risks': tie to ownership, timeouts, and observable failure modes. Flow control in distributed pipelines — not only reactive programming buzzword. `notification-service` pauses Kafka consumption when SendGrid rate limit hit; lag grows safely vs OOM. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving backpressure across services. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Backpressure** signals upstream to slow down when downstream is saturated — bounded queues, HTTP 503 with retry, reactive `request(n)`, Kafka consumer pause. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `notification-service` pauses Kafka consumption when SendGrid rate limit hit; lag grows safely vs OOM.

---

### 42. Time and clocks.

**Short answer:** **Never rely on wall-clock sync across services** for ordering — clocks skew. Use **logical clocks** (Kafka offset, DB `version`, Lamport/event sequence) or **central time source** for human display only. TTLs and token expiry need NTP discipline and margin; "last-write-wins" across regions with skew loses data. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Distributed systems time pitfalls: NTP drift, leap seconds, different TZ in logs. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Prefer `occurredAt` from producer with skepticism; use `ingestedAt` and monotonic `sequence` per aggregate. JWT `exp` leeway 30s. Scheduled jobs: leader election or external scheduler (Quartz JDBC), not `if (now() == 2am)` per pod. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Version column / event log order | `updated_at` compare across services |
|----------------------------------|--------------------------------------|
| Conflict resolution | Cross-DC last-write-wins |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Inventory conflict: reject if `request.version < current.version` — not `request.timestamp > row.timestamp`. Saga timeout uses workflow engine durable timer, not `Thread.sleep` in pod. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Distributed cron on every replica — duplicate charges.
- Assuming `Instant.now()` matches across JVMs for lease.
- Sorting events by `created_at` from two DBs.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** TrueTime / Spanner clock trust?
**A:** Senior answer to 'TrueTime / Spanner clock trust': tie to ownership, timeouts, and observable failure modes. Distributed systems time pitfalls: NTP drift, leap seconds, different TZ in logs. Inventory conflict: reject if `request.version < current.version` — not `request.timestamp > row.timestamp`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Kafka message time vs processing time?
**A:** Senior answer to 'Kafka message time vs processing time': tie to ownership, timeouts, and observable failure modes. Distributed systems time pitfalls: NTP drift, leap seconds, different TZ in logs. Inventory conflict: reject if `request.version < current.version` — not `request.timestamp > row.timestamp`. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Idempotency TTL vs clock skew?
**A:** Effectively-once means idempotent handlers plus dedup store at boundaries — HTTP idempotency keys and consumer processed_events tables. **Never rely on wall-clock sync across services** for ordering — clocks skew. Store keys with unique constraint scoped to tenant and operation; TTL 24–72 hours typical for POST. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving time and clocks. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Never rely on wall-clock sync across services** for ordering — clocks skew. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Inventory conflict: reject if `request.version < current.version` — not `request.timestamp > row.timestamp`.

---

### 43. GDPR / PII across services.

**Short answer:** **PII minimization**: each service stores only what it needs; propagate **pseudonymous IDs** not emails in events. **Right to erasure** requires orchestrated delete/anonymize across owned data and downstream projections — document in ROPA, automate with `CustomerDeleted` events and retention jobs. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Legal and architectural cross-cutting concern — not "DPO's problem" only. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Data map: which service holds what PII. Erasure saga: order history anonymized, logs redacted, warehouse crypto-shred keys. Consent flags not copied to analytics without legal basis. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
Design privacy in boundaries — retrofitting GDPR across 40 services is expensive. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
`customer-service` owns email; others store `customerId` only. `DELETE /customers/{id}` triggers events; search index tombstones; S3 objects lifecycle-deleted; proof stored in audit service without PII. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Email in every Kafka topic "for convenience."
- Logs print full request bodies with credit cards.
- No retention TTL on backups — erasure incomplete.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Anonymize vs delete orders?
**A:** Senior answer to 'Anonymize vs delete orders': tie to ownership, timeouts, and observable failure modes. Legal and architectural cross-cutting concern — not "DPO's problem" only. `customer-service` owns email; others store `customerId` only. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Cross-border replication restrictions?
**A:** Senior answer to 'Cross-border replication restrictions': tie to ownership, timeouts, and observable failure modes. Legal and architectural cross-cutting concern — not "DPO's problem" only. `customer-service` owns email; others store `customerId` only. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** DPIA for new microservice?
**A:** Senior answer to 'DPIA for new microservice': tie to ownership, timeouts, and observable failure modes. Legal and architectural cross-cutting concern — not "DPO's problem" only. `customer-service` owns email; others store `customerId` only. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving gdpr / pii across services. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **PII minimization**: each service stores only what it needs; propagate **pseudonymous IDs** not emails in events. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `customer-service` owns email; others store `customerId` only.

---

### 44. Feature flags in microservices.

**Short answer:** **Feature flags** decouple deploy from release — ship code dark, enable per tenant/region gradually. In microservices, use **consistent evaluation context** (same user → same variant across services) via shared flag service (LaunchDarkly, Unleash, App Config). Flags are not a substitute for API versioning or DB expand/contract. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Runtime toggles for behavior, experiments, and kill switches. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs. Sagas commit locally at each step; compensation is a new business operation, not a distributed ROLLBACK. The transactional outbox writes the event in the same database transaction as the aggregate change, avoiding dual-write races.

#### When to use / when NOT to use
| Flags | Not flags |
|-------|-----------|
| Gradual rollout, A/B | Permanent config |
| Emergency off switch | Hiding unfinished schema migration |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`new-payment-provider` flag 1% → 10% → 100% over 2 weeks; metrics compare success rate; instant off during incident. BFF and `order-service` read same flag key from Unleash. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Different flag defaults per service — split brain UX.
- 200 stale flags nobody owns.
- Flag check in 15 places — use strategy pattern or single decision point.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Flag vs canary deployment?
**A:** Senior answer to 'Flag vs canary deployment': tie to ownership, timeouts, and observable failure modes. Runtime toggles for behavior, experiments, and kill switches. `new-payment-provider` flag 1% → 10% → 100% over 2 weeks; metrics compare success rate; instant off during incident. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Testing with flags in CI?
**A:** Senior answer to 'Testing with flags in CI': tie to ownership, timeouts, and observable failure modes. Runtime toggles for behavior, experiments, and kill switches. `new-payment-provider` flag 1% → 10% → 100% over 2 weeks; metrics compare success rate; instant off during incident. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Compliance audit of who toggled prod?
**A:** Senior answer to 'Compliance audit of who toggled prod': tie to ownership, timeouts, and observable failure modes. Runtime toggles for behavior, experiments, and kill switches. `new-payment-provider` flag 1% → 10% → 100% over 2 weeks; metrics compare success rate; instant off during incident. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving feature flags in microservices. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Feature flags** decouple deploy from release — ship code dark, enable per tenant/region gradually. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `new-payment-provider` flag 1% → 10% → 100% over 2 weeks; metrics compare success rate; instant off during incident.

---

### 45. Internal developer platform (IDP).

**Short answer:** An **IDP** is the paved road: golden-path templates to create a service (repo, CI, K8s namespace, observability, secrets), self-service not tickets. Good IDP encodes organizational standards — database per service, pact in pipeline, SLO dashboards — so teams ship safely without reinventing Jenkins. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Platform engineering product for devs; Backstage, Cortex, custom portals. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Service catalog registers owners, dependencies, SLOs. Scaffolder creates `spring-service` from Cookiecutter with prewired OTel, Flyway, health checks. Platform measures adoption and toil reduction. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| IDP at 15+ devs | Custom snowflake per team |
|-----------------|---------------------------|
| Repeated microservice boilerplate | |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Developer runs `backstage create microservice` → gets repo with GHA, Helm chart, Argo app, Datadog monitors, Pact stub — first deploy to dev in <1 day. Exceptions documented via ADR. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Platform team builds ivory tower nobody uses.
- Mandatory IDP blocks without escape hatch for edge cases.
- No versioning of template — breaking all new services.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Platform vs enabling team?
**A:** Senior answer to 'Platform vs enabling team': tie to ownership, timeouts, and observable failure modes. Platform engineering product for devs; Backstage, Cortex, custom portals. Developer runs `backstage create microservice` → gets repo with GHA, Helm chart, Argo app, Datadog monitors, Pact stub — first deploy to dev in <1 day. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to measure IDP success?
**A:** Senior answer to 'How to measure IDP success': tie to ownership, timeouts, and observable failure modes. Platform engineering product for devs; Backstage, Cortex, custom portals. Developer runs `backstage create microservice` → gets repo with GHA, Helm chart, Argo app, Datadog monitors, Pact stub — first deploy to dev in <1 day. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Thin wrapper vs opinionated framework?
**A:** Senior answer to 'Thin wrapper vs opinionated framework': tie to ownership, timeouts, and observable failure modes. Platform engineering product for devs; Backstage, Cortex, custom portals. Developer runs `backstage create microservice` → gets repo with GHA, Helm chart, Argo app, Datadog monitors, Pact stub — first deploy to dev in <1 day. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving internal developer platform (idp). shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. An **IDP** is the paved road: golden-path templates to create a service (repo, CI, K8s namespace, observability, secrets), self-service not tickets. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Developer runs `backstage create microservice` → gets repo with GHA, Helm chart, Argo app, Datadog monitors, Pact stub — first deploy to dev in <1 day.

---

### 46. How many lines of code per service?

**Short answer:** There is no magic number — optimize for **team cognitive load** and **cohesion**, not LOC. Rule of thumb: a service should be explainable on one whiteboard; if it needs a wiki chapter, consider splitting by bounded context. Tiny "nanoservices" (200 LOC) often cost more in ops than they save in clarity. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Heuristic interview question — tests judgment over dogma. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Factors: deploy frequency, test suite time, on-call pain, distinct scale profile. Amazon "two-pizza" anecdote ≠ 200 LOC services. Cohesive domain module might be 20k LOC in one service if one team owns it. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Split when cohesion low | Keep together when |
|-------------------------|-------------------|
| Unrelated change reasons | Same aggregate lifecycle |
| Different SLAs | Refactor would net negative |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
`notification-email` and `notification-sms` merged into `notification-service` — shared templating, one on-call, 15k LOC total. Previously 800 LOC services × 4 duplicated infra. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- LOC target from executive dashboard.
- Splitting CRUD tables into services.
- Never merging overgrown services.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Nanoservices anti-pattern?
**A:** Senior answer to 'Nanoservices anti-pattern': tie to ownership, timeouts, and observable failure modes. Heuristic interview question — tests judgment over dogma. `notification-email` and `notification-sms` merged into `notification-service` — shared templating, one on-call, 15k LOC total. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Metrics besides LOC?
**A:** Senior answer to 'Metrics besides LOC': tie to ownership, timeouts, and observable failure modes. Heuristic interview question — tests judgment over dogma. `notification-email` and `notification-sms` merged into `notification-service` — shared templating, one on-call, 15k LOC total. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** When did you merge services?
**A:** Senior answer to 'When did you merge services': tie to ownership, timeouts, and observable failure modes. Heuristic interview question — tests judgment over dogma. `notification-email` and `notification-sms` merged into `notification-service` — shared templating, one on-call, 15k LOC total. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving how many lines of code per service? shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. There is no magic number — optimize for **team cognitive load** and **cohesion**, not LOC. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. `notification-email` and `notification-sms` merged into `notification-service` — shared templating, one on-call, 15k LOC total.

---

### 47. Spring Cloud vs Kubernetes-native.

**Short answer:** **Spring Cloud** (Eureka, Config, Gateway, Sleuth) made sense on VMs — clients handled discovery, config, resilience in JVM. On **Kubernetes**, DNS, ConfigMaps, Ingress, and mesh often replace Netflix stack; keep Spring for app logic, Resilience4j where needed, OTel for traces. Don't run Eureka on K8s "because we always did." The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Framework convenience vs platform primitives — evolving best practice. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Spring Cloud K8s: discovery via `spring.cloud.kubernetes`, config from ConfigMap. Remove Eureka/Ribbon — use K8s Service + Spring `RestClient`. Sleuth → Micrometer Tracing + OTel exporter. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| K8s-native | Spring Cloud Netflix |
|------------|----------------------|
| Greenfield on AKS/EKS | Brownfield VM fleet |
| Platform enforces mesh/policy | |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Migration: retire Eureka, URLs become K8s DNS; Spring Cloud Config replaced by External Secrets + Helm values; Hystrix already gone → Resilience4j; traces via OTel Java agent, no Zipkin server to maintain. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks. Service catalog entries document owning team, SLO, dependencies, and the runbook for stuck sagas or DLQ replay.

#### Common mistakes
- Triple discovery: Eureka + K8s + mesh labels conflict.
- Spring Cloud Gateway duplicating Istio ingress features without reason.
- Config server SPOF less reliable than git+Helm.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** What from Spring Cloud still valuable?
**A:** Senior answer to 'What from Spring Cloud still valuable': tie to ownership, timeouts, and observable failure modes. Framework convenience vs platform primitives — evolving best practice. Migration: retire Eureka, URLs become K8s DNS; Spring Cloud Config replaced by External Secrets + Helm values; Hystrix already gone → Resilience4j; traces via OTel Java agent, no Zipkin server to maintain. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Spring Cloud Stream vs raw Kafka client?
**A:** Senior answer to 'Spring Cloud Stream vs raw Kafka client': tie to ownership, timeouts, and observable failure modes. Framework convenience vs platform primitives — evolving best practice. Migration: retire Eureka, URLs become K8s DNS; Spring Cloud Config replaced by External Secrets + Helm values; Hystrix already gone → Resilience4j; traces via OTel Java agent, no Zipkin server to maintain. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Local dev without K8s?
**A:** Senior answer to 'Local dev without K8s': tie to ownership, timeouts, and observable failure modes. Framework convenience vs platform primitives — evolving best practice. Migration: retire Eureka, URLs become K8s DNS; Spring Cloud Config replaced by External Secrets + Helm values; Hystrix already gone → Resilience4j; traces via OTel Java agent, no Zipkin server to maintain. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving spring cloud vs kubernetes-native. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Spring Cloud** (Eureka, Config, Gateway, Sleuth) made sense on VMs — clients handled discovery, config, resilience in JVM. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Migration: retire Eureka, URLs become K8s DNS; Spring Cloud Config replaced by External Secrets + Helm values; Hystrix already gone → Resilience4j; traces via OTel Java agent, no Zipkin server to maintain.

---

### 48. Failure injection.

**Short answer:** **Chaos engineering** (Gremlin, Litmus, Toxiproxy) proactively breaks dependencies in controlled environments to verify retries, breakers, and runbooks — not random prod destruction. Start with game days: kill pod, inject latency to payment stub, verify no data corruption. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries. When this fails in production, symptoms appear as consumer lag, duplicate charges, cascading timeouts, or undeployable coordinated migrations.

#### What it is
Experiments with hypothesis: "If inventory is down 30s, checkout degrades gracefully." The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Fault injection: network delay, 500 errors, DNS failure, pod kill, CPU stress. Observe SLO burn, alert routing, idempotency. Automate in staging weekly; prod blast radius tiny with abort switches. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads.

#### When to use / when NOT to use
| Staging chaos | Prod chaos without guardrails |
|---------------|-------------------------------|
| Before peak season | |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
Toxiproxy between staging `order` and `payment` adds 5s latency — tests timeout and user messaging. Litmus kills random `catalog` pod during load test — HPA recovers, no 500 spike at gateway. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Chaos only kills pods — never tests dependency failure.
- No hypothesis — just breaking things for sport.
- Injecting prod without executive buy-in and abort budget.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** Chaos vs traditional load test?
**A:** Senior answer to 'Chaos vs traditional load test': tie to ownership, timeouts, and observable failure modes. Experiments with hypothesis: "If inventory is down 30s, checkout degrades gracefully." Toxiproxy between staging `order` and `payment` adds 5s latency — tests timeout and user messaging. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Safe prod experiments?
**A:** Senior answer to 'Safe prod experiments': tie to ownership, timeouts, and observable failure modes. Experiments with hypothesis: "If inventory is down 30s, checkout degrades gracefully." Toxiproxy between staging `order` and `payment` adds 5s latency — tests timeout and user messaging. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How to verify saga compensation under fault?
**A:** For 'How to verify saga compensation under fault': orchestrate money paths with compensations and timeouts; choreograph simple fan-out notifications. Fault injection: network delay, 500 errors, DNS failure, pod kill, CPU stress. Compensation is a new idempotent business operation — not DELETE FROM. Support tooling must show saga state by correlation ID. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving failure injection. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. **Chaos engineering** (Gremlin, Litmus, Toxiproxy) proactively breaks dependencies in controlled environments to verify retries, breakers, and runbooks — not random prod destruction. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. Toxiproxy between staging `order` and `payment` adds 5s latency — tests timeout and user messaging.

---

### 49. Documentation that seniors leave behind.

**Short answer:** Seniors document **decisions (ADRs)**, **ownership (catalog)**, **SLOs/runbooks**, **data maps**, and **onboarding paths** — not 500-page Word specs. Living docs: diagram of sync/async flows, event catalog, "how to rollback payment-service", compatibility policy. If it's not in git near the code, it rots. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Operational and architectural knowledge transfer — force multiplier for org. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
ADR: context, decision, consequences. Service catalog (Backstage): owner, tier, dependencies, dashboards. Event catalog: schema link, producers, consumers, PII classification. Runbook: alert → investigate → mitigate → escalate.

#### When to use / when NOT to use
Write docs when boundaries change or incidents reveal gaps — not documentation theater before coding. Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved). Use choreography for simple fan-out side effects; orchestrate money paths with compensations, deadlines, and audit requirements.

#### Production example
ADR-042: "Choreography for notifications, orchestration for payments" — linked from `order-service` README. Incident after missing doc → added runbook "stuck saga compensation" with SQL queries and Temporal UI steps. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- Wiki nobody can find; no review on PR.
- Diagram lying — shows sync only, omits Kafka.
- No event ownership — "who publishes CustomerUpdated?"
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** ADR vs RFC?
**A:** Senior answer to 'ADR vs RFC': tie to ownership, timeouts, and observable failure modes. Operational and architectural knowledge transfer — force multiplier for org. ADR-042: "Choreography for notifications, orchestration for payments" — linked from `order-service` README. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How keep diagrams current?
**A:** Senior answer to 'How keep diagrams current': tie to ownership, timeouts, and observable failure modes. Operational and architectural knowledge transfer — force multiplier for org. ADR-042: "Choreography for notifications, orchestration for payments" — linked from `order-service` README. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Docs for erasure/GDPR?
**A:** Senior answer to 'Docs for erasure/GDPR': tie to ownership, timeouts, and observable failure modes. Operational and architectural knowledge transfer — force multiplier for org. ADR-042: "Choreography for notifications, orchestration for payments" — linked from `order-service` README. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving documentation that seniors leave behind. shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. Seniors document **decisions (ADRs)**, **ownership (catalog)**, **SLOs/runbooks**, **data maps**, and **onboarding paths** — not 500-page Word specs. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. ADR-042: "Choreography for notifications, orchestration for payments" — linked from `order-service` README.

---

### 50. 10-year answer to "we need microservices."

**Short answer:** "Why?" — If the answer is resume-driven or "Netflix does it," push back. If bounded contexts, team scale, deploy independence, or compliance isolation are real, plan **modular monolith → strangler → services** with data ownership, observability, and contract tests from day one. Microservices are a **means** (organizational and operational scalability), not the goal; many successful systems stay modular monoliths for a decade. The senior trade-off is autonomy and blast-radius isolation versus operational complexity and eventual consistency across boundaries.

#### What it is
Capstone judgment question — seniority is restraint and roadmap, not hype. The decision is organizational as much as technical: Conway's law means runtime boundaries tend to mirror how teams communicate unless domain modeling is deliberate. Interviewers want data ownership, failure modes, and the user-visible consistency guarantee — not just the message broker brand.

#### How it works (internals)
Evaluate: team topology, ops maturity, domain clarity, cost of distribution. Roadmap: extract highest-value boundary first (payments, search), platform golden path, measure deploy frequency and MTTR — not service count. Synchronous calls chain latency and failure: total p99 approximates the sum of downstream p99 unless you parallelize with tight timeouts and bulkheads. Asynchronous integration trades temporal coupling for duplication, ordering, and consumer lag — handlers must be idempotent with correlation IDs.

#### When to use / when NOT to use
| Honest yes | Honest no |
|------------|-----------|
| Conway pain, clear contexts | Small team, unclear domain |
| Regulatory isolation | "Kubernetes is cool" |

Extract a service when a bounded context has a clear owner, independent deploy cadence, and a concrete pain that boundaries solve. Keep user-facing commit decisions synchronous when the caller waits for a definitive answer (payment authorized, stock reserved).

#### Production example
CTO asks for microservices. You propose 12-month plan: modular monolith boundaries, IDP, first extraction of `billing` after team grows, success metrics = weekly deploys and <30min incident MTTR — revisit service count quarterly. Contract tests and schema compatibility checks in CI catch breaking API or event changes before production deploy. Game days inject latency and 5xx errors between staging services to validate circuit breakers, idempotency stores, and saga compensation runbooks.

#### Common mistakes
- All-or-nothing microservices mandate.
- No success criteria — can't answer "are we better?"
- Ignoring cost: 10 services ≈ 10 on-call rotations without platform.
- Treating the pattern as ceremony without measuring SQL or consumer lag in staging.

#### Interview follow-ups (with model answers)

**Q:** What would you extract first in our domain?
**A:** 'What would you extract first in our domain' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. Capstone judgment question — seniority is restraint and roadmap, not hype. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** How do you say no to executives?
**A:** Senior answer to 'How do you say no to executives': tie to ownership, timeouts, and observable failure modes. Capstone judgment question — seniority is restraint and roadmap, not hype. CTO asks for microservices. Validate with contract tests, correlation IDs across HTTP and Kafka, and dashboards for consumer lag. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

**Q:** Modular monolith libraries you'd use?
**A:** 'Modular monolith libraries you'd use' — look for change coupling, data ownership, and team on-call alignment before drawing a service line. Capstone judgment question — seniority is restraint and roadmap, not hype. Strangler extraction: dual-write or CDC, switch reads, cut writes, retire shared table access — with contract tests at each phase. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic. Document trade-offs in a short runbook and add an integration test so dialect-specific or boundary failures are caught before peak traffic.

#### Scenario probe
During peak traffic, a flow involving 10-year answer to "we need microservices." shows stuck orders, duplicate side effects, or cascading 503s; support traces one correlation ID across HTTP and Kafka.

**Model answer:** I triage integration first: consumer lag, DLQ depth, missing idempotency hits, timeout chains, and saga state. "Why?" — If the answer is resume-driven or "Netflix does it," push back. Short-term: tighten HTTP timeouts, review circuit breakers, pause risky retries, scale consumers. Long-term: outbox, contract tests, explicit orchestration on money paths, and ADR-documented consistency. CTO asks for microservices.

---

## Deep-dive additions (Q51–Q58)

Senior topics: chaos engineering, service mesh, cell-based isolation, API composition patterns, zero-trust on Azure, event governance, Pact in CI, and modular-monolith escape hatches.

---

### 51. Chaos engineering with Chaos Mesh / Litmus on Kubernetes

**Short answer:** Chaos engineering deliberately injects failures (pod kill, network delay, DNS failure) in controlled environments to prove resilience assumptions before customers find them. **Chaos Mesh** (CNCF) and **Litmus** run experiments as Kubernetes CRDs — schedule `PodChaos`, `NetworkChaos`, or workflow steps against labeled namespaces. Start in staging with blast-radius limits and abort conditions; graduate to game days in prod with SLO guardrails. The trade-off is operational noise and false alarms if you chaos-test without observability and runbooks.

#### What it is
Chaos engineering validates that retries, circuit breakers, outbox relays, and saga timeouts actually work under real failure modes — not just on paper. Chaos Mesh (PingCAP) and Litmus (CNCF) integrate with Kubernetes RBAC, Prometheus, and CI pipelines. They sit above your microservices stack as an experimentation layer, complementary to integration tests that mock failures.

#### How it works (internals)
You define an **Experiment** CRD: selector (namespace, label `app=payment-service`), action (`pod-kill`, `network-delay`, `io-chaos`), duration, and `mode` (one, all, fixed-percent). Chaos Mesh uses `chaos-daemon` on nodes to apply tc/netem or cgroup faults; Litmus uses `chaos-runner` workflows with probe steps (HTTP health, Prometheus query) that auto-abort if error rate exceeds threshold. Experiments run on a schedule or via GitOps; results export to Grafana/Loki. Spring services should expose dependency health metrics so probes correlate user impact.

#### When to use / when NOT to use
Use when you have tracing, SLO dashboards, and on-call runbooks — chaos without observability is vandalism. Start with pod failure and dependency latency before AZ loss simulations. Skip if the platform team cannot stop experiments quickly or if staging does not mirror prod topology (single-node minikube teaches little about mesh retries). In regulated environments, document experiments and restrict prod to approved windows.

#### Production example
Before Black Friday, the platform team runs Litmus workflows in staging: kill 30% of `inventory-service` pods while checkout load test runs at 2× peak. They discover `RestClient` retries without jitter saturate payment threads — fix bulkhead pools and add retry cap. In prod game day (Tuesday 10:00 UTC), they run `PodChaos` on one `catalog-service` pod with abort if checkout p95 > 800ms; no customer impact because HPA and circuit breakers behave as designed. Post-game ADR updates retry defaults in the golden path template.

#### Common mistakes
- Chaos in prod without abort probes tied to error rate or latency SLOs.
- Killing pods while a deployment is mid-rollout — confuses root cause.
- No hypothesis ("we think payment is resilient") — just breaking things randomly.
- Ignoring stateful workloads (Kafka, DB) — coordinate with data platform before IO chaos.

#### Interview follow-ups (with model answers)

**Q:** How is chaos different from integration tests with WireMock?
**A:** Integration tests prove code paths against simulated failures in CI — fast, deterministic, narrow scope. Chaos validates the **running system**: real kube-dns, real mesh retries, real HPA timing, and operator reactions. WireMock will not catch a misconfigured `PodDisruptionBudget` or a readiness probe that passes while the app cannot serve traffic. Use both: contract and fault-injection tests in CI; chaos in staging/prod for emergent behavior. I schedule chaos after deploy to staging, never as a substitute for unit tests.

**Q:** What guardrails do you require before prod chaos?
**A:** Explicit abort conditions (Prometheus: `http_server_requests_seconds_count{status=~"5.."} rate > 2% for 2m`), on-call staffed, experiment limited to one bounded context, rollback runbook tested, and business approval for customer-facing hours. RBAC restricts who can create `ChaosEngine` in prod namespaces. I log experiment start/end in the incident channel and cap blast radius to one cell or one deployment at a time.

#### Scenario probe
Staging chaos kills the leader pod of `order-service` during a load test; checkout error rate stays flat but Kafka consumer lag doubles within three minutes.

**Model answer:** Hypothesis: order API is stateless and HPA recovers, but the outbox relay ran on the killed pod and did not resume fast enough. Check relay metrics, `PodDisruptionBudget`, and whether relay is a Deployment singleton vs part of every pod. Fix: run outbox relay as separate worker Deployment with its own HPA, or use Debezium CDC so relay is not tied to API pods. Re-run chaos with lag alert as abort probe.

#### Code / config (when useful)

```yaml
# Litmus ChaosEngine — pod delete with abort probe
apiVersion: litmuschaos.io/v1alpha1
kind: ChaosEngine
metadata:
  name: payment-pod-kill
spec:
  appinfo:
    appns: prod
    applabel: app=payment-service
    appkind: deployment
  chaosServiceAccount: litmus-admin
  experiments:
    - name: pod-delete
      spec:
        components:
          env:
            - name: TOTAL_CHAOS_DURATION
              value: "120"
            - name: PODS_AFFECTED_PERC
              value: "25"
```

---

### 52. Service mesh: Istio traffic management, mTLS, retries at mesh layer

**Short answer:** A **service mesh** (Istio, Linkerd) injects sidecar proxies (Envoy) beside each pod to handle L4/L7 traffic: mTLS, retries, timeouts, traffic splitting, and telemetry without changing application code. Istio's **VirtualService** and **DestinationRule** configure retries and circuit breaking at the mesh layer — but blind retries on non-idempotent POSTs cause duplicate charges. mTLS is often **PERMISSIVE** then **STRICT** per namespace. The trade-off is operational complexity and added latency (~1–3ms per hop) versus uniform policy and zero-trust east-west traffic.

#### What it is
Istio control plane (`istiod`) pushes config to Envoy sidecars; data plane handles all pod-to-pod traffic. **PeerAuthentication** enforces mTLS mode; **AuthorizationPolicy** restricts which identities can call which services. For Java teams, mesh retries can duplicate Spring `@Retryable` — you must choose one layer or align policies. Mesh excels when many polyglot services need consistent TLS and observability without each team implementing filters.

#### How it works (internals)
Outbound requests from the app go to localhost Envoy (`15001`); Envoy picks upstream endpoints from Kubernetes Endpoints, applies **DestinationRule** (connection pool, outlier detection), and **VirtualService** (match, rewrite, retry, fault injection). mTLS uses SPIFFE IDs in X.509 certs rotated by istiod. Retries: `retries: { attempts: 3, perTryTimeout: 2s, retryOn: 5xx,connect-failure,refused-stream }` — Envoy retries at HTTP layer before response reaches the app. Access logs and metrics export to Prometheus without Micrometer changes if headers propagated.

#### When to use / when NOT to use
Use mesh when you have 10+ services, need uniform mTLS and traffic shifting for canaries, or cannot trust every team to implement timeouts correctly. Avoid mesh on very small clusters or latency-sensitive paths where sidecar cost matters unless you use ambient mesh (Istio CNI) or eBPF alternatives. Do not enable mesh-wide retries on payment POST without idempotency keys — application layer must own that.

#### Production example
`checkout-service` calls `pricing-service` over mesh with **STRICT** mTLS in `prod` namespace. Platform sets global **DestinationRule** outlier detection (eject after 5 consecutive 5xx). For canary, **VirtualService** sends 5% traffic to `pricing-service-canary` subset. Java apps keep Resilience4j for business-level bulkheads; mesh handles TLS and connect-timeout only — documented in golden path to avoid double retries. Distributed traces show Envoy span parented under Spring span when `b3` headers propagated.

#### Common mistakes
- Mesh retries + application retries = retry storm on slow dependency.
- PERMISSIVE mTLS left forever — plaintext bypass remains.
- VirtualService host typos route traffic to blackhole.
- Ignoring sidecar resource requests — OOM during traffic spikes.

#### Interview follow-ups (with model answers)

**Q:** Istio retry vs Resilience4j — who wins?
**A:** Pick one layer for automatic retries on idempotent operations. I prefer Resilience4j in Java for business-aware retry (idempotency key check, custom backoff) and mesh for mTLS, traffic split, and connect-timeout only. If mesh must retry, disable app retries on that client and document in ADR. For GET/read paths, mesh retries are fine with `perTryTimeout` shorter than client timeout.

**Q:** How do you roll out STRICT mTLS without outage?
**A:** Phase 1: PERMISSIVE everywhere, verify all workloads have sidecars injected. Phase 2: namespace-by-namespace STRICT, starting with low-risk internal tools; monitor `istio_requests_total{response_flags="UF"}` (upstream connection failure). Phase 3: deny plaintext via AuthorizationPolicy. Rollback: revert PeerAuthentication to PERMISSIVE for one namespace. Java apps using raw IP or headless services need Service entries reviewed.

#### Scenario probe
After enabling Istio retries on `inventory-service`, support sees duplicate stock reservations during brief 503 bursts from the inventory DB connection pool exhaustion.

**Model answer:** Mesh retried POST `/reservations` three times; inventory API lacked idempotency on `orderId`. Fix: remove mesh retries on mutating routes, add `Idempotency-Key` header enforcement in inventory service, use outbox for reservation events. Add integration test that simulates 503 and asserts single reservation row.

#### Code / config (when useful)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: pricing
spec:
  hosts: [pricing-service]
  http:
    - route:
        - destination: { host: pricing-service, subset: stable }
      timeout: 3s
      retries:
        attempts: 2
        perTryTimeout: 1s
        retryOn: connect-failure,refused-stream  # not 5xx on POST paths
```

---

### 53. Cell-based architecture and blast-radius isolation

**Short answer:** **Cell-based architecture** partitions the system into **cells** — self-contained stacks (compute, data, messaging) serving a slice of tenants or geography (e.g., `cell-us-east-1`, `cell-eu-west-1`). Failure in one cell does not take down others; blast radius is bounded by design. Trade-off: higher baseline cost (duplicated infra), cross-cell operations complexity, and rare cross-cell workflows need explicit federation — versus monolithic region failure affecting all customers.

#### What it is
Popular at hyperscale (AWS, Uber, Slack): each cell has its own Kubernetes cluster or namespace boundary, regional databases, and Kafka cluster or topic prefix. Routing layer (DNS, API gateway, global load balancer) steers tenant `acme-corp` to `cell-3` based on tenant registry. Cells align with **blast-radius isolation** — bad deploy, broker corruption, or operator error affects one slice. For Java microservices, cell identity propagates via headers (`X-Cell-Id`) and config (`spring.profiles` per cell).

#### How it works (internals)
A **cell router** (custom gateway or service mesh gateway) maps `tenantId → cellId` from a strongly consistent registry (DynamoDB, etcd). Services within a cell call only in-cell dependencies by default; cross-cell calls go through a **federation API** with stricter quotas. Deployments roll cell-by-cell (canary cell before fleet). Data never shares writable cross-cell stores — each cell owns shard of tenants. Observability stacks tag metrics by cell; paging routes to cell on-call before global escalation.

#### When to use / when NOT to use
Use when you have large tenant base, strict availability SLAs (99.99%+), or regulatory data residency requiring geographic isolation. Overkill for 5 services and 20 tenants — start with namespace isolation and multi-AZ. Consider cells when incident post-mortems show "one bad migration took down everyone."

#### Production example
SaaS billing platform runs 8 cells in AKS, 500 tenants each. Tenant onboarding assigns `cellId` in registry; API gateway routes `api.example.com` with JWT `tenant_id` claim. A bad Kafka topic config in `cell-4` caused consumer stall — only 12% of customers affected; global status page showed partial degradation. Fix rolled only to `cell-4`; other cells unchanged. Cross-cell analytics aggregates via read-only replication to warehouse — not synchronous calls.

#### Common mistakes
- "Cells" that share one database — blast radius not reduced.
- Cross-cell synchronous chains for user-facing requests — latency and failure coupling.
- Forgetting cell ID in logs/traces — cannot diagnose partial outage.
- Uneven tenant distribution — one hot cell becomes bottleneck.

#### Interview follow-ups (with model answers)

**Q:** Cells vs multi-AZ in one cluster?
**A:** Multi-AZ survives rack/AZ loss within a region but not bad deploy, misconfigured broker, or operator error affecting the whole cluster. Cells add software and operational boundaries — separate deploy trains, separate data stores, separate on-call blast. Many teams start multi-AZ + namespaces, evolve to cells when tenant count and incident history justify cost.

**Q:** How do you migrate a tenant between cells?
**A:** Offline or online migration with dual-write window: mark tenant `MIGRATING`, route reads to old cell, replicate data to new cell via CDC, verify checksum, flip router entry atomically in registry, drain old cell data after retention period. Never copy Kafka offsets — replay from compacted tenant events or snapshot export. Runbook includes rollback to old cell if error rate spikes post-flip.

#### Scenario probe
A senior architect proposes one shared Postgres for all cells "to simplify reporting." Push back in an interview.

**Model answer:** Shared writable Postgres defeats cell isolation — schema migration or runaway query takes all tenants offline. Offer read replica or CDC stream to warehouse for reporting; per-cell OLTP with federated query layer for admin dashboards. Accept eventual consistency for cross-cell analytics. Cite prior incident if available.

---

### 54. API composition (orchestrator) vs API gateway aggregation

**Short answer:** **API composition** (orchestrator/BFF) is a **service** that implements business workflow — calls inventory, pricing, payment in code, handles sagas, owns timeouts and compensations. **Gateway aggregation** is a thin **edge** pattern: gateway or GraphQL layer fans out parallel HTTP calls and merges JSON — no business rules. Orchestrator belongs in `order-service` or dedicated BFF; gateway should route, auth, rate-limit — not orchestrate checkout. Mixing them creates untestable 800-line filters.

#### What it is
The **orchestrator** pattern (microservices.io) centralizes process logic for a use case (`PlaceOrder`). **API gateway aggregation** (sometimes "scatter-gather") is infrastructure-level: Spring Cloud Gateway `GatewayFilter` or GraphQL resolver calls N backends and stitches responses for a product page. Composition has state, transactions, and domain rules; aggregation is read-only fan-out for presentation. Java: orchestrator is a `@Service` with injected clients; aggregation can be WebClient parallel calls in a BFF module.

#### How it works (internals)
Orchestrator maintains saga state (`order_saga` table), emits domain events, applies compensations on failure. Gateway aggregation uses reactive `Mono.zip` or `CompletableFuture.allOf` with per-call timeouts; failures may return partial responses (degraded mode). Orchestrator tests: unit + integration with WireMock + saga DB assertions. Gateway aggregation tests: contract tests on each downstream stub. Latency: orchestrator is often sequential for writes; aggregation should parallelize reads.

#### When to use / when NOT to use
| Pattern | Use when |
|---------|----------|
| Orchestrator | Multi-step writes, compensations, idempotency, money paths |
| Gateway aggregation | Read-only product pages, mobile BFF, minimizing client round-trips |
| Neither in gateway | Any logic needing versioned releases and code review |

Do not put saga compensation in gateway filters — no transaction context, hard to test, couples edge to business.

#### Production example
Mobile product page: `mobile-bff` aggregates catalog, price, reviews in parallel — 120ms p95. Checkout: `order-service` orchestrates reserve stock → authorize payment → confirm order with explicit state machine; gateway only routes `POST /checkout` to order-service. Previous team put checkout in Kong plugin — removed after untestable incident; ADR mandates business orchestration only in deployable services.

#### Common mistakes
- Gateway `GlobalFilter` with 15 sequential HTTP calls.
- BFF that grows into god-service owning write paths for every domain.
- Aggregation without per-dependency timeouts — one slow service blocks page.
- Calling orchestrator from another orchestrator — distributed monolith of workflows.

#### Interview follow-ups (with model answers)

**Q:** GraphQL gateway vs BFF orchestrator?
**A:** GraphQL with DataLoader suits read aggregation with N+1 control — still a BFF service with code and tests. It is not a substitute for write orchestration unless mutations are thin proxies. For checkout saga, use explicit orchestrator (or Temporal), not GraphQL mutation chain across 5 services without central state.

**Q:** Where does the API gateway fit?
**A:** TLS termination, JWT validation, rate limiting, WAF, routing to BFF or domain services, request logging. Optional response caching for GET. Never compensating transactions or interpreting business error codes into partial success.

#### Scenario probe
Your team's Spring Cloud Gateway has a `CheckoutCompositeFilter` calling five services. How do you refactor?

**Model answer:** Extract filter logic to `CheckoutOrchestrator` in `order-service`, gateway delegates single route. Move state to `order_saga`, add contract tests, deploy order-service independently. Gateway repo CI blocks new business logic in filters via ArchUnit or codeowners policy.

#### Code / config (when useful)

```java
// BFF read aggregation — parallel, no saga state
@Service
class ProductPageAggregator {
    public ProductPage aggregate(String sku) {
        var catalog = CompletableFuture.supplyAsync(() -> catalogClient.get(sku));
        var price   = CompletableFuture.supplyAsync(() -> pricingClient.get(sku));
        return new ProductPage(catalog.join(), price.join());
    }
}
```

---

### 55. Zero-trust networking for microservices on Azure

**Short answer:** **Zero trust** means never assume safety inside the network perimeter — every call is authenticated, authorized, encrypted, and logged. On Azure: **Private Link** for PaaS, **AKS** with Azure CNI overlay, **Workload Identity** for pod-to-Azure RBAC, **Application Gateway + WAF** or **API Management** at edge, and **NSGs / Azure Firewall** restricting east-west. mTLS via mesh or **service endpoints** replaces flat VNet trust. Trade-off: setup complexity and certificate rotation versus reduced lateral movement after breach.

#### What it is
Zero-trust for Java microservices on Azure layers: identity (Entra ID, managed identity), network (private clusters, no public kube API), encryption (TLS 1.2+, mTLS in mesh), and policy (Conditional Access, APIM policies, Key Vault references). Replaces "everything in the VNet is trusted." Spring Boot apps use **Workload Identity** federation instead of storing service principal secrets in ConfigMaps.

#### How it works (internals)
AKS private cluster: API server on private endpoint; nodes in node pool subnet; **Azure CNI** assigns pod IPs; **Network Policy** (Calico/Cilium) denies all by default, allowlist per namespace label. APIM validates JWT, applies rate limit, forwards to internal Ingress. Microservice calls another via cluster DNS; **Istio/Linkerd** or **mutual TLS** on Ingress. Key Vault CSI driver mounts secrets; no plaintext in `application.yml` in git. **Defender for Cloud** alerts on anomalous east-west traffic.

#### When to use / when NOT to use
Required for PCI, HIPAA, or enterprise customers mandating zero trust. Implement incrementally: private endpoints first, then network policies, then mesh mTLS. Small dev sandboxes may use public API with IP restrictions temporarily — document exit criteria to private model.

#### Production example
Payment microservices on AKS: cluster outbound via Azure Firewall, Postgres on **Private Link**, APIM exposes only `/v1/payments` with subscription keys and JWT. Pods use Workload Identity to reach Key Vault for Stripe keys. Network policy: only `payment-service` namespace may reach Postgres subnet on 5432. Pen test found no lateral path from compromised `catalog` pod to payment DB — zero-trust validation passed.

#### Common mistakes
- Public AKS API server with weak RBAC.
- Secrets in Spring Cloud Config git repo.
- NSG "allow VNet" blanket rule — defeats micro-segmentation.
- Skipping workload identity — long-lived credentials in pods.

#### Interview follow-ups (with model answers)

**Q:** Azure Service Mesh vs third-party Istio on AKS?
**A:** Istio/Linkerd on AKS is common and portable; configure via Helm or AKS mesh addon when available. Choice depends on team expertise and ambient mesh needs. Zero-trust goal is identity + encryption + policy — product name matters less than STRICT mTLS and network policy default-deny.

**Q:** How do Java pods authenticate to Azure SQL?
**A:** Use managed identity / Workload Identity with Entra ID authentication to Azure SQL (`Authentication=Active Directory Managed Identity` in JDBC URL). No SQL password in Key Vault if avoidable. Connection pooling (Hikari) with token refresh handled by Azure SDK integration.

#### Scenario probe
Auditor asks how you prevent a compromised `analytics-service` pod from querying the production payment database.

**Model answer:** Network policy denies `analytics` namespace egress to payment DB subnet; payment DB firewall allows only `payment-service` managed identity; no shared credentials. Audit logs in Defender show denied connection attempts. APIM does not expose payment DB — only REST API with authZ.

#### Code / config (when useful)

```yaml
# AKS NetworkPolicy — deny all, allow payment → postgres
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: payment-to-db
  namespace: payment
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - ipBlock: { cidr: 10.0.4.0/24 }  # postgres subnet
      ports: [{ protocol: TCP, port: 5432 }]
```

---

### 56. Domain events versioning and schema registry governance

**Short answer:** Domain events evolve; **schema registry** (Confluent, Azure Schema Registry) enforces **compatibility** (BACKWARD, FORWARD, FULL) so producers and consumers deploy independently. Governance: no `auto.register.schemas=true` in prod, PR checks validate compatibility, subject naming convention (`order-value`), and tombstone/compaction policy documented. Breaking changes require new event type or versioned topic — not in-place delete of required fields. Trade-off: registry rigidity slows schema iteration versus production deserialization crashes at 2 a.m.

#### What it is
Events are contracts between bounded contexts. Avro/Protobuf/JSON Schema in registry stores versions; Kafka serializers fetch schema by ID. **BACKWARD** compatible: new consumers read old data (add optional fields). **FORWARD**: old consumers read new data (add fields with defaults). Domain event versioning aligns with DDD — `OrderCreatedV2` as new type or same subject with compatible evolution. Java: `KafkaAvroSerializer` + `specific.avro.generated` classes from CI.

#### How it works (internals)
Producer registers schema (or CI registers); broker stores payload with schema ID prefix. Consumer deserializer fetches schema from registry HTTP API. Compatibility check runs on register — rejects incompatible schema. Transitive FULL checks entire version chain. Governance workflow: schema change PR → `mvn schema-registry:validate` → deploy consumers (additive) before producers or vice versa per compatibility mode. Dead letter on `SerializationException` with alert.

#### When to use / when NOT to use
Always for Kafka at enterprise scale. JSON events without registry need equally strict CI contract tests (Pact, custom JSON schema). For low-volume internal topics, JSON + review may suffice — document the exception. Never skip governance on money or fulfillment events.

#### Production example
`OrderCreated` gains `loyaltyTier` optional field — BACKWARD compatible, deploy consumers first (ignore unknown), then producers. Team attempts to rename `customerId` → `buyerId` — registry rejects; they add `buyerId` alongside deprecated `customerId` for two releases, then remove in V3 with new topic `order-created-v2`. Incident avoided that would have stalled all shipping consumers.

#### Common mistakes
- Breaking rename without dual-field period.
- Same subject for incompatible event shapes (use new subject).
- Old messages in retention still fail new strict consumer — plan replay.
- Schema registry single point without HA backup.

#### Interview follow-ups (with model answers)

**Q:** New topic vs same topic for V2 event?
**A:** Same topic with BACKWARD-compatible evolution when shape is additive. New topic when semantics diverge (different aggregate root) or when consumer groups need clean cutover without reading mixed semantics. Use parallel consumer group on new topic, migrate, deprecate old topic after retention drains.

**Q:** Who owns the schema — producer or platform?
**A:** Producer team owns schema PRs; platform owns registry policies, naming, compatibility defaults, and CI gates. Consumer teams review breaking-change notices. Event catalog links subject to owning team Slack and on-call.

#### Scenario probe
Friday deploy: producer ships schema removing optional field; old fulfillment consumer fails Avro deserialization fleet-wide.

**Model answer:** Roll back producer; registry should have blocked FORWARD-incompatible change if old consumers still deployed. Fix process: CI compatibility check, deploy order matrix, freeze Friday prod schema changes. Consumer temporary patch: deserialize generic record if feasible — long-term registry governance.

#### Code / config (when useful)

```properties
# producer — no auto register in prod
spring.kafka.producer.properties.schema.registry.url=https://sr.example.com
spring.kafka.producer.properties.auto.register.schemas=false
spring.kafka.producer.properties.use.latest.version=false
```

---

### 57. Consumer-driven contract testing (Pact) in CI

**Short answer:** **Consumer-driven contracts** (Pact) let the **consumer** define expected request/response (or message) interactions; the **provider** verifies against published pacts in CI — catch breaking API changes before integration environments. For microservices, each Spring consumer publishes `pact` JSON to a broker (PactFlow); provider pipeline runs `@Provider` verification tests. Trade-off: pact maintenance cost versus late-stage integration failures and coordinated deploys.

#### What it is
Pact records interactions from consumer tests (`@Pact` or V4 spec builders) and compares provider actual responses to contract. Message pacts cover Kafka events. Fits Java via `au.com.dius.pact.consumer:junit5` and `provider:junit5`. Alternative: Spring Cloud Contract (producer-driven) — choose one standard per org. Consumer-driven fits when many consumers depend on few providers (pricing, catalog).

#### How it works (internals)
Consumer test generates pact file → publish to broker with `consumerVersion` git SHA. Provider CI pulls `pacticipants` pending verification, runs tests against in-memory MockMvc or Testcontainers, publishes verification result. `can-i-deploy` checks if safe to deploy consumer+provider combination. Breaking change: provider fails verification → block merge. For events, message pact defines payload shape consumer expects.

#### When to use / when NOT to use
Use for public-ish internal APIs and critical events between teams. Skip for admin-only APIs with single consumer updated in same repo. Complement with e2e smoke tests — pacts do not replace full environment tests. Do not pact-test every field of 200-field DTO — focus on fields consumer uses.

#### Production example
`checkout-service` consumer pact expects `GET /prices/{sku}` returns `amount` number. `pricing-service` refactors `amount` to string — provider CI fails on MR. Developer fixes with backward-compatible dual field or versioned `/v2/prices`. Deploy order documented: compatible provider before consumer on breaking changes. Pact broker shows `checkout@abc123` verified against `pricing@def456`.

#### Common mistakes
- Pacts not published from CI — stale contracts.
- Provider verifies against mocks that do not match production controllers.
- Ignoring message pacts for Kafka — HTTP-only coverage.
- Using random data in pacts without matchers — brittle tests.

#### Interview follow-ups (with model answers)

**Q:** Pact vs Spring Cloud Contract?
**A:** Pact is consumer-driven — consumers own expectations; great when provider serves many teams. Spring Cloud Contract is producer-driven — provider publishes stubs. Pick one org standard. I use Pact when consumer teams outnumber providers and need broker `can-i-deploy` gates.

**Q:** How do you test asynchronous events with Pact?
**A:** Message pact: consumer test defines expected `OrderCreated` payload; provider runs message verifier that invokes producer code path or test harness publishing to in-memory channel. Include type matchers for extensible fields. Pair with schema registry for double protection on Avro.

#### Scenario probe
Provider team says "we'll fix breaking change in integration env." How do you respond?

**Model answer:** Integration env lags prod and does not block bad merges. Contract tests in CI are the gate; `can-i-deploy` blocks prod promote until verified. Offer provider stub in consumer repo only for local dev — broker remains source of truth.

#### Code / config (when useful)

```java
@ExtendWith(PactConsumerTestExt.class)
class PricingClientPactTest {
    @Pact(consumer = "checkout-service")
    public RequestResponsePact pricePact(PactDslWithProvider builder) {
        return builder
            .uponReceiving("get price for sku")
            .path("/prices/WIDGET-1")
            .method("GET")
            .willRespondWith()
            .status(200)
            .body(new PactDslJsonBody().numberType("amount", 29.99))
            .toPact();
    }
}
```

---

### 58. Modular monolith escape hatches before splitting services

**Short answer:** Before extracting microservices, build **escape hatches** in the modular monolith: clear **module boundaries** (Gradle/Maven), **ports and adapters**, **ArchUnit** dependency rules, **feature flags** for routing, and **outbox-ready** event publishing. These let you swap in-process calls for HTTP/Kafka later without rewriting business logic. The trade-off is upfront discipline versus cheap extraction when the org is not ready for ops overhead of distributed systems.

#### What it is
A **modular monolith** packages domains as modules with explicit APIs (`catalog-api`, `order-impl`). Escape hatches: interface `PricingPort` implemented by `InProcessPricingAdapter` today, `HttpPricingAdapter` tomorrow; events published via `DomainEventPublisher` interface backed by Spring `ApplicationEventPublisher` then Kafka. **Strangler fig** starts at the seam you already cut in code.

#### How it works (internals)
ArchUnit: `noClasses().that().resideInPackage("..order..").should().dependOnClassesThat().resideInPackage("..billing..").except("..billing.api..")`. Module exposes only `-api` jar to consumers. Database: separate schemas per module in same Postgres instance before separate databases. Outbox table per module prepares for Debezium without dual-write. Feature flag `pricing.remote.enabled` routes `PricingPort` to HTTP client in staging.

#### When to use / when NOT to use
Use when roadmap includes likely extraction in 12–24 months but team is not ready for K8s on-call. Skip heavy modularization if domain is stable and team stays small forever — YAGNI. Essential when executives want microservices but ops maturity is 6 months out — honesty plus escape hatches.

#### Production example
Monolith modules `order`, `catalog`, `billing` with ArchUnit CI gate. Team extracts `billing` first: enable `billing.remote.enabled`, deploy `billing-service`, HTTP adapter implements same `BillingPort`, dual-write invoices for two weeks, cut over reads, retire in-process adapter. Order module unchanged except config — six-week extraction vs estimated six-month rewrite without seams.

#### Common mistakes
- Package rename only — same shared `entities` table mutated by all modules.
- No contract tests at module API — extraction breaks silently.
- Big-bang cutover without feature flag rollback.
- Skipping outbox — extraction forces dual-write crisis.

#### Interview follow-ups (with model answers)

**Q:** Modular monolith libraries for Java?
**A:** Gradle multi-module or Spring Modulith for structure and documentation tests; ArchUnit for dependency rules; internal `-api` jars; optional jMolecules for DDD markers. Spring Modulith verifies module boundaries and documents event listeners. No silver bullet — team discipline enforces ownership.

**Q:** First extraction candidate?
**A:** Bounded context with clearest data ownership, regulatory isolation (PCI), or deploy pain — often billing or notifications. Avoid extracting read-heavy catalog first if it creates distributed monolith of joins. Measure: can you delete in-process adapter without changing order module business code?

#### Scenario probe
CTO wants microservices in 90 days; you have one repo, one DB, six engineers. Proposal?

**Model answer:** 90-day plan: modular monolith boundaries, ArchUnit, outbox, observability, one extraction only if billing PCI ready — else deliver escape hatches and IDP. Success metrics: deploy frequency and module-level test coverage, not service count. Show Spring Modulith diagram and feature-flag extraction path.

#### Code / config (when useful)

```java
@Configuration
class PricingConfig {
    @Bean
    PricingPort pricingPort(
            @Value("${pricing.remote.enabled:false}") boolean remote,
            InProcessPricingAdapter local,
            HttpPricingAdapter http) {
        return remote ? http : local;
    }
}
```

---

## Scenario-based interview drills

### S1. Checkout stuck in PAYMENT_PENDING after Kafka outage

**Situation:** `order-service` publishes `OrderPlaced` after DB commit; `payment-service` consumer lag hit 6 hours during broker incident. Orders pile up; customers charged inconsistently. No saga timeout sweeper.

**What they're testing:** Async failure, saga state, consumer lag ops, user-visible consistency, compensation.

**How to structure your answer:** Detect → stop bleeding → reconcile → long-term timeouts/idempotency → comms.

**Model answer:** First, page on consumer lag and DLQ depth — freeze risky auto-retries if duplicate payment risk exists. Identify correlation ids for stuck orders in `order_saga` or workflow table. Runbook: manual replay from offset only after verifying idempotency store. Communicate status page: orders may delay. Long-term: orchestrated saga with Temporal or explicit state machine — timeout on PAYMENT_PENDING transitions to CANCELLED or MANUAL_REVIEW; payment capture idempotent on `orderId`. Outbox ensures `OrderPlaced` not lost if publish failed — relay catches up after broker recovery. Reconciliation job compares order DB vs payment provider settlements nightly. Never tell customer "eventual consistency" without pending UI state. Post-incident ADR: money path orchestrated, notifications choreographed.

**Common weak answers:** "Restart Kafka." "Delete consumer group." No idempotency or reconciliation mention.

**Follow-up probes (with answers):**

**Q:** Choreography vs orchestration for payment?
**A:** Orchestration for payment and inventory with compensations; choreography acceptable for email/analytics. Payment needs visible state and timeout sweeps.

---

### S2. Distributed monolith discovered in production

**Situation:** Five "microservices" share one Postgres schema; any migration requires coordinated deploy of all five. Deploy frequency unchanged from monolith era.

**What they're testing:** Data ownership, boundaries, strangler migration, honest architecture assessment.

**How to structure your answer:** Name problem → stop shared writes → pick first boundary → migrate data → team ownership.

**Model answer:** This is a distributed monolith — worst of both worlds. Immediate: freeze new cross-schema FKs; document which service writes which tables. Strangler plan: pick bounded context with clearest ownership (e.g., `billing`) — new schema, dual-write or CDC sync, switch reads, cut writes, deprecate shared table access. Enforce via network policy: only `billing-service` credentials on `billing` schema. Other services call API or consume events. Until migration completes, be honest — operate as modular monolith with single deploy train if needed. Success metric: independent migration and deploy for extracted service. ArchUnit + DB lint blocking cross-schema JDBC from wrong service.

**Common weak answers:** "Add more services." Kubernetes will fix it. Ignore shared database.

**Follow-up probes (with answers):**

**Q:** Can two contexts share schema temporarily?
**A:** Read-only during transition with written exit date; never shared writes. Temporary often becomes permanent without enforcement.

---

### S3. API gateway becomes orchestrator god-object

**Situation:** Spring Cloud Gateway routes embed checkout logic — call inventory, payment, shipping in filter chain. Untested, 800-line `GlobalFilter`.

**What they're testing:** Service boundaries, where business logic lives, testability.

**How to structure your answer:** Anti-pattern → move logic → gateway responsibilities → testing.

**Model answer:** Gateway should terminate TLS, authn/z, rate limit, routing, request logging — not orchestrate sagas. Move checkout saga to `order-service` or dedicated workflow (Temporal). Gateway filters become thin: validate JWT, attach headers (`X-Tenant-Id`, trace id), route. Business orchestration gets unit and integration tests with contract tests on downstream stubs. If BFF pattern for mobile, BFF is still a service with logic — not anonymous filters. Refactor plan: extract filter code to `CheckoutOrchestrator` bean in order service, gateway delegates single `POST /checkout`. Document in ADR. CI: no new business branches in gateway repo without architecture review.

**Common weak answers:** "Gateway is entry point so logic belongs there." "Works on my laptop."

**Follow-up probes (with answers):**

**Q:** BFF vs gateway?
**A:** BFF aggregates for a specific client experience and may compose calls — still a deployable with tests. Gateway is cross-cutting infrastructure shared by all clients.

---

### S4. Schema registry breaking change ships Friday

**Situation:** Producer deploys `OrderCreated` v2 removing optional field; old `shipping-service` consumer Avro deserializer fails; deployments blocked.

**What they're testing:** Event versioning, compatibility, registry governance, rollout strategy.

**How to structure your answer:** Compatibility rules → fix rollout → governance → dual-write period.

**Model answer:** Breaking schema change requires new subject or version with BACKWARD/FULL transitive policy enforced in CI. Roll back producer if consumers cannot migrate same window. Correct process: add optional fields only (BACKWARD compatible), or create `order-created-v2` topic with parallel consumer deploy, then deprecate v1. Registry PR check: `mvn schema-registry:validate`. Never `auto.register.schemas=true` in prod without review. Old messages in Kafka retention still deserialize — consumers must handle absent new fields. Feature flag consumer to read both shapes during migration. Post-incident: mandatory schema review, deploy order consumers before producers on additive changes, producers before consumers only when FORWARD compatible.

**Common weak answers:** "Delete old schema version." "Use JSON without schema." Friday deploy without consumer matrix.

**Follow-up probes (with answers):**

**Q:** Avro vs JSON for events?
**A:** Avro with registry gives enforced compatibility and smaller payloads; JSON OK for low-volume internal topics with strict CI contracts. Enterprise Kafka almost always registry.

---

### S5. Fan-out product page — 8 sequential HTTP calls

**Situation:** Mobile product page BFF calls 8 services serially; p95 1.2s. Marketing deadline immovable.

**What they're testing:** Fan-out, aggregation, caching, bulkhead, read models.

**How to structure your answer:** Measure → parallelize short-term → read model long-term → resilience.

**Model answer:** Short-term: parallelize independent calls with `CompletableFuture` or reactive WebClient with global timeout 300ms, per-call 100ms — fail partial page with degraded sections. Bulkhead thread pools per dependency so slow recommendations do not block price. Medium: build `product-read-service` document updated by `ProductUpdated`, `InventoryUpdated`, `ReviewStatsUpdated` events — single GET. Cache CDN for static assets. Do not GraphQL without DataLoader — N+1 microservice edition. Track per-dependency latency attribution. SLO: p95 < 200ms. Long-term CQRS read store with version field for cache invalidation.

**Common weak answers:** "Add more pods to BFF only." Serial calls "because simpler." No timeout mention.

**Follow-up probes (with answers):**

**Q:** Strong consistency across 8 services on read?
**A:** Impractical — define which fields must be fresh (price, stock) vs eventual (review count). Authoritative calls sync for stock/price only.

---

### S6. Dual write caused missing warehouse notification

**Situation:** `order-service` commits order then publishes to Kafka — crash between steps. Order exists, warehouse never notified.

**What they're testing:** Outbox, dual write problem, reliability patterns.

**How to structure your answer:** Failure window → outbox → relay → verification.

**Model answer:** Classic dual write — no atomicity across DB and broker. Fix: transactional outbox table in same DB transaction as order insert; relay (Debezium, polling publisher, or LogTape) publishes to Kafka with idempotent producer keys. Order state `CONFIRMED` only when outbox relayed or use inbox pattern on warehouse side reconciling missing orders. Reconciliation cron: orders `CONFIRMED` older than 5m without `WarehouseOrderCreated` event trigger alert/replay. Testing: chaos kill pod after commit before publish — outbox must eventually deliver. Document: never publish in service method after repository save without outbox.

**Common weak answers:** "Use Kafka transactions only." "Retry publish in catch block" without dedup.

**Follow-up probes (with answers):**

**Q:** Outbox vs CDC?
**A:** Outbox shapes domain events explicitly in app transaction; CDC captures row changes — good for analytics, harder for rich event semantics. Many teams use both.

---

### S7. Circuit breaker stuck open storms payment dependency

**Situation:** Payment provider blip opens Resilience4j circuit for all pods; stays half-open failing; checkout 100% fail 20 minutes after provider recovered.

**What they're testing:** Resilience patterns, breaker tuning, health checks, fallbacks.

**How to structure your answer:** Breaker behavior → tuning → half-open probe → ops → user messaging.

**Model answer:** Breaker opened correctly during outage but recovery hampered by aggressive failure threshold or single slow call keeping it open. Tune `waitDurationInOpenState`, `permittedNumberOfCallsInHalfOpenState`, separate bulkhead for admin vs checkout. Health check should call lightweight provider ping, not full charge. Alert on breaker state metric. Fallback: queue order for async payment retry with clear user message — not silent failure. After recovery, manually reset breaker via admin endpoint if stuck. Load test breaker transitions. Document provider SLA and retry budget. Idempotency on payment retry mandatory.

**Common weak answers:** "Disable circuit breaker." Infinite retries. No half-open explanation.

**Follow-up probes (with answers):**

**Q:** Retry vs circuit breaker?
**A:** Retry helps transient single failures; breaker stops hammering dead dependency and gives time to recover — use together with caps.

---

### S8. GDPR erasure across 12 services

**Situation:** Customer deletion request; data scattered across services, Kafka logs, warehouse, support tickets. Legal deadline 30 days.

**What they're testing:** Data ownership, event retention, choreography of deletion, PII mapping.

**How to structure your answer:** Data map → orchestration → per-service delete → logs → proof.

**Model answer:** Maintain data catalog: which service owns PII fields, retention, downstream copies. `CustomerDeletionRequested` event with correlation id; each service implements idempotent delete/anonymize handler; report completion to orchestration table. Kafka: tombstone or compacted topic policy — retention may keep PII unless encryption + deletion workflow. Warehouse: GDPR delete via batch job on `customer_id`. Support SaaS API delete. No cross-service SQL — each owner acts. Provide audit trail for regulator. Test quarterly deletion drill. Block new services without deletion handler in scaffold template.

**Common weak answers:** "DELETE FROM users in one DB." Ignore broker retention. No ownership map.

**Follow-up probes (with answers):**

**Q:** Anonymize vs hard delete?
**A:** Finance/audit may require anonymized retained records vs delete — legal defines per field class; engineering implements per-service policy.

---

### S9. Canary deploy causes 5xx spike — bad service boundary

**Situation:** Canary of `pricing-service` changes discount rules; `checkout-service` sends new field; old cart service version mis-parses — 5xx on 5% traffic.

**What they're testing:** Contract testing, backward compatibility, deploy order, feature flags.

**How to structure your answer:** Contract failure → compat rules → testing → deploy strategy.

**Model answer:** Breaking API change without consumer-first deploy. Fix: make new field optional with default; consumer tolerant of unknown fields (JSON ignore unknown). Pact or Spring Cloud Contract in CI — checkout tests against pricing provider stub. Deploy compatible consumer before producer, or use feature flag in pricing to emit old+new shapes during transition. Canary should monitor error rate per route tagged with version. Roll back canary. ADR: additive API changes only; breaking requires versioned endpoint `/v2`. For events, schema registry BACKWARD compatibility.

**Common weak answers:** "Coordinated big bang deploy at midnight." "Integration tests optional."

**Follow-up probes (with answers):**

**Q:** How long maintain v1 API?
**A:** Published deprecation policy — e.g., 6 months with metrics on v1 traffic before sunset.

---

### S10. Team wants 50 nanoservices — senior pushback

**Situation:** CTO mandates microservices transformation; diagram shows 50 services for CRUD app; 6 engineers, no K8s experience.

**What they're testing:** Senior judgment, organizational fit, roadmap, metrics, saying no constructively.

**How to structure your answer:** Clarify goals → assess readiness → propose phased plan → metrics → risks.

**Model answer:** I ask what pain we are solving: deploy frequency, scale, compliance isolation, team autonomy? With 6 engineers, 50 services means 50 on-call surfaces without platform team — unrealistic. Propose modular monolith with clear Gradle modules and ArchUnit boundaries; measure deploy frequency and MTTR baseline. First extraction only when bounded context + owner ready — likely payments or notifications, not every entity. Build golden path: CI, observability, contract tests, IDP docs. Success metrics: weekly deploys, <30 min incident MTTR, not service count. 12-month roadmap with executive checkpoints. Say no to nanoservices and shared DB anti-pattern honestly — distributed monolith worse than well-structured monolith. Offer training plan for K8s if extraction proceeds.

**Common weak answers:** "Yes to everything." "Microservices are best practice." No metrics or team size mention.

**Follow-up probes (with answers):**

**Q:** When would you agree to split?
**A:** Clear bounded context, dedicated team, operational maturity, concrete pain, and data ownership plan — not diagram aesthetics.

---
