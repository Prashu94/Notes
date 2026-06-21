# AWS Certified Developer – Associate (DVA-C02) Study Guide

A comprehensive, exam-aligned learning resource for developers building, deploying, securing, and troubleshooting applications on AWS. Based on the [official AWS DVA-C02 exam guide](https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html) (Version 2.1, December 2024).

---

## Exam Overview

| Item | Details |
|------|---------|
| **Exam code** | DVA-C02 |
| **Duration** | 130 minutes |
| **Scored questions** | 50 (plus 15 unscored) |
| **Question types** | Multiple choice, multiple response |
| **Passing score** | 720 / 1000 (scaled) |
| **Target experience** | 1+ year developing/maintaining AWS applications |
| **Cost** | ~$150 USD (varies by region) |

### What This Exam Tests

Unlike the Solutions Architect exam (which focuses on **designing** architectures), the Developer exam focuses on **building and operating** applications:

- Writing code that integrates with AWS service APIs and SDKs
- Configuring Lambda, API Gateway, DynamoDB, and messaging services
- Implementing authentication, encryption, and secrets management in code
- Packaging, testing, and deploying with CI/CD pipelines
- Debugging with logs, metrics, and traces

### What's Out of Scope

Per the official exam guide, you are **not** tested on:
- Designing full system architectures
- Creating CI/CD pipelines from scratch (using them, yes)
- IAM user/group administration
- Server OS administration
- VPC/Direct Connect network design

---

## Four Exam Domains

| Domain | Weight | Focus |
|--------|--------|-------|
| **1. Development with AWS Services** | 32% | Lambda, API Gateway, DynamoDB, messaging, event-driven patterns |
| **2. Security** | 26% | Cognito, IAM roles, KMS, Secrets Manager, encryption in code |
| **3. Deployment** | 24% | SAM, CloudFormation, CodePipeline, CodeBuild, CodeDeploy, deployment strategies |
| **4. Troubleshooting & Optimization** | 18% | CloudWatch, X-Ray, concurrency tuning, caching, root cause analysis |

---

## Study Path

### Phase 1 — Foundations (Week 1)
1. Read [Concepts Deep Dive](CONCEPTS-DEEP-DIVE.md) — developer-focused patterns
2. [Domain 1 Guide](domain-01-development-with-aws-services.md) — architectural patterns overview
3. [Lambda Guide](aws-lambda-dva-c02-guide.md) — highest-weight service
4. [DynamoDB Guide](aws-dynamodb-dva-c02-guide.md) — data modeling for developers
5. [API Gateway Guide](aws-api-gateway-dva-c02-guide.md) — REST APIs, authorizers, stages

### Phase 2 — Integration & Security (Week 2)
1. [Messaging Guide](aws-messaging-dva-c02-guide.md) — SQS, SNS, EventBridge, Step Functions
2. [Cognito & Security Guide](aws-security-dva-c02-guide.md) — auth, encryption, secrets
3. [Domain 2 Guide](domain-02-security.md)
4. Practice Test 01 + 02

### Phase 3 — Deployment (Week 3)
1. [CI/CD & IaC Guide](aws-cicd-dva-c02-guide.md) — SAM, CloudFormation, CodePipeline, CodeDeploy
2. [Domain 3 Guide](domain-03-deployment.md)
3. Practice Test 03

### Phase 4 — Operations & Exam Prep (Week 4)
1. [Observability Guide](aws-observability-dva-c02-guide.md) — CloudWatch, X-Ray, structured logging
2. [Domain 4 Guide](domain-04-troubleshooting-and-optimization.md)
3. Practice Tests 04 + full timed review
4. Review [Exam Strategy](#exam-strategy) below

**Target:** 85%+ on practice tests across all four domains before booking.

---

## Service Guides

| Guide | Exam relevance |
|-------|---------------|
| [Lambda](aws-lambda-dva-c02-guide.md) | ⭐⭐⭐ Core — configuration, events, VPC, layers, destinations |
| [DynamoDB](aws-dynamodb-dva-c02-guide.md) | ⭐⭐⭐ Core — keys, indexes, consistency, SDK patterns |
| [API Gateway](aws-api-gateway-dva-c02-guide.md) | ⭐⭐⭐ Core — REST, stages, authorizers, caching, throttling |
| [Messaging](aws-messaging-dva-c02-guide.md) | ⭐⭐⭐ SQS, SNS, EventBridge, Step Functions |
| [Security](aws-security-dva-c02-guide.md) | ⭐⭐⭐ Cognito, IAM, KMS, Secrets Manager, STS |
| [CI/CD & IaC](aws-cicd-dva-c02-guide.md) | ⭐⭐⭐ SAM, CloudFormation, CodePipeline, deployment strategies |
| [Observability](aws-observability-dva-c02-guide.md) | ⭐⭐ CloudWatch, X-Ray, EMF, structured logging |

### Domain Guides (Task-Level Coverage)

| Guide | Maps to |
|-------|---------|
| [Domain 1 — Development](domain-01-development-with-aws-services.md) | All Task 1.x skills |
| [Domain 2 — Security](domain-02-security.md) | All Task 2.x skills |
| [Domain 3 — Deployment](domain-03-deployment.md) | All Task 3.x skills |
| [Domain 4 — Troubleshooting](domain-04-troubleshooting-and-optimization.md) | All Task 4.x skills |

---

## In-Scope Services (Official List)

**Compute:** EC2, Elastic Beanstalk, Lambda  
**Containers:** ECR, ECS, EKS  
**Database:** Aurora, DynamoDB, ElastiCache, RDS  
**Integration:** AppSync, EventBridge, SNS, SQS, Step Functions  
**Developer Tools:** Amplify, CloudShell, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, X-Ray, Amazon Q Developer  
**Management:** AppConfig, CDK, CloudFormation, CloudTrail, CloudWatch, CLI, Systems Manager  
**Networking:** API Gateway, CloudFront, ELB, Route 53, VPC  
**Security:** Cognito, IAM, KMS, Secrets Manager, STS, WAF  
**Storage:** EBS, EFS, S3  
**Analytics:** Athena, Kinesis, OpenSearch  

---

## Exam Strategy

### High-Frequency Topics (~50%+ of questions)

1. **Lambda** — memory, timeout, concurrency, DLQ, destinations, VPC config, environment variables, layers
2. **DynamoDB** — partition keys, GSI/LSI, query vs scan, consistency, on-demand vs provisioned
3. **API Gateway** — stages, deployments, Lambda proxy integration, Cognito authorizer, caching, throttling
4. **SQS/SNS** — Standard vs FIFO, visibility timeout, DLQ, fan-out pattern, filter policies
5. **Cognito** — User Pools vs Identity Pools, JWT tokens, API Gateway integration
6. **CI/CD** — SAM templates, CodePipeline stages, CodeDeploy deployment types (blue/green, in-place)
7. **IAM** — execution roles vs task roles, assume role, resource policies, least privilege in code

### Keyword → Answer Patterns

| Keyword | Likely direction |
|---------|-----------------|
| "Least privilege for Lambda" | Execution role with minimal permissions |
| "Temporary AWS credentials in mobile app" | Cognito Identity Pool + STS |
| "User sign-up and sign-in" | Cognito User Pool |
| "Exactly-once message processing" | SQS FIFO queue |
| "Fan-out to multiple consumers" | SNS → multiple SQS queues |
| "Schedule recurring tasks" | EventBridge scheduled rules or EventBridge Scheduler |
| "Rollback failed deployment" | CodeDeploy rollback, Lambda alias weighted routing |
| "Trace requests across services" | AWS X-Ray |
| "Secret rotation without code change" | Secrets Manager with Lambda rotation |
| "Infrastructure as code for serverless" | AWS SAM or CloudFormation |
| "Test Lambda locally" | SAM CLI `sam local invoke` |
| "Decouple order processing" | SQS between services |
| "Retry failed external API calls" | Exponential backoff + circuit breaker in code |

### Common Exam Traps

| Trap | Correct understanding |
|------|----------------------|
| "Use IAM user access keys in Lambda" | Use **execution role** — never embed credentials |
| "Scan DynamoDB for every query" | Design with **Query** + GSI for access patterns |
| "API Gateway handles business logic" | API Gateway is a **proxy/router** — logic lives in Lambda/backend |
| "SQS Standard guarantees order" | Only **FIFO** guarantees order; Standard is best-effort |
| "CloudFormation = CloudFormation Designer only" | Also includes **SAM**, **CDK** (generates CloudFormation) |
| "Encrypt env vars at rest in Lambda" | Use **KMS-encrypted** environment variables or Secrets Manager |

---

## Practice Tests

| Test | Domain | Location |
|------|--------|----------|
| 01 | Development with AWS Services | `practice-tests/practice-test-01-development/` |
| 02 | Security | `practice-tests/practice-test-02-security/` |
| 03 | Deployment | `practice-tests/practice-test-03-deployment/` |
| 04 | Troubleshooting & Optimization | `practice-tests/practice-test-04-troubleshooting/` |

---

## Official Resources

- [DVA-C02 Exam Guide (PDF)](https://docs.aws.amazon.com/pdfs/aws-certification/latest/developer-associate-02/developer-associate-02.pdf)
- [AWS Lambda Developer Guide](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS SAM Developer Guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html)
- [DynamoDB Developer Guide](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html)
- [AWS Free Tier](https://aws.amazon.com/free/) — build real projects

---

## Repository Structure

```
aws-certified-developer/
├── README.md                              ← You are here
├── CONCEPTS-DEEP-DIVE.md                  ← Developer-focused patterns
├── COVERAGE-SUMMARY.md                    ← Service & skill index
├── domain-0X-*.md                           ← Four domain guides
├── aws-*-dva-c02-guide.md                 ← Service deep dives
└── practice-tests/                          ← Domain-aligned tests
```

Good luck with your Developer Associate certification! 🚀
