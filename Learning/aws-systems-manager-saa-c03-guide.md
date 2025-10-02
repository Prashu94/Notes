# AWS Systems Manager - SAA-C03 Certification Guide

## Table of Contents
1. [Introduction to AWS Systems Manager](#introduction-to-aws-systems-manager)
2. [Core Components Overview](#core-components-overview)
3. [Parameter Store](#parameter-store)
4. [Session Manager](#session-manager)
5. [Run Command](#run-command)
6. [Patch Manager](#patch-manager)
7. [Maintenance Windows](#maintenance-windows)
8. [Automation](#automation)
9. [Inventory](#inventory)
10. [State Manager](#state-manager)
11. [Compliance](#compliance)
12. [OpsCenter](#opscenter)
13. [Application Manager](#application-manager)
14. [Fleet Manager](#fleet-manager)
15. [Systems Manager Agent (SSM Agent)](#systems-manager-agent-ssm-agent)
16. [IAM Roles and Permissions](#iam-roles-and-permissions)
17. [Integration with Other AWS Services](#integration-with-other-aws-services)
18. [Security and Compliance](#security-and-compliance)
19. [Cost Optimization](#cost-optimization)
20. [Best Practices](#best-practices)
21. [Troubleshooting](#troubleshooting)
22. [SAA-C03 Exam Focus Areas](#saa-c03-exam-focus-areas)

---

## Introduction to AWS Systems Manager

AWS Systems Manager is a comprehensive management service that provides a unified interface for managing your AWS resources at scale. It offers operational insights and automated management capabilities for EC2 instances, on-premises servers, and other AWS resources.

### Key Benefits
- **Centralized Management**: Single pane of glass for resource management
- **Operational Insights**: Comprehensive visibility into resource health and performance
- **Automation**: Reduce manual tasks and human error
- **Security**: Secure remote access without bastion hosts or SSH keys
- **Compliance**: Track and maintain configuration compliance
- **Cost Efficiency**: Optimize resource utilization and reduce operational overhead

### Systems Manager vs Other AWS Management Services

| Service | Primary Purpose | Key Capabilities |
|---------|----------------|------------------|
| Systems Manager | Operational management | Parameter store, patching, automation, remote access |
| CloudFormation | Infrastructure provisioning | Infrastructure as Code, stack management |
| Config | Configuration compliance | Resource configuration tracking, compliance rules |
| CloudTrail | API auditing | API call logging, governance |
| OpsWorks | Application management | Chef/Puppet-based configuration management |

### When to Use Systems Manager
- **Hybrid environments**: Managing both AWS and on-premises resources
- **Patch management**: Automated patching across fleets
- **Configuration management**: Standardizing configurations at scale
- **Remote access**: Secure shell access without bastion hosts
- **Parameter management**: Centralized configuration and secrets management
- **Operational automation**: Automating routine maintenance tasks

---

## Core Components Overview

AWS Systems Manager consists of multiple capabilities organized into four main categories:

### 1. Operations Management
- **OpsCenter**: Central location for operational issues
- **CloudWatch Dashboards**: Integrated monitoring dashboards
- **PHD Integration**: Personal Health Dashboard integration

### 2. Application Management
- **Application Manager**: Application-centric view of resources
- **AppConfig**: Feature flag and configuration management
- **Parameter Store**: Hierarchical parameter management

### 3. Change Management
- **Change Calendar**: Track and approve changes
- **Maintenance Windows**: Schedule maintenance activities
- **Automation**: Workflow automation and orchestration

### 4. Node Management
- **Fleet Manager**: Remote desktop and file management
- **Session Manager**: Browser-based shell access
- **Run Command**: Execute commands across instances
- **State Manager**: Desired state configuration
- **Patch Manager**: Automated patch management
- **Inventory**: Collect system metadata
- **Compliance**: Track compliance status

---

## Parameter Store

AWS Systems Manager Parameter Store provides hierarchical storage for configuration data management and secrets management. It's a key service for the SAA-C03 exam.

### Key Features
- **Hierarchical Organization**: Parameters organized in tree-like structure
- **Encryption**: Native integration with AWS KMS
- **Versioning**: Track parameter changes over time
- **Cross-Region Replication**: Replicate parameters across regions
- **Fine-grained Access Control**: IAM-based permissions
- **Integration**: Native integration with other AWS services

### Parameter Types

#### Standard Parameters
- **Free tier**: Up to 10,000 parameters
- **Size limit**: 4 KB per parameter
- **No advanced features**: No policies or notifications
- **Use cases**: Basic configuration data

#### Advanced Parameters
- **Cost**: $0.05 per 10,000 parameter operations
- **Size limit**: 8 KB per parameter
- **Advanced features**: Policies, notifications, parameter hierarchies
- **Use cases**: Complex configurations, large values

### Parameter Data Types

```yaml
# String Parameter
/myapp/database/username: "dbuser"

# StringList Parameter
/myapp/allowed-regions: "us-east-1,us-west-2,eu-west-1"

# SecureString Parameter (encrypted)
/myapp/database/password: "encrypted-password-value"
```

### Hierarchical Organization

```
/myapp/
  ├── prod/
  │   ├── database/
  │   │   ├── host
  │   │   ├── port
  │   │   └── password (SecureString)
  │   └── api/
  │       ├── endpoint
  │       └── key (SecureString)
  └── dev/
      ├── database/
      │   ├── host
      │   ├── port
      │   └── password (SecureString)
      └── api/
          ├── endpoint
          └── key (SecureString)
```

### Parameter Policies (Advanced Parameters Only)

#### Expiration Policy
```json
{
  "Type": "Expiration",
  "Version": "1.0",
  "Attributes": {
    "Timestamp": "2024-12-31T23:59:59.000Z"
  }
}
```

#### ExpirationNotification Policy
```json
{
  "Type": "ExpirationNotification",
  "Version": "1.0",
  "Attributes": {
    "Before": "30",
    "Unit": "Days"
  }
}
```

#### NoChangeNotification Policy
```json
{
  "Type": "NoChangeNotification",
  "Version": "1.0",
  "Attributes": {
    "After": "60",
    "Unit": "Days"
  }
}
```

### Integration Examples

#### Lambda Function Access
```python
import boto3
import json

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Get single parameter
    response = ssm.get_parameter(
        Name='/myapp/prod/database/host',
        WithDecryption=True
    )
    db_host = response['Parameter']['Value']
    
    # Get multiple parameters by path
    response = ssm.get_parameters_by_path(
        Path='/myapp/prod/',
        Recursive=True,
        WithDecryption=True
    )
    
    parameters = {param['Name']: param['Value'] for param in response['Parameters']}
    
    return {
        'statusCode': 200,
        'body': json.dumps('Parameters retrieved successfully')
    }
```

#### EC2 Instance Access
```bash
#!/bin/bash
# Get parameter value using AWS CLI
DB_HOST=$(aws ssm get-parameter --name "/myapp/prod/database/host" --query "Parameter.Value" --output text)

# Get encrypted parameter
DB_PASSWORD=$(aws ssm get-parameter --name "/myapp/prod/database/password" --with-decryption --query "Parameter.Value" --output text)

echo "Connecting to database at $DB_HOST"
```

### Parameter Store vs AWS Secrets Manager

| Feature | Parameter Store | Secrets Manager |
|---------|----------------|-----------------|
| **Cost** | Free (Standard), $0.05 per 10K ops (Advanced) | $0.40 per secret per month + API calls |
| **Size Limit** | 4KB (Standard), 8KB (Advanced) | 64KB |
| **Rotation** | Manual | Automatic rotation support |
| **Cross-region** | Manual replication | Automatic replication |
| **Use Case** | Configuration data, simple secrets | Complex secrets, automatic rotation |

### Common Use Cases

#### 1. Application Configuration
```
/myapp/prod/config/
├── api-timeout: "30"
├── max-connections: "100"
├── feature-flags: "feature1,feature2"
└── log-level: "INFO"
```

#### 2. Database Connection Strings
```
/myapp/prod/database/
├── host: "prod-db.example.com"
├── port: "5432"
├── database: "myapp_prod"
├── username: "app_user"
└── password: "encrypted-password" (SecureString)
```

#### 3. Third-party API Keys
```
/myapp/prod/integrations/
├── stripe-api-key: "encrypted-key" (SecureString)
├── sendgrid-api-key: "encrypted-key" (SecureString)
└── slack-webhook-url: "encrypted-url" (SecureString)
```

### Best Practices for Parameter Store

#### 1. Naming Conventions
- Use hierarchical paths: `/app/environment/component/parameter`
- Be consistent with naming patterns
- Use lowercase with hyphens for readability

#### 2. Security
- Always use SecureString for sensitive data
- Implement least privilege IAM policies
- Use separate KMS keys for different environments
- Enable CloudTrail for parameter access auditing

#### 3. Organization
- Group related parameters under common paths
- Use environment-specific hierarchies
- Implement parameter tagging for cost allocation

#### 4. Monitoring
- Set up CloudWatch alarms for parameter changes
- Use parameter policies for lifecycle management
- Monitor parameter usage with CloudWatch Insights

---

## Session Manager

AWS Systems Manager Session Manager provides secure and auditable instance management without the need for bastion hosts, SSH keys, or opening inbound ports.

### Key Features
- **Browser-based Access**: Shell access through AWS Console
- **No Inbound Ports**: No need to open SSH/RDP ports
- **Audit Logging**: Complete session logging to CloudWatch/S3
- **IAM Integration**: Fine-grained access control
- **Cross-platform**: Supports Linux, Windows, and macOS
- **Port Forwarding**: Secure tunneling for applications

### Architecture and Components

#### Requirements
1. **SSM Agent**: Must be installed and running on instances
2. **IAM Instance Profile**: EC2 instances need appropriate IAM role
3. **Network Connectivity**: Instances must reach Systems Manager endpoints
4. **User Permissions**: Users need Session Manager permissions

#### Network Flow
```
User → AWS Console/CLI → Session Manager Service → SSM Agent → Instance
```

### IAM Permissions

#### Instance Role (EC2InstanceProfile)
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:UpdateInstanceInformation",
                "ssmmessages:CreateControlChannel",
                "ssmmessages:CreateDataChannel",
                "ssmmessages:OpenControlChannel",
                "ssmmessages:OpenDataChannel"
            ],
            "Resource": "*"
        }
    ]
}
```

#### User Policy for Session Access
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:StartSession"
            ],
            "Resource": [
                "arn:aws:ec2:*:*:instance/*"
            ],
            "Condition": {
                "StringEquals": {
                    "ssm:resourceTag/Environment": ["dev", "staging"]
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeInstanceInformation",
                "ssm:DescribeSessions",
                "ssm:GetConnectionStatus"
            ],
            "Resource": "*"
        }
    ]
}
```

### Session Manager Configuration

#### Session Preferences
```json
{
    "sessionType": "Standard",
    "properties": {
        "maxSessionDuration": "60",
        "allowPortForwardingForManagedNodes": true,
        "shellProfile": {
            "linux": "cd /home/ec2-user && pwd",
            "windows": "cd C:\\ && dir"
        },
        "idleSessionTimeout": "20",
        "cloudWatchLogGroupName": "/aws/ssm/sessions",
        "cloudWatchEncryptionEnabled": true,
        "cloudWatchStreamingEnabled": true,
        "kmsKeyId": "alias/session-manager-logs",
        "runAsEnabled": false,
        "runAsDefaultUser": "ec2-user"
    }
}
```

### Logging and Auditing

#### CloudWatch Logs Integration
```yaml
# Session Manager preferences for CloudWatch logging
CloudWatchLogGroupName: "/aws/ssm/sessions"
CloudWatchEncryptionEnabled: true
CloudWatchStreamingEnabled: true
```

#### S3 Logging Configuration
```yaml
# Session Manager preferences for S3 logging
S3BucketName: "my-session-logs-bucket"
S3KeyPrefix: "session-logs/"
S3EncryptionEnabled: true
```

#### Sample Log Entry
```json
{
    "version": "1.0",
    "sessionId": "session-0123456789abcdef0",
    "startTime": "2024-01-15T10:30:00Z",
    "endTime": "2024-01-15T10:45:00Z",
    "target": "i-0123456789abcdef0",
    "owner": "arn:aws:iam::123456789012:user/alice",
    "status": "Success",
    "sessionData": "base64-encoded-session-transcript"
}
```

### Port Forwarding

#### Local Port Forwarding Example
```bash
# Forward local port 8080 to instance port 80
aws ssm start-session \
    --target i-0123456789abcdef0 \
    --document-name AWS-StartPortForwardingSession \
    --parameters '{"portNumber":["80"],"localPortNumber":["8080"]}'
```

#### Remote Port Forwarding Example
```bash
# Forward instance port 3306 to local port 3307
aws ssm start-session \
    --target i-0123456789abcdef0 \
    --document-name AWS-StartPortForwardingSessionToRemoteHost \
    --parameters '{"host":["rds-instance.region.rds.amazonaws.com"],"portNumber":["3306"],"localPortNumber":["3307"]}'
```

### Use Cases

#### 1. Secure Administrative Access
- Replace bastion hosts for administrative tasks
- Eliminate SSH key management
- Centralized access control through IAM

#### 2. Troubleshooting and Debugging
- Quick shell access for troubleshooting
- No need to modify security groups
- Complete audit trail of activities

#### 3. Database Access
- Secure tunneling to RDS instances
- Port forwarding for application debugging
- Temporary access without permanent connections

#### 4. Development and Testing
- Access to private instances for development
- Safe testing environment access
- Temporary administrative access

### Session Manager vs Traditional SSH

| Feature | Session Manager | Traditional SSH |
|---------|----------------|-----------------|
| **Security Groups** | No inbound rules needed | SSH port (22) must be open |
| **Key Management** | No SSH keys required | SSH key pair management |
| **Audit Logging** | Complete session logging | Requires additional setup |
| **Network Access** | Works through NAT/VPC endpoints | Direct network connectivity |
| **User Management** | IAM-based permissions | OS-level user management |
| **Bastion Hosts** | Not required | Often required for private instances |

### Common Troubleshooting Issues

#### 1. Instance Not Appearing in Console
**Symptoms**: Instance not visible in Session Manager console
**Causes**:
- SSM Agent not installed/running
- Incorrect IAM instance profile
- Network connectivity issues
- Instance not registered with Systems Manager

**Solutions**:
```bash
# Check SSM Agent status (Amazon Linux 2)
sudo systemctl status amazon-ssm-agent

# Restart SSM Agent
sudo systemctl restart amazon-ssm-agent

# Check instance registration
aws ssm describe-instance-information --instance-information-filter-list key=InstanceIds,valueSet=i-0123456789abcdef0
```

#### 2. Access Denied Errors
**Symptoms**: "AccessDenied" when starting sessions
**Causes**:
- Missing user permissions
- Incorrect resource tags
- Session preferences restrictions

**Solutions**:
- Verify IAM permissions
- Check resource-based conditions
- Review session preferences

#### 3. Session Disconnections
**Symptoms**: Frequent session timeouts
**Causes**:
- Idle timeout settings
- Network connectivity issues
- Instance resource constraints

**Solutions**:
- Adjust session preferences
- Monitor instance resources
- Check network stability

### Best Practices

#### 1. Security
- Use condition-based IAM policies
- Enable session logging and monitoring
- Implement least privilege access
- Use KMS encryption for logs

#### 2. Monitoring
- Set up CloudWatch alarms for session activities
- Monitor session duration and frequency
- Track unusual access patterns
- Implement automated response to suspicious activities

#### 3. Network Design
- Use VPC endpoints for private subnets
- Implement proper security group configurations
- Consider network ACLs for additional security
- Plan for high availability and disaster recovery

---

## Run Command

AWS Systems Manager Run Command allows you to remotely and securely execute commands on managed instances at scale without logging into each instance.

### Key Features
- **Scalable Execution**: Run commands on thousands of instances simultaneously
- **Document-based**: Use pre-built or custom command documents
- **Secure**: No SSH/RDP access required
- **Auditable**: Complete execution history and logging
- **Rate Control**: Manage execution speed and error thresholds
- **Target Selection**: Flexible instance targeting options

### Command Documents

#### AWS-Managed Documents
```yaml
# Common AWS-provided documents
AWS-RunShellScript          # Linux shell commands
AWS-RunPowerShellScript     # Windows PowerShell commands
AWS-UpdateSSMAgent          # Update SSM Agent
AWS-ConfigureAWSPackage     # Install/uninstall AWS packages
AWS-InstallApplication      # Install applications
AWS-GatherSoftwareInventory # Collect software inventory
```

#### Custom Document Example
```yaml
# Custom document for application deployment
schemaVersion: "2.2"
description: "Deploy application from S3"
parameters:
  applicationUrl:
    type: String
    description: "S3 URL of application package"
    default: "s3://my-bucket/app.tar.gz"
  installPath:
    type: String
    description: "Installation directory"
    default: "/opt/myapp"

mainSteps:
- action: "aws:runShellScript"
  name: "downloadAndInstall"
  inputs:
    timeoutSeconds: "300"
    runCommand:
    - "#!/bin/bash"
    - "mkdir -p {{ installPath }}"
    - "cd {{ installPath }}"
    - "aws s3 cp {{ applicationUrl }} ."
    - "tar -xzf app.tar.gz"
    - "chmod +x install.sh"
    - "./install.sh"
```

### Targeting Options

#### 1. Instance IDs
```bash
aws ssm send-command \
    --instance-ids "i-0123456789abcdef0" "i-0987654321fedcba0" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["uptime","df -h"]'
```

#### 2. Tags
```bash
aws ssm send-command \
    --targets "Key=tag:Environment,Values=production" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["systemctl status nginx"]'
```

#### 3. Resource Groups
```bash
aws ssm send-command \
    --targets "Key=resource-groups:Name,Values=WebServerGroup" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["service httpd restart"]'
```

### Execution Control

#### Rate Control Settings
```bash
aws ssm send-command \
    --targets "Key=tag:Environment,Values=production" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["yum update -y"]' \
    --max-concurrency "10" \
    --max-errors "2"
```

#### Timeout Configuration
```bash
aws ssm send-command \
    --instance-ids "i-0123456789abcdef0" \
    --document-name "AWS-RunShellScript" \
    --timeout-seconds 3600 \
    --parameters 'commands=["#!/bin/bash","sleep 30","echo Done"],executionTimeout=["3600"]'
```

### Output and Logging

#### Command Output Handling
```bash
# Send command with S3 output
aws ssm send-command \
    --instance-ids "i-0123456789abcdef0" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["ps aux"]' \
    --output-s3-bucket-name "my-command-outputs" \
    --output-s3-key-prefix "run-command-logs/"
```

#### CloudWatch Logs Integration
```bash
# Enable CloudWatch Logs for command execution
aws ssm send-command \
    --instance-ids "i-0123456789abcdef0" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["tail -f /var/log/messages"]' \
    --cloud-watch-output-config '{"CloudWatchLogGroupName":"/aws/ssm/run-command","CloudWatchOutputEnabled":true}'
```

### Common Use Cases

#### 1. System Administration
```bash
# Check system health across fleet
aws ssm send-command \
    --targets "Key=tag:Role,Values=webserver" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "uptime",
        "free -m",
        "df -h",
        "systemctl status nginx"
    ]'
```

#### 2. Software Updates
```bash
# Update packages on Amazon Linux instances
aws ssm send-command \
    --targets "Key=tag:OS,Values=AmazonLinux" \
    --document-name "AWS-RunShellScript" \
    --max-concurrency "25%" \
    --max-errors "10%" \
    --parameters 'commands=[
        "yum update -y",
        "systemctl restart amazon-ssm-agent"
    ]'
```

#### 3. Configuration Management
```bash
# Deploy configuration files
aws ssm send-command \
    --targets "Key=tag:Environment,Values=production" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=[
        "aws s3 cp s3://my-config-bucket/nginx.conf /etc/nginx/",
        "nginx -t",
        "systemctl reload nginx"
    ]'
```

#### 4. Log Collection
```bash
# Collect logs from multiple instances
aws ssm send-command \
    --targets "Key=tag:Application,Values=webapp" \
    --document-name "AWS-RunShellScript" \
    --output-s3-bucket-name "log-collection-bucket" \
    --parameters 'commands=[
        "tar -czf /tmp/logs-$(date +%Y%m%d).tar.gz /var/log/application/",
        "aws s3 cp /tmp/logs-$(date +%Y%m%d).tar.gz s3://log-collection-bucket/"
    ]'
```

### Command Execution States

#### State Transitions
```
Pending → InProgress → Success/Failed/Cancelled/TimedOut
         ↓
      Cancelling → Cancelled
```

#### Monitoring Command Status
```bash
# Get command execution status
aws ssm get-command-invocation \
    --command-id "12345678-1234-1234-1234-123456789012" \
    --instance-id "i-0123456789abcdef0"

# List all commands
aws ssm list-commands \
    --filter "key=Status,value=Success"
```

### Error Handling and Troubleshooting

#### Common Error Scenarios

1. **Access Denied**
   - Missing IAM permissions
   - SSM Agent not properly configured
   - Instance not managed by Systems Manager

2. **Command Failed**
   - Script syntax errors
   - Missing dependencies
   - Insufficient privileges

3. **Timeout Issues**
   - Long-running commands
   - Network connectivity problems
   - Resource constraints

#### Debugging Commands
```bash
# Check SSM Agent logs
sudo tail -f /var/log/amazon/ssm/amazon-ssm-agent.log

# Verify instance registration
aws ssm describe-instance-information \
    --filters "Key=InstanceIds,Values=i-0123456789abcdef0"

# Check command execution details
aws ssm describe-instance-information \
    --command-id "12345678-1234-1234-1234-123456789012" \
    --instance-id "i-0123456789abcdef0" \
    --details
```

### Integration with Other Services

#### 1. EventBridge Integration
```json
{
  "source": ["aws.ssm"],
  "detail-type": ["EC2 Command Status-change Notification"],
  "detail": {
    "status": ["Success", "Failed"],
    "command-id": ["12345678-1234-1234-1234-123456789012"]
  }
}
```

#### 2. SNS Notifications
```bash
# Send command with SNS notification
aws ssm send-command \
    --targets "Key=tag:Environment,Values=production" \
    --document-name "AWS-RunShellScript" \
    --parameters 'commands=["systemctl restart application"]' \
    --notification-config "NotificationArn=arn:aws:sns:us-east-1:123456789012:command-notifications,NotificationEvents=All,NotificationType=Command"
```

#### 3. Lambda Integration
```python
import boto3
import json

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Send command to instances
    response = ssm.send_command(
        Targets=[
            {
                'Key': 'tag:Environment',
                'Values': ['production']
            }
        ],
        DocumentName='AWS-RunShellScript',
        Parameters={
            'commands': [
                'systemctl status nginx',
                'curl -f http://localhost/health || exit 1'
            ]
        },
        MaxConcurrency='10',
        MaxErrors='1'
    )
    
    command_id = response['Command']['CommandId']
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'commandId': command_id,
            'message': 'Health check command sent'
        })
    }
```

### Best Practices

#### 1. Security
- Use least privilege IAM policies
- Validate input parameters in custom documents
- Avoid hardcoding secrets in commands
- Use Parameter Store for sensitive data

#### 2. Reliability
- Implement proper error handling
- Use appropriate timeouts
- Test commands on small subsets first
- Monitor command execution status

#### 3. Performance
- Use rate control for large deployments
- Optimize command execution time
- Consider network bandwidth limitations
- Use parallel execution efficiently

#### 4. Monitoring
- Set up CloudWatch alarms for failed commands
- Use CloudWatch Logs for detailed monitoring
- Track command execution metrics
- Implement automated remediation

---

## Patch Manager

AWS Systems Manager Patch Manager automates the process of patching managed instances with security-related and other types of updates. It's a critical component for maintaining security compliance across your infrastructure.

### Key Features
- **Automated Patching**: Schedule and automate patch deployment
- **Patch Baselines**: Define approved and rejected patches
- **Maintenance Windows**: Control when patching occurs
- **Compliance Reporting**: Track patch compliance across instances
- **Cross-Platform**: Supports Windows, Linux, and macOS
- **Integration**: Works with other Systems Manager capabilities

### Patch Baselines

Patch baselines define which patches should be installed on instances. AWS provides predefined baselines, and you can create custom ones.

#### AWS-Managed Baselines

```yaml
# Amazon Linux 2 Default Baseline
AWS-AmazonLinux2DefaultPatchBaseline:
  - Security updates: Auto-approved
  - Bugfix updates: Auto-approved
  - Enhancement updates: Not approved
  - Other updates: Not approved

# Windows Default Baseline  
AWS-WindowsPredefinedPatchBaseline-OS:
  - Critical updates: Auto-approved
  - Security updates: Auto-approved
  - Service packs: Auto-approved
  - Updates: Auto-approved
  - Update rollups: Auto-approved
```

#### Custom Patch Baseline Example
```json
{
    "Name": "CustomLinuxBaseline",
    "Description": "Custom baseline for production Linux servers",
    "OperatingSystem": "AMAZON_LINUX_2",
    "ApprovalRules": [
        {
            "PatchFilterGroup": {
                "PatchFilters": [
                    {
                        "Key": "CLASSIFICATION",
                        "Values": ["Security", "Bugfix"]
                    },
                    {
                        "Key": "SEVERITY",
                        "Values": ["Critical", "Important"]
                    }
                ]
            },
            "ApproveAfterDays": 7,
            "ComplianceLevel": "HIGH"
        }
    ],
    "ApprovedPatches": [
        "kernel-4.14.123-*"
    ],
    "RejectedPatches": [
        "kernel-4.14.111-*"
    ],
    "Sources": [
        {
            "Name": "MyCustomRepo",
            "Products": ["MyProduct"],
            "Configuration": "baseurl=https://my-repo.example.com/linux/"
        }
    ]
}
```

### Patch Groups

Patch groups allow you to organize instances for different patching strategies.

#### Tagging for Patch Groups
```bash
# Tag instances for patch groups
aws ec2 create-tags \
    --resources i-0123456789abcdef0 \
    --tags Key=Patch Group,Value=ProductionServers

# Associate baseline with patch group
aws ssm register-patch-baseline-for-patch-group \
    --baseline-id pb-0123456789abcdef0 \
    --patch-group ProductionServers
```

#### Patch Group Strategy
```yaml
Development:
  - Patch Group: "Development"
  - Baseline: More permissive, immediate updates
  - Schedule: Daily during business hours

Staging:
  - Patch Group: "Staging"  
  - Baseline: Production-like, 7-day delay
  - Schedule: Weekly, off-hours

Production:
  - Patch Group: "Production"
  - Baseline: Conservative, 14-day delay
  - Schedule: Monthly, maintenance window
```

### Patch Operations

#### 1. Scan Operation
Scans instances to determine which patches are missing but doesn't install them.

```bash
# Scan instances for missing patches
aws ssm send-command \
    --targets "Key=tag:Patch Group,Values=ProductionServers" \
    --document-name "AWS-RunPatchBaseline" \
    --parameters "Operation=Scan"
```

#### 2. Install Operation
Installs approved patches on instances.

```bash
# Install patches on instances
aws ssm send-command \
    --targets "Key=tag:Patch Group,Values=ProductionServers" \
    --document-name "AWS-RunPatchBaseline" \
    --parameters "Operation=Install,RebootOption=RebootIfNeeded"
```

### Maintenance Windows Integration

#### Creating a Maintenance Window for Patching
```bash
# Create maintenance window
aws ssm create-maintenance-window \
    --name "ProductionPatchingWindow" \
    --description "Monthly patching for production servers" \
    --duration 4 \
    --cutoff 1 \
    --schedule "cron(0 2 ? * SUN#3 *)" \
    --schedule-timezone "America/New_York" \
    --allow-unassociated-targets

# Register targets
aws ssm register-target-with-maintenance-window \
    --window-id mw-0123456789abcdef0 \
    --resource-type "INSTANCE" \
    --targets "Key=tag:Patch Group,Values=ProductionServers"

# Register patch task
aws ssm register-task-with-maintenance-window \
    --window-id mw-0123456789abcdef0 \
    --targets "Key=WindowTargetIds,Values=12345678-1234-1234-1234-123456789012" \
    --task-arn "AWS-RunPatchBaseline" \
    --task-type "RUN_COMMAND" \
    --max-concurrency "25%" \
    --max-errors "10%" \
    --priority 1 \
    --task-parameters '{
        "Operation": {
            "Values": ["Install"]
        },
        "RebootOption": {
            "Values": ["RebootIfNeeded"]
        }
    }'
```

### Compliance Monitoring

#### Patch Compliance Dashboard
```bash
# Get patch compliance summary
aws ssm describe-patch-group-state \
    --patch-group "ProductionServers"

# Get detailed compliance info
aws ssm list-compliance-items \
    --resource-ids i-0123456789abcdef0 \
    --resource-types "ManagedInstance" \
    --filters "Key=ComplianceType,Values=Patch,Type=EQUAL"
```

#### CloudWatch Metrics for Compliance
```yaml
Metrics:
  - AWS/SSM-PatchCompliance/ComplianceByCriticalNonCompliantResourceCount
  - AWS/SSM-PatchCompliance/ComplianceByPatchGroup
  - AWS/SSM-PatchCompliance/NonCompliantInstanceCount
```

### Advanced Patching Scenarios

#### 1. Blue-Green Patching Strategy
```yaml
Strategy:
  Phase 1:
    - Target: Blue environment instances
    - Action: Patch and test
    - Validation: Automated testing
  
  Phase 2:
    - Action: Switch traffic to Blue
    - Target: Green environment instances  
    - Action: Patch Green instances
  
  Phase 3:
    - Action: Switch traffic to Green
    - Result: Both environments patched
```

#### 2. Rolling Patch Deployment
```bash
# Patch instances in batches
aws ssm send-command \
    --targets "Key=tag:Patch Group,Values=WebServers" \
    --document-name "AWS-RunPatchBaseline" \
    --parameters "Operation=Install,RebootOption=RebootIfNeeded" \
    --max-concurrency "2" \
    --max-errors "0"
```

#### 3. Custom Patch Repository
```json
{
    "Sources": [
        {
            "Name": "CorporateRepository",
            "Products": ["Enterprise Linux"],
            "Configuration": "baseurl=https://repo.company.com/centos/7/updates/"
        }
    ]
}
```

### Integration Examples

#### 1. EventBridge Integration
```json
{
    "source": ["aws.ssm"],
    "detail-type": ["EC2 Command Status-change Notification"],
    "detail": {
        "status": ["Success", "Failed"],
        "document-name": ["AWS-RunPatchBaseline"]
    }
}
```

#### 2. Lambda Function for Custom Actions
```python
import boto3
import json

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Get patch compliance status
    response = ssm.describe_instance_patch-states(
        Filters=[
            {
                'Key': 'PatchGroup',
                'Values': ['ProductionServers']
            }
        ]
    )
    
    non_compliant_instances = []
    for instance in response['InstancePatchStates']:
        if instance['MissingCount'] > 0:
            non_compliant_instances.append(instance['InstanceId'])
    
    if non_compliant_instances:
        # Send notification or trigger remediation
        sns = boto3.client('sns')
        sns.publish(
            TopicArn='arn:aws:sns:us-east-1:123456789012:patch-compliance',
            Message=f'Non-compliant instances found: {non_compliant_instances}',
            Subject='Patch Compliance Alert'
        )
    
    return {
        'statusCode': 200,
        'body': json.dumps('Compliance check completed')
    }
```

### Patch Manager vs Other Solutions

| Feature | Patch Manager | Traditional Tools |
|---------|---------------|-------------------|
| **Agent Management** | SSM Agent (built-in) | Separate agent installation |
| **Scheduling** | Maintenance Windows | Cron jobs or task scheduler |
| **Compliance** | Built-in reporting | Custom monitoring setup |
| **Cross-platform** | Unified interface | Platform-specific tools |
| **AWS Integration** | Native integration | Manual integration required |

### Best Practices

#### 1. Baseline Management
- Use separate baselines for different environments
- Test patches in development first
- Implement approval workflows for critical patches
- Regular review and update of patch baselines

#### 2. Scheduling Strategy
- Stagger patching across availability zones
- Use maintenance windows for controlled patching
- Plan for extended downtime during major updates
- Coordinate with application teams

#### 3. Monitoring and Compliance
- Set up CloudWatch alarms for compliance metrics
- Regular compliance reporting and review
- Automated remediation for critical vulnerabilities
- Track patch deployment success rates

#### 4. Testing and Validation
- Implement automated testing after patching
- Use canary deployments for critical systems
- Validate application functionality post-patch
- Maintain rollback procedures

---

## Maintenance Windows

AWS Systems Manager Maintenance Windows let you define a schedule for when to perform potentially disruptive actions on your instances, such as patching, updating drivers, or installing software.

### Key Concepts

#### Core Components
- **Maintenance Window**: The scheduled time frame
- **Targets**: Resources to be acted upon  
- **Tasks**: Actions to be performed
- **Task Invocations**: Individual executions of tasks

#### Maintenance Window States
```yaml
States:
  - ENABLED: Can execute scheduled tasks
  - DISABLED: Will not execute tasks
  - PENDING: Waiting for first execution
  - RUNNING: Currently executing tasks
```

### Creating Maintenance Windows

#### Basic Maintenance Window
```bash
aws ssm create-maintenance-window \
    --name "WeeklyMaintenance" \
    --description "Weekly maintenance window for web servers" \
    --duration 2 \
    --cutoff 0 \
    --schedule "cron(0 2 ? * SUN *)" \
    --schedule-timezone "America/New_York" \
    --allow-unassociated-targets
```

#### Advanced Maintenance Window Configuration
```json
{
    "Name": "ProductionMaintenanceWindow",
    "Description": "Monthly maintenance for production systems",
    "Duration": 4,
    "Cutoff": 1,
    "Schedule": "cron(0 2 ? * SUN#3 *)",
    "ScheduleTimezone": "America/New_York",
    "StartDate": "2024-01-01T00:00:00Z",
    "EndDate": "2024-12-31T23:59:59Z",
    "AllowUnassociatedTargets": false,
    "Tags": [
        {
            "Key": "Environment",
            "Value": "Production"
        },
        {
            "Key": "Team",
            "Value": "Operations"
        }
    ]
}
```

### Schedule Expressions

#### Cron Expression Format
```bash
# Format: cron(minutes hours day-of-month month day-of-week year)

# Every Sunday at 2 AM
cron(0 2 ? * SUN *)

# Third Sunday of every month at 2 AM  
cron(0 2 ? * SUN#3 *)

# Every day at 3 AM
cron(0 3 * * ? *)

# Every 15 minutes during business hours
cron(0/15 9-17 ? * MON-FRI *)

# Last day of every month at 11 PM
cron(0 23 L * ? *)
```

#### Rate Expression Format
```bash
# Every 30 minutes
rate(30 minutes)

# Every 2 hours
rate(2 hours)

# Every 7 days
rate(7 days)
```

### Targets Configuration

#### Instance Targets
```bash
# Register instance targets by ID
aws ssm register-target-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --resource-type "INSTANCE" \
    --targets "Key=InstanceIds,Values=i-0123456789abcdef0,i-0987654321fedcba0"

# Register targets by tags
aws ssm register-target-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --resource-type "INSTANCE" \
    --targets "Key=tag:Environment,Values=Production" \
    --owner-information "ProductionWebServers"
```

#### Resource Group Targets
```bash
# Register resource group as target
aws ssm register-target-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --resource-type "RESOURCE_GROUP" \
    --targets "Key=resource-groups:Name,Values=WebServerGroup"
```

### Task Types and Configuration

#### 1. Run Command Tasks
```bash
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --targets "Key=WindowTargetIds,Values=12345678-1234-1234-1234-123456789012" \
    --task-arn "AWS-RunShellScript" \
    --task-type "RUN_COMMAND" \
    --max-concurrency "5" \
    --max-errors "1" \
    --priority 1 \
    --task-parameters '{
        "commands": {
            "Values": [
                "systemctl stop nginx",
                "yum update nginx -y", 
                "systemctl start nginx",
                "systemctl status nginx"
            ]
        },
        "executionTimeout": {
            "Values": ["3600"]
        }
    }'
```

#### 2. Automation Tasks
```bash
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --targets "Key=WindowTargetIds,Values=12345678-1234-1234-1234-123456789012" \
    --task-arn "AWS-RestartEC2Instance" \
    --task-type "AUTOMATION" \
    --max-concurrency "1" \
    --max-errors "0" \
    --priority 2 \
    --task-parameters '{
        "InstanceId": {
            "Values": ["{{ TARGET_ID }}"]
        },
        "AutomationAssumeRole": {
            "Values": ["arn:aws:iam::123456789012:role/MaintenanceWindowRole"]
        }
    }'
```

#### 3. Lambda Tasks
```bash
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --task-arn "arn:aws:lambda:us-east-1:123456789012:function:MaintenanceFunction" \
    --task-type "LAMBDA" \
    --max-concurrency "1" \
    --max-errors "0" \
    --priority 3 \
    --task-parameters '{
        "Payload": {
            "Values": ["{\"windowId\": \"mw-0123456789abcdef0\", \"action\": \"maintenance\"}"]
        }
    }'
```

#### 4. Step Functions Tasks
```bash
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --task-arn "arn:aws:states:us-east-1:123456789012:stateMachine:MaintenanceWorkflow" \
    --task-type "STEP_FUNCTIONS" \
    --max-concurrency "1" \
    --max-errors "0" \
    --priority 4 \
    --task-parameters '{
        "Input": {
            "Values": ["{\"maintenanceWindow\": \"mw-0123456789abcdef0\"}"]
        }
    }'
```

### Execution Control

#### Concurrency and Error Handling
```yaml
MaxConcurrency:
  - Absolute number: "10"
  - Percentage: "25%"
  
MaxErrors:
  - Absolute number: "2"
  - Percentage: "10%"

Priority:
  - Range: 0-5 (0 = highest priority)
  - Execution: Higher priority tasks run first
```

#### Task Invocation Parameters
```json
{
    "TaskParameters": {
        "commands": {
            "Values": ["uptime", "df -h"]
        },
        "executionTimeout": {
            "Values": ["1800"]
        },
        "workingDirectory": {
            "Values": ["/tmp"]
        }
    },
    "TaskInvocationParameters": {
        "RunCommand": {
            "Comment": "Weekly system health check",
            "DocumentHash": "sha256:...",
            "DocumentHashType": "Sha256",
            "DocumentVersion": "1",
            "NotificationConfig": {
                "NotificationArn": "arn:aws:sns:us-east-1:123456789012:maintenance-notifications",
                "NotificationEvents": ["All"],
                "NotificationType": "Command"
            },
            "OutputS3BucketName": "maintenance-logs-bucket",
            "OutputS3KeyPrefix": "command-outputs/",
            "ServiceRoleArn": "arn:aws:iam::123456789012:role/MaintenanceWindowServiceRole",
            "TimeoutSeconds": 3600
        }
    }
}
```

### Monitoring and Logging

#### Execution History
```bash
# Get maintenance window executions
aws ssm describe-maintenance-window-executions \
    --window-id "mw-0123456789abcdef0" \
    --max-results 10

# Get task execution details
aws ssm describe-maintenance-window-execution-tasks \
    --window-execution-id "12345678-1234-1234-1234-123456789012"

# Get task invocation details
aws ssm describe-maintenance-window-execution-task-invocations \
    --window-execution-id "12345678-1234-1234-1234-123456789012" \
    --task-id "87654321-4321-4321-4321-210987654321"
```

#### CloudWatch Integration
```json
{
    "MetricName": "MaintenanceWindowExecutionStatus",
    "Namespace": "AWS/SSM-MaintenanceWindow",
    "Dimensions": [
        {
            "Name": "MaintenanceWindowId",
            "Value": "mw-0123456789abcdef0"
        }
    ],
    "Value": 1,
    "Unit": "Count"
}
```

### Real-world Use Cases

#### 1. Application Deployment Window
```yaml
Purpose: Deploy application updates
Schedule: Every Sunday 2 AM
Duration: 3 hours
Tasks:
  1. Stop application services
  2. Deploy new version from S3
  3. Update configuration
  4. Start services
  5. Health checks
  6. Rollback if needed
```

#### 2. Database Maintenance Window  
```yaml
Purpose: Database optimization and backup
Schedule: First Sunday of month 3 AM
Duration: 4 hours
Tasks:
  1. Create database snapshot
  2. Run VACUUM/ANALYZE operations
  3. Update statistics
  4. Clean up old log files
  5. Performance tuning
```

#### 3. Security Patching Window
```yaml
Purpose: Apply security patches
Schedule: Second Tuesday of month (Patch Tuesday + 1 week)
Duration: 6 hours
Tasks:
  1. Scan for available patches
  2. Apply security patches
  3. Reboot if required
  4. Verify services
  5. Update compliance status
```

### Advanced Scenarios

#### Multi-Phase Maintenance
```bash
# Phase 1: Pre-maintenance checks
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --task-arn "AWS-RunShellScript" \
    --task-type "RUN_COMMAND" \
    --priority 1 \
    --task-parameters '{
        "commands": {
            "Values": [
                "systemctl status application",
                "df -h",
                "free -m",
                "uptime"
            ]
        }
    }'

# Phase 2: Actual maintenance
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --task-arn "CustomMaintenanceDocument" \
    --task-type "RUN_COMMAND" \
    --priority 2 \
    --task-parameters '{
        "operation": {
            "Values": ["update-application"]
        }
    }'

# Phase 3: Post-maintenance validation
aws ssm register-task-with-maintenance-window \
    --window-id "mw-0123456789abcdef0" \
    --task-arn "AWS-RunShellScript" \
    --task-type "RUN_COMMAND" \
    --priority 3 \
    --task-parameters '{
        "commands": {
            "Values": [
                "curl -f http://localhost/health",
                "systemctl status application"
            ]
        }
    }'
```

### Best Practices

#### 1. Planning and Design
- Plan maintenance windows during low-traffic periods
- Coordinate with application teams and stakeholders
- Document maintenance procedures and rollback plans
- Test maintenance tasks in non-production environments

#### 2. Target Organization
- Use consistent tagging strategies for target selection
- Group similar resources for maintenance
- Consider dependencies between resources
- Plan for rolling maintenance across availability zones

#### 3. Error Handling
- Set appropriate concurrency and error thresholds
- Implement proper error notification
- Design idempotent maintenance tasks
- Plan for partial failure scenarios

#### 4. Security
- Use least privilege IAM roles
- Secure maintenance scripts and documents
- Audit maintenance window activities
- Encrypt sensitive maintenance data

#### 5. Monitoring
- Monitor maintenance window execution status
- Set up alerts for failed maintenance tasks
- Track maintenance window performance metrics
- Regular review of maintenance outcomes

---

## Automation

AWS Systems Manager Automation simplifies complex infrastructure management tasks by using predefined workflows called automation documents. It enables you to automate routine maintenance, deployment, and troubleshooting tasks at scale.

### Key Features
- **Pre-built Documents**: AWS-provided automation workflows
- **Custom Documents**: Create custom automation workflows
- **Multi-step Workflows**: Complex orchestration with error handling
- **Cross-service Integration**: Integrate with other AWS services
- **Approval Gates**: Human approval steps in workflows
- **Rate Control**: Control execution speed across resources

### Automation Documents

#### Document Structure
```yaml
schemaVersion: "0.3"
description: "Custom automation document example"
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  InstanceId:
    type: String
    description: "ID of the EC2 instance"
  AutomationAssumeRole:
    type: String
    description: "IAM role for automation execution"
    default: ""

mainSteps:
- name: "stopInstance" 
  action: "aws:executeAwsApi"
  inputs:
    Service: "ec2"
    Api: "StopInstances"
    InstanceIds:
    - "{{ InstanceId }}"
  
- name: "waitForInstanceStopped"
  action: "aws:waitForAwsResourceProperty"
  inputs:
    Service: "ec2"
    Api: "DescribeInstances"
    InstanceIds:
    - "{{ InstanceId }}"
    PropertySelector: "$.Reservations[0].Instances[0].State.Name"
    DesiredValues:
    - "stopped"
```

#### AWS-Managed Automation Documents
```yaml
Common Documents:
  - AWS-RestartEC2Instance: Restart EC2 instances
  - AWS-StopEC2Instance: Stop EC2 instances  
  - AWS-CreateImage: Create AMI from instance
  - AWS-CopySnapshot: Copy EBS snapshots
  - AWS-DeleteSnapshot: Delete EBS snapshots
  - AWS-UpdateLinuxAmi: Update Linux AMI
  - AWS-UpdateWindowsAmi: Update Windows AMI
  - AWS-SetupInventory: Configure inventory collection
  - AWS-ConfigureS3BucketLogging: Enable S3 logging
  - AWS-PublishSNSNotification: Send SNS notifications
```

### Automation Actions

#### 1. aws:executeAwsApi
Execute any AWS API operation.
```yaml
- name: "createSnapshot"
  action: "aws:executeAwsApi"
  inputs:
    Service: "ec2"
    Api: "CreateSnapshot"
    VolumeId: "{{ VolumeId }}"
    Description: "Automated snapshot - {{ global:DATE_TIME }}"
  outputs:
  - Name: "SnapshotId"
    Selector: "$.SnapshotId"
    Type: "String"
```

#### 2. aws:executeScript
Execute Python or PowerShell scripts.
```yaml
- name: "processData"
  action: "aws:executeScript"
  inputs:
    Runtime: "python3.8"
    Handler: "script_handler"
    Script: |
      def script_handler(events, context):
          import boto3
          ec2 = boto3.client('ec2')
          instances = ec2.describe_instances()
          return {'instanceCount': len(instances['Reservations'])}
  outputs:
  - Name: "instanceCount"
    Selector: "$.Payload.instanceCount"
    Type: "Integer"
```

#### 3. aws:executeStateMachine
Execute AWS Step Functions state machines.
```yaml
- name: "executeWorkflow"
  action: "aws:executeStateMachine"
  inputs:
    stateMachineArn: "arn:aws:states:us-east-1:123456789012:stateMachine:ProcessingWorkflow"
    input: |
      {
        "inputData": "{{ inputParameter }}"
      }
```

#### 4. aws:approve
Add manual approval steps.
```yaml
- name: "approveProduction"
  action: "aws:approve"
  inputs:
    NotificationArn: "arn:aws:sns:us-east-1:123456789012:approval-topic"
    Message: "Approve production deployment?"
    MinRequiredApprovals: 2
    Approvers:
    - "arn:aws:iam::123456789012:user/manager1"
    - "arn:aws:iam::123456789012:user/manager2"
```

#### 5. aws:branch
Conditional branching based on input values.
```yaml
- name: "checkEnvironment"
  action: "aws:branch"
  inputs:
    Choices:
    - Variable: "{{ Environment }}"
      StringEquals: "production"
      NextStep: "productionDeployment"
    - Variable: "{{ Environment }}"
      StringEquals: "staging"  
      NextStep: "stagingDeployment"
    Default: "developmentDeployment"
```

### Execution Modes

#### 1. Simple Execution
Execute automation on a single resource or set of parameters.
```bash
aws ssm start-automation-execution \
    --document-name "AWS-RestartEC2Instance" \
    --parameters "InstanceId=i-0123456789abcdef0,AutomationAssumeRole=arn:aws:iam::123456789012:role/AutomationRole"
```

#### 2. Rate Control Execution
Execute automation across multiple targets with rate control.
```bash
aws ssm start-automation-execution \
    --document-name "AWS-RestartEC2Instance" \
    --parameters "AutomationAssumeRole=arn:aws:iam::123456789012:role/AutomationRole" \
    --targets "Key=tag:Environment,Values=production" \
    --max-concurrency "25%" \
    --max-errors "10%"
```

### Real-world Automation Examples

#### 1. Automated AMI Creation and Cleanup
```yaml
schemaVersion: "0.3"
description: "Create AMI and clean up old AMIs"
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  InstanceId:
    type: String
  RetentionDays:
    type: String
    default: "30"
    
mainSteps:
- name: "createAMI"
  action: "aws:executeAwsApi"
  inputs:
    Service: "ec2"
    Api: "CreateImage"
    InstanceId: "{{ InstanceId }}"
    Name: "AutomatedAMI-{{ global:DATE_TIME }}"
    Description: "Automated AMI creation"
    NoReboot: true
  outputs:
  - Name: "ImageId"
    Selector: "$.ImageId"
    Type: "String"

- name: "waitForAMI"
  action: "aws:waitForAwsResourceProperty"
  inputs:
    Service: "ec2"
    Api: "DescribeImages"
    ImageIds:
    - "{{ createAMI.ImageId }}"
    PropertySelector: "$.Images[0].State"
    DesiredValues:
    - "available"

- name: "cleanupOldAMIs"
  action: "aws:executeScript"
  inputs:
    Runtime: "python3.8"
    Handler: "cleanup_amis"
    Script: |
      def cleanup_amis(events, context):
          import boto3
          from datetime import datetime, timedelta
          
          ec2 = boto3.client('ec2')
          retention_days = int(events['RetentionDays'])
          cutoff_date = datetime.now() - timedelta(days=retention_days)
          
          images = ec2.describe_images(Owners=['self'])
          deleted_amis = []
          
          for image in images['Images']:
              creation_date = datetime.strptime(image['CreationDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
              if creation_date < cutoff_date and 'AutomatedAMI' in image['Name']:
                  try:
                      ec2.deregister_image(ImageId=image['ImageId'])
                      deleted_amis.append(image['ImageId'])
                  except Exception as e:
                      print(f"Error deleting {image['ImageId']}: {e}")
          
          return {'deletedAMIs': deleted_amis}
    InputPayload:
      RetentionDays: "{{ RetentionDays }}"
```

#### 2. Automated Disaster Recovery Failover
```yaml
schemaVersion: "0.3"
description: "Automated disaster recovery failover"
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  PrimaryRegion:
    type: String
    default: "us-east-1"
  SecondaryRegion:
    type: String
    default: "us-west-2"
    
mainSteps:
- name: "checkPrimaryHealth"
  action: "aws:executeScript"
  inputs:
    Runtime: "python3.8"
    Handler: "health_check"
    Script: |
      def health_check(events, context):
          import boto3
          import requests
          
          # Check application health endpoint
          try:
              response = requests.get('https://app.example.com/health', timeout=10)
              return {'healthy': response.status_code == 200}
          except:
              return {'healthy': False}
  outputs:
  - Name: "isHealthy"
    Selector: "$.Payload.healthy"
    Type: "Boolean"

- name: "initiateFailover"
  action: "aws:branch"
  inputs:
    Choices:
    - Variable: "{{ checkPrimaryHealth.isHealthy }}"
      BooleanEquals: false
      NextStep: "failoverToSecondary"
    Default: "noFailoverNeeded"

- name: "failoverToSecondary"
  action: "aws:executeAwsApi"
  inputs:
    Service: "route53"
    Api: "ChangeResourceRecordSets"
    HostedZoneId: "Z123456789"
    ChangeBatch:
      Changes:
      - Action: "UPSERT"
        ResourceRecordSet:
          Name: "app.example.com"
          Type: "CNAME"
          TTL: 60
          ResourceRecords:
          - Value: "app-dr.example.com"

- name: "noFailoverNeeded"
  action: "aws:executeAwsApi"
  inputs:
    Service: "sns"
    Api: "Publish"
    TopicArn: "arn:aws:sns:us-east-1:123456789012:alerts"
    Message: "Health check passed - no failover needed"
```

#### 3. Automated Security Group Remediation
```yaml
schemaVersion: "0.3"
description: "Remove insecure security group rules"
assumeRole: "{{ AutomationAssumeRole }}"
parameters:
  SecurityGroupId:
    type: String
    
mainSteps:
- name: "analyzeSecurityGroup"
  action: "aws:executeScript"
  inputs:
    Runtime: "python3.8"
    Handler: "analyze_sg"
    Script: |
      def analyze_sg(events, context):
          import boto3
          
          ec2 = boto3.client('ec2')
          sg_id = events['SecurityGroupId']
          
          response = ec2.describe_security_groups(GroupIds=[sg_id])
          sg = response['SecurityGroups'][0]
          
          insecure_rules = []
          for rule in sg['IpPermissions']:
              for ip_range in rule.get('IpRanges', []):
                  if ip_range.get('CidrIp') == '0.0.0.0/0':
                      insecure_rules.append({
                          'IpProtocol': rule['IpProtocol'],
                          'FromPort': rule.get('FromPort', 0),
                          'ToPort': rule.get('ToPort', 0),
                          'CidrIp': '0.0.0.0/0'
                      })
          
          return {'insecureRules': insecure_rules}
    InputPayload:
      SecurityGroupId: "{{ SecurityGroupId }}"
  outputs:
  - Name: "insecureRules"
    Selector: "$.Payload.insecureRules"
    Type: "StringList"

- name: "removeInsecureRules"
  action: "aws:executeAwsApi"
  inputs:
    Service: "ec2"
    Api: "RevokeSecurityGroupIngress"
    GroupId: "{{ SecurityGroupId }}"
    IpPermissions: "{{ analyzeSecurityGroup.insecureRules }}"
  isEnd: false
  onFailure: "Continue"

- name: "notifyRemediation"
  action: "aws:executeAwsApi"
  inputs:
    Service: "sns"
    Api: "Publish"
    TopicArn: "arn:aws:sns:us-east-1:123456789012:security-alerts"
    Message: "Removed insecure rules from security group {{ SecurityGroupId }}"
```

### Integration with Other Services

#### 1. EventBridge Integration
```json
{
  "Rules": [
    {
      "Name": "AutomateOnEC2StateChange",
      "EventPattern": {
        "source": ["aws.ec2"],
        "detail-type": ["EC2 Instance State-change Notification"],
        "detail": {
          "state": ["terminated"]
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:ssm:us-east-1:123456789012:automation-definition/CleanupResources",
          "InputTransformer": {
            "InputPathsMap": {
              "instance": "$.detail.instance-id"
            },
            "InputTemplate": "{\"InstanceId\": \"<instance>\"}"
          }
        }
      ]
    }
  ]
}
```

#### 2. Lambda Integration
```python
import boto3
import json

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Start automation execution
    response = ssm.start_automation_execution(
        DocumentName='CustomMaintenanceAutomation',
        Parameters={
            'InstanceId': ['i-0123456789abcdef0'],
            'AutomationAssumeRole': ['arn:aws:iam::123456789012:role/AutomationRole']
        }
    )
    
    execution_id = response['AutomationExecutionId']
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'executionId': execution_id,
            'message': 'Automation started successfully'
        })
    }
```

### Monitoring and Troubleshooting

#### Execution Status Monitoring
```bash
# Get automation execution status
aws ssm describe-automation-executions \
    --filters "Key=DocumentName,Values=AWS-RestartEC2Instance"

# Get execution details
aws ssm get-automation-execution \
    --automation-execution-id "12345678-1234-1234-1234-123456789012"

# Get step execution details
aws ssm describe-automation-step-executions \
    --automation-execution-id "12345678-1234-1234-1234-123456789012"
```

#### CloudWatch Metrics
```yaml
Automation Metrics:
  - AWS/SSM-RunCommand/CommandsSucceeded
  - AWS/SSM-RunCommand/CommandsFailed
  - AWS/SSM-RunCommand/CommandsTimedOut
  - AWS/SSM-RunCommand/CommandsCancelled
```

### Best Practices

#### 1. Document Design
- Use descriptive names and documentation
- Implement proper error handling
- Add validation steps
- Use parameters for flexibility

#### 2. Security
- Use least privilege IAM roles
- Validate input parameters
- Audit automation executions
- Encrypt sensitive data

#### 3. Testing
- Test automations in non-production environments
- Use simulation mode when available
- Implement rollback procedures
- Monitor execution metrics

#### 4. Operations
- Use tags for organization
- Implement approval gates for critical operations
- Monitor automation performance
- Regular review and optimization

---

## Inventory

AWS Systems Manager Inventory collects metadata from your managed instances about installed applications, AWS components, instance details, network configurations, and Windows updates.

### Key Features
- **Automated Collection**: Gather system metadata automatically
- **Customizable**: Configure what data to collect
- **Searchable**: Query inventory data across instances
- **Compliance**: Track software inventory for compliance
- **Integration**: Works with other Systems Manager capabilities

### Inventory Types

#### Built-in Inventory Types
```yaml
AWS:Application:
  - Name: Installed applications
  - Data: Application name, version, publisher, install date
  - Platforms: Windows, Linux, macOS

AWS:AWSComponent:
  - Name: AWS agent information
  - Data: SSM Agent, CloudWatch agent, Inspector agent
  - Platforms: All

AWS:File:
  - Name: File information
  - Data: File path, size, creation date, checksum
  - Platforms: All (configurable paths)

AWS:Network:
  - Name: Network configuration
  - Data: IP addresses, MAC addresses, DNS, gateways
  - Platforms: All

AWS:WindowsUpdate:
  - Name: Windows update information
  - Data: Update ID, title, install date, classification
  - Platforms: Windows only

AWS:InstanceInformation:
  - Name: Instance details
  - Data: Instance ID, type, platform, IP addresses
  - Platforms: All

AWS:Service:
  - Name: Service information  
  - Data: Service name, status, start type
  - Platforms: Windows

AWS:Registry:
  - Name: Windows registry information
  - Data: Registry key paths and values
  - Platforms: Windows only

AWS:ComplianceItem:
  - Name: Compliance status
  - Data: Compliance type, status, severity
  - Platforms: All
```

### Configuring Inventory Collection

#### Basic Inventory Setup
```bash
# Associate inventory collection with instances
aws ssm put-inventory \
    --instance-id "i-0123456789abcdef0" \
    --items file://inventory-items.json
```

#### Inventory Items Configuration
```json
[
  {
    "TypeName": "AWS:Application",
    "SchemaVersion": "1.1",
    "CaptureTime": "2024-01-15T10:30:00Z"
  },
  {
    "TypeName": "AWS:File",
    "SchemaVersion": "1.1", 
    "CaptureTime": "2024-01-15T10:30:00Z",
    "Context": {
      "Path": "/etc",
      "Pattern": "*",
      "Recursive": true,
      "DirScanLimit": 1000,
      "FileScanLimit": 500
    }
  },
  {
    "TypeName": "AWS:Network",
    "SchemaVersion": "1.1",
    "CaptureTime": "2024-01-15T10:30:00Z"
  }
]
```

#### State Manager Association for Inventory
```bash
aws ssm create-association \
    --name "AWS-GatherSoftwareInventory" \
    --targets "Key=tag:Environment,Values=production" \
    --schedule-expression "rate(1 day)" \
    --association-name "DailyInventoryCollection" \
    --parameters '{
        "applications": ["Enabled"],
        "awsComponents": ["Enabled"],
        "networkConfig": ["Enabled"],
        "windowsUpdates": ["Enabled"],
        "instanceDetailedInformation": ["Enabled"],
        "customInventory": ["Enabled"]
    }'
```

### Custom Inventory Types

#### Creating Custom Inventory
```json
{
  "TypeName": "Custom:DatabaseInfo",
  "SchemaVersion": "1.0",
  "Content": [
    {
      "Name": "PostgreSQL",
      "Version": "13.7",
      "Status": "Running",
      "Port": "5432",
      "DataDirectory": "/var/lib/postgresql/13/main",
      "ConfigFile": "/etc/postgresql/13/main/postgresql.conf"
    },
    {
      "Name": "Redis",
      "Version": "6.2.7",
      "Status": "Running", 
      "Port": "6379",
      "ConfigFile": "/etc/redis/redis.conf"
    }
  ]
}
```

#### Custom Inventory Collection Script
```bash
#!/bin/bash
# Custom inventory collection script

# Collect database information
collect_database_info() {
    local db_info='[]'
    
    # Check PostgreSQL
    if systemctl is-active --quiet postgresql; then
        version=$(postgres --version | awk '{print $3}')
        db_info=$(echo "$db_info" | jq '. += [{
            "Name": "PostgreSQL",
            "Version": "'$version'",
            "Status": "Running",
            "Port": "5432"
        }]')
    fi
    
    # Check Redis
    if systemctl is-active --quiet redis; then
        version=$(redis-server --version | awk '{print $3}' | cut -d'=' -f2)
        db_info=$(echo "$db_info" | jq '. += [{
            "Name": "Redis", 
            "Version": "'$version'",
            "Status": "Running",
            "Port": "6379"
        }]')
    fi
    
    echo "$db_info"
}

# Send custom inventory to Systems Manager
INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id)
DATABASE_INFO=$(collect_database_info)

aws ssm put-inventory \
    --instance-id "$INSTANCE_ID" \
    --items '[{
        "TypeName": "Custom:DatabaseInfo",
        "SchemaVersion": "1.0",
        "CaptureTime": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'",
        "Content": '$DATABASE_INFO'
    }]'
```

### Querying Inventory Data

#### Using AWS CLI
```bash
# Get inventory for specific instance
aws ssm list-inventory-entries \
    --instance-id "i-0123456789abcdef0" \
    --type-name "AWS:Application" \
    --max-results 50

# Get inventory summary
aws ssm get-inventory-schema \
    --type-name "AWS:Application"

# Query across multiple instances
aws ssm get-inventory \
    --filters "Key=AWS:InstanceInformation.InstanceStatus,Values=Active,Type=Equal" \
    --result-attributes "AWS:Application.Name,AWS:Application.Version"
```

#### Resource Data Sync
```bash
# Create resource data sync for centralized querying
aws ssm create-resource-data-sync \
    --sync-name "InventoryDataSync" \
    --s3-destination '{
        "BucketName": "inventory-data-bucket",
        "Prefix": "inventory-data/",
        "SyncFormat": "JsonSerDe",
        "Region": "us-east-1"
    }'
```

### Inventory Analytics

#### Amazon Athena Integration
```sql
-- Query inventory data in S3 using Athena
CREATE EXTERNAL TABLE inventory_applications (
  instanceid string,
  name string,
  version string,
  publisher string,
  installdate string
)
STORED AS SERDE 'org.openx.data.jsonserde.JsonSerDe'
LOCATION 's3://inventory-data-bucket/inventory-data/AWS:Application/'

-- Find instances with specific software
SELECT instanceid, name, version 
FROM inventory_applications 
WHERE name LIKE '%Java%'

-- Count software installations
SELECT name, COUNT(*) as instance_count
FROM inventory_applications 
GROUP BY name 
ORDER BY instance_count DESC
```

#### AWS Config Integration
```yaml
Config Rules for Inventory:
  - required-software-installed: Check if required software is installed
  - approved-software-only: Ensure only approved software is installed
  - software-version-compliance: Check software version compliance
```

### Compliance and Reporting

#### Compliance Dashboard Queries
```bash
# Get compliance summary
aws ssm list-compliance-items \
    --resource-ids "i-0123456789abcdef0" \
    --resource-types "ManagedInstance" \
    --filters "Key=ComplianceType,Values=Association,Type=EQUAL"

# Get compliance summary by patch group
aws ssm list-compliance-summary-by-compliance-type \
    --compliance-type "Patch"
```

#### Custom Compliance Rules
```json
{
  "ComplianceType": "Custom:SecurityCompliance",
  "ResourceType": "ManagedInstance", 
  "ResourceId": "i-0123456789abcdef0",
  "ComplianceStatus": "COMPLIANT",
  "ExecutionSummary": {
    "ExecutionTime": "2024-01-15T10:30:00Z",
    "ExecutionId": "12345678-1234-1234-1234-123456789012",
    "ExecutionType": "Command"
  },
  "Items": [
    {
      "ComplianceType": "Custom:SecurityCompliance",
      "Status": "COMPLIANT",
      "Severity": "HIGH",
      "Title": "Antivirus Software Check",
      "Details": {
        "AntivirusName": "ClamAV",
        "Version": "0.103.6",
        "LastUpdate": "2024-01-15T09:00:00Z"
      }
    }
  ]
}
```

### Use Cases

#### 1. Software License Management
```bash
# Track licensed software installations
aws ssm get-inventory \
    --filters "Key=AWS:Application.Name,Values=Microsoft Office,Adobe,Oracle,Type=Equal" \
    --result-attributes "AWS:Application.Name,AWS:Application.Version,AWS:InstanceInformation.InstanceId"
```

#### 2. Security Compliance
```python
import boto3
import json

def check_security_compliance(instance_ids):
    ssm = boto3.client('ssm')
    compliance_results = []
    
    for instance_id in instance_ids:
        # Get application inventory
        response = ssm.list_inventory_entries(
            InstanceId=instance_id,
            TypeName='AWS:Application'
        )
        
        applications = [entry['Name'] for entry in response['Entries']]
        
        # Check for security tools
        security_tools = ['ClamAV', 'Nessus', 'OSSEC']
        installed_tools = [tool for tool in security_tools if tool in applications]
        
        compliance_results.append({
            'InstanceId': instance_id,
            'SecurityTools': installed_tools,
            'Compliant': len(installed_tools) >= 2
        })
    
    return compliance_results
```

#### 3. Patch Compliance Tracking
```bash
# Check Windows update status
aws ssm list-inventory-entries \
    --instance-id "i-0123456789abcdef0" \
    --type-name "AWS:WindowsUpdate" \
    --filters "Key=InstalledTime,Values=2024-01,Type=BeginWith"
```

### Integration Examples

#### 1. Lambda Function for Inventory Processing
```python
import boto3
import json
from datetime import datetime

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Get all managed instances
    response = ssm.describe_instance_information()
    instances = response['InstanceInformationList']
    
    inventory_summary = {}
    
    for instance in instances:
        instance_id = instance['InstanceId']
        
        # Get application inventory
        try:
            app_response = ssm.list_inventory_entries(
                InstanceId=instance_id,
                TypeName='AWS:Application'
            )
            
            applications = [entry['Name'] for entry in app_response['Entries']]
            inventory_summary[instance_id] = {
                'Platform': instance['PlatformType'],
                'ApplicationCount': len(applications),
                'Applications': applications[:10]  # Top 10
            }
        except Exception as e:
            inventory_summary[instance_id] = {
                'Error': str(e)
            }
    
    # Store results in S3 or send to monitoring system
    return {
        'statusCode': 200,
        'body': json.dumps(inventory_summary, default=str)
    }
```

#### 2. EventBridge Rule for Inventory Changes
```json
{
  "Rules": [
    {
      "Name": "InventoryChangeDetection",
      "EventPattern": {
        "source": ["aws.ssm"],
        "detail-type": ["Systems Manager Inventory State Change"],
        "detail": {
          "state": ["CHANGED"],
          "inventory-type": ["AWS:Application"]
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:lambda:us-east-1:123456789012:function:ProcessInventoryChange"
        }
      ]
    }
  ]
}
```

### Best Practices

#### 1. Collection Strategy
- Schedule inventory collection during low-usage periods
- Use appropriate collection frequency based on change rate
- Configure only necessary inventory types
- Use tags to organize inventory data

#### 2. Data Management
- Set up Resource Data Sync for centralized analytics
- Implement data retention policies
- Use compression and partitioning for large datasets
- Regular cleanup of obsolete inventory data

#### 3. Performance
- Limit file inventory scope to essential directories
- Use filters to reduce data collection volume
- Monitor inventory collection performance
- Optimize custom inventory scripts

#### 4. Security
- Encrypt inventory data in transit and at rest
- Control access to inventory data
- Audit inventory access and changes
- Sanitize sensitive data in custom inventory

---

## State Manager

AWS Systems Manager State Manager is a configuration management service that automates the process of keeping your Amazon EC2 and hybrid infrastructure in a defined state.

### Key Features
- **Desired State Configuration**: Define and maintain desired configuration state
- **Scheduled Execution**: Automatically run configurations on schedule
- **Compliance Monitoring**: Track configuration drift and compliance
- **Multi-platform Support**: Works across Windows, Linux, and macOS
- **Document-based**: Uses Systems Manager documents for configuration

### Core Concepts

#### Association
An association defines the configuration to apply to a set of targets on a schedule.

```yaml
Association Components:
  - Document: What to execute (SSM document)
  - Targets: Which resources to configure
  - Schedule: When to execute
  - Parameters: Configuration parameters
  - Output Location: Where to store execution logs
```

#### Association States
```yaml
States:
  - Pending: Association created but not executed
  - Success: Last execution completed successfully
  - Failed: Last execution failed
  - Associated: Association is active
  - Disassociated: Association is inactive
```

### Creating Associations

#### Basic Association
```bash
aws ssm create-association \
    --name "AWS-RunShellScript" \
    --targets "Key=tag:Environment,Values=production" \
    --schedule-expression "rate(30 minutes)" \
    --parameters '{
        "commands": [
            "systemctl status nginx",
            "curl -f http://localhost/health || systemctl restart nginx"
        ]
    }'
```

#### Advanced Association Configuration
```json
{
    "Name": "AWS-ConfigureAWSPackage",
    "DocumentVersion": "1",
    "Targets": [
        {
            "Key": "tag:Role",
            "Values": ["WebServer"]
        }
    ],
    "ScheduleExpression": "cron(0 2 ? * SUN *)",
    "AssociationName": "InstallCloudWatchAgent",
    "Parameters": {
        "action": ["Install"],
        "name": ["AmazonCloudWatchAgent"],
        "version": ["latest"]
    },
    "OutputLocation": {
        "S3Location": {
            "OutputS3BucketName": "state-manager-logs",
            "OutputS3KeyPrefix": "associations/"
        }
    },
    "MaxConcurrency": "25%",
    "MaxErrors": "10%",
    "ComplianceSeverity": "HIGH",
    "SyncCompliance": "AUTO"
}
```

### Common Use Cases

#### 1. Software Installation and Updates
```bash
# Install and maintain CloudWatch agent
aws ssm create-association \
    --name "AWS-ConfigureAWSPackage" \
    --targets "Key=tag:Monitoring,Values=enabled" \
    --schedule-expression "rate(1 day)" \
    --parameters '{
        "action": ["Install"],
        "name": ["AmazonCloudWatchAgent"],
        "version": ["latest"]
    }' \
    --association-name "MaintainCloudWatchAgent"
```

#### 2. Configuration Management
```yaml
# Custom document for web server configuration
schemaVersion: "2.2"
description: "Configure nginx web server"
parameters:
  ServerName:
    type: String
    description: "Server name for nginx configuration"
    default: "example.com"
  
mainSteps:
- action: "aws:runShellScript"
  name: "configureNginx"
  inputs:
    timeoutSeconds: "300"
    runCommand:
    - "#!/bin/bash"
    - "cat > /etc/nginx/sites-available/default << EOF"
    - "server {"
    - "    listen 80;"
    - "    server_name {{ ServerName }};"
    - "    location / {"
    - "        root /var/www/html;"
    - "        index index.html;"
    - "    }"
    - "}"
    - "EOF"
    - "nginx -t && systemctl reload nginx"
```

#### 3. Security Hardening
```bash
# Security hardening association
aws ssm create-association \
    --name "CustomSecurityHardening" \
    --targets "Key=tag:SecurityLevel,Values=high" \
    --schedule-expression "rate(7 days)" \
    --parameters '{
        "actions": [
            "disable-unused-services",
            "configure-firewall",
            "update-security-settings"
        ]
    }' \
    --compliance-severity "CRITICAL"
```

### Compliance Management

#### Compliance Types
```yaml
Built-in Compliance Types:
  - Association: Document execution compliance
  - Patch: Patch installation compliance
  - Custom: User-defined compliance rules

Compliance Statuses:
  - COMPLIANT: Target meets requirements
  - NON_COMPLIANT: Target doesn't meet requirements
  - UNSPECIFIED_DATA: Insufficient data
```

#### Monitoring Compliance
```bash
# Get compliance summary
aws ssm list-compliance-summary-by-compliance-type \
    --compliance-type "Association"

# Get detailed compliance information
aws ssm list-compliance-items \
    --resource-ids "i-0123456789abcdef0" \
    --resource-types "ManagedInstance" \
    --filters "Key=ComplianceType,Values=Association,Type=EQUAL"

# Get compliance by resource type
aws ssm list-compliance-summary-by-resource-type \
    --resource-type "ManagedInstance"
```

#### Custom Compliance Rules
```python
import boto3
import json

def lambda_handler(event, context):
    ssm = boto3.client('ssm')
    
    # Custom compliance check for disk space
    instances = ['i-0123456789abcdef0', 'i-0987654321fedcba0']
    
    for instance_id in instances:
        try:
            # Run disk space check
            response = ssm.send_command(
                InstanceIds=[instance_id],
                DocumentName='AWS-RunShellScript',
                Parameters={
                    'commands': ['df -h / | tail -1 | awk \'{print $5}\' | sed \'s/%//\'']
                }
            )
            
            command_id = response['Command']['CommandId']
            
            # Wait for command completion and get results
            # (In practice, you'd use a separate Lambda or polling mechanism)
            
            # Simulate compliance check result
            disk_usage = 85  # Example: 85% disk usage
            
            compliance_status = 'COMPLIANT' if disk_usage < 90 else 'NON_COMPLIANT'
            
            # Put compliance item
            ssm.put_compliance_items(
                ResourceId=instance_id,
                ResourceType='ManagedInstance',
                ComplianceType='Custom:DiskSpace',
                ExecutionSummary={
                    'ExecutionTime': '2024-01-15T10:30:00Z',
                    'ExecutionId': command_id,
                    'ExecutionType': 'Command'
                },
                Items=[
                    {
                        'ComplianceType': 'Custom:DiskSpace',
                        'Status': compliance_status,
                        'Severity': 'HIGH' if compliance_status == 'NON_COMPLIANT' else 'INFORMATIONAL',
                        'Title': 'Disk Space Check',
                        'Details': {
                            'DiskUsage': f'{disk_usage}%',
                            'Threshold': '90%'
                        }
                    }
                ]
            )
            
        except Exception as e:
            print(f"Error checking compliance for {instance_id}: {e}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Compliance check completed')
    }
```

### Association Execution Control

#### Rate Control Settings
```json
{
    "MaxConcurrency": "25%",
    "MaxErrors": "10%",
    "ComplianceSeverity": "HIGH",
    "SyncCompliance": "AUTO"
}
```

#### Execution Targets
```bash
# Target by instance IDs
--targets "Key=InstanceIds,Values=i-0123456789abcdef0,i-0987654321fedcba0"

# Target by tags
--targets "Key=tag:Environment,Values=production,staging"

# Target by resource groups
--targets "Key=resource-groups:Name,Values=WebServerGroup"

# Target all managed instances
--targets "Key=tag:SSMManaged,Values=true"
```

### Document Integration

#### Using AWS-Managed Documents
```bash
# Common AWS-managed documents for State Manager
AWS-RunShellScript              # Execute shell commands
AWS-RunPowerShellScript        # Execute PowerShell commands  
AWS-ConfigureAWSPackage        # Install/configure AWS packages
AWS-InstallApplication         # Install applications
AWS-ConfigureCloudWatchOnEC2Instance  # Configure CloudWatch
AWS-UpdateSSMAgent             # Update SSM Agent
AWS-ApplyPatchBaseline         # Apply patch baselines
```

#### Custom Document Example
```yaml
schemaVersion: "2.2"
description: "Configure application monitoring"
parameters:
  ApplicationName:
    type: String
    description: "Name of the application to monitor"
  MonitoringInterval:
    type: String
    description: "Monitoring interval in seconds"
    default: "60"
    
mainSteps:
- action: "aws:runShellScript"
  name: "setupMonitoring"
  inputs:
    timeoutSeconds: "300"
    runCommand:
    - "#!/bin/bash"
    - "APP_NAME='{{ ApplicationName }}'"
    - "INTERVAL='{{ MonitoringInterval }}'"
    - "# Create monitoring script"
    - "cat > /usr/local/bin/monitor-${APP_NAME}.sh << 'EOF'"
    - "#!/bin/bash"
    - "while true; do"
    - "  if pgrep -f ${APP_NAME} > /dev/null; then"
    - "    echo \"$(date): ${APP_NAME} is running\" >> /var/log/${APP_NAME}-monitor.log"
    - "  else"
    - "    echo \"$(date): ${APP_NAME} is not running, attempting restart\" >> /var/log/${APP_NAME}-monitor.log"
    - "    systemctl restart ${APP_NAME}"
    - "  fi"
    - "  sleep ${INTERVAL}"
    - "done"
    - "EOF"
    - "chmod +x /usr/local/bin/monitor-${APP_NAME}.sh"
    - "# Create systemd service"
    - "cat > /etc/systemd/system/${APP_NAME}-monitor.service << 'EOF'"
    - "[Unit]"
    - "Description=${APP_NAME} Monitor Service"
    - "After=network.target"
    - ""
    - "[Service]"
    - "Type=simple"
    - "ExecStart=/usr/local/bin/monitor-${APP_NAME}.sh"
    - "Restart=always"
    - ""
    - "[Install]"
    - "WantedBy=multi-user.target"
    - "EOF"
    - "systemctl daemon-reload"
    - "systemctl enable ${APP_NAME}-monitor.service"
    - "systemctl start ${APP_NAME}-monitor.service"
```

### Monitoring and Reporting

#### CloudWatch Integration
```yaml
State Manager Metrics:
  - AWS/SSM/AssociationSuccess
  - AWS/SSM/AssociationFailed
  - AWS/SSM/ComplianceByAssociation
  - AWS/SSM/ComplianceByConfigType
  - AWS/SSM/ComplianceBySeverity
```

#### EventBridge Integration
```json
{
  "Rules": [
    {
      "Name": "StateManagerComplianceChange",
      "EventPattern": {
        "source": ["aws.ssm"],
        "detail-type": ["EC2 State Manager Association State Change"],
        "detail": {
          "state": ["Failed", "Success"],
          "association-id": ["12345678-1234-1234-1234-123456789012"]
        }
      },
      "Targets": [
        {
          "Id": "1",
          "Arn": "arn:aws:sns:us-east-1:123456789012:state-manager-alerts"
        }
      ]
    }
  ]
}
```

#### Association History
```bash
# Get association execution history
aws ssm describe-association-execution-history \
    --association-id "12345678-1234-1234-1234-123456789012" \
    --max-results 10

# Get association execution targets
aws ssm describe-association-execution-targets \
    --association-id "12345678-1234-1234-1234-123456789012" \
    --execution-id "87654321-4321-4321-4321-210987654321"
```

### Troubleshooting Common Issues

#### 1. Association Execution Failures
```yaml
Common Causes:
  - SSM Agent not running or outdated
  - Insufficient IAM permissions
  - Network connectivity issues
  - Document syntax errors
  - Target instances not managed

Troubleshooting Steps:
  1. Check SSM Agent status
  2. Verify IAM roles and policies
  3. Review association execution history
  4. Check instance connectivity
  5. Validate document syntax
```

#### 2. Compliance Issues
```bash
# Debug compliance status
aws ssm get-compliance-summary

# Check specific resource compliance
aws ssm list-resource-compliance-summaries \
    --filters "Key=OverallSeverity,Values=CRITICAL,Type=EQUAL"

# Get compliance details
aws ssm list-compliance-items \
    --resource-ids "i-0123456789abcdef0" \
    --resource-types "ManagedInstance"
```

### Best Practices

#### 1. Association Design
- Use descriptive association names
- Set appropriate schedules based on requirements
- Configure proper rate control settings
- Use tags for organized targeting

#### 2. Document Management
- Version control custom documents
- Test documents thoroughly before deployment
- Use parameters for flexibility
- Implement proper error handling

#### 3. Monitoring
- Set up CloudWatch alarms for failures
- Monitor compliance trends
- Regular review of association performance
- Automated notification of compliance issues

#### 4. Security
- Follow least privilege principle for IAM roles
- Encrypt sensitive parameters
- Audit association changes
- Use secure document sharing practices

---