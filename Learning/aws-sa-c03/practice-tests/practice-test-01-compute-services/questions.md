# AWS SAA-C03 Practice Test 1: Compute Services

**Topics Covered:** EC2, Lambda, EC2 Auto Scaling  
**Number of Questions:** 65  
**Time Limit:** 130 minutes (2 minutes per question)  
**Passing Score:** 72% (47 out of 65)

---

## Instructions
- Choose the BEST answer for each question
- Some questions may have multiple correct answers where indicated
- Mark your answers and check against the answer key in `answers.md`

---

## EC2 Questions (Questions 1-30)

### Question 1
A company needs to run a high-performance computing (HPC) application that requires low network latency and high network throughput between instances. Which EC2 feature should the solutions architect recommend?

A) Spread placement group  
B) Partition placement group  
C) Cluster placement group  
D) Auto Scaling group with multiple AZs

---

### Question 2
An application requires burstable CPU performance and is expected to have periods of high and low CPU utilization. The workload is cost-sensitive and runs 24/7. Which EC2 instance type and purchasing option combination is MOST cost-effective?

A) T3 instances with On-Demand pricing  
B) M5 instances with Reserved Instances  
C) T3 instances with Reserved Instances  
D) C5 instances with Spot Instances

---

### Question 3
A solutions architect needs to ensure that EC2 instances can be quickly recovered in case of instance or Availability Zone failures. Which combination of features provides the BEST solution? (Choose TWO)

A) Use EBS snapshots for backup  
B) Configure Auto Scaling across multiple AZs  
C) Use instance store volumes for data storage  
D) Create AMIs from configured instances  
E) Use dedicated hosts

---

### Question 4
A company is migrating their on-premises SQL Server databases to AWS. They need dedicated physical servers to meet licensing requirements. Which EC2 purchasing option should they use?

A) Reserved Instances  
B) Spot Instances  
C) Dedicated Hosts  
D) Dedicated Instances

---

### Question 5
An EC2 instance running in a private subnet needs to download software updates from the internet without exposing the instance to incoming internet traffic. What is the MOST secure solution?

A) Attach an Elastic IP address to the instance  
B) Use a NAT Gateway in a public subnet  
C) Use a NAT Instance in a private subnet  
D) Configure an Internet Gateway and route table

---

### Question 6
A web application experiences predictable traffic patterns with high load during business hours (9 AM - 6 PM) on weekdays. Which EC2 instance purchasing strategy provides the BEST cost optimization?

A) Use 100% On-Demand instances  
B) Use 100% Reserved Instances  
C) Use Reserved Instances for baseline load and On-Demand for peak hours  
D) Use 100% Spot Instances

---

### Question 7
A solutions architect is designing a system where EC2 instances need to access AWS services like S3 and DynamoDB securely without storing credentials on the instances. What is the BEST approach?

A) Store IAM user credentials in the instance user data  
B) Attach an IAM role to the EC2 instances  
C) Use AWS Secrets Manager to store credentials  
D) Hard-code access keys in the application configuration

---

### Question 8
An application running on EC2 instances needs to maintain session state data. The data must persist beyond instance termination and be accessible from any instance in the Auto Scaling group. Which storage solution is MOST appropriate?

A) Instance store volumes  
B) EBS volumes attached to each instance  
C) Amazon EFS file system  
D) Amazon S3 with lifecycle policies

---

### Question 9
A company wants to launch 1000 EC2 instances simultaneously for a short-duration batch processing job. They want to minimize costs and can tolerate interruptions. What is the BEST purchasing option?

A) On-Demand Instances  
B) Reserved Instances  
C) Spot Instances  
D) Dedicated Hosts

---

### Question 10
An EC2 instance in a security group has the following outbound rules: Allow all traffic to 0.0.0.0/0. The Network ACL has default settings. The instance cannot access the internet. What is the MOST likely cause?

A) The security group is stateless and needs an inbound rule  
B) The Network ACL is blocking return traffic  
C) No Internet Gateway is attached to the VPC  
D) The route table doesn't have a NAT Gateway route

---

### Question 11
A financial services company requires EC2 instances to have predictable performance for 3 years with the option to change instance families during this period. Which Reserved Instance type should they purchase?

A) Standard Reserved Instances  
B) Convertible Reserved Instances  
C) Scheduled Reserved Instances  
D) On-Demand Capacity Reservations

---

### Question 12
An application running on EC2 needs 32 GB of RAM and requires high memory bandwidth. Which instance family is MOST suitable?

A) Compute Optimized (C5)  
B) General Purpose (M5)  
C) Memory Optimized (R5)  
D) Storage Optimized (I3)

---

### Question 13
A company wants to ensure that their EC2 instances in a production environment are distributed across different physical hardware to reduce the impact of hardware failures. What should they configure?

A) Cluster placement group  
B) Spread placement group  
C) Multiple Availability Zones  
D) Partition placement group

---

### Question 14
An EC2 instance is serving as a bastion host to provide SSH access to instances in private subnets. How should the security group be configured for the bastion host?

A) Allow SSH (port 22) from 0.0.0.0/0 inbound, allow all outbound  
B) Allow SSH (port 22) from company IP range inbound, allow SSH to private subnet outbound  
C) Allow all inbound, allow SSH outbound to private subnet  
D) Allow RDP (port 3389) inbound, allow SSH outbound

---

### Question 15
A company runs a legacy application that requires specific Intel processor features not available in all EC2 instance types. Which EC2 feature allows them to specify CPU options?

A) Enhanced networking  
B) CPU optimization  
C) Instance metadata  
D) Dedicated hosts with host affinity

---

### Question 16
An EC2 instance needs to scale vertically (change instance type) with minimal downtime. What is the BEST approach?

A) Terminate and launch a new instance with larger type  
B) Stop the instance, change instance type, start the instance  
C) Use Auto Scaling to launch larger instances  
D) Create an AMI and launch from a new instance type

---

### Question 17
A company wants to run EC2 instances for a big data processing job that will take 2-3 months to complete and must not be interrupted. They want maximum cost savings. What purchasing option should they use?

A) Spot Instances with Spot blocks  
B) On-Demand Instances  
C) Reserved Instances with 1-year term  
D) Savings Plans

---

### Question 18
An application requires GPU capabilities for machine learning inference with moderate throughput requirements. Which EC2 instance type is MOST cost-effective?

A) P4 instances  
B) P3 instances  
C) G4dn instances  
D) F1 instances

---

### Question 19
A solutions architect needs to monitor EC2 instance metrics beyond the basic CloudWatch metrics (CPU, network, disk). What is required to collect memory utilization and disk space metrics?

A) Enable detailed monitoring in EC2 console  
B) Install CloudWatch agent on instances  
C) Enable Enhanced Monitoring  
D) Use AWS Systems Manager

---

### Question 20
A company has a fleet of 100 EC2 instances that need to be patched monthly. What is the MOST efficient way to manage this?

A) Manually SSH into each instance and apply patches  
B) Use AWS Systems Manager Session Manager and Patch Manager  
C) Create a Lambda function to SSH and patch instances  
D) Use EC2 User Data to auto-patch on boot

---

### Question 21
An EC2 instance stopped unexpectedly and the status check shows "Instance Status Check Failed". What is the MOST likely cause?

A) AWS hardware failure  
B) Guest operating system issue  
C) Network connectivity problem  
D) Security group misconfiguration

---

### Question 22
A company wants to run EC2 instances that can access the internet but should not be directly accessible from the internet. Which subnet configuration is correct?

A) Place instances in public subnet with security group restrictions  
B) Place instances in private subnet with NAT Gateway in public subnet  
C) Place instances in private subnet with Internet Gateway  
D) Place instances in public subnet without Elastic IP

---

### Question 23
An application running on EC2 needs access to frequently changing configuration data stored centrally. What is the BEST solution that provides minimal latency and automatic updates?

A) Store configuration in S3 and poll every minute  
B) Use EC2 User Data to load configuration  
C) Use AWS Systems Manager Parameter Store with application integration  
D) Store configuration in DynamoDB and query on startup

---

### Question 24
A distributed database application requires multiple EC2 instances to be spread across different racks but within the same Availability Zone. Which placement strategy should be used?

A) Cluster placement group  
B) Partition placement group  
C) Spread placement group  
D) No placement group needed

---

### Question 25
A company needs to ensure that EC2 instance metadata service (IMDS) v1 is disabled for security compliance. What should they configure?

A) Use security groups to block metadata access  
B) Enable IMDSv2 only and require token authentication  
C) Disable metadata service in VPC settings  
D) Use IAM policies to restrict metadata access

---

### Question 26
An EC2 instance is running out of CPU credits frequently. What actions can the solutions architect take to resolve this? (Choose TWO)

A) Upgrade to an unlimited mode T3 instance  
B) Change to a larger T3 instance type  
C) Switch to an M5 instance type  
D) Enable detailed monitoring  
E) Attach additional EBS volumes

---

### Question 27
A company wants to migrate existing VMware virtual machines to AWS with minimal changes. Which service should they use?

A) AWS Application Discovery Service  
B) AWS VM Import/Export  
C) AWS Server Migration Service  
D) AWS Database Migration Service

---

### Question 28
An application requires 16 instances running continuously across 2 Availability Zones for 3 years. What is the MOST cost-effective solution?

A) 16 On-Demand instances  
B) 16 Standard Reserved Instances  
C) 8 Reserved Instances + 8 On-Demand instances  
D) 16 Spot Instances

---

### Question 29
An EC2 instance needs to retrieve its own instance ID, public IP address, and IAM role name. Where can this information be obtained?

A) EC2 User Data  
B) EC2 Instance Metadata Service  
C) CloudWatch Logs  
D) AWS Config

---

### Question 30
A solutions architect needs to run a fleet of EC2 instances that require EBS-optimized performance. Which statement is true about EBS optimization?

A) All instance types support EBS optimization by default  
B) EBS optimization requires additional hourly charges for all instance types  
C) Current generation instance types have EBS optimization enabled by default  
D) EBS optimization is only available for storage-optimized instances

---

## Lambda Questions (Questions 31-47)

### Question 31
A Lambda function processes messages from an SQS queue. During peak load, the function times out frequently. What is the BEST solution to improve performance?

A) Increase the Lambda function timeout value  
B) Increase Lambda memory allocation (which also increases CPU)  
C) Use Lambda reserved concurrency  
D) Switch to Lambda with provisioned concurrency

---

### Question 32
A company needs to run a Lambda function that processes large files (5 GB each). What is the MOST appropriate solution?

A) Increase Lambda ephemeral storage to 10 GB  
B) Process files directly from S3 using streaming  
C) Split files and process in parallel Lambda invocations  
D) Use EC2 instead as Lambda cannot handle files this large

---

### Question 33
A Lambda function needs to access resources in a VPC, including an RDS database in a private subnet. What must be configured?

A) Attach an Elastic IP to the Lambda function  
B) Configure Lambda with VPC settings (subnet IDs and security groups)  
C) Use VPC peering to connect Lambda to the VPC  
D) Place the Lambda function in a public subnet

---

### Question 34
An application uses Lambda to process real-time streaming data from Kinesis. The processing must maintain order for each partition key. How should the Lambda function be configured?

A) Use SQS FIFO queue as intermediary  
B) Set batch size to 1  
C) Enable ParallelizationFactor  
D) Configure Kinesis stream to trigger Lambda with batch window

---

### Question 35
A Lambda function's execution time varies between 100ms and 5 minutes depending on input data. What is the maximum configurable timeout for Lambda?

A) 5 minutes  
B) 10 minutes  
C) 15 minutes  
D) 30 minutes

---

### Question 36
A solutions architect needs to reduce cold start latency for a Lambda function that handles API requests. What is the MOST effective solution?

A) Increase memory allocation  
B) Use Lambda provisioned concurrency  
C) Enable Lambda reserved concurrency  
D) Use Lambda layers to reduce deployment package size

---

### Question 37
A Lambda function needs to store temporary data during execution. The data should be accessible across multiple invocations if the container is reused. Where should this data be stored?

A) /tmp directory (ephemeral storage)  
B) Environment variables  
C) Lambda layers  
D) S3 bucket

---

### Question 38
A company wants to automatically invoke a Lambda function whenever a new object is uploaded to an S3 bucket. What is the BEST way to configure this?

A) Create an S3 event notification to trigger Lambda  
B) Use CloudWatch Events to poll S3 for new objects  
C) Use AWS Step Functions to orchestrate  
D) Configure Lambda to poll S3 every minute

---

### Question 39
A Lambda function needs to access AWS services like DynamoDB and S3. What is the MOST secure way to grant permissions?

A) Store access keys in environment variables  
B) Use an IAM execution role attached to the Lambda function  
C) Hard-code credentials in the function code  
D) Use AWS Secrets Manager to retrieve credentials

---

### Question 40
An application uses Lambda to process asynchronous events. Failed invocations should be retried and then sent to a dead letter queue for further analysis. What should be configured?

A) Lambda destination for asynchronous invocations  
B) SQS FIFO queue for ordering  
C) Step Functions for retry logic  
D) CloudWatch Events rule for failed executions

---

### Question 41
A Lambda function requires access to a large machine learning model (500 MB) during execution. What is the BEST way to optimize this?

A) Include model in deployment package  
B) Store model in /tmp and download on each cold start  
C) Use Lambda layer for the model  
D) Store model in EFS and mount to Lambda

---

### Question 42
A company needs to limit the number of concurrent executions for a specific Lambda function to protect downstream resources. What should they configure?

A) Provisioned concurrency  
B) Reserved concurrency  
C) Lambda timeout settings  
D) API Gateway throttling

---

### Question 43
A Lambda function processing S3 events fails intermittently with "Task timed out" errors. Investigation shows network latency to external APIs. What should be optimized FIRST?

A) Increase Lambda timeout  
B) Increase Lambda memory  
C) Implement exponential backoff for API calls  
D) Switch to synchronous invocation

---

### Question 44
A solutions architect needs to share common code and dependencies across multiple Lambda functions. What is the BEST approach?

A) Copy code to each function deployment package  
B) Use Lambda layers  
C) Store code in S3 and download at runtime  
D) Use Step Functions for shared logic

---

### Question 45
A Lambda function is invoked by API Gateway and needs to return results within 30 seconds. The processing takes 2 minutes. What is the BEST solution?

A) Increase API Gateway timeout to 2 minutes  
B) Use asynchronous invocation and return immediately with a job ID  
C) Split processing across multiple Lambda functions  
D) Increase Lambda timeout to 2 minutes (API Gateway max is 29 seconds)

---

### Question 46
A Lambda function environment variable contains sensitive database credentials. How should this be secured?

A) Use AWS Secrets Manager and retrieve at runtime  
B) Encrypt environment variables using AWS KMS  
C) Store in Parameter Store as SecureString  
D) All of the above are valid options

---

### Question 47
A Lambda function needs to be triggered on a schedule to run every 15 minutes. What service should be used?

A) CloudWatch Events (EventBridge) rule with schedule expression  
B) AWS Batch  
C) EC2 Auto Scaling schedule  
D) S3 lifecycle policies

---

## EC2 Auto Scaling Questions (Questions 48-65)

### Question 48
An Auto Scaling group is configured with desired capacity of 4, minimum of 2, and maximum of 10. A scaling policy adds 2 instances but the group only launches 1 instance. What is the MOST likely cause?

A) Insufficient capacity in the Availability Zones  
B) Maximum capacity reached at 5 instances  
C) Cooldown period preventing additional scaling  
D) Launch template has errors

---

### Question 49
A web application requires instances to warm up for 5 minutes before receiving traffic from the load balancer. How should this be configured in Auto Scaling?

A) Set cooldown period to 300 seconds  
B) Set health check grace period to 300 seconds  
C) Configure target group deregistration delay  
D) Use lifecycle hooks with 300 second timeout

---

### Question 50
An Auto Scaling group should scale based on average CPU utilization across all instances staying below 60%. What type of scaling policy is MOST appropriate?

A) Simple scaling policy  
B) Step scaling policy  
C) Target tracking scaling policy  
D) Scheduled scaling policy

---

### Question 51
A company wants their Auto Scaling group to distribute instances evenly across 3 Availability Zones. Instance 1 in AZ-A fails. What will Auto Scaling do?

A) Launch new instance in any AZ with capacity  
B) Launch new instance in AZ-A to maintain balance  
C) Wait for manual intervention  
D) Redistribute existing instances across AZs

---

### Question 52
An Auto Scaling group uses target tracking policy to maintain average CPU at 50%. During scale-in, which instance will be terminated FIRST (default termination policy)?

A) Instance with oldest launch configuration  
B) Instance with highest CPU utilization  
C) Instance closest to next billing hour  
D) Random instance

---

### Question 53
A solutions architect needs to perform maintenance on specific instances in an Auto Scaling group without Auto Scaling terminating them. What should they do?

A) Set instances to standby state  
B) Detach instances from Auto Scaling group  
C) Suspend Auto Scaling processes  
D) Decrease minimum capacity temporarily

---

### Question 54
An application requires exactly 10 instances running at all times, with no scaling needed. How should Auto Scaling be configured?

A) Min=5, Desired=10, Max=15  
B) Min=10, Desired=10, Max=10  
C) Min=0, Desired=10, Max=10  
D) Don't use Auto Scaling, launch instances manually

---

### Question 55
An Auto Scaling group should scale out aggressively during traffic spikes but scale in gradually to avoid service disruption. What configuration achieves this?

A) Use different cooldown periods for scale-out vs scale-in  
B) Use step scaling with different adjustments  
C) Use target tracking with scale-in disabled  
D) Configure lifecycle hooks for gradual termination

---

### Question 56
A company uses Spot Instances in their Auto Scaling group to reduce costs. What should they configure to handle Spot interruptions gracefully?

A) Set health check grace period to 2 hours  
B) Enable instance protection  
C) Use mixed instances policy with On-Demand base capacity  
D) Disable health checks

---

### Question 57
An Auto Scaling group launches instances based on a launch template. A new version of the launch template is created with updated AMI. What happens to existing instances?

A) Existing instances are automatically replaced  
B) Existing instances continue running unchanged  
C) Auto Scaling group fails and stops launching instances  
D) Existing instances are updated in-place

---

### Question 58
A solutions architect needs to run a batch job daily at 2 AM that requires 20 instances for 3 hours. What is the MOST cost-effective Auto Scaling strategy?

A) Keep 20 instances running 24/7  
B) Use scheduled scaling to scale out at 2 AM and scale in at 5 AM  
C) Use target tracking based on queue depth  
D) Manually launch instances before batch job

---

### Question 59
An Auto Scaling group spans 3 AZs with instances: AZ-A(4), AZ-B(4), AZ-C(3). One instance in AZ-B fails health check. Where will Auto Scaling launch the replacement?

A) AZ-A  
B) AZ-B  
C) AZ-C  
D) Random AZ

---

### Question 60
A company wants to execute custom scripts when instances launch and before instances terminate in an Auto Scaling group. What feature should they use?

A) EC2 User Data  
B) Auto Scaling lifecycle hooks  
C) CloudWatch Events  
D) Lambda functions

---

### Question 61
An Auto Scaling group is associated with an Application Load Balancer. The health check type should be configured as:

A) EC2 to check instance status  
B) ELB to check target health  
C) Both EC2 and ELB  
D) Custom health check script

---

### Question 62
A web application requires minimum 5 instances during business hours (8 AM - 8 PM) and 2 instances at other times. What is the BEST scaling approach?

A) Use two scheduled scaling actions  
B) Use target tracking scaling  
C) Use step scaling policies  
D) Manually adjust capacity twice daily

---

### Question 63
An Auto Scaling group cannot launch instances and events show "Failed to launch instances". What could be the cause? (Choose TWO)

A) Launch template specifies unavailable instance type  
B) Cooldown period is active  
C) Key pair specified in launch template was deleted  
D) Health check grace period too short  
E) Maximum capacity reached

---

### Question 64
A company wants their Auto Scaling group to prioritize On-Demand instances for the first 4 instances, then use Spot instances for additional capacity. What should they configure?

A) Spot Fleet with mixed allocation  
B) Auto Scaling mixed instances policy with On-Demand base capacity of 4  
C) Two separate Auto Scaling groups  
D) Reserved Instances for first 4, Spot for rest

---

### Question 65
An Auto Scaling group uses custom CloudWatch metrics (application-level queue depth) for scaling decisions. The metric should be:

A) Published to CloudWatch and used in target tracking policy  
B) Configured in the launch template  
C) Sent via SNS to trigger scaling  
D) Stored in DynamoDB for Auto Scaling to query

---

## End of Practice Test 1

**Next Steps:**
1. Review your answers
2. Check the answer key in `answers.md`
3. Study explanations for questions you missed
4. Review relevant AWS documentation for weak areas

**Scoring Guide:**
- 47-52 correct (72-80%): Pass - Review missed topics
- 53-58 correct (81-89%): Good - Minor review needed
- 59-65 correct (90-100%): Excellent - Ready for exam

