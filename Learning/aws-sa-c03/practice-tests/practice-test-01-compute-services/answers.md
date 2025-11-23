# AWS SAA-C03 Practice Test 1: Compute Services - ANSWER KEY

**Topics Covered:** EC2, Lambda, EC2 Auto Scaling  
**Total Questions:** 65

---

## Answer Key Quick Reference

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|----|--------|----|--------|----|--------|----|--------|
| 1  | C      | 18 | C      | 35 | C      | 52 | A      |
| 2  | C      | 19 | B      | 36 | B      | 53 | A      |
| 3  | B, D   | 20 | B      | 37 | A      | 54 | B      |
| 4  | C      | 21 | B      | 38 | A      | 55 | B      |
| 5  | B      | 22 | B      | 39 | B      | 56 | C      |
| 6  | C      | 23 | C      | 40 | A      | 57 | B      |
| 7  | B      | 24 | B      | 41 | D      | 58 | B      |
| 8  | C      | 25 | B      | 42 | B      | 59 | C      |
| 9  | C      | 26 | A, C   | 43 | C      | 60 | B      |
| 10 | C      | 27 | C      | 44 | B      | 61 | B      |
| 11 | B      | 28 | B      | 45 | B      | 62 | A      |
| 12 | C      | 29 | B      | 46 | D      | 63 | A, C   |
| 13 | B      | 30 | C      | 47 | A      | 64 | B      |
| 14 | B      | 31 | B      | 48 | B      | 65 | A      |
| 15 | D      | 32 | B      | 49 | B      |    |        |
| 16 | B      | 33 | B      | 50 | C      |    |        |
| 17 | C      | 34 | B      | 51 | B      |    |        |

---

## Detailed Explanations

### EC2 Questions (1-30)

#### Question 1: Answer C - Cluster placement group
**Explanation:** Cluster placement groups place instances close together within a single AZ, providing low latency (10 Gbps) and high network throughput ideal for HPC applications.

**Why other options are incorrect:**
- A: Spread placement groups maximize availability but don't optimize for low latency
- B: Partition placement groups are for distributed workloads like Hadoop, not HPC
- D: Auto Scaling groups focus on availability, not low-latency networking

**Key Concept:** Cluster = Low latency HPC workloads in single AZ

---

#### Question 2: Answer C - T3 instances with Reserved Instances
**Explanation:** T3 instances provide burstable performance perfect for variable workloads, and Reserved Instances offer up to 72% cost savings for 24/7 workloads.

**Why other options are incorrect:**
- A: On-Demand is most expensive for continuous workloads
- B: M5 instances don't provide burstable performance and are more expensive
- D: Spot Instances can be interrupted, unsuitable for 24/7 requirements

**Key Concept:** T3 + Reserved Instances = Burstable + Cost-effective for continuous workloads

---

#### Question 3: Answer B, D - Auto Scaling across multiple AZs AND Create AMIs
**Explanation:** Auto Scaling across AZs ensures automatic replacement of failed instances. AMIs enable quick instance recreation with configured software.

**Why other options are incorrect:**
- A: While useful, snapshots alone don't provide automatic recovery
- C: Instance store is ephemeral and lost on termination
- E: Dedicated hosts don't improve recovery capabilities

**Key Concept:** High availability = Auto Scaling + Multi-AZ + AMIs

---

#### Question 4: Answer C - Dedicated Hosts
**Explanation:** Dedicated Hosts provide physical servers with visibility into sockets and cores, required for certain software licensing (like SQL Server per-socket licensing).

**Why other options are incorrect:**
- A: Reserved Instances provide cost savings but not dedicated hardware
- B: Spot Instances don't provide dedicated hardware
- D: Dedicated Instances provide isolation but don't allow socket/core visibility for licensing

**Key Concept:** Licensing requirements = Dedicated Hosts

---

#### Question 5: Answer B - NAT Gateway in public subnet
**Explanation:** NAT Gateway allows instances in private subnets to initiate outbound connections while preventing inbound connections from the internet.

**Why other options are incorrect:**
- A: Elastic IP exposes instance to incoming internet traffic
- C: NAT Instance in private subnet cannot access internet
- D: Internet Gateway alone doesn't prevent incoming traffic

**Key Concept:** Private subnet outbound access = NAT Gateway in public subnet

---

#### Question 6: Answer C - Reserved Instances for baseline + On-Demand for peaks
**Explanation:** Use Reserved Instances (up to 72% savings) for predictable baseline load and On-Demand for variable peak hours.

**Why other options are incorrect:**
- A: 100% On-Demand is most expensive
- B: Over-provisioning with Reserved Instances wastes capacity
- D: Spot Instances can be interrupted, unsuitable for production web apps

**Key Concept:** Predictable patterns = Reserved baseline + On-Demand peaks

---

#### Question 7: Answer B - Attach IAM role to EC2 instances
**Explanation:** IAM roles provide temporary credentials automatically rotated by AWS, eliminating the need to manage long-term credentials.

**Why other options are incorrect:**
- A: Storing credentials in user data is insecure and visible in console
- C: Secrets Manager adds unnecessary complexity when IAM roles suffice
- D: Hard-coding credentials is a security risk

**Key Concept:** EC2 authentication = IAM roles (never store credentials)

---

#### Question 8: Answer C - Amazon EFS file system
**Explanation:** EFS provides shared file storage accessible from multiple instances simultaneously, perfect for shared session state.

**Why other options are incorrect:**
- A: Instance store is ephemeral and not shared
- B: EBS volumes can't be shared across instances (except io2 multi-attach with limitations)
- D: S3 introduces latency and is object storage, not suitable for frequent session updates

**Key Concept:** Shared state across instances = EFS

---

#### Question 9: Answer C - Spot Instances
**Explanation:** Spot Instances offer up to 90% cost savings and are ideal for fault-tolerant, flexible workloads like batch processing.

**Why other options are incorrect:**
- A: On-Demand is most expensive for large-scale workloads
- B: Reserved Instances require commitment and aren't ideal for short-duration jobs
- D: Dedicated Hosts are expensive and unnecessary for batch jobs

**Key Concept:** Interruptible batch processing = Spot Instances

---

#### Question 10: Answer C - No Internet Gateway attached to VPC
**Explanation:** For instances to access the internet, the VPC must have an Internet Gateway attached and proper route table configuration.

**Why other options are incorrect:**
- A: Security groups are stateful; return traffic is automatically allowed
- B: Default NACLs allow all traffic
- D: NAT Gateway is for private subnet instances, not public subnet

**Key Concept:** Internet access = Internet Gateway + route table + security group

---

#### Question 11: Answer B - Convertible Reserved Instances
**Explanation:** Convertible RIs allow changing instance families, operating systems, and tenancy during the term, providing flexibility.

**Why other options are incorrect:**
- A: Standard RIs don't allow instance family changes
- C: Scheduled RIs are for predictable recurring schedules
- D: Capacity Reservations don't provide RI discounts

**Key Concept:** Flexibility with commitment = Convertible Reserved Instances

---

#### Question 12: Answer C - Memory Optimized (R5)
**Explanation:** R5 instances provide high memory-to-CPU ratios (32 GB+ per vCPU) and high memory bandwidth for memory-intensive applications.

**Why other options are incorrect:**
- A: C5 is compute-optimized, not memory-optimized
- B: M5 provides balanced resources, not optimized for high memory
- D: I3 is storage-optimized

**Key Concept:** High memory requirements = Memory Optimized (R5, X1, etc.)

---

#### Question 13: Answer B - Spread placement group
**Explanation:** Spread placement groups place instances on distinct hardware, reducing correlated failures (max 7 instances per AZ per group).

**Why other options are incorrect:**
- A: Cluster groups place instances close together
- C: Multiple AZs provide different level of isolation (entire AZ failure protection)
- D: Partition groups separate groups of instances, not individual instances

**Key Concept:** Individual instance hardware isolation = Spread placement group

---

#### Question 14: Answer B - SSH from company IP, SSH to private subnet outbound
**Explanation:** Bastion hosts should restrict inbound access to known IPs and allow SSH outbound to private instances.

**Why other options are incorrect:**
- A: Allowing SSH from 0.0.0.0/0 is insecure
- C: Allowing all inbound is a security risk
- D: RDP is for Windows, not Linux SSH

**Key Concept:** Bastion host = Restricted inbound + SSH outbound to private subnets

---

#### Question 15: Answer D - Dedicated hosts with host affinity
**Explanation:** Dedicated Hosts allow instance placement on specific physical servers with particular CPU features.

**Why other options are incorrect:**
- A: Enhanced networking improves network performance, not CPU features
- B: No such feature exists
- C: Instance metadata provides instance information, not CPU control

**Key Concept:** Specific hardware requirements = Dedicated Hosts

---

#### Question 16: Answer B - Stop, change instance type, start
**Explanation:** Stopping an EBS-backed instance, changing type, and restarting minimizes downtime (typically 2-5 minutes).

**Why other options are incorrect:**
- A: Terminating loses instance configuration
- C: Auto Scaling launches new instances but doesn't change existing ones
- D: AMI approach takes longer than stop/change/start

**Key Concept:** Vertical scaling = Stop > Change type > Start

---

#### Question 17: Answer C - Reserved Instances with 1-year term
**Explanation:** For uninterruptible workloads running 2-3 months, 1-year No Upfront RIs provide maximum savings without upfront cost.

**Why other options are incorrect:**
- A: Spot Instances can be interrupted
- B: On-Demand is most expensive
- D: Savings Plans might work but RIs provide more discount for specific workloads

**Key Concept:** Continuous multi-month workload = Reserved Instances

---

#### Question 18: Answer C - G4dn instances
**Explanation:** G4dn instances provide NVIDIA T4 GPUs optimized for ML inference at lower cost than P-series training instances.

**Why other options are incorrect:**
- A: P4 is for high-performance training (expensive)
- B: P3 is for training workloads (expensive)
- D: F1 uses FPGAs, not GPUs

**Key Concept:** ML inference = G4dn, ML training = P3/P4

---

#### Question 19: Answer B - Install CloudWatch agent
**Explanation:** CloudWatch agent must be installed on instances to collect guest OS metrics like memory and disk utilization.

**Why other options are incorrect:**
- A: Detailed monitoring only provides more frequent basic metrics (CPU, network)
- C: Enhanced Monitoring is for RDS, not EC2
- D: Systems Manager doesn't automatically send metrics to CloudWatch

**Key Concept:** Guest OS metrics = CloudWatch agent required

---

#### Question 20: Answer B - AWS Systems Manager Session Manager and Patch Manager
**Explanation:** Systems Manager provides centralized patch management without SSH key management, with automated compliance reporting.

**Why other options are incorrect:**
- A: Manual patching doesn't scale
- C: Lambda can't SSH directly to instances
- D: User Data only runs at instance launch

**Key Concept:** Patch management at scale = Systems Manager Patch Manager

---

#### Question 21: Answer B - Guest operating system issue
**Explanation:** Instance Status Check failures indicate problems with the guest OS, software, or networking within the instance.

**Why other options are incorrect:**
- A: AWS hardware issues show as System Status Check failures
- C: Network issues show differently in status checks
- D: Security group issues don't cause status check failures

**Key Concept:** Instance status check = Guest OS problems

---

#### Question 22: Answer B - Private subnet with NAT Gateway in public subnet
**Explanation:** Private subnet prevents direct inbound access while NAT Gateway enables outbound internet connectivity.

**Why other options are incorrect:**
- A: Public subnet instances can receive inbound traffic
- C: Internet Gateway doesn't provide NAT functionality
- D: Public subnet without EIP still allows inbound access

**Key Concept:** Outbound-only internet = Private subnet + NAT Gateway

---

#### Question 23: Answer C - Systems Manager Parameter Store with application integration
**Explanation:** Parameter Store provides centralized configuration with SDK integration, versioning, and low latency access.

**Why other options are incorrect:**
- A: S3 polling introduces unnecessary latency
- B: User Data only loads at launch
- D: DynamoDB adds complexity and cost

**Key Concept:** Dynamic configuration = Parameter Store

---

#### Question 24: Answer B - Partition placement group
**Explanation:** Partition placement groups spread instances across logical partitions (different racks) within an AZ, ideal for distributed databases.

**Why other options are incorrect:**
- A: Cluster groups don't provide rack isolation
- C: Spread groups limit to 7 instances per AZ
- D: Without placement group, no guaranteed rack distribution

**Key Concept:** Distributed systems in same AZ = Partition placement group

---

#### Question 25: Answer B - Enable IMDSv2 only with token requirement
**Explanation:** IMDSv2 requires session tokens, preventing SSRF attacks and meeting compliance requirements.

**Why other options are incorrect:**
- A: Security groups can't block IMDS (it's local)
- C: Can't disable metadata service at VPC level
- D: IAM policies don't control IMDS access

**Key Concept:** IMDS security = IMDSv2 token-based authentication

---

#### Question 26: Answer A, C - Unlimited mode T3 OR switch to M5
**Explanation:** T3 unlimited allows sustained high CPU usage with additional charges, or M5 provides consistent baseline performance.

**Why other options are incorrect:**
- B: Larger T3 has more credits but same baseline percentage
- D: Detailed monitoring doesn't add CPU credits
- E: EBS volumes don't affect CPU performance

**Key Concept:** CPU credit exhaustion = Unlimited mode or different instance family

---

#### Question 27: Answer C - AWS Server Migration Service
**Explanation:** AWS SMS (now AWS MGN) automates migration of VMware VMs to AWS with minimal downtime.

**Why other options are incorrect:**
- A: Discovery Service identifies on-premises resources but doesn't migrate
- B: VM Import/Export is manual and less efficient
- D: DMS is for database migration

**Key Concept:** VMware to AWS = Server Migration Service (SMS/MGN)

---

#### Question 28: Answer B - 16 Standard Reserved Instances
**Explanation:** Standard RIs provide maximum discount (up to 72%) for continuous, predictable workloads.

**Why other options are incorrect:**
- A: On-Demand is most expensive
- C: Splitting provides no benefit for continuous usage
- D: Spot Instances can be interrupted

**Key Concept:** Continuous predictable workload = Standard Reserved Instances

---

#### Question 29: Answer B - EC2 Instance Metadata Service
**Explanation:** Instance metadata available at http://169.254.169.254/latest/meta-data/ provides instance attributes and IAM role credentials.

**Why other options are incorrect:**
- A: User Data is for startup scripts
- C: CloudWatch Logs stores application logs
- D: AWS Config tracks resource configuration

**Key Concept:** Instance self-discovery = Instance Metadata Service

---

#### Question 30: Answer C - Current generation instances have EBS optimization by default
**Explanation:** Modern EC2 instance types include EBS optimization with dedicated bandwidth at no additional charge.

**Why other options are incorrect:**
- A: Some older instance types don't support optimization
- B: Current generation instances include it free
- D: All instance types can benefit from EBS optimization

**Key Concept:** EBS optimization = Default on current-generation instances

---

### Lambda Questions (31-47)

#### Question 31: Answer B - Increase Lambda memory allocation
**Explanation:** Lambda memory allocation proportionally increases CPU power. More memory = more CPU = faster processing.

**Why other options are incorrect:**
- A: Increasing timeout doesn't improve performance
- C: Reserved concurrency limits executions, doesn't improve performance
- D: Provisioned concurrency reduces cold starts but not execution time

**Key Concept:** Lambda performance = Increase memory (includes CPU)

---

#### Question 32: Answer B - Process files directly from S3 using streaming
**Explanation:** Lambda can stream large files from S3 without loading entire file into memory, working within Lambda limits.

**Why other options are incorrect:**
- A: Lambda max ephemeral storage is 10 GB but loading 5 GB files is inefficient
- C: Splitting might work but streaming is more efficient
- D: Lambda can handle large files with proper streaming

**Key Concept:** Large files in Lambda = S3 streaming

---

#### Question 33: Answer B - Configure Lambda with VPC settings
**Explanation:** Lambda requires VPC configuration (subnets and security groups) to access VPC resources like RDS.

**Why other options are incorrect:**
- A: Lambda doesn't support Elastic IPs
- C: VPC peering not needed; Lambda can be configured for VPC
- D: Lambda should be in private subnets to access RDS

**Key Concept:** Lambda VPC access = VPC configuration in Lambda settings

---

#### Question 34: Answer B - Set batch size to 1
**Explanation:** Processing one record at a time ensures order is maintained per partition key in Kinesis.

**Why other options are incorrect:**
- A: SQS adds unnecessary complexity
- C: ParallelizationFactor processes multiple batches in parallel, breaking order
- D: Batch window doesn't ensure ordering

**Key Concept:** Kinesis ordering = Batch size 1 or process sequentially

---

#### Question 35: Answer C - 15 minutes
**Explanation:** Lambda maximum timeout is 15 minutes (900 seconds).

**Why other options are incorrect:**
- A, B, D: Maximum is 15 minutes

**Key Concept:** Lambda max timeout = 15 minutes

---

#### Question 36: Answer B - Use Lambda provisioned concurrency
**Explanation:** Provisioned concurrency keeps functions initialized and warm, eliminating cold starts.

**Why other options are incorrect:**
- A: More memory helps but doesn't eliminate cold starts
- C: Reserved concurrency limits executions, doesn't prevent cold starts
- D: Layers help deployment size but don't eliminate cold starts significantly

**Key Concept:** Eliminate cold starts = Provisioned concurrency

---

#### Question 37: Answer A - /tmp directory (ephemeral storage)
**Explanation:** /tmp directory persists across invocations within the same container, providing temporary caching (up to 10 GB).

**Why other options are incorrect:**
- B: Environment variables are read-only and not for temporary data
- C: Layers are for shared code/libraries
- D: S3 introduces latency

**Key Concept:** Lambda temporary storage = /tmp directory

---

#### Question 38: Answer A - Create S3 event notification to trigger Lambda
**Explanation:** S3 event notifications provide native, real-time Lambda triggers for object events.

**Why other options are incorrect:**
- B: Polling is inefficient and delayed
- C: Step Functions adds unnecessary complexity
- D: Polling S3 is inefficient

**Key Concept:** S3 triggers = S3 event notifications

---

#### Question 39: Answer B - IAM execution role attached to Lambda
**Explanation:** Lambda execution roles provide temporary credentials with automatic rotation.

**Why other options are incorrect:**
- A: Storing credentials in environment variables is insecure
- C: Hard-coding credentials is a security risk
- D: Secrets Manager adds complexity when IAM roles suffice

**Key Concept:** Lambda permissions = Execution role

---

#### Question 40: Answer A - Lambda destination for asynchronous invocations
**Explanation:** Destinations route success/failure results to targets like SQS, SNS, Lambda, or EventBridge.

**Why other options are incorrect:**
- B: FIFO queue doesn't handle failures automatically
- C: Step Functions adds complexity
- D: CloudWatch Events can work but Destinations are purpose-built

**Key Concept:** Lambda async error handling = Destinations

---

#### Question 41: Answer D - Store model in EFS and mount to Lambda
**Explanation:** EFS can be mounted to Lambda, providing shared access to large files without including in deployment package.

**Why other options are incorrect:**
- A: Deployment package limited to 250 MB uncompressed
- B: Downloading 500 MB on each cold start is slow
- C: Lambda layers limited to 250 MB total

**Key Concept:** Large Lambda dependencies = EFS mount

---

#### Question 42: Answer B - Reserved concurrency
**Explanation:** Reserved concurrency limits maximum concurrent executions for a specific function, protecting downstream resources.

**Why other options are incorrect:**
- A: Provisioned concurrency keeps functions warm but doesn't limit
- C: Timeout controls execution time, not concurrency
- D: API Gateway throttling controls requests, not Lambda executions

**Key Concept:** Limit Lambda concurrency = Reserved concurrency

---

#### Question 43: Answer C - Implement exponential backoff for API calls
**Explanation:** Exponential backoff with retries handles intermittent API failures gracefully before optimizing infrastructure.

**Why other options are incorrect:**
- A: Timeout increase masks the problem
- B: More memory won't fix network latency
- D: Synchronous vs asynchronous doesn't fix external API issues

**Key Concept:** External API failures = Exponential backoff retry logic

---

#### Question 44: Answer B - Use Lambda layers
**Explanation:** Lambda layers allow sharing code, libraries, and dependencies across multiple functions.

**Why other options are incorrect:**
- A: Copying code creates maintenance issues
- C: Runtime downloads add latency
- D: Step Functions orchestrate workflows, don't share code

**Key Concept:** Share Lambda code = Lambda layers

---

#### Question 45: Answer B - Use asynchronous invocation with job ID
**Explanation:** API Gateway has 29-second timeout. Return immediately with job ID, process asynchronously, and provide status endpoint.

**Why other options are incorrect:**
- A: API Gateway max timeout is 29 seconds
- C: Splitting might work but async is cleaner
- D: Lambda timeout doesn't solve API Gateway timeout

**Key Concept:** Long processing in Lambda = Asynchronous pattern

---

#### Question 46: Answer D - All options are valid
**Explanation:** Secrets Manager, KMS-encrypted environment variables, and Parameter Store SecureString are all valid security approaches.

**Why other options are incorrect:**
- All are correct approaches depending on requirements

**Key Concept:** Lambda secrets = Multiple valid approaches

---

#### Question 47: Answer A - CloudWatch Events (EventBridge) with schedule
**Explanation:** EventBridge rules support cron and rate expressions for scheduled Lambda invocations.

**Why other options are incorrect:**
- B: Batch is for batch computing jobs, not scheduled functions
- C: Auto Scaling schedules are for EC2
- D: S3 lifecycle manages object storage, not Lambda scheduling

**Key Concept:** Scheduled Lambda = EventBridge (CloudWatch Events)

---

### EC2 Auto Scaling Questions (48-65)

#### Question 48: Answer B - Maximum capacity reached at 5 instances
**Explanation:** Desired was 4, adding 2 would make 6, but scaling is limited by maximum capacity (assumed to be 5).

**Why other options are incorrect:**
- A: Error messages would indicate capacity issues
- C: Cooldown prevents rapid scaling but wouldn't stop mid-scale
- D: Launch template errors would prevent any launches

**Key Concept:** Auto Scaling respects maximum capacity limits

---

#### Question 49: Answer B - Set health check grace period to 300 seconds
**Explanation:** Health check grace period delays health checks, allowing instances time to warm up before receiving traffic.

**Why other options are incorrect:**
- A: Cooldown period controls scaling actions, not health checks
- C: Deregistration delay is for removing instances
- D: Lifecycle hooks can work but grace period is simpler

**Key Concept:** Instance warm-up = Health check grace period

---

#### Question 50: Answer C - Target tracking scaling policy
**Explanation:** Target tracking automatically adjusts capacity to maintain specified metric (CPU at 60%).

**Why other options are incorrect:**
- A: Simple scaling is basic and deprecated
- B: Step scaling requires manual threshold configuration
- D: Scheduled scaling is for time-based patterns

**Key Concept:** Maintain metric target = Target tracking policy

---

#### Question 51: Answer B - Launch new instance in AZ-A
**Explanation:** Auto Scaling maintains balance across AZs by replacing failed instances in the same AZ.

**Why other options are incorrect:**
- A: Would create imbalance
- C: Auto Scaling automatically replaces
- D: Can't redistribute running instances

**Key Concept:** Auto Scaling maintains AZ balance

---

#### Question 52: Answer A - Instance with oldest launch configuration
**Explanation:** Default termination policy: 1) Oldest launch config/template, 2) Closest to next billing hour, 3) Random.

**Why other options are incorrect:**
- B: CPU utilization not considered in default policy
- C: Second priority after launch config age
- D: Random is last resort

**Key Concept:** Default termination = Oldest launch config first

---

#### Question 53: Answer A - Set instances to standby state
**Explanation:** Standby state temporarily removes instances from service without terminating, perfect for maintenance.

**Why other options are incorrect:**
- B: Detaching removes instances from ASG management
- C: Suspending affects all instances
- D: Decreasing capacity might terminate instances

**Key Concept:** Maintenance without termination = Standby state

---

#### Question 54: Answer B - Min=10, Desired=10, Max=10
**Explanation:** Setting all values to 10 ensures exactly 10 instances with no scaling.

**Why other options are incorrect:**
- A: Allows scaling between 5-15
- C: Might scale down to 0
- D: Auto Scaling provides automatic recovery

**Key Concept:** Fixed capacity = Min = Desired = Max

---

#### Question 55: Answer B - Use step scaling with different adjustments
**Explanation:** Step scaling allows different scaling amounts for scale-out vs scale-in actions.

**Why other options are incorrect:**
- A: Cooldown periods delay all scaling actions uniformly
- C: Disabling scale-in prevents capacity reduction
- D: Lifecycle hooks don't control scaling rate

**Key Concept:** Asymmetric scaling = Step scaling with different adjustments

---

#### Question 56: Answer C - Mixed instances policy with On-Demand base capacity
**Explanation:** On-Demand base capacity ensures minimum instances always available, with Spot for additional capacity.

**Why other options are incorrect:**
- A: Grace period doesn't handle Spot interruptions
- B: Instance protection prevents termination by ASG
- D: Health checks are essential

**Key Concept:** Spot resilience = Mixed policy with On-Demand base

---

#### Question 57: Answer B - Existing instances continue running unchanged
**Explanation:** Launch template version updates don't affect existing instances; they apply to new launches.

**Why other options are incorrect:**
- A: Must trigger instance refresh for replacement
- C: ASG continues with new version
- D: No in-place updates for launch template changes

**Key Concept:** Launch template updates apply to new instances only

---

#### Question 58: Answer B - Scheduled scaling for 2 AM - 5 AM
**Explanation:** Scheduled scaling actions scale out at 2 AM and scale in at 5 AM, minimizing costs.

**Why other options are incorrect:**
- A: Wastes 21 hours of capacity daily
- C: Queue depth might work but scheduled is more predictable
- D: Manual process doesn't scale

**Key Concept:** Predictable batch jobs = Scheduled scaling

---

#### Question 59: Answer C - AZ-C
**Explanation:** Auto Scaling rebalances to maintain equal distribution across AZs. AZ-C has fewest instances (3).

**Why other options are incorrect:**
- A, B: Would create further imbalance
- D: Auto Scaling follows rebalancing logic

**Key Concept:** Rebalancing launches in AZ with fewest instances

---

#### Question 60: Answer B - Auto Scaling lifecycle hooks
**Explanation:** Lifecycle hooks pause launch/termination, allowing custom actions via scripts or Lambda.

**Why other options are incorrect:**
- A: User Data only runs on launch, not termination
- C: CloudWatch Events can detect but hooks provide direct integration
- D: Lambda works with lifecycle hooks but hooks are the mechanism

**Key Concept:** Custom launch/termination actions = Lifecycle hooks

---

#### Question 61: Answer B - ELB health check type
**Explanation:** ELB health checks verify instances can serve traffic, more comprehensive than EC2 status checks.

**Why other options are incorrect:**
- A: EC2 checks only verify instance running, not application health
- C: Only ELB check needed (includes EC2 status implicitly)
- D: Custom checks add unnecessary complexity

**Key Concept:** ALB integration = ELB health check type

---

#### Question 62: Answer A - Two scheduled scaling actions
**Explanation:** Scheduled actions at 8 AM (min=5) and 8 PM (min=2) provide time-based capacity management.

**Why other options are incorrect:**
- B: Target tracking doesn't account for time-based patterns
- C: Step scaling requires metrics, not time
- D: Manual adjustment doesn't scale and error-prone

**Key Concept:** Time-based capacity = Scheduled scaling actions

---

#### Question 63: Answer A, C - Unavailable instance type OR deleted key pair
**Explanation:** Both unavailable instance types and deleted key pairs prevent instance launches.

**Why other options are incorrect:**
- B: Cooldown delays scaling but doesn't cause failures
- D: Short grace period doesn't prevent launches
- E: Would reach max capacity but not fail

**Key Concept:** Launch failures = Invalid launch template configuration

---

#### Question 64: Answer B - Mixed instances policy with On-Demand base capacity of 4
**Explanation:** Mixed instances policy allows specifying On-Demand base capacity with Spot for additional instances.

**Why other options are incorrect:**
- A: Spot Fleet is separate from Auto Scaling groups
- C: Two ASGs adds management complexity
- D: Reserved Instances are purchasing options, not capacity distribution

**Key Concept:** On-Demand + Spot mix = Mixed instances policy

---

#### Question 65: Answer A - Publish to CloudWatch and use in target tracking
**Explanation:** Custom metrics must be published to CloudWatch, then referenced in target tracking policy.

**Why other options are incorrect:**
- B: Launch template doesn't handle metrics
- C: SNS doesn't directly trigger scaling
- D: Auto Scaling pulls from CloudWatch, not DynamoDB

**Key Concept:** Custom metrics scaling = Publish to CloudWatch + target tracking

---

## Score Interpretation

### Passing Score: 47/65 (72%)

**90-100% (59-65 correct):** Excellent understanding. You're ready for this topic area.

**80-89% (52-58 correct):** Good knowledge. Review explanations for missed questions.

**72-79% (47-51 correct):** Passing, but needs improvement. Focus on weak areas.

**Below 72% (<47 correct):** More study needed. Review AWS documentation and retake.

---

## Study Recommendations by Score

### If you scored below 60% overall:
1. Review AWS EC2 documentation thoroughly
2. Practice launching different instance types
3. Study Auto Scaling configuration in AWS Console
4. Review Lambda fundamentals and event sources

### If you scored 60-80%:
1. Focus on questions you missed
2. Review specific topics (check your weak areas)
3. Practice scenario-based questions
4. Review AWS Well-Architected Framework

### If you scored above 80%:
1. Review any missed questions
2. Move to next practice test
3. Focus on integration scenarios
4. Practice time management

---

## Key Topics to Review Based on Common Mistakes

**If you missed EC2 questions:**
- Instance types and purchasing options
- Placement groups
- Security groups vs NACLs
- Instance metadata service

**If you missed Lambda questions:**
- Execution model and limits
- Event sources and triggers
- Performance optimization
- VPC configuration

**If you missed Auto Scaling questions:**
- Scaling policies (target tracking, step, scheduled)
- Launch templates vs launch configurations
- Lifecycle hooks
- Mixed instances policy

---

## Next Steps

1. **Review all explanations** for questions you missed
2. **Create flashcards** for concepts you found difficult
3. **Practice in AWS Console** - hands-on experience is invaluable
4. **Move to Practice Test 2** - Storage Services
5. **Time yourself** on next practice test (130 minutes)

**Good luck with your AWS SAA-C03 preparation! 🚀**
