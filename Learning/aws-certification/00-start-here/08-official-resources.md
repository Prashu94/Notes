# Official resources

Every link below is a primary AWS source. Use these when a CLI flag in this pack disagrees with the live docs. The live docs win.

Reviewed 11 October 2026.

## Exam guides and scheduling

| Resource | URL | Why it is here |
| --- | --- | --- |
| Exam guides index | https://docs.aws.amazon.com/aws-certification/latest/examguides/aws-certification-exam-guides.html | Current list of every exam guide on AWS Documentation |
| SAA-C03 exam guide (HTML) | https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.html | Associate domains, tasks, in-scope and out-of-scope services |
| SAA-C03 exam guide (PDF) | https://docs.aws.amazon.com/pdfs/aws-certification/latest/solutions-architect-associate-03/solutions-architect-associate-03.pdf | Offline copy of the same guide |
| Solutions Architect Associate exam page | https://aws.amazon.com/certification/certified-solutions-architect-associate/ | Price, duration, languages. No replacement exam announced as of 11 October 2026 |
| SAP-C02 exam guide (HTML) | https://docs.aws.amazon.com/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02.html | Scored domains, tasks, in-scope services |
| SAP-C02 exam guide (PDF) | https://docs.aws.amazon.com/pdfs/aws-certification/latest/solutions-architect-professional-02/solutions-architect-professional-02.pdf | Offline copy of the same guide. Copyright 2026 on the PDF fetched for this pack |
| Solutions Architect Professional exam page | https://aws.amazon.com/certification/certified-solutions-architect-professional/ | Price, duration, languages, SAP-C03 dates |
| DVA-C02 exam guide (HTML) | https://docs.aws.amazon.com/aws-certification/latest/developer-associate-02/developer-associate-02.html | Scored skills, in-scope and out-of-scope services, version 2.1 revisions |
| DVA-C02 exam guide (PDF) | https://docs.aws.amazon.com/pdfs/aws-certification/latest/developer-associate-02/developer-associate-02.pdf | Offline copy |
| Developer Associate exam page | https://aws.amazon.com/certification/certified-developer-associate/ | Price, duration, DVA-C03 dates |
| September 2026 certification update | https://aws.amazon.com/blogs/training-and-certification/september-2026-new-offerings/ | Official SAP-C03 and DVA-C03 scope, domains, and dates |
| Coming soon page | https://aws.amazon.com/certification/coming-soon/ | Beta exams and other updates. Re-check on 27 October 2026 |
| Certification FAQs | https://aws.amazon.com/certification/certification-faqs/ | Recertification, scoring, policies |
| Exam pricing | https://aws.amazon.com/certification/certification-prep/testing/ | Fees and currency notes. The exam pages quote 300 USD and 150 USD |
| Policies and identification | https://aws.amazon.com/certification/policies/ | What you can bring, online proctoring rules |
| AWS service short names | https://aws.amazon.com/certification/certified-cloud-practitioner/ (Help list is also inside the exam) | The exam uses short names. The in-exam Help button maps them |

The SAP-C03 and DVA-C03 HTML guides are not in the index yet. AWS said they publish when registration opens on 27 October 2026. Bookmark the exam pages and the blog.

## Skill Builder and hands-on

| Resource | URL | Why it is here |
| --- | --- | --- |
| AWS Skill Builder | https://skillbuilder.aws/ | Official exam prep plans, practice question sets, official practice exams |
| Exam Prep: SAA-C03 | Search Skill Builder for “Exam Prep Official Practice Question Set (SAA-C03)” and the official practice exam | Do these after `03-saa/06-saa-practice-exam.md` |
| Exam Prep: SAP-C02 | Search Skill Builder for “Exam Prep Official Practice Question Set (SAP-C02)” and “Official Practice Exam (SAP-C02)” | Closest thing to the real item style. Do these after `04-sap/08-sap-practice-exam.md` |
| Exam Prep: DVA-C02 | Search Skill Builder for the DVA-C02 practice question set and official practice exam | Same for the developer exam |
| AWS Builder Labs | https://aws.amazon.com/training/digital/aws-builder-labs/ | Guided console labs in an AWS-provided account |
| AWS SimuLearn | Linked from the exam prep plan | Scenario simulations |
| AWS Cloud Quest | https://aws.amazon.com/training/digital/aws-cloud-quest/ | Role-based practice, including a Solutions Architect path |
| AWS Workshops | https://workshops.aws/ | Free workshops. Prefer the ones named below |
| AWS Builder Center | https://builder.aws.com/ | Newer builder home linked from the docs landing page |
| AWS re:Post | https://repost.aws/ | Exam-style “why” answers. Prefer AWS-authored Knowledge Center articles |

Workshops worth the time for these two exams:

| Workshop | What it locks in |
| --- | --- |
| https://catalog.workshops.aws/startup-security-baseline/en-US | Account baseline: CloudTrail, Config, GuardDuty, IAM |
| https://catalog.workshops.aws/control-tower/en-US | Multi-account landing zone. SAP Domain 1 |
| https://catalog.workshops.aws/networking/en-US | VPC, endpoints, Transit Gateway patterns |
| https://catalog.us-east-1.prod.workshops.aws/workshops (search “Transit Gateway”) | Hybrid and multi-VPC routing |
| https://catalog.workshops.aws/well-architected-labs/en-US | Pillar labs, including cost and reliability |
| https://catalog.workshops.aws/event-driven-architecture/en-US | EventBridge, SQS, Step Functions. Both exams |
| SAM workshops linked from https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-getting-started.html | Developer deployment domain |
| https://catalog.workshops.aws/amazon-bedrock/en-US or the current Bedrock workshop on workshops.aws | SAP-C03 and DVA-C03 AI skills |

Workshop URLs move. If a catalog link 404s, search the title on https://workshops.aws/.

## Whitepapers and frameworks

These are the documents Professional questions are written from. Read them. Do not memorize page numbers.

| Paper | URL |
| --- | --- |
| AWS Well-Architected Framework | https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html |
| Operational Excellence pillar | https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html |
| Security pillar | https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html |
| Reliability pillar | https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html |
| Performance Efficiency pillar | https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html |
| Cost Optimization pillar | https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html |
| Sustainability pillar | https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/sustainability-pillar.html |
| Disaster Recovery of Workloads on AWS | https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html |
| Organizing Your AWS Environment Using Multiple Accounts | https://docs.aws.amazon.com/whitepapers/latest/organizing-your-aws-environment/organizing-your-aws-environment.html |
| Building a Scalable and Secure Multi-VPC AWS Network Infrastructure | https://docs.aws.amazon.com/whitepapers/latest/building-scalable-secure-multi-vpc-network-infrastructure/welcome.html |
| AWS Security Incident Response Guide | https://docs.aws.amazon.com/whitepapers/latest/aws-security-incident-response-guide/welcome.html |
| AWS Well-Architected Tool | https://docs.aws.amazon.com/wellarchitected/latest/userguide/intro.html |
| AWS Prescriptive Guidance home | https://docs.aws.amazon.com/prescriptive-guidance/ |
| Prescriptive Guidance: migration strategies (7 Rs) | https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-migration/welcome.html and https://docs.aws.amazon.com/prescriptive-guidance/latest/large-migration-guide/migration-strategies.html |
| Prescriptive Guidance: Resilience lifecycle | https://docs.aws.amazon.com/prescriptive-guidance/latest/resilience-lifecycle-framework/welcome.html |
| AWS Decision Guides index (from the docs home) | https://docs.aws.amazon.com/decision-guides/latest/guide-list/guide-list.html or the “Decision Guides” section of https://docs.aws.amazon.com/ |
| AWS Architecture Center | https://aws.amazon.com/architecture/ |
| AWS Solutions Library | https://aws.amazon.com/solutions/ |
| Reference architecture diagrams | Linked from the docs home as “AWS Reference Architecture Diagrams” |

Decision guides that map directly onto exam answers:

| Guide | Exam use |
| --- | --- |
| Choosing an AWS compute service | EC2, Lambda, Batch, Beanstalk, App Runner |
| Choosing a purchasing option for EC2 | On-Demand, Spot, Reserved, Savings Plans, Dedicated |
| Fargate or Lambda | Serverless compute split |
| Lightsail or EC2 | Lightsail is in scope for SAP as a simple VPS. It is the wrong answer for enterprise HA |
| Choosing a container service | ECS, EKS, Fargate, App Runner, ROSA |
| Choosing a database | Purpose-built database selection. Domain 2 and Domain 4 |
| Choosing a database for generative AI | Vector store choice on SAP-C03 |
| SQS, SNS, or EventBridge | Both exams, constantly |
| Choosing an application integration service | Adds Step Functions, MQ, AppFlow, AppSync |
| WAF or Shield | Edge protection |
| CloudTrail or CloudWatch | Audit versus telemetry |
| Choosing a storage service | S3, EBS, EFS, FSx, Storage Gateway, Backup |
| Choosing a networking service | TGW, PrivateLink, Lattice, DX, VPN, CloudFront, Global Accelerator, Route 53 |
| Choosing an identity service | IAM, Identity Center, Cognito, Directory Service, Verified Permissions |
| Choosing a cryptography service | KMS, CloudHSM, ACM, Private CA |
| Choosing a cost management strategy | Cost Explorer, Budgets, CUR, Compute Optimizer |
| Choosing a monitoring service | CloudWatch, X-Ray, Managed Grafana, Managed Prometheus, DevOps Guru |
| Choosing a migration tool | MGN, DMS, DataSync, Snow, Transfer Family, Migration Hub |
| Choosing an analytics service | Athena, EMR, Glue, Kinesis, MSK, Redshift, OpenSearch, QuickSight |
| Choosing a governance service | Organizations, Control Tower, Config, Service Catalog |
| Choosing security, identity, and governance services | Security Hub, GuardDuty, Inspector, Macie, Detective |
| Choosing an ML service | SAP in-scope ML APIs and SageMaker AI |
| Choosing a generative AI service | Bedrock versus SageMaker AI. SAP-C03 |
| Bedrock or SageMaker AI | Same decision, shorter guide |
| Choosing frontend and mobile services | Amplify, AppSync, API Gateway, Device Farm. Mostly DVA |
| Choosing an IoT service | SAP in-scope IoT services. Recognize, do not specialize |

## Service documentation you will open while studying

The service chapters link the specific pages. These are the roots:

| Area | Root |
| --- | --- |
| Documentation home | https://docs.aws.amazon.com/ |
| AWS CLI v2 reference | https://docs.aws.amazon.com/cli/latest/reference/ |
| CLI user guide | https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-welcome.html |
| SDK and tools reference (retries, credentials, endpoints) | https://docs.aws.amazon.com/sdkref/latest/guide/overview.html |
| Boto3 | https://boto3.amazonaws.com/v1/documentation/api/latest/index.html |
| AWS SDK for JavaScript v3 | https://docs.aws.amazon.com/sdk-for-javascript/v3/developer-guide/welcome.html |
| AWS SAM | https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/what-is-sam.html |
| AWS CDK | https://docs.aws.amazon.com/cdk/v2/guide/home.html |
| CloudFormation resource reference | https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-template-resource-type-ref.html |
| IAM user guide | https://docs.aws.amazon.com/IAM/latest/UserGuide/introduction.html |
| IAM policy reference | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies.html |
| STS | https://docs.aws.amazon.com/STS/latest/APIReference/welcome.html |
| Organizations | https://docs.aws.amazon.com/organizations/latest/userguide/orgs_introduction.html |
| Control Tower | https://docs.aws.amazon.com/controltower/latest/userguide/what-is-control-tower.html |
| RAM | https://docs.aws.amazon.com/ram/latest/userguide/what-is.html |
| VPC user guide | https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html |
| Transit Gateway | https://docs.aws.amazon.com/vpc/latest/tgw/what-is-transit-gateway.html |
| PrivateLink | https://docs.aws.amazon.com/vpc/latest/privatelink/what-is-privatelink.html |
| VPC Lattice | https://docs.aws.amazon.com/vpc-lattice/latest/ug/what-is-vpc-lattice.html |
| Direct Connect | https://docs.aws.amazon.com/directconnect/latest/UserGuide/Welcome.html |
| Site-to-Site VPN | https://docs.aws.amazon.com/vpn/latest/s2svpn/VPC_VPN.html |
| Route 53 | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/Welcome.html |
| Route 53 Resolver | https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/resolver.html |
| Global Accelerator | https://docs.aws.amazon.com/global-accelerator/latest/dg/what-is-global-accelerator.html |
| CloudFront | https://docs.aws.amazon.com/AmazonCloudFront/latest/DeveloperGuide/Introduction.html |
| ELB | https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html |
| WAF | https://docs.aws.amazon.com/waf/latest/developerguide/what-is-aws-waf.html |
| Shield | https://docs.aws.amazon.com/waf/latest/developerguide/shield-chapter.html |
| Network Firewall | https://docs.aws.amazon.com/network-firewall/latest/developerguide/what-is-aws-network-firewall.html |
| S3 user guide | https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html |
| S3 Glacier | https://docs.aws.amazon.com/amazonglacier/latest/dev/introduction.html |
| EBS | https://docs.aws.amazon.com/ebs/latest/userguide/what-is-amazon-ebs.html |
| EFS | https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html |
| FSx | https://docs.aws.amazon.com/fsx/latest/WindowsGuide/what-is.html and the Lustre, ONTAP, OpenZFS, and File Cache guides linked from docs home |
| Backup | https://docs.aws.amazon.com/aws-backup/latest/devguide/whatisbackup.html |
| Storage Gateway | https://docs.aws.amazon.com/storagegateway/latest/tgw/WhatIsStorageGateway.html |
| Elastic Disaster Recovery | https://docs.aws.amazon.com/drs/latest/userguide/what-is-drs.html |
| EC2 | https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html |
| Auto Scaling | https://docs.aws.amazon.com/autoscaling/ec2/userguide/what-is-amazon-ec2-auto-scaling.html |
| Lambda | https://docs.aws.amazon.com/lambda/latest/dg/welcome.html |
| Lambda Powertools | https://docs.powertools.aws.dev/lambda/python/latest/ |
| ECS | https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html |
| EKS | https://docs.aws.amazon.com/eks/latest/userguide/what-is-eks.html |
| ECR | https://docs.aws.amazon.com/AmazonECR/latest/userguide/what-is-ecr.html |
| Fargate | Covered inside the ECS and EKS guides |
| Elastic Beanstalk | https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/Welcome.html |
| App Runner | https://docs.aws.amazon.com/apprunner/latest/dg/what-is-apprunner.html |
| Batch | https://docs.aws.amazon.com/batch/latest/userguide/what-is-batch.html |
| API Gateway | https://docs.aws.amazon.com/apigateway/latest/developerguide/welcome.html |
| AppSync | https://docs.aws.amazon.com/appsync/latest/devguide/what-is-appsync.html |
| Amplify | https://docs.aws.amazon.com/amplify/latest/userguide/welcome.html |
| SQS | https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html |
| SNS | https://docs.aws.amazon.com/sns/latest/dg/welcome.html |
| EventBridge | https://docs.aws.amazon.com/eventbridge/latest/userguide/eb-what-is.html |
| Step Functions | https://docs.aws.amazon.com/step-functions/latest/dg/welcome.html |
| MQ | https://docs.aws.amazon.com/amazon-mq/latest/developer-guide/welcome.html |
| AppFlow | https://docs.aws.amazon.com/appflow/latest/userguide/what-is-appflow.html |
| RDS | https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/Welcome.html |
| Aurora | https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/CHAP_AuroraOverview.html |
| DynamoDB | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Introduction.html |
| DynamoDB Streams and Lambda | https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/Streams.Lambda.html |
| ElastiCache | https://docs.aws.amazon.com/AmazonElastiCache/latest/dg/WhatIs.html |
| MemoryDB | https://docs.aws.amazon.com/memorydb/latest/devguide/what-is-memorydb.html |
| DocumentDB | https://docs.aws.amazon.com/documentdb/latest/developerguide/what-is.html |
| Neptune | https://docs.aws.amazon.com/neptune/latest/userguide/intro.html |
| Keyspaces | https://docs.aws.amazon.com/keyspaces/latest/devguide/what-is-keyspaces.html |
| Timestream | https://docs.aws.amazon.com/timestream/latest/developerguide/what-is-timestream.html |
| Redshift | https://docs.aws.amazon.com/redshift/latest/mgmt/welcome.html |
| OpenSearch | https://docs.aws.amazon.com/opensearch-service/latest/developerguide/what-is.html |
| KMS | https://docs.aws.amazon.com/kms/latest/developerguide/overview.html |
| CloudHSM | https://docs.aws.amazon.com/cloudhsm/latest/userguide/introduction.html |
| ACM | https://docs.aws.amazon.com/acm/latest/userguide/acm-overview.html |
| Private CA | https://docs.aws.amazon.com/privateca/latest/userguide/PcaWelcome.html |
| Secrets Manager | https://docs.aws.amazon.com/secretsmanager/latest/userguide/intro.html |
| Cognito | https://docs.aws.amazon.com/cognito/latest/developerguide/what-is-amazon-cognito.html |
| Verified Permissions | https://docs.aws.amazon.com/verifiedpermissions/latest/userguide/what-is-avp.html |
| CloudWatch | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/WhatIsCloudWatch.html |
| CloudWatch Logs | https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/WhatIsCloudWatchLogs.html |
| Embedded metric format | https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/CloudWatch_Embedded_Metric_Format.html |
| X-Ray | https://docs.aws.amazon.com/xray/latest/devguide/aws-xray.html |
| CloudTrail | https://docs.aws.amazon.com/awscloudtrail/latest/userguide/cloudtrail-user-guide.html |
| Config | https://docs.aws.amazon.com/config/latest/developerguide/WhatIsConfig.html |
| Systems Manager | https://docs.aws.amazon.com/systems-manager/latest/userguide/what-is-systems-manager.html |
| Service Quotas | https://docs.aws.amazon.com/servicequotas/latest/userguide/intro.html |
| Cost Explorer | https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html |
| Cost and Usage Report | https://docs.aws.amazon.com/cur/latest/userguide/what-is-cur.html |
| Budgets | https://docs.aws.amazon.com/cost-management/latest/userguide/budgets-managing-costs.html |
| Compute Optimizer | https://docs.aws.amazon.com/compute-optimizer/latest/ug/what-is-compute-optimizer.html |
| Trusted Advisor | https://docs.aws.amazon.com/awssupport/latest/user/trusted-advisor.html |
| Security Hub | https://docs.aws.amazon.com/securityhub/latest/userguide/what-is-securityhub.html |
| GuardDuty | https://docs.aws.amazon.com/guardduty/latest/ug/what-is-guardduty.html |
| Inspector | https://docs.aws.amazon.com/inspector/latest/user/what-is-inspector.html |
| Macie | https://docs.aws.amazon.com/macie/latest/user/what-is-macie.html |
| Detective | https://docs.aws.amazon.com/detective/latest/userguide/what-is-detective.html |
| Audit Manager | https://docs.aws.amazon.com/audit-manager/latest/userguide/what-is.html |
| Firewall Manager | https://docs.aws.amazon.com/waf/latest/developerguide/fms-chapter.html |
| Access Analyzer | https://docs.aws.amazon.com/IAM/latest/UserGuide/what-is-access-analyzer.html |
| Artifact | https://docs.aws.amazon.com/artifact/latest/ug/what-is-aws-artifact.html |
| Migration Hub | https://docs.aws.amazon.com/migrationhub/latest/ug/whatishub.html |
| Application Discovery Service | https://docs.aws.amazon.com/application-discovery/latest/userguide/what-is-appdiscovery.html |
| Application Migration Service | https://docs.aws.amazon.com/mgn/latest/ug/what-is-application-migration-service.html |
| DMS | https://docs.aws.amazon.com/dms/latest/userguide/Welcome.html |
| SCT | https://docs.aws.amazon.com/SchemaConversionTool/latest/userguide/CHAP_Welcome.html |
| DataSync | https://docs.aws.amazon.com/datasync/latest/userguide/what-is-datasync.html |
| Transfer Family | https://docs.aws.amazon.com/transfer/latest/userguide/what-is-aws-transfer-family.html |
| Snow Family | https://docs.aws.amazon.com/snowball/latest/developer-guide/what-is-snowball.html |
| Glue | https://docs.aws.amazon.com/glue/latest/dg/what-is-glue.html |
| Lake Formation | https://docs.aws.amazon.com/lake-formation/latest/dg/what-is-lake-formation.html |
| Athena | https://docs.aws.amazon.com/athena/latest/ug/what-is.html |
| EMR | https://docs.aws.amazon.com/emr/latest/ManagementGuide/emr-what-is-emr.html |
| Kinesis Data Streams | https://docs.aws.amazon.com/streams/latest/dev/introduction.html |
| Data Firehose | https://docs.aws.amazon.com/firehose/latest/dev/what-is-this-service.html |
| Managed Flink | https://docs.aws.amazon.com/managed-flink/latest/java/what-is.html |
| MSK | https://docs.aws.amazon.com/msk/latest/developerguide/what-is-msk.html |
| QuickSight | https://docs.aws.amazon.com/quicksight/latest/user/welcome.html |
| CodePipeline | https://docs.aws.amazon.com/codepipeline/latest/userguide/welcome.html |
| CodeBuild | https://docs.aws.amazon.com/codebuild/latest/userguide/welcome.html |
| CodeDeploy | https://docs.aws.amazon.com/codedeploy/latest/userguide/welcome.html |
| CodeArtifact | https://docs.aws.amazon.com/codeartifact/latest/ug/welcome.html |
| AppConfig | https://docs.aws.amazon.com/appconfig/latest/userguide/what-is-appconfig.html |
| Fault Injection Service | https://docs.aws.amazon.com/fis/latest/userguide/what-is.html |
| Resilience Hub | https://docs.aws.amazon.com/resilience-hub/latest/userguide/what-is.html |
| Application Recovery Controller | https://docs.aws.amazon.com/r53recovery/latest/dg/what-is-route53-recovery.html |
| Bedrock | https://docs.aws.amazon.com/bedrock/latest/userguide/what-is-bedrock.html |
| Bedrock Guardrails | https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html |
| Bedrock AgentCore | https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/what-is-bedrock-agentcore.html |
| Amazon Q Developer | https://docs.aws.amazon.com/amazonq/latest/qdeveloper-ug/what-is.html |
| Kiro | https://kiro.dev/ or the Developer Tools entry on https://docs.aws.amazon.com/ |
| Service quotas reference | https://docs.aws.amazon.com/general/latest/gr/aws-service-information.html |
| AWS glossary | https://docs.aws.amazon.com/general/latest/gr/glos-chap.html |
| Global infrastructure regions | https://docs.aws.amazon.com/global-infrastructure/latest/regions/aws-regions.html |
| Shared responsibility model | https://aws.amazon.com/compliance/shared-responsibility-model/ |
| AWS Artifact agreements | Inside the Artifact console and https://docs.aws.amazon.com/artifact/latest/ug/what-is-aws-artifact.html |

## Code samples

| Resource | URL |
| --- | --- |
| AWS Code Example Library | https://docs.aws.amazon.com/code-library/latest/ug/what-is-code-library.html |
| Serverless examples | https://github.com/aws-samples/serverless-patterns and https://serverlessland.com/ |
| Prescriptive guidance code | Linked from each pattern page |
| Powertools for AWS Lambda | https://docs.powertools.aws.dev/lambda/python/latest/ |

Use the code library when an exercise says “implement GetItem with a condition.” Copying a whole sample into your notes does not teach the API. Type the call, then compare.

## What this pack will not duplicate

AWS owns the exam items, the whitepaper prose, and the API reference. This pack teaches you to answer. When you want the canonical sentence, open the link. When a quota in `06-reference/service-limits-and-quotas.md` looks stale, open the service quotas page for that service in your Region. Quotas change, and they are often adjustable.
