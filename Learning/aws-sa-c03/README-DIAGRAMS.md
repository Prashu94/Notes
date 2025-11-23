# AWS SAA-C03 Exam - Mermaid Flow Diagrams Index

This directory contains comprehensive Mermaid flow diagrams for AWS Solutions Architect Associate (SAA-C03) certification exam preparation. Each diagram includes default values, configuration options, decision trees, and exam scenarios to help you remember key concepts visually.

## � Diagram Files Overview

### [Diagram 01: Compute Services](diagrams-01-compute-services.md)
**Topics Covered:** EC2, Lambda, Auto Scaling, Elastic Beanstalk  
**Diagrams:** 8 comprehensive flow diagrams
- EC2 Instance Lifecycle & States
- EC2 Purchasing Options Decision Tree
- EC2 Placement Groups Guide
- Lambda Configuration & Limits
- Lambda Integration Patterns
- Auto Scaling Policies Comparison
- Auto Scaling Lifecycle Hooks
- Elastic Beanstalk Deployment Modes

### [Diagram 02: Storage Services](diagrams-02-storage-services.md)
**Topics Covered:** S3, EBS, EFS, Storage Gateway  
**Diagrams:** 7 detailed flow diagrams
- S3 Storage Classes Decision Tree
- S3 Lifecycle Policies Flow
- S3 Replication Types
- EBS Volume Types Comparison
- EBS Snapshot Strategy
- EFS Storage Classes & Lifecycle
- Storage Service Comparison Matrix

### [Diagram 03: Database Services](diagrams-03-database-services.md)
**Topics Covered:** RDS, Aurora, DynamoDB, ElastiCache  
**Diagrams:** 6 comprehensive flow diagrams
- RDS Database Engines Selection
- RDS Multi-AZ vs Read Replicas
- Aurora Architecture & Features
- DynamoDB Capacity Modes
- DynamoDB Global Tables
- ElastiCache Redis vs Memcached

### [Diagram 04: Networking Services](diagrams-04-networking-services.md)
**Topics Covered:** VPC, ELB, Route 53, CloudFront, VPN, Direct Connect  
**Diagrams:** 5 detailed flow diagrams
- VPC Architecture & Components
- VPC Connectivity Options
- Load Balancer Selection Guide
- Route 53 Routing Policies
- CloudFront Distribution Flow

### [Diagram 05: Security & Management](diagrams-05-security-management.md)
**Topics Covered:** IAM, KMS, CloudWatch, CloudTrail, Config  
**Diagrams:** 4 comprehensive flow diagrams
- IAM Policy Evaluation Logic
- KMS Encryption Flow
- CloudWatch Metrics & Alarms
- CloudTrail vs Config vs CloudWatch

### [Diagram 06: Messaging & Additional Services](diagrams-06-messaging-additional.md)
**Topics Covered:** SNS, SQS, EventBridge, Step Functions, API Gateway  
**Diagrams:** 6+ flow diagrams including architecture patterns
- SNS vs SQS vs EventBridge
- SQS Queue Types Comparison
- Step Functions Workflow Types
- API Gateway Integration Types
- EventBridge Rules & Patterns
- Decoupled Architecture Patterns

### [Diagram 07: Additional Services](diagrams-07-additional-services.md)
**Topics Covered:** FSx, Cognito, Organizations, Security Services, CloudFormation, Storage Gateway  
**Diagrams:** 6 comprehensive flow diagrams
- FSx File Systems Decision Tree (All 4 types)
- Cognito Authentication & Authorization
- AWS Organizations Structure & SCPs
- Additional Security Services (GuardDuty, Inspector, Shield, WAF, Secrets Manager, ACM)
- Infrastructure as Code & Management (CloudFormation, Systems Manager, Trusted Advisor, Backup)
- Storage Gateway Types (File, Volume, Tape)

### [Diagram 08: Final Services](diagrams-08-final-services.md)
**Topics Covered:** Active Directory, Global Accelerator, Redshift, Comparison Charts, Exam Scenarios  
**Diagrams:** 6 essential flow diagrams
- Active Directory Services (Managed AD, AD Connector, Simple AD)
- AWS Global Accelerator vs CloudFront
- Amazon Redshift Data Warehouse (Provisioned vs Serverless)
- Service Comparison Charts (Database, Storage, Network, Security)
- Exam Scenario Decision Trees (DR, Cost, HA, Migration)
- Quick Default Values Reference

---

## 📋 Complete Service Coverage

### ☁️ Compute (Diagram 01)
- ✅ Amazon EC2 (Instances, Placement Groups, Purchasing Options)
- ✅ AWS Lambda (Configuration, Limits, Integration Patterns)
- ✅ Auto Scaling (Policies, Lifecycle Hooks, Health Checks)
- ✅ Elastic Beanstalk (Deployment Modes)

### 💾 Storage (Diagrams 02, 07)
- ✅ Amazon S3 (Storage Classes, Lifecycle, Replication, Versioning, Encryption)
- ✅ Amazon S3 Glacier (Retrieval Options, Vault Lock)
- ✅ Amazon EBS (Volume Types: gp3, io2, st1, sc1)
- ✅ Amazon EFS (Storage Classes, Lifecycle, Performance Modes)
- ✅ Amazon FSx for Windows File Server (Multi-AZ, SMB, Active Directory)
- ✅ Amazon FSx for Lustre (Scratch vs Persistent, S3 Integration)
- ✅ Amazon FSx for NetApp ONTAP (Multi-protocol, Replication)
- ✅ Amazon FSx for OpenZFS (Linux, NFS, ZFS features)
- ✅ AWS Storage Gateway - File Gateway (NFS/SMB to S3)
- ✅ AWS Storage Gateway - Volume Gateway (Cached vs Stored)
- ✅ AWS Storage Gateway - Tape Gateway (VTL, Archive to Glacier)

### 🗄️ Database & Analytics (Diagrams 03, 08)
- ✅ Amazon RDS (MySQL, PostgreSQL, MariaDB, Oracle, SQL Server)
- ✅ Amazon RDS Multi-AZ (Failover, High Availability)
- ✅ Amazon RDS Read Replicas (Scaling, Cross-Region)
- ✅ Amazon Aurora (MySQL/PostgreSQL Compatible, Global Database)
- ✅ Amazon DynamoDB (Capacity Modes, Global Tables, Streams, DAX)
- ✅ Amazon ElastiCache for Redis (Cluster Mode, Replication)
- ✅ Amazon ElastiCache for Memcached (Multi-threaded)
- ✅ Amazon Redshift (Provisioned vs Serverless, Spectrum, RA3 nodes)

### 🌐 Networking & Content Delivery (Diagrams 04, 08)
- ✅ Amazon VPC (Subnets, Route Tables, Internet Gateway, NAT Gateway)
- ✅ VPC Peering (Cross-account, Cross-region)
- ✅ AWS Transit Gateway (Hub-spoke, Multi-region)
- ✅ VPC Endpoints (Gateway Endpoints, Interface Endpoints)
- ✅ Elastic Load Balancing - ALB (Application Layer 7, HTTP/HTTPS)
- ✅ Elastic Load Balancing - NLB (Network Layer 4, TCP/UDP)
- ✅ Elastic Load Balancing - CLB (Classic, Legacy)
- ✅ Amazon Route 53 (Routing Policies, Health Checks, DNS)
- ✅ Amazon CloudFront (Edge Locations, Origins, Caching, Lambda@Edge)
- ✅ AWS Global Accelerator (Anycast IPs, TCP/UDP optimization)
- ✅ AWS Site-to-Site VPN (Customer Gateway, Virtual Private Gateway)
- ✅ AWS Direct Connect (Dedicated connection, Virtual Interfaces)
- ✅ AWS VPN Gateway (VPN connections to VPC)

### 🔐 Security, Identity & Compliance (Diagrams 05, 07, 08)
- ✅ AWS IAM (Users, Groups, Roles, Policies, MFA)
- ✅ AWS Organizations (OUs, SCPs, Consolidated Billing)
- ✅ Amazon Cognito User Pools (Authentication, MFA, Social Login)
- ✅ Amazon Cognito Identity Pools (AWS Credentials, Federated Access)
- ✅ AWS Directory Service - Managed Microsoft AD (Enterprise, Standard)
- ✅ AWS Directory Service - AD Connector (Proxy to on-premises)
- ✅ AWS Directory Service - Simple AD (Samba-based, Basic)
- ✅ AWS KMS (Key Management, Encryption, CMK, Data Keys)
- ✅ AWS Secrets Manager (Auto-rotation, Cross-region replication)
- ✅ AWS Certificate Manager (ACM) (Public/Private certificates, Auto-renewal)
- ✅ Amazon GuardDuty (Threat detection, ML-based, VPC Flow Logs)
- ✅ Amazon Inspector (Vulnerability scanning, CVE, Network exposure)
- ✅ AWS Shield Standard & Advanced (DDoS protection)
- ✅ AWS WAF (Web Application Firewall, Rules, Rate limiting)
- ✅ AWS CloudTrail (API logging, Governance, Compliance)
- ✅ AWS Config (Resource compliance, Configuration history)
- ✅ Amazon CloudWatch (Metrics, Alarms, Logs, Dashboards)

### 🔄 Integration & Messaging (Diagram 06)
- ✅ Amazon SNS (Topics, Subscriptions, Fan-out)
- ✅ Amazon SQS (Standard vs FIFO, Dead Letter Queue, Visibility Timeout)
- ✅ Amazon EventBridge (Events, Rules, Event Bus, Scheduler)
- ✅ AWS Step Functions (Standard vs Express, State Machines)
- ✅ Amazon API Gateway (REST, HTTP, WebSocket, Integration Types)

### 🛠️ Management & Governance (Diagram 07, 08)
- ✅ AWS CloudFormation (Stacks, StackSets, Drift Detection, Change Sets)
- ✅ AWS Systems Manager - Session Manager (Shell access, No SSH)
- ✅ AWS Systems Manager - Run Command (Remote execution)
- ✅ AWS Systems Manager - Patch Manager (Automated patching)
- ✅ AWS Systems Manager - Parameter Store (Configuration, Secrets)
- ✅ AWS Trusted Advisor (Cost optimization, Security, Performance)
- ✅ AWS Backup (Centralized backup, Policies, Cross-region copy)

### 📊 Total Coverage
**41 AWS Services** with **70+ comprehensive diagrams** covering all SAA-C03 exam domains!

---

## 🎯 How to Use These Diagrams

### For Visual Learning
1. **Review diagrams before reading text** - Get a visual overview first
2. **Focus on decision trees** - Understand when to use each service
3. **Note default values** - Many exam questions test knowledge of defaults
4. **Study the comparison diagrams** - Understand differences between similar services

### For Exam Preparation
1. **Review diagrams daily** - Visual repetition aids memory
2. **Cover one section at a time** - Don't overwhelm yourself
3. **Practice with scenarios** - Use the Common Architecture Patterns diagram
4. **Test yourself** - Try to draw key diagrams from memory

### Key Exam Tips Highlighted
- 💰 **Cost indicators** - Shows pricing and cost optimization opportunities
- ⚡ **Performance metrics** - Default values and limits
- ✅ **Best practices** - Recommended configurations
- 🎯 **Use cases** - When to use each service
- ⚠️ **Common pitfalls** - Things to avoid

---

## 📊 Coverage by Domain

### Domain 1: Design Resilient Architectures (26%)
- Multi-AZ deployments (RDS, ELB)
- Auto Scaling with health checks
- S3 cross-region replication
- Route 53 failover routing
- DynamoDB Global Tables
- Aurora Global Database

### Domain 2: Design High-Performing Architectures (24%)
- EBS volume types (gp3, io2)
- ElastiCache (Redis, Memcached)
- CloudFront CDN
- DynamoDB DAX
- Read Replicas
- Lambda provisioned concurrency

### Domain 3: Design Secure Applications (30%)
- IAM roles and policies
- KMS encryption (SSE-S3, SSE-KMS, SSE-C)
- VPC security (Security Groups, NACLs)
- S3 bucket policies and Block Public Access
- CloudTrail logging
- Config compliance rules

### Domain 4: Design Cost-Optimized Architectures (20%)
- EC2 purchasing options (Reserved, Spot, Savings Plans)
- S3 storage classes and lifecycle policies
- DynamoDB On-Demand vs Provisioned
- Lambda vs EC2 cost comparison
- CloudWatch cost optimization
- NAT Gateway vs NAT Instance

---

## 🚀 Quick Reference Tables

### Default Values to Memorize
| Service | Setting | Default Value |
|---------|---------|---------------|
| EC2 | Instance Tenancy | Shared |
| EC2 | Auto Scaling Health Check Grace Period | 300 seconds |
| Lambda | Timeout | 3 seconds (max 900s) |
| Lambda | Memory | 128 MB (max 10,240 MB) |
| S3 | Storage Class | Standard |
| S3 | Versioning | Disabled |
| EBS | Volume Type | gp3 |
| EBS | gp3 IOPS | 3,000 |
| RDS | Backup Retention | 7 days (max 35) |
| RDS | Multi-AZ | Disabled |
| DynamoDB | Capacity Mode | On-Demand |
| DynamoDB | Read Consistency | Eventually Consistent |
| SQS | Visibility Timeout | 30 seconds |
| SQS | Message Retention | 4 days |
| CloudWatch | EC2 Metrics | 5 minutes |
| CloudWatch | Detailed Monitoring | 1 minute |

### Service Limits to Know
| Service | Limit | Value |
|---------|-------|-------|
| VPC | Subnets per VPC | 200 |
| VPC | Security Groups per VPC | 2,500 |
| VPC | Rules per Security Group | 60 inbound, 60 outbound |
| VPC | VPC Peering Connections | 125 |
| IAM | Users per Account | 5,000 |
| IAM | Groups per Account | 300 |
| S3 | Bucket Limit per Account | 100 (soft), 1,000 (hard) |
| Lambda | Concurrent Executions | 1,000 per region |
| API Gateway | Requests per Second | 10,000 |
| DynamoDB | Item Size | 400 KB |
| SQS | Message Size | 256 KB |

---

## 📝 Study Tips

### Week 1-2: Foundation
- Focus on **Compute (EC2, Lambda)** and **Storage (S3, EBS, EFS)** diagrams
- Memorize instance types, storage classes, and pricing models
- Understand EC2 purchasing options and when to use each

### Week 3-4: Core Services
- Study **Database (RDS, DynamoDB)** and **Networking (VPC, ELB)** diagrams
- Learn Multi-AZ vs Read Replicas differences
- Master VPC components and security layers

### Week 5-6: Advanced Topics
- Review **Security (IAM, KMS)** and **Messaging (SNS, SQS)** diagrams
- Understand encryption options and key management
- Learn decoupling patterns with messaging services

### Week 7-8: Integration & Review
- Study **Common Architecture Patterns** diagram
- Practice scenario-based questions
- Review all diagrams focusing on default values and limits

---

## 🎓 Exam Day Reminders

1. **Read questions carefully** - Look for keywords like "most cost-effective", "highest performance", "most secure"
2. **Eliminate wrong answers** - Cross out obviously incorrect options
3. **Consider defaults** - Many questions test knowledge of default configurations
4. **Think about AWS best practices** - When in doubt, choose the AWS-recommended approach
5. **Time management** - Flag difficult questions and move on, come back later

---

## 📚 Additional Resources

- AWS Documentation: https://docs.aws.amazon.com/
- AWS Well-Architected Framework: https://aws.amazon.com/architecture/well-architected/
- AWS Architecture Center: https://aws.amazon.com/architecture/
- AWS Whitepapers: https://aws.amazon.com/whitepapers/

---

## ✅ Pre-Exam Checklist

- [ ] Reviewed all 6 diagram files
- [ ] Memorized default values from Quick Reference table
- [ ] Practiced drawing key architecture patterns from memory
- [ ] Understand when to use each service (decision trees)
- [ ] Reviewed Common Architecture Patterns diagram
- [ ] Can explain Multi-AZ vs Read Replicas
- [ ] Know all S3 storage classes and use cases
- [ ] Understand IAM policy evaluation logic
- [ ] Can calculate DynamoDB RCU/WCU
- [ ] Familiar with VPC security layers

---

**Good luck with your AWS SAA-C03 exam! 🚀**

*Remember: These diagrams are designed to complement your study materials, not replace them. Use them as visual aids to reinforce concepts from the official AWS documentation and your study guides.*
