# SAP-C02 exam blueprint

Source: AWS Certified Solutions Architect – Professional exam guide (SAP-C02), the HTML and PDF published on AWS Documentation, reviewed 11 October 2026. The PDF cover is copyright 2026. Weights are AWS’s.

Role in one line: design optimized solutions, across applications and accounts, using the AWS Well-Architected Framework.

| Domain | Weight | One-line job |
| --- | --- | --- |
| 1. Design Solutions for Organizational Complexity | 26% | Networks, security, resilience, multi-account governance, and cost visibility for an organization that already has many teams |
| 2. Design for New Solutions | 29% | A new workload: how it is deployed, how it survives, how it is secured, how it performs, what it costs. Heaviest domain |
| 3. Continuous Improvement for Existing Solutions | 25% | The workload is already running. Find the operational, security, performance, reliability, or cost fix |
| 4. Accelerate Workload Migration and Modernization | 20% | Choose what to move, how to move it, what it lands on, and what to modernize after it lands |

65 scored questions plus 10 unscored. 180 minutes. 300 USD. Passing score 750 scaled. No case studies. Recommended experience is 2 or more years designing and implementing on AWS. The candidate can advise across multiple applications inside a complex organization.

Out of scope for the target candidate, per the guide: frontend development for mobile apps, 12-factor app methodology, and in-depth operating system knowledge. You still choose Amplify or AppSync when the stem is a mobile backend. You do not write Swift.

Emerging topics (pretest, unscored on SAP-C02, scored material on SAP-C03): Bedrock Guardrails, AgentCore Identity, and human-oversight workflows with Step Functions. Study them in `04-sap/09-sap-c03-new-skills.md` even if you sit C02, because the distractors are already in the item bank.

## How the four domains differ in the stem

The domain is usually obvious from the tense of the question.

| Stem shape | Domain |
| --- | --- |
| “A company has 40 accounts, a data center, and a security team that must see every trail.” | 1 |
| “A company is building a new checkout service. RPO is 5 minutes. They want the least operational overhead.” | 2 |
| “An existing application is slow / expensive / failing audits. What should the architect do?” | 3 |
| “A company will move 200 VMs and an Oracle database in the next two quarters.” | 4 |

Domains overlap. A migration question still has an RPO. Read the verb. “Select the migration tool” is Domain 4. “Design the landing zone the migrated apps will live in” is Domain 1 plus Domain 4.

---

## Domain 1 — Organizational complexity (26%)

### Task 1.1 — Architect network connectivity strategies

The organization has more than one VPC, or a data center, or both. Pick the connectivity, the DNS, and the segmentation. Then prove you can see the traffic.

Knowledge the guide names:

- AWS global infrastructure (Regions, Availability Zones, Local Zones, Wavelength, Outposts).
- VPC, Direct Connect, VPN, transitive routing, and AWS container networking.
- Hybrid DNS: Route 53 Resolver and on-premises DNS.
- Segmentation: subnets, IP addressing, connectivity among VPCs.
- Network traffic monitoring.

Skills the guide names:

- Connectivity options for multiple VPCs.
- Connectivity for on-premises, colocation, and cloud.
- Region and AZ choice from latency and data-residency needs.
- Troubleshooting flows with AWS tools.
- Service endpoints for integrations.

What to be able to design before you leave this task:

| Need | Design |
| --- | --- |
| Two VPCs, same Region, small, no future growth | VPC peering. It is not transitive |
| Many VPCs, shared services, on-premises, transitive | Transit Gateway. Share it with RAM |
| Thousands of VPC attachments, more segmentation | AWS Cloud WAN |
| Private access to one SaaS or one endpoint service, no routing mesh | PrivateLink (interface endpoint or endpoint service) |
| Service-to-service HTTP across VPCs and accounts with IAM auth | VPC Lattice (heavier on SAP-C03, already the right modern answer) |
| 1–10 Gbps predictable line, consistent latency | Direct Connect. Add a VPN backup or a second DX location for resilience |
| Encrypt over the internet, quick to stand up | Site-to-Site VPN. Throughput is lower and jitter is higher than DX |
| DX encryption | Private VIF or transit VIF plus VPN over DX, or MACsec where the port supports it |
| Clients on the public internet to a private ALB | Do not expose the ALB. Use CloudFront or Global Accelerator with an origin, or Client VPN / Verified Access for employees |
| Hybrid DNS, on-prem names resolved in the VPC | Resolver inbound endpoint |
| VPC names resolved on-premises | Resolver outbound endpoint plus a forwarding rule |
| Overlapping RFC1918 during a migration | Private NAT, or re-address, or a transit account with controlled NAT. Peering fails on overlap |
| See who talked to whom | VPC Flow Logs to CloudWatch Logs or S3. Traffic Mirroring for packet capture. Reachability Analyzer for “why can’t A reach B” |
| Containers that must join the same mesh | ECS with awsvpc mode, EKS with the VPC CNI, ECS Service Connect or VPC Lattice for service discovery without a wide-open security group |

Commands to practice (sandbox, one VPC is enough to learn the API shape):

```bash
aws ec2 describe-vpcs --query 'Vpcs[].{Id:VpcId,Cidr:CidrBlock}' --output table
aws ec2 describe-vpc-endpoints --query 'VpcEndpoints[].{Id:VpcEndpointId,Type:VpcEndpointType,Service:ServiceName,State:State}'
aws ec2 create-vpc-endpoint \
  --vpc-id "$VPC_ID" \
  --service-name com.amazonaws.us-east-1.s3 \
  --vpc-endpoint-type Gateway \
  --route-table-ids "$RTB_ID"
aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids "$VPC_ID" \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name /vpc/flow \
  --deliver-logs-permission-arn "$ROLE_ARN"
```

Transit Gateway and Direct Connect are design exercises unless you already pay for them. The decision table above is what the item tests.

Study: `01-foundations/05-networking-foundations-for-architects.md`, `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md`.

### Task 1.2 — Prescribe security controls

The organization needs a standard for identity, network control, encryption, and a place where security events land.

Knowledge the guide names:

- IAM and IAM Identity Center.
- Route tables, security groups, network ACLs.
- KMS and ACM.
- CloudTrail, IAM Access Analyzer, Security Hub, Inspector.

Skills:

- Cross-account access.
- Third-party identity providers.
- Encryption at rest and in transit.
- Centralized security event notification and auditing.

Design you must be able to defend:

- Humans use Identity Center, permission sets, and an external IdP (Okta, Entra ID, Ping). No long-lived IAM users for staff.
- Workloads use IAM roles. Cross-account access is `sts:AssumeRole` with an external ID when a third party is involved, or Identity Center plus RAM when the resource can be shared.
- SCPs are guardrails (maximum permissions). They do not grant access. Identity-based policies grant access. An explicit deny in an SCP wins.
- Organization trail in CloudTrail, logs in a restricted log-archive account, validated with log file integrity, optionally encrypted with a KMS key the member accounts cannot disable.
- Security Hub, GuardDuty, and Inspector delegated to a security account. EventBridge rules fan findings to a ticket or to chat.
- Access Analyzer finds resources shared outside the zone of trust. Use it when the stem says “unintended public or cross-account access.”
- KMS multi-Region keys when the same ciphertext must be decrypted in a second Region. Separate regional keys when blast radius matters more than convenience.
- ACM public certificates for ALB, CloudFront, and API Gateway. Private CA when the cert must identify internal services and public ACM is the wrong trust.
- Security groups are stateful and preferred. NACLs are stateless, subnet-wide, and the tool for a blunt deny of a CIDR.

Study: `01-foundations/02-iam-sts-identity-center-ram.md`, `01-foundations/04-accounts-organizations-control-tower.md`, `01-foundations/06-encryption-kms-certificates-secrets.md`, `02-services/13-security-hub-guardduty-inspector-macie-detective.md`.

### Task 1.3 — Design reliable and resilient architectures

This task is the organization-wide resilience standard. Task 2.2 is the same ideas applied to one new system. Learn the definitions once.

Knowledge:

- RTO and RPO.
- Disaster recovery strategies: Elastic Disaster Recovery, pilot light, warm standby, multi-site.
- Backup and restore.

Skills:

- Pick a DR pattern from RTO and RPO.
- Architectures that recover without a human clicking failover, when the requirement says automatic.
- Scale-up versus scale-out.
- Backup and restore that matches the RPO, including retention and restore testing.

The four patterns, in rising cost and falling RTO/RPO:

| Pattern | What is already running in the recovery Region | Typical RTO | Typical RPO | AWS building blocks |
| --- | --- | --- | --- | --- |
| Backup and restore | Nothing hot. Data copies exist | Hours | Hours, unless the backup is continuous | AWS Backup, S3 CRR, RDS snapshots copied cross-Region, EBS snapshots |
| Pilot light | Core data is live and replicated. Compute is off or minimal | Tens of minutes | Minutes | Aurora Global Database or DMS CDC, scaled-down ASG at zero or one, Route 53 health checks ready |
| Warm standby | A scaled-down but fully functional copy is serving or ready to scale | Minutes | Seconds to minutes | Scaled-down ASG, Aurora global or cross-Region replica, Route 53 failover |
| Multi-site active/active | Both Regions take traffic | Near zero, sometimes seconds for DNS | Near zero | DynamoDB global tables, Aurora global with write forwarding caveats, Route 53 latency or ARC routing controls |

Elastic Disaster Recovery (DRS) is the lift-and-shift answer: continuous block replication of servers into a staging area, then a failover launch. Use it when the workload is still servers and the team will not refactor before the DR requirement is due. It is not the answer for a system you are allowed to rebuild on Aurora and Lambda.

Automatic recovery means health checks, Auto Scaling, Multi-AZ, and a routing change that does not wait for a bridge call. A runbook that says “architect updates the record” fails an “automatic” stem.

Scale-up is a bigger instance. Scale-out is more instances, or more partitions, or more Lambda concurrency. Professional stems that say “variable traffic” and “survive an instance failure” want scale-out.

Study: `04-sap/06-disaster-recovery-design.md`, `02-services/18-resilience-drs-arc-fis-resilience-hub.md`.

### Task 1.4 — Design a multi-account AWS environment

Knowledge:

- Organizations and Control Tower.
- Multi-account event notifications.
- Sharing resources across environments.

Skills:

- Account structure.
- Central logging and event notifications.
- A governance model.

Account design you should draw from memory:

```text
Management (payer)          billing, SCPs, only break-glass access
  Security OU
    Security tooling        GuardDuty, Security Hub, Detective delegated admin
    Log archive             CloudTrail, Config, VPC Flow Logs, immutable bucket
  Infrastructure OU
    Network                 Transit Gateway, RAM shares, Route 53 Resolver, egress
    Shared services         CI/CD, golden AMIs, Directory, PrivateLink endpoints
  Workloads OU
    Prod / Staging / Dev    one account per application per environment when blast radius matters
  Sandbox OU                SCPs that deny expensive Regions and services
  Suspended OU              accounts being closed
```

Control Tower is the managed landing zone: Account Factory, guardrails (preventive SCPs and detective Config rules), and a dashboard. Build-it-yourself Organizations is the answer only when the stem says they already have a custom landing zone or Control Tower cannot express a required guardrail. “Least operational overhead” plus “new multi-account” is Control Tower.

Share Transit Gateway, Route 53 rules, subnets, License Manager configurations, and Aurora or RDS clusters that support it, through RAM. Do not copy the resource into every account.

Event notifications: organization CloudTrail to EventBridge in the security account, or a central bus with cross-account rules. Member accounts should not each invent a Slack webhook.

Study: `01-foundations/04-accounts-organizations-control-tower.md`, `04-sap/05-multi-account-reference-architecture.md`.

### Task 1.5 — Determine cost optimization and visibility strategies

This is organization-wide cost. Task 2.6 and Task 3.5 are the workload-level versions.

Knowledge:

- Trusted Advisor, Pricing Calculator, Cost Explorer, Budgets.
- Reserved Instances, Savings Plans, Spot.
- Compute Optimizer, S3 Storage Lens.

Skills:

- Monitor cost and usage.
- Tagging that maps spend to business units.
- How purchasing options change cost and performance.

What each tool is for:

| Tool | Use it when the stem says |
| --- | --- |
| AWS Pricing Calculator | Estimate before launch. It does not see your bill |
| Cost Explorer | Interactive history, forecasts, RI/SP recommendations |
| Cost and Usage Report (CUR) | Line-item truth in S3, query with Athena. The audit and chargeback answer |
| Cost allocation tags | User-defined tags must be activated in Billing before they split the bill |
| Budgets | Alert at a threshold. A budget does not stop resources unless you add a custom action |
| Trusted Advisor | Idle load balancers, underused instances, security checks. Full checks need Business Support or higher, with some checks now in the free tier |
| Compute Optimizer | Rightsizing recommendations from utilization |
| S3 Storage Lens | Organization-wide object storage visibility, incomplete multipart uploads, storage-class mix |
| Savings Plans | Compute, EC2 Instance, and SageMaker. Flexible across size and, for Compute SP, across EC2, Fargate, and Lambda |
| Reserved Instances | Standard and Convertible still exist. Prefer Savings Plans in new designs unless the stem is a specific RDS, ElastiCache, Redshift, OpenSearch, or DynamoDB reservation, which Savings Plans do not cover the same way |
| Spot | Fault-tolerant, interruptible. Never the only copy of state |

A tagging strategy the exam accepts: mandatory tags (`owner`, `environment`, `cost-center`, `application`) enforced by tag policies or by an SCP that denies `Create*` without tags, plus activated cost allocation tags, plus CUR.

Study: `02-services/16-cost-management.md`.

---

## Domain 2 — New solutions (29%)

### Task 2.1 — Design a deployment strategy to meet business requirements

Knowledge: CloudFormation (IaC), CI/CD, change management, Systems Manager.

Skills:

- Path for a new service or an upgrade.
- Deployment strategies and rollback.
- Managed services to cut provisioning and patching.
- Let AWS run the hard part.

Decisions:

| Requirement | Choice |
| --- | --- |
| Repeatable infrastructure, reviewable change | CloudFormation or CDK (CDK synthesizes CloudFormation). StackSets for many accounts |
| Serverless app with functions, APIs, and tables | SAM |
| Containers, the team wants a PaaS | Elastic Beanstalk or App Runner. Beanstalk when you need EB extensions, worker tiers, or more control. App Runner when the stem is “from source or image, least ops” |
| Pipeline the company owns | CodeCommit is legacy (new customers are steered to external Git). CodePipeline + CodeBuild + CodeDeploy, or a third-party pipeline that assumes a deploy role |
| Safe app release on EC2 or Lambda | CodeDeploy: all-at-once, rolling, blue/green, canary. Lambda aliases and weighted traffic |
| Servers that must be patched and joined to a state | Systems Manager: State Manager, Patch Manager, Session Manager, Parameter Store |
| Rollback | CloudFormation stack rollback, CodeDeploy automatic rollback on CloudWatch alarms, Lambda alias pointing back at the previous version, Beanstalk swap back |

“Least operational overhead” on a brand-new web API with spiky traffic is Lambda plus API Gateway or an ALB, not an ASG you patch yourself.

Study: `02-services/12-deployment-cloudformation-cdk-sam-cicd.md`, `02-services/02-lambda-and-serverless.md`.

### Task 2.2 — Design a solution to ensure business continuity

Knowledge: global infrastructure, Route 53 routing, RTO/RPO, the four DR scenarios, DR solutions on AWS.

Skills: configure DR, replicate data and databases, test DR, automate backup across AZs or Regions, survive a disruption, central monitoring that recovers proactively.

Route 53 routing policies you must separate:

| Policy | What it does | Continuity use |
| --- | --- | --- |
| Simple | One answer | No failover |
| Failover | Primary and secondary, health checked | Active/passive |
| Weighted | Percentages | Blue/green, canary, controlled migration |
| Latency | Lowest latency Region | Active/active for users |
| Geolocation | Continent/country/state of the resolver | Legal residency of *users*, compliance routing |
| Geoproximity | Bias traffic toward a Region | Shift load during an event. Traffic flow required |
| IP-based | CIDR of the client | Split a partner network |
| Multivalue answer | Several healthy records | Light health checking, not a load balancer |
| ARC routing controls | You flip a control. Health of the Region is not the signal | When the Region looks healthy and is not (gray failure) |

Database continuity, short version:

| Engine | Same-Region HA | Cross-Region |
| --- | --- | --- |
| RDS Multi-AZ | Synchronous standby, automatic failover, one endpoint | Cross-Region read replica is asynchronous. Promote it for DR |
| RDS Multi-AZ cluster (MySQL/PostgreSQL) | Two readable standbys | Still add a cross-Region replica for Region failure |
| Aurora | 6-way storage across 3 AZs, replicas are readers | Aurora Global Database: typical replication lag under a second, up to 5 secondary Regions |
| DynamoDB | Multi-AZ by default | Global tables, multi-Region active/active |
| S3 | Multi-AZ for Standard and the IA classes that say so. One-Zone classes are one AZ | CRR. Versioning required. Not a substitute for application transactions |

Test DR. AWS Elastic Disaster Recovery and backup plans both have test modes. A design that has never been failed over does not meet a stem that says “must validate recovery.”

Study: `04-sap/06-disaster-recovery-design.md`.

### Task 2.3 — Determine security controls based on requirements

Knowledge: IAM, route tables, security groups, NACLs, encryption, service endpoints, credential services, Shield, WAF, GuardDuty, Security Hub.

Skills: least privilege, inbound and outbound flows, attack mitigation for large web apps, encryption strategies, service endpoints, patch management.

Large web app, defense in order:

1. Route 53 plus CloudFront or Global Accelerator.
2. AWS Shield Standard is automatic. Shield Advanced when the stem has a large bill, custom detection, the DRT, or cost protection during a DDoS.
3. AWS WAF on CloudFront, ALB, API Gateway, or AppSync. Managed rule groups, rate-based rules, bot control when the stem says bots.
4. Security groups on the instances or tasks. NACLs only for an extra subnet deny.
5. WAF does not inspect traffic that never hits the resource it is attached to. Private origins stay private.
6. Patch with SSM Patch Manager and a maintenance window, or use Lambda and Fargate so the patch surface is the runtime AWS manages.
7. Secrets in Secrets Manager with rotation. Parameter Store for non-rotating config, SecureString when it must be encrypted.
8. Gateway endpoints for S3 and DynamoDB. Interface endpoints for everything else that must stay off the internet. Endpoint policies for least privilege.

Study: `02-services/10-edge-route53-cloudfront-global-accelerator-waf-shield.md`, `01-foundations/06-encryption-kms-certificates-secrets.md`.

### Task 2.4 — Design a strategy to meet reliability requirements

Knowledge: global infrastructure, S3/RDS/ElastiCache replication, multi-AZ and multi-Region, Auto Scaling, SNS/SQS/Step Functions, service quotas.

Skills: HA from business requirements, design for failure, loose coupling, failover operations, managed HA, Route 53 policies (latency, geolocation, simple).

Loose coupling is the reliability tool the stem describes without naming:

| Coupling smell | Replacement |
| --- | --- |
| API calls a downstream API synchronously and fails when it is slow | SQS between them, or Step Functions with retries |
| One event must reach many consumers | SNS to SQS fanout, or EventBridge |
| A workflow with compensation and human approval | Step Functions. Standard for long workflows (up to a year). Express for high-volume short workflows |
| A cache that is a hard dependency | ElastiCache with a timeout and a fallback to the database. Cache is an optimization until the stem says the working set only fits in memory |
| Quota will be hit at launch | Service Quotas request before launch. Design for the quota: partition the table, request a Lambda concurrency increase, shard the Kinesis stream |

Multi-AZ is one Region. It does not satisfy “survive a Regional outage.” Say that clearly in your notes.

Study: `02-services/05-messaging-sqs-sns-eventbridge-step-functions-mq.md`, `02-services/07-databases-rds-aurora-dynamodb-purpose-built.md`.

### Task 2.5 — Design a solution to meet performance objectives

Knowledge: performance monitoring, storage options, instance families, purpose-built databases.

Skills: large-scale access patterns, elastic architecture, caching and buffering and replicas, a method for picking purpose-built services, rightsizing.

Instance families you should recognize (names shift; the *intent* is stable):

| Intent | Family examples | Stem language |
| --- | --- | --- |
| Balanced | M6i, M7i, M7g | General web and app |
| Burstable, cheap, variable | T3, T4g | Dev, low baseline. Credits exhaust under steady high CPU |
| Compute | C6i, C7i, C7g | CPU-bound, batch, gaming |
| Memory | R6i, R7i, X2idn | In-memory, large caches, SAP HANA-class |
| Storage / local NVMe | I3, I4i, Im4gn, D3 | High sequential disk, data warehouses on EC2 |
| GPU | G, P, Inf, Trn | Training, graphics, inference |
| HPC | Hpc6id, Hpc7a | Tightly coupled MPI, cluster placement group |
| Graviton (g suffix) | Any `g` type | Price-performance when the software runs on Arm |

Placement groups: cluster for low latency inside one AZ, partition for large distributed systems (HDFS, Kafka) so racks fail separately, spread for a handful of critical instances that must be on distinct hardware.

Storage performance:

| Store | Performance story |
| --- | --- |
| EBS gp3 | Decouple IOPS and throughput from size. Default new general volume |
| EBS io2 Block Express | Highest durability and IOPS, Multi-Attach for io1/io2 in the same AZ |
| Instance store | Fastest, ephemeral. Never the only copy |
| EFS | Shared POSIX. Elastic or provisioned throughput. Max I/O versus general purpose |
| FSx for Lustre | HPC and ML, S3-linked |
| FSx for NetApp ONTAP / Windows / OpenZFS | Protocol and feature match (SMB, snapshots, multi-protocol) |
| S3 | Throughput scales with prefixes. Multipart for large objects. Use the right storage class for *access*, not for performance of the hot path |

Purpose-built data, the method:

1. Write the access pattern in one sentence (get by key, query by time range, graph traversal, full-text, warehouse scan, document by id).
2. Write the consistency, latency, and scale numbers.
3. Pick the engine that does that access natively. Do not pick relational and then hide a queue in a table unless the stem forces SQL.

Study: `02-services/01-compute-ec2-asg-batch-beanstalk.md`, `02-services/07-databases-rds-aurora-dynamodb-purpose-built.md`, `02-services/08-caching-elasticache-memorydb.md`.

### Task 2.6 — Determine a cost optimization strategy for the solution

Knowledge: Cost Explorer, Trusted Advisor, Pricing Calculator, pricing models, storage tiering, data transfer, managed services.

Skills: rightsize, pick a price model, model data transfer, put controls on spend.

Data transfer, the charges that surprise architects:

| Path | Usual charge |
| --- | --- |
| Into AWS from the internet | Free |
| Out to the internet | Charged per GB, rate depends on volume and Region |
| Cross-AZ in the same Region | Charged both ways for a lot of traffic (EC2, RDS replica lag traffic). Design AZ affinity when chatter is heavy |
| Cross-Region | Charged. Includes CRR and inter-Region VPC peering |
| Gateway endpoint to S3 or DynamoDB | No hourly endpoint charge, no NAT data processing charge |
| NAT Gateway | Hourly plus per GB. A chatty private subnet through NAT is a classic bill |
| Interface endpoint (PrivateLink) | Hourly per AZ plus data processing |
| CloudFront to the internet | Often cheaper than EC2 egress, and the origin fetch can be optimized |
| Direct Connect | Port hours plus data out. Data in is typically low or free. Good when volume is steady and large |
| Same-Region transfer to many AWS services via public endpoints | Can still be free in some cases and charged in others. Check the service page. Do not guess on exam day beyond the patterns above |

Storage tiering: S3 Intelligent-Tiering when the access pattern is unknown. Lifecycle to Glacier classes when the pattern is known and retrieval delay is acceptable. EBS gp3 instead of over-sized gp2. Delete unattached volumes and old snapshots with Data Lifecycle Manager.

Study: `02-services/16-cost-management.md`, `02-services/06-storage-s3-ebs-efs-fsx-backup-gateway.md`.

---

## Domain 3 — Continuous improvement (25%)

The system exists. The question is which change has the highest leverage. Do not redesign from zero unless the current design cannot meet the constraint.

### Task 3.1 — Improve operational excellence

Knowledge: alerting and automatic remediation, DR planning, CloudWatch, CI/CD strategies (blue/green, all-at-once, rolling), Systems Manager.

Skills: logging and monitoring strategy, improve the deployment process, prioritize automation, configuration management, failure exercises.

Map a symptom to a tool:

| Symptom | Improvement |
| --- | --- |
| They SSH to patch | Session Manager plus Patch Manager. Remove port 22 from the security group |
| Alarms page a human who runs the same commands | EventBridge or a CloudWatch alarm action to Systems Manager Automation or a Lambda remediator |
| Deploys are a Friday script | CodePipeline. Add a test stage. Rollback on alarm |
| They do not know if DR works | DRS drill, Backup restore test, or FIS experiment. Resilience Hub scores the application against an RTO/RPO policy (SAP-C03 raises this) |
| Logs are on the instance disk | CloudWatch agent, unified logs, retention, a metric filter |
| Ten accounts, ten dashboards | Cross-account observability in CloudWatch, or a log-archive account |

Deployment strategies on existing fleets:

| Strategy | Behavior | Use |
| --- | --- | --- |
| All-at-once | Stop the old, start the new | Dev. Downtime |
| Rolling | Replace a batch, then the next | Stateless ASG. Mixed versions during the deploy |
| Rolling with additional batch | Adds capacity first so capacity does not dip | Production rolling when you cannot lose throughput |
| Blue/green | Two environments, switch the listener or the DNS | Fast rollback. Needs double capacity during the cut |
| Canary | A slice of traffic | When you need production evidence before full shift |
| Linear | Traffic shifts in even steps | CodeDeploy Lambda/ECS |

Study: `02-services/11-observability-cloudwatch-xray-cloudtrail-config.md`, `02-services/18-resilience-drs-arc-fis-resilience-hub.md`.

### Task 3.2 — Improve security

Knowledge: retention and sensitivity and regulation, Config rules, Systems Manager and Secrets Manager, least privilege, security services, patching, backups.

Skills: secrets evaluation, least-privilege audit, defense in depth review, traceability, automated vulnerability response, patch process, backup process, remediation.

Improvement patterns that are correct answers:

- A static key in a repo becomes a role on the compute, or Secrets Manager if it is a third-party credential.
- `Action: *` on a human becomes Access Analyzer policy generation and permission boundaries for delegated admins.
- Public S3 becomes Block Public Access at the account, plus a bucket policy, plus Macie if the concern is sensitive data discovery.
- Unencrypted EBS becomes encryption by default and a re-encrypt or snapshot-copy into an encrypted volume.
- Config rule `restricted-ssh` or a custom rule, remediated by SSM Automation, when the stem wants detective plus corrective control.
- Inspector for CVE on EC2, ECR images, and Lambda. GuardDuty for threat *behavior*. They are not substitutes.
- CloudTrail organization trail with log file validation when an auditor asks for tamper-evident API history.
- Backup vault lock (AWS Backup) when retention must be immutable against a privileged insider or ransomware.

Study: `02-services/13-security-hub-guardduty-inspector-macie-detective.md`.

### Task 3.3 — Improve performance

Knowledge: Auto Scaling, instance fleets, placement groups, Global Accelerator, CloudFront, edge services, CloudWatch, SLAs and KPIs.

Skills: turn a business requirement into a metric, test a remediation, adopt a managed service, rightsize, find the bottleneck.

Method:

1. Put a number on the complaint (p99 latency, items per second, time to first byte).
2. Look at the metric that isolates the tier (ALB `TargetResponseTime`, RDS `ReadLatency` and `DatabaseConnections`, DynamoDB throttles, EBS `VolumeQueueLength`, NAT `BytesOutToDestination`, Lambda duration and init duration).
3. Fix the tier that is saturated. Adding CloudFront does nothing for a write-heavy API that is waiting on a single-AZ database with no reads.

Edge choice:

| Symptom | Service |
| --- | --- |
| Static and cacheable HTTP, users worldwide | CloudFront |
| Non-HTTP (UDP, MQTT, gaming) or static anycast IPs, fail over origins in seconds | Global Accelerator |
| Both | CloudFront for the HTTP cache, Global Accelerator for the TCP/UDP path |
| Users in one city, single-digit millisecond, the Region is too far | Local Zone or Wavelength or Outposts, depending on who owns the rack |

Study: `02-services/10-edge-route53-cloudfront-global-accelerator-waf-shield.md`, `02-services/01-compute-ec2-asg-batch-beanstalk.md`.

### Task 3.4 — Improve reliability

Knowledge: global infrastructure, replication, load balancing, Auto Scaling, HA, DR tools, quotas.

Skills: read growth trends, find the unreliable part, remove single points of failure, turn on replication and self-healing and elasticity.

Single points of failure the exam hides in plain sight:

- One NAT Gateway in one AZ. Put one NAT per AZ, or use Gateway endpoints so S3 and DynamoDB skip NAT.
- One RDS instance with no Multi-AZ.
- A load balancer in front of one instance.
- An Auto Scaling group with `min` 1 and a health check that is only EC2, so a dead process stays in service. Use ELB health checks.
- A queue consumer that deletes the message before the work commits.
- A service quota (Lambda concurrency 1,000 per Region as the default account quota, VPCs per Region, Elastic IPs) that the launch plan exceeds.
- DNS TTL of a day on a record they need to fail over.
- State on an instance store or on a single EBS volume with no snapshot.

Study: `04-sap/02-domain-2-new-solutions.md` (reliability section) and `04-sap/06-disaster-recovery-design.md`.

### Task 3.5 — Identify cost optimizations

Knowledge: Spot, scaling policies, rightsizing, RI and Savings Plans, network and transfer costs, alerts and reports.

Skills: usage reports for idle and hot resources, find unused resources, billing alarms, CUR at line-item level, tagging for allocation.

The usual waste, in the order questions appear:

1. Idle load balancers, unattached EIPs, unattached EBS, old snapshots, NAT in a VPC that could use gateway endpoints.
2. gp2 volumes sized up only to buy IOPS. Move to gp3 and set IOPS.
3. On-Demand steady state. Compute Savings Plan for even load. Spot for the burst fleet behind a queue.
4. Cross-AZ chatter inside a data pipeline. Pin tasks to a placement strategy or compress before you cross AZs.
5. S3 Standard for objects untouched in a year. Lifecycle or Intelligent-Tiering.
6. CloudWatch Logs retention set to never expire on debug logs.
7. A second Region “for HA” with a full copy of a workload whose RTO is 24 hours. Backup-and-restore was enough. Say so when the stem optimizes cost and the RTO allows it.

Study: `02-services/16-cost-management.md`.

---

## Domain 4 — Migration and modernization (20%)

### Task 4.1 — Select workloads and processes for migration

Knowledge: Migration Hub, portfolio assessment, asset planning, wave planning.

Skills: application migration assessment, the 7 Rs, TCO.

The 7 Rs (you will be asked to name the strategy that fits the sentence):

| Strategy | The sentence in the stem |
| --- | --- |
| Retire | Nobody uses it. Turn it off. Do not migrate it |
| Retain | Stays on-premises for now (latency to a factory, a license, a mainframe that is later) |
| Relocate | VMware to VMware on AWS (Elastic VMware Service / the older VMware Cloud path). Hypervisor-level move, little change |
| Rehost | Lift and shift servers. Application Migration Service or DRS-style replication |
| Replatform | Lift and reshape: Oracle on EC2 becomes RDS Oracle, a VM becomes Beanstalk or ECS, little code change |
| Repurchase | Buy a SaaS replacement |
| Refactor / re-architect | Change the design: monolith to services, self-managed DB to Aurora or DynamoDB |

Wave planning: discover, group by dependency, migrate the low-dependency low-risk apps first, leave tightly coupled core for a later wave. Migration Hub is the tracking pane across MGN, DMS, and partner tools. Application Discovery Service (agent or agentless collector) feeds the inventory. TCO uses the Migration Evaluator output or a Pricing Calculator model against the current data center bill. The exam will not ask you to compute a dollar figure. It will ask which input changes the decision (steady state versus burst, license, data transfer, staff).

### Task 4.2 — Determine the optimal migration approach

Knowledge: DataSync, Transfer Family, Snow Family, S3 Transfer Acceleration, Application Discovery Service, Application Migration Service, Direct Connect, Site-to-Site VPN, Route 53, Identity Center, Directory Service, DMS, SCT, Control Tower, Organizations.

Skills: pick the database mechanism, the application mechanism, the data transfer service, the security method on the tool, the governance model.

Data movement:

| Situation | Tool |
| --- | --- |
| Online file or object copy, NFS/SMB/HDFS/object, schedule and verify | DataSync |
| Ongoing SFTP/FTPS/FTP/AS2 into S3, EFS, or FSx | Transfer Family |
| Petabytes, limited bandwidth, days or weeks of ship time acceptable | Snowball Edge. Snowcone for smaller edge. Very large estates still get described as a Snowball-class offline transfer. Confirm the current device on the Snow page because device names have consolidated |
| One-time or repeated upload of large objects over a long fat network | S3 Transfer Acceleration, or multipart upload. DataSync if you want verification and a schedule |
| Database, ongoing replication, minimal downtime | DMS. Full load plus CDC |
| Schema and procedure conversion from Oracle/SQL Server to open engines | SCT, often into DMS |
| Servers, block replication, cutover in minutes | Application Migration Service |
| Already a disaster-recovery replica and you want to cut over | Elastic Disaster Recovery can also be the migration path |
| Identity during the move | Directory Service (AWS Managed Microsoft AD) when Windows auth must continue. Identity Center when you are ready to federate humans. Do not invent IAM users per employee as the migration end state |
| Network during the move | VPN to start, DX if the volume and the timeline justify a circuit. Route 53 weighted records for the cutover |

Secure the tool: IAM role on the MGN replication instance, encryption in transit (DMS and DataSync do this), KMS on the target bucket, a security group that allows replication ports only from the source, and no public snapshot sharing.

### Task 4.3 — Determine a new architecture for existing workloads

Knowledge: EC2, Elastic Beanstalk, ECS, EKS, Fargate, ECR, EBS, EFS, FSx, S3, Storage Gateway Volume Gateway, DynamoDB, OpenSearch, RDS, databases on EC2.

Skills: pick compute, container platform, storage, database.

Landing-zone choices:

| Source | Landing when change must be small | Landing when change is allowed |
| --- | --- | --- |
| Virtual machine | EC2, MGN | Beanstalk, ECS, or App Runner |
| Kubernetes already | EKS | EKS, or ECS if they want to leave Kubernetes |
| Docker, no Kubernetes requirement | ECS on Fargate | Same. EKS is extra control plane they must know |
| Windows file share | FSx for Windows File Server, or Storage Gateway if the data must also stay on-prem | S3 if the app can speak objects |
| NFS share | EFS or FSx for OpenZFS or ONTAP | S3 |
| SAN block that a server needs | EBS, or Volume Gateway for hybrid | Refactor off the SAN |
| Oracle / SQL Server | RDS for that engine, or EC2 if a feature RDS blocks | Aurora PostgreSQL/MySQL after SCT |
| MongoDB | DocumentDB, or MongoDB on EC2/self-managed if an API is incompatible | DynamoDB if the access pattern fits a key-value/document model |
| Elasticsearch | OpenSearch Service | OpenSearch, or a purpose-built store if they only needed one query type |
| Sessions or leaderboards | ElastiCache | DynamoDB with TTL, or MemoryDB if the data must be durable and Redis-compatible |

Storage Gateway Volume Gateway is the hybrid block cache or stored volume. File Gateway is NFS/SMB to S3. Tape Gateway replaces a tape library. Pick by protocol, not by the word “gateway” alone.

### Task 4.4 — Determine opportunities for modernization

Knowledge: Lambda, ECS, EKS, Fargate, S3, EFS, DynamoDB, Aurora Serverless, ElastiCache, SQS, SNS, EventBridge, Step Functions.

Skills: decouple, go serverless where it fits, pick a container service, pick a purpose-built database, pick an integration service.

Modernization is not “Lambda everywhere.” It is removing the constraint the current system pays for:

| They pay for | Modern move |
| --- | --- |
| Idle servers overnight | Lambda, Fargate, or scale-to-zero Aurora Serverless v2 for the database that is idle |
| A message table polled by cron | SQS or EventBridge |
| A nightly file dropped on a share | S3 event to EventBridge or Lambda, or Glue |
| A stored procedure orchestration | Step Functions |
| A relational table used only as a key lookup at extreme rate | DynamoDB |
| A relational database that is mostly read and still needs SQL | Aurora with readers, or ElastiCache in front |
| Long-lived WebSocket or HTTP APIs on EC2 | API Gateway or an ALB in front of Fargate |

Study the whole domain in `04-sap/04-domain-4-migration-modernization.md` and `02-services/15-migration-mgn-dms-datasync-snow-transfer.md`.

---

## In-scope service list (SAP-C02)

The guide says the list is non-exhaustive and can change. Every name below is on the guide fetched 11 October 2026. The catalog file says how deeply to learn each one.

**Analytics.** Athena, Data Exchange, Data Firehose, EMR, Glue, Kinesis Data Streams, Lake Formation, Managed Service for Apache Flink, MSK, OpenSearch Service, QuickSight.

**Application integration.** AppFlow, AppSync, EventBridge, MQ, SNS, SQS, Step Functions.

**Blockchain.** Amazon Managed Blockchain. Recognize it. Almost never the answer unless the stem says a managed blockchain network.

**Business applications.** SES. Transactional email at scale. Pinpoint is listed under frontend, not here.

**Cloud financial management.** Budgets, Cost and Usage Report, Cost Explorer, Savings Plans.

**Compute.** App Runner, AWS Auto Scaling, Batch, Elastic Beanstalk, EC2, EC2 Auto Scaling, Fargate, Lambda, Lightsail, Outposts, Wavelength.

**Containers.** ECR, ECS, ECS Anywhere, EKS, EKS Anywhere, EKS Distro.

**Database.** Aurora, Aurora Serverless, DocumentDB, DynamoDB, ElastiCache, Keyspaces, Neptune, RDS, Redshift, Timestream.

**Developer tools.** CodeArtifact, CodeBuild, CodeDeploy, CodeGuru, CodePipeline, X-Ray.

**End user computing.** AppStream 2.0, WorkSpaces. Recognize. A VDI stem. Not a web-app architecture answer.

**Frontend web and mobile.** Amplify, API Gateway, Device Farm, Pinpoint.

**IoT.** IoT Core, Device Defender, Device Management, IoT Events, Greengrass, SiteWise, Things Graph, IoT 1-Click. Things Graph and 1-Click are legacy names still printed on the guide. Recognize the current IoT family. Do not build a study week around 1-Click.

**Machine learning.** Comprehend, Fraud Detector, Kendra, Lex, Personalize, Polly, Rekognition, SageMaker AI, Textract, Transcribe, Translate. On SAP-C02 these are “which managed API matches the sentence.” Training-from-scratch details are thin. SAP-C03 adds Bedrock and AgentCore as first-class design.

**Media.** Elastic Transcoder, Kinesis Video Streams. Elastic Transcoder is the legacy transcoder. MediaConvert is the current product and may appear even if the guide still prints Elastic Transcoder. Know both names.

**Management and governance.** CloudFormation, CloudTrail, CloudWatch, CloudWatch Logs, AWS CLI, Compute Optimizer, Config, Control Tower, Health Dashboard, License Manager, Managed Grafana, Managed Service for Prometheus, Management Console, Organizations, Proton, Service Catalog, Service Quotas, Systems Manager, Trusted Advisor, Well-Architected Tool.

**Migration and transfer.** Application Discovery Service, Application Migration Service, DMS, DataSync, Migration Hub, SCT, Snow Family, Transfer Family.

**Networking and content delivery.** CloudFront, Direct Connect, ELB, Global Accelerator, PrivateLink, Route 53, Transit Gateway, VPC, VPN.

**Security, identity, and compliance.** Artifact, Audit Manager, ACM, CloudHSM, Cognito, Detective, Directory Service, Firewall Manager, GuardDuty, IAM Identity Center, IAM, Inspector, KMS, Macie, Network Firewall, RAM, Secrets Manager, Security Hub, STS, Shield, WAF.

**Storage.** AWS Backup, EBS, Elastic Disaster Recovery, EFS, FSx (all types), S3, S3 Glacier, Storage Gateway.

**Out of scope (explicit).** Game tech, Amazon GameLift. Other products can still be wrong answers.

## Technologies and concepts the guide lists

Compute, cost management, database, disaster recovery, high availability, management and governance, microservices and component decoupling, migration and data transfer, networking and content delivery, security, serverless design principles, storage.

## Score report

You get a pass/fail and a scaled score from 100 to 1000. The section table is informational. A weak domain can be carried by a strong one. Use it after a failed attempt to pick the domain file to reread. Do not chase a perfect section score at the expense of the 29% new-solutions domain.
