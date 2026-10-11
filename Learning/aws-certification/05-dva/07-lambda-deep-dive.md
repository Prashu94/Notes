# Lambda deep dive

DVA task 1.2. Mechanism also in `02-services/02-lambda-and-serverless.md`.

## Handler

```python
import json, os, boto3
table = boto3.resource("dynamodb").Table(os.environ["TABLE"])

def handler(event, context):
    if context.get_remaining_time_in_millis() < 500:
        raise TimeoutError("not enough time")
    body = json.loads(event.get("body") or "{}")
    table.put_item(Item={"pk": body["id"], "sk": "ORDER"})
    return {"statusCode": 201, "body": json.dumps({"id": body["id"]})}
```

`context.aws_request_id` goes in every log line. API Gateway's request id and this id are how you join the logs.

## Event shapes you must not mix up

| Source | Where the payload is |
| --- | --- |
| API Gateway HTTP API or REST proxy | `event["body"]` is a string. `requestContext` has the route and the authorizer claims |
| SQS | `event["Records"][i]["body"]`, receipt handle is not in the body, `messageId` is what partial batch failure wants |
| SNS | `Records[i]["Sns"]["Message"]` |
| S3 | `Records[i]["s3"]["bucket"]["name"]` and `object["key"]`. The key is URL-encoded |
| DynamoDB Streams | `Records[i]["dynamodb"]["NewImage"]` |
| EventBridge | `event["detail"]` |

Returning an API Gateway shape from an SQS handler does nothing useful. Returning `batchItemFailures` from an API handler does nothing useful. Match the source.

## Async, queues, streams

Async invoke: two retries, then the on-failure destination. Destinations beat a DLQ on new async functions because they can carry the response and can fire on success too.

SQS: the queue's redrive policy is the DLQ. Report batch item failures or the good messages in the batch retry too. Set the visibility timeout above the function timeout, or the message becomes visible while the function is still running.

Streams: bisect on error, a maximum record age, an on-failure destination, or a poison record blocks the shard until it expires.

## VPC

Attach the function only for private resources. Security group on the function. The database allows that group. Gateway endpoint for S3. Interface endpoint for Secrets Manager, SQS, KMS, and Bedrock if you call them. A NAT is the leftover path to the public internet.

## Concurrency and cold starts

Account pool, reserved cap, provisioned warm environments. Memory raises CPU. SnapStart for supported Java. A large package and a big client built inside the handler make `InitDuration` worse. Build the client at import time.

## Exercise

The SQS batch has 10 messages. Message 4 throws. The code does not catch it. What happens to messages 5 through 10, and what do you return instead?

Answer: the whole batch fails and all 10 can be retried, including the ones you already processed, unless those writes were idempotent. Catch the error for message 4 and return `{"batchItemFailures": [{"itemIdentifier": "<messageId>"}]}`. The mapping must have `ReportBatchItemFailures` enabled.

## Event shapes

| Source | Where the payload is | What you return |
| --- | --- | --- |
| API Gateway proxy | `event["body"]` is a string. Claims are on `requestContext` | `statusCode`, string `body` |
| SQS | `Records[i]["body"]`, `messageId` | `batchItemFailures` |
| SNS | `Records[i]["Sns"]["Message"]` | A normal return. SNS retries on a thrown error |
| S3 | Bucket name and a URL-encoded key | A normal return. Make the write idempotent. Avoid writing back into the same prefix |
| DynamoDB Streams | `NewImage` under `dynamodb` | Handle poison records or the shard stalls |
| EventBridge | `event["detail"]` | A normal return |

`context.aws_request_id` goes in every log line. `get_remaining_time_in_millis()` is how you stop before the timeout kills you mid-write.

Async invokes retry twice, then the on-failure destination. SQS uses the queue redrive policy, not that destination. Visibility timeout must exceed the function timeout.

A global is reused on a warm environment. Clients belong at import time. User ids do not. Memory is CPU. Reserved concurrency of 0 turns the function off. Provisioned concurrency is the warm pool you pay for. A VPC is only for private resources, plus the endpoints those subnets need.

## More exercises

2. The handler returns `{"ok": true}` to an API Gateway proxy integration. What does the client get?
3. S3 object key is `a/b%20c.txt`. You pass it to `GetObject` unchanged. What is wrong?
4. The function is in a VPC, reaches RDS, and times out on Secrets Manager. There is no NAT. What endpoint, and does RDS need one?
5. `$LATEST` is the API target. A canary shifts an alias that nothing calls. Why did production not canary?

## Answers

2. A 502. The proxy integration required `statusCode` and a string body. A bare dict is not that shape.
3. The key is URL-encoded. Decode it before `GetObject`, or you ask for a key that does not exist.
4. An interface endpoint for Secrets Manager with private DNS. RDS is a private IP. It does not use an AWS API endpoint. The function's security group must reach the endpoint's security group.
5. Production invokes `$LATEST`, which moves on every deploy and ignores the alias. Point the API at the alias. The canary then has a weight to shift, and rollback moves the alias back.
