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

---

## 7. Event-Driven Architecture Patterns

### Microservices Communication Pattern

```
┌──────────────────────────────────────────────────────────┐
│              EVENT-DRIVEN MICROSERVICES                   │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─────────────┐                                          │
│  │ Order       │──┐                                       │
│  │ Service     │  │                                       │
│  └─────────────┘  │                                       │
│                   ▼                                       │
│              ┌──────────┐                                 │
│              │ Pub/Sub  │                                 │
│              │  Topic   │                                 │
│              │ "orders" │                                 │
│              └──────────┘                                 │
│                   │                                       │
│      ┌────────────┼────────────┬────────────┐            │
│      ▼            ▼            ▼            ▼            │
│  ┌────────┐  ┌────────┐  ┌─────────┐  ┌─────────┐       │
│  │Inventory│  │Payment │  │Shipping │  │Analytics│       │
│  │Service  │  │Service │  │Service  │  │Service  │       │
│  └────────┘  └────────┘  └─────────┘  └─────────┘       │
│  (Sub 1)     (Sub 2)     (Sub 3)      (Sub 4)            │
└──────────────────────────────────────────────────────────┘

Benefits:
- Loose coupling
- Independent scaling
- Service resilience
- Easy to add new consumers
```

### Stream Processing Pattern (Real-Time Analytics)

```
┌──────────────────────────────────────────────────────────┐
│           REAL-TIME STREAM PROCESSING                     │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐           │
│  │Web Apps  │───►│IoT Devices───►│Mobile Apps│           │
│  └──────────┘    └──────────┘    └──────────┘           │
│        │              │                │                 │
│        └──────────────┼────────────────┘                 │
│                       ▼                                  │
│              ┌─────────────────┐                         │
│              │   Pub/Sub Topic │                         │
│              │   "events"      │                         │
│              └─────────────────┘                         │
│                       │                                  │
│        ┌──────────────┼──────────────┐                   │
│        ▼              ▼              ▼                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │Dataflow  │  │BigQuery  │  │Cloud     │               │
│  │(transform)  │(direct   │  │Functions │               │
│  │          │  │ ingest)  │  │(alerting)│               │
│  └──────────┘  └──────────┘  └──────────┘               │
│       │                             │                    │
│       ▼                             ▼                    │
│  ┌──────────┐              ┌──────────────┐             │
│  │BigQuery  │              │Cloud         │             │
│  │(analytics)              │Monitoring    │             │
│  └──────────┘              └──────────────┘             │
└──────────────────────────────────────────────────────────┘
```

### Event Sourcing Pattern

```
┌──────────────────────────────────────────────────────────┐
│                  EVENT SOURCING                           │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Application writes events (not state)                    │
│                                                           │
│  ┌────────────────┐                                       │
│  │ UserCreated    │──┐                                    │
│  │ AccountUpdated │  │                                    │
│  │ OrderPlaced    │  │                                    │
│  │ OrderShipped   │  │                                    │
│  └────────────────┘  │                                    │
│                      ▼                                    │
│              ┌──────────────┐                             │
│              │   Pub/Sub    │                             │
│              │ (event log)  │                             │
│              └──────────────┘                             │
│                      │                                    │
│        ┌─────────────┴─────────────┐                      │
│        ▼                           ▼                      │
│  ┌──────────────┐          ┌──────────────┐              │
│  │ Read Model 1 │          │ Read Model 2 │              │
│  │ (Firestore)  │          │ (BigQuery)   │              │
│  │ - Current    │          │ - Analytics  │              │
│  │   state      │          │   queries    │              │
│  └──────────────┘          └──────────────┘              │
│                                                           │
│  Benefits:                                                │
│  - Full audit trail                                       │
│  - Time-travel (replay to any point)                      │
│  - Multiple projections from same events                  │
└──────────────────────────────────────────────────────────┘
```

---

## 8. High-Availability and Disaster Recovery

### Multi-Region Pub/Sub Architecture

```
┌──────────────────────────────────────────────────────────┐
│            GLOBAL HIGH-AVAILABILITY PATTERN               │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  US Region                           EU Region            │
│  ┌────────────┐                     ┌────────────┐       │
│  │ Publisher  │                     │ Publisher  │       │
│  │ (US apps)  │                     │ (EU apps)  │       │
│  └────────────┘                     └────────────┘       │
│        │                                   │              │
│        ▼                                   ▼              │
│  ┌──────────────┐                   ┌──────────────┐     │
│  │  Pub/Sub     │                   │  Pub/Sub     │     │
│  │  Topic (US)  │◄─────sync────────►│  Topic (EU)  │     │
│  └──────────────┘                   └──────────────┘     │
│        │                                   │              │
│        ▼                                   ▼              │
│  ┌──────────────┐                   ┌──────────────┐     │
│  │ Subscribers  │                   │ Subscribers  │     │
│  │ (US region)  │                   │ (EU region)  │     │
│  └──────────────┘                   └──────────────┘     │
│                                                           │
│  Implementation Options:                                  │
│  1. Separate topics per region + application-level sync  │
│  2. Global topic with message storage policy              │
│  3. Dataflow for cross-region replication                │
└──────────────────────────────────────────────────────────┘
```

### Message Storage Policy for Data Residency

```bash
# Restrict message storage to specific regions (GDPR compliance)
gcloud pubsub topics create eu-orders \
    --message-storage-policy-allowed-regions=europe-west1,europe-west4

# Update existing topic
gcloud pubsub topics update orders \
    --message-storage-policy-allowed-regions=us-central1,us-east1

# No restriction (default global)
gcloud pubsub topics create global-events
```

### Snapshot and Seek for Disaster Recovery

```bash
# Create snapshot before risky deployment
gcloud pubsub snapshots create pre-deployment-snapshot \
    --subscription=my-subscription

# Deploy new code
# ... if issues found ...

# Seek back to snapshot (replay messages)
gcloud pubsub subscriptions seek my-subscription \
    --snapshot=pre-deployment-snapshot

# Or seek to specific timestamp
gcloud pubsub subscriptions seek my-subscription \
    --time="2024-01-15T10:00:00Z"
```

### Example: Disaster Recovery Workflow

```python
from google.cloud import pubsub_v1
from datetime import datetime, timedelta

project_id = "my-project"
subscription_id = "critical-subscription"
snapshot_id = f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)
snapshot_path = subscriber.snapshot_path(project_id, snapshot_id)

# 1. Create snapshot before maintenance
snapshot = subscriber.create_snapshot(
    request={"name": snapshot_path, "subscription": subscription_path}
)
print(f"Created snapshot: {snapshot.name}")

# 2. Perform maintenance/deployment
# ...

# 3. If issues occur, seek to snapshot
seek_request = pubsub_v1.types.SeekRequest(
    subscription=subscription_path,
    snapshot=snapshot_path
)
seek_response = subscriber.seek(seek_request)
print(f"Seeked to snapshot: {seek_response}")

# 4. Clean up old snapshots (after validation)
# subscriber.delete_snapshot(request={"snapshot": snapshot_path})
```

---

## 9. Exactly-Once Delivery Architecture

### How It Works

```
┌──────────────────────────────────────────────────────────┐
│           EXACTLY-ONCE DELIVERY FLOW                      │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  Publisher                                                │
│     │                                                     │
│     ├─► Message 1 (ID: msg-001) ──┐                       │
│     ├─► Message 2 (ID: msg-002)   │                       │
│     └─► Message 3 (ID: msg-003)   │                       │
│                                   ▼                       │
│                          ┌──────────────┐                 │
│                          │   Pub/Sub    │                 │
│                          │  (stores msg │                 │
│                          │   IDs)       │                 │
│                          └──────────────┘                 │
│                                   │                       │
│                                   ▼                       │
│                          ┌──────────────┐                 │
│                          │ Subscription │                 │
│                          │ (exactly-once│                 │
│                          │  enabled)    │                 │
│                          └──────────────┘                 │
│                                   │                       │
│                                   ▼                       │
│                          ┌──────────────┐                 │
│                          │  Subscriber  │                 │
│                          └──────────────┘                 │
│                                   │                       │
│     Process msg-001 ──────────────┤                       │
│     (success) ───────────────► ACK│                       │
│                                   │                       │
│     Pub/Sub deduplicates based on message ID              │
│     Even if ACK is lost, msg-001 won't be redelivered     │
└──────────────────────────────────────────────────────────┘
```

### Configuration

```bash
# Create subscription with exactly-once delivery
gcloud pubsub subscriptions create exactly-once-sub \
    --topic=my-topic \
    --enable-exactly-once-delivery

# Update existing subscription
gcloud pubsub subscriptions update my-sub \
    --enable-exactly-once-delivery
```

### Trade-offs

| Feature | At-Least-Once | Exactly-Once |
|---------|---------------|--------------|
| **Latency** | Low (< 100ms) | Slightly higher (< 200ms) |
| **Throughput** | High | Moderate |
| **Cost** | Standard | +10% (approx) |
| **Use Case** | Idempotent operations | Financial transactions |

---

## 10. Message Ordering at Scale

### Ordering Key Strategy

```python
from google.cloud import pubsub_v1

project_id = "my-project"
topic_id = "orders"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Scenario: E-commerce order lifecycle
# All events for same order must be processed in order

order_id = "ORD-12345"

events = [
    {"type": "ORDER_CREATED", "amount": 100.00},
    {"type": "PAYMENT_RECEIVED", "amount": 100.00},
    {"type": "INVENTORY_RESERVED", "items": 2},
    {"type": "ORDER_SHIPPED", "tracking": "TRK-999"}
]

for event in events:
    data = json.dumps(event).encode('utf-8')
    future = publisher.publish(
        topic_path,
        data,
        ordering_key=order_id  # Critical: Same key for same order
    )
    print(f"Published {event['type']} with message ID: {future.result()}")
```

### Handling Head-of-Line Blocking

```
Problem:
  Message 1 (user-123) → Success
  Message 2 (user-123) → Fails → Blocks
  Message 3 (user-123) → Blocked
  Message 4 (user-456) → Processes (different key)

Solution Strategies:
1. Exponential backoff with DLQ
2. Circuit breaker pattern
3. Separate topics for different priority levels
```

### Circuit Breaker Pattern for Ordering

```python
from google.cloud import pubsub_v1
import time

class OrderedSubscriberWithCircuitBreaker:
    def __init__(self, project_id, subscription_id):
        self.subscriber = pubsub_v1.SubscriberClient()
        self.subscription_path = self.subscriber.subscription_path(
            project_id, subscription_id
        )
        self.failed_keys = {}  # {ordering_key: (fail_count, last_fail_time)}
        self.circuit_breaker_threshold = 3
        self.circuit_breaker_timeout = 60  # seconds
    
    def callback(self, message):
        ordering_key = message.ordering_key
        
        # Check circuit breaker
        if ordering_key in self.failed_keys:
            fail_count, last_fail_time = self.failed_keys[ordering_key]
            if fail_count >= self.circuit_breaker_threshold:
                if time.time() - last_fail_time < self.circuit_breaker_timeout:
                    # Circuit open: Skip this message
                    print(f"Circuit open for key {ordering_key}, skipping")
                    message.nack()
                    return
                else:
                    # Reset circuit breaker
                    del self.failed_keys[ordering_key]
        
        try:
            # Process message
            process_message(message.data)
            message.ack()
            
            # Remove from failed keys if recovered
            if ordering_key in self.failed_keys:
                del self.failed_keys[ordering_key]
        
        except Exception as e:
            print(f"Error processing message: {e}")
            
            # Increment failure count
            if ordering_key in self.failed_keys:
                fail_count, _ = self.failed_keys[ordering_key]
                self.failed_keys[ordering_key] = (fail_count + 1, time.time())
            else:
                self.failed_keys[ordering_key] = (1, time.time())
            
            message.nack()
    
    def start(self):
        streaming_pull_future = self.subscriber.subscribe(
            self.subscription_path,
            callback=self.callback
        )
        print(f"Listening on {self.subscription_path}...")
        
        try:
            streaming_pull_future.result()
        except KeyboardInterrupt:
            streaming_pull_future.cancel()
```

---

## 11. Cost Optimization Strategies at Scale

### Detailed Cost Breakdown

**Pricing Tiers:**
```
First 100 GiB/month: $40.00 per TiB = $0.04/GB
Next 400 GiB/month:  $20.00 per TiB = $0.02/GB
Beyond 500 GiB/month: $10.00 per TiB = $0.01/GB

Message retention beyond ack deadline: $0.27/GB/month
```

### Cost Optimization Techniques

**1. Message Batching**

```python
# EXPENSIVE: Publish 10,000 messages of 100 bytes each
for i in range(10000):
    data = f"Message {i}".encode('utf-8')
    publisher.publish(topic_path, data)
# Total data: 10,000 × 1 KB (minimum) = 10 MB charged
# Cost: $0.0004

# OPTIMIZED: Batch into larger messages
batch_size = 100
batches = []
for i in range(0, 10000, batch_size):
    batch = []
    for j in range(batch_size):
        batch.append(f"Message {i+j}")
    batched_data = json.dumps(batch).encode('utf-8')
    publisher.publish(topic_path, batched_data)
# Total data: 100 messages × 10 KB = 1 MB charged
# Cost: $0.00004 (10x cheaper)
```

**2. Message Filtering at Subscription**

```bash
# WITHOUT FILTERING: All messages delivered (100 GB/day)
# Cost: 100 GB × 30 days × $0.04/GB = $120/month

# WITH FILTERING: Only 10% relevant (10 GB/day)
gcloud pubsub subscriptions create filtered-sub \
    --topic=events \
    --message-filter='attributes.priority = "high"'
# Cost: 10 GB × 30 days × $0.04/GB = $12/month
# Savings: $108/month (90%)
```

**3. Adjust Message Retention**

```bash
# Default: 7 days retention
# If messages typically acknowledged within 1 hour:
gcloud pubsub topics update my-topic \
    --message-retention-duration=6h

# Storage cost savings:
# Default: 100 GB avg unacked × 7 days × $0.27/GB/month = $27/month
# Optimized: 100 GB × 0.25 days × $0.27/GB/month = $0.96/month
# Savings: $26/month
```

**4. Pub/Sub Lite for High-Volume Workloads**

```
Use Case: 1 TB/day ingestion (regional)

Standard Pub/Sub:
- 1 TB × 30 days = 30 TB/month
- Cost: 30,000 GB × $0.01/GB = $300/month

Pub/Sub Lite (zonal):
- 1 TB × 30 days = 30 TB/month
- Cost: 30,000 GB × $0.0025/GB = $75/month
- Savings: $225/month (75% cheaper)

Trade-off: Zonal (not multi-zonal), manual capacity management
```

---

## 12. Advanced Security Patterns

### VPC Service Controls for Data Exfiltration Prevention

```bash
# Create service perimeter around Pub/Sub and BigQuery
gcloud access-context-manager perimeters create data_perimeter \
    --title="Data Processing Perimeter" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=pubsub.googleapis.com,bigquery.googleapis.com \
    --access-levels=corp_network,trusted_ips

# Result:
# - Publishing from outside perimeter: BLOCKED
# - Subscribing from outside perimeter: BLOCKED
# - Data stays within trusted boundary
```

### Customer-Managed Encryption Keys (CMEK)

```bash
# Create KMS key
gcloud kms keyrings create pubsub-keyring --location=us-central1

gcloud kms keys create pubsub-key \
    --keyring=pubsub-keyring \
    --location=us-central1 \
    --purpose=encryption

# Grant Pub/Sub service account access
gcloud kms keys add-iam-policy-binding pubsub-key \
    --keyring=pubsub-keyring \
    --location=us-central1 \
    --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
    --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Create topic with CMEK
gcloud pubsub topics create secure-topic \
    --topic-encryption-key=projects/PROJECT_ID/locations/us-central1/keyRings/pubsub-keyring/cryptoKeys/pubsub-key

# All messages encrypted with your key
# You control key lifecycle (rotation, revocation)
```

### Attribute-Based Access Control

```bash
# Grant conditional access based on message attributes
cat > policy.json << EOF
{
  "bindings": [
    {
      "role": "roles/pubsub.subscriber",
      "members": [
        "serviceAccount:analyst@my-project.iam.gserviceaccount.com"
      ],
      "condition": {
        "title": "Only analytics messages",
        "description": "Allow access only to analytics-tagged messages",
        "expression": "resource.name.endsWith('analytics-sub')"
      }
    }
  ]
}
EOF

gcloud pubsub subscriptions set-iam-policy analytics-sub policy.json
```

---

## 13. Integration Architecture Patterns

### Pub/Sub + Dataflow (Stream Processing)

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.transforms.window import FixedWindows

class ParseMessage(beam.DoFn):
    def process(self, element):
        import json
        data = json.loads(element.decode('utf-8'))
        yield {
            'user_id': data['user_id'],
            'event_type': data['event_type'],
            'value': float(data.get('value', 0)),
            'timestamp': data['timestamp']
        }

class FormatForBigQuery(beam.DoFn):
    def process(self, element):
        user_id, metrics = element
        yield {
            'user_id': user_id,
            'event_count': metrics['count'],
            'total_value': metrics['sum'],
            'window_start': metrics['window_start']
        }

options = PipelineOptions(
    streaming=True,
    project='my-project',
    region='us-central1'
)

with beam.Pipeline(options=options) as pipeline:
    (pipeline
     | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
         subscription='projects/my-project/subscriptions/events-sub'
     )
     | 'Parse JSON' >> beam.ParDo(ParseMessage())
     | 'Window 5 minutes' >> beam.WindowInto(FixedWindows(300))  # 5-min windows
     | 'Group by user' >> beam.GroupBy('user_id')
     | 'Aggregate' >> beam.CombinePerKey(
         beam.combiners.TupleCombineFn(
             beam.combiners.CountCombineFn(),
             beam.combiners.SumCombineFn()
         )
     )
     | 'Format' >> beam.ParDo(FormatForBigQuery())
     | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
         table='my_project:analytics.user_metrics',
         schema='user_id:STRING,event_count:INT64,total_value:FLOAT64,window_start:TIMESTAMP',
         write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
     ))
```

### Pub/Sub + Cloud Functions (Event Processing)

```python
# Function deployed with:
# gcloud functions deploy process_order \
#   --runtime=python39 \
#   --trigger-topic=orders \
#   --entry-point=process_order

import base64
import json
from google.cloud import firestore, pubsub_v1

db = firestore.Client()
publisher = pubsub_v1.PublisherClient()

def process_order(event, context):
    """Process order event and trigger downstream services."""
    
    # Parse message
    message_data = base64.b64decode(event['data']).decode('utf-8')
    order = json.loads(message_data)
    
    order_id = order['order_id']
    customer_id = order['customer_id']
    items = order['items']
    total = order['total']
    
    # Save to Firestore
    db.collection('orders').document(order_id).set({
        'customer_id': customer_id,
        'items': items,
        'total': total,
        'status': 'CREATED',
        'created_at': firestore.SERVER_TIMESTAMP
    })
    
    # Publish to downstream topics
    # 1. Inventory service
    inventory_topic = publisher.topic_path('my-project', 'inventory-check')
    publisher.publish(
        inventory_topic,
        json.dumps({'order_id': order_id, 'items': items}).encode('utf-8')
    )
    
    # 2. Payment service
    payment_topic = publisher.topic_path('my-project', 'process-payment')
    publisher.publish(
        payment_topic,
        json.dumps({'order_id': order_id, 'customer_id': customer_id, 'amount': total}).encode('utf-8')
    )
    
    # 3. Notification service
    notification_topic = publisher.topic_path('my-project', 'send-notification')
    publisher.publish(
        notification_topic,
        json.dumps({'customer_id': customer_id, 'type': 'ORDER_CONFIRMATION', 'order_id': order_id}).encode('utf-8')
    )
    
    print(f"Processed order {order_id}")
```

---

## 14. Monitoring and Observability

### Key Metrics Dashboard (SQL)

```sql
-- Pub/Sub metrics from Cloud Monitoring export to BigQuery

-- 1. Subscription backlog over time
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  resource.labels.subscription_id,
  AVG(value.double_value) as avg_undelivered_messages,
  MAX(value.double_value) as max_undelivered_messages
FROM `project.monitoring.pubsub_subscription_metrics`
WHERE metric.type = 'pubsub.googleapis.com/subscription/num_undelivered_messages'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour, subscription_id
ORDER BY hour DESC, max_undelivered_messages DESC;

-- 2. Message processing latency
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  resource.labels.subscription_id,
  AVG(value.int64_value) as avg_oldest_unacked_age_seconds,
  MAX(value.int64_value) as max_oldest_unacked_age_seconds
FROM `project.monitoring.pubsub_subscription_metrics`
WHERE metric.type = 'pubsub.googleapis.com/subscription/oldest_unacked_message_age'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour, subscription_id
ORDER BY hour DESC, max_oldest_unacked_age_seconds DESC;

-- 3. Publishing rate by topic
SELECT
  TIMESTAMP_TRUNC(timestamp, HOUR) as hour,
  resource.labels.topic_id,
  SUM(value.int64_value) as total_messages_published
FROM `project.monitoring.pubsub_topic_metrics`
WHERE metric.type = 'pubsub.googleapis.com/topic/send_request_count'
  AND timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
GROUP BY hour, topic_id
ORDER BY hour DESC, total_messages_published DESC;
```

### SLI/SLO Design

```yaml
# Example SLOs for Pub/Sub-based system

Service: Order Processing System

SLIs:
  - name: Message Delivery Success Rate
    description: Percentage of messages successfully delivered and acknowledged
    metric: (successful_acks / total_messages_published) × 100
    
  - name: End-to-End Latency
    description: Time from publish to successful processing
    metric: p99(timestamp_ack - timestamp_publish)
    
  - name: Backlog Age
    description: Age of oldest unacknowledged message
    metric: oldest_unacked_message_age

SLOs:
  - SLI: Message Delivery Success Rate
    Target: 99.9% (over 30-day window)
    Error Budget: 0.1% = ~43,000 failed messages/month (at 1M msg/day)
    
  - SLI: End-to-End Latency
    Target: p99 < 5 seconds
    Error Budget: 1% of requests can exceed 5 seconds
    
  - SLI: Backlog Age
    Target: < 60 seconds (99% of time)
    Alert: If > 300 seconds for > 5 minutes

Alerting Policy:
  - Trigger: Error budget 50% consumed
  - Action: Page on-call engineer
  - Escalation: If not resolved in 30 minutes
```

---

## 15. Real-World Reference Architectures

### Financial Trading Platform

```
┌──────────────────────────────────────────────────────────┐
│         FINANCIAL TRADING PLATFORM (LOW-LATENCY)          │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌────────────┐                                           │
│  │ Trading    │                                           │
│  │ Apps       │                                           │
│  └────────────┘                                           │
│        │                                                  │
│        ▼                                                  │
│  ┌──────────────────────────────────────┐                │
│  │  Pub/Sub Topic: "trades"             │                │
│  │  - Exactly-once delivery              │                │
│  │  - Ordering key: trading_account_id   │                │
│  │  - CMEK encrypted                     │                │
│  │  - VPC-SC perimeter                   │                │
│  └──────────────────────────────────────┘                │
│        │                                                  │
│   ┌────┴─────┬──────────┬──────────┐                     │
│   ▼          ▼          ▼          ▼                     │
│ ┌─────┐  ┌──────┐  ┌───────┐  ┌────────┐                │
│ │Risk │  │Fraud │  │Ledger │  │Audit   │                │
│ │Mgmt │  │Check │  │Update │  │Log     │                │
│ └─────┘  └──────┘  └───────┘  └────────┘                │
│  (Sub1)   (Sub2)    (Sub3)      (Sub4)                   │
│                                                           │
│ Key Features:                                             │
│ - Exactly-once delivery (no duplicate trades)             │
│ - Ordering per account (correct sequence)                 │
│ - Sub-second latency                                      │
│ - Full audit trail (compliance)                           │
│ - Encryption at rest and in transit                       │
│                                                           │
│ Cost: ~$500/month for 10M trades/day                      │
└──────────────────────────────────────────────────────────┘
```

### IoT Telemetry at Scale

```
┌──────────────────────────────────────────────────────────┐
│         IOT TELEMETRY PLATFORM (100K DEVICES)             │
├──────────────────────────────────────────────────────────┤
│                                                           │
│  ┌──────────────────────────────────────┐                │
│  │   100,000 IoT Devices                │                │
│  │   - Send metrics every 10 seconds    │                │
│  │   - ~10 TB/day                       │                │
│  └──────────────────────────────────────┘                │
│                 │                                         │
│                 ▼                                         │
│  ┌──────────────────────────────────────┐                │
│  │  Pub/Sub Lite (zonal)                │                │
│  │  - 2 partitions                      │                │
│  │  - 500 MiB/s capacity                │                │
│  │  - Message batching enabled          │                │
│  └──────────────────────────────────────┘                │
│                 │                                         │
│        ┌────────┴────────┐                                │
│        ▼                 ▼                                │
│  ┌──────────┐      ┌──────────┐                          │
│  │ Dataflow │      │BigQuery  │                          │
│  │(real-time│      │(direct   │                          │
│  │ alerts)  │      │ write)   │                          │
│  └──────────┘      └──────────┘                          │
│        │                  │                               │
│        ▼                  ▼                               │
│  ┌──────────┐      ┌───────────┐                         │
│  │ Pub/Sub  │      │ BigQuery  │                         │
│  │ (alerts) │      │ (storage) │                         │
│  └──────────┘      └───────────┘                         │
│        │                  │                               │
│        ▼                  ▼                               │
│  ┌──────────┐      ┌───────────┐                         │
│  │Cloud     │      │ Looker    │                         │
│  │Functions │      │ Dashboard │                         │
│  └──────────┘      └───────────┘                         │
│                                                           │
│ Cost Optimization:                                        │
│ - Pub/Sub Lite: $75/month (vs $3,000 for standard)       │
│ - Message batching: 50x reduction in message count       │
│ - Regional deployment: Lower latency + cost               │
│                                                           │
│ Total Cost: ~$150/month (Pub/Sub Lite + BigQuery)        │
└──────────────────────────────────────────────────────────┘
```

---

## 16. Migration from Kafka to Pub/Sub

### Assessment Checklist

```
✓ Identify Kafka topics → Pub/Sub topics mapping
✓ Analyze partition count → Consider ordering keys
✓ Review consumer groups → Pub/Sub subscriptions
✓ Check message size (max 10 MB in Pub/Sub)
✓ Evaluate exactly-once semantics requirements
✓ Plan for Kafka Connect equivalent (Dataflow)
```

### Migration Strategies

**Strategy 1: Mirror and Cutover**
```
Week 1-2: Dual-publish (Kafka + Pub/Sub)
Week 3: Migrate consumers to Pub/Sub
Week 4: Stop Kafka publishers
Week 5: Decommission Kafka
```

**Strategy 2: Gradual Migration**
```
Phase 1: Migrate non-critical topics
Phase 2: Validate performance and cost
Phase 3: Migrate critical topics
Phase 4: Decommission Kafka
```

### Example Migration Tool

```python
# Bridge: Consume from Kafka, publish to Pub/Sub
from kafka import KafkaConsumer
from google.cloud import pubsub_v1
import json

# Kafka consumer
kafka_consumer = KafkaConsumer(
    'orders',
    bootstrap_servers=['kafka-broker:9092'],
    group_id='migration-bridge',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

# Pub/Sub publisher
publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path('my-project', 'orders')

# Mirror messages
for kafka_message in kafka_consumer:
    data = json.dumps(kafka_message.value).encode('utf-8')
    
    # Preserve Kafka key as Pub/Sub ordering key
    ordering_key = kafka_message.key.decode('utf-8') if kafka_message.key else ''
    
    future = publisher.publish(
        topic_path,
        data,
        ordering_key=ordering_key,
        kafka_offset=str(kafka_message.offset),  # Attribute for tracking
        kafka_partition=str(kafka_message.partition)
    )
    
    print(f"Mirrored message from Kafka partition {kafka_message.partition}, "
          f"offset {kafka_message.offset} to Pub/Sub: {future.result()}")
```

---

## 17. PCA Exam Decision Frameworks

### Pub/Sub vs Alternatives

```
Decision Tree:

Need messaging between services?
├── NO → Direct API calls (REST/gRPC)
└── YES
    └── Need persistence/query capability?
        ├── YES → Use Firestore or BigQuery
        └── NO
            └── Within same application?
                ├── YES → In-memory queue
                └── NO → Need global availability?
                    ├── YES → **Standard Pub/Sub**
                    └── NO → Regional only?
                        ├── YES → High throughput (>100 MB/s)?
                            ├── YES → **Pub/Sub Lite**
                            └── NO → **Standard Pub/Sub**
                        └── NO → **Standard Pub/Sub**
```

### Ordering Decision Matrix

| Requirement | Solution |
|-------------|----------|
| **No ordering needed** | Standard subscription (no ordering key) |
| **Ordering per entity** | Ordering keys (e.g., user_id, order_id) |
| **Global ordering** | Single partition (Pub/Sub Lite) or app-level |
| **Partial ordering** | Multiple ordering keys |

### Delivery Guarantee Selection

| Use Case | Delivery Type | Reasoning |
|----------|---------------|-----------|
| **Log aggregation** | At-least-once | Duplicates acceptable, idempotent |
| **Financial transactions** | Exactly-once | No duplicates allowed |
| **Analytics events** | At-least-once | Dedup in BigQuery later |
| **Order processing** | Exactly-once | Prevent double-charging |

---

## 18. PCA Exam Scenarios

### Scenario 1: Global E-Commerce Platform

**Requirements:**
- Process orders from 50+ countries
- Orders must be processed exactly once
- Strict data residency (EU data stays in EU)
- High availability (99.99% SLA)

**Solution:**
```bash
# EU topic with storage policy
gcloud pubsub topics create eu-orders \
    --message-storage-policy-allowed-regions=europe-west1,europe-west4

# US topic
gcloud pubsub topics create us-orders \
    --message-storage-policy-allowed-regions=us-central1,us-east1

# Exactly-once subscriptions
gcloud pubsub subscriptions create eu-order-processor \
    --topic=eu-orders \
    --enable-exactly-once-delivery \
    --enable-message-ordering

gcloud pubsub subscriptions create us-order-processor \
    --topic=us-orders \
    --enable-exactly-once-delivery \
    --enable-message-ordering

# Global aggregation topic (multi-region)
gcloud pubsub topics create global-analytics

# Result:
# ✓ Data residency compliance
# ✓ Exactly-once processing
# ✓ High availability (multi-zonal)
# ✓ Global analytics capability
```

### Scenario 2: IoT with Cost Constraints

**Requirements:**
- 500,000 devices sending 1 KB every 30 seconds
- Regional deployment (Asia-Pacific)
- Budget: $200/month for messaging
- Latency: < 500ms acceptable

**Calculation:**
```
Standard Pub/Sub:
- Data: 500K devices × 1 KB × 2 messages/min × 60 min × 24 hr × 30 days
- = 500K × 1 KB × 2,880 = 1,440 GB/day = 43.2 TB/month
- Cost: 43,200 GB × $0.01/GB = $432/month ❌ (over budget)

Pub/Sub Lite (zonal):
- Same data: 43.2 TB/month
- Cost: 43,200 GB × $0.0025/GB = $108/month ✓
- Savings: $324/month (75% cheaper)
```

**Solution:**
```bash
# Use Pub/Sub Lite (zonal)
gcloud pubsub lite-topics create iot-telemetry \
    --location=asia-southeast1-a \
    --partitions=10 \
    --per-partition-bytes=50GiB \
    --throughput-reservation=100MiBps

gcloud pubsub lite-subscriptions create telemetry-processor \
    --location=asia-southeast1-a \
    --topic=iot-telemetry \
    --delivery-requirement=deliver-immediately

# Batch processing via Dataflow → BigQuery
# Result:
# ✓ Under budget ($108/month)
# ✓ Regional deployment (low latency)
# ✓ Scalable to 1M+ devices
```

### Scenario 3: Financial Compliance with Audit

**Requirements:**
- All messages must be auditable
- Replay capability (30 days)
- Encryption with customer keys
- No data exfiltration

**Solution:**
```bash
# 1. Create CMEK key
gcloud kms keys create financial-key \
    --keyring=finance-keyring \
    --location=us-central1 \
    --purpose=encryption

# 2. Create encrypted topic
gcloud pubsub topics create financial-transactions \
    --topic-encryption-key=projects/PROJECT/locations/us-central1/keyRings/finance-keyring/cryptoKeys/financial-key \
    --message-retention-duration=30d

# 3. VPC Service Controls
gcloud access-context-manager perimeters create finance_perimeter \
    --title="Finance Data Perimeter" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=pubsub.googleapis.com,bigquery.googleapis.com

# 4. Audit logging subscription
gcloud pubsub subscriptions create audit-log \
    --topic=financial-transactions \
    --bigquery-table=audit_dataset.transaction_log \
    --write-metadata

# Result:
# ✓ CMEK encryption (you control keys)
# ✓ 30-day replay with snapshots
# ✓ VPC-SC prevents exfiltration
# ✓ Audit trail in BigQuery
```

---

**End of Pub/Sub PCA Guide**
