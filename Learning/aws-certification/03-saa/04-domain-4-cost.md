# SAA-C03 Domain 4 — Design cost-optimized architectures (20%)

About 10 of the 50 scored items. The correct design is the cheapest one that still meets every availability, durability, performance, and security sentence in the stem. A Spot instance as the only database fails even though it is the cheapest line. A second Region for a 48-hour RTO fails even though it is the most available line. Read the other constraints first. Then spend as little as possible.

Tasks 4.1 through 4.4. The tools that show the bill do not reduce the bill. Cost Explorer, the Cost and Usage Report, Budgets, and tags explain it. Compute Optimizer and Trusted Advisor name waste. You still have to change the architecture. A budget alert does not stop a launch.

Official purchasing rules move. Before the exam, re-read the Savings Plans and S3 storage class pages if a discount percentage shows up in a blog. This file teaches the choice, not a percentage.

## Task 4.1 — Storage

### S3 classes

| Class | You pay it for | You refuse it when |
| --- | --- | --- |
| Standard | Hot objects, frequent reads, Multi-AZ durability | The object is unread for months |
| Intelligent-Tiering | Unknown or changing access. A small monitoring fee per object | The objects are tiny and the monitoring fee dominates, or you already know they become cold on a date |
| Standard-IA | Infrequent, milliseconds when you do read, a retrieval fee, 30-day minimum | The object is read daily, or it will be deleted in a week. The minimum duration still bills |
| One Zone-IA | The same idea, one AZ, cheaper | It is the only copy. An AZ failure is allowed to destroy it only if you can recreate it |
| Glacier Instant Retrieval | Rare reads, milliseconds when you read | They said hours is fine. Then you are overpaying relative to Flexible Retrieval or Deep Archive |
| Glacier Flexible Retrieval | Minutes to hours | They said milliseconds, or they retrieve it every day |
| Glacier Deep Archive | The cheapest, hours to restore, 180-day minimum, long retention | They will read it next week, or they need it in minutes during an incident |
| Express One Zone | Very high request rates in one AZ | Anyone who said "save money." It is a performance purchase |

Lifecycle rules move objects between classes and expire them. They do not shrink an EBS volume. A transition to Standard-IA before 30 days is rejected or wastes the minimum-duration charge. Abort incomplete multipart uploads. Those parts are the quiet bill. Expire noncurrent versions if versioning is on and the older copies have no retention requirement. Do not expire an object Object Lock still holds. The lock wins, and that is correct, and it is also why you do not practice compliance mode in a lab account.

"We do not know the access pattern" is Intelligent-Tiering. "We know it is untouched after 90 days and a 12-hour restore is acceptable" is a lifecycle to Deep Archive. Guessing Deep Archive for unknown access creates retrieval bills and an outage the day someone opens the file.

Requester Pays is rare. It is the answer when other accounts download a dataset you host and they should pay the transfer. It is not the answer for your own application's bucket.

S3 Storage Lens shows you which buckets are cold, unencrypted, or full of incomplete uploads. It does not move the objects. The lifecycle does.

### EBS, EFS, FSx

gp2 makes you grow the volume to buy IOPS. gp3 sets IOPS and throughput on a smaller disk. That is the block-storage cost move. io2 is justified by an IOPS and durability number, not by habit.

Unattached EBS volumes and old snapshots are waste. Data Lifecycle Manager or an AWS Backup retention policy deletes them on a schedule. A snapshot you might need for the RPO stays. A snapshot from a deleted test instance does not.

EFS has an Infrequent Access storage class and a lifecycle. Use it when the filesystem is real. If the application can store objects, S3 is usually cheaper than a file system you keep mounted and hot. FSx for Windows on SSD, sized for peak, is expensive when the working set is small and the rest is cold. HDD is the cost tier when the performance number allows it.

One Zone classes and instance store are cost wins only for data you can recreate. The only copy of a customer upload belongs in Standard or in a Multi-AZ class.

### Getting data in

DataSync is the online copy. Snow Family is the ship-a-device copy when the link cannot finish in time. The classroom rule: if the transfer on the available bandwidth takes more than about a week, price Snow. Transfer Acceleration speeds an upload over a long internet path. It costs more per GB than a normal upload. It is the performance answer, and it is the cost answer only when the alternative is a failed upload or a circuit you do not need. Direct Connect can be cheaper per GB at steady high volume and is a commitment and a circuit. It is not cheaper than VPN or the internet at small volume.

## Task 4.2 — Compute

### What you buy

| Option | You commit to | It covers | It stops matching when |
| --- | --- | --- | --- |
| On-Demand | Nothing | Anything, at the highest rate | The workload is steady and large enough that a commitment would pay |
| Compute Savings Plan | A dollar-per-hour amount, usually 1 or 3 years | EC2, Fargate, Lambda, across families, sizes, and Regions in the way the plan states | You expected it to discount RDS, ElastiCache, Redshift, or OpenSearch. Those have their own reservations |
| EC2 Instance Savings Plan | Cheaper than Compute, locked to a family in a Region | That family | You move from `m5` to `m7g` or to a different family |
| Standard Reserved Instance | The deepest RI discount, the least flexible | The attributes you bought: family, size with some normalization, Region or AZ | You change family, or you change Region on a zonal RI |
| Convertible Reserved Instance | A smaller discount, you can exchange | A changing instance family, if you do the exchange | You wanted it to be automatic like a Compute Savings Plan |
| Spot | Nothing. You can lose the instance with a short warning | Stateless workers, Batch, the interruptible half of an ASG | The only database, the only queue consumer, anything that cannot be stopped |
| Dedicated Host | A host, because a license is per socket or per core, or a compliance rule names a host | That license conversation | You only wanted "cheaper." It is not cheaper. A dedicated instance is the weaker isolation option and is rarely the answer |
| Hibernation | Nothing financial. You stop the instance and keep RAM | A workstation-style instance that supports hibernation | You needed high availability. A stopped instance is down |

Non-production does not inherit production's Multi-AZ, its instance size, or its reservation. Stop dev databases at night. Use a smaller class. Single-AZ is acceptable when the stem says developers can wait, or when it says nothing about dev availability. Production that named an AZ failure still gets Multi-AZ. The cost domain does not repeal the resilience sentence.

Spot as a fraction of an ASG, with On-Demand or a Savings Plan as the base, is the usual production compute discount. Spot as 100 percent of the only tier is the outage.

Outposts is the answer when the workload must stay in a facility and the latency to the Region is too high, or the data must stay there. It is not the cheap answer. Wavelength is the 5G edge answer. Lightsail is out of scope on the SAA guide. Do not pick it for an enterprise HA stem. It is in scope on SAP as a simple VPS and still loses those stems.

Lambda and Fargate are the utilization tools. You stop paying for idle when the work is spiky and short. They lose when the workload is steady and a Savings Plan on EC2 is cheaper, or when the runtime does not fit. A 24/7 Lambda at high concurrency can cost more than a small reserved fleet. Do the arithmetic the stem implies. If they say "idle most of the day," serverless wins. If they say "flat and high," a commitment wins.

Scheduled scaling, or Instance Scheduler, turns off the fleet that is idle nights and weekends. Hibernation is only when the memory state matters and the instance type supports it. Terminating and rebuilding from a launch template is cheaper than hibernating a fleet that had no state.

### The bill you can see

Activate cost allocation tags in the billing console. A tag on a resource that was never activated does not appear as a cost dimension. The CUR belongs in an account finance can read, often a log or billing account, not only in the payer's console screenshots. Budgets per account or per OU tell you when a team crossed a line. They do not close the account.

Compute Optimizer recommends a smaller instance after it has seen the metrics. Trusted Advisor flags idle load balancers, unattached addresses, and underused volumes. Neither one deletes the resource.

## Task 4.3 — Databases

- A quiet dev RDS instance: stop it on a schedule, or use a smaller class, or use Aurora Serverless v2 if the load is real but uneven. Do not buy Multi-AZ `db.r6i.4xlarge` for a demo.
- Read-heavy production SQL: a reader or a cache before a bigger writer, when the reads allow it.
- DynamoDB on-demand for spiky and new. Provisioned, with auto scaling, when the traffic is flat and high enough that on-demand costs more. A table that is idle in on-demand still costs nothing for capacity, which is why on-demand wins the unknown and the tiny.
- DynamoDB TTL deletes expired items so you stop paying to store them. It is not immediate. It is the cost control, not a compliance deletion you must guarantee at a precise second. Application code or a lifecycle on the object store is the precise deletion.
- Infrequent-access table classes when the table is large and cold.
- Backup retention that is longer than the policy is a bill. Match it. Copy snapshots only to Regions you will restore in.
- RDS Proxy costs money every hour. Buy it for connection storms and for failover behavior. Do not add it because the diagram looked incomplete.
- Aurora Serverless v2 costs more per ACU than a well-sized provisioned instance that is busy all day, and less than a large provisioned instance that sits idle. The stem's load shape picks.
- A cache you never invalidate, sized like the database, is a second database bill. Cache the hot keys. Give it a TTL.

MySQL versus PostgreSQL, when either would work, is the engine the team already runs. Do not migrate for taste. Migrate when a feature, a license, or a managed-service limit forces it. Oracle and SQL Server on RDS carry license cost. The exam's cost answer is often "move to a PostgreSQL-compatible Aurora if the features fit," and only when the stem allows the change. A license-included instance versus bring-your-own-license is the other Oracle and SQL Server knob. Dedicated Hosts show up when the license is tied to sockets and they already own it.

## Task 4.4 — Network

| Path | What it costs | What you do |
| --- | --- | --- |
| S3 or DynamoDB through a NAT Gateway | NAT hourly plus data processing | A gateway endpoint. No hourly charge. The route is a prefix list |
| Cross-AZ traffic | Per GB in each direction for a lot of instance-to-instance and some load balancer traffic | Keep a chatty client next to its data when the design allows. Do not collapse a Multi-AZ design to save this charge if the stem required AZ survival |
| Cross-Region replication | Inter-Region transfer, both ways over time | Replicate only if the RPO needs it. A 24-hour RTO can copy backups. It does not need Aurora Global |
| Users far away pulling bytes from EC2 | Internet egress at the EC2 rate, and a fleet you sized for the bytes | CloudFront for cacheable HTTP. The edge price is often lower, and the origin stops serving the same object |
| NAT Gateway per AZ | Two or three hourly charges | Required if the private tier must keep outbound internet during an AZ failure. One NAT is the cost answer if the stem accepts losing outbound when that AZ dies. Gateway endpoints shrink what the NAT is for |
| Many VPC peering connections | No attachment hourly fee, and no transitive routing, so the mesh grows as N squared | Transit Gateway when the operational cost of the mesh is the problem. Peering stays cheaper at two VPCs with a few GB a month |
| Idle public IPv4, idle NAT, idle ALB, idle interface endpoints | Hourly | Delete them. Public IPv4 has had a charge for a while. An ALB replaces a public IP per instance |
| Interface VPC endpoints | Hourly per AZ plus data | Worth it when NAT data processing or the security requirement ("no internet") is larger. Not worth a dedicated endpoint for a once-a-day call that can use a NAT you already pay for |
| Direct Connect | Port hours and transfer, plus the circuit from the partner | Steady high volume or a latency requirement. VPN is the cheap encrypted connectivity. The public internet plus TLS is cheaper than both when a private circuit is not a requirement |
| VPN | Hourly per connection plus the internet transfer | The right default for hybrid until the volume or the stability requires a circuit |

One shared NAT is cheaper and is a single point of failure. NAT per AZ is the resilient answer. The stem picks. If it says cheapest and also says the private tier must survive an AZ failure, the per-AZ NAT stays. If it says cheapest and the private tier can lose outbound during an AZ failure, one NAT is the cost answer. If S3 is most of the bytes, the gateway endpoint is the answer either way, and the NAT decision gets smaller.

Throttling is a cost and a protection tool. API Gateway usage plans, WAF rate-based rules, and SQS as a buffer stop one client from scaling you into a bill. Raising every quota is the performance answer.

CloudFront in front of S3 for a static site reduces origin GETs. It is not free. It wins when the bytes are cacheable and the users are not all sitting in the origin Region. It also gives you WAF and TLS at the edge, which may be why you buy it even when the cost difference is small.

## Worked scenarios

**1.** Steady EC2 all year, some unpredictable Lambda, some Fargate. They want one commitment. Compute Savings Plan. An EC2 Instance Savings Plan misses the Lambda and the Fargate, and it locks the family. A Standard RI on the current instance misses both and locks the size.

**2.** Objects retained seven years, retrieved twice, a 12-hour restore is acceptable. Glacier Deep Archive. Glacier Instant Retrieval is the answer if they said milliseconds. Intelligent-Tiering is the answer if they said they might start reading them every day and do not know.

**3.** The NAT bill is large. The diagram has no VPC endpoints. The workload reads and writes S3 and DynamoDB. Gateway endpoints for both. Keep a NAT only for the residual public internet.

**4.** A second full Region is proposed for an internal tool with an RTO of 48 hours. Backup and restore. Warm standby is the resilient design they did not ask to pay for. Multi-AZ still belongs in the primary Region if an AZ failure is in scope. The second Region is the part that is too expensive for this RTO.

**5.** A team bought a Standard Reserved Instance for `m5.xlarge` in one AZ and moved the fleet to `m7g.large`. The discount stopped matching because the family changed. A Compute Savings Plan would have followed the move across families and also covered Fargate and Lambda. A Convertible RI could be exchanged and is more work.

**6.** Two VPCs in one Region exchange a few GB a month. Peering. A Transit Gateway attachment has an hourly cost this volume will not justify. Revisit when a third VPC or a data center appears.

**7.** The CUR shows data transfer as the top cost. Look first at NAT data processing, cross-AZ chatter, and cross-Region replication or internet egress. The fixes are gateway endpoints, AZ affinity where it is safe, CloudFront, and turning off replication the RPO does not need.

**8.** A budget alert fired at 80 percent. The application is still launching instances. A budget notifies. It does not enforce. An SCP, a Service Catalog constraint, or an automation you built is what stops a launch. Anyone who answers "the budget will prevent the spend" has not used a budget.

**9.** Dev copies production: Multi-AZ, three NAT Gateways, the same instance size, running all weekend. Single-AZ, one NAT or none, a smaller class, stopped outside working hours. Put it back only for the subsystems whose downtime the stem forbade.

**10.** They want the S3 bill split by application. Tags exist on the buckets. They were never activated as cost allocation tags, and there is no CUR, only the monthly PDF. Activate the tags, wait for the next report, and deliver a CUR. Tagging alone does not split the bill you can query.

## Commands

```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-10-01,End=2026-10-11 \
  --granularity MONTHLY \
  --metrics UnblendedCost \
  --group-by Type=DIMENSION,Key=SERVICE

aws budgets describe-budgets --account-id "$ACCOUNT"

aws ec2 describe-addresses --query 'Addresses[?AssociationId==null]'
aws ec2 describe-volumes --filters Name=status,Values=available
aws ec2 describe-nat-gateways --filter Name=state,Values=available

aws s3api put-bucket-lifecycle-configuration \
  --bucket "$BUCKET" \
  --lifecycle-configuration file://lifecycle.json

aws compute-optimizer get-enrollment-status
```

A lifecycle file that matches the "cold after 90 days, abort multipart, expire old versions" story:

```json
{
  "Rules": [{
    "ID": "cold-and-clean",
    "Status": "Enabled",
    "Filter": { "Prefix": "" },
    "Transitions": [
      { "Days": 90, "StorageClass": "GLACIER" }
    ],
    "NoncurrentVersionExpiration": { "NoncurrentDays": 30 },
    "AbortIncompleteMultipartUpload": { "DaysAfterInitiation": 7 }
  }]
}
```

Use `DEEP_ARCHIVE` when the stem allowed hours and a long minimum retention. Use `GLACIER_IR` when they need milliseconds. `GLACIER` in the API is Flexible Retrieval.

## Exercise set

1. A Standard RI for `m5.xlarge` in one AZ, then the fleet moves to `m7g.large`. Why did the discount stop, and which purchase would have survived?
2. Intelligent-Tiering versus a lifecycle to Deep Archive when the access pattern is unknown.
3. Two VPCs, a few GB a month. Peering or Transit Gateway?
4. Data transfer is the top line in the CUR. Name the three transfers to look for first.
5. A budget alert fired and instances are still launching. Why?
6. One NAT Gateway or one per AZ, when the stem says the cheapest design and also says the private subnets must keep outbound internet if one AZ fails?
7. Spot, On-Demand, or a Savings Plan for the only PostgreSQL instance?
8. A dev environment runs Multi-AZ RDS all weekend with no readers. Name two cost changes that do not change the engine.
9. Public IPv4 on every instance, plus an ALB. What do you remove, and what keeps serving users?
10. S3 Transfer Acceleration versus a normal upload for users in the same Region as the bucket.
11. RDS Proxy on a single EC2 application that opens ten connections. Why is it the wrong cost answer?
12. DynamoDB on-demand versus provisioned for a brand-new table with an unknown launch-day spike.
13. Cross-Region replication on a bucket whose RPO is 24 hours and whose restore time can be a day. What do you stop paying for?
14. gp2 grown to 2 TB so the included IOPS reach 6,000, while the data is 200 GB. What do you change?
15. Cost Explorer shows the spend. The manager asks which feature reduces it. What do you tell them?

## Answers

1. A Standard RI is tied to the family and the other attributes you bought. `m7g` is a different family. A Compute Savings Plan applies across families and also covers Fargate and Lambda. A Convertible RI can be exchanged and is more operational work.
2. Intelligent-Tiering. Deep Archive is for data you know has gone cold and can wait hours to be read. Putting unknown data there creates retrieval cost and latency the day it is hot.
3. Peering. Transit Gateway's hourly attachment cost is not justified by a few GB. The day a third network or a data center shows up, price the Transit Gateway again.
4. NAT data processing, cross-AZ traffic, and cross-Region replication or internet egress. Gateway endpoints, safer AZ affinity, and CloudFront or less replication are the usual fixes.
5. A budget notifies. It does not enforce a quota. You need an SCP, a Service Catalog constraint, or your own automation to refuse the launch.
6. One NAT per AZ. The AZ-failure sentence is a resilience constraint the cost domain does not get to delete. A single NAT would be right only if losing outbound during an AZ failure were acceptable. Add gateway endpoints so the NAT is not also the S3 path.
7. Not Spot. The database cannot be interrupted. If it is steady, an RDS Reserved Instance. A Compute Savings Plan does not cover RDS. On-Demand until you know it is steady.
8. Turn off Multi-AZ if a dev outage is acceptable, and stop the instance outside working hours. Shrink the class to match the dev load. Keep backups only as long as the dev policy requires.
9. Remove the public addresses from the instances. Users enter through the ALB. The instances can sit in private subnets. You stop paying for an address per instance, and you remove a network path Domain 1 did not want.
10. A normal upload. Transfer Acceleration helps over long distance. In-Region it adds cost and does not help.
11. The proxy has an hourly cost and this application is not opening a storm of connections. It does not make the ten connections cheaper. Buy it when Lambda or a large fleet is exhausting `max_connections`.
12. On-demand. You do not know the rate, and a provisioned table you under-size will throttle on launch day. Move to provisioned later if the traffic becomes flat and the price comparison says so.
13. Continuous cross-Region replication of every PUT. Copy backups or replicate on a schedule that meets 24 hours. You keep a second copy. You stop paying to mirror every write in real time.
14. Move to gp3, set 6,000 IOPS and the throughput you measured, and shrink the volume toward the data size plus headroom. You were buying capacity to rent IOPS.
15. Cost Explorer does not reduce spend. It shows it. The reduction is the architecture change: the lifecycle, the Savings Plan, the endpoint, the deleted idle resource. Budgets do not reduce it either. They warn you.
