# DVA-C02 Concepts Deep Dive

Developer-focused concepts that appear repeatedly on the AWS Certified Developer – Associate exam. Each section explains the concept, how it applies in code, and common exam traps.

---

## Table of Contents

1. [Event-Driven Architecture Patterns](#event-driven-architecture-patterns)
2. [Lambda Execution Model](#lambda-execution-model)
3. [IAM Roles for Developers](#iam-roles-for-developers)
4. [DynamoDB for Application Developers](#dynamodb-for-application-developers)
5. [API Gateway Integration Patterns](#api-gateway-integration-patterns)
6. [Messaging Patterns (SQS, SNS, EventBridge)](#messaging-patterns)
7. [Cognito Authentication Flows](#cognito-authentication-flows)
8. [Encryption in Application Code](#encryption-in-application-code)
9. [CI/CD and Deployment Strategies](#cicd-and-deployment-strategies)
10. [Observability Stack](#observability-stack)
11. [Error Handling and Resilience Patterns](#error-handling-and-resilience-patterns)

---

## Event-Driven Architecture Patterns

### Pattern Comparison

| Pattern | Description | AWS Services | Coupling |
|---------|-------------|--------------|----------|
| **Monolithic** | Single deployable unit | EC2, Elastic Beanstalk | Tight |
| **Microservices** | Independent services, own data | Lambda, ECS, API Gateway | Loose |
| **Event-driven** | Services react to events | EventBridge, SQS, SNS, Lambda | Very loose |
| **Choreography** | Services react independently, no central coordinator | SNS fan-out, EventBridge rules | Loose |
| **Orchestration** | Central coordinator manages workflow | Step Functions | Controlled |

### When to Use Event-Driven

- **Decouple** producers from consumers (order service doesn't need to know about email, inventory, analytics)
- **Handle burst traffic** (queue absorbs spikes)
- **Retry failed processing** (DLQ captures failures)
- **Async workflows** (user doesn't wait for all downstream processing)

### Fan-Out Pattern (High Exam Value)

```
S3 Upload → SNS Topic → SQS Queue A (resize images)
                      → SQS Queue B (update metadata)
                      → Lambda (virus scan)
```

SNS delivers to **multiple subscribers**; each SQS queue gets its own copy. Consumers process independently.

---

## Lambda Execution Model

### Lifecycle

```
Event → [Init (cold start)] → Handler → [Freeze/Reuse] → [Destroy after idle]
         ↓ only on cold start
    Download code, start runtime, run init code outside handler
```

### Key Configuration (Exam Essentials)

| Setting | Default | Max | Impact |
|---------|---------|-----|--------|
| Memory | 128 MB | 10,240 MB | Also scales CPU proportionally |
| Timeout | 3 sec | 900 sec (15 min) | Must be less than API Gateway (29 sec) for sync |
| Ephemeral storage | 512 MB | 10,240 MB | `/tmp` directory |
| Concurrent executions | Account: 1,000 (soft) | Can request increase | Reserved concurrency limits function |
| Package size | 50 MB (zipped), 250 MB (unzipped) | Use S3 for larger | Layers add to limit |

### Cold Start Mitigation

| Technique | How |
|-----------|-----|
| Provisioned Concurrency | Pre-warm execution environments |
| Smaller deployment package | Less to download |
| Avoid VPC unless needed | VPC adds ENI setup time |
| Choose faster runtime | Node.js/Python faster than Java/.NET for cold start |
| Keep handler outside VPC | Only put in VPC if accessing private resources |

### Lambda + VPC

When Lambda needs to access **private resources** (RDS in private subnet, ElastiCache, internal APIs):

1. Attach Lambda to **private subnets**
2. Lambda creates **ENIs** in those subnets (uses Hyperplane for scaling since 2019)
3. Needs **NAT Gateway** or **VPC endpoints** for internet/AWS API access
4. Security group on Lambda ENI must allow traffic to target

> **Exam trap:** "Lambda can't connect to RDS" → Check VPC config, security groups, and subnet routing — not IAM alone.

### Destinations vs DLQ

| Feature | Dead Letter Queue (DLQ) | Destinations |
|---------|------------------------|--------------|
| **When** | Sync AND async failures | Async invocations only |
| **Success routing** | No | Yes — can route successful results too |
| **Targets** | SQS, SNS | SQS, SNS, Lambda, EventBridge |
| **Use case** | Capture failures for retry | Full async invocation routing |

---

## IAM Roles for Developers

### Three Roles You'll Configure

| Role | Attached to | Purpose |
|------|------------|---------|
| **Lambda execution role** | Lambda function | Permissions the function needs at runtime (DynamoDB, S3, logs) |
| **API Gateway execution role** | API Gateway | Call AWS services on your behalf (invoke Lambda, write CloudWatch) |
| **CodeBuild/CodePipeline role** | CI/CD services | Deploy resources, access S3 artifacts, run builds |

### Credential Chain in Code

```python
# AWS SDK automatically uses credential chain:
# 1. Environment variables (AWS_ACCESS_KEY_ID, etc.)
# 2. Shared credentials file (~/.aws/credentials)
# 3. IAM role (EC2 instance metadata, Lambda execution role, ECS task role)
# 4. Assume role

# On Lambda — NO credentials needed; SDK uses execution role automatically
import boto3
dynamodb = boto3.resource('dynamodb')  # Uses Lambda execution role
```

### AssumeRole Pattern

```python
# Cross-account or temporary elevated access
sts = boto3.client('sts')
response = sts.assume_role(
    RoleArn='arn:aws:iam::123456789012:role/CrossAccountRole',
    RoleSessionName='my-app-session'
)
credentials = response['Credentials']
# Use temporary credentials for subsequent calls
```

> **Exam trap:** Never hardcode access keys in Lambda, EC2 user data, or source code. Always use IAM roles.

---

## DynamoDB for Application Developers

### SDK Operations

| Operation | API call | When to use |
|-----------|----------|-------------|
| Single item read | `get_item` | Know exact key |
| Query | `query` | Same partition key, optional sort key condition |
| Scan | `scan` | Avoid — reads entire table |
| Write | `put_item`, `update_item`, `delete_item` | CRUD |
| Batch | `batch_get_item`, `batch_write_item` | Up to 25 items, 16 MB |
| Conditional write | `ConditionExpression` | Optimistic locking, prevent overwrites |
| Transaction | `transact_write_items` | All-or-nothing across up to 25 items |

### Consistency in Code

```python
# Eventually consistent (default) — half the RCU cost
response = table.get_item(Key={'PK': 'user123'})

# Strongly consistent — use when you must read latest write
response = table.get_item(
    Key={'PK': 'user123'},
    ConsistentRead=True
)
```

### Optimistic Locking Pattern

```python
# Add version attribute; condition prevents lost updates
table.update_item(
    Key={'PK': 'user123'},
    UpdateExpression='SET balance = :new_balance, version = :new_version',
    ConditionExpression='version = :current_version',
    ExpressionAttributeValues={
        ':new_balance': 100,
        ':new_version': 2,
        ':current_version': 1
    }
)
# ConditionalCheckFailedException if another writer updated first
```

### DAX (Developer Awareness)

- In-memory cache **in front of** DynamoDB
- Microsecond read latency
- **Write-through** cache — writes go to DynamoDB then cache
- Application code uses DAX client instead of DynamoDB client
- Use for **read-heavy** workloads with eventually consistent reads acceptable from cache

---

## API Gateway Integration Patterns

### Integration Types

| Type | How it works | Use case |
|------|-------------|----------|
| **Lambda proxy** | Passes full request to Lambda; Lambda returns API response format | Most common — flexible |
| **Lambda non-proxy** | API Gateway maps request/response | Legacy, mapping templates |
| **HTTP proxy** | Forwards to HTTP endpoint | Existing REST backend |
| **AWS service** | Direct integration (S3, DynamoDB, Step Functions) | Simple CRUD without Lambda |
| **Mock** | Returns static response | CORS preflight, testing |

### Lambda Proxy Integration Response Format

```python
def lambda_handler(event, context):
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': 'Hello'})
    }
```

### Stages and Deployments

```
API → Deployment (snapshot) → Stage (dev, prod, v1)
                              → Stage variables ($stageVar.lambdaAlias)
                              → Custom domain mapping
```

- **Deploy** creates an immutable snapshot
- **Stage** is a named pointer to a deployment (with optional stage variables)
- Changes don't take effect until you **deploy to a stage**

### Authorizers

| Type | Validates | Token source |
|------|-----------|-------------|
| **IAM** | AWS Signature V4 | Authorization header |
| **Cognito User Pool** | JWT from Cognito | Authorization header (Bearer) |
| **Lambda authorizer** | Custom logic | Token authorizer or request authorizer |

---

## Messaging Patterns

### SQS Essentials for Developers

```python
# Receive with long polling (reduces empty responses)
response = sqs.receive_message(
    QueueUrl=queue_url,
    MaxNumberOfMessages=10,
    WaitTimeSeconds=20,  # Long polling
    VisibilityTimeout=60
)

# Process message, then delete (or it reappears after visibility timeout)
sqs.delete_message(
    QueueUrl=queue_url,
    ReceiptHandle=message['ReceiptHandle']
)
```

| Setting | Default | Purpose |
|---------|---------|---------|
| Visibility timeout | 30 sec | Hide message after read; must exceed processing time |
| Message retention | 4 days | Max 14 days |
| Long polling | 0 sec | Set WaitTimeSeconds to 1–20 |
| Max message size | 256 KB | Use Extended Client Library + S3 for larger |

### SNS Filter Policies

```json
{
  "event_type": ["order_placed"],
  "amount": [{"numeric": [">=", 100]}]
}
```

Only matching messages delivered to subscription — reduces unnecessary Lambda invocations.

### EventBridge vs SNS vs SQS

| | EventBridge | SNS | SQS |
|--|------------|-----|-----|
| **Pattern** | Event bus with rules | Pub/sub fan-out | Queue (competing consumers) |
| **Consumers** | 100+ targets per rule | Many subscribers | One consumer per message |
| **Ordering** | No guarantee | FIFO topic option | FIFO queue option |
| **Retry** | Target retry + DLQ | Subscription retry | Visibility timeout + DLQ |
| **Schedule** | Built-in cron/rate | No | No |
| **Content filtering** | Event pattern matching | Filter policies | Message attributes |

---

## Cognito Authentication Flows

### User Pool Flow (Authentication)

```
1. User signs in → Cognito User Pool
2. Returns JWT tokens: ID token, Access token, Refresh token
3. Client sends Access token to API Gateway (Cognito authorizer)
4. API Gateway validates JWT signature against User Pool
5. Request forwarded to Lambda with claims in request context
```

### Identity Pool Flow (AWS Credentials)

```
1. User authenticated (User Pool, social login, or guest)
2. Exchange token with Identity Pool
3. Identity Pool returns temporary AWS credentials via STS
4. Client uses credentials to call AWS APIs directly (S3 upload, etc.)
```

### JWT Claims in Lambda (via API Gateway)

```python
def lambda_handler(event, context):
    claims = event['requestContext']['authorizer']['claims']
    user_id = claims['sub']
    email = claims['email']
```

---

## Encryption in Application Code

### At Rest

| Method | Developer action |
|--------|-----------------|
| **SSE-S3** | Set `ServerSideEncryption='AES256'` on S3 upload (or bucket default) |
| **SSE-KMS** | Set `ServerSideEncryption='aws:kms'`, specify KeyId; handle KMS throttling |
| **Client-side** | Encrypt before upload; you manage keys entirely |
| **DynamoDB** | Enable encryption at table level (AWS owned, AWS managed, or CMK) |
| **Lambda env vars** | Enable KMS encryption on function configuration |

### In Transit

- Always use **HTTPS** for API calls
- SDKs use TLS by default
- `aws:SecureTransport` condition in IAM policies to enforce

### Secrets in Code — Never Do This

```python
# ❌ WRONG — hardcoded secret
db_password = "my-secret-password"

# ✅ CORRECT — Secrets Manager
import boto3
client = boto3.client('secretsmanager')
secret = client.get_secret_value(SecretId='prod/db/password')
password = json.loads(secret['SecretString'])['password']

# ✅ CORRECT — Parameter Store (SecureString)
ssm = boto3.client('ssm')
password = ssm.get_parameter(Name='/prod/db/password', WithDecryption=True)['Parameter']['Value']
```

---

## CI/CD and Deployment Strategies

### AWS SAM Workflow

```bash
sam build                    # Build Lambda layers and dependencies
sam local invoke             # Test locally
sam local start-api          # Local API Gateway + Lambda
sam deploy --guided          # Deploy via CloudFormation
sam logs -n MyFunction       # Tail CloudWatch logs
```

### Deployment Strategies

| Strategy | Downtime | Rollback | Services |
|----------|----------|----------|----------|
| **In-place (rolling)** | Minimal | Manual redeploy | CodeDeploy EC2, ECS |
| **Blue/Green** | Zero | Switch traffic back | CodeDeploy, Lambda aliases |
| **Canary** | Zero | Stop traffic shift | CodeDeploy, Lambda weighted aliases |
| **Linear** | Zero | Gradual rollback | CodeDeploy |
| **All-at-once** | Brief | Redeploy previous | Lambda publish version |

### Lambda Deployment with Aliases

```
$LATEST (development) → publish → Version 1, Version 2
                                      ↓
                              Alias "prod" → Version 2 (100%)
                              Alias "prod" → Version 1 (10%) + Version 2 (90%)  ← canary
```

### CodePipeline Stages (Typical)

```
Source (CodeCommit/GitHub) → Build (CodeBuild) → Deploy (CodeDeploy/CloudFormation)
                                    ↓
                              Run tests, package artifacts
```

---

## Observability Stack

### Three Pillars

| Pillar | AWS Service | Developer action |
|--------|------------|------------------|
| **Logs** | CloudWatch Logs | `print()` / structured JSON logging; log groups per function |
| **Metrics** | CloudWatch Metrics | Built-in Lambda metrics; custom metrics via `put_metric_data` or EMF |
| **Traces** | X-Ray | Enable active tracing; annotate subsegments in code |

### Structured Logging

```python
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        'event': 'order_processed',
        'order_id': event['orderId'],
        'user_id': event['userId'],
        'request_id': context.aws_request_id
    }))
```

### X-Ray in Code

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('process_order')
def process_order(order_id):
    # Subsegment appears in X-Ray service map
    ...
```

### CloudWatch Embedded Metric Format (EMF)

```python
# Logs automatically become custom metrics — no separate PutMetricData API call
print(json.dumps({
    "_aws": {
        "Timestamp": int(time.time() * 1000),
        "CloudWatchMetrics": [{
            "Namespace": "MyApp",
            "Metrics": [{"Name": "OrdersProcessed", "Unit": "Count"}],
            "Dimensions": [["Environment"]]
        }]
    },
    "OrdersProcessed": 1,
    "Environment": "prod"
}))
```

---

## Error Handling and Resilience Patterns

### Retry with Exponential Backoff

```python
import time
import random

def retry_with_backoff(func, max_retries=5):
    for attempt in range(max_retries):
        try:
            return func()
        except ClientError as e:
            if e.response['Error']['Code'] not in ('ThrottlingException', 'ServiceUnavailable'):
                raise
            wait = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(wait)
    raise Exception("Max retries exceeded")
```

### Circuit Breaker (Skill 1.1.13)

```
Closed (normal) → failures exceed threshold → Open (fail fast)
Open → timeout expires → Half-Open (test one request)
Half-Open → success → Closed | failure → Open
```

Use when integrating with third-party APIs that may be unavailable — prevents cascade failures.

### Lambda Error Handling

| Invocation type | On error | Developer action |
|--------------|----------|-----------------|
| Sync (API Gateway) | Returns 502 to client | Catch exceptions; return proper statusCode |
| Async (S3, SNS, EventBridge) | Retries 2 times, then DLQ/destination | Configure DLQ; make handler idempotent |
| Stream (DynamoDB, Kinesis) | Retries until data expires | Handle batchItemFailures for partial batch response |

---

## Related Guides

- [README — Master Study Guide](README.md)
- [Lambda Guide](aws-lambda-dva-c02-guide.md)
- [CI/CD Guide](aws-cicd-dva-c02-guide.md)
