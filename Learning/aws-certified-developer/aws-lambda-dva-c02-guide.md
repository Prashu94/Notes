# AWS Lambda — DVA-C02 Developer Guide

The most heavily tested service on the Developer Associate exam. Focus on **configuration, event sources, error handling, VPC access, and deployment**.

**Official docs:** [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

---

## Table of Contents

1. [Function Configuration](#function-configuration)
2. [Execution Role](#execution-role)
3. [Event Sources and Invocations](#event-sources-and-invocations)
4. [Error Handling and Retries](#error-handling-and-retries)
5. [VPC Configuration](#vpc-configuration)
6. [Layers and Extensions](#layers-and-extensions)
7. [Environment Variables](#environment-variables)
8. [Versions, Aliases, and Deployment](#versions-aliases-and-deployment)
9. [Performance Optimization](#performance-optimization)
10. [Exam Scenarios](#exam-scenarios)

---

## Function Configuration

| Setting | Default | Maximum | Notes |
|---------|---------|---------|-------|
| Memory | 128 MB | 10,240 MB | CPU scales proportionally |
| Timeout | 3 sec | 900 sec (15 min) | Must be < 29 sec for API Gateway sync |
| Ephemeral storage (`/tmp`) | 512 MB | 10,240 MB | `/tmp` only |
| Concurrent executions | 1,000/account (soft) | Request increase | Reserved concurrency caps function |
| Deployment package | — | 50 MB zip / 250 MB unzipped | Use S3 or container for larger |
| Container image | — | 10 GB | Stored in ECR |
| Layers | — | 5 layers, 250 MB total unzipped | Shared dependencies |
| Env variables | — | 4 KB total | Use KMS encryption or Secrets Manager for secrets |

### Handler Signature

```python
def lambda_handler(event, context):
    # event: dict — trigger-specific payload
    # context: LambdaContext — runtime info
    print(f"Request ID: {context.aws_request_id}")
    print(f"Remaining time: {context.get_remaining_time_in_millis()}ms")
    return {"statusCode": 200, "body": "OK"}
```

---

## Execution Role

Every Lambda function needs an **execution role** (IAM role with trust policy for `lambda.amazonaws.com`).

**Minimum permissions:**
```json
{
  "Effect": "Allow",
  "Action": [
    "logs:CreateLogGroup",
    "logs:CreateLogStream",
    "logs:PutLogEvents"
  ],
  "Resource": "arn:aws:logs:*:*:*"
}
```

**Add permissions** for services your code calls (DynamoDB, S3, SQS, etc.).

> **Exam trap:** Never use IAM user access keys in Lambda code. The SDK automatically uses the execution role.

---

## Event Sources and Invocations

### Invocation Types

| Type | Trigger examples | On failure | Response |
|------|-----------------|------------|----------|
| **Synchronous** | API Gateway, ALB, CLI invoke | Error returned to caller | Waits for response |
| **Asynchronous** | S3, SNS, EventBridge, async invoke | Retries 2x, then DLQ/destination | 202 Accepted |
| **Poll-based** | SQS, Kinesis, DynamoDB Streams | Retry per source rules | Batch processing |

### Common Event Sources

| Source | Event type | Key config |
|--------|-----------|------------|
| API Gateway | Sync | Proxy integration returns API response |
| S3 | Async | `s3:ObjectCreated:*` events |
| SQS | Poll | Batch size 1–10, visibility timeout > function timeout |
| SNS | Async | One Lambda per message |
| EventBridge | Async | Rule pattern matching |
| DynamoDB Streams | Poll | Batch, starting position (LATEST/TRIM_HORIZON) |
| Kinesis | Poll | Batch size, parallelization factor |
| CloudWatch Events/Scheduler | Async | Cron or rate expression |

### SQS Event Source Mapping

```python
def lambda_handler(event, context):
    for record in event['Records']:
        body = json.loads(record['body'])
        process_message(body)
    # Auto-deletes messages on successful completion
    # Failed batch → messages return to queue after visibility timeout
```

Configure **partial batch failure** for Kinesis/DynamoDB Streams:
```python
return {'batchItemFailures': [{'itemIdentifier': record['messageId']}]}
```

---

## Error Handling and Retries

### Synchronous Invocations
- Exception → error returned to caller (502 from API Gateway)
- **You must catch exceptions** and return proper HTTP status codes

### Asynchronous Invocations
- Retry **2 times** with backoff
- Then route to **DLQ** (SQS/SNS) or **OnFailure destination**
- Make handlers **idempotent** — same event processed twice = same result

### Destinations (Async Only)

| Destination | Purpose |
|-------------|---------|
| OnSuccess | Route successful results to SQS/SNS/Lambda/EventBridge |
| OnFailure | Route failed events after retries (alternative to DLQ) |

### Dead Letter Queue (DLQ)

- Works for **async AND poll-based** invocations
- Target: SQS queue or SNS topic
- Requires IAM permission on execution role for DLQ
- Exam: "Capture failed Lambda invocations" → configure DLQ

---

## VPC Configuration

**When needed:** Access RDS, ElastiCache, private APIs in VPC.

```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    VpcConfig:
      SecurityGroupIds:
        - !Ref LambdaSecurityGroup
      SubnetIds:
        - !Ref PrivateSubnet1
        - !Ref PrivateSubnet2
```

**Requirements:**
- Private subnets (with NAT Gateway or VPC endpoints for AWS API calls)
- Security group allowing outbound to target + AWS services
- IAM: `ec2:CreateNetworkInterface`, `ec2:DescribeNetworkInterfaces`, `ec2:DeleteNetworkInterface`
- **Cold start impact:** ENI setup adds latency (Hyperplane mitigates at scale)

> **Exam trap:** Lambda in VPC without NAT/endpoints cannot reach AWS services (DynamoDB, S3) unless VPC endpoints are configured.

---

## Layers and Extensions

### Layers
- Share dependencies across functions (e.g., common Python packages, SDK)
- Max **5 layers**, total unzipped size ≤ 250 MB (with function code)
- Order matters — later layers override earlier ones

### Extensions
- Run alongside function in same execution environment
- Use cases: custom monitoring, config loading (AppConfig), security agents

---

## Environment Variables

```python
import os
table_name = os.environ['TABLE_NAME']  # Fail fast if missing
debug = os.environ.get('DEBUG', 'false')
```

**Encrypt with KMS:**
```yaml
KmsKeyArn: !GetAtt AppKey.Arn
Environment:
  Variables:
    API_ENDPOINT: !Ref ApiEndpoint
```

**Best practice:** Secrets → Secrets Manager (retrieved at init, cached in global scope).

---

## Versions, Aliases, and Deployment

```
Development: $LATEST (mutable, auto-updates)
                    ↓ publish
Production:  Version 1, Version 2, Version 3 (immutable)
                    ↓ alias
             Alias "prod" → Version 3 (100%)
             Alias "prod" → V2 (90%) + V3 (10%)  ← canary
```

- **Publish** creates immutable version
- **Alias** is pointer to version(s) with optional weighted routing
- **CodeDeploy** automates canary/linear deployments on aliases

---

## Performance Optimization

| Technique | Benefit |
|-----------|---------|
| Increase memory | More CPU → often faster → lower total cost |
| Init code outside handler | Reused on warm starts (DB connections, boto3 clients) |
| Provisioned concurrency | Eliminate cold starts for latency-sensitive |
| Minimize package size | Faster cold starts |
| Avoid unnecessary VPC | VPC adds cold start latency |
| Connection reuse | Keep HTTP/DB connections in global scope |

```python
# ✅ Reuse client outside handler
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Orders')

def lambda_handler(event, context):
    table.put_item(Item={...})  # Reuses connection
```

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Lambda can't write to DynamoDB | Check execution role permissions |
| Lambda timeout with API Gateway | Reduce timeout or use async pattern |
| Failed async invocations lost | Configure DLQ or OnFailure destination |
| Access RDS in private subnet | VPC config + security group + NAT/endpoint |
| Zero-downtime deploy | Publish version + alias + CodeDeploy canary |
| Reduce cold start latency | Provisioned concurrency |
| Process SQS messages in batch | Event source mapping with BatchSize |
| Same event processed twice causes duplicate orders | Make handler idempotent |

---

## Related Guides

- [CI/CD Guide](aws-cicd-dva-c02-guide.md) — SAM deployment
- [Concepts Deep Dive](CONCEPTS-DEEP-DIVE.md) — Lambda execution model
- [Domain 1](domain-01-development-with-aws-services.md)
