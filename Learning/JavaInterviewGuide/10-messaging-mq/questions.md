# Messaging / MQ (JMS, IBM MQ, Rabbit) — 50 Senior Interview Questions

**Bar:** Contrast with Kafka, transactional messaging, poison, HA. Bank JDs still say MQ.

### 1. What is a message queue vs a log?

**Short answer:** A message queue delivers each message to one competing consumer and typically removes it after acknowledgment. A log (Kafka) retains messages by offset so many independent consumer groups can replay history. MQ brokers support both point-to-point queues and pub/sub topics with broker-managed deletion—not offset-based replay. In production, the trade-off shows up in on-call incidents and reconciliation jobs — not in hello-world demos.

#### What it is
A queue is a work-distribution buffer: producers send, one consumer in a group receives, processing completes, message is gone (or moved to DLQ). A log is an append-only, partitioned stream where consumption advances a cursor without deleting data for others. JMS Queue vs Topic maps to these patterns; Kafka topics behave like retained logs with consumer-group cursors.

#### How it works (internals)
On IBM MQ, a queue manager stores messages in queues until GET+commit or expiry; depth reflects backlog. Kafka brokers append to partition logs and trim by retention/compaction policies. RabbitMQ routes through exchanges to queues with ack-based removal. Competing consumers on one MQ queue share work round-robin; Kafka consumer groups assign partitions exclusively. Replay on MQ requires copying messages or logging sidecars; on Kafka it is a first-class offset reset.

#### When to use / when NOT to use
Use queues when you need task distribution, request buffering, and 'process once' semantics with mature ops (payments, mainframe handoff). Use logs when you need fan-out analytics, replay, stream processing, and high-throughput event backbones. Do not call Kafka a drop-in MQ replacement in regulated batch/online systems without a migration plan.

#### Production example
A payment capture service puts ISO 20022 payloads on an IBM MQ queue; three Spring `@JmsListener` instances compete for work. Fraud scoring reads the same business events from Kafka for replay and model retraining. The queue guarantees operational handoff; the log guarantees audit and reprocessing.

#### Common mistakes
Saying 'we use Kafka as our queue' while ignoring retention cost and duplicate handling on consumer crash. Assuming MQ messages are replayable like Kafka offsets. Using a queue for broadcast (wrong pattern—use topic or log).

#### Interview follow-ups (with model answers)

**Q:** How does at-least-once differ between MQ ack and Kafka commit?
**A:** For «What is a message queue vs a log»: How does at-least-once differ between MQ ack and Kafka commit. In production, A payment capture service puts ISO 20022 payloads on an IBM MQ queue; three Spring `@JmsListener` instances compete for work. Fraud scoring reads the same business events from Kafka for replay and model retraining. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What happens to unconsumed MQ messages after broker restart with persistent delivery?
**A:** The follow-on risk of «What happens to unconsumed MQ messages after broker restart with persistent delivery» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When would you run both MQ and Kafka in one flow?
**A:** Trade-off framing for «When would you run both MQ and Kafka in one flow»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on What is a message queue vs a log.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: A payment capture service puts ISO 20022 payloads on an IBM MQ queue; three Spring `@JmsListener` instances compete for work.. I suspect saying 'we use kafka as our queue' while ignoring retention cost and duplicate handling on consumer crash until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
// JMS queue: message removed after successful processing + ack
@JmsListener(destination = "PAYMENT.IN")
public void onPayment(TextMessage msg) throws JMSException {
    paymentService.capture(msg.getText());
    // AUTO_ACKNOWLEDGE commits when method returns
}
```

---

### 2. JMS 2.0 core objects.

**Short answer:** JMS models messaging through ConnectionFactory, Connection, Session, MessageProducer/Consumer, Destination (Queue or Topic), and Message subtypes. Sessions control acknowledgment and transactions; Spring wraps this with JmsTemplate and @JmsListener containers that manage thread-safe session lifecycle. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
JMS (Java Message Service) is the standard Java API abstracting IBM MQ, ActiveMQ Artemis, HornetMQ, and Rabbit via Qpid JMS. Version 2.0 simplified API (context, shared consumers) while keeping the same object graph underneath.

#### How it works (internals)
ConnectionFactory creates Connection (TCP/SSL to broker). Connection creates Session with ack mode and transacted flag. Session creates Destination, Producer, Consumer, and Message. Producers send; consumers receive synchronously or via MessageListener. AUTO_ACKNOWLEDGE acks after listener returns; CLIENT_ACKNOWLEDGE requires explicit message.acknowledge(); transacted sessions commit/rollback as a unit. Spring's DefaultMessageListenerContainer opens one session per consumer thread.

#### When to use / when NOT to use
Use JMS when integrating Java services with enterprise brokers (especially IBM MQ in banks). Prefer JMS 2.0 APIs and Spring Boot auto-config. Avoid hand-rolling Connection/Session in every request—use JmsTemplate or listener containers.

#### Production example
Spring Boot configures `ConnectionFactory` from `spring.jms.*`; `@JmsListener` on `SETTLEMENT.OUT` with `sessionTransacted=true` pairs with `JmsTransactionManager` and `@Transactional` for local JMS+DB coordination (still not XA unless configured).

#### Common mistakes
Leaking Connection/Session without close in finally blocks. Sharing one Session across @Async threads (not thread-safe). Confusing Connection (heavy) with Session (per-thread) pooling.

#### Interview follow-ups (with model answers)

**Q:** What did JMS 2.0 add over 1.1?
**A:** For «JMS 2.0 core objects»: What did JMS 2.0 add over 1.1. In production, Spring Boot configures `ConnectionFactory` from `spring.jms.*`; `@JmsListener` on `SETTLEMENT. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Spring cache ConnectionFactory vs Session?
**A:** The follow-on risk of «How does Spring cache ConnectionFactory vs Session» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Queue vs Topic at the Destination level?
**A:** Trade-off framing for «Queue vs Topic at the Destination level»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on JMS 2.0 core objects.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Spring Boot configures `ConnectionFactory` from `spring.jms.*`; `@JmsListener` on `SETTLEMENT.. I suspect leaking connection/session without close in finally blocks until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Configuration
@EnableJms
public class JmsConfig {
    @Bean
    public DefaultJmsListenerContainerFactory factory(ConnectionFactory cf) {
        var f = new DefaultJmsListenerContainerFactory();
        f.setConnectionFactory(cf);
        f.setSessionAcknowledgeMode(Session.CLIENT_ACKNOWLEDGE);
        return f;
    }
}
```

---

### 3. JMS session concurrency.

**Short answer:** A JMS Session is not thread-safe: one session per consumer thread. Spring listener containers create dedicated sessions per listener thread; never share a Session across executor pools or @Async workers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Session holds acknowledgment state, transaction boundary, and consumer/producer handles. Concurrent use corrupts internal broker protocol state and causes subtle ack bugs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Classic JMS 1.1 required one thread per session. JMS 2.0 allows some sharing patterns with JMSContext but Spring JMS still maps one session per consumer thread in DefaultMessageListenerContainer. Concurrency is scaled by `concurrency=3-10` on @JmsListener (multiple sessions), not by sharing one session. Producers from JmsTemplate typically borrow a session from a pool per operation.

#### When to use / when NOT to use
Scale consumers by increasing listener concurrency or deploying more pods each with their own sessions. Do not pass Session into shared singleton services. For high throughput, increase competing consumers on the queue (accept ordering loss) or partition work across multiple queues.

#### Production example
Payment listener at `concurrency=5` runs five threads each with its own Session consuming from `PAYMENTS.PENDING`. Throughput rises linearly until DB or downstream limits; queue depth alerts catch saturation before thread explosion.

#### Common mistakes
Caching a Session in a @Service field used by multiple threads. Setting concurrency=50 on a queue backed by a fragile downstream with no backpressure. Assuming @JmsListener is async to HTTP thread without understanding it blocks a listener thread.

#### Interview follow-ups (with model answers)

**Q:** Is JMSContext thread-safe in JMS 2.0?
**A:** For «JMS session concurrency»: Is JMSContext thread-safe in JMS 2.0. In production, Payment listener at `concurrency=5` runs five threads each with its own Session consuming from `PAYMENTS.PENDING`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does prefetch interact with multiple sessions?
**A:** The follow-on risk of «How does prefetch interact with multiple sessions» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What limits max useful concurrency on one queue?
**A:** Trade-off framing for «What limits max useful concurrency on one queue»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on JMS session concurrency.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment listener at `concurrency=5` runs five threads each with its own Session consuming from `PAYMENTS.PENDING`.. I suspect caching a session in a @service field used by multiple threads until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 4. Delivery modes: persistent vs non-persistent.

**Short answer:** Persistent delivery asks the broker to write messages to durable storage before acknowledging the producer; non-persistent keeps messages in memory and they are lost on broker crash. For money movement and compliance trails, persistent is mandatory. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
JMS DeliveryMode.PERSISTENT vs NON_PERSISTENT maps to broker-specific persistence (IBM MQ logs, Rabbit durable queues, etc.). It is the MQ analogue of caring about durability before ack—not exactly Kafka acks=all but the same business question.

#### How it works (internals)
Producer sets delivery mode on send (or default on session). Broker persists to disk/transacted log for persistent messages before returning success to producer. Consumers still ack separately—persistence protects against broker loss, not duplicate processing. IBM MQ also has persistence at queue definition level; Rabbit combines delivery mode with durable queue and publisher confirms.

#### When to use / when NOT to use
Persistent for payments, settlements, audit events, anything that must survive broker restart. Non-persistent for metrics, ephemeral notifications, or loss-tolerant telemetry where latency matters more. Never default non-persistent in prod without explicit sign-off.

#### Production example
Wire transfer initiation uses JmsTemplate with deliveryMode=PERSISTENT to `WIRE.OUT`; ops monitors queue depth and channel status. Real-time UI tickers use NON_PERSISTENT with accept-on-loss documented in runbooks.

#### Common mistakes
Assuming persistent delivery means exactly-once to the consumer. Setting persistent but using non-durable queues on Rabbit. Ignoring disk full conditions that block persistent puts.

#### Interview follow-ups (with model answers)

**Q:** How does persistence interact with transacted sessions?
**A:** For «Delivery modes: persistent vs non-persistent»: How does persistence interact with transacted sessions. In production, Wire transfer initiation uses JmsTemplate with deliveryMode=PERSISTENT to `WIRE.OUT`; ops monitors queue depth and channel status. Real-time UI tickers use NON_PERSISTENT with accept-on-loss documented in runbooks. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Rabbit publisher confirms vs JMS persistent—compare?
**A:** The follow-on risk of «Rabbit publisher confirms vs JMS persistent—compare» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is the latency cost of persistent on IBM MQ?
**A:** Trade-off framing for «What is the latency cost of persistent on IBM MQ»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Delivery modes: persistent vs non-persis.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Wire transfer initiation uses JmsTemplate with deliveryMode=PERSISTENT to `WIRE.OUT`; ops monitors queue depth and channel status.. I suspect assuming persistent delivery means exactly-once to the consumer until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 5. Acknowledge modes.

**Short answer:** Ack modes define when the broker considers a message consumed: AUTO after listener success, CLIENT on explicit ack, DUPS_OK with lazy batching, or transacted commit. Crash after processing but before ack causes redelivery—at-least-once is normal; design idempotent consumers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Acknowledgment is the contract between consumer and broker for removing or redelivering messages. Wrong mode choice causes duplicates, loss, or stuck poison loops. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
AUTO_ACKNOWLEDGE: broker acks when MessageListener returns without exception—most common with @JmsListener. CLIENT_ACKNOWLEDGE: you call message.acknowledge(); cumulative behavior varies by provider (ack one may ack all prior on session). DUPS_OK allows duplicate delivery under failure for performance. Transacted session: commit() acks all consumed in transaction; rollback redelivers. IBM MQ syncpoint ties to unit of work.

#### When to use / when NOT to use
AUTO for simple idempotent handlers. CLIENT when you need batch ack after multiple messages or fine-grained control (know your broker). Transacted for multiple operations in one JMS UOW. Never mix ack semantics you do not understand in payment paths.

#### Production example
Settlement consumer uses CLIENT_ACK only after Oracle insert succeeds; crash mid-flight redelivers and idempotency table dedupes. AUTO on a listener that swallows exceptions causes silent message loss (acked despite failure). Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Catching exceptions without rethrow in AUTO mode (message lost). Using CLIENT and acking before DB commit. Assuming transacted JMS also rolls back JDBC without XA.

#### Interview follow-ups (with model answers)

**Q:** What is poison message behavior under AUTO vs transacted?
**A:** For «Acknowledge modes»: What is poison message behavior under AUTO vs transacted. In production, Settlement consumer uses CLIENT_ACK only after Oracle insert succeeds; crash mid-flight redelivers and idempotency table dedupes. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does IBM MQ BACKOUT interact with ack?
**A:** The follow-on risk of «How does IBM MQ BACKOUT interact with ack» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare to Kafka manual commit timing?
**A:** Trade-off framing for «Compare to Kafka manual commit timing»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Acknowledge modes.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Settlement consumer uses CLIENT_ACK only after Oracle insert succeeds; crash mid-flight redelivers and idempotency table dedupes.. I suspect catching exceptions without rethrow in auto mode (message lost) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 6. XA vs local TX vs outbox.

**Short answer:** XA coordinates JMS and JDBC in one two-phase commit (2PC)—theoretically atomic but operationally painful (in-doubt transactions, recovery, vendor tuning). Local transactions on each resource risk dual-write. The transactional outbox pattern—write business data + outbox row in one DB TX, then publish to MQ—is usually the better production default. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
XA (JTA) uses TransactionManager (Atomikos, Narayana) to enlist ConnectionFactory and DataSource as XAResources. Outbox decouples DB commit from message publish while preserving consistency via a relay process. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
2PC: prepare phase on all resources, then commit or rollback together. Failure leaves in-doubt state requiring XA recovery scans—IBM MQ + Oracle pairs still exist in banks. Local: @Transactional on DB + separate JmsTemplate send—crash between commit and send loses or duplicates messages. Outbox: same local TX inserts Order + OutboxEvent; Debezium or polling publisher sends to MQ after commit; consumer idempotency handles duplicates.

#### When to use / when NOT to use
Choose outbox for new microservices unless hard requirement for single global TX with mainframe. XA when integrating with legacy CICS/MQ/Oracle stacks that mandate it and ops team owns recovery. Avoid XA 'because it sounds safer' without measuring in-doubt incidents.

#### Production example
Team replaced Atomikos XA (frequent heuristic rollbacks) with outbox table + Spring `@Scheduled` relay to IBM MQ; duplicate MQ messages handled by natural key in consumer. Documented why XA was removed for auditors. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Believing XA gives exactly-once end-to-end (only coordinated commit, not consumer side). Outbox without idempotent consumer. XA timeout misconfiguration causing partial commits.

#### Interview follow-ups (with model answers)

**Q:** What is an in-doubt transaction and who resolves it?
**A:** For «XA vs local TX vs outbox»: What is an in-doubt transaction and who resolves it. In production, Team replaced Atomikos XA (frequent heuristic rollbacks) with outbox table + Spring `@Scheduled` relay to IBM MQ; duplicate MQ messages handled by natural key in consumer. Documented why XA was removed for auditors. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Narayana recovery work on pod restart?
**A:** The follow-on risk of «How does Narayana recovery work on pod restart» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Debezium outbox vs polling publisher trade-offs?
**A:** Trade-off framing for «Debezium outbox vs polling publisher trade-offs»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on XA vs local TX vs outbox.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Team replaced Atomikos XA (frequent heuristic rollbacks) with outbox table + Spring `@Scheduled` relay to IBM MQ; duplicate MQ messages handled by natural key i…. I suspect believing xa gives exactly-once end-to-end (only coordinated commit, not consumer side) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Transactional
public void placeOrder(Order o) {
    orderRepo.save(o);
    outboxRepo.save(new Outbox("OrderCreated", o.getId()));
    // After commit, relay publishes to MQ — not in same @Transactional without XA
}
```

---

### 7. IBM MQ specifics (high level).

**Short answer:** IBM MQ centers on queue managers, queues, channels, and message descriptors (MQMD). Messages carry persistence, priority, correlation id, and RFH2 headers for JMS mapping. Syncpoint, clustering, and RDQM provide HA; CCSID/encoding mismatches and MQRC_BACKED_OUT are common production debug paths. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
IBM MQ is the incumbent broker in financial services—mainframe z/OS, distributed Linux queue managers, and cloud-managed offerings. JMS is one client API; native MQ also uses MQI and MQSC administration. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Queue manager owns queues and channels (sender/receiver/client). Messages have MQMD (format, persistence, reply-to queue, correlId). PUT under syncpoint until COMMIT. Trigger monitors start channels or apps when depth > 0. Clustering routes to queue instances. MQRC_BACKED_OUT after max backout count moves message to backout queue. JMS over MQ maps destinations to queue names and RFH2 for properties.

#### When to use / when NOT to use
Know IBM MQ when interviewing at banks, insurance, or government integrators. Debug channel status (RUNNING vs RETRYING), listener port, SSL cipher mismatch, and authority records. Do not bluff channel troubleshooting—describe a real AMQ error you fixed.

#### Production example
Channel `TO.CORE.BANK` stuck RETRYING due to wrong SSL peer name; `runmqsc` DISPLAY CHSTATUS revealed RC. CCSID 1208 vs EBCDIC 500 on mainframe bridge caused MO encoding errors until uniform UTF-8 policy.

#### Common mistakes
Ignoring backout queue depth. Hardcoding queue names without cluster alias. Putting credentials in MQSC scripts committed to git.

#### Interview follow-ups (with model answers)

**Q:** What is the difference between local and remote queue definitions?
**A:** For «IBM MQ specifics (high level)»: What is the difference between local and remote queue definitions. In production, Channel `TO.CORE.BANK` stuck RETRYING due to wrong SSL peer name; `runmqsc` DISPLAY CHSTATUS revealed RC. CCSID 1208 vs EBCDIC 500 on mainframe bridge caused MO encoding errors until uniform UTF-8 policy. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does triggered queue start an application?
**A:** The follow-on risk of «How does triggered queue start an application» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** RDQM vs traditional multi-instance QM?
**A:** Trade-off framing for «RDQM vs traditional multi-instance QM»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on IBM MQ specifics (high level).

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Channel `TO.CORE.BANK` stuck RETRYING due to wrong SSL peer name; `runmqsc` DISPLAY CHSTATUS revealed RC.. I suspect ignoring backout queue depth until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 8. Poison messages in MQ.

**Short answer:** A poison message fails processing repeatedly; brokers track delivery count (JMSXDeliveryCount) and after a threshold back out to a dead/backout queue. Without this, infinite redelivery burns CPU and blocks healthy messages behind a bad payload. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Poison messages have valid broker delivery but application-level permanent failure—schema mismatch, bad business key, corrupt payload—not transient downstream outage. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ increments BackoutCount; exceeding BACKOUTTHRESHOLD triggers MQRC_BACKED_OUT and routes to BOQ. Rabbit uses DLX after max retries. JMS listeners should not catch-all and rethrow forever—configure max redeliveries and DLQ routing. Alert on backout queue age and depth, not just main queue.

#### When to use / when NOT to use
Always configure backout/DLQ with threshold (often 3–5). Separate poison quarantine from retry queue for transient errors. Replay tooling with schema fix for poison, not blind requeue.

#### Production example
Bad ISO date in one message caused 10k redeliveries/sec until BACKOUTTHRESHOLD moved it to `PAYMENTS.BOQ`; PagerDuty on BOQ depth > 0; support replays after fix with audit trail. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Infinite retry on NumberFormatException. Same queue for retry and poison without TTL/delay. No access control on backout queue (operators delete evidence).

#### Interview follow-ups (with model answers)

**Q:** How do you distinguish poison from transient failure?
**A:** For «Poison messages in MQ»: How do you distinguish poison from transient failure. In production, Bad ISO date in one message caused 10k redeliveries/sec until BACKOUTTHRESHOLD moved it to `PAYMENTS.BOQ`; PagerDuty on BOQ depth > 0; support replays after fix with audit trail. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What headers expose delivery count in JMS?
**A:** The follow-on risk of «What headers expose delivery count in JMS» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Safe replay procedure from backout queue?
**A:** Trade-off framing for «Safe replay procedure from backout queue»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Poison messages in MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Bad ISO date in one message caused 10k redeliveries/sec until BACKOUTTHRESHOLD moved it to `PAYMENTS.. I suspect infinite retry on numberformatexception until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 9. Request-reply on MQ.

**Short answer:** Request-reply uses JMSReplyTo destination plus JMSCorrelationID (or MessageId) to match responses. Temporary queues or dedicated reply queues per service; clients must enforce timeouts. Pattern works for low-volume integration—not for high-scale synchronous RPC (prefer HTTP/gRPC). In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Asynchronous request-reply decouples caller and responder over MQ while preserving correlation. Common in mainframe and legacy service bus patterns. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Requester sends message with ReplyTo set (temp queue or `SERVICE.REPLY`) and CorrelationID. Responder reads request, sends reply to ReplyTo with same CorrelationID. Requester blocks on receive with selector or correlation consumer. Temp queues avoid naming collisions but leak if not deleted. IBM MQ supports report messages and alternate reply queue fields in MQMD.

#### When to use / when NOT to use
Use for legacy bus integration, batch file triggers with status return, moderate-volume internal RPC where HTTP is unavailable. Avoid for user-facing latency-sensitive paths or fan-out query patterns. Kafka request-reply exists but same scale limits apply.

#### Production example
Mainframe posts inquiry to `INQUIRY.IN` with ReplyTo `INQUIRY.REPLY` and UUID correlId; Java service responds within 30s SLA; client uses receive timeout and dead-letter on expiry.

#### Common mistakes
No timeout on blocking receive (thread pool exhaustion). Shared reply queue without correlation selector (wrong reply to wrong client). Creating temp queue per request without session close.

#### Interview follow-ups (with model answers)

**Q:** Temp queue vs fixed reply queue trade-offs?
**A:** For «Request-reply on MQ»: Temp queue vs fixed reply queue trade-offs. In production, Mainframe posts inquiry to `INQUIRY.IN` with ReplyTo `INQUIRY.REPLY` and UUID correlId; Java service responds within 30s SLA; client uses receive timeout and dead-letter on expiry. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Spring JmsTemplate sendAndReceive work?
**A:** The follow-on risk of «How does Spring JmsTemplate sendAndReceive work» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Correlation id vs MessageGroupID for matching?
**A:** Trade-off framing for «Correlation id vs MessageGroupID for matching»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Request-reply on MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Mainframe posts inquiry to `INQUIRY.IN` with ReplyTo `INQUIRY.. I suspect no timeout on blocking receive (thread pool exhaustion) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
jmsTemplate.setReceiveTimeout(30_000);
Message reply = jmsTemplate.sendAndReceive("INQUIRY.IN", session -> {
    TextMessage req = session.createTextMessage(payload);
    req.setJMSReplyTo(session.createQueue("INQUIRY.REPLY"));
    req.setJMSCorrelationIDAsBytes(uuid.getBytes(StandardCharsets.UTF_8));
    return req;
});
```

---

### 10. Topic vs queue in JMS.

**Short answer:** A JMS Queue delivers each message to exactly one consumer among competing subscribers (point-to-point). A Topic broadcasts to all active subscribers; durable subscribers retain a cursor for offline clients. Kafka consumer groups resemble durable topic consumption with partition-level competing—hybrid semantics. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Queue = work sharing. Topic = publish/subscribe fan-out. Choosing wrong destination type breaks integration contracts silently (multiple processors or missed subscribers).

#### How it works (internals)
Queue: multiple consumers compete; one wins per message. Topic: each subscriber gets a copy; non-durable miss messages while offline. Durable subscription (clientId + name) stores cursor on broker. Rabbit maps topic exchanges + bindings; IBM MQ has topics and subscriptions. Kafka partitions add ordered shards with one consumer per partition per group.

#### When to use / when NOT to use
Queue for task distribution and load leveling. Topic for domain events all services must observe (with durable subs where needed). Do not use topic when you need exactly-one worker—use queue.

#### Production example
OrderPlaced published to topic `orders.events` for email, inventory, analytics subscribers. Payment execution tasks go to queue `payments.execute` with competing workers.

#### Common mistakes
Using topic for payment processing (double spend risk with multiple consumers). Durable subs without cleanup after service decommission (disk fill). Confusing Kafka topic with JMS topic semantics.

#### Interview follow-ups (with model answers)

**Q:** When do you need durable vs non-durable topic subscriber?
**A:** For «Topic vs queue in JMS»: When do you need durable vs non-durable topic subscriber. In production, OrderPlaced published to topic `orders.events` for email, inventory, analytics subscribers. Payment execution tasks go to queue `payments.execute` with competing workers. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does shared subscription work in JMS 2.0?
**A:** The follow-on risk of «How does shared subscription work in JMS 2.0» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Map this to Rabbit fanout vs work queue?
**A:** Trade-off framing for «Map this to Rabbit fanout vs work queue»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Topic vs queue in JMS.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: OrderPlaced published to topic `orders.events` for email, inventory, analytics subscribers. Payment execution tasks go to queue `payments.. I suspect using topic for payment processing (double spend risk with multiple consumers) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 11. Durable subscription.

**Short answer:** A durable topic subscription survives consumer disconnect: broker stores messages for subscriber name + clientId until consumed or expired. Non-durable subscribers only receive messages while connected. Ops must delete obsolete durables or disks fill. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Durable subscriptions give pub/sub with offline catch-up—like a named cursor on a topic distinct from competing queue consumers. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Create connection with setClientID (unique per JVM instance or carefully pooled). Session.createDurableSubscriber(topic, subscriptionName). Broker retains messages for that subscription. Unsubscribe when decommissioning. IBM MQ and Artemis track durable subs; misconfigured clientId causes 'subscription already exists' on restart.

#### When to use / when NOT to use
Use when a service must not miss topic events during deploy or network blip. Not for every subscriber—ephemeral read models can be non-durable with cache rebuild from log/MQ replay. Clean up durables in IaC/runbooks.

#### Production example
Inventory service uses durable sub `inventory-order-events` with clientId `inventory-pod-${HOSTNAME}`; blue/green requires coordinated clientId strategy or shared durable with competing shared consumer (JMS 2.0). Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Duplicate clientId across pods (only one connects). Forgot unsubscribe—messages accumulate forever. Durable on high-volume topic without retention policy.

#### Interview follow-ups (with model answers)

**Q:** clientId uniqueness in Kubernetes?
**A:** For «Durable subscription»: clientId uniqueness in Kubernetes. In production, Inventory service uses durable sub `inventory-order-events` with clientId `inventory-pod-${HOSTNAME}`; blue/green requires coordinated clientId strategy or shared durable with competing shared consumer (JMS 2.0). I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Durable subscription vs queue for single consumer?
**A:** The follow-on risk of «Durable subscription vs queue for single consumer» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to migrate subscription name safely?
**A:** Trade-off framing for «How to migrate subscription name safely»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Durable subscription.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Inventory service uses durable sub `inventory-order-events` with clientId `inventory-pod-${HOSTNAME}`; blue/green requires coordinated clientId strategy or shar…. I suspect duplicate clientid across pods (only one connects) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 12. Message selectors.

**Short answer:** JMS message selectors filter messages with SQL-like expressions on headers and properties (e.g., JMSPriority > 5 AND region = 'EU'). Broker evaluates before delivery—convenient but CPU-heavy at scale; separate queues often scale better. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Selectors push filtering to the broker so consumers only receive matching messages from a shared destination. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Selector string uses JMS header names and custom properties set by producer. Consumer createConsumer(dest, selector). Not all brokers optimize equally—high fan-in with complex selectors can peg CPU. IBM MQ supports selectors on durable subs; wrong syntax fails at createConsumer time.

#### When to use / when NOT to use
Use for low-volume multi-tenant queues or admin tooling. Prefer dedicated queues or routing keys (Rabbit) for high throughput paths. Document selector expressions in contract tests.

#### Production example
Single `NOTIFICATIONS` queue with selectors `type = 'SMS'` vs `type = 'EMAIL'` replaced by separate queues after CPU spike during marketing campaign. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Complex selectors on hot queues. Relying on selector for security isolation (use ACLs and separate destinations). Property type mismatch (string '1' vs int 1).

#### Interview follow-ups (with model answers)

**Q:** Selector vs Rabbit routing key?
**A:** For «Message selectors»: Selector vs Rabbit routing key. In production, Single `NOTIFICATIONS` queue with selectors `type = 'SMS'` vs `type = 'EMAIL'` replaced by separate queues after CPU spike during marketing campaign. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Performance impact on IBM MQ?
**A:** The follow-on risk of «Performance impact on IBM MQ» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Can selectors see message body?
**A:** Trade-off framing for «Can selectors see message body»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Message selectors.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Single `NOTIFICATIONS` queue with selectors `type = 'SMS'` vs `type = 'EMAIL'` replaced by separate queues after CPU spike during marketing campaign.. I suspect complex selectors on hot queues until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 13. RabbitMQ exchange types.

**Short answer:** Rabbit routes via exchanges: direct (exact routing key), topic (pattern), fanout (broadcast), headers (rare). Messages bind to queues through routing rules; dead-letter exchange (DLX) handles failures. Quorum queues (3.8+) improve durability over classic mirrored queues. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
RabbitMQ is an AMQP broker often chosen for flexible routing in Java/Spring ecosystems—not a log, not IBM MQ, but excellent for work queues and pub/sub with policies. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer publishes to exchange with routing key; bindings connect exchange to queues. Fanout ignores routing key. Topic uses `*` and `#` wildcards. DLX + TTL implements retry and poison paths. Quorum queues use Raft for replication; classic queues deprecated for HA. Kafka lacks this routing graph—often needs more topics or stream joins.

#### When to use / when NOT to use
Pick Rabbit when routing topology is complex and volume is moderate. Use Kafka for high-throughput retained streams. Use IBM MQ when bank standard mandates it. Do not assume Spring AMQP abstracts away DLX semantics.

#### Production example
Order events: topic exchange `orders` with keys `orders.created.uk`, bound to regional fulfillment queues. Failed processing after 3 retries dead-letters to `orders.dlx` for manual review.

#### Common mistakes
Publishing directly to queue name in Rabbit (works but bypasses exchange design). Classic mirrored queues on 3.13+ without migration plan. No DLX—poison blocks main queue.

#### Interview follow-ups (with model answers)

**Q:** Quorum vs classic queue when?
**A:** For «RabbitMQ exchange types»: Quorum vs classic queue when. In production, Order events: topic exchange `orders` with keys `orders.created.uk`, bound to regional fulfillment queues. Failed processing after 3 retries dead-letters to `orders.dlx` for manual review. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does priority queue interact with prefetch?
**A:** The follow-on risk of «How does priority queue interact with prefetch» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare fanout to JMS topic?
**A:** Trade-off framing for «Compare fanout to JMS topic»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on RabbitMQ exchange types.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order events: topic exchange `orders` with keys `orders.created.uk`, bound to regional fulfillment queues.. I suspect publishing directly to queue name in rabbit (works but bypasses exchange design) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Bean
TopicExchange ordersExchange() { return new TopicExchange("orders"); }

@Bean
Binding ukBinding(Queue ukQueue, TopicExchange ordersExchange) {
    return BindingBuilder.bind(ukQueue).to(ordersExchange).with("orders.created.uk");
}
```

---

### 14. Prefetch / QoS.

**Short answer:** Prefetch (Rabbit basicQos, IBM MQ uncommitted message limit, JMS consumer window) caps unacknowledged messages per consumer. Too high causes one greedy consumer to hoard work; too low leaves consumers idle. Tune with queue depth, processing time, and fairness goals. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
QoS prefetch is the broker-side flow control for how much work in-flight each consumer may hold before ack—analogous to Kafka max.poll.records but tied to acknowledgment, not poll batch alone.

#### How it works (internals)
Rabbit channel.basicQos(prefetchCount, global). IBM MQ GET with unlimited uncommitted msgs starves peers. Spring AMQP sets prefetch on listener container factory. High prefetch + slow consumer = large invisible backlog on one consumer. Zero prefetch can increase round-trips.

#### When to use / when NOT to use
Start prefetch ≈ concurrent processing capacity per thread (often 1–10 for heavy DB work, higher for light tasks). Measure queue age distribution across consumers. Reduce prefetch when messages are large or memory-bound.

#### Production example
Payment listeners at prefetch=1 ensured even distribution across five consumers; previously prefetch=250 left one pod with 200 unacked msgs while others idle. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Default unlimited prefetch on Rabbit with slow handler. Same prefetch for 1KB and 10MB messages. Ignoring prefetch when scaling concurrency.

#### Interview follow-ups (with model answers)

**Q:** Prefetch vs Kafka fetch.min.bytes?
**A:** For «Prefetch / QoS»: Prefetch vs Kafka fetch.min.bytes. In production, Payment listeners at prefetch=1 ensured even distribution across five consumers; previously prefetch=250 left one pod with 200 unacked msgs while others idle. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Global vs per-consumer QoS in Rabbit?
**A:** The follow-on risk of «Global vs per-consumer QoS in Rabbit» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** IBM MQ equivalent settings?
**A:** Trade-off framing for «IBM MQ equivalent settings»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Prefetch / QoS.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment listeners at prefetch=1 ensured even distribution across five consumers; previously prefetch=250 left one pod with 200 unacked msgs while others idle.. I suspect default unlimited prefetch on rabbit with slow handler until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 15. Competing consumers and ordering.

**Short answer:** Multiple consumers on one queue destroy global FIFO order—messages process in parallel and may complete out of order. Strict ordering requires single consumer, single thread, or message grouping (IBM MQ) / partition key (Kafka)—each with scale limits. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Competing consumers scale throughput by parallelizing work at the cost of ordering guarantees across the queue. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Broker delivers round-robin or similar to active consumers. Requeue and redelivery further reorder. IBM MQ message groups (GroupId) pin a group to one consumer at a time for partial order. Kafka achieves per-key order via partition assignment. Classic JMS queue without grouping: no order guarantee.

#### When to use / when NOT to use
Accept out-of-order for independent payments. Use grouping/partition for account-level serialization. Do not add consumers and expect sequence numbers to hold without design.

#### Production example
Account balance updates used MQ message grouping by accountId so one consumer owns each account; cross-account payments still parallel. Adding a sixth consumer without groups broke statement ordering. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming JMSQueue is FIFO with five listeners. Using priority to fake ordering. Scaling consumers during month-end without grouping analysis.

#### Interview follow-ups (with model answers)

**Q:** Message group hot spot problem?
**A:** For «Competing consumers and ordering»: Message group hot spot problem. In production, Account balance updates used MQ message grouping by accountId so one consumer owns each account; cross-account payments still parallel. Adding a sixth consumer without groups broke statement ordering. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When is single consumer enough?
**A:** The follow-on risk of «When is single consumer enough» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare to Kafka partition count planning?
**A:** Trade-off framing for «Compare to Kafka partition count planning»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Competing consumers and ordering.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Account balance updates used MQ message grouping by accountId so one consumer owns each account; cross-account payments still parallel.. I suspect assuming jmsqueue is fifo with five listeners until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 16. Message grouping / correlation.

**Short answer:** JMSCorrelationID links request-reply pairs; JMSXGroupID (IBM MQ MessageGroupId) forces ordered processing of related messages by one consumer. Correlation is for matching; grouping is for affinity—both reduce chaos in distributed messaging. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Correlation identifies related messages across destinations; grouping assigns a sequence of messages to the same consumer for order within the group. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer sets JMSXGroupID on all messages for one account session. Broker delivers group messages to same consumer until group ends (JMSGroupSeq or flags). Hot group id becomes hot partition—one consumer overloaded. CorrelationID typically UUID bytes on request and copied to reply.

#### When to use / when NOT to use
Use correlation for RPC patterns. Use grouping when business requires in-order handling per entity and competing consumers otherwise break it. Prefer Kafka partitions for large-scale keyed order.

#### Production example
Wire batch: GroupId=wireFileId keeps file records ordered; CorrelationID ties status response to originating API request in ops dashboard. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Same GroupId for all messages (defeats competing consumers). Confusing CorrelationID with business idempotency key. No end-of-group marker where provider requires it.

#### Interview follow-ups (with model answers)

**Q:** GroupId vs Kafka message key?
**A:** For «Message grouping / correlation»: GroupId vs Kafka message key. In production, Wire batch: GroupId=wireFileId keeps file records ordered; CorrelationID ties status response to originating API request in ops dashboard. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What happens on consumer crash mid-group?
**A:** The follow-on risk of «What happens on consumer crash mid-group» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Max group size limits on IBM MQ?
**A:** Trade-off framing for «Max group size limits on IBM MQ»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Message grouping / correlation.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Wire batch: GroupId=wireFileId keeps file records ordered; CorrelationID ties status response to originating API request in ops dashboard.. I suspect same groupid for all messages (defeats competing consumers) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 17. TTL and DLQ.

**Short answer:** Time-to-live (expiration) removes or dead-letters messages after a period—broker-specific whether expired msgs go to DLQ or drop silently. TTL is not a substitute for business timeout monitoring; alert on DLQ age and expired counts. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Message expiration limits staleness—e.g., price quotes valid 60 seconds. DLQ (dead-letter queue) holds messages that failed processing or expired for inspection.

#### How it works (internals)
JMS setJMSExpiration(timestamp) or broker policy per queue. Rabbit TTL per message or queue with DLX. IBM MQ EXPIRY field and dead-letter handling. Expired message must not be processed silently without metrics—track `expired` counter.

#### When to use / when NOT to use
TTL for time-sensitive offers and session tokens. DLQ for all failure paths with retention policy. Do not rely on TTL alone to cancel long-running business processes—use workflow state + compensating actions.

#### Production example
FX quote messages TTL 30s; expired route to `QUOTES.EXPIRED` monitored dashboard. Payment retry queue TTL 24h then DLQ for manual reconciliation.

#### Common mistakes
TTL without DLQ (silent loss). Very long TTL filling disk. Using message expiration as only timeout while consumer still processes stale payload.

#### Interview follow-ups (with model answers)

**Q:** Per-message vs queue-level TTL?
**A:** For «TTL and DLQ»: Per-message vs queue-level TTL. In production, FX quote messages TTL 30s; expired route to `QUOTES.EXPIRED` monitored dashboard. Payment retry queue TTL 24h then DLQ for manual reconciliation. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Who consumes DLQ in production?
**A:** The follow-on risk of «Who consumes DLQ in production» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare Kafka retention to MQ TTL?
**A:** Trade-off framing for «Compare Kafka retention to MQ TTL»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on TTL and DLQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: FX quote messages TTL 30s; expired route to `QUOTES.EXPIRED` monitored dashboard. Payment retry queue TTL 24h then DLQ for manual reconciliation.. I suspect ttl without dlq (silent loss) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 18. Idempotent consumers (same as Kafka).

**Short answer:** MQ redelivery on crash before ack is normal—consumers must dedupe by business key in DB (insert unique constraint, upsert, or processed-events table). Same idempotency story as Kafka at-least-once; exactly-once effect requires application design, not broker magic. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Idempotent consumer: processing the same message twice produces the same system state as once—essential for payments and ledger updates. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Store messageId or business idempotency key in table with UNIQUE constraint before side effects. On duplicate, skip or return success. Outbox relay duplicates require same guard. XA does not remove need for consumer idempotency on redelivery after commit uncertainty.

#### When to use / when NOT to use
Mandatory for all non-read-only handlers. Use natural keys (paymentId) over broker message id when business meaning matters. TTL old idempotency rows per compliance retention.

#### Production example
Consumer checks `processed_events(message_id)` before crediting account; duplicate redelivery after pod kill hits unique constraint and exits cleanly. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Only-once assumption because 'MQ is reliable.' Using JMSMessageID alone when producer retries create new ids. No cleanup of idempotency table (unbounded growth).

#### Interview follow-ups (with model answers)

**Q:** Idempotency key vs deduplication header?
**A:** For «Idempotent consumers (same as Kafka)»: Idempotency key vs deduplication header. In production, Consumer checks `processed_events(message_id)` before crediting account; duplicate redelivery after pod kill hits unique constraint and exits cleanly. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How long to retain idempotency records?
**A:** The follow-on risk of «How long to retain idempotency records» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Partial failure after side effect?
**A:** Trade-off framing for «Partial failure after side effect»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Idempotent consumers (same as Kafka).

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Consumer checks `processed_events(message_id)` before crediting account; duplicate redelivery after pod kill hits unique constraint and exits cleanly.. I suspect only-once assumption because 'mq is reliable until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Transactional
public void onPayment(String paymentId, String payload) {
    if (processedRepo.existsById(paymentId)) return;
    processedRepo.save(new ProcessedEvent(paymentId));
    ledgerService.credit(payload);
}
```

---

### 19. Large messages.

**Short answer:** Brokers enforce max message size (IBM MQ MAXMSGL, Rabbit frame limits); sending multi-MB payloads hurts memory and channels. Claim-check pattern stores blob in S3/DB and sends pointer + metadata on the queue. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Large message handling separates payload storage from messaging control plane—queue carries reference, not the blob. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer uploads file to object storage, puts `{bucket, key, checksum}` JSON on queue. Consumer fetches blob, validates checksum, processes, deletes or archives. IBM MQ has message segmentation for native large messages but claim-check is more portable. Compress only if CPU trade-off measured.

#### When to use / when NOT to use
Claim-check above ~1MB or org policy threshold. Native segmentation when both ends are same MQ version and ops approves. Never base64 huge files into JMS TextMessage.

#### Production example
Mortgage document pipeline: scan to S3, MQ message 2KB with s3:// URI; downstream fetches via IAM role; queue depth stays manageable during peak uploads. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Inline 50MB PDF in JMS BytesMessage crashing heap. No virus scan on fetched blob. Orphan S3 objects without lifecycle when message lost.

#### Interview follow-ups (with model answers)

**Q:** IBM MQ segmentation vs claim-check?
**A:** For «Large messages»: IBM MQ segmentation vs claim-check. In production, Mortgage document pipeline: scan to S3, MQ message 2KB with s3:// URI; downstream fetches via IAM role; queue depth stays manageable during peak uploads. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to enforce size at producer?
**A:** The follow-on risk of «How to enforce size at producer» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Rabbit message size limits?
**A:** Trade-off framing for «Rabbit message size limits»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Large messages.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Mortgage document pipeline: scan to S3, MQ message 2KB with s3:// URI; downstream fetches via IAM role; queue depth stays manageable during peak uploads.. I suspect inline 50mb pdf in jms bytesmessage crashing heap until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 20. Spring `@JmsListener` vs `@KafkaListener`.

**Short answer:** Both annotate methods for async consumption but differ in scaling model (JMS threads/competing consumers vs Kafka partitions), ordering, replay, and ops. Similar Spring programming model hides very different broker semantics—senior interviews test that you know what's underneath. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
@JmsListener drives JMS MessageListener containers; @KafkaListener drives KafkaConsumer poll loops with partition assignment and offset commits. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
JMS: concurrency property scales threads/sessions on same queue; ordering fragile. Kafka: scale consumers up to partition count; per-partition order; replay by resetting offsets. JMS redelivery via broker; Kafka via offset not committed. Spring Boot auto-configures factories for both but TX managers differ (JmsTransactionManager vs KafkaTransactionManager/Chained).

#### When to use / when NOT to use
JMS for IBM MQ/Rabbit enterprise integration. Kafka for event backbone, analytics, stream processing. Do not pick based on annotation ergonomics alone.

#### Production example
Same team runs `@JmsListener` on MQ for payment execution and `@KafkaListener` on audit topic—shared idempotency utility, separate monitoring (queue depth vs consumer lag). Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Copy-paste Kafka concurrency settings to JMS. Expect Kafka-style replay from MQ. Single-thread Kafka consumer with 50 partitions (40 idle).

#### Interview follow-ups (with model answers)

**Q:** Can one service use both in one TX?
**A:** For «Spring `@JmsListener` vs `@KafkaListener`»: Can one service use both in one TX. In production, Same team runs `@JmsListener` on MQ for payment execution and `@KafkaListener` on audit topic—shared idempotency utility, separate monitoring (queue depth vs consumer lag). I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Error handler differences?
**A:** The follow-on risk of «Error handler differences» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Testing strategy for each?
**A:** Trade-off framing for «Testing strategy for each»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Spring `@JmsListener` vs `@KafkaListener.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Same team runs `@JmsListener` on MQ for payment execution and `@KafkaListener` on audit topic—shared idempotency utility, separate monitoring (queue depth vs co…. I suspect copy-paste kafka concurrency settings to jms until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@JmsListener(destination = "PAY.IN", concurrency = "3-5")
public void onMq(Message msg) { ... }

@KafkaListener(topics = "audit.events", groupId = "audit-svc")
public void onKafka(AuditEvent evt) { ... }
```

---

### 21. Why banks still have MQ.

**Short answer:** Banks retain IBM MQ for mainframe/CICS integration, decades of operational runbooks, XA with Oracle, regulatory comfort, and sunk licensing—not because Kafka is inferior for all use cases. Kafka is added for analytics and event backbone; MQ replacement is a multi-year migration, not a weekend project. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Enterprise messaging in financial services is as much org and compliance as technology—MQ skills, vendor support, and proven disaster recovery matter. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Core banking still posts to MQ from z/OS; distributed Java consumes via channels. Batch settlement windows, guaranteed delivery, and existing monitoring on queue depth/channel status are entrenched. Kafka excels at replay and fan-out but does not replace CICS trigger or SWIFT gateway patterns overnight.

#### When to use / when NOT to use
In bank interviews, acknowledge coexistence: MQ for operational transaction bus, Kafka for data platform. Propose strangler patterns (bridge, dual publish) not rip-and-replace rhetoric. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Tier-1 bank runs 200+ queue managers globally; new cloud-native services use Kafka for customer analytics while wire transfers stay on MQ until certified end-to-end on new stack. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Claiming 'Kafka replaces MQ everywhere.' Dismissing MQ as legacy without naming integration constraints. Ignoring ops team skills and on-call runbooks.

#### Interview follow-ups (with model answers)

**Q:** What would a migration roadmap look like?
**A:** For «Why banks still have MQ»: What would a migration roadmap look like. In production, Tier-1 bank runs 200+ queue managers globally; new cloud-native services use Kafka for customer analytics while wire transfers stay on MQ until certified end-to-end on new stack. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Regulatory concerns with log retention?
**A:** The follow-on risk of «Regulatory concerns with log retention» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cost comparison MQ licensing vs Kafka ops?
**A:** Trade-off framing for «Cost comparison MQ licensing vs Kafka ops»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Why banks still have MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Tier-1 bank runs 200+ queue managers globally; new cloud-native services use Kafka for customer analytics while wire transfers stay on MQ until certified end-to…. I suspect claiming 'kafka replaces mq everywhere until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 22. Bridge MQ ↔ Kafka.

**Short answer:** Connectors or custom adapters copy messages between MQ and Kafka with at-least-once delivery, header mapping, and idempotent sinks. Ordering and exactly-once illusions break at the boundary—design for duplicates and partial ordering loss. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Bridge components integrate legacy MQ flows with modern Kafka event platforms without big-bang rewrites. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ source/sink connectors (Kafka Connect), Spring listener to KafkaTemplate, or IBM Event Streams bridge. Map JMSCorrelationID to Kafka headers; preserve business id. Consumer idempotency on both sides. Partition key from accountId may reorder relative to MQ FIFO. Error handling: DLQ on both brokers with correlation for trace.

#### When to use / when NOT to use
Use for gradual migration, analytics tap on operational MQ traffic, or feeding data lake from core systems. Not for synchronous request-reply without latency budget. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
MQ listener on `TRADE.EXEC` publishes to Kafka `trades.executed` with idempotent producer keys; fraud team consumes Kafka without touching MQ credentials.

#### Common mistakes
Header loss breaking correlation. Assuming 1:1 ordering preserved. No monitoring on bridge lag (Kafka consumer lag + MQ depth).

#### Interview follow-ups (with model answers)

**Q:** Kafka Connect vs custom Spring bridge?
**A:** For «Bridge MQ ↔ Kafka»: Kafka Connect vs custom Spring bridge. In production, MQ listener on `TRADE.EXEC` publishes to Kafka `trades.executed` with idempotent producer keys; fraud team consumes Kafka without touching MQ credentials. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Schema evolution across boundary?
**A:** The follow-on risk of «Schema evolution across boundary» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Handling MQ backout in bridge?
**A:** Trade-off framing for «Handling MQ backout in bridge»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Bridge MQ ↔ Kafka.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: MQ listener on `TRADE.EXEC` publishes to Kafka `trades.executed` with idempotent producer keys; fraud team consumes Kafka without touching MQ credentials.. I suspect header loss breaking correlation until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 23. Backpressure.

**Short answer:** When a queue fills, producers block or fail—that is intentional backpressure protecting downstream. Monitor queue depth and oldest message age; size capacity for peak + headroom. Kafka producers buffer then block or fail when `max.block.ms` exceeded—same discipline, different metrics. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Backpressure signals consumers cannot keep pace; without it, brokers OOM or latency explodes silently. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ CURDEPTH vs MAXDEPTH; put calls fail with MQRC_Q_FULL. Rabbit memory alarms pause publishers. JMS send may block on full queue depending on config. Producers should handle failures with retry and circuit break—not unbounded async send. Scale consumers or fix slow path before raising depth limits blindly.

#### When to use / when NOT to use
Treat full queue as alert, not normal. Capacity plan for 2× peak with consumer SLA. Use backpressure-friendly APIs (reactive limits) at edge services feeding MQ.

#### Production example
Black Friday: `ORDER.IN` depth hit 80% MAXDEPTH; autoscaled listener pods; temporary throttle on HTTP checkout when depth > threshold—documented degradation policy. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Raising MAXDEPTH to 'fix' slowness (masks root cause). No alert on oldest message age. Fire-and-forget send without syncpoint on critical path.

#### Interview follow-ups (with model answers)

**Q:** Compare Rabbit memory alarm to MQ Q_FULL?
**A:** For «Backpressure»: Compare Rabbit memory alarm to MQ Q_FULL. In production, Black Friday: `ORDER.IN` depth hit 80% MAXDEPTH; autoscaled listener pods; temporary throttle on HTTP checkout when depth > threshold—documented degradation policy. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When to reject vs block producers?
**A:** The follow-on risk of «When to reject vs block producers» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Kafka buffer tuning analog?
**A:** Trade-off framing for «Kafka buffer tuning analog»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Backpressure.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Black Friday: `ORDER.IN` depth hit 80% MAXDEPTH; autoscaled listener pods; temporary throttle on HTTP checkout when depth > threshold—documented degradation pol…. I suspect raising maxdepth to 'fix' slowness (masks root cause) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 24. High availability.

**Short answer:** MQ HA uses multi-instance queue managers, RDQM (replicated data), active/passive pairs, or cluster with shared repositories—failover must be tested, not diagrammed. Split-brain and message affinity during failover are common interview deep dives. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
High availability keeps messaging online through hardware, network, or site failure with acceptable RPO/RTO for persistent messages. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ: multi-instance QM (active/standby), RDQM with consensus replication, queue manager clusters with full repository. Failover moves queue manager; in-flight transactions may need XA recovery. Rabbit quorum queues survive node loss. Channels reconnect with retry intervals—tune heartbeats.

#### When to use / when NOT to use
Match HA tier to message criticality—payments cluster with sync replication; dev single instance fine. Run game-day failover drills quarterly. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Active/passive MQ pair; failover drill found DNS still pointed to old host—fixed automation; RTO improved from 45m to 8m. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
HA on paper only—never tested channel restart. Ignoring message affinity after failover (ordering surprises). Single network path for 'HA' pair.

#### Interview follow-ups (with model answers)

**Q:** RDQM vs traditional MI queue manager?
**A:** For «High availability»: RDQM vs traditional MI queue manager. In production, Active/passive MQ pair; failover drill found DNS still pointed to old host—fixed automation; RTO improved from 45m to 8m. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** RPO for persistent messages in failover?
**A:** The follow-on risk of «RPO for persistent messages in failover» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Split-brain detection?
**A:** Trade-off framing for «Split-brain detection»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing High availability.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Active/passive MQ pair; failover drill found DNS still pointed to old host—fixed automation; RTO improved from 45m to 8m.. I suspect ha on paper only—never tested channel restart until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 25. Security.

**Short answer:** Secure MQ with TLS on channels, authentication (LDAP, certificates, OAuth on cloud offerings), authorization on queue/object level, and secret hygiene—never commit passwords in MQSC or Spring properties to git. Message-level encryption exists but is rare; transport + network segmentation is typical. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Messaging security spans wire encryption, identity, least-privilege access to queues, and audit of admin actions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ: CHLAUTH rules, SSL cipher specs, CONNAUTH. Rabbit: users, vhosts, permissions. Rotate credentials via vault; Spring Cloud Config or K8s secrets. Separate prod/test queue managers. Log administrative commands.

#### When to use / when NOT to use
TLS everywhere for cross-datacenter channels. Principle of least privilege per app identity (only PUT to X, GET from Y). Regular access reviews for backout queues.

#### Production example
Pen test found app using MQ admin credentials—replaced with read/write-only channel auth records per service account; MQSC scripts parameterized from vault. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Shared MQ admin password across 50 apps. CHLAUTH `ADDRESSMAP('*')` ALLOW in prod. Plaintext channel on internal 'trusted' VLAN myth.

#### Interview follow-ups (with model answers)

**Q:** Certificate rotation without downtime?
**A:** For «Security»: Certificate rotation without downtime. In production, Pen test found app using MQ admin credentials—replaced with read/write-only channel auth records per service account; MQSC scripts parameterized from vault. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** mTLS between microservice and MQ?
**A:** The follow-on risk of «mTLS between microservice and MQ» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Audit requirements for message access?
**A:** Trade-off framing for «Audit requirements for message access»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Security.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Pen test found app using MQ admin credentials—replaced with read/write-only channel auth records per service account; MQSC scripts parameterized from vault.. I suspect shared mq admin password across 50 apps until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 26. Poison vs application error.

**Short answer:** Schema validation failure or unknown message type is poison—route to DLQ immediately, no retry. Transient downstream 503 warrants limited retry with backoff then DLQ. Mixing both in one retry policy causes infinite poison loops or lost legitimate retries. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Classification drives retry vs quarantine policy—the same exception handler must not treat all failures identically. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Use exception taxonomy: JsonProcessingException → DLQ + alert; RestClientException → retry 3× with delay queue; DB unique violation on idempotency → ack success. Spring ErrorHandler or DefaultRequeueRejected=false with custom routing. Metrics by failure class.

#### When to use / when NOT to use
Document matrix in runbook. Automate replay only for transient class after fix. Poison requires code or schema change before replay.

#### Production example
Listener routed `UnknownProductCode` straight to BOQ; `TimeoutException` to retry queue with 5m TTL × 3 then BOQ—support dashboard shows counts by class. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Retry everything 10 times. Same DLQ for schema poison and 'DB down for 2 minutes.' Logging stack trace without classification tag.

#### Interview follow-ups (with model answers)

**Q:** How does Spring JMS ErrorHandler help?
**A:** For «Poison vs application error»: How does Spring JMS ErrorHandler help. In production, Listener routed `UnknownProductCode` straight to BOQ; `TimeoutException` to retry queue with 5m TTL × 3 then BOQ—support dashboard shows counts by class. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Rabbit retry plugin vs manual?
**A:** The follow-on risk of «Rabbit retry plugin vs manual» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Alerting thresholds per class?
**A:** Trade-off framing for «Alerting thresholds per class»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Poison vs application error.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Listener routed `UnknownProductCode` straight to BOQ; `TimeoutException` to retry queue with 5m TTL × 3 then BOQ—support dashboard shows counts by class.. I suspect retry everything 10 times until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 27. `JmsTemplate.execute` and sessions.

**Short answer:** JmsTemplate wraps Connection/Session lifecycle for sends and synchronous receives—use execute/callback for advanced session operations without leaking resources. Pair transacted JMS with JmsTransactionManager and Spring @Transactional for coordinated local JMS transactions. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
JmsTemplate is Spring's JMS counterpart to JdbcTemplate—resource management and exception translation for producers and request-reply. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
send(), convertAndSend(), receive() borrow connections from cache. execute(SessionCallback) gives raw Session for batch puts or custom properties. sessionTransacted=true on factory participates in JmsTransactionManager—commit on TX success. Same proxy pitfalls as @Transactional (self-invocation skips TX).

#### When to use / when NOT to use
Prefer template over manual JMS code. Use execute when you need MessageProducer tweaks per send. Enable transactions only when multiple JMS ops must atomic commit.

#### Production example
Batch job uses execute to send 100 messages in one transacted session commit; failure rolls back entire batch—no partial orphan messages. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Manual Session without Spring sync—connection leak under error. @Transactional on private method expecting JMS TX. Mixing JmsTemplate send inside JDBC @Transactional without outbox/XA.

#### Interview follow-ups (with model answers)

**Q:** CachingConnectionFactory settings?
**A:** For «`JmsTemplate.execute` and sessions»: CachingConnectionFactory settings. In production, Batch job uses execute to send 100 messages in one transacted session commit; failure rolls back entire batch—no partial orphan messages. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When is sendAndReceive an anti-pattern?
**A:** The follow-on risk of «When is sendAndReceive an anti-pattern» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** JmsTransactionManager vs ChainedTransactionManager?
**A:** Trade-off framing for «JmsTransactionManager vs ChainedTransactionManager»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on `JmsTemplate.execute` and sessions.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Batch job uses execute to send 100 messages in one transacted session commit; failure rolls back entire batch—no partial orphan messages.. I suspect manual session without spring sync—connection leak under error until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
jmsTemplate.execute(session -> {
    MessageProducer producer = session.createProducer(session.createQueue("BATCH.OUT"));
    for (String line : lines) {
        producer.send(session.createTextMessage(line));
    }
    return null;
}, true); // transacted session
```

---

### 28. Conversation pattern vs fire-and-forget.

**Short answer:** Fire-and-forget sends a message with no response expected—ideal for events and commands with async outcomes. Conversation pattern chains multiple correlated messages into stateful dialog (saga steps on MQ)—powerful but complex; prefer explicit saga state in DB with simple messages. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Fire-and-forget decouples producer from consumer timing. Conversation models multi-step workflows entirely over messaging headers and body state machines. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
JMS may use SOAP/JMS or proprietary conversation IDs in RFH2. Each step expects specific reply correlId. Failure mid-conversation requires timeout and compensation. Modern microservices favor orchestrated/choreographed saga with DB state + domain events instead of broker-held conversation state.

#### When to use / when NOT to use
Fire-and-forget for OrderCreated, PaymentRequested. Avoid conversation for new greenfield—use workflow engine or saga table. Legacy mainframe may require conversation—integrate via adapter.

#### Production example
Replaced MQ conversation wire protocol with outbox + state machine table; MQ carries single Command messages; saga status queryable via API instead of correlating five queues. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Hidden state only in message headers—undebuggable. No timeout on conversation step 3 of 5. Building new features on IBM conversation APIs without team expertise.

#### Interview follow-ups (with model answers)

**Q:** Choreography vs orchestration on MQ?
**A:** For «Conversation pattern vs fire-and-forget»: Choreography vs orchestration on MQ. In production, Replaced MQ conversation wire protocol with outbox + state machine table; MQ carries single Command messages; saga status queryable via API instead of correlating five queues. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to test multi-step MQ flows?
**A:** The follow-on risk of «How to test multi-step MQ flows» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is conversation unavoidable?
**A:** Trade-off framing for «When is conversation unavoidable»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Conversation pattern vs fire-and-forget.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Replaced MQ conversation wire protocol with outbox + state machine table; MQ carries single Command messages; saga status queryable via API instead of correlati…. I suspect hidden state only in message headers—undebuggable until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 29. Priority queues.

**Short answer:** JMS priority (0–9) and Rabbit x-max-priority let urgent messages jump ahead—but low priority can starve indefinitely. Separate queues with SLA tiers often beat single priority queue in production. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Priority is a broker ordering hint when consumers are busy; it does not add capacity and can hide systemic overload. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Higher priority dequeued first when messages pending. Starvation of low priority during continuous high-priority load. IBM MQ supports priority on MQMD; not all consumers respect strict ordering with multiple sessions.

#### When to use / when NOT to use
Use sparingly for true emergencies (fraud hold release). Prefer dedicated fast-lane queue + dedicated consumer pool for SLA tiers. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
VIP payment queue `PAYMENTS.PRIORITY` with two dedicated listeners; standard traffic on `PAYMENTS.STANDARD`—avoided starvation on single priority-enabled queue.

#### Common mistakes
Priority as general performance knob. All messages priority 9. No monitoring on low-priority age.

#### Interview follow-ups (with model answers)

**Q:** Priority vs separate queue?
**A:** For «Priority queues»: Priority vs separate queue. In production, VIP payment queue `PAYMENTS.PRIORITY` with two dedicated listeners; standard traffic on `PAYMENTS.STANDARD`—avoided starvation on single priority-enabled queue. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Interaction with message groups?
**A:** The follow-on risk of «Interaction with message groups» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Kafka priority—does it exist?
**A:** Trade-off framing for «Kafka priority—does it exist»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Priority queues.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: VIP payment queue `PAYMENTS.PRIORITY` with two dedicated listeners; standard traffic on `PAYMENTS.STANDARD`—avoided starvation on single priority-enabled queue.. I suspect priority as general performance knob until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 30. Browse vs consume.

**Short answer:** Browse (MQ browse, JMS QueueBrowser, Rabbit get with no-ack in admin tools) peeks at messages without removing them—ops and support only. Applications must consume with ack/remove; browsing in app code races with real consumers and duplicates work. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Browse is read-only inspection for troubleshooting depth and poison inspection without destructive GET. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ BROWSE cursor walks queue; message remains for consumers. QueueBrowser in JMS similar. Not for processing—no syncpoint on browse. Support uses tooling to inspect BOQ payload before replay decision.

#### When to use / when NOT to use
Ops runbooks for BOQ inspection via approved scripts. Apps use normal consume path. Never 'browse then get' hack for selective processing.

#### Production example
L2 support browses first message on `PAYMENTS.BOQ` to identify bad ISO field; files ticket; replay after fix via controlled utility—not production listener. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Production code using QueueBrowser for business logic. Browse during peak load adding CPU. Assuming browse marks message consumed.

#### Interview follow-ups (with model answers)

**Q:** Security on browse operations?
**A:** For «Browse vs consume»: Security on browse operations. In production, L2 support browses first message on `PAYMENTS.BOQ` to identify bad ISO field; files ticket; replay after fix via controlled utility—not production listener. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Browse under syncpoint?
**A:** The follow-on risk of «Browse under syncpoint» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Alternatives for audit without browse?
**A:** Trade-off framing for «Alternatives for audit without browse»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Browse vs consume.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: L2 support browses first message on `PAYMENTS.BOQ` to identify bad ISO field; files ticket; replay after fix via controlled utility—not production listener.. I suspect production code using queuebrowser for business logic until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 31. Undelivered / backout queue design.

**Short answer:** Design backout/dead-letter queues with alerting, restricted access, replay tooling, and retention policy—treat as incident queue, not garbage dump. Separate retry queue (transient) from backout (poison or exhausted retries). In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Undelivered message handling is operational UX for messaging systems—how support fixes, replays, and audits failures. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Main queue → retry (TTL/delay) → backout after N attempts. IAM: only break-glass role can purge BOQ. Replay tool validates schema version, logs operator id, moves to reprocess queue. Metrics: BOQ depth, oldest age, replay success rate.

#### When to use / when NOT to use
Every critical queue pair has BOQ + runbook. Pager on BOQ age > 15m. Quarterly replay drill.

#### Production example
BOQ replay UI requires manager approval, writes audit row, republishes to `PAYMENTS.REPROCESS` with new correlation id; idempotent consumer handles overlap. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Developers purge BOQ to 'clear alerts.' No replay audit trail. Single BOQ for entire enterprise without routing keys.

#### Interview follow-ups (with model answers)

**Q:** Who owns BOQ on-call?
**A:** For «Undelivered / backout queue design»: Who owns BOQ on-call. In production, BOQ replay UI requires manager approval, writes audit row, republishes to `PAYMENTS.REPROCESS` with new correlation id; idempotent consumer handles overlap. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Legal hold on poison messages?
**A:** The follow-on risk of «Legal hold on poison messages» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Automated replay vs manual?
**A:** Trade-off framing for «Automated replay vs manual»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Undelivered / backout queue design.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: BOQ replay UI requires manager approval, writes audit row, republishes to `PAYMENTS.REPROCESS` with new correlation id; idempotent consumer handles overlap.. I suspect developers purge boq to 'clear alerts until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 32. Encoding and JMS vs native MQ.

**Short answer:** JMS TextMessage carries Unicode strings; BytesMessage for opaque bytes. IBM MQ MQMD format and CCSID (1208 UTF-8 common) must align between mainframe EBCDIC and Java UTF-8 or strings corrupt silently. Native MQ MQI bypasses JMS mapping—know RFH2 for JMS properties. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Character set and message format mismatches are classic integration bugs in bank MQ projects—more common than broker crashes. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
CCSID on queue manager, queue, channel, and message must be consistent or conversion applied. JMS provider maps properties to RFH2 folder. Mainframe 500 vs distributed 1208 requires explicit conversion or binary payload with agreed schema.

#### When to use / when NOT to use
Standardize UTF-8 end-to-end for new interfaces. Document CCSID in integration spec. Integration tests with non-ASCII data (names, addresses).

#### Production example
Customer name 'Müller' corrupted until outbound channel CCSID matched inbound; contract tests added for diacritics on every release. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming Java String 'just works' across MQ boundary. Ignoring MQFMT mismatch (STRING vs BINARY). Mixing TextMessage for compressed binary.

#### Interview follow-ups (with model answers)

**Q:** When to use BytesMessage vs TextMessage?
**A:** For «Encoding and JMS vs native MQ»: When to use BytesMessage vs TextMessage. In production, Customer name 'Müller' corrupted until outbound channel CCSID matched inbound; contract tests added for diacritics on every release. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** RFH2 header purpose?
**A:** The follow-on risk of «RFH2 header purpose» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Mainframe integration testing strategy?
**A:** Trade-off framing for «Mainframe integration testing strategy»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Encoding and JMS vs native MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Customer name 'Müller' corrupted until outbound channel CCSID matched inbound; contract tests added for diacritics on every release.. I suspect assuming java string 'just works' across mq boundary until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 33. Unit of work in MQ.

**Short answer:** IBM MQ syncpoint groups PUT/GET operations—COMMIT makes messages visible or removed; BACKOUT redelivers. Multiple puts in one UOW appear atomically to other consumers. Combining JDBC and MQ UOW requires XA or outbox—not local commit on both independently. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Unit of work (UOW) is the transaction boundary for message operations on the broker—analogous to DB transaction for messaging. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Session transacted=true in JMS maps to syncpoint. getMessage under syncpoint invisible until commit; rollback requeues. Batch send all commit together. Listener container commits session after successful invoke (mode dependent).

#### When to use / when NOT to use
Use transacted session for multi-message batch publish or consume batch ack. Do not assume UOW spans Oracle without XA/outbox. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Two related puts to `LEDGER.OUT` and `NOTIFY.OUT` in one JMS transaction—both visible or neither after commit.

#### Common mistakes
Partial commit across DB + MQ without pattern. Long-running listener holding UOW open (locks messages). Commit before side effect completes.

#### Interview follow-ups (with model answers)

**Q:** Syncpoint vs Kafka transaction?
**A:** For «Unit of work in MQ»: Syncpoint vs Kafka transaction. In production, Two related puts to `LEDGER.OUT` and `NOTIFY.OUT` in one JMS transaction—both visible or neither after commit. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** UOW and message visibility to other consumers?
**A:** The follow-on risk of «UOW and message visibility to other consumers» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Backout after business exception?
**A:** Trade-off framing for «Backout after business exception»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Unit of work in MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Two related puts to `LEDGER.OUT` and `NOTIFY.OUT` in one JMS transaction—both visible or neither after commit.. I suspect partial commit across db + mq without pattern until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 34. Duplicate detection in the broker.

**Short answer:** Some brokers offer message deduplication by sequence or duplicate flags (limited windows)—treat as optimization only, not primary idempotency. Application-level dedupe remains mandatory for business correctness across retries and bridge flows. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Broker duplicate detection may suppress exact replays within a time window; semantics vary widely by product and configuration. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ has limited duplicate detection contexts; Rabbit has none native. JMS does not standardize dedupe. Producers retrying PUT may create two messages with different MsgIds—consumer must use business key.

#### When to use / when NOT to use
Enable broker features as belt-and-suspenders if available. Always implement consumer idempotency store. Document that MsgId changes on republish from outbox relay.

#### Production example
Enabled MQ dedupe on channel for hardware retry glitch; still kept DB idempotency because bridge from Kafka duplicated overnight. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Relying solely on broker dedupe window (expires). Assuming same JMSMessageID on redelivery (usually same) vs republish (new). Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** MsgId vs CorrelId for dedupe?
**A:** For «Duplicate detection in the broker»: MsgId vs CorrelId for dedupe. In production, Enabled MQ dedupe on channel for hardware retry glitch; still kept DB idempotency because bridge from Kafka duplicated overnight. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Kafka idempotent producer vs MQ?
**A:** The follow-on risk of «Kafka idempotent producer vs MQ» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Outbox relay duplicate scenario?
**A:** Trade-off framing for «Outbox relay duplicate scenario»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Duplicate detection in the broker.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Enabled MQ dedupe on channel for hardware retry glitch; still kept DB idempotency because bridge from Kafka duplicated overnight.. I suspect relying solely on broker dedupe window (expires) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 35. Temporary destinations leak.

**Short answer:** JMS temporary queues/topics are created per request-reply session; failing to close consumers or delete temps leaks broker resources and exhausts names. Prefer pooled dedicated reply queues or shared reply queue with correlation for high volume. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Temporary destinations are convenient for RPC correlation but dangerous at scale without strict lifecycle management. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
createTemporaryQueue() tied to connection; connection close deletes temps—but long-lived connections with unclosed temps accumulate. Spring sendAndReceive may create temps; ensure session cleanup. IBM MQ monitors temp object usage.

#### When to use / when NOT to use
High-volume RPC: fixed reply queue + correlId. Low volume: temps OK with try/finally and connection pooling limits. Monitor temp queue count on broker.

#### Production example
Memory leak on QM from temp queues after bad deploy—fixed by closing Session in finally; moved to shared `REPLY.IN` with selector. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
New temp queue per HTTP request at 500 RPS. Shared connection with orphaned temp consumers. No QM alert on temp object growth.

#### Interview follow-ups (with model answers)

**Q:** Spring JmsTemplate temp queue behavior?
**A:** For «Temporary destinations leak»: Spring JmsTemplate temp queue behavior. In production, Memory leak on QM from temp queues after bad deploy—fixed by closing Session in finally; moved to shared `REPLY.IN` with selector. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** IBM MQ temp queue limits?
**A:** The follow-on risk of «IBM MQ temp queue limits» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Alternative correlation patterns?
**A:** Trade-off framing for «Alternative correlation patterns»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Temporary destinations leak.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Memory leak on QM from temp queues after bad deploy—fixed by closing Session in finally; moved to shared `REPLY.IN` with selector.. I suspect new temp queue per http request at 500 rps until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 36. Monitoring.

**Short answer:** Monitor queue depth, oldest message age (better SLA signal than depth alone), channel status, listener error rates, backout counts, and disk usage. Dashboard per critical queue with thresholds tied to paging—not only 'is broker up'. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Messaging observability connects broker metrics to business SLAs—stuck payments show as age before depth spikes. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
IBM MQ: amqpcmon, Prometheus exporters, DISPLAY QSTATUS CURDEPTH, MSGAGE. Rabbit: management API queue metrics. Spring Actuator + Micrometer for listener failures. Correlate with DB pool and downstream latency.

#### When to use / when NOT to use
Alert oldest message age > SLA (e.g., 5m for payments). Channel NOT RUNNING page immediately. Track redelivery rate spike as poison indicator.

#### Production example
Grafana: `mq_queue_oldest_msg_age_seconds` pages before depth hits MAX; saved weekend incident when downstream DB index rebuild slowed consumers. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Only TCP ping on broker host. Depth alert without age (false calm when depth low but one msg stuck 6 hours). No trace correlation id in logs.

#### Interview follow-ups (with model answers)

**Q:** Key metrics vs nice-to-have?
**A:** For «Monitoring»: Key metrics vs nice-to-have. In production, Grafana: `mq_queue_oldest_msg_age_seconds` pages before depth hits MAX; saved weekend incident when downstream DB index rebuild slowed consumers. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Synthetic probe messages?
**A:** The follow-on risk of «Synthetic probe messages» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** OpenTelemetry with JMS?
**A:** Trade-off framing for «OpenTelemetry with JMS»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Monitoring.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Grafana: `mq_queue_oldest_msg_age_seconds` pages before depth hits MAX; saved weekend incident when downstream DB index rebuild slowed consumers.. I suspect only tcp ping on broker host until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 37. `CLIENT_ACKNOWLEDGE` footgun.

**Short answer:** In CLIENT_ACKNOWLEDGE, acknowledging one message may cumulatively ack all prior unacknowledged messages on the session—provider-dependent behavior that causes premature loss or unexpected duplicates if misunderstood. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Client ack mode gives explicit control but session-level ack semantics trip up teams expecting per-message isolation. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
JMS spec allows cumulative ack; ActiveMQ Artemis and IBM MQ JMS implementations document specifics. Batch processing multiple messages on one session then ack last may ack all—or may not if you ack individually on some providers. Transacted sessions often clearer for batch.

#### When to use / when NOT to use
Prefer AUTO for single-message listeners. Use transacted for batch. If CLIENT, read vendor docs and test crash scenarios.

#### Production example
Team acked message 100 only; messages 1–99 lost on IBM MQ JMS cumulative semantics—switched to transacted batch commit. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Mixing CLIENT ack with concurrent receives on same session. Assuming Kafka-style per-record commit mental model. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** INDIVIDUAL_ACKNOWLEDGE where available?
**A:** For «`CLIENT_ACKNOWLEDGE` footgun»: INDIVIDUAL_ACKNOWLEDGE where available. In production, Team acked message 100 only; messages 1–99 lost on IBM MQ JMS cumulative semantics—switched to transacted batch commit. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Test plan for ack semantics?
**A:** The follow-on risk of «Test plan for ack semantics» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is transacted clearer than CLIENT?
**A:** Trade-off framing for «When is transacted clearer than CLIENT»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on `CLIENT_ACKNOWLEDGE` footgun.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Team acked message 100 only; messages 1–99 lost on IBM MQ JMS cumulative semantics—switched to transacted batch commit.. I suspect mixing client ack with concurrent receives on same session until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 38. Kafka "queue" mode (recent) vs MQ.

**Short answer:** Kafka has evolved share groups and queue-like consumption semantics on topics, but banks still run IBM MQ for operational integration in 2026—know both. Kafka queue modes improve task distribution on logs; they do not replace MQ channel to mainframe or existing XA stacks overnight. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Converging semantics does not mean converging operational reality—enterprise MQ estates persist alongside Kafka data platforms. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka KIP-932 share groups and related work target cooperative queue consumption on compacted/shared topics. Still retained log, different ops model, different security and compliance story. MQ: mature channel tooling, CICS, SWIFT adapters.

#### When to use / when NOT to use
Discuss trends honestly: Kafka absorbing some queue use cases; MQ remains for legacy and regulated paths. Architecture interviews reward nuance over zealotry. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
New analytics jobs use Kafka share consumption; payment settlement remains MQ—architecture diagram shows bridge, not replacement. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Declaring MQ dead from one KIP. Ignoring Kafka queue mode limitations vs classic MQ DLQ/backout maturity on IBM stack. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** Share groups vs consumer groups?
**A:** For «Kafka "queue" mode (recent) vs MQ»: Share groups vs consumer groups. In production, New analytics jobs use Kafka share consumption; payment settlement remains MQ—architecture diagram shows bridge, not replacement. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When would you pilot Kafka queue mode?
**A:** The follow-on risk of «When would you pilot Kafka queue mode» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Migration criteria checklist?
**A:** Trade-off framing for «Migration criteria checklist»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Kafka "queue" mode (recent) vs MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: New analytics jobs use Kafka share consumption; payment settlement remains MQ—architecture diagram shows bridge, not replacement.. I suspect declaring mq dead from one kip until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 39. When you'd pick MQ over Kafka.

**Short answer:** Choose MQ when you need JMS/XA with Oracle, mainframe/CICS integration, low-volume guaranteed delivery payments, request-reply over bus, ops team is MQ-native, and replay from log is not a requirement—typical core banking operational messaging. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Technology choice follows integration constraints, team skills, and semantic needs—not benchmark headlines. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
MQ strengths: mature HA pairs, backout, channel security, decades of bank runbooks, point-to-point simplicity. Kafka strengths: replay, throughput, stream processing. Hybrid common.

#### When to use / when NOT to use
Payments handoff to core ledger on IBM MQ. Batch file notification to z/OS. Internal task queue moderate TPS with strict DLQ process.

#### Production example
Wire transfer STP on MQ with Oracle XA in legacy monolith; Kafka added later only for fraud feature store ingestion. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Kafka for 50 TPS payment because 'modern.' MQ for unlimited retention analytics. Ignoring ops cost of running two systems badly.

#### Interview follow-ups (with model answers)

**Q:** Volume threshold where Kafka wins?
**A:** For «When you'd pick MQ over Kafka»: Volume threshold where Kafka wins. In production, Wire transfer STP on MQ with Oracle XA in legacy monolith; Kafka added later only for fraud feature store ingestion. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Request-reply decision tree?
**A:** The follow-on risk of «Request-reply decision tree» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Mainframe constraint examples?
**A:** Trade-off framing for «Mainframe constraint examples»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing When you'd pick MQ over Kafka.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Wire transfer STP on MQ with Oracle XA in legacy monolith; Kafka added later only for fraud feature store ingestion.. I suspect kafka for 50 tps payment because 'modern until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 40. When Kafka over MQ.

**Short answer:** Pick Kafka for event backbone, replay, many independent consumer groups, high throughput ingestion, stream processing (Flink, ksqlDB), audit log retention, and analytics—when operational bus patterns do not dominate. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Kafka is the default for data-in-motion platform patterns; MQ remains for operational transaction plumbing in many enterprises. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Log retention enables reprocessing after bug fix. Partitions scale horizontal read. Connect ecosystem integrates DB, ES, S3. MQ replay is bolt-on and expensive.

#### When to use / when NOT to use
Customer event stream, clickstream, CDC to warehouse, microservice choreography with idempotent consumers and outbox. Not for replacing CICS trigger without adapter project. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Post-outbox events land in Kafka; five teams consume independently with own offset lag SLOs; MQ only at edge to mainframe. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Kafka as task queue without idempotency. One partition for 'simplicity' on 100k TPS. Ignoring compaction vs delete retention choice.

#### Interview follow-ups (with model answers)

**Q:** Kafka as sole bus anti-pattern?
**A:** For «When Kafka over MQ»: Kafka as sole bus anti-pattern. In production, Post-outbox events land in Kafka; five teams consume independently with own offset lag SLOs; MQ only at edge to mainframe. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Stream processing requirement examples?
**A:** The follow-on risk of «Stream processing requirement examples» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Retention cost governance?
**A:** Trade-off framing for «Retention cost governance»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to When Kafka over MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Post-outbox events land in Kafka; five teams consume independently with own offset lag SLOs; MQ only at edge to mainframe.. I suspect kafka as task queue without idempotency until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 41. Message format.

**Short answer:** Prefer versioned schemas (Avro, JSON Schema, Protobuf) on MQ payloads even without Kafka Schema Registry—include content-type and schema version headers. Evolve with additive fields and explicit version negotiation; avoid ambiguous stringly-typed JSON in production. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Message format contract defines interoperability between producers and consumers across deploy cycles and teams. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Set JMS properties `contentType`, `schemaVersion`, `eventType`. Consumer rejects unknown major version to DLQ. IBM MQ RFH2 can carry properties. Align with enterprise API catalog. Breaking changes require new queue or dual-write period.

#### When to use / when NOT to use
Schema registry optional but document schemas in repo. Contract tests in CI. Never parse with regex for financial messages.

#### Production example
ISO 20022 subset wrapped in JSON with `schemaVersion: 3`; v2 consumers remain on parallel queue during migration; v3 rollout monitored via header metrics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Undocumented JSON fields 'for flexibility.' Silent default values hiding missing required fields. No backward compatibility plan.

#### Interview follow-ups (with model answers)

**Q:** Avro on MQ without Confluent?
**A:** For «Message format»: Avro on MQ without Confluent. In production, ISO 20022 subset wrapped in JSON with `schemaVersion: 3`; v2 consumers remain on parallel queue during migration; v3 rollout monitored via header metrics. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Blue/green schema migration?
**A:** The follow-on risk of «Blue/green schema migration» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Binary vs JSON on MQ latency?
**A:** Trade-off framing for «Binary vs JSON on MQ latency»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Message format.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: ISO 20022 subset wrapped in JSON with `schemaVersion: 3`; v2 consumers remain on parallel queue during migration; v3 rollout monitored via header metrics.. I suspect undocumented json fields 'for flexibility until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 42. Spring Cloud Stream abstraction.

**Short answer:** Spring Cloud Stream binders (Rabbit, Kafka) abstract `@StreamListener` style messaging—but leak broker semantics: prefetch, partitions, DLQ, and transactions differ. Fine for simple pipes; dangerous if team forgets what's underneath. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Stream abstraction trades portability for obscured operational behavior—senior engineers must still know binder-specific config. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
spring.cloud.stream bindings map destination to broker entity. Rabbit binder != Kafka binder properties. Functional model (Consumer/Supplier beans) in 3.x+. Error channels and DLQ config are binder-specific. IBM MQ often uses JMS directly, not Stream binder.

#### When to use / when NOT to use
Use Stream for homogeneous Rabbit/Kafka microservices with documented binder choice per env. Avoid 'write once deploy anywhere' myth across Kafka and Rabbit without testing both. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Team used Stream with Kafka binder in prod; dev used Rabbit binder—DLQ behavior differed; standardized on Kafka binder + integration tests in CI. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming `destination` means same thing on all binders. No binder-specific retry docs. Using Stream for IBM MQ (unsupported path—use JMS).

#### Interview follow-ups (with model answers)

**Q:** Functional vs annotation model?
**A:** For «Spring Cloud Stream abstraction»: Functional vs annotation model. In production, Team used Stream with Kafka binder in prod; dev used Rabbit binder—DLQ behavior differed; standardized on Kafka binder + integration tests in CI. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** When to drop Stream for raw JMS?
**A:** The follow-on risk of «When to drop Stream for raw JMS» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Testing binder configurations?
**A:** Trade-off framing for «Testing binder configurations»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Spring Cloud Stream abstraction.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Team used Stream with Kafka binder in prod; dev used Rabbit binder—DLQ behavior differed; standardized on Kafka binder + integration tests in CI.. I suspect assuming `destination` means same thing on all binders until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 43. Testing.

**Short answer:** Integration-test JMS with Testcontainers (RabbitMQ, ActiveMQ Artemis) or licensed IBM MQ container in CI; do not rely solely on mocking JmsTemplate. Test ack failure, redelivery, and DLQ routing with real broker behavior. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Messaging bugs appear at ack boundaries and broker config—mocks hide the failure modes seniors must handle. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Testcontainers spins real broker; @JmsListener IT sends message, asserts DB side effect and ack. Test poison → BOQ path. Contract tests for schema version. IBM MQ developer edition or official container if license allows.

#### When to use / when NOT to use
CI pipeline includes messaging module tests. Local docker-compose for dev parity. Mock unit tests only for business logic isolation.

#### Production example
Artemis Testcontainer verifies listener idempotency on double delivery by simulating rollback before ack; caught missing unique constraint before prod. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Only `@MockBean JmsTemplate`. No test for transacted rollback. Skipping CI messaging tests as 'flaky' without fixing.

#### Interview follow-ups (with model answers)

**Q:** IBM MQ in CI licensing?
**A:** For «Testing»: IBM MQ in CI licensing. In production, Artemis Testcontainer verifies listener idempotency on double delivery by simulating rollback before ack; caught missing unique constraint before prod. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Embedded broker vs Testcontainers?
**A:** The follow-on risk of «Embedded broker vs Testcontainers» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to test request-reply timeout?
**A:** Trade-off framing for «How to test request-reply timeout»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Testing.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Artemis Testcontainer verifies listener idempotency on double delivery by simulating rollback before ack; caught missing unique constraint before prod.. I suspect only `@mockbean jmstemplate` until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Testcontainers
class PaymentListenerIT {
    @Container
    static GenericContainer<?> artemis = new GenericContainer<>("apache/activemq-artemis:2.31.2")
        .withExposedPorts(61616);

    @Test
    void redeliversOnFailure() { /* send, fail once, assert single credit */ }
}
```

---

### 44. Redelivery delay.

**Short answer:** Some brokers support native redelivery delay (Artemis, Rabbit DLX+TTL); others need retry queues with visibility timeout or scheduled requeue. Never Thread.sleep in listener—it holds session and blocks prefetch. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Redelivery delay backs off transient failures without hot-loop CPU burn from immediate redelivery. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Rabbit: TTL queue → DLX → main queue after delay. IBM MQ: use separate retry queue + triggering or app scheduler. Artemis redelivery-delay property. JMS listener should throw to trigger container retry policy, not sleep.

#### When to use / when NOT to use
Exponential backoff for downstream outages. Immediate DLQ for poison. Cap max retries with alert.

#### Production example
Retry queue `PAYMENTS.RETRY` with 60s TTL returns to main via DLX; three cycles then BOQ—downstream DB outage recovered without manual replay. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Thread.sleep(60000) in onMessage. Infinite immediate redelivery hammering DB. No jitter on backoff (thundering herd).

#### Interview follow-ups (with model answers)

**Q:** Spring Retry with JMS?
**A:** For «Redelivery delay»: Spring Retry with JMS. In production, Retry queue `PAYMENTS.RETRY` with 60s TTL returns to main via DLX; three cycles then BOQ—downstream DB outage recovered without manual replay. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Visibility timeout analog in MQ?
**A:** The follow-on risk of «Visibility timeout analog in MQ» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare SQS delay queues?
**A:** Trade-off framing for «Compare SQS delay queues»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Redelivery delay.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Retry queue `PAYMENTS.RETRY` with 60s TTL returns to main via DLX; three cycles then BOQ—downstream DB outage recovered without manual replay.. I suspect thread until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 45. Transactional outbox to MQ.

**Short answer:** Same outbox pattern as Kafka: insert business row and outbox event in one DB transaction; after commit a relay publishes to MQ via JmsTemplate. Crash after commit causes duplicate MQ message—consumer idempotency required; still beats dual-write without outbox. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Transactional outbox bridges ACID database and at-least-once messaging without XA 2PC pain. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Outbox table columns: id, aggregateId, type, payload, createdAt, publishedAt. Relay polls or CDC triggers send; marks published. MQ message carries business id in properties. Order: TX commit → relay → MQ → consumer idempotent apply.

#### When to use / when NOT to use
Default for new Java services publishing to IBM MQ from Oracle/Postgres. Pair with Debezium or lightweight poller. Monitor relay lag.

#### Production example
Order saved + outbox row; relay publishes to `ORDER.CREATED`; duplicate on relay retry deduped by orderId in inventory service. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Deleting outbox row before MQ ack confirmed. Relay in same @Transactional as save (never sees commit). No relay lag alert.

#### Interview follow-ups (with model answers)

**Q:** Polling vs log-based CDC relay?
**A:** For «Transactional outbox to MQ»: Polling vs log-based CDC relay. In production, Order saved + outbox row; relay publishes to `ORDER.CREATED`; duplicate on relay retry deduped by orderId in inventory service. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Ordering guarantees from outbox?
**A:** The follow-on risk of «Ordering guarantees from outbox» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** XA still required anywhere?
**A:** Trade-off framing for «XA still required anywhere»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Transactional outbox to MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order saved + outbox row; relay publishes to `ORDER.CREATED`; duplicate on relay retry deduped by orderId in inventory service.. I suspect deleting outbox row before mq ack confirmed until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Scheduled(fixedDelay = 1000)
void publishOutbox() {
    outboxRepo.findUnpublished(PageRequest.of(0, 100)).forEach(row -> {
        jmsTemplate.convertAndSend("EVENTS", row.getPayload(),
            m -> { m.setStringProperty("eventId", row.getId().toString()); return m; });
        row.markPublished();
        outboxRepo.save(row);
    });
}
```

---

### 46. Ordering with JMS.

**Short answer:** Strict global order on one queue requires single consumer thread, persistent messages, careful prefetch, and no redelivery reordering—fragile at scale. Per-key order needs message groups (MQ) or migrate to Kafka partitions for higher throughput. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Ordering is the enemy of horizontal scale in classic JMS queues—design explicitly for the order scope you actually need. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Single active consumer = FIFO until poison/requeue. Multiple sessions interleave completion. Message groups pin group to consumer. Priority and redelivery disturb order. Transacted batch can reorder visibility.

#### When to use / when NOT to use
Scope order requirement: global (rare), per-account (groups/partitions), or none (competing consumers). Document and test failover reorder behavior. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Required global order for legacy batch file lines—temporarily single consumer with maintenance window scale plan to grouped model. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Five consumers expecting FIFO. Ignoring reorder on backout/requeue. No order test in CI.

#### Interview follow-ups (with model answers)

**Q:** Failover impact on order?
**A:** For «Ordering with JMS»: Failover impact on order. In production, Required global order for legacy batch file lines—temporarily single consumer with maintenance window scale plan to grouped model. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Groups vs single consumer trade-off?
**A:** The follow-on risk of «Groups vs single consumer trade-off» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** End-to-end order including DB?
**A:** Trade-off framing for «End-to-end order including DB»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Ordering with JMS.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Required global order for legacy batch file lines—temporarily single consumer with maintenance window scale plan to grouped model.. I suspect five consumers expecting fifo until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 47. Cluster vs HA pair.

**Short answer:** Active/passive HA pair runs one live queue manager with standby takeover; cluster distributes queues across multiple QMs with repository routing—different failover and affinity semantics. Test failover paths; diagrams lie. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
HA pair simplifies some DR stories; cluster scales capacity and provides distributed queue definitions—with operational complexity. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Multi-instance QM: active on node A, standby on B, shared storage or RDQM. Cluster: queue aliases route to owning QM; channel to cluster enters via gateway. Message loss RPO depends on sync mode. Split-brain protections required.

#### When to use / when NOT to use
Payments often active/passive with sync replication. Geographically distributed cluster for capacity across sites—know your RPO/RTO. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Cluster alias misroute sent messages to wrong QM until DISPLAY QCLUSTER fixed—failover drill discovered gap. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming cluster = automatic HA without understanding full repository. No message affinity plan after node loss. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Interview follow-ups (with model answers)

**Q:** RDQM in cluster context?
**A:** For «Cluster vs HA pair»: RDQM in cluster context. In production, Cluster alias misroute sent messages to wrong QM until DISPLAY QCLUSTER fixed—failover drill discovered gap. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Client reconnect logic?
**A:** The follow-on risk of «Client reconnect logic» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Stretch cluster pitfalls?
**A:** Trade-off framing for «Stretch cluster pitfalls»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Cluster vs HA pair.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Cluster alias misroute sent messages to wrong QM until DISPLAY QCLUSTER fixed—failover drill discovered gap.. I suspect assuming cluster = automatic ha without understanding full repository until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 48. Cloud: Azure Service Bus vs IBM MQ.

**Short answer:** Azure Service Bus offers queues, topics, sessions (ordering), peek-lock receive, dead-letter subqueues, and cloud ops—similar patterns to MQ/Rabbit but not 1:1 migration. IBM MQ on cloud or on-prem remains common in banks; ASB common in Azure-native estates. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Cloud messaging services reimplement queue/topic semantics with different limits, pricing, and identity models—migration is a project, not a config change. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
ASB: Queue vs Topic/Subscription; sessions enable FIFO within session id; max message size 256KB–100MB tier dependent. Peek-lock like Rabbit ack. DLQ on expiration or max delivery count. IBM MQ: channels, MQSC, mainframe bridges ASB lacks.

#### When to use / when NOT to use
ASB for greenfield on Azure with managed identity. IBM MQ when core bank or partner requires it. Bridge during migration with idempotent consumers both sides.

#### Production example
Lift-and-shift attempt failed on request-reply correlId semantics; kept MQ for core, ASB for digital channel notifications only. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming ASB drop-in for MQ channels to z/OS. Ignoring session id design for order. No DLQ monitoring on ASB.

#### Interview follow-ups (with model answers)

**Q:** ASB premium vs standard for latency?
**A:** For «Cloud: Azure Service Bus vs IBM MQ»: ASB premium vs standard for latency. In production, Lift-and-shift attempt failed on request-reply correlId semantics; kept MQ for core, ASB for digital channel notifications only. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Hybrid connectivity ExpressRoute?
**A:** The follow-on risk of «Hybrid connectivity ExpressRoute» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Cost model comparison?
**A:** Trade-off framing for «Cost model comparison»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Cloud: Azure Service Bus vs IBM MQ.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Lift-and-shift attempt failed on request-reply correlId semantics; kept MQ for core, ASB for digital channel notifications only.. I suspect assuming asb drop-in for mq channels to z/os until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 49. Azure Service Bus peek-lock.

**Short answer:** Peek-lock receive locks a message for LockDuration; successful processing calls complete(), failures abandon() for redelivery or dead-letter(). Lost lock (slow handler) causes duplicate delivery—same idempotency requirement as JMS/Kafka at-least-once. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Peek-lock is ASB's competing-consumer mode with visibility timeout—mental model aligns with Rabbit ack and JMS CLIENT ack, not destructive read. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Receiver receives with lock token; complete removes from queue; abandon returns immediately; deadLetter() on poison. MaxDeliveryCount then DLQ. Auto-renew lock for long processing if SDK supports. Session receiver adds FIFO within session.

#### When to use / when NOT to use
Set lock duration > p99 processing time or use auto-renew. Idempotent handler mandatory. Monitor DLQ and delivery count metrics.

#### Production example
Handler at p99 45s with 30s lock caused duplicates until lock duration raised and idempotency table added—same lesson as MQ redelivery. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Complete before DB commit. No MaxDeliveryCount (infinite poison loop). Ignoring duplicate from lock expiry as 'ASB bug'.

#### Interview follow-ups (with model answers)

**Q:** Peek-lock vs receive-and-delete?
**A:** For «Azure Service Bus peek-lock»: Peek-lock vs receive-and-delete. In production, Handler at p99 45s with 30s lock caused duplicates until lock duration raised and idempotency table added—same lesson as MQ redelivery. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Session receiver ordering?
**A:** The follow-on risk of «Session receiver ordering» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compare to IBM MQ syncpoint?
**A:** Trade-off framing for «Compare to IBM MQ syncpoint»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Azure Service Bus peek-lock.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Handler at p99 45s with 30s lock caused duplicates until lock duration raised and idempotency table added—same lesson as MQ redelivery.. I suspect complete before db commit until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
ServiceBusReceiverClient receiver = ...;
ServiceBusReceivedMessage msg = receiver.receiveMessage(Duration.ofSeconds(30));
try {
    process(msg.getBody());
    receiver.complete(msg);
} catch (PoisonException e) {
    receiver.deadLetter(msg, new DeadLetterOptions().setDeadLetterReason("POISON"));
}
```

---

### 50. Senior MQ story.

**Short answer:** A credible senior answer narrates a real incident arc: dual-write or XA pain, message loss or poison loop, concrete fix (outbox, backout alerts, idempotency), and principled rejection of XA—showing operational maturity banks hire for. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Interviewers want war stories proving you operated messaging under failure, not textbook definitions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Structure: context (system, volume, broker), failure mode (crash boundary, encoding, channel, poison), detection (metric/alert), fix (pattern, code, runbook), prevention (tests, monitoring). Mention trade-offs you rejected. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### When to use / when NOT to use
Prepare one MQ story and one Kafka story if possible. Honesty beats fabrication—describe a teammate's incident you led postmortem for if needed. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
'We dual-wrote Oracle and MQ; pod killed after DB commit before send lost settlement message; moved to outbox with relay lag SLO; backout queue alert on oldest age > 10m; skipped XA after two in-doubt TX incidents—documented for auditors with compensating idempotency controls.' Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Generic 'MQ is reliable' without incident. Blaming broker vendor only. No mention of idempotency or monitoring.

#### Interview follow-ups (with model answers)

**Q:** How did you test the fix?
**A:** For «Senior MQ story»: How did you test the fix. In production, 'We dual-wrote Oracle and MQ; pod killed after DB commit before send lost settlement message; moved to outbox with relay lag SLO; backout queue alert on oldest age > 10m; skipped XA after two in-doubt TX incidents—docume… I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What would you do differently at greenfield?
**A:** The follow-on risk of «What would you do differently at greenfield» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How did compliance respond to dropping XA?
**A:** Trade-off framing for «How did compliance respond to dropping XA»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Senior MQ story.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: 'We dual-wrote Oracle and MQ; pod killed after DB commit before send lost settlement message; moved to outbox with relay lag SLO; backout queue alert on oldest…. I suspect generic 'mq is reliable' without incident until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

## Deep-dive additions (Q51–Q55)

RabbitMQ routing, IBM MQ backout, Azure Service Bus, ordering guarantees, JMS 2.0 subscriptions.

---

### 51. RabbitMQ exchanges (direct/topic/fanout/headers) vs JMS

**Short answer:** **RabbitMQ** routes via **exchanges** bound to **queues** — **direct** (exact routing key), **topic** (pattern `orders.*`), **fanout** (broadcast), **headers** (metadata match). **JMS** (Java Message Service) is API abstraction — RabbitMQ via Spring AMQP is protocol-specific; IBM MQ and ActiveMQ implement JMS. Java teams use `JmsTemplate` or `RabbitTemplate` depending on broker. Trade-off: Rabbit flexibility versus enterprise JMS semantics on IBM MQ in banks.

#### What it is
RabbitMQ: AMQP 0-9-1, exchanges decouple publishers from queue topology. JMS: `Queue` vs `Topic`, `MessageProducer`, `ConnectionFactory` — portable across brokers with feature gaps. Spring Boot: `spring-boot-starter-amqp` vs `spring-jms`. Interview: map Rabbit concepts to JMS mental model for JD hybrid estates.

#### How it works (internals)
Publisher → exchange → bindings (routing key / headers) → queue → consumer. Topic exchange: `*` one word, `#` zero+ words. JMS point-to-point maps to queue; pub/sub to topic. Rabbit durability: exchange/queue `durable`, messages `persistent`. Consumer ack: manual `basicAck` after processing — like JMS `CLIENT_ACKNOWLEDGE`. Spring `@RabbitListener` container manages prefetch (`prefetch-count`).

#### When to use / when NOT to use
RabbitMQ: cloud-native microservices, routing complexity, moderate throughput. IBM MQ: mainframe integration, XA, bank standard. JMS API when swapping brokers rare — pick broker first. Do not fanout sensitive PII without per-queue ACL.

#### Production example
Order service publishes to `orders.topic` exchange with key `orders.created` — inventory queue binds `orders.*`, analytics binds `#`. Legacy billing on IBM MQ JMS queue via bridge. Spring config separates `RabbitTemplate` and `JmsTemplate` beans — same domain events, two transports during migration.

#### Common mistakes
- Publishing directly to queue name (anti-pattern in AMQP — use exchange).
- Topic binding typo — silent message blackhole.
- Assuming JMS `NON_PERSISTENT` survives broker restart.
- Unlimited prefetch — one slow consumer hoards messages.

#### Interview follow-ups (with model answers)

**Q:** RabbitMQ vs Kafka for order events?
**A:** Kafka: log, replay, high throughput, multiple consumer groups. Rabbit: work queues, routing, per-message ack, lower ops for task distribution. Many systems: Kafka event bus + Rabbit for worker tasks.

**Q:** How map JMS Topic to Rabbit?
**A:** Topic pub/sub ≈ fanout or topic exchange with multiple bound queues; durable subscribers ≈ durable queues per consumer name. JMS selectors map poorly — filter in consumer or use headers exchange.

#### Scenario probe
Messages published to `orders` exchange with key `order.created` never reach `shipping-queue`.

**Model answer:** Check binding: exchange type, routing key match (direct is exact), queue bound? Use Rabbit management UI `trace` or fire test message. Common fix: topic exchange needed but direct configured.

#### Code / config (when useful)

```java
@Bean
TopicExchange ordersExchange() { return new TopicExchange("orders.topic", true, false); }

@Bean
Binding shippingBinding(Queue shippingQueue, TopicExchange ordersExchange) {
    return BindingBuilder.bind(shippingQueue).to(ordersExchange).with("order.*");
}
```

---

### 52. IBM MQ dead-letter queue handling and backout threshold

**Short answer:** IBM MQ moves poison messages to **DLQ** (dead-letter queue) after **backout threshold** (`BACKOUT` count) exceeded on repeated rollback. **`BOQ`** / DLQ handler processes or discards failed messages. Java JMS: `setRollback()` on failure increments backout; configure `MQDLQ`, `BOTHRESH`, `BOQNAME` on queue. Trade-off: automatic DLQ protects consumers versus ops toil replaying from DLQ after fix.

#### What it is
Standard in banking IBM MQ estates — senior Java roles must know backout not infinite retry. WMQ channels, queue manager, Spring JMS `DefaultMessageListenerContainer` with `sessionTransacted=true`. Distinct from Kafka DLT — per-message backout count on same queue consumption attempts.

#### How it works (internals)
Message gets `BackoutCount` in MQMD; on `session.rollback()`, count increments; at threshold MQ routes to `SYSTEM.DEAD.LETTER.QUEUE` or custom DLQ via queue properties. DLQ depth monitored; replay tool `amqsput` or custom mover after root cause fix. `syncpoint` coordination with CICS/DB2 common — XA transaction rolls back message and DB together until backout.

#### When to use / when NOT to use
Always configure DLQ on integration queues — never `NOP` discard without audit. Tune threshold (often 3–10) vs infinite poison loop. Java service: catch poison schema, log message id, rollback limited times, then move to business DLQ with alert.

#### Production example
Payment JMS listener throws on bad XML — backout count hits 5, message to `PAYMENT.DLQ`. Ops fixes schema, runs replay utility to `PAYMENT.INPUT` with idempotency check on `MsgId`. Alert: DLQ depth > 0 pages payments on-call. Changed listener to validate XSD first — fail fast to DLQ without 5 retries wasting CPU.

#### Common mistakes
- No DLQ — poison blocks queue head forever.
- Replay DLQ without fixing consumer — immediate re-DLQ.
- Ignoring `BackoutCount` in logs.
- `autoAck` true — no backout semantics.

#### Interview follow-ups (with model answers)

**Q:** IBM MQ DLQ vs Kafka DLT?
**A:** MQ DLQ per poison message after local backout on same subscription. Kafka DLT topic after consumer retry policy — partition ordering preserved differently. Both need replay runbooks and idempotency.

**Q:** How prevent duplicate on DLQ replay?
**A:** Store processed `JMSMessageID` or business id in inbox table; replay tool skips if already processed. XA idempotency same as Kafka consumer pattern.

#### Scenario probe
Queue depth grows; all messages same poison payload at head — consumers idle.

**Model answer:** Classic poison message without DLQ or threshold too high. Clear: move message to DLQ manually (`MQSC` MOVE), fix consumer, replay. Long-term: DLQ + low backout threshold + schema validation before business logic.

#### Code / config (when useful)

```bash
# MQSC — set backout threshold and DLQ
ALTER QLOCAL('PAYMENT.INPUT') BOTHRESH(3) BOQNAME('PAYMENT.DLQ')
```

---

### 53. Azure Service Bus topics/subscriptions vs queues

**Short answer:** **Azure Service Bus Queue** is point-to-point — one consumer pool per queue. **Topic + Subscription** is pub/sub — multiple subscriptions each get copy with optional **SQL filter** rules. Java: `azure-messaging-servicebus` `ServiceBusClientBuilder`, `ServiceBusProcessorClient`. Compare to Rabbit topic exchange + queues. Trade-off: managed PaaS simplicity versus vendor lock-in and message size limits (256 KB standard).

#### What it is
Azure messaging for cloud-native Java on AKS/App Service. Queue for worker pattern; topic for fan-out (`OrderPlaced` → inventory sub, shipping sub, analytics sub). Sessions enable ordered processing per `sessionId`. Dead-letter sub-queue automatic after max delivery count.

#### How it works (internals)
Topic publishes once; each subscription maintains own cursor. Filter rules: `SqlFilter` on message properties. Peek-lock mode: complete/abandon like JMS ack; abandon increments delivery count → DLQ. Premium tier for lower latency and larger messages. Spring Cloud Stream Azure Service Bus binder abstracts producer/consumer.

#### When to use / when NOT to use
Use when Azure-native integration (Functions, Logic Apps). Kafka when replay/log needed at scale. Queue when single consumer group sufficient; topic when multiple independent consumers same event.

#### Production example
`order-events` topic; `inventory-sub` filter `eventType = 'OrderPlaced'`; `audit-sub` no filter. Java `@ServiceBusListener` on subscription with `maxConcurrentCalls=5`. Poison message delivery count 10 → DLQ; monitor via Azure Monitor metric `DeadletteredMessages`.

#### Common mistakes
- Using queue when need fan-out — duplicate publish anti-pattern.
- Forgetting complete() — message redelivered forever.
- Session lock lost on long processing — exceed lock duration.
- No DLQ monitoring alert.

#### Interview follow-ups (with model answers)

**Q:** Service Bus sessions vs Kafka partition key?
**A:** Sessions guarantee FIFO per `sessionId` on subscription — single consumer holds session lock. Kafka ordering per partition key with parallel consumers across keys. Pick sessions for strict per-order sequencing on Azure without Kafka.

**Q:** How integrate Spring Boot?
**A:** `spring-cloud-azure-starter-servicebus` with `@ServiceBusListener` or Stream binder. Configure `spring.cloud.azure.servicebus.connection-string` or Workload Identity. Manual settle in peek-lock for transactional processing.

#### Scenario probe
Two microservices need same `PaymentCaptured` event independently on Azure.

**Model answer:** Topic with two subscriptions — not two queues fed by duplicate HTTP calls. Optional filters if event types differ. Each service scales its own subscription consumer count.

#### Code / config (when useful)

```java
@ServiceBusClientBuilder builder = new ServiceBusClientBuilder()
    .connectionString(conn)
    .processor()
    .topicName("order-events")
    .subscriptionName("inventory-sub")
    .processMessage(ctx -> {
        handle(ctx.getMessage());
        ctx.complete();
    })
    .buildProcessorClient();
```

---

### 54. Message ordering guarantees across protocols

**Short answer:** **Ordering** is per-channel, not global: Kafka orders per **partition**; Rabbit per **queue** (single consumer); IBM MQ per **queue** with one active consumer; Service Bus per **session**. Parallel consumers break strict order — design **partition key** / **sessionId** = `orderId` when order matters. Trade-off: throughput (many consumers) versus FIFO guarantee.

#### What it is
Cross-protocol senior answer for hybrid estates. Java services must document which flows require ordering and enforce keying strategy. Global order across all events is almost never needed or feasible.

#### How it works (internals)
Kafka: producer `key=orderId` → same partition → single consumer in group processes in offset order. Rabbit: multiple consumers on one queue round-robin — no order; use consistent hash exchange or one consumer. JMS: `MessageGroupID` on IBM MQ for grouping. Service Bus: sessions serialize per id. Reordering on retry: use sequence numbers in payload to detect.

#### When to use / when NOT to use
Require ordering only for state machine per aggregate (`orderId`). Analytics aggregation order-independent. Never scale consumers beyond partitions if order required per key without sacrificing parallelism across keys.

#### Production example
Inventory reserved → committed → shipped must order per `orderId` — Kafka key `orderId`, one partition worth of parallelism across orders. Payment retries caused out-of-order `Authorized` after `Captured` — fixed with version field reject stale events.

#### Common mistakes
- Multiple consumers on queue expecting FIFO.
- Kafka key null — round-robin partitions break order.
- Retry to different partition on republish without key.
- Assuming total order across topic.

#### Interview follow-ups (with model answers)

**Q:** How detect out-of-order consumption?
**A:** Monotonic `sequence` or `version` on event; consumer discards `version <= current`. Metrics on `stale.event.dropped`. Integration test with forced reorder.

**Q:** Ordered delivery with retry?
**A:** Retry same message blocks head-of-line — use per-key queue or defer poison to side channel. Kafka: retry topic with same key preserves order for that key.

#### Scenario probe
Scaling consumers from 1 to 10 broke order processing — expected?

**Model answer:** Yes unless partitioned by key. Fix: Kafka partition count ≥ max parallel per key need; hash key orderId; or accept order only within session. Document in API contract.

#### Code / config (when useful)

```java
// Kafka producer — order per orderId
kafkaTemplate.send("order-events", order.getId(), event);
```

---

### 55. JMS 2.0 shared subscriptions and durable subscribers

**Short answer:** **JMS 2.0 shared subscriptions** let multiple consumers on **one topic subscription** load-balance messages (like queue competing consumers) while **durable subscribers** retain messages while offline. `createSharedConsumer(topic, subscriptionName)` — message delivered once across pool. Contrast **non-shared** durable: one consumer per subscription name. Trade-off: shared for scale; non-shared when each instance needs all messages (rare on topic).

#### What it is
JMS 2.0 feature in ActiveMQ Artemis, IBM MQ 9+, relevant for Java EE migration and Spring JMS config. Durable name survives broker restart; shared name allows horizontal scale on topic workload without duplicate delivery per consumer.

#### How it works (internals)
Broker stores subscription cursor; shared consumers compete for messages on same sub name. `clientId` + `subscriptionName` identifies durable. `JMSContext` API cleaner than JMS 1.1. Spring: `DefaultJmsListenerContainerFactory` `setSubscriptionShared(true)`, `setSubscriptionDurable(true)`. IBM MQ: `SHARED` attribute on subscription.

#### When to use / when NOT to use
Shared durable topic when multiple JVMs process topic events once each (work distribution). Non-shared durable when each node needs copy — use fanout/durable per instance or queues. Queue still simpler for pure work-queue pattern.

#### Production example
Five `notification-service` pods share subscription `email-dispatch` on topic `notifications` — each email sent once, load balanced. Durable ensures broker holds messages during rolling deploy. Replaced queue shim that duplicated topic into five queues manually.

#### Common mistakes
- Same subscription name different clientId — duplicate durable subs.
- Shared subscription without durable — messages lost offline.
- Mixing JMS 1.1 and 2.0 APIs in one app confusing lifecycle.
- Not closing consumer — leak subscription on broker.

#### Interview follow-ups (with model answers)

**Q:** Shared subscription vs Kafka consumer group?
**A:** Similar load-balancing semantics — one message to one consumer in group. Kafka adds log replay and partition parallelism model; JMS broker implements cursor per subscription without partition concept.

**Q:** Spring Boot config for shared durable listener?
**A:** `@JmsListener(destination = "notifications", subscription = "email-dispatch", containerFactory = "sharedDurableFactory")` with factory `setSubscriptionShared(true)`, `setSubscriptionDurable(true)`, unique `clientId` per pod or pooled connection strategy per vendor docs.

#### Scenario probe
Three pods all receive every topic message — need load balancing.

**Model answer:** Switch to shared subscription same name or use queue. Verify not creating three durable non-shared subscribers with different names accidentally.

#### Code / config (when useful)

```java
@Bean
DefaultJmsListenerContainerFactory sharedDurableFactory(ConnectionFactory cf) {
    DefaultJmsListenerContainerFactory f = new DefaultJmsListenerContainerFactory();
    f.setConnectionFactory(cf);
    f.setSubscriptionShared(true);
    f.setSubscriptionDurable(true);
    f.setClientId("notification-service"); // unique per deployment pattern per broker docs
    return f;
}
```

---

## Scenario-based interview drills

### S1. Dual-write Oracle + IBM MQ message loss

**Situation:** Settlement service `@Transactional` saves payment row then `jmsTemplate.convertAndSend` to `SETTLEMENT.OUT`. Pod killed after DB commit, before send. Reconciliation finds missing settlements; auditors involved.

**What they're testing:** Dual-write, outbox, XA vs outbox trade-offs, idempotency.

**How to structure your answer:** Failure window → why XA/outbox → concrete fix → consumer dedup → audit narrative.

**Model answer:** This is classic dual-write: JDBC commit and MQ PUT are independent transactions. JVM death after commit but before send loses the message forever while money is recorded — worse than duplicate. I'd implement transactional outbox: same Oracle TX inserts settlement + outbox row; relay process publishes to MQ after commit with `eventId` header. Consumer uses inbox/`processed_events` UNIQUE on business key. I'd reject reintroducing Atomikos XA unless mandated — document two in-doubt TX incidents as lesson. Short-term recovery: reconciliation job compares DB settlements without MQ ack marker; manual republish with audit. Prevention: outbox lag metric, integration test killing process between save and send (should still relay), never `@Transactional` spanning unrelated resources without pattern.

**Common weak answers:** "MQ is reliable"; enable XA without ops plan; retry send without outbox; ignore consumer idempotency.

**Follow-up probes (with answers):**

**Q:** Polling outbox vs Debezium for MQ?
**A:** Same as Kafka — polling simpler; CDC lower latency. MQ relay marks `published_at` after broker ack; duplicates possible — consumer idempotency required.

**Q:** How explain to auditors dropping XA?
**A:** Compensating controls: outbox atomicity, idempotent consumers, reconciliation jobs, BOQ monitoring — demonstrate with test evidence.

---

### S2. Poison message infinite redelivery on IBM MQ

**Situation:** `PAYMENTS.IN` depth grows; one message with invalid ISO date causes listener exception; JMSXDeliveryCount > 100; CPU pegged; good payments delayed.

**What they're testing:** Poison classification, BACKOUT/BOQ, retry policy, ops alerts.

**How to structure your answer:** Detect poison → BACKOUT threshold → BOQ alert → fix schema → controlled replay.

**Model answer:** Application-level permanent failure (bad date format) must not retry forever — IBM MQ increments backout count until `MQRC_BACKED_OUT` routes to BOQ per queue config. I'd alert on BOQ depth > 0 and rising `JMSXDeliveryCount` on main queue. Immediate: move message to BOQ via threshold or manual move, unblock queue. Root cause: producer bug or schema drift — fix upstream validation. Replay from BOQ through controlled tool with operator audit, not raw requeue to main. Distinguish transient DB timeout (retry queue with TTL) from poison (immediate BOQ). Spring: `DefaultMessageListenerContainer` with `setSessionTransacted(true)` and error handler that does not infinite rethrow on `ParseException`.

**Common weak answers:** Increase max redelivery; purge queue; no BOQ; same retry policy for poison and 503.

**Follow-up probes (with answers):**

**Q:** How distinguish poison from transient?
**A:** Exception taxonomy: `JsonProcessingException`/`ValidationException` → BOQ; `TransientDataAccessException` → retry with backoff cap.

**Q:** Safe BOQ replay steps?
**A:** Browse first message, fix producer, replay tool logs operator id, publish to reprocess queue, idempotent consumer.

---

### S3. CLIENT_ACK cumulative ack data loss

**Situation:** Batch listener processes 50 messages per session with `CLIENT_ACKNOWLEDGE`; developer acks only message 50; messages 1–49 considered delivered; finance missing entries.

**What they're testing:** JMS ack semantics, transacted sessions, testing.

**How to structure your answer:** Explain cumulative ack → vendor behavior → switch to transacted or per-message ack → crash tests.

**Model answer:** JMS CLIENT_ACKNOWLEDGE on many providers cumulatively acknowledges all prior unacknowledged messages on the session when one is acked — acking 50 confirms 1–50. If 1–49 failed processing but 50 succeeded, they're lost. Fix: use transacted session committing batch only after all 50 succeed, or AUTO_ACK with single-message listeners, or INDIVIDUAL_ACKNOWLEDGE where supported. I'd add integration test: process batch, fail on message 25, assert redelivery. Document IBM MQ JMS semantics in team wiki. For payments, prefer one-message-per-transaction with idempotency over large cumulative ack batches.

**Common weak answers:** Assume per-message ack; blame broker; no batch testing.

**Follow-up probes (with answers):**

**Q:** AUTO_ACK vs CLIENT for payments?
**A:** AUTO acks when listener returns — swallow exception still acks (loss). Use transacted or manual ack after side effect with rethrow on failure.

**Q:** Compare to Kafka manual commit?
**A:** Similar at-least-once story: commit/ack after success; duplicates on crash before ack; idempotency required.

---

### S4. MQ channel SSL failure blocking settlement

**Situation:** After cert rotation, channel `TO.CORE.BANK` status RETRYING; settlements queue depth 50k; `AMQ9208` SSL peer name mismatch in error log.

**What they're testing:** IBM MQ ops, channels, SSL, production debugging.

**How to structure your answer:** Channel status → SSL cipher/peer → fix cert → drain queue → prevention.

**Model answer:** I'd `DISPLAY CHSTATUS` and `DISPLAY CHLAUTH` on the queue manager, correlate AMQ error with peer certificate CN/SAN vs channel SSLPEER config. Cert rotation often updates leaf but not trust store or peer name pattern on remote QM. Fix mismatch, restart channel, verify RUNNING, then scale consumers to drain depth while watching oldest message age. Prevention: automated cert expiry alerts 30 days ahead, runbook for mutual TLS rotation with dual-trust window, synthetic probe message hourly. This is why bank JDs still test MQ — Kafka knowledge doesn't replace channel debugging.

**Common weak answers:** Restart app only; disable SSL; no depth/age monitoring.

**Follow-up probes (with answers):**

**Q:** RDQM vs MI for this incident?
**A:** Unrelated to SSL — RDQM is replicated QM HA; channel is client connectivity. Don't conflate HA with channel auth.

**Q:** How throttle producers while channel down?
**A:** Backpressure: fail PUT with MQRC_Q_FULL or app circuit breaker; don't unbounded buffer in app memory.

---

### S5. Competing consumers break account ordering

**Situation:** Account statement service runs `@JmsListener(concurrency=10)` on queue `ACCOUNT.POSTINGS`. Customer sees credits before debits; support escalations.

**What they're testing:** Ordering vs competing consumers, message groups, design trade-offs.

**How to structure your answer:** Why FIFO lost → message grouping or partition strategy → scale limits.

**Model answer:** Ten competing consumers on one queue process messages in parallel — completion order ≠ enqueue order. Redelivery and backout further reorder. If business requires per-account serialization, use IBM MQ message grouping (`JMSXGroupID=accountId`) so one consumer owns the group, or split to per-account queues (impractical), or migrate hot path to Kafka keyed by accountId. Scaling beyond one consumer per group requires multiple groups (sharded accounts). I'd measure whether global order is truly required or only per-account. Document ordering guarantee explicitly in integration contract — default JMS queue is not FIFO with concurrency > 1.

**Common weak answers:** "MQ guarantees ordering"; add consumers without grouping; priority queue as fix.

**Follow-up probes (with answers):**

**Q:** Message group hot spot?
**A:** Large account generates all messages with same GroupId — one consumer bottleneck; may need sub-sharding.

**Q:** Kafka vs MQ for this case?
**A:** Kafka partition per key scales better for high-volume per-account order; MQ groups work to moderate TPS.

---

### S6. Request-reply timeout exhausting thread pool

**Situation:** API gateway uses `jmsTemplate.sendAndReceive` to mainframe with 500 threads; mainframe slow; all threads block; HTTP 503 for unrelated endpoints.

**What they're testing:** Request-reply anti-patterns, timeouts, async alternatives.

**How to structure your answer:** Temporal coupling → thread exhaustion → timeout + async callback → when HTTP/gRPC better.

**Model answer:** Synchronous MQ RPC ties HTTP thread lifecycle to mainframe latency. `sendAndReceive` without tight `receiveTimeout` blocks indefinitely; 500 concurrent inquiries exhaust pool — cascading failure. Fix immediate: lower timeout, bulkhead thread pool for MQ calls separate from HTTP, circuit breaker. Medium: async pattern — POST returns 202 + correlId, client polls status queue or WebSocket. Long-term: REST/gRPC to modernized service; reserve MQ request-reply for legacy constraints only. Monitor reply queue depth and age. Never share listener threads between reply consumer and request pool without sizing math.

**Common weak answers:** Increase threads forever; no timeout; temp reply queue per request at high RPS without cleanup.

**Follow-up probes (with answers):**

**Q:** Temp queue vs fixed reply queue?
**A:** Temp convenient low volume; fixed + correlId selector scales; temps leak if connection not closed.

**Q:** Spring sendAndReceive internals?
**A:** Creates temp destination or uses specified reply queue; blocks calling thread until message or timeout.

---

### S7. Rabbit prefetch hoarding on one consumer

**Situation:** Five Rabbit consumers, prefetch=250, messages 2KB; one pod slow (GC); holds 200 unacked; other four idle; queue depth low but age high.

**What they're testing:** Prefetch/QoS tuning, fair dispatch, monitoring message age.

**How to structure your answer:** Prefetch mechanism → unfair distribution → tune prefetch → age metrics.

**Model answer:** Rabbit dispatches up to `prefetchCount` unacked messages per consumer channel — greedy slow consumer hoards work while fast consumers starve. Queue depth alone looks healthy while oldest message age spikes. I'd set `prefetch=1` to `10` based on handler DB latency, enable `basicQos` per-consumer not global, and alert on `message_age` per queue. Scale consumers horizontally; ensure quorum queues for HA. Compare to Kafka: `max.poll.records` similar tuning mindset. Root-fix slow pod (GC, DB locks), don't only tune prefetch.

**Common weak answers:** Raise prefetch to increase throughput blindly; only monitor queue depth.

**Follow-up probes (with answers):**

**Q:** Quorum vs classic queues?
**A:** Quorum (Raft) recommended for HA in modern Rabbit; classic mirrored deprecated; affects performance characteristics.

**Q:** Prefetch vs Kafka fetch.min.bytes?
**A:** Both control in-flight batching; MQ ties to ack; Kafka to poll loop — different backpressure signals.

---

### S8. XA in-doubt transaction after pod kill

**Situation:** Atomikos coordinates Oracle + IBM MQ; pod OOM during 2PC; queue depth frozen; DB shows in-doubt transactions; settlements halted 4 hours.

**What they're testing:** XA operational cost, recovery, why outbox often wins.

**How to structure your answer:** 2PC failure mode → in-doubt resolution → XA recovery scan → strategic outbox migration.

**Model answer:** XA prepare succeeded on one resource, coordinator died before commit — resources hold locks until recovery runs. IBM MQ and Oracle need XA recovery tools (`runmqras`, DBA `RECOVER`/`COMMIT FORCE`) — requires skilled ops, not app restart. Four-hour outage typical without runbook. I'd document heuristic hazards (one resource commits, other rolls back). Strategic fix: outbox + single-resource TX on Oracle, at-least-once MQ with idempotent consumer — accept duplicates, eliminate in-doubt class. If XA mandated by compliance, invest in automated recovery drills, timeout tuning, and dedicated support — not casual adoption.

**Common weak answers:** "XA gives exactly-once"; restart pod fixes in-doubt; no recovery drill.

**Follow-up probes (with answers):**

**Q:** Narayana recovery on K8s?
**A:** Store transaction log on persistent volume; recovery on startup; multiple pods must not share coordinator without clustering.

**Q:** Outbox duplicate vs in-doubt?
**A:** Duplicates handled by idempotency — operational trade teams accept vs hours-long freeze.

---

### S9. Bridge MQ → Kafka ordering and duplicates

**Situation:** Spring listener reads `TRADE.EXEC` from MQ, publishes to Kafka `trades.executed` for analytics. Fraud team sees duplicate trades and occasional out-of-order timestamps after bridge pod restart.

**What they're testing:** Bridge semantics, idempotency, key selection, monitoring.

**How to structure your answer:** At-least-once bridge → idempotent Kafka producer + keys → order scope → lag monitoring.

**Model answer:** Bridge is at-least-once: MQ redelivery after crash before ack duplicates Kafka publishes unless producer uses idempotent keys (`tradeId`) and consumer dedupes. Order: MQ FIFO per queue ≠ Kafka order unless partition key maps trade/account consistently. On restart, unacked MQ messages replay — Kafka may get duplicates; analytics must `UPSERT` by tradeId. Monitor MQ depth + Kafka lag + bridge error rate. Header mapping: preserve `JMSCorrelationID` as Kafka header for trace. Do not claim exactly-once across boundary. Consider Kafka Connect IBM MQ source connector for ops ownership vs bespoke Spring.

**Common weak answers:** Assume bridge is lossless and ordered; no idempotency on sink; ignore MQ backout in bridge.

**Follow-up probes (with answers):**

**Q:** MQ backout message in bridge?
**A:** Route to bridge DLQ, alert, don't publish partial corrupt record to Kafka; schema validate before produce.

**Q:** Connect vs custom Spring?
**A:** Connect gives offset management, scaling tasks; Spring flexible for transforms — ops preference.

---

### S10. Senior MQ war story interview

**Situation:** Interviewer: "Tell me about a hard messaging production incident and what you changed."

**What they're testing:** Operational maturity, patterns, trade-off reasoning — banks hire for this.

**How to structure your answer:** STAR with technical depth: context, failure mode, detection, fix, prevention, rejected alternatives.

**Model answer:** I'd narrate: dual-write settlement loss after pod kill between Oracle commit and MQ send — detected by reconciliation batch, not broker alerts. Root cause: `@Transactional` on DB only, JMS send after commit in separate thread. Fix: outbox table in same TX, polling relay with `published_at`, inbox on consumer with `settlementId` UNIQUE. Rejected Atomikos XA after prior in-doubt incident. Added BOQ alerts, oldest message age dashboard, ISO schema validation at producer. Load test with kill -9 between commit and relay — outbox relay recovered all messages within SLO. Compliance accepted documented idempotency controls replacing XA. This shows I understand crash boundaries, not just API names.

**Common weak answers:** Vague "we restarted the broker"; no business impact; no pattern name; blame vendor only.

**Follow-up probes (with answers):**

**Q:** How test the fix?
**A:** Integration test with Testcontainers/Artemis or MQ dev edition; chaos kill relay; assert exactly-once business effect via idempotency.

**Q:** Greenfield choice today?
**A:** Outbox + MQ or Kafka at boundary; XA only if hard requirement; always idempotent consumers.

---
