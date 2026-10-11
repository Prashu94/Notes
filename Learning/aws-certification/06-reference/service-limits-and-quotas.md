# Quotas that change an answer

Soft quotas move. Before exam day, open Service Quotas for your Region if a number in a stem looks off. The numbers below are the ones items are written around. When the stem gives a different number, use the stem.

Official: https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html and the Service Quotas console.

## Timeouts, because three of them get swapped

| Limit | Number people mix up | What you do when the work is longer |
| --- | --- | --- |
| API Gateway integration | 29 seconds | Queue the work, return 202. Raising the Lambda timeout does not raise this |
| Lambda function | 15 minutes | A job longer than that is Step Functions, ECS, or Batch, not a bigger function |
| ALB idle timeout | 60 seconds by default, can be raised | Still the wrong place to hide a 10-minute report |
| SQS visibility timeout | 30 seconds default, 12 hours maximum | Set it above the consumer's timeout |
| SQS long poll | 20 seconds maximum | `WaitTimeSeconds` |
| CloudFront origin response | Default is short. You can raise it on a custom origin | Still not a 15-minute API |

## Payloads

| Limit | Why it is an item |
| --- | --- |
| Lambda synchronous payload, 6 MB | A bigger request does not go through a synchronous invoke |
| Lambda asynchronous payload, 256 KB | The event is over the limit. Put the body in S3 and pass the key |
| SQS and SNS messages, 256 KB on the long-standing exam number | The pointer-to-S3 pattern. Confirm the current quota. If AWS raised it, the "too big for the queue" item still wants S3 for multi-megabyte bodies |
| API Gateway payload, 10 MB | A video upload is S3 with a presigned URL, not the API body |
| DynamoDB item, 400 KB | The large attribute goes to S3. The item keeps the key |
| Step Functions payload, 256 KB | Pass ARNs and keys, not the document, between states |
| EventBridge event, 256 KB | Same pattern |

## DynamoDB, the numbers that explain a throttle

A single partition is on the order of 3,000 read capacity units and 1,000 write capacity units, and about 10 GB. A table can be huge and still throttle if every write uses one partition key. A filter does not change this. On-demand raises the table ceiling. It does not fix a hot key.

`BatchWriteItem` is 25 items. A transaction is 100 actions. A query returns 1 MB per call and you paginate with `LastEvaluatedKey`.

## S3, the numbers that explain a lifecycle

A single PUT is 5 GB. Above that you multipart. An object can be 5 TB. Incomplete multipart uploads are a bill until a lifecycle rule aborts them.

Standard-IA and one-zone IA have a 30-day minimum storage duration. Glacier Flexible Retrieval is 90 days. Glacier Deep Archive is 180 days. A lifecycle that moves an object to IA on day 1 fails. A lifecycle that moves logs to Deep Archive and then reads them the next morning is the wrong storage class.

## Identity and policy size

An IAM role session defaults to one hour. The maximum you can request is 12 hours. A cached credential past `Expiration` is `ExpiredToken`.

An SCP document is small (the published ceiling is 5,120 characters). A huge SCP is a design problem, not a reason to put the workload in the management account. Five versions is the ceiling on a customer managed IAM policy. You delete an old version before you add a sixth.

CloudTrail Event history in the console is 90 days. Longer retention is a trail to S3, with a lock on the bucket if the stem says nobody may delete it.

## Concurrency

The default Lambda concurrency pool is 1,000 per Region, and it is adjustable. Reserved concurrency subtracts from that pool. Zero means the function cannot run. Unreserved functions share whatever is left. Provisioned concurrency is a subset you pay to keep warm, and it also counts against the reserved cap if you set one.

## What you should not memorize

Default VPCs per Region, rules per security group, and rules per NACL are adjustable and have moved. The exam point is the behavior: a NACL is stateless and short, a security group is stateful, and a long allow-list belongs in the security group or in a prefix list, not in a 40-line NACL you hope is the firewall.

Interface endpoint, NAT gateway, and Transit Gateway attachment prices are not quotas. They are the cost items in `03-saa/04-domain-4-cost.md`.
