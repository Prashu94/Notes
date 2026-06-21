# Domain 4: Troubleshooting and Optimization (18%) — DVA-C02

Maps to **Task 4.1** (root cause analysis), **Task 4.2** (observability), and **Task 4.3** (optimization).

See [Observability Guide](aws-observability-dva-c02-guide.md).

---

## Task 4.1: Root Cause Analysis

### Skill 4.1.1 — Debug Code Defects

Common Lambda bugs:
- **Unhandled exceptions** → 502 from API Gateway (sync) or retry loop (async)
- **Timeout** → Function killed at timeout limit; check CloudWatch duration metric
- **Permission denied** → Execution role missing action; check IAM policy
- **VPC connectivity** → Security group, subnet routing, NAT missing

### Skill 4.1.2 — Interpret Metrics, Logs, Traces

| Source | What to look for |
|--------|-----------------|
| **CloudWatch Metrics** | Errors, Duration, Throttles, ConcurrentExecutions |
| **CloudWatch Logs** | Stack traces, custom log messages, `[ERROR]` lines |
| **X-Ray** | Service map bottlenecks, fault/error nodes, latency distribution |

### Skill 4.1.3 — Query Logs

```sql
-- CloudWatch Logs Insights
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 50

-- Trace specific request
fields @timestamp, @message, @requestId
| filter @requestId = "abc-123-def"
```

### Skill 4.1.4 — Custom Metrics (EMF)

Embedded Metric Format — log a JSON document that CloudWatch automatically extracts as metrics. No separate API call needed.

### Skill 4.1.6 — Deployment Failure Logs

- **CloudFormation events** — stack rollback reason
- **CodeDeploy deployment logs** — traffic shift failures
- **CodeBuild logs** — build/test failures in CodePipeline

### Skill 4.1.7 — Service Integration Issues

Debug checklist:
1. **IAM permissions** — execution role vs resource policy (both sides for cross-service)
2. **Network** — VPC, security groups, endpoints
3. **Event format** — Lambda expecting different event structure than source sends
4. **Timeout chain** — API Gateway (29s) > Lambda timeout > downstream timeout
5. **Throttling** — Lambda concurrency, API Gateway rate limits, DynamoDB capacity

---

## Task 4.2: Instrument Code for Observability

### Skill 4.2.1 — Logging vs Monitoring vs Observability

| | Logging | Monitoring | Observability |
|--|---------|------------|---------------|
| **What** | Discrete events | Metrics over time | Understand system from outputs |
| **AWS** | CloudWatch Logs | CloudWatch Metrics/Alarms | Logs + Metrics + X-Ray traces |
| **Developer** | `print` / logger | Custom metrics, EMF | X-Ray SDK annotations |

### Skill 4.2.2 — Effective Logging Strategy

```python
import json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        'level': 'INFO',
        'action': 'process_order',
        'order_id': event.get('orderId'),
        'request_id': context.aws_request_id
    }))
```

**Best practices:**
- **Structured JSON** — queryable in Logs Insights
- **Correlation ID** — pass request ID through all services
- **Log levels** — ERROR for failures, INFO for business events, DEBUG for dev only
- **Don't log secrets** — sanitize PII

### Skill 4.2.6 — X-Ray Tracing

Enable on Lambda:
```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Tracing: Active
```

In code:
```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('validate_order')
def validate_order(order):
    ...
```

X-Ray shows: service map, trace timeline, downstream calls (DynamoDB, HTTP), error annotations.

### Skill 4.2.8 — Health Checks

```python
def health_handler(event, context):
    checks = {
        'dynamodb': check_dynamodb(),
        'external_api': check_external_api()
    }
    healthy = all(checks.values())
    return {
        'statusCode': 200 if healthy else 503,
        'body': json.dumps({'status': 'healthy' if healthy else 'degraded', 'checks': checks})
    }
```

---

## Task 4.3: Optimize Applications

### Skill 4.3.1 — Concurrency

| Setting | Purpose |
|---------|---------|
| **Account concurrency** | Shared pool (default 1,000) |
| **Reserved concurrency** | Guarantee min capacity for function; also caps max |
| **Provisioned concurrency** | Pre-warmed instances; eliminates cold starts |
| **Burst concurrency** | Initial burst then 500/min scaling (regional) |

**Throttling (`TooManyRequestsException`):**
- Account limit reached → request reserved concurrency or limit increase
- Function reserved concurrency = 0 → effectively disabled

### Skill 4.3.3 — Right-Size Memory

Lambda **CPU scales with memory**. More memory often = faster execution = lower total cost:

```
Test at 128, 256, 512, 1024, 2048 MB
Compare: duration × memory cost = total cost per invocation
Power Tuning tool (AWS Labs) automates this
```

### Skill 4.3.4 — SNS/SQS Filter Policies

Reduce unnecessary processing by filtering at subscription level — don't invoke Lambda for irrelevant events.

### Skill 4.3.5–4.3.6 — Caching

| Layer | Service | Developer action |
|-------|---------|-----------------|
| API responses | API Gateway caching | Enable per stage; cache key from query/path/header |
| Database reads | DAX, ElastiCache | Use cache-aside pattern in code |
| Content | CloudFront | Cache-Control headers from origin |

**Cache-aside pattern:**
```python
def get_user(user_id):
    cached = cache.get(f"user:{user_id}")
    if cached:
        return cached
    user = dynamodb.get_item(Key={'PK': user_id})['Item']
    cache.set(f"user:{user_id}", user, ttl=300)
    return user
```

### Skill 4.3.7–4.3.9 — Performance Analysis

**CloudWatch Lambda metrics to watch:**

| Metric | Indicates |
|--------|-----------|
| Duration | Execution time — optimize code or increase memory |
| Errors | Unhandled exceptions — check logs |
| Throttles | Concurrency limit — increase or optimize |
| IteratorAge | Stream processing lag — scale consumers |
| DeadLetterErrors | DLQ misconfigured — fix IAM on DLQ |

**DynamoDB optimization:**
- Use **Query** not Scan
- **BatchGetItem** for multiple keys
- **On-demand** for unpredictable traffic
- **DAX** for read-heavy caching

---

## Troubleshooting Decision Tree

```
Application error?
├── 502 from API Gateway → Lambda exception or timeout
├── 403 from API Gateway → Authorizer failure or IAM
├── 429 → Throttling (API GW or Lambda concurrency)
├── Lambda timeout → Increase timeout or optimize code
├── Lambda permission error → Fix execution role
├── DynamoDB throttling → On-demand mode or increase capacity
├── SQS messages reprocessed → Increase visibility timeout; check delete call
└── Intermittent failures → Check X-Ray for downstream latency/errors
```

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Find why Lambda fails intermittently | CloudWatch Logs + X-Ray traces |
| Reduce Lambda cold starts | Provisioned concurrency |
| Prevent runaway Lambda costs | Reserved concurrency cap |
| Optimize Lambda cost/performance | Power tuning (memory vs duration) |
| Reduce unnecessary Lambda invocations | SNS/EventBridge filter policies |
| Debug cross-service latency | X-Ray service map |
| Query logs across functions | CloudWatch Logs Insights |

**Related:** [Observability Guide](aws-observability-dva-c02-guide.md) | [Lambda Guide](aws-lambda-dva-c02-guide.md)
