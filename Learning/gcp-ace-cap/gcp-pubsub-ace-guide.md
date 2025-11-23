# Google Cloud Pub/Sub ACE Guide

## 1. Overview
Cloud Pub/Sub is an asynchronous messaging service that decouples services that produce events from services that process events.

### Key Concepts
- **Topic:** A named resource to which messages are sent by publishers.
- **Subscription:** A named resource representing the stream of messages from a single specific topic, to be delivered to the subscribing application.
- **Message:** The data that moves through the service.
- **Publisher:** An application that creates and sends messages to a topic.
- **Subscriber:** An application that receives messages from a subscription.

## 2. Managing Topics

### Creating a Topic
```bash
# Create a topic
gcloud pubsub topics create my-topic

# Create a topic with a schema (Avro/Protobuf)
gcloud pubsub schemas create my-schema \
    --type=AVRO \
    --definition='{"type": "record", "name": "User", "fields": [{"name": "name", "type": "string"}]}'

gcloud pubsub topics create my-topic-with-schema \
    --schema=my-schema \
    --message-encoding=JSON
```

### Managing Topics
```bash
# List topics
gcloud pubsub topics list

# Delete a topic
gcloud pubsub topics delete my-topic
```

## 3. Managing Subscriptions

### Subscription Types
1.  **Pull:** Subscriber pulls messages from Pub/Sub.
2.  **Push:** Pub/Sub pushes messages to a webhook endpoint (HTTPS).
3.  **BigQuery Export:** Writes messages directly to a BigQuery table.
4.  **Cloud Storage Export:** Writes messages directly to a GCS bucket.

### Creating Subscriptions
```bash
# Create a Pull subscription
gcloud pubsub subscriptions create my-sub --topic=my-topic

# Create a Push subscription
gcloud pubsub subscriptions create my-push-sub \
    --topic=my-topic \
    --push-endpoint=https://my-app.com/push-handler

# Create a BigQuery Export subscription
gcloud pubsub subscriptions create my-bq-sub \
    --topic=my-topic \
    --bigquery-table=my-project:my_dataset.my_table
```

### Managing Subscriptions
```bash
# List subscriptions
gcloud pubsub subscriptions list

# Pull messages (for testing)
gcloud pubsub subscriptions pull my-sub --auto-ack

# Delete a subscription
gcloud pubsub subscriptions delete my-sub
```

## 4. Publishing & Receiving Messages

### Publishing
```bash
# Publish a message
gcloud pubsub topics publish my-topic --message="Hello World"

# Publish with attributes
gcloud pubsub topics publish my-topic --message="Order Created" --attribute=priority=high
```

### Receiving (Pull)
- **Synchronous Pull:** Client waits for messages.
- **Streaming Pull:** Persistent connection for high throughput (recommended).

## 5. Message Ordering & Filtering

### Ordering
- Enabled per subscription.
- Requires an **Ordering Key** when publishing.
- Messages with the same key are delivered in order.

```bash
# Create an ordered subscription
gcloud pubsub subscriptions create my-ordered-sub \
    --topic=my-topic \
    --enable-message-ordering
```

### Filtering
- Filter messages at the subscription level to receive only a subset.
- Reduces cost and egress.

```bash
# Create a subscription with a filter
gcloud pubsub subscriptions create my-filtered-sub \
    --topic=my-topic \
    --message-filter='attributes.priority = "high"'
```

## 6. Security & IAM

### Roles
- **Pub/Sub Admin:** Full access.
- **Pub/Sub Editor:** Edit topics/subscriptions.
- **Pub/Sub Publisher:** Publish messages only.
- **Pub/Sub Subscriber:** Consume messages only.

### Service Accounts
- Push subscriptions require a service account to authenticate the push request (OIDC token).

## 7. Monitoring
- **`subscription/num_undelivered_messages`:** Backlog size.
- **`subscription/oldest_unacked_message_age`:** Latency/Stuck processing.
- **`topic/byte_cost`:** Cost estimation.

---

## 8. Message Acknowledgment and Retry

### Acknowledgment Flow

```
Publisher → Topic → Subscription → Subscriber
                                      ├─ Process Message
                                      ├─ Success → ACK
                                      └─ Failure → NACK
```

### ACK Deadline
- Default: 10 seconds
- Subscriber must acknowledge within this time
- Can be extended programmatically (modifyAckDeadline)

```bash
# Create subscription with custom ACK deadline
gcloud pubsub subscriptions create my-sub \
    --topic=my-topic \
    --ack-deadline=60
```

### Retry Policy
- Messages are redelivered if not acknowledged
- Exponential backoff between retries
- Maximum retry attempts configurable

```bash
# Create subscription with retry policy
gcloud pubsub subscriptions create my-sub \
    --topic=my-topic \
    --min-retry-delay=10s \
    --max-retry-delay=600s
```

---

## 9. Dead Letter Queues (DLQ)

Messages that fail repeatedly can be sent to a DLQ for investigation.

```bash
# Create DLQ topic
gcloud pubsub topics create my-topic-dlq

# Create main subscription with DLQ
gcloud pubsub subscriptions create my-sub \
    --topic=my-topic \
    --dead-letter-topic=my-topic-dlq \
    --max-delivery-attempts=5

# Grant Pub/Sub service account permission
gcloud pubsub topics add-iam-policy-binding my-topic-dlq \
    --member="serviceAccount:service-PROJECT_NUMBER@gcp-sa-pubsub.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# Subscribe to DLQ for inspection
gcloud pubsub subscriptions create dlq-sub \
    --topic=my-topic-dlq
```

---

## 10. Push Subscriptions

### Configuration

```bash
# Create push subscription with authentication
gcloud pubsub subscriptions create my-push-sub \
    --topic=my-topic \
    --push-endpoint=https://myapp.com/pubsub-push \
    --push-auth-service-account=my-sa@my-project.iam.gserviceaccount.com
```

### Endpoint Requirements
- Must be HTTPS
- Must return 2xx status for successful ACK
- Return 4xx for permanent failure (no retry)
- Return 5xx for temporary failure (retry with backoff)

### Example Push Handler (Python)

```python
from flask import Flask, request
import base64
import json

app = Flask(__name__)

@app.route('/pubsub-push', methods=['POST'])
def pubsub_push():
    envelope = request.get_json()
    
    # Verify request is from Pub/Sub
    if not envelope:
        return 'Bad Request', 400
    
    # Decode message
    message_data = base64.b64decode(envelope['message']['data']).decode('utf-8')
    attributes = envelope['message'].get('attributes', {})
    
    print(f"Received message: {message_data}")
    print(f"Attributes: {attributes}")
    
    # Process message
    try:
        process_message(message_data, attributes)
        return '', 204  # Success - message will be ACKed
    except Exception as e:
        print(f"Error: {e}")
        return '', 500  # Retry - message will be redelivered
```

---

## 11. Pull Subscriptions

### Synchronous Pull (Testing)

```bash
# Pull one message
gcloud pubsub subscriptions pull my-sub --auto-ack --limit=1

# Pull multiple messages without auto-ack
gcloud pubsub subscriptions pull my-sub --limit=10
```

### Streaming Pull (Production)

```python
from google.cloud import pubsub_v1
import time

project_id = "my-project"
subscription_id = "my-sub"

subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_id)

def callback(message):
    print(f"Received message: {message.data.decode('utf-8')}")
    print(f"Attributes: {message.attributes}")
    
    # Process message
    try:
        process_message(message.data, message.attributes)
        message.ack()  # Acknowledge successful processing
    except Exception as e:
        print(f"Error processing message: {e}")
        message.nack()  # Negative acknowledgment - will be redelivered

# Start streaming pull
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
print(f"Listening for messages on {subscription_path}...")

try:
    streaming_pull_future.result()  # Block indefinitely
except KeyboardInterrupt:
    streaming_pull_future.cancel()
```

---

## 12. Publishing Messages (Advanced)

### Batch Publishing for Performance

```python
from google.cloud import pubsub_v1
from concurrent import futures

project_id = "my-project"
topic_id = "my-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Configure batch settings
batch_settings = pubsub_v1.types.BatchSettings(
    max_messages=100,  # Batch up to 100 messages
    max_bytes=1024 * 1024,  # 1 MB
    max_latency=0.1,  # 100 ms
)
publisher = pubsub_v1.PublisherClient(batch_settings=batch_settings)

# Publish messages
publish_futures = []
for i in range(1000):
    data = f"Message {i}".encode('utf-8')
    future = publisher.publish(topic_path, data, origin="batch-publisher")
    publish_futures.append(future)

# Wait for all messages to publish
futures.wait(publish_futures, return_when=futures.ALL_COMPLETED)
print(f"Published {len(publish_futures)} messages")
```

### Publishing with Ordering Key

```python
from google.cloud import pubsub_v1

project_id = "my-project"
topic_id = "my-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Publish messages with ordering key
for i in range(10):
    data = f"Order event {i}".encode('utf-8')
    future = publisher.publish(
        topic_path,
        data,
        ordering_key="order-123"  # All messages with same key are ordered
    )
    print(f"Published message ID: {future.result()}")
```

### Publishing with Attributes

```python
from google.cloud import pubsub_v1

project_id = "my-project"
topic_id = "my-topic"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Publish with attributes
data = "Critical system alert".encode('utf-8')
future = publisher.publish(
    topic_path,
    data,
    priority="high",
    source="monitoring-system",
    timestamp=str(time.time())
)
message_id = future.result()
print(f"Published message {message_id}")
```

---

## 13. Message Filtering

### Filter Syntax

```
# Equality
attributes.priority = "high"

# Multiple conditions
attributes.priority = "high" AND attributes.region = "us-west"

# IN operator
attributes.status IN ("pending", "processing")

# NOT operator
NOT attributes.type = "test"

# Existence check
hasPrefix(attributes.name, "prod-")
```

### Creating Filtered Subscriptions

```bash
# Filter by priority
gcloud pubsub subscriptions create high-priority-sub \
    --topic=events \
    --message-filter='attributes.priority = "high"'

# Filter by region
gcloud pubsub subscriptions create us-events-sub \
    --topic=events \
    --message-filter='attributes.region = "us-west" OR attributes.region = "us-east"'

# Complex filter
gcloud pubsub subscriptions create production-alerts \
    --topic=alerts \
    --message-filter='attributes.environment = "production" AND attributes.severity IN ("critical", "high")'
```

---

## 14. Schemas

Enforce message structure using Avro or Protocol Buffers.

### Avro Schema

```bash
# Create Avro schema
cat > user_schema.avsc << EOF
{
  "type": "record",
  "name": "User",
  "fields": [
    {"name": "id", "type": "string"},
    {"name": "name", "type": "string"},
    {"name": "email", "type": "string"},
    {"name": "age", "type": "int"}
  ]
}
EOF

# Register schema
gcloud pubsub schemas create user-schema \
    --type=AVRO \
    --definition-file=user_schema.avsc

# Create topic with schema
gcloud pubsub topics create users \
    --schema=user-schema \
    --message-encoding=JSON
```

### Publishing to Schema-Validated Topic

```python
from google.cloud import pubsub_v1
import json

project_id = "my-project"
topic_id = "users"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_id)

# Valid message (conforms to schema)
user_data = {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30
}

data = json.dumps(user_data).encode('utf-8')
future = publisher.publish(topic_path, data)
print(f"Published: {future.result()}")

# Invalid message will be rejected
invalid_data = {"id": "456"}  # Missing required fields
data = json.dumps(invalid_data).encode('utf-8')
try:
    future = publisher.publish(topic_path, data)
    future.result()
except Exception as e:
    print(f"Rejected: {e}")
```

---

## 15. Pub/Sub Lite

Lower-cost option for high-throughput messaging within a single region/zone.

### Comparison

| Feature | Pub/Sub | Pub/Sub Lite |
|---------|---------|--------------|
| **Scope** | Global | Regional/Zonal |
| **Pricing** | $40/TiB | $2.50/TiB (zonal) |
| **Throughput** | Auto-scaling | Manual reservation |
| **Ordering** | Per key | Per partition |
| **Storage** | Unlimited | Configurable |

### Creating Pub/Sub Lite Resources

```bash
# Create Lite topic
gcloud pubsub lite-topics create my-lite-topic \
    --location=us-central1-a \
    --partitions=2 \
    --per-partition-bytes=30GiB

# Create Lite subscription
gcloud pubsub lite-subscriptions create my-lite-sub \
    --location=us-central1-a \
    --topic=my-lite-topic
```

---

## 16. Integration with Other Services

### Cloud Functions Trigger

```bash
# Deploy function triggered by Pub/Sub
gcloud functions deploy process_message \
    --runtime=python39 \
    --trigger-topic=my-topic \
    --entry-point=process_pubsub
```

```python
# main.py
import base64

def process_pubsub(event, context):
    """Triggered from a message on a Cloud Pub/Sub topic."""
    message_data = base64.b64decode(event['data']).decode('utf-8')
    attributes = event.get('attributes', {})
    
    print(f"Processing message: {message_data}")
    print(f"Attributes: {attributes}")
    
    # Your processing logic here
```

### Cloud Run with Pub/Sub

```bash
# Deploy Cloud Run service
gcloud run deploy my-service \
    --image=gcr.io/my-project/my-image \
    --platform=managed \
    --region=us-central1

# Create push subscription to Cloud Run
gcloud pubsub subscriptions create my-cloudrun-sub \
    --topic=my-topic \
    --push-endpoint=https://my-service-xxxx.run.app/pubsub \
    --push-auth-service-account=my-sa@my-project.iam.gserviceaccount.com
```

### Dataflow Pipeline

```python
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

options = PipelineOptions(streaming=True)

with beam.Pipeline(options=options) as pipeline:
    messages = (
        pipeline
        | 'Read from Pub/Sub' >> beam.io.ReadFromPubSub(
            subscription='projects/my-project/subscriptions/my-sub'
        )
        | 'Decode' >> beam.Map(lambda x: x.decode('utf-8'))
        | 'Process' >> beam.Map(lambda x: process_message(x))
        | 'Write to BigQuery' >> beam.io.WriteToBigQuery(
            table='my_project:dataset.table',
            schema='message:STRING,timestamp:TIMESTAMP',
            write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
        )
    )
```

---

## 17. Cost Optimization

### Pricing Model

**Message Delivery:**
- $0.04 per GB for first 100 GB/month
- $0.02 per GB for next 400 GB/month
- $0.01 per GB beyond 500 GB/month

**Message Storage:**
- $0.27 per GB/month (messages retained beyond ack deadline)

### Cost-Saving Tips

1. **Use message filtering**: Reduce unnecessary message delivery
2. **Set appropriate message retention**: Default is 7 days, adjust based on needs
3. **Use Pub/Sub Lite**: For high-volume, regional workloads
4. **Batch publishing**: Reduces API call overhead
5. **Acknowledge messages promptly**: Avoid storage charges

```bash
# Set message retention to 1 hour (minimum)
gcloud pubsub topics update my-topic \
    --message-retention-duration=1h

# Enable message storage policy
gcloud pubsub topics update my-topic \
    --message-storage-policy-allowed-regions=us-central1
```

---

## 18. Security Best Practices

### IAM Configuration

```bash
# Grant publish-only access
gcloud pubsub topics add-iam-policy-binding my-topic \
    --member="serviceAccount:publisher@my-project.iam.gserviceaccount.com" \
    --role="roles/pubsub.publisher"

# Grant subscribe-only access
gcloud pubsub subscriptions add-iam-policy-binding my-sub \
    --member="serviceAccount:subscriber@my-project.iam.gserviceaccount.com" \
    --role="roles/pubsub.subscriber"

# View IAM policies
gcloud pubsub topics get-iam-policy my-topic
```

### VPC Service Controls

Prevent data exfiltration by restricting Pub/Sub to authorized VPCs.

```bash
# Create service perimeter
gcloud access-context-manager perimeters create pubsub_perimeter \
    --title="Pub/Sub Perimeter" \
    --resources=projects/PROJECT_NUMBER \
    --restricted-services=pubsub.googleapis.com \
    --access-levels=corp_network
```

### Encryption

- **Default**: Google-managed encryption at rest
- **CMEK**: Customer-managed encryption keys via Cloud KMS

```bash
# Create topic with CMEK
gcloud pubsub topics create my-secure-topic \
    --topic-encryption-key=projects/my-project/locations/us-central1/keyRings/my-ring/cryptoKeys/my-key
```

---

## 19. Monitoring and Troubleshooting

### Key Metrics

```bash
# View metrics in Cloud Monitoring
# subscription/num_undelivered_messages - Backlog size
# subscription/oldest_unacked_message_age - Processing lag
# subscription/pull_request_count - Pull frequency
# topic/send_request_count - Publish rate
# subscription/ack_message_count - Processing rate
```

### Create Alerts

```bash
# Alert on high backlog
gcloud alpha monitoring policies create \
    --notification-channels=CHANNEL_ID \
    --display-name="High Pub/Sub Backlog" \
    --condition-display-name="Undelivered messages > 10000" \
    --condition-threshold-value=10000 \
    --condition-threshold-duration=300s \
    --condition-resource-type=pubsub_subscription \
    --condition-metric-type=pubsub.googleapis.com/subscription/num_undelivered_messages
```

### Common Issues

**Issue 1: Messages not being delivered**
```bash
# Check subscription exists
gcloud pubsub subscriptions describe my-sub

# Check IAM permissions
gcloud pubsub subscriptions get-iam-policy my-sub

# Check if subscriber is pulling
gcloud pubsub subscriptions pull my-sub --limit=1
```

**Issue 2: High message age (backlog)**
```bash
# Check oldest unacked message
gcloud pubsub subscriptions describe my-sub --format="value(oldestUnackedMessageAge)"

# Scale subscribers or increase ack deadline
gcloud pubsub subscriptions update my-sub --ack-deadline=120
```

**Issue 3: Messages going to DLQ**
```bash
# Pull from DLQ to inspect
gcloud pubsub subscriptions pull dlq-sub --limit=10

# Common causes:
# - Invalid message format
# - Processing errors in subscriber
# - Network issues
```

---

## 20. ACE Exam Tips

### Key Concepts

1. **Topics are global**, subscriptions are regional
2. **Multiple subscriptions** can read from same topic
3. **At-least-once delivery** guarantee (not exactly-once by default)
4. **Message ordering** requires ordering key
5. **Push subscriptions** require HTTPS endpoint
6. **Pull subscriptions** better for batch processing
7. **DLQ** for failed messages after max delivery attempts
8. **Schemas** enforce message structure
9. **Pub/Sub Lite** for cost-sensitive, regional workloads
10. **Filtering** reduces egress and processing costs

### Common Commands

```bash
# Create topic
gcloud pubsub topics create TOPIC_NAME

# Create pull subscription
gcloud pubsub subscriptions create SUB_NAME --topic=TOPIC_NAME

# Create push subscription
gcloud pubsub subscriptions create SUB_NAME \
    --topic=TOPIC_NAME \
    --push-endpoint=HTTPS_URL

# Publish message
gcloud pubsub topics publish TOPIC_NAME --message="DATA"

# Pull message
gcloud pubsub subscriptions pull SUB_NAME --auto-ack

# Delete resources
gcloud pubsub subscriptions delete SUB_NAME
gcloud pubsub topics delete TOPIC_NAME
```

### Decision Matrix

| Use Case | Recommendation |
|----------|----------------|
| **Asynchronous task queue** | Pull subscription + Cloud Functions |
| **Real-time data pipeline** | Push to Cloud Run or Dataflow |
| **Event-driven microservices** | Pub/Sub + Cloud Run |
| **Log aggregation** | Pub/Sub → BigQuery subscription |
| **High-throughput (regional)** | Pub/Sub Lite |
| **Ordered processing** | Enable ordering + ordering key |
| **Message validation** | Schema (Avro/Protobuf) |

### Best Practices

1. **Use exponential backoff** for retries
2. **Set appropriate ACK deadlines** (based on processing time)
3. **Monitor backlog metrics** (num_undelivered_messages)
4. **Use DLQ** for poison pill messages
5. **Enable message filtering** to reduce costs
6. **Use batch publishing** for high throughput
7. **Idempotent processing** (handle duplicate messages)
8. **Set message retention** appropriately
9. **Use IAM roles** for least privilege access
10. **Test with pull subscription** before deploying push

---

**End of Pub/Sub ACE Guide**
