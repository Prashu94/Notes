# Kafka — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**Stack:** Docker (Redpanda or Apache Kafka), Spring Boot 3 + `spring-kafka`.

```bash
# Redpanda (lightweight)
docker run -d --name redpanda -p 9092:9092 -p 9644:9644 \
  docker.redpanda.com/redpandadata/redpanda:latest \
  redpanda start --overprovisioned --smp 1 --memory 1G --reserve-memory 0M \
  --node-id 0 --check=false --kafka-addr PLAINTEXT://0.0.0.0:29092,OUTSIDE://0.0.0.0:9092 \
  --advertise-kafka-addr PLAINTEXT://redpanda:29092,OUTSIDE://localhost:9092

# Or Apache Kafka (KRaft)
docker compose -f docker/kafka-compose.yml up -d
```

`application.yml`:

```yaml
spring.kafka.bootstrap-servers: localhost:9092
spring.kafka.consumer.group-id: demo-group
spring.kafka.consumer.auto-offset-reset: earliest
```

---

# Part A — Basic (10)

## Exercise 1 — Create topic and produce via CLI

**Task:** Create `demo` with 3 partitions; produce 10 messages.

**Solution:**

```bash
docker exec -it redpanda rpk topic create demo -p 3

for i in $(seq 1 10); do
  echo "msg-$i" | docker exec -i redpanda rpk topic produce demo -k "key-$((i % 3))"
done

docker exec -it redpanda rpk topic consume demo -n 10
```

---

## Exercise 2 — Consumer group: one member, three partitions

**Task:** Start one consumer in group `g1`; observe one thread handles all partitions (lag distributed).

**Solution:**

```bash
docker exec -it redpanda rpk group describe g1  # before: no members

docker exec -it redpanda rpk topic consume demo -g g1 &
# produce more messages
for i in $(seq 11 20); do echo "lag-$i" | docker exec -i redpanda rpk topic produce demo; done

docker exec -it redpanda rpk group describe g1
# LAG column per partition
```

**Spring:**

```java
@KafkaListener(topics = "demo", groupId = "g1")
void listen(String msg) {
    log.info("got: {}", msg);
}
```

Set `spring.kafka.listener.concurrency=3` — now one consumer instance uses 3 threads (one per partition).

---

## Exercise 3 — Two consumer groups = fan-out

**Task:** Prove `g1` and `g2` each receive **all** messages.

**Solution:**

```bash
docker exec -it redpanda rpk topic consume demo -g g1 -n 5 &
docker exec -it redpanda rpk topic consume demo -g g2 -n 5 &
echo "fanout-test" | docker exec -i redpanda rpk topic produce demo
# both consumers print fanout-test
```

---

## Exercise 4 — Key ordering within a partition

**Task:** Produce 100 messages with key `order-7`; consume and verify order preserved for that key.

**Solution:**

```bash
for i in $(seq 1 100); do
  echo "order-7-seq-$i" | docker exec -i redpanda rpk topic produce demo -k order-7
done

docker exec -it redpanda rpk topic consume demo -g order-check -f '%k: %v\n' | grep '^order-7:'
# seq-1 .. seq-100 in order
```

**Java producer:**

```java
kafkaTemplate.send("demo", "order-7", "payload-" + seq);
```

Same key → same partition → order preserved **per partition only**.

---

## Exercise 5 — Manual offset commit in Spring

**Task:** Disable auto-commit; ack after processing.

**Solution:**

```yaml
spring.kafka.consumer.enable-auto-commit: false
spring.kafka.listener.ack-mode: manual
```

```java
@KafkaListener(topics = "payments", groupId = "pay-processor")
void on(ConsumerRecord<String, String> rec, Acknowledgment ack) {
    process(rec.value());
    ack.acknowledge();  // commit offset
}
```

---

## Exercise 6 — `auto-offset-reset: earliest` vs `latest`

**Task:** New group `fresh` — compare first consume with each setting.

**Solution:**

```yaml
# earliest: reads from beginning of retention
spring.kafka.consumer.auto-offset-reset: earliest

# latest: only new messages after group joins
# spring.kafka.consumer.auto-offset-reset: latest
```

```bash
# Create new group, consume once
docker exec -it redpanda rpk topic consume demo -g fresh-new -o beginning -n 3
docker exec -it redpanda rpk topic consume demo -g fresh-new -o end -n 3
```

---

## Exercise 7 — Spring `KafkaTemplate` producer with acks

**Task:** Configure `acks=all` and `retries=3`.

**Solution:**

```yaml
spring.kafka.producer.acks: all
spring.kafka.producer.retries: 3
spring.kafka.producer.properties.enable.idempotence: true
```

```java
@Service
class PaymentProducer {
    private final KafkaTemplate<String, PaymentEvent> template;

    void send(PaymentEvent evt) {
        template.send("payments", evt.orderId(), evt)
                .whenComplete((result, ex) -> {
                    if (ex != null) log.error("send failed", ex);
                    else log.info("offset={}", result.getRecordMetadata().offset());
                });
    }
}
```

---

## Exercise 8 — Topic config: partition count

**Task:** Create topic with 6 partitions; describe topic.

**Solution:**

```bash
docker exec -it redpanda rpk topic create orders -p 6 -r 1
docker exec -it redpanda rpk topic describe orders -p
```

```java
@Bean
NewTopic ordersTopic() {
    return TopicBuilder.name("orders").partitions(6).replicas(1).build();
}
```

**Senior takeaway:** Increasing partitions later does **not** redistribute existing keys — plan partition count up front for throughput targets.

---

## Exercise 9 — Consumer concurrency vs partition count

**Task:** 3 partitions, concurrency=4 — prove 4th thread is idle.

**Solution:**

```yaml
spring.kafka.listener.concurrency: 4
```

```java
@KafkaListener(topics = "demo", groupId = "g1", concurrency = "4")
void listen(ConsumerRecord<String, String> rec) {
    log.info("thread={} partition={} offset={}",
            Thread.currentThread().getName(), rec.partition(), rec.offset());
}
```

Max active consumers in a group ≤ partition count (for standard assignor).

---

## Exercise 10 — Basic error logging (no DLT yet)

**Task:** Log and skip bad JSON without crashing the container.

**Solution:**

```java
@KafkaListener(topics = "demo")
void listen(String raw) {
    try {
        mapper.readValue(raw, PaymentEvent.class);
    } catch (JsonProcessingException e) {
        log.error("bad payload: {}", raw, e);
        // Part B: route to DLT
    }
}
```

---

# Part B — Intermediate (10)

## Exercise 11 — Duplicate insert on rebalance

**Task:** Show duplicate DB rows after crash before ack; fix with unique constraint.

**Broken:**

```java
@KafkaListener(topics = "payments", groupId = "ledger")
void on(PaymentEvent p, Acknowledgment ack) {
    jdbc.update("INSERT INTO ledger(event_id, amount) VALUES (?, ?)", p.id(), p.amount());
    if (p.simulateCrash()) throw new RuntimeException("boom");
    ack.acknowledge();
}
```

**Solution:**

```sql
CREATE TABLE ledger (
  event_id VARCHAR(64) PRIMARY KEY,
  amount   BIGINT NOT NULL
);
```

```java
@KafkaListener(topics = "payments", groupId = "ledger")
void on(PaymentEvent p, Acknowledgment ack) {
    int inserted = jdbc.update(
            "INSERT INTO ledger(event_id, amount) VALUES (?, ?) ON CONFLICT DO NOTHING",
            p.id(), p.amount());
    if (inserted == 0) log.info("duplicate {}", p.id());
    ack.acknowledge();
}
```

Kill app mid-processing, restart — no duplicate rows.

---

## Exercise 12 — Auto-commit race

**Task:** Document the race: 5s processing, 1s auto-commit, exception thrown.

**Solution:**

```yaml
# RISKY
spring.kafka.consumer.enable-auto-commit: true
spring.kafka.consumer.auto-commit-interval: 1000
```

If auto-commit fires before processing completes and then processing fails, you can **lose** the message (offset advanced, not processed). If commit happens after failure depending on timing, you may **retry** — behavior is non-deterministic.

**Fix:** `enable-auto-commit: false` + manual ack after successful side effects.

---

## Exercise 13 — Dead Letter Topic (DLT)

**Task:** Route poison messages to `payments.DLT` after 2 retries.

**Solution:**

```java
@Configuration
class KafkaErrorConfig {
    @Bean
    DefaultErrorHandler errorHandler(KafkaTemplate<String, String> template) {
        var recoverer = new DeadLetterPublishingRecoverer(template,
                (rec, ex) -> new TopicPartition(rec.topic() + ".DLT", rec.partition()));
        var backoff = new FixedBackOff(1000L, 2L);
        return new DefaultErrorHandler(recoverer, backoff);
    }
}
```

```bash
docker exec -it redpanda rpk topic create payments.DLT -p 3
echo 'not-json' | docker exec -i redpanda rpk topic produce payments
docker exec -it redpanda rpk topic consume payments.DLT -n 1
```

Add Micrometer counter `kafka.dlt.published` for alerting.

---

## Exercise 14 — Compacted topic (changelog)

**Task:** Produce updates and tombstone; consume from beginning after compaction.

**Solution:**

```bash
docker exec -it redpanda rpk topic create user-state \
  -c cleanup.policy=compact \
  -c min.cleanable.dirty.ratio=0.01

docker exec -i redpanda rpk topic produce user-state -k user1 <<< '{"name":"Alice"}'
docker exec -i redpanda rpk topic produce user-state -k user1 <<< '{"name":"Bob"}'
docker exec -i redpanda rpk topic produce user-state -k user1 <<< ''  # tombstone (null value)

# Wait for compaction cycle, then:
docker exec -it redpanda rpk topic consume user-state -o beginning
# latest value for user1 is tombstone or absent
```

Use case: Kafka Streams state, CDC snapshots.

---

## Exercise 15 — Consumer lag dashboard

**Task:** Slow listener; watch lag rise and recover.

**Solution:**

```java
@KafkaListener(topics = "demo", groupId = "lag-demo")
void slow(String msg) throws InterruptedException {
    Thread.sleep(500);
    log.info(msg);
}
```

```bash
# Produce burst
for i in $(seq 1 500); do echo "burst-$i" | docker exec -i redpanda rpk topic produce demo; done

watch -n 2 'docker exec redpanda rpk group describe lag-demo'
```

**Alert rule:** `lag > 10_000 for 5m AND lag increasing` — paging, not email.

Export `kafka.consumer.lag` via Micrometer + Prometheus.

---

## Exercise 16 — Schema evolution (Avro + compatibility)

**Task:** Add optional field with default (works); add required field without default (fails).

**Solution:**

```json
// v1
{ "type": "record", "name": "Payment", "fields": [
  { "name": "id", "type": "string" },
  { "name": "amount", "type": "long" }
]}
```

```json
// v2 — BACKWARD compatible
{ "name": "amount", "type": "long" },
{ "name": "currency", "type": "string", "default": "USD" }
```

```json
// v3 — BREAKS compatibility
{ "name": "currency", "type": "string" }  // required, no default
```

```bash
# Confluent Schema Registry (if available)
curl -X POST -H "Content-Type: application/vnd.schemaregistry.v1+json" \
  --data '{"schema": "..."}' http://localhost:8081/subjects/payments-value/versions
```

---

## Exercise 17 — Transactional producer

**Task:** Send two records in one transaction; aborted TX invisible to `read_committed` consumer.

**Solution:**

```yaml
spring.kafka.producer.transaction-id-prefix: order-tx-
```

```java
@Service
class OrderEnricher {
    private final KafkaTemplate<String, String> template;

    @Transactional("kafkaTransactionManager")
    void enrich(String key, String raw, String enriched) {
        template.send("orders-raw", key, raw);
        template.send("orders-enriched", key, enriched);
    }
}
```

```yaml
spring.kafka.consumer.isolation-level: read_committed
```

Kill mid-transaction — consumer on `orders-enriched` must not see partial output.

---

## Exercise 18 — Hot key observation

**Task:** 90% of messages use key `hot`; watch single partition lag.

**Solution:**

```java
for (int i = 0; i < 1_000_000; i++) {
    String key = ThreadLocalRandom.current().nextInt(100) < 90 ? "hot" : "key-" + i;
    template.send("demo", key, "payload-" + i);
}
```

```bash
docker exec -it redpanda rpk topic describe demo -p
# One partition has vastly higher high-water mark
```

**Mitigation preview:** salt `hot` → `hot-0`..`hot-15` (Exercise 25).

---

## Exercise 19 — Transactional outbox table + publisher

**Task:** Insert business row + outbox row in same DB TX; separate publisher sends to Kafka.

**Solution:**

```sql
CREATE TABLE outbox (
  id         BIGSERIAL PRIMARY KEY,
  topic      VARCHAR(128) NOT NULL,
  key        VARCHAR(128),
  payload    TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now(),
  sent_at    TIMESTAMPTZ
);
```

```java
@Transactional
void placeOrder(Order o) {
    orderRepo.save(o);
    outboxRepo.save(new Outbox("orders", o.getId(), toJson(new OrderPlaced(o.getId()))));
}

@Scheduled(fixedDelay = 500)
void publishOutbox() {
    List<Outbox> batch = outboxRepo.findUnsent(50, FOR_UPDATE_SKIP_LOCKED);
    for (Outbox row : batch) {
        template.send(row.topic(), row.key(), row.payload());
        row.setSentAt(Instant.now());
    }
    outboxRepo.saveAll(batch);
}
```

Crash after send before mark → duplicate Kafka message → idempotent consumer (Exercise 11).

---

## Exercise 20 — Rebalance: add 4th consumer to 3 partitions

**Task:** Prove 4th consumer in group stays idle; adding 2nd **instance** rebalances partitions.

**Solution:**

```bash
# Terminal 1: consumer instance A (partitions 0,1)
# Terminal 2: consumer instance B (partition 2)
# Terminal 3: consumer instance C — idle

docker exec -it redpanda rpk group describe g1
```

During rebalance, processing pauses — use cooperative sticky assignor in production to minimize stop-the-world.

---

# Part C — Hard (8)

## Exercise 21 — EOS: consume-transform-produce in one transaction

**Task:** Read `orders`, write `orders-enriched` atomically.

**Solution:**

```java
@Bean
KafkaTransactionManager<String, String> kafkaTransactionManager(ProducerFactory<String, String> pf) {
    return new KafkaTransactionManager<>(pf);
}

@Service
class EnrichmentPipeline {
    @Transactional("kafkaTransactionManager")
    public void process(ConsumerRecord<String, String> in) {
        String enriched = enrich(in.value());
        template.send("orders-enriched", in.key(), enriched);
        // consumer offset committed in same TX when using chained listener container
    }
}
```

```yaml
spring.kafka.consumer.isolation-level: read_committed
spring.kafka.listener.ack-mode: manual_immediate
```

Requires `read_committed` on downstream consumers.

---

## Exercise 22 — Hot key salting + downstream merge

**Task:** Salt `hot` into 16 keys; merge in a state store or second stage.

**Solution:**

```java
int salt = ThreadLocalRandom.current().nextInt(16);
String saltedKey = "hot-" + salt;
template.send("demo", saltedKey, payload);

// Downstream aggregator (simplified)
@KafkaListener(topics = "demo", groupId = "hot-merger")
void merge(ConsumerRecord<String, String> rec) {
    String logicalKey = rec.key().startsWith("hot-") ? "hot" : rec.key();
    stateStore.merge(logicalKey, rec.value());
}
```

Trade-off: ordering per logical key is lost across salts — acceptable for counters, not for strict sequence.

---

## Exercise 23 — Full outbox + idempotent consumer end-to-end

**Task:** Test matrix: crash after DB commit, crash after Kafka send, duplicate delivery.

**Solution:**

| Crash point | DB state | Kafka state | Fix |
|-------------|----------|-------------|-----|
| After outbox insert | row + outbox | none | publisher retries |
| After send, before mark sent | outbox unsent | duplicate | consumer idempotency |
| After mark sent | sent | ok | none |

```java
// Consumer
@KafkaListener(topics = "orders")
void on(OrderPlaced e) {
    inboxRepo.insertIgnore(e.eventId());  // PK violation = already processed
    projectionService.apply(e);
}
```

Integration test with `@DirtiesContext` and embedded Kafka + Testcontainers Postgres.

---

## Exercise 24 — Exactly-once payment flow (design + code sketch)

**Task:** `PaymentAuthorized` must update balance once even with retries.

**Solution:**

```sql
CREATE TABLE processed_events (event_id VARCHAR PRIMARY KEY, processed_at TIMESTAMPTZ);
CREATE TABLE accounts (id VARCHAR PRIMARY KEY, balance BIGINT);
```

```java
@Transactional
void handle(PaymentAuthorized e) {
    if (processedEvents.exists(e.id())) return;
    processedEvents.insert(e.id());
    accounts.credit(e.accountId(), e.amount());
}
```

Kafka EOS reduces duplicates; **DB idempotency** is still required for external side effects.

---

## Exercise 25 — Rebalance storm under deploy

**Task:** Rolling deploy 3 pods; observe rebalance churn; tune `session.timeout.ms` and cooperative assignor.

**Solution:**

```yaml
spring.kafka.consumer.properties.partition.assignment.strategy: \
  org.apache.kafka.clients.consumer.CooperativeStickyAssignor
spring.kafka.consumer.properties.session.timeout.ms: 45000
spring.kafka.consumer.properties.heartbeat.interval.ms: 15000
spring.kafka.listener.shutdown-timeout: 30s
```

```bash
kubectl rollout restart deployment/order-consumer
# Watch consumer group members flip
docker exec -it redpanda rpk group describe order-consumer
```

Use static membership (`group.instance.id`) where supported to reduce rebalance on restart.

---

## Exercise 26 — DLT replay strategy

**Task:** Admin endpoint replays `payments.DLT` to `payments` with rate limit; skip if already in inbox.

**Solution:**

```java
@PostMapping("/admin/dlt/replay")
void replay(@RequestParam(defaultValue = "100") int limit) {
    try (var consumer = dltConsumerFactory.create()) {
        consumer.assign(List.of(new TopicPartition("payments.DLT", 0)));
        var records = consumer.poll(Duration.ofSeconds(5));
        for (var rec : records) {
            if (inboxRepo.exists(extractEventId(rec))) continue;
            template.send("payments", rec.key(), rec.value());
        }
    }
}
```

Guard with auth + audit log. Fix root cause before mass replay.

---

## Exercise 27 — Transactional outbox + Kafka transactions together

**Task:** When you need both DB and Kafka atomicity — document limits.

**Solution:**

```
┌─────────────┐     same TX      ┌────────┐
│ App         │ ───────────────► │ outbox │
│ placeOrder()│                  └────────┘
└─────────────┘
       │ publisher (separate process)
       ▼
   Kafka (at-least-once)
       │
       ▼
  idempotent consumer
```

Kafka transactions **do not** include your Postgres commit. Pattern: outbox for DB→Kafka; Kafka TX for Kafka→Kafka only.

---

## Exercise 28 — Partition count change breaks key order

**Task:** Increase partitions 3→6; explain why `order-7` messages may interleave with older sequence.

**Solution:**

```bash
docker exec -it redpanda rpk topic alter-config demo --set max.message.bytes=1048576
# Increase partitions (tool-specific):
docker exec -it redpanda rpk topic add-partitions demo --num 3  # 3→6
```

```java
// partition = hash(key) % numPartitions
// numPartitions changed → same key may map to different partition
```

**Rule:** Never increase partitions if strict per-key ordering is required unless you drain and replay with a new topic.

---

## Exercise 29 — Kafka Connect JDBC sink DLQ config

**Difficulty:** Intermediate

**Task:** Document a connector JSON with `errors.tolerance=all` and DLQ topic. Explain what happens when one record fails deserialization.

**Solution:**

```json
"errors.tolerance": "all",
"errors.deadletterqueue.topic.name": "connect-dlq",
"errors.deadletterqueue.context.headers.enable": "true"
```

Failed record → DLQ with headers; other records continue. Alert on DLQ count > 0.

**Senior takeaway:** Connect error tolerance trades strictness for uptime — monitor DLQ like any consumer lag.

---

## Exercise 30 — Kafka Streams word count (local)

**Difficulty:** Basic

**Task:** Run Kafka Streams app counting words from `input` topic to `output` topic. Verify with `kafka-console-consumer`.

**Solution:**

```java
builder.stream("input")
    .flatMapValues(v -> Arrays.asList(v.toLowerCase().split("\\W+")))
    .groupBy((k, v) -> v)
    .count()
    .toStream()
    .to("output", Produced.with(Serdes.String(), Serdes.Long()));
```

**Senior takeaway:** Streams embeds in Spring Boot — no separate Flink cluster for simple aggregations.

---

## Exercise 31 — Topic retention vs cost worksheet

**Difficulty:** Basic

**Task:** For topic `audit-events` (500 GB/day, 7-year retention), estimate local-disk cost vs tiered S3. Set `retention.ms` and `local.retention.ms` values you would propose.

**Solution:**

| Option | Rough math |
|--------|------------|
| Local only | 500GB × 365 × 7 ≈ 1.27 PB — prohibitive |
| Tiered | 7d local hot + S3 cold — ~90% cost reduction |

```properties
retention.ms=220752000000
local.retention.ms=604800000
```

**Senior takeaway:** Long retention belongs in tiered storage or warehouse sink — not broker NVMe alone.

---

## Exercise 32 — KRaft controller quorum sketch

**Difficulty:** Intermediate

**Task:** Write `server.properties` snippet for 3-node KRaft quorum (no ZK). List one ops task ZK used to do that KRaft replaces.

**Solution:**

```properties
process.roles=broker,controller
controller.quorum.voters=1@k1:9093,2@k2:9093,3@k3:9093
```

ZK task replaced: metadata storage and controller election — now internal Raft log.

**Senior takeaway:** New clusters should start on KRaft; plan ZK migration with vendor runbook.

---

## Exercise 33 — MM2 loop prevention regex

**Difficulty:** Hard

**Task:** Given bidirectional clusters `us` and `eu`, write `topics.exclude` so `us.orders` mirrored to `eu` is not replicated back to `us` infinitely.

**Solution:**

```properties
# On eu cluster connector consuming from us
topics.exclude=eu\\..*,.*checkpoints,.*heartbeats
```

**Senior takeaway:** Active-active Kafka requires naming discipline — MM2 will not resolve write conflicts for you.

---

# Weekend challenge

1. Draw on paper: producer acks, leader, ISR, consumer group, offset commit, DB unique key. Narrate duplicate payment in 3 minutes.
2. Run Exercises 11 + 19 + 23 as one mini-project: outbox publisher + idempotent consumer + chaos test (kill -9 mid-flight).
3. Produce 1M messages with 90% hot key; screenshot partition lag skew; implement salting and show improved spread.
4. Configure Prometheus alert on DLT publish rate > 0 for 1 minute.
