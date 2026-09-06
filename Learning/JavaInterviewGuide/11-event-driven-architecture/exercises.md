# Event-Driven Architecture — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**Stack:** Spring Boot 3, Kafka or JMS, Postgres, optional Temporal for sagas.

---

# Part A — Basic (10)

## Exercise 1 — Event vs command naming

**Task:** Classify each message; rename violations.

**Solution:**

| Message | Type | Good name |
|---------|------|-----------|
| `CreateOrder` | Command | `CreateOrder` (imperative) |
| `OrderPlaced` | Event | `OrderPlaced` (past tense) |
| `UpdateInventory` | Command | sent to inventory service |
| `StockReserved` | Event | fact that happened |
| `GetOrderStatus` | Query | **not** an event — use REST/gRPC |

**Rules:** Events = immutable facts (past tense). Commands = intent (imperative). Don't publish queries on the event bus.

---

## Exercise 2 — `AFTER_COMMIT` listener is not durable delivery

**Task:** Show order committed but Kafka never receives event; replace with outbox.

**Broken:**

```java
@Transactional
public void place(Order o) {
    repo.save(o);
    events.publishEvent(new OrderPlaced(o.getId()));
}

@TransactionalEventListener(phase = TransactionPhase.AFTER_COMMIT)
void send(OrderPlaced e) {
    kafka.send("orders", e.orderId(), toJson(e));  // crash here = lost event
}
```

**Solution:**

```java
@Transactional
public void place(Order o) {
    repo.save(o);
    outboxRepo.save(Outbox.kafka("orders", o.getId(), new OrderPlaced(o.getId(), Instant.now())));
}
```

`AFTER_COMMIT` only guarantees the DB TX finished — not that external publish succeeded.

---

## Exercise 3 — Thin vs fat events

**Task:** Implement both; count HTTP calls for a dashboard.

**Solution:**

```java
// Thin — consumer fetches details
public record OrderPlaced(String orderId, Instant at) {}

@KafkaListener(topics = "orders")
void on(OrderPlaced e) {
    OrderDetails details = orderApi.get(e.orderId());  // +1 HTTP per event
    projection.update(details);
}

// Fat — self-contained
public record OrderPlacedFat(
    String orderId, String customerId, List<LineItem> lines, long totalCents, Instant at) {}

@KafkaListener(topics = "orders")
void on(OrderPlacedFat e) {
    projection.update(e);  // no HTTP
}
```

**Trade-off:** Fat = fewer chattier calls, larger payloads, tighter coupling to schema. Thin = stable contracts, more latency on consume. Default thin + cache for read models.

---

## Exercise 4 — Event envelope with metadata

**Task:** Wrap payload with `eventId`, `type`, `version`, `occurredAt`.

**Solution:**

```java
public record EventEnvelope<T>(
    String eventId,
    String type,
    int version,
    Instant occurredAt,
    String correlationId,
    String causationId,
    T data
) {
    static <T> EventEnvelope<T> wrap(T data, String type, String correlationId) {
        return new EventEnvelope<>(
                UUID.randomUUID().toString(), type, 1, Instant.now(),
                correlationId, null, data);
    }
}
```

```json
{
  "eventId": "evt_01HQ...",
  "type": "OrderPlaced",
  "version": 1,
  "occurredAt": "2026-09-05T10:00:00Z",
  "correlationId": "req_abc",
  "causationId": null,
  "data": { "orderId": "ord_1", "amountCents": 5000 }
}
```

---

## Exercise 5 — Correlation and causation IDs

**Task:** Propagate `correlationId` from HTTP request through all published events.

**Solution:**

```java
@Component
class CorrelationFilter extends OncePerRequestFilter {
    static final String HDR = "X-Correlation-Id";

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        String corr = Optional.ofNullable(req.getHeader(HDR)).orElse(UUID.randomUUID().toString());
        MDC.put("correlationId", corr);
        res.setHeader(HDR, corr);
        chain.doFilter(req, res);
        MDC.clear();
    }
}

void publish(OrderPlaced e) {
    String corr = MDC.get("correlationId");
    kafka.send(ProducerRecord.withHeaders("orders", e.orderId(), toJson(e),
            new RecordHeader("correlationId", corr.getBytes())));
}
```

`causationId` = `eventId` of the event that caused this one (e.g. `PaymentCaptured` caused by `PaymentRequested`).

---

## Exercise 6 — Event versioning strategy

**Task:** Add `version` field; upcast v1 → v2 in consumer.

**Solution:**

```java
@KafkaListener(topics = "orders")
void on(String raw) {
    JsonNode node = mapper.readTree(raw);
    int version = node.path("version").asInt(1);
    OrderPlaced event = switch (version) {
        case 1 -> upcastV1(node);
        case 2 -> mapper.treeToValue(node.path("data"), OrderPlacedV2.class);
        default -> throw new UnsupportedVersionException(version);
    };
    handler.handle(event);
}

OrderPlacedV2 upcastV1(JsonNode node) {
    var v1 = mapper.treeToValue(node.path("data"), OrderPlacedV1.class);
    return new OrderPlacedV2(v1.orderId(), v1.amountCents(), "USD");  // default currency
}
```

---

## Exercise 7 — Consumer idempotency table

**Task:** `processed_events` PK prevents double side effect.

**Solution:**

```sql
CREATE TABLE processed_events (
  event_id     VARCHAR(64) PRIMARY KEY,
  event_type   VARCHAR(64) NOT NULL,
  processed_at TIMESTAMPTZ DEFAULT now()
);
```

```java
@Transactional
void handle(EventEnvelope<OrderPlaced> env) {
    if (processedRepo.exists(env.eventId())) return;
    processedRepo.insert(env.eventId(), env.type());
    projection.apply(env.data());
}
```

---

## Exercise 8 — Pub/sub vs point-to-point diagram

**Task:** Draw topology for `OrderPlaced` → inventory, analytics, notifications.

**Solution:**

```
                    ┌─────────────────┐
  Order Service ──► │  orders topic   │ ──► Inventory (group: inventory-svc)
                    │  (pub/sub)      │ ──► Analytics (group: analytics-svc)
                    └─────────────────┘ ──► Notifications (group: notify-svc)
```

Each consumer group gets **every** message (fan-out). Within a group, partitions divide work (competing consumers).

---

## Exercise 9 — AsyncAPI lite

**Task:** Document `OrderPlaced` and `PaymentCaptured` channels.

**Solution:**

```yaml
asyncapi: 3.0.0
info:
  title: Order Events
  version: 1.0.0
channels:
  orders:
    address: orders
    messages:
      OrderPlaced:
        payload:
          type: object
          required: [orderId, amountCents]
          properties:
            orderId: { type: string }
            amountCents: { type: integer }
  payments:
    address: payments
    messages:
      PaymentCaptured:
        headers:
          type: object
          properties:
            correlationId: { type: string }
            causationId: { type: string }
        payload:
          type: object
          properties:
            orderId: { type: string }
            paymentId: { type: string }
```

---

## Exercise 10 — Event catalog entry

**Task:** Write catalog row for `OrderPlaced`.

**Solution:**

| Field | Value |
|-------|-------|
| Event | `OrderPlaced` |
| Version | 1 |
| Producer | order-service |
| Consumers | inventory-service, analytics-service, notification-service |
| Schema | `orderId` (string), `amountCents` (long), `occurredAt` (ISO-8601) |
| Compatibility | BACKWARD |
| Retention | 7 days |
| Idempotency key | `eventId` |

Bring this table to system design interviews.

---

# Part B — Intermediate (10)

## Exercise 11 — Inbox + outbox in one transaction

**Task:** Consume Kafka message, update account, emit downstream event — atomically.

**Solution:**

```sql
CREATE TABLE inbox (
  event_id     VARCHAR(64) PRIMARY KEY,
  processed_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE outbox (
  id       BIGSERIAL PRIMARY KEY,
  topic    VARCHAR(128),
  payload  TEXT,
  sent_at  TIMESTAMPTZ
);
CREATE TABLE account (
  id       VARCHAR(64) PRIMARY KEY,
  balance  BIGINT NOT NULL
);
```

```java
@Transactional
void handlePaymentCaptured(PaymentCaptured e) {
    inboxRepo.insert(e.eventId());  // PK violation if duplicate → skip or catch
    accountRepo.credit(e.accountId(), e.amount());
    outboxRepo.save(Outbox.kafka("account-updated", e.accountId(), ...));
}
```

Replay same Kafka message → inbox insert fails → no double credit.

---

## Exercise 12 — Out-of-order event versions

**Task:** `v=2` arrives before `v=1`; projection must end correct.

**Solution:**

```java
@Entity
class OrderProjection {
    @Id String orderId;
    int version;
    String status;
}

void apply(OrderStatusChanged e) {
    OrderProjection p = repo.findById(e.orderId()).orElse(new OrderProjection(e.orderId()));
    if (e.version() <= p.getVersion()) {
        log.info("stale event v={} current={}", e.version(), p.getVersion());
        return;
    }
    p.setStatus(e.status());
    p.setVersion(e.version());
    repo.save(p);
}
```

```java
@Test
void outOfOrder_ignoresStale() {
    handler.apply(new OrderStatusChanged("o1", 2, "SHIPPED"));
    handler.apply(new OrderStatusChanged("o1", 1, "PENDING"));
    assertThat(repo.find("o1").status()).isEqualTo("SHIPPED");
}
```

---

## Exercise 13 — Stuck saga detection query

**Task:** Admin list of sagas not terminal for > 15 minutes.

**Solution:**

```sql
CREATE TABLE saga_instance (
  id          VARCHAR(64) PRIMARY KEY,
  type        VARCHAR(64) NOT NULL,
  status      VARCHAR(32) NOT NULL,
  updated_at  TIMESTAMPTZ NOT NULL,
  payload     JSONB
);

SELECT id, type, status, updated_at,
       EXTRACT(EPOCH FROM (now() - updated_at)) / 60 AS minutes_stuck
  FROM saga_instance
 WHERE status NOT IN ('COMPLETED', 'FAILED', 'CANCELLED')
   AND updated_at < now() - INTERVAL '15 minutes'
 ORDER BY updated_at;
```

```java
@GetMapping("/admin/sagas/stuck")
List<StuckSagaDto> stuck() { return sagaRepo.findStuck(Duration.ofMinutes(15)); }
```

Ops interview talking point: **who gets paged** and **manual compensation** workflow.

---

## Exercise 14 — Replay-safe vs unsafe handlers

**Task:** Classify handlers; add dedupe for email.

**Solution:**

| Handler | Replay-safe? | Fix |
|---------|--------------|-----|
| Update projection table | Yes (with version check) | — |
| Send email | No | `UNIQUE(order_id, notification_type)` |
| Charge credit card | No | idempotency key on payment gateway |
| Increment metric counter | Yes if monotonic id | use eventId as metric tag |

```sql
CREATE TABLE notifications (
  order_id VARCHAR(64),
  type     VARCHAR(32),
  sent_at  TIMESTAMPTZ,
  PRIMARY KEY (order_id, type)
);
```

```java
@Transactional
void sendShippedEmail(OrderShipped e) {
    if (notifications.exists(e.orderId(), "SHIPPED")) return;
    emailService.send(...);
    notifications.insert(e.orderId(), "SHIPPED");
}
```

Replay Kafka from earliest → emails sent once.

---

## Exercise 15 — Random consumer `group-id` bug

**Task:** `${random.uuid}` per pod → each pod is its own group → duplicate processing.

**Broken:**

```yaml
spring.kafka.consumer.group-id: ${random.uuid}  # NEVER in production
```

**Symptom:** 3 pods = 3 groups = each message processed 3 times (if all subscribe to same topic with different groups).

**Fix:**

```yaml
spring.kafka.consumer.group-id: order-service
```

Fan-out requires **different** services with **different** stable group names, not different pods of the same service.

---

## Exercise 16 — Choreography vs orchestration

**Task:** Draw cancel-order flow both ways.

**Solution:**

**Choreography (no central coordinator):**

```
OrderCancelled ──► Inventory → StockReleased
              ──► Payment   → PaymentRefunded
              ──► Notify    → CancellationEmailSent
```

**Orchestration (saga manager):**

```
CancelOrder command ──► Saga Orchestrator
   ├──► ReleaseStock
   ├──► RefundPayment
   └──► SendEmail
   (on failure → compensating commands)
```

Choreography = fewer moving parts, harder to debug. Orchestration = visible state machine, single place for timeouts.

---

## Exercise 17 — Compensating events

**Task:** Define compensations for happy-path saga.

**Solution:**

| Forward event | Compensation |
|---------------|--------------|
| `StockReserved` | `StockReleased` |
| `PaymentCaptured` | `PaymentRefunded` |
| `OrderConfirmed` | `OrderCancelled` |

```java
@KafkaListener(topics = "payments")
void on(PaymentFailed e) {
    outboxRepo.save(Outbox.kafka("inventory", e.orderId(),
            new ReleaseStock(e.orderId(), e.reason())));
}
```

Compensations are **new events**, not deletes — audit trail preserved.

---

## Exercise 18 — Saga state machine in code

**Task:** `PENDING → RESERVED → PAID → CONFIRMED` with failure paths.

**Solution:**

```java
enum SagaStatus { PENDING, STOCK_RESERVED, PAID, CONFIRMED, CANCELLED, FAILED }

@Transactional
void on(StockReserved e) {
    SagaInstance saga = sagaRepo.find(e.orderId());
    if (saga.getStatus() != PENDING) return;
    saga.transition(STOCK_RESERVED);
    outboxRepo.save(commandToPayment(e.orderId()));
}

@Transactional
void on(StockRejected e) {
    SagaInstance saga = sagaRepo.find(e.orderId());
    saga.transition(CANCELLED);
    outboxRepo.save(new OrderCancelled(e.orderId(), e.reason()));
}
```

Illegal transitions throw — caught by stuck-saga monitor (Exercise 13).

---

## Exercise 19 — CQRS read model (basic projection)

**Task:** `order_summary` table updated only from events.

**Solution:**

```sql
CREATE TABLE order_summary (
  order_id   VARCHAR(64) PRIMARY KEY,
  customer_id VARCHAR(64),
  status     VARCHAR(32),
  total      BIGINT,
  updated_at TIMESTAMPTZ
);
```

```java
@KafkaListener(topics = "orders", groupId = "order-projection")
void project(OrderPlaced e) {
    summaryRepo.upsert(e.orderId(), e.customerId(), "PLACED", e.totalCents());
}

@KafkaListener(topics = "orders", groupId = "order-projection")
void project(OrderShipped e) {
    summaryRepo.updateStatus(e.orderId(), "SHIPPED");
}
```

API reads from `order_summary` only — never joins write model tables.

---

## Exercise 20 — `read-your-writes` in event-driven UI

**Task:** User places order; UI shows confirmation before projection catches up.

**Solution:**

```java
@PostMapping("/orders")
ResponseEntity<OrderDto> create(@RequestBody CreateOrderRequest req) {
    Order o = service.place(req);
    // Return write model response immediately
    return ResponseEntity.created(...).body(OrderDto.from(o));
}

@GetMapping("/orders/{id}")
OrderSummaryDto get(@PathVariable String id) {
    return summaryRepo.find(id)
            .or(() -> orderRepo.find(id).map(OrderSummaryDto::fromWriteModel))
            .orElseThrow(() -> new NotFoundException(id));
}
```

Or: poll `/orders/{id}` until projection version ≥ write version. Document eventual consistency in API docs.

---

# Part C — Hard (8)

## Exercise 21 — Choreographed saga (three services, no orchestrator)

**Task:** Implement order → inventory → payment → confirm with compensations.

**Solution:**

```
order-service:
  POST /orders → Order PENDING, outbox OrderPlaced

inventory-service:
  on OrderPlaced → reserve stock → outbox StockReserved | StockRejected

payment-service:
  on StockReserved → capture → outbox PaymentCaptured | PaymentFailed

order-service:
  on PaymentCaptured → CONFIRMED
  on PaymentFailed | StockRejected → CANCELLED, outbox OrderCancelled

inventory-service:
  on OrderCancelled → ReleaseStock
```

```java
// inventory-service
@Transactional
void on(OrderPlaced e) {
    if (inbox.exists(e.eventId())) return;
    inbox.insert(e.eventId());
    try {
        stock.reserve(e.orderId(), e.lines());
        outbox.save(new StockReserved(e.orderId()));
    } catch (InsufficientStock ex) {
        outbox.save(new StockRejected(e.orderId(), ex.getMessage()));
    }
}
```

Integration test with Testcontainers: kill payment after reserve → assert `StockReleased` published.

---

## Exercise 22 — Distributed outbox (multi-region)

**Task:** Publisher in `eu-west` writes outbox; relay to `us-east` Kafka cluster.

**Solution:**

```
┌──────────── EU ────────────┐     ┌──────────── US ────────────┐
│ App → outbox (Postgres)    │     │ Kafka cluster (primary)    │
│ Outbox relay → MirrorMaker │ ──► │ Consumers                  │
└────────────────────────────┘     └────────────────────────────┘
```

```java
@Scheduled(fixedDelay = 200)
void relayToUsCluster() {
    outboxRepo.findUnsent().forEach(row -> {
        usKafkaTemplate.send(row.topic(), row.key(), row.payload());
        row.markSent();
    });
}
```

**Caveats:** relay is at-least-once; consumers idempotent; clock skew affects `occurredAt` ordering — use `eventId` not wall clock for causality.

---

## Exercise 23 — Event replay at scale

**Task:** Rebuild `order_summary` from Kafka earliest offset without emailing customers.

**Solution:**

```java
@Component
class ProjectionRebuilder {
    void rebuild() {
        summaryRepo.truncate();
        processedEventsRepo.truncate();  // replay-safe handlers only

        var consumer = kafkaConsumerFactory.create("rebuild-" + UUID.randomUUID());
        consumer.assign(allPartitions("orders"));
        consumer.seekToBeginning(consumer.assignment());

        while (true) {
            var records = consumer.poll(Duration.ofMillis(500));
            if (records.isEmpty()) break;
            for (var rec : records) {
                EventEnvelope<?> env = parse(rec);
                projectionHandler.apply(env);  // NO email side effects here
            }
        }
    }
}
```

Run during maintenance window; dual-write to v2 table then swap.

---

## Exercise 24 — CQRS projection rebuild with version checkpoints

**Task:** Store `last_processed_offset` per partition for resumable rebuild.

**Solution:**

```sql
CREATE TABLE projection_checkpoint (
  projection_name VARCHAR(64),
  topic           VARCHAR(128),
  partition       INT,
  offset          BIGINT,
  PRIMARY KEY (projection_name, topic, partition)
);
```

```java
void processBatch(ConsumerRecords<String, String> records) {
    for (var rec : records) {
        handler.apply(rec);
        checkpointRepo.save("order_summary", rec.topic(), rec.partition(), rec.offset());
    }
}
```

Resume rebuild from checkpoint instead of `seekToBeginning`.

---

## Exercise 25 — Eventual consistency UX patterns

**Task:** Design UI for "order processing" state with timeout.

**Solution:**

```typescript
// Client polls with backoff
async function waitForConfirmation(orderId: string) {
  for (let i = 0; i < 20; i++) {
    const o = await api.getOrder(orderId);
    if (o.status === 'CONFIRMED') return o;
    if (o.status === 'CANCELLED') throw new Error(o.reason);
    await sleep(Math.min(1000 * 2 ** i, 10000));
  }
  throw new TimeoutError('Still processing — check email');
}
```

Server: WebSocket or SSE push when projection updates (optional). Always show `PENDING` immediately after `201 Created`.

---

## Exercise 26 — Multi-region event ordering

**Task:** Same `orderId` events from EU and US — merge with version, not timestamp.

**Solution:**

```java
void apply(OrderEvent e) {
    var current = stateRepo.find(e.orderId());
    if (e.globalVersion() <= current.globalVersion()) return;

    // Tie-break: higher version wins; if equal use sourceRegion priority
    if (e.globalVersion() == current.globalVersion()
            && !e.sourceRegion().equals(primaryRegion)) return;

    stateRepo.save(merge(current, e));
}
```

Consider CRDTs for counters; stick to single-writer-per-aggregate where possible.

---

## Exercise 27 — Schema registry in EDA pipeline

**Task:** Register Avro schema; consumer fails fast on incompatible change.

**Solution:**

```yaml
spring.kafka.producer.value-serializer: io.confluent.kafka.serializers.KafkaAvroSerializer
spring.kafka.consumer.value-deserializer: io.confluent.kafka.serializers.KafkaAvroDeserializer
spring.kafka.properties.schema.registry.url: http://localhost:8081
```

```bash
# BACKWARD compatibility check before deploy
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  -d '{"schema": "..."}' \
  http://localhost:8081/compatibility/subjects/orders-value/versions/latest
```

CI gate: incompatible schema change blocks producer deploy.

---

## Exercise 28 — Death letter + saga recovery runbook

**Task:** `PaymentFailed` stuck in DLT; saga in `STOCK_RESERVED`; document recovery.

**Solution:**

```
1. Alert: saga stuck + DLT depth > 0
2. Query saga_instance WHERE id = :orderId → status STOCK_RESERVED
3. Inspect DLT message: PaymentFailed? Timeout? Deserialization?
4. If transient (gateway 503):
   a. Fix gateway
   b. Replay DLT → payments topic (idempotent consumer)
5. If permanent (card declined):
   a. Manually emit OrderCancelled (admin API with audit)
   b. Inventory releases stock via compensation handler
   c. Mark saga CANCELLED
6. Post-incident: add integration test for this failure path
```

```java
@PostMapping("/admin/sagas/{id}/cancel")
@PreAuthorize("hasRole('OPS')")
void forceCancel(@PathVariable String id, @RequestBody CancelReason reason) {
    audit.log("force-cancel", id, reason);
    outboxRepo.save(new OrderCancelled(id, reason.text()));
    sagaRepo.transition(id, CANCELLED);
}
```

---

## Exercise 29 — AsyncAPI event spec in repo

**Difficulty:** Basic

**Task:** Write minimal AsyncAPI 2.6 spec for `order.created` channel with JSON payload schema (`orderId`, `total`). Add kafka topic binding.

**Solution:**

```yaml
asyncapi: '2.6.0'
info: { title: Order Events, version: '1.0.0' }
channels:
  order.created:
    publish:
      message:
        payload:
          type: object
          required: [orderId, total]
          properties:
            orderId: { type: string }
            total: { type: number }
    bindings:
      kafka: { topic: orders.events }
```

**Senior takeaway:** AsyncAPI is OpenAPI for events — catalog entries should link to it.

---

## Exercise 30 — Message Pact consumer test

**Difficulty:** Hard

**Task:** Define Pact message expectation for `OrderCreated` with `orderId` matcher; verify consumer handler processes fixture.

**Solution:**

```java
@Pact(consumer = "inventory-service")
MessagePact orderCreatedPact(MessagePactBuilder builder) {
    return builder
        .given("order exists")
        .expectsToReceive("order created event")
        .withContent(new PactDslJsonBody().stringType("orderId"))
        .toPactV4();
}
```

**Senior takeaway:** Message pacts catch schema drift before integration env — pair with registry compatibility.

---

## Exercise 31 — Temporal workflow sleep sketch

**Difficulty:** Intermediate

**Task:** Pseudocode workflow: authorize payment, sleep 24h, capture — explain why DB cron saga table is weaker.

**Solution:**

```java
payment.authorize(req);
Workflow.sleep(Duration.ofHours(24));
payment.capture(req);
```

Sleep survives worker restarts via Temporal event history; cron table loses timer if scheduler down.

**Senior takeaway:** Durable timers belong in workflow engines — not `@Scheduled` on saga rows.

---

## Exercise 32 — Fatten event with API fallback flag

**Difficulty:** Intermediate

**Task:** Implement consumer: if event contains `lines`, use them; else `GET /orders/{id}`. Feature flag `inventory.use-fat-events`.

**Solution:**

```java
if (flags.isEnabled("inventory.use-fat-events") && event.lines() != null) {
    reserve(event.lines());
} else {
    reserve(orderClient.getLines(event.orderId()));
}
```

**Senior takeaway:** ECST migration is phased — metrics on API fallback traffic prove readiness to remove sync calls.

---

## Exercise 33 — GDPR erasure handler idempotency

**Difficulty:** Hard

**Task:** Table `erasure_requests(request_id PK, customer_id, done_at)`. Handler skips if `request_id` exists; anonymizes customer; marks done.

**Solution:**

```sql
CREATE TABLE erasure_requests (
  request_id VARCHAR2(36) PRIMARY KEY,
  customer_id VARCHAR2(36) NOT NULL,
  done_at TIMESTAMP
);
```

```java
@Transactional
void handle(ErasureCommand cmd) {
    if (repo.existsByRequestId(cmd.requestId())) return;
    customerRepo.anonymize(cmd.customerId());
    repo.save(new ErasureRecord(cmd.requestId(), cmd.customerId(), Instant.now()));
}
```

**Senior takeaway:** Erasure events redeliver — idempotent per `requestId` and purge all projections, not just OLTP.

---

# Weekend challenge

1. Event-storm a "cancel order" flow on paper: commands, events, policies, compensations. Photograph for revision.
2. Implement Exercises 2 + 11 + 21 in a three-module Spring Boot monorepo (order, inventory, payment) with shared outbox library.
3. Break Exercise 15 on purpose (`random.uuid` group) — measure duplicate emails in a test; fix and re-run.
4. Write AsyncAPI for your saga (Exercise 9 extended) and generate a diagram with AsyncAPI Studio.
