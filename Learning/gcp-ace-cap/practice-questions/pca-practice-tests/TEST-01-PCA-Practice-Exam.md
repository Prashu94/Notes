# GCP Professional Cloud Architect Practice Test 01

## Exam Instructions

- **Total Questions**: 50
- **Time Limit**: 2 hours (120 minutes)
- **Passing Score**: 70% (35 correct answers)
- **Format**: Scenario-based, architectural decision questions
- **Difficulty**: Professional level

**Note**: PCA exam focuses on designing complete solutions, not just configuring individual services.

---

## Questions

### Question 1
Your company is migrating a monolithic application to GCP. The application has:
- Web tier with session state
- Application tier (CPU-intensive)
- PostgreSQL database (5TB)
- Current: 50,000 daily active users
- Requirement: 99.95% availability, auto-scaling

Which migration strategy and architecture should you recommend?

**A)** Lift-and-shift to Compute Engine, then modernize later
**B)** Refactor to microservices on GKE, Cloud SQL HA, Cloud Memorystore for sessions
**C)** Replatform to App Engine Flexible, Cloud SQL, Cloud Memorystore
**D)** Rebuild as serverless with Cloud Run, Cloud SQL, Firestore

**Answer**: B

---

### Question 2
A financial services company requires:
- Data must stay in EU
- Customer-managed encryption keys
- 99.99% availability
- Real-time fraud detection
- Complete audit trail for 10 years

Which database solution meets ALL requirements?

**A)** Cloud SQL PostgreSQL multi-region
**B)** Cloud Spanner EUR3 configuration with CMEK
**C)** Firestore with CMEK
**D)** Bigtable in EU region

**Answer**: B

---

### Question 3
Your IoT platform receives 100,000 messages/second from devices globally. You need real-time dashboards and historical analysis. Which architecture is most appropriate?

**A)** Devices → Load Balancer → Compute Engine → Cloud SQL → Data Studio
**B)** Devices → Cloud IoT Core → Pub/Sub → Dataflow (streaming) → BigQuery → Looker
**C)** Devices → Cloud Functions → Firestore → Cloud Run
**D)** Devices → API Gateway → Cloud Run → Bigtable → BigQuery

**Answer**: B

---

### Question 4
You need to design a disaster recovery solution with RPO=15 minutes and RTO=1 hour for a critical application. Which approach is most suitable?

**A)** Daily backups to Cloud Storage in another region
**B)** Hot standby: Active-passive with Cloud SQL HA and cross-region read replica, automated failover
**C)** Cold standby: Weekly snapshots, manual restoration
**D)** Warm standby: Pilot light with minimal resources, manual scaling on failover

**Answer**: B

---

### Question 5
Your application needs to process 10TB of data daily using Apache Spark. Cost optimization is critical. Which service should you use?

**A)** Dataproc cluster running 24/7
**B)** Dataproc with autoscaling and scheduled deletion
**C)** Dataflow batch jobs
**D)** Compute Engine with manual Spark installation

**Answer**: B

---

### Question 6
A gaming company needs to migrate their leaderboard system handling 1 million writes/second globally with single-digit millisecond latency. Which database should you recommend?

**A)** Cloud SQL with read replicas
**B)** Cloud Spanner multi-region
**C)** Bigtable with multiple clusters worldwide
**D)** Firestore in Datastore mode

**Answer**: C

---

### Question 7
Your company has a hybrid environment with on-premises datacenter and GCP. You need private, high-bandwidth (10Gbps+) connectivity. Which solution should you choose?

**A)** Cloud VPN with multiple tunnels
**B)** Dedicated Interconnect with 10Gbps connection
**C)** Partner Interconnect through service provider
**D)** Direct Peering

**Answer**: B

---

### Question 8
You need to implement a CI/CD pipeline for containerized applications with automated testing, security scanning, and deployment to multiple environments (dev, staging, prod). Which services should you use?

**A)** Cloud Build + Binary Authorization + GKE + Cloud Deploy
**B)** Jenkins on Compute Engine + GKE
**C)** Cloud Functions + Cloud Run
**D)** GitHub Actions + Cloud Run

**Answer**: A

---

### Question 9
Your application stores PII data in BigQuery. You need to implement column-level security where specific users can see email addresses as "***@example.com". What should you implement?

**A)** Authorized views with SQL functions to mask data
**B)** BigQuery column-level security policies
**C)** Data Loss Prevention (DLP) API with de-identification
**D)** IAM policies with dataset access

**Answer**: A

---

### Question 10
A media company needs to transcode 1PB of video files stored in Cloud Storage. The process is not time-sensitive but must be cost-effective. What should you use?

**A)** Compute Engine standard instances
**B)** Preemptible VMs with checkpointing and retry logic
**C)** Cloud Functions processing files
**D)** Cloud Run jobs

**Answer**: B

---

### Question 11
Your organization has multiple projects and needs centralized VPC management with subnet sharing across projects. What should you implement?

**A)** VPC Peering between all projects
**B)** Shared VPC with host and service projects
**C)** Independent VPCs with VPN connections
**D)** Organization-level default VPC

**Answer**: B

---

### Question 12
You need to ensure all Compute Engine VMs use specific custom images and cannot use public images. How should you enforce this?

**A)** IAM policies preventing image access
**B)** Organization Policy constraint requiring trusted images
**C)** Custom scripts on all VMs
**D)** VPC firewall rules

**Answer**: B

---

### Question 13
Your application requires a NoSQL database for user sessions with:
- Global distribution
- Strong consistency
- Automatic multi-region replication
- Less than 10ms latency

Which database should you use?

**A)** Firestore in Native mode
**B)** Cloud Spanner
**C)** Bigtable
**D)** Memorystore for Redis Cluster

**Answer**: B

---

### Question 14
You need to migrate 500TB of data from on-premises to Cloud Storage in one week. Internet bandwidth is limited to 1Gbps. What method should you use?

**A)** gsutil rsync over internet
**B)** Storage Transfer Service over VPN
**C)** Transfer Appliance (physical device)
**D)** Third-party transfer tool

**Answer**: C

---

### Question 15
Your GKE application needs to access Cloud SQL. The connection should be secure and not require managing IP addresses. What should you use?

**A)** Public IP with authorized networks
**B)** Private IP with Private Service Access
**C)** Cloud SQL Proxy as sidecar container
**D)** VPN tunnel

**Answer**: C

---

### Question 16
A healthcare application must comply with HIPAA. Which GCP features should you implement? (Choose ALL that apply)

**A)** Sign Business Associate Agreement (BAA) with Google
**B)** Enable Cloud Audit Logs - Data Access
**C)** Use CMEK for encryption
**D)** All of the above

**Answer**: D

---

### Question 17
You need to load balance TCP traffic for a non-HTTP application with SSL termination and global distribution. Which load balancer should you use?

**A)** Network Load Balancer
**B)** HTTP(S) Load Balancer
**C)** SSL Proxy Load Balancer (global)
**D)** Internal TCP/UDP Load Balancer

**Answer**: C

---

### Question 18
Your Cloud Run service experiences traffic spikes. You need to ensure it can handle 10,000 concurrent requests. What should you configure?

**A)** Increase memory allocation
**B)** Set max instances to 10,000 and configure concurrency
**C)** Use Cloud Functions instead
**D)** Scale manually based on metrics

**Answer**: B

---

### Question 19
You need to implement a data pipeline: Cloud Storage → Transform → BigQuery with exactly-once processing guarantee. Which service should you use?

**A)** Cloud Functions
**B)** Dataflow with deduplication
**C)** Cloud Composer (Airflow)
**D)** Pub/Sub + Cloud Run

**Answer**: B

---

### Question 20
Your organization requires all API calls to be logged and monitored for unusual activity. Which combination should you implement?

**A)** Cloud Audit Logs + Cloud Logging + Log Analytics
**B)** Cloud Trace only
**C)** Custom application logging
**D)** VPC Flow Logs only

**Answer**: A

---

### Question 21
A machine learning model needs to process real-time predictions with <100ms latency for 1 million requests/day. Which deployment option is most suitable?

**A)** Vertex AI Online Prediction with autoscaling
**B)** Batch predictions in BigQuery ML
**C)** Cloud Functions with TensorFlow
**D)** Vertex AI Batch Prediction

**Answer**: A

---

### Question 22
You need to ensure kubernetes secrets are encrypted with your own keys in GKE. What should you enable?

**A)** Application-layer secret encryption
**B)** CMEK for GKE cluster (application-layer secrets encryption)
**C)** Encrypt secrets before storing
**D)** Use external secret manager only

**Answer**: B

---

### Question 23
Your application uses multiple GCP services (Compute Engine, Cloud Storage, BigQuery). You need to grant a service account minimum required permissions. What approach should you use?

**A)** Grant Editor role at project level
**B)** Grant predefined roles per service (Compute Admin, Storage Object Admin, BigQuery Data Editor)
**C)** Create single custom role with specific permissions needed
**D)** Use basic roles (Owner, Editor, Viewer)

**Answer**: C

---

### Question 24
You need to route traffic to different GKE services based on HTTP path (/api → API service, /web → Web service). What should you configure?

**A)** Multiple load balancers
**B)** Kubernetes Ingress with path-based routing
**C)** Network Load Balancer
**D)** Multiple Cloud Run services

**Answer**: B

---

### Question 25
Your Cloud Storage bucket contains sensitive data. You need to ensure it cannot be accessed from outside your VPC. What should you implement?

**A)** Bucket-level IAM policies
**B)** VPC Service Controls perimeter
**C)** Signed URLs only
**D)** Make bucket private

**Answer**: B

---

### Question 26
You need to analyze logs in real-time to detect security threats. Which architecture is most appropriate?

**A)** Cloud Logging → Log sink → Pub/Sub → Dataflow → BigQuery → Alert
**B)** Cloud Logging → BigQuery → Manual queries
**C)** Export logs to Cloud Storage → Batch processing
**D)** Cloud Logging → Cloud Functions → Email alerts

**Answer**: A

---

### Question 27
Your multi-tier application requires database transactions across multiple services. Which pattern should you implement?

**A)** Distributed transactions with two-phase commit
**B)** Saga pattern with compensating transactions
**C)** Single database for all services
**D)** Eventual consistency without transactions

**Answer**: B

---

### Question 28
You need to provide temporary elevated access to production for incident response. Which IAM feature should you use?

**A)** Grant permanent elevated permissions
**B)** Just-in-time access with time-bound IAM conditions
**C)** Share service account keys temporarily
**D)** Create temporary user account

**Answer**: B

---

### Question 29
Your application needs to fan-out messages to multiple subscribers with guaranteed delivery. Which service should you use?

**A)** Cloud Pub/Sub with multiple subscriptions
**B)** Cloud Tasks
**C)** HTTP endpoints
**D)** Firestore real-time listeners

**Answer**: A

---

### Question 30
You need to implement blue/green deployment for a GKE application with instant rollback capability. What approach should you use?

**A)** Rolling update strategy
**B)** Split traffic between two deployments using Service with multiple backends
**C)** Recreate strategy
**D)** Canary deployment with gradual rollout

**Answer**: B

---

### Question 31
A SaaS company needs to isolate customer data while sharing the same application infrastructure. What architecture should you use?

**A)** Separate projects per customer
**B)** Multi-tenant architecture with VPC Service Controls and row-level security
**C)** Separate GCP organizations per customer
**D)** Separate cloud providers per customer

**Answer**: B

---

### Question 32
You need to optimize BigQuery costs for a dataset queried frequently but with most data older than 90 days. What should you implement?

**A)** Delete old data
**B)** Partition by date and cluster tables, use date filters in queries
**C)** Export to Cloud Storage
**D)** Use multiple tables by date

**Answer**: B

---

### Question 33
Your application needs a message queue with task deduplication and scheduling. Which service should you use?

**A)** Cloud Pub/Sub
**B)** Cloud Tasks
**C)** Cloud Scheduler + Pub/Sub
**D)** Cloud Functions with delays

**Answer**: B

---

### Question 34
You need to implement network micro-segmentation in GKE to control pod-to-pod communication. What should you use?

**A)** VPC firewall rules
**B)** Kubernetes Network Policies
**C)** Cloud Armor
**D)** Service mesh (Anthos Service Mesh)

**Answer**: B

---

### Question 35
Your organization requires audit logs be immutable for 7 years for compliance. What should you implement?

**A)** Export to BigQuery with locked tables
**B)** Export to Cloud Storage with retention policy and bucket lock
**C)** Keep in Cloud Logging (max 30 days)
**D)** Export to external system

**Answer**: B

---

### Question 36
You need to deploy a stateful application in GKE that requires persistent storage and stable network identity. Which Kubernetes resource should you use?

**A)** Deployment
**B)** StatefulSet
**C)** DaemonSet
**D)** Job

**Answer**: B

---

### Question 37
Your application reads data from Cloud Storage in a hot loop. How can you optimize costs?

**A)** Use Nearline storage class
**B)** Enable Cloud CDN for Cloud Storage
**C)** Implement application-level caching (Memorystore)
**D)** Use Archive storage class

**Answer**: C

---

### Question 38
You need to ensure all GKE nodes are automatically patched and updated with minimal disruption. What should you enable?

**A)** Manual node upgrades
**B)** Auto-upgrade with maintenance windows and surge upgrades
**C)** Delete and recreate cluster regularly
**D)** Custom scripts for patching

**Answer**: B

---

### Question 39
Your application requires DNS resolution of custom domains within your VPC. What should you create?

**A)** Cloud DNS private managed zone
**B)** /etc/hosts on each VM
**C)** External DNS server
**D)** Public Cloud DNS zone

**Answer**: A

---

### Question 40
You need to implement least privilege for Cloud Functions accessing BigQuery. What should you grant?

**A)** BigQuery Admin role
**B)** Predefined role: BigQuery Data Viewer
**C)** Custom role with only required permissions (bigquery.tables.getData)
**D)** Project Editor role

**Answer**: C

---

### Question 41
Your Cloud SQL instance is approaching storage limit. What is the recommended action?

**A)** Delete old data
**B)** Increase storage (automatic, no downtime)
**C)** Create new instance and migrate
**D)** Archive to Cloud Storage

**Answer**: B

---

### Question 42
You need to implement request tracing across microservices to debug latency issues. What should you use?

**A)** Cloud Logging only
**B)** Cloud Trace with distributed tracing
**C)** Cloud Monitoring metrics
**D)** Application-level logging

**Answer**: B

---

### Question 43
Your application requires 99.99% availability. Which Cloud SQL configuration meets this requirement?

**A)** Single instance with backups
**B)** High availability (HA) regional configuration
**C)** Read replicas
**D)** Cloud SQL doesn't provide 99.99% SLA (max 99.95%)

**Answer**: D

---

### Question 44
You need to migrate a MongoDB database to GCP. Which service should you use?

**A)** Cloud SQL (doesn't support MongoDB)
**B)** Firestore in Datastore mode
**C)** MongoDB Atlas on GCP Marketplace or Compute Engine
**D)** Bigtable

**Answer**: C

---

### Question 45
Your GKE cluster needs to scale from 10 to 100 nodes based on pod demand. What should you enable?

**A)** Manual scaling
**B)** Cluster Autoscaler
**C)** Horizontal Pod Autoscaler
**D)** Vertical Pod Autoscaler

**Answer**: B

---

### Question 46
You need to implement data lifecycle management for Cloud Storage: hot data in Standard, data >30 days in Nearline, data >90 days in Coldline. What should you use?

**A)** Manual scripts
**B)** Object Lifecycle Management policies
**C)** Cloud Scheduler + Cloud Functions
**D)** Dataflow pipeline

**Answer**: B

---

### Question 47
Your application requires consistent hashing for session distribution across instances. Which load balancer feature should you use?

**A)** Round robin
**B)** Session affinity (client IP or generated cookie)
**C)** Random distribution
**D)** Least connections

**Answer**: B

---

### Question 48
You need to scan container images for vulnerabilities before deploying to GKE. What should you use?

**A)** Manual security reviews
**B)** Container Analysis + Binary Authorization
**C)** Third-party scanners only
**D)** Runtime scanning only

**Answer**: B

---

### Question 49
Your organization requires all data in transit be encrypted. Which GCP features provide this by default?

**A)** HTTPS/TLS for external traffic only
**B)** All Google Cloud services encrypt data in transit automatically
**C)** Manual VPN configuration required
**D)** Encryption only at rest, not in transit

**Answer**: B

---

### Question 50
You need to implement a data warehouse for analytics with SQL compatibility, petabyte scale, and serverless operation. Which service should you use?

**A)** Cloud SQL
**B)** Cloud Spanner
**C)** BigQuery
**D)** Bigtable

**Answer**: C

---

## Answer Key

| Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer | Q# | Answer |
|----|--------|----|----|----|----|----|----|----|----|
| 1  | B | 11 | B | 21 | A | 31 | B | 41 | B |
| 2  | B | 12 | B | 22 | B | 32 | B | 42 | B |
| 3  | B | 13 | B | 23 | C | 33 | B | 43 | D |
| 4  | B | 14 | C | 24 | B | 34 | B | 44 | C |
| 5  | B | 15 | C | 25 | B | 35 | B | 45 | B |
| 6  | C | 16 | D | 26 | A | 36 | B | 46 | B |
| 7  | B | 17 | C | 27 | B | 37 | C | 47 | B |
| 8  | A | 18 | B | 28 | B | 38 | B | 48 | B |
| 9  | A | 19 | B | 29 | A | 39 | A | 49 | B |
| 10 | B | 20 | A | 30 | B | 40 | C | 50 | C |

**Score: ___/50**

---

## Topic Distribution

- **Architecture & Migration**: 8 questions
- **Security & Compliance**: 8 questions
- **GKE & Containers**: 8 questions
- **Data & Analytics**: 7 questions
- **Networking**: 6 questions
- **Operations & Cost Optimization**: 6 questions
- **Storage & Databases**: 5 questions
- **Serverless**: 2 questions

---

## Scoring Guide

- **45-50 (90-100%)**: Excellent! Ready for PCA exam
- **40-44 (80-88%)**: Very good! Review missed concepts
- **35-39 (70-78%)**: Passing level, more study needed
- **30-34 (60-68%)**: Significant review required
- **<30 (<60%)**: Study all topics systematically

---

**Test completed on**: __________
**Time taken**: __________ minutes
**Topics to review**: _________________________

---

## Next Steps

1. Review explanations in topic-specific guides for questions you missed
2. Study architectural patterns and trade-offs
3. Practice designing complete solutions, not just service configurations
4. Take PCA Practice Test 02 after reviewing weak areas

**Remember**: PCA exam tests your ability to design complete, production-ready architectures!
