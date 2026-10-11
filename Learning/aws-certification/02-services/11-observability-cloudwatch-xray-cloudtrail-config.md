# Observability: CloudWatch, X-Ray, CloudTrail, Config

SAA uses these as the visibility tools. SAP task 3.1 lives here. DVA domain 4 lives here. SAP-C03 adds synthetics, RUM, and container and model metrics.

Official:

- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/AnalyzingLogData.html
- https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html
- https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html
- https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html
- https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html

## Three different records

| System | Records | Does not record |
| --- | --- | --- |
| CloudTrail | API calls. Who called `RunInstances` | The HTTP 500 inside your function, unless the function logged it |
| CloudWatch metrics and logs | The workload. CPU, 5xx, your log lines | A durable audit of every IAM change, unless you also have a trail |
| Config | Configuration over time. Was this security group open on Tuesday | The request that caused the latency |
| X-Ray | One request across services | A bill, a config history, or an API audit |

If the stem says "an auditor" it is CloudTrail, often with log file validation. If it says "the app is slow" it is metrics, logs, and a trace. If it says "the security group changed" it is Config, and CloudTrail will also show who called the API.

## CloudWatch

Namespaces, metrics, dimensions, periods. Custom metrics via `PutMetricData` or EMF. EMF is a log line CloudWatch turns into a metric. High-cardinality dimensions such as a user id make the bill explode. Put the user id in the log. Put the status code in the metric.

Logs Insights:

```sql
fields @timestamp, @message
| filter @message like /ERROR/
| stats count() by bin(5m)
```

Alarms target an SNS topic, an Auto Scaling policy, or an Systems Manager action. A dashboard without an alarm does not page anyone. Composite alarms reduce noise when five alarms are the same incident.

Agent: the unified CloudWatch agent ships logs and memory and disk metrics. Those are not on by default for EC2.

Cross-account observability lets a monitoring account see metrics and logs from source accounts. That is the Professional "one dashboard" answer. The log-archive account is still where the trail lands.

Container Insights for ECS and EKS. Lambda Insights for functions. Contributor Insights for "which key is hot."

Synthetics canaries hit an endpoint on a schedule. RUM takes a snippet in the browser. SAP-C03 names both. A canary fails when the user path is down even if your CPU alarm is green.

## X-Ray

Turn tracing on at API Gateway and Lambda (`--tracing-config Mode=Active`) and in the SDK. One header, `X-Amzn-Trace-Id`, ties the segments together. Annotations are indexed. Metadata is not. Put the order id in an annotation if you will search for it.

The service map answers "which downstream is the red segment." A trace does not replace a metric alarm. You still alarm on the SLO.

## CloudTrail

Organization trail, all Regions, log file validation, KMS, a bucket policy that denies delete, delivered to the log-archive account. Data events (S3 object-level, Lambda invokes) cost more and are off until you enable them. Management events are the control-plane story. "Who deleted the object" needs data events or S3 server access logs. Server access logs and CloudTrail data events are different. Know which one the stem asked for.

Insights on a trail look for unusual API volumes. GuardDuty is the threat detector. Do not swap them.

```bash
aws cloudtrail create-trail --name org --s3-bucket-name "$BUCKET" --is-multi-region-trail --is-organization-trail --enable-log-file-validation --kms-key-id alias/trail
aws cloudtrail start-logging --name org
aws cloudtrail lookup-events --lookup-attributes AttributeKey=EventName,AttributeValue=ConsoleLogin
aws logs start-query --log-group-name /aws/lambda/orders --start-time "$START" --end-time "$END" --query-string 'fields @message | filter @message like /Timeout/'
```

## Config

A recorder, a delivery channel, rules. Managed rules such as `restricted-ssh`, `s3-bucket-public-read-prohibited`, `encrypted-volumes`. Remediation is an SSM Automation document. Config does not block the API. An SCP blocks. Config notices, then remediates.

An aggregator in the security account sees every account. Conformance packs bundle rules for a standard.

## Exercises

1. The auditor wants proof that nobody changed a trail file after delivery. Which CloudTrail feature?
2. Checkout p99 rose. CPU on the app is fine. Which two tools, in which order?
3. A security group was opened to the world last Tuesday. Which service shows the before and after, and which shows the principal?
4. A Lambda logs every user id as a CloudWatch metric dimension. Why is that a bad metric and a fine log?

## Answers

1. Log file validation. Integrity digests, not just encryption.
2. The ALB and database metrics first, then an X-Ray trace of a slow request. Guessing a bigger instance first skips the tier that is actually waiting.
3. Config shows the configuration timeline. CloudTrail shows who called `AuthorizeSecurityGroupIngress`.
4. A dimension per user creates a metric per user and the cost follows. The log line can hold the user id. The metric should be a count of errors.

## Metrics, logs, traces, and which question each one answers

| Question | Tool |
| --- | --- |
| Is the error count above the line? | A CloudWatch metric and an alarm |
| What did this request log? | Logs Insights on the log group, filtered by the request id |
| Which downstream took the time? | X-Ray |
| Who called the API? | CloudTrail |
| Did the security group change, and what did it look like before? | Config |
| Which shard or which user is hot, as a ranked list? | Contributor Insights |

A metric has a namespace, a name, dimensions, and a statistic over a period. Dimensions are part of the identity. `Errors` with `FunctionName=pay` is not the same series as `Errors` with no dimension. High cardinality (a dimension per user, per order, per IP) creates a series per value and the bill follows. Put the id in the log line. Keep dimensions to a small set: function, stage, status class.

EMF writes a structured log line that CloudWatch turns into a metric. That avoids `PutMetricData` on every request. A metric filter counts occurrences of a pattern such as `ERROR` and is the bridge from a log you already have to an alarm. Use the filter when you cannot change the code. Use EMF when you can.

Alarms need a threshold, a period, evaluation periods, and a missing-data treatment. `notBreaching` means silence is fine, which is right for an error count when nobody is calling. `breaching` means silence pages you, which is right for a heartbeat. An alarm with no action is a graph. The action is SNS, an Auto Scaling policy, or a Systems Manager document. Composite alarms fire when several alarms are in alarm together, so a deploy page waits for both error rate and latency instead of paging on either alone. Anomaly detection is the band around a seasonal metric. It is the wrong tool for a threshold you already know, such as DLQ depth greater than zero.

## Logs

The application logs to stdout. The agent or the Lambda runtime ships them. Retention is set on the group. "Never expire" is a storage bill and sometimes a compliance problem. A subscription filter fans a group out to OpenSearch, Kinesis, or Lambda for analysis beyond Insights.

Insights queries are not real-time metrics. They search what has been ingested. The join key between an ALB access log and a Lambda log is the request id. Log both. Do not log the body, the Authorization header, or the secret.

## X-Ray

A trace is a tree of segments. Lambda with active tracing emits the service segment. Subsegments appear when the SDK is instrumented, so you can see DynamoDB versus the time you spent in code. Annotations are indexed and can be filtered. Metadata is extra context and is not indexed the same way. Sampling keeps the cost down. A trace of every request on a hot API is a bill. A 502 whose trace stops at the function with no subsegment means you are looking at the function's own time, not a downstream you failed to wrap.

## CloudTrail and Config

Management events are the control-plane calls: `RunInstances`, `DeleteTrail`, `PutBucketPolicy`. They are the default trail. Data events are object-level and item-level: `GetObject`, `PutObject`, DynamoDB item APIs. They cost more. Turn them on for the buckets and tables the stem called sensitive, not for every object in the company unless the stem said that. Insight events are unusual API activity. They are not GuardDuty.

An organization trail, all Regions, log file validation, KMS, a bucket in the log-archive account, and a policy that denies delete is the auditor's trail. Log file validation proves the files were not edited after delivery. Encryption proves they are unreadable without the key. They are different controls. A trail that can be stopped by the application admin is not evidence. Event history in the console is 90 days and is not a trail.

Config records resource configuration over time. A rule evaluates compliance. Remediation can call Automation. An aggregator in the security account sees every account. Conformance packs bundle rules. Config does not show the principal. CloudTrail does. Use both when the stem asks what changed and who changed it.

VPC Flow Logs are not in this paragraph's tools, and people reach for them anyway. They answer who connected on the network. They do not answer who called the API.

## More exercises

5. DLQ depth should page someone, including when the metric has been missing and then appears. Which comparison and which missing-data setting?
6. You need to search every Lambda log line containing a request id across one group. Metric filter or Insights?
7. X-Ray is on. The trace shows the function and not the DynamoDB call. What is missing?
8. A trail has data events off. The auditor asks who read a specific object. Can you answer?
9. Config says the bucket became public. You need the role that called `PutBucketPolicy`. Which log?

## Answers

5. `GreaterThanThreshold` of 0, or greater than or equal, on `ApproximateNumberOfMessagesVisible`. Missing data should be `notBreaching` if an empty queue simply stops publishing, so you do not page when the queue is idle. You page when the depth is actually above zero. A heartbeat is the opposite missing-data choice.
6. Insights. A metric filter turns a pattern into a count. It does not return the lines.
7. The AWS SDK call is not instrumented, or the X-Ray daemon and permissions are missing on a non-Lambda compute. Active tracing on Lambda alone gives you the function segment. The downstream segment needs the SDK.
8. Not from this trail. Data events were off, so object reads were not recorded. Enable data events on that bucket going forward. You cannot backfill the read that already happened.
9. CloudTrail. Config has the configuration timeline. The event name and the principal are on the trail. GuardDuty might notice the public bucket later. It is not the system of record for the API call.
