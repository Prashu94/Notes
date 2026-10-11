# SAA-C03 exam blueprint

Source: AWS Certified Solutions Architect – Associate exam guide (SAA-C03), HTML and PDF on AWS Documentation, reviewed 11 October 2026.

https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html

https://docs.aws.amazon.com/pdfs/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.pdf

The exam code is **SAA-C03**. People say “SA-C03” in conversation. The booking code, the guide, and the score report say SAA-C03. There is no separate “SA-C03” exam.

Role in one line: design a solution that is secure, resilient, high-performing, and cost-optimized, using the Well-Architected Framework, for a workload that usually lives in one organization and one or two accounts.

| Domain | Weight | One-line job |
| --- | --- | --- |
| 1. Design Secure Architectures | 30% | Who can call what, how the network is segmented, how data is encrypted and retained. Heaviest domain |
| 2. Design Resilient Architectures | 26% | Loose coupling, scaling, Multi-AZ, Multi-Region, and a DR pattern that matches RTO and RPO |
| 3. Design High-Performing Architectures | 24% | Storage, compute, database, network, and data-ingestion choices that meet a latency or throughput number |
| 4. Design Cost-Optimized Architectures | 20% | The same choices when the winning constraint is the bill |

50 scored questions plus 15 unscored. 130 minutes. 150 USD. Passing score 720 scaled. No case studies. Recommended experience is at least 1 year designing solutions on AWS. Compensatory scoring: you do not need to pass each domain. Unanswered items are wrong. There is no penalty for guessing.

The guide also says the candidate must be able to review an existing solution and recommend improvements. That shows up as “a company currently uses X. The company needs Y.” Do not rip out X unless Y is impossible on X.

No SAA-C04 date has been published. The September 2026 certification blog updates SAP-C02 and DVA-C02. It does not retire SAA-C03. Study this blueprint as the current Associate exam.

## How SAA differs from the other two exams in this pack

| | SAA-C03 | SAP-C02 / SAP-C03 | DVA-C02 / DVA-C03 |
| --- | --- | --- | --- |
| Question shape | Pick the service and the pattern | Pick the design under several constraints at once, often across accounts | Pick the API, the IAM action, the deployment config, or the log line |
| Depth of Organizations | SCPs, Control Tower, and cross-account roles appear. You are not designing a full landing zone from scratch every item | Landing zones, delegated admin, RAM, central logging | Out of scope as administration. Roles in code are in scope |
| Networking design | VPC, subnets, one NAT pattern, peering versus Transit Gateway, endpoints | Hybrid DNS, overlapping CIDRs, Cloud WAN, DX resiliency, Lattice | You attach a Lambda to a VPC. You do not design the VPC |
| DR | Name the pattern from RTO/RPO | Design the replication, the failover, and the test | Not a design exam |
| Code | None | None | Python, JavaScript, Java, or the SDK call |
| Out of scope that surprises people | CDK, CodeBuild, CodeDeploy, CodeCommit, CodeArtifact, CloudShell, FIS, the SDK itself, Lightsail, IoT, MWAA, Location Service, most media services except Elastic Transcoder and Kinesis Video Streams | GameLift. Frontend mobile development. Deep OS internals | Architecture design, pipeline design, IAM user administration, OS administration, VPC/DX design. Shield is listed out of scope on DVA-C02 |

If a service is out of scope for SAA, it can still be a wrong answer. Know the one-line reason it loses.

## How a stem picks a domain

The domain is the constraint, not the service. S3 appears in all four domains.

| Last line of the stem | Domain |
| --- | --- |
| “Most secure” / “meet compliance” / “least privilege” | 1 |
| “Highly available” / “no single point of failure” / “RTO of 2 hours” | 2 |
| “p99 under 50 ms” / “millions of requests” / “ingest 50,000 events per second” | 3 |
| “Most cost-effective” / “reduce cost with minimal change” | 4 |

When two constraints appear, both must hold. “Most cost-effective highly available design” is Domain 4 judged inside a Domain 2 floor: Multi-AZ still required, second Region only if the RTO needs it.

---

## Domain 1 — Secure architectures (30%)

### Task 1.1 — Design secure access to AWS resources

Knowledge the guide names: multi-account access control, federated access (IAM, IAM Identity Center), global infrastructure, least privilege, the shared responsibility model.

Skills:

- MFA on IAM users and on the root user.
- An authorization model of users, groups, roles, and policies.
- STS, role switching, cross-account access.
- A multi-account strategy with Control Tower and SCPs.
- Resource policies.
- When to federate a directory with IAM roles.

What you must be able to choose:

| Requirement | Design |
| --- | --- |
| A person needs access to a console | IAM Identity Center permission set, or an IAM role they assume. An IAM user with an access key is the legacy answer and loses “best practice” stems |
| Root | Lock it. MFA hardware key. No daily work. No access keys |
| An EC2 instance, Lambda, or ECS task calls S3 | A role attached to the compute. No keys in the AMI, the environment, or the repo |
| Account A reads a bucket in account B | A role in B that trusts A, or a bucket policy that allows the role in A. Both sides must allow it. A resource policy alone is not enough when the identity policy does not allow the action, except for some anonymous and cross-account cases you should still write both |
| A third party assumes your role | `sts:ExternalId` in the trust policy so a confused deputy cannot reuse the role |
| Many accounts, a team must be prevented from leaving a guardrail | An SCP. SCPs filter. They never grant. A deny in an SCP wins against every allow in the account, including admin, except for the management account itself, which SCPs do not apply to |
| New multi-account setup, least operational overhead | Control Tower |
| Workforce already in Microsoft AD or an external IdP | Identity Center connected to that IdP. Directory Service when the workload itself must bind to AD (Windows, FSx for Windows, RDS SQL Server auth) |
| A service must be the only principal that can write a bucket | Bucket policy with `aws:PrincipalArn` or a condition on `aws:SourceAccount` / `aws:SourceArn` for service-to-service (SNS, CloudTrail) |

Shared responsibility, the version the exam uses:

| AWS | You |
| --- | --- |
| Facilities, hardware, hypervisor, managed-service patching of the platform | Data, IAM, security groups, OS patches on EC2, client-side encryption, application code |
| Encryption *capability* in S3, EBS, RDS | Turning it on, picking the key, and the key policy |

MFA: root and every human. STS can require MFA with `aws:MultiFactorAuthPresent`. That condition does not apply cleanly to Identity Center the same way. For Identity Center, turn MFA on in the identity source.

Commands:

```bash
aws iam get-account-summary
aws iam list-mfa-devices --user-name "$USER"
aws iam create-role --role-name app-s3-read \
  --assume-role-policy-document file://trust.json
aws iam put-role-policy --role-name app-s3-read \
  --policy-name read-one-bucket \
  --policy-document file://permissions.json
aws sts assume-role \
  --role-arn "arn:aws:iam::ACCOUNT_ID:role/app-s3-read" \
  --role-session-name lab
aws organizations list-policies --filter SERVICE_CONTROL_POLICY
```

`trust.json` for same-account EC2:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Service": "ec2.amazonaws.com" },
    "Action": "sts:AssumeRole"
  }]
}
```

Study: `01-foundations/02-iam-sts-identity-center-ram.md`, `01-foundations/04-accounts-organizations-control-tower.md`, `03-saa/01-domain-1-secure.md`.

### Task 1.2 — Design secure workloads and applications

Knowledge: credentials in config, service endpoints, ports and protocols, Cognito, GuardDuty, Macie, DDoS, SQL injection, VPN, Direct Connect.

Skills: VPC security (security groups, route tables, NACLs, NAT), public versus private subnets, Shield, WAF, Identity Center, Secrets Manager, securing the path in and out of AWS.

Associate VPC you should draw without looking:

```text
VPC 10.0.0.0/16
  public subnet AZ-a   10.0.0.0/24    route 0.0.0.0/0 -> IGW
  public subnet AZ-b   10.0.1.0/24    route 0.0.0.0/0 -> IGW
  private subnet AZ-a  10.0.10.0/24   route 0.0.0.0/0 -> NAT in AZ-a
  private subnet AZ-b  10.0.11.0/24   route 0.0.0.0/0 -> NAT in AZ-b
  data subnet AZ-a     10.0.20.0/24   no route to IGW
  data subnet AZ-b     10.0.21.0/24   no route to IGW
```

| Piece | Rule |
| --- | --- |
| Internet Gateway | One per VPC is enough. It is horizontally scaled. “Add a second IGW for HA” is wrong |
| NAT Gateway | AZ-scoped. One NAT in one AZ is a single point of failure and a cross-AZ data charge. One per AZ for production. A NAT instance is the cost outlier and the availability loss |
| Security group | Stateful. Allow inbound on 443 from the ALB security group id, not from 0.0.0.0/0, on the app tier. Return traffic is automatic |
| NACL | Stateless. Numbered rules. Use it for a subnet-wide deny. Default NACL allows all. Custom NACL starts by denying all until you add rules, including ephemeral ports if you must allow return traffic |
| Bastion on port 22 | Loses to Session Manager. No inbound SSH |
| S3 from a private subnet | Gateway endpoint. Traffic stays on the AWS network and skips NAT |
| Everything else AWS from a private subnet | Interface endpoint (PrivateLink) |
| Employees into the VPC | Client VPN or Site-to-Site VPN. Direct Connect when the volume or the latency is a circuit problem, not a “quick and encrypted” problem |
| Public website, DDoS and SQLi | CloudFront, Shield (Standard is already on; Advanced when they need the DRT or cost protection), WAF on the CloudFront distribution |
| App users, sign-up, social login, JWT | Cognito user pools. Identity pools only when the app needs temporary AWS credentials |
| API keys and database passwords | Secrets Manager with rotation. Parameter Store SecureString for config that does not need rotation |
| “Someone may already be calling odd APIs” | GuardDuty |
| “Find PII in S3” | Macie |
| “CVE on the instances and images” | Inspector |
| “One place for findings” | Security Hub |

SQL injection is an application and WAF problem. A security group does not parse SQL. The WAF managed rule group for SQL injection is the AWS control the stem wants when they will not rewrite the app this quarter.

### Task 1.3 — Determine data security controls

Knowledge: access and governance, recovery, retention and classification, encryption and keys.

Skills: map a control to a compliance need, encrypt at rest with KMS, encrypt in transit with ACM and TLS, key policies, backups and replication, lifecycle and protection policies, key rotation and certificate renewal.

| Data need | Control |
| --- | --- |
| Encrypt an S3 object with a key you can disable | SSE-KMS (`aws:kms`). Bucket keys cut the KMS request cost |
| Encrypt with a key AWS manages, less audit | SSE-S3. Weaker answer when the stem says “customer managed” or “key policy” |
| Encrypt before the data reaches AWS | Client-side encryption. The SDK or the client holds the key. AWS cannot help you read it |
| EBS | Encryption by default in the account. A snapshot of an encrypted volume is encrypted. Sharing that snapshot across accounts requires sharing the KMS key too |
| RDS | Encryption at creation. You cannot flip the flag later in place. Snapshot, copy encrypted, restore |
| TLS on ALB, CloudFront, API Gateway | ACM public certificate in the same Region as the ALB. CloudFront certificates must be in us-east-1 |
| Private service names inside the company | AWS Private CA. Public ACM will not issue those names |
| Key rotation | Customer managed KMS keys: automatic yearly rotation, or on-demand. AWS managed keys rotate on AWS’s schedule. Imported key material is your rotation problem |
| “Retain objects so even root cannot delete them for 7 years” | S3 Object Lock, compliance mode. Governance mode can be overridden by a special principal |
| Backup that survives an account compromise | AWS Backup vault in another account, vault lock, or a copy to a locked bucket |
| Logs an auditor will trust | Organization CloudTrail, log file validation, KMS encryption, bucket policy that denies delete |

Compliance papers (ISO, SOC, PCI) come from AWS Artifact. Artifact does not make you compliant. It gives you AWS’s reports. Your scope is still IAM, encryption, logging, and the application.

---

## Domain 2 — Resilient architectures (26%)

### Task 2.1 — Scalable and loosely coupled architectures

Knowledge the guide packs into this task is most of the “which service” catalog: API Gateway, Transfer Family, SQS, Secrets Manager, caching, stateless versus stateful, event-driven design, horizontal versus vertical scaling, CloudFront, containers, ALB, multi-tier, pub/sub, Fargate, Lambda, object versus file versus block, ECS, EKS, read replicas, Step Functions.

Skills: design the architecture, pick a scaling strategy, decouple, choose containers, choose serverless, recommend compute, storage, network, and database, use a purpose-built service.

Decoupling choices at Associate depth:

| Need | Service |
| --- | --- |
| One producer, one consumer, buffer, retries | SQS. FIFO when order and exactly-once processing matter and throughput can live inside FIFO limits. Standard when throughput and at-least-once are fine |
| One message, many consumers | SNS, with an SQS queue per consumer so each consumer has its own retry buffer |
| React to AWS or SaaS events, content filter, archive, replay | EventBridge |
| A business workflow with steps, waits, and retries | Step Functions |
| Existing app speaks JMS, AMQP, MQTT, or needs ActiveMQ / RabbitMQ | Amazon MQ |
| SaaS to AWS data flow, little code | AppFlow |
| HTTP API in front of Lambda or HTTP backends | API Gateway. REST when you need API keys, usage plans, and the older feature set. HTTP API when it is cheaper and the feature list fits |
| Users download the same bytes worldwide | CloudFront |
| Web tier, app tier, data tier | Public ALB, private app instances in an ASG across two AZs, data subnets with no IGW route |

Stateless versus stateful: put session state in DynamoDB or ElastiCache, not on the instance disk, or the next scaled-out instance will not see it. Sticky sessions on an ALB are the compromise when the app cannot be changed. They hurt even scaling.

Horizontal scaling is more instances. Vertical scaling is a bigger instance. Variable web traffic wants horizontal. A license that is per-socket and cannot run twice wants vertical, and you say so.

Containers versus Lambda:

| Signal | Choice |
| --- | --- |
| Short request, scales to zero, no special runtime | Lambda |
| A container that already exists, long-running process, WebSocket server you do not want to reshape | ECS on Fargate |
| The team requires the Kubernetes API | EKS |
| You must control the host | ECS or EKS on EC2 |
| A web app from a platform, the team does not want to build a cluster | Elastic Beanstalk, or App Runner when the stem is allowed to use it. App Runner is in the SAP guide more clearly than the SAA in-scope list. On SAA, Beanstalk and Fargate are the safe managed compute answers |

Read replicas are for read scale and for a cross-Region copy you can promote. They are not automatic failover. Multi-AZ is failover.

### Task 2.2 — Highly available and fault-tolerant architectures

Knowledge: Regions, AZs, Route 53, a curious guide example that says “AWS Managed Services (AMS)” and then names Comprehend and Polly (treat that as “managed AWS services,” and treat AMS the operations product as out of scope unless a stem uses the initials), route tables, the four DR strategies plus active-active, RPO, RTO, distributed patterns, failover, immutable infrastructure, ALB, RDS Proxy, service quotas, storage durability, X-Ray.

Skills: automation that keeps infrastructure intact, HA across AZs or Regions, metrics that prove availability, remove single points of failure, durable data, pick a DR strategy, improve a legacy app you cannot change.

RTO is how long you may be down. RPO is how much data you may lose. Match the pattern:

| Pattern | Compute in the other Region | Data | When it wins |
| --- | --- | --- | --- |
| Backup and restore | Built at failover time | Backups and snapshots | RTO of many hours, lowest cost |
| Pilot light | Core data live, compute small or off | Continuous replication | RTO of tens of minutes |
| Warm standby | Scaled-down full stack already running | Replication | RTO of minutes |
| Active-active | Both Regions serve users | Multi-Region writes (DynamoDB global tables, or careful Aurora global design) | RTO near zero |

Immutable infrastructure means you replace instances from a new AMI or a new launch template. You do not SSH and patch one box. ASG plus a golden AMI, or Beanstalk, or Lambda.

Legacy app you cannot change:

- Put an ALB in front and an ASG around it if it can run as more than one copy.
- If it cannot, Multi-AZ is still possible with a failover pattern, but scale-out is not. Say that.
- RDS Proxy if the failure mode is “too many connections” from a chatty app or from Lambda.
- X-Ray if the failure mode is “we cannot see which tier is slow.” X-Ray is in scope on SAA. The SDK and FIS are not. You select X-Ray. You do not write the SDK instrumentation on this exam.

Single points of failure that are automatic wrong answers: one AZ, one NAT for a design that claimed Multi-AZ, one EBS volume with the only copy of the data, an Auto Scaling group whose health check is EC2-only while the process is dead, a database with no backup.

Automation for integrity: CloudFormation (in scope), launch templates, AMI pipelines, Systems Manager. CDK is listed out of scope for SAA. CloudFormation is the IaC answer on this exam.

---

## Domain 3 — High-performing architectures (24%)

### Task 3.1 — High-performing storage

Knowledge: hybrid storage, S3, EFS, EBS, object versus file versus block.

Skills: pick the service and the configuration that meets the performance number, and that can grow.

| Access | Service |
| --- | --- |
| Put and get by key, any size of object, durable | S3 |
| POSIX shared files, many instances, Linux | EFS. General Purpose for latency. Elastic throughput unless you have a known baseline |
| SMB, Windows ACLs, AD | FSx for Windows File Server |
| Lustre, HPC, training data | FSx for Lustre, often linked to S3 |
| Multi-protocol NAS, snapshots, SnapMirror familiar to a NetApp team | FSx for NetApp ONTAP |
| A single instance disk, a database file system | EBS. gp3 for general. io2 when you must provision very high IOPS and durability |
| Scratch that can vanish | Instance store |
| On-premises file share that should land in S3 | Storage Gateway, File Gateway. DataSync to copy. Transfer Family if the protocol is SFTP |

S3 performance scales by prefix and by parallel requests. Multipart upload for large objects. A single-threaded upload of a 200 GB object is the slow design.

### Task 3.2 — High-performing elastic compute

Knowledge: Batch, EMR, Fargate, edge, pub/sub, EC2 Auto Scaling and AWS Auto Scaling, Lambda, ECS, EKS.

Skills: decouple so tiers scale alone, pick the metric, pick the instance family, pick Lambda memory.

Scaling metrics that match the bottleneck:

| Tier | Metric |
| --- | --- |
| Web behind ALB | `ALBRequestCountPerTarget` or target response time. CPU if the app is actually CPU bound |
| Queue consumer | SQS `ApproximateNumberOfMessagesVisible`. Scale on backlog, not on CPU of an idle poller |
| Lambda | Memory is the size dial. More memory adds CPU. Timeout is separate. Reserved concurrency protects a downstream database. Provisioned concurrency removes cold starts when the stem has a latency SLO on the first request |
| Spot plus On-Demand | A mixed-instances ASG. Spot for the interruptible share. On-Demand or a Savings Plan for the base |

Instance family intent is in `02-sap-c02-exam-blueprint.md` Task 2.5 and will be repeated in the compute service chapter. For SAA, recognize general (M), compute (C), memory (R), burstable (T), storage (I, D), and accelerated (G, P). A T instance that runs hot all day runs out of CPU credits. That is a performance incident, not a bargain.

EMR is the managed Hadoop and Spark answer. Batch is the queue of jobs answer when the work is batch and not a Spark cluster. Do not swap them.

### Task 3.3 — High-performing databases

Knowledge: caching, access patterns, capacity units, instance types, provisioned IOPS, proxies, homogeneous versus heterogeneous migration, read replicas, serverless versus relational versus non-relational versus in-memory.

Skills: read replicas, architecture, engine choice, Aurora versus DynamoDB, caching.

| Pattern | Database |
| --- | --- |
| SQL, joins, a familiar engine, Multi-AZ | RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server) |
| SQL, higher performance, readers, fast failover, MySQL or PostgreSQL compatible | Aurora. Aurora Serverless v2 when the load varies and you want capacity to move in ACUs |
| Key lookup, extreme scale, single-digit millisecond, no joins | DynamoDB. On-demand when the traffic is unknown. Provisioned plus auto scaling when it is steady |
| Cache, leaderboards, sessions | ElastiCache. Redis OSS or Valkey when you need structures and replication. Memcached when you need a simple cache that can shard |
| Documents, MongoDB-compatible | DocumentDB |
| Graph | Neptune |
| Cassandra-compatible | Keyspaces |
| Warehouse, columnar scans | Redshift |
| Search | OpenSearch Service |
| Time series | Timestream is the purpose-built answer when it is in the stem. It is on the SAP in-scope list. On SAA the guide’s database list does not print Timestream. Prefer DynamoDB or a purpose-built mention only if the stem offers it |

Read replica: asynchronous, readable, can be cross-Region, you promote it yourself for DR. Multi-AZ: synchronous standby, not a second read endpoint on classic Multi-AZ instance deployments. Aurora readers are different: they are first-class read endpoints on the shared storage volume.

RDS Proxy: pool connections, faster failover from the app’s point of view, IAM auth. Use it when Lambda or a large fleet would open too many connections.

Homogeneous migration stays on the same engine (Oracle to RDS Oracle) and is simpler. Heterogeneous (Oracle to Aurora PostgreSQL) needs schema conversion. DMS moves the data. SCT converts schema. SCT is a SAP-emphasized tool. On SAA, know DMS is the data mover and that a heterogeneous move is a bigger project.

### Task 3.4 — High-performing and scalable networks

Knowledge: CloudFront, Global Accelerator, subnet tiers, routing, IP addressing, ALB, VPN, Direct Connect, PrivateLink.

Skills: topology (global, hybrid, multi-tier), a design that can grow, placement, load balancer choice.

Load balancers:

| Balancer | Layer | Pick it when |
| --- | --- | --- |
| ALB | 7, HTTP, HTTPS, gRPC, WebSocket | Path rules, host rules, Lambda targets, Cognito auth on the listener, one balancer for many apps |
| NLB | 4, TCP, UDP, TLS | Static IP, PrivateLink in front of your own service, extreme performance, non-HTTP |
| Gateway Load Balancer | 3, GENEVE | Insert a firewall appliance fleet. Security inspection, not app routing |

CloudFront versus Global Accelerator:

| | CloudFront | Global Accelerator |
| --- | --- | --- |
| Protocol | HTTP and HTTPS | TCP and UDP, and HTTP too |
| Cache | Yes | No. It is an anycast network path |
| Typical stem | Static assets, video, API caching, WAF at the edge | Gaming, IoT, static anycast IPs, fast failover between Regions |

Hybrid: VPN over the internet to start. Direct Connect for a private circuit. They combine when you want encryption over DX (VPN over DX) or a backup path. PrivateLink publishes a service to another VPC without peering the whole network.

Placement: put the resource in the Region where the users or the data-residency rule says. Spread subnets across AZs. Do not put the database in a public subnet.

### Task 3.5 — High-performing data ingestion and transformation

Knowledge: Athena, Lake Formation, QuickSight (the PDF text extraction shows “Amazon Quick”; the service is QuickSight), ingestion frequency, DataSync, Storage Gateway, Glue, Kinesis, secure access points, size and speed, EMR.

Skills: data lake, streaming architecture, transfer, visualization, EMR versus other compute, ingestion configuration, CSV to Parquet.

| Job | Service |
| --- | --- |
| Stream of events, custom consumers, replay | Kinesis Data Streams |
| Stream that must land in S3, Redshift, OpenSearch, or HTTP with little code | Data Firehose |
| Kafka API | MSK |
| Catalog, crawl, ETL jobs | Glue. Convert CSV to Parquet or ORC in the job. Partition the S3 layout |
| SQL on S3 | Athena. It wants columnar formats and partitions or the bill and the latency get worse |
| Lake permissions, not just a bucket | Lake Formation on top of the Glue catalog |
| Dashboards for business users | QuickSight |
| Spark at cluster scale | EMR |
| Copy a file system or object store into AWS | DataSync |
| Ongoing hybrid file access | Storage Gateway |

Secure the ingestion point: VPC endpoint, a bucket policy, KMS, and no public bucket. A data lake bucket that is world-readable fails Domain 1 even if the pipeline is fast.

---

## Domain 4 — Cost-optimized architectures (20%)

Cost items still have to work. The cheapest design that misses the RTO is wrong. The right move is the cheapest design that meets every other sentence in the stem.

### Task 4.1 — Cost-optimized storage

Knowledge: Requester Pays, cost allocation tags, multi-account billing, Cost Explorer, Budgets, CUR, FSx, EFS, S3, EBS, backup, HDD versus SSD, lifecycles, DataSync, Transfer Family, Storage Gateway, access patterns, tiering.

Skills: batch versus single uploads, size, cheapest transfer path, when storage should autoscale, S3 lifecycle, backup and archive, migration service, tier, the storage service itself.

S3 classes you must separate:

| Class | Use |
| --- | --- |
| Standard | Hot, frequent, Multi-AZ |
| Intelligent-Tiering | Unknown or changing access. Small monitoring fee. The “we do not know the pattern” answer |
| Standard-IA and One Zone-IA | Infrequent, retrieval fee. One Zone-IA is one AZ and loses a durability stem |
| Glacier Instant Retrieval | Rarely accessed, milliseconds when you do access it |
| Glacier Flexible Retrieval | Minutes to hours |
| Glacier Deep Archive | Cheapest, hours, long retention |
| Express One Zone | Extreme S3 performance in one AZ. A performance answer, and a cost increase. Do not pick it to save money |

Lifecycle rules move objects. They do not shrink an EBS volume. EBS type changes (gp2 to gp3) are the block-storage cost move. gp3 sets IOPS and throughput without inflating the size.

EFS Infrequent Access and lifecycle, FSx HDD versus SSD, and “do you need a file system at all” are the file-storage cost moves. If the app can use S3, S3 is usually cheaper than a file system you keep hot.

Transfer cost into AWS: DataSync online, Snow Family when the link would take too long (the rough classroom rule is: if the transfer would take more than about a week on the available bandwidth, look at Snow). Transfer Acceleration speeds an upload over long distance. It is not the cheapest per GB. It is the fastest internet path.

Requester Pays: the caller pays the transfer. Rare stem. It is the answer when a bucket is shared with other accounts who should bear the egress.

### Task 4.2 — Cost-optimized compute

Knowledge: tags, billing tools, Regions, Spot, Reserved Instances, Savings Plans, edge, Outposts, instance families, containers and serverless as utilization tools, Auto Scaling, hibernation.

Skills: ALB versus NLB versus Gateway Load Balancer (also a cost question when someone buys an NLB they do not need), horizontal versus vertical, hibernation, Lambda versus EC2 versus Fargate, prod versus non-prod availability, family, size.

Purchasing:

| Option | Pay for | Lose when |
| --- | --- | --- |
| On-Demand | No commitment | The workload is steady and large |
| Compute Savings Plan | A $/hour commit, flexible across EC2, Fargate, Lambda | You need a specific RDS reservation. Savings Plans do not cover RDS the way RDS Reserved Instances do |
| EC2 Instance Savings Plan | Cheaper, locked to a family in a Region | The family might change |
| Standard Reserved Instance | Steadiest discount, least flexible | You might change size or Region. Convertible RI is the more flexible RI |
| Spot | Up to a large discount | The instance can be interrupted. Fine behind a queue. Wrong for the only database |
| Dedicated Host | Licensing that is per-socket or per-core, or a compliance rule | You wanted isolation of a kernel exploit. That stem wants a dedicated host only if the license says so. A dedicated instance is a weaker, less common answer |
| Hibernation | Stop and keep RAM state, no hourly compute | The instance type must support it. It is not HA |

Non-prod does not need Multi-AZ unless the stem says developers cannot work during a failure. Prod does.

Outposts is the cost and the placement answer when the workload must stay in a facility AWS does not own and latency to the Region is too high. It is not the cheap answer. Wavelength is the 5G edge answer. Both are in scope.

### Task 4.3 — Cost-optimized databases

Knowledge: caching, retention, capacity units, proxies, engines, replicas, Aurora, DynamoDB.

Skills: backup frequency, MySQL versus PostgreSQL when either would work (pick the one the team runs, unless a feature forces the other), DynamoDB versus RDS, time-series and columnar types, migrating schema and data.

Cost moves that are correct:

- A rarely used dev database on RDS: stop it, or use Aurora Serverless v2, or use a smaller class. Do not buy a Multi-AZ db.r6i.4xlarge for a demo.
- Read-heavy RDS: one reader, or a cache, before a bigger writer.
- DynamoDB on-demand for spiky and new. Provisioned for flat and high. Infrequent access tables and TTL to delete expired items.
- Backup retention: automated backups kept longer than the RPO needs cost money. Match retention to the policy. Copy snapshots only to the Regions you will restore in.
- RDS Proxy costs money. Buy it when connection storms are the incident. Do not add it as a default decoration.

### Task 4.4 — Cost-optimized networks

Knowledge: load balancers, NAT instance versus NAT Gateway, private versus dedicated versus VPN, Transit Gateway versus peering, DNS.

Skills: one shared NAT versus NAT per AZ (shared is cheaper and is a single point of failure; per AZ is the resilient answer; the stem tells you which constraint wins), DX versus VPN versus internet, routes that avoid cross-AZ and cross-Region and NAT charges, CloudFront and edge cache, throttle, VPN count and DX port speed.

The bill you should see coming:

| Path | What to do |
| --- | --- |
| Private subnet to S3 through NAT | Gateway endpoint |
| Private subnet to DynamoDB through NAT | Gateway endpoint |
| Cross-AZ application chatter | Keep a client and its database traffic in-AZ when you can, or accept the charge for real Multi-AZ |
| Cross-Region replication | Only if the DR pattern needs it |
| Users far away hitting EC2 directly | CloudFront for cacheable HTTP |
| Many VPCs peered in a mesh | Transit Gateway. Peering is cheaper at two VPCs and does not transit |
| Idle public IPv4 and idle NAT and idle load balancers | Delete them. Trusted Advisor and Compute Optimizer point at waste. IPv4 public addresses have had a charge for a while. Do not design a public IP per instance when an ALB will do |

Throttling: API Gateway usage plans, WAF rate-based rules, and SQS as a buffer are the cost and protection tools when a client can overrun you. Raising every quota is the performance answer, not the cost answer.

---

## In-scope services (SAA-C03)

The guide says the list is non-exhaustive. Names below are the ones printed on the guide reviewed 11 October 2026. “Amazon Quick” in the analytics list is QuickSight.

**Analytics.** Athena, Data Exchange, Data Firehose, EMR, Glue, Kinesis, Lake Formation, MSK, OpenSearch Service, QuickSight, Redshift.

**Application integration.** AppFlow, EventBridge, MQ, SNS, SQS, Step Functions.

**Cost.** Budgets, Cost and Usage Report, Cost Explorer, Savings Plans.

**Compute.** Batch, EC2, EC2 Auto Scaling, Elastic Beanstalk, Outposts, Serverless Application Repository, VMware Cloud on AWS, Wavelength.

**Containers.** ECR, ECS, ECS Anywhere, EKS, EKS Anywhere, EKS Distro.

**Database.** Aurora, Aurora Serverless, DocumentDB, DynamoDB, ElastiCache, Keyspaces, Neptune, RDS, Redshift.

**Developer tools.** X-Ray only. The rest of the developer-tool family is listed out of scope for this exam.

**Frontend.** Amplify, API Gateway, Device Farm.

**Machine learning.** Comprehend, Lex, Polly, Rekognition, SageMaker AI, Textract, Transcribe, Translate. These are “pick the API that matches the sentence” items. You are not training a model on SAA.

**Management.** AWS Auto Scaling, CLI, CloudFormation, CloudTrail, CloudWatch, Compute Optimizer, Config, Control Tower, Health Dashboard, License Manager, Managed Grafana, Managed Prometheus, the console, Organizations, Service Catalog, Systems Manager, Trusted Advisor, Well-Architected Tool.

**Media.** Elastic Transcoder, Kinesis Video Streams.

**Migration.** Application Migration Service, DataSync, DMS, Snow Family, Transfer Family.

**Networking.** Client VPN, CloudFront, Direct Connect, ELB, Global Accelerator, PrivateLink, Route 53, Site-to-Site VPN, Transit Gateway, VPC.

**Security.** Artifact, ACM, CloudHSM, Cognito, Detective, Directory Service, Firewall Manager, GuardDuty, IAM Identity Center, Inspector, KMS, Macie, Network Firewall, RAM, Secrets Manager, Security Hub, Shield, WAF, IAM.

**Serverless.** Fargate, Lambda.

**Storage.** Backup, EBS, EFS, FSx for all types, S3, S3 Glacier, Storage Gateway.

## Out of scope on the SAA-C03 guide

Know these well enough to discard them. Do not build a study week around them for this exam. Several are in scope on SAP or DVA, and this pack still teaches them there.

| Listed out of scope | Why a stem might still mention it |
| --- | --- |
| MWAA | A managed Airflow distractor against Step Functions |
| Amazon Sumerian | Dead AR product |
| Managed Blockchain | SAP lists it in scope. SAA lists it out |
| Lightsail | The simple VPS. SAP lists it in scope. SAA lists it out. Enterprise HA stems do not want it on either exam |
| RDS on VMware | Legacy |
| CDK, CloudShell, CodeArtifact, CodeBuild, CodeCommit, CodeDeploy, Corretto, FIS, “AWS Tools and SDKs” | Developer exam material. On SAA the IaC answer is CloudFormation. Failure drills are described, but FIS is not the named tool on this guide |
| Location Service | Mobile maps |
| GameLift | Also out on SAP |
| All of IoT | SAP lists IoT in scope. SAA does not |
| MXNet, DeepComposer, DLAMI, Deep Learning Containers, DevOps Guru, Elastic Inference, HealthLake, Inferentia, Personalize, PyTorch, TensorFlow | ML specialty noise. SageMaker AI and the managed AI APIs above are the SAA ML list |
| Console mobile app, ADOT | Ops tooling |
| Elemental media products and IVS | Media specialty. Elastic Transcoder remains the in-scope transcoder name on this guide |
| Migration Evaluator | Portfolio cost tool. Not the migration mechanism |
| Cloud Map | Service discovery. ECS Service Connect and Cloud Map matter more on SAP-C03 |
| Braket, Ground Station | Not this exam |

## Technologies the guide lists

Compute, cost management, database, disaster recovery, high performance, management and governance, microservices and component delivery, migration and data transfer, networking, resiliency, security, serverless and event-driven design, storage.

## Where the rest of the Associate study lives

| Need | File |
| --- | --- |
| Every task taught as scenarios, with exercises | `03-saa/01-domain-1-secure.md` through `04-domain-4-cost.md` |
| Hands-on drills | `03-saa/05-saa-exercises.md` and `05-labs/` |
| Timed original exam | `03-saa/06-saa-practice-exam.md` |
| Service mechanics shared with Professional and Developer | `02-services/` |
| Older service-by-service notes, diagrams, and extra practice tests | `../aws-sa-c03/` |

Use this file as the checklist. If you cannot answer a task’s “what you must be able to choose” table out loud, you are not ready for that domain, regardless of how many practice questions you have clicked.
