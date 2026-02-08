# AWS Identity and Access Management (IAM) - SAA-C03 Guide

## Table of Contents
1. [Introduction to AWS IAM](#introduction-to-aws-iam)
2. [IAM Fundamentals](#iam-fundamentals)
3. [Users, Groups, and Roles](#users-groups-and-roles)
4. [IAM Policies](#iam-policies)
5. [Security Features](#security-features)
6. [Advanced IAM Concepts](#advanced-iam-concepts)
7. [Best Practices](#best-practices)
8. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
9. [Common Scenarios and Use Cases](#common-scenarios-and-use-cases)
10. [Practice Questions](#practice-questions)
11. [AWS CLI Commands Reference](#aws-cli-commands-reference)

---

## Introduction to AWS IAM

AWS Identity and Access Management (IAM) is a web service that enables you to securely control access to AWS services and resources. IAM allows you to create and manage AWS users, groups, and permissions to allow and deny their access to AWS resources.

### Key Benefits
- **Fine-grained access control**: Control who can access what resources and when
- **Secure by default**: No permissions granted by default
- **Integration**: Works with all AWS services
- **Free to use**: No additional charges for IAM
- **Global service**: IAM is global across all AWS regions

### Core Purpose
IAM answers three fundamental questions:
1. **Who** can access resources (Authentication)
2. **What** they can access (Authorization) 
3. **When** they can access it (Conditions)

---

## IAM Fundamentals

### Authentication vs Authorization

**Authentication** (AuthN): *Who are you?*
- Process of verifying identity
- Methods: Username/password, access keys, temporary credentials, federated identity

**Authorization** (AuthZ): *What are you allowed to do?*
- Process of granting or denying permissions
- Controlled through IAM policies
- Principle of least privilege

### IAM Principals

A principal is an entity that can make requests to AWS resources:

1. **Root User**
   - Complete access to all AWS resources
   - Created when AWS account is first opened
   - Should only be used for initial setup and billing
   - Cannot be restricted by IAM policies

2. **IAM Users**
   - Individual people or applications
   - Long-term credentials (password, access keys)
   - Can be assigned policies directly or through groups

3. **IAM Roles**
   - Temporary credentials for AWS resources, applications, or users
   - No permanent credentials
   - Assumed by trusted entities

4. **AWS Services**
   - EC2 instances, Lambda functions, etc.
   - Use roles for permissions

### IAM Components Architecture

```
AWS Account (Root)
├── IAM Users
│   ├── Policies (attached directly)
│   └── Groups (inherit group policies)
├── IAM Groups
│   └── Policies (attached to group)
├── IAM Roles
│   ├── Trust Policy (who can assume)
│   └── Permissions Policy (what they can do)
└── IAM Policies
    ├── Managed Policies (AWS/Customer)
    └── Inline Policies
```

### Key Concepts

- **Identity**: Users, groups, or roles
- **Resource**: AWS services and objects (S3 buckets, EC2 instances, etc.)
- **Action**: Operations that can be performed (s3:GetObject, ec2:StartInstance)
- **Condition**: Circumstances under which policies apply
- **Effect**: Allow or Deny

---

## Users, Groups, and Roles

### IAM Users

IAM users represent individual people or applications that interact with AWS.

#### User Characteristics
- **Permanent Identity**: Long-term credentials
- **Direct Policy Assignment**: Policies can be attached directly
- **Group Membership**: Can belong to multiple groups
- **Access Methods**: Console access, programmatic access, or both
- **Credential Types**: Password, access keys, MFA devices

#### User Limits
- 5,000 users per AWS account
- 10 groups per user
- 10 managed policies per user
- 2 access keys per user

#### Best Practices for Users
- Create individual users (no shared accounts)
- Use groups for permission management
- Enable MFA for console users
- Rotate access keys regularly
- Follow naming conventions

### IAM Groups

Groups are collections of users that make permission management easier.

#### Group Characteristics
- **No Identity**: Groups cannot be identified in resource policies
- **Policy Inheritance**: Users inherit permissions from group policies
- **No Nesting**: Groups cannot contain other groups
- **No Default Group**: No automatic group membership

#### Group Strategy
```
Example Organization Structure:
├── Administrators (Full access)
├── Developers (Dev environment access)
├── QA-Team (Test environment access)
├── ReadOnly-Users (Read-only access)
└── DatabaseAdmins (Database management)
```

#### Group Limits
- 300 groups per AWS account
- 100 users per group
- 10 managed policies per group

### IAM Roles

Roles provide temporary access without long-term credentials.

#### Role Types

1. **AWS Service Roles**
   - Used by AWS services (EC2, Lambda, etc.)
   - Service assumes the role to perform actions
   ```json
   Trust Policy Example (EC2):
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "Service": "ec2.amazonaws.com"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

2. **Cross-Account Roles**
   - Allow access from different AWS accounts
   - Enables resource sharing between organizations
   ```json
   Trust Policy Example (Cross-Account):
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Principal": {
           "AWS": "arn:aws:iam::123456789012:root"
         },
         "Action": "sts:AssumeRole"
       }
     ]
   }
   ```

3. **Identity Provider Roles**
   - For federated users from external identity providers
   - SAML, OIDC, or Web Identity Federation

4. **AWS Service-Linked Roles**
   - Predefined by AWS services
   - Cannot be modified
   - Automatically created/deleted by services

#### Role Components

**Trust Policy (Who can assume the role)**
- Defines which principals can assume the role
- Required for all roles
- Controls the "who" aspect

**Permissions Policy (What the role can do)**
- Defines what actions the role can perform
- Attached as managed or inline policies
- Controls the "what" aspect

#### Role Session Duration
- Default: 1 hour
- Maximum: 12 hours (for roles assumed by users)
- Maximum: 6 hours (for federated users)
- Can be configured per role

#### Role Use Cases

| Use Case | Role Type | Example |
|----------|-----------|---------|
| EC2 accessing S3 | Service Role | EC2 instance reads from S3 bucket |
| Lambda function | Service Role | Lambda accesses DynamoDB |
| Cross-account access | Cross-Account Role | Dev account accesses prod resources |
| Temporary access | Assumed Role | Contractor needs temporary permissions |
| External users | Identity Provider Role | Corporate SSO integration |

### Comparison: Users vs Groups vs Roles

| Aspect | Users | Groups | Roles |
|--------|--------|--------|--------|
| Identity | Yes | No | Yes (when assumed) |
| Permanent Credentials | Yes | No | No |
| Policy Attachment | Direct | Direct | Direct |
| Use Case | Individual access | Permission grouping | Temporary/Service access |
| Cross-Account | Limited | No | Yes |
| AWS Service Use | Limited | No | Yes |

---

## IAM Policies

IAM policies are JSON documents that define permissions. They determine what actions are allowed or denied on which resources and under what conditions.

### Policy Types

#### 1. AWS Managed Policies
- Created and maintained by AWS
- Automatically updated by AWS
- Cannot be modified
- Versioned and rollback capable
- Examples: `AmazonS3ReadOnlyAccess`, `PowerUserAccess`

#### 2. Customer Managed Policies
- Created and maintained by customers
- Full control over policy content
- Versioned (up to 5 versions)
- Can be attached to multiple entities
- Reusable across users, groups, and roles

#### 3. Inline Policies
- Embedded directly in a single user, group, or role
- One-to-one relationship with identity
- Deleted when the identity is deleted
- Use for unique, one-off permissions

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Id": "PolicyId",
  "Statement": [
    {
      "Sid": "StatementId",
      "Effect": "Allow",
      "Principal": "arn:aws:iam::account:user/username",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-server-side-encryption": "aws:kms"
        }
      }
    }
  ]
}
```

#### Policy Elements

| Element | Required | Description | Example |
|---------|----------|-------------|---------|
| Version | Yes | Policy language version | "2012-10-17" |
| Statement | Yes | Array of permission statements | [...] |
| Sid | No | Statement identifier | "AllowS3Access" |
| Effect | Yes | Allow or Deny | "Allow" |
| Principal | Sometimes | Who the policy applies to | "arn:aws:iam::123456789012:user/Bob" |
| Action | Yes | What actions are allowed/denied | "s3:GetObject" |
| Resource | Yes | Which resources | "arn:aws:s3:::my-bucket/*" |
| Condition | No | When the policy applies | IP restrictions, time-based |

### Policy Evaluation Logic

AWS uses the following evaluation flow:

```
1. By default, all requests are DENIED
2. Look for explicit DENY → If found, DENY (cannot be overridden)
3. Look for explicit ALLOW → If found, ALLOW
4. If no explicit ALLOW found → DENY
```

#### Policy Evaluation Order
1. **Explicit Deny**: Always wins
2. **Organizations SCPs**: Service Control Policies
3. **Resource-based policies**: S3 bucket policies, etc.
4. **Identity-based policies**: User/group/role policies
5. **IAM permissions boundaries**: Maximum permissions
6. **Session policies**: For assumed roles

### Common Policy Patterns

#### 1. Full Service Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*"
    }
  ]
}
```

#### 2. Read-Only Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:Get*",
        "s3:List*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 3. Specific Resource Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ]
    }
  ]
}
```

#### 4. Conditional Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:*",
      "Resource": "*",
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "203.0.113.0/24"
        }
      }
    }
  ]
}
```

### Policy Conditions

Conditions provide fine-grained control over when policies apply.

#### Common Condition Operators

| Operator | Description | Example |
|----------|-------------|---------|
| StringEquals | Exact string match | "aws:username": "john" |
| StringLike | Wildcard matching | "s3:prefix": "home/*" |
| IpAddress | IP address/CIDR | "aws:SourceIp": "203.0.113.0/24" |
| DateGreaterThan | Time-based | "aws:CurrentTime": "2023-01-01T00:00:00Z" |
| Bool | Boolean conditions | "aws:SecureTransport": "true" |
| NumericLessThan | Numeric comparison | "s3:max-keys": "10" |

#### Condition Examples

**Time-based access:**
```json
"Condition": {
  "DateGreaterThan": {
    "aws:CurrentTime": "2023-01-01T00:00:00Z"
  },
  "DateLessThan": {
    "aws:CurrentTime": "2023-12-31T23:59:59Z"
  }
}
```

**IP-based access:**
```json
"Condition": {
  "IpAddress": {
    "aws:SourceIp": ["203.0.113.0/24", "198.51.100.0/24"]
  }
}
```

**MFA requirement:**
```json
"Condition": {
  "Bool": {
    "aws:MultiFactorAuthPresent": "true"
  },
  "NumericLessThan": {
    "aws:MultiFactorAuthAge": "3600"
  }
}
```

### Policy Boundaries

Permission boundaries set the maximum permissions an entity can have.

#### Use Cases
- Delegated administration
- Developer sandbox environments
- Compliance requirements
- Risk mitigation

#### Example Boundary Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "ec2:Describe*",
        "ec2:RunInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

### Resource-Based Policies

Some AWS services support resource-based policies that are attached to resources rather than identities.

#### Services Supporting Resource-Based Policies
- S3 (Bucket Policies)
- Lambda (Function Policies)
- KMS (Key Policies)
- SNS (Topic Policies)
- SQS (Queue Policies)

#### S3 Bucket Policy Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
```

---

## Security Features

### Multi-Factor Authentication (MFA)

MFA adds an extra layer of security by requiring two or more verification factors.

#### MFA Device Types

1. **Virtual MFA Devices**
   - Software applications (Google Authenticator, Authy, AWS MFA)
   - Most common and cost-effective
   - Support for multiple accounts

2. **Hardware MFA Devices**
   - Physical tokens (YubiKey, Gemalto)
   - Higher security for sensitive environments
   - More expensive but tamper-resistant

3. **SMS MFA** (Not recommended for root account)
   - Text message verification codes
   - Less secure due to SIM swapping attacks

#### MFA Implementation

**For Console Access:**
```bash
# Users must provide:
1. Username/Password (something they know)
2. MFA code (something they have)
```

**For API/CLI Access:**
```bash
# Use STS to get temporary credentials
aws sts get-session-token --serial-number arn:aws:iam::123456789012:mfa/user --token-code 123456
```

#### MFA Policy Example
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "BoolIfExists": {
          "aws:MultiFactorAuthPresent": "false"
        }
      }
    }
  ]
}
```

### Password Policies

Password policies enforce complexity requirements and rotation schedules.

#### Password Policy Settings

| Setting | Description | Recommendation |
|---------|-------------|----------------|
| Minimum Length | Character count | 14+ characters |
| Character Types | Upper, lower, numbers, symbols | Require all types |
| Password Reuse | Previous passwords to remember | 24 passwords |
| Max Age | Days before expiration | 90 days |
| Password Recovery | Self-service reset | Enable with MFA |

#### Account Lockout Settings
- **Failed Attempts**: 3-5 attempts before lockout
- **Lockout Duration**: 15-30 minutes
- **Admin Override**: Allow admin unlock

### Access Keys Management

Access keys provide programmatic access to AWS APIs.

#### Access Key Best Practices

1. **Rotation Strategy**
   ```bash
   # Rotate access keys regularly (90 days)
   # Create new key → Update applications → Delete old key
   ```

2. **Least Privilege**
   - Assign minimal required permissions
   - Use temporary credentials when possible

3. **Secure Storage**
   - Never hardcode in applications
   - Use AWS Systems Manager Parameter Store
   - Use environment variables or config files

4. **Monitoring**
   - Track access key usage with CloudTrail
   - Monitor for unused keys
   - Alert on suspicious activity

#### Access Key States
- **Active**: Can be used for API calls
- **Inactive**: Cannot be used but not deleted
- **Deleted**: Permanently removed

### AWS Security Token Service (STS)

STS provides temporary, limited-privilege credentials.

#### STS Operations

1. **AssumeRole**
   - Switch to different role
   - Cross-account access
   - Temporary escalation

2. **GetSessionToken**
   - MFA-enabled temporary credentials
   - Same permissions as permanent credentials

3. **AssumeRoleWithWebIdentity**
   - Federated access with web identity providers
   - Mobile applications, web applications

4. **AssumeRoleWithSAML**
   - SAML-based federated access
   - Enterprise identity providers

#### STS Token Structure
```json
{
  "Credentials": {
    "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY",
    "SessionToken": "AQoEXAMPLEH4aoAH0gNCAPyJxz4BlCFFxWNE1OPTgk5TthT...",
    "Expiration": "2023-11-09T13:34:41Z"
  }
}
```

### IAM Credential Reports

Credential reports provide account-wide credential usage information.

#### Report Contents
- All users in the account
- Status of passwords, access keys, MFA devices
- Last used information
- Certificate status

#### Use Cases
- Security audits
- Compliance reporting
- Identifying unused credentials
- Password rotation tracking

### AWS CloudTrail Integration

CloudTrail logs all IAM API calls for security monitoring.

#### Key Events to Monitor
- User creation/deletion
- Policy changes
- Role assumptions
- Failed authentication attempts
- Privilege escalation attempts

#### Security Monitoring Queries
```json
// Failed console logins
{
  "eventName": "ConsoleLogin",
  "responseElements.ConsoleLogin": "Failure"
}

// Root account usage
{
  "userIdentity.type": "Root"
}

// Policy modifications
{
  "eventName": ["CreatePolicy", "DeletePolicy", "AttachUserPolicy"]
}
```

### IAM Access Analyzer

Access Analyzer identifies resources shared with external entities.

#### Capabilities
- **External Access Detection**: Resources accessible outside your account
- **Unused Access**: Permissions that haven't been used
- **Policy Validation**: Check policies for security issues
- **Access Preview**: Preview access changes before implementation

#### Supported Resources
- S3 buckets and access points
- IAM roles
- KMS keys
- Lambda functions
- SQS queues
- Secrets Manager secrets

---

## Advanced IAM Concepts

### Cross-Account Access

Cross-account access allows resources in one AWS account to access resources in another account.

#### Implementation Methods

1. **Cross-Account Roles (Recommended)**
   - Create role in target account
   - Trust policy allows source account
   - Users assume role for access

2. **Resource-Based Policies**
   - Attach policy directly to resource
   - Grant access to external principals
   - Simpler for specific resources

#### Cross-Account Role Setup

**Step 1: Create role in Account B (Target)**
```json
// Trust Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::ACCOUNT-A:user/CrossAccountUser"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "UniqueExternalId"
        }
      }
    }
  ]
}
```

**Step 2: Grant assume role permission in Account A**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "sts:AssumeRole",
      "Resource": "arn:aws:iam::ACCOUNT-B:role/CrossAccountRole"
    }
  ]
}
```

**Step 3: Assume role from Account A**
```bash
aws sts assume-role \
  --role-arn arn:aws:iam::ACCOUNT-B:role/CrossAccountRole \
  --role-session-name CrossAccountSession \
  --external-id UniqueExternalId
```

### Identity Federation

Federation allows users from external identity systems to access AWS resources.

#### Federation Types

1. **SAML 2.0 Federation**
   - Enterprise identity providers (Active Directory, ADFS)
   - Single Sign-On (SSO) capabilities
   - Browser-based and API access

2. **OpenID Connect (OIDC)**
   - Web identity providers (Google, Facebook, Amazon)
   - Mobile and web applications
   - JWT-based tokens

3. **Custom Identity Brokers**
   - Custom authentication systems
   - Direct STS API calls
   - Full control over authentication flow

#### SAML Federation Flow

```
1. User authenticates with IdP
2. IdP returns SAML assertion
3. Application calls AWS STS AssumeRoleWithSAML
4. STS validates assertion and returns temporary credentials
5. Application uses credentials to access AWS resources
```

#### Web Identity Federation Example

```javascript
// Mobile app using Cognito
AWS.config.credentials = new AWS.CognitoIdentityCredentials({
  IdentityPoolId: 'us-east-1:1234567890abcdef',
  Logins: {
    'graph.facebook.com': fbToken
  }
});
```

### AWS Single Sign-On (SSO)

AWS SSO provides centralized access management for multiple AWS accounts.

#### SSO Components
- **Permission Sets**: Collections of policies
- **Account Assignments**: User/group access to accounts
- **Identity Source**: Users and groups (SSO, AD, External IdP)

#### Benefits
- Centralized user management
- Consistent permissions across accounts
- Audit trail and compliance
- Integration with external identity providers

### AWS Organizations and SCPs

Service Control Policies (SCPs) provide guardrails for IAM permissions.

#### SCP Characteristics
- **Preventive controls**: What can't be done
- **Apply to OUs and accounts**: Hierarchical inheritance
- **Filter permissions**: Cannot grant permissions
- **Override IAM**: Even deny root user actions

#### SCP Example - Deny specific regions
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "StringNotEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    }
  ]
}
```

### IAM Identity Center (Successor to AWS SSO)

Modern identity management for AWS accounts and applications.

#### Key Features
- **Multi-account permissions**: Manage access across AWS organization
- **Application assignments**: SSO to cloud applications
- **Identity source flexibility**: Built-in directory, AD, external IdP
- **Permission sets**: Reusable IAM policies

#### Permission Set Structure
```json
{
  "SessionDuration": "PT4H",
  "InlinePolicy": {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "s3:ListAllMyBuckets",
        "Resource": "*"
      }
    ]
  },
  "ManagedPolicyArns": [
    "arn:aws:iam::aws:policy/ReadOnlyAccess"
  ]
}
```

### Temporary Security Credentials

Understanding when and how to use temporary credentials.

#### Use Cases
- **Cross-account access**: Temporary access to resources in other accounts
- **Federated users**: External identity provider authentication
- **EC2 instance roles**: Service access for applications
- **Lambda functions**: Function execution permissions
- **Mobile applications**: Client-side AWS API access

#### Credential Hierarchy
```
Root User (Permanent, Full Access)
├── IAM Users (Permanent, Limited Access)
├── IAM Roles (Temporary, Specific Purpose)
│   ├── EC2 Instance Roles
│   ├── Lambda Execution Roles
│   ├── Cross-Account Roles
│   └── Federated User Roles
└── Temporary Credentials (STS-generated)
```

### IAM Best Practices Summary

#### Account Security
- Use root account only for initial setup
- Enable MFA on root account
- Create separate AWS account for production

#### User Management
- Create individual IAM users
- Use groups for permission management
- Apply principle of least privilege
- Rotate credentials regularly

#### Role Strategy
- Use roles for AWS services
- Prefer roles over users for applications
- Use cross-account roles for external access
- Implement external ID for additional security

#### Policy Management
- Use managed policies over inline policies
- Implement permission boundaries
- Regular policy reviews and cleanup
- Document policy purposes

#### Monitoring and Auditing
- Enable CloudTrail in all regions
- Use IAM credential reports
- Implement Access Analyzer
- Set up alerting for suspicious activities

---

## Best Practices

### Security Best Practices

#### 1. Principle of Least Privilege
- Grant minimum permissions required for tasks
- Regular permission audits and cleanup
- Use IAM Access Analyzer to identify unused permissions
- Implement just-in-time access where possible

#### 2. Defense in Depth
- Multiple layers of security controls
- Combine IAM with other AWS security services
- Use SCPs for organizational guardrails
- Implement network-level controls

#### 3. Identity Management
- Use federation instead of IAM users when possible
- Centralize identity management with AWS Identity Center
- Implement strong password policies
- Mandate MFA for human access

#### 4. Monitoring and Logging
- Enable CloudTrail in all regions and accounts
- Monitor for privilege escalation attempts
- Set up automated responses to security events
- Regular access reviews and compliance checks

### Operational Best Practices

#### 1. Automation
- Use Infrastructure as Code for IAM resources
- Automate credential rotation
- Implement automated compliance checks
- Use AWS Config for resource compliance

#### 2. Documentation
- Document all custom policies and their purposes
- Maintain role and responsibility matrices
- Keep architecture diagrams up to date
- Document incident response procedures

#### 3. Testing
- Test IAM policies before deployment
- Use IAM policy simulator for validation
- Implement least privilege testing
- Regular penetration testing

---

## SAA-C03 Exam Tips

### Key Concepts for the Exam

#### 1. IAM Fundamentals (High Importance)
- **Users vs Roles**: Know when to use each
- **Groups**: Cannot be nested, users inherit permissions
- **Policies**: Effect evaluation order (Deny always wins)
- **Global Service**: IAM is not region-specific

#### 2. Cross-Account Access (High Importance)
- **Preferred Method**: Cross-account roles with trust policies
- **External ID**: Additional security for third-party access
- **Resource-based policies**: Alternative for specific resources
- **STS**: Understanding temporary credentials

#### 3. Federation (Medium Importance)
- **SAML 2.0**: Enterprise identity providers
- **Web Identity**: Mobile and web applications
- **AWS SSO/Identity Center**: Multi-account management
- **STS AssumeRole operations**: Different federation methods

#### 4. Security Features (High Importance)
- **MFA**: When required and how to enforce
- **Password policies**: Account-level settings
- **Access keys**: Rotation and security
- **CloudTrail**: IAM API logging

### Common Exam Scenarios

#### Scenario 1: Cross-Account Access
**Question Type**: "Company A needs to grant Company B access to specific S3 buckets"

**Solution Pattern**:
1. Create cross-account role in Company A
2. Trust policy allows Company B's account
3. Use external ID for additional security
4. Grant minimal required permissions

#### Scenario 2: Application Authentication
**Question Type**: "EC2 application needs to access AWS services securely"

**Solution Pattern**:
1. Create IAM role for EC2
2. Attach role to EC2 instance
3. Application uses AWS SDK with default credential chain
4. No hardcoded credentials needed

#### Scenario 3: Temporary Access
**Question Type**: "Developer needs temporary access to production account"

**Solution Pattern**:
1. Create assume-able role in production account
2. Grant developer permission to assume role
3. Use STS to get temporary credentials
4. Access expires automatically

#### Scenario 4: Federated Access
**Question Type**: "Integrate corporate Active Directory with AWS"

**Solution Pattern**:
1. Set up SAML identity provider in AWS
2. Create roles for different AD groups
3. Configure trust relationship with SAML provider
4. Users authenticate via corporate SSO

### Exam Question Patterns

#### 1. "Most Secure" Questions
- Look for MFA requirements
- Temporary credentials over permanent
- Least privilege principle
- External ID for third-party access

#### 2. "Cost-Effective" Questions
- IAM is free (choose IAM solutions)
- Avoid unnecessary services
- Use managed policies over custom when possible
- Centralized management approaches

#### 3. "Operational Excellence" Questions
- Automation over manual processes
- Infrastructure as Code
- Centralized logging and monitoring
- Standardized approaches

### Key Facts to Remember

#### Limits and Numbers
- 5,000 IAM users per account
- 300 groups per account
- 10 managed policies per user/group/role
- 2 access keys per user
- 1 hour default role session duration
- 12 hours maximum role session duration

#### Policy Evaluation
1. Explicit Deny (always wins)
2. Organizations SCP (filter)
3. Resource-based policies
4. Identity-based policies
5. Permission boundaries (filter)
6. Session policies (filter)

#### Authentication Methods
- **Console**: Username/password + MFA
- **CLI/API**: Access keys or temporary credentials
- **Cross-account**: Assume role
- **Federated**: Identity provider + role assumption

---

## Common Scenarios and Use Cases

### Scenario 1: Multi-Account Organization

**Business Requirement**: Large enterprise with development, staging, and production accounts

**IAM Solution**:
```
AWS Organizations
├── Master Account (Billing, IAM Identity Center)
├── Production Account
│   ├── Production Roles
│   └── Cross-account access from master
├── Staging Account
│   ├── Staging Roles
│   └── Developer access roles
└── Development Account
    ├── Developer full access
    └── Sandbox environments
```

**Implementation**:
1. Set up AWS Organizations in master account
2. Configure IAM Identity Center for centralized access
3. Create permission sets for different roles
4. Implement SCPs for security guardrails
5. Set up cross-account access patterns

### Scenario 2: Application Running on EC2

**Business Requirement**: Web application needs to access S3, DynamoDB, and SES

**IAM Solution**:
```json
// EC2 Instance Role Policy
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem"
      ],
      "Resource": "arn:aws:dynamodb:us-east-1:123456789012:table/MyAppTable"
    },
    {
      "Effect": "Allow",
      "Action": "ses:SendEmail",
      "Resource": "*"
    }
  ]
}
```

### Scenario 3: Third-Party Integration

**Business Requirement**: Grant monitoring company access to CloudWatch metrics

**IAM Solution**:
```json
// Trust Policy with External ID
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::MONITORING-COMPANY-ACCOUNT:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-external-id-from-monitoring-company"
        }
      }
    }
  ]
}
```

### Scenario 4: Developer Temporary Access

**Business Requirement**: Developers need temporary production access for troubleshooting

**IAM Solution**:
```json
// Break-glass role with time restrictions
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*",
      "Condition": {
        "Bool": {
          "aws:MultiFactorAuthPresent": "true"
        },
        "NumericLessThan": {
          "aws:MultiFactorAuthAge": "3600"
        },
        "DateGreaterThan": {
          "aws:CurrentTime": "${aws:TokenIssueTime}"
        },
        "DateLessThan": {
          "aws:CurrentTime": "${aws:TokenIssueTime + 2 hours}"
        }
      }
    }
  ]
}
```

---

## Practice Questions

### Question 1
A company needs to provide temporary access to external auditors to review security configurations across multiple AWS accounts. The auditors should have read-only access and the solution should be secure and auditable.

**What is the MOST secure approach?**

A) Create IAM users in each account with read-only permissions
B) Create a cross-account IAM role with ReadOnlyAccess policy and external ID
C) Share root account credentials temporarily
D) Create access keys and share them securely

**Answer: B** - Cross-account roles with external ID provide secure, temporary, and auditable access.

### Question 2
An application running on EC2 needs to access S3 buckets, but the security team requires that no permanent credentials be stored on the instance.

**What is the BEST solution?**

A) Store access keys in the application configuration file
B) Use environment variables for access keys
C) Create an IAM role and assign it to the EC2 instance
D) Use AWS Systems Manager Parameter Store for credentials

**Answer: C** - EC2 instance roles provide temporary credentials without storing permanent credentials.

### Question 3
A company wants to enforce MFA for all users accessing the AWS Management Console, but API access should work without MFA for automation scripts.

**Which policy condition should be used?**

A) `"aws:MultiFactorAuthPresent": "true"`
B) `"aws:RequestedRegion": "us-east-1"`
C) `"aws:SourceIp": "corporate-ip-range"`
D) `"aws:SecureTransport": "true"`

**Answer: A** - This condition ensures MFA is present for console access while allowing API access.

### Question 4
An organization has 50 AWS accounts and wants to ensure that users can only launch EC2 instances in approved regions.

**What is the MOST effective approach?**

A) Create IAM policies in each account restricting regions
B) Use AWS Config rules to monitor region compliance
C) Implement Service Control Policies (SCPs) in AWS Organizations
D) Use CloudTrail to audit region usage

**Answer: C** - SCPs provide preventive controls across all accounts in an organization.

### Question 5
A development team needs full access to their development account but should be denied the ability to delete CloudTrail logs.

**Which approach should be used?**

A) Remove CloudTrail permissions from their policies
B) Use an explicit Deny statement for CloudTrail delete actions
C) Create a separate role for CloudTrail management
D) Use resource-based policies on CloudTrail

**Answer: B** - Explicit Deny always takes precedence and cannot be overridden.

---

## AWS CLI Commands Reference

This section provides comprehensive AWS CLI commands for managing IAM resources. These commands are essential for automation, scripting, and operational tasks.

### Prerequisites

```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure AWS CLI with credentials
aws configure
# You'll be prompted for:
# - AWS Access Key ID
# - AWS Secret Access Key
# - Default region name
# - Default output format (json, yaml, text, table)

# Verify configuration
aws sts get-caller-identity
```

### User Management

#### Create Users

```bash
# Create a new IAM user
aws iam create-user --user-name john-doe

# Create user with tags
aws iam create-user \
  --user-name jane-smith \
  --tags Key=Department,Value=Engineering Key=Team,Value=DevOps

# Create user and set console password
aws iam create-user --user-name developer1
aws iam create-login-profile \
  --user-name developer1 \
  --password 'TempPassword123!' \
  --password-reset-required
```

#### List and Get Users

```bash
# List all IAM users
aws iam list-users

# List users with specific output format
aws iam list-users --output table

# Get specific user details
aws iam get-user --user-name john-doe

# List users with pagination
aws iam list-users --max-items 10

# Get current authenticated user
aws iam get-user
```

#### Update Users

```bash
# Change user name
aws iam update-user \
  --user-name john-doe \
  --new-user-name john-smith

# Update user's path (for organizational hierarchy)
aws iam update-user \
  --user-name john-smith \
  --new-path /engineering/developers/
```

#### Delete Users

```bash
# Delete login profile (console password)
aws iam delete-login-profile --user-name john-doe

# Delete access keys first
aws iam list-access-keys --user-name john-doe
aws iam delete-access-key \
  --user-name john-doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Detach managed policies
aws iam list-attached-user-policies --user-name john-doe
aws iam detach-user-policy \
  --user-name john-doe \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Delete inline policies
aws iam list-user-policies --user-name john-doe
aws iam delete-user-policy \
  --user-name john-doe \
  --policy-name MyInlinePolicy

# Remove from groups
aws iam list-groups-for-user --user-name john-doe
aws iam remove-user-from-group \
  --user-name john-doe \
  --group-name Developers

# Finally, delete the user
aws iam delete-user --user-name john-doe
```

### Group Management

#### Create Groups

```bash
# Create a new group
aws iam create-group --group-name Developers

# Create group with path
aws iam create-group \
  --group-name Admins \
  --path /privileged/
```

#### List Groups

```bash
# List all groups
aws iam list-groups

# List groups for a specific user
aws iam list-groups-for-user --user-name john-doe

# Get group details
aws iam get-group --group-name Developers

# List users in a group
aws iam get-group --group-name Developers --output json | jq '.Users[].UserName'
```

#### Manage Group Membership

```bash
# Add user to group
aws iam add-user-to-group \
  --user-name john-doe \
  --group-name Developers

# Add multiple users to a group (using loop)
for user in alice bob charlie; do
  aws iam add-user-to-group --user-name $user --group-name Developers
done

# Remove user from group
aws iam remove-user-from-group \
  --user-name john-doe \
  --group-name Developers
```

#### Delete Groups

```bash
# Remove all users from group first
aws iam get-group --group-name Developers --query 'Users[].UserName' --output text | \
  xargs -n 1 -I {} aws iam remove-user-from-group --user-name {} --group-name Developers

# Detach all managed policies
aws iam list-attached-group-policies --group-name Developers --query 'AttachedPolicies[].PolicyArn' --output text | \
  xargs -n 1 -I {} aws iam detach-group-policy --group-name Developers --policy-arn {}

# Delete all inline policies
aws iam list-group-policies --group-name Developers --query 'PolicyNames[]' --output text | \
  xargs -n 1 -I {} aws iam delete-group-policy --group-name Developers --policy-name {}

# Delete the group
aws iam delete-group --group-name Developers
```

### Role Management

#### Create Roles

```bash
# Create role with trust policy from file
cat > trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name EC2-S3-Access-Role \
  --assume-role-policy-document file://trust-policy.json \
  --description "Allows EC2 instances to access S3 buckets"

# Create role for Lambda
cat > lambda-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

aws iam create-role \
  --role-name Lambda-Execution-Role \
  --assume-role-policy-document file://lambda-trust-policy.json

# Create cross-account role with external ID
cat > cross-account-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:root"
      },
      "Action": "sts:AssumeRole",
      "Condition": {
        "StringEquals": {
          "sts:ExternalId": "unique-external-id-12345"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name CrossAccountRole \
  --assume-role-policy-document file://cross-account-trust-policy.json

# Create role with tags
aws iam create-role \
  --role-name AppRole \
  --assume-role-policy-document file://trust-policy.json \
  --tags Key=Environment,Value=Production Key=Application,Value=WebApp
```

#### List and Get Roles

```bash
# List all roles
aws iam list-roles

# List roles with path prefix
aws iam list-roles --path-prefix /service-role/

# Get specific role
aws iam get-role --role-name EC2-S3-Access-Role

# List instance profiles
aws iam list-instance-profiles

# List instance profiles for a role
aws iam list-instance-profiles-for-role --role-name EC2-S3-Access-Role
```

#### Assume Role

```bash
# Assume a role and get temporary credentials
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/CrossAccountRole \
  --role-session-name my-session \
  --duration-seconds 3600

# Assume role with external ID
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/CrossAccountRole \
  --role-session-name my-session \
  --external-id unique-external-id-12345

# Assume role with MFA
aws sts assume-role \
  --role-arn arn:aws:iam::123456789012:role/AdminRole \
  --role-session-name admin-session \
  --serial-number arn:aws:iam::123456789012:mfa/john-doe \
  --token-code 123456

# Use assumed role credentials (export to environment)
RESPONSE=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/MyRole --role-session-name session1)
export AWS_ACCESS_KEY_ID=$(echo $RESPONSE | jq -r '.Credentials.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo $RESPONSE | jq -r '.Credentials.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo $RESPONSE | jq -r '.Credentials.SessionToken')
```

#### Update Roles

```bash
# Update role description
aws iam update-role \
  --role-name EC2-S3-Access-Role \
  --description "Updated description for EC2 S3 access"

# Update assume role policy
aws iam update-assume-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-document file://updated-trust-policy.json

# Update max session duration (1 to 12 hours)
aws iam update-role \
  --role-name EC2-S3-Access-Role \
  --max-session-duration 43200
```

#### Instance Profiles

```bash
# Create instance profile
aws iam create-instance-profile \
  --instance-profile-name EC2-S3-Instance-Profile

# Add role to instance profile
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-S3-Instance-Profile \
  --role-name EC2-S3-Access-Role

# Remove role from instance profile
aws iam remove-role-from-instance-profile \
  --instance-profile-name EC2-S3-Instance-Profile \
  --role-name EC2-S3-Access-Role

# Delete instance profile
aws iam delete-instance-profile \
  --instance-profile-name EC2-S3-Instance-Profile

# Attach instance profile to EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-1234567890abcdef0 \
  --iam-instance-profile Name=EC2-S3-Instance-Profile
```

#### Delete Roles

```bash
# Remove from instance profiles
aws iam list-instance-profiles-for-role --role-name MyRole --query 'InstanceProfiles[].InstanceProfileName' --output text | \
  xargs -n 1 -I {} aws iam remove-role-from-instance-profile --instance-profile-name {} --role-name MyRole

# Detach managed policies
aws iam list-attached-role-policies --role-name MyRole --query 'AttachedPolicies[].PolicyArn' --output text | \
  xargs -n 1 -I {} aws iam detach-role-policy --role-name MyRole --policy-arn {}

# Delete inline policies
aws iam list-role-policies --role-name MyRole --query 'PolicyNames[]' --output text | \
  xargs -n 1 -I {} aws iam delete-role-policy --role-name MyRole --policy-name {}

# Delete the role
aws iam delete-role --role-name MyRole
```

### Policy Management

#### Create Managed Policies

```bash
# Create a custom managed policy
cat > my-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    },
    {
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::my-bucket"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name MyS3AccessPolicy \
  --policy-document file://my-policy.json \
  --description "Grants read and write access to my-bucket"

# Create policy with tags
aws iam create-policy \
  --policy-name MyTaggedPolicy \
  --policy-document file://my-policy.json \
  --tags Key=Environment,Value=Production Key=Team,Value=DevOps
```

#### List and Get Policies

```bash
# List all customer managed policies
aws iam list-policies --scope Local

# List AWS managed policies
aws iam list-policies --scope AWS

# List all policies
aws iam list-policies --scope All

# List policies with pagination
aws iam list-policies --max-items 20

# Get policy details
aws iam get-policy \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy

# Get specific policy version
aws iam get-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy \
  --version-id v1

# Get default (active) policy version document
POLICY_ARN="arn:aws:iam::123456789012:policy/MyS3AccessPolicy"
VERSION_ID=$(aws iam get-policy --policy-arn $POLICY_ARN --query 'Policy.DefaultVersionId' --output text)
aws iam get-policy-version --policy-arn $POLICY_ARN --version-id $VERSION_ID
```

#### Update Policies

```bash
# Create a new policy version (updates the policy)
cat > updated-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
EOF

aws iam create-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy \
  --policy-document file://updated-policy.json \
  --set-as-default

# List all policy versions
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy

# Set a specific version as default
aws iam set-default-policy-version \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy \
  --version-id v2

# Delete old policy versions (keep only current)
aws iam list-policy-versions \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy \
  --query 'Versions[?!IsDefaultVersion].VersionId' \
  --output text | \
  xargs -n 1 -I {} aws iam delete-policy-version \
    --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy \
    --version-id {}
```

#### Inline Policies

```bash
# Put inline policy on user
cat > user-inline-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "ec2:DescribeInstances",
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-user-policy \
  --user-name john-doe \
  --policy-name EC2ReadOnlyAccess \
  --policy-document file://user-inline-policy.json

# Put inline policy on group
aws iam put-group-policy \
  --group-name Developers \
  --policy-name DevelopmentResources \
  --policy-document file://group-inline-policy.json

# Put inline policy on role
aws iam put-role-policy \
  --role-name MyRole \
  --policy-name RoleInlinePolicy \
  --policy-document file://role-inline-policy.json

# Get inline policy document
aws iam get-user-policy \
  --user-name john-doe \
  --policy-name EC2ReadOnlyAccess

aws iam get-group-policy \
  --group-name Developers \
  --policy-name DevelopmentResources

aws iam get-role-policy \
  --role-name MyRole \
  --policy-name RoleInlinePolicy

# List inline policies
aws iam list-user-policies --user-name john-doe
aws iam list-group-policies --group-name Developers
aws iam list-role-policies --role-name MyRole

# Delete inline policies
aws iam delete-user-policy \
  --user-name john-doe \
  --policy-name EC2ReadOnlyAccess

aws iam delete-group-policy \
  --group-name Developers \
  --policy-name DevelopmentResources

aws iam delete-role-policy \
  --role-name MyRole \
  --policy-name RoleInlinePolicy
```

#### Delete Managed Policies

```bash
# List all entities attached to the policy
POLICY_ARN="arn:aws:iam::123456789012:policy/MyS3AccessPolicy"

# Detach from users
aws iam list-entities-for-policy --policy-arn $POLICY_ARN --entity-filter User --query 'PolicyUsers[].UserName' --output text | \
  xargs -n 1 -I {} aws iam detach-user-policy --user-name {} --policy-arn $POLICY_ARN

# Detach from groups
aws iam list-entities-for-policy --policy-arn $POLICY_ARN --entity-filter Group --query 'PolicyGroups[].GroupName' --output text | \
  xargs -n 1 -I {} aws iam detach-group-policy --group-name {} --policy-arn $POLICY_ARN

# Detach from roles
aws iam list-entities-for-policy --policy-arn $POLICY_ARN --entity-filter Role --query 'PolicyRoles[].RoleName' --output text | \
  xargs -n 1 -I {} aws iam detach-role-policy --role-name {} --policy-arn $POLICY_ARN

# Delete all non-default versions
aws iam list-policy-versions --policy-arn $POLICY_ARN --query 'Versions[?!IsDefaultVersion].VersionId' --output text | \
  xargs -n 1 -I {} aws iam delete-policy-version --policy-arn $POLICY_ARN --version-id {}

# Delete the policy
aws iam delete-policy --policy-arn $POLICY_ARN
```

### Attach and Detach Policies

#### Attach Managed Policies

```bash
# Attach AWS managed policy to user
aws iam attach-user-policy \
  --user-name john-doe \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Attach custom managed policy to user
aws iam attach-user-policy \
  --user-name john-doe \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy

# Attach policy to group
aws iam attach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Attach policy to role
aws iam attach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Attach multiple policies to a user
for policy in arn:aws:iam::aws:policy/ReadOnlyAccess \
              arn:aws:iam::aws:policy/IAMUserChangePassword; do
  aws iam attach-user-policy --user-name john-doe --policy-arn $policy
done
```

#### List Attached Policies

```bash
# List managed policies attached to user
aws iam list-attached-user-policies --user-name john-doe

# List managed policies attached to group
aws iam list-attached-group-policies --group-name Developers

# List managed policies attached to role
aws iam list-attached-role-policies --role-name EC2-S3-Access-Role

# List all entities that a policy is attached to
aws iam list-entities-for-policy \
  --policy-arn arn:aws:iam::123456789012:policy/MyS3AccessPolicy
```

#### Detach Managed Policies

```bash
# Detach policy from user
aws iam detach-user-policy \
  --user-name john-doe \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

# Detach policy from group
aws iam detach-group-policy \
  --group-name Developers \
  --policy-arn arn:aws:iam::aws:policy/PowerUserAccess

# Detach policy from role
aws iam detach-role-policy \
  --role-name EC2-S3-Access-Role \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Detach all managed policies from a user
aws iam list-attached-user-policies --user-name john-doe --query 'AttachedPolicies[].PolicyArn' --output text | \
  xargs -n 1 -I {} aws iam detach-user-policy --user-name john-doe --policy-arn {}
```

### Access Keys Management

#### Create Access Keys

```bash
# Create access key for a user
aws iam create-access-key --user-name john-doe

# Create access key and save to file
aws iam create-access-key --user-name john-doe > john-doe-keys.json

# Extract and display keys (save securely!)
aws iam create-access-key --user-name john-doe | jq -r '.AccessKey | "Access Key ID: \(.AccessKeyId)\nSecret Access Key: \(.SecretAccessKey)"'

# Create access key for current user
CURRENT_USER=$(aws iam get-user --query 'User.UserName' --output text)
aws iam create-access-key --user-name $CURRENT_USER
```

#### List and Get Access Keys

```bash
# List access keys for a user
aws iam list-access-keys --user-name john-doe

# List access keys for current user
aws iam list-access-keys

# Get access key metadata
aws iam get-access-key-last-used \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Find all users with multiple access keys
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  key_count=$(aws iam list-access-keys --user-name $user --query 'length(AccessKeyMetadata)')
  if [ "$key_count" -gt 1 ]; then
    echo "User $user has $key_count access keys"
  fi
done
```

#### Update Access Keys

```bash
# Deactivate an access key
aws iam update-access-key \
  --user-name john-doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Inactive

# Activate an access key
aws iam update-access-key \
  --user-name john-doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE \
  --status Active

# Rotate access keys (create new, test, delete old)
NEW_KEY=$(aws iam create-access-key --user-name john-doe)
echo "New key created. Test it before deleting the old one."
echo $NEW_KEY | jq -r '.AccessKey | "Access Key ID: \(.AccessKeyId)\nSecret Access Key: \(.SecretAccessKey)"'
# After testing, delete old key:
# aws iam delete-access-key --user-name john-doe --access-key-id OLD_KEY_ID
```

#### Delete Access Keys

```bash
# Delete a specific access key
aws iam delete-access-key \
  --user-name john-doe \
  --access-key-id AKIAIOSFODNN7EXAMPLE

# Delete all inactive access keys for a user
aws iam list-access-keys --user-name john-doe --query 'AccessKeyMetadata[?Status==`Inactive`].AccessKeyId' --output text | \
  xargs -n 1 -I {} aws iam delete-access-key --user-name john-doe --access-key-id {}
```

### MFA Device Management

#### Virtual MFA Devices

```bash
# Create virtual MFA device
aws iam create-virtual-mfa-device \
  --virtual-mfa-device-name john-doe-mfa \
  --outfile john-doe-mfa-qr.png \
  --bootstrap-method QRCodePNG

# Enable MFA device for user
# After scanning QR code and getting two consecutive codes from authenticator app:
aws iam enable-mfa-device \
  --user-name john-doe \
  --serial-number arn:aws:iam::123456789012:mfa/john-doe-mfa \
  --authentication-code-1 123456 \
  --authentication-code-2 789012

# List MFA devices for user
aws iam list-mfa-devices --user-name john-doe

# List virtual MFA devices
aws iam list-virtual-mfa-devices
```

#### Hardware MFA Devices

```bash
# Enable hardware MFA device
aws iam enable-mfa-device \
  --user-name john-doe \
  --serial-number GAHT12345678 \
  --authentication-code-1 123456 \
  --authentication-code-2 789012
```

#### Deactivate and Delete MFA

```bash
# Deactivate MFA device
aws iam deactivate-mfa-device \
  --user-name john-doe \
  --serial-number arn:aws:iam::123456789012:mfa/john-doe-mfa

# Delete virtual MFA device (must be deactivated first)
aws iam delete-virtual-mfa-device \
  --serial-number arn:aws:iam::123456789012:mfa/john-doe-mfa

# Resync MFA device (if out of sync)
aws iam resync-mfa-device \
  --user-name john-doe \
  --serial-number arn:aws:iam::123456789012:mfa/john-doe-mfa \
  --authentication-code-1 123456 \
  --authentication-code-2 789012
```

### Password Policy Configuration

```bash
# Get current password policy
aws iam get-account-password-policy

# Set custom password policy
aws iam update-account-password-policy \
  --minimum-password-length 14 \
  --require-symbols \
  --require-numbers \
  --require-uppercase-characters \
  --require-lowercase-characters \
  --allow-users-to-change-password \
  --max-password-age 90 \
  --password-reuse-prevention 5 \
  --hard-expiry

# Set less strict password policy
aws iam update-account-password-policy \
  --minimum-password-length 8 \
  --allow-users-to-change-password \
  --no-require-symbols \
  --no-require-numbers

# Delete password policy (revert to defaults)
aws iam delete-account-password-policy
```

### User Password Management

```bash
# Create login profile with password
aws iam create-login-profile \
  --user-name john-doe \
  --password 'TempPassword123!' \
  --password-reset-required

# Update user password
aws iam update-login-profile \
  --user-name john-doe \
  --password 'NewPassword456!' \
  --no-password-reset-required

# Get login profile
aws iam get-login-profile --user-name john-doe

# Delete login profile (removes console access)
aws iam delete-login-profile --user-name john-doe

# Change your own password (requires old password)
aws iam change-password \
  --old-password 'OldPassword123!' \
  --new-password 'NewPassword456!'
```

### Service-Linked Roles

```bash
# List service-linked roles
aws iam list-roles --path-prefix /aws-service-role/

# Create service-linked role
aws iam create-service-linked-role \
  --aws-service-name elasticbeanstalk.amazonaws.com

aws iam create-service-linked-role \
  --aws-service-name autoscaling.amazonaws.com

# Create service-linked role with custom suffix
aws iam create-service-linked-role \
  --aws-service-name autoscaling.amazonaws.com \
  --custom-suffix my-custom-suffix

# Get service-linked role deletion status
aws iam get-service-linked-role-deletion-status \
  --deletion-task-id task-id-from-delete-response

# Delete service-linked role (AWS handles cleanup)
aws iam delete-service-linked-role \
  --role-name AWSServiceRoleForAutoScaling
```

### Permission Boundaries

```bash
# Create permission boundary policy
cat > permission-boundary.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*",
        "ec2:Describe*",
        "cloudwatch:*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Deny",
      "Action": [
        "iam:*",
        "organizations:*",
        "account:*"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name DeveloperBoundary \
  --policy-document file://permission-boundary.json

# Set permission boundary on user
aws iam put-user-permissions-boundary \
  --user-name john-doe \
  --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary

# Set permission boundary on role
aws iam put-role-permissions-boundary \
  --role-name MyRole \
  --permissions-boundary arn:aws:iam::123456789012:policy/DeveloperBoundary

# Get user with permission boundary info
aws iam get-user --user-name john-doe

# Delete permission boundary from user
aws iam delete-user-permissions-boundary --user-name john-doe

# Delete permission boundary from role
aws iam delete-role-permissions-boundary --role-name MyRole
```

### Tags for IAM Resources

```bash
# Tag a user
aws iam tag-user \
  --user-name john-doe \
  --tags Key=Department,Value=Engineering Key=Environment,Value=Production

# Tag a role
aws iam tag-role \
  --role-name MyRole \
  --tags Key=Application,Value=WebApp Key=CostCenter,Value=12345

# Tag a policy
aws iam tag-policy \
  --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
  --tags Key=Compliance,Value=SOC2 Key=Owner,Value=SecurityTeam

# List tags for user
aws iam list-user-tags --user-name john-doe

# List tags for role
aws iam list-role-tags --role-name MyRole

# List tags for policy
aws iam list-policy-tags \
  --policy-arn arn:aws:iam::123456789012:policy/MyPolicy

# Untag resources
aws iam untag-user \
  --user-name john-doe \
  --tag-keys Department Environment

aws iam untag-role \
  --role-name MyRole \
  --tag-keys Application CostCenter

aws iam untag-policy \
  --policy-arn arn:aws:iam::123456789012:policy/MyPolicy \
  --tag-keys Compliance Owner
```

### Account Alias

```bash
# Create account alias (for friendly sign-in URL)
aws iam create-account-alias --account-alias my-company-name

# List account aliases
aws iam list-account-aliases

# Delete account alias
aws iam delete-account-alias --account-alias my-company-name

# Get account sign-in URL
ALIAS=$(aws iam list-account-aliases --query 'AccountAliases[0]' --output text)
if [ "$ALIAS" != "None" ]; then
  echo "Sign-in URL: https://${ALIAS}.signin.aws.amazon.com/console"
else
  ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
  echo "Sign-in URL: https://${ACCOUNT_ID}.signin.aws.amazon.com/console"
fi
```

### Credential Reports

```bash
# Generate credential report
aws iam generate-credential-report

# Get credential report status
aws iam generate-credential-report --query 'State' --output text

# Download credential report
aws iam get-credential-report --output text --query 'Content' | base64 --decode > credential-report.csv

# View credential report
cat credential-report.csv | column -t -s, | less -S

# Analyze credential report (find users with old passwords)
aws iam get-credential-report --output text --query 'Content' | base64 --decode | \
  awk -F',' 'NR>1 && $5!="N/A" && $5!="no_information" {print $1, $5}' | \
  while read user age; do
    days=$(( ($(date +%s) - $(date -d "$age" +%s)) / 86400 ))
    if [ $days -gt 90 ]; then
      echo "User $user has not changed password in $days days"
    fi
  done

# Find users without MFA
aws iam get-credential-report --output text --query 'Content' | base64 --decode | \
  awk -F',' 'NR>1 && $4=="false" && $8=="true" {print "User without MFA: " $1}'
```

### Access Analyzer

```bash
# Create access analyzer
aws accessanalyzer create-analyzer \
  --analyzer-name my-account-analyzer \
  --type ACCOUNT \
  --tags Key=Environment,Value=Production

# Create organization analyzer (requires AWS Organizations)
aws accessanalyzer create-analyzer \
  --analyzer-name my-org-analyzer \
  --type ORGANIZATION

# List analyzers
aws accessanalyzer list-analyzers

# Get analyzer details
aws accessanalyzer get-analyzer \
  --analyzer-name my-account-analyzer

# List findings
aws accessanalyzer list-findings \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer

# List findings with filters
aws accessanalyzer list-findings \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
  --filter '{"status": {"eq": ["ACTIVE"]}}'

# Get finding details
aws accessanalyzer get-finding \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
  --id finding-id-12345

# Update finding status
aws accessanalyzer update-findings \
  --analyzer-arn arn:aws:access-analyzer:us-east-1:123456789012:analyzer/my-account-analyzer \
  --ids finding-id-12345 \
  --status ARCHIVED

# Start policy generation
aws accessanalyzer start-policy-generation \
  --policy-generation-details '{"principalArn":"arn:aws:iam::123456789012:role/MyRole"}' \
  --cloud-trail-details '{"accessRole":"arn:aws:iam::123456789012:role/AccessAnalyzerRole","trails":[{"cloudTrailArn":"arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail"}],"startTime":"2024-01-01T00:00:00Z","endTime":"2024-01-31T23:59:59Z"}'

# Get generated policy
aws accessanalyzer get-generated-policy \
  --job-id policy-gen-job-id-12345

# Delete analyzer
aws accessanalyzer delete-analyzer \
  --analyzer-name my-account-analyzer
```

### Policy Simulation

```bash
# Simulate custom policy
cat > test-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-bucket/*"
    }
  ]
}
EOF

aws iam simulate-custom-policy \
  --policy-input-list file://test-policy.json \
  --action-names s3:GetObject s3:PutObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Simulate principal policy (test user's effective permissions)
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/john-doe \
  --action-names s3:GetObject s3:PutObject ec2:DescribeInstances \
  --resource-arns arn:aws:s3:::my-bucket/file.txt arn:aws:ec2:us-east-1:123456789012:instance/*

# Simulate with context (e.g., IP address condition)
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/john-doe \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/* \
  --context-entries "ContextKeyName=aws:SourceIp,ContextKeyValues=203.0.113.0,ContextKeyType=ip"

# Simulate with MFA context
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/john-doe \
  --action-names iam:DeleteUser \
  --resource-arns "*" \
  --context-entries "ContextKeyName=aws:MultiFactorAuthPresent,ContextKeyValues=true,ContextKeyType=boolean"

# Simulate with resource policy
aws iam simulate-custom-policy \
  --policy-input-list file://identity-policy.json \
  --resource-policy file://resource-policy.json \
  --action-names s3:GetObject \
  --resource-arns arn:aws:s3:::my-bucket/file.txt

# Simulate permissions boundary effect
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::123456789012:user/john-doe \
  --permissions-boundary-policy-input-list file://boundary-policy.json \
  --action-names s3:DeleteBucket ec2:TerminateInstances \
  --resource-arns "*"
```

### SAML and OIDC Identity Providers

#### SAML Providers

```bash
# Create SAML provider
aws iam create-saml-provider \
  --saml-metadata-document file://saml-metadata.xml \
  --name MyCompanySAML

# List SAML providers
aws iam list-saml-providers

# Get SAML provider details
aws iam get-saml-provider \
  --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyCompanySAML

# Update SAML provider metadata
aws iam update-saml-provider \
  --saml-metadata-document file://updated-saml-metadata.xml \
  --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyCompanySAML

# Delete SAML provider
aws iam delete-saml-provider \
  --saml-provider-arn arn:aws:iam::123456789012:saml-provider/MyCompanySAML

# Create role for SAML federation
cat > saml-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:saml-provider/MyCompanySAML"
      },
      "Action": "sts:AssumeRoleWithSAML",
      "Condition": {
        "StringEquals": {
          "SAML:aud": "https://signin.aws.amazon.com/saml"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name SAML-Admin-Role \
  --assume-role-policy-document file://saml-trust-policy.json
```

#### OIDC Providers

```bash
# Create OIDC provider (e.g., for GitHub Actions)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1

# List OIDC providers
aws iam list-open-id-connect-providers

# Get OIDC provider details
aws iam get-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com

# Add client ID to OIDC provider
aws iam add-client-id-to-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com \
  --client-id my-application

# Remove client ID from OIDC provider
aws iam remove-client-id-from-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com \
  --client-id my-application

# Update OIDC provider thumbprint
aws iam update-open-id-connect-provider-thumbprint \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 a031c46782e6e6c662c2c87c76da9aa62ccabd8e

# Delete OIDC provider
aws iam delete-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com

# Create role for OIDC federation (GitHub Actions example)
cat > oidc-trust-policy.json << 'EOF'
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
        },
        "StringLike": {
          "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:*"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name GitHubActionsRole \
  --assume-role-policy-document file://oidc-trust-policy.json
```

### Account Summary and Statistics

```bash
# Get account summary
aws iam get-account-summary

# Get specific metrics from account summary
aws iam get-account-summary --query 'SummaryMap.{Users:Users,Groups:Groups,Roles:Roles,Policies:Policies}'

# Count resources
echo "Users: $(aws iam list-users --query 'length(Users)' --output text)"
echo "Groups: $(aws iam list-groups --query 'length(Groups)' --output text)"
echo "Roles: $(aws iam list-roles --query 'length(Roles)' --output text)"
echo "Policies: $(aws iam list-policies --scope Local --query 'length(Policies)' --output text)"

# Get account authorization details (comprehensive dump)
aws iam get-account-authorization-details > account-authorization-details.json

# Get account authorization details filtered by type
aws iam get-account-authorization-details --filter User
aws iam get-account-authorization-details --filter Role
aws iam get-account-authorization-details --filter Group
aws iam get-account-authorization-details --filter LocalManagedPolicy
aws iam get-account-authorization-details --filter AWSManagedPolicy
```

### Useful Combination Commands

```bash
# Find all resources with a specific tag
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  tags=$(aws iam list-user-tags --user-name $user --query 'Tags[?Key==`Environment`].Value' --output text)
  if [ -n "$tags" ]; then
    echo "User: $user, Environment: $tags"
  fi
done

# Audit users without MFA
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  mfa=$(aws iam list-mfa-devices --user-name $user --query 'MFADevices' --output text)
  if [ -z "$mfa" ]; then
    echo "WARNING: User $user does not have MFA enabled"
  fi
done

# Find inactive access keys (not used in 90+ days)
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  for key in $(aws iam list-access-keys --user-name $user --query 'AccessKeyMetadata[].AccessKeyId' --output text); do
    last_used=$(aws iam get-access-key-last-used --access-key-id $key --query 'AccessKeyLastUsed.LastUsedDate' --output text)
    if [ "$last_used" != "None" ]; then
      days_ago=$(( ($(date +%s) - $(date -d "$last_used" +%s)) / 86400 ))
      if [ $days_ago -gt 90 ]; then
        echo "User: $user, Key: $key, Last used: $days_ago days ago"
      fi
    fi
  done
done

# Generate security report
cat > security-report.sh << 'EOFSCRIPT'
#!/bin/bash
echo "=================================="
echo "IAM Security Report"
echo "Generated: $(date)"
echo "=================================="
echo ""
echo "Account Summary:"
aws iam get-account-summary --query 'SummaryMap.{Users:Users,Groups:Groups,Roles:Roles}' --output table
echo ""
echo "Users without MFA:"
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  mfa=$(aws iam list-mfa-devices --user-name $user --query 'MFADevices' --output text)
  if [ -z "$mfa" ]; then
    echo "  - $user"
  fi
done
echo ""
echo "Unused Access Keys (90+ days):"
for user in $(aws iam list-users --query 'Users[].UserName' --output text); do
  for key in $(aws iam list-access-keys --user-name $user --query 'AccessKeyMetadata[].AccessKeyId' --output text); do
    last_used=$(aws iam get-access-key-last-used --access-key-id $key --query 'AccessKeyLastUsed.LastUsedDate' --output text)
    if [ "$last_used" != "None" ]; then
      days=$(( ($(date +%s) - $(date -d "$last_used" +%s)) / 86400 ))
      if [ $days -gt 90 ]; then
        echo "  - User: $user, Key: $key ($days days)"
      fi
    fi
  done
done
EOFSCRIPT
chmod +x security-report.sh
./security-report.sh

# Bulk operations: Create multiple users
cat > users.txt << 'EOF'
alice
bob
charlie
diana
EOF

while read username; do
  echo "Creating user: $username"
  aws iam create-user --user-name $username
  aws iam add-user-to-group --user-name $username --group-name Developers
  aws iam create-login-profile --user-name $username --password "TempPass123!" --password-reset-required
done < users.txt

# Export all policies to files
mkdir -p iam-policies
for policy_arn in $(aws iam list-policies --scope Local --query 'Policies[].Arn' --output text); do
  policy_name=$(echo $policy_arn | awk -F'/' '{print $NF}')
  version_id=$(aws iam get-policy --policy-arn $policy_arn --query 'Policy.DefaultVersionId' --output text)
  aws iam get-policy-version --policy-arn $policy_arn --version-id $version_id --query 'PolicyVersion.Document' > "iam-policies/${policy_name}.json"
  echo "Exported: $policy_name"
done
```

### Best Practices for CLI Usage

```bash
# Use profiles for multiple accounts
aws configure --profile production
aws configure --profile development

# Use with specific profile
aws iam list-users --profile production

# Set default region
aws configure set region us-east-1
aws configure set region eu-west-1 --profile production

# Use output formats
aws iam list-users --output json    # Default, programmatic
aws iam list-users --output yaml    # Human-readable
aws iam list-users --output table   # Formatted table
aws iam list-users --output text    # Tab-delimited

# Use JQ for JSON parsing
aws iam list-users | jq '.Users[] | {name: .UserName, created: .CreateDate}'
aws iam list-users | jq -r '.Users[].UserName'

# Use query parameter (built-in JMESPath)
aws iam list-users --query 'Users[].UserName'
aws iam list-users --query 'Users[?contains(UserName, `admin`)]'
aws iam list-users --query 'Users[].{Name:UserName,ID:UserId}' --output table

# Dry run and validation
aws iam create-user --user-name test-user --generate-cli-skeleton
aws iam create-user --user-name test-user --cli-input-json file://user-config.json

# Debugging
aws iam list-users --debug 2> debug.log
aws iam list-users --no-verify-ssl  # For testing only

# Pagination handling
aws iam list-users --max-items 100 --starting-token $NEXT_TOKEN

# Using environment variables
export AWS_DEFAULT_REGION=us-east-1
export AWS_DEFAULT_OUTPUT=json
export AWS_PROFILE=production
```

---

## Summary

This comprehensive guide covers all essential IAM concepts for the AWS Solutions Architect Associate (SAA-C03) certification:

### Key Takeaways

1. **IAM is Global**: Not region-specific, but some features have regional components
2. **Principle of Least Privilege**: Always grant minimum required permissions
3. **Roles over Users**: Prefer roles for applications and cross-account access
4. **Federation**: Use external identity providers when possible
5. **Temporary Credentials**: More secure than permanent credentials
6. **Monitor Everything**: Use CloudTrail, Access Analyzer, and credential reports

### Exam Success Tips

- Understand when to use users vs roles vs groups
- Know cross-account access patterns
- Memorize policy evaluation logic
- Practice with IAM policy simulator
- Focus on security best practices
- Understand integration with other AWS services

### Final Recommendations

- Hands-on practice with IAM console and CLI
- Review AWS documentation for latest features
- Take practice exams focusing on IAM scenarios
- Understand real-world implementation patterns
- Study AWS Well-Architected Framework security pillar

Good luck with your SAA-C03 certification! 🚀