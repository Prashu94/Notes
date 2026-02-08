# AWS Inspector - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [Key Concepts](#key-concepts)
3. [AWS Inspector Classic vs. Inspector V2](#aws-inspector-classic-vs-inspector-v2)
4. [Features and Capabilities](#features-and-capabilities)
5. [Integration with Other AWS Services](#integration-with-other-aws-services)
6. [Security and Compliance](#security-and-compliance)
7. [Pricing and Cost Optimization](#pricing-and-cost-optimization)
8. [Best Practices](#best-practices)
9. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
10. [SAA-C03 Exam Tips](#saa-c03-exam-tips)
11. [AWS CLI Commands Reference](#aws-cli-commands-reference)
12. [Hands-on Labs](#hands-on-labs)

## Overview

### What is AWS Inspector?
Amazon Inspector is an automated security assessment service that helps improve the security and compliance of applications deployed on AWS. It automatically assesses applications for exposure, vulnerabilities, and deviations from best practices.

### Key Features
- **Automated Security Assessments**: Continuous vulnerability assessments
- **Network Reachability Analysis**: Analyzes network configuration
- **Agent-based Assessments**: Deep inspection of EC2 instances
- **Integration with Security Hub**: Centralized security findings
- **Compliance Reporting**: Helps meet regulatory requirements

### Use Cases
- **Vulnerability Management**: Identify and remediate security vulnerabilities
- **Compliance Auditing**: Meet regulatory and organizational security standards
- **Security Monitoring**: Continuous security posture assessment
- **DevSecOps Integration**: Embed security into CI/CD pipelines

## Key Concepts

### Assessment Types

#### 1. Network Reachability Assessment
- Analyzes network configuration of EC2 instances
- Identifies unintended network accessibility
- No agent required
- Examines security groups, NACLs, route tables, and gateways

#### 2. Host Assessment (Inspector Classic)
- Requires Inspector agent on EC2 instances
- Analyzes the running operating system
- Identifies software vulnerabilities
- Checks for security best practices

#### 3. Container Image Assessment (Inspector V2)
- Scans container images for vulnerabilities
- Works with Amazon ECR
- Integrated into CI/CD pipelines
- No agent required for container scanning

#### 4. Lambda Function Assessment (Inspector V2)
- Scans Lambda functions for vulnerabilities
- Analyzes application code and dependencies
- Automatic scanning when functions are updated
- No configuration required

### Assessment Targets
- **EC2 Instances**: Virtual machines running in AWS
- **Container Images**: Images stored in Amazon ECR
- **Lambda Functions**: Serverless functions
- **Network Configuration**: VPC networking components

### Rules Packages
Pre-defined security rules for different assessment types:

#### Common Vulnerabilities and Exposures (CVE)
- Database of publicly known security vulnerabilities
- Regularly updated with new CVE entries
- Cross-references with installed software

#### Security Best Practices
- Checks for secure configuration
- Operating system hardening recommendations
- Network security configurations

#### Runtime Behavior Analysis
- Monitors application behavior during assessment
- Identifies potential security issues in runtime

## AWS Inspector Classic vs. Inspector V2

### Inspector Classic (Legacy)
```
Features:
├── Agent-based EC2 assessments
├── Network reachability assessments
├── Rules packages for different check types
├── Manual assessment runs
└── Basic integration with Security Hub
```

#### Limitations
- Manual agent installation and management
- Limited automation capabilities
- Separate console and APIs
- More complex setup and configuration

### Inspector V2 (Current)
```
Features:
├── Automatic EC2 scanning (agentless)
├── Container image vulnerability scanning
├── Lambda function scanning
├── Continuous monitoring
├── Enhanced Security Hub integration
├── Unified management console
└── Improved automation and APIs
```

#### Key Improvements
- **Agentless Operation**: No manual agent installation
- **Continuous Assessment**: Ongoing vulnerability monitoring
- **Broader Coverage**: EC2, containers, and Lambda functions
- **Better Integration**: Enhanced AWS service integration
- **Simplified Management**: Unified console experience

## Features and Capabilities

### Vulnerability Assessment

#### Software Vulnerability Detection
```yaml
Assessment Scope:
  Operating System: 
    - Package vulnerabilities
    - System configuration issues
    - Security patches status
  
  Application Dependencies:
    - Third-party library vulnerabilities
    - Runtime dependencies
    - Package manager vulnerabilities
  
  Container Images:
    - Base image vulnerabilities
    - Application layer vulnerabilities
    - Configuration issues
```

#### Severity Scoring
```
Critical: CVSS 9.0-10.0
  - Immediate attention required
  - High impact vulnerabilities
  - Remote code execution risks

High: CVSS 7.0-8.9
  - Significant security risk
  - Potential data exposure
  - Privilege escalation

Medium: CVSS 4.0-6.9
  - Moderate security risk
  - Limited impact vulnerabilities
  - Information disclosure

Low: CVSS 0.1-3.9
  - Minimal security risk
  - Low impact issues
  - Best practice violations

Informational: CVSS 0.0
  - Configuration recommendations
  - Security best practices
  - Non-exploitable findings
```

### Network Reachability Analysis

#### Assessment Scope
```
Network Components:
├── Security Groups
│   ├── Inbound rules analysis
│   ├── Outbound rules analysis
│   └── Port accessibility check
├── Network ACLs
│   ├── Subnet-level filtering
│   └── Rule precedence analysis
├── Route Tables
│   ├── Routing configuration
│   └── Internet accessibility
├── Internet Gateways
│   ├── Public subnet access
│   └── External connectivity
├── NAT Gateways/Instances
│   ├── Outbound internet access
│   └── Network translation
└── VPC Peering
    ├── Cross-VPC connectivity
    └── Route propagation
```

#### Reachability Findings
```yaml
Finding Types:
  UnintendedInternetAccess:
    Description: "Instance accessible from internet"
    Risk: "High - Potential unauthorized access"
    Remediation: "Restrict security group rules"
  
  UnusedSecurityGroupRules:
    Description: "Security group rules not utilized"
    Risk: "Medium - Unnecessary attack surface"
    Remediation: "Remove unused rules"
  
  OverlyPermissiveRules:
    Description: "Broad IP range permissions"
    Risk: "High - Increased attack surface"
    Remediation: "Implement least privilege"
```

### Container Security

#### ECR Integration
```python
# Example: ECR repository with Inspector scanning
{
    "repositoryName": "my-app",
    "imageScanningConfiguration": {
        "scanOnPush": True
    },
    "encryptionConfiguration": {
        "encryptionType": "AES256"
    }
}
```

#### Scan Triggers
- **Push-based Scanning**: Automatic scan on image push
- **Scheduled Scanning**: Regular vulnerability assessments
- **Manual Scanning**: On-demand vulnerability checks
- **API-triggered Scanning**: Programmatic scan initiation

### Lambda Function Security

#### Scanning Coverage
```yaml
Lambda Assessment:
  Code Vulnerabilities:
    - Application code analysis
    - Dependency vulnerabilities
    - Runtime-specific issues
  
  Configuration Issues:
    - IAM permissions analysis
    - Environment variable security
    - Network configuration
  
  Runtime Dependencies:
    - Package vulnerabilities
    - Library security issues
    - Version compatibility
```

## Integration with Other AWS Services

### AWS Security Hub

#### Findings Aggregation
```json
{
  "SchemaVersion": "2018-10-08",
  "Id": "arn:aws:inspector2:us-east-1:123456789012:finding/0123456789abcdef",
  "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/inspector",
  "GeneratorId": "aws-inspector2",
  "AwsAccountId": "123456789012",
  "Types": [
    "Software and Configuration Checks/Vulnerabilities/CVE"
  ],
  "Severity": {
    "Label": "HIGH",
    "Normalized": 70
  },
  "Title": "CVE-2021-44228 - Apache Log4j2 Remote Code Execution",
  "Description": "Apache Log4j2 versions 2.0-beta9 through 2.15.0 JNDI features...",
  "Remediation": {
    "Recommendation": {
      "Text": "Update to Log4j 2.17.1 or later",
      "Url": "https://logging.apache.org/log4j/2.x/security.html"
    }
  }
}
```

### AWS Systems Manager

#### Agent Management (Inspector Classic)
```bash
# Install Inspector agent via Systems Manager
aws ssm send-command \
  --document-name "AmazonInspector-ManageAWSAgent" \
  --parameters "operation=Install" \
  --targets "Key=tag:Environment,Values=Production"
```

#### Patch Management Integration
```yaml
Patch Baseline:
  OperatingSystem: "AMAZON_LINUX_2"
  ApprovalRules:
    - PatchFilters:
        - Key: "CLASSIFICATION"
          Values: ["Security", "Bugfix"]
        - Key: "SEVERITY"
          Values: ["Critical", "Important"]
      ApproveAfterDays: 7
```

### AWS Config

#### Configuration Compliance
```json
{
  "ConfigRuleName": "inspector-assessment-enabled",
  "Description": "Checks if Amazon Inspector assessment is enabled",
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "INSPECTOR_ENABLED"
  },
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  }
}
```

### Amazon EventBridge

#### Event-driven Automation
```python
# Example: EventBridge rule for Inspector findings
{
    "Rules": [{
        "Name": "InspectorCriticalFindings",
        "EventPattern": {
            "source": ["aws.inspector2"],
            "detail-type": ["Inspector2 Finding"],
            "detail": {
                "severity": ["CRITICAL"]
            }
        },
        "Targets": [{
            "Id": "1",
            "Arn": "arn:aws:lambda:us-east-1:123456789012:function:HandleCriticalFinding"
        }]
    }]
}
```

### AWS Lambda

#### Automated Remediation
```python
import boto3
import json

def lambda_handler(event, context):
    """
    Automated response to Inspector findings
    """
    inspector = boto3.client('inspector2')
    ec2 = boto3.client('ec2')
    
    # Parse Inspector finding
    finding = event['detail']
    instance_id = finding['resources'][0]['id']
    severity = finding['severity']
    
    if severity == 'CRITICAL':
        # Stop instance for critical vulnerabilities
        ec2.stop_instances(InstanceIds=[instance_id])
        
        # Create snapshot before patching
        volumes = ec2.describe_instances(
            InstanceIds=[instance_id]
        )['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        
        for volume in volumes:
            volume_id = volume['Ebs']['VolumeId']
            ec2.create_snapshot(
                VolumeId=volume_id,
                Description=f'Pre-patch snapshot for {instance_id}'
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Automated response completed')
    }
```

## Security and Compliance

### Compliance Frameworks

#### SOC 2 Type II
```yaml
Inspector Contributions:
  Security Monitoring:
    - Continuous vulnerability assessment
    - Security configuration validation
    - Access control verification
  
  Change Management:
    - Configuration drift detection
    - Security impact assessment
    - Automated compliance reporting
```

#### PCI DSS
```yaml
Requirements Addressed:
  Requirement_6:
    Description: "Develop and maintain secure systems"
    Inspector_Role: "Vulnerability scanning and assessment"
  
  Requirement_11:
    Description: "Regularly test security systems"
    Inspector_Role: "Automated security testing"
```

#### HIPAA
```yaml
Safeguards:
  Technical_Safeguards:
    - Access control validation
    - Audit controls implementation
    - Integrity monitoring
    - Transmission security
```

### Data Protection

#### Encryption at Rest
```json
{
  "EncryptionConfiguration": {
    "EncryptionType": "KMS",
    "KmsKeyId": "arn:aws:kms:us-east-1:123456789012:key/12345678-1234-1234-1234-123456789012"
  }
}
```

#### Encryption in Transit
- All API communications use TLS 1.2+
- Agent communications encrypted
- Assessment data encrypted during transmission
- Cross-region replication encryption

### Access Control

#### IAM Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "inspector2:ListFindings",
        "inspector2:GetFindings",
        "inspector2:DescribeOrganizationConfiguration"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "aws:RequestedRegion": ["us-east-1", "us-west-2"]
        }
      }
    }
  ]
}
```

#### Resource-based Policies
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "CrossAccountAccess",
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::SECURITY-ACCOUNT:root"
      },
      "Action": "inspector2:GetFindings",
      "Resource": "*"
    }
  ]
}
```

## Pricing and Cost Optimization

### Pricing Model

#### Inspector V2 Pricing (as of 2024)
```yaml
EC2_Scanning:
  Price: "$0.15 per instance per month"
  Billing: "Per instance scanned"
  Minimum: "No minimum usage"

Container_Scanning:
  Initial_Scan: "$0.09 per image"
  Rescan: "$0.01 per image"
  Frequency: "On-demand or scheduled"

Lambda_Scanning:
  Price: "$0.30 per 100,000 function invocations scanned"
  Billing: "Per function assessment"
```

### Cost Optimization Strategies

#### 1. Selective Scanning
```python
# Example: Tag-based scanning strategy
{
    "ResourceGroupArn": "arn:aws:resource-groups:us-east-1:123456789012:group/production-instances",
    "ResourceType": "ECR_CONTAINER_IMAGE",
    "ScanConfiguration": {
        "ScanOnPush": False,
        "ScheduledScan": {
            "Frequency": "WEEKLY"
        }
    }
}
```

#### 2. Assessment Scheduling
```yaml
Optimization Strategy:
  Production Environment:
    Frequency: "Daily scanning"
    Priority: "All severity levels"
  
  Development Environment:
    Frequency: "Weekly scanning"
    Priority: "High and Critical only"
  
  Testing Environment:
    Frequency: "On-demand scanning"
    Priority: "Critical only"
```

#### 3. Lifecycle Management
```python
# Automated cleanup of old assessment data
import boto3
from datetime import datetime, timedelta

def cleanup_old_assessments():
    inspector = boto3.client('inspector2')
    
    # Delete assessments older than 90 days
    cutoff_date = datetime.now() - timedelta(days=90)
    
    # List and delete old assessment runs
    old_runs = inspector.list_assessment_runs(
        filter={
            'completedTimeRange': {
                'endTime': cutoff_date
            }
        }
    )
    
    for run in old_runs['assessmentRunArns']:
        inspector.delete_assessment_run(
            assessmentRunArn=run
        )
```

## Best Practices

### Deployment Best Practices

#### 1. Multi-Account Strategy
```yaml
Account Structure:
  Security Account:
    Role: "Central security monitoring"
    Resources: "Inspector delegated administrator"
  
  Production Account:
    Role: "Production workloads"
    Resources: "Inspector member account"
  
  Development Account:
    Role: "Development workloads"
    Resources: "Inspector member account"
```

#### 2. Assessment Strategy
```python
# Comprehensive assessment configuration
assessment_config = {
    "assessmentTargetArn": "arn:aws:inspector:us-east-1:123456789012:target/0-abc123def",
    "assessmentTemplateArn": "arn:aws:inspector:us-east-1:123456789012:template/0-def456ghi",
    "assessmentRunName": f"Security-Assessment-{datetime.now().strftime('%Y-%m-%d')}",
    "durationInSeconds": 3600  # 1 hour assessment
}
```

### Security Best Practices

#### 1. Least Privilege Access
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "inspector2:ListFindings"
      ],
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "inspector2:FindingSeverity": ["CRITICAL", "HIGH"]
        }
      }
    }
  ]
}
```

#### 2. Finding Management
```python
# Automated finding prioritization
def prioritize_findings(findings):
    """
    Prioritize Inspector findings based on severity and exploitability
    """
    priority_matrix = {
        'CRITICAL': {
            'network_reachable': 1,  # Highest priority
            'not_network_reachable': 2
        },
        'HIGH': {
            'network_reachable': 3,
            'not_network_reachable': 4
        },
        'MEDIUM': {
            'network_reachable': 5,
            'not_network_reachable': 6
        }
    }
    
    prioritized_findings = []
    for finding in findings:
        severity = finding['severity']
        network_reachable = finding.get('networkReachabilityDetails', {}).get('networkPath', {}).get('steps', [])
        reachability = 'network_reachable' if network_reachable else 'not_network_reachable'
        
        priority = priority_matrix.get(severity, {}).get(reachability, 10)
        finding['priority'] = priority
        prioritized_findings.append(finding)
    
    return sorted(prioritized_findings, key=lambda x: x['priority'])
```

#### 3. Remediation Workflow
```yaml
Remediation Process:
  1_Triage:
    - Severity assessment
    - Impact analysis
    - Business criticality review
  
  2_Planning:
    - Remediation strategy
    - Change management approval
    - Rollback plan preparation
  
  3_Implementation:
    - Patch deployment
    - Configuration changes
    - Verification testing
  
  4_Validation:
    - Re-scan verification
    - Functional testing
    - Security validation
```

### Operational Best Practices

#### 1. Automation Integration
```python
# CI/CD pipeline integration
def integrate_inspector_with_pipeline():
    """
    Integrate Inspector scanning into CI/CD pipeline
    """
    pipeline_config = {
        'stages': [
            {
                'name': 'build',
                'actions': ['build', 'test']
            },
            {
                'name': 'security-scan',
                'actions': [
                    {
                        'name': 'inspector-scan',
                        'actionTypeId': {
                            'category': 'Invoke',
                            'owner': 'AWS',
                            'provider': 'Lambda',
                            'version': '1'
                        },
                        'configuration': {
                            'FunctionName': 'trigger-inspector-scan'
                        }
                    }
                ]
            },
            {
                'name': 'deploy',
                'actions': ['deploy-to-staging']
            }
        ]
    }
    return pipeline_config
```

#### 2. Monitoring and Alerting
```python
# CloudWatch integration for Inspector metrics
import boto3

def setup_inspector_monitoring():
    """
    Setup CloudWatch monitoring for Inspector
    """
    cloudwatch = boto3.client('cloudwatch')
    
    # Create custom metric for critical findings
    cloudwatch.put_metric_alarm(
        AlarmName='InspectorCriticalFindings',
        ComparisonOperator='GreaterThanThreshold',
        EvaluationPeriods=1,
        MetricName='CriticalFindings',
        Namespace='AWS/Inspector2',
        Period=300,
        Statistic='Sum',
        Threshold=0.0,
        ActionsEnabled=True,
        AlarmActions=[
            'arn:aws:sns:us-east-1:123456789012:security-alerts'
        ],
        AlarmDescription='Alert on critical Inspector findings'
    )
```

## Monitoring and Troubleshooting

### CloudWatch Metrics

#### Available Metrics
```yaml
Metrics:
  FindingCounts:
    - TotalFindings
    - CriticalFindings
    - HighFindings
    - MediumFindings
    - LowFindings
  
  AssessmentMetrics:
    - AssessmentDuration
    - AssessmentSuccess
    - AssessmentFailure
  
  ResourceMetrics:
    - InstancesScanned
    - ImagesScanned
    - FunctionsScanned
```

#### Custom Metrics
```python
# Publishing custom Inspector metrics
import boto3

def publish_custom_metrics(findings):
    """
    Publish custom metrics based on Inspector findings
    """
    cloudwatch = boto3.client('cloudwatch')
    
    # Count findings by severity
    severity_counts = {}
    for finding in findings:
        severity = finding['severity']
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Publish metrics
    for severity, count in severity_counts.items():
        cloudwatch.put_metric_data(
            Namespace='Custom/Inspector',
            MetricData=[
                {
                    'MetricName': f'{severity}Findings',
                    'Value': count,
                    'Unit': 'Count'
                }
            ]
        )
```

### Troubleshooting Common Issues

#### 1. Agent Installation Issues (Inspector Classic)
```bash
# Check agent status
sudo service awsagent status

# Restart agent
sudo service awsagent restart

# Check agent logs
sudo tail -f /var/log/aws/amazoncloudwatch-agent/amazoncloudwatch-agent.log
```

#### 2. Network Connectivity Issues
```python
# Diagnose network connectivity
def diagnose_connectivity(instance_id):
    """
    Diagnose Inspector connectivity issues
    """
    ec2 = boto3.client('ec2')
    
    # Check security groups
    instance = ec2.describe_instances(InstanceIds=[instance_id])
    security_groups = instance['Reservations'][0]['Instances'][0]['SecurityGroups']
    
    for sg in security_groups:
        sg_details = ec2.describe_security_groups(GroupIds=[sg['GroupId']])
        print(f"Security Group: {sg['GroupId']}")
        print("Outbound Rules:")
        for rule in sg_details['SecurityGroups'][0]['IpPermissionsEgress']:
            print(f"  Protocol: {rule.get('IpProtocol')}")
            print(f"  Port Range: {rule.get('FromPort')}-{rule.get('ToPort')}")
```

#### 3. Permission Issues
```json
{
  "Error": {
    "Code": "AccessDenied",
    "Message": "User is not authorized to perform: inspector2:ListFindings"
  },
  "Resolution": {
    "Action": "Add required permissions to IAM policy",
    "RequiredPermissions": [
      "inspector2:ListFindings",
      "inspector2:GetFindings",
      "inspector2:DescribeOrganizationConfiguration"
    ]
  }
}
```

### Log Analysis

#### CloudTrail Integration
```python
# Analyze Inspector API calls via CloudTrail
def analyze_inspector_api_calls():
    """
    Analyze Inspector API usage patterns
    """
    cloudtrail = boto3.client('cloudtrail')
    
    # Lookup Inspector API events
    events = cloudtrail.lookup_events(
        LookupAttributes=[
            {
                'AttributeKey': 'EventSource',
                'AttributeValue': 'inspector2.amazonaws.com'
            }
        ],
        StartTime=datetime.now() - timedelta(days=7)
    )
    
    api_usage = {}
    for event in events['Events']:
        event_name = event['EventName']
        api_usage[event_name] = api_usage.get(event_name, 0) + 1
    
    return api_usage
```

## SAA-C03 Exam Tips

### Key Exam Topics

#### 1. Security Assessment Capabilities
```yaml
Exam Focus Areas:
  Vulnerability Assessment:
    - Software vulnerability detection
    - Configuration assessment
    - Compliance checking
  
  Network Security:
    - Reachability analysis
    - Security group validation
    - Network path analysis
  
  Container Security:
    - Image vulnerability scanning
    - Registry integration
    - CI/CD pipeline integration
```

#### 2. Integration Scenarios
```yaml
Common Exam Scenarios:
  Multi-Account Setup:
    Question: "How to centrally manage Inspector across accounts?"
    Answer: "Use AWS Organizations with delegated administrator"
  
  Compliance Requirements:
    Question: "How to meet PCI DSS scanning requirements?"
    Answer: "Implement regular Inspector assessments with automated reporting"
  
  Cost Optimization:
    Question: "How to minimize Inspector costs?"
    Answer: "Use selective scanning based on criticality and scheduling"
```

### Scenario-Based Questions

#### Scenario 1: Multi-Tier Application Security
```yaml
Context:
  Architecture: "Web tier, App tier, Database tier"
  Requirement: "Comprehensive security assessment"
  Constraints: "Minimal performance impact"

Solution:
  Inspector_V2:
    - Enable EC2 scanning for all tiers
    - Configure container scanning for containerized components
    - Set up network reachability analysis
  
  Integration:
    - Security Hub for centralized findings
    - EventBridge for automated responses
    - Lambda for remediation workflows
```

#### Scenario 2: Compliance Automation
```yaml
Context:
  Industry: "Healthcare (HIPAA compliance)"
  Requirement: "Automated compliance monitoring"
  Frequency: "Continuous monitoring required"

Solution:
  Assessment_Strategy:
    - Daily vulnerability scans
    - Immediate critical finding alerts
    - Automated compliance reporting
  
  Automation:
    - EventBridge rules for findings
    - Lambda for automated responses
    - Config for compliance tracking
```

### Common Exam Mistakes to Avoid

1. **Confusing Inspector Classic with Inspector V2**
   - Remember V2 is agentless for EC2
   - V2 includes container and Lambda scanning

2. **Overlooking Network Reachability**
   - Inspector analyzes network configuration
   - No agent required for network assessment

3. **Misunderstanding Pricing Model**
   - V2 pricing is per-resource scanned
   - Different pricing for EC2, containers, and Lambda

4. **Ignoring Integration Capabilities**
   - Inspector works with Security Hub
   - EventBridge enables automation
   - Config provides compliance tracking

## AWS CLI Commands Reference

### 1. Enable Inspector

#### Enable Inspector V2
```bash
# Enable Inspector V2 for the account
aws inspector2 enable \
  --resource-types EC2 ECR LAMBDA

# Enable Inspector V2 for specific resource types
aws inspector2 enable \
  --resource-types EC2 ECR

# Enable Inspector V2 with account IDs (for delegated administrator)
aws inspector2 enable \
  --resource-types EC2 ECR LAMBDA \
  --account-ids "111122223333" "444455556666"

# Check enablement status
aws inspector2 batch-get-account-status \
  --account-ids "$(aws sts get-caller-identity --query Account --output text)"
```

#### Disable Inspector V2
```bash
# Disable Inspector V2 for specific resource types
aws inspector2 disable \
  --resource-types ECR

# Disable all resource types
aws inspector2 disable \
  --resource-types EC2 ECR LAMBDA

# Disable for specific accounts (delegated administrator)
aws inspector2 disable \
  --resource-types EC2 ECR LAMBDA \
  --account-ids "111122223333" "444455556666"
```

### 2. Create Assessment Targets (Inspector Classic)

#### Create Assessment Target
```bash
# Create assessment target with all instances in VPC
aws inspector create-assessment-target \
  --assessment-target-name "Production-WebServers" \
  --resource-group-arn arn:aws:inspector:us-east-1:123456789012:resourcegroup/0-AbCdEfGh

# Create resource group first
aws inspector create-resource-group \
  --resource-group-tags key=Environment,value=Production key=Role,value=WebServer

# Then create assessment target with the resource group
RESGROUP_ARN=$(aws inspector create-resource-group \
  --resource-group-tags key=Environment,value=Production \
  --query 'resourceGroupArn' \
  --output text)

aws inspector create-assessment-target \
  --assessment-target-name "Production-Servers" \
  --resource-group-arn $RESGROUP_ARN
```

#### List and Describe Assessment Targets
```bash
# List all assessment targets
aws inspector list-assessment-targets

# Describe specific assessment target
aws inspector describe-assessment-targets \
  --assessment-target-arns arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh

# List assessment targets with filtering
aws inspector list-assessment-targets \
  --filter '{"assessmentTargetNamePattern": "Production*"}'
```

### 3. Create Assessment Templates (Inspector Classic)

#### Create Assessment Template
```bash
# Get rules package ARNs for your region
REGION="us-east-1"

# Common Vulnerabilities and Exposures
CVE_RULES="arn:aws:inspector:$REGION:316112463485:rulespackage/0-gEjTy7T7"

# Security Best Practices
SBP_RULES="arn:aws:inspector:$REGION:316112463485:rulespackage/0-R01qwB5Q"

# Network Reachability
NETWORK_RULES="arn:aws:inspector:$REGION:316112463485:rulespackage/0-PmNV0Tcd"

# CIS Operating System Security Configuration Benchmarks
CIS_RULES="arn:aws:inspector:$REGION:316112463485:rulespackage/0-rExsr2X8"

# Create assessment template
aws inspector create-assessment-template \
  --assessment-target-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --assessment-template-name "Weekly-Security-Assessment" \
  --duration-in-seconds 3600 \
  --rules-package-arns $CVE_RULES $SBP_RULES $NETWORK_RULES $CIS_RULES

# Create template with user attributes for tagging
aws inspector create-assessment-template \
  --assessment-target-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --assessment-template-name "Production-Assessment" \
  --duration-in-seconds 3600 \
  --rules-package-arns $CVE_RULES $SBP_RULES \
  --user-attributes-for-findings key=Environment,value=Production key=Team,value=Security
```

#### List and Describe Assessment Templates
```bash
# List all assessment templates
aws inspector list-assessment-templates

# List templates for specific target
aws inspector list-assessment-templates \
  --assessment-target-arns arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh

# Describe assessment template
aws inspector describe-assessment-templates \
  --assessment-template-arns arn:aws:inspector:us-east-1:123456789012:template/0-XyZ123Ab
```

### 4. Start Assessment Runs

#### Start Assessment Run (Inspector Classic)
```bash
# Start assessment run from template
aws inspector start-assessment-run \
  --assessment-template-arn arn:aws:inspector:us-east-1:123456789012:template/0-XyZ123Ab \
  --assessment-run-name "Manual-Run-$(date +%Y%m%d-%H%M%S)"

# Start assessment run with custom name
RUN_ARN=$(aws inspector start-assessment-run \
  --assessment-template-arn arn:aws:inspector:us-east-1:123456789012:template/0-XyZ123Ab \
  --assessment-run-name "Weekly-Security-Scan-Week-$(date +%V)" \
  --query 'assessmentRunArn' \
  --output text)

echo "Started assessment run: $RUN_ARN"
```

#### Monitor Assessment Run Status
```bash
# Describe assessment run
aws inspector describe-assessment-runs \
  --assessment-run-arns $RUN_ARN

# Get assessment run state
STATE=$(aws inspector describe-assessment-runs \
  --assessment-run-arns $RUN_ARN \
  --query 'assessmentRuns[0].state' \
  --output text)

echo "Assessment run state: $STATE"

# Wait for assessment run to complete
while [ "$STATE" != "COMPLETED" ] && [ "$STATE" != "FAILED" ]; do
  sleep 30
  STATE=$(aws inspector describe-assessment-runs \
    --assessment-run-arns $RUN_ARN \
    --query 'assessmentRuns[0].state' \
    --output text)
  echo "Current state: $STATE"
done
```

#### Stop Assessment Run
```bash
# Stop a running assessment
aws inspector stop-assessment-run \
  --assessment-run-arn $RUN_ARN
```

### 5. List Findings (Inspector V2)

#### List All Findings
```bash
# List findings with basic filters
aws inspector2 list-findings \
  --max-results 100

# List findings sorted by severity
aws inspector2 list-findings \
  --max-results 50 \
  --sort-criteria '{"field": "SEVERITY", "sortOrder": "DESC"}'

# List findings with pagination
aws inspector2 list-findings \
  --max-results 100 \
  --next-token <token-from-previous-call>
```

#### Filter Findings by Criteria
```bash
# List critical and high severity findings
aws inspector2 list-findings \
  --filter-criteria '{
    "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
    "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
  }'

# List findings for specific EC2 instances
aws inspector2 list-findings \
  --filter-criteria '{
    "resourceType": [{"comparison": "EQUALS", "value": "AWS_EC2_INSTANCE"}],
    "ec2InstanceImageId": [{"comparison": "EQUALS", "value": "ami-0abcdef1234567890"}]
  }'

# List findings for ECR images
aws inspector2 list-findings \
  --filter-criteria '{
    "resourceType": [{"comparison": "EQUALS", "value": "AWS_ECR_CONTAINER_IMAGE"}],
    "ecrRepositoryName": [{"comparison": "EQUALS", "value": "my-app-repo"}]
  }'

# List findings with available fixes
aws inspector2 list-findings \
  --filter-criteria '{
    "fixAvailable": [{"comparison": "EQUALS", "value": "YES"}],
    "severity": [{"comparison": "EQUALS", "value": "HIGH"}]
  }'

# List Lambda findings
aws inspector2 list-findings \
  --filter-criteria '{
    "resourceType": [{"comparison": "EQUALS", "value": "AWS_LAMBDA_FUNCTION"}],
    "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
  }'
```

#### Filter by Finding Type and CVE
```bash
# List findings by vulnerability ID
aws inspector2 list-findings \
  --filter-criteria '{
    "vulnerabilityId": [{"comparison": "EQUALS", "value": "CVE-2021-44228"}]
  }'

# List package vulnerability findings
aws inspector2 list-findings \
  --filter-criteria '{
    "findingType": [{"comparison": "EQUALS", "value": "PACKAGE_VULNERABILITY"}]
  }'

# List findings by EPSS score (exploit prediction)
aws inspector2 list-findings \
  --filter-criteria '{
    "epssScore": [{"lowerInclusive": 0.8, "upperInclusive": 1.0}]
  }'
```

### 6. Describe Findings

#### Get Detailed Finding Information (Inspector V2)
```bash
# Describe specific findings
aws inspector2 batch-get-findings \
  --finding-arns \
    "arn:aws:inspector2:us-east-1:123456789012:finding/abcd1234-ef56-7890-ghij-klmn12345678" \
    "arn:aws:inspector2:us-east-1:123456789012:finding/wxyz5678-ab90-1234-cdef-ghij56789012"

# Get finding details with JQ for parsing
aws inspector2 batch-get-findings \
  --finding-arns "arn:aws:inspector2:us-east-1:123456789012:finding/abcd1234-ef56-7890-ghij-klmn12345678" \
  | jq '.findings[] | {title: .title, severity: .severity, status: .status, description: .description}'
```

#### Describe Findings (Inspector Classic)
```bash
# List findings for assessment run
aws inspector list-findings \
  --assessment-run-arns $RUN_ARN

# Describe specific findings
FINDING_ARN="arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh/template/0-XyZ123Ab/run/0-PqRs456Tu/finding/0-VwXyZ789"

aws inspector describe-findings \
  --finding-arns $FINDING_ARN

# Describe findings with locale
aws inspector describe-findings \
  --finding-arns $FINDING_ARN \
  --locale EN_US

# List findings filtered by severity
aws inspector list-findings \
  --assessment-run-arns $RUN_ARN \
  --filter '{"severities": ["High", "Medium"]}'

# List findings filtered by attributes
aws inspector list-findings \
  --assessment-run-arns $RUN_ARN \
  --filter '{
    "attributes": [
      {"key": "SEVERITY", "value": "High"},
      {"key": "RULES_PACKAGE_ARN", "value": "'$CVE_RULES'"}
    ]
  }'
```

### 7. Get Assessment Reports

#### Generate Assessment Report (Inspector Classic)
```bash
# Generate HTML report
aws inspector get-assessment-report \
  --assessment-run-arn $RUN_ARN \
  --report-file-format HTML \
  --report-type FULL

# Generate PDF report
aws inspector get-assessment-report \
  --assessment-run-arn $RUN_ARN \
  --report-file-format PDF \
  --report-type FINDING

# Check report generation status
REPORT_ARN=$(aws inspector get-assessment-report \
  --assessment-run-arn $RUN_ARN \
  --report-file-format HTML \
  --report-type FULL \
  --query 'url' \
  --output text)

echo "Report URL: $REPORT_ARN"

# Download report
wget -O assessment-report.html "$REPORT_ARN"
```

#### Export Findings (Inspector V2)
```bash
# Create finding report (exports to S3)
aws inspector2 create-findings-report \
  --report-format JSON \
  --s3-destination '{"bucketName": "my-inspector-reports", "keyPrefix": "reports/"}' \
  --filter-criteria '{
    "severity": [{"comparison": "EQUALS", "value": "CRITICAL"}],
    "findingStatus": [{"comparison": "EQUALS", "value": "ACTIVE"}]
  }'

# Create CSV report
aws inspector2 create-findings-report \
  --report-format CSV \
  --s3-destination '{"bucketName": "my-inspector-reports", "keyPrefix": "reports/", "kmsKeyArn": "arn:aws:kms:us-east-1:123456789012:key/abc-123"}'

# Get report status
aws inspector2 get-findings-report-status \
  --report-id <report-id>
```

### 8. Rules Packages (Inspector Classic)

#### List Available Rules Packages
```bash
# List all rules packages available in region
aws inspector list-rules-packages

# Describe rules package
aws inspector describe-rules-packages \
  --rules-package-arns $CVE_RULES

# List all rules packages with descriptions
for arn in $(aws inspector list-rules-packages --query 'rulesPackageArns[]' --output text); do
  echo "Rules Package: $arn"
  aws inspector describe-rules-packages --rules-package-arns $arn
  echo "---"
done
```

#### Common Rules Package ARNs by Region
```bash
# US East (N. Virginia) - us-east-1
CVE_US_EAST_1="arn:aws:inspector:us-east-1:316112463485:rulespackage/0-gEjTy7T7"
CIS_US_EAST_1="arn:aws:inspector:us-east-1:316112463485:rulespackage/0-rExsr2X8"
SECURITY_US_EAST_1="arn:aws:inspector:us-east-1:316112463485:rulespackage/0-R01qwB5Q"
RUNTIME_US_EAST_1="arn:aws:inspector:us-east-1:316112463485:rulespackage/0-gBONHN9h"

# US West (Oregon) - us-west-2
CVE_US_WEST_2="arn:aws:inspector:us-west-2:758058086616:rulespackage/0-9hgA516p"
CIS_US_WEST_2="arn:aws:inspector:us-west-2:758058086616:rulespackage/0-H5hpSawc"
SECURITY_US_WEST_2="arn:aws:inspector:us-west-2:758058086616:rulespackage/0-JJOtZiqQ"
RUNTIME_US_WEST_2="arn:aws:inspector:us-west-2:758058086616:rulespackage/0-vg5GGHSD"

# EU (Ireland) - eu-west-1
CVE_EU_WEST_1="arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-ubA5XvBh"
CIS_EU_WEST_1="arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-sJBhCr0F"
SECURITY_EU_WEST_1="arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-SnojL3Z6"
RUNTIME_EU_WEST_1="arn:aws:inspector:eu-west-1:357557129151:rulespackage/0-lLmwe1zd"
```

### 9. Tags Management

#### Tag Resources (Inspector V2)
```bash
# Tag specific findings
aws inspector2 tag-resource \
  --resource-arn "arn:aws:inspector2:us-east-1:123456789012:finding/abcd1234-ef56-7890-ghij-klmn12345678" \
  --tags Team=Security,Priority=High,Environment=Production

# List tags for resource
aws inspector2 list-tags-for-resource \
  --resource-arn "arn:aws:inspector2:us-east-1:123456789012:finding/abcd1234-ef56-7890-ghij-klmn12345678"

# Untag resource
aws inspector2 untag-resource \
  --resource-arn "arn:aws:inspector2:us-east-1:123456789012:finding/abcd1234-ef56-7890-ghij-klmn12345678" \
  --tag-keys Priority Environment
```

#### Set Tags for Assessment Resources (Inspector Classic)
```bash
# Set tags for assessment template
aws inspector set-tags-for-resource \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:template/0-XyZ123Ab \
  --tags key=Environment,value=Production key=Schedule,value=Weekly

# Set tags for assessment target
aws inspector set-tags-for-resource \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --tags key=Department,value=IT key=CostCenter,value=CC001

# Set tags for assessment run
aws inspector set-tags-for-resource \
  --resource-arn $RUN_ARN \
  --tags key=RunType,value=Manual key=Requester,value=SecurityTeam
```

#### List Tags (Inspector Classic)
```bash
# List tags for assessment template
aws inspector list-tags-for-resource \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:template/0-XyZ123Ab

# List tags for assessment target
aws inspector list-tags-for-resource \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh

# List tags for assessment run
aws inspector list-tags-for-resource \
  --resource-arn $RUN_ARN
```

### 10. Additional Commands

#### Subscription to Findings (Inspector Classic)
```bash
# Subscribe to SNS topic for findings
aws inspector subscribe-to-event \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --event ASSESSMENT_RUN_COMPLETED \
  --topic-arn arn:aws:sns:us-east-1:123456789012:inspector-notifications

# Subscribe to other events
aws inspector subscribe-to-event \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --event FINDING_REPORTED \
  --topic-arn arn:aws:sns:us-east-1:123456789012:inspector-findings

# List event subscriptions
aws inspector list-event-subscriptions \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh

# Unsubscribe from event
aws inspector unsubscribe-from-event \
  --resource-arn arn:aws:inspector:us-east-1:123456789012:target/0-AbCdEfGh \
  --event ASSESSMENT_RUN_COMPLETED \
  --topic-arn arn:aws:sns:us-east-1:123456789012:inspector-notifications
```

#### Coverage Statistics (Inspector V2)
```bash
# Get coverage statistics
aws inspector2 list-coverage \
  --max-results 100

# Get coverage for specific resource type
aws inspector2 list-coverage \
  --filter-criteria '{
    "resourceType": [{"comparison": "EQUALS", "value": "AWS_EC2_INSTANCE"}]
  }'

# Get coverage statistics summary
aws inspector2 list-coverage-statistics \
  --group-by RESOURCE_TYPE

# Get account coverage details
aws inspector2 batch-get-account-status \
  --account-ids "$(aws sts get-caller-identity --query Account --output text)"
```

#### Suppression Rules (Inspector V2)
```bash
# Create suppression rule
aws inspector2 create-filter \
  --name "Suppress-Test-Environment" \
  --description "Suppress findings from test environment" \
  --action SUPPRESS \
  --filter-criteria '{
    "resourceTags": [{"comparison": "EQUALS", "key": "Environment", "value": "test"}]
  }'

# List filters/suppression rules
aws inspector2 list-filters

# Update filter
aws inspector2 update-filter \
  --filter-arn "arn:aws:inspector2:us-east-1:123456789012:owner/123456789012/filter/abcdef123456" \
  --action SUPPRESS \
  --filter-criteria '{
    "severity": [{"comparison": "EQUALS", "value": "LOW"}]
  }'

# Delete filter
aws inspector2 delete-filter \
  --filter-arn "arn:aws:inspector2:us-east-1:123456789012:owner/123456789012/filter/abcdef123456"
```

#### Member Account Management (Inspector V2)
```bash
# Enable delegated administrator
aws inspector2 enable-delegated-admin-account \
  --delegated-admin-account-id "123456789012"

# Disable delegated administrator
aws inspector2 disable-delegated-admin-account \
  --delegated-admin-account-id "123456789012"

# Associate member accounts
aws inspector2 associate-member \
  --account-id "111122223333"

# Disassociate member accounts
aws inspector2 disassociate-member \
  --account-id "111122223333"

# List members
aws inspector2 list-members

# Get member details
aws inspector2 get-member \
  --account-id "111122223333"
```

#### Update Organization Configuration (Inspector V2)
```bash
# Update organization configuration to auto-enable
aws inspector2 update-organization-configuration \
  --auto-enable '{"ec2": true, "ecr": true, "lambda": true}'

# Describe organization configuration
aws inspector2 describe-organization-configuration
```

## Hands-on Labs

### Lab 1: Setting Up Inspector V2

#### Prerequisites
- AWS Account with appropriate permissions
- EC2 instances in multiple availability zones
- Container images in Amazon ECR
- Lambda functions deployed

#### Step 1: Enable Inspector V2
```bash
# Enable Inspector V2 using AWS CLI
aws inspector2 enable \
  --account-ids 123456789012 \
  --resource-types ECR_CONTAINER_IMAGE EC2_INSTANCE LAMBDA_FUNCTION
```

#### Step 2: Configure Assessment Scope
```python
import boto3

def configure_inspector_scope():
    """
    Configure Inspector assessment scope
    """
    inspector = boto3.client('inspector2')
    
    # Enable scanning for specific resource types
    response = inspector.batch_update_member_ec2_deep_inspection_status(
        accountIds=[
            {
                'accountId': '123456789012',
                'activateDeepInspection': True
            }
        ]
    )
    
    return response
```

#### Step 3: Create Assessment Filter
```python
def create_assessment_filter():
    """
    Create filter to focus on critical findings
    """
    inspector = boto3.client('inspector2')
    
    filter_criteria = {
        'findingArn': [],
        'awsAccountId': [],
        'findingType': ['PACKAGE_VULNERABILITY'],
        'severity': ['CRITICAL', 'HIGH'],
        'firstObservedAt': [],
        'lastObservedAt': [],
        'updatedAt': [],
        'findingStatus': ['ACTIVE'],
        'title': [],
        'inspectorScore': [],
        'vendorSeverity': [],
        'vulnerabilityId': [],
        'vulnerabilitySource': [],
        'vulnerablePackages': [],
        'relatedVulnerabilities': [],
        'fixAvailable': ['YES'],
        'lambdaFunctionName': [],
        'lambdaFunctionLayers': [],
        'lambdaFunctionRuntime': [],
        'ecrRepositoryName': [],
        'ecrImageArchitecture': [],
        'ecrImageHash': [],
        'ecrImageTags': [],
        'ec2InstanceImageId': [],
        'ec2InstanceVpcId': [],
        'ec2InstanceSubnetId': []
    }
    
    response = inspector.create_filter(
        action='NONE',  # Don't suppress findings
        description='Filter for critical and high severity findings with available fixes',
        filterCriteria=filter_criteria,
        name='CriticalHighSeverityWithFixes'
    )
    
    return response
```

### Lab 2: Automated Remediation Workflow

#### Step 1: Create EventBridge Rule
```python
def create_eventbridge_rule():
    """
    Create EventBridge rule for Inspector findings
    """
    eventbridge = boto3.client('events')
    
    rule_response = eventbridge.put_rule(
        Name='InspectorCriticalFindings',
        EventPattern=json.dumps({
            "source": ["aws.inspector2"],
            "detail-type": ["Inspector2 Finding"],
            "detail": {
                "severity": ["CRITICAL"]
            }
        }),
        State='ENABLED',
        Description='Trigger on critical Inspector findings'
    )
    
    return rule_response
```

#### Step 2: Create Lambda Function for Remediation
```python
import boto3
import json
from datetime import datetime

def remediation_lambda_handler(event, context):
    """
    Automated remediation for Inspector findings
    """
    # Initialize AWS clients
    ssm = boto3.client('ssm')
    sns = boto3.client('sns')
    ec2 = boto3.client('ec2')
    
    # Parse the Inspector finding
    finding_detail = event['detail']
    severity = finding_detail['severity']
    resource = finding_detail['resources'][0]
    
    remediation_actions = []
    
    if resource['type'] == 'AWS_EC2_INSTANCE':
        instance_id = resource['id']
        
        # For critical findings on EC2 instances
        if severity == 'CRITICAL':
            # Create snapshot before remediation
            try:
                instance_details = ec2.describe_instances(InstanceIds=[instance_id])
                volumes = instance_details['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
                
                for volume in volumes:
                    volume_id = volume['Ebs']['VolumeId']
                    snapshot_response = ec2.create_snapshot(
                        VolumeId=volume_id,
                        Description=f'Pre-remediation snapshot for {instance_id}'
                    )
                    remediation_actions.append(f"Created snapshot: {snapshot_response['SnapshotId']}")
                
                # Run patch management
                ssm_response = ssm.send_command(
                    InstanceIds=[instance_id],
                    DocumentName='AWS-RunPatchBaseline',
                    Parameters={
                        'Operation': ['Install']
                    }
                )
                remediation_actions.append(f"Initiated patching: {ssm_response['Command']['CommandId']}")
                
            except Exception as e:
                remediation_actions.append(f"Error in remediation: {str(e)}")
    
    # Send notification
    notification_message = {
        'finding_id': finding_detail.get('findingArn', 'Unknown'),
        'severity': severity,
        'resource': resource['id'],
        'actions_taken': remediation_actions,
        'timestamp': datetime.now().isoformat()
    }
    
    sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:inspector-remediation',
        Message=json.dumps(notification_message, indent=2),
        Subject=f'Inspector Automated Remediation - {severity}'
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Remediation completed',
            'actions': remediation_actions
        })
    }
```

#### Step 3: Add Lambda Target to EventBridge Rule
```python
def add_lambda_target():
    """
    Add Lambda function as target for EventBridge rule
    """
    eventbridge = boto3.client('events')
    
    target_response = eventbridge.put_targets(
        Rule='InspectorCriticalFindings',
        Targets=[
            {
                'Id': '1',
                'Arn': 'arn:aws:lambda:us-east-1:123456789012:function:inspector-remediation',
                'InputTransformer': {
                    'InputPathsMap': {
                        'severity': '$.detail.severity',
                        'findingArn': '$.detail.findingArn'
                    },
                    'InputTemplate': '{"detail": <aws.events.event>}'
                }
            }
        ]
    )
    
    return target_response
```

### Lab 3: Security Hub Integration

#### Step 1: Enable Security Hub
```python
def enable_security_hub():
    """
    Enable Security Hub and Inspector integration
    """
    securityhub = boto3.client('securityhub')
    
    # Enable Security Hub
    try:
        securityhub.enable_security_hub(
            Tags={
                'Environment': 'Production',
                'Purpose': 'Security-Monitoring'
            },
            EnableDefaultStandards=True
        )
    except ClientError as e:
        if e.response['Error']['Code'] != 'ResourceConflictException':
            raise
    
    # Enable Inspector integration
    securityhub.enable_import_findings_for_product(
        ProductArn='arn:aws:securityhub:us-east-1::product/aws/inspector'
    )
    
    return "Security Hub enabled with Inspector integration"
```

#### Step 2: Custom Insights for Inspector Findings
```python
def create_inspector_insights():
    """
    Create custom Security Hub insights for Inspector findings
    """
    securityhub = boto3.client('securityhub')
    
    insights = [
        {
            'Name': 'Critical Inspector Findings by Resource',
            'Filters': {
                'ProductName': [{'Value': 'Inspector', 'Comparison': 'EQUALS'}],
                'SeverityLabel': [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'}],
                'RecordState': [{'Value': 'ACTIVE', 'Comparison': 'EQUALS'}]
            },
            'GroupByAttribute': 'ResourceId'
        },
        {
            'Name': 'Inspector Findings Trend',
            'Filters': {
                'ProductName': [{'Value': 'Inspector', 'Comparison': 'EQUALS'}],
                'CreatedAt': [
                    {
                        'Start': '2024-01-01T00:00:00.000Z',
                        'End': '2024-12-31T23:59:59.999Z',
                        'DateRange': {'Unit': 'DAYS', 'Value': 30}
                    }
                ]
            },
            'GroupByAttribute': 'CreatedAt'
        }
    ]
    
    created_insights = []
    for insight in insights:
        response = securityhub.create_insight(**insight)
        created_insights.append(response['InsightArn'])
    
    return created_insights
```

### Lab 4: Cost Optimization Dashboard

#### Step 1: Create Cost Tracking Lambda
```python
def create_cost_tracking():
    """
    Track Inspector usage and costs
    """
    import boto3
    from datetime import datetime, timedelta
    
    cloudwatch = boto3.client('cloudwatch')
    inspector = boto3.client('inspector2')
    
    # Get current month usage
    start_date = datetime.now().replace(day=1)
    end_date = datetime.now()
    
    # Track EC2 instances scanned
    ec2_usage = inspector.list_usage_totals(
        maxResults=100
    )
    
    # Track container images scanned
    ecr_usage = inspector.list_findings(
        filterCriteria={
            'findingType': ['PACKAGE_VULNERABILITY'],
            'resourceType': ['AWS_ECR_CONTAINER_IMAGE']
        },
        maxResults=100
    )
    
    # Calculate estimated costs
    estimated_costs = {
        'ec2_cost': len(ec2_usage.get('totals', [])) * 0.15,  # $0.15 per instance
        'ecr_cost': len(ecr_usage.get('findings', [])) * 0.09,  # $0.09 per initial scan
        'lambda_cost': 0  # Calculate based on function scans
    }
    
    # Publish cost metrics
    for cost_type, amount in estimated_costs.items():
        cloudwatch.put_metric_data(
            Namespace='Custom/Inspector/Costs',
            MetricData=[
                {
                    'MetricName': cost_type,
                    'Value': amount,
                    'Unit': 'None',
                    'Timestamp': datetime.now()
                }
            ]
        )
    
    return estimated_costs
```

This comprehensive guide covers all aspects of AWS Inspector relevant to the SAA-C03 certification exam. The guide includes practical examples, best practices, and hands-on labs that will help you understand and implement Inspector effectively in real-world scenarios.