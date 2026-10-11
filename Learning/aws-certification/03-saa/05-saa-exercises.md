# SAA-C03 exercises

Closed book. Write the service and the one constraint that made the other option wrong. Answers start at the line `## Answers`.

These sit on top of the four domain files. Do those first.

## Set A — security

1. A build server in a private subnet needs to pull from S3 and from the public internet. Security will not allow a public IP on the instance. Which two network components do you use, and which traffic uses which?
2. A company wants AWS to stop content submitted to AI services from being used to improve those services, across every member account. Which Organizations policy type?
3. An ALB serves `https://app.example.com`. The certificate is in ACM in the same Region. Users also reach the site through CloudFront. The CloudFront certificate was issued in the ALB's Region, which is `eu-central-1`. What do you change?
4. GuardDuty reports an instance calling an unusual IP. Inspector reports a CVE on the same instance. Which finding is the vulnerability, and which is the suspicious behavior?
5. A bucket must be readable by a specific role in another account, encrypted with a customer managed key, and unreachable from the public internet even if a policy is edited wrong. List the controls.

## Set B — resilience

6. RTO 30 minutes, RPO 5 minutes, SQL, lowest operational burden, Regional failure in scope. Name the database feature and the DNS feature.
7. An application writes to a local EBS volume and the team calls that "HA" because the ASG has two instances. What is wrong?
8. A Step Functions Standard workflow updates DynamoDB and then calls a shipping API that is down for an hour. What should the state machine do instead of failing the order?
9. You must prove a backup can be restored, every quarter, without an outage. Which AWS Backup feature do you run?
10. A single-AZ RDS instance, an ALB, and an ASG across two AZs. Put these failure domains in order: instance process crash, AZ loss, Region loss. Which ones does this design survive?

## Set C — performance

11. A global user base downloads a 200 MB dataset that changes monthly. The origin is S3. What do you put in front, and what TTL fits?
12. Workers poll SQS in a tight loop and the queue is usually empty. CPU is low and the SQS bill is not. What parameter do you set?
13. A reporting query joins three tables and runs every night. DynamoDB or Aurora?
14. Kinesis Data Streams consumers fall behind. Which metric do you look at, and what do you add?
15. An EFS general purpose file system serves a home directory to hundreds of instances. Latency spikes when many clients create small files at once. Which performance mode is the older escape hatch, and what do you check first in current EFS (throughput mode)?

## Set D — cost

16. A fleet runs 24x7 at a stable size. The team refreshes instance families twice a year. Which Savings Plan?
17. Logs in S3 are queried twice a year and must return in under a second when they are queried. Which Glacier class, if any?
18. A NAT gateway processes 50 TB of S3 traffic a month. What endpoint removes that processing charge?
19. Development RDS is Multi-AZ and runs all weekend. The team can tolerate a restore from a snapshot on Monday morning. What do you change?
20. A design uses inter-Region VPC peering for a nightly 2 GB copy and also has S3 CRR of 20 TB. Which transfer do you attack first?

## Set E — mixed constraints

21. "Most cost-effective" and "survive an AZ" and "SQL." Can you drop Multi-AZ to save money?
22. "Least operational overhead" and "a standard Node web app" and "the team has never run a cluster." Lambda, EKS, or Elastic Beanstalk?
23. "The application cannot be modified" and "sessions are in memory" and "they need two AZs." What ALB feature do you enable, and what outage do you still have during scale-in?
24. "Migrate 200 TB this weekend" and "the link is 100 Mbps." DataSync or Snow?
25. "Detect public snapshots" versus "prevent public snapshots." Config rule or SCP?

## Answers

1. An S3 gateway endpoint for S3. A NAT gateway in a public subnet, with the private route table pointing at it, for the public internet. No public IP on the instance.
2. An AI services opt-out policy in Organizations.
3. Issue an ACM certificate in `us-east-1` and attach that to CloudFront. Leave the ALB certificate in `eu-central-1`.
4. Inspector is the CVE. GuardDuty is the behavior.
5. Block Public Access, a bucket policy limited to that role, SSE-KMS with a key policy that allows the role, and an S3 gateway or interface path from the consumer VPC if they must stay private. A VPC endpoint policy can limit the bucket. "Unreachable from the internet" is Block Public Access plus no public endpoint, not security group rules on S3.
6. Aurora Global Database (or a cross-Region replica if you accept a promote step inside 30 minutes). Route 53 failover records with health checks after promotion. RPO of 5 minutes is inside Aurora Global's typical lag. A daily snapshot is not.
7. Each instance has its own volume. The ASG does not replicate EBS. A new instance does not see the other's disk. Put shared state in a database or in EFS or S3.
8. Retry with backoff on that state, and a Catch that parks the order or sends it to a queue. A one-hour outage should not require a new execution if the retry window covers it. Standard workflows can wait.
9. A restore test job, or an on-demand restore into an isolated vault or account. AWS Backup supports restore testing plans. A successful backup job is not a restore test.
10. It survives a process crash if the ELB health check is on and the ASG replaces the instance. It does not survive AZ loss of the database. It does not survive Region loss.
11. CloudFront. A TTL on the order of days or the remaining time until the monthly change, and invalidate or version the object key when the file changes.
12. `ReceiveMessageWaitTimeSeconds` of 20, long polling.
13. Aurora or RDS. Joins are the relational job. DynamoDB would push the join into the application and still might be wrong at that shape.
14. Iterator age. Add shards, or add consumers, and check that the consumer is not failing and retrying the same records.
15. Max I/O is the older mode. First check whether you are bursting and should move to Elastic or Provisioned throughput. Mode changes are not the first current lever.
16. Compute Savings Plan. It survives a family change. An EC2 Instance Savings Plan is cheaper and breaks when the family changes.
17. Glacier Instant Retrieval. Deep Archive and Flexible Retrieval miss the one-second requirement. Standard-IA also works and may cost more if the objects are large and truly cold. Instant Retrieval is the Glacier class that fits.
18. An S3 gateway endpoint on the route tables that currently send that traffic to the NAT.
19. Single-AZ, smaller class, and stop it over the weekend, with a snapshot before you change it. Keep the snapshot retention they need for Monday.
20. The 20 TB CRR. The 2 GB peering copy is noise.
21. No. Multi-AZ is the AZ-survival control for RDS. You can still pick a smaller instance class and gp3. You cannot meet "survive an AZ" with a single-AZ database.
22. Elastic Beanstalk, or Lambda if the app fits a short request model. EKS is the most operational burden and loses this stem. If the app is a few HTTP functions, Lambda plus API Gateway is even less to run. "Standard Node web app" often maps to Beanstalk when they want a long-running process.
23. Sticky sessions. Scale-in of the instance that holds the session still logs that user out. The durable fix needs a code change.
24. Snow. 200 TB on 100 Mbps is many weeks. 100 Mbps is about 1 TB per day in a rough classroom estimate. DataSync is the answer when the link can finish inside the window.
25. A Config rule detects. An SCP, or a permission that denies `ec2:ModifyImageAttribute` and the snapshot share API, prevents. Detection does not stop the first share.
