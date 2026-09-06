# Event-Driven Architecture — 50 Senior Interview Questions

**Bar:** Dual write, causality, contracts, "eventual" UX. EDA is in the fullstack JDs explicitly.

---

### 1. Event vs command vs query.

**Short answer:** Events are immutable facts in past tense (`OrderPlaced`); commands express intent and may be rejected (`PlaceOrder`); queries read state with no side effects. Mixing these leads to consumers treating rejected intents as truth and breaking idempotency. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Event-driven architecture separates **what happened** (events) from **what someone wants** (commands) and **what someone needs to know now** (queries). This mirrors CQRS at the messaging layer: write paths emit facts; read paths serve projections. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Commands travel on a command bus or HTTP endpoint with validation, authorization, and aggregate invariants. On success, the domain emits one or more events. Events are append-only notifications consumed by many subscribers. Queries never mutate state — they hit read models, APIs, or materialized views built from events.

#### When to use / when NOT to use
Use events for cross-service integration and eventual consistency. Use commands for synchronous user actions that need immediate accept/reject. Do not publish commands to a topic and expect every subscriber to treat them as facts — that is choreography without contracts.

#### Production example
An order service accepts `PlaceOrder` via REST, persists the aggregate, writes an outbox row `OrderPlaced`, and a notification service subscribes to build email. Inventory listens to `OrderPlaced`, not to `PlaceOrder`. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Subscribing to command topics. Naming events in imperative form (`PlaceOrder` instead of `OrderPlaced`). Emitting events before the transaction commits (lost on crash).

#### Interview follow-ups (with model answers)

**Q:** How does this relate to CQRS?
**A:** For «Event vs command vs query»: How does this relate to CQRS. In production, An order service accepts `PlaceOrder` via REST, persists the aggregate, writes an outbox row `OrderPlaced`, and a notification service subscribes to build email. Inventory listens to `OrderPlaced`, not to `PlaceOrder`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Can a command handler emit multiple events?
**A:** The follow-on risk of «Can a command handler emit multiple events» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is an integration event vs a domain event?
**A:** Trade-off framing for «What is an integration event vs a domain event»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Event vs command vs query.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: An order service accepts `PlaceOrder` via REST, persists the aggregate, writes an outbox row `OrderPlaced`, and a notification service subscribes to build email…. I suspect subscribing to command topics until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 2. Notification event vs event-carried state transfer vs event sourcing.

**Short answer:** Notification events carry minimal identifiers and force consumers to fetch state. Event-carried state transfer (ECST) embeds enough data to act without a callback. Event sourcing stores the event log as the system of record. Most production systems use ECST plus a relational DB as source of truth, not full event sourcing everywhere.

#### What it is
These are three levels of payload richness and persistence strategy. Notification is the thinnest; ECST is the pragmatic middle; event sourcing is the architectural extreme where replay reconstructs all state. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Notification: producer emits `OrderUpdated(orderId=5)`; consumer calls GET `/orders/5` — chatty, coupled to API availability. ECST: payload includes `status`, `lineItems`, `total` so inventory and billing act locally. Event sourcing: every state change is an event in a store; snapshots accelerate rebuild; projections are derived views.

#### When to use / when NOT to use
ECST when consumers need autonomy and you accept denormalized duplication. Notification when payload size or PII is a concern and the consumer is the same team. Full event sourcing for audit-heavy domains (ledger, compliance) — not for every CRUD microservice.

#### Production example
`OrderPlaced` ECST event includes `customerId`, `sku`, `qty`, `priceAtOrderTime`. Billing never calls Order API at checkout peak. Order DB remains SoT; Kafka holds integration events with retention policy.

#### Common mistakes
Thin events everywhere, then 15 sync REST calls per event. Event sourcing without snapshot strategy — rebuild takes hours. Confusing Kafka retention with eternal event store.

#### Interview follow-ups (with model answers)

**Q:** How do you handle schema drift in ECST payloads?
**A:** For «Notification event vs event-carried state transfer vs event sourcing»: How do you handle schema drift in ECST payloads. In production, `OrderPlaced` ECST event includes `customerId`, `sku`, `qty`, `priceAtOrderTime`. Billing never calls Order API at checkout peak. Order DB remains SoT; Kafka holds integration events with retention policy. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When would you add event sourcing to one aggregate only?
**A:** The follow-on risk of «When would you add event sourcing to one aggregate only» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is the dual-write problem with each approach?
**A:** Trade-off framing for «What is the dual-write problem with each approach»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Notification event vs event-carried stat.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `OrderPlaced` ECST event includes `customerId`, `sku`, `qty`, `priceAtOrderTime`. Billing never calls Order API at checkout peak.. I suspect thin events everywhere, then 15 sync rest calls per event until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 3. Thin vs fat events.

**Short answer:** Thin events carry IDs only; fat events carry denormalized business data. Fat reduces coupling to read APIs and improves resilience; thin reduces PII spread and versioning pain. A hybrid — key IDs plus a few stable fields — is what most mature teams land on. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
A design trade-off about how much data crosses the integration boundary in a single message. It directly affects choreography coupling, GDPR scope, and consumer availability requirements. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Thin: consumer must hydrate from another service or local cache — failure or latency in the source API blocks processing. Fat: consumer writes its projection from the payload alone — eventual consistency bounded by event delivery, not by N+1 HTTP. Versioning fat payloads requires additive-only evolution and contract tests.

#### When to use / when NOT to use
Fat when downstream services must stay available during source outages and sagas must not block on REST. Thin when data is sensitive, changes frequently, or consumers are few and co-located. Avoid fat events that embed entire aggregate graphs that change every sprint.

#### Production example
`PaymentCaptured` includes `orderId`, `amount`, `currency`, `paymentMethod` (no full PAN). Fraud service processes without calling Payment API. Customer name stays thin — fetched only when UI needs it.

#### Common mistakes
Fat events with PII that replicate to five topics. Thin events that cause thundering herd on the Order API during replay. Changing field semantics without a new event version.

#### Interview follow-ups (with model answers)

**Q:** How does ECST relate to bounded context boundaries?
**A:** For «Thin vs fat events»: How does ECST relate to bounded context boundaries. In production, `PaymentCaptured` includes `orderId`, `amount`, `currency`, `paymentMethod` (no full PAN). Fraud service processes without calling Payment API. Customer name stays thin — fetched only when UI needs it. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What fields belong in the integration envelope vs payload?
**A:** The follow-on risk of «What fields belong in the integration envelope vs payload» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How do you compact or tombstone fat events under GDPR?
**A:** Trade-off framing for «How do you compact or tombstone fat events under GDPR»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Thin vs fat events.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `PaymentCaptured` includes `orderId`, `amount`, `currency`, `paymentMethod` (no full PAN). Fraud service processes without calling Payment API.. I suspect fat events with pii that replicate to five topics until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 4. Dual-write problem.

**Short answer:** Writing the database and the message broker in two separate operations guarantees that one can succeed while the other fails — the classic dual-write bug. Fix it with the transactional outbox (same DB transaction) or CDC from the WAL, never with "best effort" publish after commit. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The foundational reliability problem in event-driven systems: two side effects (persist state, emit event) without a single atomic unit spanning both stores. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Pattern A: `@Transactional` saves business row, then `kafkaTemplate.send()` — if JVM dies after commit but before send, consumers never see the event; if send succeeds and DB rolls back, consumers see a ghost event. Pattern B: outbox table insert in same TX as business write; separate relay publishes and marks sent. Pattern C: Debezium reads binlog/WAL and emits change records — no app-level second write.

#### When to use / when NOT to use
Always solve dual-write before scaling event consumers. Outbox when you control the app and want explicit integration events. CDC when retrofitting legacy monoliths or when ops owns Debezium. Never rely on `@TransactionalEventListener` alone for money paths.

#### Production example
Order service INSERT into `orders` and `outbox` in one `@Transactional` method. Outbox relay publishes to `orders.events` keyed by `orderId`. Payment service inbox deduplicates `OrderPlaced`.

#### Common mistakes
"Fire-and-forget Kafka after save." Assuming Kafka transactions update Oracle. Retry loops that double-charge because publish succeeded twice.

#### Interview follow-ups (with model answers)

**Q:** Compare outbox polling vs CDC for your stack?
**A:** For «Dual-write problem»: Compare outbox polling vs CDC for your stack. In production, Order service INSERT into `orders` and `outbox` in one `@Transactional` method. Outbox relay publishes to `orders.events` keyed by `orderId`. Payment service inbox deduplicates `OrderPlaced`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What happens on outbox relay crash mid-batch?
**A:** The follow-on risk of «What happens on outbox relay crash mid-batch» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How does idempotency on the consumer side help?
**A:** Trade-off framing for «How does idempotency on the consumer side help»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Dual-write problem.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order service INSERT into `orders` and `outbox` in one `@Transactional` method. Outbox relay publishes to `orders.events` keyed by `orderId`.. I suspect "fire-and-forget kafka after save until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 5. Outbox pattern details.

**Short answer:** Persist the outbound message in an `outbox` table inside the same database transaction as the business write, then relay it to the broker asynchronously. Key by aggregate ID for ordering, mark rows published after ack, and make the relay idempotent. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The standard Java/Spring pattern for reliable event publication without XA or dual-write. It turns "publish event" into "insert row" — something your DB already commits atomically. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Schema: `outbox(id, aggregate_type, aggregate_id, event_type, payload, created_at, published_at)`. Business TX inserts domain row + outbox row. Relay: polling (`SELECT ... WHERE published_at IS NULL FOR UPDATE SKIP LOCKED`) or log-based CDC on the outbox table. Partition key = `aggregate_id` preserves per-order ordering. Idempotent publish: same outbox id → same Kafka record key + dedup on consumer.

#### When to use / when NOT to use
Default choice for new Spring microservices with Postgres/Oracle. CDC-on-outbox when polling lag is unacceptable. Skip outbox only for truly fire-and-forget analytics where loss is acceptable.

#### Production example
Spring `@Transactional` service method; Debezium connector on `outbox` with `transforms` to map to Avro; consumer groups keyed by `orderId`; inbox table stores `event_id` unique constraint. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Publishing before commit (AFTER_COMMIT listener without outbox). No `SKIP LOCKED` → relay instances fight. Huge JSON blobs in outbox without retention cleanup.

#### Interview follow-ups (with model answers)

**Q:** How often do you poll vs use Debezium?
**A:** For «Outbox pattern details»: How often do you poll vs use Debezium. In production, Spring `@Transactional` service method; Debezium connector on `outbox` with `transforms` to map to Avro; consumer groups keyed by `orderId`; inbox table stores `event_id` unique constraint. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Outbox cleanup and archival strategy?
**A:** The follow-on risk of «Outbox cleanup and archival strategy» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How do you handle outbox ordering across aggregates?
**A:** Trade-off framing for «How do you handle outbox ordering across aggregates»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Outbox pattern details.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Spring `@Transactional` service method; Debezium connector on `outbox` with `transforms` to map to Avro; consumer groups keyed by `orderId`; inbox table stores…. I suspect publishing before commit (after_commit listener without outbox) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```sql
-- Same TX as business write
INSERT INTO outbox (id, aggregate_id, event_type, payload)
VALUES (:uuid, :orderId, 'OrderPlaced', :json);
```

---

### 6. CDC (Debezium) as EDA.

**Short answer:** Change Data Capture reads the database write-ahead log and emits change events without application code changes. Powerful for legacy integration, but raw table CDC leaks internal schema, complicates deletes, and requires a translation layer before treating rows as public integration events. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Debezium (and similar tools) turn database mutations into Kafka topics by tailing Oracle redo, Postgres WAL, or MySQL binlog. It is an alternative outbox relay that observes storage, not domain intent. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Connector captures INSERT/UPDATE/DELETE with before/after images. Initial snapshot bootstraps existing rows. Schema changes propagate via Debezium schema topic. Deletes become tombstones or delete events — consumers must handle. Transform pipeline (SMTs) can route, filter, and mask columns before public topics.

#### When to use / when NOT to use
Use when retrofitting a monolith, when multiple consumers need the same change stream, or when outbox retrofit is too invasive. Avoid exposing raw `orders` table CDC as your public contract — translate to `OrderPlaced` in a stream processor or dedicated ACL service. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Debezium on `outbox` table only (hybrid). Or CDC on `orders` → Kafka Connect → Spring stream app maps row to integration Avro → `orders.public.events`. PII columns stripped in SMT.

#### Common mistakes
Publishing every column including internal flags. No handling of hard DELETE vs soft delete. Snapshot + streaming gap during connector restart without monitoring.

#### Interview follow-ups (with model answers)

**Q:** How do you handle Oracle supplemental logging?
**A:** For «CDC (Debezium) as EDA»: How do you handle Oracle supplemental logging. In production, Debezium on `outbox` table only (hybrid). Or CDC on `orders` → Kafka Connect → Spring stream app maps row to integration Avro → `orders.public.events`. PII columns stripped in SMT. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Snapshot vs streaming lag SLO?
**A:** The follow-on risk of «Snapshot vs streaming lag SLO» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is CDC worse than explicit outbox?
**A:** Trade-off framing for «When is CDC worse than explicit outbox»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on CDC (Debezium) as EDA.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Debezium on `outbox` table only (hybrid). Or CDC on `orders` → Kafka Connect → Spring stream app maps row to integration Avro → `orders.public.events`.. I suspect publishing every column including internal flags until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 7. Choreography coupling.

**Short answer:** Pure choreography means services react to each other's events without a central coordinator — fast to start, fragile at scale. Changing a field on `OrderPlaced` silently breaks five teams unless you treat events as versioned public contracts with anti-corruption layers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Choreography is decentralized saga coordination: each service knows "when I see X, I do Y." Logical coupling remains even when temporal coupling is removed. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Service A emits fact; B, C, D subscribe independently. No single place shows the full workflow. Refactoring A's event schema ripples to all subscribers. Mitigations: integration event layer (translate domain → public), schema registry compatibility, consumer-driven contract tests, and explicit policy documentation.

#### When to use / when NOT to use
Choreography for 2–3 step side effects with stable domains. Orchestration (or Temporal) when workflows have timers, human steps, or 10+ participants. Never let internal domain events leak across context boundaries.

#### Production example
Order emits `OrderPlacedV2` on public topic; internal `OrderEntitySaved` stays in-process. Inventory anti-corruption mapper converts to its `ReservationRequest` command — not raw JSON coupling. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
"We're decoupled because we use Kafka." Breaking changes without version bump. Hidden policies in random `@KafkaListener` classes.

#### Interview follow-ups (with model answers)

**Q:** Choreography vs orchestration for a checkout saga?
**A:** For «Choreography coupling»: Choreography vs orchestration for a checkout saga. In production, Order emits `OrderPlacedV2` on public topic; internal `OrderEntitySaved` stays in-process. Inventory anti-corruption mapper converts to its `ReservationRequest` command — not raw JSON coupling. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you discover all consumers of an event?
**A:** The follow-on risk of «How do you discover all consumers of an event» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is the strangler pattern for event contracts?
**A:** Trade-off framing for «What is the strangler pattern for event contracts»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Choreography coupling.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order emits `OrderPlacedV2` on public topic; internal `OrderEntitySaved` stays in-process.. I suspect "we're decoupled because we use kafka until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 8. Process manager / orchestrator.

**Short answer:** A process manager (saga orchestrator) holds workflow state, sends commands to participants, and reacts to their events. It gives visibility and centralized timeout handling but can become a god service if you embed domain logic instead of routing. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The orchestration half of saga patterns — explicit state machine for long-running business processes like order fulfillment or loan approval. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Orchestrator stores saga instance: `{sagaId, state, step, correlationId}`. On `OrderPlaced`, sends `ReserveInventory` command; waits for `InventoryReserved` or `InventoryFailed`; emits compensations on failure. Implemented as a stateful service, workflow engine (Temporal, Camunda), or dedicated module — not scattered listeners.

#### When to use / when NOT to use
Use when the business needs a visible process, SLA timers, or human approval steps. Avoid a single orchestrator owning all microservices' domain rules. Keep it thin: route, correlate, timeout — domain stays in bounded contexts.

#### Production example
Checkout saga orchestrator in Temporal: activities call Inventory/Payment APIs; saga state durable; compensation runs `ReleaseInventory` + `VoidPayment` with idempotency keys. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Orchestrator directly updating another service's tables. No timeout → saga stuck forever. Compensations that aren't idempotent.

#### Interview follow-ups (with model answers)

**Q:** How is this different from choreography?
**A:** For «Process manager / orchestrator»: How is this different from choreography. In production, Checkout saga orchestrator in Temporal: activities call Inventory/Payment APIs; saga state durable; compensation runs `ReleaseInventory` + `VoidPayment` with idempotency keys. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Where do correlation IDs live?
**A:** The follow-on risk of «Where do correlation IDs live» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When would you pick Temporal over a homemade table?
**A:** Trade-off framing for «When would you pick Temporal over a homemade table»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Process manager / orchestrator.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Checkout saga orchestrator in Temporal: activities call Inventory/Payment APIs; saga state durable; compensation runs `ReleaseInventory` + `VoidPayment` with id…. I suspect orchestrator directly updating another service's tables until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 9. Idempotency and at-least-once.

**Short answer:** Every mainstream broker defaults to at-least-once delivery — duplicates will happen. Handlers must be idempotent: processing the same event twice produces the same outcome. Prefer database unique constraints on `event_id` over check-then-insert without locking. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
The pairing that makes eventual consistency safe: unreliable delivery semantics plus deterministic handler design. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer retries, consumer rebalance, and partial failure all cause redelivery. Idempotency strategies: natural keys (`UPSERT` on `orderId`), inbox table with `UNIQUE(event_id)`, business idempotency keys on commands, or state version checks (`apply if version = n+1`). "Check if exists then insert" races under concurrent consumers — use constraints.

#### When to use / when NOT to use
Always for payment, inventory, and notification side effects. At-most-once only for metrics where loss beats duplication. Exactly-once Kafka EOS still requires idempotent side effects on external DBs.

#### Production example
Inbox: `INSERT INTO processed_events(event_id, processed_at)` — duplicate key → skip handler, ack offset. Payment handler uses idempotency key from event envelope. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Non-idempotent `sendEmail()` on every replay. Relying on Kafka EOS to prevent double charge in Oracle. In-memory dedup caches that lose state on restart.

#### Interview follow-ups (with model answers)

**Q:** Inbox vs idempotency key vs optimistic locking?
**A:** For «Idempotency and at-least-once»: Inbox vs idempotency key vs optimistic locking. In production, Inbox: `INSERT INTO processed_events(event_id, processed_at)` — duplicate key → skip handler, ack offset. Payment handler uses idempotency key from event envelope. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How long do you retain processed event IDs?
**A:** The follow-on risk of «How long do you retain processed event IDs» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What about partial failure after DB commit but before ack?
**A:** Trade-off framing for «What about partial failure after DB commit but before ack»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Idempotency and at-least-once.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Inbox: `INSERT INTO processed_events(event_id, processed_at)` — duplicate key → skip handler, ack offset.. I suspect non-idempotent `sendemail()` on every replay until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```sql
CREATE UNIQUE INDEX ux_inbox_event ON processed_events (event_id);
-- duplicate insert → skip business logic
```

---

### 10. Ordering and causality.

**Short answer:** Brokers guarantee order only within a partition or queue shard keyed consistently — typically per aggregate ID. Cross-aggregate ordering does not exist without a global sequencer. Use monotonic version numbers on events and reject stale applies to preserve causal correctness locally. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Ordering constraints define what consumers can assume about event sequence. Causality is which event caused which — tracked via `causationId`, not broker timestamps alone. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka: same key → same partition → FIFO per key. Multiple keys interleave arbitrarily. Sagas spanning services may see `PaymentCaptured` before `OrderPlaced` if mis-keyed — design keys deliberately. Version field on aggregate events: consumer applies only if `event.version == current + 1`.

#### When to use / when NOT to use
Per-aggregate ordering for state machine transitions. Do not design for global order across all orders in the system. Vector clocks are overkill for most Java microservices — version integers suffice.

#### Production example
All `order-12345` events keyed to partition hash of `12345`. Inventory projection stores `lastAppliedVersion`; ignores out-of-order lower versions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Null keys → round-robin → order lost. Changing partition count without migration plan. Sorting by consumer timestamp instead of event version.

#### Interview follow-ups (with model answers)

**Q:** What breaks when you increase partition count?
**A:** For «Ordering and causality»: What breaks when you increase partition count. In production, All `order-12345` events keyed to partition hash of `12345`. Inventory projection stores `lastAppliedVersion`; ignores out-of-order lower versions. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do causation and correlation IDs differ?
**A:** The follow-on risk of «How do causation and correlation IDs differ» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Ordering guarantees in SQS FIFO vs Kafka?
**A:** Trade-off framing for «Ordering guarantees in SQS FIFO vs Kafka»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Ordering and causality.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: All `order-12345` events keyed to partition hash of `12345`. Inventory projection stores `lastAppliedVersion`; ignores out-of-order lower versions.. I suspect null keys → round-robin → order lost until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 11. Out-of-order events.

**Short answer:** Retries, multiple producers, partition reassignment, and cross-region replication all deliver events out of order. Buffer with version checks, drop stale events explicitly, or use saga orchestration — never assume last-write-wins without understanding lost updates. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
A runtime reality in distributed logs, not an edge case. Projections and aggregate rebuilds must tolerate reordering within the consistency model you promise. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Network retry can deliver `OrderShipped` before `OrderPaid` if keyed differently or from different services. Strategies: (1) ignore if `event.version <= currentVersion`; (2) buffer pending events in a priority queue by version (memory cost); (3) orchestrator enforces step order; (4) idempotent handlers where order doesn't matter.

#### When to use / when NOT to use
Version gate for single-aggregate projections. Buffering when strict sequential apply is required and volume is bounded. Last-write-wins only for idempotent scalar fields with clear timestamp authority — dangerous for counters.

#### Production example
Customer profile projector: `if (incoming.version <= row.version) return;` else apply. Alert if gap detected (`version > current + 1`) — signals missing event.

#### Common mistakes
Blind LWW on status fields — `CANCELLED` overwritten by late `SHIPPED`. No metric for version gaps. Blocking partition on one bad ordered sequence.

#### Interview follow-ups (with model answers)

**Q:** How long do you buffer out-of-order events?
**A:** For «Out-of-order events»: How long do you buffer out-of-order events. In production, Customer profile projector: `if (incoming.version <= row.version) return;` else apply. Alert if gap detected (`version > current + 1`) — signals missing event. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What if the missing event never arrives?
**A:** The follow-on risk of «What if the missing event never arrives» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Relationship to CQRS rebuild?
**A:** Trade-off framing for «Relationship to CQRS rebuild»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Out-of-order events.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Customer profile projector: `if (incoming.version <= row.version) return;` else apply. Alert if gap detected (`version > current + 1`) — signals missing event.. I suspect blind lww on status fields — `cancelled` overwritten by late `shipped` until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 12. Read models / projections.

**Short answer:** Projections are query-optimized tables built asynchronously from events — the read side of CQRS. They lag the write model by design; you rebuild from the log when corrupted, subject to retention limits on compacted or time-bound topics. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Consumers that transform event streams into SQL documents, Elasticsearch indices, or cache entries tailored for UI and reporting. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Event handler applies delta: `OrderPlaced` → insert row in `order_search_view`. Offset stored in same DB transaction (inbox pattern) for exactly-once effect. Full rebuild: reset consumer to earliest offset or replay from event store — impossible if topic retention expired and no archive.

#### When to use / when NOT to use
Use when read patterns differ from write model (search, dashboards, BFF aggregation). Same table for read/write only when consistency requirements are simple. Plan retention and archival before promising "rebuild anytime."

#### Production example
Spring `@KafkaListener` updates Postgres `order_read_model`; composite index on `(customer_id, created_at)`; lag monitored; nightly reconcile job compares counts to source. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Projection logic in the write service. No rebuild runbook. Assuming infinite Kafka retention for audit rebuild.

#### Interview follow-ups (with model answers)

**Q:** How do you measure projection lag SLO?
**A:** For «Read models / projections»: How do you measure projection lag SLO. In production, Spring `@KafkaListener` updates Postgres `order_read_model`; composite index on `(customer_id, created_at)`; lag monitored; nightly reconcile job compares counts to source. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Snapshot + event replay hybrid?
**A:** The follow-on risk of «Snapshot + event replay hybrid» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Multiple projections from one topic — consumer groups?
**A:** Trade-off framing for «Multiple projections from one topic — consumer groups»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Read models / projections.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Spring `@KafkaListener` updates Postgres `order_read_model`; composite index on `(customer_id, created_at)`; lag monitored; nightly reconcile job compares count…. I suspect projection logic in the write service until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 13. CQRS without two databases.

**Short answer:** CQRS separates command and query models logically, not necessarily physically. Start with one database and different tables or schemas — `orders` write table plus `order_summary` projection in the same Postgres instance. Split databases only when scale or team boundaries require it. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Command Query Responsibility Segregation: writes go through aggregates and emit events; reads hit optimized models. The split is about model shape and consistency boundaries, not mandatory microservice topology. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Write path: validate command, mutate aggregate, outbox event. Read path: query projection table — may be milliseconds to seconds stale. Same DB: transactional consistency for outbox + write row; projection updated async in same instance avoids network partition between write and read DB.

#### When to use / when NOT to use
Same DB CQRS when team is small and eventual read lag is acceptable. Separate read DB when read QPS dominates or analytics workloads threaten OLTP. Don't CQRS a simple admin CRUD — operational cost isn't worth it.

#### Production example
Oracle `ORDERS` + `ORDER_READ_MV` maintained by consumer; UI list page reads MV; detail page optionally reads write model for read-your-writes on redirect after submit. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Two databases on day one without ops maturity. No strategy for read-your-writes UX. Confusing CQRS with "must use Kafka."

#### Interview follow-ups (with model answers)

**Q:** When do you split read DB to Mongo/Elasticsearch?
**A:** For «CQRS without two databases»: When do you split read DB to Mongo/Elasticsearch. In production, Oracle `ORDERS` + `ORDER_READ_MV` maintained by consumer; UI list page reads MV; detail page optionally reads write model for read-your-writes on redirect after submit. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does saga compensation interact with read models?
**A:** The follow-on risk of «How does saga compensation interact with read models» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Eventual consistency messaging to product owners?
**A:** Trade-off framing for «Eventual consistency messaging to product owners»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on CQRS without two databases.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Oracle `ORDERS` + `ORDER_READ_MV` maintained by consumer; UI list page reads MV; detail page optionally reads write model for read-your-writes on redirect after…. I suspect two databases on day one without ops maturity until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 14. Event versioning.

**Short answer:** Evolve events additively by default — new optional fields, never change semantics of existing fields. Use explicit `eventType` and `schemaVersion`; add upcasters for old consumers; renames and breaking changes mean a new event type, not silent mutation. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Contract evolution discipline for integration events that may live in Kafka for years and be replayed by consumers you don't control. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Envelope: `{ "type": "OrderPlaced", "version": 2, "payload": {...} }`. Upcaster maps v1 → v2 in consumer before handler. Schema registry (Avro) enforces BACKWARD compatibility. CI runs compatibility checks on producer PRs. Dual-publish v1 and v2 during migration window if needed.

#### When to use / when NOT to use
Always version public integration events. Internal in-process domain events can move faster with co-deployed services. Never "fix" a field meaning in place — consumers replaying old offsets will corrupt state.

#### Production example
`OrderPlacedV1` had `amount`; V2 adds optional `currency` with default `USD` in upcaster. Registry subject `orders-OrderPlaced-value` compatibility BACKWARD. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Removing fields without tombstone strategy. JSON without contract tests. Assuming all consumers deploy same day.

#### Interview follow-ups (with model answers)

**Q:** UPcaster vs downcaster?
**A:** For «Event versioning»: UPcaster vs downcaster. In production, `OrderPlacedV1` had `amount`; V2 adds optional `currency` with default `USD` in upcaster. Registry subject `orders-OrderPlaced-value` compatibility BACKWARD. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How long dual-write two event versions?
**A:** The follow-on risk of «How long dual-write two event versions» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Avro WRITER vs READER schema?
**A:** Trade-off framing for «Avro WRITER vs READER schema»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Event versioning.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `OrderPlacedV1` had `amount`; V2 adds optional `currency` with default `USD` in upcaster. Registry subject `orders-OrderPlaced-value` compatibility BACKWARD.. I suspect removing fields without tombstone strategy until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 15. Schema registry vs JSON cowboy.

**Short answer:** A schema registry (Confluent with Avro/Protobuf/JSON Schema) enforces compatibility at publish time. JSON without discipline becomes "cowboy" — breaking changes ship silently. Pick one governance model and enforce it in CI; hybrid JSON events need consumer-driven contract tests as strict as registry rules. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
The tooling layer that prevents incompatible producers from breaking downstream projections and sagas. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Registry stores schema IDs embedded in Kafka messages (Avro wire format). Producer registers schema; incompatible evolution rejected. JSON Schema registry similar with compatibility levels. Without registry: Pact or manual fixture tests, example payloads in repo, lint on PR — easy to skip under deadline pressure.

#### When to use / when NOT to use
Registry when multiple teams publish/consume and replay matters. JSON with strict Pact when polyglot or human-readable debugging dominates — but apply the same compatibility rules manually. Don't mix unregistered JSON and Avro on the same public topic without clear boundaries.

#### Production example
All `*.events` topics Avro BACKWARD; Spring Cloud Stream with `KafkaAvroSerializer`; breaking change blocked in CI `mvn schema-registry:test-compatibility`. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
`latest` schema auto-registered in prod without review. FORWARD compatibility assumed when consumers lag weeks. No subject naming strategy — chaos.

#### Interview follow-ups (with model answers)

**Q:** BACKWARD vs FULL compatibility for your consumers?
**A:** For «Schema registry vs JSON cowboy»: BACKWARD vs FULL compatibility for your consumers. In production, All `*.events` topics Avro BACKWARD; Spring Cloud Stream with `KafkaAvroSerializer`; breaking change blocked in CI `mvn schema-registry:test-compatibility`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you version JSON events without Avro?
**A:** The follow-on risk of «How do you version JSON events without Avro» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Schema evolution with CDC Debezium payloads?
**A:** Trade-off framing for «Schema evolution with CDC Debezium payloads»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Schema registry vs JSON cowboy.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: All `*.events` topics Avro BACKWARD; Spring Cloud Stream with `KafkaAvroSerializer`; breaking change blocked in CI `mvn schema-registry:test-compatibility`.. I suspect `latest` schema auto-registered in prod without review until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 16. PII in events.

**Short answer:** Events persist on disk with retention — treat the bus as a long-lived datastore, not ephemeral RAM. Minimize PII in payloads, tokenize identifiers, encrypt sensitive fields, and plan crypto-shredding or tombstones for GDPR erasure — legal hold may conflict with right-to-be-forgotten. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Privacy and compliance design for integration events that replicate customer data across services and regions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Prefer opaque `customerToken` over email in events. Field-level encryption with per-subject keys; shred key on delete request. Compacted topics retain last value per key — tombstone `null` value to propagate delete. Audit who consumes PII topics. DLP scanning on produce path.

#### When to use / when NOT to use
Zero PII in public topics when possible — consumers fetch from authorized API with audit. Tokenization when downstream needs stable correlation. Never log full payloads with PAN/SSN in application logs mirroring events.

#### Production example
`CustomerRegistered` carries `customerId` only; notification service calls Customer API with service account for email. Encrypted `emailEncrypted` field for one consumer with shared KMS key rotation documented. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Full customer object in every fat event. GDPR DELETE in SQL only — Kafka still has six copies. Ignoring compacted topic resurrection after tombstone ages out.

#### Interview follow-ups (with model answers)

**Q:** Crypto-shred vs rewrite topic for erasure?
**A:** For «PII in events»: Crypto-shred vs rewrite topic for erasure. In production, `CustomerRegistered` carries `customerId` only; notification service calls Customer API with service account for email. Encrypted `emailEncrypted` field for one consumer with shared KMS key rotation documented. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does PII affect schema registry retention?
**A:** The follow-on risk of «How does PII affect schema registry retention» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Data residency across replicated topics?
**A:** Trade-off framing for «Data residency across replicated topics»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on PII in events.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `CustomerRegistered` carries `customerId` only; notification service calls Customer API with service account for email.. I suspect full customer object in every fat event until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 17. Temporal coupling vs logical coupling.

**Short answer:** Async messaging removes the requirement that both services are up at the same instant — temporal decoupling. Logical coupling remains: consumers still depend on the meaning and schema of your events. Claiming "fully decoupled" because you use Kafka is a red flag in senior interviews. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Two dimensions of dependency: **when** (availability timing) and **what** (semantic contract). EDA solves the first, not the second. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Temporal: Order service down doesn't block Inventory from processing yesterday's backlog — lag grows but system progresses. Logical: Inventory still breaks if `OrderPlaced` schema changes without notice. Anti-corruption layers and versioned contracts reduce logical coupling; they don't eliminate it.

#### When to use / when NOT to use
Async when peak load, resilience, or multi-subscriber fan-out justify eventual consistency UX. Sync when user waits for answer now. Be honest in architecture docs about semantic dependencies.

#### Production example
Billing consumes `OrderPlaced` asynchronously — temporal decoupling. Billing team reads AsyncAPI catalog and runs Pact — acknowledges logical coupling to Order's public contract. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Architecture slides showing zero arrows between boxes. No lag SLO → product surprised by stale UI. Sync REST fallback on every thin event — reintroduces temporal coupling.

#### Interview follow-ups (with model answers)

**Q:** Is choreography more or less logically coupled than orchestration?
**A:** For «Temporal coupling vs logical coupling»: Is choreography more or less logically coupled than orchestration. In production, Billing consumes `OrderPlaced` asynchronously — temporal decoupling. Billing team reads AsyncAPI catalog and runs Pact — acknowledges logical coupling to Order's public contract. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you document semantic dependencies?
**A:** The follow-on risk of «How do you document semantic dependencies» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Failure modes when logical contract breaks?
**A:** Trade-off framing for «Failure modes when logical contract breaks»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Temporal coupling vs logical coupling.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Billing consumes `OrderPlaced` asynchronously — temporal decoupling.. I suspect architecture slides showing zero arrows between boxes until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 18. UI and eventual consistency.

**Short answer:** Users expect feedback immediately; distributed writes commit asynchronously. Use optimistic UI, pending states, polling or WebSockets, and read-your-writes patterns — never show "Paid" until the payment fact exists in a model the UI reads. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Product-facing design for systems where write model and read projections diverge by seconds or more — the UX layer of eventual consistency. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
After submit: UI shows `Payment processing…` with correlation ID. Options: (1) read from write model API on redirect for read-your-writes; (2) poll projection until status catches up; (3) WebSocket push on `PaymentCaptured` event to UI gateway; (4) optimistic update with rollback on failure event. Don't cache stale projection without TTL indicator.

#### When to use / when NOT to use
Optimistic UI for low-risk actions (likes, cart). Strict confirmation for money and legal consent. Define max staleness with product — "search index 5s behind" on the settings page.

#### Production example
Checkout returns `202 Accepted` + `orderId`; UI polls `GET /orders/{id}` on write API until `CONFIRMED`, then switches to search-powered list knowing ES lags 3s — badge "Updating…" Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Showing success on HTTP 200 from command API before saga completes. No pending state → user double-clicks pay. Hiding lag until support tickets arrive.

#### Interview follow-ups (with model answers)

**Q:** Read-your-writes without hitting write DB on every read?
**A:** For «UI and eventual consistency»: Read-your-writes without hitting write DB on every read. In production, Checkout returns `202 Accepted` + `orderId`; UI polls `GET /orders/{id}` on write API until `CONFIRMED`, then switches to search-powered list knowing ES lags 3s — badge "Updating…" Teams that skip load testing and failur… I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do WebSockets fit CQRS?
**A:** The follow-on risk of «How do WebSockets fit CQRS» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What SLO do you promise end users?
**A:** Trade-off framing for «What SLO do you promise end users»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on UI and eventual consistency.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Checkout returns `202 Accepted` + `orderId`; UI polls `GET /orders/{id}` on write API until `CONFIRMED`, then switches to search-powered list knowing ES lags 3s…. I suspect showing success on http 200 from command api before saga completes until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 19. Exactly-once processing illusion.

**Short answer:** True exactly-once end-to-end across Kafka and Oracle doesn't exist as a magic flag. Achieve **effectively-once** semantics: idempotent consumers plus inbox, outbox for publish, and Kafka EOS for consume-transform-produce within the broker. Explain both layers — interviewers test whether you know the boundary. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
The gap between marketing terminology and distributed systems reality — critical for senior credibility. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka EOS: transactional producer + `read_committed` consumer isolates aborted batches within the log. External DB: separate transaction boundary — dual-write returns. Effectively-once recipe: store `event_id` and projection in one DB TX, then commit consumer offset in same TX (or store offset in DB). Duplicate delivery → unique constraint no-op.

#### When to use / when NOT to use
Kafka transactions for stream processing without external side effects, or with idempotent sink. Inbox/outbox for DB-backed services. Don't enable EOS globally without understanding `transactional.id` fencing and performance cost.

#### Production example
Consumer receives event → BEGIN TX → upsert projection + insert inbox → COMMIT → sync commit offset stored in `consumer_offsets` table not Kafka auto-commit. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
"enable.idempotence=true fixes double charge." Assuming `@Transactional` spans Kafka and JDBC. Offset commit before DB write — message loss.

#### Interview follow-ups (with model answers)

**Q:** Kafka EOS vs DB inbox — when each?
**A:** For «Exactly-once processing illusion»: Kafka EOS vs DB inbox — when each. In production, Consumer receives event → BEGIN TX → upsert projection + insert inbox → COMMIT → sync commit offset stored in `consumer_offsets` table not Kafka auto-commit. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Performance impact of transactional producer?
**A:** The follow-on risk of «Performance impact of transactional producer» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is read_committed?
**A:** Trade-off framing for «What is read_committed»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Exactly-once processing illusion.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Consumer receives event → BEGIN TX → upsert projection + insert inbox → COMMIT → sync commit offset stored in `consumer_offsets` table not Kafka auto-commit.. I suspect "enable until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 20. Dead letters and replay.

**Short answer:** Failed messages go to a dead-letter topic (DLT) after bounded retries. Replay from offset or time window must be idempotent — replays re-trigger side effects like emails unless handlers are classified replay-safe or guarded by dedup flags. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Operational recovery path when poison messages, transient bugs, or downstream outages block processing. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Spring Kafka `DefaultErrorHandler` + `DeadLetterPublishingRecoverer` after N failures. DLT retains original headers + stack trace. Replay: reset offsets or dedicated reprocessor consumer reading DLT. Classify handlers: **replay-safe** (idempotent projection) vs **not** (send email — check `notification_sent_at` before send).

#### When to use / when NOT to use
DLT for poison and unexpected exceptions. Business rejections (`PaymentDeclined`) are normal events, not DLT. Replay after fix deploy — never blind replay DLT to prod without idempotency audit.

#### Production example
Inventory consumer DLT `inventory.orders.dlt`; ops dashboard shows lag; after bugfix v2.3.1, reprocessor reads DLT with `replay=true` header skipping email handler branch.

#### Common mistakes
Infinite retry blocking partition ordering. Replay sends 10,000 duplicate emails. No alert on DLT rate spike.

#### Interview follow-ups (with model answers)

**Q:** DLT vs retry topic vs blocking retry?
**A:** For «Dead letters and replay»: DLT vs retry topic vs blocking retry. In production, Inventory consumer DLT `inventory.orders.dlt`; ops dashboard shows lag; after bugfix v2.3.1, reprocessor reads DLT with `replay=true` header skipping email handler branch. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Who approves production replay?
**A:** The follow-on risk of «Who approves production replay» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How do you test replay idempotency?
**A:** Trade-off framing for «How do you test replay idempotency»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Dead letters and replay.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Inventory consumer DLT `inventory.orders.dlt`; ops dashboard shows lag; after bugfix v2.3.. I suspect infinite retry blocking partition ordering until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 21. Event storming (workshop).

**Short answer:** Event storming is a collaborative workshop mapping domain events, commands, aggregates, policies, and actors on sticky notes. Senior value is facilitating bounded context conversations and discovering hidden policies — not drawing Kafka topology on a whiteboard. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
A Domain-Driven Design facilitation technique (Alberto Brandolini) that aligns business and engineering on language and flows before choosing brokers or schemas. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Orange stickies: domain events chronologically. Blue: commands. Yellow: aggregates. Lilac: policies ("whenever X then Y"). Identify bounded contexts, hot spots, and external systems. Output: event catalog draft, saga boundaries, and integration points — inputs to outbox design and CQRS splits.

#### When to use / when NOT to use
Kickoff for new domain or strangler migration. Skip for trivial CRUD with one team — workshop overhead isn't justified. Remote: Miro with timeboxed sessions.

#### Production example
Checkout workshop surfaces that "PaymentAuthorized" and "PaymentCaptured" are different contexts — leads to two integration events and explicit saga orchestrator instead of one fat `PaymentDone`. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Jumping to topic names before domain events agreed. No product owner in room — wrong language. Workshop output never becomes AsyncAPI catalog.

#### Interview follow-ups (with model answers)

**Q:** How does event storming relate to bounded contexts?
**A:** For «Event storming (workshop)»: How does event storming relate to bounded contexts. In production, Checkout workshop surfaces that "PaymentAuthorized" and "PaymentCaptured" are different contexts — leads to two integration events and explicit saga orchestrator instead of one fat `PaymentDone`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Difference from process modeling in BPMN?
**A:** The follow-on risk of «Difference from process modeling in BPMN» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How do you prioritize which saga to build first?
**A:** Trade-off framing for «How do you prioritize which saga to build first»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Event storming (workshop).

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Checkout workshop surfaces that "PaymentAuthorized" and "PaymentCaptured" are different contexts — leads to two integration events and explicit saga orchestrato…. I suspect jumping to topic names before domain events agreed until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 22. Policy: "whenever X then Y".

**Short answer:** A policy is an explicit reaction rule — when event X occurs, perform action Y. In EDA it becomes a consumer with a documented name, owner, and idempotency story — not a hidden `@KafkaListener` buried in a utils package. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The bridge between event storming lilac stickies and runnable code — often the source of choreography coupling if undocumented. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Policy `WheneverOrderPlacedThenReserveInventory`: consumer group `inventory-order-placed-policy`, subscribes to `OrderPlaced`, emits command or internal event. Document in event catalog: trigger, action, compensation, SLO. Multiple policies on same event compose — order of execution undefined unless orchestrated.

#### When to use / when NOT to use
Explicit policies for each side effect team owns. Consolidate into orchestrator when policies need strict ordering or shared timeout. Avoid god-listener that switches on 40 event types.

#### Production example
AsyncAPI `x-policy` extension documents policy; CODEOWNERS file maps policy package to Inventory team; integration test: given `OrderPlaced`, expect `InventoryReserved` within 5s. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Policy logic copy-pasted across services. Two policies compensating inconsistently on failure. No owner — orphaned listener after reorg.

#### Interview follow-ups (with model answers)

**Q:** Policy vs saga step?
**A:** For «Policy: "whenever X then Y"»: Policy vs saga step. In production, AsyncAPI `x-policy` extension documents policy; CODEOWNERS file maps policy package to Inventory team; integration test: given `OrderPlaced`, expect `InventoryReserved` within 5s. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do conflicting policies on same event resolve?
**A:** The follow-on risk of «How do conflicting policies on same event resolve» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Testing policies in isolation?
**A:** Trade-off framing for «Testing policies in isolation»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Policy: "whenever X then Y".

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: AsyncAPI `x-policy` extension documents policy; CODEOWNERS file maps policy package to Inventory team; integration test: given `OrderPlaced`, expect `InventoryR…. I suspect policy logic copy-pasted across services until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 23. Correlation and causation ids.

**Short answer:** Correlation ID tracks the entire business transaction or saga across services; causation ID identifies the specific event or command that directly caused this message. Propagate both in every envelope and persist on saga state for support and distributed tracing. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Metadata standards that make eventual consistency debuggable — without them, replaying a failed checkout in logs is guesswork. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
HTTP request generates `correlationId` (UUID); first command carries it; each emitted event copies same `correlationId` and sets `causationId` to prior event ID. OpenTelemetry traceId may align but business correlation survives across async boundaries. Saga record indexes by `correlationId` for ops UI.

#### When to use / when NOT to use
Always on integration events and public APIs. Optional for internal debug metrics. Store in MDC logging context in every handler.

#### Production example
Checkout `correlationId=abc-123` from browser header through Order outbox, Payment consumer, email service — Grafana Loki query `{correlationId="abc-123"}` shows full path. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
New UUID per event — breaks trace. Dropping headers on DLT replay. Correlation ID only in HTTP, not Kafka headers.

#### Interview follow-ups (with model answers)

**Q:** Difference from OpenTelemetry trace ID?
**A:** For «Correlation and causation ids»: Difference from OpenTelemetry trace ID. In production, Checkout `correlationId=abc-123` from browser header through Order outbox, Payment consumer, email service — Grafana Loki query `{correlationId="abc-123"}` shows full path. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Where is correlation stored in outbox payload vs headers?
**A:** The follow-on risk of «Where is correlation stored in outbox payload vs headers» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Causation chains for audit?
**A:** Trade-off framing for «Causation chains for audit»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Correlation and causation ids.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Checkout `correlationId=abc-123` from browser header through Order outbox, Payment consumer, email service — Grafana Loki query `{correlationId="abc-123"}` show…. I suspect new uuid per event — breaks trace until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```json
{
  "correlationId": "abc-123",
  "causationId": "evt-order-placed-456",
  "type": "PaymentCaptured",
  "payload": { }
}
```

---

### 24. Synchronous REST inside an event flow.

**Short answer:** Calling REST mid-handler to hydrate thin events reintroduces temporal coupling and availability risk — the Inventory service can't process orders when Order API is down. Prefer ECST fat enough payloads or maintain a local read model synced by events; reserve sync calls for true gaps with circuit breakers and fallbacks. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The anti-pattern of "event-driven on the outside, request-driven on the inside" — common when teams start with thin events. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Handler receives `OrderPlaced(orderId)` → `restTemplate.getForObject("/orders/"+id)` → process. Failure modes: timeout blocks consumer partition, retry amplifies load on struggling API, cascading failure. Mitigations: cache with event-driven invalidation, bulkhead thread pool, circuit breaker, or redesign event payload.

#### When to use / when NOT to use
Acceptable for rare enrichment non-critical to path (marketing segment). Unacceptable on hot path payment/inventory without fallback. Saga orchestrator synchronous command/response is intentional coupling — document SLAs.

#### Production example
Replace GET with `OrderPlaced` ECST; maintain `order_cache` table updated by same topic — handler reads local SQL only. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
N+1 REST from batch consumer. No timeout on enrichment call → `max.poll.interval` exceeded. Circular sync calls between two event-driven services.

#### Interview follow-ups (with model answers)

**Q:** Circuit breaker settings in Kafka consumer thread?
**A:** For «Synchronous REST inside an event flow»: Circuit breaker settings in Kafka consumer thread. In production, Replace GET with `OrderPlaced` ECST; maintain `order_cache` table updated by same topic — handler reads local SQL only. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Cache invalidation via events?
**A:** The follow-on risk of «Cache invalidation via events» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is orchestrator REST acceptable?
**A:** Trade-off framing for «When is orchestrator REST acceptable»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Synchronous REST inside an event flow.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Replace GET with `OrderPlaced` ECST; maintain `order_cache` table updated by same topic — handler reads local SQL only.. I suspect n+1 rest from batch consumer until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 25. Event clocks.

**Short answer:** Distinguish event time (when the business fact occurred), ingestion time (broker append), and processing time (consumer handled). Sort and expire business rules by event time; never reorder business logic by `consumedAt` — clock skew across producers breaks it. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Temporal semantics in distributed logs — especially important for windows, SLA timers, and audit. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer sets `occurredAt` from business context (order placed at register). Broker adds `timestamp` on append. Consumer records `processedAt`. Stream joins (Kafka Streams) should use `TimestampExtractor` on event time with allowed lateness for out-of-order arrivals. Scheduled sagas use workflow engine clocks, not consumer wall clock alone.

#### When to use / when NOT to use
Event time for fraud rules ("payment within 5 minutes of order"). Processing time for ops metrics only. NTP sync on producers; document timezone (always UTC in payloads).

#### Production example
`PaymentCaptured.occurredAt` drives refund eligibility; Kafka broker timestamp used only for lag monitoring dashboard. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Sorting audit log by consume time. Mixing `Instant.now()` at consume with producer timestamps in same comparison. No allowed lateness in windowed aggregations.

#### Interview follow-ups (with model answers)

**Q:** Watermarks in Kafka Streams?
**A:** For «Event clocks»: Watermarks in Kafka Streams. In production, `PaymentCaptured.occurredAt` drives refund eligibility; Kafka broker timestamp used only for lag monitoring dashboard. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do sagas implement timeouts with event time?
**A:** The follow-on risk of «How do sagas implement timeouts with event time» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cross-region clock skew?
**A:** Trade-off framing for «Cross-region clock skew»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Event clocks.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `PaymentCaptured.occurredAt` drives refund eligibility; Kafka broker timestamp used only for lag monitoring dashboard.. I suspect sorting audit log by consume time until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 26. Snapshot + events.

**Short answer:** Event sourcing rebuilds state by replaying all events — slow for aggregates with thousands of mutations. Periodic snapshots capture state at version N; replay loads snapshot then applies events after N. Version snapshot schema independently from events. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Performance optimization for event-sourced aggregates and long-retention projections — not required for simple outbox + relational SoT systems. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Every 100 events, persist snapshot `{aggregateId, version, state blob}`. On load: fetch latest snapshot, apply events with version > snapshot.version. Snapshot store (S3, table) separate from event log. Migration: upcast snapshot format or rebuild from events when schema changes.

#### When to use / when NOT to use
Snapshots when replay exceeds SLA (seconds to rebuild). Skip for integration-event-only architectures without event store. CQRS read models use DB tables as implicit "snapshots" maintained incrementally.

#### Production example
Order aggregate event store in Kafka compacted topic; snapshot every 50 events in Postgres; rebuild pod loads snapshot + tails compacted topic from offset. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
No snapshot version — incompatible blob after deploy. Snapshot without events retention — can't rebuild after snapshot corrupt. Confusing Kafka compaction with snapshot.

#### Interview follow-ups (with model answers)

**Q:** Who triggers snapshot — aggregate or background job?
**A:** For «Snapshot + events»: Who triggers snapshot — aggregate or background job. In production, Order aggregate event store in Kafka compacted topic; snapshot every 50 events in Postgres; rebuild pod loads snapshot + tails compacted topic from offset. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Snapshot frequency trade-offs?
**A:** The follow-on risk of «Snapshot frequency trade-offs» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Event sourcing without snapshots — when OK?
**A:** Trade-off framing for «Event sourcing without snapshots — when OK»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Snapshot + events.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order aggregate event store in Kafka compacted topic; snapshot every 50 events in Postgres; rebuild pod loads snapshot + tails compacted topic from offset.. I suspect no snapshot version — incompatible blob after deploy until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 27. GDPR delete in EDA.

**Short answer:** Deleting a row in SQL doesn't erase copies on Kafka, S3 archives, Elasticsearch, or consumer projections. GDPR requires a strategy: tombstone events, crypto-shred encrypted fields, topic rewrite (expensive), or retention bounded so data ages out — legal hold may override erasure. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Right-to-be-forgotten in systems where events fan out immutably — the dark side of fat events and long retention. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Propagation: publish `CustomerDeleted` or compacted tombstone on `customerId` key. Each consumer purges projection rows. For encrypted PII, destroy DEK — ciphertext becomes useless. Topic rewrite: copy topic excluding key — downtime and cost. Document what can't be erased (invoice legal retention).

#### When to use / when NOT to use
Tombstone + compacted topics for reference data keyed by customer. Crypto-shred when PII must have been in payload historically. Minimize PII at source — best GDPR strategy.

#### Production example
`CustomerErasureRequested` saga: SQL anonymize, tombstone Kafka keys, ES delete-by-query, shred KMS key for email field, audit log retained pseudonymized. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
DELETE in one DB only. Replay old events resurrecting PII into projection without erasure handler. No legal hold process.

#### Interview follow-ups (with model answers)

**Q:** Tombstone vs delete marker event?
**A:** For «GDPR delete in EDA»: Tombstone vs delete marker event. In production, `CustomerErasureRequested` saga: SQL anonymize, tombstone Kafka keys, ES delete-by-query, shred KMS key for email field, audit log retained pseudonymized. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Compacted topic still has data in segments until compaction?
**A:** The follow-on risk of «Compacted topic still has data in segments until compaction» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cross-border replication erasure?
**A:** Trade-off framing for «Cross-border replication erasure»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on GDPR delete in EDA.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `CustomerErasureRequested` saga: SQL anonymize, tombstone Kafka keys, ES delete-by-query, shred KMS key for email field, audit log retained pseudonymized.. I suspect delete in one db only until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 28. Testing event flows.

**Short answer:** Test behavior given event sequences, not just unit-test handler methods in isolation. Use contract tests on schemas, given-when-then integration tests with embedded Kafka or Testcontainers, virtual clocks for timeouts, and verify idempotency by delivering the same event twice. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Quality strategy for asynchronous, eventually consistent systems — where failures appear only under redelivery or reordering. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Unit: handler with mocked deps. Integration: `@EmbeddedKafka` or Testcontainers, publish to topic, await projection row with Awaitility. Contract: Pact or schema compatibility in CI. Saga: simulate failure after step 2, assert compensation event. Chaos: kill consumer mid-TX, verify inbox dedup on restart.

#### When to use / when NOT to use
Contract tests mandatory for public events. E2E few golden paths. Don't mock Kafka in every test — at least one path hits real broker semantics.

#### Production example
`OrderPlacedIntegrationTest`: insert outbox, run relay, assert Inventory inbox row; publish duplicate, assert single reservation. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Testing happy path only. No assertion on ordering/version behavior. Flaky tests with `Thread.sleep` instead of Awaitility.

#### Interview follow-ups (with model answers)

**Q:** Testcontainers vs EmbeddedKafka trade-offs?
**A:** For «Testing event flows»: Testcontainers vs EmbeddedKafka trade-offs. In production, `OrderPlacedIntegrationTest`: insert outbox, run relay, assert Inventory inbox row; publish duplicate, assert single reservation. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you test DLT and replay?
**A:** The follow-on risk of «How do you test DLT and replay» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Consumer-driven contracts for events?
**A:** Trade-off framing for «Consumer-driven contracts for events»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Testing event flows.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `OrderPlacedIntegrationTest`: insert outbox, run relay, assert Inventory inbox row; publish duplicate, assert single reservation.. I suspect testing happy path only until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 29. Observability.

**Short answer:** Monitor event type rates, consumer lag (records and time), handler latency, DLT rate, saga age for stuck workflows, and end-to-end traces from produce to consume. Alert on lag SLO breach and DLT spikes — not only on consumer up/down. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Operations visibility for systems where failure is silent staleness rather than HTTP 500. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Metrics: `kafka.consumer.lag`, handler timer per `event.type`, outbox unpublished count, saga `state=PENDING` age histogram. Tracing: inject trace context in outbox relay and Kafka headers; span links across async gap. Logs: structured with `correlationId`, `eventId`, `partition`, `offset`. Dashboards per consumer group and projection freshness.

#### When to use / when NOT to use
Lag alert on business-critical projections (inventory, payment). Synthetic probe events in canary. Don't rely on broker JMX alone — business SLO on projection age.

#### Production example
Datadog monitor: `order_search_lag_seconds > 300` pages OnCall; runbook links to reset consumer or scale pods; Grafana saga panel shows checkout stuck > 15m. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Alert only on pod restarts. No correlation between trace and business ID. Missing outbox backlog metric — silent publish failure.

#### Interview follow-ups (with model answers)

**Q:** Lag vs time-based SLO?
**A:** For «Observability»: Lag vs time-based SLO. In production, Datadog monitor: `order_search_lag_seconds > 300` pages OnCall; runbook links to reset consumer or scale pods; Grafana saga panel shows checkout stuck > 15m. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you trace across outbox relay delay?
**A:** The follow-on risk of «How do you trace across outbox relay delay» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Golden signals for EDA?
**A:** Trade-off framing for «Golden signals for EDA»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Observability.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Datadog monitor: `order_search_lag_seconds > 300` pages OnCall; runbook links to reset consumer or scale pods; Grafana saga panel shows checkout stuck > 15m.. I suspect alert only on pod restarts until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 30. Backpressure.

**Short answer:** When consumers can't keep up, lag grows — that's backpressure signal. Pause consumption, scale consumers (up to partition count), optimize handler, or fix downstream DB — don't buffer unbounded in JVM memory queues pretending the problem isn't real. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Flow control in pipeline systems where producers don't automatically slow down when consumers struggle. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka: consumer lag increases; broker retains per policy — disk full risk. `consumer.pause()` on partition while batching writes. Reactive streams backpressure doesn't apply naively to Kafka poll loop — you control via `max.poll.records` and processing rate. Outbox relay should throttle if broker or consumer lag exceeds threshold.

#### When to use / when NOT to use
Scale consumers first if partitions allow. Pause and retry when downstream Oracle is in recovery. Never unbounded `LinkedBlockingQueue` between poll and worker without drop policy.

#### Production example
Lag > 100k triggers HPA on consumer deployment (max = partition count 12); handler batch INSERT 500 rows; DB connection pool sized to avoid thundering herd. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Increasing `fetch.max.bytes` without faster processing — OOM. Auto-commit with huge batches — massive redelivery on crash. Ignoring hot partition — scaling pods doesn't help.

#### Interview follow-ups (with model answers)

**Q:** Pause vs reduce max.poll.records?
**A:** For «Backpressure»: Pause vs reduce max.poll.records. In production, Lag > 100k triggers HPA on consumer deployment (max = partition count 12); handler batch INSERT 500 rows; DB connection pool sized to avoid thundering herd. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Backpressure upstream to outbox relay?
**A:** The follow-on risk of «Backpressure upstream to outbox relay» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When to reject load at API vs queue?
**A:** Trade-off framing for «When to reject load at API vs queue»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Backpressure.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Lag > 100k triggers HPA on consumer deployment (max = partition count 12); handler batch INSERT 500 rows; DB connection pool sized to avoid thundering herd.. I suspect increasing `fetch until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 31. Fan-out vs multicast.

**Short answer:** Fan-out in Kafka means multiple consumer groups each receive every message — true broadcast semantics. Multicast colloquially similar; the Kafka mechanism is independent consumer group progress per subscriber. One group scales horizontally; different groups don't compete for partitions. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Messaging pattern for one event driving many independent reactions — billing, inventory, analytics each at their own pace. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Topic `orders.events` with 12 partitions. Consumer group `inventory` and `billing` each maintain offset — both get all messages. Within `inventory`, 12 consumers max (one per partition). Adding group `analytics` doesn't steal messages from `inventory`.

#### When to use / when NOT to use
Separate groups per downstream domain. Don't create new group id per deployment for same logical consumer — that's the K8s bug (Q32). Rabbit fanout exchange analogous but different offset model.

#### Production example
`OrderPlaced` consumed by inventory-group, fraud-group, datawarehouse-group — three lag metrics, three SLOs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Same group name typo → duplicate processing or no processing. One mega-consumer doing unrelated policies — can't scale independently. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** Compare to RabbitMQ fanout?
**A:** For «Fan-out vs multicast»: Compare to RabbitMQ fanout. In production, `OrderPlaced` consumed by inventory-group, fraud-group, datawarehouse-group — three lag metrics, three SLOs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Partition count vs fan-out groups?
**A:** The follow-on risk of «Partition count vs fan-out groups» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cost of duplicate storage for many groups?
**A:** Trade-off framing for «Cost of duplicate storage for many groups»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Fan-out vs multicast.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `OrderPlaced` consumed by inventory-group, fraud-group, datawarehouse-group — three lag metrics, three SLOs.. I suspect same group name typo → duplicate processing or no processing until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 32. Unique group id bug in Kubernetes.

**Short answer:** Setting `group-id: ${HOSTNAME}` or random UUID per pod makes every restart a new consumer group. With `auto.offset.reset=latest`, new groups skip backlog; with `earliest`, they reprocess everything — both are production incidents. Use stable group IDs per logical consumer. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
A classic Kubernetes + Kafka misconfiguration that breaks EDA ordering, idempotency assumptions, and lag monitoring. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Consumer group membership is keyed by `group.id`. New group has no committed offset → `auto.offset.reset` applies. StatefulSet with stable hostname still wrong if pod name used intentionally for "unique" scaling. Correct: `group-id: inventory-order-placed` constant in config map; scale pods sharing same group.

#### When to use / when NOT to use
Stable group for normal consumers. Unique groups only when you intentionally want independent full replay (rare reprocessing tool). Helm chart review checklist item.

#### Production example
Incident: deploy used `spring.kafka.consumer.group-id: order-consumer-${POD_NAME}` → 20 pods → 20 groups → lag metric 0 while messages pile up unread on `latest`.

#### Common mistakes
Copy-paste from tutorial using random group for "local dev" into prod chart. Blue/green deploy with different group id per color without offset migration. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** How do you reprocess with a new group safely?
**A:** For «Unique group id bug in Kubernetes»: How do you reprocess with a new group safely. In production, Incident: deploy used `spring.kafka.consumer.group-id: order-consumer-${POD_NAME}` → 20 pods → 20 groups → lag metric 0 while messages pile up unread on `latest`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Static membership and K8s?
**A:** The follow-on risk of «Static membership and K8s» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Offset reset policies explained?
**A:** Trade-off framing for «Offset reset policies explained»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Unique group id bug in Kubernetes.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Incident: deploy used `spring.kafka.consumer.group-id: order-consumer-${POD_NAME}` → 20 pods → 20 groups → lag metric 0 while messages pile up unread on `latest…. I suspect copy-paste from tutorial using random group for "local dev" into prod chart until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```yaml
spring:
  kafka:
    consumer:
      group-id: inventory-order-placed  # stable — NOT ${HOSTNAME}
      auto-offset-reset: earliest       # only for new groups — understand impact
```

---

### 33. Domain event vs integration event.

**Short answer:** Domain events are rich, model-internal facts meaningful inside a bounded context. Integration events are stable, translated contracts at the boundary — never publish Hibernate entities or table rows as public API. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Anti-corruption at the messaging edge — separates refactorable internals from promises to other teams. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Inside Order context: `OrderLineItemAdded` with full object graph. At boundary: mapper emits `OrderPlaced` integration event with DTO schema registered in Avro. Translation layer in same service (before outbox) or dedicated ACL service consuming CDC — latter still needs explicit mapping, not raw CDC as contract.

#### When to use / when NOT to use
Always translate before cross-team topics. Domain events can use in-process Spring `ApplicationEventPublisher`. Integration events versioned and cataloged. Same name different payload across contexts is OK inside boundaries, fatal on public bus.

#### Production example
`@DomainEventHandler` updates read model internally; `@Transactional` outbox writes `OrderPlacedIntegrationEvent` JSON mapped by `OrderEventMapper` — entity never serialized. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Publishing JPA entity JSON to Kafka. Using DB column names in event fields (`ORD_STAT_CD`). Leaking "temporary" flags other teams build on.

#### Interview follow-ups (with model answers)

**Q:** Where does translation happen — producer or intermediary?
**A:** For «Domain event vs integration event»: Where does translation happen — producer or intermediary. In production, `@DomainEventHandler` updates read model internally; `@Transactional` outbox writes `OrderPlacedIntegrationEvent` JSON mapped by `OrderEventMapper` — entity never serialized. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** CDC vs explicit integration event?
**A:** The follow-on risk of «CDC vs explicit integration event» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Bounded context map to event ownership?
**A:** Trade-off framing for «Bounded context map to event ownership»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Domain event vs integration event.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `@DomainEventHandler` updates read model internally; `@Transactional` outbox writes `OrderPlacedIntegrationEvent` JSON mapped by `OrderEventMapper` — entity nev…. I suspect publishing jpa entity json to kafka until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 34. Outbox polling vs CDC.

**Short answer:** Outbox polling is simple — a scheduled job queries unpublished rows and publishes — but adds latency and DB read load. CDC on the outbox table (Debezium) is near-real-time with ops complexity. Both beat dual-write; choice depends on team skills and lag SLO. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Two relay mechanisms for the same transactional outbox pattern — application poller vs log tailing infrastructure. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Polling: `@Scheduled` every 100ms, `FOR UPDATE SKIP LOCKED`, batch 100, publish, update `published_at`. Lag typically hundreds of ms to seconds. CDC: connector streams outbox inserts as change events, separate lightweight publisher or direct to public topic with transforms. Failure: poller stuck → growing outbox table alert; CDC → connector lag, schema migration coordination.

#### When to use / when NOT to use
Polling for MVP and low volume. CDC when sub-second publish SLO or many outbox tables. Don't CDC entire OLTP schema when outbox-only CDC suffices.

#### Production example
Phase 1: Spring `@Scheduled` outbox relay. Phase 2: Debezium on outbox only, poller disabled, `outbox_unpublished_gauge` still monitored. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Polling without index on `(published_at)` — full table scan. Two relays active — duplicate publish without idempotency. CDC without handling UPDATE on published_at.

#### Interview follow-ups (with model answers)

**Q:** SKIP LOCKED behavior on Oracle vs Postgres?
**A:** For «Outbox polling vs CDC»: SKIP LOCKED behavior on Oracle vs Postgres. In production, Phase 1: Spring `@Scheduled` outbox relay. Phase 2: Debezium on outbox only, poller disabled, `outbox_unpublished_gauge` still monitored. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Outbox row delete vs mark published?
**A:** The follow-on risk of «Outbox row delete vs mark published» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Exactly-once from relay to Kafka?
**A:** Trade-off framing for «Exactly-once from relay to Kafka»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Outbox polling vs CDC.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Phase 1: Spring `@Scheduled` outbox relay. Phase 2: Debezium on outbox only, poller disabled, `outbox_unpublished_gauge` still monitored.. I suspect polling without index on `(published_at)` — full table scan until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 35. Transactional messaging and Spring.

**Short answer:** Spring `@TransactionalEventListener(phase = AFTER_COMMIT)` fires only after DB commit — but if the JVM crashes after commit and before the listener runs, the event is lost forever. That is not an outbox. Say this explicitly in interviews; use outbox for guaranteed publication. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Common Spring misconception equating transactional event listeners with reliable messaging. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
AFTER_COMMIT listener runs in a new thread after TX commit — not in the same TX as outbox. Crash window between commit and listener execution. BEFORE_COMMIT in same TX still isn't broker delivery — only coordinates in-process handlers. `KafkaTemplate.send` in listener is separate TX from JDBC — dual-write. Correct: outbox insert in `@Transactional` business method.

#### When to use / when NOT to use
AFTER_COMMIT for local side effects: cache eviction, metrics, non-critical email. Outbox for integration events other services depend on. `ApplicationEventPublisher` for in-monolith modularization only.

#### Production example
Order service: outbox for `OrderPlaced`; AFTER_COMMIT listener triggers in-process read model refresh in same service — acceptable loss on crash with rebuild from events. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
"We use `@TransactionalEventListener` so it's transactional with Kafka." ChainedTransactionManager fantasies. Critical payment notification only via listener.

#### Interview follow-ups (with model answers)

**Q:** Difference AFTER_COMMIT vs AFTER_COMPLETION?
**A:** For «Transactional messaging and Spring»: Difference AFTER_COMMIT vs AFTER_COMPLETION. In production, Order service: outbox for `OrderPlaced`; AFTER_COMMIT listener triggers in-process read model refresh in same service — acceptable loss on crash with rebuild from events. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does outbox interact with Spring `@Transactional`?
**A:** The follow-on risk of «How does outbox interact with Spring `@Transactional`» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Can you combine outbox + listener?
**A:** Trade-off framing for «Can you combine outbox + listener»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Transactional messaging and Spring.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order service: outbox for `OrderPlaced`; AFTER_COMMIT listener triggers in-process read model refresh in same service — acceptable loss on crash with rebuild fr…. I suspect "we use `@transactionaleventlistener` so it's transactional with kafka until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
// NOT sufficient for cross-service guarantees
@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
void onOrderPlaced(OrderPlaced event) { kafka.send(...); } // crash window

// Correct: outbox row in same @Transactional as save()
```

---

### 36. Sagas that never finish.

**Short answer:** Distributed sagas stall without timeouts, missing compensation paths, or lost events — leaving orders "pending payment" forever. Production requires saga state persistence, deadline timers, dead-letter sagas, human ops console, and alerts on saga age — compensations must be idempotent and tested. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The operational failure mode of long-running choreography/orchestration without lifecycle management. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Saga instance tracks steps completed. Missing `PaymentCaptured` after `OrderPlaced` — timeout fires `CancelOrder` compensation or escalates to ops. Stuck reasons: consumer lag, poison message, orchestrator bug, missing event version. Workflow engines (Temporal) encode timers natively; homemade needs `scheduled_at` column + sweeper job.

#### When to use / when NOT to use
Always define max saga duration with product. Human-in-loop for exception paths. Don't start saga without compensation design for each forward step.

#### Production example
Checkout saga timeout 30m → `SagaTimedOut` → release inventory, void auth; ops UI lists sagas `age > 1h`; Temporal workflow `Workflow.await(Duration.ofMinutes(30))`.

#### Common mistakes
Happy-path-only saga code. Compensation throws → money captured, inventory held. No idempotency on compensate → double refund.

#### Interview follow-ups (with model answers)

**Q:** Choreography timeout without central orchestrator?
**A:** For «Sagas that never finish»: Choreography timeout without central orchestrator. In production, Checkout saga timeout 30m → `SagaTimedOut` → release inventory, void auth; ops UI lists sagas `age > 1h`; Temporal workflow `Workflow.await(Duration.ofMinutes(30))`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Poison message mid-saga?
**A:** The follow-on risk of «Poison message mid-saga» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Temporal vs DB saga table?
**A:** Trade-off framing for «Temporal vs DB saga table»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Sagas that never finish.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Checkout saga timeout 30m → `SagaTimedOut` → release inventory, void auth; ops UI lists sagas `age > 1h`; Temporal workflow `Workflow.await(Duration.. I suspect happy-path-only saga code until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 37. Inbox pattern.

**Short answer:** The inbox records processed message IDs (and optionally payload hash) in the same database transaction as the business side effect — consumer dedup paired with outbox on the publish side. Together they deliver effectively-once processing across at-least-once brokers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Consumer-side mirror of the outbox pattern — idempotency anchor in the datastore that matters. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Receive event → BEGIN TX → INSERT inbox `event_id` (unique) → apply business logic → COMMIT → commit Kafka offset (stored in DB or after TX with care). Duplicate delivery hits unique violation → skip logic, still ack. Payload hash detects replay attacks or corrupted duplicates.

#### When to use / when NOT to use
Mandatory for payment, inventory, notification dedup. Can combine with natural idempotency (`UPSERT` on business key). Store offset in same TX for projection consumers.

#### Production example
Payment service `processed_events` table; handler wrapped in `@Transactional`; Micrometer counter `inbox.duplicate.skipped`.

#### Common mistakes
Inbox insert after external HTTP call — partial failure inconsistency. Pruning inbox IDs too aggressively — replay after retention reprocesses. Separate TX for inbox and business update.

#### Interview follow-ups (with model answers)

**Q:** Inbox vs Kafka EOS?
**A:** For «Inbox pattern»: Inbox vs Kafka EOS. In production, Payment service `processed_events` table; handler wrapped in `@Transactional`; Micrometer counter `inbox.duplicate.skipped`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Retention period for processed IDs?
**A:** The follow-on risk of «Retention period for processed IDs» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Inbox with CDC consumers?
**A:** Trade-off framing for «Inbox with CDC consumers»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Inbox pattern.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment service `processed_events` table; handler wrapped in `@Transactional`; Micrometer counter `inbox.duplicate.skipped`.. I suspect inbox insert after external http call — partial failure inconsistency until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```sql
BEGIN;
INSERT INTO processed_events (event_id) VALUES (:id); -- unique
UPDATE accounts SET balance = balance - :amt WHERE id = :acct;
COMMIT;
```

---

### 38. Event-driven ≠ no API.

**Short answer:** Healthy EDA is hybrid: HTTP/gRPC for commands users trigger now and queries that need immediate answers; events for facts that propagate with eventual consistency. Claiming "no sync APIs" is architecture theater — the order form still POSTs. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Pragmatic architecture stance — messaging augments, rarely replaces, request-response for human-facing paths. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Command API accepts `PlaceOrder`, validates, writes DB + outbox. Query API serves read model or write model for read-your-writes. Events notify Inventory, Billing, Search indexer asynchronously. BFF may still aggregate sync calls for UI while domain integration stays event-driven.

#### When to use / when NOT to use
Sync for user authorization, validation errors, and read-your-writes immediately after submit. Async for fan-out side effects and peak absorption. Don't force event-only query for simple GET by ID if write model suffices.

#### Production example
POST `/orders` sync returns 202 + id; GET `/orders/{id}` sync on write DB; GET `/orders/search` async ES projection with staleness header `X-Lag-Seconds`. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Publishing command to Kafka from browser. No query API — UI polls topic. Sync chain of 8 services disguised as "microservices."

#### Interview follow-ups (with model answers)

**Q:** GraphQL BFF with event-backed read models?
**A:** For «Event-driven ≠ no API»: GraphQL BFF with event-backed read models. In production, POST `/orders` sync returns 202 + id; GET `/orders/{id}` sync on write DB; GET `/orders/search` async ES projection with staleness header `X-Lag-Seconds`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Webhooks vs events for external partners?
**A:** The follow-on risk of «Webhooks vs events for external partners» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** CQRS command bus over Kafka — when?
**A:** Trade-off framing for «CQRS command bus over Kafka — when»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Event-driven ≠ no API.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: POST `/orders` sync returns 202 + id; GET `/orders/{id}` sync on write DB; GET `/orders/search` async ES projection with staleness header `X-Lag-Seconds`.. I suspect publishing command to kafka from browser until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 39. Ordering across microservices.

**Short answer:** Global total order across independent services is impossible without a single sequencer bottleneck. Design workflows so each aggregate has local order (partition key) and sagas tolerate cross-service reordering via versioning and idempotency — don't wait for `PaymentBeforeShipping` globally. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Architectural constraint that drives saga design, key selection, and UX honesty about eventual consistency. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Service A and B write to different partitions — no shared order. Orchestrator can impose logical sequence by not sending step 2 until step 1 event received — that's workflow order, not broker order. Cross-service race: `Shipped` arrives before `Paid` — handler must defer or use saga gate.

#### When to use / when NOT to use
Per-aggregate keys for all events about same order ID. Orchestration when strict step order mandatory. Avoid distributed locks across services for ordering — fragile.

#### Production example
All order lifecycle events keyed `order-123`; Fulfillment waits for projection row `paymentStatus=CAPTURED` updated by Payment consumer — logical gate, not global Kafka order. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Single partition for whole topic — throughput ceiling. Assuming FIFO queue between two services without shared key. Debug by consumed order only.

#### Interview follow-ups (with model answers)

**Q:** Single sequencer anti-pattern?
**A:** For «Ordering across microservices»: Single sequencer anti-pattern. In production, All order lifecycle events keyed `order-123`; Fulfillment waits for projection row `paymentStatus=CAPTURED` updated by Payment consumer — logical gate, not global Kafka order. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How orchestrator imposes order without global log?
**A:** The follow-on risk of «How orchestrator imposes order without global log» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** FIFO SQS between two services — trade-offs?
**A:** Trade-off framing for «FIFO SQS between two services — trade-offs»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Ordering across microservices.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: All order lifecycle events keyed `order-123`; Fulfillment waits for projection row `paymentStatus=CAPTURED` updated by Payment consumer — logical gate, not glob…. I suspect single partition for whole topic — throughput ceiling until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 40. Materialized view lag SLO.

**Short answer:** Define measurable lag SLOs with product — e.g., "99% of search results reflect new orders within 5 seconds." Measure projection timestamp vs event `occurredAt`, display staleness where needed, and page OnCall when SLO breaks — not when consumer merely restarts. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
The business-facing contract for eventual consistency — bridges engineering metrics and UX expectations. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Metric: `lag = now() - projection.updated_at` or compare max event version applied vs source. SLO dashboard per projection. Product signs off on acceptable staleness for search vs inventory vs analytics. Autoscale consumer on lag; root-cause slow SQL not just add pods.

#### When to use / when NOT to use
Any user-visible async read path needs documented SLO. Internal analytics can lag hours — document separately. Don't promise strong consistency on projection without sync read fallback.

#### Production example
SLA doc: Order search ES index p99 lag < 5s; monitor `order_search_lag_seconds`; UI badge if lag > 10s from health endpoint. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
No product agreement — "real-time" means different things. Measuring broker lag only, not end-to-end projection age. Ignoring hot key lag on one partition.

#### Interview follow-ups (with model answers)

**Q:** Error budget for lag SLO?
**A:** For «Materialized view lag SLO»: Error budget for lag SLO. In production, SLA doc: Order search ES index p99 lag < 5s; monitor `order_search_lag_seconds`; UI badge if lag > 10s from health endpoint. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Read-your-writes bypass for checkout confirmation?
**A:** The follow-on risk of «Read-your-writes bypass for checkout confirmation» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How rebuild affects SLO?
**A:** Trade-off framing for «How rebuild affects SLO»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Materialized view lag SLO.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: SLA doc: Order search ES index p99 lag < 5s; monitor `order_search_lag_seconds`; UI badge if lag > 10s from health endpoint.. I suspect no product agreement — "real-time" means different things until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 41. Poison vs business reject.

**Short answer:** Poison messages fail technical processing — deserialization errors, NPE, schema mismatch — route to DLT after retries. Business rejections are valid domain outcomes — emit `PaymentDeclined` or `InventoryUnavailable` events and continue; never dump expected business "no" into DLT. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Error classification that keeps DLT signal-to-noise ratio usable and sagas completing correctly. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Poison: retry won't help without code/schema fix → DLT + alert. Business reject: handler publishes negative fact, saga compensates or alternate path — consumer commits offset normally. Gray area: downstream 503 — retry with backoff, then DLT if permanent.

#### When to use / when NOT to use
DLT for exceptional technical failure. Domain events for expected validation failures. Schema validation at producer prevents many poison pills.

#### Production example
Invalid Avro → DLT `orders.dlt` immediately after 0 retries with schema check. Insufficient stock → `InventoryRejected` event, Order saga triggers cancel — not DLT.

#### Common mistakes
Catch `BusinessException` and send to DLT. Infinite retry on poison blocking partition. Same handler for both without branching.

#### Interview follow-ups (with model answers)

**Q:** Retry count before DLT?
**A:** For «Poison vs business reject»: Retry count before DLT. In production, Invalid Avro → DLT `orders.dlt` immediately after 0 retries with schema check. Insufficient stock → `InventoryRejected` event, Order saga triggers cancel — not DLT. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Schema validation at gateway vs consumer?
**A:** The follow-on risk of «Schema validation at gateway vs consumer» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Business reject in saga compensation?
**A:** Trade-off framing for «Business reject in saga compensation»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Poison vs business reject.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Invalid Avro → DLT `orders.dlt` immediately after 0 retries with schema check.. I suspect catch `businessexception` and send to dlt until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 42. Schema-on-read vs on-write.

**Short answer:** Schema-on-write validates payload structure at publish time — registry, producer SDK, API gateway. Schema-on-read pushes tolerance to consumers — flexible but breaks silently. Prefer validate at produce with compatible evolution; consumers still defensively handle unknown fields. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Governance model for event contracts — where compatibility is enforced in the pipeline. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
On-write: Schema Registry rejects incompatible Avro; producer tests in CI. On-read: consumer parses JSON defensively — optional fields, defaults. Hybrid JSON: producer validates against JSON Schema in CI without registry. CDC often schema-on-read at consumer mapping layer — risky without generated models.

#### When to use / when NOT to use
On-write for multi-team Kafka. On-read only for exploratory internal topics with short retention. Never schema-on-read for financial events without contract tests equivalent to registry.

#### Production example
Producer PR fails CI if Avro not BACKWARD compatible; consumer uses generated SpecificRecord with unknown field ignore policy. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
"JSON is flexible" as excuse for breaking changes. Consumer strict parse rejects additive producer deploy. No CI compatibility step.

#### Interview follow-ups (with model answers)

**Q:** Proto vs Avro for on-write?
**A:** For «Schema-on-read vs on-write»: Proto vs Avro for on-write. In production, Producer PR fails CI if Avro not BACKWARD compatible; consumer uses generated SpecificRecord with unknown field ignore policy. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Debezium schema evolution?
**A:** The follow-on risk of «Debezium schema evolution» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Tolerant reader pattern?
**A:** Trade-off framing for «Tolerant reader pattern»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Schema-on-read vs on-write.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Producer PR fails CI if Avro not BACKWARD compatible; consumer uses generated SpecificRecord with unknown field ignore policy.. I suspect "json is flexible" as excuse for breaking changes until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 43. Event naming.

**Short answer:** Name events in past tense with ubiquitous language — `OrderPlaced`, not `PlaceOrder` or `OrderTableUpdated`. Version via type suffix (`OrderPlacedV2`) or envelope `schemaVersion`, not silent reuse. Integration names reflect business facts, not infrastructure. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Naming convention that makes logs, catalogs, and code readable across teams and prevents command/event confusion. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Pattern: `[Aggregate][PastTenseVerb]` or `OrderPlaced`. Avoid CRUD leakage: `OrderUpdated` too vague — prefer `OrderShippingAddressChanged`. Technical events prefixed or kept internal: `OutboxPublished` not on public bus. AsyncAPI `title` matches code constant. Namespace events by bounded context in topic names (`orders.OrderPlaced`) when multiple domains share a cluster — avoids collisions and clarifies ownership in logs and metrics.

#### When to use / when NOT to use
Strict naming for integration catalog. Looser internal domain events within repo. Rename = new event type + deprecation period, not rename in place.

#### Production example
Public topic events: `OrderPlaced`, `OrderCancelled`, `PaymentCaptured`. Internal: `OrderAggregatePersisted` never exported. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Imperative names. DB trigger names as events. One `EntityChanged` for everything — useless for consumers.

#### Interview follow-ups (with model answers)

**Q:** Granular vs coarse event names?
**A:** For «Event naming»: Granular vs coarse event names. In production, Public topic events: `OrderPlaced`, `OrderCancelled`, `PaymentCaptured`. Internal: `OrderAggregatePersisted` never exported. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Naming in event storming vs code?
**A:** The follow-on risk of «Naming in event storming vs code» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Deprecating badly named legacy events?
**A:** Trade-off framing for «Deprecating badly named legacy events»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Event naming.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Public topic events: `OrderPlaced`, `OrderCancelled`, `PaymentCaptured`. Internal: `OrderAggregatePersisted` never exported.. I suspect imperative names until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 44. When EDA is the wrong hammer.

**Short answer:** Skip heavy EDA for simple CRUD owned by one team, when you need immediate strong consistency everywhere, or when ops can't run brokers and monitors. A modular monolith with in-process events plus clear modules often beats premature Kafka. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Senior judgment — knowing when distributed eventual consistency costs exceed benefits. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
EDA shines: fan-out, peak buffering, cross-team integration, audit trail. Poor fit: single team admin panel, low volume, strong ACID across entities today, no SRE for Kafka lag. Alternative: modular monolith, direct calls, outbox only at true boundary.

#### When to use / when NOT to use
Not when "microservices mandate Kafka." Yes when bounded contexts independently deploy and UX accepts eventual read models. Strangler: monolith first, events at extracted seams.

#### Production example
Internal HR tool — stay monolith. Customer checkout across Payment/Inventory/Fraud — EDA + saga + outbox at boundaries extracted from monolith. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Kafka for 100 messages/day. Event sourcing entire company. EDA without idempotency story — guaranteed incident.

#### Interview follow-ups (with model answers)

**Q:** Modular monolith vs microservices events?
**A:** For «When EDA is the wrong hammer»: Modular monolith vs microservices events. In production, Internal HR tool — stay monolith. Customer checkout across Payment/Inventory/Fraud — EDA + saga + outbox at boundaries extracted from monolith. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When to introduce outbox in monolith?
**A:** The follow-on risk of «When to introduce outbox in monolith» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cost of operating Kafka for small team?
**A:** Trade-off framing for «Cost of operating Kafka for small team»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing When EDA is the wrong hammer.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Internal HR tool — stay monolith. Customer checkout across Payment/Inventory/Fraud — EDA + saga + outbox at boundaries extracted from monolith.. I suspect kafka for 100 messages/day until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 45. Workflow engines (Camunda, Temporal) vs homemade saga.

**Short answer:** Homemade saga tables work for 3-step flows with simple timeouts. Workflow engines add durable state, timers, visibility, and versioning — worth it at 15+ steps, human tasks, or complex compensation. Cost is platform learning and ops — not free magic. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Build vs buy for orchestrated sagas and long-running processes in event-driven systems. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Homemade: `saga_instance` table, state enum, cron sweeper for timeouts — you own persistence, retry, UI. Temporal: workflow code as state machine, history replay, automatic recovery. Camunda: BPMN model, external task pattern with Kafka. Engines survive process worker crashes; homemade must get idempotent step execution right.

#### When to use / when NOT to use
Temporal/Camunda when business asks "where is my order" and timers/compensation chains are complex. Homemade OK for MVP extract with 2 compensations. Don't build Camunda in a spreadsheet for 20-step loan origination.

#### Production example
Phase 1 homemade checkout saga in Postgres. Phase 3 migrate to Temporal — same events, activities call existing services, saga visibility for support. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Homemade without timeout sweeper. Engine for two-step flow — overkill. Workflow versioning ignored — deploy breaks in-flight sagas.

#### Interview follow-ups (with model answers)

**Q:** Temporal vs Camunda for Java shop?
**A:** For «Workflow engines (Camunda, Temporal) vs homemade saga»: Temporal vs Camunda for Java shop. In production, Phase 1 homemade checkout saga in Postgres. Phase 3 migrate to Temporal — same events, activities call existing services, saga visibility for support. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Event-driven vs orchestrator calling REST?
**A:** The follow-on risk of «Event-driven vs orchestrator calling REST» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How migrate in-flight homemade to engine?
**A:** Trade-off framing for «How migrate in-flight homemade to engine»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Workflow engines (Camunda, Temporal) vs .

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Phase 1 homemade checkout saga in Postgres. Phase 3 migrate to Temporal — same events, activities call existing services, saga visibility for support.. I suspect homemade without timeout sweeper until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 46. Kafka Streams as a projector.

**Short answer:** Kafka Streams excels at stream joins, windowed aggregations, and changelog state stores — good for real-time enrichment pipelines. For simple "event → SQL row" projections, a Spring Kafka consumer writing Postgres is often simpler ops-wise; Streams adds rebalance state restore complexity. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Stream processing framework choice for CQRS read-side and event-driven transformations. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
`KStream`/`KTable`, state stores backed by compacted changelog topics, repartition topics on join. Rebalance triggers state restore from changelog — lag spike on deploy. EOS supported within Streams app. JDBC sink often via separate consumer pattern or kafka-streams-jdbc extensions with idempotent upsert.

#### When to use / when NOT to use
Streams for joining `OrderPlaced` with `CustomerProfile` by key in flight. Simple projector: `@KafkaListener` + JDBC batch. Avoid Streams if team lacks ops experience and job is CRUD projection.

#### Production example
Fraud scoring: Streams joins payment stream with device fingerprint table, emits `RiskScored` — windows and joins justified. Order search indexer: Spring consumer → ES bulk API. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Streams app without monitoring restore time. Using Streams for one map operation. State store disk full on RocksDB.

#### Interview follow-ups (with model answers)

**Q:** KTable vs compacted topic?
**A:** For «Kafka Streams as a projector»: KTable vs compacted topic. In production, Fraud scoring: Streams joins payment stream with device fingerprint table, emits `RiskScored` — windows and joins justified. Order search indexer: Spring consumer → ES bulk API. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Rebalance impact on SLA?
**A:** The follow-on risk of «Rebalance impact on SLA» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Flink vs Kafka Streams?
**A:** Trade-off framing for «Flink vs Kafka Streams»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Kafka Streams as a projector.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Fraud scoring: Streams joins payment stream with device fingerprint table, emits `RiskScored` — windows and joins justified.. I suspect streams app without monitoring restore time until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 47. Exactly-once projection.

**Short answer:** Store the consumer offset in the same database transaction as the projection write — classic inbox pattern — so crash after DB commit never loses offset progress and duplicate delivery never double-applies. Kafka Streams EOS or offset-in-Postgres beats naive auto-commit. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
The projection-specific recipe for effectively-once read model updates under at-least-once delivery. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Pattern: BEGIN TX → upsert projection → insert `consumer_offsets(partition, offset)` or inbox event_id → COMMIT; then async Kafka commit or use Kafka's `sendOffsetsToTransaction` only within Streams topology. On restart, re-read from stored offset; duplicates hit unique constraint on event_id. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### When to use / when NOT to use
Mandatory for financial projections and inventory counts. Idempotent upsert sufficient for idempotent keys without offset table if business keys cover all duplicates — offset table still safer. Don't auto-commit before DB write.

#### Production example
Postgres table `projection_offsets` updated in same `@Transactional` as `order_read_model` upsert; listener manual ack after TX success. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Commit offset then crash before DB — lost event. Separate microservice for projection without TX boundary. Assuming ES is transactional with Kafka.

#### Interview follow-ups (with model answers)

**Q:** Offset storage vs inbox event_id?
**A:** For «Exactly-once projection»: Offset storage vs inbox event_id. In production, Postgres table `projection_offsets` updated in same `@Transactional` as `order_read_model` upsert; listener manual ack after TX success. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Kafka Connect JDBC exactly-once?
**A:** The follow-on risk of «Kafka Connect JDBC exactly-once» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Rebuild projection offset reset strategy?
**A:** Trade-off framing for «Rebuild projection offset reset strategy»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Exactly-once projection.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Postgres table `projection_offsets` updated in same `@Transactional` as `order_read_model` upsert; listener manual ack after TX success.. I suspect commit offset then crash before db — lost event until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```sql
BEGIN;
INSERT INTO order_read_model (...) VALUES (...);
INSERT INTO consumer_inbox (topic, partition, offset, event_id) VALUES (...);
COMMIT;
-- then commitSync() to broker
```

---

### 48. Multi-region EDA.

**Short answer:** Multi-region event replication introduces lag, ordering loss across regions, and active-active conflict resolution — usually harder than multi-region REST. Most enterprises run active-passive Kafka mirroring (MM2) with single writer region; active-active requires CRDTs, last-writer-wins with business rules, or region-scoped aggregates. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Geographic distribution strategy for event buses and projections — DR and latency vs consistency trade-offs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
MirrorMaker 2 replicates topics EU → US with offset mapping lag. Consumers in DR region idle until failover. Active-active: same customer written in two regions → conflicting events on replicated topic — need region id in key, conflict handler, or sticky routing. Outbox + CDC replicate; saga timeouts cross region clock skew.

#### When to use / when NOT to use
Active-passive for DR and regulatory data residency. Active-active only with explicit conflict model and product acceptance. Don't mirror all topics — cost and PII duplication.

#### Production example
Primary Kafka in `eu-west`; MM2 to `us-east` for read-only analytics; failover runbook promotes US consumers with accepted 30s RPO on events. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Active-active without conflict design. Replicating PII topics to non-compliant region. Failover with `auto.offset.reset=latest` on new groups — data loss.

#### Interview follow-ups (with model answers)

**Q:** MM2 vs Cluster Linking?
**A:** For «Multi-region EDA»: MM2 vs Cluster Linking. In production, Primary Kafka in `eu-west`; MM2 to `us-east` for read-only analytics; failover runbook promotes US consumers with accepted 30s RPO on events. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Data residency and topic replication?
**A:** The follow-on risk of «Data residency and topic replication» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Saga behavior during region failover?
**A:** Trade-off framing for «Saga behavior during region failover»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Multi-region EDA.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Primary Kafka in `eu-west`; MM2 to `us-east` for read-only analytics; failover runbook promotes US consumers with accepted 30s RPO on events.. I suspect active-active without conflict design until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 49. Documentation: event catalog.

**Short answer:** Maintain an event catalog: type, schema version, producer, consumers, partition key, compatibility mode, PII classification, retention, and lag SLO. AsyncAPI is the standard machine-readable format — without it, integration is tribal knowledge and breaking changes ship Friday afternoon. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Living documentation for event-driven contracts — the API docs equivalent for async integration. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Each entry: `OrderPlaced`, Avro schema link, owning team Order, consumers [Inventory, Billing], key `orderId`, BACKWARD, PII none, retention 30d, SLO 2s to Inventory projection. AsyncAPI YAML in repo; CI validates against registry. Link to runbooks for replay and DLT.

#### When to use / when NOT to use
Mandatory for public integration topics at two+ consumers. Internal topics can be lighter. Update catalog in same PR as schema change — review gate.

#### Production example
`docs/events/order-placed.asyncapi.yaml` generated HTML in Backstage; breaking change PR requires consumer team approval checkbox.

#### Common mistakes
Confluence doc stale since 2022. No consumer list — breaking change surprise. Missing partition key documentation → hot spots.

#### Interview follow-ups (with model answers)

**Q:** AsyncAPI vs OpenAPI for events?
**A:** For «Documentation: event catalog»: AsyncAPI vs OpenAPI for events. In production, `docs/events/order-placed.asyncapi.yaml` generated HTML in Backstage; breaking change PR requires consumer team approval checkbox. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Who owns catalog — producer or platform?
**A:** The follow-on risk of «Who owns catalog — producer or platform» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Event catalog vs schema registry?
**A:** Trade-off framing for «Event catalog vs schema registry»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Documentation: event catalog.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `docs/events/order-placed.asyncapi.yaml` generated HTML in Backstage; breaking change PR requires consumer team approval checkbox.. I suspect confluence doc stale since 2022 until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 50. Senior EDA interview speech.

**Short answer:** Close with a coherent production story: integration events from transactional outbox keyed by aggregate ID, CDC or poller relay, idempotent consumers with inbox, CQRS projections with explicit lag SLO, sagas with timeouts and compensation, AFTER_COMMIT listeners only for non-critical local work — and honest acknowledgment that exactly-once into Oracle requires effectively-once patterns, not broker flags alone. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
The capstone narrative tying dual-write, eventual consistency, sagas, and CQRS into one credible senior answer interviewers expect when you claim EDA experience. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Publish path: `@Transactional` business write + outbox row → Debezium or relay → Kafka keyed by aggregate → schema registry BACKWARD. Consume path: inbox dedup + projection TX + offset → saga orchestrator or choreography with documented policies → DLT for poison, not business reject. UX: read-your-writes on command path, staleness SLO on search. Ops: lag, saga age, outbox backlog, trace by correlationId.

#### When to use / when NOT to use
Use this framing when asked "how would you design event-driven order flow?" or "what went wrong in your last Kafka incident?" Adapt detail to company stack (Spring, Oracle, Azure Event Hubs analogs).

#### Production example
"We never dual-write — outbox in Oracle, Debezium to `orders.events`, Inventory inbox on `event_id`, checkout saga in Temporal with 30m timeout, search projection p99 lag 5s SLO, GDPR tombstones on customer key, replay runbook with email handler classified non-replay-safe."

#### Common mistakes
Buzzwords without outbox/inbox. Claiming exactly-once everywhere. Ignoring UX eventual consistency. No mention of catalog or contract testing.

#### Interview follow-ups (with model answers)

**Q:** Walk through dual-write failure scenario?
**A:** For «Senior EDA interview speech»: Walk through dual-write failure scenario. In production, "We never dual-write — outbox in Oracle, Debezium to `orders.events`, Inventory inbox on `event_id`, checkout saga in Temporal with 30m timeout, search projection p99 lag 5s SLO, GDPR tombstones on customer key, replay r… I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Compare choreography vs orchestration for your saga?
**A:** The follow-on risk of «Compare choreography vs orchestration for your saga» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How measure and alert projection lag?
**A:** Trade-off framing for «How measure and alert projection lag»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Senior EDA interview speech.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: "We never dual-write — outbox in Oracle, Debezium to `orders.events`, Inventory inbox on `event_id`, checkout saga in Temporal with 30m timeout, search projecti…. I suspect buzzwords without outbox/inbox until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

## Deep-dive additions (Q51–Q55)

Event catalogs, EDA testing, saga engines, notification vs state transfer, GDPR erasure.

---

### 51. Event catalog and schema ownership (Confluent/AsyncAPI)

**Short answer:** An **event catalog** is the discoverable registry of domain events — name, schema, owner team, topic, compatibility, and sample payloads. **Confluent Schema Registry** governs Avro/Protobuf schemas; **AsyncAPI** documents async APIs like OpenAPI for HTTP. **Schema ownership** means producer team approves changes; consumers subscribe to catalog notifications. Trade-off: governance friction versus integration chaos without a single source of truth.

#### What it is
Platform engineering delivers catalog (Backstage plugin, Confluent Stream Catalog, EventCatalog tool) linked to Kafka subjects and AsyncAPI YAML in git. Java teams publish `OrderCreated` v3 only after catalog PR approved. Interview: "where do I find who owns `PaymentCaptured`?" — catalog entry with Slack, on-call, retention, PII classification.

#### How it works (internals)
AsyncAPI defines channels, messages, bindings (kafka topic). CI validates YAML on merge. Schema registry enforces BACKWARD compatibility on register. Catalog syncs from registry + git via API. Lineage: event → producers → consumers (Pact broker integration). Deprecation workflow: `deprecated: true`, sunset date, consumer checklist.

#### When to use / when NOT to use
Mandatory at 20+ events and 10+ teams. Small startup: markdown in repo acceptable until pain. Never skip PII tagging in catalog for GDPR.

#### Production example
Backstage `EventComponent` for `order.created` links to AsyncAPI spec, Avro schema ID 42, owner `@order-platform`, consumers `[inventory, billing]`. Breaking change PR blocked until consumers verify in Pact. New hire finds integration docs in 5 minutes — previously Slack archaeology.

#### Common mistakes
- Catalog drift from reality — no CI sync.
- Schema owner unclear — two teams register conflicting subjects.
- AsyncAPI without kafka bindings — useless for ops.
- No deprecation dates — zombie events forever.

#### Interview follow-ups (with model answers)

**Q:** AsyncAPI vs schema registry alone?
**A:** Registry enforces payload schema; AsyncAPI documents channels, headers, retry semantics, and ownership narrative. Use both — registry for runtime, AsyncAPI for human and CI lint.

**Q:** Who approves new event type?
**A:** Architecture review or event governance board; producer team implements; platform merges registry subject; consumers opt-in via catalog watch. Emergency hotfix still needs retroactive catalog update within 48h.

#### Scenario probe
Two teams publish different `OrderShipped` schemas to same topic.

**Model answer:** Governance failure — one subject one owner. Freeze producer, align schema, new subject if semantics diverge. Catalog lists canonical owner; CI blocks second producer registration.

#### Code / config (when useful)

```yaml
# asyncapi/order-created.yaml (excerpt)
channels:
  order.created:
    publish:
      message:
        name: OrderCreated
        payload:
          $ref: '#/components/schemas/OrderCreated'
bindings:
  kafka:
    topic: orders.events
    schemaId: 42
```

---

### 52. Event-driven microservices testing: contract + topology tests

**Short answer:** **Contract tests** (Pact message pacts, schema compatibility) verify payload shape between producer and consumer. **Topology tests** verify the **wiring** — which services publish/subscribe to which topics — matches architecture diagram (Testcontainers Kafka + schema registry, or `topology-test` tools). Combine with **consumer-driven** pacts and **e2e** smoke for money paths. Trade-off: test pyramid investment versus production-only discovery of missing subscription.

#### What it is
EDA testing beyond unit: message pact consumer expects `OrderCreated` fields; provider verifies; topology test fails if `billing-service` no longer listens to `orders.events` but ADR says it should. Java: Spring tests with `@EmbeddedKafka`, Testcontainers, Pact JVM, optional ArchUnit for `@KafkaListener` topic constants.

#### How it works (internals)
Message pact flow same as HTTP Pact. Topology: declarative YAML `billing consumes orders.events` compared to runtime discovery (grep listeners, Spring Cloud Stream bindings, or broker ACL audit). CI on every MR. E2E: publish golden event, assert DB side effect in consumer with Testcontainers. Chaos: kill consumer mid-process, assert idempotent replay.

#### When to use / when NOT to use
Contract for every public event between teams. Topology when microservices count >15 and ghost consumers common. Skip topology YAML if monolith — use module tests.

#### Production example
Topology test failed: `shipping-service` refactor removed `@KafkaListener` on `orders.events` — deploy blocked. Pact alone would not catch — consumer still compiled but wrong topic constant typo. Combined gate saved silent missed shipments.

#### Common mistakes
- Only testing HTTP — events untested.
- Pact without broker publish verification.
- E2E only — slow, flaky, no contract granularity.
- Topology doc never updated — false green.

#### Interview follow-ups (with model answers)

**Q:** How test ordering and idempotency?
**A:** Integration test publish same `eventId` twice, assert one DB row. Publish out-of-order versions, assert consumer rejects stale. Use `@EmbeddedKafka` with manual offset control.

**Q:** Pact vs schema registry CI?
**A:** Registry checks Avro rules; Pact checks consumer actually uses fields correctly. Both gates — registry does not know consumer ignored required business field with default null.

#### Scenario probe
Consumer deployed but not receiving events — tests were green.

**Model answer:** Unit tests mocked listener; no topology/e2e. Add test asserting listener container subscribed to correct topic name from config; smoke test publish to real Testcontainers Kafka.

#### Code / config (when useful)

```java
@Test
void topology_billingConsumesOrdersTopic() {
    var listeners = KafkaListenerInspector.findTopics(BillingConsumer.class);
    assertThat(listeners).contains("orders.events");
}
```

---

### 53. Temporal vs Camunda for long-running sagas

**Short answer:** **Temporal** (workflow-as-code) and **Camunda** (BPMN engine) orchestrate long-running sagas with timers, human tasks, and compensation. **Temporal**: developers write Java/Go workflows as code — durable execution, strong versioning story, popular for cloud-native microservices. **Camunda**: BPMN diagrams for business/ops visibility, mature in enterprises, Java delegates. Trade-off: Temporal code-first agility versus Camunda process model accessibility for non-devs.

#### What it is
Saga orchestration for order fulfillment spanning days (payment auth expiry, warehouse pick, human approval). Spring apps invoke Temporal worker or Camunda external tasks. Interview: when not to use either — 2-step choreography OK; 10+ steps with timers → orchestrator.

#### How it works (internals)
Temporal: Workflow service stores event history; worker replays on recovery; `Activity` calls microservices with retries; `Sleep` durable. Versioning via `Workflow.getVersion`. Camunda: process engine persists tokens; job workers poll; BPMN XML deploy. Both need idempotent activities. Temporal namespace isolation; Camunda multi-tenancy via tenant id.

#### When to use / when NOT to use
| Choose | When |
|--------|------|
| Temporal | Dev-owned workflows, rapid change, K8s native, strong testability |
| Camunda | BPMN mandate, business process modeling, existing ops Camunda ops team |
| Choreography | 2–3 steps, no timers, clear events |

#### Production example
Bank onboarding saga 12 steps, 30-day timer — Camunda BPMN for compliance audit trail. Startup order saga — Temporal Java SDK in `order-worker` deployment; replaced brittle DB `saga_state` table cron. Migration: Camunda stays for regulated; Temporal for new product lines.

#### Common mistakes
- Orchestrating inside Kafka consumer thread — use workflow engine.
- Non-idempotent activities — duplicate side effects on replay.
- BPMN drift from deployed delegates — no CI diagram diff.
- Ignoring workflow versioning on breaking change.

#### Interview follow-ups (with model answers)

**Q:** Temporal vs hand-rolled saga table?
**A:** Hand-rolled works for 3 states; timers, retries, visibility, and replay explode complexity. Temporal gives durable sleep and history for free; ops UI via Temporal Web. Use saga table only if org bans external orchestrator.

**Q:** Camunda 8 vs 7 for cloud?
**A:** Camunda 8 Zeebe broker cloud-native; 7 monolithic engine common on-prem. Java delegates similar; migration path topic for enterprise JD.

#### Scenario probe
Order saga stuck — payment timer should fire in 24h but never does.

**Model answer:** Cron-based saga table missed scheduler pod death. Temporal/Camunda durable timer survives worker restart. Migrate timer steps to workflow engine; add alert on stuck workflow count.

#### Code / config (when useful)

```java
@WorkflowInterface
public interface OrderWorkflow {
    @WorkflowMethod
    void placeOrder(OrderRequest req);
}

public class OrderWorkflowImpl implements OrderWorkflow {
    public void placeOrder(OrderRequest req) {
        var payment = Workflow.newActivityStub(PaymentActivities.class, options);
        payment.authorize(req);
        Workflow.sleep(Duration.ofHours(24));
        payment.capture(req);
    }
}
```

---

### 54. Event notification vs event-carried state transfer — migration path

**Short answer:** **Event notification** carries minimal data (`orderId`, event type) — consumers call API for details. **Event-carried state transfer** (ECST) embeds full payload consumers need — no callback. Migration: start notification + stable API; add fields to event incrementally; deprecate sync API reads when consumers confirm self-sufficient payload; watch message size and PII exposure. Trade-off: notification keeps events small but couples availability; ECST decouples but duplicates data and versioning burden.

#### What it is
DDD integration patterns. Notification: `OrderPlaced { orderId }` → inventory calls `GET /orders/{id}`. ECST: `OrderPlaced { orderId, lines[], shipAddress }` — inventory never calls order service. Migration common during scale-out — reduce sync fan-out.

#### How it works (internals)
Phase 1: notification + API with SLA. Phase 2: **fat events** optional fields BACKWARD compatible. Phase 3: consumers stop API — metric `order-api.calls.from.inventory` zero. Phase 4: remove API path or rate-limit. Schema registry tracks growth. GDPR: ECST duplicates PII — propagate retention and erasure to all consumer stores.

#### When to use / when NOT to use
Notification when order aggregate large or sensitive fields restricted. ECST when consumer availability independent and low latency critical. Hybrid: notification + snapshot id for cache lookup.

#### Production example
Inventory called order API 50k/min — bottleneck. Evolved `OrderPlaced` to include `lines` and `warehouseHint`; feature flag consumer uses embedded data with API fallback. Six weeks later API fallback removed. Event size 4KB → acceptable; monitored schema evolution.

#### Common mistakes
- Big-bang ECST without consumer readiness — deserialization failures.
- ECST with unbounded aggregate — 1MB Kafka message.
- Notification without API SLO — cascading failure.
- Forgetting consumer projection schema migration.

#### Interview follow-ups (with model answers)

**Q:** How avoid breaking consumers during fattening?
**A:** Add optional Avro fields BACKWARD compatible; consumers ignore unknown; dual-read API fallback behind flag; Pact message pact updated per consumer before producer deploy.

**Q:** Event notification and CQRS read models?
**A:** Notification + API is sync coupling; ECST feeds read model directly — classic CQRS event path. Pick based on coupling tolerance.

#### Scenario probe
CTO wants ECST immediately to "delete all sync calls."

**Model answer:** Phased migration with metrics; start with read-heavy consumers; keep API for audit until reconciliation proves parity. Document PII duplication in event catalog.

#### Code / config (when useful)

```java
// Phase 2 — fat event with optional API fallback
if (event.hasLines()) {
    reserveFromEvent(event);
} else {
    reserveFromApi(event.orderId());
}
```

---

### 55. GDPR right-to-erasure in event-sourced systems

**Short answer:** **Right to erasure** (GDPR Art. 17) conflicts with immutable **event logs** — you cannot truly delete from Kafka retention without tombstones/compaction policy and coordinated **consumer projections** purge. Strategy: **crypto-shredding** (delete encryption key for user's events), **tombstone** compacted topics, **anonymize** PII fields in projections, **orchestrated deletion choreography** across services with audit proof. Trade-off: legal compliance versus perfect event-sourcing immutability theology.

#### What it is
Event-sourced/CQRS systems store `CustomerRegistered` forever — GDPR erasure must reach read models, warehouses, search indexes, and log archives. Java services implement `CustomerErasureRequested` handler idempotent per service. Legal may accept anonymization vs hard delete for finance records.

#### How it works (internals)
Orchestrator emits erasure event with `correlationId`; each service deletes/anonymizes PII in DB, S3, cache; reports ACK to orchestration table. Kafka: publish tombstone `key=customerId, value=null` on compacted PII topic; non-compacted requires retention policy + archive purge workflow. Crypto-shredding: per-user DEK in vault — delete key renders events unreadable. Reconciliation job verifies no PII in search index post-erasure.

#### When to use / when NOT to use
Design erasure from day one in event catalog PII tags. Retrofit painful — scan all consumers. Finance audit may mandate retain anonymized transaction, not delete — legal defines per field class.

#### Production example
`CustomerDeletionRequested` choreography across 11 services; 30-day SLA. Search index purge via API; warehouse batch job `DELETE WHERE customer_id`. Kafka compacted `customer-profile` tombstoned. Auditor receives deletion certificate JSON from orchestration table. Failed service blocks completion alert — not silent partial erasure.

#### Common mistakes
- Delete OLTP row only — projections and Kafka retain PII.
- No idempotent erasure handler — duplicate events confuse state.
- Infinite retention audit topic without erasure workflow.
- Claiming "events are immutable so GDPR impossible" — legal rejects.

#### Interview follow-ups (with model answers)

**Q:** Tombstone vs delete topic?
**A:** Tombstone on compacted topic removes key after compaction — eventual. Active delete requires topic admin + consumer compaction understanding. For non-compacted, rely on projection purge not broker forget.

**Q:** Erasure in event sourcing audit trail?
**A:** Anonymize event payload in event store where law allows; retain non-PII facts (`PaymentAmount` without name). Legal sign-off per jurisdiction.

#### Scenario probe
Customer requests deletion; events in S3 archive for 7 years.

**Model answer:** Erasure workflow includes archive purge or crypto-shred keys used for archived payloads. Document in ROPA. Cannot ignore cold storage — regulator checks all copies.

#### Code / config (when useful)

```java
@KafkaListener(topics = "privacy.erasure")
void onErasure(ErasureCommand cmd) {
    if (erasureLog.alreadyProcessed(cmd.requestId())) return;
    customerRepo.anonymize(cmd.customerId());
    searchClient.deleteByCustomerId(cmd.customerId());
    erasureLog.markDone(cmd.requestId());
}
```

---

## Scenario-based interview drills

### S1. Checkout saga stuck in "pending payment"

**Situation:** E-commerce checkout saga: `OrderPlaced` → reserve inventory → capture payment. 2% of orders stuck `PENDING_PAYMENT` > 2 hours. Payment service shows `PaymentCaptured` in logs; order service never updated. Kafka lag normal.

**What they're testing:** Saga timeouts, lost events, choreography coupling, correlation debugging.

**How to structure your answer:** Trace correlationId → consumer inbox → event version → missing compensation → saga sweeper.

**Model answer:** Lag normal rules out slow consumers — suspect lost event, wrong consumer group, schema reject to DLT, or saga state machine not handling `PaymentCaptured`. I'd search logs/traces by `correlationId` across Order and Payment services. Check Payment published to correct topic with compatible schema; Order listener errors in DLT? Verify inbox didn't dedupe incorrectly (same eventId reused). Choreography gap: no timeout — add saga `scheduled_at` sweeper emitting `PaymentTimedOut` → release inventory. Long-term: orchestrator (Temporal) with durable timer, or explicit policy table documenting reactions. Prevention: contract tests, saga age alert > 30m, dashboard by state. Explain difference between technical loss (outbox) vs logical stuck (missing transition).

**Common weak answers:** "Restart Kafka"; scale consumers when lag zero; no correlation tracing.

**Follow-up probes (with answers):**

**Q:** Choreography timeout without orchestrator?
**A:** Scheduled job scans `saga_instance` where `state=PENDING_PAYMENT` and `updated_at < now()-30m`, publishes compensating command — must be idempotent.

**Q:** PaymentCaptured before OrderPlaced out-of-order?
**A:** Version gate on aggregate; defer apply until `OrderPlaced` seen; metric for gap detection.

---

### S2. Dual-write ghost events after rollback

**Situation:** Developer adds `kafkaTemplate.send` inside `@Transactional` order method before fix review. Under DB deadlock, transaction rolls back but message already on bus; inventory reserves stock for non-existent order.

**What they're testing:** Dual-write, outbox, transaction boundaries.

**How to structure your answer:** Interleaved TX boundaries → ghost event → outbox fix → consumer defense.

**Model answer:** Kafka send defaults to async — may land on broker before JDBC rollback completes. Inventory consumed ghost `OrderPlaced`. Fix: remove direct send; insert outbox row in same TX as order; relay only after commit. Consumer-side: validate `orderId` exists or inbox with saga correlation before reserve. Detection: reconciliation comparing Kafka event count to DB orders. CI rule blocking `KafkaTemplate` in `@Transactional` without outbox. Teach: Spring TX does not include Kafka unless chained TX (fragile) — outbox is default pattern.

**Common weak answers:** "Use @Transactional on listener"; enable Kafka EOS globally; blame inventory only.

**Follow-up probes (with answers):**

**Q:** @TransactionalEventListener AFTER_COMMIT enough?
**A:** No — crash after commit before listener still loses event; outbox row committed with business data is the guarantee.

**Q:** Inventory defense?
**A:** Idempotent reserve checking order exists in read model; reject unknown `orderId` with metric.

---

### S3. Thin events cause Order API outage cascade

**Situation:** `OrderPlaced` carries only `orderId`. Inventory `@KafkaListener` calls `GET /orders/{id}` for every message. Order API overloaded during sale; inventory lag explodes; `max.poll.interval` exceeded.

**What they're testing:** Temporal coupling, ECST, fat events, consumer design.

**How to structure your answer:** Identify sync coupling → ECST or local cache → circuit breaker → poll tuning interim.

**Model answer:** Thin events + HTTP hydration reintroduce temporal coupling — Inventory cannot process when Order API down, and partition processing blocks on slow REST, triggering rebalance. Fix structural: enrich `OrderPlaced` ECST with `sku`, `qty`, `warehouseId` needed for reservation (no PAN). Maintain `order_cache` table updated by same topic for other fields. Interim: circuit breaker with bounded queue per partition, reduce `max.poll.records`, but ECST is real fix. Document bounded context: integration event carries fulfillment slice only. Measure API call elimination post-deploy.

**Common weak answers:** Scale Order API only; infinite HTTP timeout; thicker events with entire aggregate graph and PII.

**Follow-up probes (with answers):**

**Q:** When is thin event OK?
**A:** Same team, co-deployed, low volume, or consumer is API gateway with different SLAs — not hot-path inventory.

**Q:** Circuit breaker in listener thread?
**A:** Risky — opens circuit but partition still blocked; better remove sync call.

---

### S4. Schema breaking change Friday deploy

**Situation:** Team adds required field `currency` to `PaymentCaptured` Avro without default. Old inventory consumer crashes; DLT fills; payments captured but stock not decremented.

**What they're testing:** Schema evolution, registry compatibility, deployment order.

**How to structure your answer:** BACKWARD violation → consumer-first rule → fix compatibility → replay → CI gate.

**Model answer:** Required field without default breaks BACKWARD compatibility — old readers cannot decode. Inventory listener throws `SerializationException` → DLT after retries. Fix: add `currency` optional with default `USD` in schema, register BACKWARD compatible, redeploy consumers before producers (or simultaneous). Replay DLT with idempotent inventory handler. Prevention: Schema Registry CI `mvn schema-registry:test-compatibility`, blocking PR. Blue/green: dual-publish v1/v2 during migration window. Distinguish business reject (insufficient stock) from technical poison (schema) — only latter to DLT.

**Common weak answers:** "JSON is flexible"; skip registry in prod; replay DLT without schema fix.

**Follow-up probes (with answers):**

**Q:** FORWARD vs BACKWARD for consumer lagging?
**A:** BACKWARD: new schema, old consumer reads old records — default for consumer-first rollout. FORWARD when producers lag — rare.

**Q:** JSON without registry?
**A:** Pact/contract tests + explicit `schemaVersion` in envelope + CI fixtures — same discipline manually.

---

### S5. Unique Kubernetes group.id replay disaster

**Situation:** Helm chart sets `group-id: billing-${POD_NAME}` for "scaling." After deploy, 20 pods create 20 groups with `auto.offset.reset=earliest`. Billing duplicates charges; finance halts deploy.

**What they're testing:** Consumer group semantics, K8s misconfig, idempotency as safety net.

**How to structure your answer:** Explain multiple groups → duplicate processing → stable group id → idempotency saved or didn't → helm fix.

**Model answer:** Each pod became its own consumer group — all read full topic from earliest independently — 20× processing. If inbox idempotency worked, duplicates skipped but load spiked; if not, double charges. Fix: constant `group-id: billing-projection-v1` in ConfigMap; HPA scales pods sharing group. Document anti-pattern `${HOSTNAME}` in Kafka checklist. Recovery: pause billing, reconcile ledger, verify inbox. Prevention: smoke test asserts single group lag metric matches pod count, not 20× groups.

**Common weak answers:** Scale partitions to fix group id bug; use `latest` without understanding skip vs duplicate.

**Follow-up probes (with answers):**

**Q:** Blue/green different group id?
**A:** Intentional only with offset migration plan; not per-pod random groups.

**Q:** Static group membership?
**A:** `group.instance.id` reduces rebalance on rolling restart — distinct from unique group per pod bug.

---

### S6. GDPR erasure vs event replay resurrection

**Situation:** Customer erasure completed in CRM DB. Marketing replayed Kafka topic from yesterday for bug fix; customer emails sent again; legal escalation.

**What they're testing:** GDPR, replay safety, PII minimization, handler classification.

**How to structure your answer:** Replay re-executes side effects → classify handlers → erasure events → replay guards.

**Model answer:** Replay is not time travel — handlers re-run emails, charges unless guarded. Erasure must propagate: tombstone on `customerId` compacted topics, projection purge, `CustomerErased` event consumers honor. Replay runbook classifies handlers: replay-safe (idempotent projection) vs not (notifications check `notification_sent_at` or erasure flag). Post-erasure replay must filter erased customers or use sanitized archive. Prevention: minimal PII in events, erasure saga checklist before any replay, legal sign-off. Technical: replay tool accepts `--skip-notifications` and queries erasure registry.

**Common weak answers:** "Replay is safe if idempotent"; DB delete enough; no erasure registry.

**Follow-up probes (with answers):**

**Q:** Tombstone vs erase event?
**A:** Tombstone for compacted key-value; explicit `CustomerErased` integration event for choreographed purge across SQL/ES/cache.

**Q:** Compacted topic after erasure?
**A:** Tombstone + compaction lag — still plan segment retention audit.

---

### S7. Orchestration vs choreography for loan approval

**Situation:** Loan flow: credit check, fraud, manual underwriter, document sign, fund — 12 steps, 5 services, 48-hour SLA, human pause.

**What they're testing:** Saga pattern choice, Temporal/Camunda vs homemade, visibility.

**How to structure your answer:** Criteria for orchestrator → human timers → compensation → avoid god service.

**Model answer:** Pure choreography across 12 steps becomes undebuggable — no single view, implicit ordering via events, timeout scattered. I'd choose orchestration: Temporal workflow with activities calling each service, durable timers for 48h underwriter wait, compensation paths defined per step (idempotent `VoidCreditCheck`). Orchestrator thin — routes, correlates, times out; domain rules stay in services. Choreography OK for 2–3 side effects (email, metrics). Human step: signal API to workflow when underwriter completes. Visibility for support UI from workflow history. Homemade saga table OK for MVP 3-step — not 12-step with humans.

**Common weak answers:** "All choreography because decoupled"; orchestrator updating foreign DB tables; no compensation design.

**Follow-up probes (with answers):**

**Q:** Temporal vs Camunda for Java shop?
**A:** Temporal code-first, strong Java SDK, popular for microservice sagas; Camunda BPMN if business wants visual models and external tasks.

**Q:** Event-driven orchestrator?
**A:** Orchestrator emits commands/events; still central state — not pure choreography.

---

### S8. Projection lag SLO breach during DB index rebuild

**Situation:** Order search ES projection p99 lag SLO 5s; DBA rebuilds index on source Postgres; lag hits 45 minutes; product unaware "real-time search" stale.

**What they're testing:** CQRS lag SLO, UX honesty, monitoring, operational communication.

**How to structure your answer:** Measure end-to-end lag → source cause → comms → scale consumer → read fallback.

**Model answer:** Consumer handler blocked on slow SQL — lag metric `now - projection.updated_at` breaches SLO. Immediate: coordinate with DBA pause or throttle rebuild, scale consumer pods to partition limit, batch writes to ES. Product: enable staleness badge from health endpoint `X-Lag-Seconds`, temporarily route detail search to write DB for support tools. Long-term: lag SLO in error budget, maintenance window policy, consumer pool sized for headroom, alert at 2× SLO. Distinguish broker lag vs projection age — here broker fine, DB slow. Postmortem: SLO document signed by product defining "real-time" as 5s p99 not zero.

**Common weak answers:** Only watch Kafka lag; promise strong consistency on search; silent degradation.

**Follow-up probes (with answers):**

**Q:** Read-your-writes after checkout?
**A:** POST returns orderId; UI polls write-model API until confirmed — not ES projection.

**Q:** Rebuild projection after corruption?
**A:** Reset consumer offset if retention allows; else snapshot + incremental — plan retention/archival first.

---

### S9. Outbox polling vs CDC migration

**Situation:** Outbox poller every 5s works at 200 TPS; business wants sub-500ms publish SLO for `OrderPlaced` at 2k TPS peak. Team debates Debezium.

**What they're testing:** Outbox relay mechanisms, trade-offs, phased migration.

**How to structure your answer:** Measure current lag → polling limits → CDC benefits/costs → hybrid migration.

**Model answer:** At 2k TPS, 5s poll interval plus `SELECT` contention causes multi-second lag — fails SLO. Options: reduce interval to 200ms with `FOR UPDATE SKIP LOCKED` and index on `(published_at IS NULL)`, multiple relay instances — may achieve sub-second without CDC. If SLO < 500ms consistently, Debezium on outbox table tails WAL — milliseconds lag, ops owns connector HA, schema migrations coordinated. Phased: add CDC parallel, compare `outbox_lag` metrics, cut poller when CDC stable. Consumer idempotency unchanged either path. Don't CDC entire OLTP schema when outbox-only suffices.

**Common weak answers:** Jump to CDC without measuring poller tuning; dual relay without dedup; delete outbox rows before Kafka ack.

**Follow-up probes (with answers):**

**Q:** SKIP LOCKED on Oracle?
**A:** Supported in 11g+ — pattern `WHERE published_at IS NULL FOR UPDATE SKIP LOCKED` — verify execution plan.

**Q:** Exactly-once relay?
**A:** At-least-once relay + consumer idempotency; mark published after broker ack in same relay TX.

---

### S10. Senior EDA whiteboard: order platform end-to-end

**Situation:** "Design event-driven order flow for microservices — how do you avoid dual-write, handle failures, and set UX expectations?"

**What they're testing:** Full EDA stack: outbox, inbox, CQRS, saga, contracts, ops, honesty on exactly-once.

**How to structure your answer:** Command API → outbox → events → consumers → sagas → read models → UX → observability → anti-patterns rejected.

**Model answer:** Hybrid architecture: `POST /orders` sync command validates, writes aggregate + outbox in one Oracle TX. Relay (Debezium/poll) publishes `OrderPlaced` Avro keyed by `orderId`, Schema Registry BACKWARD. Inventory/Billing/Fraud separate consumer groups with inbox `event_id` UNIQUE, manual Kafka ack after TX. Checkout saga via Temporal: 30m timeout, compensations idempotent. CQRS: `order_read_model` projection with p99 lag 5s SLO; UI read-your-writes via write API post-submit. No dual-write; `@TransactionalEventListener` only for local cache eviction. CorrelationId in all envelopes. DLT for poison; `PaymentDeclined` is normal event not DLT. GDPR: tokenized customer id in events. Observability: outbox lag, projection age, saga stuck alert, trace by correlationId. I state clearly: effectively-once via inbox/outbox, not broker EOS into Oracle.

**Common weak answers:** Kafka-only no APIs; exactly-once everywhere; no saga timeout; fat events with PAN; no catalog.

**Follow-up probes (with answers):**

**Q:** When choreography over orchestration here?
**A:** Email/analytics side effects choreographed; payment/inventory path orchestrated due to timeouts and compensations.

**Q:** When NOT use EDA?
**A:** Single-team CRUD, strong consistency everywhere, no ops for broker — modular monolith first.

---
