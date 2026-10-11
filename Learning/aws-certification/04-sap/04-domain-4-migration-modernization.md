# SAP Domain 4 — Migration and modernization (20%)

Tasks 4.1 through 4.4. Tools and commands: `02-services/15-migration-mgn-dms-datasync-snow-transfer.md`.

## 4.1 What moves, and in which wave

The 7 Rs:

| Strategy | The sentence |
| --- | --- |
| Retire | Nobody uses it. Do not migrate it |
| Retain | Stays on-premises for now. Factory latency, a license, a later mainframe |
| Relocate | Hypervisor move. VMware to VMware on AWS |
| Rehost | Lift-and-shift servers. Application Migration Service |
| Replatform | Small change. Oracle on EC2 becomes RDS. A VM becomes Beanstalk or ECS |
| Repurchase | Replace it with SaaS |
| Refactor | Change the design. Monolith to services, database to Aurora or DynamoDB |

Discover with Application Discovery Service. Track with Migration Hub. Wave plan: low dependency and low risk first. TCO is Pricing Calculator or Migration Evaluator against the data center bill. The exam will not ask you to compute the dollars. It will ask which input changes the decision: steady versus burst, license, transfer, people.

## 4.2 How it moves

| Situation | Tool |
| --- | --- |
| Servers, cut over in minutes | Application Migration Service |
| Already replicating for DR and you will cut over | Elastic Disaster Recovery |
| Database, minimal downtime | DMS full load plus CDC |
| Schema change of engine | SCT, then DMS |
| Files online, verify, schedule | DataSync |
| SFTP into S3 | Transfer Family |
| Petabytes, the link is too slow | Snow Family |
| Long fat network, one bucket | S3 Transfer Acceleration or multipart. DataSync if you want verification |
| People | Identity Center when you are ready to federate. Managed Microsoft AD when Windows must keep AD |
| Network | VPN to start. DX if volume and timeline justify a circuit. Route 53 weighted records for the cutover |
| Governance | Control Tower or Organizations before the workloads land, not after forty accounts exist |

Encrypt the path. IAM role on the replication instance. KMS on the target. Security group limited to the replication ports. No public snapshot sharing.

## 4.3 Where it lands

| Source | Small change | Allowed to change |
| --- | --- | --- |
| VM | EC2 via MGN | Beanstalk, ECS, App Runner |
| Kubernetes | EKS | ECS if they want to leave Kubernetes |
| Docker, no Kubernetes | ECS on Fargate | Same |
| Windows share | FSx for Windows or File Gateway | S3 if the app can use objects |
| NFS | EFS, OpenZFS, or ONTAP | S3 |
| Oracle or SQL Server | RDS for that engine, or EC2 if a feature blocks RDS | Aurora after SCT |
| MongoDB | DocumentDB if the API fits | DynamoDB if the access pattern is key-value |
| Elasticsearch | OpenSearch | A purpose-built store if they only needed one query |

## 4.4 What gets modern afterwards

Modernization removes a cost they are paying, not a slogan.

| They pay for | Move |
| --- | --- |
| Idle servers at night | Lambda, Fargate, or Aurora Serverless v2 |
| A table polled by cron | SQS or EventBridge |
| A file drop | S3 event |
| Stored-procedure orchestration | Step Functions |
| A relational table used only as a key lookup at extreme rate | DynamoDB |
| Read-heavy SQL | Aurora readers or a cache |

Lambda everywhere is not the task. The task is the constraint the current system pays for.

## Scenario

Two hundred VMs, one Oracle database, a file share, a weekend cutover window, the link would take a month for the files, the database must lose under a minute. MGN for the VMs. Snow for the bulk files, DataSync for the last delta if the share is still changing. DMS CDC for Oracle. FSx or File Gateway for the share depending on whether users stay on SMB. Route 53 weighted records for the cutover. Do not start with a refactor of all two hundred.

## The 7 Rs, as a decision you can defend

Retire first. A server nobody can name does not get an MGN agent. Retain when the factory network, a mainframe schedule, or a license makes this wave the wrong wave. Say what would have to change for a later wave. Relocate is the VMware-to-VMware-on-AWS move, and it is not rehost. Rehost is MGN onto EC2, the server image, the same operational shape, the fastest way to leave a data center lease. Replatform is one managed-service change: the same app on RDS instead of Oracle-on-EC2, or on Fargate instead of a VM you patch. Repurchase is SaaS, and the constraint is the data export and the identity federation, not a VPC diagram. Refactor is a new design. It is the slowest R. It is the right R when the current shape cannot meet a scale or a cost number they have already committed to, and the wrong R when the lease ends in ninety days.

Application Discovery Service collects what is installed and how it talks. Migration Hub is the tracker across tools. Migration Evaluator is the business case against the data center bill. The exam will not ask you to compute dollars. It will ask which fact changes the wave: a license that is cheaper on a Dedicated Host, a chatty database that should move with its app, a file share that is larger than the circuit can carry, a team that can run RDS and cannot run a refactor.

Wave order: few dependencies, low risk, high learning. The database that every app calls is not wave one unless the apps are moving with it. Identity and the network land before the workloads, or every wave invents its own VPC and its own IAM users.

## How the data actually moves

MGN installs an agent, replicates block changes, and cuts over by launching the instance and redirecting. The cutover window is minutes when replication is healthy. It is not the tool for a database whose RPO is a transaction log you understand. Use it for the servers. Use DMS for the database so the cutover is a CDC checkpoint and not a crash-consistent disk.

DMS full load plus CDC is the minimal-downtime database move. The replication instance needs a security group path to the source and the target, and it needs enough CPU and memory for the change rate. A tiny replication instance is why CDC falls behind and the cutover window disappears. Homogeneous (Oracle to RDS Oracle) does not need schema conversion. Heterogeneous (Oracle to Aurora PostgreSQL) needs the Schema Conversion Tool, a human to fix what SCT could not convert, and a test of the queries. SCT does not move the data. DMS does not convert the procedures. People swap them.

DataSync verifies, schedules, and can use an agent on-premises. It is the file tool. It is not Snow. Snow is the device you ship when the math on the link fails. After Snow imports into S3, DataSync or a final sync catches the delta if the source is still changing. Transfer Family is the SFTP front door onto S3, for partners who will not install DataSync. Transfer Acceleration is an S3 upload path, not a migration product for a data center.

Storage Gateway File Gateway is the ongoing SMB or NFS mount in front of S3, for users who stay on a share. FSx for Windows is the ongoing Windows share with ACLs and AD. DataSync into FSx is the migration onto that share. Do not answer File Gateway when they need NTFS ACLs preserved for a Windows estate, and do not answer FSx when the applications can be changed to use S3 and the cost stem is serious.

Cutover traffic: Route 53 weighted records, or a load balancer target, or a Global Accelerator endpoint weight. Lower the TTL before the weekend. A one-day TTL on Thursday means Sunday's cutover is invisible to half the clients. Database cutover is: stop the writers, let CDC catch up, verify a checksum or a row count, repoint, do not start the old writers again. Two writers without a design is split brain.

The path is encrypted. The replication instance's role is not admin. The target bucket and the target database are encrypted with a key the migration team can use and the whole company cannot administer. Snapshots are not shared public. A security group allows the replication port from the source CIDR, not `0.0.0.0/0`.

## Where it is allowed to land

| Source | If the stem says smallest change | If the stem allows a managed service | If the stem says modernize |
| --- | --- | --- | --- |
| VM | EC2 via MGN | Beanstalk or ECS, if the app is a web process | Break it up only after it is off the lease |
| Kubernetes | EKS | EKS on Fargate to drop nodes | ECS only if they want to leave the Kubernetes API |
| Docker, no Kubernetes | ECS on Fargate | The same | Lambda only for the pieces that are short requests |
| Windows share | FSx for Windows | File Gateway if ACLs can soften | S3 if the app can change |
| NFS | FSx for OpenZFS or ONTAP, or EFS | EFS | S3 |
| Oracle or SQL Server | RDS for that engine, or EC2 if a feature or a license blocks RDS | Aurora after SCT, if the features fit | The same, plus readers, plus removing the procedures that were the orchestration |
| MongoDB | DocumentDB if the API surface fits | DynamoDB if the access is key-value and they will change the driver | Do not force DocumentDB to be a relational store |
| Elasticsearch | OpenSearch | OpenSearch | A purpose-built store if they only had one query type |
| Mainframe or a factory system | Retain this wave | A strangler only for the interfaces they named | Not MGN |

Identity moves with the people. Identity Center federated to the existing IdP is the target. A two-year period of IAM users "until we finish migrating" is how the users become permanent. Managed Microsoft AD is for the Windows workloads that must join a domain, in parallel with Identity Center, not instead of it.

Network moves before the servers. A Transit Gateway, a VPN or Direct Connect, and the Resolver rules, so a migrated server can still reach what remains on-premises. Migrating the app and leaving DNS for the following quarter is a cutover outage.

Governance moves before the fortieth account. Control Tower or an existing landing zone, the organization trail, the SCPs, the billing CUR. Accounts created ad hoc during a migration are the mess Domain 1 then has to repair.

## Modernization after the move, still tied to a bill

Idle servers at night become scheduled scaling, Fargate, or Lambda, not a slogan. A table polled by cron becomes SQS or EventBridge. A file drop becomes an S3 event. Stored procedures that call other systems become Step Functions, because the retry and the audit then exist. A relational table used only as a key lookup at a rate RDS cannot meet becomes DynamoDB. Read-heavy SQL gets a reader or a cache before it gets a new engine.

Lambda everywhere fails the task when the process is a long transaction, a stateful protocol, or a library that does not fit the runtime. The modernization has to name the cost or the limit that went away.

Strangler fig is the pattern when the monolith stays up and one route at a time moves to a new service behind the same API or the same hostname. It is the refactor that does not need a weekend for all two hundred VMs. Big-bang cutover is the rehost. Do not mix the words.

## Worked scenarios

**1.** The lease ends in four months. Two hundred VMs, unknown dependencies. Discovery first, then MGN, waves, no refactor in this lease. A team that starts by drawing microservices will still be in the data center when the lease ends.

**2.** Oracle, features SCT cannot convert, the license is already owned and is per socket. RDS Oracle or Oracle on EC2 on a Dedicated Host, after you check which features RDS blocks. Aurora PostgreSQL is the answer only when SCT and the application owners have signed the gap list. "Aurora is managed" does not compile a package the tool could not convert.

**3.** 200 TB of files, 200 Mbps, a six-week deadline. The link cannot finish. Snow for the bulk, DataSync for the delta, a checksum. Transfer Acceleration does not change the fact that the volume is larger than the weeks you have.

**4.** The database must lose less than a minute and the app servers can take an hour. DMS CDC for the database, MGN for the servers, and the cutover order is database first only when the servers are ready to be repointed. Practice the CDC lag a week before, on production change rates.

**5.** Users must keep `\\fileserver\share` and NTFS permissions. FSx for Windows File Server, joined to AD, DataSync or the FSx migration path onto it. S3 and a File Gateway fail the ACL sentence. Retraining every user to a web upload fails the "must keep the share" sentence.

**6.** After rehost, the bill is higher than the data center because everything is On-Demand, Multi-AZ, and running all night. That is the modernization wave: Savings Plans, dev schedules, gp3, lifecycle, and only then a refactor of the one system whose shape is the expensive part. The migration is not a failure because you did not refactor during the cutover.

## Exercise

For the two-hundred-VM scenario, write the order of operations from discovery to the Monday after cutover. Include what you do not do.

A complete order: discover and draw dependencies, place the landing zone and the network, replicate with MGN without cutting over, start DMS full load and CDC, ship Snow for the bulk files, lower DNS TTL, a dress rehearsal of the database catch-up, the weekend cutover (stop writers, CDC catch-up, launch cutover instances, weighted DNS, verify), keep the source powered and read-only until the backout window expires, then the cost wave. You do not refactor the estate in the cutover window. You do not open the database security group to the world so the replication instance is "easier."
