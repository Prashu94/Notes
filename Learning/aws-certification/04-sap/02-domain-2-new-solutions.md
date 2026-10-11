# SAP Domain 2 — New solutions (29%)

The heaviest Professional domain. The workload does not exist yet. You choose how it is deployed, how it survives, how it is locked down, how fast it is, and what it costs. Every sentence in the stem is a constraint. The option that violates one constraint is wrong even if the service is famous.

## 2.1 Deployment

| Requirement | Choice |
| --- | --- |
| Reviewable infrastructure, many accounts | CloudFormation StackSets, or CDK that synthesizes them |
| Serverless app | SAM |
| Web app, team does not want a cluster | Elastic Beanstalk or App Runner |
| Containers, no Kubernetes requirement | ECS on Fargate |
| Kubernetes is a requirement | EKS |
| Safe release and fast rollback | CodeDeploy blue/green or canary, Lambda aliases, Beanstalk immutable |
| Patch and no SSH | Systems Manager |
| Least operational overhead | The managed service. EC2 you patch yourself loses |

Rollback is part of the design. A pipeline with no alarm and no previous version is not a deployment strategy.

Detail: `02-services/12-deployment-cloudformation-cdk-sam-cicd.md`.

## 2.2 Business continuity

Use `06-disaster-recovery-design.md`. For a new system, design the replication with the RPO, not after the first outage.

Route 53: failover for active-passive, latency for active-active, weighted for a migration cutover, geolocation when the law cares where the user is. ARC routing controls when the Region looks healthy and is not.

Database: Aurora Global for SQL with about a second of lag and a promote. DynamoDB global tables for multi-Region writes. S3 CRR with RTC when the RPO is 15 minutes for objects. RDS cross-Region replica when they must stay on RDS and will promote it.

Test it. A Backup restore-testing plan or a DRS drill is the answer when the stem says they must prove recovery.

## 2.3 Security for the new system

Least privilege role. Security groups that reference each other. No 0.0.0.0/0 on the database. Gateway endpoints for S3 and DynamoDB. Interface endpoints when the subnet must not have a NAT. WAF and Shield on the public edge. Secrets Manager for anything that rotates. Patch Manager or a service that has no OS. Encryption with a customer managed key when they must disable it.

## 2.4 Reliability

Loose coupling is the reliability tool. SQS between tiers that fail independently. SNS or EventBridge for fanout. Step Functions when the process has steps and waits. Multi-AZ for the data store. An ASG with ELB health checks. Service quotas requested before launch. DNS that can move.

A cache is not a dependency unless the stem says the working set only fits in memory. Design the miss path.

## 2.5 Performance

Write the access pattern, then the engine. Do not pick RDS and hide a queue in a table. Do not pick DynamoDB and then require ad hoc joins.

Instance families: M general, C compute, R memory, T burstable and credit-limited, I or D local disk and ephemeral, G or P GPU. Placement groups: cluster for latency in one AZ, partition for rack-aware systems, spread for a few critical nodes.

gp3, not an oversized gp2. Aurora readers or ElastiCache before a bigger writer. Lambda memory is the CPU dial.

## 2.6 Cost of the new design

Price the data path. NAT, cross-AZ, and cross-Region show up as the surprise. Gateway endpoints, CloudFront for cacheable HTTP, and a DR pattern that matches the RTO are the cost controls. Compute Savings Plan for the base. Spot for the queue consumers. Intelligent-Tiering when access is unknown.

A second full Region for a 24-hour RTO fails this task. Backup and restore was enough.

## Scenarios

1. New checkout, RPO 1 minute, RTO 15 minutes, SQL, least operations. Aurora Global Database, a scaled-down fleet in the second Region (warm standby or pilot light depending on how fast the ASG can grow), Route 53 failover, a tested promote.
2. New image API, global users, files change monthly. S3 plus CloudFront. Not Global Accelerator. Not EC2 in every Region.
3. New internal API, no internet, calls S3, SQS, and Secrets Manager. VPC endpoints. No NAT. Interface endpoints for SQS and Secrets Manager, gateway for S3.
4. Spiky HTTP, under a second, unknown traffic next quarter. Lambda plus API Gateway or a Fargate service with target tracking. Not a fixed EC2 fleet sized for the peak.

## Deployment, with the failure mode

CloudFormation is the reviewable artifact. A change set shows a replacement before you execute it. A stack policy refuses a replacement of the database. `DeletionPolicy: Retain` or `Snapshot` means a stack delete is not a data delete. StackSets with service-managed permissions deploy the baseline into an OU, so a new account does not wait for someone to remember the trail, the Config recorder, and the roles. CDK synthesizes CloudFormation. On Professional, CDK is a normal answer when the team writes it and the pipeline runs `cdk diff`. The thing you review is still the change set.

The pipeline does not live in the management account and it is not `AdministratorAccess`. It lives in shared services. It assumes a deploy role in the workload account. That role can update the application stacks and cannot edit the SCP, the trail, or the account contacts. A manual approval sits in front of production. An alarm rolls the deploy back. Image scanning and dependency scanning fail the build. That last sentence is also the SAP-C03 pipeline skill. It is already the right design on C02.

| Release shape | You are buying | You are refusing |
| --- | --- | --- |
| All-at-once | Speed in dev | Any production availability sentence |
| Rolling with an extra batch | Capacity never drops below the current size | An instant return to the old code. You are moving a batch at a time |
| Blue/green | The old environment stays up. The listener moves. Rollback is moving it back | The cost of two copies during the deploy, and a database migration that cannot run twice |
| Canary | A slice of production traffic, then an alarm | A change that is unsafe at 5 percent. Schema migrations that break the old code still break the canary |
| Lambda alias plus CodeDeploy | The version is immutable. `$LATEST` is not the production target | Publishing over `$LATEST` and pointing the API at it |
| Immutable on Beanstalk | A new ASG, then the cutover | In-place updates that leave half the instances patched |

Rollback is a designed object: the previous task definition, the previous AMI, the previous Lambda version, the previous CloudFormation stack. "We will redeploy the old git tag by hand" is not a strategy if the schema has already moved. The stem that includes a schema change wants an expand-contract migration: add the new column, deploy code that writes both, backfill, switch readers, then remove the old column. One deployment that drops the old column first fails the rollback sentence.

## Business continuity for a system that does not exist yet

Design the replication with the RPO. Do not add it after the first outage and call it the architecture.

| Data | Replication that matches a short RPO | What you still do at failover |
| --- | --- | --- |
| Aurora | Global Database, typically sub-second lag on the storage | Fail over the writer. Promote is an operation, not a hope |
| RDS | Cross-Region read replica | Promote it. Repoint. Accept the lag |
| DynamoDB | Global tables | Both Regions already write. You designed the conflict, or you were wrong to pick it |
| S3 | CRR, and Replication Time Control when they name 15 minutes | RTC is a feature you turn on, not a property of every CRR rule. Existing objects need a replication batch |
| EBS servers | Elastic Disaster Recovery | A drill. The drill is the product |
| Anything whose RPO is hours | AWS Backup, cross-Region copy, a timed restore | You do not pay for continuous replication |

Route 53 failover is active-passive and needs a health check that can see the failure. Latency routing is active-active. Weighted routing is the migration cutover, where you move 10 percent and watch. Geolocation is the law, not the latency. Geoproximity is latency plus a bias you set. ARC routing controls are the answer when the health check would stay green. A one-day TTL on the record they intend to fail over is a self-inflicted RTO. Set the TTL to something the RTO can afford, and prefer Accelerator or ARC when the RTO is seconds.

Quotas in the second Region are part of the design. A pilot light that has never been scaled will fail on EIP, VPC, Lambda concurrency, or a Regional service limit. Request the quota as part of the build, not as part of the incident.

## Security, reliability, performance, cost, as one design

A new system gets one paragraph each, and they have to agree.

Security. Least-privilege roles, separate task role and execution role, security groups by reference, no database route to an IGW, gateway endpoints for S3 and DynamoDB, interface endpoints when there must be no NAT, WAF on the public HTTP edge, Shield Advanced only when they asked for the response team or cost protection, Secrets Manager for rotation, customer managed KMS when they must disable the key, patching via the managed service or Patch Manager. Cognito for app users. Identity Center for staff. Do not invent IAM users for the new company.

Reliability. SQS between tiers that fail independently, with an idempotent consumer and a DLQ that is alarmed. SNS or EventBridge when more than one consumer must see the event. Step Functions when there are steps and a wait. Multi-AZ for the data store that has a Multi-AZ mode. An ASG with an ELB health check and a minimum of two. The cache has a miss path. The health check does not depend on a dependency whose failure should drain the whole fleet unless that is what you meant.

Performance. Write the access pattern, then the engine. A queue hidden in a SQL table is a poll. DynamoDB with a hot key is a throttle with a low table-level metric. Aurora readers or a cache before a bigger writer. gp3 rather than a gp2 volume grown for IOPS. Lambda memory is the CPU dial. Placement groups are for the latency inside one AZ, which contradicts Multi-AZ, so they apply to a specific tier and not to the web fleet. Families: M general, C compute, R memory, T burstable and credit-limited, I or D for local disk, G or P for GPU.

Cost. Price the path. NAT data processing, cross-AZ, and cross-Region are the surprise lines. Gateway endpoints, CloudFront for cacheable HTTP, and a DR pattern that matches the RTO are the controls. Compute Savings Plan for the base. Spot for consumers that can die. Intelligent-Tiering when access is unknown. A second hot Region for a 24-hour RTO fails this task. Backup and restore was enough. Non-production does not copy production's Multi-AZ unless they said developers cannot work during a failure.

## Scenarios, worked

**1.** New checkout. RPO one minute. RTO 15 minutes. SQL. Least operations. Aurora Global Database. A scaled-down fleet in the second Region if 15 minutes is a scale-up, which is warm standby, or pilot light if you have timed the ASG and the promote inside 15 minutes and the stem wants the lower bill. Route 53 failover with a health check. A tested promote. DynamoDB would win only if they allowed you to leave SQL. Multi-AZ alone fails the Regional RPO.

**2.** New image API. Users worldwide. Files change monthly. S3 plus CloudFront, origin access control, a long TTL, invalidation or a versioned object key when a file does change. Global Accelerator does not cache. EC2 in every Region is the bill and the patch load.

**3.** New internal API. No internet. Calls S3, SQS, and Secrets Manager. Gateway endpoint for S3. Interface endpoints for SQS and Secrets Manager, private DNS on. No NAT. The security groups on the interface endpoints allow the application subnets. A NAT "just in case" fails the no-internet sentence and recreates the data-processing bill.

**4.** Spiky HTTP, under a second of work, unknown traffic next quarter. Lambda and API Gateway, or Fargate with target tracking from a small minimum. Not a fixed EC2 fleet sized for a peak you have not measured. If the p99 on a cold start breaks the SLO, provisioned concurrency or a small warm Fargate service. If the work can run for minutes, do not put it behind the 29-second API integration. Queue it.

**5.** The team knows Kubernetes and the company standard is EKS. Do not move them to ECS to show a preference. Do not move a team with no Kubernetes skill onto EKS because it was in a blog. The stem's skill constraint is a real constraint. Fargate on EKS is the "Kubernetes API, no nodes to patch" middle.

**6.** A new data pipeline. Producers are applications. Consumers are a warehouse and a search index. Kinesis or MSK if they need replay and multiple independent readers. Firehose if the only job is to land in S3 and Redshift. SQS if each event is a unit of work for one worker. Step Functions if the steps are a business process with a failure state a human reads. Picking all of them is how diagrams get expensive.

## Exercise

Write four constraints: an RPO, a protocol, a team skill, and a cost word. For each, name one famous service you reject and the sentence that rejects it.

A complete answer looks like this. RPO of 24 hours rejects Aurora Global Database, because backup copy meets it for less money. Protocol UDP rejects CloudFront. A team that cannot run Kubernetes rejects EKS even if the scale would suit it. "Lowest cost" plus an RTO of two days rejects a warm standby you run all month. If you cannot write the rejection, the constraint is still a slogan.
