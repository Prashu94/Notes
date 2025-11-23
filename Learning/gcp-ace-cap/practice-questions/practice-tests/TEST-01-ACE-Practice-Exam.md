# GCP Associate Cloud Engineer Practice Test 01

## Exam Instructions

- **Total Questions**: 50
- **Time Limit**: 2 hours (120 minutes)
- **Passing Score**: 70% (35 correct answers)
- **Question Format**: Multiple choice (single correct answer)
- **No negative marking**

**Instructions**:
1. Set a timer for 120 minutes
2. Answer all questions without looking at the answer key
3. Mark questions you're unsure about for review
4. After completing, check answers in the Answer Key section
5. Review explanations for ALL questions, especially incorrect ones

---

## Questions

### Question 1
Your company needs to deploy a web application that handles variable traffic throughout the day. The application should automatically scale based on CPU utilization. Which compute option should you choose?

**A)** Compute Engine instances with manual scaling

**B)** Compute Engine managed instance group with autoscaling

**C)** App Engine flexible environment

**D)** Cloud Functions

**Answer**: B

---

### Question 2
You need to grant a developer read-only access to view all Compute Engine instances but prevent them from making any changes. Which role should you assign?

**A)** roles/compute.admin

**B)** roles/compute.viewer

**C)** roles/viewer

**D)** roles/compute.instanceAdmin

**Answer**: B

---

### Question 3
Your application stores user-uploaded images that are accessed frequently for the first 30 days, then rarely accessed. Which Cloud Storage strategy is most cost-effective?

**A)** Use Standard storage class only

**B)** Use Nearline storage class

**C)** Use Standard storage class with lifecycle policy to transition to Nearline after 30 days

**D)** Use Archive storage class

**Answer**: C

---

### Question 4
You need to allow SSH access to a Compute Engine instance only from your office IP address (203.0.113.50). What should you configure?

**A)** VPC firewall rule allowing TCP:22 from source range 203.0.113.50/32

**B)** IAM policy granting SSH permissions

**C)** Security group allowing port 22

**D)** Network ACL rules

**Answer**: A

---

### Question 5
Your Cloud SQL database needs to be highly available with automatic failover. What should you configure?

**A)** Create manual backups hourly

**B)** Enable high availability (Regional) configuration

**C)** Create a read replica in another zone

**D)** Use Cloud Spanner instead

**Answer**: B

---

### Question 6
You need to run a batch processing job that can tolerate interruptions and want to minimize costs. Which Compute Engine option should you use?

**A)** Standard VM instances

**B)** Preemptible VM instances

**C)** Sole-tenant nodes

**D)** Shared-core instances

**Answer**: B

---

### Question 7
Your application running on GKE needs to access Cloud Storage buckets. What is the recommended authentication method?

**A)** Download service account key and mount as Kubernetes secret

**B)** Use Workload Identity

**C)** Use default Compute Engine service account

**D)** Embed credentials in the container image

**Answer**: B

---

### Question 8
You need to ensure that objects in a Cloud Storage bucket cannot be deleted for 7 years to meet regulatory requirements. What should you implement?

**A)** Bucket lifecycle policy

**B)** Bucket retention policy

**C)** IAM policy preventing deletion

**D)** Object versioning

**Answer**: B

---

### Question 9
Your company wants to monitor all IAM policy changes across the organization. What should you configure?

**A)** Cloud Monitoring alert on IAM metrics

**B)** Cloud Logging sink exporting Admin Activity logs to BigQuery

**C)** Custom Cloud Function to track changes

**D)** Enable Data Access logs

**Answer**: B

---

### Question 10
You need to estimate the cost of a BigQuery query before running it. What command should you use?

**A)** bq query --cost-estimate

**B)** bq query --dry_run

**C)** bq estimate

**D)** bq query --preview

**Answer**: B

---

### Question 11
Your web application needs a global load balancer with SSL termination. Which load balancer should you create?

**A)** Network Load Balancer

**B)** Internal HTTP(S) Load Balancer

**C)** External HTTP(S) Load Balancer

**D)** TCP Proxy Load Balancer

**Answer**: C

---

### Question 12
You need to connect your on-premises data center to Google Cloud with a dedicated 10 Gbps connection. What should you use?

**A)** Cloud VPN

**B)** Cloud Interconnect - Dedicated

**C)** Direct Peering

**D)** Partner Interconnect

**Answer**: B

---

### Question 13
A Compute Engine instance needs to access Google APIs without an external IP address. What should you enable?

**A)** Cloud NAT

**B)** Private Google Access

**C)** VPC Peering

**D)** Cloud VPN

**Answer**: B

---

### Question 14
You need to deploy a containerized application that automatically scales to zero when not in use. Which service should you choose?

**A)** Google Kubernetes Engine with HPA

**B)** Cloud Run

**C)** Compute Engine with autoscaling

**D)** App Engine Standard

**Answer**: B

---

### Question 15
Your organization requires all Cloud Storage data to be encrypted with customer-managed keys. What should you use?

**A)** Default encryption (Google-managed keys)

**B)** Customer-Managed Encryption Keys (CMEK) in Cloud KMS

**C)** Customer-Supplied Encryption Keys (CSEK)

**D)** Application-level encryption

**Answer**: B

---

### Question 16
You need to create a custom IAM role with specific permissions for listing and starting Compute Engine instances. Which command should you use?

**A)** gcloud iam roles create --permissions=compute.instances.list,compute.instances.start

**B)** gcloud compute roles create --permissions=list,start

**C)** gcloud projects add-iam-policy-binding --role=custom

**D)** gcloud iam create-role --permissions=instances.list

**Answer**: A

---

### Question 17
Your application logs need to be retained for 90 days for compliance. Cloud Logging only retains for 30 days. What should you do?

**A)** Export logs to Cloud Storage using a log sink

**B)** Increase Cloud Logging retention period

**C)** Copy logs manually each month

**D)** Use Cloud Monitoring for log storage

**Answer**: A

---

### Question 18
You need to partition a BigQuery table by date to optimize query performance and reduce costs. Which partitioning type should you use?

**A)** Integer range partitioning

**B)** Ingestion-time partitioning

**C)** Time-unit column partitioning

**D)** Hash partitioning

**Answer**: C

---

### Question 19
Your GKE cluster needs to automatically add nodes when pods are pending due to insufficient resources. What should you enable?

**A)** Horizontal Pod Autoscaler

**B)** Vertical Pod Autoscaler

**C)** Cluster Autoscaler

**D)** Manual node pool scaling

**Answer**: C

---

### Question 20
You need to restore a Cloud SQL database to a specific point in time from yesterday. What feature should you use?

**A)** Automated backups only

**B)** Point-in-time recovery (PITR)

**C)** Manual snapshots

**D)** Export/Import

**Answer**: B

---

### Question 21
Your company wants to share a VPC network across multiple projects. What should you implement?

**A)** VPC Peering

**B)** Shared VPC

**C)** Cloud VPN

**D)** Cloud Interconnect

**Answer**: B

---

### Question 22
You need to allow traffic between two VMs in different VPCs. What should you configure?

**A)** VPC Peering

**B)** External IP addresses

**C)** Cloud NAT

**D)** Shared VPC

**Answer**: A

---

### Question 23
Your Cloud Run service needs to access Secret Manager secrets. What is the recommended approach?

**A)** Mount secrets using Secret Manager CSI driver

**B)** Environment variables with secret references

**C)** Download secrets in startup script

**D)** Embed secrets in container image

**Answer**: B

---

### Question 24
You need to migrate a 5TB MySQL database from on-premises to Cloud SQL with minimal downtime. What should you use?

**A)** mysqldump and import

**B)** Database Migration Service

**C)** Manual replication setup

**D)** Take snapshot and upload

**Answer**: B

---

### Question 25
Your application requires a managed NoSQL database with multi-region replication and strong consistency. Which service should you use?

**A)** Cloud SQL

**B)** Firestore

**C)** Cloud Spanner

**D)** Bigtable

**Answer**: C

---

### Question 26
You need to ensure at least 3 out of 5 pods remain available during voluntary disruptions like updates. What should you create?

**A)** HorizontalPodAutoscaler with minReplicas=3

**B)** PodDisruptionBudget with minAvailable=3

**C)** Deployment with replicas=5

**D)** DaemonSet

**Answer**: B

---

### Question 27
Your organization needs to enforce that all Compute Engine instances must use specific machine types. What should you implement?

**A)** IAM custom roles

**B)** Organization Policy constraints

**C)** VPC firewall rules

**D)** Resource quotas

**Answer**: B

---

### Question 28
You need to view all ERROR level logs from your Cloud Run service in the last 24 hours. Which query should you use?

**A)** resource.type="cloud_run_revision" severity>=ERROR timestamp>="-24h"

**B)** resource.type="gce_instance" severity=ERROR

**C)** logName="cloud_run" level=ERROR

**D)** service="cloud_run" error=true

**Answer**: A

---

### Question 29
Your application needs to process messages asynchronously with guaranteed delivery. Which service should you use?

**A)** Cloud Storage events

**B)** Cloud Pub/Sub

**C)** Cloud Tasks

**D)** HTTP endpoints

**Answer**: B

---

### Question 30
You need to load a 100GB CSV file from Cloud Storage into BigQuery efficiently. What method should you use?

**A)** BigQuery web UI upload

**B)** bq load command

**C)** Streaming inserts

**D)** Manual INSERT statements

**Answer**: B

---

### Question 31
Your Compute Engine instance needs a larger machine type. The instance must remain in the same zone. What should you do?

**A)** Create a new instance and migrate data

**B)** Stop the instance, change machine type, then start it

**C)** Change machine type while instance is running

**D)** Delete instance and recreate with new type

**Answer**: B

---

### Question 32
You need to grant a service account permission to impersonate another service account. Which role should you assign?

**A)** roles/iam.serviceAccountUser

**B)** roles/iam.serviceAccountTokenCreator

**C)** roles/iam.serviceAccountAdmin

**D)** roles/iam.serviceAccountKeyAdmin

**Answer**: B

---

### Question 33
Your website serves static content globally and you want to reduce latency. What should you implement?

**A)** Multi-region Cloud Storage bucket

**B)** Cloud CDN with Cloud Storage backend

**C)** Compute Engine instances in multiple regions

**D)** Regional Cloud Storage buckets in each continent

**Answer**: B

---

### Question 34
You need to create an alert that triggers when CPU utilization exceeds 80% for 5 minutes. What should you create?

**A)** Cloud Monitoring alert policy

**B)** Cloud Logging sink

**C)** Uptime check

**D)** Custom dashboard

**Answer**: A

---

### Question 35
Your GKE deployment needs to perform a rolling update to a new image version without downtime. What command should you use?

**A)** kubectl delete deployment && kubectl create deployment

**B)** kubectl set image deployment/name container=new-image

**C)** kubectl scale deployment --replicas=0

**D)** kubectl replace deployment

**Answer**: B

---

### Question 36
You need to copy 10TB of data from AWS S3 to Cloud Storage. What is the most efficient method?

**A)** Download to local machine, then upload to Cloud Storage

**B)** Storage Transfer Service

**C)** gsutil in a loop

**D)** Write custom script

**Answer**: B

---

### Question 37
Your Cloud SQL instance is running out of storage. What is the recommended action?

**A)** Delete old data

**B)** Increase storage size (no instance restart required)

**C)** Create new instance with larger storage

**D)** Export data to Cloud Storage

**Answer**: B

---

### Question 38
You need to allow only specific columns of a BigQuery table to be viewed by certain users. What should you create?

**A)** IAM column-level permissions

**B)** View with selected columns

**C)** Separate table with required columns

**D)** Row-level security

**Answer**: B

---

### Question 39
Your application needs to run a scheduled task every day at 2 AM. Which GCP service is most appropriate?

**A)** Cloud Scheduler

**B)** Cron job on Compute Engine

**C)** Cloud Tasks

**D)** Manual execution

**Answer**: A

---

### Question 40
You need to install the Cloud Monitoring agent on Compute Engine instances to collect memory metrics. What should you install?

**A)** Legacy Monitoring agent

**B)** Ops Agent

**C)** Stackdriver agent

**D)** Fluentd

**Answer**: B

---

### Question 41
Your organization requires audit logging of all data access to Cloud Storage. What type of logs should you enable?

**A)** Admin Activity logs

**B)** Data Access logs

**C)** System Event logs

**D)** Policy Denied logs

**Answer**: B

---

### Question 42
You need to provide temporary download access to a private Cloud Storage object for 2 hours. What should you create?

**A)** Signed URL with 2-hour expiration

**B)** Make object public temporarily

**C)** Grant IAM permissions temporarily

**D)** Create temporary service account

**Answer**: A

---

### Question 43
Your BigQuery query is scanning too much data and costs are high. What optimization should you implement?

**A)** Add partitioning and clustering

**B)** Increase query timeout

**C)** Use larger BigQuery slots

**D)** Run queries at night

**Answer**: A

---

### Question 44
You need to connect to a Cloud SQL instance from a GKE pod. What is the recommended method?

**A)** Public IP with authorized networks

**B)** Cloud SQL Proxy sidecar container

**C)** Direct connection using private IP

**D)** VPN tunnel

**Answer**: B

---

### Question 45
Your application on Compute Engine needs to read objects from Cloud Storage. The VM should not have an external IP. What should you configure?

**A)** Cloud NAT

**B)** Private Google Access on the subnet

**C)** VPN connection

**D)** Cloud Interconnect

**Answer**: B

---

### Question 46
You need to create a GKE cluster that can automatically scale from 1 to 10 nodes based on pod demand. What should you enable?

**A)** Horizontal Pod Autoscaler

**B)** Vertical Pod Autoscaler

**C)** Cluster Autoscaler

**D)** Manual scaling

**Answer**: C

---

### Question 47
Your team needs to query data from multiple BigQuery datasets across different projects. What should you use?

**A)** Export all data to one project

**B)** Fully-qualified table names (project.dataset.table)

**C)** BigQuery Data Transfer Service

**D)** Create views in each project

**Answer**: B

---

### Question 48
You need to ensure a Kubernetes deployment always has at least 2 replicas running. What should you set?

**A)** minReplicas in HorizontalPodAutoscaler

**B)** replicas in Deployment spec

**C)** minAvailable in PodDisruptionBudget

**D)** Both A and C

**Answer**: D

---

### Question 49
Your Cloud Functions need to be triggered when a file is uploaded to a Cloud Storage bucket. What trigger type should you configure?

**A)** HTTP trigger

**B)** Cloud Storage trigger

**C)** Pub/Sub trigger

**D)** Cloud Scheduler trigger

**Answer**: B

---

### Question 50
You need to check if your website is accessible globally and get alerts if it goes down. What should you create?

**A)** Cloud Monitoring alert on compute metrics

**B)** Uptime check with alerting

**C)** Log-based metric

**D)** Custom monitoring script

**Answer**: B

---

## Answer Key

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|----|--------|----|----|----|----|----|----|----|----|
| 1  | B | 11 | C | 21 | B | 31 | B | 41 | B |
| 2  | B | 12 | B | 22 | A | 32 | B | 42 | A |
| 3  | C | 13 | B | 23 | B | 33 | B | 43 | A |
| 4  | A | 14 | B | 24 | B | 34 | A | 44 | B |
| 5  | B | 15 | B | 25 | C | 35 | B | 45 | B |
| 6  | B | 16 | A | 26 | B | 36 | B | 46 | C |
| 7  | B | 17 | A | 27 | B | 37 | B | 47 | B |
| 8  | B | 18 | C | 28 | A | 38 | B | 48 | D |
| 9  | B | 19 | C | 29 | B | 39 | A | 49 | B |
| 10 | B | 20 | B | 30 | B | 40 | B | 50 | B |

---

## Scoring Guide

- **45-50 correct (90-100%)**: Excellent! You're well-prepared for the ACE exam.
- **40-44 correct (80-88%)**: Very good! Review topics you missed.
- **35-39 correct (70-78%)**: Good. You're near passing. Focus on weak areas.
- **30-34 correct (60-68%)**: More study needed. Review all topics systematically.
- **Below 30 (< 60%)**: Significant study required. Go through all topic guides and practice questions.

---

## Topic Distribution

This practice test covers:
- **Compute Engine**: 10 questions
- **Cloud Storage**: 8 questions
- **Networking**: 8 questions
- **GKE**: 7 questions
- **IAM & Security**: 6 questions
- **Databases**: 5 questions
- **Cloud Operations**: 4 questions
- **BigQuery**: 2 questions

---

## Next Steps

1. **Review ALL explanations** in the topic-specific practice question files for questions you got wrong
2. **Hands-on practice**: Try the commands for topics you struggled with
3. **Take Practice Test 02** after reviewing weak areas
4. **Track your progress**: Note your score and improvement areas

**Good luck with your ACE certification preparation! 🎓**
