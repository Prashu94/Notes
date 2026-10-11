# Lambda and serverless

SAA 2.1 and 3.2. SAP 2.1, 4.4, and SAP-C03 serverless pipelines. DVA task 1.2 in full. This chapter is the mechanism. `05-dva/07-lambda-deep-dive.md` is the code.

Official:

- https://docs.aws.amazon.com/lambda/latest/dg/welcome.html
- https://docs.aws.amazon.com/lambda/latest/dg/invocation-async.html
- https://docs.aws.amazon.com/lambda/latest/dg/lambda-intro-execution-role.html
- https://docs.aws.amazon.com/lambda/latest/dg/with-sqs.html
- https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html

## When Lambda wins

The work is short, stateless, event-shaped, and you do not want an OS. It loses when you need a GPU, a listen port that stays open for hours, a Windows installer, more than 15 minutes, or more than 10 GB of memory. The current ceiling is 15 minutes and 10 GB. If AWS raises it, the exam still wants "the managed short-lived function" versus "the container."

| Caller | Invocation |
| --- | --- |
| API Gateway proxy, ALB, SDK `RequestResponse` | Synchronous. The error returns to the caller. No Lambda retry |
| S3, SNS, EventBridge, SDK `Event` | Asynchronous. Lambda retries twice. Then the on-failure destination or the DLQ |
| SQS, Kinesis, DynamoDB Streams | Event source mapping. Lambda polls. Retry behavior is the mapping's, not the async retry |

## Execution role

The role's trust is `lambda.amazonaws.com`. The permissions are the AWS APIs the code calls. `AWSLambdaBasicExecutionRole` is the log permission. Add the data permissions yourself. A function URL or an API does not add S3 permissions. People confuse the resource policy (who can invoke the function) with the execution role (what the function can call).

```bash
aws lambda create-function --function-name orders \
  --package-type Zip --runtime python3.12 --handler app.handler \
  --role "$ROLE_ARN" --timeout 10 --memory-size 512 \
  --zip-file fileb://function.zip \
  --environment "Variables={TABLE=orders}" \
  --tracing-config Mode=Active
aws lambda create-function-url-config --function-name orders --auth-type AWS_IAM
```

## Concurrency

| Knob | Effect |
| --- | --- |
| Account concurrency | Default 1,000 per Region, shared by functions that do not have reserved concurrency. Adjustable |
| Reserved concurrency | Caps the function and guarantees that cap from the account pool. A reserve of 0 throttles the function off. Useful to protect a database |
| Provisioned concurrency | Pre-warmed environments on a version or alias. Removes cold starts for that number. You pay while they are idle |
| SnapStart | Java and some runtimes. A snapshot after init. Not the same as provisioned concurrency |

A throttle is `TooManyRequestsException` or a 429 from API Gateway. The fix is not always "raise the account limit." Sometimes the fix is a queue so the function's reserved concurrency matches the database.

## Cold starts

The init phase runs static code and the runtime start. It shows up as `InitDuration`. Cut it by shrinking the package, raising memory (which raises CPU), using a lighter runtime, SnapStart where it applies, or provisioned concurrency when the SLO covers the first request. A VPC attachment used to dominate cold start. Hyperplane ENIs made that much smaller. A stem that still says "Lambda in a VPC is always too slow to use" is out of date. A stem that says "the first request after idle must be fast" is provisioned concurrency or a container that stays warm.

## Versions, aliases, traffic

Publish a version. It is immutable. `$LATEST` is not. An alias (`live`, `prod`) points at a version. CodeDeploy shifts traffic on the alias: canary, linear, all-at-once. Rollback is the alias pointing at the previous version. Stage variables in API Gateway can pass the alias name so dev and prod are configuration.

## Destinations and DLQs

Async only: on-success and on-failure destinations can be SQS, SNS, Lambda, or EventBridge. The record includes the response. A DLQ is failure-only and is the older feature. New designs use destinations.

SQS mappings do not use Lambda Destinations. They use the queue redrive policy. Turn on `ReportBatchItemFailures` or one poison message blocks the batch until the visibility timeout and the redrive max receives send it to the DLQ.

Kinesis and DynamoDB Streams retry until the record expires unless you set a bisect-on-error, a maximum retry, and an on-failure destination. Iterator age is the metric that says you are falling behind.

## VPC

Attach subnets and a security group only when the target is private. Then add endpoints or a NAT for any AWS API the function still calls. Security group on the function is the client SG. The RDS SG must allow that SG on the database port.

## SAM, one page

```yaml
AWSTemplateFormatVersion: "2010-09-09"
Transform: AWS::Serverless-2016-10-31
Resources:
  Orders:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: src/
      Handler: app.handler
      Runtime: python3.12
      MemorySize: 512
      Timeout: 15
      Architectures: [arm64]
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref Table
      Events:
        Api:
          Type: Api
          Properties:
            Path: /orders
            Method: post
```

```bash
sam build
sam local invoke Orders -e events/post.json
sam deploy --guided
```

`arm64` is Graviton and is the price-performance default when your dependencies ship wheels for it.

Powertools (Python, TypeScript, Java, .NET) gives structured logs, EMF metrics, and tracing in a few lines. The exam will not require the import. It will describe the outcome: one log line that becomes a metric.

## Serverless Application Repository

Publish and consume prebuilt SAM apps. Least operational overhead when the stem says "a standard application already published" and building it is not the point. You still review the IAM the template asks for.

## Exercises

1. A function writes to RDS and to S3. It is not in a VPC. RDS is private. S3 is standard. What do you attach, and what extra network do you add so S3 still works without a NAT?
2. An SQS trigger processes batches of 10. One message throws. The other nine succeed and then get processed again. What did the function fail to return, and what setting must be on?
3. Prod must move 10% of traffic to a new version for 10 minutes and roll back if errors rise. Which two Lambda features?
4. The account concurrency is 1,000. One noisy function consumes it and a payments function starts throttling. What do you set on the noisy function?
5. A designer sets the Lambda timeout to 15 minutes and the API Gateway timeout to 29 seconds, then wonders why clients see 503s while the function is still running. Explain the two timeouts.

## Answers

1. Put the function in the VPC subnets that can reach RDS, with a security group the database allows. Add an S3 gateway endpoint on those route tables so S3 does not need a NAT.
2. It should return `batchItemFailures` for the failed message id, and the event source mapping needs `ReportBatchItemFailures`. Otherwise Lambda retries the whole batch.
3. A published version, an alias, and a CodeDeploy canary (or Lambda weighted alias) with a CloudWatch alarm. The alias is what traffic is attached to.
4. Reserved concurrency on the noisy function, sized to what it may use, so the rest of the account pool remains for payments. Optionally reserved concurrency on payments too, so its floor is guaranteed.
5. API Gateway will not wait 15 minutes. The integration times out around 29 seconds and the client gets an error. The function keeps running and may still write. For long work, accept the request, put it on SQS, and return 202.

## The execution environment

A cold start creates an environment, runs init (imports, clients you built at module scope), then the handler. A warm start reuses the environment, including globals and files in `/tmp`. Two invocations do not run on one environment at the same time. Many environments do run. A global is a cache for that environment. It is not a session and it is not shared.

Build the SDK client at import time. Building it inside the handler pays init on every call. Do not store a user id in a global. The next invocation on that environment is a different user.

Memory is the CPU dial. More memory adds CPU until duration stops falling. Timeout is a separate knob and does not make the function faster. Ephemeral storage (`/tmp`) defaults small and can be raised when the function needs scratch. The deployment package has a direct-upload size limit and a larger unzipped limit. Bigger artifacts belong in S3 or in a container image. Layers are shared libraries you version, up to five. A layer is not a junk drawer.

SnapStart, on supported Java runtimes, snapshots the initialized environment so cold start drops. It does not fix a slow handler. Provisioned concurrency keeps environments warm and is what you buy when the SLO applies to the first request. It costs money while they sit idle. Reserved concurrency is a cap, and it subtracts from the account pool. Zero means the function cannot run. Do not confuse the two. The default account pool is 1,000 per Region and is adjustable. A noisy function with no cap eats the pool and throttles payments.

## How the event arrives

| Invoke | Retry | Where failure goes |
| --- | --- | --- |
| Synchronous (`RequestResponse`), API Gateway, ALB | The caller retries | The caller sees the error. No Lambda destination |
| Asynchronous (`Event`), S3, SNS, EventBridge | Two retries, then stop | On-failure destination: SQS, SNS, Lambda, or EventBridge. A DLQ is the older async option. Destinations can also fire on success and can carry the response |
| SQS poll | The message stays until you delete it or the redrive policy moves it | The queue's DLQ after `maxReceiveCount`. Destinations are not the SQS retry mechanism |
| Stream poll (Kinesis, DynamoDB) | The batch blocks the shard | Bisect on error, maximum record age, an on-failure destination. Iterator age is the lag metric |

The response shape must match the source. API Gateway proxy wants `statusCode` and a string `body`. SQS wants `batchItemFailures` with the message id, and the mapping must have `ReportBatchItemFailures` or the return value is ignored. A 200 from an SQS handler does not delete messages by itself. The poller deletes messages that were not reported as failures.

Visibility timeout on the queue must exceed the function timeout. Otherwise the message becomes visible while the function is still running and a second environment takes it.

Filters on the event source drop events before you pay for an invoke. A function whose first line returns because the event type is wrong is a filter you forgot to set.

## Network and permissions

No VPC: the function reaches the public internet and public AWS APIs, and it cannot reach a private RDS. In a VPC: ENIs in the subnets you name, a security group, and no internet unless those subnets have a NAT. S3 and DynamoDB want a gateway endpoint. Secrets Manager, SQS, KMS, and CloudWatch Logs want interface endpoints if there is no NAT. A timeout is the network. `AccessDenied` is IAM and comes back fast.

One role per function. `logs:CreateLogGroup`, `CreateLogStream`, `PutLogEvents` are the minimum besides the data actions. `AWSLambdaBasicExecutionRole` is that log statement and is wider than a single log group. The resource policy on the function must allow the caller (API Gateway's source ARN, S3, the event source mapping's service). A function URL with `AuthType NONE` is a public HTTP endpoint. Use `AWS_IAM` unless the stem is a public webhook you have otherwise authenticated.

Recursive loop protection exists because an S3 notification that writes back to the same bucket will invoke forever. The exam version is: filter the prefix, or write to a different bucket.

## Versions, aliases, and the 29-second door

`$LATEST` moves when you deploy. A published version does not. An alias points at a version and is what API Gateway, the event source, and the canary should call. CodeDeploy shifts the alias. Rollback moves the alias back. Deleting the version is not the rollback.

API Gateway's integration timeout is about 29 seconds. The Lambda maximum is 15 minutes. A two-minute PDF is a queue and a 202. Raising memory does not stretch the front door. Function URLs and ALBs have their own timeout behavior. The 29-second number is the API Gateway one.

## More exercises

6. `InitDuration` is large and `Duration` is small. The function is in a VPC and imports a 200 MB library in the handler. What do you move, and what do you buy if the first request has an SLO?
7. Reserved concurrency is 0. The function "disappeared." What does 0 mean?
8. An S3 trigger writes a thumbnail back to the same bucket and prefix. What happens, and what is the smallest fix?
9. The SQS batch size is 10. You catch errors, log them, and return normally. What happens to the poison message?
10. Two functions share one role that can read both tables. Why is that a security defect when one function is compromised?

## Answers

6. Import and create clients at module scope, shrink the package, and keep the function out of the VPC if it does not need private resources. If the SLO is on the first request, add provisioned concurrency. Raising the timeout only hides the cold start from a gateway that may already have given up.
7. The function is not allowed to run. Reserved concurrency is a cap. Zero is an off switch, and it also contributes nothing useful to the pool.
8. Each thumbnail is a new object that invokes the function again. Filter the notification to the uploads prefix, and write thumbnails to a different prefix that does not match.
9. The poller treats the batch as success and deletes all ten, including the poison message. You swallowed the failure. Return that message id in `batchItemFailures`, with the mapping configured to honor it, or let the exception fail the invocation if you accept the whole batch retrying.
10. The attacker who can run one function can read both tables. One role per function, scoped to that function's table.
