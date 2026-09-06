# Apache Kafka — 50 Senior Interview Questions

**Bar:** Partitions, consumer groups, delivery semantics, rebalances, ops. “It’s a queue” fails immediately.

### 1. What is Kafka, if not a queue?

**Short answer:** Kafka is a distributed commit log, not a queue. Producers append records to partitions; consumers read by offset without removing messages. Multiple consumer groups independently track progress on the same data, and retention is governed by time, size, or compaction — not by consumption. In production, the trade-off shows up in on-call incidents and reconciliation jobs — not in hello-world demos.

#### What it is
Apache Kafka is a distributed streaming platform built around an append-only log replicated across brokers. It sits between operational systems and analytics pipelines, carrying high-volume event streams with replay capability. Unlike a traditional message queue where a message disappears after ack, Kafka retains data so any number of downstream readers can catch up, rewind, or reprocess.

#### How it works (internals)
Producers send batches to topic partitions; the broker leader appends to segment files on disk and replicates to followers in the ISR (in-sync replica set). Consumers belong to consumer groups identified by `group.id`; the group coordinator assigns partitions and tracks committed offsets in the `__consumer_offsets` internal topic. Reads are pull-based via `poll()`. Ordering is guaranteed only within a single partition.

#### When to use / when NOT to use
Use Kafka when you need durable, replayable event streams, fan-out to many services, and high throughput with horizontal scale. Do not use it as a work-queue where one consumer deletes a job, or when you need per-message transactional integration with a DB without an outbox/idempotency pattern — Kafka does not replace your OLTP database. Teams that skip load testing and failure injection here usually learn the lesson during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
An e-commerce platform publishes `OrderPlaced`, `PaymentCaptured`, and `ShipmentDispatched` to Kafka. Analytics, fraud, inventory, and email services each have their own consumer group reading the same topics at different speeds. When a bug ships in the inventory projection, ops reset the consumer offset and replay 24 hours of events without republishing from the order service.

#### Common mistakes
Calling Kafka a queue and expecting messages to vanish after read. Assuming one consumer group is the only reader. Underestimating operational cost — brokers, ACLs, schema governance, and consumer lag alerts are part of the product.

#### Interview follow-ups (with model answers)

**Q:** How does Kafka differ from RabbitMQ for work queues?
**A:** For «What is Kafka, if not a queue»: How does Kafka differ from RabbitMQ for work queues. In production, An e-commerce platform publishes `OrderPlaced`, `PaymentCaptured`, and `ShipmentDispatched` to Kafka. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What happens to data after retention expires?
**A:** The follow-on risk of «What happens to data after retention expires» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Why is replay both a feature and an operational risk?
**A:** Trade-off framing for «Why is replay both a feature and an operational risk»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on What is Kafka, if not a queue.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: An e-commerce platform publishes `OrderPlaced`, `PaymentCaptured`, and `ShipmentDispatched` to Kafka.. I suspect calling kafka a queue and expecting messages to vanish after read until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
# Producer — fire-and-forget vs durable
acks=all
enable.idempotence=true
retries=2147483647
```

---

### 2. Topic, partition, offset, replica, ISR.

**Short answer:** A topic is a named stream split into partitions — ordered logs and the unit of parallelism. An offset is a monotonic position within a partition. Replicas are copies for fault tolerance; the leader serves reads/writes while followers catch up. The ISR is the set of replicas sufficiently caught up; `acks=all` waits for ISR acknowledgment.

#### What it is
These five concepts are the vocabulary of every Kafka incident. Topics group related events (`order-events`). Partitions shard a topic for scale. Offsets let consumers resume exactly where they left off. Replication protects against broker loss. ISR is the broker's view of which replicas are safe to acknowledge for durability.

#### How it works (internals)
Each partition has one leader broker and zero or more followers. Producers and consumers talk to the leader. Followers fetch from the leader; when lag is within bounds, they join the ISR. If the leader dies, a controller elects a new leader from the ISR. Consumer offset commits are stored per `(group, topic, partition)` tuple. RF=3 with `min.insync.replicas=2` means a write is durable only when at least two replicas acknowledge.

#### When to use / when NOT to use
Design topics with enough partitions for expected consumer parallelism — changing partition count later reshuffles keyed routing. Set RF≥3 in production and pair `acks=all` with `min.insync.replicas` for money paths. Do not run RF=1 outside dev.

#### Production example
Topic `payments.events` with 12 partitions keyed by `merchantId`, RF=3, `min.insync.replicas=2`. A payment service producer uses `acks=all`; if ISR drops below two during a rack failure, produce fails fast rather than accepting a single-replica write that could be lost on broker crash.

#### Common mistakes
Confusing topic-level ordering with global ordering. Ignoring ISR shrink during disk or network issues. Setting `acks=1` on financial events while claiming durability.

#### Interview follow-ups (with model answers)

**Q:** What happens when all ISR members are offline?
**A:** For «Topic, partition, offset, replica, ISR»: What happens when all ISR members are offline. In production, Topic `payments.events` with 12 partitions keyed by `merchantId`, RF=3, `min.insync.replicas=2`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does the controller pick a new leader?
**A:** The follow-on risk of «How does the controller pick a new leader» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Where are consumer offsets stored?
**A:** Trade-off framing for «Where are consumer offsets stored»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Topic, partition, offset, replica, ISR.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Topic `payments.events` with 12 partitions keyed by `merchantId`, RF=3, `min.insync.replicas=2`.. I suspect confusing topic-level ordering with global ordering until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 3. Why order is per partition, not per topic.

**Short answer:** Total ordering exists only within one partition. Across partitions, no order is guaranteed. Keyed messages land on the same partition via hash, giving per-key order — until you change the partition count, which reshuffles keys and breaks that guarantee. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Kafka scales by splitting a topic into independent ordered logs. There is no global sequence number across a topic. If you need all events for customer A processed in order, you must route all of customer A's events to the same partition — typically by using customer A's ID as the record key.

#### How it works (internals)
The default partitioner maps `hash(key) % partitionCount` (Murmur2 in Java clients). Records with the same key go to the same partition and retain produce order for that key when idempotence/in-flight settings are correct. Records without a key may round-robin or use sticky batching — no key-level order. Consumers in a group read assigned partitions sequentially by offset.

#### When to use / when NOT to use
Use partition keys deliberately for entities that require sequential processing (`orderId`, `accountId`). Do not expect cross-partition causality without application-level sequencing (version vectors, timestamps with careful handling). Avoid increasing partition count on keyed topics without a migration plan.

#### Production example
All lifecycle events for `orderId=42` use key `42` so `OrderCreated`, `PaymentAuthorized`, and `OrderShipped` land in partition 7 and are processed in offset order by one consumer thread. A separate analytics consumer reading all partitions sees interleaved orders — acceptable because analytics aggregates are commutative. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Using a constant key for all messages (hot partition). Changing from 6 to 12 partitions and wondering why payment and refund for the same order now race. Assuming `@KafkaListener` concurrency creates global order.

#### Interview follow-ups (with model answers)

**Q:** How does sticky partitioning affect null-key order?
**A:** For «Why order is per partition, not per topic»: How does sticky partitioning affect null-key order. In production, All lifecycle events for `orderId=42` use key `42` so `OrderCreated`, `PaymentAuthorized`, and `OrderShipped` land in partition 7 and are processed in offset order by one consumer thread. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Can headers replace keys for routing?
**A:** The follow-on risk of «Can headers replace keys for routing» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is the impact of custom partitioners?
**A:** Trade-off framing for «What is the impact of custom partitioners»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Why order is per partition, not per topi.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: All lifecycle events for `orderId=42` use key `42` so `OrderCreated`, `PaymentAuthorized`, and `OrderShipped` land in partition 7 and are processed in offset or…. I suspect using a constant key for all messages (hot partition) until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 4. How partitioning works.

**Short answer:** Records route to partitions via the partitioner: default Murmur2 hash of key modulo partition count, null keys round-robin/sticky, or a custom `Partitioner` implementation. Changing partition count breaks key-to-partition mapping — plan partition count early or migrate with dual-write and careful cutover. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Partitioning is how Kafka achieves parallelism while preserving local order. The producer chooses a partition (explicitly, via key hash, or custom logic). Brokers do not re-partition on ingest — the partition is fixed at produce time.

#### How it works (internals)
Java producer: if `partition` is set on `ProducerRecord`, that wins. Else if key present, `DefaultPartitioner` uses murmur2. Null key uses sticky partitioner (batch locality) in modern clients. Custom partitioners implement business rules (geo routing, tenant shards). Consumers scale up to partition count — extra consumers idle.

#### When to use / when NOT to use
Choose partition count based on peak throughput, consumer parallelism, and retention disk math — not a round number from a blog. Use custom partitioners sparingly; they complicate upgrades and testing. For compacted changelog topics, partition by entity id.

#### Production example
A multi-tenant SaaS uses `tenantId` as key with 48 partitions — enough for 48 concurrent consumer threads per group. One noisy tenant still caps at one partition's throughput; ops add salted sub-keys only for high-volume tenants where per-tenant strict order can be relaxed. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Adding partitions to fix lag without understanding hot keys. Custom partitioner returning random partitions for keyed financial events. Hard-coding partition numbers in application code.

#### Interview follow-ups (with model answers)

**Q:** How do you estimate partition count?
**A:** For «How partitioning works»: How do you estimate partition count. In production, A multi-tenant SaaS uses `tenantId` as key with 48 partitions — enough for 48 concurrent consumer threads per group. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What is KIP-794 sticky partitioner behavior?
**A:** The follow-on risk of «What is KIP-794 sticky partitioner behavior» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How would you re-partition a production topic?
**A:** Trade-off framing for «How would you re-partition a production topic»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing How partitioning works.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: A multi-tenant SaaS uses `tenantId` as key with 48 partitions — enough for 48 concurrent consumer threads per group.. I suspect adding partitions to fix lag without understanding hot keys until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
ProducerRecord<String, OrderEvent> record =
    new ProducerRecord<>("order-events", order.getOrderId(), event);
```

---

### 5. Consumer group: the contract.

**Short answer:** A consumer group is identified by `group.id`. Each partition is assigned to at most one consumer in the group at a time. Scale consumers up to the partition count; extras idle. Different groups maintain independent offsets — fan-out without copying data.

#### What it is
Consumer groups are Kafka's load-balancing and fan-out mechanism. All consumers sharing a `group.id` cooperate as one logical subscriber. The group coordinator broker runs partition assignment and heartbeats.

#### How it works (internals)
On join, the group leader runs a partition assignor (range, round-robin, sticky, cooperative sticky). Each consumer polls its assigned partitions, processes records, and commits offsets. Rebalance revokes and reassigns partitions when members join, leave, or miss heartbeats. Static membership (`group.instance.id`) reduces unnecessary rebalances on rolling restarts.

#### When to use / when NOT to use
One group per microservice deployment that needs competing consumption. Separate groups for billing vs analytics on the same topic. Do not give every developer a unique `group.id` in shared staging without understanding offset commits — you will hide production lag patterns.

#### Production example
Topic `clickstream` has 24 partitions. The `recommendation-engine` service runs 24 pods each with one consumer thread — full parallelism. The `data-lake-ingest` group on the same topic runs 6 heavy consumers — each handles 4 partitions. Both progress independently.

#### Common mistakes
Running 50 consumers against 12 partitions and expecting 50× throughput. Using the same `group.id` for blue and green deployments simultaneously. Forgetting that partition assignment defines which instance owns which keys.

#### Interview follow-ups (with model answers)

**Q:** What is static group membership?
**A:** For «Consumer group: the contract»: What is static group membership. In production, Topic `clickstream` has 24 partitions. The `recommendation-engine` service runs 24 pods each with one consumer thread — full parallelism. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do assignors differ (range vs sticky)?
**A:** The follow-on risk of «How do assignors differ (range vs sticky)» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Can one JVM run multiple consumers in one group?
**A:** Trade-off framing for «Can one JVM run multiple consumers in one group»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Consumer group: the contract.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Topic `clickstream` has 24 partitions. The `recommendation-engine` service runs 24 pods each with one consumer thread — full parallelism.. I suspect running 50 consumers against 12 partitions and expecting 50× throughput until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
spring.kafka.consumer.group-id=payment-projection-v2
spring.kafka.listener.concurrency=6
```

---

### 6. Cooperative vs eager rebalance.

**Short answer:** Eager rebalance stops the world: all consumers revoke all partitions, then reassignment happens — total processing pause. Cooperative sticky rebalance (default in modern clients) revokes only partitions that must move, reducing downtime but still requiring careful handling of in-flight work. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Rebalance is how Kafka reshuffles partition ownership when group membership changes. The protocol evolved from eager (classic) to cooperative incremental to reduce lag spikes during rolling deploys and autoscaling events. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Eager: `onPartitionsRevoked` clears everything; no poll until reassignment completes. Cooperative: first callback revokes subset; consumer keeps unrevoked partitions; second phase assigns new partitions. Both require you to finish commits for revoked partitions before returning from the callback. Rebalances still cause duplicate processing under at-least-once because in-flight messages may be reprocessed by the new owner.

#### When to use / when NOT to use
Stay on cooperative sticky assignors in production (`CooperativeStickyAssignor`). Use static membership and incremental cooperative rebalance tuning for large groups. Avoid custom rebalance listeners that block — they extend stop-the-world windows.

#### Production example
During a Kubernetes rollout of 30 consumers, cooperative rebalance moves only partitions whose pod changed instead of freezing all 30. Lag spikes drop from minutes to seconds, but payment service still uses idempotent DB upserts because duplicates during rebalance remain possible. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming cooperative means no duplicates. Blocking inside `onPartitionsRevoked` waiting for DB — triggers `max.poll.interval.ms` violation and another rebalance. Ignoring rebalance metrics until lag alerts fire.

#### Interview follow-ups (with model answers)

**Q:** What is `partition.assignment.strategy` in Java clients?
**A:** For «Cooperative vs eager rebalance»: What is `partition.assignment.strategy` in Java clients. In production, During a Kubernetes rollout of 30 consumers, cooperative rebalance moves only partitions whose pod changed instead of freezing all 30. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Spring Kafka expose rebalance listeners?
**A:** The follow-on risk of «How does Spring Kafka expose rebalance listeners» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When does cooperative rebalance still pause a partition?
**A:** Trade-off framing for «When does cooperative rebalance still pause a partition»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Cooperative vs eager rebalance.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: During a Kubernetes rollout of 30 consumers, cooperative rebalance moves only partitions whose pod changed instead of freezing all 30.. I suspect assuming cooperative means no duplicates until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 7. What triggers a rebalance?

**Short answer:** Rebalances fire when consumers join or leave the group, subscription patterns change, partition counts change, session timeouts expire (failed heartbeats), or `max.poll.interval.ms` is exceeded because processing took too long between polls. In production, the trade-off shows up in on-call incidents and reconciliation jobs — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before claiming this is solved. The wrong default here usually surfaces as silent data loss, duplicate money movement, or unbounded lag — not as a broker crash.

#### What it is
Rebalance is the group's response to membership or assignment invalidation. It is normal during deploys but pathological when triggered repeatedly by slow consumers or flaky networks. Teams that skip load testing and failure injection here usually learn the lesson during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Heartbeats run on a background thread (Java consumer) while the application thread must call `poll()` within `max.poll.interval.ms`. Long GC pauses, synchronous DB calls inside the poll loop, or thread starvation cause the consumer to be kicked — partitions reassigned while work may still be in flight. `session.timeout.ms` and `heartbeat.interval.ms` govern liveness; `max.poll.interval.ms` governs processing time between polls.

#### When to use / when NOT to use
Set `max.poll.interval.ms` above worst-case batch processing time plus headroom. Reduce `max.poll.records` if processing is heavy. Use pause/resume or async processing patterns only when you understand offset commit ordering. Fix chronic rebalance loops before scaling consumers.

#### Production example
A consumer processing 500-record batches with Oracle upserts averaged 6 minutes per poll — exceeded default `max.poll.interval.ms` (5 minutes). Consumer was removed from group every few minutes, causing endless rebalance churn and duplicate charges until interval was raised and batch size cut.

#### Common mistakes
Blaming Kafka for duplicates without checking rebalance rate metrics. Setting infinite interval instead of fixing slow handlers. Running CPU-throttled pods that miss heartbeats under load.

#### Interview follow-ups (with model answers)

**Q:** Difference between session timeout and max poll interval?
**A:** For «What triggers a rebalance»: Difference between session timeout and max poll interval. In production, A consumer processing 500-record batches with Oracle upserts averaged 6 minutes per poll — exceeded default `max.poll.interval.ms` (5 minutes). I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do you detect rebalance storms in metrics?
**A:** The follow-on risk of «How do you detect rebalance storms in metrics» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is `group.instance.id` for?
**A:** Trade-off framing for «What is `group.instance.id` for»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on What triggers a rebalance.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: A consumer processing 500-record batches with Oracle upserts averaged 6 minutes per poll — exceeded default `max.poll.interval.ms` (5 minutes).. I suspect blaming kafka for duplicates without checking rebalance rate metrics until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 8. poll loop: the law.

**Short answer:** The consumer must call `poll()` frequently enough to stay in the group and receive records. Heartbeats prove liveness; poll also drives partition fetch. Never block the poll thread indefinitely on slow I/O — increase intervals, shrink batches, or offload work with clear offset commit rules. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
The poll loop is the heartbeat of every Kafka consumer application. Everything else — deserialization, business logic, DB writes — competes with the requirement to return to `poll()` in time. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Each `poll(Duration)` returns records from assigned partitions and sends heartbeats. Processing happens between polls. If processing exceeds `max.poll.interval.ms`, the coordinator removes the member. Async patterns: hand off to worker pool but commit offsets only after successful processing; use `pause()` on partitions while backlog builds. Spring `@KafkaListener` wraps this — long `@Transactional` methods still block the listener thread unless concurrency/async is configured.

#### When to use / when NOT to use
Keep poll-thread work short; push heavy CPU to worker pools with ordered per-partition executors if order matters. Tune `max.poll.records` with measured processing time. Do not call external HTTP inside poll without timeout budgets.

#### Production example
Inventory service uses `max.poll.records=50`, processes each batch in under 2 seconds, commits manually after DB flush. Peak Black Friday traffic stays within poll interval; lag stays flat because rebalance is rare.

#### Common mistakes
Single-threaded consumer calling a 30-second REST API per message. Using `@KafkaListener` with default settings on a method that runs a 10-minute report. Assuming heartbeats alone suffice without polling during long work.

#### Interview follow-ups (with model answers)

**Q:** How does pause/resume interact with commits?
**A:** For «poll loop: the law»: How does pause/resume interact with commits. In production, Inventory service uses `max.poll.records=50`, processes each batch in under 2 seconds, commits manually after DB flush. Peak Black Friday traffic stays within poll interval; lag stays flat because rebalance is rare. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What ack mode does Spring use by default?
**A:** The follow-on risk of «What ack mode does Spring use by default» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Can virtual threads change poll tuning?
**A:** Trade-off framing for «Can virtual threads change poll tuning»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on poll loop: the law.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Inventory service uses `max.poll.records=50`, processes each batch in under 2 seconds, commits manually after DB flush.. I suspect single-threaded consumer calling a 30-second rest api per message until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
while (running) {
    ConsumerRecords<K, V> records = consumer.poll(Duration.ofMillis(500));
    for (ConsumerRecord<K, V> record : records) {
        process(record);
    }
    consumer.commitSync();
}
```

---

### 9. Auto-commit vs manual commit.

**Short answer:** Auto-commit periodically commits the last offset returned by poll — not the last successfully processed record. That enables loss (commit before process completes) or duplicates (process then crash before next auto-commit). Production services disable auto-commit and commit explicitly after side effects succeed. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Offset commit is how a consumer group records progress. Auto-commit is convenient for demos; manual commit is how you implement at-least-once or coordinate with transactions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
`enable.auto.commit=true` (default) commits on interval independent of your handler success. Manual: `commitSync()` or `commitAsync()` after DB write; Spring `AckMode.MANUAL_IMMEDIATE` or `RECORD`. Transactional consume-transform-produce uses `sendOffsetsToTransaction`. Committing before side effects = at-most-once; after = at-least-once with duplicates on failure.

#### When to use / when NOT to use
Disable auto-commit for any service with external side effects (DB, payments, email). Use auto-commit only for best-effort metrics where loss is acceptable. Pair manual commit with idempotent consumers.

#### Production example
Payment projection sets `enable.auto.commit=false`, upserts into Oracle inside a transaction, then commits offset. Crash after DB commit but before offset commit causes redelivery — handled by unique constraint on `eventId`.

#### Common mistakes
Enabling auto-commit because manual is harder — then losing events silently on handler exceptions. Committing per record on a 10k batch (throughput collapse). Async commit without error callback logging failures.

#### Interview follow-ups (with model answers)

**Q:** What is `commitSync` vs `commitAsync` trade-off?
**A:** For «Auto-commit vs manual commit»: What is `commitSync` vs `commitAsync` trade-off. In production, Payment projection sets `enable.auto.commit=false`, upserts into Oracle inside a transaction, then commits offset. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does BATCH ack mode work in Spring?
**A:** The follow-on risk of «How does BATCH ack mode work in Spring» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When would you commit before processing?
**A:** Trade-off framing for «When would you commit before processing»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Auto-commit vs manual commit.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment projection sets `enable.auto.commit=false`, upserts into Oracle inside a transaction, then commits offset.. I suspect enabling auto-commit because manual is harder — then losing events silently on handler exceptions until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
enable.auto.commit=false
# commit in listener after successful processing
```

---

### 10. At-most-once vs at-least-once vs exactly-once.

**Short answer:** At-most-once commits before processing — messages can be lost. At-least-once processes then commits — duplicates on retry. Exactly-once in Kafka combines idempotent producer and transactions with `read_committed` consumers; exactly-once effect across DB requires idempotent consumers plus outbox or dedup tables. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Delivery semantics describe what happens when producers retry and consumers crash mid-batch. Senior interviews expect you to name both broker-level EOS and application-level idempotency. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
At-most-once: auto-commit or commit-before-process. At-least-once: process then commit; duplicates on rebalance/crash. Kafka EOS: `enable.idempotence=true` dedups producer retries per partition; `transactional.id` fences zombies and atomically writes multi-partition batches plus offset commits. Consumers with `isolation.level=read_committed` skip aborted transactions. JDBC/Oracle writes are not in the Kafka transaction — dual-write remains.

#### When to use / when NOT to use
Default production path: at-least-once + idempotent consumer. Use Kafka transactions for consume-transform-produce within Kafka only. Do not claim EOS to stakeholders without defining the boundary (Kafka vs end-to-end).

#### Production example
Fraud scoring reads from `payments`, writes scores to `fraud-scores`, commits offsets in one Kafka transaction — EOS within Kafka. Billing service consumes `fraud-scores` and updates Oracle with inbox table keyed by `eventId` — end-to-end exactly-once effect. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Saying exactly-once without mentioning duplicates on rebalance. Assuming `@Transactional` on Spring service covers Kafka offset and Oracle row atomically. Using EOS producer without `read_committed` consumers.

#### Interview follow-ups (with model answers)

**Q:** What does read_uncommitted expose?
**A:** For «At-most-once vs at-least-once vs exactly-once»: What does read_uncommitted expose. In production, Fraud scoring reads from `payments`, writes scores to `fraud-scores`, commits offsets in one Kafka transaction — EOS within Kafka. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does outbox achieve end-to-end reliability?
**A:** The follow-on risk of «How does outbox achieve end-to-end reliability» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Is at-least-once always good enough?
**A:** Trade-off framing for «Is at-least-once always good enough»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to At-most-once vs at-least-once vs exactly.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Fraud scoring reads from `payments`, writes scores to `fraud-scores`, commits offsets in one Kafka transaction — EOS within Kafka.. I suspect saying exactly-once without mentioning duplicates on rebalance until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 11. Idempotent producer.

**Short answer:** Enable with `enable.idempotence=true` (default on recent Java clients). The broker assigns a producer ID (PID) and tracks sequence numbers per partition, deduplicating retries caused by network blips. It does not deduplicate two different producer instances sending the same business event. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Idempotent producer solves the 'retry creates duplicate messages' problem at the transport layer for a single producer instance. It is a prerequisite for transactional producer and a baseline for durable produce. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
On first produce to a partition, broker registers PID and sequence 0, 1, 2… Retries with same sequence are ignored as duplicates. Requires `acks=all`, `retries>0`, and caps `max.in.flight.requests.per.connection` (≤5 with idempotence). New producer instance gets new PID — duplicate business events from two pods are not deduped.

#### When to use / when NOT to use
Leave idempotence enabled in production. Still use business keys and idempotent consumers for multi-instance producers. Do not disable to shave latency without measuring.

#### Production example
Order service pod restarts mid-send; producer retries `OrderPlaced` three times; broker accepts one copy. A blue/green deploy with two pods both publishing the same order without idempotent consumer still creates duplicate downstream rows. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Believing idempotent producer equals idempotent business processing. Disabling idempotence to debug without re-enabling. Assuming keys alone prevent duplicates from retries.

#### Interview follow-ups (with model answers)

**Q:** What happens on broker restart to PID state?
**A:** For «Idempotent producer»: What happens on broker restart to PID state. In production, Order service pod restarts mid-send; producer retries `OrderPlaced` three times; broker accepts one copy. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Interaction with `max.in.flight.requests`?
**A:** The follow-on risk of «Interaction with `max.in.flight.requests`» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Does idempotence work with `acks=1`?
**A:** Trade-off framing for «Does idempotence work with `acks=1`»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Idempotent producer.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order service pod restarts mid-send; producer retries `OrderPlaced` three times; broker accepts one copy.. I suspect believing idempotent producer equals idempotent business processing until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
enable.idempotence=true
acks=all
retries=2147483647
max.in.flight.requests.per.connection=5
```

---

### 12. Transactional producer (`transactional.id`).

**Short answer:** Set a unique `transactional.id` per producer instance. Transactions atomically write to multiple partitions and can commit consumer offsets via `sendOffsetsToTransaction` for consume-transform-produce pipelines. Old instances are fenced with `ProducerFencedException`. Consumers must use `isolation.level=read_committed`.

#### What it is
Transactional producer extends idempotence with atomic multi-record commits and zombie fencing — the foundation of Kafka's exactly-once semantics within the broker. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer calls `initTransactions()`, `beginTransaction()`, sends records, optionally `sendOffsetsToTransaction`, then `commitTransaction()` or `abortTransaction()`. Transaction coordinator broker tracks epochs; a stale producer with old epoch is fenced. Aborted records are invisible to `read_committed` consumers. Transaction timeout aborts hung transactions.

#### When to use / when NOT to use
Use for stream processing that writes multiple output topics and commits input offsets atomically. Requires ops to manage `transactional.id` uniqueness per instance (often prefix + static member id). Overkill for simple fire-and-forget publish from a REST controller.

#### Production example
Stream job reads `orders`, emits to `enriched-orders` and `order-metrics`, commits source offsets in one transaction per batch. Rolling deploy fences old pod's producer before it can double-write metrics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Reusing same `transactional.id` on two running instances — fencing loops. Forgetting `read_committed` on downstream consumers — they see aborted data. Long transactions exceeding `transaction.timeout.ms`.

#### Interview follow-ups (with model answers)

**Q:** How does fencing work with epochs?
**A:** For «Transactional producer (`transactional.id`)»: How does fencing work with epochs. In production, Stream job reads `orders`, emits to `enriched-orders` and `order-metrics`, commits source offsets in one transaction per batch. Rolling deploy fences old pod's producer before it can double-write metrics. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Spring `KafkaTransactionManager` setup?
**A:** The follow-on risk of «Spring `KafkaTransactionManager` setup» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Performance cost of transactions?
**A:** Trade-off framing for «Performance cost of transactions»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Transactional producer (`transactional.i.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Stream job reads `orders`, emits to `enriched-orders` and `order-metrics`, commits source offsets in one transaction per batch.. I suspect reusing same `transactional until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, "billing-tx-" + instanceId);
props.put(ConsumerConfig.ISOLATION_LEVEL_CONFIG, "read_committed");
```

---

### 13. Why EOS doesn't magically update Oracle.

**Short answer:** Kafka transactions commit only within Kafka. Writing to Oracle and Kafka in two separate systems is a dual write — no single atomic commit spans both. Patterns: transactional outbox in Oracle, inbox dedup table, or CDC from DB — not blind `@Transactional` wrapping both. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
End-to-end exactly-once across Kafka and a relational database is the question that separates senior candidates from those who read marketing slides. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka TX coordinates partition writes and offset commits on Kafka brokers. JDBC commits on Oracle are independent. Failure modes: Oracle committed, offset not — duplicate on replay; offset committed, Oracle rolled back — ghost progress. Outbox: insert business row + outbox row in one Oracle TX; relay publishes to Kafka. Consumer side: process in Oracle TX with idempotency key, then commit Kafka offset.

#### When to use / when NOT to use
Never assume Spring `@Transactional` + `kafkaTemplate.send` is atomic. Use outbox for publish-after-DB. Use inbox/`processed_events` for consume-to-DB. Kafka Connect JDBC sink has its own semantics — read docs before money paths.

#### Production example
Order service saves order and outbox entry in one `@Transactional` JPA method. Debezium or polling relay publishes to Kafka. Payment consumer inserts into `processed_events` with PK on `eventId`, updates balances, then commits offset manually.

#### Common mistakes
Calling it exactly-once because EOS is enabled on producer. Publishing to Kafka before DB commit. Using Kafka as source of truth for balances without constraints.

#### Interview follow-ups (with model answers)

**Q:** Compare outbox vs CDC for publishing?
**A:** For «Why EOS doesn't magically update Oracle»: Compare outbox vs CDC for publishing. In production, Order service saves order and outbox entry in one `@Transactional` JPA method. Debezium or polling relay publishes to Kafka. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What is the inbox pattern?
**A:** The follow-on risk of «What is the inbox pattern» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Can XA/JTA solve this cleanly?
**A:** Trade-off framing for «Can XA/JTA solve this cleanly»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Why EOS doesn't magically update Oracle.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order service saves order and outbox entry in one `@Transactional` JPA method. Debezium or polling relay publishes to Kafka.. I suspect calling it exactly-once because eos is enabled on producer until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 14. Log compaction.

**Short answer:** For compacted topics, the broker retains the latest record per key and eventually removes older versions. Tombstones (null value) delete keys. Ideal for changelog topics, KTables, and entity state — not for immutable event histories keyed by random UUIDs. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Log compaction is Kafka's way to keep a compacted snapshot stream: the last known value per key survives, turning the topic into a materialized key-value log rather than an infinite append history. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Cleaner thread scans log segments; for each key, only the latest offset survives (plus tombstones until `delete.retention.ms`). Compaction runs in the background — tail reads may still see superseded values briefly. `cleanup.policy=compact` or `compact,delete`. Requires meaningful keys; UUID-per-event keys never compact meaningfully.

#### When to use / when NOT to use
Use compacted topics for config, feature flags, user profile snapshots, Kafka Streams state changelog topics. Do not compact raw audit logs keyed by event id. Combine with `delete` policy when you need both snapshot and time retention.

#### Production example
Topic `account-balances` keyed by `accountId` holds latest balance for fast bootstrap of new fraud service instances — they compact-read to build local cache without replaying five years of transfers. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Compacting clickstream with random keys expecting disk savings. Reading before compaction completes and assuming stale value is truth. Missing tombstones on GDPR deletes.

#### Interview follow-ups (with model answers)

**Q:** Head vs tail compaction behavior?
**A:** For «Log compaction»: Head vs tail compaction behavior. In production, Topic `account-balances` keyed by `accountId` holds latest balance for fast bootstrap of new fraud service instances — they compact-read to build local cache without replaying five years of transfers. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do Streams changelog topics use compaction?
**A:** The follow-on risk of «How do Streams changelog topics use compaction» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is `min.compaction.lag.ms`?
**A:** Trade-off framing for «What is `min.compaction.lag.ms`»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Log compaction.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Topic `account-balances` keyed by `accountId` holds latest balance for fast bootstrap of new fraud service instances — they compact-read to build local cache wi…. I suspect compacting clickstream with random keys expecting disk savings until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 15. Tombstones.

**Short answer:** A tombstone is a record with a key and null value. On compacted topics, it signals deletion of that key; the cleaner removes the key after `delete.retention.ms`. Consumers must treat null payloads as deletes in materialized views. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Tombstones are how Kafka represents deletion in a log-based system that otherwise only appends. They matter for GDPR, entity removal, and KTable semantics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer sends `ProducerRecord<>(key, null)`. Compaction retains tombstone until delete retention elapses, then removes key entirely. Consumers building RocksDB state stores apply tombstone as delete. Non-compacted topics may retain tombstones like normal records until segment deletion.

#### When to use / when NOT to use
Emit tombstones when an entity is deleted and downstream caches must drop it. Set `delete.retention.ms` high enough for slow consumers to observe deletes. Pair with compacted topics keyed by entity id.

#### Production example
User profile topic emits tombstone on account closure; recommendation service removes features from cache; compliance verifies key absent after compaction lag plus delete retention window. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Null payload on non-compacted topic confusing consumers. Tombstone without compact policy — useless retention bloat. Consumers ignoring null values and serving stale GDPR data.

#### Interview follow-ups (with model answers)

**Q:** How long do tombstones linger?
**A:** For «Tombstones»: How long do tombstones linger. In production, User profile topic emits tombstone on account closure; recommendation service removes features from cache; compliance verifies key absent after compaction lag plus delete retention window. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Compacted topic + GDPR erasure workflow?
**A:** The follow-on risk of «Compacted topic + GDPR erasure workflow» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Spring deserializer handling null values?
**A:** Trade-off framing for «Spring deserializer handling null values»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Tombstones.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: User profile topic emits tombstone on account closure; recommendation service removes features from cache; compliance verifies key absent after compaction lag p…. I suspect null payload on non-compacted topic confusing consumers until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 16. Retention vs compaction vs `delete` policy.

**Short answer:** `cleanup.policy=delete` drops segments by time (`retention.ms`) or size. `compact` keeps latest per key. `compact,delete` applies both — compact keys and delete segments by retention. Random UUID keys with compact policy waste cleaner CPU.

#### What it is
Retention policies define how long data lives on disk and what guarantees consumers have for replay windows. Compaction and delete solve different problems and are often combined. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Delete-only topics: events age out uniformly — good for immutable event logs with bounded replay. Compact: changelog semantics. Combined: changelog capped by time — old keys eventually disappear entirely if no new writes. `retention.bytes` and per-partition limits prevent disk fill.

#### When to use / when NOT to use
Event sourcing integration topics: delete with 7–30 day retention plus cold storage export. Entity state: compact. High-volume telemetry: delete only, short retention. Document retention per topic in runbooks.

#### Production example
`order-events` delete retention 14 days for replay during incidents. `order-snapshot` compact,delete with 90-day retention for projection rebuild without infinite disk. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Compact on UUID-keyed events. Infinite retention on high-QPS topics without disk alerts. Changing policy without recalculating disk budget.

#### Interview follow-ups (with model answers)

**Q:** How does tiered storage affect retention?
**A:** For «Retention vs compaction vs `delete` policy»: How does tiered storage affect retention. In production, `order-events` delete retention 14 days for replay during incidents. `order-snapshot` compact,delete with 90-day retention for projection rebuild without infinite disk. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Can you change cleanup.policy live?
**A:** The follow-on risk of «Can you change cleanup.policy live» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** What is segment.bytes impact?
**A:** Trade-off framing for «What is segment.bytes impact»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Retention vs compaction vs `delete` poli.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `order-events` delete retention 14 days for replay during incidents.. I suspect compact on uuid-keyed events until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 17. Consumer lag.

**Short answer:** Lag is roughly `endOffset - committedOffset` per partition (or current position vs log end). High lag means consumers cannot keep up — from slow processing, GC, rebalances, hot partitions, insufficient consumers, or downstream DB bottlenecks. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Consumer lag is the primary health signal for Kafka-backed pipelines. It translates directly into stale dashboards, delayed fraud checks, and missed SLAs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Metrics: `records-lag-max`, `records-lag`, per-partition lag in Burrow or Kafka exporter. Causes include long handler time, `max.poll.records` too high, rebalance storms, skewed keys, Oracle lock contention, and under-provisioned consumer pods. Alert on lag magnitude and lag time (how far behind wall clock for time-sensitive topics).

#### When to use / when NOT to use
Monitor lag per group and partition, not just cluster CPU. Scale consumers to partition count, optimize hot keys, tune batch sizes. Do not only alert on absolute offset lag without time context.

#### Production example
Fraud lag on partition 3 spikes while others flat — investigation finds one merchantId dominates key space. Salting strategy documented; lag SLO restored after targeted fix rather than blind scale-out. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Scaling consumers beyond partition count expecting improvement. Ignoring lag during rebalance as normal forever. No alert on growing lag derivative.

#### Interview follow-ups (with model answers)

**Q:** Difference between offset lag and time lag?
**A:** For «Consumer lag»: Difference between offset lag and time lag. In production, Fraud lag on partition 3 spikes while others flat — investigation finds one merchantId dominates key space. Salting strategy documented; lag SLO restored after targeted fix rather than blind scale-out. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Kafka Exporter expose lag?
**A:** The follow-on risk of «How does Kafka Exporter expose lag» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is lag acceptable by design?
**A:** Trade-off framing for «When is lag acceptable by design»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Consumer lag.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Fraud lag on partition 3 spikes while others flat — investigation finds one merchantId dominates key space.. I suspect scaling consumers beyond partition count expecting improvement until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 18. Hot partitions.

**Short answer:** When one key dominates traffic, a single partition becomes the throughput ceiling for that topic — hot partition. Fixes include better key design, salting with acceptance of ordering trade-offs, more partitions (does not help one key), or async fan-out within the consumer. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Hot partitions are the Kafka equivalent of a database hot row — all parallelism collapses to one broker disk and one consumer thread for that key's world. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Keyed routing sends all events for `tenant=WALMART` to one partition. Producer batching amplifies leader load on that broker. Consumer group assigns one consumer that partition — others idle for that key's work. Monitoring shows one partition with high produce/consume rate and lag while peers are idle.

#### When to use / when NOT to use
Identify dominant keys in staging load tests. Split business keys (per-store vs per-chain) when order allows. Use dedicated topics for mega-tenants. Salting (`key + shard`) only when strict per-tenant order can relax.

#### Production example
Global retailer keyed by parent tenant id saturated partition 0. Refactored to `storeId` key — order per store preserved, load spreads across 24 partitions, peak lag dropped 80%. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Adding 100 partitions when one key causes heat. Random keys on events that must be ordered. Ignoring broker-level metrics per partition.

#### Interview follow-ups (with model answers)

**Q:** How to detect hot keys in production?
**A:** For «Hot partitions»: How to detect hot keys in production. In production, Global retailer keyed by parent tenant id saturated partition 0. Refactored to `storeId` key — order per store preserved, load spreads across 24 partitions, peak lag dropped 80%. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Salt pattern without losing all ordering?
**A:** The follow-on risk of «Salt pattern without losing all ordering» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Dedicated cluster for noisy neighbor?
**A:** Trade-off framing for «Dedicated cluster for noisy neighbor»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Hot partitions.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Global retailer keyed by parent tenant id saturated partition 0.. I suspect adding 100 partitions when one key causes heat until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 19. Producer acks and `min.insync.replicas`.

**Short answer:** `acks=0` fire-and-forget; `acks=1` waits for leader only; `acks=all` waits for all ISR members to acknowledge. Durability requires `acks=all` plus broker topic config `min.insync.replicas` (typically 2 when RF=3). If ISR shrinks below min, produce fails — availability vs durability trade-off. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Producer acknowledgments and ISR minimum define how many replica failures you survive without silent data loss. This is core Kafka ops knowledge for any Java backend role. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Leader appends to local log; followers fetch. ISR = replicas within lag bound. `acks=all` means leader waits for ISR acks before responding. `min.insync.replicas=2` on RF=3 means at least two brokers must acknowledge or produce throws `NotEnoughReplicasException`. `acks=1` can lose data if leader dies before replication.

#### When to use / when NOT to use
Money and order events: `acks=all`, RF=3, `min.insync.replicas=2`. Metrics/logging: maybe `acks=1` with eyes open. Never `acks=0` for anything downstream humans trust.

#### Production example
During rack maintenance ISR drops to 1; payment producer correctly fails fast; ops pause traffic rather than accept single-copy writes. Clickstream producer on `acks=1` continues with documented RPO. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Claiming RF=3 alone guarantees durability without min.insync.replicas. Using `acks=all` with RF=1 in dev and copying to prod unchanged. Lowering min ISR to restore availability during incident without postmortem.

#### Interview follow-ups (with model answers)

**Q:** What is `unclean.leader.election` interaction?
**A:** For «Producer acks and `min.insync.replicas`»: What is `unclean.leader.election` interaction. In production, During rack maintenance ISR drops to 1; payment producer correctly fails fast; ops pause traffic rather than accept single-copy writes. Clickstream producer on `acks=1` continues with documented RPO. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do clients retry NotEnoughReplicas?
**A:** The follow-on risk of «How do clients retry NotEnoughReplicas» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Latency impact of acks=all?
**A:** Trade-off framing for «Latency impact of acks=all»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Producer acks and `min.insync.replicas`.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: During rack maintenance ISR drops to 1; payment producer correctly fails fast; ops pause traffic rather than accept single-copy writes.. I suspect claiming rf=3 alone guarantees durability without min until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
# broker topic config
min.insync.replicas=2
replication.factor=3

# producer
acks=all
```

---

### 20. Replication factor and ISR shrink.

**Short answer:** Replication factor (RF) is copy count per partition — RF=3 is production standard. ISR shrink happens when followers fall behind or die; with `unclean.leader.election.enable=false` (recommended), Kafka prefers unavailability over electing an out-of-sync leader that would lose data. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Replication is Kafka's fault tolerance story. ISR dynamics explain many production write outages and read inconsistency windows. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Each partition has one leader and RF-1 followers. Controller manages leader election from ISR. Follower out of ISR cannot become leader if unclean election disabled — partition may be unavailable to produce with `acks=all`. Disk loss, network partition, or slow broker shrinks ISR. Monitor under-replicated partitions and offline replicas.

#### When to use / when NOT to use
RF=3 across racks/AZ when possible. Keep unclean leader election disabled for data-critical clusters. Accept brief write unavailability during broker loss rather than silent truncation.

#### Production example
Broker disk failure removes follower; ISR goes from 3 to 2; cluster healthy. Two simultaneous failures with min ISR=2 block produces until ops replaces broker — correct behavior for payment cluster. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Enabling unclean election to green-light a cluster — trades data loss for uptime. RF=2 without rack awareness. Ignoring under-replicated partition alerts.

#### Interview follow-ups (with model answers)

**Q:** How long can a partition be under-replicated?
**A:** For «Replication factor and ISR shrink»: How long can a partition be under-replicated. In production, Broker disk failure removes follower; ISR goes from 3 to 2; cluster healthy. Two simultaneous failures with min ISR=2 block produces until ops replaces broker — correct behavior for payment cluster. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Preferred leader election?
**A:** The follow-on risk of «Preferred leader election» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** RF vs min ISR math?
**A:** Trade-off framing for «RF vs min ISR math»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Replication factor and ISR shrink.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Broker disk failure removes follower; ISR goes from 3 to 2; cluster healthy.. I suspect enabling unclean election to green-light a cluster — trades data loss for uptime until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 21. Message size and batching.

**Short answer:** Producers batch records using `batch.size` and `linger.ms` before sending — throughput vs latency trade-off. Huge messages hurt brokers and consumers; cap with `max.message.bytes` / `max.request.size` and store blobs externally with pointers in Kafka. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Batching is how Kafka achieves millions of msgs/sec; message size limits protect brokers from OOM and slow consumers from choke points. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer accumulates records per partition until batch full or linger elapsed, then sends compressed batch. Broker `message.max.bytes` rejects oversize. Large payloads inflate replication time, consumer heap, and rebalance recovery. Anti-pattern: 5MB JSON in Kafka — use S3 + reference.

#### When to use / when NOT to use
Tune `linger.ms` (5–20ms) and `batch.size` (16–128KB) for throughput. Keep messages KB-scale for events; MB for exceptional cases with raised limits cluster-wide. Align `max.poll.records` with deserialize cost.

#### Production example
Product catalog change event carries SKU metadata under 4KB; image bytes live in object storage; Kafka message has `{sku, s3Url, checksum}`. Broker `message.max.bytes=1048576` as safety net.

#### Common mistakes
Default producer with no batching on high-QPS service — CPU burn. Raising max message to 10MB to fix design smell. Consumer OOM on fat JSON batches.

#### Interview follow-ups (with model answers)

**Q:** How does batching interact with compression?
**A:** For «Message size and batching»: How does batching interact with compression. In production, Product catalog change event carries SKU metadata under 4KB; image bytes live in object storage; Kafka message has `{sku, s3Url, checksum}`. Broker `message.max.bytes=1048576` as safety net. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Per-topic size limits?
**A:** The follow-on risk of «Per-topic size limits» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Fetch size tuning on consumer?
**A:** Trade-off framing for «Fetch size tuning on consumer»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Message size and batching.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Product catalog change event carries SKU metadata under 4KB; image bytes live in object storage; Kafka message has `{sku, s3Url, checksum}`. Broker `message.. I suspect default producer with no batching on high-qps service — cpu burn until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
linger.ms=10
batch.size=65536
max.request.size=1048576
```

---

### 22. Compression.

**Short answer:** Compression happens on the producer (`compression.type`: lz4, snappy, gzip, zstd). Brokers store compressed batches; consumers decompress. zstd often gives best ratio/CPU today. Avoid double-compressing already gzipped payloads.

#### What it is
Compression trades CPU for network and disk — usually a win on JSON event streams at scale. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer compresses entire batch per partition. Broker may recompress if broker-level type differs (avoid mismatch). Consumer pays decompression cost on read. Metrics: compression rate on broker JMX. lz4/snappy for low latency; zstd for analytics ingress.

#### When to use / when NOT to use
Enable compression on text-heavy events unless CPU-bound on tiny messages. Standardize type cluster-wide where possible. Do not gzip in app then set compression.type=gzip on nested garbage.

#### Production example
Order events JSON compress 4:1 with zstd — cross-AZ bandwidth bill drops; p99 produce latency unchanged on c5 instances. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Compression=none on 1KB messages wondering why network saturated. Mixing snappy produce and gzip broker recompress. Ignoring consumer CPU after enabling zstd.

#### Interview follow-ups (with model answers)

**Q:** Broker vs producer compression config?
**A:** For «Compression»: Broker vs producer compression config. In production, Order events JSON compress 4:1 with zstd — cross-AZ bandwidth bill drops; p99 produce latency unchanged on c5 instances. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Impact on log compaction?
**A:** The follow-on risk of «Impact on log compaction» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When compression hurts?
**A:** Trade-off framing for «When compression hurts»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Compression.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order events JSON compress 4:1 with zstd — cross-AZ bandwidth bill drops; p99 produce latency unchanged on c5 instances.. I suspect compression=none on 1kb messages wondering why network saturated until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
compression.type=zstd
# or lz4 for lower CPU
```

---

### 23. Schema Registry (Avro/JSON Schema/Protobuf).

**Short answer:** Schema Registry stores versioned schemas; serializers embed schema id (Confluent wire format). Compatibility modes (BACKWARD, FORWARD, FULL) govern evolution. Breaking changes — required fields without defaults, type changes — fail registration or break consumers at runtime. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Schema Registry is the contract enforcement layer for Kafka events in typed ecosystems — essential when dozens of Java services share topics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer registers schema (or uses id); payload carries magic byte + schema id + serialized bytes. Consumer fetches schema by id. BACKWARD: new schema reads old data (add optional fields). FORWARD: old consumer reads new data. Subject strategies: TopicNameStrategy vs RecordNameStrategy. JSON Schema and Protobuf supported alongside Avro.

#### When to use / when NOT to use
Adopt Registry before v2 of your event platform. CI checks compatibility on PR. Prefer BACKWARD for consumer-first rollouts. Do not publish raw JSON strings without version discipline in multi-team orgs.

#### Production example
Team adds optional `loyaltyPoints` to `OrderPlaced` Avro record — BACKWARD compatible; old consumers ignore field; new consumers read it. Someone tries to change `orderId` int→string — registration rejected in CI. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Skipping compatibility check in prod register. Using TOPIC strategy when multiple event types share topic. Required field additions without default breaking old consumers silently at decode.

#### Interview follow-ups (with model answers)

**Q:** Avro vs Protobuf for Java teams?
**A:** For «Schema Registry (Avro/JSON Schema/Protobuf)»: Avro vs Protobuf for Java teams. In production, Team adds optional `loyaltyPoints` to `OrderPlaced` Avro record — BACKWARD compatible; old consumers ignore field; new consumers read it. Someone tries to change `orderId` int→string — registration rejected in CI. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** What is schema id caching?
**A:** The follow-on risk of «What is schema id caching» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How do tombstones work with Avro?
**A:** Trade-off framing for «How do tombstones work with Avro»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Schema Registry (Avro/JSON Schema/Protob.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Team adds optional `loyaltyPoints` to `OrderPlaced` Avro record — BACKWARD compatible; old consumers ignore field; new consumers read it.. I suspect skipping compatibility check in prod register until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
# Avro serializer config
schema.registry.url=https://schema-registry:8081
value.subject.name.strategy=io.confluent.kafka.serializers.subject.TopicRecordNameStrategy
```

---

### 24. Poison pill.

**Short answer:** A poison pill is a record that always fails deserialization or business validation — infinite retry blocks the partition under strict ordering. Strategies: bounded retries, dead-letter topic (DLT), skip with audit (breaks order), or validate at producer (best). In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Poison pills are the operational reality of immutable logs — one bad byte sequence or schema mismatch can stall an entire partition if you naively retry forever. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
With per-partition order, failing record N prevents processing N+1. Spring `DefaultErrorHandler` with `DeadLetterPublishingRecoverer` sends to DLT after N failures. Retry topics with backoff sacrifice order for liveness. Schema validation at producer prevents many pills.

#### When to use / when NOT to use
Always define DLT + alert path before production. Choose stall vs skip based on domain — payments stall with manual intervention; metrics can DLT. Log partition, offset, key, hex payload header for triage.

#### Production example
Malformed Avro after bad deploy: consumer fails; after 3 retries record goes to `orders.DLT`; PagerDuty fires; ops fix schema and replay DLT with tooling — main partition unblocked. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Infinite retry on `NumberFormatException`. DLT without monitoring — silent data loss. Replay DLT into main topic without fixing root cause — immediate re-poison.

#### Interview follow-ups (with model answers)

**Q:** Spring Kafka ErrorHandler configuration?
**A:** For «Poison pill»: Spring Kafka ErrorHandler configuration. In production, Malformed Avro after bad deploy: consumer fails; after 3 retries record goes to `orders.DLT`; PagerDuty fires; ops fix schema and replay DLT with tooling — main partition unblocked. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Ordering implications of retry topics?
**A:** The follow-on risk of «Ordering implications of retry topics» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to replay DLT safely?
**A:** Trade-off framing for «How to replay DLT safely»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Poison pill.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Malformed Avro after bad deploy: consumer fails; after 3 retries record goes to `orders.. I suspect infinite retry on `numberformatexception` until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Bean
DefaultErrorHandler handler() {
    return new DefaultErrorHandler(
        new DeadLetterPublishingRecoverer(kafkaTemplate),
        new FixedBackOff(1000L, 3L));
}
```

---

### 25. Retry topics vs block.

**Short answer:** In-place retry on the main partition preserves order but stalls all messages behind the failure. Retry topics with delay break ordering for that key but restore liveness. Payments often block; clickstream often DLTs quickly. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
This is the fundamental tension between ordering guarantees and system progress — Kafka forces you to choose explicitly. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Block: consumer loops retry same offset — partition frozen. Retry topic: failed record republished to `orders-retry-1` with header metadata; separate consumer retries later — other keys on main partition continue. Spring non-blocking retry topics implement staged delays. Re-entering main topic must preserve idempotency.

#### When to use / when NOT to use
Choose block when every message for a key must serialize (ledger). Choose retry/DLT when independent keys dominate and staleness is worse than temporary disorder. Document choice in service ADR.

#### Production example
Wire transfer consumer stalls partition on transient Oracle lock — acceptable for 30 seconds with backoff cap. Clickstream bad user-agent string goes to DLT in one shot — 0.01% loss acceptable.

#### Common mistakes
Retry topic without idempotent consumer — duplicates on re-entry. Blocking forever on non-transient bug. Using retry for poison schema without fixing producer.

#### Interview follow-ups (with model answers)

**Q:** Spring `@RetryableTopic` semantics?
**A:** For «Retry topics vs block»: Spring `@RetryableTopic` semantics. In production, Wire transfer consumer stalls partition on transient Oracle lock — acceptable for 30 seconds with backoff cap. Clickstream bad user-agent string goes to DLT in one shot — 0.01% loss acceptable. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to preserve order with per-key executors?
**A:** The follow-on risk of «How to preserve order with per-key executors» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When is blocking mandatory?
**A:** Trade-off framing for «When is blocking mandatory»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Retry topics vs block.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Wire transfer consumer stalls partition on transient Oracle lock — acceptable for 30 seconds with backoff cap.. I suspect retry topic without idempotent consumer — duplicates on re-entry until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 26. Spring Kafka `@KafkaListener`.

**Short answer:** Spring Kafka wraps the consumer poll loop in `@KafkaListener` methods with configurable concurrency, error handlers, ack modes, and DLT support. Each concurrent listener consumer participates in the same group; concurrency should align with assigned partitions. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
`@KafkaListener` is how most Java microservices consume Kafka — understanding its threading, ack, and error semantics is essential for Spring-heavy JDs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Container factory creates listener containers — one consumer per concurrency slot by default. Ack modes: `BATCH`, `RECORD`, `MANUAL`, `MANUAL_IMMEDIATE`, `TIME`. `DefaultErrorHandler` replaces deprecated `SeekToCurrentErrorHandler`. Transactions bind producer and consumer via `ChainedKafkaTransactionManager` or `KafkaTransactionManager`. Listeners start after context refresh — gate readiness on DB migrations.

#### When to use / when NOT to use
Use Spring Kafka for standard microservice consumption with team familiarity. Drop to raw `KafkaConsumer` only when you need exotic control. Configure DLT and retry explicitly — defaults won't match your SLO.

#### Production example
`@KafkaListener(topics = "orders", groupId = "billing-v3", concurrency = "6")` with `AckMode.MANUAL_IMMEDIATE`, commits after Oracle upsert. `DeadLetterPublishingRecoverer` routes poison to `orders-billing.DLT`.

#### Common mistakes
Concurrency 12 on 6 partitions — half idle threads assumed working. `@KafkaListener` calling `@Transactional` service that also produces without EOS config. Starting listeners before Flyway completes.

#### Interview follow-ups (with model answers)

**Q:** Record vs batch ack in Spring?
**A:** For «Spring Kafka `@KafkaListener`»: Record vs batch ack in Spring. In production, `@KafkaListener(topics = "orders", groupId = "billing-v3", concurrency = "6")` with `AckMode.MANUAL_IMMEDIATE`, commits after Oracle upsert. `DeadLetterPublishingRecoverer` routes poison to `orders-billing.DLT`. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to test `@KafkaListener` with EmbeddedKafka?
**A:** The follow-on risk of «How to test `@KafkaListener` with EmbeddedKafka» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Interaction with `@RetryableTopic`?
**A:** Trade-off framing for «Interaction with `@RetryableTopic`»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Spring Kafka `@KafkaListener`.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: `@KafkaListener(topics = "orders", groupId = "billing-v3", concurrency = "6")` with `AckMode.MANUAL_IMMEDIATE`, commits after Oracle upsert.. I suspect concurrency 12 on 6 partitions — half idle threads assumed working until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@KafkaListener(topics = "orders", groupId = "billing-v3")
public void onOrder(ConsumerRecord<String, OrderEvent> record, Acknowledgment ack) {
    billingService.apply(record.value());
    ack.acknowledge();
}
```

---

### 27. `ConcurrentKafkaListenerContainerFactory` concurrency.

**Short answer:** `concurrency=N` creates N consumer instances in the same group (typically N threads). Effective parallelism is min(N, partitions assigned to this instance). N greater than partitions per JVM wastes resources; N less than partitions means one consumer handles multiple partitions. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
The container factory is where Spring Kafka maps your desired parallelism to Kafka consumer group mechanics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
In a single-app deployment with 12 partitions and concurrency=6 on one pod, one JVM runs 6 consumers sharing work. With 2 pods × concurrency=6, group has 12 consumers — one per partition. Partition assignment is broker-side; factory only spins containers. Batch listeners multiply records per invocation.

#### When to use / when NOT to use
Set concurrency from partition count and pod count: `partitions >= pods × concurrency`. Load test before prod. Do not set concurrency=1 globally out of habit on high-partition topics.

#### Production example
48 partitions, 4 pods, concurrency=12 → 48 consumers — full utilization. Autoscale pods not beyond partition math without adding partitions. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
concurrency=24 on 6-partition topic with 1 pod — 18 idle consumers. Confusing Spring concurrency with Kafka partition count at topic creation. Each pod using different groupId by misconfiguration.

#### Interview follow-ups (with model answers)

**Q:** Single-threaded listener vs concurrent factory?
**A:** For «`ConcurrentKafkaListenerContainerFactory` concurrency»: Single-threaded listener vs concurrent factory. In production, 48 partitions, 4 pods, concurrency=12 → 48 consumers — full utilization. Autoscale pods not beyond partition math without adding partitions. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does batch listener affect threads?
**A:** The follow-on risk of «How does batch listener affect threads» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Virtual threads with Kafka listener?
**A:** Trade-off framing for «Virtual threads with Kafka listener»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on `ConcurrentKafkaListenerContainerFactory.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: 48 partitions, 4 pods, concurrency=12 → 48 consumers — full utilization. Autoscale pods not beyond partition math without adding partitions.. I suspect concurrency=24 on 6-partition topic with 1 pod — 18 idle consumers until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
factory.setConcurrency(6);
factory.getContainerProperties().setAckMode(ContainerProperties.AckMode.MANUAL);
```

---

### 28. Exactly-once in Spring Kafka.

**Short answer:** Configure `transaction-id-prefix`, `isolation-level=read_committed`, and `@Transactional` on listener with `KafkaTransactionManager` for consume-transform-produce within Kafka. Writing to Oracle still requires idempotent DB logic — Spring EOS does not span JDBC. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Spring Kafka EOS wraps Kafka transactional producer and consumer into familiar `@Transactional` annotations — with sharp boundaries senior interviewers probe. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
`ChainedKafkaTransactionManager` can coordinate Kafka TX with DataSource TX in some setups but is fragile for most teams. Preferred: EOS for Kafka-only side effects; outbox/inbox for DB. `DefaultKafkaProducerFactory` with unique transactional id per app instance. Listener container with `setTransactionManager`. eosMode V2 improvements in recent Spring Kafka versions.

#### When to use / when NOT to use
Use Spring Kafka EOS for stream-like processing between topics. Do not enable chained TX as default architecture. Document that business exactly-once still needs dedup keys.

#### Production example
Enrichment service `@Transactional` listener reads raw events, writes enriched topic, commits offsets in Kafka TX. Separate Oracle writer consumes enriched topic with inbox table — end-to-end safe. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Believing `@Transactional` on listener makes Oracle + Kafka atomic. Duplicate `transaction-id-prefix` on scaled pods. Missing read_committed on downstream.

#### Interview follow-ups (with model answers)

**Q:** ChainedKafkaTransactionManager pitfalls?
**A:** For «Exactly-once in Spring Kafka»: ChainedKafkaTransactionManager pitfalls. In production, Enrichment service `@Transactional` listener reads raw events, writes enriched topic, commits offsets in Kafka TX. Separate Oracle writer consumes enriched topic with inbox table — end-to-end safe. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to assign transactional id in K8s?
**A:** The follow-on risk of «How to assign transactional id in K8s» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Testing transactional listeners?
**A:** Trade-off framing for «Testing transactional listeners»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Exactly-once in Spring Kafka.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Enrichment service `@Transactional` listener reads raw events, writes enriched topic, commits offsets in Kafka TX.. I suspect believing `@transactional` on listener makes oracle + kafka atomic until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
spring.kafka.producer.transaction-id-prefix=billing-tx-
spring.kafka.consumer.isolation-level=read_committed
```

---

### 29. Kafka vs JMS vs Rabbit.

**Short answer:** Kafka is a durable distributed log with replay, consumer groups, and high throughput — ops-heavy. JMS/IBM MQ offers mature operational messaging with queue semantics and sometimes XA. RabbitMQ excels at routing and work queues, not long-term replay logs. Enterprises often use MQ for payments and Kafka for event/analytics platforms.

#### What it is
Senior candidates map each technology to problems — not a single winner. Bank JDs mention both mainframe MQ integration and Kafka event hubs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka: pull consumers, retained log, partition scale, no built-in per-message ack to broker after process (offset commit). JMS/MQ: push or pull, message often removed on ack, strong ordering queues, dead letter queues native. Rabbit: exchanges, bindings, competing consumers on queues, shorter retention default.

#### When to use / when NOT to use
Kafka for event backbone, CDC, stream processing, audit replay. MQ/JMS when vendor mandates, XA needed with CICS/legacy, or strict queue contracts. Rabbit for task dispatch with complex routing. Hybrid is normal.

#### Production example
Core banking still posts to IBM MQ for settlement; same transaction emits `PaymentInitiated` to Kafka for customer notifications and data lake — integration layer translates, not one-size-fits-all. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Replacing MQ with Kafka for request-reply without design. Using Kafka as task queue with auto-delete expectation. Ignoring MQ ops maturity when SLA demands it.

#### Interview follow-ups (with model answers)

**Q:** When is Kafka wrong for job queues?
**A:** For «Kafka vs JMS vs Rabbit»: When is Kafka wrong for job queues. In production, Core banking still posts to IBM MQ for settlement; same transaction emits `PaymentInitiated` to Kafka for customer notifications and data lake — integration layer translates, not one-size-fits-all. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How does Kafka Connect relate to MQ bridges?
**A:** The follow-on risk of «How does Kafka Connect relate to MQ bridges» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Request-reply pattern in Kafka?
**A:** Trade-off framing for «Request-reply pattern in Kafka»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Kafka vs JMS vs Rabbit.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Core banking still posts to IBM MQ for settlement; same transaction emits `PaymentInitiated` to Kafka for customer notifications and data lake — integration lay…. I suspect replacing mq with kafka for request-reply without design until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 30. Kafka Connect.

**Short answer:** Kafka Connect is a framework for source and sink connectors running on workers — JDBC source polling, Debezium CDC, S3 sink, etc. Converters map bytes; Single Message Transforms (SMTs) mutate records. Prefer Connect over bespoke pollers when a certified connector exists. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Connect is how platforms ingest from databases and export to warehouses without every team writing a custom producer loop. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Distributed mode: connectors split into tasks across workers; offsets stored in internal topics. Source connectors track source position; sinks track Kafka offsets. Debezium reads DB transaction log for true CDC vs JDBC incremental timestamp/id polling. SMTs for routing, masking — keep logic light.

#### When to use / when NOT to use
Use Debezium for Oracle/Postgres CDC to Kafka. JDBC source only for low-volume or legacy without log access. Sink to S3/OpenSearch via Connect for platform teams. App teams still use Spring for domain events with outbox.

#### Production example
Platform team runs Debezium Oracle connector → `oracle.cdc.orders` topic; analytics subscribes without touching OLTP. Custom JDBC poller retired after missed deletes discovered.

#### Common mistakes
Heavy transforms in SMT chain — debug nightmare. JDBC source assuming deletes propagate. Running Connect tasks without monitoring task failure.

#### Interview follow-ups (with model answers)

**Q:** Debezium vs JDBC source trade-offs?
**A:** For «Kafka Connect»: Debezium vs JDBC source trade-offs. In production, Platform team runs Debezium Oracle connector → `oracle.cdc.orders` topic; analytics subscribes without touching OLTP. Custom JDBC poller retired after missed deletes discovered. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How are connector offsets stored?
**A:** The follow-on risk of «How are connector offsets stored» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Who owns Connect in your org?
**A:** Trade-off framing for «Who owns Connect in your org»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Kafka Connect.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Platform team runs Debezium Oracle connector → `oracle.cdc.orders` topic; analytics subscribes without touching OLTP.. I suspect heavy transforms in smt chain — debug nightmare until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 31. Kafka Streams vs ksqlDB vs Flink vs consumer app.

**Short answer:** Kafka Streams is a JVM library for stateful stream processing with embedded topology. ksqlDB adds SQL interface over Streams. Flink is a separate cluster for heavy event-time streaming. Simple Spring `@KafkaListener` consumer is enough for most microservice projection — don't adopt Streams for a single DB upsert.

#### What it is
Tool selection is about operational surface area vs processing complexity — senior answers weigh team skills and SLAs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Streams: local RocksDB state, changelog topics, repartition topics, interactive queries. ksqlDB: server wrapping Streams for SQL teams. Flink: checkpointing, watermarks, CEP at scale. Consumer app: you manage offset, state in Oracle, windows in app — simplest ops.

#### When to use / when NOT to use
Streams/ksql for sessionization, joins, aggregations colocated with Kafka. Flink for high-scale CEP with dedicated ops. Plain consumer for CRUD projections and callouts to REST/DB.

#### Production example
Fraud team uses Flink for complex event-time rules across millions of events/sec. Order service uses Spring consumer to upsert read model — no Streams dependency. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Kafka Streams for cron-like batch job once daily. Flink for 3 filters and count. ksqlDB without understanding underlying changelog restore time.

#### Interview follow-ups (with model answers)

**Q:** When does Streams rebalance hurt?
**A:** For «Kafka Streams vs ksqlDB vs Flink vs consumer app»: When does Streams rebalance hurt. In production, Fraud team uses Flink for complex event-time rules across millions of events/sec. Order service uses Spring consumer to upsert read model — no Streams dependency. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Interactive queries production use?
**A:** The follow-on risk of «Interactive queries production use» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Flink vs Streams checkpoint model?
**A:** Trade-off framing for «Flink vs Streams checkpoint model»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Kafka Streams vs ksqlDB vs Flink vs cons.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Fraud team uses Flink for complex event-time rules across millions of events/sec.. I suspect kafka streams for cron-like batch job once daily until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 32. State store and changelog.

**Short answer:** Kafka Streams maintains local RocksDB state stores backed by compacted changelog topics. On rebalance, tasks restore state from changelog — restore time and disk size are first-class ops concerns. Interactive queries expose store data per instance. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
State stores are how stream processors remember aggregations without an external DB — at the cost of rebalance recovery lag. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Every stateful operator has a changelog topic (compacted). On assignment, task replays changelog into RocksDB. Large state + many threads = long rebalance. `standby.replicas` reduce failover time by hot standby copies. Interactive queries route by key to correct instance.

#### When to use / when NOT to use
Size state stores consciously; monitor restore duration. Use standby replicas for SLA-critical queries. Externalize very large state to Cassandra/Oracle when restore exceeds tolerance.

#### Production example
Session aggregator rebalance after deploy took 20 minutes restore — ops added standby replicas and increased partition count planning. Incident led to runbook for rolling upgrade windows. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Ignoring changelog disk on broker. Stateful topology without monitoring restore. Querying interactive API without key routing — 404 on wrong pod.

#### Interview follow-ups (with model answers)

**Q:** What is `acceptable.recovery.lag`?
**A:** For «State store and changelog»: What is `acceptable.recovery.lag`. In production, Session aggregator rebalance after deploy took 20 minutes restore — ops added standby replicas and increased partition count planning. Incident led to runbook for rolling upgrade windows. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Changelog compaction tuning?
**A:** The follow-on risk of «Changelog compaction tuning» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Global vs window state stores?
**A:** Trade-off framing for «Global vs window state stores»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on State store and changelog.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Session aggregator rebalance after deploy took 20 minutes restore — ops added standby replicas and increased partition count planning.. I suspect ignoring changelog disk on broker until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 33. Windowing and event time.

**Short answer:** Event time is when something happened in the domain; processing time is when the processor sees it. Windowed aggregations ( tumbling, hopping, session ) must use event time with watermarks to handle late data — wall-clock windows lie under lag or replay. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Time semantics separate toy stream demos from production analytics and fraud systems where late arrivals are normal. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Kafka Streams and Flink track event timestamps in records; watermarks signal lateness bound. Allowed lateness drops or side-outputs late events. Processing-time windows shift under consumer lag — dangerous for billing periods. Session windows gap on inactivity.

#### When to use / when NOT to use
Use event-time with watermark strategy for user sessions, billing windows, SLA metrics. Processing time only for approximate real-time dashboards with documented inaccuracy. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Mobile events arrive late on flaky networks; fraud window uses 5-minute allowed lateness; events 6 minutes late go to side output for manual review — not silently dropped or double-counted. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
System.currentTimeMillis() as window boundary. No late-data policy — silent loss or duplicate counts on replay. Mixing processing and event time in same topology.

#### Interview follow-ups (with model answers)

**Q:** Tumbling vs hopping vs session windows?
**A:** For «Windowing and event time»: Tumbling vs hopping vs session windows. In production, Mobile events arrive late on flaky networks; fraud window uses 5-minute allowed lateness; events 6 minutes late go to side output for manual review — not silently dropped or double-counted. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do watermarks propagate?
**A:** The follow-on risk of «How do watermarks propagate» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Replay impact on windows?
**A:** Trade-off framing for «Replay impact on windows»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Windowing and event time.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Mobile events arrive late on flaky networks; fraud window uses 5-minute allowed lateness; events 6 minutes late go to side output for manual review — not silent…. I suspect system until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 34. Compacted changelog vs event log.

**Short answer:** Event log topics append every fact — often delete retention, keys optional or unique per event. Changelog topics key by entity id and compact to latest state. Mixing both semantics in one topic confuses consumers expecting only deltas or only snapshots. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Naming and cleanup policy should signal whether consumers replay history or bootstrap current state. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Event log: `OrderPlaced`, `OrderCancelled` as separate immutable events keyed by orderId or eventId. Changelog: latest `OrderState` per orderId after compaction. Consumers rebuilding from changelog miss intermediate transitions unless they also read the event log.

#### When to use / when NOT to use
Separate topics: `order-events` (log) and `order-state` (compact changelog projection). Document which downstream uses which. Do not compact high-cardinality random keys.

#### Production example
Analytics reads full `order-events` log. Mobile BFF subscribes to compacted `order-snapshot` for fast cold start — two contracts, two topics. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Single topic trying to be both audit log and compacted cache. Consumers assuming compacted topic contains full history. Compaction deleting evidence needed for compliance.

#### Interview follow-ups (with model answers)

**Q:** Can one consumer use both log and changelog?
**A:** For «Compacted changelog vs event log»: Can one consumer use both log and changelog. In production, Analytics reads full `order-events` log. Mobile BFF subscribes to compacted `order-snapshot` for fast cold start — two contracts, two topics. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Materialized view naming conventions?
**A:** The follow-on risk of «Materialized view naming conventions» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** GDPR on compacted PII topics?
**A:** Trade-off framing for «GDPR on compacted PII topics»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Compacted changelog vs event log.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Analytics reads full `order-events` log. Mobile BFF subscribes to compacted `order-snapshot` for fast cold start — two contracts, two topics.. I suspect single topic trying to be both audit log and compacted cache until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 35. Security: SASL, ACLs, encryption.

**Short answer:** Production Kafka uses SASL (SCRAM-SHA-512, OAuth/OIDC) or mutual TLS for authentication, ACLs for authorization per topic/group/cluster actions, and TLS in transit. At-rest encryption is typically disk/volume level. Treat topic data as sensitive as database rows — PII belongs masked or tokenized. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Security is non-optional on shared clusters — multi-tenant platforms fail audits without ACLs and encryption. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
ACLs: `User:app-billing` ALLOW READ on `payments`, ALLOW WRITE on `billing-events`, ALLOW READ on group `billing-*`. Deny by default. mTLS identifies clients via certificates. SCRAM stores credentials in Kafka metadata. MirrorMaker and Connect need their own principals. Encrypt inter-broker traffic on multi-tenant clusters.

#### When to use / when NOT to use
Enable ACLs before opening cluster beyond platform team. Principle of least privilege per service account. Separate clusters for PCI vs marketing when policy demands isolation beyond ACLs.

#### Production example
Each microservice gets K8s secret with SCRAM creds scoped to two topics. Attempt to produce to `admin-config` denied and logged in SIEM. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
ANONYMOUS in prod. Shared admin credentials in every app. PII in clear on shared topic without column-level masking.

#### Interview follow-ups (with model answers)

**Q:** SCRAM vs mTLS operational trade-offs?
**A:** For «Security: SASL, ACLs, encryption»: SCRAM vs mTLS operational trade-offs. In production, Each microservice gets K8s secret with SCRAM creds scoped to two topics. Attempt to produce to `admin-config` denied and logged in SIEM. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How do ACLs interact with Connect?
**A:** The follow-on risk of «How do ACLs interact with Connect» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** OAuth for Kafka in cloud?
**A:** Trade-off framing for «OAuth for Kafka in cloud»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Security: SASL, ACLs, encryption.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Each microservice gets K8s secret with SCRAM creds scoped to two topics. Attempt to produce to `admin-config` denied and logged in SIEM.. I suspect anonymous in prod until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 36. Rebalance + duplicate payments (the bar-raiser).

**Short answer:** Consumer processes payment, crashes before offset commit — rebalance assigns partition to another consumer — same payment processed twice. Fix with idempotent DB upsert on `eventId`/`paymentId` inside a transaction, then commit offset — not unlimited retries alone. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
This scenario separates engineers who read Kafka docs from those who shipped money through it. Interviewers expect the full story with DB and offset ordering. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Failure sequence: poll batch → process payment success → JVM kill before commit → new consumer reads same offset → second charge. Kafka transactions help only if all effects stay in Kafka. Oracle path: `INSERT INTO processed_events (event_id) ... ON CONFLICT DO NOTHING` then apply payment, commit TX, then Kafka offset commit.

#### When to use / when NOT to use
Always implement consumer idempotency before launch. Pair with metrics on duplicate detection hits. Kafka EOS for Kafka-only pipelines; inbox for DB.

#### Production example
Payment listener checks inbox table; duplicate `PaymentCaptured` event hits unique constraint, skips business logic, still commits offset — customer charged once, audit shows two deliveries. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Exactly-once producer without DB dedup. Committing offset before Oracle TX commits. Assuming rebalance is rare so duplicates impossible.

#### Interview follow-ups (with model answers)

**Q:** Compare inbox vs natural idempotency keys?
**A:** For «Rebalance + duplicate payments (the bar-raiser)»: Compare inbox vs natural idempotency keys. In production, Payment listener checks inbox table; duplicate `PaymentCaptured` event hits unique constraint, skips business logic, still commits offset — customer charged once, audit shows two deliveries. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Would Kafka TX alone fix this?
**A:** The follow-on risk of «Would Kafka TX alone fix this» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to test duplicate delivery?
**A:** Trade-off framing for «How to test duplicate delivery»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on Rebalance + duplicate payments (the bar-.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment listener checks inbox table; duplicate `PaymentCaptured` event hits unique constraint, skips business logic, still commits offset — customer charged onc…. I suspect exactly-once producer without db dedup until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@Transactional
public void handle(PaymentEvent e) {
    if (!inbox.markProcessed(e.getEventId())) return;
    ledger.capture(e);
}
```

---

### 37. `enable.auto.commit=true` incident.

**Short answer:** With auto-commit, offsets advance on timer after poll — not after successful processing. Handler throws after auto-commit interval elapsed → message skipped forever while the group thinks progress was made. This is the classic silent data loss story every senior should tell. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Auto-commit is the default footgun — production incidents often trace to it combined with exception swallowing. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Consumer polls records at T0; auto-commit fires at T1 committing offsets through end of poll batch; processing at T2 fails on record in middle of batch — that record won't be redelivered to this group. Contrast with manual commit after success: failure before commit → redelivery (duplicate risk, not loss). Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### When to use / when NOT to use
Disable auto-commit in every service with side effects. Tell this incident narrative in interviews with timestamps. Use integration tests that kill process mid-batch.

#### Production example
Billing consumer auto-commit enabled; NullPointerException on 2% of messages after commit; finance reconciliation finds missing invoices weeks later; fix: manual ack + DLT + replay from upstream. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Leaving auto-commit because default worked in dev. Catching exceptions without negative ack. No reconciliation job detecting gap.

#### Interview follow-ups (with model answers)

**Q:** Can partial batch commit happen?
**A:** For «`enable.auto.commit=true` incident»: Can partial batch commit happen. In production, Billing consumer auto-commit enabled; NullPointerException on 2% of messages after commit; finance reconciliation finds missing invoices weeks later; fix: manual ack + DLT + replay from upstream. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Spring default ack mode?
**A:** The follow-on risk of «Spring default ack mode» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to replay lost messages?
**A:** Trade-off framing for «How to replay lost messages»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on `enable.auto.commit=true` incident.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Billing consumer auto-commit enabled; NullPointerException on 2% of messages after commit; finance reconciliation finds missing invoices weeks later; fix: manua…. I suspect leaving auto-commit because default worked in dev until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
enable.auto.commit=false
# spring.kafka.listener.ack-mode=manual_immediate
```

---

### 38. Head-of-line blocking.

**Short answer:** One slow or failing message at offset N blocks all later messages on that partition — head-of-line blocking. Mitigations: dead-letter with ordering trade-off, parallel processing of different partitions, per-key executor pools with careful offset management, or splitting hot keys to new topics. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Ordered logs inherit queue-like blocking per partition — a core limitation when adapting queue mental models to Kafka. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Single-threaded partition processing means poison or slow record stalls everything behind it. Parallelizing within partition breaks strict offset order unless you use complex pause/commit schemes. Multiple partitions allow parallelism across keys.

#### When to use / when NOT to use
For strict order paths, accept blocking and fix slow handlers. For mixed workloads, DLT poison quickly. Advanced: per-key task queues with ordered commits — high complexity.

#### Production example
Shipping updates stall behind one giant payload message — ops move large attachments to S3, replay skipped offset from DLT after fix. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Infinite retry on one bad record freezing fulfillment for all customers on partition. DLT without understanding order break for downstream. Adding consumers doesn't help blocked partition internally.

#### Interview follow-ups (with model answers)

**Q:** Does retry topic solve HoL?
**A:** For «Head-of-line blocking»: Does retry topic solve HoL. In production, Shipping updates stall behind one giant payload message — ops move large attachments to S3, replay skipped offset from DLT after fix. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Per-partition executor patterns?
**A:** The follow-on risk of «Per-partition executor patterns» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When to split topics?
**A:** Trade-off framing for «When to split topics»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Head-of-line blocking.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Shipping updates stall behind one giant payload message — ops move large attachments to S3, replay skipped offset from DLT after fix.. I suspect infinite retry on one bad record freezing fulfillment for all customers on partition until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 39. MirrorMaker 2 / cluster link.

**Short answer:** MirrorMaker 2 (MM2) replicates topics between Kafka clusters — active-active or DR. Offsets are not portable across clusters; consumers failing over must reset by timestamp or track offsets separately. Cluster Link (Confluent) offers managed replication with similar semantic caveats. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Multi-datacenter Kafka is an architecture interview topic — offset translation and identity headers matter more than the replication tool name. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
MM2 runs connectors per direction, syncs topic configs and ACLs optionally, maintains offset mapping internal topics. Active-active needs conflict avoidance (per-DC keys, compacted entity routing). Failover consumer uses `offsets.alter` or timestamp reset — not assume partition 5 offset 900 is same remotely.

#### When to use / when NOT to use
Use MM2 for DR read replica or gradual migration. Design global keys with DC prefix. Do not run dual-active writes to same entity without merge strategy.

#### Production example
US-East primary; MM2 replicates to US-West; DR runbook starts consumers at `auto.offset.reset=by_duration` 15 minutes before failover — practiced quarterly.

#### Common mistakes
Assuming MM2 copies consumer offsets for seamless flip. Split-brain dual write without CRDT or authority model. Ignoring replication lag in RPO math.

#### Interview follow-ups (with model answers)

**Q:** Active-active pitfalls?
**A:** For «MirrorMaker 2 / cluster link»: Active-active pitfalls. In production, US-East primary; MM2 replicates to US-West; DR runbook starts consumers at `auto.offset.reset=by_duration` 15 minutes before failover — practiced quarterly. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to test DR failover?
**A:** The follow-on risk of «How to test DR failover» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** MM2 vs Confluent Cluster Link?
**A:** Trade-off framing for «MM2 vs Confluent Cluster Link»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing MirrorMaker 2 / cluster link.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: US-East primary; MM2 replicates to US-West; DR runbook starts consumers at `auto.offset.reset=by_duration` 15 minutes before failover — practiced quarterly.. I suspect assuming mm2 copies consumer offsets for seamless flip until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 40. Disk and why Kafka is sequential.

**Short answer:** Kafka appends sequentially to segment files and relies on OS page cache — sequential I/O is orders of magnitude faster than random writes. Brokers are not databases; random read patterns on huge compacted logs punish HDDs. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Understanding Kafka's disk model explains broker sizing, retention planning, and why SSD/NVMe matters at scale. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Each partition is a directory of segment files (`000000000000000000.log`). Writes append; reads mostly sequential for consumers catching up. Page cache keeps hot tail in memory. Compaction rewrites segments in background — temporary disk amplification. Monitor disk usage, flush latency, and iowait.

#### When to use / when NOT to use
Size disks for retention × throughput × RF headroom. Prefer SSD for broker logs at meaningful scale. Avoid treating Kafka as random-access store.

#### Production example
Broker disk usage alert at 70%; retention trimmed on low-value topics; NVMe brokers sustain 500MB/s ingest while HDD cluster struggled with same load — architectural split by topic tier. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Unbounded retention on verbose JSON. Compaction + high write rate without disk monitor. Sharing OS disk with ZooKeeper/KRaft without isolation.

#### Interview follow-ups (with model answers)

**Q:** KRaft log sizing differences?
**A:** For «Disk and why Kafka is sequential»: KRaft log sizing differences. In production, Broker disk usage alert at 70%; retention trimmed on low-value topics; NVMe brokers sustain 500MB/s ingest while HDD cluster struggled with same load — architectural split by topic tier. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Tiered storage trade-offs?
**A:** The follow-on risk of «Tiered storage trade-offs» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Why fsync and flush matter?
**A:** Trade-off framing for «Why fsync and flush matter»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Disk and why Kafka is sequential.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Broker disk usage alert at 70%; retention trimmed on low-value topics; NVMe brokers sustain 500MB/s ingest while HDD cluster struggled with same load — architec…. I suspect unbounded retention on verbose json until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 41. `max.poll.records` tuning.

**Short answer:** `max.poll.records` caps records per poll — smaller batches mean more frequent polls (better rebalance hygiene, lower memory), larger batches improve throughput but extend processing time and risk exceeding `max.poll.interval.ms`. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
This knob couples consumer performance with liveness — tune it with measured handler latency, not defaults. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Default 500 may be too many for fat JSON + Oracle batch upsert. Reduce to 50–100 for heavy handlers; increase for lightweight filtering. Pair with fetch bytes settings. Spring `max.poll.records` in consumer props applies per listener consumer.

#### When to use / when NOT to use
Load test with production-sized payloads. Set `max.poll.interval.ms` ≥ (max.poll.records × p99 process time × safety factor). Document chosen values in service README.

#### Production example
Inventory listener reduced max.poll.records from 500 to 80; poll interval compliance restored; throughput maintained by faster commits and better DB batching.

#### Common mistakes
Only tuning concurrency while interval timeouts persist. max.poll.records=5000 with 2s record processing — math guarantees rebalance. Ignoring heap impact of large batches.

#### Interview follow-ups (with model answers)

**Q:** Relation to fetch.min.bytes?
**A:** For «`max.poll.records` tuning»: Relation to fetch.min.bytes. In production, Inventory listener reduced max.poll.records from 500 to 80; poll interval compliance restored; throughput maintained by faster commits and better DB batching. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Batch listener implications?
**A:** The follow-on risk of «Batch listener implications» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** How to measure process time per record?
**A:** Trade-off framing for «How to measure process time per record»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on `max.poll.records` tuning.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Inventory listener reduced max.poll.records from 500 to 80; poll interval compliance restored; throughput maintained by faster commits and better DB batching.. I suspect only tuning concurrency while interval timeouts persist until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
max.poll.records=100
max.poll.interval.ms=300000
```

---

### 42. Producer `max.in.flight.requests` and ordering.

**Short answer:** Without idempotence, `max.in.flight.requests.per.connection > 1` allows reordering on retry — record B may appear before A. Idempotent producer (Kafka 0.11+) preserves order per partition up to 5 in-flight with sequence dedup. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
In-flight requests trade latency for throughput; ordering-sensitive keyed pipelines must understand the interaction with retries. This setting is often overlooked because defaults work until the first network blip during a payment or inventory update burst. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer pipelines batches to broker; multiple in-flight requests mean later batch can ack before earlier failed batch retries — reorder unless idempotence serializes sequence numbers. Legacy fix: `max.in.flight=1` (throughput hit). Modern: enable idempotence, keep in-flight ≤5. With `acks=all` and retries enabled, the Java client may resend batch 1 while batch 2 already landed — consumers see permuted offsets for the same key. Idempotence assigns PID + monotonic sequence per partition so broker rejects out-of-order retries.

#### When to use / when NOT to use
Enable idempotence for all ordered keyed produce paths. If idempotence off, set in-flight=1 for strict order acceptance of throughput cost. Load-test with fault injection (iptables drop) before declaring ordering guarantees in design docs.

#### Production example
Stock price updates keyed by symbol use idempotent producer with in-flight=5; no reorder observed under synthetic retry fault injection. Throughput stays within SLA because batching and compression offset the in-flight cap. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Disabling idempotence for perf on order-critical topic. Confusing partition order with global order. Not testing retry reorder scenario. Setting in-flight=1 without measuring whether broker latency is the real bottleneck.

#### Interview follow-ups (with model answers)

**Q:** Does acks=1 affect ordering?
**A:** For «Producer `max.in.flight.requests` and ordering»: Does acks=1 affect ordering. In production, Stock price updates keyed by symbol use idempotent producer with in-flight=5; no reorder observed under synthetic retry fault injection. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Custom partitioner + in-flight?
**A:** The follow-on risk of «Custom partitioner + in-flight» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Idempotence broker version requirements?
**A:** Trade-off framing for «Idempotence broker version requirements»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Producer `max.in.flight.requests` and or.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Stock price updates keyed by symbol use idempotent producer with in-flight=5; no reorder observed under synthetic retry fault injection.. I suspect disabling idempotence for perf on order-critical topic until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 43. Header vs payload.

**Short answer:** Headers carry metadata — traceId, eventType, schema hints, retry count — without parsing payload. Payload holds business data. Keep headers small (Kafka header size limits apply); never put megabytes in headers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos.

#### What it is
Headers enable routing, observability, and cross-cutting concerns without deserializing payload — standard in event-driven Java services. They are the envelope around your domain event, similar to HTTP headers versus JSON body. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Record headers are key-value bytes parallel to payload. Interceptors add trace propagation (OpenTelemetry). Conventional: `ce-type` for CloudEvents, custom `X-Event-Id`. Schema id often in Confluent wire format in payload magic byte, not header — both patterns exist. Spring `KafkaTemplate` exposes headers via `ProducerRecord` and `ConsumerRecord.headers()`. SMTs and routing engines can branch on header values without Avro decode — useful for canary traffic or multi-tenant routing filters.

#### When to use / when NOT to use
Put correlation ids and content-type in headers. Keep payload schema-versioned via Registry. Avoid duplicating large fields in both. Standardize header names org-wide (`x-correlation-id`) so mesh, logs, and DLT replays align.

#### Production example
All services inject `traceparent` header; mesh traces Kafka path end-to-end; payload stays pure Avro OrderEvent. On-call finds poison pill in minutes by searching trace id across HTTP ingress and Kafka consumer logs. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
1MB JSON duplicated into header. Business logic only in headers without schema governance. Sensitive PII in headers logged by debug interceptors. Relying on header `eventType` without Registry while payload schema drifted silently.

#### Interview follow-ups (with model answers)

**Q:** CloudEvents Kafka binding?
**A:** For «Header vs payload»: CloudEvents Kafka binding. In production, All services inject `traceparent` header; mesh traces Kafka path end-to-end; payload stays pure Avro OrderEvent. On-call finds poison pill in minutes by searching trace id across HTTP ingress and Kafka consumer logs. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Header size limits?
**A:** The follow-on risk of «Header size limits» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Spring MessageHeaders usage?
**A:** Trade-off framing for «Spring MessageHeaders usage»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Header vs payload.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: All services inject `traceparent` header; mesh traces Kafka path end-to-end; payload stays pure Avro OrderEvent.. I suspect 1mb json duplicated into header until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
record.headers().add("traceId", traceId.getBytes(StandardCharsets.UTF_8));
```

---

### 44. Multi-tenancy on one cluster.

**Short answer:** Shared clusters isolate tenants via topic prefixes, ACLs, quotas (`client.quota`), and monitoring — noisy neighbor remains a risk. PCI or regulated workloads often warrant separate clusters despite ACL isolation. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Multi-tenant Kafka is cost-efficient but requires platform discipline — senior candidates discuss blast radius not just ACL syntax. Platform teams own onboarding automation; app teams get scoped credentials, not cluster admin. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Quotas cap produce/fetch bytes per client id or user. ACLs scope principals to `tenantA.*` topics. Metric tags per tenant for lag and throughput. Dedicated pool of brokers for mega-tenant optional. Schema Registry namespaces per domain. Rate-limit misbehaving clients before they exhaust disk or trigger ISR shrink affecting neighbors.

#### When to use / when NOT to use
Single cluster for general event platform with strict ACL/quotas. Separate cluster for cardholder data. Document tenant onboarding checklist including topic naming, retention, and offboarding tombstone policy.

#### Production example
SaaS platform assigns `tenantId` topic prefix; ACL automation from K8s service account; quota prevents one tenant saturating cluster; still migrated largest tenant to dedicated cluster after incident. Post-incident review cited noisy neighbor on compaction, not ACL gap. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Shared admin user for all apps. No quotas — one bad deploy DOSes cluster. PII tenants mixed with public analytics on same brokers without network segmentation. Manual ACL tickets slowing every new microservice launch.

#### Interview follow-ups (with model answers)

**Q:** Quota tuning examples?
**A:** For «Multi-tenancy on one cluster»: Quota tuning examples. In production, SaaS platform assigns `tenantId` topic prefix; ACL automation from K8s service account; quota prevents one tenant saturating cluster; still migrated largest tenant to dedicated cluster after incident. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Dedicated vs shared cluster decision?
**A:** The follow-on risk of «Dedicated vs shared cluster decision» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Tenant isolation in Schema Registry?
**A:** Trade-off framing for «Tenant isolation in Schema Registry»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Multi-tenancy on one cluster.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: SaaS platform assigns `tenantId` topic prefix; ACL automation from K8s service account; quota prevents one tenant saturating cluster; still migrated largest ten…. I suspect shared admin user for all apps until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 45. Monitoring that matters.

**Short answer:** Watch under-replicated partitions, ISR shrink, broker request latency, produce/fetch error rates, consumer lag (records and time), rebalance rate, disk free, and client GC — not CPU alone. Alert on trends that precede data loss or extended outage. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
Kafka operability is metric-driven; senior engineers name signals that map to failure modes, not generic infrastructure dashboards. A healthy CPU graph while URP > 0 is a false comfort — you are already losing redundancy. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Broker JMX: `UnderReplicatedPartitions`, `OfflinePartitionsCount`, `RequestHandlerAvgIdlePercent`. Consumer: lag per partition, commit rate, rebalance total. Producer: record error rate, batch size avg. Burrow/LinkedIn or Kafka Exporter for consumer group health. Trace correlation for end-to-end latency. Correlate broker disk usage slope with retention policy changes. Track `kafka.server:type=FetcherLagMetrics` for follower drift before ISR drop.

#### When to use / when NOT to use
Dashboard per cluster and critical consumer group. Page on offline partitions and lag SLO breach. Run game days for broker loss. Define lag SLO in wall-clock time for business topics, not only offset delta.

#### Production example
Payment group lag time > 5 minutes pages on-call; root cause rebalance storm from mis-set max.poll.interval — fixed before finance SLA miss. Secondary alert on rising `records-consumed-rate` variance flagged hot partition before lag exploded.

#### Common mistakes
Only monitoring broker CPU. No consumer lag alerts. Ignoring produce error rate spike until disk full. Treating rebalance as noise because lag recovers without fixing root cause.

#### Interview follow-ups (with model answers)

**Q:** Burrow vs Kafka Exporter?
**A:** For «Monitoring that matters»: Burrow vs Kafka Exporter. In production, Payment group lag time > 5 minutes pages on-call; root cause rebalance storm from mis-set max.poll.interval — fixed before finance SLA miss. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Which lag metric for SLO?
**A:** The follow-on risk of «Which lag metric for SLO» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** OpenTelemetry for Kafka clients?
**A:** Trade-off framing for «OpenTelemetry for Kafka clients»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Monitoring that matters.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment group lag time > 5 minutes pages on-call; root cause rebalance storm from mis-set max.poll.interval — fixed before finance SLA miss.. I suspect only monitoring broker cpu until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 46. `auto.offset.reset`.

**Short answer:** `earliest` vs `latest` applies when no committed offset exists for `(group, topic, partition)` — new consumer group or expired offsets. `latest` skips backlog on first deploy; `earliest` replays all retained history — ops surprise if undocumented. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved.

#### What it is
First-deploy consumer behavior catches teams who never tested new group.id in staging with production retention. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
On subscribe/join, consumer checks `__consumer_offsets`. If none: `auto.offset.reset` decides start position. `none` throws exception — strict environments. Changing group id creates new group — reset policy applies again. Does not affect groups with existing commits.

#### When to use / when NOT to use
Production event processors: usually `earliest` with idempotent consumer to avoid silent skip. Real-time dashboards on new group: `latest`. Document in runbook when creating group.

#### Production example
New `billing-v4` group deployed with `latest` accidentally — missed day of payments; rollback to `earliest` with idempotent inbox recovered state. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Assuming reset applies every restart. Using random group id per pod. Expired offsets (compact internal topic) causing unexpected replay without notice.

#### Interview follow-ups (with model answers)

**Q:** When do committed offsets expire?
**A:** For «`auto.offset.reset`»: When do committed offsets expire. In production, New `billing-v4` group deployed with `latest` accidentally — missed day of payments; rollback to `earliest` with idempotent inbox recovered state. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Difference from seek()?
**A:** The follow-on risk of «Difference from seek()» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Spring `auto-offset-reset` property?
**A:** Trade-off framing for «Spring `auto-offset-reset` property»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A bad schema deploy stalls one partition or queue while others look healthy on `auto.offset.reset`.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: New `billing-v4` group deployed with `latest` accidentally — missed day of payments; rollback to `earliest` with idempotent inbox recovered state.. I suspect assuming reset applies every restart until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
auto.offset.reset=earliest
# for new billing-v4 consumer group — document in runbook
```

---

### 47. Compacted topic as a source of truth?

**Short answer:** A compacted topic can hold latest entity state for distribution and rebuild, but Kafka lacks OLTP query semantics, constraints, and ad-hoc joins — use as materialized distribution plus DB as authority, not primary financial ledger. In production, the trade-off shows up in on-call incidents and reconciliation jobs — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before claiming this is solved. The wrong default here usually surfaces as silent data loss, duplicate money movement, or unbounded lag — not as a broker crash.

#### What it is
This question tests whether you understand Kafka's role in data architecture vs replacing Oracle. Compacted topics are excellent caches and bootstrap sources, not replacements for transactional stores with ACID invariants across aggregates. Teams that skip load testing and failure injection here usually learn the lesson during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Compacted changelog gives key→latest value replay for cache warm-up and disaster rebuild. No foreign keys, no transactional multi-row invariants across keys, no interactive SQL. Event log plus DB remains pattern for audit and compliance. Compaction is asynchronous — tail readers may briefly see superseded values; plan read-your-writes via API not raw topic tail.

#### When to use / when NOT to use
Use compacted topics for read model bootstrap and cross-region cache sync. Keep Oracle/Postgres as SoT with outbox. Combine with retention for bounded rebuild window. Run periodic reconciliation jobs comparing compacted snapshot counts to DB.

#### Production example
Order snapshot topic rebuilds mobile cache after app reinstall; authoritative totals still from `GET /orders` backed by Oracle. Finance audit pulls immutable event log, not compacted snapshot alone. Teams that skip load testing and failure injection here usually learn the lesson during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Storing balances only in compacted topic. Compaction lag mistaken for real-time truth. No tombstone on delete — zombie entities. Claiming GDPR erasure complete after DB delete without tombstone on compacted topic.

#### Interview follow-ups (with model answers)

**Q:** KTable vs Oracle materialized view?
**A:** For «Compacted topic as a source of truth»: KTable vs Oracle materialized view. In production, Order snapshot topic rebuilds mobile cache after app reinstall; authoritative totals still from `GET /orders` backed by Oracle. Finance audit pulls immutable event log, not compacted snapshot alone. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Rebuild time estimation?
**A:** The follow-on risk of «Rebuild time estimation» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Compliance retention on compacted PII?
**A:** Trade-off framing for «Compliance retention on compacted PII»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Durability gates block producers during ISR shrink or channel failure; product demands you weaken guarantees on Compacted topic as a source of truth.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Order snapshot topic rebuilds mobile cache after app reinstall; authoritative totals still from `GET /orders` backed by Oracle.. I suspect storing balances only in compacted topic until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 48. Transactions and zombie fencing.

**Short answer:** Transactional producer uses `transactional.id` and epoch; when a new instance registers the same id, brokers fence old producers with `ProducerFencedException` — preventing zombie instances from committing stale transactions after failover or slow GC pause. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Zombie fencing is the safety latch for EOS when JVM processes don't die cleanly — common in Kubernetes where SIGTERM does not instantly kill a hung thread still holding an open transaction. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
On initTransactions, broker bumps epoch for transactional id. Old producer attempting commit gets fenced. Consumer `read_committed` never sees aborted zombie writes. Requires unique transactional id per logical producer instance lifecycle. Transaction coordinator tracks open transactions; `transaction.timeout.ms` aborts hung ones, freeing resources. Fencing is per transactional.id — not a substitute for consumer idempotency on DB writes.

#### When to use / when NOT to use
Always handle `ProducerFencedException` — close producer and exit or re-init. Use instance-specific transactional id suffix (pod uid). Don't share ids across replicas. During rolling deploys, expect brief fencing as healthy behavior, not an alert storm, if old pods shut down promptly.

#### Production example
Rolling deploy: new pod initTransactions fences old pod mid-transaction; old pod logs fenced and shuts down cleanly — no duplicate enriched records published. Playbook documents max 30s overlap during deploy before paging. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Two pods same transactional.id — both fenced loop. Ignoring fenced exception and retrying blindly. Long stop-the-world GC causing false fencing storms. Reusing transactional id across restarts without static instance id — unnecessary fencing on every health restart.

#### Interview follow-ups (with model answers)

**Q:** transaction.timeout.ms tuning?
**A:** For «Transactions and zombie fencing»: transaction.timeout.ms tuning. In production, Rolling deploy: new pod initTransactions fences old pod mid-transaction; old pod logs fenced and shuts down cleanly — no duplicate enriched records published. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** EOS with Kubernetes replicas?
**A:** The follow-on risk of «EOS with Kubernetes replicas» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Relationship to consumer group static membership?
**A:** Trade-off framing for «Relationship to consumer group static membership»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.

#### Scenario probe

**Situation:** Reconciliation finds DB rows without matching bus events (or the reverse) after a pod OOM on Transactions and zombie fencing.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Rolling deploy: new pod initTransactions fences old pod mid-transaction; old pod logs fenced and shuts down cleanly — no duplicate enriched records published.. I suspect two pods same transactional until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

---

### 49. Testing Kafka.

**Short answer:** Use Testcontainers for broker integration tests, Spring `EmbeddedKafka` for listener unit/integration tests, schema compatibility tests in CI, and fault injection (kill broker, rebalance) in staging — not only mocking `@KafkaListener` method calls. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
Kafka testing strategy proves delivery, error handling, and serialization — areas mocks hide. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Testcontainers spins real Kafka in Docker — closer to prod than embedded. `@EmbeddedKafka` fast for Spring context tests. Contract tests: produce sample Avro, consume with old consumer schema. Test DLT path, commit failure, rebalance listener behavior.

#### When to use / when NOT to use
CI: unit tests with EmbeddedKafka; nightly Testcontainers suite; schema compatibility gate on PR. Don't mock KafkaTemplate only — test serializer failures. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Production example
Payment listener test publishes bad record, asserts DLT topic receives it and main offset advances after handler policy — catches regression in error handler config. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Only `@MockBean KafkaTemplate`. No test for new consumer group offset reset. Skipping schema break test in CI.

#### Interview follow-ups (with model answers)

**Q:** EmbeddedKafka vs Testcontainers?
**A:** For «Testing Kafka»: EmbeddedKafka vs Testcontainers. In production, Payment listener test publishes bad record, asserts DLT topic receives it and main offset advances after handler policy — catches regression in error handler config. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** How to test transactional listener?
**A:** The follow-on risk of «How to test transactional listener» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** Contract testing with Pact and Kafka?
**A:** Trade-off framing for «Contract testing with Pact and Kafka»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** A hot key or message group saturates one shard while autoscaled pods sit idle processing Testing Kafka.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Payment listener test publishes bad record, asserts DLT topic receives it and main offset advances after handler policy — catches regression in error handler co…. I suspect only `@mockbean kafkatemplate` until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```java
@EmbeddedKafka(partitions = 1, topics = {"orders"})
@SpringBootTest
class OrderListenerIT { /* ... */ }
```

---

### 50. Senior design: order events.

**Short answer:** Design: topic `order-events` keyed by `orderId` for per-order ordering; Avro with BACKWARD evolution; producer transactional outbox from order service; consumer idempotent upsert plus DLT; optional compacted `order-state` projection; RF=3, min ISR=2, lag SLO, partitions sized for peak consumers. In production, the trade-off surfaces in on-call incidents and reconciliation — not in hello-world demos. Senior teams document the failure mode, monitoring signal, and rollback path before calling this solved. The wrong default here usually means silent data loss, duplicate money movement, or unbounded lag.

#### What it is
The capstone question — draw topics, keys, groups, DB, and failure paths in five minutes. This is what Kafka interviews converge on. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### How it works (internals)
Producer: REST → Oracle TX → outbox → relay to Kafka keyed by orderId. Consumer groups: billing, inventory, notifications — independent offsets. Schema Registry enforces compatible evolution. Poison → DLT with alert. Rebalance duplicates handled by inbox. Monitoring: lag time, URP, rebalance rate.

#### When to use / when NOT to use
Walk interviewer through dual-write avoidance, ordering scope, delivery semantics, and ops metrics. Mention partition count planning and replay runbook. Optional: compacted snapshot for cache, not sole SoT.

#### Production example
Whiteboard: `order-events` 24 partitions; `OrderService` outbox; three consumer groups; `processed_events` inbox; `orders.DLT`; Grafana lag panel; RF=3 — candidate explains failover and duplicate payment story unprompted. Teams that skip load testing and failure injection here usually learn during a revenue-impacting incident. Document defaults, owner, and alert thresholds in the service runbook — not only in architecture slides.

#### Common mistakes
Queue mental model. No key on order events. Auto-commit consumer on billing. Single partition because easier. No schema strategy.

#### Interview follow-ups (with model answers)

**Q:** How would you add a new consumer group safely?
**A:** For «Senior design: order events»: How would you add a new consumer group safely. In production, Whiteboard: `order-events` 24 partitions; `OrderService` outbox; three consumer groups; `processed_events` inbox; `orders. I disable auto-commit on money paths, commit offsets only after idempotent DB work (inbox/`event_id` UNIQUE), and page on lag time plus rebalance rate — not broker CPU alone. Concrete verification: reconciliation between ledger and bus, duplicate-skip metrics, and a chaos test that kills the pod between DB commit and ack.

**Q:** Replay strategy after bad deploy?
**A:** The follow-on risk of «Replay strategy after bad deploy» is optimizing throughput while breaking ordering, durability, or idempotency. I validate with fault injection: ISR shrink, cert rotation, poison pill on one partition, or MQ backout storm. Spring/Java: `@KafkaListener`/`@JmsListener` concurrency matches partitions or fair queue consumption; bounded retry then DLT/BOQ; outbox on publish, inbox on consume. If I cannot map this to a 2 a.m. symptom and runbook fix, it does not ship on settlement or billing paths.

**Q:** When would you split into multiple topics?
**A:** Trade-off framing for «When would you split into multiple topics»: match volume, compliance, and ops maturity — hybrid IBM MQ + Kafka is normal in banks. Outbox beats dual-write and usually beats XA for new Java services; Kafka EOS covers broker-only boundaries, not Oracle. Choreography suits 2–3 side effects; Temporal/Camunda when timers, humans, or 10+ saga steps appear. Rollback playbook: offset reset by timestamp, DLT replay after schema fix, fail checkout on `NotEnoughReplicas` — never silent `acks=1` on payments.



#### Scenario probe

**Situation:** During a rolling deploy, consumer lag spikes and finance reports duplicate or missing entries tied to Senior design: order events.

**Model answer:** I start with business impact — duplicate charge vs silent loss — then trace correlation ids across logs while checking lag time, rebalance/backout depth, and outbox relay age. Context: Whiteboard: `order-events` 24 partitions; `OrderService` outbox; three consumer groups; `processed_events` inbox; `orders.. I suspect queue mental model until disproven. I verify side effects land in DB before offset/ack commit; inbox idempotency on `event_id` handles redelivery from rebalance or MQ backout. Poison/schema failures get bounded retry then DLT/BOQ with paging — not infinite loop on one offset. If durability gates (`acks=all`, `min.insync.replicas`) block produce, I fail checkout loudly rather than accept single-replica writes. Fix pairs code/runbook change with reconciliation job and chaos test (SIGKILL between DB commit and ack). I explain RPO/RTO trade-offs to product instead of quietly weakening guarantees.

#### Code / config (when useful)
```properties
# order-events topic
partitions=24
replication.factor=3
min.insync.replicas=2
cleanup.policy=delete
retention.ms=1209600000

# consumer
group.id=billing-projection-v1
enable.auto.commit=false
isolation.level=read_committed
```

---

## Deep-dive additions (Q51–Q55)

Kafka Connect, stream processing choices, tiered storage, KRaft operations, and MirrorMaker 2.

---

### 51. Kafka Connect: source/sink connectors, SMT, error tolerance

**Short answer:** **Kafka Connect** is a distributed framework for streaming data between Kafka and external systems (Oracle, S3, Elasticsearch) via **connector plugins**. **Source** connectors ingest into topics; **sink** connectors export from topics. **Single Message Transforms (SMT)** mutate records in-flight (mask PII, route topic). **Error tolerance** (`errors.tolerance=all`, DLQ topic) prevents one poison row from stopping the connector. Trade-off: managed Connect cluster ops versus custom Spring `@KafkaListener` ETL you fully control.

#### What it is
Connect runs as separate worker cluster (or Confluent Cloud managed). Debezium is popular **source** for CDC; JDBC sink for warehouse loads. Java teams often use Connect for integration boundaries while app services use producers/consumers for domain events. SMT chain configured in connector JSON — no redeploy for simple field renames.

#### How it works (internals)
Worker loads connector JAR; tasks partition work (e.g., one task per table). Offsets stored in `connect-offsets` internal topic. SMT: `ExtractField`, `RegexRouter`, `MaskField` applied per record. `errors.deadletterqueue.topic.name` routes failures with context. Converters: Avro, JSON, ByteArray. Throughput tuned via `tasks.max`, batch size, and source DB log retention (Debezium needs transaction log).

#### When to use / when NOT to use
Use Connect for boilerplate JDBC/CDC/S3 pipelines with ops team owning workers. Custom Java consumer when complex business rules, sagas, or idempotent upsert logic belongs in domain service. Do not duplicate same CDC path in Connect and Debezium embedded in app without coordination.

#### Production example
Debezium Oracle connector streams `ORDERS` to `oracle.orders`; SMT `ExtractField` pulls `after` image; sink to Snowflake JDBC connector with `errors.tolerance=all` and DLQ `connect-dlq`. Poison `NULL` key routed to DLQ — ops replay after fix without stopping main pipeline.

#### Common mistakes
- `errors.tolerance=all` without monitoring DLQ — silent data loss perception.
- SMT ordering wrong — transform before converter breaks schema.
- More tasks than partitions — idle tasks.
- Debezium without log mining retention on Oracle — snapshot gaps.

#### Interview follow-ups (with model answers)

**Q:** Connect vs custom Spring Kafka consumer for JDBC sink?
**A:** Connect for generic table mirror with ops-managed scaling; Spring when merge logic, enrichment, and idempotency are domain-specific (payment projection). Many enterprises: Connect to raw topic, Java consumer to curated projection.

**Q:** How scale Connect workers?
**A:** Increase `tasks.max` up to topic partitions for sink; horizontal workers with same `group.id`. Monitor `task-status`, rebalance on worker failure, and lag on source connector offset.

#### Scenario probe
JDBC sink connector stops entirely on one bad JSON field in topic.

**Model answer:** Enable `errors.tolerance=all`, DLQ with `errors.deadletterqueue.context.headers.enable=true`, alert on DLQ rate. Fix producer schema; replay DLQ with transformation. Document that `none` tolerance is only for dev.

#### Code / config (when useful)

```json
{
  "name": "orders-sink",
  "config": {
    "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
    "topics": "orders",
    "errors.tolerance": "all",
    "errors.deadletterqueue.topic.name": "connect-dlq-orders",
    "transforms": "extractKey",
    "transforms.extractKey.type": "org.apache.kafka.connect.transforms.ExtractField$Key",
    "transforms.extractKey.field": "orderId"
  }
}
```

---

### 52. Kafka Streams vs ksqlDB vs external stream processing

**Short answer:** **Kafka Streams** is a Java library for stateful stream processing inside your app (embedded). **ksqlDB** is SQL layer over Kafka Streams for declarative queries and materialized views. **Flink/Spark Streaming** are external clusters for heavy windowing, large state, and mixed sources. Choose Streams/ksqlDB when team is JVM-heavy and workloads fit partition parallelism; Flink when CEP at scale, event-time windows across huge state, or non-Kafka sources dominate. Trade-off: operational simplicity (fewer clusters) versus Flink's power and ops cost.

#### What it is
Stream processing turns event topics into derived topics or KTables. Kafka Streams deploys as Spring Boot jar — no separate cluster. ksqlDB server runs persistent queries (`CREATE STREAM ... AS SELECT`). Flink offers exactly-once across Kafka + JDBC with checkpointing. Senior Java interview: know when not to put Flink in stack for 3 simple aggregations.

#### How it works (internals)
Kafka Streams: topology of processors, state stores (RocksDB), changelog topics for fault tolerance, repartition topics for key change. ksqlDB compiles SQL to Streams topology. Flink: JobManager/TaskManagers, checkpoint to S3, watermarks for late events. Consumer group semantics differ — Streams uses `application.id`, Flink own offset management via checkpoints.

#### When to use / when NOT to use
| Tool | Fit |
|------|-----|
| Kafka Streams | JVM microservice, aggregations, joins, moderate state |
| ksqlDB | Analysts + devs, SQL metrics, quick MVs |
| Flink | High scale CEP, session windows, multi-source, ML pipelines |

Avoid Flink for simple `count per key per minute` if team has no Flink ops.

#### Production example
Fraud team started Flink for velocity rules — ops overhead high. Moved simple rules to Kafka Streams in existing `risk-service` jar; kept Flink only for 24-hour session window CEP. ksqlDB used by ops for ad-hoc `SELECT count(*) FROM payments WHERE amount > 10000 EMIT CHANGES` dashboard.

#### Common mistakes
- Repartition storm from changing key without planning topic count.
- Streams state store disk full on long retention KTable.
- ksqlDB persistent query without `DROP` governance — zombie load.
- Flink mini-cluster in prod without HA checkpoint config.

#### Interview follow-ups (with model answers)

**Q:** Kafka Streams exactly-once?
**A:** `processing.guarantee=exactly_once_v2` with transactional producer and read_committed consumer — effects within Kafka ecosystem. JDBC sink still needs idempotent write or eos connect — same boundary as plain consumer.

**Q:** When migrate Streams to Flink?
**A:** State exceeds single machine RocksDB practicality, need event-time across out-of-order streams at massive scale, or integrate Kafka + Kinesis + files in one job. Cost-benefit includes team skills.

#### Scenario probe
Team proposes Flink cluster for `GROUP BY customer_id COUNT` on one topic — pushback?

**Model answer:** Kafka Streams or ksqlDB in existing platform — Flink ops (checkpoint tuning, upgrades) unjustified. Revisit Flink when CEP rules exceed Streams expressiveness or state TB-scale.

#### Code / config (when useful)

```java
StreamsBuilder builder = new StreamsBuilder();
KStream<String, Payment> payments = builder.stream("payments");
payments.groupByKey().count().toStream().to("payments-per-customer-count");
```

---

### 53. Tiered storage and log retention cost optimization

**Short answer:** **Tiered storage** (Confluent, Apache Kafka 3.6+ tiered) moves older log segments to **object storage** (S3, Azure Blob) while hot data stays on broker disks — cuts retention cost for compliance topics (7-year audit) without buying petabytes of NVMe. **Retention policy** (`retention.ms`, `retention.bytes`) plus compaction for keyed topics balances cost and replay needs. Trade-off: cold read latency versus dollar per GB-month.

#### What it is
Kafka brokers traditionally retain all segments on local disk — expensive at long retention. Tiered offload: local hot tier recent hours/days; remote tier older segments; consumers transparently fetch from remote. Relevant for finance audit logs and CDC topics you must keep but rarely replay.

#### How it works (internals)
Leader enforces retention; tiering plugin uploads closed segments to S3 with metadata in internal topic. Fetch path: try local, then remote object. `local.retention.ms` controls hot window. Compacted topics still tier with key retention semantics. Monitoring: remote fetch latency, upload lag, S3 costs. Not all clients equal — very old offset replay slower.

#### When to use / when NOT to use
Use when retention mandated in years and replay of old data is rare. Short retention dev clusters: standard delete policy sufficient. Combine with mirror to warehouse for analytics instead of infinite Kafka retention when possible.

#### Production example
`audit-events` 7-year retention — local NVMe would cost $2M; tiered S3 $200k/year. `local.retention.ms=604800000` (7 days) for operational replay; compliance replay accepts 30s fetch from cold tier. Alert on tier upload failures — disk fills if upload stuck.

#### Common mistakes
- Tiering without monitoring local disk — upload failure fills broker.
- Assuming replay SLA same for 6-year-old offsets.
- Compaction + tier misconfiguration dropping keys.
- Ignoring egress costs on massive replay.

#### Interview follow-ups (with model answers)

**Q:** Tiered storage vs archive to S3 via Connect sink?
**A:** Tier keeps Kafka consumer API for old offsets; sink moves to parquet for analytics warehouse — different access patterns. Many use tier for compliance replay capability, sink for BI.

**Q:** What retention for CDC topics?
**A:** Long enough for new consumer group bootstrap or snapshot + delta — often days to weeks hot, tier or snapshot to object store for history. Debezium snapshot + incremental offsets reduce need for infinite retention.

#### Scenario probe
CFO asks to keep all payment events 10 years in Kafka — broker disk quote unacceptable.

**Model answer:** Enable tiered storage to S3 with 7-day local hot; document cold replay SLA. Alternative: compacted latest state + warehouse archive for analytics. Cost model comparing tier vs Connect sink.

#### Code / config (when useful)

```properties
# server.properties (Confluent tiered example)
tiered.storage.enable=true
remote.log.storage.system.enable=true
local.retention.ms=604800000
```

---

### 54. KRaft mode — no ZooKeeper operations changes

**Short answer:** **KRaft** (Kafka Raft metadata mode) replaces **ZooKeeper** with internal Raft quorum for cluster metadata — simplifies ops, faster controller failover, supports millions of partitions roadmap. Operators manage **controller quorum** (`process.roles=broker,controller`), format storage once, no ZK ensemble to patch. Trade-off: migration effort from ZK clusters versus long-term operational simplicity.

#### What it is
Traditional Kafka: brokers + ZooKeeper for metadata. KRaft 3.3+ production-ready: controllers elect leader metadata log; brokers subscribe. Java clients unchanged — same protocol. Relevant for platform teams upgrading Kafka 2.x and interview "how Kafka works without ZK."

#### How it works (internals)
Quorum of controller nodes (typically 3 or 5) replicate metadata log via Raft. Broker registration, partition assignment, leader election in metadata log — faster than ZK watch storms. `kafka-storage.sh format` with `cluster.id` once. Migration tools: dual-write metadata phase in supported versions. Monitoring: `MetadataLogEndOffset`, controller active count.

#### When to use / when NOT to use
New clusters: KRaft default. Existing ZK: plan migration per vendor guide (Confluent, Strimzi). Do not run mixed metadata modes in same cluster. Spring apps unaware — only broker bootstrap URLs change if any.

#### Production example
Strimzi migration ZK → KRaft during maintenance window; controllers on dedicated small nodes; brokers `process.roles=broker`. Failover test: kill active controller — metadata recovery <3s vs previous ZK session timeout 18s. Java consumers no code change.

#### Common mistakes
- Even number of controllers (no quorum).
- Skipping storage format on new node join wrong.
- Assuming KRaft removes need for `min.insync.replicas` durability thinking.
- Upgrading without reading migration prerequisites.

#### Interview follow-ups (with model answers)

**Q:** What happens to clients during KRaft migration?
**A:** Kafka protocol stable — clients reconnect on broker restart. Plan rolling broker upgrade; metadata migration is operator concern. Test consumer groups in staging during migration rehearsal.

**Q:** KRaft vs ZooKeeper failure modes?
**A:** ZK session expiry caused controller flapping; KRaft Raft quorum clearer majority rules. Both need odd controller/quorum count and network stability.

#### Scenario probe
Ops wants to eliminate ZK patching toil — outline KRaft migration risks.

**Model answer:** Staging rehearsal, backup, controller quorum sizing, rollback window, verify Strimzi/Kafka version matrix. Application teams: no producer/consumer config change except if admin client used for ZK tools — replace with Kafka Admin API.

#### Code / config (when useful)

```properties
process.roles=broker,controller
node.id=1
controller.quorum.voters=1@ctrl1:9093,2@ctrl2:9093,3@ctrl3:9093
```

---

### 55. MirrorMaker 2 active-active caveats

**Short answer:** **MirrorMaker 2 (MM2)** replicates topics between Kafka clusters (DR, geo-distribution). **Active-active** (bidirectional) risks **infinite replication loops**, **offset mapping confusion**, and **write conflicts** on compacted keys unless topics are **source-specific** (`prefix.source.topic`) and consumers are **cell-aware**. Prefer active-passive for simplicity; active-active only with strict naming, heartbeat topics excluded, and idempotent consumers. Trade-off: geo latency versus operational nightmare.

#### What it is
MM2 uses Connect framework: `MirrorSourceConnector`, `MirrorCheckpointConnector`, `MirrorHeartbeatConnector`. Replicates topic `orders` from `us-east` to `eu-west` as `us-east.orders` or with config prefix. Java consumers must read local cluster primarily; failover runbook defines offset translate via checkpoint topic.

#### How it works (internals)
MM2 tracks offset mapping in internal topics; `sync.topic.acls.enabled` optional. Bidirectional: cluster A → B and B → A requires `replication.policy.separator` and **exclude** mirrored topics from reverse replication (`topics.exclude` regex). Compact topics: last write wins per key — concurrent writes both clusters → undefined winner. Heartbeats detect lag and connectivity.

#### When to use / when NOT to use
Active-passive DR: MM2 one direction, consumers failover to secondary. Active-active: multi-region write with **outbox per region** and **global ID** — not naive topic mirror. Many teams use MM2 for DR only; use separate regional topics for true multi-master.

#### Production example
Attempted active-active `customer-updates` both regions — MM2 loop inflated traffic 10× until `topics.exclude=.*\\.heartbeats,.*\\.checkpoints,us-east\\..*` fixed. Resolution: each region publishes `us-east.customer-updates` only; other region consumes for read models, writes local topic only — no bidirectional same topic name.

#### Common mistakes
- Same topic name written in both clusters without conflict strategy.
- Forgetting to exclude MM2 internal topics from reverse mirror.
- Consumer group offset assumed portable without checkpoint connector.
- No monitoring on replication lag between regions.

#### Interview follow-ups (with model answers)

**Q:** MM2 vs Cluster Linking (Confluent)?
**A:** Both replicate metadata/offsets; Cluster Linking is Confluent-managed lower-latency option. MM2 is open-source portable. Interview: explain loop prevention and offset mapping regardless of product.

**Q:** Failover consumer to DR cluster steps?
**A:** Stop producers to primary if split-brain risk; redirect consumers to DR bootstrap; translate offsets from checkpoint topic or reset with reconciliation job; verify `min.insync.replicas` on DR. Runbook tested quarterly.

#### Scenario probe
Global bank wants active-active Kafka for trading — both NY and London publish `trades`.

**Model answer:** Do not mirror same topic both ways. Use region-prefixed topics, aggregate in each region for local risk, or single writer region per instrument class with read replicas via MM2 one-way. Conflict resolution on compacted keys is business logic, not MM2 feature.

#### Code / config (when useful)

```properties
# MM2 — prevent reverse replication of mirrored topics
topics.exclude=.*[\-\.]heartbeats,.*[\-\.]checkpoints,.*[\-\.]offset-syncs,us-east\..*
replication.policy.class=org.apache.kafka.connect.mirror.DefaultReplicationPolicy
```

---

## Scenario-based interview drills

### S1. Consumer lag spike during Black Friday rollout

**Situation:** E-commerce `payment-projection` consumer group on topic `payments.events` (24 partitions, RF=3). During a K8s rolling deploy of 24 pods, Grafana shows `records-lag-max` jumping from 2k to 400k in 8 minutes. Finance reports delayed fraud holds. No broker alerts; CPU on consumers is moderate.

**What they're testing:** Rebalance storms, `max.poll.interval.ms`, cooperative vs eager rebalance, idempotent consumers, and whether you diagnose consumer-side vs broker-side.

**How to structure your answer:** State symptom → check rebalance rate metric → correlate with deploy → inspect handler p99 and poll interval → explain duplicate risk → propose fix and prevention.

**Model answer:** First I'd pull consumer group rebalance rate and `kafka.consumer:type=consumer-coordinator-metrics` for the payment group — a deploy-time spike usually means partitions revoked mid-batch. I'd check whether cooperative sticky assignor is configured and if `max.poll.interval.ms` was exceeded because Oracle upserts in the listener averaged 6+ minutes on fat batches. The lag spike is likely rebalance churn: consumers kicked, partitions reassigned, same offsets reprocessed while new owners catch up. I'd verify `enable.auto.commit=false` and manual ack after DB commit, with inbox dedup on `eventId` — duplicates during rebalance are expected, not bugs. Short-term: pause deploy, raise interval modestly, cut `max.poll.records` from 500 to 80, add static `group.instance.id` for rolling restarts. Long-term: idempotent upsert, rebalance listener metrics, alert on rebalance rate > 0.1/min, load-test deploy under peak. I would NOT scale pods beyond 24 — extra consumers idle on 24 partitions.

**Common weak answers:** "Add more consumers" without partition math; blaming Kafka without checking rebalance metrics; claiming EOS fixes Oracle duplicates; ignoring that lag recovered but payments doubled.

**Follow-up probes (with answers):**

**Q:** How do you prove duplicates happened vs just lag?
**A:** Query `processed_events` for duplicate `eventId` inserts hitting unique constraint, compare ledger entries to Kafka offsets for same `paymentId`, and check consumer logs for same `partition:offset` processed twice. Metrics: `inbox.duplicate.skipped` counter should spike during incident. Reconciliation job comparing sum(payments) to source events confirms business impact.

**Q:** Would Kafka transactions eliminate this?
**A:** Only for effects inside Kafka (consume-transform-produce). Oracle writes are outside the transaction boundary — you still need inbox idempotency. Transactions help if the projection wrote only to another Kafka topic; they do not span JDBC.

---

### S2. `acks=all` producer outage during rack failure

**Situation:** Payment producer uses `acks=all`, topic RF=3, `min.insync.replicas=2`. One AZ loses power; two followers on a hot partition go offline; ISR shrinks to 1. Producers throw `NotEnoughReplicasException`; checkout cannot publish `PaymentCaptured`. Ops wants to lower `min.insync.replicas` to 1 to restore traffic.

**What they're testing:** Durability vs availability trade-off, ISR semantics, operational judgment under incident pressure.

**How to structure your answer:** Explain why produce fails → what lowering min ISR risks → alternative mitigations → decision framework for money paths.

**Model answer:** With `acks=all` and `min.insync.replicas=2`, Kafka correctly refuses writes that could be lost if the sole surviving replica dies — this is working as designed, not a misconfiguration. Lowering min ISR to 1 restores availability but accepts RPO > 0: a single-replica write can vanish on broker crash, which is unacceptable for payment facts. I'd first verify unclean leader election is disabled, check if followers are recoverable vs permanently lost, and consider moving leadership after broker replacement. Short-term business mitigation: queue captures in Oracle outbox (already committed) and pause checkout banner — do not silently accept single-replica Kafka writes. If ISR is temporarily low during planned maintenance, fail fast with clear ops runbook rather than weaken durability. Post-incident: rack-aware broker placement, monitor under-replicated partitions, document that payment producers must never use `acks=1` as a 'fix.'

**Common weak answers:** "Lower min ISR immediately"; "Use acks=1 for now"; not mentioning unclean leader election; treating RF=3 as sufficient without min ISR.

**Follow-up probes (with answers):**

**Q:** What is the difference between ISR shrink and under-replicated partitions?
**A:** Under-replicated means fewer live replicas than RF; ISR is the subset considered caught-up enough for `acks=all`. A partition can be under-replicated while ISR=2 if one follower is lagging out of ISR. Both metrics matter: URP for redundancy health, ISR size for produce eligibility.

**Q:** How do clients handle `NotEnoughReplicasException`?
**A:** Idempotent producer retries with backoff until timeout (`delivery.timeout.ms`). Application should surface failure to caller, not swallow. Circuit-break checkout if produce fails consistently; rely on outbox for eventual publish once cluster healthy.

---

### S3. Hot partition on mega-tenant key

**Situation:** SaaS billing topic keyed by `tenantId`, 48 partitions. One enterprise tenant generates 40% of traffic. Partition 7 lag is 2M records; other partitions near zero. Adding consumer pods does not help.

**What they're testing:** Partitioning strategy, hot keys, salting trade-offs, monitoring per-partition lag.

**How to structure your answer:** Diagnose skew → explain why scale-out fails → propose key redesign → mention ordering impact.

**Model answer:** Kafka assigns all messages with the same key to one partition — a dominant `tenantId` creates a single hot partition capped by one broker disk and one consumer thread in the group. Adding pods cannot parallelize one partition. I'd confirm skew via per-partition produce/consume rate metrics and key distribution sampling. Fixes depend on ordering needs: if per-tenant strict order is required, isolate the mega-tenant to a dedicated topic with more partitions using salted sub-keys only if sub-entity order suffices (e.g., `tenantId:invoiceId`). If strict tenant order is mandatory, accept vertical scaling on that shard or negotiate async billing SLA. Operational mitigations: dedicated consumer instance for hot partition assignment (custom assignor), optimize handler (batch JDBC), compress payloads. Prevention: capacity review at onboarding for large tenants, document partition count cannot fix single-key heat.

**Common weak answers:** "Increase partitions to 96" without re-keying; random keys losing order; "Kafka is horizontally scalable" without partition caveats.

**Follow-up probes (with answers):**

**Q:** How do you salt keys without losing all ordering?
**A:** Use composite key `tenantId:shardId` where `shardId = hash(subEntityId) % N` — order holds within sub-entity (invoice) but not across invoices. Document the narrowed guarantee in the contract.

**Q:** How detect hot keys before production?
**A:** Load test with production key distribution; metric `records-lag` per partition; broker `BytesInPerSec` per partition; sample producer logs for key frequency.

---

### S4. Poison pill blocks fulfillment partition

**Situation:** `shipping-updates` consumer processes keyed by `orderId`. After a bad deploy, one Avro record fails deserialization. Consumer retries indefinitely; 50k messages behind on partition 3; customers see stale tracking.

**What they're testing:** Head-of-line blocking, DLT strategy, ordering vs liveness, Spring ErrorHandler.

**How to structure your answer:** Recognize HoL blocking → classify poison vs transient → DLT with alert → safe replay → producer-side validation.

**Model answer:** Kafka preserves order per partition — a failing record at offset N blocks N+1 indefinitely if we retry in place. This is head-of-line blocking, not a broker bug. I'd confirm with logs (deserialization error, same offset repeated), then route to DLT after bounded retries using Spring `DefaultErrorHandler` + `DeadLetterPublishingRecoverer` with `FixedBackOff(1000, 3)`. Alert on DLT rate and partition lag. Main partition unblocks immediately after skip/DLT. Root cause: schema mismatch from deploy — fix producer compatibility, register schema in CI. Replay DLT only after fix, with idempotent consumer (tracking state upsert by `eventId`). Prevention: schema compatibility gate in CI, canary consumer on new schema, consider quarantine topic for unknown versions. For payments I'd stall; for tracking, DLT-after-3 is appropriate.

**Common weak answers:** Infinite retry; "add consumers" on one blocked partition; replay DLT without fixing schema; deleting messages manually without audit.

**Follow-up probes (with answers):**

**Q:** Does retry topic preserve order?
**A:** Not globally — retry topic breaks strict partition order but restores liveness. Re-entry to main topic must be idempotent; downstream should tolerate slight reordering within an order if multiple events exist.

**Q:** How to replay DLT safely?
**A:** Dedicated reprocessor with tooling that logs operator, validates schema version, publishes to main with `replay=true` header; handlers skip non-idempotent side effects when header set.

---

### S5. EOS producer + Oracle — double charge incident

**Situation:** Team enabled `enable.idempotence=true` and `@Transactional` Kafka listener writing to Oracle. Customer reports double charge after pod restart. Logs show same `PaymentCaptured` processed twice.

**What they're testing:** EOS boundaries, dual-write, inbox pattern, rebalance duplicates.

**How to structure your answer:** Explain why EOS didn't help Oracle → failure sequence → inbox fix → offset commit order.

**Model answer:** Kafka EOS (idempotent producer + transactions + `read_committed`) guarantees no duplicate records within the broker log for a single producer instance — it does not make Oracle writes atomic with offset commits. The likely sequence: listener charged Oracle, crashed before `ack.acknowledge()`, rebalance reassigned partition, second consumer reprocessed same offset. Alternatively, chained TX fantasy — Spring `@Transactional` on JDBC and Kafka are separate resources. Fix: inbox table `INSERT INTO processed_events(event_id)` with UNIQUE in same `@Transactional` as ledger update; on duplicate key, skip business logic but still ack offset. Commit order: DB TX first, then Kafka offset. Outbox on publish side if producer. Educate team: "EOS" in docs means Kafka-only; end-to-end requires idempotent consumers. Add metric for duplicate skips and integration test that kills pod mid-handler.

**Common weak answers:** "Enable exactly-once on producer"; ChainedKafkaTransactionManager as silver bullet; commit offset before DB.

**Follow-up probes (with answers):**

**Q:** Would storing offset in Oracle help?
**A:** Yes — same TX as projection/inbox (`consumer_offsets` table) gives effectively-once: commit DB including offset, then sync commit to Kafka, or read offset from DB on startup. Duplicate delivery hits inbox constraint.

**Q:** How test duplicate delivery?
**A:** Testcontainers Kafka, process message, kill thread before ack, restart consumer, assert single ledger row; publish same event twice, assert idempotent outcome.

---

### S6. New consumer group `auto.offset.reset=latest` data loss

**Situation:** Team deploys `billing-v4` with `spring.kafka.consumer.group-id: billing-v4` and `auto-offset-reset: latest` copied from a real-time dashboard service. Billing misses 18 hours of `OrderPlaced` events; revenue recognition wrong.

**What they're testing:** Consumer groups, offset reset, operational discipline for new groups.

**How to structure your answer:** Explain new group has no commits → latest skips backlog → recovery with earliest + idempotency → process for new groups.

**Model answer:** A new `group.id` has no entries in `__consumer_offsets` — on first subscribe, `auto.offset.reset` decides start position. `latest` jumps to log end, silently skipping retained history — catastrophic for billing, correct for live dashboards. Detection: zero lag while business metrics diverge. Recovery: temporarily set `earliest` or use `kafka-consumer-groups --reset-offsets --to-datetime`, with idempotent inbox because replay reprocesses history. Long-term: runbook for new consumer groups mandates `earliest` + idempotent design; integration test that asserts first deploy processes seeded topic; never copy config between heterogeneous consumers. Consider explicit migration from v3 group with offset translation if same logical consumer.

**Common weak answers:** Assuming reset applies every restart; using `${HOSTNAME}` as group id; no reconciliation between billing and orders.

**Follow-up probes (with answers):**

**Q:** When is `latest` appropriate?
**A:** New real-time metrics consumer where historical backfill is unnecessary or handled by separate batch job. Document the intentional skip in runbook.

**Q:** How prevent in CI/CD?
**A:** Helm chart review checklist; assert `group-id` stable string; smoke test publishes event before consumer starts, verifies processing.

---

### S7. Outbox relay lag causing stale integrations

**Situation:** Order service uses transactional outbox in Oracle. Orders appear in DB immediately but `OrderPlaced` events arrive in Kafka 3–8 minutes late. Inventory oversells during flash sale.

**What they're testing:** Outbox polling vs CDC, relay monitoring, integration SLOs.

**How to structure your answer:** Measure relay lag → compare polling vs CDC → index/fix poller → SLO and alerts.

**Model answer:** The outbox pattern guarantees eventual publish after DB commit — not instantaneous. Multi-minute lag suggests polling interval too high, missing index on `(published_at)`, poller single-threaded falling behind flash volume, or lock contention on `SELECT FOR UPDATE`. I'd metric `outbox_unpublished_count` and age of oldest unpublished row. Check poller logs and DB execution plan — full table scan is common footgun. Fixes: index on unpublished rows, `FOR UPDATE SKIP LOCKED` with multiple relay instances, reduce poll interval, batch size tuning. If SLO needs sub-second, migrate outbox table to Debezium CDC — near real-time with ops overhead. Business mitigation: inventory holds sync API read-your-writes on order confirmation while async catches up. Alert when oldest unpublished > 30s during peak.

**Common weak answers:** "Use Kafka transactions"; delete outbox before publish confirmed; no relay monitoring; blaming inventory service only.

**Follow-up probes (with answers):**

**Q:** Polling vs Debezium for outbox?
**A:** Polling is simpler, adds DB read load and seconds lag. Debezium tails redo/WAL — lower latency, needs connector ops and schema handling. Many teams start poll, CDC when SLO tightens.

**Q:** Duplicate publish from relay?
**A:** Possible on crash after publish before `published_at` update — consumer idempotency by `outbox_id`/`event_id` is mandatory; producer keys by aggregate id.

---

### S8. Compact topic + GDPR erasure gap

**Situation:** `customer-profiles` compacted topic keyed by `customerId` feeds recommendation engine. Customer exercises right to erasure; SQL anonymized; legal asks for Kafka proof of deletion.

**What they're testing:** Compaction, tombstones, retention, GDPR in event systems.

**How to structure your answer:** DB delete ≠ Kafka delete → tombstone → compaction lag → crypto-shred alternative → audit.

**Model answer:** Compacted topics retain the latest value per key until tombstone and `delete.retention.ms` elapse. SQL DELETE does not remove Kafka segments — consumers and disk still hold PII until a tombstone record (`key=customerId`, `value=null`) is produced and compaction runs. I'd verify compaction lag and segment age; produce tombstone from erasure saga; confirm consumers handle null as delete in materialized views. For historical fat events with PII, field-level encryption with DEK destruction (crypto-shred) may be faster than topic rewrite. Document that compaction is asynchronous — tail readers may see stale data briefly. Prevention: minimize PII in events (token ids only), retention bounds, erasure handler in every projection consumer. Legal hold may block erasure — separate workflow.

**Common weak answers:** "We deleted the database row"; compact topic as instant delete; no consumer tombstone handling.

**Follow-up probes (with answers):**

**Q:** How long until tombstone removes data?
**A:** After compaction cycle plus `delete.retention.ms` (default 24h) — plan audits accordingly; monitor `log-cleaner` metrics.

**Q:** Replay resurrecting PII?
**A:** Yes — replaying pre-erasure offsets restores old values; erasure must include projection rebuild from sanitized snapshot or replay with erasure events applied.

---

### S9. MirrorMaker 2 failover offset confusion

**Situation:** US-East primary Kafka; MM2 replicates to US-West. DR drill fails over consumers in West but projections duplicate 6 hours of events. Runbook said "start consumers."

**What they're testing:** MM2 semantics, offset portability, DR procedures.

**How to structure your answer:** Offsets are not portable → reset strategy → by_timestamp → idempotent consumers.

**Model answer:** MM2 replicates topic data, not consumer group offsets in a directly portable way — partition offset 900 in East is not guaranteed same semantic position in West after replication lag. Starting West consumers without offset strategy defaults to `auto.offset.reset` behavior for new groups or stale commits. Correct DR: predefine consumer group offset mapping MM2 topics, or reset `--to-datetime` to RPO boundary (e.g., 15 min before failover), with idempotent inbox because overlap duplicates expected. Drill quarterly; measure replication lag as RPO input. Active-active dual-write without conflict resolution is worse — stick active-passive for payments. Document that failback requires careful offset reconciliation.

**Common weak answers:** Assuming MM2 copies offsets seamlessly; `latest` on failover; no idempotency during DR.

**Follow-up probes (with answers):**

**Q:** How set RPO with MM2?
**A:** Monitor replication lag metrics (max lag time per topic/partition); RPO ≈ lag at failover + detection time; size West cluster to catch up after failback.

**Q:** Active-active when viable?
**A:** Only with region in key, conflict handler, or CRDT — rare for financial aggregates; most banks active-passive.

---

### S10. Senior whiteboard: order events platform

**Situation:** Interview asks: "Design Kafka for order lifecycle — 5k orders/sec peak, billing, inventory, analytics, fraud; money path; replay after bugs."

**What they're testing:** End-to-end architecture: topics, keys, outbox, groups, semantics, ops.

**How to structure your answer:** Topics/partitions → produce path (outbox) → consumer groups → idempotency → schema → failure/replay → metrics.

**Model answer:** I'd propose topic `order-events` with 24–48 partitions keyed by `orderId` for per-order ordering, RF=3, `min.insync.replicas=2`, delete retention 14–30 days for replay. Order service writes Oracle + outbox in one TX; Debezium or poller publishes Avro `OrderPlaced`/`OrderCancelled` with Schema Registry BACKWARD. Separate consumer groups: `inventory-projection`, `billing-projection`, `fraud-scoring`, `analytics` — independent lag SLOs. All consumers: `enable.auto.commit=false`, inbox on `eventId`, manual ack after DB TX. Billing path explains rebalance duplicate story unprompted. Poison → DLT with alert. Optional compacted `order-snapshot` for cache bootstrap, not financial SoT. Monitoring: lag time (not just offset), URP, rebalance rate, outbox age. Replay runbook: reset offsets to timestamp after fix, idempotent handlers, classify email as non-replay-safe. I explicitly reject dual-write and auto-commit. Partition count planned upfront — increase requires migration plan.

**Common weak answers:** Single partition; queue mental model; EOS fixes Oracle; no schema strategy; one consumer group for all.

**Follow-up probes (with answers):**

**Q:** How add new consumer group safely?
**A:** New stable `group.id`, `earliest` with idempotent inbox, deploy during low traffic, monitor lag catch-up, reconcile output against source before cutting over.

**Q:** When split topics?
**A:** When retention, security classification, or schema churn differ — e.g., `order-events` vs PII-light `order-analytics` vs compacted `order-snapshot`.

---
