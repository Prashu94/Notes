# AWS SAA-C03 Practice Test 3: Database Services

**Topics Covered:** RDS, Aurora, DynamoDB, Redshift  
**Number of Questions:** 65  
**Time Limit:** 130 minutes (2 minutes per question)  
**Passing Score:** 72% (47 out of 65)

---

## RDS Questions (Questions 1-25)

### Question 1
A company needs high availability for their MySQL database with automatic failover in case of failure. The RTO should be under 2 minutes. What RDS feature should be used?

A) RDS Read Replicas  
B) RDS Multi-AZ deployment  
C) Manual snapshots with automated restore  
D) RDS Proxy

### Question 2
An application requires a read-heavy database workload with ability to scale read capacity independently. What solution should be implemented?

A) Increase RDS instance size  
B) Create RDS Read Replicas  
C) Enable Multi-AZ  
D) Use DynamoDB instead

### Question 3
A company wants to encrypt an existing unencrypted RDS database. What is the correct procedure?

A) Enable encryption on the existing DB instance  
B) Create encrypted snapshot, restore to new encrypted instance  
C) Use KMS to encrypt in-place  
D) Modify DB instance to enable encryption

### Question 4
An RDS MySQL database experiences performance degradation during peak hours. Which actions can help? (Choose TWO)

A) Create Read Replicas for read traffic  
B) Upgrade to larger instance class  
C) Enable Multi-AZ  
D) Increase backup retention period  
E) Move to different region

### Question 5
A solutions architect needs to migrate an on-premises Oracle database to AWS with minimal downtime. What service should be used?

A) AWS DataSync  
B) AWS Database Migration Service (DMS)  
C) AWS Snow family  
D) Manual backup and restore

### Question 6
An RDS instance requires 20,000 IOPS for consistent performance. What storage type should be provisioned?

A) General Purpose (gp2)  
B) General Purpose (gp3)  
C) Provisioned IOPS (io1)  
D) Magnetic storage

### Question 7
A company needs to perform maintenance on an RDS Multi-AZ deployment with minimal downtime. What happens during a maintenance window?

A) Maintenance on primary, then failover, then standby  
B) Maintenance on standby, failover to standby, then primary  
C) Both instances maintained simultaneously  
D) Application downtime required for both instances

### Question 8
An application needs to connect to RDS database from Lambda functions. Connection pooling overhead is causing timeouts. What service can help?

A) RDS Proxy  
B) ElastiCache  
C) API Gateway  
D) Direct Connect

### Question 9
An RDS Read Replica is lagging significantly behind the primary instance. What could be the cause?

A) Network latency between AZs  
B) High write load on primary instance  
C) Read replica instance too small  
D) All of the above

### Question 10
A company wants to restore an RDS database to a specific point in time from 3 days ago. What is required?

A) Manual snapshot from 3 days ago  
B) Automated backups with point-in-time recovery enabled  
C) Read replica from 3 days ago  
D) Database logs from 3 days ago

### Question 11
An RDS PostgreSQL database needs to be accessible from a specific on-premises IP range only. How should this be configured?

A) RDS instance in public subnet with security group allowing IP range  
B) RDS instance in private subnet with VPN and security group rules  
C) Use RDS public accessibility with IAM authentication  
D) Use RDS Proxy with IP filtering

### Question 12
A company requires cross-region disaster recovery for RDS with RPO of 5 minutes. What solution provides this?

A) Automated backups copied to another region  
B) Cross-region Read Replica  
C) Multi-AZ deployment in two regions  
D) Manual snapshots copied daily

### Question 13
An RDS MySQL instance uses default parameter group. Custom settings need to be applied. What should be done?

A) Modify default parameter group  
B) Create custom parameter group and associate with DB instance  
C) Edit settings directly in MySQL  
D) Use RDS CLI to modify parameters

### Question 14
A solutions architect needs to monitor RDS database performance metrics. What service provides this visibility?

A) AWS CloudTrail  
B) Amazon CloudWatch  
C) AWS X-Ray  
D) AWS Config

### Question 15
An RDS database requires temporary capacity increase for month-end processing. What is the MOST cost-effective approach?

A) Permanently upgrade instance size  
B) Temporarily scale up before processing, scale down after  
C) Use Read Replicas for processing  
D) Move to Aurora Serverless

### Question 16
A company stores sensitive data in RDS and must ensure encryption in transit. How should this be configured?

A) Enable SSL/TLS connections and enforce in security group  
B) Use VPN connection to RDS  
C) Enable RDS encryption at rest  
D) Use IAM database authentication

### Question 17
An RDS SQL Server instance requires native backup capability for compliance. What option group feature enables this?

A) Native backup to S3  
B) Automated backups  
C) Manual snapshots  
D) Read replicas

### Question 18
A multi-tenant SaaS application uses RDS. Each tenant needs isolated database. What is the MOST scalable approach?

A) Single database with tenant_id column  
B) Separate schema per tenant in single database  
C) Separate RDS instance per tenant  
D) Use DynamoDB instead

### Question 19
An RDS instance is experiencing high CPU utilization. Enhanced Monitoring shows which process is consuming resources. What additional monitoring is needed?

A) No additional monitoring needed  
B) Performance Insights for query-level analysis  
C) CloudTrail for API calls  
D) VPC Flow Logs

### Question 20
A company needs to upgrade RDS MySQL from version 5.7 to 8.0 with minimal downtime. What is the BEST approach?

A) Create snapshot, restore to new version  
B) Use Read Replica on new version, promote when ready  
C) In-place upgrade during maintenance window  
D) Use DMS to migrate to new version

### Question 21
An RDS database should only accept connections from application servers in specific subnets. What combination provides this security? (Choose TWO)

A) DB subnet group defining allowed subnets  
B) Security group allowing traffic from application security group  
C) Network ACL rules  
D) IAM database authentication  
E) RDS encryption

### Question 22
A company requires automated failover testing for RDS Multi-AZ. How can failover be triggered?

A) Stop primary instance  
B) Use "Reboot with failover" option  
C) Delete primary instance  
D) Modify Multi-AZ setting

### Question 23
An RDS instance has automated backups enabled with 7-day retention. On day 5, database is accidentally deleted. Can data be recovered?

A) Yes, from automated backups  
B) No, automated backups deleted with instance  
C) Yes, if final snapshot was created  
D) Only if Read Replica exists

### Question 24
A company wants to reduce RDS costs for development databases running 8 hours/day. What strategy should be used?

A) Use Reserved Instances  
B) Stop databases when not in use  
C) Use Aurora Serverless  
D) Reduce instance size

### Question 25
An RDS Oracle instance requires specific licensing model. What options are available?

A) License Included or Bring Your Own License (BYOL)  
B) Open source license only  
C) AWS managed licensing only  
D) No licensing required

---

## Aurora Questions (Questions 26-40)

### Question 26
A company needs a MySQL-compatible database with automatic scaling storage and 15 read replicas. What service provides this?

A) RDS MySQL with Read Replicas  
B) Amazon Aurora MySQL  
C) DynamoDB  
D) Redshift

### Question 27
An application has unpredictable database workloads varying from minimal to high. What Aurora deployment model is MOST cost-effective?

A) Aurora provisioned instances  
B) Aurora Serverless  
C) Aurora Global Database  
D) Aurora Read Replicas

### Question 28
A solutions architect needs to implement cross-region disaster recovery with RPO < 1 second for Aurora. What feature should be used?

A) Aurora Read Replicas in another region  
B) Aurora Global Database  
C) Manual snapshots copied to another region  
D) Aurora Multi-AZ

### Question 29
An Aurora MySQL cluster has primary instance and 5 Aurora Replicas. What endpoint should the application use for read traffic load balancing?

A) Cluster endpoint  
B) Primary instance endpoint  
C) Reader endpoint  
D) Custom endpoint

### Question 30
A company wants to create a test database clone from production Aurora cluster without impacting performance. What feature provides this?

A) Aurora snapshot and restore  
B) Aurora cloning (copy-on-write)  
C) Aurora Read Replica  
D) Manual export to S3

### Question 31
An Aurora cluster experiences planned primary instance failure. What is the typical failover time?

A) 60-120 seconds  
B) < 30 seconds  
C) 5-10 minutes  
D) Immediate (no downtime)

### Question 32
A solutions architect needs to restore an Aurora database to 4 hours ago. What feature enables this?

A) Automated backups with point-in-time recovery  
B) Aurora Backtrack (MySQL only)  
C) Manual snapshots  
D) Aurora Replica promotion

### Question 33
An Aurora PostgreSQL cluster requires 100,000 IOPS. How is Aurora storage performance scaled?

A) Manually provision IOPS  
B) Aurora storage auto-scales with cluster size  
C) Upgrade to larger instance type  
D) Enable Provisioned IOPS

### Question 34
A company needs to analyze Aurora database performance and identify slow queries. What service provides this?

A) CloudWatch metrics  
B) Aurora Performance Insights  
C) CloudTrail logs  
D) Enhanced Monitoring

### Question 35
An Aurora Serverless cluster is experiencing frequent scaling events. What can be done to optimize?

A) Increase max ACUs  
B) Set more appropriate scaling configuration  
C) Switch to provisioned Aurora  
D) Add Read Replicas

### Question 36
A multi-region application requires local read replicas in each region with Aurora. What feature enables this?

A) Cross-region Read Replicas  
B) Aurora Global Database  
C) Aurora Serverless in each region  
D) RDS Multi-AZ across regions

### Question 37
An Aurora MySQL cluster needs custom database parameters. What should be configured?

A) DB parameter group  
B) DB cluster parameter group  
C) Both DB and cluster parameter groups  
D) Aurora doesn't support custom parameters

### Question 38
A company wants to migrate from RDS MySQL to Aurora MySQL with minimal downtime. What is the BEST approach?

A) Create Aurora Read Replica of RDS, promote when ready  
B) Snapshot and restore to Aurora  
C) Use DMS for live migration  
D) Manual export/import

### Question 39
An Aurora cluster requires connection pooling and read/write split routing. What service provides this?

A) Application Load Balancer  
B) RDS Proxy  
C) Route 53  
D) Custom application logic

### Question 40
An Aurora database has storage size of 50 GB. If database grows to 75 GB, what happens to storage?

A) Storage automatically expands in 10 GB increments  
B) Manual storage upgrade required  
C) Database stops accepting writes  
D) Oldest data automatically archived

---

## DynamoDB Questions (Questions 41-55)

### Question 41
An application needs consistent sub-10ms latency for key-value queries at any scale. What database should be used?

A) RDS MySQL  
B) Amazon DynamoDB  
C) Amazon Redshift  
D) Aurora MySQL

### Question 42
A DynamoDB table stores user profiles with UserID as partition key. The application frequently queries by Email. What should be implemented?

A) Use Scan operation with filter  
B) Create Global Secondary Index (GSI) with Email as key  
C) Create Local Secondary Index (LSI) with Email as key  
D) Duplicate data with Email as partition key

### Question 43
A DynamoDB table has unpredictable traffic patterns. What capacity mode is MOST cost-effective?

A) Provisioned capacity  
B) On-demand capacity  
C) Reserved capacity  
D) Auto-scaling provisioned capacity

### Question 44
An application requires strongly consistent reads from DynamoDB for financial transactions. How should reads be configured?

A) Use GetItem with ConsistentRead=true  
B) Use Query with eventual consistency  
C) Use Scan operation  
D) Consistent reads not supported in DynamoDB

### Question 45
A solutions architect needs to process DynamoDB item changes in real-time. What feature enables this?

A) DynamoDB Backups  
B) DynamoDB Streams with Lambda  
C) CloudWatch Events  
D) DynamoDB Accelerator (DAX)

### Question 46
A DynamoDB table experiences read throttling during peak hours. What solutions can help? (Choose TWO)

A) Increase read capacity units  
B) Implement DynamoDB Accelerator (DAX)  
C) Use Scan instead of Query  
D) Enable DynamoDB Streams  
E) Add Global Secondary Indexes

### Question 47
A multi-region application requires active-active DynamoDB replication with multi-master writes. What feature provides this?

A) DynamoDB Streams to replicate  
B) DynamoDB Global Tables  
C) Cross-region Read Replicas  
D) Manual replication with Lambda

### Question 48
A DynamoDB table has partition key ProductID and sort key Timestamp. The application needs to query items by ProductID for last 7 days. What operation should be used?

A) Scan with filter on Timestamp  
B) Query with ProductID and Timestamp range  
C) GetItem with ProductID  
D) BatchGetItem for date range

### Question 49
A company needs point-in-time recovery for DynamoDB table to restore to any point in last 35 days. What feature should be enabled?

A) Automated backups  
B) Point-in-Time Recovery (PITR)  
C) DynamoDB Streams  
D) Manual snapshots

### Question 50
An application performs multiple DynamoDB operations that must all succeed or all fail. What feature provides this?

A) Batch operations  
B) DynamoDB Transactions  
C) Conditional writes  
D) DynamoDB Streams

### Question 51
A DynamoDB table uses on-demand capacity but costs are high. Analysis shows predictable traffic. What change reduces costs?

A) Stay with on-demand  
B) Switch to provisioned capacity with auto-scaling  
C) Reduce item size  
D) Delete unnecessary GSIs

### Question 52
A solutions architect needs to perform complex queries across multiple DynamoDB attributes. What AWS service can help?

A) DynamoDB Query operation  
B) Amazon Athena querying DynamoDB exports  
C) ElasticSearch integration  
D) Use RDS instead

### Question 53
A DynamoDB table stores IoT sensor data with DeviceID (partition key) and Timestamp (sort key). The application needs to query all devices' latest reading. What is the MOST efficient approach?

A) Scan entire table  
B) Create GSI with inverted keys  
C) Query each DeviceID separately  
D) Use DynamoDB Streams

### Question 54
A company needs to export a full DynamoDB table to S3 for analysis without impacting production workload. What feature should be used?

A) Scan operation to export  
B) DynamoDB export to S3  
C) DynamoDB Streams to S3  
D) AWS Glue ETL job

### Question 55
An application stores frequently accessed data in DynamoDB. Adding caching layer could reduce costs and latency. What service provides microsecond latency caching?

A) Amazon ElastiCache  
B) Amazon CloudFront  
C) DynamoDB Accelerator (DAX)  
D) Amazon S3

---

## Redshift Questions (Questions 56-65)

### Question 56
A company needs a data warehouse for complex analytics on petabytes of structured data. What AWS service should be used?

A) RDS PostgreSQL  
B) Amazon Redshift  
C) DynamoDB  
D) Aurora PostgreSQL

### Question 57
A Redshift cluster requires the ability to query data directly in S3 without loading. What feature provides this?

A) Redshift COPY command  
B) Redshift Spectrum  
C) AWS Glue  
D) Athena

### Question 58
A solutions architect needs to implement disaster recovery for Redshift cluster in another region. What approach should be used?

A) Automated snapshots copied to another region  
B) Redshift Read Replicas  
C) Multi-AZ Redshift cluster  
D) DMS replication

### Question 59
A Redshift cluster experiences slow query performance. What features can help optimize performance? (Choose TWO)

A) Distribution keys and sort keys  
B) Increase node count  
C) Use DynamoDB instead  
D) Enable Multi-AZ  
E) Add Read Replicas

### Question 60
A company has unpredictable analytics workloads and wants to pay only for queries executed. What Redshift deployment model should be used?

A) Redshift provisioned cluster  
B) Redshift Serverless  
C) Redshift Spectrum  
D) Redshift with auto-pause

### Question 61
A Redshift cluster should only be accessible from specific application servers. How should network security be configured?

A) Public cluster with security group rules  
B) Private cluster in VPC with security group allowing application servers  
C) Use IAM authentication only  
D) Public cluster with IP whitelist

### Question 62
A solutions architect needs to load large datasets from S3 into Redshift efficiently. What is the BEST approach?

A) Use INSERT statements  
B) Use COPY command from S3  
C) Use AWS Glue ETL  
D) Use DMS

### Question 63
A Redshift cluster requires encryption at rest for compliance. What encryption options are available?

A) AWS KMS encryption  
B) SSE-S3 encryption  
C) Client-side encryption only  
D) Encryption not supported

### Question 64
A company needs to resize Redshift cluster to handle increased workload. What resize option minimizes downtime?

A) Classic resize (cluster unavailable)  
B) Elastic resize (minutes of downtime)  
C) Snapshot and restore to larger cluster  
D) Add nodes with zero downtime

### Question 65
A Redshift cluster uses RA3 node types. What is the primary benefit of RA3 compared to DC2?

A) Lower cost for compute  
B) Managed storage that scales independently from compute  
C) Better network performance  
D) Support for more concurrent queries

---

## End of Practice Test 3

**Next Steps:**
1. Review your answers
2. Check the answer key in `answers.md`
3. Study explanations for questions you missed
4. Review relevant AWS documentation for weak areas
