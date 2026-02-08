# Amazon Macie - SAA-C03 Comprehensive Guide

## Table of Contents
1. [Overview and Introduction](#overview-and-introduction)
2. [How Macie Works](#how-macie-works)
3. [Sensitive Data Discovery](#sensitive-data-discovery)
4. [S3 Bucket Security](#s3-bucket-security)
5. [Findings and Alerts](#findings-and-alerts)
6. [Integration with Other Services](#integration-with-other-services)
7. [Multi-Account Management](#multi-account-management)
8. [Security and Compliance](#security-and-compliance)
9. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
10. [Best Practices](#best-practices)
11. [AWS CLI Commands Reference](#aws-cli-commands-reference)
12. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
13. [Practice Questions](#practice-questions)

---

## Overview and Introduction

### What is Amazon Macie?

Amazon Macie is a **fully managed data security and privacy service** that uses machine learning and pattern matching to discover and protect sensitive data stored in Amazon S3.

### Key Capabilities

1. **Sensitive Data Discovery**: Automatically detect PII, financial data, credentials
2. **S3 Security Assessment**: Evaluate bucket security configurations
3. **Continuous Monitoring**: Ongoing surveillance of S3 data
4. **Compliance Support**: Help meet regulatory requirements (GDPR, HIPAA, PCI-DSS)

### Core Use Cases

- **Data Privacy**: Find and protect personal information
- **Compliance**: Meet regulatory data protection requirements
- **Security Posture**: Identify misconfigured S3 buckets
- **Data Classification**: Understand what sensitive data you have and where

### Macie at a Glance

```
┌─────────────────────────────────────────────────────────────────┐
│                    Amazon Macie Overview                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Amazon S3                        Macie Analysis                │
│   ┌─────────────────┐                                           │
│   │                 │            ┌──────────────────────┐       │
│   │  ┌───────────┐  │            │  Machine Learning    │       │
│   │  │ Documents │  │            │  + Pattern Matching  │       │
│   │  │   Data    │──┼──────────► │                      │       │
│   │  │  Images   │  │            │  Discovers:          │       │
│   │  │   Logs    │  │            │  • PII               │       │
│   │  └───────────┘  │            │  • Financial data    │       │
│   │                 │            │  • Credentials       │       │
│   └─────────────────┘            │  • Custom patterns   │       │
│                                  └──────────┬───────────┘       │
│                                             │                    │
│                                             ▼                    │
│                                  ┌──────────────────────┐       │
│                                  │      Findings        │       │
│                                  │  • EventBridge       │       │
│                                  │  • Security Hub      │       │
│                                  │  • S3/KMS            │       │
│                                  └──────────────────────┘       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## How Macie Works

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                   Macie Architecture                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │                      Amazon Macie                       │    │
│   │                                                         │    │
│   │   ┌─────────────────┐    ┌─────────────────────────┐   │    │
│   │   │  Bucket         │    │  Sensitive Data         │   │    │
│   │   │  Inventory      │    │  Discovery Jobs         │   │    │
│   │   │  & Monitoring   │    │                         │   │    │
│   │   │                 │    │  • Scheduled            │   │    │
│   │   │  • Security     │    │  • On-demand            │   │    │
│   │   │  • Public access│    │  • Custom scope         │   │    │
│   │   │  • Encryption   │    │                         │   │    │
│   │   └─────────────────┘    └─────────────────────────┘   │    │
│   │            │                        │                   │    │
│   │            └────────────┬───────────┘                   │    │
│   │                         │                               │    │
│   │                         ▼                               │    │
│   │              ┌─────────────────────┐                   │    │
│   │              │      Findings       │                   │    │
│   │              │  • Policy findings  │                   │    │
│   │              │  • Sensitive data   │                   │    │
│   │              │    findings         │                   │    │
│   │              └─────────────────────┘                   │    │
│   │                                                         │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
│   Data Sources:                    Outputs:                      │
│   • S3 buckets                    • EventBridge events          │
│   • S3 objects                    • Security Hub findings       │
│   • S3 access logs               • S3 (detailed results)        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Macie Components

#### 1. S3 Bucket Inventory

Macie automatically maintains an inventory of S3 buckets:
- Bucket count, size, object count
- Security settings (encryption, public access, permissions)
- Region and account information

#### 2. Sensitive Data Discovery Jobs

Configure jobs to scan S3 objects for sensitive data:
- Define scope (buckets, prefixes, tags)
- Set schedule (one-time or recurring)
- Choose managed or custom data identifiers

#### 3. Findings

Results from bucket analysis and data discovery:
- **Policy findings**: Security misconfigurations
- **Sensitive data findings**: Discovered sensitive information

---

## Sensitive Data Discovery

### What Macie Can Detect

```
┌─────────────────────────────────────────────────────────────────┐
│              Sensitive Data Types Detected by Macie              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Personal Data (PII):                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Names                    • Driver's license numbers   │  │
│   │  • Addresses                • Passport numbers           │  │
│   │  • Email addresses          • National ID numbers        │  │
│   │  • Phone numbers            • Date of birth              │  │
│   │  • Social Security numbers  • Biometric data             │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Financial Data:                                                │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Credit card numbers      • Bank account numbers       │  │
│   │  • Credit card CVV          • Bank routing numbers       │  │
│   │  • Credit card expiry       • Financial identifiers      │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Credentials & Secrets:                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • AWS secret keys          • API keys                   │  │
│   │  • Private keys (PEM, PGP)  • Database credentials       │  │
│   │  • SSH keys                 • OAuth tokens               │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Healthcare:                                                    │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Health insurance IDs     • Medical record numbers     │  │
│   │  • Drug Enforcement numbers • Healthcare provider IDs    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Managed Data Identifiers

Macie provides **100+ built-in data identifiers** for common sensitive data types:

| Category | Examples |
|----------|----------|
| **Financial** | Credit cards, bank accounts, tax IDs |
| **Personal** | SSN, passport, driver's license, DOB |
| **Healthcare** | HIPAA identifiers, DEA numbers |
| **Credentials** | AWS keys, API tokens, private keys |
| **Contact** | Email, phone, address |

### Custom Data Identifiers

Create your own identifiers using:
- **Regular expressions**: Pattern matching
- **Keywords**: Proximity-based detection
- **Maximum match distance**: Keywords within N characters

```
┌─────────────────────────────────────────────────────────────────┐
│              Custom Data Identifier Example                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Scenario: Detect internal employee IDs (format: EMP-123456)   │
│                                                                  │
│   Configuration:                                                 │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Name: Employee ID Detector                              │  │
│   │  Regex: EMP-[0-9]{6}                                     │  │
│   │  Keywords: employee, emp id, staff number                │  │
│   │  Maximum match distance: 50 characters                   │  │
│   │  Severity: HIGH                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Sample Match:                                                  │
│   "The employee ID is EMP-123456 for John Smith"                │
│          ↑ keyword          ↑ pattern match                     │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Allow Lists

Exclude specific patterns or text from findings:
- Reduce false positives
- Ignore known safe data
- Two types:
  - **Predefined text**: Exact strings to ignore
  - **Regular expression**: Patterns to ignore

---

## S3 Bucket Security

### Bucket Monitoring

Macie continuously monitors S3 buckets for security issues:

```
┌─────────────────────────────────────────────────────────────────┐
│              S3 Bucket Security Monitoring                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Security Checks:                                               │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   Public Access:                                         │  │
│   │   • Block public access settings                        │  │
│   │   • Bucket policies with public access                  │  │
│   │   • ACLs granting public access                         │  │
│   │                                                          │  │
│   │   Encryption:                                            │  │
│   │   • Server-side encryption status                       │  │
│   │   • Encryption type (SSE-S3, SSE-KMS, SSE-C)           │  │
│   │   • Default encryption configuration                    │  │
│   │                                                          │  │
│   │   Access Control:                                        │  │
│   │   • Shared access (other AWS accounts)                  │  │
│   │   • Cross-account access                                │  │
│   │   • Sensitive bucket policies                           │  │
│   │                                                          │  │
│   │   Replication:                                           │  │
│   │   • Replication configuration                           │  │
│   │   • Replication destination security                    │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Bucket Statistics Dashboard

Macie provides insights into your S3 environment:

| Metric | Description |
|--------|-------------|
| Total buckets | Number of monitored buckets |
| Total size | Aggregate storage used |
| Publicly accessible | Buckets with public access |
| Unencrypted | Buckets without encryption |
| Shared | Buckets shared with other accounts |
| Classifiable | Buckets that can be scanned |

---

## Findings and Alerts

### Types of Findings

```
┌─────────────────────────────────────────────────────────────────┐
│                    Macie Finding Types                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Policy Findings (Security Misconfigurations):                  │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   Policy:IAMUser/S3BlockPublicAccessDisabled            │  │
│   │   • Public access block disabled                         │  │
│   │                                                          │  │
│   │   Policy:IAMUser/S3BucketEncryptionDisabled             │  │
│   │   • Default encryption not enabled                       │  │
│   │                                                          │  │
│   │   Policy:IAMUser/S3BucketPublic                         │  │
│   │   • Bucket is publicly accessible                        │  │
│   │                                                          │  │
│   │   Policy:IAMUser/S3BucketSharedExternally               │  │
│   │   • Bucket shared with external accounts                │  │
│   │                                                          │  │
│   │   Policy:IAMUser/S3BucketReplicatedExternally           │  │
│   │   • Bucket replicating to external account              │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│   Sensitive Data Findings (Discovered Sensitive Data):           │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │                                                          │  │
│   │   SensitiveData:S3Object/Credentials                    │  │
│   │   • AWS credentials found in object                      │  │
│   │                                                          │  │
│   │   SensitiveData:S3Object/Financial                      │  │
│   │   • Credit card or financial data found                 │  │
│   │                                                          │  │
│   │   SensitiveData:S3Object/Personal                       │  │
│   │   • PII found (SSN, passport, etc.)                     │  │
│   │                                                          │  │
│   │   SensitiveData:S3Object/Multiple                       │  │
│   │   • Multiple sensitive data types found                 │  │
│   │                                                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Finding Severity

| Severity | Description | Example |
|----------|-------------|---------|
| **Critical** | Requires immediate attention | AWS credentials exposed publicly |
| **High** | Significant risk | PII in public bucket |
| **Medium** | Moderate risk | Unencrypted sensitive data |
| **Low** | Minor risk | Shared bucket without sensitive data |
| **Informational** | No immediate risk | Successfully classified data |

### Finding Structure

```json
{
    "schemaVersion": "1.0",
    "id": "finding-id",
    "accountId": "123456789012",
    "region": "us-east-1",
    "type": "SensitiveData:S3Object/Personal",
    "severity": {
        "score": 8,
        "description": "High"
    },
    "resourcesAffected": {
        "s3Bucket": {
            "name": "my-bucket",
            "publicAccess": {
                "effectivePermission": "NOT_PUBLIC"
            }
        },
        "s3Object": {
            "key": "data/customers.csv",
            "size": 1048576
        }
    },
    "classificationDetails": {
        "result": {
            "sensitiveData": [
                {
                    "category": "PERSONAL_INFORMATION",
                    "detections": [
                        {
                            "type": "USA_SOCIAL_SECURITY_NUMBER",
                            "count": 150
                        }
                    ]
                }
            ]
        }
    }
}
```

---

## Integration with Other Services

### EventBridge Integration

```
┌─────────────────────────────────────────────────────────────────┐
│              Macie + EventBridge Integration                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐    ┌──────────────┐    ┌────────────────┐   │
│   │    Macie     │    │ EventBridge  │    │    Targets     │   │
│   │   Finding    │───►│    Rule      │───►│                │   │
│   └──────────────┘    └──────────────┘    │  • Lambda      │   │
│                                           │  • SNS         │   │
│                                           │  • Step Func   │   │
│                                           │  • SQS         │   │
│                                           └────────────────┘   │
│                                                                  │
│   Example Event Pattern:                                         │
│   {                                                              │
│     "source": ["aws.macie"],                                    │
│     "detail-type": ["Macie Finding"],                           │
│     "detail": {                                                  │
│       "severity": {                                             │
│         "description": ["High", "Critical"]                     │
│       }                                                         │
│     }                                                           │
│   }                                                             │
│                                                                  │
│   Use Cases:                                                     │
│   • Send alerts to Slack/Teams                                  │
│   • Trigger Lambda for auto-remediation                         │
│   • Create tickets in JIRA/ServiceNow                          │
│   • Quarantine affected S3 objects                             │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Security Hub Integration

```
┌─────────────────────────────────────────────────────────────────┐
│              Macie + Security Hub Integration                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌──────────────┐                      ┌──────────────────┐   │
│   │    Macie     │                      │   Security Hub   │   │
│   │   Findings   │─────────────────────►│                  │   │
│   └──────────────┘                      │  • Aggregation   │   │
│                                         │  • Dashboard     │   │
│   ┌──────────────┐                      │  • Compliance    │   │
│   │  GuardDuty   │─────────────────────►│  • Insights      │   │
│   │   Findings   │                      │                  │   │
│   └──────────────┘                      └──────────────────┘   │
│                                                                  │
│   Benefits:                                                      │
│   • Centralized security view                                   │
│   • Correlate findings across services                         │
│   • Compliance reporting                                        │
│   • Single pane of glass for security                          │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Automated Remediation Example

```
┌─────────────────────────────────────────────────────────────────┐
│           Automated Remediation Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   1. Macie detects public bucket with PII                       │
│   ┌──────────────┐                                              │
│   │    Macie     │──► Finding: Public bucket with SSN data     │
│   └──────────────┘                                              │
│          │                                                       │
│          ▼                                                       │
│   2. EventBridge triggers Lambda                                │
│   ┌──────────────┐    ┌──────────────┐                         │
│   │ EventBridge  │───►│   Lambda     │                         │
│   └──────────────┘    └──────────────┘                         │
│                              │                                   │
│                              ▼                                   │
│   3. Lambda remediates                                          │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  • Block public access                                   │  │
│   │  • Enable encryption                                     │  │
│   │  • Move sensitive objects to secure bucket              │  │
│   │  • Send notification to security team                   │  │
│   └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│   4. Notify team                                                │
│   ┌──────────────┐    ┌──────────────┐                         │
│   │     SNS      │───►│   Security   │                         │
│   │              │    │    Team      │                         │
│   └──────────────┘    └──────────────┘                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-Account Management

### AWS Organizations Integration

```
┌─────────────────────────────────────────────────────────────────┐
│              Macie Multi-Account Setup                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌────────────────────────────────────────────────────────┐    │
│   │              AWS Organizations                          │    │
│   │                                                         │    │
│   │   ┌──────────────────────────────────────────────────┐ │    │
│   │   │            Macie Administrator                    │ │    │
│   │   │            (Delegated Admin Account)              │ │    │
│   │   │                                                   │ │    │
│   │   │   • Manages Macie for all member accounts        │ │    │
│   │   │   • Views findings from all accounts             │ │    │
│   │   │   • Creates organization-wide discovery jobs     │ │    │
│   │   │   • Configures settings centrally                │ │    │
│   │   └──────────────────────────────────────────────────┘ │    │
│   │                          │                              │    │
│   │        ┌─────────────────┼─────────────────┐           │    │
│   │        │                 │                 │           │    │
│   │        ▼                 ▼                 ▼           │    │
│   │   ┌─────────┐      ┌─────────┐      ┌─────────┐       │    │
│   │   │ Member  │      │ Member  │      │ Member  │       │    │
│   │   │Account 1│      │Account 2│      │Account 3│       │    │
│   │   │         │      │         │      │         │       │    │
│   │   │ S3 Data │      │ S3 Data │      │ S3 Data │       │    │
│   │   └─────────┘      └─────────┘      └─────────┘       │    │
│   │                                                         │    │
│   └────────────────────────────────────────────────────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Administrator Account Capabilities

| Capability | Description |
|------------|-------------|
| **View findings** | See findings from all member accounts |
| **Run discovery jobs** | Create jobs across member accounts |
| **Manage settings** | Configure Macie for organization |
| **Add/remove members** | Control which accounts are monitored |
| **Export findings** | Centralize findings export |

---

## Security and Compliance

### Compliance Support

Macie helps with compliance for:

| Regulation | How Macie Helps |
|------------|-----------------|
| **GDPR** | Discover PII, track data locations |
| **HIPAA** | Find PHI, monitor healthcare data |
| **PCI-DSS** | Detect credit card data |
| **CCPA** | Identify California resident data |
| **SOC 2** | Data classification, access monitoring |

### Data Classification Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│              Data Classification for Compliance                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Step 1: Discovery                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Macie scans S3 buckets and identifies sensitive data    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 2: Classification                                         │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Data categorized by type:                               │  │
│   │  • PII (GDPR, CCPA)                                     │  │
│   │  • PHI (HIPAA)                                          │  │
│   │  • Financial (PCI-DSS)                                  │  │
│   │  • Credentials (security risk)                          │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 3: Reporting                                              │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Generate findings and reports for:                      │  │
│   │  • Compliance audits                                     │  │
│   │  • Risk assessment                                       │  │
│   │  • Data inventory                                        │  │
│   └──────────────────────────────────────────────────────────┘  │
│                            ↓                                     │
│   Step 4: Remediation                                            │
│   ┌──────────────────────────────────────────────────────────┐  │
│   │  Take action based on findings:                          │  │
│   │  • Encrypt unprotected data                             │  │
│   │  • Restrict access to sensitive buckets                 │  │
│   │  • Remove/redact exposed credentials                    │  │
│   └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Pricing and Cost Optimization

### Pricing Model

| Component | Price |
|-----------|-------|
| **Bucket evaluation** | Free (first 30 days), then $0.10 per bucket/month |
| **Sensitive data discovery** | $1.00 per GB for first 50 TB/month |
|  | $0.50 per GB for next 450 TB/month |
|  | $0.25 per GB for over 500 TB/month |

### Cost Optimization Strategies

1. **Scope discovery jobs carefully**
   - Scan only necessary buckets/prefixes
   - Use tags to target specific data

2. **Schedule strategically**
   - Scan new/modified data incrementally
   - Avoid full scans unless necessary

3. **Use sampling for large datasets**
   - Sample data to estimate sensitive data presence
   - Full scan only where needed

4. **Leverage findings**
   - Use findings to prioritize remediation
   - Reduce repeat scans of known clean data

### Cost Estimation Example

```
┌─────────────────────────────────────────────────────────────────┐
│                    Cost Estimation Example                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Scenario: 100 buckets, 10 TB of data to scan monthly          │
│                                                                  │
│   Bucket Evaluation:                                             │
│   100 buckets × $0.10 = $10.00/month                            │
│                                                                  │
│   Sensitive Data Discovery:                                      │
│   10 TB × $1.00/GB = 10,000 GB × $1.00 = $10,000/month         │
│                                                                  │
│   Total: $10,010/month                                          │
│                                                                  │
│   Cost Optimization:                                             │
│   • Scan only 1 TB (high-risk data): $1,010/month              │
│   • Use incremental scans: ~$500/month                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Best Practices

### Discovery Job Configuration

1. **Start with high-risk data**: Prioritize buckets likely to contain sensitive data
2. **Use incremental scans**: Scan new/modified objects, not entire buckets
3. **Apply filters**: Use prefixes, tags, and file extensions to narrow scope
4. **Schedule appropriately**: Daily for active data, weekly for archives

### Finding Management

1. **Review findings promptly**: Address high-severity findings first
2. **Use suppression rules**: Reduce noise from known acceptable patterns
3. **Integrate with workflows**: Connect to ticketing systems for tracking
4. **Automate remediation**: Use EventBridge + Lambda for common issues

### Organization-Wide Deployment

1. **Use delegated administrator**: Centralize management in security account
2. **Enable for all accounts**: Ensure comprehensive coverage
3. **Standardize configurations**: Use consistent custom identifiers
4. **Centralize findings**: Export to central S3 bucket for analysis

---

## AWS CLI Commands Reference

### Enable and Configure Macie

#### Enable Macie

```bash
# Enable Macie in current region
aws macie2 enable-macie \
  --status ENABLED \
  --finding-publishing-frequency FIFTEEN_MINUTES

# Available publishing frequencies:
# - FIFTEEN_MINUTES
# - ONE_HOUR  
# - SIX_HOURS

# Check Macie status
aws macie2 get-macie-session

# Update Macie configuration
aws macie2 update-macie-session \
  --status ENABLED \
  --finding-publishing-frequency ONE_HOUR

# Disable Macie (this deletes all Macie resources)
aws macie2 disable-macie
```

### Classification Jobs

#### Create Classification Jobs

```bash
# Create a one-time classification job for specific S3 buckets
aws macie2 create-classification-job \
  --job-type ONE_TIME \
  --name "PII-Discovery-Job-$(date +%Y%m%d)" \
  --description "Scan production buckets for PII" \
  --s3-job-definition '{
    "bucketDefinitions": [
      {
        "accountId": "123456789012",
        "buckets": ["my-production-bucket", "user-data-bucket"]
      }
    ],
    "scoping": {
      "includes": {
        "and": [
          {
            "simpleScopeTerm": {
              "key": "OBJECT_EXTENSION",
              "comparator": "EQ",
              "values": ["csv", "json", "txt"]
            }
          }
        ]
      }
    }
  }' \
  --managed-data-identifier-ids \
    CREDIT_CARD_NUMBER \
    US_SOCIAL_SECURITY_NUMBER \
    EMAIL_ADDRESS

# Create scheduled classification job (daily)
aws macie2 create-classification-job \
  --job-type SCHEDULED \
  --name "Daily-Sensitive-Data-Scan" \
  --schedule-frequency '{
    "dailySchedule": {}
  }' \
  --s3-job-definition '{
    "bucketDefinitions": [
      {
        "accountId": "123456789012",
        "buckets": ["data-lake-bucket"]
      }
    ]
  }'

# Create job with custom data identifiers
CUSTOM_IDENTIFIER_ID="custom-12345678-1234-1234-1234-123456789012"

aws macie2 create-classification-job \
  --job-type ONE_TIME \
  --name "Custom-Pattern-Scan" \
  --s3-job-definition '{
    "bucketDefinitions": [
      {
        "accountId": "123456789012",
        "buckets": ["logs-bucket"]
      }
    ]
  }' \
  --custom-data-identifier-ids $CUSTOM_IDENTIFIER_ID

# List all classification jobs
aws macie2 list-classification-jobs \
  --filter-criteria '{
    "includes": [
      {
        "key": "jobStatus",
        "values": ["RUNNING", "PAUSED"]
      }
    ]
  }'

# Describe a specific job
JOB_ID="job-12345678-1234-1234-1234-123456789012"
aws macie2 describe-classification-job \
  --job-id $JOB_ID

# Get job statistics
aws macie2 get-classification-job-statistics \
  --job-id $JOB_ID
```

#### Manage Classification Jobs

```bash
# Pause a classification job
aws macie2 update-classification-job \
  --job-id $JOB_ID \
  --job-status PAUSED

# Resume a paused job
aws macie2 update-classification-job \
  --job-id $JOB_ID \
  --job-status RUNNING

# Cancel a job
aws macie2 update-classification-job \
  --job-id $JOB_ID \
  --job-status CANCELLED

# Delete a job and its findings
aws macie2 delete-classification-job \
  --job-id $JOB_ID
```

### Findings Management

#### List Findings

```bash
# List all findings
aws macie2 list-findings

# List findings with filters
aws macie2 list-findings \
  --finding-criteria '{
    "criterion": {
      "severity.description": {
        "eq": ["High"]
      },
      "type": {
        "eq": ["SensitiveData:S3Object/Personal"]
      }
    }
  }'

# List findings from last 24 hours
aws macie2 list-findings \
  --finding-criteria '{
    "criterion": {
      "createdAt": {
        "gte": '$(date -u -d '24 hours ago' '+%Y-%m-%dT%H:%M:%SZ')'
      }
    }
  }'

# List findings for specific bucket
aws macie2 list-findings \
  --finding-criteria '{
    "criterion": {
      "resourcesAffected.s3Bucket.name": {
        "eq": ["my-sensitive-data-bucket"]
      }
    }
  }'

# Sort findings by severity
aws macie2 list-findings \
  --sort-criteria '{
    "attributeName": "severity.score",
    "orderBy": "DESC"
  }' \
  --max-results 50
```

#### Get Finding Details

```bash
# Get details for specific findings
FINDING_ID="finding-12345678901234567890123456789012"

aws macie2 get-findings \
  --finding-ids $FINDING_ID

# Get multiple findings
aws macie2 get-findings \
  --finding-ids \
    "finding-12345678901234567890123456789012" \
    "finding-98765432109876543210987654321098"

# Get findings and extract specific fields
aws macie2 get-findings \
  --finding-ids $FINDING_ID \
  --query 'findings[*].[id,type,severity.description,resourcesAffected.s3Object.key]' \
  --output table
```

#### Update Finding Status

```bash
# Archive a finding
aws macie2 update-findings \
  --finding-ids $FINDING_ID \
  --status ARCHIVED

# Archive with comment
aws macie2 update-findings \
  --finding-ids $FINDING_ID \
  --status ARCHIVED \
  --comment "False positive - test data"

# Unarchive a finding
aws macie2 update-findings \
  --finding-ids $FINDING_ID \
  --status UNARCHIVED
```

### Custom Data Identifiers

```bash
# Create custom data identifier with regex
aws macie2 create-custom-data-identifier \
  --name "Employee-ID-Pattern" \
  --description "Detects company employee IDs" \
  --regex "EMP-[0-9]{6}" \
  --maximum-match-distance 50 \
  --keywords "employee" "personnel" "staff"

# Create custom identifier with ignore words
aws macie2 create-custom-data-identifier \
  --name "API-Key-Pattern" \
  --description "Detects API keys" \
  --regex "[A-Z0-9]{32}" \
  --keywords "api_key" "apikey" "key" \
  --ignore-words "example" "sample" "test"

# List all custom data identifiers
aws macie2 list-custom-data-identifiers

# Get custom identifier details
CUSTOM_ID="custom-12345678-1234-1234-1234-123456789012"
aws macie2 get-custom-data-identifier \
  --id $CUSTOM_ID

# Update custom data identifier
aws macie2 update-custom-data-identifier \
  --id $CUSTOM_ID \
  --description "Updated description" \
  --name "Employee-ID-Pattern-v2"

# Delete custom data identifier
aws macie2 delete-custom-data-identifier \
  --id $CUSTOM_ID

# Test custom data identifier
aws macie2 test-custom-data-identifier \
  --regex "EMP-[0-9]{6}" \
  --sample-text "Employee ID: EMP-123456. Contact: john@example.com"
```

### Allow Lists

```bash
# Create S3-based allow list
aws macie2 create-allow-list \
  --name "Known-Test-Data" \
  --description "Test data to exclude from findings" \
  --criteria '{
    "s3WordsList": {
      "bucketName": "macie-allow-lists",
      "objectKey": "test-data-patterns.txt"
    }
  }'

# Create regex-based allow list
aws macie2 create-allow-list \
  --name "Test-Accounts-Regex" \
  --description "Exclude test account numbers" \
  --criteria '{
    "regex": "(000-00-0000|111-11-1111|123-45-6789)"
  }'

# List all allow lists
aws macie2 list-allow-lists

# Get allow list details
ALLOW_LIST_ID="allowlist-12345678-1234-1234-1234-123456789012"
aws macie2 get-allow-list \
  --id $ALLOW_LIST_ID

# Update allow list
aws macie2 update-allow-list \
  --id $ALLOW_LIST_ID \
  --description "Updated allow list description"

# Delete allow list
aws macie2 delete-allow-list \
  --id $ALLOW_LIST_ID
```

### Sensitive Data Discovery

```bash
# Get sensitive data discovery configuration
aws macie2 get-automated-discovery-configuration

# Enable automated sensitive data discovery
aws macie2 update-automated-discovery-configuration \
  --status ENABLED

# Disable automated discovery
aws macie2 update-automated-discovery-configuration \
  --status DISABLED

# List managed data identifiers
aws macie2 list-managed-data-identifiers

# Get usage statistics for sensitive data discovery
aws macie2 get-usage-statistics \
  --time-range '{
    "key": "PAST_30_DAYS"
  }' \
  --filter-by '[
    {
      "key": "accountId",
      "values": ["123456789012"]
    }
  ]'

# Get sensitive data occurrences
aws macie2 get-sensitive-data-occurrences \
  --finding-id $FINDING_ID

# Retrieve sample occurrences from findings
aws macie2 get-sensitive-data-occurrences-availability \
  --finding-id $FINDING_ID
```

### S3 Bucket Configuration

```bash
# List S3 buckets tracked by Macie
aws macie2 describe-buckets

# Get specific bucket details
aws macie2 describe-buckets \
  --criteria '{
    "bucketName": {
      "eq": ["my-sensitive-bucket"]
    }
  }'

# Update bucket classification scope
aws macie2 update-classification-scope \
  --id "bucket-scope-123" \
  --s3 '{
    "excludes": {
      "bucketNames": ["logs-bucket", "temp-bucket"]
    }
  }'

# Get bucket statistics
aws macie2 get-bucket-statistics \
  --account-id 123456789012

# Update S3 resource classification
aws macie2 update-resource-profile \
  --resource-arn "arn:aws:s3:::my-bucket" \
  --sensitivity-score-override 75

# Detach S3 resources from Macie
aws macie2 update-resource-profile-detections \
  --resource-arn "arn:aws:s3:::my-bucket" \
  --suppress-data-identifiers \
    custom-12345678-1234-1234-1234-123456789012
```

### Member Account Management

```bash
# Create Macie member accounts (run from administrator account)
aws macie2 create-member \
  --account '{
    "accountId": "123456789012",
    "email": "member@example.com"
  }'

# Invite member account
aws macie2 create-invitations \
  --account-ids 123456789012 234567890123 \
  --disable-email-notification

# List member accounts
aws macie2 list-members

# Get member account details
aws macie2 get-member \
  --id 123456789012

# Accept invitation (run from member account)
aws macie2 accept-invitation \
  --administrator-account-id 111111111111 \
  --invitation-id inv-12345678901234567890

# Decline invitation (run from member account)
aws macie2 decline-invitations \
  --account-ids 111111111111

# Disassociate from administrator (run from member account)
aws macie2 disassociate-from-administrator-account

# Disassociate member (run from administrator account)
aws macie2 disassociate-member \
  --id 123456789012

# Delete member
aws macie2 delete-member \
  --id 123456789012

# List invitations received
aws macie2 list-invitations

# Get administrator account info (run from member)
aws macie2 get-administrator-account
```

### Organization Delegated Administrator

```bash
# Enable Macie delegated administrator (run from management account)
aws macie2 enable-organization-admin-account \
  --admin-account-id 123456789012

# List delegated administrators
aws macie2 list-organization-admin-accounts

# Disable delegated administrator
aws macie2 disable-organization-admin-account \
  --admin-account-id 123456789012
```

### Finding Filters

```bash
# Create finding filter to auto-archive findings
aws macie2 create-findings-filter \
  --name "Auto-Archive-Test-Findings" \
  --description "Automatically archive findings in test buckets" \
  --action ARCHIVE \
  --finding-criteria '{
    "criterion": {
      "resourcesAffected.s3Bucket.name": {
        "eq": ["test-bucket", "dev-bucket"]
      }
    }
  }'

# Create filter for high severity findings
aws macie2 create-findings-filter \
  --name "High-Severity-Alert" \
  --description "Tag high severity findings" \
  --action NOOP \
  --finding-criteria '{
    "criterion": {
      "severity.description": {
        "eq": ["High"]
      }
    }
  }'

# List finding filters
aws macie2 list-findings-filters

# Get finding filter details
FILTER_ID="filter-12345678-1234-1234-1234-123456789012"
aws macie2 get-findings-filter \
  --id $FILTER_ID

# Update finding filter
aws macie2 update-findings-filter \
  --id $FILTER_ID \
  --action ARCHIVE \
  --description "Updated filter description"

# Delete finding filter
aws macie2 delete-findings-filter \
  --id $FILTER_ID
```

### Export and Reporting

```bash
# Configure finding publication to S3
aws macie2 put-findings-publication-configuration \
  --destination-configuration '{
    "s3Destination": {
      "bucketName": "macie-findings-export",
      "keyPrefix": "findings/",
      "kmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
    }
  }'

# Get finding publication configuration
aws macie2 get-findings-publication-configuration

# Get finding statistics
aws macie2 get-finding-statistics \
  --group-by "type" \
  --finding-criteria '{
    "criterion": {
      "createdAt": {
        "gte": "2024-01-01T00:00:00Z"
      }
    }
  }'

# Get finding statistics by severity
aws macie2 get-finding-statistics \
  --group-by "severity.description"
```

### Practical Automation Scripts

#### Comprehensive Findings Report

```bash
#!/bin/bash
# Generate comprehensive Macie findings report

REPORT_FILE="macie-findings-report-$(date +%Y%m%d).json"

echo "Generating Macie findings report..."

# Get all findings
FINDINGS=$(aws macie2 list-findings --max-results 1000 --output json)
FINDING_IDS=$(echo $FINDINGS | jq -r '.findingIds[]')

if [ -z "$FINDING_IDS" ]; then
  echo "No findings found"
  exit 0
fi

# Get detailed findings
IDS_ARRAY=$(echo $FINDING_IDS | jq -R 'split(" ")' | jq -c '.')
aws macie2 get-findings --finding-ids $(echo $FINDING_IDS | tr '\n' ' ') > $REPORT_FILE

echo "Report generated: $REPORT_FILE"

# Generate summary
echo "\nFindings Summary:"
jq -r '.findings | group_by(.severity.description) | .[] | "\(.[] |.severity.description): \(length)"' $REPORT_FILE | sort | uniq
```

#### Auto-Remediation Script

```bash
#!/bin/bash
# Automatically remediate public S3 buckets found by Macie

echo "Checking for public bucket findings..."

# Find policy findings for public buckets
FINDINGS=$(aws macie2 list-findings \
  --finding-criteria '{
    "criterion": {
      "category": {"eq": ["POLICY"]},
      "type": {"eq": ["Policy:IAMUser/S3BucketPublic"]}
    }
  }' --query 'findingIds' --output text)

if [ -z "$FINDINGS" ]; then
  echo "No public bucket findings"
  exit 0
fi

# Process each finding
for FINDING_ID in $FINDINGS; do
  echo "Processing finding: $FINDING_ID"
  
  # Get bucket name from finding
  BUCKET=$(aws macie2 get-findings \
    --finding-ids $FINDING_ID \
    --query 'findings[0].resourcesAffected.s3Bucket.name' \
    --output text)
  
  echo "Remediating bucket: $BUCKET"
  
  # Block public access
  aws s3api put-public-access-block \
    --bucket $BUCKET \
    --public-access-block-configuration \
      "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"
  
  if [ $? -eq 0 ]; then
    echo "✅ Remediated: $BUCKET"
    
    # Archive the finding
    aws macie2 update-findings \
      --finding-ids $FINDING_ID \
      --status ARCHIVED \
      --comment "Auto-remediated: Public access blocked"
  else
    echo "❌ Failed to remediate: $BUCKET"
  fi
done
```

#### Multi-Region Macie Setup

```bash
#!/bin/bash
# Enable Macie across all regions

REGIONS=("us-east-1" "us-west-2" "eu-west-1" "ap-southeast-1")

for REGION in "${REGIONS[@]}"; do
  echo "Enabling Macie in $REGION..."
  
  aws macie2 enable-macie \
    --region $REGION \
    --status ENABLED \
    --finding-publishing-frequency FIFTEEN_MINUTES
  
  if [ $? -eq 0 ]; then
    echo "✅ Enabled in $REGION"
  else
    echo "❌ Failed in $REGION"
  fi
done
```

---

## SAA-C03 Exam Tips

### Key Concepts

1. **Macie = S3 data security** and sensitive data discovery
2. **Machine learning + pattern matching** for data identification
3. **Automatic PII detection** (SSN, credit cards, etc.)
4. **S3 bucket security assessment**
5. **Integration with EventBridge, Security Hub**

### Common Exam Scenarios

#### Scenario 1: Find PII in S3
**Question**: Need to automatically discover PII stored in S3 buckets.
**Answer**: Amazon Macie

#### Scenario 2: GDPR Compliance
**Question**: Identify personal data for GDPR compliance.
**Answer**: Amazon Macie sensitive data discovery

#### Scenario 3: Alert on Public Buckets
**Question**: Get notified when S3 buckets become public and contain sensitive data.
**Answer**: Macie + EventBridge for notifications

#### Scenario 4: Multi-Account Data Security
**Question**: Centrally monitor sensitive data across AWS accounts.
**Answer**: Macie with AWS Organizations integration

### Exam Question Keywords

| Keyword | Usually Points To |
|---------|------------------|
| "Discover PII in S3" | Macie |
| "Sensitive data in S3" | Macie |
| "Data privacy" | Macie |
| "S3 data classification" | Macie |
| "GDPR/HIPAA data discovery" | Macie |
| "Find credit card numbers in S3" | Macie |
| "S3 security posture" | Macie |

### Macie vs Other Security Services

```
┌─────────────────────────────────────────────────────────────────┐
│              Security Service Comparison                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   Macie vs GuardDuty:                                           │
│   • Macie: S3 data content, sensitive data discovery            │
│   • GuardDuty: Threat detection, suspicious activity            │
│                                                                  │
│   Macie vs Inspector:                                           │
│   • Macie: Data security in S3                                  │
│   • Inspector: EC2/container vulnerability scanning             │
│                                                                  │
│   Macie vs Security Hub:                                        │
│   • Macie: Generates findings about S3 data                     │
│   • Security Hub: Aggregates findings from multiple services    │
│                                                                  │
│   Macie vs Config:                                              │
│   • Macie: S3 data classification                               │
│   • Config: Resource configuration compliance                    │
│                                                                  │
│   Decision Matrix:                                               │
│   • "Find sensitive data" → Macie                               │
│   • "Detect threats" → GuardDuty                                │
│   • "Scan for vulnerabilities" → Inspector                      │
│   • "Aggregate findings" → Security Hub                         │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Practice Questions

### Question 1
A company needs to automatically identify all S3 buckets containing credit card numbers for PCI-DSS compliance. What service should they use?

A) AWS Config  
B) Amazon GuardDuty  
C) Amazon Macie  
D) Amazon Inspector  

**Answer: C** - Macie is specifically designed to discover sensitive data like credit card numbers in S3.

### Question 2
An organization wants to receive immediate alerts when Macie discovers sensitive data in public S3 buckets. What integration should they use?

A) AWS CloudTrail  
B) Amazon EventBridge  
C) AWS Config  
D) Amazon CloudWatch Logs  

**Answer: B** - EventBridge receives Macie findings and can trigger alerts, Lambda functions, or other actions.

### Question 3
A security team needs to discover sensitive data across 50 AWS accounts. What's the BEST approach?

A) Enable Macie separately in each account  
B) Use Macie with AWS Organizations delegated administrator  
C) Create cross-account IAM roles  
D) Use AWS Config aggregator  

**Answer: B** - Using delegated administrator with AWS Organizations provides centralized management and visibility.

### Question 4
Which type of sensitive data can Amazon Macie automatically detect? (Select THREE)

A) Social Security numbers  
B) EC2 security group misconfigurations  
C) AWS access keys  
D) Credit card numbers  
E) Lambda function vulnerabilities  

**Answer: A, C, D** - Macie detects sensitive data in S3 including SSN, credentials (access keys), and financial data (credit cards). EC2 and Lambda issues are handled by other services.

### Question 5
A company wants to detect custom employee ID numbers (format: EMP-XXXXXX) in their S3 data. What Macie feature should they use?

A) Managed data identifiers  
B) Custom data identifiers  
C) Allow lists  
D) Suppression rules  

**Answer: B** - Custom data identifiers allow you to define regex patterns for organization-specific sensitive data.

---

## Summary

Amazon Macie is a data security service focused on S3:

**Key Points**:
- **Purpose**: Discover and protect sensitive data in S3
- **Methods**: ML + pattern matching
- **Data types**: PII, financial, credentials, healthcare
- **Outputs**: Findings, EventBridge events, Security Hub integration

**Core Features**:
1. Sensitive data discovery (automated)
2. S3 bucket security assessment
3. Custom data identifiers
4. Multi-account management

**SAA-C03 Focus**:
- Macie = S3 sensitive data discovery
- Use for GDPR, HIPAA, PCI-DSS compliance
- Integrates with EventBridge for automation
- Different from GuardDuty (threats) and Inspector (vulnerabilities)
