# Decision trees

Exam morning. One constraint from the stem, then the service. If two answers both "work," the one that matches the constraint in the last sentence is the one they want.

## Storage

| The stem says | Pick |
| --- | --- |
| Object, any size, HTTP, durable | S3 |
| Shared files, NFS, many instances | EFS |
| Windows file share, SMB | FSx for Windows File Server |
| High IOPS on one instance, block | EBS (io2 when they name durability and IOPS) |
| Petabytes, weeks, no network | Snow family |
| Ongoing copy from a data center, files | DataSync |
| S3 to S3 across Regions, new objects | Cross-Region replication. Existing objects need a batch replication job |
| Cannot be deleted, including by root, for N years | Object Lock compliance |
| Unknown access pattern | S3 Intelligent-Tiering |
| Read once a year, delay is fine | Glacier. Not if they need milliseconds |

## Database

| The stem says | Pick |
| --- | --- |
| Relational, joins, one Region, AZ failure | RDS Multi-AZ or Aurora |
| Relational, read scaling in the same Region | Read replica. It does not fail over by itself |
| Relational, second Region, one writer | Aurora Global Database |
| Key-value, single-digit milliseconds, any scale | DynamoDB |
| DynamoDB in two Regions, both write | Global tables. Design for conflicts |
| Cache, sub-millisecond, disposable | ElastiCache. MemoryDB when the cache must be durable |
| Graph, ledger, time series, wide column | Neptune, QLDB, Timestream, Keyspaces. Purpose-built beats "put it in RDS" when the stem names that access |
| Full text search | OpenSearch |
| Too many SQL connections from Lambda | RDS Proxy, or the Aurora Data API |
| "The filter will make the scan cheap" | No. A filter does not reduce RCUs. Change the key |

## Compute

| The stem says | Pick |
| --- | --- |
| Long-running, you control the OS | EC2 in an Auto Scaling group, across AZs |
| Request, seconds, no OS | Lambda |
| Containers, you do not want nodes | ECS on Fargate |
| Containers, you want Kubernetes | EKS |
| Batch, spot, queues of jobs | AWS Batch |
| Web app, platform, low control | Elastic Beanstalk |
| Simple HTTP container, little else | App Runner |
| Steady 24/7 for a year | Compute Savings Plans or Reserved Instances. Spot is for interruptible |
| GPU this week in a sandbox | An SCP that denies it, if the stem is about cost control |

## Network

| The stem says | Pick |
| --- | --- |
| Two VPCs, no growth | Peering |
| Many VPCs plus on-premises | Transit Gateway. Cloud WAN at multi-Region WAN scale |
| S3 or DynamoDB from a private subnet | Gateway endpoint |
| Any other AWS API from a private subnet | Interface endpoint |
| One service published, rest of the VPC hidden | PrivateLink |
| Service-to-service HTTP with IAM | VPC Lattice |
| Overlapping CIDRs | Private NAT. Peering will not form |
| HTTP cache, TLS, WAF, custom domain | CloudFront. Certificate in us-east-1 |
| Static anycast IPs, non-HTTP failover | Global Accelerator |
| Regional HTTP, path routing, auth at the listener | ALB |
| Static IP, millions of packets, TLS passthrough | NLB |
| Third-party virtual appliance, in line | Gateway Load Balancer |
| Edge DDoS on a CloudFront or ALB you already have | Shield Standard is already there. Shield Advanced when they name cost protection and a response team |
| SQL injection and bots on HTTP | WAF on CloudFront or ALB. Not on an NLB |
| 10 Gbps, stable, not this week | Direct Connect, with a VPN backup |
| This week, encrypted, modest bandwidth | Site-to-Site VPN |

## Integration

| The stem says | Pick |
| --- | --- |
| Buffer, one consumer, retries | SQS |
| Fanout, many consumers, no buffer by itself | SNS, then a queue per consumer |
| Many producers, rules, archive, replay | EventBridge |
| A workflow with steps, waits, and a human approval | Step Functions |
| A broker protocol you already use, JMS, strict order across the whole system | Amazon MQ |
| One poison message should not fail the batch | SQS partial batch failure, or a bisect on a stream |
| Exactly once, in those words | They are describing a want. You still design for at-least-once and idempotent writes |

## Security and identity

| The stem says | Pick |
| --- | --- |
| Staff, many accounts | IAM Identity Center permission sets. Not IAM users |
| A person who left | Disable the IdP user. Session length limits the leftover credentials |
| EC2, Lambda, ECS calling AWS | A role. Instance profile, execution role, task role. Not keys on disk |
| Cross-account | `AssumeRole`, and `ExternalId` when the caller is a vendor |
| GitHub Actions, EKS pod | `AssumeRoleWithWebIdentity` |
| Ceiling on an OU, including admins | SCP. Does not apply to the management account |
| Limit one role without editing every policy | Permissions boundary |
| Browser calls AWS APIs | Cognito identity pool |
| Browser calls your API | Cognito user pool JWT, or a Lambda authorizer |
| Per-document rules that are not IAM | Verified Permissions, or a check in code |
| Rotating database password | Secrets Manager |
| A config flag, not a secret | Parameter Store, or AppConfig when you need a bake |
| "Encrypted" and a key administrator | SSE-KMS. SSE-S3 when nobody administers a key |
| AWS must not see plaintext | Client-side encryption |
| Who called an API | CloudTrail. Data events if the stem is about GetObject or a DynamoDB item |
| Malicious activity, a finding | GuardDuty. Security Hub to aggregate. Detective to investigate |
| Sensitive data in a bucket | Macie |

## Disaster recovery

| Numbers | Pattern |
| --- | --- |
| Hours, backups exist | Backup and restore |
| Data is current, compute is not | Pilot light |
| A small copy is already serving | Warm standby |
| Both Regions take users | Active/active |
| One AZ | Multi-AZ. Do not answer with a second Region |

## Migration

| The stem says | Pick |
| --- | --- |
| Servers, as they are | Application Migration Service (MGN) |
| Database, ongoing replication, then cutover | DMS |
| Files, ongoing | DataSync |
| Petabytes, once | Snow |
| Rebuild as managed services | That is the modernization answer, not a tool. Lambda, DynamoDB, SQS, Aurora |

## Developer-only forks

| The stem says | Pick |
| --- | --- |
| Pagination bug, silent success | Continuation token or a paginator |
| 200 with an error in the body | The handler set `statusCode` wrong |
| JWT, no signature check | Verify, then read claims |
| `latest` image tag | Pin a digest or an immutable tag |
| Reserved concurrency 0 | The function cannot run |
| Cache key without the user | One user sees another's response |
| Prompt in the logs, role can delete the table | Redact, and scope the tool role. A model is not an authorization decision |
