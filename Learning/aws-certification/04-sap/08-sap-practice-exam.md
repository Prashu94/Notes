# SAP practice exam

25 original questions. The real exam is 75 questions and 180 minutes. This drill is the decision density, not the clock. Answers in `08-sap-practice-exam-answers.md`.

1. A company has 50 VPCs and a data center. CIDRs do not overlap. They want transitive routing and one operational hub. Which design?
   A. A full mesh of VPC peering
   B. A Transit Gateway in a network account, shared with RAM, plus a Direct Connect gateway or transit VIF
   C. One Internet Gateway per VPC and the public internet
   D. VPC Lattice only

2. Two acquired networks both use `10.1.0.0/16`. Peering fails. What do you add?
   A. A second Transit Gateway route table and private NAT so the ranges can talk without renumbering this quarter
   B. Turn on transitive peering
   C. One security group that allows the overlap
   D. S3 Transfer Acceleration

3. Member account administrators must be unable to stop the organization CloudTrail. The trail stores logs in a central bucket. Which control?
   A. An IAM managed policy named ReadOnlyAccess
   B. An SCP denying `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail`, attached to the workload OUs
   C. A CloudWatch alarm with no action
   D. SSE-S3 on the bucket

4. RPO is 5 seconds. RTO is 15 minutes. The database is PostgreSQL. The company will accept a compatible engine. Lowest operational burden that meets the numbers for a Region failure.
   A. Nightly snapshots
   B. Aurora Global Database and a pilot-light or warm-standby app tier with Route 53 failover
   C. Multi-AZ RDS only
   D. DynamoDB, because it is always the Professional answer

5. RTO is 36 hours. RPO is 12 hours. The CFO asked for the lowest cost. What do you recommend?
   A. Active-active
   B. Backup and restore with cross-Region backup copies
   C. Aurora Global Database with a full fleet in both Regions
   D. Global Accelerator for the database

6. A third party assumes a role and a different product in their account started using it. What do you change?
   A. Add `sts:ExternalId` to the trust policy
   B. Make the role's permissions `*`
   C. Put the role in a public subnet
   D. Disable CloudTrail so the calls are cheaper

7. Static images, global users, files change weekly. The API is a separate write path in one Region.
   A. CloudFront for the images, the API stays regional
   B. Global Accelerator for the images because it caches
   C. Snowball for each user
   D. One unencrypted EBS volume

8. Private subnets call S3, SQS, and the public package mirrors. NAT cost is dominated by S3. AZ failure must keep both S3 and the package mirrors working.
   A. Delete every NAT and add only an S3 gateway endpoint
   B. S3 gateway endpoint plus a NAT gateway in each AZ
   C. One NAT in one AZ and no endpoints
   D. VPC peering to the internet

9. A Beanstalk application has outages during rolling deploys. The team will stay on Beanstalk.
   A. Move to EKS this week
   B. Immutable or blue/green, swap after health checks
   C. SSH and yum update on the bad instances
   D. Remove the load balancer

10. Two hundred VMs, an Oracle database that can change engines later but not this quarter, 150 TB of files, a 100 Mbps link, cutover in two weeks, database downtime under five minutes.
    A. Refactor everything to Lambda first
    B. MGN for VMs, Snow plus a final DataSync delta for files, DMS CDC for Oracle
    C. Email the files
    D. A single `aws s3 cp` from a laptop

11. Findings from GuardDuty in 40 accounts are ignored. Least operational overhead.
    A. Ask each team to open the console daily
    B. Delegated admin in the security account, org auto-enable, EventBridge to the ticketing system
    C. Turn GuardDuty off
    D. Send findings only to the root email of each account with no process

12. A DR test in the second Region fails. Lambda throttles and the latest AMI is not there. The data is in Aurora Global and looks fine. What was missing?
    A. Quotas and AMI or snapshot copies in the recovery Region
    B. A larger NAT gateway in the primary Region only
    C. S3 Intelligent-Tiering
    D. An extra IAM user

13. Chargeback by `cost-center` does not appear in Cost Explorer. Tags are on the resources.
    A. Activate the cost allocation tag and use the CUR for line-item proof
    B. Buy Savings Plans and wait
    C. Enable MFA
    D. Turn on S3 versioning

14. A new checkout must survive an AZ failure, stay on SQL, and avoid connection storms from Lambda.
    A. Single-AZ RDS, no proxy
    B. Aurora or RDS Multi-AZ, RDS Proxy in front of Lambda
    C. DynamoDB with joins in the application because the stem said SQL
    D. One EC2 database with a public IP

15. The company wants a landing zone next month and has no existing one. Least operational overhead.
    A. AWS Control Tower
    B. A spreadsheet of accounts created by hand
    C. Lightsail
    D. One account and resource tags only

16. An agent may draft a fee reversal. Reversals over a threshold need a person. Account numbers must not land in logs. You are designing for SAP-C03.
    A. One admin IAM user shared by the agent
    B. Bedrock with a guardrail, a knowledge base scoped by IAM, a Step Functions approval, redacted logs
    C. The model writes straight to the general ledger with no approval
    D. Store prompts in a public bucket so they are easy to debug

17. Post-quantum signatures for artifacts that must still verify in fifteen years. Which family did AWS name for SAP-C03?
    A. ML-DSA
    B. SSE-S3
    C. A longer password
    D. MD5

18. Two companies must run a joint query without exchanging raw rows.
    A. A public S3 bucket
    B. AWS Clean Rooms
    C. Email the CSV
    D. A shared root password

19. App Mesh is in the options for a new ECS service-to-service design, next to Service Connect and VPC Lattice. The callers include a Lambda in another account.
    A. A new App Mesh
    B. VPC Lattice
    C. Security group `0.0.0.0/0`
    D. Peering every task

20. A hot partition key is `status = OPEN`. The table has unused capacity and still throttles.
    A. Raise the account's S3 quota
    B. Redesign the partition key to a high-cardinality value
    C. Turn on Multi-AZ for DynamoDB
    D. Add a NAT gateway

21. Which backup design survives an administrator in the application account who tries to delete recovery points?
    A. Snapshots in the same account with a tag that says please
    B. AWS Backup vault in another account with a vault lock
    C. A local disk on the bastion
    D. CloudWatch Logs retention of one day

22. A gray failure: health checks pass and users still cannot check out. DNS health will not flip. What do you want in the design?
    A. ARC routing controls
    B. A higher TTL
    C. Sticky sessions
    D. A larger gp2 volume

23. Windows file shares must survive the migration and stay on SMB with Active Directory.
    A. Amazon EFS
    B. Amazon FSx for Windows File Server
    C. Instance store
    D. Amazon Neptune

24. The pipeline must deploy to production accounts. Long-lived keys are forbidden.
    A. `aws_access_key_id` in the repo
    B. OIDC or a pipeline role that assumes a deploy role in each account
    C. The root key in Parameter Store as a String
    D. One IAM user whose key is in the AMI

25. A steady mixed bill of EC2, Fargate, and Lambda. Families change during the year.
    A. Compute Savings Plan
    B. A Standard RI for one `m5.large`
    C. Spot for the database
    D. Dedicated Hosts for the Lambda functions
