# SAP Domain 3 — Continuous improvement (25%)

The system is already running. Do not redesign it from zero unless the current design cannot meet the constraint. Name the change with the highest leverage.

## 3.1 Operational excellence

| What they do now | What you change |
| --- | --- |
| SSH to patch | Session Manager and Patch Manager. Remove port 22 |
| A human runs the same commands on every alarm | EventBridge or a CloudWatch alarm action to Systems Manager Automation |
| Friday deploy script | Pipeline, test stage, rollback on alarm |
| DR never tested | Backup restore testing, a DRS drill, or a Fault Injection Service experiment |
| Logs on the instance disk | CloudWatch agent, retention, a metric filter |
| Ten accounts, ten dashboards | Cross-account CloudWatch observability, or logs in the log-archive account |

Deployment on a live fleet: rolling with an extra batch when you cannot dip capacity, blue/green when you need an instant rollback, canary when you need production evidence. All-at-once is dev.

## 3.2 Security improvement

| Finding | Change |
| --- | --- |
| Key in git | Role on the compute, or Secrets Manager for a third-party credential |
| `Action: *` | Access Analyzer policy generation, then a boundary for delegated admins |
| Public bucket | Block Public Access at the account. Macie if the concern is the data, not the ACL |
| Unencrypted EBS | Encryption by default, snapshot-copy to an encrypted volume |
| They want detective plus corrective | Config rule plus SSM Automation remediation |
| CVE | Inspector |
| Odd API behavior | GuardDuty |
| Auditor wants tamper-evident history | Organization trail, log file validation |
| Ransomware retention | Backup vault lock, or S3 Object Lock |

## 3.3 Performance improvement

Put a number on the complaint. Then read the metric for that tier.

| Metric | Tier |
| --- | --- |
| `TargetResponseTime` | ALB |
| `ReadLatency`, `DatabaseConnections` | RDS |
| Throttled requests | DynamoDB |
| `VolumeQueueLength` | EBS |
| `BytesOutToDestination` | NAT, often an unexpected S3 path |
| `Duration` and `InitDuration` | Lambda |
| Iterator age | Kinesis |

CloudFront does not speed up a write path that is waiting on a single-AZ database. Global Accelerator is the non-HTTP or fast-failover path. A Local Zone is the "the Region is too far" path.

## 3.4 Reliability improvement

Single points of failure that hide in a diagram that looks fine:

- One NAT gateway.
- RDS without Multi-AZ.
- An ASG of one, or a health check that is only EC2.
- A consumer that deletes the SQS message before the commit.
- A Regional quota never raised in the standby Region.
- A DNS TTL of a day on a record they need to fail over.
- The only copy of the data on instance store.

## 3.5 Cost on a running system

Idle load balancers, unattached EIPs, unattached EBS, old snapshots, NAT in front of S3, gp2 sized for IOPS, On-Demand steady state, cross-AZ chatter, Standard storage for cold objects, log retention set to never, a second hot Region whose RTO did not require it.

CUR at line-item level is how you prove it. Tagging is how you assign it. Compute Optimizer is how you rightsize it.

## Scenario method

1. Quote the constraint that is currently missed.
2. Name the smallest change that meets it.
3. Reject the option that rebuilds the platform.

A team on Beanstalk with slow deploys does not need EKS. They need an immutable or blue/green policy and a health check. A team with a hot NAT bill does not need Direct Connect first. They need a gateway endpoint.

## Operational excellence, the changes that are actually small

Session Manager needs three things or it "does not work" and someone reopens port 22: the instance role, a path to the SSM endpoints (NAT or interface endpoints), and the agent, which is on current Amazon Linux and Windows AMIs. Patch Manager uses maintenance windows so you do not patch the whole fleet at 09:00. A golden AMI pipeline is the other patch path. Both beat SSH. State Manager keeps the agent and a baseline configuration present. If someone can still SSH, the security group is unfinished.

Runbooks belong in Systems Manager Automation documents. An alarm or an EventBridge rule invokes the document. The document assumes a role that can do the one repair, not admin. A human approval step belongs in the document when the repair restarts production. ChatOps that pastes the same CLI into a channel is not the improvement.

Observability has a join key. The ALB access log, the application log, and the X-Ray trace need the request id. Without it you have three tools and no incident. Logs Insights is how you search. A metric filter or EMF is how a log line becomes an alarm. X-Ray is how you see which downstream took the time. CloudTrail is who called the API. Contributor Insights and Container Insights are the "which shard or which task" tools. Do not answer "turn on X-Ray" for an IAM question, or "turn on CloudTrail" for a latency question.

Cross-account operations: CloudWatch cross-account observability, or a log destination in the log-archive account. Each account's local dashboard is how a Friday incident misses the account that is actually on fire. Health Dashboard and the Personal Health Dashboard tell you about AWS, as distinct from your app. A Support plan is the escalation path. It is not a monitoring design.

A deployment improvement on a live system keeps the current platform:

| They have | You change | You do not |
| --- | --- | --- |
| Beanstalk, slow and scary deploys | Immutable updates, a proper health check, a rollback | A migration to EKS in the same quarter |
| CodeDeploy all-at-once | Canary or blue/green plus an alarm | A new CI vendor |
| Lambda, users on `$LATEST` | Publish a version, an alias, a canary | A rewrite in containers "for reliability" |
| A bash script on a bastion | A pipeline in shared services, a deploy role, a change set | Giving the script AdministratorAccess and calling it automation |
| DR documentation and no test | A restore test, a DRS drill, or a FIS experiment with a stop condition | A second active Region they did not budget |

FIS is in scope for this domain on Professional and is called out again on SAP-C03. An experiment has a role, an action, a target, and a stop condition that is a CloudWatch alarm. No stop condition means you are breaking production on purpose with no brake. Run it in an account that can afford the blast. SAA lists FIS out of scope. Do not drag it into an Associate answer.

## Security improvement, mapped to the finding

Access Analyzer policy generation looks at CloudTrail and drafts a tighter identity policy. You still read it. A permissions boundary on delegated admins stops the next `Action: *` role. Account-level S3 Block Public Access stops the next public bucket even if a team attaches a public policy. Encryption by default on EBS stops the next unencrypted volume. Neither rewrites the old ones. Old volumes are snapshot, copy encrypted, swap. Old objects are copied onto themselves with the new encryption.

Config rules detect drift. A remediation action can call SSM Automation. That is detective plus corrective. It is slower than an SCP, and it is what you use when the control is "this bucket must have versioning" rather than "this API is forbidden." Some configurations cannot be remediated safely. Those stay as findings a human owns.

Detective is the investigation tool after GuardDuty or Security Hub has a finding: who assumed the role, what did they touch. It is not the detector. Macie is the detector for sensitive data in S3. Inspector is the detector for CVEs. GuardDuty is the detector for malicious behavior. Security Hub is the inbox. If the stem says findings are ignored, the improvement is the routing to a ticket system and an owner, not a fifth detector.

Ransomware retention is Backup vault lock or Object Lock in compliance mode, in an account the application role cannot administer. A backup in the same account, with the same admin, is what ransomware deletes first.

## Performance, read the metric they implied

They will describe a symptom. You name the metric and then the change.

| They say | You look at | The usual change |
| --- | --- | --- |
| The site is slow for users, the servers look idle | ALB `TargetResponseTime`, then the downstream | The app is waiting. A bigger instance does nothing if CPU is low. Find the database or the remote call |
| Checkout times out, CPU on the API is low | The dependency | SQS, or a timeout and a bulkhead so one dependency cannot hold every thread |
| RDS CPU is low, the app reports too many connections | `DatabaseConnections` | RDS Proxy, or a smaller Lambda concurrency |
| RDS CPU is high on SELECT | Readers, a cache, or a missing index | A bigger writer is the last move, not the first, when the reads can go elsewhere |
| DynamoDB throttles, table capacity looks spare | The hot key, in Contributor Insights | Change the key. Raising the table mode does not fix one partition |
| Disk queue on the database volume | `VolumeQueueLength`, IOPS | gp3 or io2 with the IOPS set. A bigger instance if the limit is the instance's EBS bandwidth |
| NAT bytes are enormous and the app is "just storing files" | `BytesOutToDestination` | Gateway endpoint. The files were going through the NAT |
| Lambda is slow only on the first request | `InitDuration` | Provisioned concurrency, a smaller package, SnapStart for a supported Java runtime |
| Lambda is slow on every request | `Duration` versus memory | Raise memory until duration stops falling |
| A stream consumer falls behind | Iterator age | More shards, more consumers, or a poison-record policy. Not a bigger shard-consumer instance that still processes one record at a time and then dies on the poison |
| Users far away, static content | Origin bytes versus edge bytes | CloudFront. Accelerator if the content is not cacheable |

A Local Zone or an Outpost is the improvement when the number cannot be met from the Region and they have a city or a building that qualifies. It is not the answer to a slow SQL query.

## Reliability improvements that are still small

One NAT. Add a NAT per AZ or remove the need with endpoints. RDS without Multi-AZ. Turn it on, in a maintenance window, and know it is not a Region strategy. An ASG of one. Raise the minimum and add a subnet. An EC2 health check. Switch it to ELB. A consumer that deletes the SQS message and then writes the database. Reverse the order and make the write idempotent. A DNS TTL of a day. Lower it before the incident, not during it. The only copy on instance store. Put it on EBS or S3 and snapshot it. A standby Region whose quotas were never raised. Open a quota request and run a scale test.

A cache with no TTL and no miss path becomes a reliability incident wearing a performance costume. The improvement is the miss path and the TTL, not a second cache.

## Cost on a system you are not allowed to rebuild

Idle load balancers, unattached Elastic IPs, unattached EBS volumes, snapshots of deleted test instances, NAT in front of S3, gp2 sized to rent IOPS, steady On-Demand, cross-AZ chatter that a placement change would remove, Standard storage for objects nobody reads, log retention set to never, interface endpoints in three AZs for an API called once a day, a second hot Region whose RTO was 48 hours.

Prove it with the CUR at line-item granularity. Assign it with activated tags. Rightsize it with Compute Optimizer after the agent or the metrics exist. S3 Storage Lens for the buckets. Trusted Advisor for the idle network objects. Then change one thing and show the next month. A recommendation you did not apply is not an improvement.

The reject list for this domain is "migrate to microservices," "adopt multi-Region active-active," and "replace RDS with DynamoDB" unless the current design cannot meet the constraint. Most stems can be met with an endpoint, a health check, a lifecycle rule, a Savings Plan, or a Multi-AZ flag.

## Worked improvements

**1.** Deploys SSH into instances and `git pull`. The fleet drifts. A pipeline builds an AMI or a container, an ASG instance refresh or a CodeDeploy deployment group rolls it, the old version stays available for rollback, port 22 closes. The application code can stay a monolith.

**2.** GuardDuty findings exist. Nobody sees them for a week. EventBridge rule on the finding, to SNS or to the ticketing endpoint, with a severity filter so the queue is not noise. Security Hub custom insights if they need one view across accounts. Another detector does not fix an unread queue.

**3.** The NAT bill passed the EC2 bill. VPC flow logs or the NAT metric show S3 prefixes. Add the gateway endpoint. Do not buy Direct Connect to make S3 cheaper.

**4.** Users in one country see multi-second loads of the same images. CloudFront, a cache policy, origin in the existing Region. A full stack in a new Region is the improvement you propose only after the cache is in and the stem is about dynamic, non-cacheable, Regional failure.

**5.** Backups are green. A restore has never been timed. Turn on restore testing or put a quarterly drill on the calendar and write down the actual RTO. The improvement is the evidence, not another backup vault in the same account.
