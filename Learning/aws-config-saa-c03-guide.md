# AWS Config - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction to AWS Config](#introduction-to-aws-config)
2. [Core Concepts](#core-concepts)
3. [Configuration Recorder](#configuration-recorder)
4. [Configuration Items](#configuration-items)
5. [Configuration History](#configuration-history)
6. [Configuration Snapshots](#configuration-snapshots)
7. [Config Rules](#config-rules)
8. [Remediation Actions](#remediation-actions)
9. [Conformance Packs](#conformance-packs)
10. [Organization Config](#organization-config)
11. [Multi-Account and Multi-Region Setup](#multi-account-and-multi-region-setup)
12. [Integration with Other AWS Services](#integration-with-other-aws-services)
13. [Cost Management](#cost-management)
14. [Security and Compliance](#security-and-compliance)
15. [Monitoring and Alerting](#monitoring-and-alerting)
16. [Troubleshooting](#troubleshooting)
17. [Best Practices](#best-practices)
18. [SAA-C03 Exam Focus Areas](#saa-c03-exam-focus-areas)

---

## Introduction to AWS Config

AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. Config continuously monitors and records your AWS resource configurations and allows you to automate the evaluation of recorded configurations against desired configurations.

### Key Capabilities
- **Configuration Management**: Track resource configurations and changes over time
- **Compliance Monitoring**: Evaluate resources against organizational policies
- **Change Management**: Understand relationships between resources and track changes
- **Security Analysis**: Identify security vulnerabilities and misconfigurations
- **Operational Troubleshooting**: Investigate configuration-related issues

### Config vs Other AWS Services

| Service | Purpose | Key Features |
|---------|---------|--------------|
| AWS Config | Configuration compliance & governance | Resource configuration tracking, compliance rules |
| CloudTrail | API activity logging | Who, what, when, where of API calls |
| CloudWatch | Monitoring & observability | Metrics, logs, alarms, dashboards |
| Systems Manager | Operational management | Patch management, automation, parameter store |
| Security Hub | Centralized security findings | Security posture, compliance standards |

### When to Use AWS Config
- **Compliance requirements**: SOC, PCI-DSS, HIPAA compliance
- **Change management**: Track and audit configuration changes
- **Security governance**: Enforce security best practices
- **Operational excellence**: Maintain desired configurations
- **Cost optimization**: Identify unused or misconfigured resources

---

## Core Concepts

### Configuration Recorder
A configuration recorder records the configurations of supported AWS resources in your account and delivers the configuration information to a delivery channel.

**Key Points:**
- Only one configuration recorder per region per account
- Must be turned on to start recording
- Can be stopped and started as needed
- Records configuration changes for supported resource types

### Delivery Channel
Provides the configuration information recorded by the configuration recorder to an S3 bucket and optionally to an Amazon SNS topic.

**Components:**
- **S3 Bucket**: Primary destination for configuration data
- **SNS Topic**: Optional notifications for configuration changes
- **Delivery Properties**: Frequency and format of deliveries

### Resource Types
AWS Config supports tracking of 100+ AWS resource types including:
- **Compute**: EC2 instances, Auto Scaling groups, Lambda functions
- **Storage**: S3 buckets, EBS volumes, EFS file systems
- **Network**: VPCs, security groups, NACLs, load balancers
- **Database**: RDS instances, DynamoDB tables
- **Security**: IAM users, roles, policies, KMS keys

### Supported Regions
AWS Config is available in all commercial AWS regions and AWS GovCloud regions.

---

## Configuration Recorder

### Setting Up Configuration Recorder

#### Basic Configuration
```json
{
  "ConfigurationRecorder": {
    "name": "default",
    "roleARN": "arn:aws:iam::123456789012:role/aws-config-role",
    "recordingGroup": {
      "allSupported": true,
      "includeGlobalResourceTypes": true,
      "resourceTypes": []
    }
  }
}
```

#### Selective Recording
```json
{
  "ConfigurationRecorder": {
    "name": "selective-recorder",
    "roleARN": "arn:aws:iam::123456789012:role/aws-config-role",
    "recordingGroup": {
      "allSupported": false,
      "includeGlobalResourceTypes": false,
      "resourceTypes": [
        "AWS::EC2::Instance",
        "AWS::EC2::SecurityGroup",
        "AWS::S3::Bucket",
        "AWS::RDS::DBInstance"
      ]
    }
  }
}
```

### Recording Group Options

#### All Supported Resources
- Records all supported resource types
- Automatically includes new resource types as they become available
- Includes global resources (IAM, CloudFront, etc.)

#### Specific Resource Types
- Records only specified resource types
- More cost-effective for targeted compliance
- Requires manual updates for new resource types

### Global Resources
- **IAM**: Users, groups, roles, policies
- **CloudFront**: Distributions
- **Route 53**: Hosted zones
- **WAF**: Web ACLs

**Important:** Global resources are recorded in the US East (N. Virginia) region but can be included in any region's configuration recorder.

---

## Configuration Items

### What is a Configuration Item?
A configuration item (CI) is a point-in-time snapshot of the various attributes of a supported AWS resource.

### Configuration Item Components
```json
{
  "configurationItemVersion": "1.3",
  "accountId": "123456789012",
  "configurationItemCaptureTime": "2023-01-01T12:00:00.000Z",
  "configurationItemStatus": "ResourceDiscovered",
  "configurationStateId": "1234567890",
  "resourceId": "i-1234567890abcdef0",
  "resourceType": "AWS::EC2::Instance",
  "resourceName": "MyWebServer",
  "awsRegion": "us-east-1",
  "availabilityZone": "us-east-1a",
  "resourceCreationTime": "2023-01-01T10:00:00.000Z",
  "tags": {
    "Environment": "Production",
    "Application": "WebApp"
  },
  "relatedEvents": [],
  "relationships": [
    {
      "resourceId": "sg-12345678",
      "resourceType": "AWS::EC2::SecurityGroup",
      "name": "Is associated with SecurityGroup"
    }
  ],
  "configuration": {
    "instanceId": "i-1234567890abcdef0",
    "imageId": "ami-0abcdef1234567890",
    "state": {
      "code": 16,
      "name": "running"
    },
    "privateDnsName": "ip-10-0-1-100.ec2.internal",
    "publicDnsName": "ec2-1-2-3-4.compute-1.amazonaws.com",
    "instanceType": "t3.micro",
    "keyName": "my-key-pair",
    "securityGroups": [
      {
        "groupName": "web-sg",
        "groupId": "sg-12345678"
      }
    ]
  }
}
```

### Configuration Item Status
- **ResourceDiscovered**: Resource discovered and recorded for the first time
- **OK**: Resource configuration recorded successfully
- **ResourceNotRecorded**: Resource not recorded (e.g., resource type not selected)
- **ResourceDeleted**: Resource has been deleted
- **ResourceDeletedNotRecorded**: Deleted resource was not being recorded

### Resource Relationships
Config tracks relationships between resources:
- **Direct relationships**: EC2 instance → Security Group
- **Indirect relationships**: EC2 instance → Subnet → VPC
- **Dependency mapping**: Understanding impact of changes

---

## Configuration History

### Overview
Configuration history provides a chronological view of configuration changes for each resource.

### Accessing Configuration History

#### AWS CLI
```bash
# Get configuration history for a resource
aws configservice get-resource-config-history \
    --resource-type AWS::EC2::Instance \
    --resource-id i-1234567890abcdef0

# Get configuration history for a specific time period
aws configservice get-resource-config-history \
    --resource-type AWS::EC2::Instance \
    --resource-id i-1234567890abcdef0 \
    --earlier-time 2023-01-01T00:00:00Z \
    --later-time 2023-01-31T23:59:59Z
```

#### AWS Console
- Navigate to Config → Resources
- Select resource type and specific resource
- View configuration timeline and changes

### Configuration Timeline
Shows chronological sequence of configuration changes:
- **Change detection**: When changes occurred
- **Configuration differences**: What changed between versions
- **Related events**: CloudTrail events that caused changes
- **Impact analysis**: Effects on related resources

### Use Cases for Configuration History
- **Change auditing**: Track who changed what and when
- **Troubleshooting**: Identify when issues started
- **Compliance reporting**: Demonstrate configuration compliance over time
- **Rollback planning**: Understand previous working configurations

---

## Configuration Snapshots

### Overview
Configuration snapshots provide a point-in-time view of all recorded resources in your account.

### Creating Snapshots
```bash
# Deliver configuration snapshot
aws configservice deliver-config-snapshot \
    --delivery-channel-name default

# Schedule periodic snapshots via delivery channel
aws configservice put-delivery-channel \
    --delivery-channel '{
      "name": "default",
      "s3BucketName": "my-config-bucket",
      "configSnapshotDeliveryProperties": {
        "deliveryFrequency": "TwentyFour_Hours"
      }
    }'
```

### Snapshot Contents
- Complete inventory of all recorded resources
- Current configuration state of each resource
- Resource relationships and dependencies
- Metadata about the snapshot creation

### Delivery Frequencies
- **One_Hour**: Every hour
- **Three_Hours**: Every 3 hours
- **Six_Hours**: Every 6 hours
- **Twelve_Hours**: Every 12 hours
- **TwentyFour_Hours**: Daily (most common)

### Snapshot Use Cases
- **Backup configurations**: Point-in-time recovery reference
- **Change management**: Compare configurations across time
- **Compliance reporting**: Regular compliance state documentation
- **Disaster recovery**: Understand pre-incident configurations

---

## Config Rules

### Overview
Config rules represent desired configurations for your resources and evaluate whether your resources comply with these configurations.

### Types of Config Rules

#### AWS Managed Rules
Pre-built rules created and maintained by AWS:

```bash
# Example: Check if S3 buckets are publicly readable
aws configservice put-config-rule \
    --config-rule '{
      "ConfigRuleName": "s3-bucket-public-read-prohibited",
      "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED"
      }
    }'
```

#### Custom Config Rules
Custom rules using AWS Lambda functions:

```json
{
  "ConfigRuleName": "custom-security-group-rule",
  "Source": {
    "Owner": "AWS_LAMBDA",
    "SourceIdentifier": "arn:aws:lambda:us-east-1:123456789012:function:CustomConfigRule",
    "SourceDetails": [
      {
        "EventSource": "aws.config",
        "MessageType": "ConfigurationItemChangeNotification"
      }
    ]
  },
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::SecurityGroup"
    ]
  }
}
```

### Common AWS Managed Rules

#### Security Rules
- **root-access-key-check**: Root account access keys
- **mfa-enabled-for-iam-console-access**: MFA for console access
- **s3-bucket-public-access-prohibited**: S3 bucket public access
- **encrypted-volumes**: EBS volume encryption
- **rds-storage-encrypted**: RDS encryption

#### Operational Rules
- **approved-amis-by-id**: Approved AMI usage
- **desired-instance-type**: Approved instance types
- **ec2-instance-managed-by-systems-manager**: SSM management
- **eip-attached**: Elastic IP attachment

#### Cost Optimization Rules
- **ec2-instance-no-public-ip**: Instances without public IPs
- **ebs-optimized-instance**: EBS-optimized instances
- **underutilized-ebs-volume**: Underutilized EBS volumes

### Rule Evaluation

#### Evaluation Triggers
- **Configuration change**: When resource configuration changes
- **Periodic**: On schedule (1, 3, 6, 12, or 24 hours)
- **Hybrid**: Both configuration change and periodic

#### Compliance States
- **COMPLIANT**: Resource meets rule requirements
- **NON_COMPLIANT**: Resource violates rule requirements
- **NOT_APPLICABLE**: Rule doesn't apply to resource
- **INSUFFICIENT_DATA**: Not enough data to evaluate

### Rule Parameters
```json
{
  "ConfigRuleName": "required-tags",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "REQUIRED_TAGS"
  },
  "InputParameters": "{\"tag1Key\": \"Environment\", \"tag1Value\": \"Production,Development,Test\"}"
}
```

### Custom Lambda Rule Example
```python
import boto3
import json

def lambda_handler(event, context):
    config_client = boto3.client('config')
    
    # Get configuration item
    configuration_item = event['configurationItem']
    
    # Evaluate compliance
    compliance_type = 'COMPLIANT'
    
    if configuration_item['resourceType'] == 'AWS::EC2::Instance':
        # Check if instance has required tags
        tags = configuration_item.get('tags', {})
        if 'Environment' not in tags:
            compliance_type = 'NON_COMPLIANT'
    
    # Put evaluation
    config_client.put_evaluations(
        Evaluations=[
            {
                'ComplianceResourceType': configuration_item['resourceType'],
                'ComplianceResourceId': configuration_item['resourceId'],
                'ComplianceType': compliance_type,
                'OrderingTimestamp': configuration_item['configurationItemCaptureTime']
            }
        ],
        ResultToken=event['resultToken']
    )
    
    return {'statusCode': 200}
```

---

## Remediation Actions

### Overview
Config remediation allows you to automatically remediate non-compliant resources using AWS Systems Manager automation documents.

### Types of Remediation
- **Automatic remediation**: Automatically fix non-compliant resources
- **Manual remediation**: Require manual approval before fixing

### Setting Up Remediation

#### Automatic Remediation Example
```json
{
  "ConfigRuleName": "s3-bucket-public-read-prohibited",
  "RemediationConfigurations": [
    {
      "ConfigRuleName": "s3-bucket-public-read-prohibited",
      "TargetType": "SSM_DOCUMENT",
      "TargetId": "AWSConfigRemediation-RemoveS3BucketPublicReadAccess",
      "TargetVersion": "1",
      "Parameters": {
        "AutomationAssumeRole": {
          "StaticValue": {
            "Values": ["arn:aws:iam::123456789012:role/aws-config-remediation-role"]
          }
        },
        "BucketName": {
          "ResourceValue": {
            "Value": "RESOURCE_ID"
          }
        }
      },
      "Automatic": true,
      "ExecutionControls": {
        "SsmControls": {
          "ConcurrentExecutionRatePercentage": 25,
          "ErrorPercentage": 10
        }
      }
    }
  ]
}
```

#### Manual Remediation Example
```json
{
  "ConfigRuleName": "ec2-security-group-attached-to-eni",
  "RemediationConfigurations": [
    {
      "ConfigRuleName": "ec2-security-group-attached-to-eni",
      "TargetType": "SSM_DOCUMENT",
      "TargetId": "AWSConfigRemediation-DeleteUnusedSecurityGroup",
      "Automatic": false,
      "Parameters": {
        "AutomationAssumeRole": {
          "StaticValue": {
            "Values": ["arn:aws:iam::123456789012:role/aws-config-remediation-role"]
          }
        }
      }
    }
  ]
}
```

### Common Remediation Actions

#### Security Remediations
- Remove S3 bucket public access
- Attach IAM policies to users
- Enable MFA for root account
- Encrypt unencrypted EBS volumes
- Update security group rules

#### Operational Remediations
- Stop non-compliant EC2 instances
- Attach IAM roles to EC2 instances
- Enable detailed monitoring
- Apply required tags to resources

### Custom Remediation Documents
```yaml
schemaVersion: '0.3'
description: Custom remediation to tag EC2 instances
assumeRole: '{{ AutomationAssumeRole }}'
parameters:
  InstanceId:
    type: String
    description: EC2 Instance ID
  AutomationAssumeRole:
    type: String
    description: IAM role for automation
mainSteps:
  - name: TagInstance
    action: 'aws:executeAwsApi'
    inputs:
      Service: ec2
      Api: CreateTags
      Resources:
        - '{{ InstanceId }}'
      Tags:
        - Key: Environment
          Value: Production
        - Key: Compliance
          Value: Remediated
```

---

## Conformance Packs

### Overview
Conformance packs are a collection of Config rules and remediation actions that can be easily deployed as a single entity in an account and region or across an organization.

### AWS Conformance Pack Templates

#### Security Best Practices Pack
```yaml
Parameters:
  S3BucketPublicAccessProhibitedParamBucketName:
    Type: String
    Default: ""
    
Resources:
  S3BucketPublicReadProhibited:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: s3-bucket-public-read-prohibited
      Source:
        Owner: AWS
        SourceIdentifier: S3_BUCKET_PUBLIC_READ_PROHIBITED
        
  RootAccessKeyCheck:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: root-access-key-check
      Source:
        Owner: AWS
        SourceIdentifier: ROOT_ACCESS_KEY_CHECK
        
  MfaEnabledForIamConsoleAccess:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: mfa-enabled-for-iam-console-access
      Source:
        Owner: AWS
        SourceIdentifier: MFA_ENABLED_FOR_IAM_CONSOLE_ACCESS
```

#### Operational Best Practices Pack
```yaml
Resources:
  Ec2InstanceManagedBySystemsManager:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: ec2-instance-managed-by-systems-manager
      Source:
        Owner: AWS
        SourceIdentifier: EC2_INSTANCE_MANAGED_BY_SSM
        
  RequiredTags:
    Type: AWS::Config::ConfigRule
    Properties:
      ConfigRuleName: required-tags
      Source:
        Owner: AWS
        SourceIdentifier: REQUIRED_TAGS
      InputParameters: |
        {
          "tag1Key": "Environment",
          "tag2Key": "Owner"
        }
```

### Deploying Conformance Packs
```bash
# Deploy conformance pack
aws configservice put-conformance-pack \
    --conformance-pack-name security-best-practices \
    --template-s3-uri s3://my-bucket/security-conformance-pack.yaml \
    --delivery-s3-bucket my-config-bucket

# Deploy across organization
aws configservice put-organization-conformance-pack \
    --organization-conformance-pack-name org-security-pack \
    --template-s3-uri s3://my-bucket/security-conformance-pack.yaml \
    --delivery-s3-bucket my-org-config-bucket
```

### Conformance Pack Benefits
- **Standardization**: Consistent rules across accounts
- **Compliance frameworks**: Pre-built packs for standards
- **Simplified deployment**: Deploy multiple rules at once
- **Organization-wide**: Deploy to all accounts in organization

---

## Organization Config

### Overview
AWS Organizations integration with Config enables you to centrally manage Config across all accounts in your organization.

### Aggregated View
```bash
# Create configuration aggregator
aws configservice put-configuration-aggregator \
    --configuration-aggregator-name organization-aggregator \
    --organization-aggregation-source '{
      "RoleArn": "arn:aws:iam::123456789012:role/aws-config-role",
      "AwsRegions": ["us-east-1", "us-west-2", "eu-west-1"],
      "AllAwsRegions": false
    }'
```

### Multi-Account Config Rules
```bash
# Deploy organization Config rule
aws configservice put-organization-config-rule \
    --organization-config-rule-name org-s3-bucket-public-read-prohibited \
    --organization-managed-rule-metadata '{
      "Description": "Organization rule for S3 bucket public read",
      "RuleIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED",
      "InputParameters": "{}"
    }'
```

### Centralized Compliance Monitoring
- **Aggregated compliance**: View compliance across all accounts
- **Exception management**: Handle account-specific exceptions
- **Drift detection**: Identify configuration drift across organization
- **Reporting**: Generate organization-wide compliance reports

### Required IAM Roles

#### Organization Config Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

#### Policy for Organization Config
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "organizations:ListAccounts",
        "organizations:DescribeOrganization",
        "organizations:ListAWSServiceAccessForOrganization"
      ],
      "Resource": "*"
    }
  ]
}
```

---

## Multi-Account and Multi-Region Setup

### Architecture Patterns

#### Centralized Logging Architecture
```
Management Account
├── Config Aggregator
├── Central S3 Bucket
└── SNS Topics

Member Accounts (per region)
├── Configuration Recorder
├── Delivery Channel → Central S3
└── Config Rules
```

#### Distributed Architecture
```
Each Account
├── Configuration Recorder
├── Local S3 Bucket
├── Config Rules
└── Local Compliance Monitoring
```

### Cross-Account S3 Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AWSConfigBucketPermissionsCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "s3:GetBucketAcl",
      "Resource": "arn:aws:s3:::central-config-bucket",
      "Condition": {
        "StringEquals": {
          "AWS:SourceAccount": [
            "111111111111",
            "222222222222",
            "333333333333"
          ]
        }
      }
    },
    {
      "Sid": "AWSConfigBucketExistenceCheck",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::central-config-bucket"
    },
    {
      "Sid": "AWSConfigBucketDelivery",
      "Effect": "Allow",
      "Principal": {
        "Service": "config.amazonaws.com"
      },
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::central-config-bucket/AWSLogs/*/Config/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control",
          "AWS:SourceAccount": [
            "111111111111",
            "222222222222",
            "333333333333"
          ]
        }
      }
    }
  ]
}
```

### Multi-Region Configuration
```bash
# Enable Config in multiple regions
for region in us-east-1 us-west-2 eu-west-1; do
  aws configservice put-configuration-recorder \
    --region $region \
    --configuration-recorder file://recorder-config.json
    
  aws configservice put-delivery-channel \
    --region $region \
    --delivery-channel file://delivery-channel-config.json
    
  aws configservice start-configuration-recorder \
    --region $region \
    --configuration-recorder-name default
done
```

---

## Integration with Other AWS Services

### Amazon S3
- **Primary storage**: Configuration items and history
- **Snapshot delivery**: Regular configuration snapshots
- **Cross-account access**: Centralized logging
- **Lifecycle policies**: Cost optimization for old data

#### S3 Integration Configuration
```json
{
  "DeliveryChannel": {
    "name": "default",
    "s3BucketName": "my-config-bucket",
    "s3KeyPrefix": "config-data",
    "configSnapshotDeliveryProperties": {
      "deliveryFrequency": "TwentyFour_Hours"
    }
  }
}
```

### Amazon SNS
- **Change notifications**: Real-time alerts for configuration changes
- **Rule compliance**: Notifications for compliance violations
- **Integration**: Connect to email, SMS, HTTP endpoints, Lambda

#### SNS Integration Example
```json
{
  "DeliveryChannel": {
    "name": "default",
    "s3BucketName": "my-config-bucket",
    "snsTopicARN": "arn:aws:sns:us-east-1:123456789012:config-notifications",
    "configSnapshotDeliveryProperties": {
      "deliveryFrequency": "TwentyFour_Hours"
    }
  }
}
```

### AWS Lambda
- **Custom rules**: Implement organization-specific compliance checks
- **Event processing**: Process Config change notifications
- **Automation**: Automated remediation actions
- **Integration**: Connect with other AWS services

#### Lambda Config Rule Example
```python
import json
import boto3

def lambda_handler(event, context):
    # Process Config rule evaluation
    config_item = event['configurationItem']
    
    # Example: Check if EC2 instance has required tags
    compliance = 'COMPLIANT'
    
    if config_item['resourceType'] == 'AWS::EC2::Instance':
        tags = config_item.get('tags', {})
        required_tags = ['Environment', 'Owner', 'Project']
        
        for tag in required_tags:
            if tag not in tags:
                compliance = 'NON_COMPLIANT'
                break
    
    # Return evaluation result
    return {
        'compliance_type': compliance,
        'annotation': f'Evaluated {config_item["resourceType"]} for required tags'
    }
```

### AWS Systems Manager
- **Remediation actions**: Automated compliance remediation
- **Automation documents**: Pre-built remediation workflows
- **Parameter Store**: Store configuration parameters
- **Patch Manager**: Track patch compliance

### Amazon EventBridge
- **Event routing**: Route Config events to targets
- **Cross-account events**: Send events to other accounts
- **Integration**: Connect with external systems
- **Automation**: Trigger automated workflows

#### EventBridge Rule for Config
```json
{
  "Rules": [
    {
      "Name": "ConfigComplianceRule",
      "EventPattern": {
        "source": ["aws.config"],
        "detail-type": ["Config Rules Compliance Change"],
        "detail": {
          "newEvaluationResult": {
            "complianceType": ["NON_COMPLIANT"]
          }
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:lambda:us-east-1:123456789012:function:HandleNonCompliance"
        }
      ]
    }
  ]
}
```

### AWS Security Hub
- **Security findings**: Aggregate Config findings
- **Compliance standards**: Map to security standards
- **Centralized view**: Single pane for security posture
- **Integration**: Combine with other security tools

---

## Cost Management

### Config Pricing Components

#### Configuration Items
- **Recording fee**: $0.003 per configuration item recorded
- **Free tier**: 1,000 configuration items per month per region

#### Config Rules
- **Rule evaluations**: $0.001 per evaluation
- **Free tier**: 100,000 evaluations per month per region

#### Conformance Packs
- **Pack evaluations**: $0.0012 per evaluation

### Cost Optimization Strategies

#### 1. Selective Resource Recording
```json
{
  "recordingGroup": {
    "allSupported": false,
    "includeGlobalResourceTypes": false,
    "resourceTypes": [
      "AWS::EC2::Instance",
      "AWS::EC2::SecurityGroup",
      "AWS::S3::Bucket",
      "AWS::IAM::Role"
    ]
  }
}
```

#### 2. Regional Optimization
- Record global resources in only one region
- Use aggregators instead of multiple recorders
- Consider resource distribution across regions

#### 3. Rule Optimization
```bash
# Use periodic evaluation for less critical rules
aws configservice put-config-rule \
    --config-rule '{
      "ConfigRuleName": "cost-optimized-rule",
      "Source": {
        "Owner": "AWS",
        "SourceIdentifier": "REQUIRED_TAGS"
      },
      "MaximumExecutionFrequency": "TwentyFour_Hours"
    }'
```

#### 4. S3 Lifecycle Management
```json
{
  "Rules": [
    {
      "ID": "ConfigDataLifecycle",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "AWSLogs/"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        },
        {
          "Days": 90,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 365,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ]
    }
  ]
}
```

### Cost Monitoring
```bash
# Monitor Config costs using Cost Explorer
aws ce get-cost-and-usage \
    --time-period Start=2023-01-01,End=2023-01-31 \
    --granularity MONTHLY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=SERVICE \
    --filter '{
      "Dimensions": {
        "Key": "SERVICE",
        "Values": ["AWS Config"]
      }
    }'
```

---

## Security and Compliance

### IAM Permissions

#### Config Service Role
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetBucketAcl",
        "s3:ListBucket"
      ],
      "Resource": "arn:aws:s3:::my-config-bucket"
    },
    {
      "Effect": "Allow",
      "Action": "s3:PutObject",
      "Resource": "arn:aws:s3:::my-config-bucket/AWSLogs/123456789012/Config/*",
      "Condition": {
        "StringEquals": {
          "s3:x-amz-acl": "bucket-owner-full-control"
        }
      }
    },
    {
      "Effect": "Allow",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-config-bucket/AWSLogs/123456789012/Config/*"
    },
    {
      "Effect": "Allow",
      "Action": "sns:Publish",
      "Resource": "arn:aws:sns:us-east-1:123456789012:config-topic"
    }
  ]
}
```

#### Read-Only Access Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "config:Get*",
        "config:Describe*",
        "config:List*",
        "config:Select*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Encryption

#### S3 Bucket Encryption
```json
{
  "Rules": [
    {
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "aws:kms",
        "KMSMasterKeyID": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
      },
      "BucketKeyEnabled": true
    }
  ]
}
```

#### SNS Topic Encryption
```json
{
  "KmsMasterKeyId": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
}
```

### Compliance Frameworks

#### SOC 2 Compliance
- Track access controls and configurations
- Monitor security group changes
- Audit IAM policy modifications
- Document configuration baselines

#### PCI-DSS Compliance
- Monitor cardholder data environment
- Track network segmentation changes
- Audit encryption configurations
- Maintain configuration documentation

#### HIPAA Compliance
- Monitor PHI access controls
- Track encryption configurations
- Audit network security changes
- Maintain audit trails

### Compliance Monitoring Rules
```json
{
  "ComplianceRules": [
    {
      "RuleName": "hipaa-encrypted-volumes",
      "Source": "AWS",
      "Identifier": "ENCRYPTED_VOLUMES",
      "ComplianceType": "REQUIRED"
    },
    {
      "RuleName": "pci-security-group-compliance",
      "Source": "CUSTOM",
      "Identifier": "custom-sg-pci-check",
      "ComplianceType": "REQUIRED"
    }
  ]
}
```

---

## Monitoring and Alerting

### CloudWatch Integration

#### Config Metrics
AWS Config publishes metrics to CloudWatch:
- `NumberOfResourcesCompliant`
- `NumberOfResourcesNonCompliant`
- `NumberOfResourcesNotApplicable`
- `ComplianceByConfigRule`

#### Custom Metrics
```python
import boto3

def publish_config_metrics():
    config_client = boto3.client('config')
    cloudwatch = boto3.client('cloudwatch')
    
    # Get compliance summary
    response = config_client.get_compliance_summary_by_config_rule()
    
    # Publish custom metrics
    cloudwatch.put_metric_data(
        Namespace='Custom/Config',
        MetricData=[
            {
                'MetricName': 'CompliancePercentage',
                'Value': calculate_compliance_percentage(response),
                'Unit': 'Percent'
            }
        ]
    )
```

### EventBridge Rules

#### Compliance Change Notifications
```json
{
  "Rules": [
    {
      "Name": "ConfigComplianceAlert",
      "EventPattern": {
        "source": ["aws.config"],
        "detail-type": ["Config Rules Compliance Change"],
        "detail": {
          "configRuleName": ["critical-security-rule"],
          "newEvaluationResult": {
            "complianceType": ["NON_COMPLIANT"]
          }
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:sns:us-east-1:123456789012:security-alerts"
        }
      ]
    }
  ]
}
```

#### Configuration Change Alerts
```json
{
  "Rules": [
    {
      "Name": "SecurityGroupChanges",
      "EventPattern": {
        "source": ["aws.config"],
        "detail-type": ["Config Configuration Item Change"],
        "detail": {
          "configurationItem": {
            "resourceType": ["AWS::EC2::SecurityGroup"]
          }
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:lambda:us-east-1:123456789012:function:SecurityGroupChangeHandler"
        }
      ]
    }
  ]
}
```

### Automated Response

#### Lambda Function for Automated Response
```python
import json
import boto3

def lambda_handler(event, context):
    # Process Config compliance change
    detail = event['detail']
    
    if detail['newEvaluationResult']['complianceType'] == 'NON_COMPLIANT':
        resource_type = detail['resourceType']
        resource_id = detail['resourceId']
        config_rule = detail['configRuleName']
        
        # Send notification
        send_alert(resource_type, resource_id, config_rule)
        
        # Log incident
        log_compliance_incident(detail)
        
        # Trigger remediation if automated
        if should_auto_remediate(config_rule):
            trigger_remediation(resource_type, resource_id, config_rule)
    
    return {'statusCode': 200}

def send_alert(resource_type, resource_id, rule_name):
    sns = boto3.client('sns')
    message = f"COMPLIANCE ALERT: {resource_type} {resource_id} failed rule {rule_name}"
    
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:compliance-alerts',
        Message=message,
        Subject='Config Compliance Violation'
    )
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. Configuration Recorder Not Starting

**Issue**: Configuration recorder fails to start
```
InsufficientDeliveryPolicyException: Insufficient permissions in the policy
```

**Possible Causes:**
- IAM role lacks necessary permissions
- S3 bucket policy doesn't allow Config access
- SNS topic policy restricts Config access

**Solutions:**
```bash
# Verify recorder status
aws configservice get-configuration-recorder-status

# Check IAM role permissions
aws iam get-role-policy --role-name aws-config-role --policy-name ConfigRolePolicy

# Verify S3 bucket policy
aws s3api get-bucket-policy --bucket my-config-bucket

# Test recorder configuration
aws configservice put-configuration-recorder --configuration-recorder file://recorder.json
```

#### 2. Config Rules Not Evaluating

**Issue**: Config rules show "No results recorded"

**Possible Causes:**
- No resources of the specified type exist
- Resources not being recorded by configuration recorder
- Rule scope doesn't match existing resources
- Lambda function errors (for custom rules)

**Solutions:**
```bash
# Check rule status
aws configservice describe-config-rules --config-rule-names my-rule

# Get rule evaluation results
aws configservice get-compliance-details-by-config-rule --config-rule-name my-rule

# Check if resources are being recorded
aws configservice list-discovered-resources --resource-type AWS::EC2::Instance

# For custom rules, check Lambda logs
aws logs describe-log-streams --log-group-name /aws/lambda/my-config-rule
```

#### 3. High Config Costs

**Issue**: Unexpected high Config charges

**Possible Causes:**
- Recording all supported resource types
- High-frequency rule evaluations
- Many configuration items being recorded
- Global resources recorded in multiple regions

**Solutions:**
```bash
# Review current recording configuration
aws configservice describe-configuration-recorders

# Check rule evaluation frequency
aws configservice describe-config-rules --query 'ConfigRules[*].{Name:ConfigRuleName,Frequency:MaximumExecutionFrequency}'

# Analyze cost breakdown
aws ce get-cost-and-usage \
    --time-period Start=2023-01-01,End=2023-01-31 \
    --granularity DAILY \
    --metrics BlendedCost \
    --group-by Type=DIMENSION,Key=USAGE_TYPE \
    --filter '{"Dimensions":{"Key":"SERVICE","Values":["AWS Config"]}}'
```

#### 4. Aggregator Data Issues

**Issue**: Configuration aggregator not showing data from all accounts

**Possible Causes:**
- Missing IAM permissions for cross-account access
- Accounts not properly configured in aggregator
- Regional configuration issues
- Network connectivity problems

**Solutions:**
```bash
# Check aggregator status
aws configservice describe-configuration-aggregators

# Verify aggregator authorization
aws configservice describe-aggregation-authorizations

# Check aggregator compliance
aws configservice get-aggregate-compliance-details-by-config-rule \
    --configuration-aggregator-name my-aggregator \
    --config-rule-name my-rule
```

### Debugging Tools

#### 1. AWS Config Console
- Configuration recorder status and settings
- Rule evaluation results and history
- Resource inventory and relationships
- Compliance dashboard and trends

#### 2. AWS CLI Debugging
```bash
# Enable debug output
aws configservice describe-config-rules --debug

# Get detailed rule information
aws configservice get-config-rule-evaluation-status --config-rule-names my-rule

# Check configuration history
aws configservice get-resource-config-history \
    --resource-type AWS::EC2::Instance \
    --resource-id i-1234567890abcdef0
```

#### 3. CloudWatch Logs Analysis
```bash
# Query Config service logs
aws logs start-query \
    --log-group-name '/aws/config/configuration-history' \
    --start-time $(date -d '1 hour ago' +%s) \
    --end-time $(date +%s) \
    --query-string 'fields @timestamp, @message | filter @message like /ERROR/'
```

---

## Best Practices

### Configuration Management

#### 1. Strategic Resource Selection
```json
{
  "recordingGroup": {
    "allSupported": false,
    "includeGlobalResourceTypes": true,
    "resourceTypes": [
      "AWS::EC2::Instance",
      "AWS::EC2::SecurityGroup",
      "AWS::EC2::VPC",
      "AWS::S3::Bucket",
      "AWS::IAM::Role",
      "AWS::IAM::Policy",
      "AWS::RDS::DBInstance"
    ]
  }
}
```

#### 2. Regional Strategy
- Record global resources in primary region only
- Use aggregators for multi-region visibility
- Consider compliance requirements by region
- Optimize costs through strategic recording

#### 3. Rule Implementation Strategy
```yaml
RuleDeploymentStrategy:
  Phase1_Critical:
    - root-access-key-check
    - mfa-enabled-for-iam-console-access
    - s3-bucket-public-read-prohibited
  Phase2_Security:
    - encrypted-volumes
    - rds-storage-encrypted
    - security-group-restrictions
  Phase3_Operational:
    - required-tags
    - approved-amis-by-id
    - instance-type-compliance
```

### Operational Excellence

#### 1. Automated Remediation Strategy
```json
{
  "RemediationStrategy": {
    "AutomaticRemediation": [
      "s3-bucket-public-read-prohibited",
      "security-group-unrestricted-access"
    ],
    "ManualRemediation": [
      "iam-policy-changes",
      "critical-resource-changes"
    ],
    "AlertOnly": [
      "informational-compliance",
      "cost-optimization-rules"
    ]
  }
}
```

#### 2. Compliance Monitoring
- Set up real-time alerts for critical violations
- Implement escalation procedures for non-compliance
- Regular compliance reporting and reviews
- Automated compliance dashboards

#### 3. Change Management Integration
```python
def config_change_handler(event, context):
    change_details = event['detail']
    
    # Integrate with change management system
    if is_unauthorized_change(change_details):
        create_incident_ticket(change_details)
        notify_security_team(change_details)
        
    # Update CMDB
    update_configuration_database(change_details)
```

### Security Best Practices

#### 1. Access Control
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/ConfigAdminRole"
      },
      "Action": [
        "config:Put*",
        "config:Delete*",
        "config:Start*",
        "config:Stop*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:role/ConfigReadOnlyRole"
      },
      "Action": [
        "config:Get*",
        "config:List*",
        "config:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

#### 2. Data Protection
- Encrypt Config data in S3 using KMS
- Use VPC endpoints for private communication
- Implement least privilege access
- Regular access reviews and audits

#### 3. Monitoring and Alerting
- Monitor Config service health
- Alert on configuration recorder failures
- Track compliance trend changes
- Monitor for unusual rule evaluation patterns

---

## SAA-C03 Exam Focus Areas

### Key Exam Topics

#### 1. Config Fundamentals
- **Question Types**: Basic setup, configuration recorder, delivery channels
- **Key Concepts**: Configuration items, resource relationships, supported resources
- **Study Focus**: What Config records, how it works, basic architecture

#### 2. Compliance Monitoring
- **Question Types**: Config rules, compliance evaluation, remediation
- **Key Concepts**: Managed vs custom rules, evaluation triggers, compliance states
- **Study Focus**: Rule types, when to use each, compliance scenarios

#### 3. Multi-Account Setup
- **Question Types**: Organization Config, aggregators, cross-account scenarios
- **Key Concepts**: Centralized vs distributed, aggregation, organization rules
- **Study Focus**: Architecture patterns, cost optimization, governance

#### 4. Integration Patterns
- **Question Types**: Config integration with other AWS services
- **Key Concepts**: S3, SNS, Lambda, Systems Manager integration
- **Study Focus**: Event-driven architectures, automated remediation

### Exam Scenarios and Solutions

#### Scenario 1: Compliance Monitoring Setup
*Question*: How to monitor S3 bucket configurations for compliance across multiple AWS accounts?

*Answer*:
1. Set up Config in each account with configuration recorder
2. Create organization Config aggregator in management account
3. Deploy organization-wide Config rules for S3 compliance
4. Set up automated remediation for non-compliant resources

```bash
# Deploy organization Config rule
aws configservice put-organization-config-rule \
    --organization-config-rule-name org-s3-bucket-public-read-prohibited \
    --organization-managed-rule-metadata '{
      "RuleIdentifier": "S3_BUCKET_PUBLIC_READ_PROHIBITED",
      "Description": "S3 buckets should not allow public read access"
    }'
```

#### Scenario 2: Change Tracking and Auditing
*Question*: How to track and audit security group changes across the organization?

*Answer*:
1. Enable Config recording for EC2 security groups
2. Set up EventBridge rules for security group changes
3. Create automated alerts for unauthorized changes
4. Implement approval workflow for security group modifications

```json
{
  "EventPattern": {
    "source": ["aws.config"],
    "detail-type": ["Config Configuration Item Change"],
    "detail": {
      "configurationItem": {
        "resourceType": ["AWS::EC2::SecurityGroup"]
      }
    }
  }
}
```

#### Scenario 3: Automated Compliance Remediation
*Question*: How to automatically remediate non-compliant EC2 instances that don't have required tags?

*Answer*:
1. Create Config rule to check for required tags
2. Set up automatic remediation using Systems Manager
3. Create custom SSM document to add missing tags
4. Configure rule to trigger remediation automatically

```json
{
  "RemediationConfiguration": {
    "ConfigRuleName": "required-tags",
    "TargetType": "SSM_DOCUMENT",
    "TargetId": "AWSConfigRemediation-AddTagsToResource",
    "Automatic": true,
    "Parameters": {
      "ResourceId": {
        "ResourceValue": {
          "Value": "RESOURCE_ID"
        }
      }
    }
  }
}
```

#### Scenario 4: Cost-Effective Multi-Region Setup
*Question*: How to set up Config across multiple regions while minimizing costs?

*Answer*:
1. Record global resources in primary region only
2. Use selective resource recording for non-critical regions
3. Set up aggregator for centralized view
4. Implement S3 lifecycle policies for historical data

```json
{
  "recordingGroup": {
    "allSupported": false,
    "includeGlobalResourceTypes": false,
    "resourceTypes": [
      "AWS::EC2::Instance",
      "AWS::EC2::SecurityGroup",
      "AWS::S3::Bucket"
    ]
  }
}
```

### Important Exam Points

#### 1. Configuration Recorder Limitations
- One configuration recorder per region per account
- Must be started to begin recording
- Can record all supported resources or specific types
- Global resources recorded in us-east-1 by default

#### 2. Config Rules Evaluation
- **Configuration change**: Triggered when resource changes
- **Periodic**: Scheduled evaluation (1, 3, 6, 12, 24 hours)
- **Hybrid**: Both change-triggered and periodic

#### 3. Compliance States
- **COMPLIANT**: Meets rule requirements
- **NON_COMPLIANT**: Violates rule requirements
- **NOT_APPLICABLE**: Rule doesn't apply
- **INSUFFICIENT_DATA**: Not enough data to evaluate

#### 4. Cost Factors
- Configuration items recorded: $0.003 per item
- Rule evaluations: $0.001 per evaluation
- Conformance pack evaluations: $0.0012 per evaluation
- S3 storage and requests charges apply

### Practice Questions Focus

1. **Setup and Configuration**: Configuration recorder, delivery channels, IAM roles
2. **Rule Types**: When to use managed vs custom rules, evaluation triggers
3. **Multi-Account**: Organization Config, aggregators, cross-account access
4. **Integration**: How Config works with other services for automation
5. **Compliance**: Remediation strategies, conformance packs
6. **Cost**: Optimization strategies, selective recording

### Key Formulas and Calculations

#### Cost Calculation
```
Monthly Config Cost = 
  (Configuration Items × $0.003) +
  (Rule Evaluations × $0.001) +
  (Conformance Pack Evaluations × $0.0012) +
  S3 Storage Costs +
  SNS Notification Costs
```

#### Rule Evaluation Frequency
```
Daily Evaluations = 
  (Resources × Rules × Evaluation Frequency)
  
Example: 100 resources × 10 rules × 4 evaluations/day = 4,000 evaluations/day
```

---

## Conclusion

AWS Config is essential for maintaining configuration compliance and governance in AWS environments. For the SAA-C03 certification, focus on:

1. **Understanding Config components** - Configuration recorder, delivery channels, rules
2. **Compliance monitoring strategies** - Rule types, evaluation triggers, remediation
3. **Multi-account architecture** - Organization Config, aggregators, centralized governance
4. **Integration patterns** - How Config works with other AWS services for automation
5. **Cost optimization** - Selective recording, efficient rule design, lifecycle management
6. **Security and compliance** - Encryption, access control, compliance frameworks

### Key Takeaways for the Exam
- **Config tracks configuration changes** - Not API calls (that's CloudTrail)
- **One configuration recorder per region** - But can aggregate across regions/accounts
- **Rules evaluate compliance** - Don't prevent non-compliant actions
- **Remediation can be automatic or manual** - Uses Systems Manager for automation
- **Organization Config enables governance** - Centralized rules and compliance monitoring
- **Cost is based on items and evaluations** - Optimize through selective recording

### Study Tips
1. **Hands-on practice**: Set up Config with different configurations
2. **Understand the components**: Know how recorder, rules, and remediation work together
3. **Practice rule creation**: Both managed and custom rules
4. **Learn integration patterns**: How Config works with other services
5. **Know the costs**: Understand pricing model and optimization strategies

---

*This guide covers the essential AWS Config concepts needed for the SAA-C03 certification. Focus on understanding the practical applications and architectural patterns for implementing configuration governance and compliance monitoring.*