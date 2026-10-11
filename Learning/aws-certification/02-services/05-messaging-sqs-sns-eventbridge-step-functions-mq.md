# Messaging: SQS, SNS, EventBridge, Step Functions, MQ, AppFlow

SAA 2.1. SAP 2.4 and 4.4. DVA 1.1.8 and 1.1.12. SAP-C03 treats Step Functions as the durable workflow service.

Official:

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html
- https://docs.aws.amazon.com/sns/latest/dg/welcome.html
- https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html
- https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html
- https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/welcome.html
- https://docs.aws.amazon.com/appflow/latest/userguide/what-is-appflow.html

## Pick one

| Sentence | Service |
| --- | --- |
| Buffer between two services. One consumer group. Retries | SQS |
| One event, many independent consumers, push | SNS, usually with an SQS queue per consumer |
| React to an AWS or SaaS event, filter on content, archive, replay, schema | EventBridge |
| A multi-step business process, waits, human approval, compensation | Step Functions |
| The app already speaks JMS, AMQP, MQTT, OpenWire, STOMP | Amazon MQ (ActiveMQ or RabbitMQ) |
| Copy data between a SaaS and AWS on a schedule, little code | AppFlow |
| A workflow inside one service's console (Glue workflows, SFN is still the general answer) | Step Functions |
| Email or SMS to a person | SNS, or SES when the stem is a real email product with bounce handling |
| Decouple a monolith's background work | SQS. Not a second database table polled by cron |

Choreography is EventBridge: each service emits and nobody calls the next one. Orchestration is Step Functions: one state machine calls the steps and knows the status. Fanout is SNS to many SQS queues. Do not put five consumers on one SQS queue and expect each message to be processed by all five. A standard queue message is received by one consumer and then deleted. Competing consumers share work. They do not each get a copy.

## SQS

| | Standard | FIFO |
| --- | --- | --- |
| Order | Best effort | Strict inside a message group |
| Delivery | At least once | Exactly-once processing with the deduplication id, still write idempotent consumers |
| Throughput | Nearly unbounded | High with batching and high-throughput mode, still the constrained option |
| When | Default | Payments, ordered commands, anything that breaks if B runs before A |

Visibility timeout hides a message while a consumer works. If the consumer crashes, the message returns. If the timeout is shorter than the work, a second consumer runs the same message. Set the timeout above the worst-case processing time, and heartbeat it with `ChangeMessageVisibility` for long jobs. Delete the message only after the side effect commits.

Receive wait time of 20 seconds is long polling. Short polling returns early and you pay for empty receives.

A redrive policy sends a message to a DLQ after `maxReceiveCount`. Alarm on `ApproximateNumberOfMessagesVisible` of the DLQ. A DLQ without an alarm is a bin you never look at.

```bash
aws sqs create-queue --queue-name orders-dlq
aws sqs create-queue --queue-name orders \
  --attributes 'VisibilityTimeout=60,ReceiveMessageWaitTimeSeconds=20,RedrivePolicy="{\"deadLetterTargetArn\":\"ARN\",\"maxReceiveCount\":\"5\"}"'
aws sqs send-message --queue-url "$URL" --message-body '{"id":"1"}'
aws sqs receive-message --queue-url "$URL" --wait-time-seconds 20 --max-number-of-messages 10
aws sqs delete-message --queue-url "$URL" --receipt-handle "$HANDLE"
```

FIFO deduplication: a `MessageDeduplicationId`, or content-based deduplication, over a 5-minute window. A message group id is the order scope. One group id for every message serializes the whole queue. Use the order id or the user id as the group.

Fair queues and message group isolation have been added over time so one noisy tenant does not block others. If the stem says one tenant's backlog delays everyone, you want per-tenant group ids, not one queue-wide group.

SQS has no subscriber filter. Filter before send, use SNS filter policies, or use Lambda event filtering on the mapping.

## SNS

Topics push to SQS, Lambda, HTTP, email, SMS, mobile push, and Firehose. Consumers do not poll. If the HTTP endpoint is down, SNS retries and then can land in a DLQ.

Filter policies on a subscription drop messages that do not match attributes. That is DVA skill 4.3.4. Put the filter attribute on the message. A filter that requires a body parse is the EventBridge pattern, not an SNS attribute filter, unless you use payload-based filtering and accept its limits.

FIFO topics feed FIFO queues and keep order. A standard topic to a FIFO queue is not the ordered design.

Fanout pattern: the producer publishes once. Each consumer has a queue subscribed to the topic. One slow consumer does not block the others because each queue has its own backlog.

```bash
aws sns create-topic --name orders
aws sns subscribe --topic-arn "$TOPIC" --protocol sqs --notification-endpoint "$QUEUE_ARN" \
  --attributes '{"FilterPolicy":"{\"type\":[\"created\"]}"}'
aws sns publish --topic-arn "$TOPIC" --message '{"id":"1"}' \
  --message-attributes 'type={DataType=String,StringValue=created}'
```

## EventBridge

A bus. The default bus receives AWS service events. A custom bus receives your events. A partner bus receives SaaS events.

A rule matches a pattern and sends to a target: Lambda, SQS, Step Functions, API destination, Kinesis, and others. Rules are independent. One event can match many rules. That is choreography.

| Feature | Why it wins the stem |
| --- | --- |
| Archive and replay | The consumer was deployed broken and you must reprocess a day of events |
| Schema registry | Producers and consumers share a contract |
| API destinations | Call a third-party HTTPS API with a rate limit, without a Lambda |
| Scheduler | One-time or cron invocations. Replaces a CloudWatch Events rule you would have written years ago, and replaces cron on an instance |
| Pipes | Point-to-point from SQS, Kinesis, DynamoDB Streams, or Kafka to a target, with filter and enrichment, without you running a Lambda just to move the message |
| Cross-account buses | A central bus in the security or platform account. SAP multi-account eventing |
| Global endpoints | Fail over event ingestion to a second Region |

```bash
aws events put-rule --name orders-created --event-bus-name orders \
  --event-pattern '{"source":["orders.app"],"detail-type":["OrderCreated"]}'
aws events put-targets --rule orders-created --event-bus-name orders \
  --targets "Id=1,Arn=$QUEUE_ARN"
aws scheduler create-schedule --name nightly --schedule-expression 'cron(0 2 * * ? *)' \
  --flexible-time-window Mode=OFF \
  --target "{\"Arn\":\"$FN_ARN\",\"RoleArn\":\"$ROLE_ARN\"}"
```

At-least-once still applies. Consumers stay idempotent.

## Step Functions

| Workflow type | Duration | Use |
| --- | --- | --- |
| Standard | Up to a year. Exactly-once workflow execution. Priced per transition | Orders, approvals, anything a human waits on |
| Express | Up to five minutes. High volume. At-least-once or at-most-once depending on sync or async | Per-request orchestration inside a hot path |

States you must recognize: Task, Choice, Parallel, Map (fan-out over an array, including distributed Map over an S3 object list), Wait, Succeed, Fail, and a Catch/Retry. Service integrations call DynamoDB, SQS, ECS, Glue, and hundreds of others without a Lambda in the middle. Use a Lambda only when you have code that is not an API call.

A callback pattern (`.waitForTaskToken`) parks the workflow until a human or an external system returns the token. That is the SAP-C03 human-oversight pattern for an AI action: the model proposes, the workflow waits, a person approves, the workflow continues.

```bash
aws stepfunctions create-state-machine --name orders --type STANDARD \
  --role-arn "$ROLE" --definition file://machine.asl.json
aws stepfunctions start-execution --state-machine-arn "$SM" --input '{"orderId":"1"}'
```

Do not use Step Functions as a queue. It is the coordinator. SQS is the buffer in front of workers the state machine runs.

## Amazon MQ and AppFlow

MQ is the migration answer for a broker you cannot rewrite this quarter. It is not the green-field answer. You still patch and size the broker, even though AWS runs the nodes. ActiveMQ for JMS and features. RabbitMQ when that is the protocol the app speaks.

AppFlow moves Salesforce, SAP, Slack, and similar sources into S3, Redshift, or EventBridge on a schedule or an event. It loses to a custom Lambda when the transform is unique and already written. It wins "least code" against a team about to build a SaaS connector.

## Exercises

1. An order must be billed, then shipped, and a human must approve refunds over 500 USD. The flow can last three days. Which service, and which workflow type?
2. Five microservices all need a copy of `OrderCreated`. One of them is down for an hour and must catch up without the others waiting. Draw the services.
3. A FIFO queue uses one message group id for every message. Throughput collapses. What do you change, and what invariant must you keep?
4. A Lambda SQS consumer deletes the message and then the database commit fails. What do users observe, and what is the order of operations?
5. A SaaS sends webhooks today to a Lambda that crashes under bursts. You may change the ingestion. What do you put in front, if you need retries and a backlog rather than a dead webhook?

## Answers

1. Standard Step Functions, with a service integration or Lambda for bill and ship, and a callback task token (or a manual approval step) for the refund.
2. The producer publishes to SNS or, if you need filtering and archive, to EventBridge. Each service has its own SQS queue. The down service drains its queue when it returns. The others are unaffected.
3. A message group id per order or per entity that actually requires order. Messages in different groups run in parallel. Order inside one order id stays.
4. The work is lost. SQS will not redeliver a deleted message. Commit the database first, then delete. Or use a transaction outbox. If the commit fails, do not delete, and let the visibility timeout return the message.
5. API Gateway or a Lambda that only does `SendMessage`, then SQS, then the worker. The webhook gets a fast 200. The backlog absorbs the burst. EventBridge API destinations are the other direction (you call out). For inbound bursts, the queue is the shock absorber.

## SQS

Standard queues are at-least-once and best-effort ordered. The consumer is idempotent. FIFO queues are ordered inside a message group and deduplicated for a window (the deduplication id, or content-based deduplication). Throughput collapses if every message shares one group id, because one group is a single lane. Use one group per entity that actually needs order, such as an order id. High-throughput FIFO raises the ceiling and does not remove the group-id rule.

Visibility timeout hides a message after a receive. It must be longer than the work. A message that becomes visible mid-process is a second consumer. The timeout can be extended with `ChangeMessageVisibility` if the work is long. Retention defaults to 4 days and can be 14. A message you never delete sits until retention expires. That is not a DLQ. A DLQ is a redrive policy: after `maxReceiveCount` receives, move it. Alarm on DLQ depth. A DLQ nobody reads is a bin.

Long polling (`WaitTimeSeconds` up to 20) avoids empty receives. Short polling is the older expensive way to learn the queue is empty. Delay queues and per-message delay hold a message before it becomes visible. That is "wait 30 seconds," not a workflow. A 256 KB payload limit is the long-standing exam number. Larger bodies go to S3 and the message carries the key. Confirm the current quota if a stem quotes a different size.

The consumer deletes after a successful commit. A conditional write that finds the row already present is success. A throttle is not. Do not delete and then write.

## SNS and EventBridge

SNS is fanout. One topic, many subscribers. Each subscriber that needs its own retry gets its own SQS queue. A filter policy drops messages before a subscriber is invoked, which saves invocations. SNS FIFO exists when the fanout must stay ordered. Email and SMS subscribers are for humans. They are a bad place to put a payload you cannot lose.

EventBridge is a bus. Rules match source, detail-type, and content. Targets include Lambda, SQS, Step Functions, API destinations, and other buses. Archive and replay are why you pick it over SNS when you must reprocess yesterday. A schema registry is the contract. Pipes connect a source (SQS, stream, DynamoDB) to a target with optional filter and enrichment, without you running a Lambda whose only job is to forward. Cross-account delivery uses resource policies and, often, a bus in the receiving account.

S3 can notify EventBridge, SNS, SQS, or Lambda. EventBridge when many teams react. SQS when one worker needs a backlog.

## Step Functions

Standard workflows last up to a year, are exactly-once in the execution sense you can audit, and are the three-day approval. Express workflows are high rate and short, and they are not the history you read next week. A state machine is orchestration. EventBridge is choreography. A Lambda that calls four other Lambdas is neither. It is a distributed monolith with no state when the caller dies.

States you must recognize: Task, Choice, Wait, Parallel, Map, Succeed, Fail. A callback pattern (`.waitForTaskToken`) is the human approval or the external system that later calls `SendTaskSuccess`. The token is the correlation. Service integrations call DynamoDB, SQS, and ECS without a wrapper Lambda. Retries and catchers belong on the state, with backoff, so a throttle does not fail the execution on the first try. The input to the next state should be keys and ids, not a multi-megabyte document. The document lives in S3.

## MQ and AppFlow

Amazon MQ is ActiveMQ or RabbitMQ for a protocol you cannot change this quarter: JMS, AMQP. You still size and patch. It is not the green-field queue. SQS is cheaper and less to run when you can change the client. AppFlow is the least-code path from a named SaaS product into S3, Redshift, or EventBridge. A custom transform you already operate can stay a Lambda. A team about to write a Salesforce connector should look at AppFlow first.

## More exercises

6. A message is received, the worker crashes, and 30 seconds later another worker gets it. What setting made that possible, and what do you set instead if the work takes two minutes?
7. EventBridge or SNS: you must replay Friday's events after a bad deploy, and you also want a content filter.
8. A Map state fans out over 50,000 keys in S3. You pass the file bytes in the state input. What do you pass?
9. FIFO deduplication makes a retry inside the window disappear. The first attempt failed after the message was deleted. What is wrong with relying on deduplication alone?
10. A topic has three SQS subscribers and no filter. One subscriber is a debug queue that now receives every order, including ones with card numbers. What do you change first?

## Answers

6. The visibility timeout is 30 seconds or less. Set it above two minutes, and above the consumer's timeout, so the message stays hidden until the worker finishes or fails cleanly.
7. EventBridge, with an archive. SNS can fan out and filter. It is not the replay log. You can put SQS on the target either way.
8. The bucket and the key. State payloads are small. The Map iteration reads the object. Stuffing the bytes into the execution history is how you hit the limit and the bill.
9. Deduplication hides a second send. It does not redo a message you already deleted. Do not delete until the work commits. Deduplication is a bonus on FIFO, not the idempotency of the write.
10. A filter policy so the debug queue does not get production payment events, and stop putting card numbers on the bus at all. Encryption does not fix a subscriber that is allowed to receive the message. The filter and the payload design do.
