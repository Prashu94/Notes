# SDK patterns

DVA skills 1.1.5, 1.1.9, 1.1.13. Python is the sample. The JavaScript v3 sample is the same idea: a client from the default chain, a paginator, a timeout.

Official: https://docs.aws.amazon.com/sdkref/latest/guide/overview.html and https://boto3.amazonaws.com/v1/documentation/api/latest/guide/retries.html

## Client

```python
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

cfg = Config(
    retries={"max_attempts": 8, "mode": "adaptive"},
    connect_timeout=2,
    read_timeout=5,
)
ddb = boto3.resource("dynamodb", config=cfg)
table = ddb.Table("orders")
s3 = boto3.client("s3", config=cfg)
```

Create the client outside the handler so warm starts reuse it. Do not pass keys.

## Paginate

```python
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="BUCKET", Prefix="in/"):
    for obj in page.get("Contents", []):
        handle(obj["Key"])
```

## Retry only what will change

```python
def is_throttle(err: ClientError) -> bool:
    code = err.response["Error"]["Code"]
    return code in {"Throttling", "ThrottlingException", "TooManyRequestsException", "ProvisionedThroughputExceededException", "RequestLimitExceeded"}
```

`AccessDenied`, `ConditionalCheckFailedException`, and `ValidationException` need a code change, not a retry. A circuit breaker around a third-party HTTP call fails fast when the dependency is down. A retry with full jitter is for the short blip. Both belong in the same client. Retrying a dead dependency a hundred times is how you extend the outage.

## Idempotent write

```python
try:
    table.put_item(
        Item={"pk": order_id, "sk": "ORDER", "status": "NEW"},
        ConditionExpression="attribute_not_exists(pk)",
    )
except ClientError as err:
    if err.response["Error"]["Code"] != "ConditionalCheckFailedException":
        raise
```

The second delivery of the same order id is a success, not a second charge.

## Assume a role when you must hop

```python
sts = boto3.client("sts")
creds = sts.assume_role(RoleArn=ROLE, RoleSessionName="orders", ExternalId=EXTERNAL)["Credentials"]
# build a client with the temporary key, secret, and session token
# refresh before Credentials["Expiration"]
```

The function's own role does not need this. The SDK already has it.

## Exercise

The list function returns 1,000 keys and exits 0. The bucket has 50,000. What line is missing?

Answer: a paginator or a loop on `NextContinuationToken`. The first page is not the bucket.

## What the SDK is doing

Create the client once, outside the handler, with timeouts shorter than the Lambda timeout and retries only for throttling. Adaptive mode adds jitter. Do not pass keys. A paginator hides the token. If you write the loop yourself, you must pass the token back or you reread page one.

Idempotency is a conditional write or a stored key, not a retry setting. `AssumeRole` is for a hop into another role. The execution role is already on the client. Refresh temporary credentials before `Expiration`.

Waiters do not belong in a request path. Pagination bugs exit zero. `AccessDenied` should not be retried.

## More exercises

2. The client is constructed inside `handler` with `aws_access_key_id` from an environment variable. Name two defects.
3. `read_timeout` is 60 and the Lambda timeout is 10. What happens when S3 hangs?
4. A retry loop catches `ConditionalCheckFailedException` and tries the put again. What is the result?
5. You need every item in a partition, not every item in the table. Which call, and which token?

## Answers

2. A new client on every invoke, which wastes the warm environment, and a long-lived key in the environment. Use the default chain and the execution role. Build the client at import time.
3. The SDK waits longer than the function is allowed to live. The function is killed first and the error is a Lambda timeout, not a clean SDK error. Set the client timeout lower so you can catch it and return a controlled failure.
4. The same exception, until you give up. The item exists. Treat that code as success for an idempotent create.
5. `Query` with the partition key, following `LastEvaluatedKey`. A `Scan` reads the table. The query's next token is not the S3 continuation token. Do not mix them.
