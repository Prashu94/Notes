# SAP-C03 transition

Source: the AWS Training and Certification blog, 1 September 2026, “Certification updates from AWS Training and Certification: September 2026.”

https://aws.amazon.com/blogs/training-and-certification/september-2026-new-offerings/

The exam page repeats the dates:

https://aws.amazon.com/certification/certified-solutions-architect-professional/

The detailed task-by-task exam guide is **not** public until registration opens. Anything in this file that is a skill list comes from that blog. Anything that is a weight, a question count per domain, or a sample item would be a guess, so this file does not invent those.

## Dates and format

| Item | Fact from AWS |
| --- | --- |
| Registration opens | 27 October 2026, all languages the exam already supports |
| Last day of SAP-C02 | 16 November 2026 |
| First day of SAP-C03 delivery | 17 November 2026 |
| Duration | 180 minutes |
| Questions | 75 |
| Price | 300 USD |
| Delivery | Pearson VUE, test center or online |
| Experience AWS recommends | 2 or more years designing and implementing on AWS, including guidance on cloud-native, serverless, and AI-integrated architectures |
| Credential if you pass SAP-C02 | Stays valid through its original expiration. You do not have to sit C03 to “upgrade” a current cert |

## Why AWS says the exam is changing

The blog’s description of the role: architects still design for availability and cost, and they also integrate generative and agentic AI, implement post-quantum cryptography, design resilience patterns, and build DevSecOps automation into the stack. The exam still uses the Well-Architected Framework.

## The five domains

AWS published the names, not the percentages.

1. Cloud-native architecture design and implementation
2. Security, compliance, and governance
3. Cost-optimized architecture design
4. Resilience, migration, and business continuity
5. Operational excellence and automation

How this sits on top of SAP-C02, as a study map (this mapping is ours, for study order, and is not an AWS crosswalk):

| SAP-C02 material you already need | Where it lives in the new names |
| --- | --- |
| Domain 2 deployment, serverless, containers, integration, performance | Domain 1, cloud-native |
| Domain 1 security controls, encryption, identity, Organizations | Domain 2, security, compliance, governance |
| Domain 1 cost visibility and Domain 2/3 cost tasks | Domain 3, cost-optimized design |
| Domain 1 resilience, Domain 2 business continuity, Domain 4 migration | Domain 4, resilience, migration, business continuity |
| Domain 3 operational excellence, automation, observability | Domain 5, operational excellence and automation |

Do not drop migration, hybrid networking, or cost. AWS said existing skills are updated, not deleted.

## Additions AWS named

Study these as scored material if you sit SAP-C03. On SAP-C02, Guardrails, AgentCore Identity, and human oversight are the emerging pretest topics. The rest of this list is new relative to the C02 guide.

### Generative AI and agentic AI (11 new skills)

AWS named the themes, not the eleven individual skill sentences:

- Design integrations with Amazon Bedrock.
- AI agent architectures on Amazon Bedrock AgentCore.
- Retrieval-augmented generation (RAG) architectures.
- Bedrock Guardrails for content filtering.
- Human-oversight workflows for AI operations.

Taught in `04-sap/09-sap-c03-new-skills.md` and `02-services/17-generative-ai-bedrock-q-kiro.md`.

### Resilience engineering

- AWS Fault Injection Service.
- AWS Resilience Hub.
- AWS Application Recovery Controller (ARC).
- Automated runbooks in Systems Manager.

Taught in `02-services/18-resilience-drs-arc-fis-resilience-hub.md`.

### Cloud-native patterns (7 new skills)

- Serverless data pipelines.
- Durable workflows with Step Functions.
- Service mesh with VPC Lattice and ECS Service Connect.
- Container image security.
- Multi-tenant architectures.
- Real-time data architectures.

Taught across `02-services/02-lambda-and-serverless.md`, `02-services/03-containers-ecs-eks-fargate-ecr.md`, `02-services/05-messaging-sqs-sns-eventbridge-step-functions-mq.md`, `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md`, and `02-services/14-data-analytics-kinesis-glue-athena-lake-redshift-msk.md`.

### DevSecOps and observability (6 new skills)

- Pipeline vulnerability scanning.
- Multi-account deployment pipelines.
- Container monitoring.
- AI and ML metrics monitoring.
- Synthetic monitoring and real-user monitoring.

Taught in `02-services/12-deployment-cloudformation-cdk-sam-cicd.md` and `02-services/11-observability-cloudwatch-xray-cloudtrail-config.md`.

### Data and analytics (3 new skills)

- Lakehouse architectures with Lake Formation and Apache Iceberg.
- Real-time and batch analytics pipelines.
- Cross-account data sharing with AWS Clean Rooms.

Taught in `02-services/14-data-analytics-kinesis-glue-athena-lake-redshift-msk.md`.

### Post-quantum cryptography

- AWS KMS with ML-DSA and ML-KEM.

Taught in `01-foundations/06-encryption-kms-certificates-secrets.md`. Confirm key specs in the KMS developer guide on the day you study them. Algorithm identifiers in CLI flags have changed during the preview-to-GA path of this feature.

## What to do on 27 October 2026

1. Open the SAP-C03 exam guide from the exam page or from https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html
2. Copy the domain weights into the top of this file. They were not published in September.
3. Diff the in-scope service list against `02-services/20-full-product-catalog.md`. Add any service AWS added. Mark any service AWS removed.
4. Diff the task statements against `04-sap/09-sap-c03-new-skills.md`. If AWS published eleven GenAI skill sentences, paste nothing verbatim from the guide into this repo beyond short task titles. Write a scenario for each new sentence.
5. If you are booked on SAP-C02 before 16 November, do not switch plans because the new guide looks interesting. Finish C02. The credential remains valid.

## Who should wait

Wait if your job already includes Bedrock, multi-account pipelines, and resilience engineering, and you cannot sit before 16 November. The blog’s own advice matches that: sit C02 if you are ready now; wait for C03 if you want the credential to name the new skills.

## Services to add to your C02 notes even if you do not wait

These are already the right production answers, and C02 stems can use them as the modern option:

- VPC Lattice and ECS Service Connect next to App Mesh (App Mesh is in maintenance; do not pick it for a new design).
- Aurora Serverless v2 and Aurora Global Database.
- gp3, S3 Express One Zone only when the stem demands single-digit millisecond object access in one AZ.
- Compute Savings Plans ahead of new Standard RIs for EC2.
- IAM Identity Center ahead of per-account IAM users.
- Versioned S3, Object Lock, and Backup vault lock for ransomware.
- EventBridge pipes and Step Functions service integrations ahead of a fan-in Lambda you would have to operate.
