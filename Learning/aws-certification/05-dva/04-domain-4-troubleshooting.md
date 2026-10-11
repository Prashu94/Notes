# DVA Domain 4 — Troubleshooting and optimization (18%)

Skills 4.1 through 4.3. The question gives you a symptom and a log line. You name the cause and the change, not a new architecture.

## Where you look

| Symptom | First place |
| --- | --- |
| 502 from API Gateway | Lambda error, timeout, or the integration timeout near 29 seconds. The request id joins the API log and the function log |
| `AccessDenied` in the function log | The execution role, the resource policy, or KMS. Not "make the bucket public" |
| `ExpiredToken` | Cached STS credentials past `Expiration` |
| Messages back on the queue | Visibility timeout shorter than the work, or you never deleted, or you returned the whole batch as failed |
| Iterator age climbing | Consumers behind. Shards, concurrency, or a poison record |
| `InitDuration` large, `Duration` fine | Cold start. Provisioned concurrency or a smaller init |
| ECS task stops immediately | `StoppedReason`, the image pull, the execution role, or a failed health check |
| Works in dev, fails in prod | A stage variable, a missing environment variable, an SCP, or a missing VPC endpoint |

Logs Insights for the request id. X-Ray when you need the downstream segment. EMF when you need a metric without a `PutMetricData` call. An alarm on the DLQ depth, because a DLQ nobody watches is a bin.

## Optimize

Reserved concurrency caps a noisy function so it cannot eat the account pool. Provisioned concurrency pays to kill cold starts. Do not set reserved concurrency to 0 unless you mean to turn the function off.

SNS filter policies and EventBridge patterns drop work before you pay for it. API Gateway and CloudFront cache only responses that are safe to share. An in-process cache needs a TTL. ElastiCache is the shared cache.

Raise Lambda memory until duration stops falling. That is the CPU dial. Then stop.

Health checks: readiness fails when a dependency is down, so the load balancer stops sending. Liveness fails when the process is wedged, so the task restarts. One check for both will restart every task when the database blips.

## Exercise

A function is reserved at 100. The account limit is 1,000. Other functions throttle and this function does not. What did the reservation do, and what do you change if this function was supposed to be the quiet one?

Answer: reserved concurrency both caps and takes 100 from the shared pool. The noisy neighbor is this reservation if 100 was too high, or another function with no cap. Cap the noisy function. Leave a pool for the rest. Optionally reserve a floor for payments so it cannot be starved.

## How this domain asks the question

The stem gives you a symptom and a log line or a metric name. You name the cause and the smallest change. You do not propose a new architecture. "Rewrite it as microservices" is the wrong shape of answer. "The visibility timeout is 30 seconds and the function timeout is 60" is the right shape.

Domain weight moves from 18 percent on DVA-C02 to 22 percent on DVA-C03. The skills are the same family: find the cause, instrument the code, remove the waste.

## Where you look, with the next command

| Symptom | First place | The change |
| --- | --- | --- |
| HTTP 502 from API Gateway | The function log for that request id. A timeout, an unhandled exception, or a response that is not the proxy shape | Fix the exception. If the work is longer than 29 seconds, stop waiting and queue it |
| HTTP 504 | The integration timed out. API Gateway did not get a response in time | Same split. Do not only raise the Lambda timeout |
| HTTP 200 and an error in the body | Your handler set 200 | Return the real status. Alarms on the status code will then see the failure |
| `AccessDenied` in the function log | The role, the resource policy, the key policy, the SCP | Add the missing allow. Do not make the bucket public |
| `ExpiredToken` | A cache of STS credentials past `Expiration` | Refresh on expiry. Do not embed a long-lived key to "avoid" STS |
| `ConditionalCheckFailedException` you did not expect | A retry racing a second writer, or a bug in the condition | If it is the idempotent retry, treat it as success. If it is two users editing one item, you need a version attribute |
| Messages reappear on the queue | Visibility timeout shorter than the work, the function crashed before delete, or you returned the whole batch as failed | Raise the visibility timeout above the function timeout. Delete only after success. Use partial batch failure |
| A message sits until it hits the DLQ | A poison body. The function throws on the same message every time | Log the message id, not the body if the body is sensitive. Fix the handler or divert that shape. Alarm on DLQ depth |
| Iterator age climbing | Consumers are behind, or one poison record blocks the shard | More parallelism, bisect on error, a maximum record age, an on-failure destination |
| `InitDuration` large, `Duration` fine | Cold start. Package size, VPC ENI attachment, init-time work | Provisioned concurrency, less init work, SnapStart for supported Java. Do not raise the timeout to hide init |
| `Duration` large at every memory size | The downstream or the algorithm | Fix the call. More memory only helps while CPU was the limit |
| ECS task stops immediately | `StoppedReason`. Image pull, execution role, a failed health check, an essential container that exited | `CannotPullContainer` is the execution role or the tag. A health-check failure is the probe, not IAM |
| Works in dev, fails in prod | Stage variable, missing environment variable, a different role, an SCP, a missing VPC endpoint, a different table name | Compare configuration. The artifact is the same if you promoted it |
| Throttling on one function and not others | Account concurrency, or this function's reserved concurrency at the cap | Raise the account quota if the whole account is out, or stop reserving the entire pool for one function |
| DynamoDB throttle, consumed capacity looks low | A hot partition | Change the key. Do not only switch to on-demand and hope |
| High cost, low traffic | A metric dimension per user, a log group with no retention, a Lambda in a VPC with a NAT it does not need, provisioned concurrency on a function called twice a day | Fix the cardinality, the retention, the network path, the concurrency setting |

The join key is `context.aws_request_id` in the function log and the API Gateway request id in the access log. Put both in the log line if you have both. X-Ray ties the segments together when you need the downstream time. A trace with no subsegments means the SDK clients were not instrumented. The Lambda service segment still shows the function.

CloudWatch Logs Insights is the query. A metric filter turns a count of `ERROR` into a metric you can alarm on. EMF embeds the metric in the log line so you do not call `PutMetricData` per request. `PutMetricData` per request from a hot function is a cost and a latency item. High-cardinality dimensions (a user id, an order id) create a metric per value. That bill is the optimization question.

Alarms need a period, a threshold, and a missing-data treatment. `notBreaching` means silence is fine. `breaching` means silence pages you, which is correct for a heartbeat and wrong for an error count that is quiet when nobody is calling. The alarm action is SNS, or a rollback hook, or an SSM document. An alarm with no action is a graph.

## Optimize, still the smallest change

Reserved concurrency caps a noisy function and removes that amount from the account pool. Use it so a batch job cannot eat the pool the API needs. Do not set it to 0 unless the function should be off. Provisioned concurrency is the cold-start spend. It counts against the reserved cap. Buy it for the functions with an SLO on the first request, not for everything.

Filters on EventBridge, SNS, and the event-source mapping drop work before you pay for the invocation. A function whose first line returns because the event type is irrelevant is a filter you forgot.

Caches. API Gateway and CloudFront cache responses that are safe to share. A cache key that omits the user serves one user's response to another. An in-process cache on Lambda needs a TTL and must not hold another user's session. ElastiCache is the cache the whole fleet sees. DAX is the DynamoDB item cache.

Lambda memory: raise it until `Duration` stops falling, then stop. ARM architecture is a cost and performance option when the dependencies are built for it. A VPC attachment adds init cost. Remove the VPC if the function does not need private resources. If it needs them, use endpoints so the VPC does not also imply a NAT for AWS APIs.

SDK. A client created inside the handler pays init on every call. A client created at import pays it on the cold start. Timeouts must be shorter than the function timeout so you can return a controlled error. Retries with jitter for throttling. No retries for `AccessDenied`. Pagination, or you process one page and report success.

Health checks. Readiness fails when a dependency is down, so the load balancer stops sending, and the task stays up. Liveness fails when the process is wedged, so the task restarts. One probe for both restarts every task during a database blip and makes the outage worse.

SQL. A connection per invocation exhausts the database. RDS Proxy or the Data API. A query that scans because the attribute is not the key belongs in the data model, not in a bigger instance.

## Exercises

1. Reserved concurrency is 100. The account limit is 1,000. Other functions throttle and this one does not. What did the reservation do?
2. API Gateway returns 504 at 29 seconds. The Lambda timeout is 15 minutes. Which timeout fired?
3. The same SQS message is processed by two functions at once. The visibility timeout is 15 seconds. The function timeout is 45 seconds. What is the race?
4. Iterator age grows. The function's error count is also growing. What do you look for on the shard before you add shards?
5. A metric called `Orders` with dimension `orderId` costs more every day. Why, and what dimension is safe?
6. Dev can reach Secrets Manager. The same function in a VPC in prod times out on the secret and can still reach RDS. What is missing?

## Answers

1. It reserved 100 concurrent executions for this function and removed those 100 from the shared pool. If this function is the noisy one, lower the reservation. If another function is noisy and unreserved, cap that one. Leave pool for the rest. A small reservation on the payment function protects it from being starved.
2. API Gateway's integration timeout. The Lambda timeout never got a chance. Queue the long work and return 202, or finish in under 29 seconds.
3. The message becomes visible while the first invocation is still running, so a second invocation takes it. Set the visibility timeout above the function timeout, with room for retries the SDK does inside the function. Partial batch failure does not fix a visibility timeout that is too short.
4. A poison record. Adding shards does not help the shard that is stuck on one record. Bisect the batch, cap the record age, and send failures to a destination. Then scale, if iterator age is still high because of volume.
5. Each order id is a new metric stream. You pay for cardinality. Dimension on a small set: status, function name, stage. Put the order id in the log line, not in the metric.
6. A path to the Secrets Manager API: an interface VPC endpoint with private DNS, or a NAT. RDS is a private IP inside the VPC, so it never needed that path. The function's security group must be allowed to the endpoint's security group. The role still needs `secretsmanager:GetSecretValue`. A timeout rather than `AccessDenied` means the network, not IAM. IAM failures are fast.
