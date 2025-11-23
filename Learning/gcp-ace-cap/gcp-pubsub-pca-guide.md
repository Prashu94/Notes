# Google Cloud Pub/Sub PCA Guide

## 1. Architecture & Design Patterns

### Global vs. Regional
- **Global Service:** Pub/Sub is global by default. Topics and subscriptions are global resources.
- **Data Residency:** You can restrict message storage to specific regions using **Message Storage Policies**.

### Common Patterns
1.  **Fan-out:** One publisher, multiple subscriptions. Each subscription gets a copy of every message.
    - *Use Case:* Order placed -> Send Email, Update Inventory, Notify Analytics.
2.  **Work Queue:** Multiple subscribers on a *single* subscription. Messages are load-balanced across subscribers.
    - *Use Case:* Image processing workers.
3.  **Event Sourcing:** Capture all changes as a sequence of events.
4.  **Dead Letter Queue (DLQ):** Handle poison pill messages that fail processing repeatedly.

## 2. Reliability & Delivery Guarantees

### At-Least-Once Delivery (Default)
- Messages are replicated across multiple zones.
- Duplicates can happen (e.g., ack lost). Applications must be **idempotent**.

### Exactly-Once Delivery
- Pub/Sub can enforce exactly-once delivery within a subscription.
- Requires enabling "Exactly-once delivery" on the subscription.
- Performance trade-off: Slightly higher latency.

### Ordering
- **Ordering Keys:** Guarantees order for messages with the same key.
- **Head-of-Line Blocking:** If a message fails, subsequent messages with the same key are blocked until the failure is resolved or the message expires.

## 3. Handling Failures & Replay

### Dead Letter Topics
- Automatically forward undeliverable messages to a separate topic after `N` delivery attempts.
- Allows main processing to continue while isolating bad data.

### Snapshots & Seek
- **Snapshot:** Captures the acknowledgment state of a subscription at a point in time.
- **Seek:** Replay messages by seeking to a snapshot or a timestamp.
- *Use Case:* A bug in the subscriber code processed messages incorrectly. Fix the bug, then seek back to replay and re-process correctly.

## 4. Migration & Integration

### Kafka vs. Pub/Sub
| Feature | Apache Kafka | Cloud Pub/Sub |
| :--- | :--- | :--- |
| **Management** | Self-managed / Confluent | Fully Managed (Serverless) |
| **Scaling** | Partitions (Manual) | Auto-scaling (Per-message) |
| **Ordering** | Per Partition | Per Ordering Key |
| **Retention** | Log-based (Time/Size) | Per Subscription (Acked/Unacked) |

### Pub/Sub Lite
- Zonal, partition-based service (Kafka-like).
- Lower cost for high-throughput, predictable workloads.
- Manual capacity management (provision throughput).

## 5. Cost Optimization

- **Message Size:** Pricing is based on data volume (minimum 1KB per message).
    - *Tip:* Batch small messages into a single Pub/Sub message if they are < 1KB.
- **Filtering:** Filter messages at the subscription level to avoid paying for egress and processing of unneeded messages.
- **Retention:** Minimize unacknowledged message retention duration if not needed.
- **Ack Deadline:** Set appropriate deadlines to avoid redelivery (and re-processing costs).

## 6. Decision Matrix

| Requirement | Solution |
| :--- | :--- |
| **Global, Serverless, Auto-scaling** | **Standard Pub/Sub** |
| **High Throughput, Low Cost, Zonal** | **Pub/Sub Lite** |
| **Strict Ordering** | **Pub/Sub with Ordering Keys** |
| **Replay Capability** | **Pub/Sub Snapshots / Seek** |
| **IoT Ingestion** | **Cloud IoT Core (Deprecated) -> Pub/Sub** |
