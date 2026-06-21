# AWS Messaging Services — DVA-C02 Developer Guide

SQS, SNS, EventBridge, and Step Functions — core integration services for event-driven applications.

---

## Amazon SQS

### Standard vs FIFO

| | Standard | FIFO |
|--|----------|------|
| Throughput | Unlimited | 3,000 msg/sec (30,000 with batching) |
| Ordering | Best-effort | Strict FIFO |
| Delivery | At-least-once (duplicates possible) | Exactly-once processing |
| Name | Any | Must end in `.fifo` |
| Use case | High throughput, order not critical | Financial, order processing |

### Key Settings

| Setting | Default | Max | Developer note |
|---------|---------|-----|----------------|
| Visibility timeout | 30 sec | 12 hours | Must exceed Lambda processing time |
| Message retention | 4 days | 14 days | |
| Long polling | 0 sec | 20 sec | Set WaitTimeSeconds=20 |
| Max message size | 256 KB | 256 KB | Extended client library + S3 for larger |
| Delay queue | 0 sec | 15 min | Delay all messages |

### Developer Pattern

```python
# Send
sqs.send_message(QueueUrl=url, MessageBody=json.dumps({'orderId': '123'}))

# Receive (long polling)
msgs = sqs.receive_message(QueueUrl=url, WaitTimeSeconds=20, MaxNumberOfMessages=10)
for msg in msgs.get('Messages', []):
    process(json.loads(msg['Body']))
    sqs.delete_message(QueueUrl=url, ReceiptHandle=msg['ReceiptHandle'])
```

### Dead Letter Queue (DLQ)

- After `maxReceiveCount` failed receives → message moves to DLQ
- Configure redrive policy on source queue
- **Exam:** "Capture failed messages for analysis" → DLQ

### Lambda + SQS

- Event source mapping polls queue automatically
- Batch size 1–10; partial batch failure for reporting failed items
- Visibility timeout ≥ 6 × Lambda timeout (recommended)
- Lambda deletes messages on successful batch completion

---

## Amazon SNS

### Pub/Sub Fan-Out

```
Publisher → SNS Topic → Subscription 1 (SQS Queue → Lambda)
                      → Subscription 2 (Lambda)
                      → Subscription 3 (Email)
                      → Subscription 4 (HTTP endpoint)
```

### Message Filtering

```json
{
  "event_type": ["order_placed"],
  "amount": [{"numeric": [">=", 100]}]
}
```

Only matching messages delivered — reduces unnecessary Lambda invocations.

### SNS + SQS Fan-Out Pattern (Exam Favorite)

```
S3 → SNS → SQS Queue A → Lambda (resize)
         → SQS Queue B → Lambda (metadata)
```

**Why SQS between SNS and Lambda?**
- Buffering and retry per consumer
- Independent scaling and failure isolation
- DLQ per queue

### FIFO Topics
- Pair with FIFO queues for ordered fan-out
- Content-based deduplication option

---

## Amazon EventBridge

### Event Bus Architecture

```
Event Sources → Event Bus → Rules (pattern matching) → Targets
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                 Lambda        SQS      Step Functions
```

### Rule Pattern Matching

```json
{
  "source": ["myapp.orders"],
  "detail-type": ["Order Placed"],
  "detail": {
    "amount": [{"numeric": [">=", 100]}]
  }
}
```

### Scheduled Rules

```json
{
  "schedule": "rate(5 minutes)"
}
// or
{
  "schedule": "cron(0 12 * * ? *)"
}
```

**EventBridge Scheduler** — one-time and recurring schedules with more flexibility than CloudWatch Events.

### PutEvents (Custom Events)

```python
events.put_events(Entries=[{
    'Source': 'com.myapp',
    'DetailType': 'Order Placed',
    'Detail': json.dumps({'orderId': '123', 'amount': 99.99}),
    'EventBusName': 'default'
}])
```

### EventBridge vs SNS vs SQS

| Need | Service |
|------|---------|
| Competing consumers, buffer | SQS |
| Fan-out to many subscribers | SNS |
| Content-based routing, schedules, SaaS events | EventBridge |
| Simple point-to-point async | SQS |
| Cross-account event routing | EventBridge (resource policy on bus) |

---

## AWS Step Functions

### Workflow Types

| Type | Use case | Duration |
|------|----------|----------|
| **Standard** | Long-running, auditable, exactly-once | Up to 1 year |
| **Express** | High volume, short duration | Up to 5 minutes |

### State Types (Developer Awareness)

- **Task** — invoke Lambda, activity, AWS service
- **Choice** — conditional branching
- **Parallel** — concurrent branches
- **Wait** — delay
- **Succeed/Fail** — terminal states
- **Map** — iterate over array

### Orchestration vs Choreography

| | Choreography | Orchestration |
|--|-------------|---------------|
| Coordinator | None (EventBridge/SNS) | Step Functions |
| Coupling | Loose | Centralized logic |
| Visibility | Harder to trace | Visual workflow |
| Use when | Simple event reactions | Complex multi-step workflows |

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Decouple order and inventory services | SQS between them |
| Fan-out S3 upload to multiple processors | SNS → multiple SQS → Lambda |
| Exactly-once order processing | SQS FIFO queue |
| Schedule Lambda every hour | EventBridge scheduled rule |
| Route events by content | EventBridge rule pattern |
| Failed messages after 3 retries | SQS DLQ with maxReceiveCount=3 |
| Multi-step workflow with branching | Step Functions |
| Buffer burst traffic | SQS queue |

---

## Related Guides

- [Lambda Guide](aws-lambda-dva-c02-guide.md)
- [Concepts Deep Dive](CONCEPTS-DEEP-DIVE.md#messaging-patterns)
