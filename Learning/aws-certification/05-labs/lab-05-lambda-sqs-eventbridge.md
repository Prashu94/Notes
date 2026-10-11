# Lab 05 — Lambda, SQS, partial batch failure, EventBridge

SAA task 2.1 and DVA skills 1.2. One function, one queue, one rule. No VPC.

```bash
export AWS_PROFILE=sandbox
export AWS_DEFAULT_REGION=us-east-1
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
```

## 1. The function

```bash
mkdir -p /tmp/lab05 && cd /tmp/lab05
cat > handler.py <<'PY'
import json

def handler(event, context):
    failures = []
    for record in event.get("Records", []):
        body = record["body"]
        print(json.dumps({"requestId": context.aws_request_id, "messageId": record["messageId"]}))
        if "poison" in body:
            failures.append({"itemIdentifier": record["messageId"]})
            continue
    return {"batchItemFailures": failures}
PY
zip -q function.zip handler.py

cat > /tmp/lab05-trust.json <<'EOF'
{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}
EOF

aws iam create-role --role-name Lab05Role \
  --assume-role-policy-document file:///tmp/lab05-trust.json
aws iam attach-role-policy --role-name Lab05Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# The basic execution policy covers logs. SQS needs its own statements.
cat > /tmp/lab05-sqs.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["sqs:ReceiveMessage","sqs:DeleteMessage","sqs:GetQueueAttributes","sqs:SendMessage"],
    "Resource": "arn:aws:sqs:${AWS_DEFAULT_REGION}:${ACCOUNT}:lab05-orders"
  }]
}
EOF
aws iam put-role-policy --role-name Lab05Role --policy-name sqs \
  --policy-document file:///tmp/lab05-sqs.json

sleep 10
ROLE_ARN="arn:aws:iam::${ACCOUNT}:role/Lab05Role"
aws lambda create-function --function-name lab05-consumer \
  --runtime python3.12 --role "$ROLE_ARN" --handler handler.handler \
  --zip-file fileb:///tmp/lab05/function.zip --timeout 10
```

`SendMessage` is on the role so the same role can be the EventBridge target's invocation path later. The function itself only needs receive and delete. Leaving send on a consumer is wider than production. The exam wants the consumer limited to receive, delete, and get-queue-attributes.

## 2. Queue, DLQ, mapping

Visibility timeout must be longer than the function timeout. A message that becomes visible while the function is still running is delivered twice on purpose.

```bash
DLQ=$(aws sqs create-queue --queue-name lab05-orders-dlq --query QueueUrl --output text)
DLQ_ARN=$(aws sqs get-queue-attributes --queue-url "$DLQ" --attribute-names QueueArn --query Attributes.QueueArn --output text)

Q=$(aws sqs create-queue --queue-name lab05-orders \
  --attributes "{\"VisibilityTimeout\":\"30\",\"RedrivePolicy\":\"{\\\"deadLetterTargetArn\\\":\\\"${DLQ_ARN}\\\",\\\"maxReceiveCount\\\":\\\"3\\\"}\"}" \
  --query QueueUrl --output text)
Q_ARN=$(aws sqs get-queue-attributes --queue-url "$Q" --attribute-names QueueArn --query Attributes.QueueArn --output text)

aws lambda create-event-source-mapping \
  --function-name lab05-consumer \
  --event-source-arn "$Q_ARN" \
  --batch-size 5 \
  --function-response-types ReportBatchItemFailures
```

Without `ReportBatchItemFailures`, the `batchItemFailures` return value is ignored and one poison message fails the whole batch.

## 3. A good message and a poison message

```bash
aws sqs send-message --queue-url "$Q" --message-body '{"order":"1001"}'
aws sqs send-message --queue-url "$Q" --message-body '{"order":"poison"}'
sleep 20
aws logs tail /aws/lambda/lab05-consumer --since 10m
aws sqs get-queue-attributes --queue-url "$DLQ" --attribute-names ApproximateNumberOfMessages
```

The good message is deleted. The poison message is retried until `maxReceiveCount`, then it sits in the DLQ. An alarm on that depth is the difference between a DLQ and a bin. This lab does not create the alarm. Lab 08 does.

## 4. EventBridge to the same queue

```bash
aws events put-rule --name lab05-orders-created --event-pattern '{
  "source": ["lab.orders"],
  "detail-type": ["OrderCreated"]
}'
aws events put-targets --rule lab05-orders-created --targets "Id"="orders","Arn"="$Q_ARN"
aws sqs set-queue-attributes --queue-url "$Q" --attributes "{\"Policy\":\"{\\\"Version\\\":\\\"2012-10-17\\\",\\\"Statement\\\":[{\\\"Effect\\\":\\\"Allow\\\",\\\"Principal\\\":{\\\"Service\\\":\\\"events.amazonaws.com\\\"},\\\"Action\\\":\\\"sqs:SendMessage\\\",\\\"Resource\\\":\\\"${Q_ARN}\\\",\\\"Condition\\\":{\\\"ArnEquals\\\":{\\\"aws:SourceArn\\\":\\\"arn:aws:events:${AWS_DEFAULT_REGION}:${ACCOUNT}:rule/lab05-orders-created\\\"}}}]}\"}"

aws events put-events --entries "[{
  \"Source\": \"lab.orders\",
  \"DetailType\": \"OrderCreated\",
  \"Detail\": \"{\\\"order\\\":\\\"1008\\\"}\"
}]"
```

EventBridge is the bus. SQS is the buffer. Lambda is the worker. The exam uses that split when the stem says more than one consumer, or retries, or "do not lose the event if the function is down." A rule with no queue, targeting Lambda directly, is fine for a single consumer that can tolerate the async retry policy.

SNS fanout is the other shape: one topic, one queue per consumer. You did not build it. You should be able to say why you would.

## Cleanup

```bash
MAP=$(aws lambda list-event-source-mappings --function-name lab05-consumer \
  --query 'EventSourceMappings[0].UUID' --output text)
aws lambda delete-event-source-mapping --uuid "$MAP"
aws events remove-targets --rule lab05-orders-created --ids orders
aws events delete-rule --name lab05-orders-created
aws lambda delete-function --function-name lab05-consumer
aws sqs delete-queue --queue-url "$Q"
aws sqs delete-queue --queue-url "$DLQ"
aws iam delete-role-policy --role-name Lab05Role --policy-name sqs
aws iam detach-role-policy --role-name Lab05Role \
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
aws iam delete-role --role-name Lab05Role
rm -rf /tmp/lab05 /tmp/lab05-trust.json /tmp/lab05-sqs.json
```

Wait about a minute if the mapping delete is still in progress, then delete the function.
