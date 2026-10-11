# Twelve-week study plan

Three exams, one sequence. Weeks 1–6 make you dangerous on SAA-C03. Weeks 7–9 sit the Associate exam or start Professional depth. Weeks 7–12 for a developer run in parallel from week 4 once Lambda and IAM are honest.

A week is five days, 90 minutes, plus one lab block. If you only have 45 minutes, do the exercise and skip the reread.

| Week | Outcome | Read and do |
| --- | --- | --- |
| 1 | You can draw a VPC and explain who is responsible for a leaked key | `01-foundations/01-global-infrastructure-and-well-architected.md`, `02-iam-sts-identity-center-ram.md`, `03-cli-sdk-credentials-and-retries.md`. Lab `05-labs/lab-01-cli-identity.md` |
| 2 | You can encrypt a bucket, lock a trail, and write a least-privilege role | `01-foundations/06-encryption-kms-certificates-secrets.md`, `02-services/06-storage-s3-ebs-efs-fsx-backup-gateway.md`. Lab `lab-03-s3-encryption-lifecycle.md`. SAA domain 1 exercises |
| 3 | You can pick compute and make it survive an AZ failure | `02-services/01-compute-ec2-asg-batch-beanstalk.md`, `02-lambda-and-serverless.md`, `03-containers-ecs-eks-fargate-ecr.md`. SAA domain 2 |
| 4 | You can pick a database from an access pattern and write the SDK call | `02-services/07-databases-rds-aurora-dynamodb-purpose-built.md`, `08-caching-elasticache-memorydb.md`, `05-dva/06-dynamodb-for-developers.md`. Lab `lab-04-dynamodb-patterns.md` |
| 5 | You can decouple a tier and put an API in front of it | `02-services/05-messaging-sqs-sns-eventbridge-step-functions-mq.md`, `04-api-gateway-appsync-amplify.md`, `05-dva/07-lambda-deep-dive.md`. Lab `lab-05-lambda-sqs-eventbridge.md` |
| 6 | You can defend networking cost, edge, and hybrid at Associate depth | `01-foundations/05-networking-foundations-for-architects.md`, `02-services/09-networking-vpc-tgw-dx-vpn-privatelink-lattice.md`, `10-edge-route53-cloudfront-global-accelerator-waf-shield.md`. Lab `lab-02-vpc-endpoints-tgw.md` |
| 7 | SAA timed exam, then repair | `03-saa/05-saa-exercises.md`, then `03-saa/06-saa-practice-exam.md` timed. Same week, the official Skill Builder question set. Book SAA-C03 if you are at 80%+ |
| 8 | Developer security and deploy, or Professional multi-account | Developers: `05-dva/02-domain-2-security.md`, `03-domain-3-deployment.md`, `05-labs/lab-06-api-gateway-cognito.md`, `05-labs/lab-07-sam-cicd.md`. Architects: `01-foundations/04-accounts-organizations-control-tower.md`, `04-sap/05-multi-account-reference-architecture.md`, `05-labs/lab-09-multi-account-design.md` |
| 9 | Observability and cost | `02-services/11-observability-cloudwatch-xray-cloudtrail-config.md`, `16-cost-management.md`, `12-deployment-cloudformation-cdk-sam-cicd.md`. Lab `lab-08-observability-xray.md` |
| 10 | Migration, DR, analytics | `02-services/15-migration-mgn-dms-datasync-snow-transfer.md`, `18-resilience-drs-arc-fis-resilience-hub.md`, `14-data-analytics-kinesis-glue-athena-lake-redshift-msk.md`. `04-sap/06-disaster-recovery-design.md` and `05-labs/lab-10-disaster-recovery-patterns.md` |
| 11 | The exam you will sit | SAP: `04-sap/01` through `04`, then `07-sap-exercises.md`. DVA: `05-dva/01` through `04`, then `08-dva-exercises.md`. Both: `04-sap/09-sap-c03-new-skills.md` or `05-dva/10-dva-c03-new-skills.md` if you are waiting for the new exam |
| 12 | Timed originals, then official practice, then traps only | `06-reference/decision-trees.md`, `exam-traps.md`, `command-index.md`. One timed exam. Repair only missed tasks on `07-objective-map.md` |

## If you can only sit one exam in the next 30 days

| Seat | Cut the plan to |
| --- | --- |
| SAA-C03 | Weeks 1–7, plus `06-reference/exam-traps.md`. Skip Bedrock, Lattice internals, and SDK pagination |
| SAP-C02 before 16 November 2026 | You already need weeks 1–6 in your head. Spend the days on weeks 8–12 architect column, especially multi-account, DR, and migration |
| SAP-C03 after 17 November 2026 | SAP-C02 plan plus `04-sap/09-sap-c03-new-skills.md` and `02-services/17-generative-ai-bedrock-q-kiro.md` |
| DVA-C02 before 30 November 2026 | Weeks 1, 4, 5, 8, 9, and `05-dva/` in full. VPC design weeks shrink to "Lambda in a VPC" |
| DVA-C03 after 1 December 2026 | DVA-C02 plan plus containers lab and `05-dva/10-dva-c03-new-skills.md` |

## Daily loop

1. Read one section with the exercise covered.
2. Answer the exercise in a scratch file.
3. Uncover the answer. Write the constraint you missed, in one sentence.
4. Run the command from that section in the sandbox, or run the lab if it is the lab day.
5. Add one card to your trap list only if you missed it.

## What “done” means before you pay Pearson VUE

- You can complete the objective map’s “say it out loud” column without opening the chapter.
- The original practice exam in this pack is at or above 80% timed.
- The official AWS practice question set is at or above 80%, and every miss maps to a file you then reread.
- You have deleted the sandbox resources from the labs you ran.
