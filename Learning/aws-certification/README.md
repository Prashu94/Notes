# AWS certification study pack

English study material for three exams. Two of them have a new version landing in late 2026:

- **AWS Certified Solutions Architect – Associate (SAA-C03)** — design secure, resilient, high-performing, cost-optimized solutions with the Well-Architected Framework. This is the current Associate exam. There is no SAA-C04 announcement as of 11 October 2026.
- **AWS Certified Solutions Architect – Professional** — the same job at organizational scale: many accounts, hybrid networks, migration, and explicit tradeoffs. Current exam **SAP-C02** (last day 16 November 2026). Updated exam **SAP-C03** (registration opens 27 October 2026, delivery starts 17 November 2026).
- **AWS Certified Developer – Associate** — develop, secure, deploy, and debug applications on AWS. Current exam **DVA-C02** (last day 30 November 2026). Updated exam **DVA-C03** (registration opens 27 October 2026, delivery starts 1 December 2026).

Written against the exam guides and the AWS Training and Certification announcement current as of 11 October 2026. AWS can change product names, quotas, CLI flags, and objectives at any time. Before you book a seat, re-read:

- [SAA-C03 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html)
- [Solutions Architect Associate exam page](https://aws.amazon.com/certification/certified-solutions-architect-associate/)
- [SAP-C02 exam guide](https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02.html)
- [Solutions Architect Professional exam page](https://aws.amazon.com/certification/certified-solutions-architect-professional/)
- [DVA-C02 exam guide](https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html)
- [Developer Associate exam page](https://aws.amazon.com/certification/certified-developer-associate/)
- [September 2026 certification update (SAP-C03 and DVA-C03)](https://aws.amazon.com/blogs/training-and-certification/september-2026-new-offerings/)
- [AWS documentation home](https://docs.aws.amazon.com/)
- [Exam guides index](https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html)

The full SAP-C03 and DVA-C03 task lists are published when registration opens on 27 October 2026. This pack teaches every scored task on the current exams, plus every addition AWS named in the September 2026 announcement. On 27 October, open the new guides and check `00-start-here/03-sap-c03-transition.md` and `00-start-here/06-dva-c03-transition.md` against them.

This pack is original study notes. It is not a copy of AWS documentation or of the exam guides. Commands are the ones you run. Official docs remain the source of truth for flags that change.

The older folder [`../aws-sa-c03`](../aws-sa-c03/README.md) is an earlier SAA-C03 service set (guides, diagrams, seven practice tests). This pack is the one to study from. It teaches SAA-C03 task by task, then Professional and Developer. Service chapters in `02-services/` are shared. Each one is tagged SAA, SAP, DVA, or a combination, so you do not maintain two copies of S3 or IAM.

## How the folder is organized

| Path | What it is |
| --- | --- |
| `00-start-here/` | Exam facts, every official task for SAA-C03, SAP-C02, and DVA-C02, the C03 transitions, a study plan, the objective map, and the resource list |
| `01-foundations/` | Global infrastructure, Well-Architected, IAM and STS, CLI and SDK credentials, Organizations, networking, encryption |
| `02-services/` | Every product family that is in scope for any of the three exams: when to use it, architecture, commands, exam traps, exercises |
| `03-saa/` | Associate domains, exercises, and a full SAA-C03 practice exam |
| `04-sap/` | Professional domains, reference architectures, exercises, a full practice exam, and the SAP-C03 skills |
| `05-dva/` | Developer domains, SDK patterns, Lambda and DynamoDB depth, exercises, a full practice exam, and the DVA-C03 skills |
| `05-labs/` | End-to-end labs you can run in a sandbox account, plus design labs for services that are too expensive to stand up |
| `06-reference/` | Decision trees, a command index, traps, quotas that change answers. The documentation catalog is `02-services/20-full-product-catalog.md` |

## Exam logistics

Confirmed from the exam pages and the 1 September 2026 AWS Training and Certification blog.

| | SAA-C03 | SAP-C02 (through 16 Nov 2026) | SAP-C03 (from 17 Nov 2026) | DVA-C02 (through 30 Nov 2026) | DVA-C03 (from 1 Dec 2026) |
| --- | --- | --- | --- | --- | --- |
| Length | 130 minutes | 180 minutes | 180 minutes | 130 minutes | 130 minutes |
| Questions on screen | 65 (50 scored + 15 unscored) | 75 (65 scored + 10 unscored) | 75 | 65 (50 scored + 15 unscored) | 65 (50 scored + 15 unscored) |
| Question types | Multiple choice, multiple response | Same | Same | Same | Same |
| Fee | 150 USD | 300 USD | 300 USD | 150 USD | 150 USD |
| Passing score | 720 / 1000 scaled | 750 / 1000 scaled | Confirm on the new guide | 720 / 1000 scaled | 720 / 1000 scaled |
| Validity | 3 years | 3 years | 3 years. A SAP-C02 pass stays valid through its original expiry | 3 years | 3 years |
| Recommended experience | 1+ year designing on AWS | 2+ years designing and implementing | 2+ years, including cloud-native and AI-integrated designs | 1+ year developing applications on AWS | 1+ year, plus AI-assisted development |
| Case studies | None | None | None announced | None | None |
| Prerequisite certification | None. Associate is not required before Professional | None | None | None | None |
| Scoring | Compensatory. You pass the exam as a whole | Compensatory | Same model expected | Compensatory | Same |
| Guessing | Unanswered items are wrong. There is no penalty for guessing | Same | Same | Same | Same |

SAP-C02 languages on the exam page: English, Japanese, Korean, Portuguese (Brazil), Simplified Chinese, Spanish (Latin America). SAP-C03 launches in the languages the exam already supports. Developer languages are listed on the [Developer exam page](https://aws.amazon.com/certification/certified-developer-associate/); re-check them when you schedule because AWS adds languages over time.

Delivery for all five sittings: Pearson VUE test center or online proctoring. SAA-C03 languages are listed on the Associate exam page. Re-check them when you schedule.

Once you hold any active AWS Certification, the certification account offers 50% off the next exam. Recertification is by passing the current version of the same exam before expiry.

## Which sitting to book

Today is 11 October 2026. SAA-C03 is the stable Associate exam. Registration for the two updated exams opens in 16 days. Their new guides are not public yet.

- Book **SAA-C03** first if you cannot yet defend a VPC, a Multi-AZ database, an IAM role, and an S3 lifecycle on a whiteboard. Professional items assume those choices and then add accounts, RPO numbers, and migration tools. There is no announced retirement date for SAA-C03.

- Book **SAP-C02** if you can sit on or before **16 November 2026** and you already know multi-account design, hybrid networking, disaster recovery, migration, and cost. The credential stays valid for its full term.
- Wait for **SAP-C03** if you want the credential to include generative AI architecture, agentic AI, post-quantum KMS, resilience engineering, VPC Lattice, and lakehouse design. Use the weeks before 27 October to finish the SAP-C02 core in this pack. On 27 October, read the new guide and finish `04-sap/09-sap-c03-new-skills.md`.
- Book **DVA-C02** if you can sit on or before **30 November 2026** and you can already write Lambda, DynamoDB, API Gateway, IAM role code, CI/CD, and X-Ray.
- Wait for **DVA-C03** if you want AI-assisted development, Bedrock and AgentCore security, containers (ECR, ECS, EKS, Fargate), PrivateLink, and Data Firehose on the scored exam. Domain weights shift: Development 30%, Security 26%, Testing and Deployment 22%, Troubleshooting and Optimization 22%.

## Suggested order

1. Read `00-start-here/04-saa-c03-exam-blueprint.md` first. Then the Professional and Developer blueprints for the exam you will sit second. Read the two transition files so you know what arrives in SAP-C03 and DVA-C03.
2. Do `01-foundations/`. Associate questions are won on IAM, VPC, encryption, and the shared responsibility model. Professional questions add Organizations, SCPs, and hybrid DNS on top of the same model.
3. Work through `02-services/` in order. Do the exercises before you read the answers. The SAA tag on a section is the Associate depth. The SAP tag is the extra design constraint. The DVA tag is the API and the code.
4. Run the labs in `05-labs/` in a sandbox account with a budget alarm. Reading commands is a different skill from typing them.
5. Associate candidates: `03-saa/` after the core service chapters (compute, storage, database, network, security, cost). The practice exam is original. Buy the official SAA-C03 practice question set on AWS Skill Builder as well.
6. Professional candidates: `04-sap/` after Associate-level choices feel automatic. The practice exam is original.
7. Developer candidates: `05-dva/` can start in parallel once IAM, Lambda, DynamoDB, and API Gateway are done. Write the code.
8. Last week: `06-reference/decision-trees.md` and `06-reference/exam-traps.md`. Most wrong answers are a service that solves a nearby problem.

## What “do not miss a topic” means in this pack

`02-services/20-full-product-catalog.md` walks the documentation catalog at [docs.aws.amazon.com](https://docs.aws.amazon.com/): every technology area, with exam weight (must know for SAP, must know for DVA, recognize, or out of scope) and the command or console path. Services AWS lists as out of scope are included so you can see they were considered.

`00-start-here/07-objective-map.md` maps every SAP-C02 task and every DVA-C02 skill number to a file in this pack.

`00-start-here/08-official-resources.md` lists the whitepapers, prescriptive guidance, decision guides, workshops, and Skill Builder paths that match these exams.

## Product names used on the current exams

AWS shortens some names on the exam. The Help button in the exam lists the short name and the full name. Learn both.

| Say this | You will also see |
| --- | --- |
| Amazon SNS | Amazon Simple Notification Service |
| Amazon SQS | Amazon Simple Queue Service |
| AWS KMS | AWS Key Management Service |
| AWS DMS | AWS Database Migration Service |
| AWS IAM Identity Center | The older name AWS Single Sign-On (SSO) still appears in blogs and some CLI (`aws sso`) |
| Amazon SageMaker AI | Previously Amazon SageMaker. The SAP-C02 guide uses SageMaker AI |
| Amazon Data Firehose | Previously Amazon Kinesis Data Firehose. CLI is still `aws firehose` in many accounts |
| Amazon OpenSearch Service | The successor to Amazon Elasticsearch Service |
| AWS Elastic Disaster Recovery | The successor to CloudEndure Disaster Recovery |
| AWS Application Migration Service (MGN) | The successor to CloudEndure Migration |
| Amazon Bedrock AgentCore | Named in the SAP-C03 and DVA-C03 announcements for agent runtime, identity, and tool use |
| Kiro | Named as a new in-scope developer tool on DVA-C03. Spec-driven AI coding. Docs list it under Developer Tools |

## How to practice without a surprise bill

1. Use a sandbox account that is not production. If you use Organizations, use a dedicated management account and member accounts you can close.
2. Create an AWS Budget with an email alert at a number you will notice (10 USD is enough for most labs here). A budget alert does not stop spend. You stop spend by deleting resources.
3. Prefer `us-east-1` or your nearest Region and stay in one Region unless the lab is about multi-Region.
4. Delete stacks with `aws cloudformation delete-stack` and confirm `DELETE_COMPLETE`. NAT gateways, Elastic IPs, unattached EBS volumes, Global Accelerator, and Direct Connect virtual interfaces are the usual leftovers.
5. Do not build Direct Connect, Snowball, Shield Advanced, Macie in a huge bucket, or a multi-Region Aurora Global Database “just to see.” Those labs are design exercises with the CLI shown for the parts that are cheap.

## Official prep you should still buy or enroll in

This pack does not replace AWS’s own scored practice.

- [AWS Skill Builder](https://skillbuilder.aws/) exam prep plan for each certification: official practice question set, then the official practice exam.
- [AWS Builder Labs](https://aws.amazon.com/training/digital/aws-builder-labs/) and AWS SimuLearn for console clicks this pack cannot watch you do.
- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) and the six pillar whitepapers.
- [Disaster Recovery of Workloads on AWS](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html).
- [Organizing Your AWS Environment Using Multiple Accounts](https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html).
- [AWS Prescriptive Guidance](https://docs.aws.amazon.com/prescriptive-guidance/) patterns for migration, modernization, and resilience.
- [AWS Decision Guides](https://aws.amazon.com/getting-started/decision-guides/) linked from the documentation home page. The catalog file maps each one to an exam task.
