# Messaging / MQ — Practical Exercises

Type these. Run them. Break them. Reading is not practice.

**Structure:** Part A (Basic) · Part B (Intermediate) · Part C (Hard) · Weekend challenge  
**Stack:** Apache Artemis (JMS) or RabbitMQ; Spring Boot `spring-boot-starter-artemis` or `spring-rabbit`.

```bash
# Artemis
docker run -d --name artemis -p 61616:61616 -p 8161:8161 \
  -e ARTEMIS_USER=admin -e ARTEMIS_PASSWORD=admin \
  apache/activemq-artemis:latest

# RabbitMQ
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

`application.yml` (Artemis):

```yaml
spring.artemis:
  broker-url: tcp://localhost:61616
  user: admin
  password: admin
```

---

# Part A — Basic (10)

## Exercise 1 — Send and receive on a point-to-point queue

**Task:** Producer sends `"hello"` to `demo.queue`; listener prints it.

**Solution:**

```java
@Configuration
class JmsConfig {
    @Bean
    Queue demoQueue() { return new ActiveMQQueue("demo.queue"); }
}

@Component
class DemoProducer {
    private final JmsTemplate jms;
    DemoProducer(JmsTemplate jms) { this.jms = jms; }

    void send(String text) {
        jms.convertAndSend("demo.queue", text);
    }
}

@Component
class DemoListener {
    @JmsListener(destination = "demo.queue")
    void on(String msg) {
        log.info("received: {}", msg);
    }
}
```

```java
@SpringBootTest
class JmsBasicTest {
    @Autowired DemoProducer producer;
    @Test void sendReceive() { producer.send("hello"); }
}
```

---

## Exercise 2 — Queue vs Topic

**Task:** Two subscribers on a **topic** both receive the message; queue delivers to one consumer only.

**Solution:**

```java
@Bean Topic orderEvents() { return new ActiveMQTopic("order.events"); }

@JmsListener(destination = "order.events", containerFactory = "topicListenerFactory")
void analytics(String msg) { log.info("analytics: {}", msg); }

@JmsListener(destination = "order.events", containerFactory = "topicListenerFactory")
void notifications(String msg) { log.info("notify: {}", msg); }
```

```java
@Bean
DefaultJmsListenerContainerFactory topicListenerFactory(ConnectionFactory cf) {
    var f = new DefaultJmsListenerContainerFactory();
    f.setConnectionFactory(cf);
    f.setPubSubDomain(true);
    f.setSubscriptionDurable(true);
    f.setClientId("notify-service");
    f.setSubscriptionName("notify-sub");
    return f;
}
```

Publish once → both listeners log. On a **queue**, only one listener gets the message.

---

## Exercise 3 — Message headers / properties

**Task:** Send with `type=A`; read `JMSCorrelationID` in listener.

**Solution:**

```java
jms.send("demo.queue", session -> {
    Message msg = session.createTextMessage("payload");
    msg.setStringProperty("type", "A");
    msg.setJMSCorrelationID("corr-123");
    return msg;
});

@JmsListener(destination = "demo.queue")
void on(Message msg) throws JMSException {
    log.info("type={} corr={} body={}",
            msg.getStringProperty("type"),
            msg.getJMSCorrelationID(),
            ((TextMessage) msg).getText());
}
```

---

## Exercise 4 — JSON message conversion

**Task:** Send `OrderPlaced` POJO; receive as typed object.

**Solution:**

```java
@Bean
MessageConverter jacksonJmsMessageConverter(ObjectMapper mapper) {
    MappingJackson2MessageConverter converter = new MappingJackson2MessageConverter();
    converter.setObjectMapper(mapper);
    converter.setTypeIdPropertyName("_type");
    return converter;
}

record OrderPlaced(String orderId, long amountCents) {}

jms.convertAndSend("orders", new OrderPlaced("ord-1", 5000));

@JmsListener(destination = "orders")
void on(OrderPlaced event) {
    log.info("order {}", event.orderId());
}
```

---

## Exercise 5 — Acknowledgment modes: `AUTO` vs `CLIENT`

**Task:** Throw exception in listener; observe redelivery with `CLIENT_ACKNOWLEDGE`.

**Solution:**

```yaml
spring.jms.listener.session.acknowledge-mode: client
```

```java
@JmsListener(destination = "payments")
void on(Payment p, Message msg, Session session) throws JMSException {
    try {
        process(p);
        msg.acknowledge();
    } catch (Exception e) {
        // no ack → message redelivered
        throw e;
    }
}
```

With `AUTO_ACKNOWLEDGE`, message may be acked before your catch block — prefer `CLIENT` or transacted sessions for at-least-once you control.

---

## Exercise 6 — `JmsTemplate` request-reply

**Task:** Send message with `JMSReplyTo`; blocking receive on temp queue.

**Solution:**

```java
String response = (String) jms.sendAndReceive("rpc.queue", session -> {
    TextMessage req = session.createTextMessage("balance-request:ACC1");
    req.setJMSReplyTo(session.createTemporaryQueue());
    return req;
});
log.info("response: {}", response);
```

```java
@JmsListener(destination = "rpc.queue")
void handle(Message req, @Header("JMSReplyTo") Destination replyTo) throws JMSException {
    jms.send(replyTo, session -> session.createTextMessage("balance:1000"));
}
```

---

## Exercise 7 — Connection factory and pooling

**Task:** Configure pooled connections (avoid opening TCP per send).

**Solution:**

```xml
<dependency>
  <groupId>org.messaginghub</groupId>
  <artifactId>pooled-jms</artifactId>
</dependency>
```

```java
@Bean
ConnectionFactory pooledConnectionFactory(ActiveMQConnectionFactory amq) {
    JmsPoolConnectionFactory pool = new JmsPoolConnectionFactory();
    pool.setConnectionFactory(amq);
    pool.setMaxConnections(10);
    return pool;
}
```

---

## Exercise 8 — `@JmsListener` concurrency

**Task:** `concurrency = "3-10"` on a queue — three competing consumers.

**Solution:**

```java
@JmsListener(destination = "work.queue", concurrency = "3-10")
void process(String job) throws InterruptedException {
    Thread.sleep(100);
    log.info("done {} on {}", job, Thread.currentThread().getName());
}
```

Enqueue 100 jobs; observe parallel threads. **Ordering is not guaranteed** across consumers.

---

## Exercise 9 — Durable subscription on topic

**Task:** Subscriber offline during publish; on reconnect, receives missed messages.

**Solution:**

```java
@JmsListener(
    destination = "order.events",
    containerFactory = "durableTopicFactory",
    subscription = "inventory-service")
void onOrderEvent(String payload) { ... }
```

```java
f.setSubscriptionDurable(true);
f.setClientId("inventory-service");  // must be unique per JVM
```

Publish while listener stopped → start listener → backlog delivered.

---

## Exercise 10 — Dead letter queue (DLQ) basics

**Task:** After 3 failed deliveries, message lands in `ActiveMQ.DLQ` (Artemis) or configured DLX (Rabbit).

**Solution (Artemis):**

```xml
<!-- broker.xml excerpt -->
<address-settings>
  <address-setting match="#">
    <dead-letter-address>DLQ</dead-letter-address>
    <max-delivery-attempts>3</max-delivery-attempts>
  </address-setting>
</address-settings>
```

```java
@JmsListener(destination = "demo.queue")
void fail(String msg) {
    throw new RuntimeException("poison");
}
```

After 3 attempts, inspect DLQ in Artemis console `http://localhost:8161`.

---

# Part B — Intermediate (10)

## Exercise 11 — At-least-once redelivery and `JMSXDeliveryCount`

**Task:** Log delivery count; route to DLQ after 5 attempts.

**Solution:**

```java
@JmsListener(destination = "payments")
void on(Message msg) throws JMSException {
    int count = msg.getIntProperty("JMSXDeliveryCount");
    log.info("attempt {}", count);
    if (count >= 5) {
        jms.convertAndSend("payments.DLQ", ((TextMessage) msg).getText());
        msg.acknowledge();
        return;
    }
    throw new RuntimeException("retry");
}
```

**RabbitMQ equivalent:**

```java
@RabbitListener(queues = "payments")
void on(Message msg, Channel ch, @Header(AmqpHeaders.DELIVERY_TAG) long tag) throws IOException {
    try {
        process(msg);
        ch.basicAck(tag, false);
    } catch (Exception e) {
        ch.basicNack(tag, false, false);  // route to DLX after max retries
    }
}
```

---

## Exercise 12 — Dual-write vs outbox to a queue

**Task:** Prove crash between DB commit and JMS send causes lost message; fix with outbox.

**Broken:**

```java
@Transactional
void createOrder(Order o) {
    repo.save(o);
    jms.convertAndSend("orders", new OrderPlaced(o.getId()));  // not same TX as DB
}
```

**Solution:**

```java
@Transactional
void createOrder(Order o) {
    repo.save(o);
    outboxRepo.save(Outbox.forQueue("orders", o.getId(), event));
}

@Scheduled(fixedDelay = 500)
void publish() {
    outboxRepo.findUnsent().forEach(row -> {
        jms.convertAndSend(row.destination(), row.payload());
        row.markSent();
    });
}
```

Consumer uses `messageId` / `eventId` unique constraint for idempotency.

---

## Exercise 13 — Competing consumers and lost order

**Task:** Two listeners on one queue; produce 1..5; observe interleaving.

**Solution:**

```java
for (int i = 1; i <= 5; i++) jms.convertAndSend("seq.queue", String.valueOf(i));

@JmsListener(destination = "seq.queue", concurrency = "2")
void on(String n) {
    log.info("processed {} on {}", n, Thread.currentThread().getName());
}
// Output might be: 1, 3, 2, 5, 4
```

**When OK:** email notifications, metrics. **When not OK:** balance updates — use single consumer, message groups (JMS `JMSXGroupID`), or Kafka keyed partitions.

---

## Exercise 14 — Request-reply timeout (no temp queue leak)

**Task:** RPC with 2s timeout; server takes 10s — client must not leak resources.

**Solution:**

```java
@Bean
JmsTemplate rpcTemplate(ConnectionFactory cf) {
    JmsTemplate t = new JmsTemplate(cf);
    t.setReceiveTimeout(2000);
    return t;
}

@Test
void rpcTimesOut() {
    assertThatThrownBy(() -> jms.sendAndReceive("slow.rpc", session -> {
        TextMessage m = session.createTextMessage("ping");
        m.setJMSReplyTo(session.createTemporaryQueue());
        return m;
    })).isInstanceOf(JmsException.class);  // or null after timeout
}
```

Use `try-with-resources` for temporary queues or Spring's managed reply handling.

---

## Exercise 15 — Azure Service Bus peek-lock (Azure JD)

**Task:** Complete vs abandon vs dead-letter; show lock expiry duplicate.

**Solution:**

```java
@ServiceBusQueueTrigger(name = "payments", connection = "ServiceBus")
public void handle(ServiceBusReceivedMessage msg, ServiceBusMessageActions actions) {
    try {
        process(msg.getBody().toString());
        actions.complete(msg);           // remove from queue
    } catch (TransientException e) {
        actions.abandon(msg);            // requeue with delivery count++
    } catch (PoisonException e) {
        actions.deadLetter(msg, "BadPayload", e.getMessage());
    }
}
```

Let lock expire (don't complete within `lockDuration`) → message visible again → **duplicate processing** unless idempotency table:

```sql
CREATE TABLE processed_messages (message_id VARCHAR PRIMARY KEY);
```

---

## Exercise 16 — Prefetch / QoS fairness

**Task:** Prefetch=1000 on two consumers — slow one hoards messages.

**Solution:**

```java
@Bean
DefaultJmsListenerContainerFactory fairFactory(ConnectionFactory cf) {
    var f = new DefaultJmsListenerContainerFactory();
    f.setConnectionFactory(cf);
    f.setSessionTransacted(true);
    // Artemis: set consumerWindowSize low via connection URI or property
    return f;
}
```

**RabbitMQ:**

```yaml
spring.rabbitmq.listener.simple.prefetch: 1
```

Enqueue 100 messages; consumer A sleeps 1s, B is fast — with prefetch=1 both share fairly; with prefetch=1000 A may starve B.

---

## Exercise 17 — Message selector (and why two queues is better)

**Task:** Two consumers: `type='A'` vs `type='B'`.

**Solution:**

```java
@JmsListener(destination = "mixed", selector = "type = 'A'")
void handleA(String msg) { ... }

@JmsListener(destination = "mixed", selector = "type = 'B'")
void handleB(String msg) { ... }

jms.send("mixed", session -> {
    TextMessage m = session.createTextMessage("payload-a");
    m.setStringProperty("type", "A");
    return m;
});
```

**Refactor:** `queue.orders.typeA` and `queue.orders.typeB` — selectors scan all messages (broker-dependent cost), separate queues give clear metrics and scaling.

---

## Exercise 18 — Poison message handling playbook

**Task:** Document detect → quarantine → fix → replay for `payments.DLQ`.

**Solution:**

```
1. Alert on DLQ depth > 0
2. Inspect message headers: JMSXDeliveryCount, correlationId, timestamp
3. Classify: bad schema (fix producer) vs transient (replay) vs bug (patch + replay)
4. Replay tool:
```

```java
@JmsListener(destination = "payments.DLQ")
void inspect(TextMessage msg) throws JMSException {
    log.error("DLQ payload={} props={}", msg.getText(), extractProps(msg));
}

void replayToMain(String payload) {
    jms.convertAndSend("payments", payload);
}
```

Never blind-replay without fixing root cause.

---

## Exercise 19 — Transacted send (JMS local transaction)

**Task:** Send two messages atomically; rollback on failure.

**Solution:**

```java
jms.execute(session -> {
    MessageProducer p = session.createProducer(session.createQueue("a"));
    p.send(session.createTextMessage("1"));
    p.send(session.createTextMessage("2"));
    if (shouldFail) session.rollback();
    else session.commit();
    return null;
}, true);  // transacted
```

Only covers **broker** atomicity — not DB. For DB + queue use outbox.

---

## Exercise 20 — MQ vs Kafka decision memo

**Task:** One page: payments authorization vs clickstream analytics — pick a broker for each.

**Solution:**

| Criterion | Payments (MQ) | Clickstream (Kafka) |
|-----------|---------------|---------------------|
| Delivery | At-least-once + idempotency, DLQ per message | High throughput, replay |
| Ordering | Per-queue FIFO with single consumer | Per-key partition order |
| Retention | Delete after ack | Days/weeks log retention |
| Routing | Selectors, DLX, priority queues | Topics + consumer groups |
| Ops model | Queue depth, poison messages | Lag, partition skew |

**Pick:** Artemis/Rabbit/SQS for payment commands; Kafka for analytics event firehose. Narrate in 5 minutes.

---

# Part C — Hard (8)

## Exercise 21 — Transactional consume + single DB write

**Task:** JMS transacted session: process message and update DB in one local JMS TX **or** use outbox pattern correctly.

**Solution (outbox — production):**

```java
@JmsListener(destination = "payments")
@Transactional  // Spring DB transaction
void on(PaymentCmd cmd) {
    if (inboxRepo.exists(cmd.id())) return;
    inboxRepo.insert(cmd.id());
    ledger.credit(cmd.accountId(), cmd.amount());
    // ack happens after TX commit via DefaultJmsListenerContainerFactory sessionTransacted=false + ChainedTransactionManager if needed
}
```

**XA (avoid in microservices):**

```java
@Bean
JmsTransactionManager jmsTransactionManager(ConnectionFactory cf) {
    return new JmsTransactionManager(cf);
}
// + JtaTransactionManager for DB — slow, brittle, prefer outbox
```

---

## Exercise 22 — Message deduplication at scale

**Task:** `message_id` UUID in header; dedupe table with TTL cleanup.

**Solution:**

```sql
CREATE TABLE message_dedup (
  message_id   VARCHAR(64) PRIMARY KEY,
  processed_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ix_dedup_ts ON message_dedup (processed_at);
```

```java
@JmsListener(destination = "orders")
@Transactional
void on(Message msg) throws JMSException {
    String id = msg.getJMSMessageID();
    if (dedupRepo.exists(id)) { msg.acknowledge(); return; }
    dedupRepo.insert(id);
    process(((TextMessage) msg).getText());
}

@Scheduled(cron = "0 0 * * * *")
void purgeOld() { dedupRepo.deleteOlderThan(Duration.ofDays(7)); }
```

---

## Exercise 23 — Ordered processing with message groups

**Task:** `JMSXGroupID = orderId` — all messages for one order processed sequentially.

**Solution:**

```java
jms.send("orders", session -> {
    TextMessage m = session.createTextMessage("step-1");
    m.setStringProperty("JMSXGroupID", "order-42");
    return m;
});

@JmsListener(destination = "orders", concurrency = "5-10")
void on(String body, @Header("JMSXGroupID") String group) {
    log.info("group={} body={}", group, body);
}
```

Artemis/Rabbit (quorum queues + single active consumer) or IBM MQ message groups — semantics vary; read broker docs.

---

## Exercise 24 — Session recovery after broker failover

**Task:** Kill broker mid-consume; client reconnects; unacked messages redelivered.

**Solution:**

```yaml
spring.artemis:
  broker-url: tcp://localhost:61616
  # failover URL for cluster:
  # broker-url: tcp://host1:61616,tcp://host2:61616?ha=true&retryInterval=1000
```

```java
@JmsListener(destination = "payments")
void on(Payment p) {
    // idempotent handler required — redelivery on failover
    processIdempotent(p);
}
```

Test: `docker stop artemis` during processing → restart → verify no lost messages (at-least-once) and no duplicate side effects (idempotency).

---

## Exercise 25 — Bridge JMS → Kafka (anti-corruption layer)

**Task:** Read from `legacy.queue`, publish to `modern.topic` with schema mapping.

**Solution:**

```java
@Component
class JmsToKafkaBridge {
    @JmsListener(destination = "legacy.orders")
    void bridge(String xmlPayload) {
        OrderEvent evt = legacyXmlParser.parse(xmlPayload);
        kafkaTemplate.send("orders", evt.orderId(), avroMapper.toBytes(evt));
    }
}
```

Run bridge as separate deployable — isolates legacy from Kafka consumer groups. Monitor lag on both sides.

---

## Exercise 26 — Failover cluster (Artemis HA)

**Task:** Document primary-backup vs shared-store HA; client failover URL.

**Solution:**

```
# docker-compose excerpt — primary + backup
services:
  artemis-primary:
    image: apache/activemq-artemis:latest
    environment:
      ARTEMIS_USER: admin
      ARTEMIS_PASSWORD: admin
  artemis-backup:
    image: apache/activemq-artemis:latest
    depends_on: [artemis-primary]
```

```yaml
spring.artemis.broker-url: \
  tcp://primary:61616,tcp://backup:61616?ha=true&initialConnectAttempts=-1&reconnectAttempts=-1
```

Fail primary → clients reconnect to backup; unacked messages redelivered.

---

## Exercise 27 — Priority queue for urgent payments

**Task:** Send priority 9 (urgent) and priority 0 (bulk); urgent processed first.

**Solution:**

```java
jms.send("payments.priority", session -> {
    TextMessage m = session.createTextMessage("urgent-payment");
    // JMSPriority 0-9, default 4
    m.setJMSPriority(9);
    return m;
});
```

```xml
<address-setting match="payments.priority">
  <default-priority-delivery>true</default-priority-delivery>
</address-setting>
```

**Caveat:** Starvation of low-priority — use separate queues if SLA differs wildly.

---

## Exercise 28 — End-to-end: outbox → JMS → idempotent consumer → DLQ

**Task:** Wire full flow with integration test.

**Solution:**

```java
// 1. API creates order + outbox
// 2. Publisher sends to orders.queue
// 3. Consumer credits inventory; throws on bad SKU → DLQ after 3 tries
// 4. Inbox table prevents duplicate credit on redelivery

@Test
void fullFlow() {
    api.post("/orders", validBody());
    await().atMost(10, SECONDS).until(() -> inventory.get("SKU1") == 99);

    api.post("/orders", bodyWithBadSku());
    await().until(() -> dlqDepth("orders.DLQ") == 1);
}
```

This is the interview story: **never dual-write**; always **idempotent consumer**; **DLQ** for poison.

---

## Exercise 29 — RabbitMQ topic binding trap

**Difficulty:** Basic

**Task:** Create topic exchange `orders.topic`, queue `shipping-q` bound to `order.*`, publish with key `orders.created` — observe no delivery. Fix binding or routing key.

**Solution:**

```java
// Fix: routing key must match pattern — use "order.created" not "orders.created"
rabbitTemplate.convertAndSend("orders.topic", "order.created", payload);
```

**Senior takeaway:** AMQP routing is exact/pattern sensitive — always trace bindings in management UI.

---

## Exercise 30 — IBM MQ backout to DLQ (conceptual lab)

**Difficulty:** Intermediate

**Task:** Document MQSC commands: `BOTHRESH(3)`, `BOQNAME('PAYMENT.DLQ')`. Write JMS listener pseudo-code that rolls back on failure and completes on success.

**Solution:**

```bash
ALTER QLOCAL('PAYMENT.INPUT') BOTHRESH(3) BOQNAME('PAYMENT.DLQ')
```

```java
@JmsListener(destination = "PAYMENT.INPUT", containerFactory = "transactedFactory")
void onMessage(Message m) throws JMSException {
    try { process(m); }
    catch (Exception e) { throw new JMSException("rollback"); } // increments backout
}
```

**Senior takeaway:** MQ poison messages must escalate to DLQ — infinite rollback blocks the queue.

---

## Exercise 31 — Azure Service Bus topic + two subscriptions

**Difficulty:** Intermediate

**Task:** Sketch ARM or portal setup: topic `order-events`, subscriptions `inventory` and `audit` with SQL filter on inventory.

**Solution:**

```
Topic: order-events
Sub inventory: SqlFilter "eventType = 'OrderPlaced'"
Sub audit: (no filter)
```

Each subscription has independent cursor and DLQ after max delivery count.

**Senior takeaway:** Topics fan out; queues point-to-point — pick before writing publishers.

---

## Exercise 32 — Kafka key for order sequencing

**Difficulty:** Basic

**Task:** Prove with test: two keys interleave but single-key messages preserve order in one partition.

**Solution:**

```java
template.send("events", "order-1", "e1");
template.send("events", "order-2", "e2");
template.send("events", "order-1", "e3");
// Consumer: order-1 events always e1 before e3
```

**Senior takeaway:** Ordering is per partition key — not global across topic.

---

## Exercise 33 — JMS 2.0 shared durable listener config

**Difficulty:** Hard

**Task:** Configure Spring `DefaultJmsListenerContainerFactory` for shared durable subscription `dispatch` on topic `notifications`.

**Solution:**

```java
@Bean
DefaultJmsListenerContainerFactory sharedFactory(ConnectionFactory cf) {
    var f = new DefaultJmsListenerContainerFactory();
    f.setConnectionFactory(cf);
    f.setPubSubDomain(true);
    f.setSubscriptionShared(true);
    f.setSubscriptionDurable(true);
    return f;
}

@JmsListener(destination = "notifications", subscription = "dispatch",
    containerFactory = "sharedFactory")
void handle(TextMessage m) { ... }
```

**Senior takeaway:** Shared durable subscriptions scale topic consumption without duplicate delivery per pod.

---

# Weekend challenge

1. Map every MQ concept to Kafka: queue ≈ topic+consumer group, ack ≈ offset commit, DLQ ≈ DLT, XA ≈ outbox+EOS. Recite from memory.
2. Run Exercise 13 and 16 side by side — screenshot prefetch impact on consumer fairness.
3. Implement Exercise 12 + 28 in a scratch Spring Boot app with Artemis Testcontainer.
4. Write a one-page runbook for `payments.DLQ` depth alert (detect, triage, replay, prevent).
