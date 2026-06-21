# Domain 1: Development with AWS Services (32%) — DVA-C02

Maps to **Task 1.1** (hosted applications), **Task 1.2** (Lambda), and **Task 1.3** (data stores).

**Official reference:** [DVA-C02 Exam Guide — Domain 1](https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html)

---

## Task 1.1: Develop Code for Applications Hosted on AWS

### Skill 1.1.1 — Architectural Patterns

| Pattern | Description | AWS implementation |
|---------|-------------|-------------------|
| **Monolithic** | Single deployable unit | Elastic Beanstalk, EC2 |
| **Microservices** | Independent services with own data | Lambda + API Gateway + DynamoDB per service |
| **Event-driven** | React to events, async processing | EventBridge, SQS, SNS, Lambda |
| **Choreography** | No central coordinator; services react independently | SNS fan-out, EventBridge rules |
| **Orchestration** | Central workflow engine coordinates steps | Step Functions |
| **Fan-out** | One event triggers multiple parallel processors | SNS → multiple SQS/Lambda |

**Exam tip:** "Decouple services with minimum coupling" → event-driven with SQS or EventBridge, not direct HTTP calls.

### Skill 1.1.2–1.1.4 — Stateful/Stateless, Coupling, Sync/Async

| Concept | Stateful | Stateless |
|---------|----------|-----------|
| Session data | Stored on server | Stored in ElastiCache/DynamoDB/client |
| Scaling | Sticky sessions or dedicated instances | Any instance handles any request |
| Failure | Session lost if instance dies | No session loss |

| Coupling | Tight | Loose |
|----------|-------|-------|
| Communication | Direct API calls, shared DB | Messages, events, separate data stores |
| Failure impact | Cascading failures | Isolated failures |
| AWS pattern | Monolith on EC2 | SQS between Lambda functions |

| Sync | Async |
|------|-------|
| Caller waits for response | Fire-and-forget |
| API Gateway → Lambda (sync) | S3 event → Lambda (async) |
| Lower latency for user | Better resilience and scaling |

### Skill 1.1.5 — Fault-Tolerant Application Code

Implement in your programming language:
- **Idempotent handlers** — same event processed twice produces same result
- **Graceful degradation** — return partial results when dependencies fail
- **Health checks** — `/health` endpoint for load balancer
- **Timeouts** on all external calls

### Skill 1.1.6 — APIs (API Gateway)

Key developer tasks:
- **Request/response transformations** — mapping templates (VTL) or Lambda proxy
- **Validation** — request validator on API Gateway models
- **Status code overrides** — integration response mapping
- **CORS** — enable on API Gateway or return CORS headers from Lambda

See [API Gateway Guide](aws-api-gateway-dva-c02-guide.md).

### Skill 1.1.7 — Unit Tests (SAM)

```bash
# Test Lambda locally with SAM
sam local invoke MyFunction -e events/order.json

# Generate sample events
sam local generate-event apigateway aws-proxy > events/api.json
```

### Skill 1.1.8 — Messaging in Code

See [Messaging Guide](aws-messaging-dva-c02-guide.md) for SQS, SNS, EventBridge SDK patterns.

### Skill 1.1.9 — AWS SDK Integration

```python
import boto3

# Boto3 uses default credential chain (Lambda execution role on Lambda)
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Pagination for large result sets
paginator = s3.get_paginator('list_objects_v2')
for page in paginator.paginate(Bucket='my-bucket'):
    for obj in page.get('Contents', []):
        process(obj)
```

**SDK best practices:**
- Reuse clients outside handler (warm start optimization)
- Use resource API for higher-level operations
- Handle `ClientError` exceptions with specific error codes
- Enable retries (default adaptive retry mode)

### Skill 1.1.10 — Streaming Data

| Service | Use case | Developer pattern |
|---------|----------|-------------------|
| **Kinesis Data Streams** | Real-time ingestion, custom processing | Lambda event source mapping with batch size |
| **Kinesis Firehose** | Near-real-time delivery to S3/Redshift | PutRecord API or agent |
| **DynamoDB Streams** | React to table changes | Lambda trigger on stream events |

### Skill 1.1.11 — Amazon Q Developer

- AI coding assistant integrated in IDE
- Generate unit tests, explain code, suggest AWS SDK usage
- Exam awareness: know it exists and assists with development tasks

### Skill 1.1.12 — EventBridge Event-Driven Patterns

```python
# Put custom event on default or custom event bus
events = boto3.client('events')
events.put_events(Entries=[{
    'Source': 'myapp.orders',
    'DetailType': 'Order Placed',
    'Detail': json.dumps({'orderId': '123', 'amount': 99.99}),
    'EventBusName': 'default'
}])
```

Rules match on `source`, `detail-type`, and `detail` content → route to Lambda, SQS, Step Functions, etc.

### Skill 1.1.13 — Resilient Third-Party Integrations

- **Retry with exponential backoff** — for transient failures (429, 503)
- **Circuit breaker** — stop calling failing service to prevent cascade
- **Timeouts** — don't block indefinitely
- **Fallback responses** — cached data or degraded functionality

---

## Task 1.2: Develop Code for AWS Lambda

See [Lambda Guide](aws-lambda-dva-c02-guide.md) for full coverage.

### Skill Summary

| Skill | Key points |
|-------|-----------|
| 1.2.1 VPC access | Private subnets + security groups + NAT/endpoints for AWS API |
| 1.2.2 Configuration | Memory, timeout, env vars, layers, triggers, destinations |
| 1.2.3 Event lifecycle | Sync vs async retry; DLQ; partial batch failures for streams |
| 1.2.4 Testing | SAM local, test events, integration tests |
| 1.2.5 Integration | SDK calls using execution role permissions |
| 1.2.6 Performance | Right-size memory; minimize cold starts; reuse connections |
| 1.2.7 Real-time processing | Kinesis/DynamoDB Streams triggers; batch processing |

---

## Task 1.3: Use Data Stores in Application Development

See [DynamoDB Guide](aws-dynamodb-dva-c02-guide.md).

### Skill Summary

| Skill | Key points |
|-------|-----------|
| 1.3.1 High-cardinality keys | UUID, composite keys — avoid hot partitions |
| 1.3.2 Consistency | Strongly vs eventually consistent reads |
| 1.3.3 Query vs Scan | Query = efficient; Scan = expensive, avoid in prod |
| 1.3.4 Keys and indexes | PK, SK, GSI (different PK), LSI (same PK, different SK) |
| 1.3.5 Serialization | JSON, DynamoDB type annotations in SDK |
| 1.3.6 Manage data stores | CRUD, batch operations, transactions |
| 1.3.7 Data lifecycles | TTL attribute for automatic expiry |
| 1.3.8 Caching | ElastiCache, DAX, API Gateway caching |
| 1.3.9 Specialized stores | OpenSearch for full-text search and log analytics |

### DynamoDB TTL Example

```python
import time
# Set expiry epoch timestamp — DynamoDB deletes item automatically (within 48 hrs)
table.put_item(Item={
    'sessionId': 'abc123',
    'data': {...},
    'ttl': int(time.time()) + 3600  # Expire in 1 hour
})
```

---

## Practice Focus

After studying this domain, you should be able to:

1. Choose sync vs async integration for a given scenario
2. Configure Lambda memory, timeout, VPC, DLQ, and destinations
3. Write DynamoDB queries using partition key + GSI
4. Implement SQS message processing with proper delete/visibility timeout
5. Explain Cognito → API Gateway → Lambda auth flow
6. Use SAM CLI for local testing

**Next:** [Domain 2 — Security](domain-02-security.md) | [Lambda Guide](aws-lambda-dva-c02-guide.md)
