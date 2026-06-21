# AWS Observability — DVA-C02 Guide

CloudWatch, X-Ray, and CloudTrail for debugging, monitoring, and optimizing applications.

---

## CloudWatch Logs

### Lambda Logging

- Automatic log group: `/aws/lambda/<function-name>`
- Retention configurable (default: never expire — set retention to save costs)
- **Structured logging** (JSON) enables Logs Insights queries

```python
import json, logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(json.dumps({
        'event': 'order_created',
        'order_id': event['orderId'],
        'request_id': context.aws_request_id
    }))
```

### CloudWatch Logs Insights

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)

-- Find slow requests
fields @timestamp, @duration
| filter @type = "REPORT"
| sort @duration desc
| limit 20
```

### Subscription Filters

Route log data to:
- Lambda (real-time processing)
- Kinesis Data Firehose (S3, OpenSearch)
- Kinesis Data Streams

---

## CloudWatch Metrics

### Lambda Built-in Metrics

| Metric | Meaning |
|--------|---------|
| Invocations | Total invocation count |
| Duration | Execution time (ms) |
| Errors | Unhandled exceptions |
| Throttles | Concurrency limit hit |
| ConcurrentExecutions | Current concurrent invocations |
| DeadLetterErrors | Failed to write to DLQ |
| IteratorAge | Stream processing lag (Kinesis/DynamoDB) |

### Custom Metrics

```python
cloudwatch = boto3.client('cloudwatch')
cloudwatch.put_metric_data(
    Namespace='MyApp',
    MetricData=[{
        'MetricName': 'OrdersProcessed',
        'Value': 1,
        'Unit': 'Count',
        'Dimensions': [{'Name': 'Environment', 'Value': 'prod'}]
    }]
)
```

### Embedded Metric Format (EMF)

Log JSON that CloudWatch auto-extracts as metrics — no separate API call:

```python
print(json.dumps({
    "_aws": {
        "Timestamp": int(time.time() * 1000),
        "CloudWatchMetrics": [{
            "Namespace": "MyApp",
            "Dimensions": [["Environment"]],
            "Metrics": [{"Name": "ProcessingTime", "Unit": "Milliseconds"}]
        }]
    },
    "ProcessingTime": 150,
    "Environment": "prod"
}))
```

### CloudWatch Alarms

- Trigger on metric threshold → SNS notification, Auto Scaling action, or Lambda
- **Composite alarms** — combine multiple alarms with AND/OR
- Use for CodeDeploy rollback triggers

---

## AWS X-Ray

### Enable Tracing

```yaml
# SAM template
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Tracing: Active
```

Or enable X-Ray on API Gateway stage for end-to-end traces.

### X-Ray SDK Annotations

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('process_payment')
def process_payment(order_id, amount):
    subsegment = xray_recorder.current_subsegment()
    subsegment.put_annotation('order_id', order_id)
    subsegment.put_metadata('payment', {'amount': amount})
    # ... payment logic
```

### Service Map

Visualizes:
- Request flow across services
- Latency per service (p50, p90, p99)
- Error and fault rates
- Downstream calls (DynamoDB, HTTP, SQS)

### Trace Analysis

- **Fault** — application error (4xx from your code)
- **Error** — unhandled exception (5xx)
- **Throttle** — rate limited

---

## CloudTrail (Developer Awareness)

- Logs **API calls** (who did what, when, from where)
- Not for application debugging — use CloudWatch Logs
- Use for: security audit, compliance, investigating unauthorized access
- **Data events** (optional): S3 object-level, Lambda function-level API logging

---

## Logging vs Monitoring vs Observability

| | Logging | Monitoring | Observability |
|--|---------|------------|---------------|
| **Question answered** | What happened? | Is it healthy? | Why is it slow/failing? |
| **Data type** | Text events | Numeric metrics | Logs + metrics + traces correlated |
| **AWS tools** | CloudWatch Logs | CloudWatch Metrics/Alarms | All three + X-Ray |
| **Developer action** | Structured JSON logs | Custom metrics/EMF | X-Ray annotations |

---

## Troubleshooting Workflow

```
1. Alarm fires (Errors > threshold)
2. Check CloudWatch Logs for stack trace
3. Query Logs Insights for error patterns
4. Open X-Ray trace for failing request
5. Identify slow/failing downstream (DynamoDB, HTTP)
6. Fix code, deploy, verify metrics return to normal
```

---

## Exam Scenarios

| Scenario | Answer |
|----------|--------|
| Find Lambda error stack traces | CloudWatch Logs |
| Query logs across time range | CloudWatch Logs Insights |
| Visualize request flow across services | X-Ray service map |
| Custom business metric without API call | Embedded Metric Format |
| Alert when Lambda errors exceed threshold | CloudWatch Alarm → SNS |
| Debug API Gateway + Lambda latency | X-Ray with active tracing on both |
| Audit who deleted a DynamoDB table | CloudTrail |
| Identify Lambda cold start duration | CloudWatch REPORT log line or X-Ray init segment |

---

## Related Guides

- [Domain 4 — Troubleshooting](domain-04-troubleshooting-and-optimization.md)
- [Lambda Guide](aws-lambda-dva-c02-guide.md)
