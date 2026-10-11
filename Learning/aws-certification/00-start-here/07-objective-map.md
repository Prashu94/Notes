# Objective map

Every scored task on the three current exams, and where this pack teaches it. C03 additions are marked. Open the chapter and do the exercise. Checking the box because you recognized the service name does not count.

## SAA-C03

| Task | Weight home | Chapter | Lab |
| --- | --- | --- | --- |
| 1.1 Secure access to AWS resources | Domain 1, 30% | `01-foundations/02-iam-sts-identity-center-ram.md`, `03-saa/01-domain-1-secure.md` | `05-labs/lab-01-cli-identity.md` |
| 1.2 Secure workloads and applications | Domain 1 | `01-foundations/05-networking-foundations-for-architects.md`, `02-services/10-edge-route53-cloudfront-global-accelerator-waf-shield.md`, `02-services/13-security-hub-guardduty-inspector-macie-detective.md` | `lab-02-vpc-endpoints-tgw.md` |
| 1.3 Data security controls | Domain 1 | `01-foundations/06-encryption-kms-certificates-secrets.md`, `02-services/06-storage-s3-ebs-efs-fsx-backup-gateway.md` | `lab-03-s3-encryption-lifecycle.md` |
| 2.1 Scalable and loosely coupled | Domain 2, 26% | `02-services/01-compute-ec2-asg-batch-beanstalk.md`, `02-lambda-and-serverless.md`, `05-messaging-sqs-sns-eventbridge-step-functions-mq.md`, `03-saa/02-domain-2-resilient.md` | `lab-05-lambda-sqs-eventbridge.md` |
| 2.2 Highly available and fault-tolerant | Domain 2 | `03-saa/02-domain-2-resilient.md`, `04-sap/06-disaster-recovery-design.md` | `lab-10-disaster-recovery-patterns.md` |
| 3.1 High-performing storage | Domain 3, 24% | `02-services/06-storage-s3-ebs-efs-fsx-backup-gateway.md`, `03-saa/03-domain-3-performance.md` | `lab-03` |
| 3.2 High-performing elastic compute | Domain 3 | `02-services/01-compute-ec2-asg-batch-beanstalk.md`, `02-lambda-and-serverless.md`, `03-containers-ecs-eks-fargate-ecr.md` | |
| 3.3 High-performing databases | Domain 3 | `02-services/07-databases-rds-aurora-dynamodb-purpose-built.md`, `08-caching-elasticache-memorydb.md` | `lab-04-dynamodb-patterns.md` |
| 3.4 High-performing networks | Domain 3 | `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md`, `10-edge-route53-cloudfront-global-accelerator-waf-shield.md` | `lab-02` |
| 3.5 Ingestion and transformation | Domain 3 | `02-services/14-data-analytics-kinesis-glue-athena-lake-redshift-msk.md` | |
| 4.1 Cost-optimized storage | Domain 4, 20% | `03-saa/04-domain-4-cost.md`, storage chapter | |
| 4.2 Cost-optimized compute | Domain 4 | `03-saa/04-domain-4-cost.md`, `02-services/16-cost-management.md` | |
| 4.3 Cost-optimized databases | Domain 4 | `03-saa/04-domain-4-cost.md`, database chapter | |
| 4.4 Cost-optimized networks | Domain 4 | `03-saa/04-domain-4-cost.md`, networking chapter | `lab-02` |

## SAP-C02

| Task | Weight home | Chapter |
| --- | --- | --- |
| 1.1 Network connectivity strategies | Domain 1, 26% | `04-sap/01-domain-1-organizational-complexity.md`, `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md` |
| 1.2 Prescribe security controls | Domain 1 | `01-foundations/02-iam-sts-identity-center-ram.md`, `02-services/13-security-hub-guardduty-inspector-macie-detective.md` |
| 1.3 Reliable and resilient architectures | Domain 1 | `04-sap/06-disaster-recovery-design.md`, `02-services/18-resilience-drs-arc-fis-resilience-hub.md` |
| 1.4 Multi-account environment | Domain 1 | `01-foundations/04-accounts-organizations-control-tower.md`, `04-sap/05-multi-account-reference-architecture.md` |
| 1.5 Cost optimization and visibility | Domain 1 | `02-services/16-cost-management.md` |
| 2.1 Deployment strategy | Domain 2, 29% | `02-services/12-deployment-cloudformation-cdk-sam-cicd.md`, `04-sap/02-domain-2-new-solutions.md` |
| 2.2 Business continuity | Domain 2 | `04-sap/06-disaster-recovery-design.md` |
| 2.3 Security controls for a new solution | Domain 2 | `04-sap/02-domain-2-new-solutions.md`, edge and encryption chapters |
| 2.4 Reliability requirements | Domain 2 | `04-sap/02-domain-2-new-solutions.md`, messaging chapter |
| 2.5 Performance objectives | Domain 2 | compute, database, cache chapters |
| 2.6 Cost strategy for the solution | Domain 2 | `02-services/16-cost-management.md` |
| 3.1 Operational excellence | Domain 3, 25% | `04-sap/03-domain-3-continuous-improvement.md`, observability chapter |
| 3.2 Improve security | Domain 3 | security chapter, `04-sap/03-domain-3-continuous-improvement.md` |
| 3.3 Improve performance | Domain 3 | edge chapter, compute chapter |
| 3.4 Improve reliability | Domain 3 | DR chapter |
| 3.5 Cost optimizations on a running system | Domain 3 | cost chapter |
| 4.1 Select workloads to migrate | Domain 4, 20% | `04-sap/04-domain-4-migration-modernization.md` |
| 4.2 Optimal migration approach | Domain 4 | `02-services/15-migration-mgn-dms-datasync-snow-transfer.md` |
| 4.3 New architecture for existing workloads | Domain 4 | `04-sap/04-domain-4-migration-modernization.md` |
| 4.4 Modernization | Domain 4 | lambda, messaging, database chapters |

SAP-C03 additions (scored only after 17 November 2026): `04-sap/09-sap-c03-new-skills.md`. Map them onto domains 1–5 of `00-start-here/03-sap-c03-transition.md` when the official guide publishes weights.

## DVA-C02 skills

| Skills | Chapter |
| --- | --- |
| 1.1.1–1.1.13 application code, patterns, SDK, EventBridge, Q Developer | `05-dva/01-domain-1-development.md`, `05-dva/05-sdk-patterns.md` |
| 1.2.1–1.2.7 Lambda | `05-dva/07-lambda-deep-dive.md`, `02-services/02-lambda-and-serverless.md` |
| 1.3.1–1.3.9 data stores | `05-dva/06-dynamodb-for-developers.md`, database and cache chapters |
| 2.1.1–2.1.8 authN and authZ | `05-dva/02-domain-2-security.md`, IAM foundation, `02-services/19-identity-cognito-directory-verified-permissions.md` |
| 2.2.1–2.2.7 encryption | encryption foundation |
| 2.3.1–2.3.6 sensitive data | `05-dva/02-domain-2-security.md` |
| 3.1.1–3.1.5 artifacts and AppConfig | `05-dva/03-domain-3-deployment.md`, `02-services/12-deployment-cloudformation-cdk-sam-cicd.md` |
| 3.2.1–3.2.5 testing | `05-dva/03-domain-3-deployment.md`, `05-labs/lab-07-sam-cicd.md` |
| 3.3.1–3.3.6 automated test and IaC | deployment chapter |
| 3.4.1–3.4.11 CI/CD and strategies | `05-dva/03-domain-3-deployment.md` |
| 4.1.1–4.1.7 root cause | `05-dva/04-domain-4-troubleshooting.md`, observability chapter |
| 4.2.1–4.2.8 instrumentation | `05-labs/lab-08-observability-xray.md` |
| 4.3.1–4.3.9 optimization | `05-dva/04-domain-4-troubleshooting.md` |

DVA-C03 Task 2.3 and the container and AI-tool additions: `05-dva/10-dva-c03-new-skills.md`.

## Say it out loud before exam day

If you cannot answer these in one breath, the map row above is not done.

1. Security group versus NACL, including ephemeral ports.
2. Multi-AZ versus read replica versus global table, and what fails over by itself.
3. Gateway endpoint versus interface endpoint versus PrivateLink service versus VPC Lattice.
4. SQS versus SNS versus EventBridge versus Step Functions versus MQ.
5. The four DR patterns and one AWS service that implements each.
6. SCP versus identity policy versus permission boundary versus session policy.
7. SSE-S3 versus SSE-KMS versus client-side, and who can decrypt.
8. ALB versus NLB versus Gateway Load Balancer versus CloudFront versus Global Accelerator.
9. Lambda async retries, destinations, and partial batch failure.
10. DynamoDB query versus scan, and why a filter does not save read units.
