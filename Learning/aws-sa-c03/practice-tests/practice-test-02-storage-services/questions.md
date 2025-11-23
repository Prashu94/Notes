# AWS SAA-C03 Practice Test 2: Storage Services

**Topics Covered:** S3, EBS, EFS, FSx, Storage Gateway, AWS Backup  
**Number of Questions:** 65  
**Time Limit:** 130 minutes (2 minutes per question)  
**Passing Score:** 72% (47 out of 65)

---

## Instructions
- Choose the BEST answer for each question
- Some questions may have multiple correct answers where indicated
- Mark your answers and check against the answer key in `answers.md`

---

## S3 Questions (Questions 1-30)

### Question 1
A company stores mission-critical data in S3 that must be protected from accidental deletion. The solution must allow recovery within 30 days and comply with regulations. What is the MOST cost-effective solution?

A) Enable S3 Versioning and configure lifecycle policy to delete old versions after 30 days  
B) Enable S3 Versioning with MFA Delete and S3 Object Lock in Governance mode  
C) Create daily snapshots using AWS Backup  
D) Enable S3 Versioning and configure Cross-Region Replication

---

### Question 2
An application requires immediate access to frequently accessed files stored in S3, but access patterns are unpredictable. Some files haven't been accessed in months. What storage class provides the BEST cost optimization?

A) S3 Standard  
B) S3 Standard-IA  
C) S3 Intelligent-Tiering  
D) S3 One Zone-IA

---

### Question 3
A company needs to host a static website with custom domain `www.example.com` using S3. The website should support HTTPS. What is the MOST complete solution?

A) Enable S3 static website hosting, use Route 53 alias record  
B) Enable S3 static website hosting, use CloudFront with ACM certificate, Route 53  
C) Use EC2 instance to serve static content  
D) Enable S3 static website hosting with S3 bucket policy for HTTPS

---

### Question 4
An S3 bucket receives 5,000 PUT requests per second with keys that start with timestamps `2024-01-15-HH-MM-SS-`. Performance is degrading. What should be done to improve performance?

A) Use S3 Transfer Acceleration  
B) Add random prefix to keys to distribute across partitions  
C) Enable S3 Cross-Region Replication  
D) Upgrade to S3 Express One Zone

---

### Question 5
A solutions architect needs to ensure that objects in an S3 bucket are automatically deleted 90 days after creation, but objects with "archive" tag should be transitioned to Glacier instead. How should this be configured?

A) Create single lifecycle rule with two transitions  
B) Create two separate lifecycle rules with tag filters  
C) Use S3 Batch Operations to manually manage objects  
D) Create Lambda function triggered by S3 events

---

### Question 6
A company stores sensitive financial data in S3 and must ensure encryption at rest, in transit, and full audit trail of all access. Which combination meets these requirements? (Choose TWO)

A) Enable S3 default encryption with SSE-S3  
B) Enable S3 default encryption with SSE-KMS  
C) Enable S3 Access Logging  
D) Enable AWS CloudTrail data events for S3  
E) Use S3 Transfer Acceleration

---

### Question 7
An application uploads 10 GB video files to S3. Uploads frequently fail due to network interruptions. What feature should be implemented to improve upload reliability?

A) S3 Transfer Acceleration  
B) S3 Multipart Upload  
C) S3 Cross-Region Replication  
D) AWS DataSync

---

### Question 8
A company wants to store archive data that must be retained for 10 years for compliance but is rarely accessed. When needed, data can be retrieved within 12 hours. What is the MOST cost-effective storage solution?

A) S3 Standard-IA  
B) S3 Glacier Instant Retrieval  
C) S3 Glacier Flexible Retrieval  
D) S3 Glacier Deep Archive

---

### Question 9
An S3 bucket in the us-east-1 region needs to be replicated to an S3 bucket in eu-west-1 for disaster recovery. The replication must include existing objects and delete markers. What should be configured?

A) Enable S3 Cross-Region Replication with existing object replication  
B) Use AWS DataSync for initial copy, then enable CRR  
C) Use S3 Batch Operations to copy objects, then enable CRR  
D) Enable S3 Same-Region Replication first, then CRR

---

### Question 10
A web application allows users to upload images. The images should be publicly readable but only the application should be able to write. How should the S3 bucket policy be configured?

A) Allow public read access, restrict write to application IAM role  
B) Use pre-signed URLs for uploads and CloudFront for reads  
C) Make bucket fully public with ACLs  
D) Use S3 Access Points with different policies

---

### Question 11
A company needs to analyze large amounts of log data stored in S3 without loading data into a database. What is the MOST efficient solution?

A) Use Amazon Athena to query S3 data directly  
B) Load data into Amazon Redshift for analysis  
C) Use EMR to process data  
D) Create Lambda function to parse logs

---

### Question 12
An S3 bucket has versioning enabled. A 1 GB file has been modified 50 times. The company wants to reduce storage costs while maintaining the ability to recover the last 10 versions. What should they do?

A) Disable versioning  
B) Create lifecycle rule to delete noncurrent versions after 10 versions  
C) Use S3 Intelligent-Tiering  
D) Manually delete old versions

---

### Question 13
A solutions architect needs to prevent all public access to an S3 bucket, even if bucket policies or ACLs are misconfigured. What feature should be enabled?

A) S3 Bucket Policies  
B) S3 Block Public Access  
C) S3 Access Control Lists  
D) VPC Endpoints for S3

---

### Question 14
A company uploads encrypted files to S3 and wants to ensure that only encrypted uploads are accepted. How should this be enforced?

A) Enable S3 default encryption  
B) Create bucket policy denying PUT requests without encryption header  
C) Use KMS key policy to enforce encryption  
D) Enable S3 Object Lock

---

### Question 15
An application serves frequently accessed images from S3. Users worldwide experience latency. What is the BEST solution to reduce latency?

A) Use S3 Transfer Acceleration  
B) Create S3 buckets in multiple regions  
C) Use CloudFront CDN with S3 as origin  
D) Enable S3 Cross-Region Replication

---

### Question 16
A company needs to grant temporary access to specific S3 objects to external partners without creating IAM users. What is the MOST secure approach?

A) Make objects public temporarily  
B) Generate pre-signed URLs with expiration  
C) Share AWS access keys  
D) Create IAM users with limited permissions

---

### Question 17
An S3 bucket receives objects from multiple sources with different retention requirements. Some objects must be immutable for 7 years. How should this be implemented?

A) Use S3 Versioning with lifecycle policies  
B) Use S3 Object Lock in Compliance mode with 7-year retention  
C) Create separate buckets for different retention periods  
D) Use S3 Glacier Vault Lock

---

### Question 18
A solutions architect needs to track all changes to objects in an S3 bucket and receive notifications. What combination should be used? (Choose TWO)

A) Enable S3 Versioning  
B) Enable S3 Event Notifications to SNS  
C) Enable S3 Access Logging  
D) Use CloudWatch Events  
E) Enable AWS Config rules for S3

---

### Question 19
A company stores data in S3 Standard and wants to automatically transition objects to lower-cost storage classes after specific periods: 30 days → Standard-IA, 90 days → Glacier. What feature accomplishes this?

A) S3 Lifecycle Policies  
B) S3 Intelligent-Tiering  
C) S3 Batch Operations  
D) Lambda function with CloudWatch Events

---

### Question 20
An application requires read-after-write consistency for PUT requests and objects must be immediately available after upload for GET requests. Which S3 consistency model provides this?

A) Eventual consistency  
B) Strong read-after-write consistency (default in S3)  
C) Configured through S3 bucket settings  
D) Only available with S3 Express One Zone

---

### Question 21
A company wants to share large datasets (100+ TB) stored in S3 with research institutions without egress charges. What AWS service should be used?

A) S3 Transfer Acceleration  
B) AWS DataSync  
C) S3 Requester Pays buckets  
D) AWS Snowball

---

### Question 22
A solutions architect needs to prevent objects in an S3 bucket from being deleted for 90 days while allowing updates. What feature should be configured?

A) S3 Versioning  
B) S3 Object Lock in Governance mode with 90-day retention  
C) S3 Lifecycle policies  
D) IAM policy denying delete permissions

---

### Question 23
An application uploads files to S3 and processes them with Lambda. The Lambda function must only trigger when .jpg files are uploaded to the "images/" prefix. How should this be configured?

A) S3 event notification with prefix "images/" and suffix ".jpg"  
B) Lambda function filters events internally  
C) Use EventBridge rule to filter events  
D) Create separate bucket for .jpg files

---

### Question 24
A company needs to optimize costs for S3 storage that contains millions of small files (< 128 KB each). What challenge might they face?

A) S3 charges minimum 128 KB per object for Glacier storage classes  
B) S3 has request costs that can exceed storage costs  
C) Small files cannot use S3 Intelligent-Tiering  
D) Both A and B are correct

---

### Question 25
A solutions architect must ensure S3 data is protected from ransomware by preventing deletion even by root users. What is the MOST secure solution?

A) Enable MFA Delete on bucket versioning  
B) Use S3 Object Lock in Compliance mode  
C) Create IAM policy denying delete operations  
D) Enable S3 Versioning with lifecycle policies

---

### Question 26
An application requires cross-account access to S3 objects. What is the MOST secure way to grant access?

A) Make bucket publicly accessible  
B) Use bucket policy to allow access from another AWS account  
C) Share access keys between accounts  
D) Create IAM user in source account for destination account

---

### Question 27
A company stores application logs in S3 and needs to search through logs quickly without a database. What combination provides the BEST solution?

A) S3 Select to filter data, Athena for complex queries  
B) Load all logs into ElasticSearch  
C) Use S3 Batch Operations  
D) Create Lambda function to parse logs

---

### Question 28
An S3 bucket policy denies access from specific IP addresses. However, users from those IPs can still access objects. What could be the reason?

A) VPC Endpoint is being used, bypassing IP restriction  
B) CloudFront is caching objects  
C) S3 Access Logging is interfering  
D) S3 Versioning is enabled

---

### Question 29
A company needs to copy petabytes of data from on-premises storage to S3 with a 1-week deadline and limited network bandwidth (100 Mbps). What is the MOST practical solution?

A) Use S3 Transfer Acceleration  
B) Use AWS DataSync over VPN  
C) Use AWS Snowball Edge devices  
D) Use Direct Connect

---

### Question 30
A solutions architect needs to serve different versions of objects to different users based on their location. What S3 feature enables this?

A) S3 Versioning  
B) S3 Object Lambda  
C) S3 Access Points  
D) CloudFront with Lambda@Edge

---

## EBS Questions (Questions 31-45)

### Question 31
An application requires 20,000 IOPS for a database with consistent performance and the lowest latency. What EBS volume type should be used?

A) gp3  
B) gp2  
C) io2  
D) st1

---

### Question 32
A solutions architect needs to create an EBS volume that can be attached to multiple EC2 instances simultaneously in the same AZ for a clustered application. What volume type and feature should be used?

A) gp3 with Multi-Attach  
B) io2 with Multi-Attach  
C) io1 with Multi-Attach  
D) Both B and C are correct

---

### Question 33
An EC2 instance with a 500 GB gp2 volume is experiencing performance issues. The application requires consistent 8,000 IOPS. What is the MOST cost-effective solution?

A) Increase gp2 volume size to 2,667 GB  
B) Switch to gp3 and provision 8,000 IOPS  
C) Switch to io2 and provision 8,000 IOPS  
D) Use RAID 0 with multiple gp2 volumes

---

### Question 34
A company needs to move an EBS volume from us-east-1a to us-east-1b. What is the correct approach?

A) Detach volume and reattach in different AZ  
B) Create snapshot, create volume from snapshot in target AZ  
C) Use AWS DataSync to copy data  
D) Enable Multi-AZ for EBS volume

---

### Question 35
An application requires temporary high-performance storage for processing large datasets. Data doesn't need to persist after instance termination. What storage solution should be used?

A) EBS gp3 volume  
B) EBS io2 volume  
C) Instance Store volumes  
D) EFS file system

---

### Question 36
A critical database requires 99.999% durability for block storage. Which EBS volume type provides the highest durability?

A) gp3  
B) gp2  
C) io2  
D) io1

---

### Question 37
A solutions architect needs to restore an EBS volume from a snapshot quickly with full performance immediately available. What feature should be used?

A) Standard snapshot restore (pre-warm by reading)  
B) Fast Snapshot Restore (FSR)  
C) EBS Direct APIs  
D) AWS Backup instant restore

---

### Question 38
An application requires 500 MB/s sequential throughput for log processing. What is the MOST cost-effective EBS volume type?

A) gp3  
B) io2  
C) st1 (Throughput Optimized HDD)  
D) sc1 (Cold HDD)

---

### Question 39
A company wants to encrypt an existing unencrypted EBS volume. What is the correct procedure?

A) Enable encryption on the existing volume directly  
B) Create snapshot, copy snapshot with encryption, create encrypted volume  
C) Use AWS KMS to encrypt volume in-place  
D) Attach new encrypted volume and use rsync

---

### Question 40
An EBS volume has reached its IOPS limit and application performance is degrading. What should the solutions architect do? (Choose TWO)

A) Increase EBS volume size  
B) Switch to higher performance volume type  
C) Enable EBS optimization on EC2 instance  
D) Add more EBS volumes in RAID configuration  
E) Increase EC2 instance memory

---

### Question 41
A development team needs EBS volumes for development environments that can be easily backed up and restored daily. What is the MOST operationally efficient solution?

A) Manual daily snapshots  
B) AWS Data Lifecycle Manager (DLM) with automated policies  
C) Lambda function with CloudWatch Events  
D) AWS Backup with backup plans

---

### Question 42
An EC2 instance is experiencing high VolumeQueueLength in CloudWatch metrics. What does this indicate?

A) Volume is out of storage space  
B) Too many I/O requests are queued waiting for processing  
C) Network connectivity issues  
D) EBS optimization is disabled

---

### Question 43
A company needs to share EBS snapshots with another AWS account for disaster recovery testing. How should this be accomplished?

A) Copy snapshot to S3 bucket accessible by other account  
B) Modify snapshot permissions to allow access from specific AWS account ID  
C) Create IAM role for cross-account access  
D) Export snapshot and reimport in other account

---

### Question 44
An application uses gp2 volumes and frequently exhausts burst credits. What solutions can improve performance? (Choose TWO)

A) Increase volume size to increase baseline IOPS  
B) Switch to gp3 with provisioned IOPS  
C) Enable EBS optimization  
D) Use st1 volumes instead  
E) Add more RAM to EC2 instance

---

### Question 45
A solutions architect needs to monitor EBS volumes for performance degradation due to stale snapshots. What metric should be tracked?

A) BurstBalance  
B) VolumeIdleTime  
C) VolumeThroughputPercentage  
D) VolumeConsumedReadWriteOps

---

## EFS and FSx Questions (Questions 46-55)

### Question 46
A web application requires shared file storage accessible from multiple EC2 instances across different AZs. Files are frequently accessed and require POSIX compliance. What is the BEST solution?

A) EBS with Multi-Attach  
B) Amazon EFS with Standard storage class  
C) Amazon S3 with VPC endpoint  
D) Amazon FSx for Windows File Server

---

### Question 47
A company wants to migrate their on-premises Windows file shares to AWS with minimal changes to user access patterns. SMB protocol support is required. What service should be used?

A) Amazon EFS  
B) Amazon FSx for Windows File Server  
C) Amazon S3  
D) Amazon FSx for Lustre

---

### Question 48
An EFS file system experiences high latency for metadata operations. What performance mode should be configured?

A) General Purpose performance mode  
B) Max I/O performance mode  
C) Bursting throughput mode  
D) Provisioned throughput mode

---

### Question 49
A high-performance computing (HPC) workload requires sub-millisecond latency and hundreds of GB/s throughput for parallel processing. What storage solution is MOST appropriate?

A) Amazon EFS  
B) Amazon EBS io2  
C) Amazon FSx for Lustre  
D) Amazon S3

---

### Question 50
A company stores infrequently accessed files in EFS and wants to reduce storage costs. What feature should be enabled?

A) EFS Lifecycle Management to transition to Infrequent Access storage class  
B) EFS Intelligent-Tiering  
C) EFS Provisioned Throughput  
D) EFS Backup

---

### Question 51
An application requires consistent throughput of 500 MB/s regardless of file system size. The EFS file system is small (50 GB) and uses bursting mode. What should be configured?

A) Increase file system size to increase burst credits  
B) Enable Provisioned Throughput mode with 500 MB/s  
C) Switch to Max I/O performance mode  
D) Use EFS Infrequent Access storage class

---

### Question 52
A solutions architect needs to ensure EFS data is automatically backed up daily with 30-day retention. What is the BEST solution?

A) Manual EFS snapshots  
B) AWS Backup with backup plan for EFS  
C) EFS-to-EFS replication with lifecycle policies  
D) Lambda function with CloudWatch Events

---

### Question 53
A Windows-based application requires Active Directory integration and multi-AZ deployment for file storage. What service provides this capability?

A) Amazon EFS  
B) Amazon FSx for Windows File Server with Multi-AZ  
C) Amazon S3  
D) Amazon FSx for NetApp ONTAP

---

### Question 54
A machine learning workload needs to process training data stored in S3 (10 TB) with high-throughput file system access. What is the MOST efficient solution?

A) Copy data to EFS using DataSync  
B) Use FSx for Lustre with S3 integration  
C) Mount S3 directly using s3fs  
D) Use EBS volumes with S3 sync

---

### Question 55
An EFS file system needs to be accessed from on-premises servers over AWS Direct Connect. What must be configured?

A) VPN connection to VPC  
B) EFS mount targets in VPC, route through Direct Connect  
C) S3 VPC Gateway Endpoint  
D) EFS Access Points

---

## Storage Gateway and AWS Backup Questions (Questions 56-65)

### Question 56
A company wants to integrate on-premises applications with cloud storage using NFS protocol, with frequently accessed data cached locally. What AWS service should be used?

A) AWS DataSync  
B) AWS Storage Gateway - File Gateway  
C) AWS Storage Gateway - Volume Gateway  
D) AWS Transfer Family

---

### Question 57
An on-premises application requires block storage volumes backed by S3 for disaster recovery. Primary data should remain on-premises with cloud backup. What Storage Gateway configuration is appropriate?

A) File Gateway  
B) Volume Gateway - Cached Volumes  
C) Volume Gateway - Stored Volumes  
D) Tape Gateway

---

### Question 58
A company needs to replace physical tape backup infrastructure while maintaining existing backup workflows. What AWS solution provides this?

A) AWS Backup  
B) AWS Storage Gateway - Tape Gateway (VTL)  
C) Amazon S3 Glacier  
D) AWS DataSync

---

### Question 59
A solutions architect needs to centrally manage backups across EC2, EBS, EFS, RDS, DynamoDB, and Aurora with compliance reporting. What service provides this capability?

A) AWS Backup  
B) AWS Data Lifecycle Manager  
C) Manual snapshots for each service  
D) AWS Systems Manager

---

### Question 60
An on-premises VMware environment needs to be backed up to AWS with incremental backups. What is the MOST efficient solution?

A) AWS Storage Gateway - Volume Gateway  
B) AWS Backup with VMware plugin  
C) Manual VM exports to S3  
D) AWS DataSync

---

### Question 61
A File Gateway is configured but on-premises applications experience slow performance accessing files. What can improve performance?

A) Increase cache storage on File Gateway appliance  
B) Enable S3 Transfer Acceleration  
C) Use Storage Gateway - Volume Gateway instead  
D) Enable S3 Intelligent-Tiering

---

### Question 62
A company requires cross-region backup copies for compliance. AWS Backup is being used for EBS and RDS backups. What feature enables this?

A) Create separate backup plans in each region  
B) Enable cross-region backup copy in AWS Backup plan  
C) Use S3 Cross-Region Replication for backups  
D) Manually copy snapshots to other regions

---

### Question 63
A Volume Gateway Stored Volumes deployment requires 10 TB of on-premises storage. All data is stored locally with async backups to AWS. What is the maximum volume size supported?

A) 1 TB  
B) 16 TB  
C) 32 TB  
D) 512 TB (per gateway)

---

### Question 64
A solutions architect needs to migrate 500 TB of data from on-premises NFS storage to S3 with ongoing synchronization. What service is MOST appropriate?

A) AWS Storage Gateway - File Gateway  
B) AWS DataSync  
C) AWS Transfer Family  
D) AWS Snowball with DataSync

---

### Question 65
An AWS Backup plan should backup EFS file systems daily, retain for 30 days, and transition to cold storage after 7 days. What configuration achieves this?

A) Lifecycle policy: 30-day retention, 7-day transition to cold storage  
B) Two separate backup plans  
C) EFS lifecycle policies only  
D) Manual backup management

---

## End of Practice Test 2

**Next Steps:**
1. Review your answers
2. Check the answer key in `answers.md`
3. Study explanations for questions you missed
4. Review relevant AWS documentation for weak areas

**Scoring Guide:**
- 47-52 correct (72-80%): Pass - Review missed topics
- 53-58 correct (81-89%): Good - Minor review needed
- 59-65 correct (90-100%): Excellent - Ready for exam

**Key Topics Covered:**
- S3 storage classes, lifecycle policies, encryption, security
- EBS volume types, performance optimization, snapshots
- EFS performance modes, integration patterns
- FSx for Windows and Lustre use cases
- Storage Gateway types and configurations
- AWS Backup centralized management
