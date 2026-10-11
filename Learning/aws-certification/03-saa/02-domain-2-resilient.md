# SAA-C03 Domain 2 — Design resilient architectures (26%)

About 13 of the 50 scored items. The stem has a failure: an AZ, a Region, a slow dependency, a single instance, a process that is dead while the host is up. Name the failure first. Then pick the cheapest pattern that survives it. A second Region for an AZ failure is the wrong scope. Multi-AZ for a Region failure is the wrong scope.

Tasks 2.1 and 2.2. Service detail sits in the compute, messaging, database, and edge chapters. DR patterns are repeated, with the operational steps, in `04-sap/06-disaster-recovery-design.md` and `05-labs/lab-10-disaster-recovery-patterns.md`.

## Task 2.1 — Loose coupling and scaling

### Stateless, or you cannot scale

The app tier stores nothing that the next request needs, except in a store every instance can see. Session files on the instance disk, an in-memory cart, and a local upload directory all break the moment the load balancer sends the next request somewhere else.

| State | Where it goes | When the nearby option loses |
| --- | --- | --- |
| Session | DynamoDB or ElastiCache | Sticky sessions. They work and they pin a user to a dying instance. Use them only when the code cannot move |
| A file many instances must read and write as a filesystem | EFS, mount target in each AZ | S3, if they insisted on POSIX and will not change the code. S3, if they can change the code to GET and PUT |
| A large object | S3 | EBS, which is one AZ and one attachment story for a single writer |
| A shopping cart the user must not lose | DynamoDB | A Lambda global, which is one warm environment and not a database |
| Something you can recompute | A cache, with a TTL | A cache with no TTL, and a design that treats the cache as the only copy |

Horizontal scaling means more instances behind a load balancer. Vertical scaling means a bigger instance. Variable web traffic wants horizontal. A per-socket license that cannot run twice wants vertical, and you say the license is the constraint. Vertical scaling still dies when that one box dies.

### Decouple the slow or unreliable side

| What is breaking | Insert | Why the neighbor loses |
| --- | --- | --- |
| The API waits on a slow billing or email call and times out | SQS. The API writes the message and returns. A consumer does the slow work | A bigger API instance. The coupling is the bug |
| One event must reach several systems, and each system fails independently | SNS, with one SQS queue per subscriber. Or EventBridge, one rule and one target queue per consumer | One shared queue. The slow consumer blocks the others, or one poison message punishes everyone |
| You must react to an AWS API event, a SaaS event, or you want archive and replay | EventBridge | SNS, which is the fanout product and not the event bus with schema archive |
| A business process has steps, a wait, a retry, and a human approval | Step Functions. Standard for workflows that last longer than a few minutes and must be audited. Express for a high-rate, short workflow | A Lambda that calls the next Lambda in code. You lose the state when that process dies |
| The application already speaks JMS, AMQP, MQTT, or expects ActiveMQ or RabbitMQ | Amazon MQ | SQS. SQS is the right queue when you can change the client. It is the wrong answer when the protocol is the constraint |
| A schedule, and cron on one instance | EventBridge Scheduler, or an EventBridge rule on a schedule | A single EC2 crontab. That instance is the scheduler's availability |
| SaaS data into AWS with little code | AppFlow | A custom poller you will own forever |
| An HTTP API in front of Lambda | API Gateway. REST when you need API keys, usage plans, request validation, and the older feature set. HTTP APIs when the feature list fits and the price matters | An ALB, which is the right front door for instances and containers and a possible front door for Lambda, and the wrong "API product" when they asked for usage plans |

SQS standard is at-least-once and best-effort order. The consumer must be idempotent: a conditional write on the business key, so the second delivery does not create a second order. SQS FIFO gives ordering within a message group and exactly-once processing via a deduplication id, at a lower throughput ceiling. FIFO is the answer when the stem says order and duplicates matter and the rate fits. It is the wrong answer when they need the highest throughput and can tolerate a rewrite of the consumer to be idempotent.

A dead-letter queue is not a success path. It is where a message goes after `maxReceiveCount`. Something must alarm on the depth and something must repair or replay. A DLQ nobody reads is a bin.

Visibility timeout must be longer than the consumer's processing time. If the message becomes visible while the consumer is still working, a second consumer takes it. That is a duplicate you caused with a timeout, not with SQS's delivery model.

### Compute that survives a dead instance

| Signal | Choice |
| --- | --- |
| A request, under 15 minutes, scales to zero, no special OS | Lambda |
| A container that already exists, a long-running process | ECS on Fargate |
| The team requires the Kubernetes API | EKS |
| You must control the host, GPU, or a daemon | ECS or EKS on EC2, in an ASG across AZs |
| A web app, the team wants a platform, not a cluster | Elastic Beanstalk. Immutable or rolling with an extra batch, not "all at once" on the only environment |
| Hours of batch work, a queue of jobs | AWS Batch. Spot for the interruptible share |
| Spark or Hadoop | EMR. Do not answer Batch for a Spark cluster, or EMR for a bag of unrelated shell jobs |
| The first request after idle has a latency SLO | Provisioned concurrency for Lambda, or a warm minimum on the service |

Auto Scaling groups: minimum 2 for a tier that claimed high availability, subnets in at least two AZs, a launch template, and an ELB health check. An EC2 health check only notices that the hypervisor thinks the instance is up. A process that returns HTTP 500 stays in service. The health check path must prove the app, and it must not depend on a downstream you are willing to survive without. If the health check calls the database and the database blips, the ASG replaces every instance. That is a good database health check on a readiness gate only when you understand you will drain the fleet.

Scale on the bottleneck. Web tier: `ALBRequestCountPerTarget` or CPU if the app is actually CPU bound. Queue consumers: `ApproximateNumberOfMessagesVisible`, not the CPU of an idle poller. Target tracking is the default policy. Step policies when you know the increments. Scheduled scaling when the spike is the Monday morning you can see on a calendar. Predictive scaling is the extra, not the first answer.

A launch template plus an instance refresh replaces the fleet from a new AMI. That is immutable infrastructure. SSH and `yum update` on one box is how the fleet drifts and how the next scale-out launches the old bug. Systems Manager Patch Manager is the managed patch path when you are not replacing the AMI the same day. CloudFormation is the IaC answer on this exam. CDK is out of scope for SAA. Do not pick CDK when CloudFormation is an option.

### Data tier, said precisely

| Feature | What it does | What it does not do |
| --- | --- | --- |
| RDS Multi-AZ | Synchronous standby in another AZ. Automatic failover. The endpoint stays the same | It is not a second read endpoint on the classic instance deployment. It does not survive a Region failure |
| Aurora | Storage is replicated across three AZs already. A reader is a compute endpoint you can fail over to and you can read from | One writer instance with no reader still has the storage durability. Failover is faster when a reader already exists |
| Read replica | Asynchronous. You can read from it. It can be in another Region. You promote it yourself | It does not fail over by itself. Replication lag means the replica is not a synchronous copy |
| Aurora Global Database | One writer Region, readers in other Regions, typical lag under a second. You fail over the writer | It is not multi-master by default. Write forwarding exists and has limits. Do not describe it as DynamoDB global tables |
| DynamoDB | Multi-AZ inside the Region as part of the service. Global tables when another Region must accept writes | There is no "turn on Multi-AZ" checkbox. The exam mistake is adding an AZ design to a service that already has it, or forgetting global tables when the stem says a second Region |
| S3 Standard | Designed for the loss of an AZ | One Zone-IA and S3 Express One Zone are not |
| EBS | One AZ. Snapshots are stored in S3 and can rebuild a volume in another AZ | A volume is not a Multi-AZ disk. io2 Block Express is still one AZ |
| ElastiCache | A cache. Multi-AZ replication for Redis or Valkey keeps a standby | If the cache is required for correctness, it is not a cache. The database must be able to serve, slower |

RDS Proxy belongs in this domain when the failure is a connection storm or a failover that drops thousands of Lambda connections. The proxy holds the pool and can make failover less visible to the app. It is not a performance tuner for a single EC2 app with ten connections. It costs money. Domain 4 will take it back off if you added it for decoration.

DMS and read replicas are not the HA design for a database you already run on RDS. They are migration and read-scale tools. Multi-AZ is the HA checkbox.

## Task 2.2 — Availability, fault tolerance, and disaster recovery

### RTO and RPO

RTO is how long you may be down. RPO is how much data you may lose. Get both numbers from the stem before you look at products. "Highly available" is not a number. If they did not give a number, the smallest scope that removes the single point of failure they named is the answer.

| Pattern | What is already running in the other Region | RTO shape | Data |
| --- | --- | --- | --- |
| Backup and restore | Nothing but backups | Hours. You build the stack, then restore | AWS Backup, snapshots, S3 replication or a copied snapshot. You lose everything after the last good backup |
| Pilot light | The data is live. Compute is small or off | Tens of minutes. You scale the compute and switch routing | Continuous replication. Aurora Global or a cross-Region replica or DRS for servers |
| Warm standby | A scaled-down full stack is already up | Minutes. You scale up and switch routing | Replication, and the small stack is something you patch and pay for every day |
| Active-active | Both Regions serve users | Near zero for an AZ or a single Region, if the other Region can take the load | Writes in both places: DynamoDB global tables, or a write strategy you can defend on Aurora. Conflict handling is your problem |

Route 53 failover records plus a health check are the active-passive DNS switch. Latency or weighted records are the active-active user routing. A low TTL is part of the DNS story and is useless if the client or a resolver caches longer, and it is useless if you needed the switch in seconds and should have used Global Accelerator or ARC. At Associate level, health checks plus failover records are the answer. Application Recovery Controller is the Professional tool for a gray failure, where the health check stays green and the site is broken. If ARC is in the options and the stem says the Region looks healthy and is not, ARC is the answer even on an Associate-style question.

Elastic Disaster Recovery continuously replicates servers at the block level and can drill a failover. It is the lift-and-shift RTO tool when they will not refactor. AWS Backup is the cross-service backup plan and the backup-and-restore pattern. Multi-AZ is neither of those. Do not answer "turn on Multi-AZ" when the stem said the Region is unavailable.

### Single points of failure that are automatic wrong answers

- One subnet, or an ASG that lists one subnet.
- One NAT Gateway for a design that claimed the private tier survives an AZ failure.
- A database that is not Multi-AZ, in a design that claimed the application is Multi-AZ.
- An EBS volume that holds the only copy of the data.
- EC2 health checks while the process is the thing that dies.
- A queue consumer that is one instance with no ASG.
- Cron on one instance.
- A Route 53 record with a health check that checks the wrong thing, or a failover record with no health check at all.
- A standby Region where you never raised service quotas. The failover fails with a limit, not with a missing AMI. Request the quota before the test.
- S3 Cross-Region Replication as the database DR story. CRR copies objects. It does not copy RDS.

### Legacy code you cannot change

Put an ALB in front and an ASG around the process if it can run as more than one copy. Move sessions out if you can. If it cannot run twice, say so: you can still Multi-AZ the database and keep a single compute node with a fast rebuild from an AMI, and you do not promise scale-out. RDS Proxy if the failure mode is connection count. X-Ray if the failure mode is "we cannot see which tier is slow." X-Ray is in scope on SAA. You select it. You do not write the SDK on this exam. FIS is out of scope on the SAA guide. A "run a failure drill" stem on SAA is answered with a game day, a backup restore test, or a Multi-AZ failover test, not with the FIS product, unless the options only make sense that way and you are actually sitting SAP.

### Quotas are a resilience control

A warm standby that has never been scaled to production size will fail the day you need it, on Lambda concurrency, on VPC count, on EIP count, or on a Regional service limit. The exam phrase is "request a quota increase in the standby Region before the failover test." Trusted Advisor and Service Quotas are where you see the limit. Raising every limit in production without a reason is a Domain 4 failure. Raising the ones the failover needs is a Domain 2 requirement.

### What fails over by itself

| Failure | Moves without you | Does not |
| --- | --- | --- |
| An AZ, RDS Multi-AZ | The database endpoint, to the standby | A read replica. You promote that |
| An AZ, Aurora with a reader | Failover to a reader, faster when the reader exists | A cross-Region Aurora secondary, until you fail over the global database |
| An AZ, ALB plus ASG across subnets | New tasks or instances in the healthy subnet, if capacity and the AMI exist | An instance that was not in an ASG |
| An AZ, S3 Standard, DynamoDB, SQS, the managed control planes | Already designed for it. There is no checkbox | EBS, instance store, a single NAT, a single-AZ RDS |
| A Region | Nothing, unless you built one of the four patterns and a routing change | Multi-AZ |

## Routing and front doors, only the resilience cut

ALB across two subnets is the minimum. One subnet means one AZ. NLB when you need a static IP or a protocol that is not HTTP, and you still put it in two subnets. Route 53 health checks should hit an endpoint that proves the application. A TCP check on port 80 stays green while the app returns 500.

Global Accelerator gives you two static anycast IPs and shifts traffic off an unhealthy Regional endpoint in seconds. Use it when DNS TTL is too slow or the protocol is UDP. CloudFront origin failover is the HTTP cache's version of a second origin. It is not the same product.

## Worked scenarios

**1.** RTO 4 hours, RPO 1 hour, lowest cost. The application runs in one Region today. Automated backups with a retention that meets the RPO, a cross-Region copy of those backups, and a written restore you have timed. Pilot light replicates data all day and costs more than this RTO requires. Warm standby costs more again. Active-active is the availability design and the wrong cost design.

**2.** RPO of about a second, RTO of about a minute, PostgreSQL, one writer. Aurora Global Database. A cross-Region RDS read replica that you promote by hand loses if the RTO is shorter than the promote-and-repoint work. DynamoDB global tables are the answer only when they can leave SQL. Multi-AZ is the answer only when the failure in the stem is an AZ, not a Region.

**3.** Checkout calls inventory over HTTP and the sale times out when inventory is slow. Put SQS between them. Checkout records the order as accepted for processing and returns. Inventory consumes the queue. Do not scale the inventory EC2 as the first answer. Do not make checkout wait on a bigger timeout. The coupling is the bug. The order write has to be idempotent because the queue will deliver twice.

**4.** The architecture diagram shows S3 CRR and RDS Multi-AZ, and the stem asks what survives a Region failure. The bucket's replica survives. The database does not. Add a cross-Region replica, Aurora Global, or a backup copy in the other Region, plus a way to bring the compute up. CRR also has a replication lag and does not by itself replicate existing objects unless you configured that.

**5.** One NAT Gateway. The private fleet is Multi-AZ. When the NAT's AZ dies, the other AZ's private instances lose their default route. One NAT per AZ, and gateway endpoints so S3 and DynamoDB never needed the NAT.

**6.** The ASG is healthy in two AZs. Users still see errors. The target group uses a TCP check. Switch the check to HTTP and a path that returns 200 only when the app can do its job. Also look at the database: if it is single-AZ, the ASG never had a chance.

**7.** Sessions are in memory. Scale-out made users log in again, and a deploy logs everyone out. Move sessions to ElastiCache or DynamoDB. Sticky sessions are the compromise if the vendor will not ship a new build. Say the compromise out loud so you do not pick it when the code can change.

**8.** A nightly job runs as cron on the only admin instance. EventBridge Scheduler invokes a Lambda or sends a message to a queue. The admin instance can die without taking the calendar with it.

**9.** They want to test that backups restore, and they have never restored one. An AWS Backup restore test, or a documented restore onto a throwaway instance, on a schedule. Owning a backup plan you have never restored fails the resilience stem even though the backup job is green.

**10.** Two Regions, DynamoDB global tables, an ALB in each, Route 53 latency routing. That is active-active. The item they still have to design is conflict: both Regions can write the same key. If the stem cannot accept that, they do not want global tables. They want one writer.

## Commands

```bash
aws autoscaling create-auto-scaling-group \
  --auto-scaling-group-name app \
  --min-size 2 --max-size 6 \
  --vpc-zone-identifier "$SUBNET_A,$SUBNET_B" \
  --health-check-type ELB --health-check-grace-period 120 \
  --launch-template LaunchTemplateName=app,Version='$Latest'

aws autoscaling put-scaling-policy \
  --auto-scaling-group-name app \
  --policy-name track-requests \
  --policy-type TargetTrackingScaling \
  --target-tracking-configuration file://track.json

aws rds create-db-instance \
  --db-instance-identifier app \
  --engine postgres \
  --db-instance-class db.m7g.large \
  --allocated-storage 100 \
  --multi-az \
  --backup-retention-period 7 \
  --manage-master-user-password

aws rds create-db-instance-read-replica \
  --db-instance-identifier app-dr \
  --source-db-instance-identifier app \
  --region us-west-2

aws sqs create-queue --queue-name orders \
  --attributes VisibilityTimeout=60,RedrivePolicy=file://redrive.json

aws events put-rule --name nightly --schedule-expression "cron(0 2 * * ? *)"
aws backup create-backup-plan --backup-plan file://plan.json
aws route53 change-resource-record-sets --hosted-zone-id "$ZONE" --change-batch file://failover.json
```

A failover change batch has two records with the same name. The primary has `Failover: PRIMARY` and a health check id. The secondary has `Failover: SECONDARY`. A weighted pair with no health check does not move when the origin dies.

## Exercise set

1. An ASG spans two AZs. RDS is a single-AZ instance. Is the architecture highly available? What do you turn on?
2. A read replica in another Region and a Route 53 failover record. What step is still yours when the Regional database fails?
3. Standard SQS delivers an order message twice. What must the consumer do, and when does it delete the message?
4. Pilot light versus warm standby, one sentence each, for a system whose data is already on Aurora Global Database.
5. The ALB health check is TCP on port 80. The process accepts the connection and returns HTTP 500. Will it be removed? What do you change?
6. FIFO or standard SQS: 50,000 unrelated orders a second, duplicates are acceptable if the write is conditional, order across orders does not matter.
7. Why is one Internet Gateway not a single point of failure, while one NAT Gateway is?
8. The only copy of a reporting database's files is an EBS volume. What failure does a snapshot protect you from, and what failure does it not?
9. Lambda in two AZs behind an ALB, and a DynamoDB table. Which of those three do you "enable Multi-AZ" on?
10. RTO 15 minutes, RPO near zero, they will not change the monolithic servers this year. Which product replicates the servers, and which DR pattern is that closest to?
11. Sticky sessions are enabled. One instance is sick and the user is pinned to it. What does the user experience, and what design removes the pin?
12. A backup job has been successful for a year. Nobody has restored it. What resilience claim can you not make?
13. EventBridge or SNS or SQS: a file landing in S3 must start two independent processors, each with its own retry buffer.
14. A step function must wait three days for a supplier and then continue, and you must see which step failed last Tuesday. Standard or Express?
15. The standby Region has a Lambda concurrency quota of 10. Production uses 500. When does this hurt, and what do you do before the drill?

## Answers

1. No. The database AZ is a single point of failure. Enable Multi-AZ, or move to Aurora, whose storage is already across three AZs, and add a reader if you want a warm failover target.
2. You promote the replica. It does not promote itself. Route 53 can only send users to whatever endpoint you have already made the primary and marked healthy. Update the record if the promoted endpoint's address changed and the health check was not already aimed at it.
3. The write is idempotent. A condition that the order id does not already exist, and a successful "it already exists" is treated as success. Delete the message after the commit. Deleting first loses the order if the write then fails.
4. Pilot light keeps the Aurora secondary and little or no application compute. Warm standby keeps a scaled-down application fleet already deployed in the second Region, so the RTO is a scale-up plus a routing change rather than a deploy.
5. No. TCP is satisfied by the accept. Change the target group to an HTTP check that expects 200 on a path the application owns.
6. Standard. FIFO's throughput and ordering are not the requirement. The conditional write covers the duplicate.
7. The Internet Gateway is a VPC component AWS scales and keeps available across AZs. The NAT Gateway is a zonal resource you placed in one subnet. Its failure removes the default route for every subnet that points at it.
8. A snapshot lets you create a volume in another AZ after this AZ's volume is gone, back to the time of the snapshot. It does not keep the application up during the failure, and it does not protect writes after the snapshot. It is also not a second Region unless you copied the snapshot.
9. None of them, as a checkbox. ALB subnets must be in two AZs, which is your configuration. Lambda runs in multiple AZs unless you attached it to one subnet. DynamoDB already spreads across AZs. The exam wants you to stop "enabling Multi-AZ" on services that do not have that knob, and to fix the ones that do, which are RDS and the AZ placement of NAT, EBS, and subnets.
10. Elastic Disaster Recovery. That is closest to pilot light: the data is continuously at the recovery site and the compute is brought up for a drill or a failover, rather than a full warm stack you run all day.
11. The user stays on the sick instance until the stickiness cookie expires or the instance is removed by a real health check. Move the session to a shared store and turn sticky sessions off.
12. You cannot claim the RTO. You have not timed a restore. A successful backup job is not a successful restore.
13. S3 can notify EventBridge, and two rules can each target a queue. Or S3 notifies SNS, and SNS fans out to two SQS queues. One queue with two consumers competing is the wrong picture, because each message is processed by one consumer. Fanout means each processor gets its own copy.
14. Standard. Express is short and not the audit history you look at next week. A three-day wait is a Standard workflow.
15. It hurts the day you fail over and the standby cannot run the production concurrency. Request the quota increase in the standby Region before the drill, and scale a test that proves it.
