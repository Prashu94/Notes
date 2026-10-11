# Lab 08 — Logs, a metric, an alarm, X-Ray

DVA skills 4.1 and 4.2. Uses the function from lab 05 or lab 07. If you already deleted them, the first block recreates a tiny function. Delete it at the end.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
FN=lab08-traced
```

## 1. Function with tracing

```bash
mkdir -p /tmp/lab08
cat > /tmp/lab08/handler.py <<'PY'
import json, time
def handler(event, context):
    print(json.dumps({"requestId": context.aws_request_id, "path": event.get("rawPath")}))
    if event.get("queryStringParameters", {}) and event["queryStringParameters"].get("fail"):
        raise RuntimeError("lab08 forced failure")
    time.sleep(0.2)
    return {"statusCode": 200, "body": "{}"}
PY
(cd /tmp/lab08 && zip -q function.zip handler.py)

cat > /tmp/lab08-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF
aws iam create-role --role-name Lab08Role --assume-role-policy-document file:///tmp/lab08-trust.json
aws iam attach-role-policy --role-name Lab08Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam attach-role-policy --role-name Lab08Role \
  --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
sleep 10

aws lambda create-function --function-name "$FN" --runtime python3.12 \
  --role "arn:aws:iam::${ACCOUNT}:role/Lab08Role" --handler handler.handler \
  --zip-file fileb:///tmp/lab08/function.zip --timeout 10 \
  --tracing-config Mode=Active
aws lambda invoke --function-name "$FN" --payload '{"rawPath":"/ok"}' \
  --cli-binary-format raw-in-base64-out /tmp/lab08-out.json
aws lambda invoke --function-name "$FN" --payload '{"queryStringParameters":{"fail":"1"}}' \
  --cli-binary-format raw-in-base64-out /tmp/lab08-fail.json
```

`Mode=Active` is what makes Lambda emit a trace. PassThrough only forwards a header that already exists. The X-Ray write policy is how the segments leave the function. Without it the function still runs and the trace does not.

## 2. Find the request

In the console, CloudWatch Logs Insights on `/aws/lambda/lab08-traced`:

```sql
fields @timestamp, @message
| filter @message like /lab08/
| sort @timestamp desc
| limit 20
```

The CLI equivalent when you already know the stream is `aws logs tail /aws/lambda/lab08-traced --since 30m`. Insights is the exam tool when the stem says "find the log lines for this request id." CloudTrail is the tool when the stem says "who called DeleteTrail."

X-Ray: `aws xray get-trace-summaries --start-time $(date -u -v-1H +%s) --end-time $(date -u +%s)` on macOS. A trace with a fault is the forced failure. A subsegment would appear if the function had called DynamoDB or S3 with the X-Ray SDK. The service segment from Lambda is enough to see that tracing is on.

## 3. Alarm on errors

```bash
aws cloudwatch put-metric-alarm --alarm-name lab08-errors \
  --namespace AWS/Lambda --metric-name Errors \
  --dimensions Name=FunctionName,Value="$FN" \
  --statistic Sum --period 60 --evaluation-periods 1 \
  --threshold 1 --comparison-operator GreaterThanOrEqualToThreshold \
  --treat-missing-data notBreaching
aws cloudwatch describe-alarms --alarm-names lab08-errors \
  --query 'MetricAlarms[0].StateValue'
```

There is no SNS action on this alarm, so it changes state and nobody is paged. Production adds an SNS topic and a subscription. A DLQ depth alarm is the same shape with namespace `AWS/SQS` and metric `ApproximateNumberOfMessagesVisible`.

`treat-missing-data notBreaching` means "no traffic" is not an incident. `breaching` means "no traffic" pages you. The exam uses that distinction for heartbeat metrics.

## 4. The cardinality trap

Do not publish a metric dimension per user id. One custom metric per user is a bill, and it is the optimization item in domain 4. A dimension of `status` or `function` is a small set. EMF (embedded metric format) is how a log line becomes a metric without `PutMetricData`. You do not need a library for the exam. You need to know a log line with the EMF JSON is scraped into a metric.

## Cleanup

```bash
aws cloudwatch delete-alarms --alarm-names lab08-errors
aws lambda delete-function --function-name "$FN"
aws logs delete-log-group --log-group-name "/aws/lambda/${FN}"
aws iam detach-role-policy --role-name Lab08Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam detach-role-policy --role-name Lab08Role \
  --policy-arn arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess
aws iam delete-role --role-name Lab08Role
rm -rf /tmp/lab08 /tmp/lab08-trust.json /tmp/lab08-out.json /tmp/lab08-fail.json
```
