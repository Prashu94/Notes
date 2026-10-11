# DVA-C02 exam blueprint

Source: AWS Certified Developer – Associate exam guide (DVA-C02), version 2.1 published 12 December 2024, HTML and PDF on AWS Documentation, reviewed 11 October 2026.

https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html

https://docs.aws.amazon.com/pdfs/aws-certification/latest/developer-associate-02/developer-associate-02.pdf

Role in one line: develop, test, deploy, and debug applications that call AWS APIs. You are not designing the multi-account network. You are writing the code and the deployment that run inside one.

| Domain | Weight | One-line job |
| --- | --- | --- |
| 1. Development with AWS Services | 32% | Patterns, Lambda, data stores, SDK calls. Heaviest domain |
| 2. Security | 26% | AuthN, authZ, encryption, secrets, tenant isolation |
| 3. Deployment | 24% | Packages, tests, IaC, CI/CD, rollback |
| 4. Troubleshooting and Optimization | 18% | Logs, metrics, traces, concurrency, caching |

50 scored questions plus 15 unscored. 130 minutes. 150 USD. Passing score 720 scaled. Compensatory scoring. No penalty for guessing. Recommended experience is 1 or more years developing and maintaining applications on AWS, plus one high-level language, the application lifecycle, AWS APIs, the CLI, SDKs, and a CI/CD workflow you can use. The guide says you are not expected to design the pipeline. You are expected to commit code that a pipeline builds and to pick a deployment strategy the pipeline already supports.

Out of scope, from the guide:

- Designing architectures (distributed systems, microservices topologies, database schemas and data modeling).
- Designing and creating CI/CD pipelines.
- Administering IAM users and groups.
- Administering servers and operating systems.
- Designing VPC or Direct Connect.

You still use those things. A Lambda in a VPC, an IAM role the function assumes, and a CodePipeline stage that already exists are in scope. Drawing the VPC CIDR plan is not.

Version 2.1 added skills for Amazon Q Developer, EventBridge, retries and circuit breakers, Lambda near-real-time transforms, OpenSearch as a specialized store, application-level authorization, cross-service auth in microservices, data masking, multi-tenant access, AppConfig, event-driven tests, custom metrics and health checks, and application caching. CodeGuru and AWS Copilot left the in-scope list. Amazon Q Developer joined it.

Emerging topics are unscored pretest items: AI-assisted coding, AI security, AI-generated tests, AI in CI/CD, AI troubleshooting, AI optimization. DVA-C03 makes that material scored. Study `06-dva-c03-transition.md` either way.

---

## Domain 1 — Development with AWS Services (32%)

### Task 1 — Develop code for applications hosted on AWS

| Skill | What the item is asking | What you do |
| --- | --- | --- |
| 1.1.1 Patterns | event-driven, microservices, monolith, choreography, orchestration, fanout | Name the pattern from the failure mode. Choreography: each service emits an event and nobody is in charge (EventBridge). Orchestration: one workflow calls the steps (Step Functions). Fanout: one event, many queues (SNS to SQS) |
| 1.1.2 Stateful vs stateless | Where does session live? | Stateless handlers scale. State goes to DynamoDB, ElastiCache, or S3. A static variable on Lambda is not a session store. Execution environments are reused and are not yours |
| 1.1.3 Tight vs loose coupling | A slow downstream fails the request | Put SQS between them. The HTTP handler returns after `SendMessage`. The consumer retries |
| 1.1.4 Sync vs async | The caller needs the body now, or it does not | Sync: API Gateway to Lambda proxy, or SDK call that waits. Async: S3 event, SNS, SQS, EventBridge, Lambda async invocation. Async Lambda retries twice, then the destination or DLQ |
| 1.1.5 Fault-tolerant code | Language is your choice: Java, C#, Python, JavaScript, TypeScript, Go | Timeouts on every SDK client. Retries with jitter. Idempotent writes. Do not catch `Exception` and return 200 |
| 1.1.6 APIs | response mapping, validation, status codes | API Gateway request validator, mapping template or Lambda proxy that sets `statusCode`, models. Override a 200 from an integration that actually failed |
| 1.1.7 Unit tests with SAM | `sam local invoke`, `sam local start-api` | Test the handler with a fake event JSON. Mock AWS with stubs. Do not hit production in a unit test |
| 1.1.8 Messaging code | SQS, SNS, EventBridge | `SendMessage`, `ReceiveMessage`, delete only after success, change visibility on failure, publish with a subject and attributes |
| 1.1.9 SDK and API | SigV4, pagination, waiters | Use the SDK. Paginate `list_*` calls. Do not invent a `while True` on an unpaginated first page |
| 1.1.10 Streaming | Kinesis, Firehose | Process records in batches. Checkpoint. Handle partial batch failure (`ReportBatchItemFailures` on Lambda) |
| 1.1.11 Amazon Q Developer | generate, explain, transform code | In scope as a tool you use. It does not replace tests. Do not paste secrets into a prompt that lands in logs |
| 1.1.12 EventBridge | event-driven patterns | Put events on a bus. Rules filter. Archive and replay when the consumer was down |
| 1.1.13 Third-party resilience | retry, circuit breaker, error handling | Exponential backoff with full jitter. Open the circuit when the dependency is dead so you fail fast. A retry storm is not resilience |

SDK shape you must be able to read in Python and in JavaScript. The exam will not grade your syntax. It will show a snippet and ask which call is wrong.

```python
import boto3
from botocore.config import Config

session = boto3.Session(region_name="us-east-1")
s3 = session.client(
    "s3",
    config=Config(
        retries={"max_attempts": 5, "mode": "adaptive"},
        connect_timeout=2,
        read_timeout=5,
    ),
)
paginator = s3.get_paginator("list_objects_v2")
for page in paginator.paginate(Bucket="BUCKET", Prefix="incoming/"):
    for obj in page.get("Contents", []):
        print(obj["Key"])
```

```javascript
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { DynamoDBDocumentClient, GetCommand } from "@aws-sdk/lib-dynamodb";

const doc = DynamoDBDocumentClient.from(new DynamoDBClient({}));
const out = await doc.send(new GetCommand({
  TableName: process.env.TABLE_NAME,
  Key: { pk: orderId },
  ConsistentRead: true,
}));
```

Default credential chain, in order the SDK actually walks: environment variables, the shared credentials file, the SSO cache, ECS task role or EC2 instance metadata. On Lambda the role is already in the environment. Hard-coding `aws_access_key_id` in source fails skill 2.1.3 and skill 2.3.3.

Idempotency: SQS standard is at-least-once. Your consumer must tolerate a second delivery. Use a condition expression on DynamoDB (`attribute_not_exists(pk)`) or a deduplication key. FIFO queues add deduplication ids and group ids. They do not remove the need for a correct consumer when the visibility timeout is shorter than the work.

### Task 2 — Develop code for AWS Lambda

| Skill | The fact that answers the item |
| --- | --- |
| 1.2.1 Private resources | Attach the function to the VPC subnets and security groups that can reach the resource. The function then needs a NAT gateway or VPC endpoints to call public AWS APIs, unless you add interface endpoints. Hyperplane ENIs are shared. Cold starts still exist |
| 1.2.2 Configuration | Memory (also scales CPU), timeout, runtime, handler, environment variables, layers, extensions, triggers, destinations, reserved and provisioned concurrency. Environment variables are visible in the console. Encrypt them with a KMS key if they are secrets, or prefer Secrets Manager |
| 1.2.3 Event lifecycle | Sync invoke: the caller gets the error. Async invoke: two retries, then on-failure destination (SQS, SNS, Lambda, EventBridge) or a DLQ. Stream sources: bisect and report batch item failures or the whole batch retries until the record expires |
| 1.2.4 Tests | `sam local invoke -e event.json`. A unit test calls the handler function with the event dict. Integration tests use a deployed alias |
| 1.2.5 Integrations | S3, SNS, SQS, DynamoDB Streams, Kinesis, EventBridge, API Gateway, ALB, Cognito, IoT. The event shape differs. Read `event["Records"]` for S3, SQS, SNS, DynamoDB, Kinesis. Read `event["requestContext"]` for API Gateway proxy |
| 1.2.6 Performance | Right-size memory from the CloudWatch `Duration` and `InitDuration` and from Lambda Power Tuning or the console recommendations. Provisioned concurrency for latency. Avoid heavy work in the global scope unless you want it reused across invocations. Do not open a new SDK client per invoke if the global client is safe |
| 1.2.7 Near-real-time transform | Kinesis or DynamoDB Streams to Lambda. Filter events at the source so you do not pay for invokes you will drop. Firehose can also transform with Lambda |

Handler contract:

```python
def handler(event, context):
    # context.get_remaining_time_in_millis()
    # context.aws_request_id
    return {"statusCode": 200, "body": "ok"}
```

Destinations versus DLQ: destinations carry the response payload and work for both success and failure on async invokes. A DLQ is the older failure-only path and only receives the original event after retries. Prefer destinations on new async functions. SQS event-source mappings use the queue's own redrive policy, not Lambda Destinations.

Partial batch response:

```python
def handler(event, context):
    failures = []
    for record in event["Records"]:
        try:
            process(record)
        except Exception:
            failures.append({"itemIdentifier": record["messageId"]})
    return {"batchItemFailures": failures}
```

The event source mapping must have `FunctionResponseTypes` set to `ReportBatchItemFailures`. Otherwise a thrown exception fails the whole batch.

### Task 3 — Use data stores in application development

| Skill | The fact |
| --- | --- |
| 1.3.1 High-cardinality partition keys | A hot partition throttles even when the table has spare capacity. Put the high-cardinality value in the partition key. Do not use `status=OPEN` as a partition key |
| 1.3.2 Consistency | DynamoDB `GetItem` / `Query` default to eventually consistent and cost half a read unit. `ConsistentRead=True` is strongly consistent and costs one unit. Strongly consistent reads stay in the same Region. Global tables are eventually consistent across Regions |
| 1.3.3 Query vs Scan | `Query` uses the key. `Scan` reads every item and then filters. A filter does not reduce read units. A scan in production is the bug |
| 1.3.4 Keys and indexes | Partition key plus optional sort key. GSI has its own partition and sort and its own throughput. LSI shares the table partition key, must be created with the table, and projects a different sort key. Sparse indexes omit items that lack the GSI key |
| 1.3.5 Serialize | Store JSON-friendly types through the document client. Do not store a raw Python object. Decimal, not float, for money in DynamoDB |
| 1.3.6 Maintain stores | Migrations, backups (PITR on DynamoDB, automated backups on RDS), IAM auth for RDS, Data API for Aurora Serverless when you do not want a VPC connection from Lambda |
| 1.3.7 Lifecycles | DynamoDB TTL deletes expired items. It is not immediate and it is not a backup. S3 lifecycle is a different feature |
| 1.3.8 Caching | ElastiCache or the DynamoDB Accelerator (DAX) or an in-process cache with a TTL. Cache invalidation is the hard part. Do not cache personalized responses on a shared key |
| 1.3.9 Specialized stores | OpenSearch for full text and log analytics. Do not make DynamoDB do relevance ranking |

Single-table design is a modeling choice. The guide says schema design is out of scope, then tests keys, query versus scan, and cardinality. You must read an access pattern and say whether the key supports it. You are not asked to invent a full ERD.

RDS from Lambda: use RDS Proxy or the Data API. Opening a connection per invoke exhausts `max_connections`. Store the proxy endpoint in configuration, the password in Secrets Manager.

---

## Domain 2 — Security (26%)

### Task 1 — Authentication and authorization

| Skill | What you implement |
| --- | --- |
| 2.1.1 Federated access | Cognito user pool for app users (JWT). Cognito identity pool when the app needs AWS credentials. IAM Identity Center is for workforce. SAML or OIDC to STS for a custom broker |
| 2.1.2 Bearer tokens | `Authorization: Bearer <jwt>`. API Gateway Cognito authorizer or a Lambda authorizer. Validate issuer, audience, expiry, signature. Do not decode a JWT and trust it without verification |
| 2.1.3 Programmatic access | Roles. `aws configure sso` for humans. Access keys are a last resort and they rotate. On compute, the metadata service provides the credentials |
| 2.1.4 Authenticated calls | The SDK signs with SigV4 from the default chain. API Gateway IAM auth checks `execute-api:Invoke` |
| 2.1.5 Assume a role | `sts.assume_role`. Pass `ExternalId` for a third party. Session tags and permission boundaries when a platform vends roles to tenants |
| 2.1.6 Permissions for principals | Identity policy allows the action. Resource policy must agree for cross-account. Least privilege means the resource ARN, not `*` |
| 2.1.7 Application-level authZ | Fine-grained checks in code or with Verified Permissions (Cedar). DynamoDB leading keys that include the tenant id so a query cannot cross tenants. IAM condition `dynamodb:LeadingKeys` |
| 2.1.8 Cross-service auth in microservices | Each service has its own role. Service A assumes nothing of Service B's role unless you designed role chaining. Pass a caller identity in a trusted header only after the authorizer set it. Do not let the client pick the tenant header unchecked |

Cognito tokens:

| Token | Use |
| --- | --- |
| ID token | The app learns who the user is. Claims. Do not send it to AWS APIs as an IAM credential |
| Access token | Call your API. Scopes and groups |
| Refresh token | Get new tokens. Store it carefully. It lives longer |

Temporary credentials from STS expire. The SDK refreshes role credentials. If you cache `AccessKeyId` in a global and ignore `Expiration`, the process breaks after an hour.

### Task 2 — Encryption

| Skill | What you implement |
| --- | --- |
| 2.2.1 At rest and in transit | TLS everywhere. SSE-KMS or SSE-S3 on buckets. Encrypted EBS and RDS. DynamoDB encryption at rest is on by default |
| 2.2.2 Certificates | ACM for public certs on API Gateway, ALB, CloudFront. AWS Private CA when the name is internal. Developers generate a dev cert. They do not run a production CA on a laptop and call it done |
| 2.2.3 Client-side vs server-side | Server-side: S3 encrypts as it writes. Client-side: you encrypt before `PutObject`. Client-side is required when AWS must not see plaintext. You then own key distribution |
| 2.2.4 Use keys | `kms.encrypt`, `kms.decrypt`, or the encryption context on S3. Encryption context must match on decrypt. It is logged in CloudTrail and it is not secret |
| 2.2.5 Dev certificates and SSH keys | `openssl` or `ssh-keygen` for local dev. EC2 key pairs are for the rare SSH path. Session Manager removes that need |
| 2.2.6 Cross-account encryption | The key policy must allow the other account. The caller still needs `kms:Decrypt` in their identity policy. A bucket policy that allows `s3:GetObject` fails if KMS denies |
| 2.2.7 Rotation | Enable automatic rotation on customer managed keys. Rotating a key does not re-encrypt old objects until they are rewritten. Disable a key and decrypt starts failing. That is the point of a disable during an incident, and it is also how you cause an outage |

```bash
aws kms create-key --description "orders" --key-usage ENCRYPT_DECRYPT --key-spec SYMMETRIC_DEFAULT
aws kms enable-key-rotation --key-id "$KEY_ID"
aws s3api put-bucket-encryption --bucket "$BUCKET" --server-side-encryption-configuration '{
  "Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "aws:kms", "KMSMasterKeyID": "'"$KEY_ID"'"}, "BucketKeyEnabled": true}]
}'
```

### Task 3 — Sensitive data in code

| Skill | What you implement |
| --- | --- |
| 2.3.1 Classification | PII, PHI, card data. Know which store is allowed to hold it. Log redaction is part of classification |
| 2.3.2 Encrypted environment variables | Lambda encryption with a customer managed key. `kms:Decrypt` on the execution role. Console still shows ciphertext, not the value, when you use a customer key correctly. Prefer Secrets Manager for values that rotate |
| 2.3.3 Secret services | Secrets Manager `GetSecretValue`. Cache the secret in memory with a TTL. Do not call KMS on every request if you can cache for a minute. Parameter Store `GetParameter` with `WithDecryption` for non-rotating config |
| 2.3.4 Sanitize | Strip tokens, passwords, and card numbers before you log the event. API Gateway access logs that print `$input.body` will leak passwords |
| 2.3.5 Masking | Return `****1234` from the API. Store the real value encrypted. Do not build the mask by logging the raw value "just in dev" |
| 2.3.6 Multi-tenant data access | Tenant id in the partition key. Authorizer injects the tenant. The handler ignores a tenant id supplied by the body when it disagrees with the token. IAM policy `dynamodb:LeadingKeys` = `${aws:PrincipalTag/tenant}` when you vend credentials per tenant |

```python
import boto3, json, os
_sm = boto3.client("secretsmanager")
_cache = {}

def get_secret(name):
    if name not in _cache:
        raw = _sm.get_secret_value(SecretId=name)["SecretString"]
        _cache[name] = json.loads(raw)
    return _cache[name]
```

The cache lives for the life of the execution environment. After a rotation, either let the environment recycle or cache with a timestamp and refresh.

---

## Domain 3 — Deployment (24%)

### Task 1 — Prepare artifacts

| Skill | What you produce |
| --- | --- |
| 3.1.1 Dependencies inside the package | `requirements.txt` installed into the artifact, or a container image, or a Lambda layer for the heavy shared bits. A layer is for reuse. It is not a dump of the entire company |
| 3.1.2 Directory layout | SAM: `template.yaml`, `src/`, `events/`. The handler path in the template matches the file |
| 3.1.3 Repositories | Git is the source. ECR holds images. CodeArtifact holds language packages. A zip in an S3 bucket is the Lambda deployment package CodeDeploy or CloudFormation points at |
| 3.1.4 Resource requirements | Memory and vCPU in the task definition or the function config. Set them from measurement, then from the SLO |
| 3.1.5 Environment config | AppConfig application, environment, configuration profile, hosted or S3 source, deployment strategy with bake time. Feature flags. Do not rebuild the artifact to change a timeout |

### Task 2 — Test in development environments

| Skill | What you run |
| --- | --- |
| 3.2.1 Test deployed code | Hit the deployed URL or invoke the alias. Read CloudWatch logs for that version |
| 3.2.2 Integration tests and mocks | Moto, LocalStack, or hand-written stubs for unit tests. A separate AWS account for integration. Do not mock so much that you never call AWS before production |
| 3.2.3 API Gateway stages | `dev`, `test`, `prod` stages. Stage variables point at different Lambda aliases or HTTP endpoints. A stage is not a separate API unless you want separate APIs |
| 3.2.4 Stack updates | `sam deploy --config-env staging` with a different stack name and parameter file. CloudFormation change sets show the delta first |
| 3.2.5 Event-driven tests | Put a test event on the bus with a `source` your rule matches only in dev. Or invoke with `sam local generate-event sqs` |

### Task 3 — Automate deployment testing

| Skill | What you automate |
| --- | --- |
| 3.3.1 Test events | JSON files checked into `events/`. `sam local generate-event` |
| 3.3.2 APIs to many environments | Same template, different parameters, different stages |
| 3.3.3 Approved versions | Lambda aliases (`live` points at version 12). Image tags that are not `latest` in production. Amplify branches per environment. The guide's 2.1 revision removed Copilot from the in-scope list. Aliases, image tags, and Amplify branches remain |
| 3.3.4 IaC | SAM templates and CloudFormation. CDK is in scope on DVA (it is out of scope on SAA). `cdk deploy` still ships a CloudFormation stack |
| 3.3.5 Per-service environments | API Gateway stages, Lambda aliases, DynamoDB tables named with the stage, separate stacks |
| 3.3.6 Q Developer for tests | Generate the test, then read it. A test that mocks the function under test is not a test |

### Task 4 — CI/CD services

You use the pipeline. The guide says designing the pipeline is out of scope. Questions still show CodeCommit/GitHub to CodeBuild to CodeDeploy or SAM and ask what happens.

| Skill | The behavior |
| --- | --- |
| 3.4.1 Lambda packaging | Zip plus the runtime, container image from ECR, or SAM build. Image lambdas suit large dependencies. Zip plus a layer suits shared libraries under the layer size quota |
| 3.4.2 Stages and custom domains | A custom domain maps base path mappings onto stages. ACM cert in the same Region for regional APIs, in us-east-1 for edge-optimized |
| 3.4.3 Update templates | Change the template, deploy, let CloudFormation do the update. A stack policy can prevent replacement of the database |
| 3.4.4 Manage environments | Parameters and mappings. Do not fork the template per environment |
| 3.4.5 Deployment strategies | All-at-once, rolling, blue/green, canary, linear. See the table below |
| 3.4.6 Commit invokes the pipeline | A webhook or an EventBridge connection from the repo. CodeBuild `buildspec.yml` runs test then package |
| 3.4.7 Orchestrated workflows | CodePipeline stages: source, build, deploy-staging, approval, deploy-prod. Step Functions is the application workflow. Do not confuse them |
| 3.4.8 Rollback | CodeDeploy automatic rollback on a CloudWatch alarm or a failed hook. Lambda alias points back at the previous version. CloudFormation stack rollback on a failed update |
| 3.4.9 Labels and branches | `main` deploys to prod only through the pipeline. Tags mark releases. `latest` as a production image tag loses the question |
| 3.4.10 Runtime configuration | API Gateway stage variables read inside the integration or passed to Lambda. AppConfig for flags. Changing a stage variable does not require a new Lambda zip |
| 3.4.11 Configure strategies | Blue/green, canary, rolling. You must match the strategy to the compute |

| Strategy | Lambda | ECS / EC2 CodeDeploy | Rollback |
| --- | --- | --- | --- |
| All-at-once | Alias jumps to 100% of the new version | Every instance updates | Point the alias back, or redeploy the old revision |
| Canary | 10% for N minutes, then 100%. CloudWatch alarms abort | A slice of traffic via the listener | Automatic if the alarm fires |
| Linear | 10% every N minutes | Same idea on Lambda traffic shifting | Same |
| Blue/green | Weighted alias, or two API stages and a domain switch | New task set, then the listener swaps. Needs room for both | Swap back. The old tasks are still there until you terminate them |
| Rolling | Not the Lambda model | Replace a batch of instances | Stop and redeploy the previous revision. In-flight batch may be mixed |

`buildspec.yml` minimum:

```yaml
version: 0.2
phases:
  install:
    runtime-versions:
      python: 3.12
  build:
    commands:
      - pip install -r requirements.txt -t package
      - sam build
      - sam deploy --no-confirm-changeset --no-fail-on-empty-changeset
artifacts:
  files:
    - packaged.yaml
```

SAM template fragment you must be able to read:

```yaml
Resources:
  Api:
    Type: AWS::Serverless::Function
    Properties:
      Handler: app.handler
      Runtime: python3.12
      CodeUri: src/
      MemorySize: 512
      Timeout: 10
      Environment:
        Variables:
          TABLE: !Ref Orders
      Policies:
        - DynamoDBCrudPolicy:
            TableName: !Ref Orders
      Events:
        GetOrder:
          Type: Api
          Properties:
            Path: /orders/{id}
            Method: get
```

`DynamoDBCrudPolicy` is still broad. Production templates narrow the actions. The exam accepts the SAM policy template when the stem says least operational overhead and the table is the one just created.

---

## Domain 4 — Troubleshooting and optimization (18%)

### Task 1 — Root cause analysis

| Skill | Where you look |
| --- | --- |
| 4.1.1 Debug defects | Reproduce with the event JSON. Log `aws_request_id`. One request id ties API Gateway, Lambda, and X-Ray together |
| 4.1.2 Metrics, logs, traces | Metric says it is slow. Log says which branch. Trace says which downstream |
| 4.1.3 Query logs | CloudWatch Logs Insights. `filter @message like /ERROR/ \| stats count() by bin(5m)` |
| 4.1.4 Embedded metric format | Print a structured log that CloudWatch extracts as a metric. No `PutMetricData` call required. You still need the EMF library or the correct JSON |
| 4.1.5 Dashboards | CloudWatch dashboard, Lambda insights, Container Insights. A dashboard is not an alarm. Add the alarm |
| 4.1.6 Deployment failures | CloudFormation events, CodeBuild log, CodeDeploy deployment hook logs, ECS `StoppedReason`, Lambda `LastUpdateStatusReason` |
| 4.1.7 Integration bugs | Wrong event shape, missing permission (`AccessDenied` in the log), timeout to a VPC resource with no route, DDB `ConditionalCheckFailedException`, SQS message still in flight because you never deleted it |

Permission errors are not fixed by making the resource public. They are fixed by the missing action on the role that the log names.

### Task 2 — Instrument code

| Skill | What you add |
| --- | --- |
| 4.2.1 Logging vs monitoring vs observability | Logs are events. Metrics are numbers over time. Traces are one request across services. Observability is being able to ask a question you did not pre-aggregate |
| 4.2.2 Logging strategy | Structured JSON. Levels. Correlation id. No secrets. Retention set so you do not pay forever |
| 4.2.3 Custom metrics | EMF or `PutMetricData`. High-cardinality dimensions (user id) explode cost. Use a metric for the SLO and a log for the user id |
| 4.2.4 Annotations | X-Ray annotations are indexed (`annotation.orderId`). Metadata is not indexed. Put the value you will filter on into an annotation |
| 4.2.5 Alerts | Alarm on the SLO, on DLQ depth, on deployment failure, on quota. SNS or EventBridge to the ticket system |
| 4.2.6 Tracing | Enable X-Ray on API Gateway, Lambda, and the SDK (`patch` in Python, or the X-Ray SDK / ADOT). One trace header (`X-Amzn-Trace-Id`) propagates |
| 4.2.7 Structured logging | JSON with `level`, `message`, `requestId`, `tenant`. Logs Insights parses JSON fields automatically |
| 4.2.8 Health checks | ALB target health, ECS readiness versus liveness. Readiness fails when dependencies are down so the load balancer stops sending traffic. Liveness fails when the process is wedged so the task restarts. Do not use the same check for both if a dependency blip would then kill every task |

```python
import json, logging, os
logger = logging.getLogger()
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

def log(level, message, **fields):
    logger.info(json.dumps({"level": level, "message": message, **fields}))
```

### Task 3 — Optimize

| Skill | The move |
| --- | --- |
| 4.3.1 Concurrency | Lambda account concurrency (default 1,000 per Region, adjustable) is a pool. Reserved concurrency isolates a function and also caps it. Unreserved functions share what is left. Provisioned concurrency is pre-initialized environments and costs money while idle |
| 4.3.2 Profile | Duration, billed duration, init duration, iterator age on streams, ECS CPU and memory vs the task limit |
| 4.3.3 Minimum memory and CPU | Lambda: raise memory until duration stops falling. ECS: the task size that stays under 80% at peak. EC2: the family that matches the bottleneck, then the size |
| 4.3.4 Subscription filters | SNS filter policies so a subscriber does not receive every message. EventBridge rule patterns. SQS does not filter on receive. Filter before the queue, or use Lambda event filtering |
| 4.3.5 Cache on request headers | API Gateway cache key includes headers you name. CloudFront cache policy. If you forget `Authorization` in the cache key, one user receives another user's response. If you include it, you barely cache |
| 4.3.6 Application caching | ElastiCache, DAX, or a short in-memory TTL. Cache the read that dominates. Writes go to the database and then invalidate |
| 4.3.7 Resource usage | Right-size. Graviton (`arm64` Lambda, Graviton Fargate) when the runtime supports it and the stem wants price-performance |
| 4.3.8 Analyze performance | X-Ray service map. The slow segment is the one you fix. Adding cache in front of a fast function does nothing for a slow query |
| 4.3.9 Logs as the bottleneck finder | A log line with duration around the SDK call shows whether DynamoDB or your JSON parsing is the cost |

---

## In-scope services (DVA-C02)

**Analytics.** Athena, Kinesis, OpenSearch Service.

**Application integration.** AppSync, EventBridge, SNS, SQS, Step Functions.

**Compute.** EC2, Elastic Beanstalk, Lambda.

**Containers.** ECR, ECS, EKS. Fargate is how you run ECS and EKS without servers. DVA-C03 names Fargate explicitly. Treat it as required knowledge now.

**Database.** Aurora, DynamoDB, ElastiCache, RDS.

**Developer tools.** Amplify, CloudShell, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, X-Ray, Amazon Q Developer.

**Management.** AppConfig, CDK, CloudFormation, CloudTrail, CloudWatch, CLI, Systems Manager.

**Networking.** API Gateway, CloudFront, Elastic Load Balancing, Route 53, VPC.

**Security.** Cognito, IAM, KMS, Secrets Manager, STS, WAF.

**Storage.** EBS, EFS, S3.

## Out of scope on the DVA-C02 guide

QuickSight, Chime, Connect, WorkMail, AppStream 2.0, WorkSpaces, GameLift, Polly, Rekognition, AWS Managed Services, Elastic Transcoder, Application Discovery Service, Application Migration Service, Shield Standard, Shield Advanced, Snow Family, Storage Gateway.

Removed from in-scope at version 2.1: AWS Copilot, Amazon CodeGuru. Removed from the out-of-scope list (so they are no longer called out as excluded): Device Farm, Lex, Service Catalog, DMS. Do not build a study week on them. Know DMS is a database migration tool if a snippet mentions it.

## Where the rest of the developer study lives

| Need | File |
| --- | --- |
| Scenarios for each domain | `05-dva/01-domain-1-development.md` through `04-domain-4-troubleshooting.md` |
| SDK patterns | `05-dva/05-sdk-patterns.md` |
| DynamoDB for developers | `05-dva/06-dynamodb-for-developers.md` |
| Lambda | `05-dva/07-lambda-deep-dive.md` |
| Exercises | `05-dva/08-dva-exercises.md` |
| Timed original exam | `05-dva/09-dva-practice-exam.md` |
| DVA-C03 additions | `05-dva/10-dva-c03-new-skills.md` and `00-start-here/06-dva-c03-transition.md` |
