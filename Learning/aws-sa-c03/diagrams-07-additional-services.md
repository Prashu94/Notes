# AWS SAA-C03 - Additional Services Flow Diagrams

## FSx File Systems Decision Tree

```mermaid
flowchart TD
    Start([Choose FSx File System]) --> Protocol{Protocol & Workload?}
    
    Protocol --> |Windows SMB<br/>Active Directory| FSxWindows[FSx for Windows File Server<br/>---<br/>🪟 SMB Protocol 2.x/3.x<br/>🔐 Active Directory Integration<br/>📁 NTFS Features ACLs, Quotas<br/>💾 DFS Namespaces Support<br/>---<br/>Deployment:<br/>• Single-AZ: Dev/Test<br/>• Multi-AZ: Production HA<br/>---<br/>Storage:<br/>• SSD: Up to 2 GB/s, 100K IOPS<br/>• HDD: Cost-effective, 12K IOPS<br/>---<br/>Features:<br/>• Data Deduplication<br/>• Shadow Copies VSS<br/>• Encryption at Rest/Transit<br/>• Automatic Backups<br/>---<br/>💰 Pay for Storage + Throughput<br/>💡 Windows Applications]
    
    Protocol --> |High Performance<br/>HPC/ML| FSxLustre[FSx for Lustre<br/>---<br/>⚡ High Performance Computing<br/>🔬 Machine Learning Training<br/>🎬 Media Processing<br/>🔗 S3 Integration Native<br/>---<br/>Performance:<br/>• Up to 1,000s GB/s Throughput<br/>• Millions of IOPS<br/>• Sub-millisecond Latency<br/>---<br/>Deployment Types:<br/>1️⃣ Scratch: Temporary, 2x performance<br/>2️⃣ Persistent: Long-term, replicated<br/>---<br/>S3 Integration:<br/>• Import from S3<br/>• Export to S3<br/>• Lazy Load from S3<br/>• Automatic Export on Change<br/>---<br/>💰 Pay for Storage + Throughput<br/>💡 Burst Workloads, Analytics]
    
    Protocol --> |Multi-Protocol<br/>Enterprise NAS| FSxONTAP[FSx for NetApp ONTAP<br/>---<br/>🌐 Multi-Protocol Support<br/>• NFS Linux<br/>• SMB Windows<br/>• iSCSI Block Storage<br/>---<br/>Features:<br/>• Snapshots & Cloning<br/>• Replication SnapMirror<br/>• Data Tiering<br/>• Storage Efficiency<br/>• Thin Provisioning<br/>---<br/>Deployment:<br/>• Multi-AZ HA<br/>• Single-AZ<br/>---<br/>Migration:<br/>• Lift-and-shift NetApp<br/>• Hybrid Cloud<br/>---<br/>💰 Most Feature-Rich<br/>💡 Enterprise Migrations]
    
    Protocol --> |Linux<br/>ZFS Features| FSxOpenZFS[FSx for OpenZFS<br/>---<br/>🐧 Linux Workloads<br/>📊 NFS Protocol v3/4/4.1/4.2<br/>⚡ Up to 1 million IOPS<br/>---<br/>Features:<br/>• Snapshots Instant<br/>• Cloning Fast<br/>• Data Compression<br/>• Z-Standard Compression<br/>• Point-in-time Recovery<br/>---<br/>Performance:<br/>• Up to 12.5 GB/s Throughput<br/>• Sub-millisecond Latency<br/>• NVMe Storage<br/>---<br/>Use Cases:<br/>• Linux Databases<br/>• DevOps<br/>• Media Processing<br/>---<br/>💰 Cost-Effective Performance<br/>💡 Linux File Shares]
    
    FSxWindows --> WindowsDetails[FSx Windows Details<br/>---<br/>Active Directory Options:<br/>1️⃣ AWS Managed Microsoft AD<br/>   • Fully managed<br/>   • Native AWS integration<br/>---<br/>2️⃣ Self-Managed AD<br/>   • On-premises AD<br/>   • Requires VPN/DX<br/>   • Trust relationships<br/>---<br/>3️⃣ AD Connector<br/>   • Proxy to on-premises<br/>   • No caching<br/>---<br/>Backup Strategy:<br/>• Automatic Daily Backups<br/>• Retention: Up to 90 days<br/>• User-initiated: Up to 10 years<br/>• Shadow Copies for Users<br/>---<br/>Throughput Capacity:<br/>8 MB/s to 2,048 MB/s per TB]
    
    FSxLustre --> LustreDetails[FSx Lustre Details<br/>---<br/>Deployment Types:<br/>---<br/>Scratch File System:<br/>⚡ 2x Performance<br/>💾 No Replication<br/>⚠️ Data Not Persisted<br/>💰 Lower Cost<br/>💡 Temporary Workloads<br/>---<br/>Persistent File System:<br/>💾 Replicated within AZ<br/>🔄 Automatic Recovery<br/>📦 Long-term Storage<br/>💰 Higher Cost<br/>💡 Production Workloads<br/>---<br/>S3 Linking:<br/>• Import: Copy S3 to FSx<br/>• Export: Export FSx to S3<br/>• AutoImport: New S3 objects<br/>• AutoExport: FSx changes to S3<br/>---<br/>💡 3-5x Cost of S3<br/>100x Performance of S3]
    
    FSxONTAP --> ONTAPDetails[FSx ONTAP Details<br/>---<br/>Storage Efficiency:<br/>• Deduplication<br/>• Compression<br/>• Compaction<br/>• Thin Provisioning<br/>---<br/>Data Protection:<br/>• Snapshots Instant<br/>• SnapMirror Replication<br/>• SnapVault Backup<br/>• Clone Volumes<br/>---<br/>Tiering:<br/>• Hot Tier: SSD<br/>• Cool Tier: Capacity Pool<br/>• Auto-tiering Policies<br/>---<br/>Performance:<br/>• Up to 2 GB/s Throughput<br/>• Up to 80,000 IOPS<br/>---<br/>💡 Best for NetApp Migrations]
    
    FSxOpenZFS --> OpenZFSDetails[FSx OpenZFS Details<br/>---<br/>ZFS Features:<br/>• Copy-on-Write<br/>• Data Integrity Checks<br/>• Snapshots Zero-copy<br/>• Compression Z-Standard<br/>---<br/>Performance Tiers:<br/>• Up to 160 MB/s per TiB<br/>• Up to 1 million IOPS<br/>• Configurable Throughput<br/>---<br/>Volume Management:<br/>• Multiple Volumes<br/>• Nested Volumes<br/>• Quotas & Reservations<br/>---<br/>Snapshot Strategy:<br/>• Unlimited Snapshots<br/>• Instant Creation<br/>• No Performance Impact<br/>• Point-in-time Restore<br/>---<br/>💡 Best Price-Performance]
    
    style FSxWindows fill:#4CAF50
    style FSxLustre fill:#FF6B6B
    style FSxONTAP fill:#2196F3
    style FSxOpenZFS fill:#9C27B0
```

## Cognito Authentication & Authorization

```mermaid
flowchart TD
    Start([User Authentication Need]) --> CognitoType{Cognito Component?}
    
    CognitoType --> |User Directory<br/>Authentication| UserPools[Cognito User Pools<br/>---<br/>👤 User Directory Service<br/>🔐 Sign-up & Sign-in<br/>🎯 Authentication Only<br/>---<br/>Authentication Methods:<br/>• Username/Password<br/>• Email/Phone + Password<br/>• Social Providers<br/>• SAML/OIDC Federation<br/>• Multi-Factor Auth MFA<br/>---<br/>Features:<br/>• User Management<br/>• Password Policies<br/>• Account Recovery<br/>• Email/SMS Verification<br/>• Lambda Triggers<br/>---<br/>💡 "Who are you?"]
    
    CognitoType --> |AWS Credentials<br/>Authorization| IdentityPools[Cognito Identity Pools<br/>Federated Identities<br/>---<br/>🎫 Temporary AWS Credentials<br/>🔑 IAM Role Assumption<br/>🎯 Authorization for AWS<br/>---<br/>Identity Providers:<br/>• Cognito User Pools<br/>• Social Facebook, Google<br/>• SAML<br/>• OpenID Connect<br/>• Guest Unauthenticated<br/>---<br/>Returns:<br/>• Access Key ID<br/>• Secret Access Key<br/>• Session Token<br/>• Expiration<br/>---<br/>💡 "What can you access?"]
    
    UserPools --> UserPoolsFeatures[User Pool Features<br/>---<br/>Tokens Issued JWT:<br/>1️⃣ ID Token<br/>   • User Identity Info<br/>   • User Attributes<br/>   • Valid: 1 hour default<br/>---<br/>2️⃣ Access Token<br/>   • Authorization to Resources<br/>   • Contains Scopes<br/>   • Valid: 1 hour default<br/>---<br/>3️⃣ Refresh Token<br/>   • Get New Tokens<br/>   • Valid: 30 days default<br/>   • Max: 10 years<br/>---<br/>MFA Options:<br/>• SMS Text Message<br/>• TOTP Time-based<br/>• Software Token Apps<br/>---<br/>Advanced Security:<br/>• Adaptive Authentication<br/>• Compromised Credentials<br/>• Risk-based Auth]
    
    IdentityPools --> IdentityPoolsFeatures[Identity Pool Features<br/>---<br/>IAM Roles:<br/>• Authenticated Role<br/>• Unauthenticated Role<br/>• Role-based Access<br/>---<br/>Access Control:<br/>• Fine-grained AWS Access<br/>• Temporary Credentials<br/>• Automatic Rotation<br/>---<br/>Policy Variables:<br/>• cognito-identity.amazonaws.com:sub<br/>• User-specific Permissions<br/>• Dynamic Policies<br/>---<br/>Use Cases:<br/>• Mobile App → S3 Access<br/>• Web App → DynamoDB<br/>• IoT Device → IoT Core<br/>• Guest Access Limited]
    
    UserPoolsFeatures --> Integration{Integration<br/>Pattern?}
    
    Integration --> |API Access| APIGW[API Gateway + User Pools<br/>---<br/>Flow:<br/>1️⃣ User Authenticates<br/>2️⃣ Receives ID/Access Token<br/>3️⃣ Calls API with Token<br/>4️⃣ API Gateway Validates<br/>5️⃣ Passes to Backend<br/>---<br/>Configuration:<br/>• Cognito Authorizer<br/>• Token Validation<br/>• Automatic Verification<br/>---<br/>💡 Serverless Auth Pattern]
    
    Integration --> |Web/Mobile App| AppIntegration[Application Integration<br/>---<br/>Web App Flow:<br/>1️⃣ Hosted UI or Custom<br/>2️⃣ OAuth 2.0/OIDC<br/>3️⃣ Callback URL<br/>4️⃣ Token Exchange<br/>---<br/>Mobile App Flow:<br/>1️⃣ AWS Amplify SDK<br/>2️⃣ Native Sign-in<br/>3️⃣ Token Management<br/>4️⃣ Automatic Refresh<br/>---<br/>Social Login:<br/>• Facebook<br/>• Google<br/>• Amazon<br/>• Apple<br/>---<br/>💡 Drop-in UI Available]
    
    Integration --> |Enterprise SSO| Federation[Enterprise Federation<br/>---<br/>SAML 2.0:<br/>• Corporate IdP<br/>• Okta, OneLogin<br/>• Azure AD<br/>---<br/>OpenID Connect:<br/>• Custom OIDC Provider<br/>• JWT-based<br/>---<br/>Process:<br/>1️⃣ User → Corporate IdP<br/>2️⃣ IdP → SAML/OIDC Token<br/>3️⃣ Token → User Pool<br/>4️⃣ User Pool → JWT Tokens<br/>---<br/>💡 Enterprise SSO Solution]
    
    IdentityPoolsFeatures --> AWSAccess[AWS Resource Access<br/>---<br/>Direct Access Pattern:<br/>Mobile/Web App<br/>↓ Authenticate<br/>Cognito Identity Pool<br/>↓ Assume IAM Role<br/>Temporary Credentials<br/>↓ Direct Access<br/>AWS Services S3, DynamoDB<br/>---<br/>Benefits:<br/>✅ No Backend Server<br/>✅ Secure Credentials<br/>✅ Fine-grained Control<br/>✅ Cost-effective<br/>---<br/>💡 Serverless Pattern]
    
    style UserPools fill:#4CAF50
    style IdentityPools fill:#2196F3
    style APIGW fill:#FF6B6B
```

## AWS Organizations Structure & SCPs

```mermaid
flowchart TD
    Start([AWS Organization]) --> Root[Root<br/>---<br/>🏢 Organization Container<br/>👑 Management Account<br/>📊 All Member Accounts<br/>---<br/>Management Account:<br/>• Pays All Charges<br/>• Full Admin Control<br/>• Cannot be Restricted by SCP<br/>• Creates Organization<br/>---<br/>Member Accounts:<br/>• Subject to SCPs<br/>• One Org at a Time<br/>• Can be Moved between OUs]
    
    Root --> OUStructure{Organizational Units?}
    
    OUStructure --> |Environment-based| EnvOU[Environment OUs<br/>---<br/>Root<br/>├── Production OU<br/>│   ├── Prod-Web<br/>│   └── Prod-DB<br/>├── Staging OU<br/>│   └── Staging-Test<br/>└── Development OU<br/>    ├── Dev-Team1<br/>    └── Dev-Team2<br/>---<br/>Benefits:<br/>• Clear Separation<br/>• Different Policies<br/>• Cost Tracking<br/>---<br/>💡 Most Common Pattern]
    
    OUStructure --> |Function-based| FunctionOU[Functional OUs<br/>---<br/>Root<br/>├── Security OU<br/>│   ├── Log Archive<br/>│   └── Security Audit<br/>├── Shared Services OU<br/>│   ├── Networking<br/>│   └── DNS<br/>└── Workloads OU<br/>    ├── Applications<br/>    └── Databases<br/>---<br/>Benefits:<br/>• Service Isolation<br/>• Centralized Services<br/>• Security Focus<br/>---<br/>💡 Enterprise Pattern]
    
    OUStructure --> |Business Unit| BusinessOU[Business Unit OUs<br/>---<br/>Root<br/>├── Marketing OU<br/>│   ├── Campaigns<br/>│   └── Analytics<br/>├── Finance OU<br/>│   ├── Accounting<br/>│   └── Reporting<br/>└── Engineering OU<br/>    ├── Product-A<br/>    └── Product-B<br/>---<br/>Benefits:<br/>• Department Isolation<br/>• Cost Allocation<br/>• Autonomy<br/>---<br/>💡 Large Organizations]
    
    EnvOU --> SCP
    FunctionOU --> SCP
    BusinessOU --> SCP
    
    SCP[Service Control Policies SCPs<br/>---<br/>🛡️ Permission Boundaries<br/>🚫 Guardrails NOT Grants<br/>📋 JSON Policy Documents<br/>---<br/>Characteristics:<br/>• Restrict Maximum Permissions<br/>• Hierarchical Inheritance<br/>• Affect IAM Users & Roles<br/>• Don't Affect Management Acct<br/>---<br/>Evaluation:<br/>Account Must Pass:<br/>1️⃣ SCP Check<br/>2️⃣ IAM Permission Check<br/>Both Required!]
    
    SCP --> SCPType{SCP Strategy?}
    
    SCPType --> |Default<br/>More Permissive| DenyList[Deny List Blacklist<br/>---<br/>📋 Default: Allow All<br/>🚫 Explicitly Deny Specific<br/>---<br/>Example:<br/>"Effect": "Deny"<br/>"Action": "ec2:TerminateInstances"<br/>---<br/>Use Cases:<br/>• Prevent Region Access<br/>• Block Services<br/>• Protect Resources<br/>• Compliance Requirements<br/>---<br/>Common Denies:<br/>• Leaving Region<br/>• Root User Actions<br/>• Disabling CloudTrail<br/>• Deleting KMS Keys<br/>---<br/>💡 Easier to Manage]
    
    SCPType --> |Restrictive<br/>More Secure| AllowList[Allow List Whitelist<br/>---<br/>📋 Default: Deny All<br/>✅ Explicitly Allow Specific<br/>---<br/>Example:<br/>"Effect": "Allow"<br/>"Action": ["s3:*", "ec2:*"]<br/>---<br/>Use Cases:<br/>• High Security<br/>• Regulatory Compliance<br/>• Limited Service Access<br/>• Sandbox Accounts<br/>---<br/>Requirements:<br/>• Must Allow All Needed<br/>• More Maintenance<br/>• Careful Planning<br/>---<br/>💡 Maximum Security]
    
    DenyList --> SCPExamples[Common SCP Patterns<br/>---<br/>1️⃣ Restrict Regions:<br/>"Condition": <br/>  "StringNotEquals":<br/>    "aws:RequestedRegion":<br/>      ["us-east-1", "us-west-2"]<br/>---<br/>2️⃣ Require MFA:<br/>"Condition":<br/>  "BoolIfExists":<br/>    "aws:MultiFactorAuthPresent": "false"<br/>---<br/>3️⃣ Prevent Root Access:<br/>"Condition":<br/>  "StringLike":<br/>    "aws:PrincipalArn": "arn:aws:iam::*:root"<br/>---<br/>4️⃣ Enforce Encryption:<br/>"Condition":<br/>  "StringNotEquals":<br/>    "s3:x-amz-server-side-encryption":<br/>      "AES256"]
    
    AllowList --> SCPExamples
    
    SCPExamples --> ConsolidatedBilling[Consolidated Billing<br/>---<br/>💰 Single Bill for All Accounts<br/>📊 Volume Discounts<br/>🎯 Cost Allocation Tags<br/>---<br/>Benefits:<br/>• Volume Pricing Tiers<br/>• Reserved Instance Sharing<br/>• Savings Plan Sharing<br/>• Unified Billing View<br/>---<br/>Cost Allocation:<br/>• Tag-based Breakdown<br/>• Per-Account Costs<br/>• Per-OU Reports<br/>• Detailed Cost Explorer<br/>---<br/>Pricing Advantages:<br/>✅ S3 Volume Discounts<br/>✅ EC2 RI Sharing<br/>✅ Compute Savings Plans<br/>---<br/>💡 Major Cost Benefit]
    
    ConsolidatedBilling --> Features[Organizations Features<br/>---<br/>🔧 Service Integration:<br/>• CloudTrail → Org Trail<br/>• Config → Org Aggregator<br/>• GuardDuty → Org<br/>• Security Hub → Org<br/>• Firewall Manager → Org<br/>---<br/>🔒 Security:<br/>• Centralized Logging<br/>• Cross-Account Roles<br/>• Compliance Policies<br/>• Tag Policies<br/>---<br/>📊 Management:<br/>• Account Creation API<br/>• Automatic Account Setup<br/>• StackSets Deployment<br/>---<br/>💡 Enterprise Governance]
    
    style Root fill:#FF6B6B
    style EnvOU fill:#4CAF50
    style DenyList fill:#2196F3
    style ConsolidatedBilling fill:#FFC107
```

## Additional Security Services

```mermaid
flowchart TD
    Start([Security Services]) --> Type{Service Type?}
    
    Type --> |Threat Detection<br/>ML-based| GuardDuty[Amazon GuardDuty<br/>---<br/>🔍 Threat Detection Service<br/>🤖 Machine Learning<br/>⚡ Real-time Monitoring<br/>---<br/>Data Sources:<br/>• VPC Flow Logs<br/>• CloudTrail Events<br/>• DNS Logs<br/>• EKS Audit Logs<br/>• S3 Data Events<br/>---<br/>Detects:<br/>• Cryptocurrency Mining<br/>• Unusual API Calls<br/>• Compromised Instances<br/>• Reconnaissance Attempts<br/>• Unauthorized Access<br/>---<br/>💰 30-Day Free Trial<br/>💡 Enable in All Accounts]
    
    Type --> |Vulnerability<br/>Assessment| Inspector[Amazon Inspector<br/>---<br/>🔎 Automated Vulnerability Scanning<br/>🖥️ EC2, ECR, Lambda<br/>📊 Risk-based Scoring<br/>---<br/>Scans:<br/>• Software Vulnerabilities<br/>• Network Exposure<br/>• Package Vulnerabilities<br/>• CVE Database<br/>---<br/>Findings:<br/>• CVSS Scores<br/>• Remediation Steps<br/>• Prioritized by Risk<br/>• Integration with Security Hub<br/>---<br/>💰 Pay per Assessment<br/>💡 Continuous Scanning]
    
    Type --> |DDoS Protection<br/>Network Layer| Shield[AWS Shield<br/>---<br/>🛡️ DDoS Protection<br/>---<br/>Shield Standard:<br/>• Free for All<br/>• Layer 3/4 Protection<br/>• Always-On Detection<br/>• Automatic Mitigation<br/>---<br/>Shield Advanced:<br/>💰 $3,000/month<br/>• Enhanced Protection<br/>• Application Layer Layer 7<br/>• 24/7 DDoS Response Team<br/>• Cost Protection<br/>• CloudFront, Route 53, ELB<br/>• Real-time Notifications<br/>• Attack Forensics<br/>---<br/>💡 Standard = Free<br/>💡 Advanced = Enterprise]
    
    Type --> |Web App Firewall<br/>Layer 7| WAF[AWS WAF<br/>---<br/>🔥 Web Application Firewall<br/>🌐 Layer 7 HTTP/HTTPS<br/>🎯 Rule-based Filtering<br/>---<br/>Protects:<br/>• CloudFront<br/>• Application Load Balancer<br/>• API Gateway<br/>• AppSync<br/>---<br/>Rules:<br/>• IP Address Allow/Block<br/>• HTTP Headers<br/>• HTTP Body<br/>• URI Strings<br/>• SQL Injection Protection<br/>• XSS Protection<br/>• Geo-matching<br/>• Rate-based Rules<br/>---<br/>Managed Rules:<br/>• AWS Managed<br/>• Marketplace Rules<br/>• Custom Rules<br/>---<br/>💰 $5/month + per request<br/>💡 Protect Web Apps]
    
    Type --> |Secrets Storage<br/>Rotation| Secrets[AWS Secrets Manager<br/>---<br/>🔐 Secrets Storage<br/>🔄 Automatic Rotation<br/>🔑 API-based Access<br/>---<br/>Stores:<br/>• Database Credentials<br/>• API Keys<br/>• OAuth Tokens<br/>• SSH Keys<br/>• Custom Secrets<br/>---<br/>Features:<br/>• Automatic Rotation<br/>• Lambda Integration<br/>• Fine-grained IAM<br/>• Encryption at Rest KMS<br/>• Audit with CloudTrail<br/>• Cross-Region Replication<br/>---<br/>Rotation:<br/>• RDS/Aurora: Automatic<br/>• Custom: Lambda Function<br/>• Schedule: 30-365 days<br/>---<br/>💰 $0.40/month per secret<br/>💡 Better than Parameter Store]
    
    Type --> |Certificate<br/>Management| ACM[AWS Certificate Manager<br/>---<br/>📜 SSL/TLS Certificates<br/>🆓 Free Public Certificates<br/>🔄 Automatic Renewal<br/>---<br/>Certificate Types:<br/>1️⃣ Public Certificates Free<br/>   • DV Certificates<br/>   • Wildcard Support<br/>   • Auto-renewal<br/>---<br/>2️⃣ Private Certificates<br/>   • Private CA Required<br/>   • Internal Applications<br/>   • Pay per Certificate<br/>---<br/>Integrations:<br/>• CloudFront<br/>• Elastic Load Balancer<br/>• API Gateway<br/>• CloudFormation<br/>---<br/>💡 Free Public Certs<br/>💡 Auto-renewal]
    
    GuardDuty --> GuardDutyDetails[GuardDuty Details<br/>---<br/>Severity Levels:<br/>• Low 0.1-3.9<br/>• Medium 4.0-6.9<br/>• High 7.0-8.9<br/>---<br/>Finding Types:<br/>• Backdoor: Unusual traffic<br/>• Behavior: Anomalous activity<br/>• Cryptocurrency: Mining<br/>• Pentest: Penetration testing<br/>• Persistence: Unauthorized access<br/>• Policy: IAM issues<br/>• Recon: Reconnaissance<br/>• ResourceConsumption: Abuse<br/>• Stealth: Hide activities<br/>• Trojan: Malware<br/>• UnauthorizedAccess<br/>---<br/>Response:<br/>• EventBridge Rules<br/>• Lambda Remediation<br/>• SNS Notifications<br/>---<br/>💰 14-day Free Trial]
    
    Inspector --> InspectorDetails[Inspector Details<br/>---<br/>Assessment Types:<br/>1️⃣ Network Assessments<br/>   • No Agent Required<br/>   • Network Reachability<br/>   • Port Analysis<br/>---<br/>2️⃣ Host Assessments<br/>   • Agent Required<br/>   • CVE Vulnerabilities<br/>   • CIS Benchmarks<br/>   • Security Best Practices<br/>---<br/>Supported:<br/>• EC2 Instances<br/>• ECR Container Images<br/>• Lambda Functions<br/>---<br/>Reporting:<br/>• Detailed Findings<br/>• Remediation Guidance<br/>• Integration Security Hub<br/>---<br/>💡 Continuous Monitoring]
    
    Secrets --> SecretsDetails[Secrets Manager Details<br/>---<br/>vs Systems Manager Parameter Store:<br/>---<br/>Secrets Manager:<br/>✅ Automatic Rotation<br/>✅ Cross-Region Replication<br/>✅ Fine-grained Access<br/>💰 $0.40/secret/month<br/>💰 $0.05 per 10K API calls<br/>---<br/>Parameter Store:<br/>✅ Free Standard<br/>✅ Simple Key-Value<br/>✅ Integration SSM<br/>❌ No Auto-rotation Standard<br/>💰 Advanced: $0.05/param/month<br/>---<br/>Choose Secrets Manager:<br/>• Database Credentials<br/>• Automatic Rotation<br/>• High Security Needs<br/>---<br/>Choose Parameter Store:<br/>• Configuration Data<br/>• Cost-sensitive<br/>• Simple Secrets]
    
    style GuardDuty fill:#FF6B6B
    style WAF fill:#4CAF50
    style Secrets fill:#2196F3
    style Shield fill:#9C27B0
```

## Infrastructure as Code & Management

```mermaid
flowchart TD
    Start([Infrastructure Management]) --> Service{Management Service?}
    
    Service --> |Infrastructure as Code<br/>Declarative| CloudFormation[AWS CloudFormation<br/>---<br/>📄 Infrastructure as Code<br/>📋 JSON/YAML Templates<br/>🔄 Stack Management<br/>---<br/>Components:<br/>• Templates: Define resources<br/>• Stacks: Deployed resources<br/>• StackSets: Multi-account/region<br/>• Change Sets: Preview changes<br/>---<br/>Features:<br/>• Drift Detection<br/>• Rollback on Failure<br/>• Cross-Stack References<br/>• Nested Stacks<br/>• Custom Resources Lambda<br/>---<br/>Benefits:<br/>✅ Version Control<br/>✅ Reproducible<br/>✅ Automated<br/>✅ Free Service<br/>---<br/>💡 AWS-native IaC]
    
    Service --> |Automated Patching<br/>Operations| SystemsManager[AWS Systems Manager<br/>---<br/>🔧 Operational Management<br/>🖥️ EC2 & On-Premises<br/>🤖 Automation & Compliance<br/>---<br/>Key Components:<br/>• Session Manager<br/>• Run Command<br/>• Patch Manager<br/>• Parameter Store<br/>• Automation<br/>• State Manager<br/>• OpsCenter<br/>---<br/>Agent Required:<br/>• SSM Agent<br/>• Pre-installed on Amazon Linux<br/>• Install on Other OSs<br/>---<br/>💡 Unified Management]
    
    Service --> |Cost Optimization<br/>Recommendations| TrustedAdvisor[AWS Trusted Advisor<br/>---<br/>💡 Best Practice Checks<br/>📊 Recommendations<br/>🎯 5 Categories<br/>---<br/>Categories:<br/>1️⃣ Cost Optimization<br/>   • Unused Resources<br/>   • Reserved Instance Recs<br/>---<br/>2️⃣ Performance<br/>   • Service Limits<br/>   • Throughput Issues<br/>---<br/>3️⃣ Security<br/>   • Open Ports<br/>   • IAM Use<br/>   • MFA on Root<br/>---<br/>4️⃣ Fault Tolerance<br/>   • Backup Strategy<br/>   • Multi-AZ<br/>---<br/>5️⃣ Service Limits<br/>   • Approaching Limits<br/>---<br/>💰 Basic: 7 Core Checks<br/>💰 Business+: All Checks]
    
    Service --> |Resource Backup<br/>Centralized| Backup[AWS Backup<br/>---<br/>💾 Centralized Backup Service<br/>📅 Policy-based Backup<br/>🔄 Cross-Region/Account<br/>---<br/>Supported Services:<br/>• EC2 & EBS<br/>• RDS & Aurora<br/>• DynamoDB<br/>• EFS & FSx<br/>• Storage Gateway<br/>• DocumentDB<br/>• Neptune<br/>---<br/>Features:<br/>• Backup Plans Schedules<br/>• Retention Policies<br/>• Lifecycle Rules<br/>• Cross-Region Copy<br/>• Compliance Reports<br/>• Point-in-time Recovery<br/>---<br/>💰 Pay for Storage<br/>💡 Unified Backup Solution]
    
    CloudFormation --> CFDetails[CloudFormation Details<br/>---<br/>Template Sections:<br/>• Parameters: Input values<br/>• Mappings: Static variables<br/>• Conditions: Conditional logic<br/>• Resources: AWS resources Required<br/>• Outputs: Return values<br/>• Metadata: Additional info<br/>---<br/>Intrinsic Functions:<br/>• Ref: Reference parameters<br/>• Fn::GetAtt: Get attributes<br/>• Fn::Join: String concat<br/>• Fn::Sub: Substitute variables<br/>• Fn::ImportValue: Cross-stack<br/>---<br/>Stack Operations:<br/>• Create: Deploy new<br/>• Update: Modify existing<br/>• Delete: Remove all<br/>• Change Set: Preview changes<br/>---<br/>💡 Free - Pay for Resources]
    
    SystemsManager --> SSMDetails[Systems Manager Components<br/>---<br/>Session Manager:<br/>• No SSH/RDP needed<br/>• No Bastion Host<br/>• Audit with CloudTrail<br/>• No open ports<br/>💡 Secure Shell Access<br/>---<br/>Run Command:<br/>• Execute scripts remotely<br/>• Patch instances<br/>• Install software<br/>• No SSH required<br/>---<br/>Patch Manager:<br/>• Automated patching<br/>• Patch baselines<br/>• Maintenance windows<br/>• Compliance reporting<br/>---<br/>Parameter Store:<br/>• Configuration storage<br/>• Secrets management<br/>• Hierarchical storage<br/>• Free standard tier<br/>---<br/>Automation:<br/>• Predefined runbooks<br/>• Custom workflows<br/>• Event-driven]
    
    TrustedAdvisor --> TADetails[Trusted Advisor Tiers<br/>---<br/>Basic & Developer:<br/>🆓 Free<br/>✅ 7 Core Checks<br/>• S3 Bucket Permissions<br/>• Security Groups Unrestricted<br/>• IAM Use<br/>• MFA on Root<br/>• EBS Public Snapshots<br/>• RDS Public Snapshots<br/>• Service Limits<br/>---<br/>Business & Enterprise:<br/>💰 Support Plan Required<br/>✅ All Checks 115+<br/>✅ AWS Support API<br/>✅ CloudWatch Integration<br/>✅ Weekly Email<br/>✅ Refresh Every 5 Min<br/>---<br/>Notifications:<br/>• CloudWatch Events<br/>• Email Alerts<br/>• Lambda Integration<br/>---<br/>💡 Essential for Production]
    
    Backup --> BackupDetails[AWS Backup Details<br/>---<br/>Backup Plans:<br/>• Schedule: Cron expression<br/>• Retention: Days to keep<br/>• Transition: To cold storage<br/>• Copy: To other regions<br/>---<br/>Resource Assignment:<br/>• By Tags<br/>• By Resource ID<br/>• By Resource Type<br/>---<br/>Backup Vault:<br/>• Logical Container<br/>• Encryption KMS<br/>• Access Policies<br/>• Vault Lock Compliance<br/>---<br/>Cross-Account Backup:<br/>• Organizations Integration<br/>• Central Backup Account<br/>• Compliance Reporting<br/>---<br/>💰 Pricing:<br/>• Storage: $0.05/GB/month<br/>• Restore: $0.02/GB<br/>• Cross-Region: Data transfer<br/>---<br/>💡 Compliance & DR Solution]
    
    style CloudFormation fill:#FF6B6B
    style SystemsManager fill:#4CAF50
    style TrustedAdvisor fill:#FFC107
    style Backup fill:#2196F3
```

## Storage Gateway Types

```mermaid
flowchart TD
    Start([Hybrid Cloud Storage]) --> GWType{Gateway Type?}
    
    GWType --> |File Access<br/>NFS/SMB| FileGateway[File Gateway<br/>---<br/>📁 NFS & SMB Protocol<br/>☁️ Files Stored in S3<br/>💾 Local Cache<br/>---<br/>How it Works:<br/>1️⃣ Deploy Gateway On-Prem/EC2<br/>2️⃣ Mount NFS/SMB Share<br/>3️⃣ Write Files Locally<br/>4️⃣ Async Upload to S3<br/>5️⃣ Local Cache for Recent<br/>---<br/>S3 Storage Classes:<br/>• Standard<br/>• Standard-IA<br/>• One Zone-IA<br/>• Intelligent-Tiering<br/>---<br/>Use Cases:<br/>• Backup to Cloud<br/>• File Share Migration<br/>• Cloud Bursting<br/>• Archive to S3<br/>---<br/>💡 Most Common Type]
    
    GWType --> |Block Storage<br/>iSCSI| VolumeGateway[Volume Gateway<br/>---<br/>💾 Block Storage iSCSI<br/>🖥️ Virtual Hard Drives<br/>📦 EBS Snapshots<br/>---<br/>Two Modes:<br/>1️⃣ Cached Volumes<br/>2️⃣ Stored Volumes]
    
    GWType --> |Tape Backup<br/>VTL| TapeGateway[Tape Gateway VTL<br/>---<br/>📼 Virtual Tape Library<br/>💾 Backup to S3/Glacier<br/>🔄 Existing Backup Software<br/>---<br/>Components:<br/>• Virtual Tapes<br/>• Virtual Tape Library VTL<br/>• Virtual Tape Shelf VTS<br/>---<br/>Storage:<br/>• Active Tapes → S3<br/>• Archived Tapes → Glacier<br/>---<br/>Compatible With:<br/>• NetBackup<br/>• Veeam<br/>• Backup Exec<br/>• All Major Backup Apps<br/>---<br/>Use Cases:<br/>• Replace Physical Tapes<br/>• Long-term Archive<br/>• Compliance<br/>---<br/>💡 Legacy Backup Migration]
    
    VolumeGateway --> VolumeMode{Volume Mode?}
    
    VolumeMode --> |Primary Cloud<br/>Hot Data Local| Cached[Cached Volumes<br/>---<br/>☁️ Primary Data in S3<br/>💾 Cache Recent Data Locally<br/>📦 Low-latency Access<br/>---<br/>How it Works:<br/>1️⃣ Full Data in S3<br/>2️⃣ Recent Data Cached<br/>3️⃣ Point-in-time Snapshots<br/>4️⃣ EBS Snapshots in S3<br/>---<br/>Capacity:<br/>• Volume Size: 1 GB - 32 TB<br/>• Total Volumes: 32 per gateway<br/>• Max Storage: 1 PB<br/>---<br/>Benefits:<br/>✅ Lower On-Prem Storage<br/>✅ Scalable<br/>✅ Durable in S3<br/>---<br/>💡 Cloud-First Strategy]
    
    VolumeMode --> |Primary On-Prem<br/>Backup to Cloud| Stored[Stored Volumes<br/>---<br/>💾 Primary Data On-Premises<br/>☁️ Async Backup to S3<br/>📦 Local Low Latency<br/>---<br/>How it Works:<br/>1️⃣ Full Data On-Premises<br/>2️⃣ Async Copy to S3<br/>3️⃣ Point-in-time Snapshots<br/>4️⃣ EBS Snapshots in S3<br/>---<br/>Capacity:<br/>• Volume Size: 1 GB - 16 TB<br/>• Total Volumes: 32 per gateway<br/>• Max Storage: 512 TB<br/>---<br/>Benefits:<br/>✅ Low-latency Local Access<br/>✅ Durable S3 Backup<br/>✅ DR in Cloud<br/>---<br/>💡 On-Prem-First Strategy]
    
    FileGateway --> FileDetails[File Gateway Details<br/>---<br/>Protocols:<br/>• NFS v3, v4.1<br/>• SMB v2, v3<br/>---<br/>Active Directory:<br/>• SMB requires AD<br/>• User authentication<br/>• Access control<br/>---<br/>Local Cache:<br/>• SSD recommended<br/>• Stores recent files<br/>• Reduces latency<br/>• Automatic eviction<br/>---<br/>S3 Features:<br/>• S3 Lifecycle Policies<br/>• S3 Versioning<br/>• S3 Replication<br/>• S3 Object Lock<br/>---<br/>💡 Direct S3 API Access Too]
    
    TapeGateway --> TapeDetails[Tape Gateway Details<br/>---<br/>Virtual Tape:<br/>• Size: 100 GB - 5 TB<br/>• Total: 1,500 tapes<br/>• Max: 1 PB<br/>---<br/>Storage Tiers:<br/>1️⃣ VTL Virtual Tape Library<br/>   • Active Tapes<br/>   • S3 Storage<br/>   • Immediate Restore<br/>---<br/>2️⃣ VTS Virtual Tape Shelf<br/>   • Archived Tapes<br/>   • Glacier Storage<br/>   • 3-5 Hours Restore<br/>---<br/>Backup Software:<br/>✅ Works with existing<br/>✅ No code changes<br/>✅ Standard iSCSI<br/>---<br/>💡 Cost-Effective Archive]
    
    Cached --> GatewayCommon[Common Features<br/>---<br/>Deployment Options:<br/>• VMware ESXi<br/>• Microsoft Hyper-V<br/>• Linux KVM<br/>• EC2 Instance<br/>• Hardware Appliance<br/>---<br/>Bandwidth Optimization:<br/>• Compression<br/>• Bandwidth Throttling<br/>• Upload Buffer<br/>---<br/>Security:<br/>• Encryption in Transit SSL<br/>• Encryption at Rest S3<br/>• IAM for Access Control<br/>---<br/>Monitoring:<br/>• CloudWatch Metrics<br/>• CloudWatch Alarms<br/>• Health Notifications<br/>---<br/>💡 Hybrid Cloud Bridge]
    
    Stored --> GatewayCommon
    
    style FileGateway fill:#4CAF50
    style Cached fill:#2196F3
    style TapeGateway fill:#9C27B0
```
