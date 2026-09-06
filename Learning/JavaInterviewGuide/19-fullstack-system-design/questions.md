# Fullstack System Design — 60 Senior Interview Questions

**Bar:** Stitch Java + Spring + React + Kafka + SQL + Azure + Helm + Terraform. Own the trade-offs, failure paths, and what you would defer—not the buzzword diagram.

---

### 1. How you start any design (90 seconds).

**Short answer:** Clarify users and core flows, scale (read/write QPS, data retention), consistency and latency SLOs, compliance, and team ownership—ask three sharp questions, then sketch boxes. Do not open with "we'll use Kafka"; earn async after you know sync boundaries and failure modes.

#### What it is
The opening frame separates seniors from diagram tourists. Interviewers want structured discovery before technology. Your first 90 seconds set whether the next 40 minutes are coherent or a laundry list of Azure services.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Template: (1) Who uses it—shopper, merchant admin, batch job? (2) Happy path in one sentence. (3) NFRs: p99 latency, RPO/RTO, multi-tenant?, PCI? (4) Scale: orders/day, peak multiplier, storage growth. (5) Constraints: existing Oracle, two squads, 6-week MVP. Then draw client → API → datastore → async only if sync cannot meet SLO or coupling is unacceptable. Label idempotency and owner per box.

#### When to use / when NOT to use
Always start here in design loops. Skip deep technology until scope pinned—if interviewer says "design checkout," do not spend 10 minutes on Terraform. If they say "already on AKS," do not re-pitch Kubernetes.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-service` → Azure SQL with outbox; mention Kafka only for downstream notifications after stating sync create order + idempotency key. Interviewer nods—you earned the bus.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Kafka-first without throughput math. Missing compliance question on payments. No failure arrow on diagram. Ignoring team boundary ("who owns inventory DB?"). Jumping to microservices before load justification.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Three questions you always ask first?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-serv… Common miss: Kafka-first without throughput math. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** When do you introduce Kafka?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-serv… Common miss: Kafka-first without throughput math. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** How timebox the opening?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-serv… Common miss: Kafka-first without throughput math. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Functional vs non-functional ordering?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-serv… Common miss: Kafka-first without throughput math. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for How you start any design (90 seconds).—error budget is burning.

**Model answer:** Clarify users and core flows, scale (read/write QPS, data retention), consistency and latency SLOs, compliance, and team ownership—ask three sharp questions, then sketch boxes. Do not open with "we'll use Kafka"; earn as In practice: Prompt: "Design order placement." You ask: peak checkout QPS? Strong consistency on inventory or eventual? Existing payment PSP? Draw React → APIM → `order-service` → Azure SQL wit… I check whether we hit a known mistake (Kafka-first without throughput math. Missing compliance question on payments. No…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 2. Order management (the canonical).

**Short answer:** React SPA → BFF/API → `order-service` persists order + outbox in Azure SQL → relay publishes `order-events` keyed by `orderId` → inventory, payment, notification consumers advance saga with timeouts. Frontend: pending states, `If-Match`/`ETag`, 409 on conflict; POST carries `Idempotency-Key`.

#### What it is
Order management is the default fullstack design pattern: OLTP system of record, async choreography for side effects, clear state machine (`PENDING` → `PAID` → `SHIPPED`). Interviewers use it to test sagas, APIs, and UX under partial failure.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`POST /orders` validates cart, inserts `orders` + `order_lines` in one transaction, writes outbox row. Debezium or polling relay publishes `OrderPlaced` to Kafka partition keyed by `orderId` for ordering per order. Inventory consumer reserves stock; payment consumer captures funds; each emits success/failure events. Orchestrator or process manager tracks timeout—release reservation if payment stalls. React polls or SSE on `GET /orders/{id}`; optimistic UI only where safe.

#### When to use / when NOT to use
Use this pattern for B2C/B2B checkout with multiple downstream systems. Defer Kafka if MVP is single monolith with sync inventory table and <100 TPS—add outbox when extracting services. Do not dual-write order row and message without outbox.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Vault. Idempotency table keyed by client UUID prevents double-submit on mobile retry. Saga completes in p99 4s; notification email async.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Dual-write to DB and Kafka. No idempotency on POST. Inventory and payment race without partition key ordering. React shows success before `201` ack. OFFSET pagination on order history at scale.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Outbox vs dual-write?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Va… Common miss: Dual-write to DB and Kafka. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Orchestration vs choreography?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Va… Common miss: Dual-write to DB and Kafka. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Partition key choice?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Va… Common miss: Dual-write to DB and Kafka. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** React pending UX?
**A:** AI drafts inside guardrails—sister Helm chart, EXPLAIN on SQL, conventional commits I edit—then Checkov, compile, and human review. Example: B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Va… Common miss: Dual-write to DB and Kafka. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Order management (the canonical).—error budget is burning.

**Model answer:** React SPA → BFF/API → `order-service` persists order + outbox in Azure SQL → relay publishes `order-events` keyed by `orderId` → inventory, payment, notification consumers advance saga with timeouts. Frontend: pending st In practice: B2C retailer: 800 peak orders/min. Spring Boot on AKS, Azure SQL Hyperscale, Event Hubs Kafka API. Helm deploys `order-service` with workload identity to Key Vault. Idempotency tab… I check whether we hit a known mistake (Dual-write to DB and Kafka. No idempotency on POST. Inventory and payment race w…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```text
POST /orders
Idempotency-Key: 7c9e6679-7425-40de-944b-e07fc1f90ae7
→ 201 { orderId, status: PENDING, etag: "W/\"abc123\"" }
→ outbox → Kafka order-events (key=orderId)
```

---

### 3. Payments: the extra constraints.

**Short answer:** PCI scope: never store PAN; tokenize with PSP; idempotency keys on capture; ledger append-only; webhooks HMAC-verified; compensation is refund/chargeback flow—not rolling back a captured authorization like a DB transaction.

#### What it is
Payments sit inside order saga with regulatory and financial invariants. Design must show trust boundary with Stripe/Adyen, audit trail, and reconcile jobs—not just "payment microservice."  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Browser gets client token from PSP JS; server charges with idempotency key stored in `payment_attempts`. Webhook confirms async outcomes—verify signature, upsert status idempotently by `psp_event_id`. Immutable `ledger_entries` for finance. If order fails after capture, publish `RefundRequested`—do not DELETE payment row. MQ to PSP still common for batch settlements. Scope reduction: SAQ A if card fields never touch your servers.

#### When to use / when NOT to use
Always separate payment domain schema from catalog. Never log full card data. Use outbox for payment events to Kafka. Defer building own PSP—integrate.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
`payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data warehouse. Nightly reconcile job compares PSP CSV to ledger. Chargeback links to original `idempotency_key`.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Storing PAN in `orders` table. Treating webhook as optional. No reconcile job. "Rollback" of capture via DB delete. Missing idempotency on retry storm after timeout.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** PCI scope reduction tactics?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data wa… Common miss: Storing PAN in `orders` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Ledger schema design?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data wa… Common miss: Storing PAN in `orders` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Webhook verification?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data wa… Common miss: Storing PAN in `orders` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Compensation vs DB rollback?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: `payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data wa… Common miss: Storing PAN in `orders` table. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Payments: the extra constraints.—error budget is burning.

**Model answer:** PCI scope: never store PAN; tokenize with PSP; idempotency keys on capture; ledger append-only; webhooks HMAC-verified; compensation is refund/chargeback flow—not rolling back a captured authorization like a DB transacti In practice: `payment-service` on AKS calls Adyen API; stores token + status in Azure SQL; webhook endpoint behind APIM with rate limit. Kafka `payment-events` feeds data warehouse. Nightly rec… I check whether we hit a known mistake (Storing PAN in `orders` table. Treating webhook as optional. No reconcile job. "…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 4. Inventory reservation.

**Short answer:** Reserve stock in OLTP with `SELECT FOR UPDATE SKIP LOCKED` or optimistic version column—trade over-sell risk vs lock contention. Reservation TTL pairs with payment timeout; release on saga failure.

#### What it is
Inventory is the concurrency hotspot in checkout. Design names who owns stock rows, reservation TTL, and what happens when payment succeeds but ship fails.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
On `OrderPlaced`, consumer decrements `available_qty` and inserts `reservation` row with expiry. High contention SKUs: partition by `warehouse_id`, queue, or short pessimistic lock on row. Alternative: optimistic `UPDATE ... WHERE version = ?` retry. Over-sell monitoring compares reservations to physical counts. Do not rely on cache as source of truth for stock.

#### When to use / when NOT to use
Pessimistic for low-SKU flash sales. Optimistic for long-tail catalog. Eventual inventory from Kafka projection only for read models—not authoritative at checkout without sync validate.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Helm HPA on consumer lag. Expired reservations cron releases stock every minute.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Read-modify-write race without locking. No reservation expiry—ghost holds. Checking cache then writing DB without transaction. Global lock on `inventory` table.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Pessimistic vs optimistic when?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Hel… Common miss: Read-modify-write race without locking. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Hot SKU strategy?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Hel… Common miss: Read-modify-write race without locking. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Reservation TTL value?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Hel… Common miss: Read-modify-write race without locking. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Oversell detection?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Hel… Common miss: Read-modify-write race without locking. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Inventory reservation.—error budget is burning.

**Model answer:** Reserve stock in OLTP with `SELECT FOR UPDATE SKIP LOCKED` or optimistic version column—trade over-sell risk vs lock contention. Reservation TTL pairs with payment timeout; release on saga failure. In practice: Flash drop 10k units, 50k concurrent checkouts. `inventory-service` uses `SKIP LOCKED` to process reservations in order; 409 `INSUFFICIENT_STOCK` to client. Helm HPA on consumer la… I check whether we hit a known mistake (Read-modify-write race without locking. No reservation expiry—ghost holds. Check…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```sql
UPDATE inventory
SET available_qty = available_qty - :qty, version = version + 1
WHERE sku = :sku AND available_qty >= :qty AND version = :expectedVersion;
```

---

### 5. Search vs OLTP.

**Short answer:** Product search reads from Elasticsearch/OpenSearch or Azure Cognitive Search index fed by Kafka CDC—not from transactional Oracle/Azure SQL with `LIKE`. OLTP stays normalized; search denormalizes for facets, typo tolerance, and ranking.

#### What it is
Splitting search from OLTP prevents reporting queries from locking checkout rows. Catalog browse is read-heavy, fuzzy, and eventually consistent with warehouse truth.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`catalog-service` writes product row; outbox → Kafka `catalog-events` → search indexer consumer updates document with title, facets, price, stock signal (not authoritative qty). React search hits search API; product detail may hit OLTP for buy button truth. Reindex job for disaster. Lag SLA: 30s acceptable for browse; not for cart price—price validated at order time from OLTP.

#### When to use / when NOT to use
Add search index when SQL `LIKE` or JSON queries exceed 200ms p95 or need facets. Skip for 500-SKU B2B catalog—SQL + cache enough. Do not run Elastic as money system of record.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via Helm; OLTP scales separately. Stale index 10s—acceptable; checkout revalidates price.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Dual-write product to SQL and ES. Search index as inventory authority. No reindex playbook. Massive JOIN in OLTP for browse page.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Index lag tolerance?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via He… Common miss: Dual-write product to SQL and ES. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Price consistency at checkout?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via He… Common miss: Dual-write product to SQL and ES. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Reindex without downtime?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via He… Common miss: Dual-write product to SQL and ES. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Azure AI Search vs self-hosted ES?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via He… Common miss: Dual-write product to SQL and ES. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Search vs OLTP.—error budget is burning.

**Model answer:** Product search reads from Elasticsearch/OpenSearch or Azure Cognitive Search index fed by Kafka CDC—not from transactional Oracle/Azure SQL with `LIKE`. OLTP stays normalized; search denormalizes for facets, typo toleran In practice: Marketplace 2M SKUs: Azure SQL catalog OLTP, OpenSearch cluster on AKS, indexer from Kafka. React uses typeahead API. Black Friday: scale search replicas via Helm; OLTP scales sepa… I check whether we hit a known mistake (Dual-write product to SQL and ES. Search index as inventory authority. No reinde…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 6. Notifications.

**Short answer:** Email/SMS/push via async Kafka `notification-events` with templating service, provider adapters (SendGrid, Twilio), idempotent send log, and DLQ for bounces—never block order path on SMTP.

#### What it is
Notifications are side effects: order confirmed, shipped, password reset. Design includes retry, unsubscribe compliance, and PII in template variables—not a synchronous call from `order-service`.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Order consumer publishes `NotificationRequested` with channel, templateId, locale, and variables (no PAN). Worker renders Thymeleaf or Handlebars template, calls provider API with idempotency key per `(orderId, templateId, channel)`. Store `notification_log` status with provider message ID for support lookup. DLQ for hard bounces; suppress list for CAN-SPAM and GDPR marketing opt-out. Rate limit per user to prevent abuse and provider throttling. React in-app notifications via SSE/WebSocket separate from email worker—different SLO and retry policy. Priority queue: transactional (order receipt) before marketing campaigns.

#### When to use / when NOT to use
Always async for order emails. Sync only for critical in-app toast from same BFF read. Batch digest emails via scheduler.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
`notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email; Twilio adapter behind interface for SMS. Helm HPA scales replicas when lag >5000 for 3 minutes. GDPR delete-user saga scrubs `notification_log` PII and removes from marketing lists. Order API latency unchanged—`OrderPlaced` handler only appends Kafka record in same thread as outbox relay, sub-5ms.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
SMTP in request thread blocking checkout. No idempotency—duplicate emails on Kafka redelivery after consumer crash. Logging phone numbers in plain text. Missing unsubscribe on marketing. Hard-coded English templates without i18n keys.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Channel priority?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email;… Common miss: SMTP in request thread blocking checkout. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** DLQ handling?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email;… Common miss: SMTP in request thread blocking checkout. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Template versioning?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email;… Common miss: SMTP in request thread blocking checkout. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** In-app vs email architecture?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email;… Common miss: SMTP in request thread blocking checkout. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Notifications.—error budget is burning.

**Model answer:** Email/SMS/push via async Kafka `notification-events` with templating service, provider adapters (SendGrid, Twilio), idempotent send log, and DLQ for bounces—never block order path on SMTP. In practice: `notification-service` Spring Boot on AKS consumes `notification-events` with consumer group `notification-worker-v3`. Azure Communication Services sends email; Twilio adapter behi… I check whether we hit a known mistake (SMTP in request thread blocking checkout. No idempotency—duplicate emails on Kaf…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 7. Multi-tenant SaaS.

**Short answer:** Pick isolation model early: shared schema + `tenant_id` column, schema-per-tenant, or silo-per-tenant—trade cost vs blast radius. Every query and Kafka key carries tenant context; JWT claim enforced in repository layer, not only UI.

#### What it is
Multi-tenant design affects DB indexes, caching, noisy neighbor, and compliance (data residency per tenant tier). B2B SaaS order management often starts row-level, evolves to silo for enterprise.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Row-level: `tenant_id` on all tables, composite indexes leading with `tenant_id`, RLS in Postgres optional. APIM validates JWT `tid`; Spring `@PreAuthorize` + custom `TenantContext`. Kafka headers propagate tenant; consumers filter. Enterprise tier: dedicated AKS namespace + DB per tenant via Terraform module. No cross-tenant cache keys without prefix.

#### When to use / when NOT to use
Row-level for SMB thousands of tenants. Silo for regulated enterprise. Do not start silo for MVP unless contract requires—it ops-heavy.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign. React admin passes tenant from subdomain. Load test proves index on `(tenant_id, created_at)` keeps list API p99 <200ms.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Missing `tenant_id` in one query—BOLA. Global cache poisoning. Tenant in URL only, not verified server-side. Noisy neighbor on shared Kafka topic without quotas.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Isolation model choice?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: 5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign… Common miss: Missing `tenant_id` in one query—BOLA. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** BOLA prevention?
**A:** Security stays human-reviewed: Semgrep, BOLA tests, and no AI-only `SecurityFilterChain`—I reject permissive CORS and hardcoded keys in generated tests. Example: 5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign… Common miss: Missing `tenant_id` in one query—BOLA. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Enterprise silo provisioning?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: 5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign… Common miss: Missing `tenant_id` in one query—BOLA. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka multi-tenancy?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: 5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign… Common miss: Missing `tenant_id` in one query—BOLA. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Multi-tenant SaaS.—error budget is burning.

**Model answer:** Pick isolation model early: shared schema + `tenant_id` column, schema-per-tenant, or silo-per-tenant—trade cost vs blast radius. Every query and Kafka key carries tenant context; JWT claim enforced in repository layer,  In practice: 5000 SMB merchants share Azure SQL with `tenant_id`; enterprise bank gets dedicated SQL + namespace provisioned by Terraform pipeline triggered on contract sign. React admin passes… I check whether we hit a known mistake (Missing `tenant_id` in one query—BOLA. Global cache poisoning. Tenant in URL onl…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 8. File upload (KYC docs).

**Short answer:** Browser uploads directly to Azure Blob via short-lived SAS or pre-signed URL; metadata in SQL; virus scan + manual review queue; never stream large files through Spring Boot pod memory.

#### What it is
KYC document flow: passport, utility bill. Design covers encryption at rest, PII access audit, retention, and async verification—not multipart to JVM heap.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`POST /uploads/init` returns SAS URL + `uploadId`. Client PUTs to Blob. Callback or Event Grid triggers scan function (ClamAV). `kyc_documents` table stores blob path, hash, status `PENDING_REVIEW`. Admin React back office lists queue; approve/reject updates merchant status. TLS everywhere; customer-managed keys for enterprise. Delete blob on retention expiry job.

#### When to use / when NOT to use
Direct-to-blob always for >5MB. Sync through API only for tiny avatars with size cap. PCI KYC still not PAN—separate controls.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Azure Function ClamAV scan; on clean, publishes Kafka `kyc-events` consumed by compliance Spring worker updating `kyc_documents.status`. Admin React queue shows pending items with signed read URL expiring 15 min. Spring API never buffers file bytes—pod memory stays flat under concurrent uploads. Helm workload identity grants `Storage Blob Data Contributor` without account keys in cluster.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
OOM on large multipart through Tomcat. Public blob container ACL. No malware scan before analyst opens file. PII filename in application logs on upload failure. SAS TTL too long—leaked URL window.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** SAS vs proxy upload?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Az… Common miss: OOM on large multipart through Tomcat. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Scan pipeline?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Az… Common miss: OOM on large multipart through Tomcat. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Retention policy?
**A:** I publish a green/yellow/red allowlist in CONTRIBUTING: tests and README in green; Kafka listeners and Helm prod in yellow; authz, IAM, and large Flyway in red. Example: Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Az… Common miss: OOM on large multipart through Tomcat. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Admin review UX?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Az… Common miss: OOM on large multipart through Tomcat. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for File upload (KYC docs).—error budget is burning.

**Model answer:** Browser uploads directly to Azure Blob via short-lived SAS or pre-signed URL; metadata in SQL; virus scan + manual review queue; never stream large files through Spring Boot pod memory. In practice: Fintech onboarding: React requests SAS from `POST /kyc/uploads/init`; PUTs 4MB passport image directly to Blob path `kyc/{tenantId}/{uuid}`. Event Grid fires Azure Function ClamAV … I check whether we hit a known mistake (OOM on large multipart through Tomcat. Public blob container ACL. No malware sca…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 9. Real-time order status.

**Short answer:** Combine short-poll or SSE from BFF with Kafka-driven projection; WebSocket optional for high-touch tracking—always show stale indicator and reconcile with `GET /orders/{id}` ETag.

#### What it is
Customers expect live order tracking without hammering OLTP. Design balances freshness, connection cost, and mobile battery.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`order-service` updates status in SQL; outbox publishes `OrderStatusChanged`. `order-status-projector` updates Redis or materialized view. BFF SSE endpoint streams events per `orderId` with auth check. React subscribes while tab active; falls back to poll every 30s. Mobile uses FCM push for shipped. p99 staleness 2s acceptable; source of truth remains SQL on refresh.

#### When to use / when NOT to use
SSE for web order tracker. WebSocket if bidirectional chat with driver. Poll-only for MVP low traffic. Do not query Kafka from browser.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderStatusChanged` event. React Query `useEffect` opens EventSource with bearer token in query param or cookie; exponential backoff reconnect on proxy timeout. Black Friday: dedicated `order-bff-sse` Deployment with 2× connection limits in Helm; APIM timeout raised to 120s for long-lived streams. Fallback poll every 45s when SSE unavailable on corporate proxy.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Client polls OLTP every second—DB melts. WebSocket subscribe without verifying JWT owns `orderId` (BOLA). Showing driver GPS without privacy consent and retention policy. No UX handling when SSE drops mid-payment—user thinks order failed.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** SSE vs WebSocket?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderS… Common miss: Client polls OLTP every second—DB melts. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Cache invalidation?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderS… Common miss: Client polls OLTP every second—DB melts. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Mobile push integration?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderS… Common miss: Client polls OLTP every second—DB melts. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Staleness UX?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderS… Common miss: Client polls OLTP every second—DB melts. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Real-time order status.—error budget is burning.

**Model answer:** Combine short-poll or SSE from BFF with Kafka-driven projection; WebSocket optional for high-touch tracking—always show stale indicator and reconcile with `GET /orders/{id}` ETag. In practice: AKS hosts `order-bff` exposing `GET /orders/{id}/stream` as SSE; `order-status-projector` consumer writes Redis `order:{id}:status` with 24h TTL on each `OrderStatusChanged` event.… I check whether we hit a known mistake (Client polls OLTP every second—DB melts. WebSocket subscribe without verifying J…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 10. Admin back office vs customer SPA.

**Short answer:** Separate React apps or routes with different auth (Entra ID groups), stricter audit, heavier queries, and BFF endpoints—not the same controllers with hidden admin params. Admin can tolerate higher latency; needs export and bulk actions.

#### What it is
Back office supports CS agents, catalog editors, finance reconcile. Threat model differs: powerful actions, BOLA across tenants if misconfigured.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`admin.acme.com` SPA with Entra ID + role `ORDER_ADMIN`. `admin-bff` Spring service with broader queries, cursor pagination, CSV export to Blob async job. Customer SPA on `shop.acme.com` with stripped DTOs. Shared Kafka events but separate read models where needed. All admin mutations audit-logged to immutable store.

#### When to use / when NOT to use
Split when admin features >20% API surface or compliance mandates separation. Single SPA with role guards only for tiny teams—document migration path.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET /admin/orders/search` with cursor pagination and `POST /admin/orders/{id}/cancel` requiring step-up MFA via Conditional Access. Customer JWT cannot call admin routes—APIM policy blocks by audience claim. Bulk CSV export of 50k orders runs as async job writing to Blob; admin polls `GET /jobs/{id}` rather than blocking HTTP. Every admin mutation writes `audit_events` row consumed by compliance SIEM. Helm deploys `admin-bff` in `admin` namespace with NetworkPolicy denying ingress from customer namespace.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
`?isAdmin=true` query param on shared customer controller. Shared JWT scope `orders:write` for both apps. Admin export synchronous—gateway timeout at 30s. No audit on refund button—SOC2 finding.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Same BFF or split?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET… Common miss: `?isAdmin=true` query param on shared customer controller. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Auth difference?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET… Common miss: `?isAdmin=true` query param on shared customer controller. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Bulk export design?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET… Common miss: `?isAdmin=true` query param on shared customer controller. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Audit requirements?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET… Common miss: `?isAdmin=true` query param on shared customer controller. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Admin back office vs customer SPA.—error budget is burning.

**Model answer:** Separate React apps or routes with different auth (Entra ID groups), stricter audit, heavier queries, and BFF endpoints—not the same controllers with hidden admin params. Admin can tolerate higher latency; needs export a In practice: Customer SPA on `shop.acme.com` with Entra B2C; admin on `admin.acme.com` behind corporate Entra ID group `ORDER_ADMIN`. `admin-bff` Spring service exposes `GET /admin/orders/searc… I check whether we hit a known mistake (`?isAdmin=true` query param on shared customer controller. Shared JWT scope `ord…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 11. Reporting.

**Short answer:** Operational reports and finance dashboards read from warehouse (Snowflake, Azure Synapse, or read replica)—never heavy aggregations on OLTP during peak. Kafka CDC or nightly ETL feeds star schema; React admin embeds Power BI or pre-aggregated API.

#### What it is
Reporting is read path with different SLAs: minutes/hours lag OK, complex joins OK, must not slow checkout. Separates OLTP schema from analyst-friendly dimensions.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Kafka Connect or ADF pipelines `order-events` to warehouse. Fact `orders`, dims `customer`, `product`, `date`. Materialized views for daily GMV. Admin React calls reporting API with date range—query warehouse with row-level security matching tenant. Ad hoc SQL only for analysts, not production microservice. Cache dashboard tiles 15 min.

#### When to use / when NOT to use
Replica/warehouse at >100GB OLTP or when finance needs historical trends. MVP: nightly batch job copying summaries table—upgrade before Black Friday OLTP chokes on `GROUP BY`.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `fct_orders` and `dim_customer` with `tenant_id` row-level security for embedded Power BI. CFO dashboard queries Synapse only—zero DTU impact on checkout during month-end close. Ad hoc analyst SQL runs in read-only workspace; cannot join back to prod connection string. Stale warehouse 15 min acceptable for revenue flash report; finance signs SLA.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m. Real-time CFO dashboard on OLTP—locks during batch. Missing tenant filter in warehouse RLS—cross-merchant leak in BI. Kafka consumer doing monthly aggregation inline—consumer lag incident.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** CDC vs batch ETL?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `f… Common miss: Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Replica lag tolerance?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `f… Common miss: Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Embed vs custom charts?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `f… Common miss: Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Finance reconcile source?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `f… Common miss: Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Reporting.—error budget is burning.

**Model answer:** Operational reports and finance dashboards read from warehouse (Snowflake, Azure Synapse, or read replica)—never heavy aggregations on OLTP during peak. Kafka CDC or nightly ETL feeds star schema; React admin embeds Powe In practice: Orders OLTP on Azure SQL Hyperscale; Azure Data Factory copies `order-events` from Event Hubs to Synapse nightly and incremental CDC every 15 min. dbt builds `fct_orders` and `dim_… I check whether we hit a known mistake (Report microservice running `SELECT SUM(total) FROM orders` on primary at 2 p.m.…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 12. CQRS for a product catalog.

**Short answer:** Command side writes product master in OLTP; query side serves denormalized catalog reads from Redis or read DB fed by Kafka—accept eventual consistency on browse, revalidate price/stock at cart.

#### What it is
CQRS splits write model from read model when read patterns differ radically (faceted browse vs rare admin edits). Not mandatory for CRUD catalog—earn complexity with measured pain.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`PUT /admin/products` updates Azure SQL normalized tables, emits `ProductUpdated`. Projector builds Redis hash `product:{id}` and search document. React PLP reads query API; PDP merges query view with live `GET /inventory/{sku}` for buy box. Version field on product detects stale cache. Replay projector from Kafka offset for rebuild.

#### When to use / when NOT to use
Use when read:write ratio >50:1 and joins hurt. Skip CQRS on 200 products—YAGNI. Do not call it CQRS if you only added Redis cache—name honestly.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redis cluster. Black Friday browse survives; admin edit visible in 5s.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
CQRS without rebuild story. Query side authoritative for stock. No versioning—stale PDP price. Dual-write instead of event projection.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** When CQRS overkill?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redi… Common miss: CQRS without rebuild story. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Rebuild projector how?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redi… Common miss: CQRS without rebuild story. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Cart price validation?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redi… Common miss: CQRS without rebuild story. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Event schema evolution?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redi… Common miss: CQRS without rebuild story. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for CQRS for a product catalog.—error budget is burning.

**Model answer:** Command side writes product master in OLTP; query side serves denormalized catalog reads from Redis or read DB fed by Kafka—accept eventual consistency on browse, revalidate price/stock at cart. In practice: Marketplace catalog: 50k admin updates/day, 2M reads/min. `catalog-query-service` scales 20 pods on AKS; `catalog-command` three pods. Terraform provisions Redis cluster. Black Fri… I check whether we hit a known mistake (CQRS without rebuild story. Query side authoritative for stock. No versioning—st…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```text
Command: PUT /admin/products/{id} → SQL → outbox → ProductUpdated
Query:   GET /catalog/products/{id} → Redis (eventually consistent)
Checkout: GET /inventory/{sku} → OLTP authoritative
```

---

### 13. Rate limiting.

**Short answer:** Rate limit at edge (APIM/Azure Front Door) by IP/API key/user; stricter on auth and payment endpoints; return 429 with `Retry-After`; backend still validates—edge limit is first shield, not only defense.

#### What it is
Rate limiting protects OLTP, PSP, and neighbor tenants from abuse, scrapers, and accidental retry storms. Design names limits per endpoint class and override for partners.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
APIM policies: 100 req/min per subscription key on catalog; 10/min on `POST /orders` per user JWT `sub`. Token bucket in Redis for distributed limit inside cluster if APIM insufficient. Kafka consumers throttle downstream PSP calls. React backs off on 429 with jitter. Whitelist internal batch jobs by mTLS identity.

#### When to use / when NOT to use
Always on public APIs. Higher limits for B2B partners with contract. Do not rate-limit health checks. Coordinate with WAF DDoS rules.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec global semaphore in Redis. Helm ConfigMap stores limits; Terraform APIM policy as code.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Limit only at gateway—internal service still hammered. No `Retry-After`. Same limit for read and write. Blocking entire tenant for one bad IP on shared NAT.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** APIM vs app-level limit?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec … Common miss: Limit only at gateway—internal service still hammered. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Partner burst allowance?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec … Common miss: Limit only at gateway—internal service still hammered. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** 429 client handling?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec … Common miss: Limit only at gateway—internal service still hammered. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PSP rate coordination?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec … Common miss: Limit only at gateway—internal service still hammered. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Rate limiting.—error budget is burning.

**Model answer:** Rate limit at edge (APIM/Azure Front Door) by IP/API key/user; stricter on auth and payment endpoints; return 429 with `Retry-After`; backend still validates—edge limit is first shield, not only defense. In practice: Checkout `POST /orders` 5 req/min/user prevents card testing attack. APIM returns 429; React shows "try again." Payment service separate limit 20 PSP calls/sec global semaphore in … I check whether we hit a known mistake (Limit only at gateway—internal service still hammered. No `Retry-After`. Same li…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 14. Idempotency across the stack.

**Short answer:** Idempotency keys on HTTP POST from React through BFF to service; DB unique constraints; Kafka consumers use inbox/`processed_events` table; PSP calls keyed—same business operation must survive retries at every hop.

#### What it is
Distributed systems retry. Idempotency is the glue preventing duplicate orders, double charges, and duplicate emails. Design documents key storage TTL and conflict response semantics.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Client generates UUID `Idempotency-Key` header on `POST /orders`. Server stores `(key, tenant_id) → response` 24h; replay returns same `201` body. Kafka consumer: `INSERT INTO inbox(event_id) ON CONFLICT DO NOTHING` then process. Payment PSP idempotency key = orderId + attempt. React disables double-submit; still send key on background retry.

#### When to use / when NOT to use
Mandatory on all mutating APIs and consumers touching money/inventory. GET safe by definition. DELETE idempotent by resource id. TTL keys after response stable.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constraint no-ops second insert. Notification worker skips duplicate `notification_log` row.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Idempotency only at gateway. Key only in memory—lost on pod restart. No unique constraint on consumer inbox. Different keys on client retry.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Key TTL how long?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constrain… Common miss: Idempotency only at gateway. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** 409 vs replay same 201?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constrain… Common miss: Idempotency only at gateway. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka inbox schema?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constrain… Common miss: Idempotency only at gateway. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PSP key format?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constrain… Common miss: Idempotency only at gateway. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Idempotency across the stack.—error budget is burning.

**Model answer:** Idempotency keys on HTTP POST from React through BFF to service; DB unique constraints; Kafka consumers use inbox/`processed_events` table; PSP calls keyed—same business operation must survive retries at every hop. In practice: Mobile app retries `POST /orders` on timeout—server returns original orderId from idempotency store. Payment webhook redelivered—`psp_event_id` unique constraint no-ops second inse… I check whether we hit a known mistake (Idempotency only at gateway. Key only in memory—lost on pod restart. No unique c…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```java
@PostMapping("/orders")
public ResponseEntity<OrderResponse> place(@RequestHeader("Idempotency-Key") String key,
    @RequestBody PlaceOrderRequest req) {
  return idempotencyStore.executeOnce(key, () -> orderService.place(req));
}
```

---

### 15. Tracing a click to Kafka to DB.

**Short answer:** W3C `traceparent` from React (fetch interceptor) through APIM/BFF to Spring Micrometer tracing, propagated to Kafka headers and JDBC—one traceId in Grafana/Jaeger from button click to SQL insert and consumer span.

#### What it is
End-to-end tracing proves you can debug latency and prove saga path in interview. Ties frontend action to backend spans without hand-waving "we have logs."  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
React OpenTelemetry web SDK or BFF generates trace on `POST /orders`. Spring Boot 3 `micrometer-tracing-bridge-otel` exports to Azure Monitor or Tempo. Kafka producer interceptor injects trace context in headers; consumer continues span. SQL span shows query time. Log correlation: `traceId` in JSON logs. Sample 10% prod, 100% staging errors.

#### When to use / when NOT to use
Instrument all sync path + Kafka consumers on day one of microservices. Skip full browser OTel if BFF is single entry—BFF span enough for MVP. Always propagate on payment path.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`. Slow inventory lock identified. Helm chart sets `OTEL_EXPORTER_OTLP_ENDPOINT`.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Broken context at Kafka boundary. APIM strips headers. No trace in batch jobs. Logs without traceId grep useless at scale.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Header names propagated?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`… Common miss: Broken context at Kafka boundary. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Sampling strategy?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`… Common miss: Broken context at Kafka boundary. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Azure Monitor vs self-hosted?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`… Common miss: Broken context at Kafka boundary. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Broken trace debugging?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`… Common miss: Broken context at Kafka boundary. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Tracing a click to Kafka to DB.—error budget is burning.

**Model answer:** W3C `traceparent` from React (fetch interceptor) through APIM/BFF to Spring Micrometer tracing, propagated to Kafka headers and JDBC—one traceId in Grafana/Jaeger from button click to SQL insert and consumer span. In practice: User clicks Place Order; Jaeger shows: `http POST 180ms` → `order-service placeOrder 120ms` → `jdbc insert 40ms` → `kafka send 15ms` → `inventory-consumer 90ms`. Slow inventory loc… I check whether we hit a known mistake (Broken context at Kafka boundary. APIM strips headers. No trace in batch jobs. L…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```yaml
# application.yaml
management.tracing.sampling.probability: 0.1
spring.kafka.producer.properties.interceptor.classes: io.opentelemetry.instrumentation.kafkaclients.TracingProducerInterceptor
```

---

### 16. SLO design.

**Short answer:** Pick user-journey SLOs—checkout p99 <3s, order API availability 99.9%, Kafka consumer lag <30s—and derive SLIs from metrics you already emit. Error budget drives release policy; SLO on "Kubernetes up" is useless.

#### What it is
SLOs align engineering with business risk. Fullstack design names what good looks like for shopper path vs admin vs async pipeline.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
SLI examples: Micrometer `http_server_requests_seconds` p99 for `POST /orders`, success rate excluding 4xx client errors, `kafka_consumer_records_lag` max per group, `outbox_pending_count` gauge. SLO 99.9% monthly availability ≈ 43 minutes error budget. Multi-window burn-rate alerts (Google SRE workbook) page on-call before budget exhausted in hours. Document which SLO is customer-facing (checkout) vs internal (email delivery). Error budget policy: freeze risky Friday deploys when 50% budget burned before month end.

#### When to use / when NOT to use
Define SLO before launch for revenue paths. Internal-only batch can be 99%. Do not SLO everything—three critical journeys max initially.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day rolling window; product gets weekly error budget report. Notification email tier-2 SLO: 99% delivered within 5 minutes—pages email on-call, not checkout on-call. Black Friday: pre-approved temporary SLO waiver documented with customer comms plan—not silent threshold change.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
SLO on pod CPU instead of shopper latency. No exclusion annotation for planned Helm maintenance windows. Same 99.99% target for beta sandbox and prod—team ignores SLO. Measuring SLIs without alert routing—dashboard vanity.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Three SLOs for order flow?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day roll… Common miss: SLO on pod CPU instead of shopper latency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Error budget policy?
**A:** I publish a green/yellow/red allowlist in CONTRIBUTING: tests and README in green; Kafka listeners and Helm prod in yellow; authz, IAM, and large Flyway in red. Example: Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day roll… Common miss: SLO on pod CPU instead of shopper latency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** SLI vs SLAs to customers?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day roll… Common miss: SLO on pod CPU instead of shopper latency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka lag SLO?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day roll… Common miss: SLO on pod CPU instead of shopper latency. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for SLO design.—error budget is burning.

**Model answer:** Pick user-journey SLOs—checkout p99 <3s, order API availability 99.9%, Kafka consumer lag <30s—and derive SLIs from metrics you already emit. Error budget drives release policy; SLO on "Kubernetes up" is useless. In practice: Checkout journey SLO: 99.95% availability and p99 <2.5s on `POST /orders` measured at APIM edge—excludes client network. Grafana SLO dashboard shows 28-day rolling window; product … I check whether we hit a known mistake (SLO on pod CPU instead of shopper latency. No exclusion annotation for planned H…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 17. Capacity.

**Short answer:** Estimate from peak QPS × request cost: thread pools, DB connections, Kafka partitions, and pod CPU—load test validates; plan 2× headroom for flash sales; scale DB and consumers independently.

#### What it is
Capacity planning connects design boxes to numbers: orders/sec, KB per event, connection pool size, partition count. Interviewers want math, not "we'll autoscale."  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Example: 500 orders/sec peak, 50ms service time → 25 concurrent threads minimum per instance; 10 pods → pool sizing. Kafka: target 1MB/s per partition, key by orderId, 24 partitions for parallel consumers. Azure SQL vCores from DTU calc + read replica for reporting. HPA on CPU and custom metric consumer lag. Terraform variables for node pool max.

#### When to use / when NOT to use
Rough napkin math in design interview; detailed Gatling before launch. Revisit after 10× growth or new market. Do not partition Kafka to 1000 on day one—rebalance cost.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Helm `resources.requests` set from load test, not defaults.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
HPA only on CPU while DB saturates. One consumer per partition forgotten. Connection pool × pods > DB max connections. No capacity for webhook burst.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Partition count formula?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Hel… Common miss: HPA only on CPU while DB saturates. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** DB connection math?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Hel… Common miss: HPA only on CPU while DB saturates. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Pre-scale vs reactive?
**A:** AI drafts inside guardrails—sister Helm chart, EXPLAIN on SQL, conventional commits I edit—then Checkov, compile, and human review. Example: Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Hel… Common miss: HPA only on CPU while DB saturates. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Load test tool choice?
**A:** PR template requires `./mvnw verify` and at least one failure-case test written without AI; mutation or ArchUnit catches weak asserts AI loves. Example: Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Hel… Common miss: HPA only on CPU while DB saturates. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Capacity.—error budget is burning.

**Model answer:** Estimate from peak QPS × request cost: thread pools, DB connections, Kafka partitions, and pod CPU—load test validates; plan 2× headroom for flash sales; scale DB and consumers independently. In practice: Black Friday 3× normal: pre-scale AKS node pool min 20, SQL tier bump week prior, Kafka partitions pre-provisioned. Gatling script in CI nightly on staging. Helm `resources.request… I check whether we hit a known mistake (HPA only on CPU while DB saturates. One consumer per partition forgotten. Connec…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 18. Failure: payment captured, order not confirmed.

**Short answer:** Reconcile job compares PSP settlements to `orders` + `payments` tables; saga timeout marks `PAYMENT_UNKNOWN`; manual/automated refund if order stuck `PENDING_PAYMENT` with capture_id; never ignore—money moved without fulfillment is top incident class.

#### What it is
Split-brain between payment success and order state happens on network timeout, consumer crash after capture, or duplicate webhook. Design requires reconciliation and compensating refund—not hope.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Payment consumer idempotent on webhook `CAPTURED` → update order `PAID`. If HTTP to client timed out after capture, client retries with idempotency key—server returns same order. Background reconcile every 15 min: PSP report vs DB `payment_status=CAPTURED AND order_status!=PAID`. Alert + auto-refund policy or CS queue. Audit log every refund with `capture_id`. Kafka DLQ for poison payment events.

#### When to use / when NOT to use
Build reconcile before prod payments. Manual spreadsheet reconcile only as temporary bridge. Compensate with refund API, not DB delete.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem adds inventory consumer HA and lag alert.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
No reconcile job. Trust client to retry forever. Refund without linking ledger entry. Hiding stuck state in UI as "processing" indefinitely.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Reconcile frequency?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem… Common miss: No reconcile job. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Auto-refund threshold?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem… Common miss: No reconcile job. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Customer communication?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem… Common miss: No reconcile job. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Ledger entries on refund?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem… Common miss: No reconcile job. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Failure: payment captured, order not confirmed.—error budget is burning.

**Model answer:** Reconcile job compares PSP settlements to `orders` + `payments` tables; saga timeout marks `PAYMENT_UNKNOWN`; manual/automated refund if order stuck `PENDING_PAYMENT` with capture_id; never ignore—money moved without ful In practice: Adyen webhook arrives; inventory consumer down 20 min—order stuck. Reconcile detects; auto-refund after 30 min policy; customer email explains delay. Postmortem adds inventory cons… I check whether we hit a known mistake (No reconcile job. Trust client to retry forever. Refund without linking ledger e…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```sql
-- reconcile candidates
SELECT p.capture_id, o.id, o.status
FROM payments p JOIN orders o ON p.order_id = o.id
WHERE p.status = 'CAPTURED' AND o.status NOT IN ('PAID','SHIPPED','CANCELLED');
```

---

### 19. Failure: Kafka down.

**Short answer:** Order OLTP still accepts orders if business allows async side effects delayed—outbox buffers events; alert on relay lag; degrade notifications/inventory sync with clear UX; do not pretend synchronous saga completed.

#### What it is
Kafka unavailable means choreography pauses—not necessarily total outage. Design states which features degrade and how outbox prevents message loss.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Transactional outbox in SQL holds events until broker returns. Relay retries with backoff; lag metric pages platform. `POST /orders` may still succeed if policy is "capture order now, fulfill later." Inventory reservation might block if cannot publish—product choice: pessimistic reserve in same TX as order without Kafka, or reject checkout with 503. React shows "confirmation delayed" if async pipeline stale. Multi-AZ Event Hubs reduces single-broker risk.

#### When to use / when NOT to use
Outbox mandatory if Kafka is part of write path. Run game day Kafka blackout. Do not lose events in memory queue on pod crash.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; checkout stayed up per ADR. Consumer lag alert fired at 2 min.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
In-memory publish before commit. No outbox—events lost. Claiming exactly-once without explaining buffer. User sees "shipped" when consumer never ran.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Accept orders when Kafka down?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; check… Common miss: In-memory publish before commit. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Outbox relay monitoring?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; check… Common miss: In-memory publish before commit. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** UX degradation message?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; check… Common miss: In-memory publish before commit. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Multi-region Kafka?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; check… Common miss: In-memory publish before commit. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Failure: Kafka down.—error budget is burning.

**Model answer:** Order OLTP still accepts orders if business allows async side effects delayed—outbox buffers events; alert on relay lag; degrade notifications/inventory sync with clear UX; do not pretend synchronous saga completed. In practice: Event Hubs outage 12 min: orders accumulate in outbox, relay catches up without duplicate publish due to monotonic outbox id. Email notifications delayed; checkout stayed up per AD… I check whether we hit a known mistake (In-memory publish before commit. No outbox—events lost. Claiming exactly-once wi…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 20. Failure: Oracle down.

**Short answer:** Primary OLTP down is sev-1: fail fast on writes with 503, serve read-only catalog from cache if stale OK, queue critical admin actions, execute DR failover per RTO—Kafka consumers backlog until DB returns; do not dual-write to random store.

#### What it is
Database outage tests whether design has read replicas, caching, and honest failure modes—not silent corruption. Many enterprises still on Oracle RAC/Data Guard.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Health check fails `readiness`—Kubernetes stops routing writes. Read replica promotes in DR per runbook (45 min RTO example). React maintenance page for checkout; browse from CDN+cache with banner. Consumers pause or retry idempotently—lag grows. No "write to local SQLite" hacks. Flyway migrations paused. Terraform DR region standby costs documented.

#### When to use / when NOT to use
Game day DB failover annually. Cache stale browse only if business accepts. Payment capture may need PSP pause if cannot record—coordinate with finance.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: manual Data Guard switchover per runbook.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Retry storm without backoff killing DB on recovery. Serving writes to replica. No readiness probe—traffic to dead pods. Consumers corrupt data without idempotency after duplicate processing.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** RTO/RPO targets?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: m… Common miss: Retry storm without backoff killing DB on recovery. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Read during write outage?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: m… Common miss: Retry storm without backoff killing DB on recovery. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Consumer behavior?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: m… Common miss: Retry storm without backoff killing DB on recovery. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Failover automation level?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: m… Common miss: Retry storm without backoff killing DB on recovery. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Failure: Oracle down.—error budget is burning.

**Model answer:** Primary OLTP down is sev-1: fail fast on writes with 503, serve read-only catalog from cache if stale OK, queue critical admin actions, execute DR failover per RTO—Kafka consumers backlog until DB returns; do not dual-wr In practice: Azure SQL failover group auto-failover 30s; apps reconnect via JDBC failover partner. 2 min blip on checkout. Oracle RAC node loss: transparent; full DC loss: manual Data Guard swi… I check whether we hit a known mistake (Retry storm without backoff killing DB on recovery. Serving writes to replica. N…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 21. Blue/green with schema.

**Short answer:** Blue/green deploys new app version (green) beside old (blue); traffic switch via Ingress/APIM after smoke tests—schema migrations must be expand-contract: backward-compatible first, then code switch, then cleanup migration.

#### What it is
Blue/green reduces deploy risk on AKS. Schema coupling kills naive blue/green—new code on old schema or old code on new column breaks one side.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Phase 1 migration: add nullable column `shipping_tier`. Deploy green pods reading/writing both columns. Switch traffic 10%→100% via APIM weight or second Helm release. Phase 2: remove old column after blue decommission. Kafka consumers: deploy green consumers with new schema handler before switch. Rollback = traffic back to blue if schema compatible.

#### When to use / when NOT to use
Use for high-risk payment deploys. Rolling update fine for stateless typo fixes. Never drop column same release as code depending on it.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
`order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods drained. V43 drop deprecated flag next week.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Breaking migration with blue still running. Shared database session state between colors. Forgetting Kafka consumer compatibility. Green never gets traffic—stale environment.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Expand-contract example?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: `order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods draine… Common miss: Breaking migration with blue still running. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka schema in blue/green?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: `order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods draine… Common miss: Breaking migration with blue still running. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Rollback with migration?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: `order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods draine… Common miss: Breaking migration with blue still running. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** APIM vs Ingress switch?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods draine… Common miss: Breaking migration with blue still running. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Blue/green with schema.—error budget is burning.

**Model answer:** Blue/green deploys new app version (green) beside old (blue); traffic switch via Ingress/APIM after smoke tests—schema migrations must be expand-contract: backward-compatible first, then code switch, then cleanup migrati In practice: `order-service` v2 adds `cancel_reason`. Flyway V42 add column nullable. Green Helm release `order-service-green` passes smoke; APIM routes 100%. v1 pods drained. V43 drop deprecat… I check whether we hit a known mistake (Breaking migration with blue still running. Shared database session state betwee…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```yaml
# Helm: green deployment alongside blue
fullnameOverride: order-service-green
service:
  labels:
    slot: green
```

---

### 22. Feature flag + Kafka.

**Short answer:** LaunchDarkly/Unleash flag gates new consumer logic or topic routing—deploy code dark, enable per tenant, kill switch without redeploy; flags do not replace schema compatibility or idempotent consumers.

#### What it is
Feature flags decouple deploy from release for risky saga steps or new payment provider. Kafka adds complexity: flag must be evaluated per message or per consumer instance consistently.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Flag `new-inventory-reservation` checked in consumer before calling new algorithm; default off in prod. React checkout flag for UI only—server enforces same flag on API. Avoid splitting traffic by partition without sticky tenant mapping. Document flag cleanup ticket—permanent `if (flag)` rot. Spring `@ConditionalOnProperty` for coarse enablement in lower envs.

#### When to use / when NOT to use
Gradual rollout of new PSP or tax engine. Not for emergency kill switch on fire—use circuit breaker + traffic shift. Remove flag within 2 sprints after full enable.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders route to legacy Stripe path. Post-flag removal deletes dead code path.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Flag only in frontend. Different flag state per pod causing split brain. Kafka topic per flag without consumer capacity. Never removing flags.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Flag eval in consumer?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders … Common miss: Flag only in frontend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kill switch vs flag?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders … Common miss: Flag only in frontend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Tenant gradual rollout?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders … Common miss: Flag only in frontend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Flag cleanup process?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders … Common miss: Flag only in frontend. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Feature flag + Kafka.—error budget is burning.

**Model answer:** LaunchDarkly/Unleash flag gates new consumer logic or topic routing—deploy code dark, enable per tenant, kill switch without redeploy; flags do not replace schema compatibility or idempotent consumers. In practice: New Adyen integration behind flag; internal tenants on first week. Kafka consumer reads flag from SDK cache 30s TTL. Incident: flag off globally in 10s; orders route to legacy Stri… I check whether we hit a known mistake (Flag only in frontend. Different flag state per pod causing split brain. Kafka t…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 23. Security architecture.

**Short answer:** Defense in depth: Entra ID/OAuth2 for users, mTLS or subscription keys service-to-service, APIM WAF, private AKS networking, workload identity to Key Vault, BOLA checks in every repository query, Kafka ACLs, and audit on admin mutations.

#### What it is
Security architecture is trust boundaries across React, BFF, microservices, data stores, and third parties—not a single "JWT everywhere" sentence.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
User JWT short-lived; BFF exchanges for service token or passes user claims. Network policies deny pod-to-pod except allowlist. Secrets from External Secrets Operator—never Helm values. PSP webhooks verify HMAC. SQL parameterized; OWASP API Top 10 checklist on design review. PII encrypted at rest; field-level encryption for tax IDs if required. Break-glass admin roles MFA + session recording.

#### When to use / when NOT to use
Threat model every external integration. Zero-trust between namespaces in multi-tenant silo. Do not roll custom crypto—use platform primitives.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform deploys private AKS + Azure Firewall egress allowlist to PSP IPs.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Long-lived API keys in mobile app. Trusting `userId` query param. Flat network in cluster. Secrets in git. Admin API without step-up MFA.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** BOLA prevention pattern?
**A:** Security stays human-reviewed: Semgrep, BOLA tests, and no AI-only `SecurityFilterChain`—I reject permissive CORS and hardcoded keys in generated tests. Example: React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform… Common miss: Long-lived API keys in mobile app. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Service-to-service auth?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform… Common miss: Long-lived API keys in mobile app. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka ACL model?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform… Common miss: Long-lived API keys in mobile app. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PCI network segmentation?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform… Common miss: Long-lived API keys in mobile app. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Security architecture.—error budget is burning.

**Model answer:** Defense in depth: Entra ID/OAuth2 for users, mTLS or subscription keys service-to-service, APIM WAF, private AKS networking, workload identity to Key Vault, BOLA checks in every repository query, Kafka ACLs, and audit on In practice: React PKCE to Entra; APIM validates JWT; `order-service` checks `tenant_id` claim matches row. Kafka ACL: `order-service` produce `order-events` only. Terraform deploys private AKS… I check whether we hit a known mistake (Long-lived API keys in mobile app. Trusting `userId` query param. Flat network i…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 24. Secrets rotation.

**Short answer:** Short-lived credentials via workload identity; database passwords in Key Vault rotated on schedule; apps reload via External Secrets Operator refresh; zero-downtime rotation requires dual-credential window or connection pool drain—document in runbook.

#### What it is
Secrets rotation limits blast radius of leak. Design covers K8s secrets, DB users, API keys to PSP, and TLS certs—not one-time setup.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
AKS workload identity → Key Vault secret `db-password-v2`. ESO syncs to K8s Secret; pod restart or Spring Cloud refresh reloads. Rotation: create `user_app_v2` in SQL, deploy with new secret, revoke `v1` after pool drain. APIM subscription keys rotated quarterly with partner notice. Cert-manager auto-renews Ingress TLS. Never bake secrets in Terraform state plaintext—use vault references.

#### When to use / when NOT to use
Automate cert and DB rotation prod. Manual rotation acceptable dev. Game day rotation drill yearly.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transactions due to Hikari validation query retry. PSP API key rotation coordinated with dual-key support window.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Single shared DB password forever. Rotation requires full outage. Secrets logged on connection failure. Terraform tfvars in git.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Workload identity flow?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transac… Common miss: Single shared DB password forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Zero-downtime DB password?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transac… Common miss: Single shared DB password forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** ESO refresh interval?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transac… Common miss: Single shared DB password forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PSP key dual-active?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transac… Common miss: Single shared DB password forever. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Secrets rotation.—error budget is burning.

**Model answer:** Short-lived credentials via workload identity; database passwords in Key Vault rotated on schedule; apps reload via External Secrets Operator refresh; zero-downtime rotation requires dual-credential window or connection  In practice: Monthly Azure SQL password rotation via automation runbook; ESO updates Secret; rolling restart `order-service` Deployment maxUnavailable 1. Zero failed transactions due to Hikari … I check whether we hit a known mistake (Single shared DB password forever. Rotation requires full outage. Secrets logged…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 25. Cost-aware design.

**Short answer:** Right-size AKS node pools, SQL tier, Kafka retention, and egress; use reserved capacity for baseline; cold storage for old orders; avoid over-partitioning and 24/7 max scale—cost is NFR with trade-off explicit in design.

#### What it is
Seniors justify Azure bill: scale-to-zero where possible, tiered storage, async over sync workers, managed services vs self-operated Kafka unless volume demands.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Orders hot 90 days in SQL; archive to Blob parquet via job. Event Hubs vs self-hosted Kafka TCO at 500MB/s break-even analysis. AKS cluster autoscaler min nodes off-peak. APIM consumption tier dev, premium prod. Terraform tags `cost-center` per namespace. Review monthly FinOps dashboard; right-size over-provisioned Helm `resources.limits`.

#### When to use / when NOT to use
Mention cost when interviewer asks scale-down or startup budget. Do not optimize pennies before product-market fit—do avoid architectural million-dollar mistakes (cross-region egress flood).  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka cluster at current 50MB/s—revisit at 200MB/s in ADR.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Max replicas 24/7 from load test peak. Infinite Kafka retention. Cross-region replication without business need. Giant AKS nodes for tiny Java heap.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Archive strategy?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka clust… Common miss: Max replicas 24/7 from load test peak. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Managed vs self-hosted Kafka cost?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka clust… Common miss: Max replicas 24/7 from load test peak. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** FinOps review cadence?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka clust… Common miss: Max replicas 24/7 from load test peak. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Egress optimization?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka clust… Common miss: Max replicas 24/7 from load test peak. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Cost-aware design.—error budget is burning.

**Model answer:** Right-size AKS node pools, SQL tier, Kafka retention, and egress; use reserved capacity for baseline; cold storage for old orders; avoid over-partitioning and 24/7 max scale—cost is NFR with trade-off explicit in design. In practice: Notification email batch nightly reduces SendGrid cost vs per-event API. Synapse pause off-hours saves 40%. Chose Event Hubs Standard over dedicated Kafka cluster at current 50MB/s… I check whether we hit a known mistake (Max replicas 24/7 from load test peak. Infinite Kafka retention. Cross-region re…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 26. Team boundaries.

**Short answer:** Align services to team ownership (Conway's law): order squad owns `order-service` + order DB schema + `order-events` contract; platform owns AKS/Helm/Terraform base; clear API and event contracts prevent shared-database microservices.

#### What it is
Team boundaries drive deploy independence and on-call. Design interview should label which squad owns each box and how they coordinate schema changes.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Each service repo with own CI/CD and Helm chart. Shared Kafka schema registry with PR review from consumers. No cross-team direct DB access—only APIs/events. Platform provides golden paths: Spring starter, tracing, ESO. Architecture guild resolves disputes. Staff engineer owns cross-cutting saga timeouts.

#### When to use / when NOT to use
Split when cognitive load or deploy cadence conflict exceeds integration cost. Two-pizza teams per service cluster. Monolith modular boundaries if one team—still document future seams.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avro schema—breaking change requires 14-day consumer notice in `#architecture`. Platform squad owns AKS cluster, Terraform modules, and golden Spring starter with tracing. No team queries another team's Oracle schema directly—contract test in CI fails if `OrderPlaced` JSON field removed. On-call rotation per service PagerDuty schedule; cross-team incidents use shared bridge with incident commander.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Five teams ALTER same shared `ORDERS` table. Kafka topic `order-events` no owner in service catalog. Platform team manually deploys every microservice—bottleneck. Breaking event schema on Friday without consumer coordination.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Conway's law example?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avr… Common miss: Five teams ALTER same shared `ORDERS` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Contract testing between teams?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avr… Common miss: Five teams ALTER same shared `ORDERS` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Platform vs product boundary?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avr… Common miss: Five teams ALTER same shared `ORDERS` table. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** On-call mapping?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avr… Common miss: Five teams ALTER same shared `ORDERS` table. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Team boundaries.—error budget is burning.

**Model answer:** Align services to team ownership (Conway's law): order squad owns `order-service` + order DB schema + `order-events` contract; platform owns AKS/Helm/Terraform base; clear API and event contracts prevent shared-database  In practice: Inventory squad owns `inventory-service` repo, Helm chart, `inventory` schema, and consumer group `inventory-projection-v2`. Order squad owns `order-events` Avro schema—breaking ch… I check whether we hit a known mistake (Five teams ALTER same shared `ORDERS` table. Kafka topic `order-events` no owner…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 27. Modular monolith first.

**Short answer:** Start with well-bounded modules in one Spring Boot repo—order, catalog, payment packages with internal APIs—extract to services when independent scale, deploy cadence, or team split justifies Kafka and distributed ops tax.

#### What it is
Modular monolith is valid senior answer for MVP and many scale points. Interviewers test whether you know when not to microservice.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Gradle/Maven multi-module: `order-api`, `order-domain`, `catalog`, shared `platform`. Database single Azure SQL with schema separation or table prefixes. In-process events for now; outbox table ready for later Kafka. React still one BFF module. Helm one Deployment until CPU or team boundaries force split. ADR documents extraction triggers: >500 TPS on order module, separate compliance zone.

#### When to use / when NOT to use
Default for new product until proven pain. Extract payment first if PCI silo required. Do not modular monolith forever at 50 engineers on one repo without tooling.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to payment only. Terraform adds second namespace when needed.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Microservices day one for resume driven development. Monolith without module boundaries—big ball of mud. Extracting before stable domain model.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Extraction triggers?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to pa… Common miss: Microservices day one for resume driven development. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** In-process vs Kafka first?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to pa… Common miss: Microservices day one for resume driven development. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Module package structure?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to pa… Common miss: Microservices day one for resume driven development. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** When monolith wrong?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to pa… Common miss: Microservices day one for resume driven development. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Modular monolith first.—error budget is burning.

**Model answer:** Start with well-bounded modules in one Spring Boot repo—order, catalog, payment packages with internal APIs—extract to services when independent scale, deploy cadence, or team split justifies Kafka and distributed ops ta In practice: Year 1: monolith 4 modules, 3 engineers, 200 orders/min—ships fast. Year 2: extract `payment-service` for PCI audit scope; order stays monolith with Kafka to payment only. Terrafor… I check whether we hit a known mistake (Microservices day one for resume driven development. Monolith without module bou…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 28. Strangler a J2EE monolith.

**Short answer:** Route traffic incrementally via APIM/reverse proxy to new Spring Boot services; extract read paths or bounded contexts first; anti-corruption layer wraps legacy EJB calls; dual-write only with outbox or reconcile—big-bang rewrite fails.

#### What it is
Strangler fig pattern migrates legacy J2EE/WebLogic/IBM stack to cloud-native without multi-year freeze. Common in enterprise Java interviews.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
APIM sends `GET /catalog/*` to new React+Spring; `POST /orders` still to WebLogic until slice ready. Kafka syncs legacy DB changes via CDC to new read models. ACL translates legacy DTOs to domain events. Feature flag routes 5% traffic to new path. Decommission legacy queue when metric zero for 30 days. Terraform provisions new AKS; legacy stays on-prem initially.

#### When to use / when NOT to use
Strangle when rewrite risk high and business needs continuous delivery. Do not strangle without observability on both sides. Payment extraction often early due compliance.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then strangler routes `POST` with idempotency bridge table linking legacy order id to UUID.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Big bang cutover weekend. Dual-write without reconcile. Ignoring legacy session affinity. No rollback route in APIM.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** First slice to extract?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then str… Common miss: Big bang cutover weekend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** CDC tool choice?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then str… Common miss: Big bang cutover weekend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Anti-corruption layer?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then str… Common miss: Big bang cutover weekend. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Success metrics?
**A:** I measure lead time, review minutes, and escaped defects—not Copilot acceptance rate; quarterly retro tunes allowlists without tying comp to AI usage. Example: Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then str… Common miss: Big bang cutover weekend. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Strangler a J2EE monolith.—error budget is burning.

**Model answer:** Route traffic incrementally via APIM/reverse proxy to new Spring Boot services; extract read paths or bounded contexts first; anti-corruption layer wraps legacy EJB calls; dual-write only with outbox or reconcile—big-ban In practice: Retail J2EE order EJB: new `order-service` handles `GET /orders/{id}` from projection fed by Oracle GoldenGate CDC; place order still legacy 12 months; then strangler routes `POST`… I check whether we hit a known mistake (Big bang cutover weekend. Dual-write without reconcile. Ignoring legacy session …). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 29. React state vs server state.

**Short answer:** Server state (orders, catalog) lives in TanStack Query/SWR with cache keys and invalidation; UI state (modal open, form draft) stays in React `useState`/Zustand—never duplicate source of truth for order status in global client store.

#### What it is
Frontend architecture choice affects consistency with Kafka-updated backend. Seniors separate ephemeral UI from authoritative API data.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`useQuery(['order', id])` fetches from BFF; `staleTime` 30s; invalidate on mutation success or SSE event. Optimistic update on cancel with rollback on 409. Form wizard state local until submit sends idempotency key. URL state for filters (`?page=2`). Avoid Redux for server entities unless historical reasons—React Query covers cache.

#### When to use / when NOT to use
React Query default for B2C SPA. Zustand for cart UI before checkout submit. Do not poll entire order list every 2s—cursor pagination + focus refetch.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` clears cart. No stale "shipped" after websocket disconnect—refetch on window focus.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Redux mirroring entire API. No invalidation after mutation. Optimistic UI on payment without rollback. Global store for pagination offset bugs.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** React Query vs Redux?
**A:** AI drafts inside guardrails—sister Helm chart, EXPLAIN on SQL, conventional commits I edit—then Checkov, compile, and human review. Example: Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` … Common miss: Redux mirroring entire API. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Optimistic update when?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` … Common miss: Redux mirroring entire API. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** SSE + cache sync?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` … Common miss: Redux mirroring entire API. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Form state location?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` … Common miss: Redux mirroring entire API. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for React state vs server state.—error budget is burning.

**Model answer:** Server state (orders, catalog) lives in TanStack Query/SWR with cache keys and invalidation; UI state (modal open, form draft) stays in React `useState`/Zustand—never duplicate source of truth for order status in global  In practice: Order detail page: Query cache updated by SSE `OrderStatusChanged` event handler calling `queryClient.setQueryData`. Cart count in Zustand until `POST /orders` clears cart. No stal… I check whether we hit a known mistake (Redux mirroring entire API. No invalidation after mutation. Optimistic UI on pay…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```typescript
const queryClient = useQueryClient();
eventSource.onmessage = (e) => {
  const update = JSON.parse(e.data);
  queryClient.setQueryData(['order', update.orderId], update);
};
```

---

### 30. TypeScript contract.

**Short answer:** Generate TypeScript types from OpenAPI (springdoc) or shared AsyncAPI for events—CI fails if frontend types drift from backend; BFF DTOs are contract, not hand-copied interfaces.

#### What it is
Contract between React and Spring prevents field rename bugs. Fullstack design includes how types flow through pipeline.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`springdoc-openapi` publishes spec on build; `openapi-typescript` generates `api.ts` in frontend repo CI. Breaking change bumps API version `/v2`. Kafka schemas in Schema Registry generate types for BFF event consumers if needed. Contract tests (Pact) optional for critical paths. PR check: spec diff reviewed.

#### When to use / when NOT to use
Codegen mandatory at >5 frontend engineers. Small team can hand-maintain with discipline. Never duplicate `Order` interface in three repos manually.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/types.ts`; React build fails if component still assumes old type. Breaking rename `orderId`→`id` without `/v2` prefix triggers Pact consumer failure in `order-bff` pipeline—deploy blocked until coordinated release. Contract diff posted as PR comment for frontend reviewer. Event types: AsyncAPI optional for `order-events` Avro docs consumed by data team.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Hand-written `interface Order` in React stale for three sprints. `Instant` serialized as epoch in JSON but TS expects string—runtime undefined in prod. Skipping CI regen—developer forgets locally. BFF aggregates fields not in published OpenAPI—mobile team broken silently.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Codegen toolchain?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/t… Common miss: Hand-written `interface Order` in React stale for three sprints. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Breaking change policy?
**A:** I publish a green/yellow/red allowlist in CONTRIBUTING: tests and README in green; Kafka listeners and Helm prod in yellow; authz, IAM, and large Flyway in red. Example: Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/t… Common miss: Hand-written `interface Order` in React stale for three sprints. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Pact vs OpenAPI only?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/t… Common miss: Hand-written `interface Order` in React stale for three sprints. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Event schema typing?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/t… Common miss: Hand-written `interface Order` in React stale for three sprints. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for TypeScript contract.—error budget is burning.

**Model answer:** Generate TypeScript types from OpenAPI (springdoc) or shared AsyncAPI for events—CI fails if frontend types drift from backend; BFF DTOs are contract, not hand-copied interfaces. In practice: Backend adds optional `cancelReason` on `OrderResponse`—`springdoc-openapi-maven-plugin` emits spec artifact; CI job `openapi-typescript` regenerates `src/api/types.ts`; React buil… I check whether we hit a known mistake (Hand-written `interface Order` in React stale for three sprints. `Instant` seria…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 31. Multi-region.

**Short answer:** Multi-region active-active is hard for OLTP orders—start with active-passive DR region, global APIM/Front Door routing users to nearest edge, async replication with RPO measured; Kafka mirroring or single-region bus with clear failover story.

#### What it is
Multi-region design addresses latency, disaster recovery, and data residency (EU vs US). Interviewers want honesty about CAP trade-offs on checkout.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Active-passive: primary EU West SQL, secondary EU North async replica; failover manual or automated 30 min RPO. Active-active catalog read from regional Redis replica fed by global Kafka MirrorMaker 2. Writes single-region for order idempotency unless CRDTs justified (rare). Terraform modules per region; Helm same chart different values. React static on global CDN. Conflict resolution: last-writer-wins bad for money—avoid multi-master orders.

#### When to use / when NOT to use
DR region before active-active. Data residency drives region pair selection. Do not claim active-active orders without conflict design.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via warehouse cross-region. RPO 15 min acceptable per business sign-off.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Split-brain dual write orders. Ignoring cross-region egress cost. Kafka mirror lag unmonitored. DNS failover without session handling.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Active-active vs passive?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via … Common miss: Split-brain dual write orders. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** RPO/RPO for orders?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via … Common miss: Split-brain dual write orders. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Data residency drivers?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via … Common miss: Split-brain dual write orders. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka mirroring?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via … Common miss: Split-brain dual write orders. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Multi-region.—error budget is burning.

**Model answer:** Multi-region active-active is hard for OLTP orders—start with active-passive DR region, global APIM/Front Door routing users to nearest edge, async replication with RPO measured; Kafka mirroring or single-region bus with In practice: US + EU deployments; EU customers hit EU APIM → EU AKS; orders DB not cross-region sync—accounts separate per regulation. Global admin reporting aggregates via warehouse cross-regi… I check whether we hit a known mistake (Split-brain dual write orders. Ignoring cross-region egress cost. Kafka mirror l…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 32. DR tabletop.

**Short answer:** Annual game day: simulate region loss, Kafka blackout, DB failover—run actual runbooks with timed steps, roles, and communication templates; measure RTO against target; fix runbook lies discovered in exercise.

#### What it is
DR tabletop is operational readiness, not diagram box. Shows senior ownership of production survival beyond happy-path design.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Scenario cards: "Primary Azure SQL unavailable." Team executes: declare incident, fail over to secondary, verify `order-service` readiness, check consumer lag backlog plan, customer comms status page. Record actual RTO 52 min vs target 45. Update Terraform, Helm values, and runbooks. Include PSP pause/refund policy in payment scenarios.

#### When to use / when NOT to use
Tabletop quarterly for revenue systems; full failover test annually in staging. Do not first run runbook during real earthquake.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead, comms. Team executes runbook: fail DNS to EU North passive cluster, verify `order-service` readiness probes green, measure RTO 38 min vs 45 target. Discovered APIM backend pool still pointed at old Ingress IP—Terraform fix filed. Kafka scenario: practice draining outbox relay before maintenance. Post-tabletop: update runbook revision, schedule full failover test in staging next quarter.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
PowerPoint-only drill—no one types commands. Runbook namespace typo `payment` vs `payments`. No customer status page owner assigned. PSP not in scope—finance cannot settle during DR confusion.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Last game day outcome?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead… Common miss: PowerPoint-only drill—no one types commands. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** RTO measurement?
**A:** I measure lead time, review minutes, and escaped defects—not Copilot acceptance rate; quarterly retro tunes allowlists without tying comp to AI usage. Example: Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead… Common miss: PowerPoint-only drill—no one types commands. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Customer comms plan?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead… Common miss: PowerPoint-only drill—no one types commands. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PSP in DR scope?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead… Common miss: PowerPoint-only drill—no one types commands. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for DR tabletop.—error budget is burning.

**Model answer:** Annual game day: simulate region loss, Kafka blackout, DB failover—run actual runbooks with timed steps, roles, and communication templates; measure RTO against target; fix runbook lies discovered in exercise. In practice: Scenario: "Primary Azure region network partition—simulate APIM cannot reach EU West AKS." Tabletop at 10 a.m.: incident commander, order on-call, platform lead, comms. Team execut… I check whether we hit a known mistake (PowerPoint-only drill—no one types commands. Runbook namespace typo `payment` vs…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 33. Observability design.

**Short answer:** Metrics (RED/USE), structured logs with traceId, distributed traces, and business KPI dashboards—design names golden signals per service: order place rate, error ratio, p99 latency, consumer lag, outbox depth.

#### What it is
Observability is how you operate the system you designed. Three pillars plus SLO dashboards and synthetic probes.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Micrometer → Prometheus/Azure Monitor; RED on HTTP; USE on nodes. JSON logs to Log Analytics with `orderId`, `tenantId`, `traceId`. Jaeger/Tempo traces as in Q15. Custom metrics: `orders_placed_total`, `saga_timeouts_total`. Synthetic canary places test order every 5 min from Azure Function. Helm annotations for scrape. Terraform creates workspace and alerts.

#### When to use / when NOT to use
Instrument at service creation—not post-incident. Business metrics for product; infra metrics for platform. Do not log PII in debug.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
`order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, p99, 5xx ratio; row 2: `kafka_consumer_lag{group="inventory-projection"}`; row 3: `outbox_pending_count`. Synthetic Azure Function in prod places canary order every 5 min with test tenant—alerts if missing success in 10 min. Log Analytics KQL saved query joins `traceId` across app logs when support escalates. Helm chart sets `podAnnotations` for Prometheus scrape and OpenTelemetry exporter endpoint.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Logs as unstructured printf—cannot grep `orderId`. Dashboards built once, broken after metric rename in Boot 3. No business metric—only infra CPU. PII in debug logs during incident—GDPR incident.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Golden signals per service?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, … Common miss: Logs as unstructured printf—cannot grep `orderId`. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Synthetic monitoring?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, … Common miss: Logs as unstructured printf—cannot grep `orderId`. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Log PII policy?
**A:** I publish a green/yellow/red allowlist in CONTRIBUTING: tests and README in green; Kafka listeners and Helm prod in yellow; authz, IAM, and large Flyway in red. Example: `order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, … Common miss: Logs as unstructured printf—cannot grep `orderId`. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Outbox depth metric?
**A:** I measure lead time, review minutes, and escaped defects—not Copilot acceptance rate; quarterly retro tunes allowlists without tying comp to AI usage. Example: `order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, … Common miss: Logs as unstructured printf—cannot grep `orderId`. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Observability design.—error budget is burning.

**Model answer:** Metrics (RED/USE), structured logs with traceId, distributed traces, and business KPI dashboards—design names golden signals per service: order place rate, error ratio, p99 latency, consumer lag, outbox depth. In practice: `order-service` exports RED metrics to Azure Monitor workspace provisioned by Terraform module `observability-base`. Grafana dashboard row 1: place-order rate, p99, 5xx ratio; row … I check whether we hit a known mistake (Logs as unstructured printf—cannot grep `orderId`. Dashboards built once, broken…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```yaml
management.endpoints.web.exposure.include: health,prometheus,metrics
management.metrics.tags.application: order-service
```

---

### 34. Alerting.

**Short answer:** Page humans on SLO burn and customer-visible failure—consumer lag beyond SLO, error rate spike, payment reconcile gap—not on CPU 70%. Every alert links runbook; tune thresholds after false pages.

#### What it is
Alerting policy separates wake-up events from ticket queue items. Design includes who gets paged for order vs platform vs payment.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Multi-window burn alerts on 99.9% SLO. Lag alert: `kafka_consumer_lag > 10000 for 5m` pages order on-call. Reconcile alert: `uncaptured_orders > 0 for 15m` pages payments. Warning channel for disk 80%. PagerDuty escalation policy. Alert annotation includes Helm release version from Kubernetes downward API.

#### When to use / when NOT to use
Page on revenue path degradation. Ticket on single pod restart if HPA recovers. Review alerts monthly—delete noisy ones.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-5xx.md`. Kafka lag alert `inventory-projection lag >10000 for 5m` routes to inventory squad Slack before page. Payment reconcile SQL metric `stuck_captures >0 for 15m` pages payments—higher severity than email lag. False page storm from CPU alert removed; replaced with `http_5xx_rate > 1% for 3m` on `POST /orders`. Every alert rule annotates `helm_shasum` and `runbook_url`.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Paging on pod restart when HPA self-heals in 30s. Alert text without query link. Inventory and checkout share one PagerDuty service—wrong person wakes. Forgetting Alertmanager mute during approved maintenance.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Page vs ticket criteria?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-… Common miss: Paging on pod restart when HPA self-heals in 30s. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Burn rate alerts?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-… Common miss: Paging on pod restart when HPA self-heals in 30s. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** On-call rotation?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-… Common miss: Paging on pod restart when HPA self-heals in 30s. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Alert noise reduction?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-… Common miss: Paging on pod restart when HPA self-heals in 30s. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Alerting.—error budget is burning.

**Model answer:** Page humans on SLO burn and customer-visible failure—consumer lag beyond SLO, error rate spike, payment reconcile gap—not on CPU 70%. Every alert links runbook; tune thresholds after false pages. In practice: Checkout burn-rate alert fires when 5% of monthly error budget consumed in 1 hour—PagerDuty pages primary order on-call with Grafana link and runbook `checkout-5xx.md`. Kafka lag a… I check whether we hit a known mistake (Paging on pod restart when HPA self-heals in 30s. Alert text without query link.…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 35. Load test.

**Short answer:** Gatling or k6 scripts simulate realistic checkout mix—validate p99, error rate, and DB pool under 2× peak before Black Friday; run in staging with prod-like data volume masked; fix bottlenecks before scaling pods blindly.

#### What it is
Load test proves capacity plan (Q17). Design interview mentions when you'd run it and what pass criteria mean.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Scenario: 70% browse, 20% add cart, 10% checkout with idempotency keys. Ramp 0→500 users over 10 min, sustain 30 min. Monitor SQL DTU, Hikari pending, Kafka lag, PSP mock latency. Fail if p99 >3s or error >0.5%. CI nightly smoke load smaller scale. Terraform scales staging to prod SKU for test week.

#### When to use / when NOT to use
Before major sale and after architecture change. Not on prod without isolated canary environment. Include soak test 4h for memory leaks.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead of more pods.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Load test only health endpoint. Unrealistic think time zero. Mock PSP unlimited—hides rate limit issue. One-time test never repeated.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Tool choice Gatling vs k6?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead … Common miss: Load test only health endpoint. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Pass/fail criteria?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead … Common miss: Load test only health endpoint. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** CI integration?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead … Common miss: Load test only health endpoint. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Soak test duration?
**A:** PR template requires `./mvnw verify` and at least one failure-case test written without AI; mutation or ArchUnit catches weak asserts AI loves. Example: Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead … Common miss: Load test only health endpoint. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Load test.—error budget is burning.

**Model answer:** Gatling or k6 scripts simulate realistic checkout mix—validate p99, error rate, and DB pool under 2× peak before Black Friday; run in staging with prod-like data volume masked; fix bottlenecks before scaling pods blindly In practice: Gatling found N+1 in order history at 200 RPS—fixed before launch. Second test validated HPA adds pods at CPU 60%; DB became bottleneck—scaled SQL tier instead of more pods. Outcom… I check whether we hit a known mistake (Load test only health endpoint. Unrealistic think time zero. Mock PSP unlimited—…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 36. Data lifecycle.

**Short answer:** Define retention: hot orders in SQL 2 years, warm archive to Blob parquet, cold delete per GDPR—with legal hold exceptions; PII minimization in Kafka (IDs not emails); tombstone jobs and right-to-erasure cascade across warehouse.

#### What it is
Data lifecycle is compliance and cost: what stays where how long, how delete propagates from OLTP to search index to backups.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Partition `orders` by month; archive job moves >24mo to Blob; drop partition after legal sign-off. Kafka retention 7d for events; warehouse keeps history. GDPR erasure: pseudonymize PII in SQL, reindex search, note backups expire in 30d. Terraform lifecycle policies on storage tiers Cool/Archive.

#### When to use / when NOT to use
Document retention in design for EU customers day one. Anonymize over delete where law allows analytics. Do not infinite-retain Kafka on PII topics.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrubbing email from notifications log and blob KYC paths.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
PII in Kafka forever. Backup restore resurrects deleted user. No legal hold process. Archive breaks foreign keys without denormalized copy.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Retention periods?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrub… Common miss: PII in Kafka forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** GDPR erasure flow?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrub… Common miss: PII in Kafka forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Kafka vs warehouse retention?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrub… Common miss: PII in Kafka forever. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Legal hold?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrub… Common miss: PII in Kafka forever. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Data lifecycle.—error budget is burning.

**Model answer:** Define retention: hot orders in SQL 2 years, warm archive to Blob parquet, cold delete per GDPR—with legal hold exceptions; PII minimization in Kafka (IDs not emails); tombstone jobs and right-to-erasure cascade across w In practice: Nightly job exports old orders to parquet; SQL partition detached; Synapse still queries archive via external table. Customer delete request triggers saga scrubbing email from noti… I check whether we hit a known mistake (PII in Kafka forever. Backup restore resurrects deleted user. No legal hold proc…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 37. Audit.

**Short answer:** Immutable audit log for admin actions, payment state changes, and consent events—who/when/what/old/new value; separate from application logs; tamper-evident storage (append-only table or WORM Blob); retained 7 years for finance.

#### What it is
Audit supports compliance, dispute resolution, and security investigations. Distinct from debug logging and metrics.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`audit_events` table append-only with DB permissions denying UPDATE/DELETE to app role; alternative Azure Immutable Blob WORM with retention lock for finance. Spring AOP `@Audited` on admin controllers captures JWT `sub`, `tenant_id`, source IP, user-agent, action, resource type/id, before/after JSON diff hash. Optional Kafka `audit-events` stream to Splunk/Azure Sentinel with tamper detection. React admin order detail embeds paginated audit timeline. All timestamps UTC with NTP-synced nodes; include `correlation_id` linking to distributed trace.

#### When to use / when NOT to use
Mandatory for finance, healthcare, enterprise B2B. Do not audit every GET—focus mutations and sensitive reads. Balance volume vs requirement.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `reason_code`; parallel Kafka `audit-events` indexed in Sentinel. SOC2 auditor exports Q4 refund sample without production DB access. Chargeback dispute: payment team proves capture timestamp from audit chain matching PSP ledger—merchant wins case. Retention: 7 years in cool storage per finance policy; legal hold flag prevents purge on litigation.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Mutable `audit_events` table app role can UPDATE. Storing full PAN in audit payload. No retention or partition strategy—multi-TB table slows admin UI. Using `log.info` as substitute—logs rotated and not legally defensible.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Audit storage choice?
**A:** RAG and AI drafts are starting points: reindex on merge, verify commands in game day, ADRs need rejected options and SLOs a human signs. Example: CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `rea… Common miss: Mutable `audit_events` table app role can UPDATE. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Fields captured?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `rea… Common miss: Mutable `audit_events` table app role can UPDATE. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** SIEM integration?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `rea… Common miss: Mutable `audit_events` table app role can UPDATE. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Retention vs GDPR delete?
**A:** I clarify users and NFRs first, sketch sync path with idempotency and outbox, then async—failure/reconcile before buzzwords. Example: CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `rea… Common miss: Mutable `audit_events` table app role can UPDATE. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Audit.—error budget is burning.

**Model answer:** Immutable audit log for admin actions, payment state changes, and consent events—who/when/what/old/new value; separate from application logs; tamper-evident storage (append-only table or WORM Blob); retained 7 years for  In practice: CS agent clicks Refund in admin React → `admin-bff` calls `POST /admin/refunds` → `audit_events` row `REFUND_ISSUED` with `actor_id`, `order_id`, `amount`, `reason_code`; parallel … I check whether we hit a known mistake (Mutable `audit_events` table app role can UPDATE. Storing full PAN in audit payl…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 38. Batch + online coexistence.

**Short answer:** Online OLTP path stays low-latency; batch jobs (nightly pricing, reconcile, warehouse ETL) use separate schedulers, off-peak windows, and read replicas or warehouse—never long table scan on primary during peak.

#### What it is
Most enterprises run Spring Batch or ADF alongside real-time Kafka. Design prevents batch from locking checkout rows.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Spring Batch chunk jobs on read replica or Synapse source. ShedLock prevents duplicate job pods. Pricing batch publishes `PriceChanged` events after commit; catalog projector updates Redis. Reconcile batch (Q18) runs every 15 min with row limits. Online API never triggers full table export synchronously—async job + poll `GET /jobs/{id}`.

#### When to use / when NOT to use
Batch for heavy aggregation; stream for near-real-time inventory signals. Schedule cron 02:00 local off-peak. Throttle batch JDBC fetch size.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on larger replica SKU via Terraform variable.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Batch UPDATE on primary noon. No job locking—double run. Online request triggers unbounded export timeout. Batch failure silent—no alert.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Scheduler choice?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: 02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on … Common miss: Batch UPDATE on primary noon. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Replica vs primary batch?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: 02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on … Common miss: Batch UPDATE on primary noon. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Job failure alerting?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: 02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on … Common miss: Batch UPDATE on primary noon. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Event publish after batch?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: 02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on … Common miss: Batch UPDATE on primary noon. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Batch + online coexistence.—error budget is burning.

**Model answer:** Online OLTP path stays low-latency; batch jobs (nightly pricing, reconcile, warehouse ETL) use separate schedulers, off-peak windows, and read replicas or warehouse—never long table scan on primary during peak. In practice: 02:00 UTC pricing job updates 100k SKUs on replica, emits Kafka events, completes 40 min. Checkout unaffected. Black Friday: defer non-critical batch or run on larger replica SKU v… I check whether we hit a known mistake (Batch UPDATE on primary noon. No job locking—double run. Online request triggers…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 39. GraphQL BFF.

**Short answer:** GraphQL BFF aggregates order + catalog + customer for React in one round-trip—use when mobile bandwidth matters; REST per service still fine behind BFF for simpler caching; federation adds ops cost—justify with client needs.

#### What it is
BFF pattern reduces chatty REST from React. GraphQL optional layer over internal REST/gRPC microservices—not exposed to public internet without depth/complexity limits.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`order-bff` Spring GraphQL or Node Apollo resolves `order { lines { product { title } } }` via parallel calls to internal services with timeout and bulkhead. DataLoader batches catalog fetches. Auth at BFF; downstream mTLS. Persisted queries on mobile. Rate limit expensive queries. Cache `@cacheControl` on catalog fields.

#### When to use / when NOT to use
GraphQL when mobile app needs flexible queries. Stick REST BFF if one web client and stable shapes. Avoid GraphQL directly on Kafka—sync resolver only.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 replicas.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
GraphQL N+1 without DataLoader. Public GraphQL introspection in prod. BFF business logic creep—belongs in domain services. No timeout on resolver cascade.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** GraphQL vs REST BFF?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 re… Common miss: GraphQL N+1 without DataLoader. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** N+1 prevention?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 re… Common miss: GraphQL N+1 without DataLoader. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Auth where?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 re… Common miss: GraphQL N+1 without DataLoader. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Complexity limits?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 re… Common miss: GraphQL N+1 without DataLoader. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for GraphQL BFF.—error budget is burning.

**Model answer:** GraphQL BFF aggregates order + catalog + customer for React in one round-trip—use when mobile bandwidth matters; REST per service still fine behind BFF for simpler caching; federation adds ops cost—justify with client ne In practice: React web uses REST BFF three endpoints; mobile GraphQL reduces battery drain. Complexity limit 200 prevents malicious deep query. Helm deploys `order-bff` 3 replicas. Outcome metr… I check whether we hit a known mistake (GraphQL N+1 without DataLoader. Public GraphQL introspection in prod. BFF busine…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 40. Azure Functions in the design.

**Short answer:** Use Functions for event-driven spikes—virus scan on blob upload, lightweight webhook adapters, scheduled reconcile—not for core order OLTP; cold start and VPC integration matter; prefer AKS Spring for consistent order path.

#### What it is
Serverless functions fill glue roles in Azure-native design alongside AKS microservices and Terraform-provisioned resources.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Event Grid blob upload → Function ClamAV scan → Service Bus message. Durable Functions orchestrate infrequent multi-step human approval with timeout. Premium plan reduces cold start if latency-sensitive. VNet integration for private SQL access. Terraform `azurerm_linux_function_app` with managed identity. Not replacement for Kafka consumer doing 500 msg/sec sustained—use Spring on AKS.

#### When to use / when NOT to use
Functions for <1 min sporadic work with Azure triggers. AKS for order service, inventory consumer. Logic Apps for low-code integration prototypes.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7 pod for 5 min daily work.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Order API on Consumption plan cold start. Function with 500 dependencies duplicating monolith. No idempotency on trigger retry. Secrets in app settings unrotated.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Functions vs AKS consumer?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7… Common miss: Order API on Consumption plan cold start. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Cold start mitigation?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7… Common miss: Order API on Consumption plan cold start. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** VNet integration?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7… Common miss: Order API on Consumption plan cold start. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Durable Functions when?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7… Common miss: Order API on Consumption plan cold start. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Azure Functions in the design.—error budget is burning.

**Model answer:** Use Functions for event-driven spikes—virus scan on blob upload, lightweight webhook adapters, scheduled reconcile—not for core order OLTP; cold start and VPC integration matter; prefer AKS Spring for consistent order pa In practice: KYC scan Function on Event Grid; core `order-service` on AKS. Nightly reconcile Function timer triggers Spring Batch job via HTTP internal. Cost lower than 24/7 pod for 5 min daily… I check whether we hit a known mistake (Order API on Consumption plan cold start. Function with 500 dependencies duplica…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```hcl
resource "azurerm_linux_function_app" "kyc_scan" {
  name                = "kyc-scan-${var.env}"
  resource_group_name = azurerm_resource_group.main.name
  storage_account_name = azurerm_storage_account.func.name
  service_plan_id     = azurerm_service_plan.premium.id
}
```

---

### 41. Helm/TF split in the design.

**Short answer:** Terraform provisions durable cloud resources—AKS cluster, SQL, Key Vault, APIM, networking; Helm releases application workloads on top—Deployments, Services, HPA, per-service values. Never mix app version deploy into TF apply on every release.

#### What it is
IaC layering separates platform (slow change) from app (fast change). Interviewers want clear ownership: platform team TF, app squad Helm.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Terraform modules: `azurerm_kubernetes_cluster`, `azurerm_mssql_server`, VNet, ACR. Outputs kubeconfig + identity IDs to CI. Helm chart in app repo: `helm upgrade order-service ./chart -f values-prod.yaml --set image.tag=$SHA`. Argo CD optional GitOps for Helm. ESO CRDs may be Helm; Key Vault itself TF. State backends separate: `terraform.tfstate` platform vs no TF for app image.

#### When to use / when NOT to use
TF for infra drift correction weekly. Helm each merge to main for app. Do not `terraform apply` to change pod replica count on every deploy—use HPA/Helm.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs all Helm releases from Git in 20 min.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Helm chart creating Azure SQL per deploy. TF managing `image: latest` per commit. No separation of state—blast radius huge. Manual `kubectl set image` fighting GitOps.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** TF vs Helm boundary?
**A:** AI drafts inside guardrails—sister Helm chart, EXPLAIN on SQL, conventional commits I edit—then Checkov, compile, and human review. Example: Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs a… Common miss: Helm chart creating Azure SQL per deploy. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Argo CD role?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs a… Common miss: Helm chart creating Azure SQL per deploy. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Who owns what pipeline?
**A:** Enterprise SKUs define retention, training opt-out, and regional hosting—legal approves before any prod code or PII enters prompts; consumer ChatGPT stays off regulated paths. Example: Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs a… Common miss: Helm chart creating Azure SQL per deploy. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** State backend strategy?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs a… Common miss: Helm chart creating Azure SQL per deploy. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Helm/TF split in the design.—error budget is burning.

**Model answer:** Terraform provisions durable cloud resources—AKS cluster, SQL, Key Vault, APIM, networking; Helm releases application workloads on top—Deployments, Services, HPA, per-service values. Never mix app version deploy into TF  In practice: Platform TF pipeline monthly upgrades AKS patch version. Order squad deploys 12 times/day via Helm with digest pin. Disaster: TF recreates cluster; Argo syncs all Helm releases fro… I check whether we hit a known mistake (Helm chart creating Azure SQL per deploy. TF managing `image: latest` per commit…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```text
Terraform: AKS, Azure SQL, Key Vault, APIM, VNet
Helm:      order-service Deployment, Service, HPA, Ingress
CI:        build image → push ACR → helm upgrade --set image.tag=$SHA
```

---

### 42. Local dev story.

**Short answer:** `docker compose up` for Kafka/Zookeeper or Redpanda, Postgres/Azure SQL edge, Redis; Spring profiles `local`; React proxy to `localhost:8080`; Testcontainers in CI for parity—document one-command start in README; optional Telepresence to dev AKS for integration debugging.

#### What it is
Local dev experience affects velocity. Design mentions how engineers run full stack without prod credentials.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Compose file: `kafka:9092`, `postgres:5432`, `redis:6379`. `application-local.yaml` points JDBC and Kafka bootstrap. Flyway migrates on boot. React `VITE_API_URL=http://localhost:8080`. Seed data script for test merchant. Makefile targets: `make up`, `make test`, `make reset-db`. Tilt/Skaffold optional for K8s-local purists.

#### When to use / when NOT to use
Compose default for microservices team. Dev AKS namespace per engineer only if compose insufficient (GPU, managed identity testing). Never prod data in local—synthetic fixtures.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
`make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspring-boot.run.profiles=local` applies Flyway V1–V42; `npm run dev` in `web/` proxies `/api` to `localhost:8080`. Seed script inserts test merchant and 10 SKUs. CI uses Testcontainers with same Postgres and Redpanda images—parity catches `JSONB` dialect issues H2 would miss. Optional Telepresence doc for attaching local `payment-service` to dev AKS namespace when debugging Adyen sandbox webhooks.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
README references Kafka on 9092 but compose moved to 19092. Developer uses H2 locally while prod Azure SQL—`NVARCHAR` length surprises. Committed `.env` with sandbox API keys. Eight-step manual setup—new hire stuck day one.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Compose services list?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspri… Common miss: README references Kafka on 9092 but compose moved to 19092. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Profile strategy?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspri… Common miss: README references Kafka on 9092 but compose moved to 19092. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Testcontainers parity?
**A:** PR template requires `./mvnw verify` and at least one failure-case test written without AI; mutation or ArchUnit catches weak asserts AI loves. Example: `make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspri… Common miss: README references Kafka on 9092 but compose moved to 19092. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Telepresence when?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: `make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspri… Common miss: README references Kafka on 9092 but compose moved to 19092. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Local dev story.—error budget is burning.

**Model answer:** `docker compose up` for Kafka/Zookeeper or Redpanda, Postgres/Azure SQL edge, Redis; Spring profiles `local`; React proxy to `localhost:8080`; Testcontainers in CI for parity—document one-command start in README; optiona In practice: `make dev` in monorepo README: `docker compose -f infra/compose.yml up -d` starts Redpanda, Postgres 16, Redis; `./mvnw spring-boot:run -pl order-service -Dspring-boot.run.profiles… I check whether we hit a known mistake (README references Kafka on 9092 but compose moved to 19092. Developer uses H2 lo…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 43. API pagination + React.

**Short answer:** Use cursor/keyset pagination (`?cursor=eyJpZCI6MTIzfQ`) for order history at scale—never OFFSET on million-row tables; React infinite scroll or "Load more" with stable sort key; return `nextCursor` in response.

#### What it is
Pagination design prevents DB meltdown and UI jank. Ties OLTP indexing strategy to frontend list components.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
`GET /orders?limit=20&cursor=base64(lastId,lastCreatedAt)` uses index `(tenant_id, created_at DESC, id)`. Response `{ items, nextCursor, hasMore }`. React TanStack Query `useInfiniteQuery` appends pages. Avoid total count on huge tables—`hasMore` enough. Admin export uses async job not paginated loop in browser.

#### When to use / when NOT to use
Cursor for user order history, audit logs. Offset OK for admin page 1–10 on small tables only. Document sort stability—tie-breaker column required.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
OFFSET pagination in prod. Cursor without unique tie column—duplicates across pages. Client fetches all pages for "export." Unstable sort on `updated_at` only.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Cursor encoding?
**A:** Tool choice is workflow: Cursor for multi-file agent edits with `.cursorrules`; Copilot for IntelliJ inline—terminal allowlist, branch per session, never prod kubeconfig on agent machines. Example: Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys. Outc… Common miss: OFFSET pagination in prod. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Index design?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys. Outc… Common miss: OFFSET pagination in prod. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Infinite scroll UX?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys. Outc… Common miss: OFFSET pagination in prod. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Total count when needed?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys. Outc… Common miss: OFFSET pagination in prod. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for API pagination + React.—error budget is burning.

**Model answer:** Use cursor/keyset pagination (`?cursor=eyJpZCI6MTIzfQ`) for order history at scale—never OFFSET on million-row tables; React infinite scroll or "Load more" with stable sort key; return `nextCursor` in response. In practice: Customer order list 50k orders: OFFSET page 500 took 8s—migrated to cursor, p95 40ms. React infinite scroll preserves scroll position via Query cache keys. Outcome metric: escaped … I check whether we hit a known mistake (OFFSET pagination in prod. Cursor without unique tie column—duplicates across pa…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```json
GET /orders?limit=20&cursor=eyJjcmVhdGVkQXQiOiIyMDI2LTAxLTE1VDEwOjAwOjAwWiIsImlkIjoiYWJjIn0
{ "items": [...], "nextCursor": "eyJ...", "hasMore": true }
```

---

### 44. Hot partition in design.

**Short answer:** Kafka hot partition happens when key skew—one `merchantId` or `celebrityProductId` dominates traffic; mitigate with salt in key, dedicated topic, async queue per hot entity, or sync shard in DB—not only "add partitions."

#### What it is
Hot partition breaks horizontal scale assumption. Design interview should identify skew scenarios in order/catalog domains.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Default key `orderId` spreads well. Bad: key=`country` with 90% US traffic. Fixes: composite key `hash(merchantId)%N` sub-topics; bulkhead thread pool for hot consumer; cache hot SKU inventory in Redis with single-writer queue. Monitor per-partition lag in Grafana. Black Friday celebrity drop: pre-scale consumer on predicted partition or route to dedicated service instance.

#### When to use / when NOT to use
Analyze key distribution before launch. Salt keys when one tenant is whale. Do not partition count alone fix skewed keys.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload for analytics only. Lag flattened across 24 partitions.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Partition=1 topic. Key by `status=PENDING`—all new orders one partition. Ignoring per-partition lag metric. DB hot row same as Kafka hot key—need both fixes.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Detect hot partition?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload f… Common miss: Partition=1 topic. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Key salting example?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload f… Common miss: Partition=1 topic. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** DB hot row vs Kafka?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload f… Common miss: Partition=1 topic. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Celebrity drop playbook?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload f… Common miss: Partition=1 topic. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Hot partition in design.—error budget is burning.

**Model answer:** Kafka hot partition happens when key skew—one `merchantId` or `celebrityProductId` dominates traffic; mitigate with salt in key, dedicated topic, async queue per hot entity, or sync shard in DB—not only "add partitions." In practice: Influencer drop: 80% orders same `campaignId` key caused single partition lag 200k. Changed producer key to `orderId` for events, kept `campaignId` in payload for analytics only. L… I check whether we hit a known mistake (Partition=1 topic. Key by `status=PENDING`—all new orders one partition. Ignorin…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 45. Exactly-once story end-to-end.

**Short answer:** True exactly-once across HTTP, DB, and Kafka is impractical—design for exactly-once *effect*: idempotent consumers, transactional outbox, idempotency keys, unique constraints, and reconcile jobs; say this clearly, then walk one order from click to email without duplicate side effects.

#### What it is
Interview trap question. Senior answer decomposes layers and names pragmatic patterns, not Kafka EOS marketing alone.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Click: `Idempotency-Key` on POST. DB: single TX order+outbox. Kafka: at-least-once delivery + inbox `event_id` unique. Payment: PSP idempotency key. Email: `(orderId,templateId)` unique. Effectively-once = no duplicate charge, one email, one inventory decrement. EOS Kafka transactions only if team operates read_committed consumers and short transactions—often skip for complexity.

#### When to use / when NOT to use
Prefer outbox+inbox over Kafka transactions unless staff Kafka expertise. Always reconcile payments. Document failure duplicates and how system absorbs them.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; customer receives one confirmation. Diagram each dedupe point.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Claiming "Kafka exactly-once" without consumer idempotency. No inbox table. Ignoring PSP duplicate webhooks. Dual-write order row and message.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Why not Kafka EOS everywhere?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; c… Common miss: Claiming "Kafka exactly-once" without consumer idempotency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Inbox schema?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; c… Common miss: Claiming "Kafka exactly-once" without consumer idempotency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PSP duplicate handling?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; c… Common miss: Claiming "Kafka exactly-once" without consumer idempotency. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Reconcile role?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; c… Common miss: Claiming "Kafka exactly-once" without consumer idempotency. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Exactly-once story end-to-end.—error budget is burning.

**Model answer:** True exactly-once across HTTP, DB, and Kafka is impractical—design for exactly-once *effect*: idempotent consumers, transactional outbox, idempotency keys, unique constraints, and reconcile jobs; say this clearly, then w In practice: Trace order `7c9e6679`: idempotent POST returns same body on retry; outbox publishes once; consumer inbox skips redelivery; payment webhook duplicate ignored; customer receives one… I check whether we hit a known mistake (Claiming "Kafka exactly-once" without consumer idempotency. No inbox table. Igno…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
#### Code / config (when useful)
```sql
CREATE TABLE processed_events (
  event_id   VARCHAR(64) PRIMARY KEY,
  processed_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

---

### 46. Whiteboard hygiene.

**Short answer:** Label every box with owner service and datastore; draw sync vs async arrows; mark idempotency points and failure paths in red; legible text; leave space for depth—interviewers score clarity and trade-off narration, not microservice count.

#### What it is
Whiteboard hygiene is communication skill in system design loops. Messy diagram loses panel even if architecture sound.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Left-to-right: users → edge → services → data. Legend: solid=sync HTTP, dashed=Kafka, cylinder=SQL. Number happy path 1–5. Add "if payment timeout → refund" branch when discussing failures. Erase and redraw rather than spaghetti. State assumptions top corner: "10k orders/min, EU only, PCI SAQ A."

#### When to use / when NOT to use
Practice 45-min mock weekly. Zoom: use Excalidraw large font. Do not spend 15 minutes on logo art.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hired for clarity.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
20 unnamed boxes. Kafka in middle with no topic names. No datastore on write path. Cannot read handwriting on video call.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Diagram legend habits?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hi… Common miss: 20 unnamed boxes. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Time on diagram vs depth?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hi… Common miss: 20 unnamed boxes. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** How show failure paths?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hi… Common miss: 20 unnamed boxes. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Tools preference?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hi… Common miss: 20 unnamed boxes. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Whiteboard hygiene.—error budget is burning.

**Model answer:** Label every box with owner service and datastore; draw sync vs async arrows; mark idempotency points and failure paths in red; legible text; leave space for depth—interviewers score clarity and trade-off narration, not m In practice: Candidate draws APIM, two services, one DB, outbox to Kafka—panel asks depth on inventory; candidate adds failure arrow in 30 seconds because space reserved. Hired for clarity. Out… I check whether we hit a known mistake (20 unnamed boxes. Kafka in middle with no topic names. No datastore on write pat…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 47. Why not serverless everything?

**Short answer:** Order OLTP, Kafka consumers, and long-lived connections need predictable latency, JVM ecosystem, and operability at sustained QPS—Functions excel at glue, not core checkout at 500 RPS with complex sagas; cost and cold start bite; team skills matter.

#### What it is
Pushback against "serverless all the things" shows maturity. Azure has Functions, Container Apps, and AKS—pick per workload shape.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
AKS Spring: steady traffic, connection pools, Micrometer, mature Kafka client tuning. Functions: blob trigger scan, timer reconcile. Container Apps middle ground for spiky HTTP. Cold start 1–3s unacceptable on `POST /orders`. VPC integration complexity multiplies per function. Local dev parity harder. Vendor lock-in on triggers vs portable K8s Helm.

#### When to use / when NOT to use
Serverless for event glue and low QPS APIs. K8s for core domain and high-throughput consumers. Revisit Container Apps when ops team small and traffic bursty non-critical.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AKS Deployment with HPA.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Resume-driven serverless. Ignoring Kafka consumer sustained load on Functions. Debugging distributed Functions harder than one JVM trace. Cost surprise on high invocation count.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Functions appropriate workloads?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AK… Common miss: Resume-driven serverless. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Cold start impact?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AK… Common miss: Resume-driven serverless. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Container Apps middle ground?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AK… Common miss: Resume-driven serverless. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Team skill factor?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AK… Common miss: Resume-driven serverless. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Why not serverless everything?—error budget is burning.

**Model answer:** Order OLTP, Kafka consumers, and long-lived connections need predictable latency, JVM ecosystem, and operability at sustained QPS—Functions excel at glue, not core checkout at 500 RPS with complex sagas; cost and cold st In practice: Core five services on AKS; 12 Functions for integrations (SFTP poll, image resize). Attempted order API on Functions—cold start p99 ruined checkout; moved to AKS Deployment with HP… I check whether we hit a known mistake (Resume-driven serverless. Ignoring Kafka consumer sustained load on Functions. D…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 48. AI features in the product.

**Short answer:** Product AI (support chatbot, search rerank) needs RAG on approved docs, eval CI, content filters, rate limits, fallback when model down, and PII scrubbing—separate from developer Copilot; mention in design if customer-facing AI touches order data.

#### What it is
Modern designs may include merchant assistant or semantic product search. Security and reliability requirements differ from batch reporting.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
React widget calls BFF → Azure OpenAI with retrieved chunks from AI Search index (catalog+FAQ only). Prompt template versioned; no raw order PII in prompt—use orderId lookup server-side after auth. Eval golden questions in release pipeline. Thumbs down logs for retraining queue. Circuit breaker returns static FAQ on model timeout. Cost cap per tenant per day.

#### When to use / when NOT to use
Add when product demands—not by default. Human handoff for payment disputes. Do not send full order JSON to public LLM.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—different risk profile documented in security review.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Customer PII in prompts logged. No fallback UX. No eval regression on prompt change. Confusing dev AI with product AI in compliance docs.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** RAG architecture?
**A:** RAG and AI drafts are starting points: reindex on merge, verify commands in game day, ADRs need rejected options and SLOs a human signs. Example: Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—differen… Common miss: Customer PII in prompts logged. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** PII handling?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—differen… Common miss: Customer PII in prompts logged. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Eval in release?
**A:** I measure lead time, review minutes, and escaped defects—not Copilot acceptance rate; quarterly retro tunes allowlists without tying comp to AI usage. Example: Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—differen… Common miss: Customer PII in prompts logged. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Fallback UX?
**A:** Human owns ack mode, idempotency inbox, and groupId; AI may draft the listener only against a golden `@PaymentCapturedListener`—I Testcontainers-verify duplicate delivery before merge. Example: Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—differen… Common miss: Customer PII in prompts logged. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for AI features in the product.—error budget is burning.

**Model answer:** Product AI (support chatbot, search rerank) needs RAG on approved docs, eval CI, content filters, rate limits, fallback when model down, and PII scrubbing—separate from developer Copilot; mention in design if customer-fa In practice: Merchant support bot answers "how to cancel order" from help docs RAG; cannot execute cancel without OAuth admin scope. Dev team uses Cursor separately—different risk profile docum… I check whether we hit a known mistake (Customer PII in prompts logged. No fallback UX. No eval regression on prompt cha…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 49. 45-minute design checklist.

**Short answer:** Minutes 0–5: clarify requirements and NFRs. 5–15: high-level diagram happy path. 15–30: deep dive data model + API + async. 30–40: failures, scale, security. 40–45: trade-offs, MVP cut, what you'd monitor—check off idempotency, observability, and deploy story before time ends.

#### What it is
Checklist prevents rambling and ensures interview coverage expected at senior bar. Meta-question about process—answer with actual checklist you use.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
□ Users and core flows □ QPS/storage □ Sync vs async justified □ Datastores per service □ Idempotency keys □ Kafka topics+keys □ Failure scenarios (payment, Kafka, DB) □ SLO sketch □ Security (auth, BOLA) □ Helm/TF mention □ MVP vs phase 2 □ Open questions to interviewer. Tick mentally while speaking; pivot if interviewer redirects.

#### When to use / when NOT to use
Every onsite design round. Adapt depth to prompt—payment heavy vs catalog heavy. Skip Terraform deep dive if not cloud-focused interview.  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates "production ready thinking."  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
No time for failures. Diving API field names too early. Never asking clarifying questions. Ending without trade-off summary.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** What you cut if time short?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates… Common miss: No time for failures. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Deep dive selection?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates… Common miss: No time for failures. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** How practice checklist?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates… Common miss: No time for failures. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** MVP phrasing?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates… Common miss: No time for failures. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for 45-minute design checklist.—error budget is burning.

**Model answer:** Minutes 0–5: clarify requirements and NFRs. 5–15: high-level diagram happy path. 15–30: deep dive data model + API + async. 30–40: failures, scale, security. 40–45: trade-offs, MVP cut, what you'd monitor—check off idemp In practice: Candidate finishes order design at minute 38 with failure path uncovered; uses checklist, spends 7 minutes on payment captured/order stuck reconcile—panel rates "production ready t… I check whether we hit a known mistake (No time for failures. Diving API field names too early. Never asking clarifying …). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 50. Closing sentence that sounds like 10+ years.

**Short answer:** Close with synthesis: "I'd start modular monolith with outbox-ready order path, prove SLOs under load, extract payment for PCI, and only then scale Kafka consumers—shipping safely matters more than diagram elegance." Shows judgment, phasing, and ops awareness—not buzzwords.

#### What it is
Final impression line after 45 minutes. Signals staff-level prioritization and wariness of over-engineering.  At staff bar, name owners, failure arrows, and what you defer—not a laundry list of Azure services.

#### How it works (internals)
Template: (1) what you'd build first MVP, (2) what you'd defer with trigger, (3) how you'd know it's working (SLO/metrics), (4) biggest risk you'd monitor. Tone: confident practitioner, invites follow-up. Avoid "that's it" or trailing off.

#### When to use / when NOT to use
When interviewer says "anything else?" or clock hits 44 min. Do not force if they already ended. One sentence plus optional "happy to go deeper on X."  Revisit the allowlist after any near-miss; norms should evolve from incidents, not slide decks.

#### Production example
"Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, and load-test before Black Friday—that's where I'd spend my first sprint as staff on this system." Panel nods.  Outcome metric: escaped defects flat or down, review time explicit, and rollback path documented.

#### Common mistakes
Trailing into new architecture rabbit hole. Humble-brag without substance. "I think microservices are best." No mention of ops or risk.  On-call cost is highest when verification was skipped because 'the model sounded confident.'

#### Interview follow-ups (with model answers)


**Q:** Your personal closing line?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: "Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, … Common miss: Trailing into new architecture rabbit hole. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** MVP vs vision balance?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: "Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, … Common miss: Trailing into new architecture rabbit hole. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** Risk you'd highlight?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: "Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, … Common miss: Trailing into new architecture rabbit hole. I close with MVP scope, deferred work, and the SLO that proves it.

**Q:** How end mock designs?
**A:** On «this topic», I pair AI speed with unchanged verification: compile, tests, and line-by-line review. Example: "Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, … Common miss: Trailing into new architecture rabbit hole. I close with MVP scope, deferred work, and the SLO that proves it.
#### Scenario probe

**Situation:** During a deploy or incident, the team debates a quick AI-assisted fix for Closing sentence that sounds like 10+ years.—error budget is burning.

**Model answer:** Close with synthesis: "I'd start modular monolith with outbox-ready order path, prove SLOs under load, extract payment for PCI, and only then scale Kafka consumers—shipping safely matters more than diagram elegance." Sho In practice: "Given your 2k peak orders/min and PCI requirement, I'd nail idempotent checkout on Azure SQL with outbox this quarter, defer multi-region until RPO forces it, and load-test before… I check whether we hit a known mistake (Trailing into new architecture rabbit hole. Humble-brag without substance. "I th…). Contain: rollback or redact prompts; verify with CI and integration tests. Then update allowlist/runbook and add a guard (ArchUnit, eval golden task, or CODEOWNERS).
---

### 51. Design a fraud detection pipeline (rules + ML + human review)

**Short answer:** Ingest payment and login events via Kafka; rules engine flags known patterns fast; ML model scores risk asynchronously; high scores route to human review queue before capture/settlement. Never block checkout on ML latency—use rules for sync path, ML for review hold or post-auth.

#### What it is
Fraud pipeline combines deterministic rules (velocity, geo mismatch, device fingerprint) with ML probability scores and analyst workflow. Sits parallel to payment saga—not inside critical path unless rules are sub-10ms.

#### How it works (internals)
Events → `fraud-events` topic → Flink or Spring stream for rules → feature store lookup → model inference service → score persisted → if > threshold, `FraudReviewRequired` to case management UI. Humans approve/reject; outcomes feed model retraining with governance. Audit every decision.

#### When to use / when NOT to use
Rules for hard blocks; ML for subtle patterns; human for edge cases and regulatory disputes. Do not synchronous call slow ML on every click. PCI: minimize features with raw PAN.

#### Production example
Fintech: `PaymentAttempted` scored in 30ms rules layer; 2% flagged to ML; 0.3% to human queue in React admin. False positive SLA 4h. Kafka keyed by `orderId`. Model version in audit log.

#### Common mistakes
Blocking checkout on 500ms model. No feedback loop—model drifts. Single global threshold—per-merchant tuning needed. Storing full device fingerprint without consent.

#### Interview follow-ups (with model answers)

**Q:** Rules vs ML boundary?
**A:** Rules: explainable, regulatory, fast—stolen card BIN list. ML: behavioral anomalies. Human override always for account holder dispute.

**Q:** Feature store?
**A:** Online store (Redis) for user velocity; offline warehouse for training—never train on PII without governance.

**Q:** False positive UX?
**A:** Soft decline with retry; do not accuse user—route to step-up auth before hard block.

#### Scenario probe

**Situation:** Fraud team wants synchronous ML on `POST /orders` for 100% coverage.

**Model answer:** I keep sync path to rules + device id only; ML async hold on capture if score high after auth. Diagram latency budget 300ms checkout. Offer phase-2 shadow mode ML without user impact.

---

### 52. Design a subscription billing system (Stripe-like) with dunning

**Short answer:** Subscriptions: plans, trials, proration, invoices, payment retries (dunning), webhooks from PSP. Ledger append-only; idempotent webhook handling; state machine per subscription; dunning emails via async notification topic.

#### What it is
Billing is money + time: renewals, failed cards, grace periods, cancellations. Stripe-like means you may integrate Stripe Billing or build—design shows invoice lifecycle and dunning either way.

#### How it works (internals)
`subscriptions` table with status ACTIVE/PAST_DUE/CANCELLED. Scheduler publishes `InvoiceDue` → charge via PSP idempotency key → on failure increment `dunning_step`, schedule retry per policy (day 1,3,7), send email events. Webhook `invoice.paid` updates ledger. React customer portal shows payment method update.

#### When to use / when NOT to use
Integrate PSP Billing until scale justifies build. Dunning must be configurable per plan. Never delete invoice rows—credit notes.

#### Production example
SaaS on AKS: Stripe Billing webhooks to `billing-service`, outbox to `billing-events`, dunning worker consumes retry schedule. Admin adjusts dunning template in Helm config. MRR dashboard from warehouse.

#### Common mistakes
Retry storm on same card without backoff. No idempotent webhooks—duplicate invoices. Proration math wrong on mid-cycle upgrade. Missing cancel-at-period-end.

#### Interview follow-ups (with model answers)

**Q:** Dunning vs churn?
**A:** Dunning recovers revenue; after N failures cancel with retention offer—product policy drives steps.

**Q:** Ledger?
**A:** Append-only entries per charge/refund; reconcile PSP daily.

**Q:** Trial conversion?
**A:** Webhook `customer.subscription.trial_will_end` triggers notification 3 days prior.

#### Scenario probe

**Situation:** CEO wants custom dunning same day as Stripe integration go-live.

**Model answer:** Phase 1: Stripe default dunning; phase 2: custom emails via `notification-events`. Document webhook idempotency and ledger first—UX second.

---

### 53. Design a real-time collaborative document editor (OT/CRDT high level)

**Short answer:** Clients connect via WebSocket to collaboration service; edits as operations with revision vectors; OT or CRDT for merge; periodic snapshot to blob storage; auth per document. At senior level explain trade-off—OT needs server ordering; CRDT works offline-friendly with larger payloads.

#### What it is
Google Docs-like editing: multiple cursors, low latency, eventual consistency of document state. Not the same as CRUD REST on whole document.

#### How it works (internals)
WebSocket room per `documentId`; server assigns op sequence (OT) or clients send CRDT updates with lamport/version. Persistence: append op log + snapshot every N ops to S3/Blob. React editor plugin (Yjs/Automerge). ACL on join.

#### When to use / when NOT to use
OT simpler server-authoritative; CRDT better offline/mobile. Pick one—do not hybrid in interview without deep reason. MVP: single-region, OT with Redis pub/sub fanout.

#### Production example
10k concurrent editors rare—design for 50 per doc. Yjs + Spring WebSocket on AKS; snapshot to Azure Blob; load doc from snapshot + tail ops.

#### Common mistakes
HTTP polling for edits. No auth on WebSocket join—doc ID guessing. Saving whole doc every keystroke to SQL.

#### Interview follow-ups (with model answers)

**Q:** OT vs CRDT one-liner?
**A:** OT: transform ops against concurrent ops on server. CRDT: mathematically merge without central ordering—more metadata.

**Q:** Conflict UX?
**A:** Rare with text; show cursor; for structured fields use last-writer-wins with audit.

**Q:** Scale?
**A:** Shard rooms by documentId; sticky sessions or Redis bridge between nodes.

#### Scenario probe

**Situation:** Interviewer asks CRDT; you only know REST autosave.

**Model answer:** Honest: autosave REST for MVP; CRDT when real-time multi-user required. Sketch Yjs architecture and snapshot recovery—depth over buzzword.

---

### 54. Design a marketplace (buyers, sellers, escrow, disputes)

**Short answer:** Three-sided: listings, checkout with escrow hold, release on delivery confirm, dispute window with evidence upload to blob, admin arbitration. Money flow separate from order state—ledger entries.

#### What it is
Marketplace adds seller onboarding, split payments, escrow, ratings, disputes—beyond simple B2C checkout.

#### How it works (internals)
Buyer pays → PSP capture to platform escrow account → order SHIPPED → buyer confirms or timeout → payout to seller minus fee. Dispute freezes payout; admin UI reviews SAS-uploaded evidence. Kafka `marketplace-events` for notifications and DW.

#### When to use / when NOT to use
Escrow via PSP capabilities (Stripe Connect) vs building—buy Connect. Disputes async; never block browse on dispute logic.

#### Production example
Etsy-like: seller KYC blob upload, `escrow-hold` service, 14-day dispute window, payout batch nightly. React buyer/seller/admin SPAs separated.

#### Common mistakes
Direct pay seller without escrow. No dispute state machine. BOLA on order IDs across tenants.

#### Interview follow-ups (with model answers)

**Q:** Stripe Connect role?
**A:** Platform account, connected accounts for sellers, application fees—reduces PCI scope.

**Q:** Dispute evidence?
**A:** SAS upload like KYC Q8; immutable audit trail.

**Q:** Payout timing?
**A:** Configurable hold post-delivery; fraud score may extend.

#### Scenario probe

**Situation:** Founder wants instant seller payout day one.

**Model answer:** Explain chargeback risk—escrow + hold period or Connect risk controls. MVP: delayed payout 7 days; metrics on dispute rate before instant.

---

### 55. Design a telemetry/observability platform for 500 microservices

**Short answer:** Agents/exporters per service → OTLP collectors (scale horizontally) → Kafka buffer → processors → long-term store (Mimir/Prometheus/Cortex or vendor); logs to Loki/Log Analytics; traces Tempo/Jaeger. Cardinality control and tenant isolation critical.

#### What it is
Central observability for hundreds of services: metrics, logs, traces, SLO dashboards, alert routing—not each team running separate Prometheus.

#### How it works (internals)
OpenTelemetry SDK in Spring Boot → regional collectors → Kafka `telemetry` topics by signal type → consumers write to TSDB with label policies; high-cardinality dropped or aggregated. Grafana unified UI; Alertmanager routes by service owner.

#### When to use / when NOT to use
Managed vendor (Datadog/Azure Monitor) vs self-host—500 services favors hybrid: OTLP standard, vendor backend for ops cost. Drop debug logs at ingest.

#### Production example
AKS: OTel operator daemonset, collectors HPA on ingest rate, 30-day metrics retention, trace sampling 10% prod. Service catalog maps `team` label to PagerDuty.

#### Common mistakes
Unbounded label cardinality (`userId` on every metric). No sampling—cost explosion. 500 separate Prometheus without federation.

#### Interview follow-ups (with model answers)

**Q:** Cardinality example?
**A:** Never `http_path` with raw UUID—bucket to route template.

**Q:** Kafka in observability path?
**A:** Buffers spikes during AZ failure; consumers scale independently.

**Q:** SLO platform?
**A:** Recording rules pre-aggregate SLI; multi-tenant Grafana folders.

#### Scenario probe

**Situation:** Budget cap: build vs Datadog for 500 services.

**Model answer:** Napkin: ingest TB/day, retention, engineer cost to run Mimir vs vendor quote. Often hybrid: OTLP open, vendor store until Mimir ops team exists.

---

### 56. Design multi-region active-active with conflict resolution

**Short answer:** Active-active for reads and partitionable writes; conflict-prone entities (inventory, order state) need single-writer region, CRDT, or last-writer-wins with business rules—not naive dual-master SQL.

#### What it is
Stretch goal interview: name what can be active-active (catalog CDN, sessionless API) vs what cannot (order payment without conflict design).

#### How it works (internals)
Catalog: multi-region Redis/CRDB with async replication; orders: home region per `accountId` routing at APIM; conflict on rare cross-region migration via explicit handoff. Kafka MirrorMaker or global Event Hubs. Terraform per region.

#### When to use / when NOT to use
Honest CAP trade-off. Data residency may force EU-only writes. Reconcile jobs for drift.

#### Production example
Global SaaS: US/EU APIM; account created in EU stays EU SQL; catalog replicated read-only both sides. Admin reporting aggregates warehouse cross-region.

#### Common mistakes
Dual-write orders both regions. LWW on money fields. No DR drill.

#### Interview follow-ups (with model answers)

**Q:** CRDT for cart?
**A:** Maybe for cart merge; not for captured payment—source of truth single region.

**Q:** RPO for orders?
**A:** Zero for paid—async replicate not enough; route writes one region.

**Q:** DNS?
**A:** Geo DNS to nearest edge; APIM validates residency claim.

#### Scenario probe

**Situation:** CTO mandates active-active orders everywhere.

**Model answer:** Push back with conflict example: double ship same SKU. Offer active-active browse + single-region order writer with fast failover passive—measurable RPO.

---

### 57. Design a feature-flag platform at scale (LaunchDarkly-like)

**Short answer:** Flag service evaluates rules (user, tenant, % rollout) with sub-ms cache; SDK in app and React; audit changes; kill switch without redeploy. Flags stored in DB replicated to CDN/edge cache; real-time update via streaming.

#### What it is
LaunchDarkly-like: targeting, percentage rollouts, experiments, flag lifecycle—not env vars only.

#### How it works (internals)
Control plane API → flag definitions + rules → distribution to Redis/CDN; SDK polls or SSE. Spring `@FeatureFlag` aspect; React hook. Kafka optional for audit `flag-changed`. Stale cache TTL 30s acceptable for most flags.

#### When to use / when NOT to use
Build when hundreds of flags and compliance audit needed; else Unleash/Flipt open source. Remove flags after full rollout—debt rots.

#### Production example
500 microservices use shared `flags-service`; Helm env only for infra toggles. Payment provider switch uses flag with tenant allowlist; incident kill switch flips global in 10s.

#### Common mistakes
Flag only in frontend. Per-pod different flag state. 5000 permanent flags nobody removes.

#### Interview follow-ups (with model answers)

**Q:** Consistent rollout?
**A:** Sticky by userId hash; same user always same variant.

**Q:** Kafka consumer flag?
**A:** Evaluate at message processing time; document consumer version skew.

**Q:** vs Helm env?
**A:** Helm for deploy-time; flags for runtime product experiments.

#### Scenario probe

**Situation:** Team uses 12 env vars for 'flags' causing redeploy to toggle.

**Model answer:** Migrate hot toggles to platform; keep Helm for structural config. Diagram SDK cache path and kill switch drill.

---

### 58. Design a data export/GDPR erasure system across Kafka + DB

**Short answer:** Export: async job gathers user data from OLTP, search index, blob, warehouse pointers—zip to SAS download. Erasure: orchestrated saga pseudonymize/delete per store; legal hold blocks; Kafka tombstones or compacted topics policy documented.

#### What it is
GDPR data subject requests span SQL, Redis, Elasticsearch, S3, Kafka retained events, backups.

#### How it works (internals)
`POST /privacy/export` → saga `ExportRequested` → workers per system → manifest in blob → email link. Erasure: `DELETE_USER` saga with ordered steps; backup retention exception documented; reindex search; scrub notification logs.

#### When to use / when NOT to use
30-day SLA typical. Erasure is not instant delete everywhere—backups expire on schedule. Minimize PII in Kafka payloads day one.

#### Production example
EU tenant: export job on AKS writes encrypted zip; erasure saga marks SQL pseudonym, removes ES doc, schedules blob delete; Kafka compacted topics drop keys after retention.

#### Common mistakes
DELETE without warehouse plan. PII in Kafka forever. Export synchronous timeout.

#### Interview follow-ups (with model answers)

**Q:** Kafka erasure?
**A:** Tombstone keys, compaction, or accept retention window with no PII in payload.

**Q:** Legal hold?
**A:** Flag blocks erasure; audit why.

**Q:** Cross-border?
**A:** Export stays in EU region storage.

#### Scenario probe

**Situation:** Marketing wants email in Kafka for 'analytics forever.'

**Model answer:** Push userId-only events; hash email in warehouse with salt rotation. Document retention and erasure path before topic create.

---

### 59. Design API rate limiting at edge vs service vs DB

**Short answer:** Edge (APIM/CDN) stops abuse before it hits cluster; service-level token bucket for business rules; DB is last resort—if you rate limit in SQL, you are already in pain. Layer defenses with consistent identity key.

#### What it is
Rate limiting protects cost and fairness: per IP, API key, user, tenant, endpoint class.

#### How it works (internals)
APIM: 1000 req/min per subscription; WAF bot rules. Service Redis sliding window per `userId` on expensive endpoints. Payment calls global semaphore to PSP. 429 with `Retry-After`; React exponential backoff.

#### When to use / when NOT to use
Edge for DDoS and coarse limits; service for nuanced; never only in-app if multiple entry points. Whitelist partner mTLS.

#### Production example
Checkout 5/min/user at APIM; catalog 200/min; internal batch jobs mTLS bypass separate policy. Helm documents limits; Terraform APIM as code.

#### Common mistakes
Single global limit. Rate limit health checks. No coordination—each pod different counter without Redis.

#### Interview follow-ups (with model answers)

**Q:** APIM vs Redis?
**A:** APIM first shield; Redis when APIM cannot see custom claims.

**Q:** Burst?
**A:** Token bucket allows short burst; leaky bucket smooths.

**Q:** 429 client?
**A:** Respect Retry-After; idempotency keys on retry POST.

#### Scenario probe

**Situation:** Only app-level limit; attacker bypasses via direct pod IP.

**Model answer:** Network policy + ingress only through APIM; move limit to edge; pod-level redundant as defense in depth.

---

### 60. Staff-level trade-off: build vs buy for payments, search, email

**Short answer:** Payments: buy (Stripe/Adyen) unless you are a payment company. Search: buy managed (Algolia/Azure AI Search) until scale/custom ranking forces ES ops. Email: buy SendGrid/ACS—deliverability is the product. Build core domain order/inventory; buy commodity.

#### What it is
Staff interview tests judgment: TCO, team skills, compliance, time-to-market—not 'we build everything.'

#### How it works (internals)
Scorecard: strategic differentiation, regulatory burden, ops headcount, unit cost at 3-year volume, exit strategy. Payments build needs PCI program; search build needs cluster ops; email needs SPF/DKIM reputation.

#### When to use / when NOT to use
Buy commodity; build where competitive advantage and data moat. Hybrid: Stripe + custom ledger reconcile.

#### Production example
Marketplace launched Stripe Connect in 8 weeks vs 18-month internal PSP fantasy. OpenSearch self-host at 2M SKUs when Algolia bill crossed threshold—ADR documented.

#### Common mistakes
Build payments 'to save 2% fees' without PCI budget. NIH on email. Vendor lock-in fear without integration abstraction port.

#### Interview follow-ups (with model answers)

**Q:** When build search?
**A:** Custom ranking, data residency, bill > FTE cost of ES cluster with existing platform team.

**Q:** Abstraction layer?
**A:** PSP interface in domain; swap adapter—do not sprinkle Stripe SDK everywhere.

**Q:** Email build?
**A:** Almost never—deliverability and compliance favor ACS/SendGrid.

#### Scenario probe

**Situation:** CEO wants in-house payments to avoid fees at $10M GMV.

**Model answer:** Model PCI cost, fraud ops, opportunity cost vs 2.9% fee. Recommend Connect + negotiate volume pricing; revisit at $100M with dedicated payments team.

---



## Scenario-based interview drills

### S1. Checkout succeeds but inventory never reserved

**Situation:** Black Friday: `POST /orders` 201, UI pending forever. Kafka healthy; `inventory-projection` lag zero but no reservations.

**What they're testing:** Outbox, topic routing, consumer logic, observability.

**How to structure your answer:**
- Trace event path
- Verify topic and handler
- Schema mismatch
- Fix and replay

**Model answer:** Check outbox relay published `OrderPlaced`; grep consumer subscribes to wrong topic name AI renamed. Schema adds field consumer deserializer rejects—silent skip in bad code. Fix consumer, deploy, replay from outbox or offset. Add contract test on Avro. Alert on `orders PENDING > 5min` business metric.

**Common weak answers:** Only checking broker up; scaling consumers without reading errors.

**Follow-up probes (with answers):**

**Q:** Replay strategy?
**A:** Fix forward; replay DLT/outbox with idempotent reserve handler.


### S2. Subscription dunning emails duplicate

**Situation:** Customers report 5 failed-payment emails in one hour. Kafka consumer scaled to 12; notification idempotency missing.

**What they're testing:** Idempotency at worker, Kafka redelivery, dunning state machine.

**How to structure your answer:**
- Unique key design
- Consumer inbox
- Dunning step guard

**Model answer:** Add `notification_log` unique (subscriptionId, dunningStep, day). Consumer checks before SendGrid. Dunning scheduler idempotent with ShedLock. Root cause: at-least-once + retry without dedupe.

**Common weak answers:** Blaming SendGrid; scaling consumers without inbox.

**Follow-up probes (with answers):**

**Q:** Dunning state?
**A:** Track `dunning_step` on subscription; only advance on PSP webhook.


### S3. Marketplace escrow payout before delivery

**Situation:** Bug releases payout on `OrderPlaced` instead of `DeliveryConfirmed`. Sellers paid; buyers never shipped.

**What they're testing:** State machine, escrow gates, reconcile.

**How to structure your answer:**
- Stop batch payout
- Manual hold
- Fix state transition
- Ledger reconcile

**Model answer:** Kill payout job flag; freeze pending payouts. Fix transition; reconcile PSP balance vs ledger; CS outreach. Postmortem: integration test on state machine table; admin audit on payout triggers.

**Common weak answers:** Refund without ledger entry; hiding behind 'edge case.'

**Follow-up probes (with answers):**

**Q:** PSP escrow?
**A:** Use Connect separate charges and transfers with delayed transfer date.


### S4. OTel cardinality explosion

**Situation:** Metrics bill 3× after deploy adding `userId` label on HTTP metrics. Prometheus scrape timeout.

**What they're testing:** Cardinality, RED metrics, platform guardrails.

**How to structure your answer:**
- Drop label
- Recording rules
- Policy

**Model answer:** Remove high-cardinality label; use exemplars/traces for user debug. Enforce allowlist labels in CI review for custom metrics. Aggregate to route template.

**Common weak answers:** Increasing scrape interval only; buying bigger Prometheus without fix.

**Follow-up probes (with answers):**

**Q:** Trace vs metric?
**A:** Traces sample per request; metrics aggregate—never per-user counters at scale.


### S5. Active-active cart merge lost items

**Situation:** User edits cart on phone (EU) and laptop (US) with naive LWW sync—items disappear.

**What they're testing:** CRDT vs single region; cart semantics.

**How to structure your answer:**
- User experience
- Technical fix
- Residency

**Model answer:** Cart is per-account home region write; or CRDT merge (Yjs-style structure). LWW wrong for union sets—use max-quantity merge rules. Educate product on residency routing.

**Common weak answers:** Global dual-write SQL cart.

**Follow-up probes (with answers):**

**Q:** Session cart?
**A:** Server cart keyed accountId; merge on login with conflict UI.


### S6. Feature flag split-brain during incident

**Situation:** Half of pods cached `new-psp=true`, half false—payments split between Stripe and Adyen mid-incident.

**What they're testing:** Flag consistency, cache TTL, kill switch.

**How to structure your answer:**
- Flip flag global
- Reduce TTL
- Restart vs SSE push

**Model answer:** Use centralized flag service with short TTL + push update; or restart pods after kill switch. Document incident: flags are runtime config needing same care as deploy.

**Common weak answers:** Editing Helm only without flag service during fire.

**Follow-up probes (with answers):**

**Q:** Kafka consumer flag?
**A:** Evaluate per message; version skew doc for deploy+flag change order.


### S7. GDPR erasure incomplete—search still shows user

**Situation:** Erasure saga completed SQL; customer still in OpenSearch typeahead.

**What they're testing:** Erasure orchestration, index lag, verification.

**How to structure your answer:**
- Saga step for search
- Reindex job
- Verification API

**Model answer:** Add search delete step with completion check; automated test subject erasure in staging. Typeahead separate index must be in catalog.

**Common weak answers:** Claiming GDPR done when SQL only.

**Follow-up probes (with answers):**

**Q:** Kafka PII?
**A:** Prevent by design—userId only in events.


### S8. Rate limit bypass hits database

**Situation:** Scraper uses distributed IPs; APIM limit per IP ineffective. DB CPU 95%.

**What they're testing:** Layered limits, identity, WAF.

**How to structure your answer:**
- Authenticated limits
- WAF bot score
- Expensive endpoint protection

**Model answer:** Require API key or auth for catalog bulk; CAPTCHA on suspect ASNs; Redis global limit on `GET /products` per API key. Circuit break to cache read-only.

**Common weak answers:** Only IP limit; scaling DB vertically forever.

**Follow-up probes (with answers):**

**Q:** Partner whitelist?
**A:** mTLS identity separate bucket from anonymous IP.


### S9. Fraud ML blocks legitimate flash sale

**Situation:** Model threshold low; 40% checkouts manual review queue; revenue drop.

**What they're testing:** Rules vs ML ops, threshold tuning, shadow mode.

**How to structure your answer:**
- Rollback threshold
- Rules override for campaign
- Human capacity

**Model answer:** Raise threshold; add campaign allowlist rule; scale review team temporary. Shadow mode new models before enforcing. KPI: precision/recall per segment.

**Common weak answers:** Disabling fraud entirely; only ML no rules.

**Follow-up probes (with answers):**

**Q:** Human queue SLA?
**A:** Staff capacity plan for peak; auto-approve low $ with step-up.


### S10. 45-minute design: 'Design Uber for groceries' scope creep

**Situation:** Interviewer keeps adding driver GPS, chat, dynamic pricing in minute 10.

**What they're testing:** Scope control, MVP, checklist.

**How to structure your answer:**
- Clarify MVP
- Phase table
- Timebox depth

**Model answer:** I table MVP: order, inventory, delivery assign, payment—defer chat and surge pricing to phase 2 with triggers. Use checklist minute 40 for failures/idempotency. Staff close: ship vertical slice with SLO then iterate.

**Common weak answers:** Drawing everything; no failure paths; no idempotency.

**Follow-up probes (with answers):**

**Q:** When push back on scope?
**A:** When NFRs undefined—ask QPS and consistency before boxes.
