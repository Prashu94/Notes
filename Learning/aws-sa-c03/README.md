# AWS Certified Solutions Architect – Associate (SAA-C03) Study Guide

A comprehensive, exam-aligned learning resource covering **49+ AWS services**, visual diagrams, practice tests, and deep conceptual explanations. Based on the [official AWS SAA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html).

---

## Exam Overview

| Item | Details |
|------|---------|
| **Exam code** | SAA-C03 |
| **Duration** | 130 minutes |
| **Scored questions** | 50 (plus 15 unscored) |
| **Question types** | Multiple choice, multiple response |
| **Passing score** | 720 / 1000 (scaled) |
| **Target experience** | 1+ year designing AWS solutions |
| **Cost** | ~$150 USD (varies by region) |

The exam validates your ability to **design solutions** using the **AWS Well-Architected Framework** — not to memorize trivia, but to choose the right service for a scenario.

---

## Four Exam Domains

| Domain | Weight | Focus |
|--------|--------|-------|
| **1. Design Secure Architectures** | 30% | IAM, encryption, VPC security, compliance, data protection |
| **2. Design Resilient Architectures** | 26% | HA, fault tolerance, DR, decoupling, scaling |
| **3. Design High-Performing Architectures** | 24% | Compute, storage, database, network, data ingestion performance |
| **4. Design Cost-Optimized Architectures** | 20% | Pricing models, right-sizing, lifecycle policies, transfer costs |

### Domain → Guide Mapping

#### Domain 1: Secure Architectures (30%)
- [IAM](aws-iam-saa-c03-guide.md) · [KMS](aws-kms-saa-c03-guide.md) · [Secrets Manager](aws-secrets-manager-saa-c03-guide.md) · [ACM](aws-certificate-manager-saa-c03-guide.md)
- [VPC Security](aws-vpc-saa-c03-guide.md) · [WAF & Shield](aws-waf-shield-saa-c03-guide.md) · [GuardDuty](aws-guardduty-saa-c03-guide.md) · [Inspector](aws-inspector-saa-c03-guide.md) · [Macie](aws-macie-saa-c03-guide.md)
- [Cognito](aws-cognito-saa-c03-guide.md) · [Organizations](aws-organizations-saa-c03-guide.md) · [Config](aws-config-saa-c03-guide.md) · [CloudTrail](aws-cloudtrail-saa-c03-guide.md)

#### Domain 2: Resilient Architectures (26%)
- [EC2 & Auto Scaling](aws-ec2-saa-c03-guide.md) · [EC2 Scaling](aws-ec2-scaling-saa-c03-guide.md) · [Lambda](aws-lambda-saa-c03-guide.md) · [ECS/EKS/Fargate](aws-ecs-eks-fargate-saa-c03-guide.md)
- [ELB](aws-elb-saa-c03-guide.md) · [Route 53](aws-route53-saa-c03-guide.md) · [SQS](aws-sqs-saa-c03-guide.md) · [SNS](aws-sns-saa-c03-guide.md) · [EventBridge](aws-eventbridge-saa-c03-guide.md)
- [RDS Multi-AZ & Replicas](aws-rds-saa-c03-guide.md) · [Aurora](aws-aurora-saa-c03-guide.md) · [DynamoDB Global Tables](aws-dynamodb-saa-c03-guide.md) · [Backup](aws-backup-saa-c03-guide.md)

#### Domain 3: High-Performing Architectures (24%)
- [S3 & Glacier](aws-s3-and-glacier-saa-c03-guide.md) · [EBS](aws-ebs-saa-c03-guide.md) · [EFS](aws-efs-saa-c03-guide.md) · [FSx](aws-fsx-saa-c03-guide.md)
- [DynamoDB](aws-dynamodb-saa-c03-guide.md) · [ElastiCache](aws-elasticache-saa-c03-guide.md) · [Redshift](aws-redshift-saa-c03-guide.md)
- [CloudFront](aws-cloudfront-saa-c03-guide.md) · [Global Accelerator](aws-global-accelerator-saa-c03-guide.md) · [Networking](aws-networking-saa-c03-guide.md)
- [Kinesis](aws-kinesis-saa-c03-guide.md) · [Athena](aws-athena-saa-c03-guide.md) · [Glue](aws-glue-saa-c03-guide.md)

#### Domain 4: Cost-Optimized Architectures (20%)
- [EC2 Pricing](aws-ec2-saa-c03-guide.md) · [S3 Lifecycle & Storage Classes](aws-s3-and-glacier-saa-c03-guide.md)
- [Trusted Advisor](aws-trusted-advisor-saa-c03-guide.md) · [CloudWatch](aws-cloudwatch-saa-c03-guide.md)
- See [Concepts Deep Dive – Cost Optimization](CONCEPTS-DEEP-DIVE.md#cost-optimization-decision-framework)

---

## Start Here: Conceptual Foundations

Before diving into individual services, read these — they explain *why* exam answers are what they are:

1. **[Well-Architected Framework Guide](aws-well-architected-framework-saa-c03-guide.md)** — The lens AWS uses to evaluate every scenario
2. **[Concepts Deep Dive](CONCEPTS-DEEP-DIVE.md)** — Shared concepts that appear across multiple services:
   - Shared responsibility model
   - Multi-AZ vs Multi-Region vs Read Replicas
   - Security Groups vs NACLs (stateful vs stateless)
   - Gateway vs Interface VPC endpoints
   - Synchronous vs asynchronous integration
   - DR strategies (Backup/Restore → Pilot Light → Warm Standby → Active-Active)
   - EC2 pricing models (On-Demand, RI, Savings Plans, Spot)
   - Database selection decision tree

---

## 4-Week Study Plan

### Week 1 — Core Infrastructure (Highest ROI)
| Day | Topics | Guides |
|-----|--------|--------|
| 1–2 | IAM, KMS, Well-Architected | IAM, KMS, Well-Architected |
| 3–4 | VPC, Security Groups, Endpoints | VPC, Networking |
| 5–6 | S3, EBS, EFS | S3, EBS, EFS |
| 7 | Practice Test 01 (Compute) + review | `practice-tests/` |

### Week 2 — Compute, Databases, Messaging
| Day | Topics | Guides |
|-----|--------|--------|
| 1–2 | EC2, Auto Scaling, Lambda | EC2, Scaling, Lambda |
| 3–4 | RDS, Aurora, DynamoDB | RDS, Aurora, DynamoDB |
| 5 | SQS, SNS, EventBridge | Messaging guides |
| 6–7 | Practice Tests 02–03 + review | Storage, Database |

### Week 3 — Networking, Security, Integration
| Day | Topics | Guides |
|-----|--------|--------|
| 1–2 | ELB, Route 53, CloudFront, Global Accelerator | Networking guides |
| 3–4 | WAF, GuardDuty, Cognito, Organizations | Security guides |
| 5–6 | API Gateway, CloudFormation, Systems Manager | Integration, IaC |
| 7 | Practice Tests 04–05 | Networking, Security |

### Week 4 — Advanced Services & Exam Strategy
| Day | Topics | Guides |
|-----|--------|--------|
| 1–2 | Kinesis, Athena, Glue, DataSync, Snow | Analytics, Migration |
| 3 | DR, HA patterns, cost optimization | Concepts Deep Dive, Diagrams 08 |
| 4–5 | All diagram files + weak-area review | `diagrams-*.md` |
| 6–7 | Practice Tests 06–07, timed full review | All practice tests |

**Target:** 85%+ on practice tests across all four domains before booking the exam.

---

## Visual Diagrams

See [README-DIAGRAMS.md](README-DIAGRAMS.md) for **70+ Mermaid diagrams** organized by category:

| File | Coverage |
|------|----------|
| `diagrams-01-compute-services.md` | EC2, Lambda, Auto Scaling |
| `diagrams-02-storage-services.md` | S3, EBS, EFS, Glacier |
| `diagrams-03-database-services.md` | RDS, Aurora, DynamoDB |
| `diagrams-04-networking-services.md` | VPC, ELB, Route 53 |
| `diagrams-05-security-management.md` | IAM, KMS, CloudWatch |
| `diagrams-06-messaging-additional.md` | SNS, SQS, EventBridge |
| `diagrams-07-additional-services.md` | FSx, Cognito, Organizations, WAF |
| `diagrams-08-final-services.md` | DR trees, cost optimization, comparisons |

---

## Practice Tests

Seven domain-aligned practice tests in `practice-tests/`:

| Test | Domain | Questions |
|------|--------|-----------|
| 01 | Compute Services | 20 |
| 02 | Storage Services | 20 |
| 03 | Database Services | 20 |
| 04 | Networking Services | 20 |
| 05 | Security & Identity | 20 |
| 06 | Management & Governance | 20 |
| 07 | Application Integration | 20 |

Each test includes detailed answer explanations in `answers.md`.

---

## Exam Strategy

### How to Read Scenario Questions

1. **Underline constraints:** cost, latency, compliance, operational overhead, RTO/RPO
2. **Eliminate wrong answers first:** transitive peering, multiple IGWs, wrong storage class transitions
3. **Prefer managed services** when the question asks for "least operational overhead"
4. **Prefer roles over users** for application and cross-account access
5. **Always consider Multi-AZ** for production HA unless cost is the primary constraint

### High-Frequency "Answer Patterns"

| Keyword in question | Likely answer direction |
|--------------------|------------------------|
| "Least operational overhead" | Managed service (RDS not EC2 DB, Fargate not ECS on EC2) |
| "Most cost-effective" | Spot, S3 lifecycle, Gateway endpoint, Intelligent-Tiering |
| "Highly available" | Multi-AZ, Auto Scaling across 2+ AZs, Route 53 health checks |
| "Disaster recovery" | Match RTO/RPO to DR tier (see Concepts Deep Dive) |
| "Secure cross-account" | IAM role + trust policy + external ID |
| "Reduce data transfer cost" | VPC Gateway endpoint, CloudFront, same-AZ traffic |
| "Unpredictable access patterns" | S3 Intelligent-Tiering, DynamoDB on-demand |
| "Global low latency" | CloudFront (HTTP/S), Global Accelerator (TCP/UDP) |

### Services That Appear Most Often

1. **S3** — storage classes, lifecycle, encryption, replication
2. **EC2 + Auto Scaling + ELB** — instance types, ALB vs NLB, scaling policies
3. **VPC** — subnets, NAT, endpoints, SG vs NACL
4. **RDS + Aurora + DynamoDB** — Multi-AZ vs replicas, access patterns
5. **IAM** — roles, policies, federation, SCPs
6. **SQS + SNS + EventBridge** — decoupling, FIFO, DLQ, fan-out

---

## Official Resources

- [SAA-C03 Exam Guide (PDF)](https://docs.aws.amazon.com/pdfs/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.pdf)
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [AWS Free Tier](https://aws.amazon.com/free/) — hands-on practice
- [AWS Skill Builder](https://skillbuilder.aws/) — official training paths

---

## Repository Structure

```
aws-sa-c03/
├── README.md                          ← You are here
├── CONCEPTS-DEEP-DIVE.md              ← Cross-service concepts explained in depth
├── aws-well-architected-framework-saa-c03-guide.md
├── COVERAGE-SUMMARY.md                ← Full service index
├── README-DIAGRAMS.md                 ← Diagram index
├── aws-*-saa-c03-guide.md             ← 49+ service guides
├── diagrams-*.md                      ← Visual study aids
└── practice-tests/                    ← 7 practice tests with answers
```

Good luck with your certification! 📚
