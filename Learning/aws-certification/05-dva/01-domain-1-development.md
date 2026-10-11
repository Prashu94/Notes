# DVA Domain 1 — Development with AWS services (32%)

Skills 1.1.1 through 1.3.9. The blueprint has the skill table. This file is how those skills show up in a snippet.

Companion code: `05-sdk-patterns.md`, `06-dynamodb-for-developers.md`, `07-lambda-deep-dive.md`.

## Patterns the stem names

| Word | Meaning in code |
| --- | --- |
| Monolith | One deployable. A change ships the whole thing. Fine until the stem says independent scaling |
| Microservices | Separate deployables. Each has its own role. Do not share one database password across all of them |
| Choreography | EventBridge or SNS. No central caller |
| Orchestration | Step Functions. The state machine knows the step |
| Fanout | SNS to one queue per consumer |
| Stateless | The handler keeps no session in a global that must survive another environment |
| Sync | The caller waits. API Gateway proxy, `RequestResponse` |
| Async | SQS, SNS, EventBridge, Lambda `Event`. Retries exist. Your write must be idempotent |

A global dict on Lambda is a cache for the life of that environment. It is not a session store and it is not shared across environments. Two concurrent invocations of the same environment do not happen. Two environments do.

## SDK rules that decide items

Paginate. Set timeouts. Retry throttling with jitter. Do not retry `AccessDenied`. Do not construct the client with a hard-coded key. Use the default chain. Idempotency tokens stay stable across the retry of the same business action.

Pagination bugs look like "the script reports success and misses objects." The missing field is the continuation token.

## API Gateway items

Proxy integration: you return `statusCode`. A 200 from your code is what the client sees, even if your downstream failed, unless you set 502 yourself. Request validators reject bad bodies before Lambda runs. Mapping templates are the REST feature. Stage variables are how one API points dev and prod at different aliases.

## Streams

Kinesis and DynamoDB Streams to Lambda. Turn on partial batch failure. Filter at the event source so you do not pay for invokes you will drop. Checkpoint by succeeding the batch. Iterator age is the "you are behind" metric.

## Data

Query, do not scan, when the key can answer it. A filter does not reduce read units. High-cardinality partition keys. Consistent read when the next action depends on a write you just made in the same Region. Cache with a TTL. OpenSearch when the stem says full text. RDS Proxy or the Data API when Lambda would open too many SQL connections.

## Q Developer

Use it to draft the handler and the test. Read both. A test that mocks the function under test is not a test. A suggestion that logs the secret is a defect you delete.

## Exercise

An order handler does `requests.post` to the shipping URL, then writes the order, then returns 200. Shipping times out and the user is charged with no order row. Rewrite the sequence in three steps using SQS and a conditional DynamoDB put. Do not look at the messaging chapter until you have a sequence.

Answer: enqueue a message that contains the order id, put the order with `attribute_not_exists` on the key, return. The consumer calls shipping and deletes the message only after shipping accepts it. A second delivery sees the existing order and does not double-charge. The HTTP handler does not wait on shipping.

## What "development" means on this exam

You are not designing a landing zone. You are choosing the API call, the data shape, and the failure behavior of code that already has a place to run. The stem shows a snippet or describes one. The wrong answers are a different service that a solutions architect would pick for a neighboring sentence, or the same service used with the wrong consistency, the wrong status code, or a client built inside the hot path.

Skills 1.1 are the application patterns. Skills 1.2 are Lambda, and they are taught again in `07-lambda-deep-dive.md` because the event shapes are where people lose points. Skills 1.3 are the data stores, taught again in `06-dynamodb-for-developers.md`. This file is the map of those skills onto a decision.

## Patterns, with the code-level consequence

A monolith is one deployable unit. One bug rolls the whole process back, and one spike scales the whole process. That is acceptable until the stem says the inventory module must scale independently of the web process, or teams must deploy without waiting for each other. Microservices are separate deployables, each with its own role and its own data. Sharing one database user across all of them fails least privilege and makes the "independent deploy" claim false, because a migration in one service locks the shared tables.

Choreography means no central caller. Something emits an event. EventBridge rules or SNS subscriptions decide who cares. Adding a consumer is a new rule, not a change to the producer. Orchestration means a state machine knows the next step. Step Functions is that machine. Use it when the process has a wait, a choice, a compensation, or a human approval. Use choreography when the steps are independent reactions to a fact that already happened ("an order was placed"). A Lambda that calls four other Lambdas with `RequestResponse` and no state machine is a distributed monolith. If the third call fails, you have no record of which step to retry.

Fanout is one message, many consumers, each with a buffer. SNS to a queue per consumer, or EventBridge to a queue per rule. A single SQS queue with two competing consumers is not fanout. Each message is processed by one of them.

Stateless means the handler does not keep the user's session in a global that another environment cannot see. A global that caches a configuration or a database client is correct. A global that stores `current_user` is a bug the moment the environment is reused for the next invocation. Lambda does not run two invocations on the same environment at the same time. It does run many environments. Anything you needed to share belongs in DynamoDB, ElastiCache, S3, or the event itself.

Synchronous is the caller waiting. API Gateway proxy, ALB target, `InvocationType=RequestResponse`. The status code you return is the status code the caller sees. Asynchronous is SQS, SNS, EventBridge, S3 events, or Lambda `Event`. The caller has already been told the work was accepted. Retries will happen. The write is idempotent or you will double-charge.

## Idempotency, because every retry item is this

A retry is a second delivery of the same business action. The second delivery must not create a second order, a second charge, or a second email if the first one succeeded, and it must complete the work if the first one failed before the commit.

The DynamoDB form is a conditional put: `attribute_not_exists` on the key that is the business id. `ConditionalCheckFailedException` means the row is already there. Treat that as success in the consumer, then delete the message. The Stripe-style form is an idempotency key stored with the result, so the second call returns the first result. The SQS FIFO form is a message deduplication id, which covers a five-minute window and does not replace the conditional write if the consumer can fail after the deduplication window or if you are on a standard queue.

Delete the message after the successful write. Delete it also when the conditional check says the write already happened. Do not delete it when the write failed for a throttle or a timeout. That failure must become a retry. If you catch all exceptions and delete anyway, you have built a queue that loses work and looks healthy.

## API surface you are expected to shape

API Gateway proxy integration gives your function the HTTP request and expects `{statusCode, headers, body}`. `body` is a string. If you return a Python dict as the body, the client gets something that is not your JSON. If you return 200 because the code reached the last line, the client and the alarm think the dependency failure was a success. Set 502 or 503 when the downstream failed and you did not queue the work. Set 202 when you did queue it. Set 400 when the body failed validation you chose to do in the function. Prefer a request validator on the REST API so the bad body never invokes the function.

Stage variables are how one API definition points the dev stage at one Lambda alias and the prod stage at another, or how it passes a table name. They are not a secret store. A secret in a stage variable shows up in the API configuration to anyone who can read the API.

Mapping templates are the REST feature for reshaping the request before it reaches the integration. HTTP APIs are cheaper and have fewer of those features. Pick REST when the stem names API keys, usage plans, request validation, or AWS service integrations of the older kind. Pick HTTP APIs when it is a Lambda proxy and cost is the point. An ALB in front of Lambda is the answer when the same balancer already serves instance targets and the API features are not required.

AppSync is the GraphQL answer. The client asks for a shape. Resolvers read DynamoDB or call Lambda. It is not the default for a CRUD JSON API the team already expressed as REST. It is the answer when the stem says GraphQL, or when different clients need different slices of the same data and they named that problem.

## Streams and batches

Kinesis and DynamoDB Streams are not SQS. The unit of retry can be a batch, and a poison record blocks progress on that shard until you bisect, set a maximum record age, or send the failure to an on-failure destination. Iterator age is the "you are behind" metric. It is not a queue depth. You scale consumers and shards. You do not add a visibility timeout. Streams do not have one.

SQS event-source mappings have visibility timeouts and partial batch failure. Turn `ReportBatchItemFailures` on and return the failed message ids. Filter the event source so you do not pay for invocations you will drop. The filter belongs on the mapping or on the EventBridge rule, not as the first line of a function that has already been billed.

S3 event notifications can target Lambda, SQS, SNS, or EventBridge. EventBridge is the answer when more than one team needs to react and you want archive. SQS is the answer when the processor must have a backlog and a DLQ. Lambda direct is the answer when the work is small and a failed invocation's retry policy is enough.

## Data access, the developer cut

Query on a key you designed. A scan with a filter still reads the items. A GSI is a second key shape you pay to write. A sparse index omits items that do not have the attribute, which is how "only open orders" stays cheap. Transactions are for a small set of items that must all commit. They are not a join. Single-table design shows up as one table with a composite key (`pk`, `sk`) rather than ten tables. You should be able to read an item and say which access pattern it serves.

SQL from Lambda: RDS Proxy or the Aurora Data API (the HTTP data API) so you do not open a connection per invocation. A global SQL connection created at import time is still one connection per environment, and a burst of environments is a burst of connections. The proxy is the pool. The Data API has no persistent connection at all and has its own limits. Secrets Manager holds the password. The function does not.

ElastiCache is the hot key and the session. The function in a VPC reaches it. The security group allows the function. There is no public endpoint story you should design.

OpenSearch is the full-text path. You do not `scan` DynamoDB to implement search.

## Q Developer and the tests

Q Developer drafts handlers, tests, and transformations. You accept a draft after you have run it and after you have removed anything that looks like a secret from the prompt. A test that mocks the function under test proves the mock. A test that mocks the SDK client and asserts the parameters you passed to `put_item` is a unit test. A test that runs against the production table is not a unit test. `sam local invoke` with a fixture event is the local check. A separate stage or account is the integration check.

C03 adds Kiro as a tool that may draft the same artifacts. The rule does not change. The tool is not an authorization boundary. The role is.

## More exercises

1. A function writes a global `user_id` from the first event. Why does a later invocation see the wrong user, and where does the id belong?
2. `list_objects_v2` is called once. The bucket has 50,000 keys. What does the script miss, and what is the field or the API you use instead?
3. The handler returns `{"message": "failed"}` with the default status 200. What does API Gateway send the client?
4. Two consumers read one SQS queue. Each message must be processed by both. What do you insert?
5. A Step Functions state passes a 6 MB document to the next state. What do you pass instead, and where does the document sit?

## Answers

1. The environment was reused. Globals survive across invocations. Keep `user_id` in a local variable, and keep durable session state in DynamoDB or ElastiCache.
2. Every page after the first. `IsTruncated` and `NextContinuationToken`, or a paginator. The script can exit zero and still be wrong.
3. HTTP 200 with a body that says failed. The proxy integration trusts `statusCode`. Set 500 or 503.
4. SNS or EventBridge in front, with one queue per consumer. Two consumers on one queue split the messages. They do not clone them.
5. Pass the S3 key and the bucket. The 256 KB-class state limit, and the cost of pushing the document through every transition, both reject the inline document. The exact state payload limit is in `06-reference/service-limits-and-quotas.md`. The pattern does not depend on memorizing the byte count if the stem says the document is large.
