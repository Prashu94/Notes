# Product catalog and exam weight

Every area on the AWS documentation home page as reviewed for this pack (the uploaded docs landing page and the three exam guides, October 2026). Weight means how you study it for these exams.

| Weight | Meaning |
| --- | --- |
| Must | A scenario answer. Read the service chapter |
| Recognize | One honest sentence, so the distractor loses |
| Out | The guide says out of scope, or the product never decides these exams. Still know the sentence |

SAA, SAP, and DVA columns. "C03" means the September 2026 announcement raises it.

## Analytics

| Service | SAA | SAP | DVA | Sentence |
| --- | --- | --- | --- | --- |
| Athena | Must | Must | Must | SQL on S3 |
| Glue | Must | Must | Recognize | ETL and catalog |
| Kinesis Data Streams | Must | Must | Must | Replayable stream |
| Data Firehose | Must | Must | C03 must | Delivery, not replay |
| EMR | Must | Must | Out as a design tool | Spark and Hadoop |
| Lake Formation | Must | Must, C03 higher | Recognize | Lake permissions |
| MSK | Must | Must | Recognize | Kafka |
| OpenSearch | Must | Must | Must | Search and logs |
| Redshift | Must | Must | Out | Warehouse |
| QuickSight | Must | Must | Out | Dashboards |
| Managed Flink | Recognize | Must | Out | Stream processing |
| Data Exchange | Recognize | Recognize | Out | Third-party data sets |
| Clean Rooms | Recognize | C03 must | Out | Joint analytics without sharing rows |
| DataZone, FinSpace, CloudSearch | Out | Recognize the name | Out | Not the default answer |

## Application integration

| Service | SAA | SAP | DVA |
| --- | --- | --- | --- |
| SQS, SNS, EventBridge, Step Functions | Must | Must | Must |
| AppSync | Recognize | Must | Must |
| MQ | Must | Must | Recognize |
| AppFlow | Must | Must | Out |
| MWAA | Out | Recognize | Out |
| SWF | Out | Recognize as legacy | Out |
| B2B Data Interchange | Out | Out | Out |

## Compute and containers

| Service | SAA | SAP | DVA |
| --- | --- | --- | --- |
| EC2, ASG, Lambda, Beanstalk | Must | Must | Must for Lambda and the app host |
| Fargate, ECS, EKS, ECR | Must | Must | C03 must. C02 lists ECR, ECS, EKS |
| Batch | Must | Must | Out |
| Outposts, Wavelength | Must | Must | Out |
| Lightsail | Out | Recognize | Out |
| App Runner | Recognize | Must | Recognize |
| ParallelCluster, App2Container | Recognize | Recognize | Out |
| ROSA | Recognize | Recognize | Out |

## Databases

Aurora, RDS, DynamoDB, ElastiCache: must on SAA and SAP. DVA must for Aurora, DynamoDB, ElastiCache, RDS. DocumentDB, Neptune, Keyspaces: SAA and SAP recognize and sometimes must when the model is named. Timestream: SAP recognize. MemoryDB: SAP and SAA when durability plus Redis is the sentence. QLDB: recognize. RDS on VMware: out.

## Developer tools

| Service | SAA | SAP | DVA |
| --- | --- | --- | --- |
| CloudFormation | Must | Must | Must |
| CDK | Out | Recognize, often the real tool | Must |
| SAM | Recognize | Must | Must |
| CodeBuild, CodeDeploy, CodePipeline, CodeArtifact | Out | Must | Must |
| CodeCommit | Out | Recognize | Recognize. New work uses external Git |
| X-Ray | Must | Must | Must |
| Q Developer | Out | Recognize | Must |
| Kiro | Out | Out | C03 must |
| CloudShell | Out | Recognize | Must |
| CodeGuru, Copilot | Out | CodeGuru is on the SAP list | Removed from DVA in guide 2.1 |
| FIS | Out on the SAA guide | C03 must | Out |
| Cloud9 | Out | Out | Recognize |

## Management

Organizations, Control Tower, Config, CloudTrail, CloudWatch, Systems Manager, Trusted Advisor, Service Catalog, Compute Optimizer, Backup: must for SAA and SAP. DVA must for CloudTrail, CloudWatch, Systems Manager, AppConfig, CloudFormation, CDK. Resilience Hub, ARC: SAP C03 must. Proton, License Manager, Managed Grafana, Managed Prometheus: SAP recognize, C03 higher for container metrics. Well-Architected Tool: recognize.

## Migration

MGN, DMS, DataSync, Snow, Transfer Family: SAA and SAP must. DVA lists Discovery and MGN as out. SCT and Migration Hub: SAP must, SAA recognize.

## Networking

VPC, Route 53, CloudFront, ELB, TGW, PrivateLink, DX, VPN, Global Accelerator: SAA and SAP must. DVA must for API Gateway, CloudFront, ELB, Route 53, VPC at the "Lambda in a VPC" depth. Lattice: SAP C03 must. Client VPN: SAA must. Verified Access: recognize. Cloud Map: SAA guide says out. App Mesh: do not pick for a new design.

## Security

IAM, KMS, Cognito, ACM, Secrets Manager, WAF, Shield, GuardDuty, Inspector, Macie, Security Hub, Directory Service, Identity Center, Private CA, CloudHSM, Network Firewall, RAM, Firewall Manager: SAA and SAP as in the domain chapters. DVA must: Cognito, IAM, KMS, Secrets Manager, STS, WAF. Shield is out of scope on the DVA-C02 guide. Detective, Audit Manager, Artifact: SAP and SAA recognize to must. Verified Permissions: DVA and SAA when the stem is app authZ.

## Storage

S3, EBS, EFS, FSx, Backup, Glacier: must. Storage Gateway: SAA and SAP must, DVA out. DRS: SAP must, SAA recognize.

## Machine learning beyond the AI chapter

SAA and SAP: the managed APIs (Comprehend, Lex, Polly, Rekognition, SageMaker AI, Textract, Transcribe, Translate) are "pick the API." Training details are out. Personalize, Fraud Detector, Kendra are on the SAP list. Polly and Rekognition are out on DVA-C02. SageMaker AI is out of scope for DVA-C03 by the September blog. Bedrock is SAP-C03 and DVA-C03.

## Everything else on the docs home

| Area | Weight |
| --- | --- |
| Game tech, GameLift, Lumberyard | Out on all three |
| IoT | Out on SAA and DVA. SAP recognize the names on the C02 list |
| Media Elemental, IVS | Out, except Elastic Transcoder and Kinesis Video Streams on SAA and SAP |
| Business apps: Connect, Chime, Pinpoint, SES | SES and Pinpoint recognize on SAP and SAA. Chime, Connect, WorkMail out on DVA |
| End user: WorkSpaces, AppStream | SAP recognize. SAA out. DVA out |
| Blockchain, Braket, Ground Station, RoboMaker | Out or recognize-only |
| Front end: Amplify, Device Farm, Location | Amplify and API Gateway and Device Farm as in the API chapter. Location out on SAA |
| Cost, Billing, Savings Plans | Must. See the cost chapter |
| Marketplace, Partner Central, Support, Artifact | Recognize |
| Quantum, Satellite, Mainframe Modernization, Transform | Recognize the name, do not build a week around it |

When a new service appears on the docs home after October 2026, add a row. Do not add a study week until an exam guide names it.
