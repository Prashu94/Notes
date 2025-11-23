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
