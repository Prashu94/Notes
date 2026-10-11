# SAA-C03 practice exam

50 original questions. One best answer unless the stem says choose two. 90 minutes is a fair drill. The real exam is 65 questions and 130 minutes, of which 15 questions are unscored.

Score it after you finish. Answers and the reason are in `06-saa-practice-exam-answers.md` in this folder. Do not open that file first.

Passing this drill at 80% is a signal to take the official Skill Builder practice set, not a signal that you are done.

## Questions

1. A company runs one AWS account. Developers share an IAM user access key stored in a wiki. The CISO wants MFA, unique identities, and the ability to disable one person without rotating a shared key. Which approach meets the requirements with the least ongoing risk?
   A. Create one IAM user per developer and email them the shared wiki key
   B. Enable IAM Identity Center, require MFA, and assign permission sets to groups
   C. Put the access key in Secrets Manager and let every developer read it
   D. Enable MFA on the root user and continue to share the root password

2. An application in a private subnet must read and write an S3 bucket. The team wants to avoid NAT gateway data processing charges for that traffic. What should they add?
   A. An S3 interface endpoint
   B. An S3 gateway endpoint on the subnet route table
   C. A second NAT gateway
   D. VPC peering to a public subnet

3. A bucket stores financial reports. A regulator requires that objects cannot be deleted or overwritten for seven years, including by the root user. Which control meets the requirement?
   A. SSE-S3
   B. S3 versioning only
   C. S3 Object Lock in compliance mode
   D. A bucket policy that denies `s3:DeleteObject` for `IAM` users

4. Users of a global website download the same images all day from EC2. The images change about once a week. Which change most reduces load on the instances?
   A. Move the images to S3 and put CloudFront in front of the bucket
   B. Put a Network Load Balancer in front of the instances
   C. Enable Multi-AZ on the instances
   D. Use a NAT gateway

5. A REST API must authenticate application users who sign up with email or a social identity provider, and it must authorize calls per user. The API runs on API Gateway and Lambda. Which service issues the user tokens?
   A. IAM Identity Center
   B. Cognito user pools
   C. AWS Directory Service
   D. Secrets Manager

6. A company detected attempted SQL injection against a public web application. The application team cannot change the code this quarter. Which control blocks common injection patterns at the edge?
   A. A security group that denies port 80
   B. A network ACL rule that denies port 1433
   C. AWS WAF with a SQL injection managed rule group, attached to CloudFront or the ALB
   D. Amazon Inspector

7. An Amazon EC2 instance role needs to read objects encrypted with a customer managed KMS key in another account. `s3:GetObject` is allowed on both sides. Reads still fail. Which additional permission is required?
   A. `kms:Decrypt` allowed in the key policy and in the role
   B. `s3:GetBucketPolicy`
   C. `kms:CreateGrant` on `*` in the caller account only
   D. Make the object SSE-S3

8. A web tier Auto Scaling group uses the EC2 health check. Instances stay in service after the application process crashes and the ALB returns 502. What should the team change?
   A. Switch the ASG health check to ELB and use an HTTP health check
   B. Add a second Internet Gateway
   C. Move the instances to a cluster placement group
   D. Enable detailed monitoring only

9. A shopping cart is stored in memory on one EC2 instance. The team wants to scale out without logging users out. The application can be changed. Where should the session move?
   A. An instance store volume
   B. Amazon ElastiCache or DynamoDB
   C. A second EBS volume on the same instance
   D. The ALB access logs

10. An order API must accept the order even when the shipping service is down for 20 minutes. Shipping can happen after the user gets a response. Which change meets this?
    A. Call shipping synchronously and raise the timeout to 20 minutes
    B. Put the shipping request on Amazon SQS and return success after the send
    C. Use a larger EC2 instance for shipping
    D. Enable Multi-AZ on the API instances

11. A PostgreSQL database must fail over automatically if an Availability Zone is lost. Readers are not required. Which configuration meets this?
    A. A single-AZ RDS instance and a manual snapshot
    B. RDS Multi-AZ
    C. A cross-Region read replica with no promotion plan
    D. DynamoDB global tables

12. The RTO is 24 hours and the RPO is 4 hours if an entire Region fails. The company wants the lowest cost. Which DR pattern fits?
    A. Active-active in two Regions
    B. Warm standby at full size
    C. Backup and restore, with backups copied to the second Region
    D. Aurora Global Database with a full fleet always running in both Regions

13. A company needs a workflow that bills a customer, waits up to two days for a warehouse acknowledgment, and then notifies shipping. Which service fits?
    A. SQS delay queues only
    B. Standard Step Functions
    C. A cron job on one EC2 instance
    D. SNS email

14. An application reads a product row by product id at a very high request rate. The data is key-value. SQL joins are not required. Which database fits?
    A. Amazon RDS for MySQL on a single `db.t3.micro`
    B. Amazon DynamoDB
    C. Amazon Neptune
    D. AWS Glue Data Catalog

15. A reporting team runs complex SQL joins every hour against the production transactional database and slows checkout. Which change protects checkout and serves the reports?
    A. A read replica or an Aurora reader endpoint for the reports
    B. Move checkout to a scan in DynamoDB
    C. Put the reports on the primary and checkout on a replica
    D. Disable backups during the day

16. Static and dynamic HTTP content is served to users worldwide. Dynamic responses must not be cached. Static files should be. Failover between Regions is less important than caching. Which service fits the static tier?
    A. AWS Global Accelerator
    B. Amazon CloudFront
    C. AWS Direct Connect
    D. A NAT gateway in each Region

17. A UDP game server needs static anycast IP addresses and fast failover between two Regions. Which service fits?
    A. Amazon CloudFront
    B. AWS Global Accelerator in front of Network Load Balancers
    C. Amazon Route 53 simple routing only
    D. AWS WAF

18. A nightly job converts CSV in S3 into partitioned Parquet for analysts who query with SQL. Which two services complete this with the least custom code? (Choose two.)
    A. AWS Glue
    B. Amazon Athena
    C. Amazon MQ
    D. AWS Snowball
    E. Amazon Inspector

19. A team will copy 80 TB from an on-premises NFS server to S3 over a weekend. The available bandwidth would take three weeks. Which service fits?
    A. AWS DataSync only
    B. AWS Snow Family
    C. S3 multipart upload from a laptop
    D. AWS Transfer Family

20. Objects are large, rarely accessed after 30 days, and must be retrieved in milliseconds when they are accessed. Which S3 class after day 30?
    A. Glacier Deep Archive
    B. Glacier Flexible Retrieval
    C. Glacier Instant Retrieval
    D. S3 Express One Zone for cost savings

21. A steady fleet of EC2 and Fargate tasks runs all year. Instance families change every few months. Which purchasing option gives a discount across those changes?
    A. A Standard Reserved Instance for the current size
    B. A Compute Savings Plan
    C. Spot only
    D. Dedicated Hosts

22. A batch worker can be interrupted and restarted from a checkpoint. It runs for two hours. Which compute purchase cuts the cost?
    A. Spot
    B. Dedicated Host
    C. Lambda with a 15-minute timeout and no checkpoint
    D. A NAT gateway

23. A Multi-AZ application in private subnets downloads OS patches and also reads S3. One NAT gateway in one AZ is the current design. The company wants to survive an AZ failure and reduce S3 processing charges. Which two changes? (Choose two.)
    A. A NAT gateway in each AZ
    B. Remove all NAT gateways and add no endpoints
    C. An S3 gateway endpoint
    D. An Internet Gateway on the data subnets
    E. Turn off DNS support

24. A development database is Multi-AZ `db.r6g.2xlarge` and is used two hours a day. The team can recreate it from a snapshot. Which change most reduces cost without blocking development?
    A. Aurora Global Database
    B. A smaller single-AZ instance, stopped outside working hours
    C. DynamoDB global tables
    D. Enable RDS Proxy and a second Region

25. Cost Explorer shows NAT data processing as the largest line. The private instances mostly call S3 and DynamoDB. What is the first change?
    A. Gateway endpoints for S3 and DynamoDB
    B. Direct Connect
    C. A larger NAT gateway instance size
    D. S3 Intelligent-Tiering

26. A company has 40 accounts. Even administrators in member accounts must be unable to disable CloudTrail. Which control enforces that?
    A. An IAM policy attached to each administrator user
    B. A service control policy
    C. A CloudWatch dashboard
    D. S3 Block Public Access

27. New accounts must be created with guardrails and a standard network. The team wants the least operational overhead and has no existing landing zone. Which service?
    A. Manually run a wiki checklist
    B. AWS Control Tower
    C. Amazon Lightsail
    D. AWS Device Farm

28. A partner account must assume a role in your account. You want to prevent a confused-deputy problem. What do you add to the trust policy?
    A. `sts:ExternalId`
    B. `s3:prefix`
    C. A NAT gateway
    D. An S3 lifecycle rule

29. Which statement about security groups and network ACLs is correct?
    A. Both are stateful
    B. Security groups are stateful and network ACLs are stateless
    C. Security groups support deny rules and network ACLs do not
    D. Network ACLs are attached to elastic network interfaces

30. A Lambda function must read a private RDS database and write results to S3. The function is not in a VPC. RDS is not publicly accessible. What is the minimum network change?
    A. Attach the function to the database subnets and add an S3 gateway endpoint so S3 does not require a NAT
    B. Make RDS publicly accessible
    C. Put the database password in the function code and leave the network unchanged
    D. Use a Network Load Balancer without attaching the function to the VPC

31. An API Gateway REST integration times out at about 29 seconds. The work takes two minutes. What should the API do?
    A. Raise the Lambda timeout to 15 minutes and keep the client waiting
    B. Return HTTP 202 after enqueueing the work to SQS or Step Functions
    C. Switch the health check to TCP
    D. Enable S3 Transfer Acceleration

32. A CloudFront distribution must use an ACM certificate for `www.example.com`. In which Region must that certificate be requested?
    A. The Region of the S3 bucket
    B. us-east-1
    C. Every Region where users live
    D. The Region of the NAT gateway

33. Which storage is a shared POSIX file system for Linux instances in many Availability Zones?
    A. One EBS volume with Multi-Attach across Regions
    B. Amazon EFS
    C. Amazon S3
    D. Instance store

34. An on-premises application must continue to use SMB to read and write files that are stored durably in S3. Users are in the office. Which service provides the SMB endpoint?
    A. AWS Storage Gateway File Gateway
    B. Amazon EBS
    C. AWS Snowball only, with no ongoing endpoint
    D. Amazon DynamoDB

35. A Kinesis data stream is consumed by custom code that must be able to reprocess the last 24 hours. Which service fits better than Firehose?
    A. Amazon Kinesis Data Streams
    B. Amazon Data Firehose with no backup
    C. AWS Glue crawler only
    D. Amazon MQ

36. Analysts need a dashboard on data that already sits in S3 as Parquet. They know SQL and should not manage servers. Which service queries the data?
    A. Amazon Athena
    B. Amazon Neptune
    C. AWS WAF
    D. Amazon Inspector

37. A company wants one backup policy for RDS, EFS, and DynamoDB, with a copy in a second Region and a vault that cannot be deleted early by an administrator. Which service?
    A. Manual `aws rds create-db-snapshot` only
    B. AWS Backup with a copy rule and a vault lock
    C. S3 lifecycle on the databases
    D. Amazon Macie

38. Which Route 53 routing policy sends users to the healthy primary endpoint and to a secondary endpoint when the primary health check fails?
    A. Simple
    B. Failover
    C. Geoproximity with no health checks
    D. Multivalue answer with one record

39. A team tags resources with `cost-center` but Cost Explorer still cannot group by that tag. What did they skip?
    A. Activating the cost allocation tag in the billing console
    B. Creating a NAT gateway
    C. Enabling S3 versioning
    D. Purchasing a Dedicated Host

40. Amazon GuardDuty, Amazon Inspector, and AWS Security Hub are enabled. Which statement is correct?
    A. Inspector finds CVEs. GuardDuty finds suspicious activity. Security Hub aggregates findings
    B. They are three names for the same detector
    C. GuardDuty encrypts EBS volumes
    D. Security Hub replaces IAM

41. A monolithic Java application should move to AWS with the fewest changes. The team wants a managed platform that handles the load balancer and the Auto Scaling group. Which service?
    A. Amazon EKS with a service mesh they must operate
    B. AWS Elastic Beanstalk
    C. Amazon Macie
    D. AWS Snowball Edge

42. A containerized service has no Kubernetes requirement and the team does not want to manage EC2. Which compute platform fits?
    A. Amazon ECS on AWS Fargate
    B. Amazon EKS on self-managed nodes because it is always simpler
    C. A single EC2 instance with Docker installed by SSH
    D. AWS Device Farm

43. An application writes audit events that many downstream systems must each process. One downstream system is often offline and must catch up later without blocking the others. Which pattern?
    A. One SQS queue with five competing consumers that delete each message
    B. Amazon SNS to a separate SQS queue for each consumer
    C. One DynamoDB item overwritten by each consumer
    D. A single Lambda with no retry

44. A DynamoDB table uses `status` as the partition key. Almost all items have status `OPEN` and the table throttles while total capacity looks unused. What is the cause?
    A. A hot partition
    B. S3 eventual consistency
    C. A missing Internet Gateway
    D. The wrong S3 storage class

45. Which statement about an Amazon RDS read replica is correct?
    A. It is a synchronous standby that fails over automatically and never serves reads
    B. It is an asynchronous copy that can serve reads and can be promoted
    C. It provides strongly consistent writes in a second Region with no lag
    D. It replaces backups

46. A company must run a Windows file share integrated with Active Directory and available in two AZs. Which service?
    A. Amazon EFS
    B. Amazon FSx for Windows File Server, Multi-AZ
    C. Instance store
    D. AWS Glue

47. Private subnets must resolve `corp.example.com` using on-premises DNS servers. Which Route 53 feature?
    A. A Resolver outbound endpoint and a forwarding rule
    B. A public hosted zone with a simple record
    C. Transfer Acceleration
    D. A gateway endpoint

48. The CFO wants an email when the monthly bill forecast exceeds 5,000 USD. The email does not need to stop resources. Which service?
    A. AWS Budgets
    B. AWS Artifact
    C. Amazon Macie
    D. AWS WAF

49. A data processing job can use either a shared file system or object storage. The job will be rewritten to process independent objects in parallel. The data is cold most of the year. Which store is the better default?
    A. Amazon S3 with a lifecycle policy
    B. A large gp2 volume on one instance
    C. Instance store
    D. A Dedicated Host

50. After a deployment, half the EC2 fleet runs the new version and the new version fails its health check. Users hit both versions. Which Elastic Beanstalk deployment policy would have kept the original environment serving until the new one was healthy?
    A. All at once
    B. Rolling
    C. Immutable or blue/green with a swap after health checks
    D. Delete the load balancer during deployment
