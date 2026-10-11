# SAA-C03 practice exam answers

Score one point per fully correct question. Questions 18 and 23 need both options. 40 of 50 is 80%.

| # | Answer | Why |
| --- | --- | --- |
| 1 | B | Identity Center gives each person an identity, MFA, and a permission set. A shared key fails the "disable one person" requirement. Root is not an application identity |
| 2 | B | S3 and DynamoDB use gateway endpoints, which also avoid the hourly interface-endpoint charge. An interface endpoint is the wrong type for S3 when a gateway endpoint is offered |
| 3 | C | Compliance mode blocks delete and overwrite for the retention period, including root. A bucket policy against IAM users does not stop root and does not stop a principal you forgot. SSE-S3 encrypts. It does not retain |
| 4 | A | The bytes are cacheable and global. CloudFront plus S3 removes that traffic from EC2. An NLB does not cache. Multi-AZ is not a setting you "enable on instances" to cache images |
| 5 | B | User pools issue tokens for application users, including social sign-in. Identity Center is the workforce console. Directory Service is Active Directory. Secrets Manager stores secrets |
| 6 | C | WAF inspects HTTP. A security group does not parse SQL. Port 1433 is not the injection path. Inspector reports vulnerabilities. It does not sit in the request path |
| 7 | A | SSE-KMS with a customer managed key requires `kms:Decrypt` on the key policy and the caller. The S3 permission is not sufficient |
| 8 | A | EC2 health checks do not see a dead process. ELB health checks do |
| 9 | B | A shared store survives instance replacement. Instance store and a local EBS volume die with the instance or stay stuck to it. Access logs are not a session store |
| 10 | B | The queue decouples shipping. A 20-minute synchronous HTTP call will break API Gateway and user patience. A bigger instance does not survive the shipping process being down |
| 11 | B | Multi-AZ is automatic failover inside the Region. A snapshot is not automatic. A replica does not fail over until you promote it. Global tables abandon PostgreSQL |
| 12 | C | 24 hours and 4 hours fit backup and restore. The other options cost more than the RTO requires |
| 13 | B | Standard workflows last up to a year and can wait. An SQS delay queue maxes out at 15 minutes. Cron on one box is a single point of failure. SNS sends a message. It does not wait two days for an acknowledgment |
| 14 | B | Key-value at high rate is DynamoDB. A `t3.micro` relational instance is the performance trap. Neptune is a graph. The Glue catalog is not the product database |
| 15 | A | Reports go to a reader. Checkout stays on the writer. Reversing that slows checkout. Scans do not replace SQL joins |
| 16 | B | CloudFront caches the static tier and can bypass cache for dynamic paths. Global Accelerator does not cache. Direct Connect and NAT are not CDNs |
| 17 | B | UDP plus static anycast IPs plus Regional failover is Global Accelerator with NLBs. CloudFront is HTTP. Simple routing does not health-check. WAF is not a UDP accelerator |
| 18 | A and B | Glue converts and catalogs. Athena queries. MQ, Snowball, and Inspector do not transform the lake for SQL |
| 19 | B | The bandwidth misses the window. Snow is the offline transfer. DataSync is the answer when the link can finish in time |
| 20 | C | Instant Retrieval is the milliseconds Glacier class. Deep Archive and Flexible Retrieval are slower. Express One Zone is a hot, single-AZ performance class and not the cheap infrequent class |
| 21 | B | A Compute Savings Plan applies across EC2, Fargate, and instance family changes. A Standard RI is pinned to what you bought. Spot can be interrupted. Dedicated Hosts are for licensing |
| 22 | A | Spot fits interruptible checkpointed work. Lambda's 15-minute limit loses a two-hour job. A Dedicated Host and a NAT gateway do not make the worker cheaper in the way the stem asks |
| 23 | A and C | One NAT per AZ so an AZ loss does not remove outbound internet. A gateway endpoint so S3 skips the NAT. Removing every NAT with no endpoint breaks patch downloads. An IGW on the data subnet makes the data tier public |
| 24 | B | The database is idle most of the week and they accepted a snapshot restore. Global Database and a second Region increase cost. Proxy does not replace a right-sized instance |
| 25 | A | Gateway endpoints remove the NAT processing charge for those two services. Intelligent-Tiering changes storage class, not NAT. Direct Connect does not fix a VPC route to S3 |
| 26 | B | An SCP is the ceiling administrators cannot detach. An IAM policy can be changed by the admin it is meant to stop. A dashboard and Block Public Access do not enforce CloudTrail |
| 27 | B | Control Tower is the landing zone with the least operational overhead when you do not already have one. Lightsail and Device Farm are not account vending |
| 28 | A | `sts:ExternalId` is the confused-deputy control on a cross-account trust |
| 29 | B | Security groups are stateful allow lists on ENIs. Network ACLs are stateless allow and deny lists on subnets |
| 30 | A | The function must join the VPC to reach private RDS. An S3 gateway endpoint keeps S3 off a NAT. Making RDS public fails the security requirement. A password in code is a separate defect and does not create a network path |
| 31 | B | API Gateway will not wait two minutes. Acknowledge and process asynchronously |
| 32 | B | CloudFront only sees ACM certificates in us-east-1 |
| 33 | B | EFS is the Multi-AZ shared POSIX file system. EBS Multi-Attach is single-AZ and not a general shared filesystem across Regions. S3 is object storage. Instance store is local and ephemeral |
| 34 | A | File Gateway presents NFS or SMB and stores the data in S3. EBS is not an office SMB share. Snowball is a transfer appliance. DynamoDB is not SMB |
| 35 | A | Streams retain data for the consumer to replay. Firehose is delivery onward. A crawler and a broker do not provide that retention model |
| 36 | A | Athena queries Parquet in S3 with SQL and no servers. Neptune is a graph. WAF and Inspector are not query engines |
| 37 | B | AWS Backup covers those services in one plan, copies across Regions, and vault lock stops early deletion. A single RDS snapshot command ignores EFS and DynamoDB. Lifecycle and Macie are not backup plans |
| 38 | B | Failover routing uses a primary, a secondary, and health checks. Simple routing does not fail over. Multivalue is not a primary/secondary pair |
| 39 | A | User-defined tags become cost allocation tags only after they are activated. The other options do not create a billing dimension |
| 40 | A | Three different jobs. Security Hub is the aggregation point. It is not IAM and it does not encrypt disks. GuardDuty is not a CVE scanner |
| 41 | B | Beanstalk is the managed platform for a traditional web app. EKS is more operations. Macie and Snowball do not host the application |
| 42 | A | ECS on Fargate runs the container without EC2 and without Kubernetes. Self-managed EKS nodes are more work. SSH to one instance is the availability and operations trap. Device Farm tests phones |
| 43 | B | Fanout gives each consumer a queue and a backlog. Competing consumers on one queue share messages. They do not each get a copy |
| 44 | A | A low-cardinality partition key concentrates traffic. Spare table capacity does not help that partition |
| 45 | B | Replicas are asynchronous and readable. Promotion is a deliberate step. They are not the Multi-AZ standby and they do not replace backups |
| 46 | B | FSx for Windows File Server is SMB plus Active Directory, and it has a Multi-AZ deployment. EFS is NFS for Linux. Instance store is not a share. Glue is ETL |
| 47 | A | An outbound Resolver endpoint forwards the company domain to on-premises DNS. A public zone does not reach a private corporate namespace. Transfer Acceleration and a gateway endpoint are not DNS forwarders |
| 48 | A | Budgets send the forecast alert. They do not stop spend unless you add an action. Artifact, Macie, and WAF do not watch the bill |
| 49 | A | Object storage plus lifecycle matches parallel processing and cold data. A single EBS volume does not parallelize across a fleet. Instance store is ephemeral. A Dedicated Host does not store the objects |
| 50 | C | Immutable and blue/green leave the old fleet in place until the new one is healthy. Rolling and all-at-once expose users to the bad version. Deleting the load balancer is an outage |
