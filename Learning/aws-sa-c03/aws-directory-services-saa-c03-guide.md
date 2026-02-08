# AWS Directory Services - SAA-C03 Certification Guide

## Table of Contents
1. [Overview](#overview)
2. [AWS Managed Microsoft AD](#aws-managed-microsoft-ad)
3. [AD Connector](#ad-connector)
4. [Simple AD](#simple-ad)
5. [Amazon Cognito](#amazon-cognito)
6. [Integration with AWS Services](#integration-with-aws-services)
7. [Security and Compliance](#security-and-compliance)
8. [Monitoring and Troubleshooting](#monitoring-and-troubleshooting)
9. [Cost Optimization](#cost-optimization)
10. [Best Practices](#best-practices)
11. [Common Exam Scenarios](#common-exam-scenarios)
12. [AWS CLI Commands Reference](#aws-cli-commands-reference)
13. [Hands-On Labs](#hands-on-labs)

---

## Overview

AWS Directory Services provides multiple ways to use Microsoft Active Directory with AWS services. It enables you to run directory-aware workloads in the AWS Cloud and manage users and groups.

### Key Services:
- **AWS Managed Microsoft AD**: Fully managed Microsoft Active Directory
- **AD Connector**: Directory gateway for existing on-premises AD
- **Simple AD**: Simple, cost-effective AD-compatible directory
- **Amazon Cognito**: Identity service for web and mobile applications

### Use Cases:
- Single sign-on (SSO) to AWS applications
- Domain joining EC2 instances
- LDAP authentication for applications
- User and group management
- Policy enforcement

---

## AWS Managed Microsoft AD

### Overview
AWS Managed Microsoft AD is a fully managed service that provides an actual Microsoft Active Directory running in the AWS Cloud.

### Key Features:
- **Full Microsoft AD functionality**
- **Multi-AZ deployment** for high availability
- **Automatic backups** and patching
- **Integration with AWS services**
- **Trust relationships** with on-premises AD

### Architecture:
```
┌─────────────────────────────────────┐
│           AWS Managed AD            │
├─────────────────────────────────────┤
│  ┌─────────────┐ ┌─────────────┐   │
│  │  Primary DC │ │ Replica DC  │   │
│  │    AZ-a     │ │    AZ-b     │   │
│  └─────────────┘ └─────────────┘   │
└─────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────┐
│      On-Premises Active Directory   │
│         (Trust relationship)        │
└─────────────────────────────────────┘
```

### Configuration Steps:

#### 1. Create Directory
```bash
# AWS CLI command to create managed AD
aws ds create-microsoft-ad \
    --name corp.example.com \
    --password MySecurePassword123! \
    --description "Corporate Active Directory" \
    --vpc-settings VpcId=vpc-12345678,SubnetIds=subnet-12345678,subnet-87654321 \
    --edition Standard
```

#### 2. Network Configuration
- **VPC Requirements**: Must be deployed in VPC with at least 2 subnets in different AZs
- **Security Groups**: Configure appropriate inbound/outbound rules
- **DNS**: Ensure proper DNS resolution

### Trust Relationships:

#### One-Way Trust (Outgoing):
- AWS Managed AD trusts on-premises AD
- On-premises users can access AWS resources
- AWS users cannot access on-premises resources

#### Two-Way Trust:
- Bidirectional trust relationship
- Users from both directories can access resources in either environment

#### Trust Configuration:
```powershell
# PowerShell command to establish trust
New-ADTrust -Name "aws.corp.example.com" \
    -Type Forest \
    -Direction Bidirectional \
    -TrustPassword (ConvertTo-SecureString "TrustPassword123!" -AsPlainText -Force)
```

### Integration Examples:

#### EC2 Domain Join:
```json
{
    "Type": "AWS::EC2::Instance",
    "Properties": {
        "ImageId": "ami-12345678",
        "InstanceType": "t3.medium",
        "SecurityGroupIds": ["sg-12345678"],
        "SubnetId": "subnet-12345678",
        "IamInstanceProfile": "EC2DomainJoinRole",
        "UserData": {
            "Fn::Base64": {
                "Fn::Join": ["", [
                    "<powershell>\n",
                    "Add-Computer -DomainName corp.example.com -Credential (Get-Credential) -Restart\n",
                    "</powershell>\n"
                ]]
            }
        }
    }
}
```

### Pricing:
- **Standard Edition**: ~$109/month per directory
- **Enterprise Edition**: ~$219/month per directory
- Additional charges for data transfer and storage

---

## AD Connector

### Overview
AD Connector is a directory gateway that redirects directory requests to your on-premises Microsoft Active Directory without caching any information in the cloud.

### Key Features:
- **Proxy service** - No AD data stored in AWS
- **On-premises authentication**
- **AWS service integration**
- **Cost-effective** for existing AD environments

### Architecture:
```
┌─────────────────────────────────────┐
│              AWS Cloud              │
│  ┌─────────────────────────────────┐│
│  │         AD Connector            ││
│  │    ┌─────────────────────────┐  ││
│  │    │   Directory Proxy       │  ││
│  │    │   (No data storage)     │  ││
│  │    └─────────────────────────┘  ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
            │
            ▼ (VPN/Direct Connect)
┌─────────────────────────────────────┐
│      On-Premises Network            │
│  ┌─────────────────────────────────┐│
│  │    Active Directory Domain      ││
│  │         Controllers             ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Prerequisites:
- Existing on-premises Active Directory
- VPN or AWS Direct Connect connectivity
- Service account with appropriate permissions

### Configuration:

#### 1. Network Connectivity
```bash
# Verify connectivity to on-premises AD
telnet your-ad-server.corp.com 389  # LDAP
telnet your-ad-server.corp.com 636  # LDAPS
telnet your-ad-server.corp.com 88   # Kerberos
```

#### 2. Service Account Setup
```powershell
# Create service account for AD Connector
New-ADUser -Name "AWSConnectorService" \
    -SamAccountName "awsconnector" \
    -UserPrincipalName "awsconnector@corp.com" \
    -AccountPassword (ConvertTo-SecureString "SecurePassword123!" -AsPlainText -Force) \
    -Enabled $true \
    -PasswordNeverExpires $true

# Grant necessary permissions
Add-ADGroupMember -Identity "Domain Admins" -Members "awsconnector"
```

#### 3. Create AD Connector
```bash
aws ds connect-directory \
    --name corp.example.com \
    --description "AD Connector for corp domain" \
    --size Small \
    --connect-settings VpcId=vpc-12345678,SubnetIds=subnet-12345678,subnet-87654321,CustomerDnsIps=10.0.0.100,10.0.0.101,CustomerUserName=awsconnector
```

### Use Cases:
- **AWS SSO** with existing AD
- **WorkSpaces** authentication
- **EC2 domain joining** without data replication
- **Cost-sensitive** scenarios

### Limitations:
- Requires constant connectivity to on-premises
- Limited AWS service integrations compared to Managed AD
- Performance depends on network latency

---

## Simple AD

### Overview
Simple AD is a standalone, managed directory that is powered by Linux Samba Active Directory-compatible server. It provides a subset of AD features.

### Key Features:
- **Cost-effective** solution
- **Basic AD functionality**
- **No on-premises requirement**
- **Kerberos-based SSO**
- **LDAP support**

### Architecture:
```
┌─────────────────────────────────────┐
│              AWS Cloud              │
│  ┌─────────────────────────────────┐│
│  │           Simple AD             ││
│  │  ┌─────────────────────────────┐││
│  │  │    Samba AD Server         │││
│  │  │   (Linux-based)            │││
│  │  │                            │││
│  │  │  ┌─────────┐ ┌─────────┐   │││
│  │  │  │  Node 1 │ │  Node 2 │   │││
│  │  │  │   AZ-a  │ │   AZ-b  │   │││
│  │  │  └─────────┘ └─────────┘   │││
│  │  └─────────────────────────────┘││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
```

### Supported Features:
- User accounts and groups
- Group policies (limited)
- Kerberos-based SSO
- LDAP support
- DNS services

### Not Supported:
- Trust relationships
- Advanced AD features
- Schema extensions
- PowerShell AD cmdlets (limited)

### Configuration Example:
```bash
# Create Simple AD
aws ds create-directory \
    --name corp.example.com \
    --description "Simple AD for development" \
    --size Small \
    --vpc-settings VpcId=vpc-12345678,SubnetIds=subnet-12345678,subnet-87654321
```

### Use Cases:
- **Development environments**
- **Small organizations**
- **Cost-sensitive scenarios**
- **Basic LDAP requirements**

### Pricing:
- **Small**: ~$36/month
- **Large**: ~$146/month

---

## Amazon Cognito

### Overview
Amazon Cognito provides authentication, authorization, and user management for web and mobile applications.

### Components:
1. **User Pools**: User directory for authentication
2. **Identity Pools**: Federated identities for AWS resource access

### User Pools Features:
- User registration and sign-in
- Multi-factor authentication (MFA)
- Social identity providers
- SAML and OIDC federation
- Custom authentication flows

### Identity Pools Features:
- Temporary AWS credentials
- Federated access to AWS resources
- Guest user access
- Fine-grained permissions

### Architecture:
```
┌─────────────────────────────────────┐
│          Web/Mobile App             │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           Amazon Cognito            │
│  ┌─────────────────────────────────┐│
│  │          User Pool              ││
│  │    ┌─────────────────────────┐  ││
│  │    │   User Directory        │  ││
│  │    │   Authentication        │  ││
│  │    │   MFA, Policies         │  ││
│  │    └─────────────────────────┘  ││
│  └─────────────────────────────────┘│
│  ┌─────────────────────────────────┐│
│  │        Identity Pool            ││
│  │    ┌─────────────────────────┐  ││
│  │    │   AWS Credentials       │  ││
│  │    │   Federated Access      │  ││
│  │    └─────────────────────────┘  ││
│  └─────────────────────────────────┘│
└─────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│           AWS Services              │
│        (S3, DynamoDB, etc.)         │
└─────────────────────────────────────┘
```

### Configuration Examples:

#### User Pool Creation:
```json
{
    "PoolName": "MyUserPool",
    "Policies": {
        "PasswordPolicy": {
            "MinimumLength": 8,
            "RequireUppercase": true,
            "RequireLowercase": true,
            "RequireNumbers": true,
            "RequireSymbols": true
        }
    },
    "MfaConfiguration": "OPTIONAL",
    "Schema": [
        {
            "Name": "email",
            "AttributeDataType": "String",
            "Required": true,
            "Mutable": true
        }
    ]
}
```

#### Identity Pool with Roles:
```json
{
    "IdentityPoolName": "MyIdentityPool",
    "AllowUnauthenticatedIdentities": true,
    "CognitoIdentityProviders": [
        {
            "ProviderName": "cognito-idp.us-east-1.amazonaws.com/us-east-1_ABC123DEF",
            "ClientId": "1example23456789",
            "ServerSideTokenCheck": false
        }
    ]
}
```

---

## Integration with AWS Services

### Amazon WorkSpaces
```yaml
# CloudFormation template for WorkSpaces with Directory Services
Resources:
  Workspace:
    Type: AWS::WorkSpaces::Workspace
    Properties:
      DirectoryId: !Ref DirectoryId
      BundleId: wsb-bh8rsxt14  # Standard bundle
      UserName: john.doe
      WorkspaceProperties:
        ComputeTypeName: STANDARD
        UserVolumeSizeGib: 50
        RootVolumeSizeGib: 80
```

### Amazon RDS (SQL Server)
```json
{
    "DBInstanceClass": "db.t3.medium",
    "Engine": "sqlserver-se",
    "MasterUsername": "admin",
    "MasterUserPassword": "MySecurePassword123!",
    "Domain": "d-123456789a",
    "DomainIAMRoleName": "rds-directoryservice-role"
}
```

### AWS SSO Integration
```bash
# Enable AWS SSO with Directory Services
aws sso-admin create-permission-set \
    --instance-arn arn:aws:sso:::instance/ssoins-1234567890abcdef \
    --name DirectoryUsersAccess \
    --description "Access for directory users" \
    --session-duration PT4H
```

### Amazon FSx Integration
```yaml
FileSystem:
  Type: AWS::FSx::FileSystem
  Properties:
    FileSystemType: WINDOWS
    StorageCapacity: 32
    SubnetIds:
      - subnet-12345678
    SecurityGroupIds:
      - sg-12345678
    WindowsConfiguration:
      ActiveDirectoryId: d-123456789a
      ThroughputCapacity: 8
      WeeklyMaintenanceStartTime: "4:16:30"
```

---

## Security and Compliance

### Network Security
- **VPC Security Groups**: Control access to directory services
- **NACLs**: Additional network-level security
- **Private Subnets**: Deploy directories in private subnets

### Encryption
- **Data in Transit**: TLS/SSL encryption
- **Data at Rest**: Encrypted using AWS KMS
- **Custom KMS Keys**: For additional security control

### Access Control
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ds.amazonaws.com"
            },
            "Action": "kms:*",
            "Resource": "*",
            "Condition": {
                "StringEquals": {
                    "kms:ViaService": "ds.region.amazonaws.com"
                }
            }
        }
    ]
}
```

### Compliance Considerations
- **GDPR**: Data residency and privacy controls
- **HIPAA**: Healthcare compliance requirements
- **SOC**: Service Organization Control compliance
- **PCI DSS**: Payment card industry standards

---

## Monitoring and Troubleshooting

### CloudWatch Metrics
```bash
# Key metrics to monitor
aws cloudwatch get-metric-statistics \
    --namespace AWS/DirectoryService \
    --metric-name Replication \
    --dimensions Name=DirectoryId,Value=d-123456789a \
    --start-time 2023-01-01T00:00:00Z \
    --end-time 2023-01-01T23:59:59Z \
    --period 300 \
    --statistics Average
```

### Important Metrics:
- **Replication**: Directory replication status
- **DomainControllerStatus**: Health of domain controllers
- **LDAPResponseTime**: LDAP query performance
- **KerberosAuthentication**: Kerberos auth success rate

### CloudTrail Integration
```json
{
    "eventVersion": "1.05",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDACKCEVSQ6C2EXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/Administrator"
    },
    "eventTime": "2023-01-01T12:00:00Z",
    "eventSource": "ds.amazonaws.com",
    "eventName": "CreateDirectory",
    "sourceIPAddress": "203.0.113.12"
}
```

### Common Troubleshooting Steps:

#### Connectivity Issues:
```bash
# Test network connectivity
nslookup corp.example.com
telnet domain-controller.corp.com 389
ping domain-controller.corp.com
```

#### Authentication Problems:
```bash
# Check Kerberos configuration
kinit user@CORP.EXAMPLE.COM
klist

# Test LDAP binding
ldapsearch -x -h domain-controller.corp.com -p 389 -D "cn=user,dc=corp,dc=com" -W
```

---

## Cost Optimization

### Sizing Guidelines:
- **Simple AD Small**: Up to 500 users
- **Simple AD Large**: Up to 5,000 users
- **AD Connector Small**: Up to 500 users
- **AD Connector Large**: Up to 5,000 users

### Cost Comparison:
```
Service Type          Monthly Cost (Small)    Monthly Cost (Large)
Simple AD             $36                     $146
AD Connector          $36                     $146
Managed AD (Standard) $109                    N/A
Managed AD (Enterprise) $219                  N/A
```

### Optimization Strategies:
1. **Right-sizing**: Choose appropriate directory size
2. **Regional placement**: Consider data transfer costs
3. **Lifecycle management**: Remove unused directories
4. **Monitoring**: Track usage patterns

---

## Best Practices

### Design Principles:
1. **Multi-AZ Deployment**: For high availability
2. **Separate environments**: Dev, test, production directories
3. **Least privilege access**: Minimal required permissions
4. **Regular backups**: Automated backup strategies

### Security Best Practices:
```json
{
    "PasswordPolicy": {
        "MinimumLength": 12,
        "RequireUppercase": true,
        "RequireLowercase": true,
        "RequireNumbers": true,
        "RequireSymbols": true,
        "MaxPasswordAge": 90,
        "PasswordHistorySize": 12
    }
}
```

### Network Best Practices:
- Use dedicated VPC for directory services
- Implement proper DNS forwarding
- Configure security groups restrictively
- Use VPC endpoints where possible

### Operational Best Practices:
- Regular health checks
- Automated monitoring alerts
- Disaster recovery planning
- Documentation and runbooks

---

## Common Exam Scenarios

### Scenario 1: Hybrid Cloud Authentication
**Question**: A company has 1,000 employees with existing on-premises Active Directory. They want to enable AWS SSO while maintaining their current authentication system. What solution should they choose?

**Answer**: AD Connector
- Maintains existing on-premises AD
- Enables AWS SSO
- No data duplication in cloud
- Cost-effective for existing AD environments

### Scenario 2: New Cloud-Native Application
**Question**: A startup is building a new web application and needs user authentication with social login support. They have no existing directory infrastructure. What's the best solution?

**Answer**: Amazon Cognito User Pools
- No infrastructure to manage
- Built-in social identity providers
- Scalable and cost-effective
- Integrated with AWS services

### Scenario 3: Enterprise Migration
**Question**: An enterprise is migrating to AWS and needs full Active Directory functionality in the cloud with trust relationships to on-premises. What solution is appropriate?

**Answer**: AWS Managed Microsoft AD
- Full Microsoft AD features
- Trust relationships supported
- Multi-AZ high availability
- Enterprise-grade security

### Scenario 4: Development Environment
**Question**: A small development team needs basic LDAP authentication for their test applications. They want a cost-effective solution without complex setup.

**Answer**: Simple AD
- Basic LDAP functionality
- No on-premises requirements
- Cost-effective
- Quick setup

---

## AWS CLI Commands Reference

### Directory Management

#### Create AWS Managed Microsoft AD
```bash
# Create a Standard Edition Managed Microsoft AD
aws ds create-microsoft-ad \
    --name corp.example.com \
    --short-name CORP \
    --password MySecureP@ssw0rd! \
    --description "Corporate Active Directory" \
    --vpc-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456 \
    --edition Standard \
    --tags Key=Environment,Value=Production Key=Owner,Value=IT

# Create an Enterprise Edition Managed Microsoft AD
aws ds create-microsoft-ad \
    --name enterprise.example.com \
    --short-name ENTERPRISE \
    --password MySecureP@ssw0rd! \
    --description "Enterprise Active Directory" \
    --vpc-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456 \
    --edition Enterprise \
    --region us-east-1
```

#### Create AD Connector
```bash
# Create an AD Connector to on-premises Active Directory
aws ds connect-directory \
    --name onprem.example.com \
    --short-name ONPREM \
    --password ConnectorP@ssw0rd! \
    --description "Connector to on-premises AD" \
    --size Small \
    --connect-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456,CustomerDnsIps=10.0.0.10,10.0.0.11,CustomerUserName=admin@onprem.example.com

# Create a large AD Connector for higher throughput
aws ds connect-directory \
    --name onprem.example.com \
    --short-name ONPREM \
    --password ConnectorP@ssw0rd! \
    --size Large \
    --connect-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456,CustomerDnsIps=10.0.0.10,10.0.0.11,CustomerUserName=admin@onprem.example.com
```

#### Create Simple AD
```bash
# Create a Small Simple AD directory
aws ds create-directory \
    --name simple.example.com \
    --short-name SIMPLE \
    --password SimpleP@ssw0rd! \
    --description "Simple AD for development" \
    --size Small \
    --vpc-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456

# Create a Large Simple AD directory
aws ds create-directory \
    --name simple.example.com \
    --short-name SIMPLE \
    --password SimpleP@ssw0rd! \
    --size Large \
    --vpc-settings VpcId=vpc-0123456789abcdef0,SubnetIds=subnet-abc123,subnet-def456 \
    --tags Key=Environment,Value=Development
```

### Directory Operations

#### Describe Directories
```bash
# List all directories in the region
aws ds describe-directories

# Describe a specific directory
aws ds describe-directories \
    --directory-ids d-1234567890

# Get directory details with specific output format
aws ds describe-directories \
    --directory-ids d-1234567890 \
    --query 'DirectoryDescriptions[0].[DirectoryId,Name,Type,Stage]' \
    --output table

# List all directories and their status
aws ds describe-directories \
    --query 'DirectoryDescriptions[*].[DirectoryId,Name,Type,Stage]' \
    --output table
```

#### Delete Directory
```bash
# Delete a directory
aws ds delete-directory \
    --directory-id d-1234567890

# Delete directory without confirmation (use with caution)
aws ds delete-directory \
    --directory-id d-1234567890 \
    --no-cli-auto-prompt
```

### Trust Relationships

#### Create Trust Relationship
```bash
# Create one-way outgoing trust (AWS trusts on-premises)
aws ds create-trust \
    --directory-id d-1234567890 \
    --remote-domain-name onprem.example.com \
    --trust-password TrustP@ssw0rd! \
    --trust-direction One-Way:Outgoing \
    --trust-type Forest

# Create two-way trust
aws ds create-trust \
    --directory-id d-1234567890 \
    --remote-domain-name onprem.example.com \
    --trust-password TrustP@ssw0rd! \
    --trust-direction Two-Way \
    --trust-type Forest

# Create one-way incoming trust (on-premises trusts AWS)
aws ds create-trust \
    --directory-id d-1234567890 \
    --remote-domain-name onprem.example.com \
    --trust-password TrustP@ssw0rd! \
    --trust-direction One-Way:Incoming \
    --trust-type External
```

#### Manage Trusts
```bash
# Describe trusts for a directory
aws ds describe-trusts \
    --directory-id d-1234567890

# Verify trust relationship
aws ds verify-trust \
    --trust-id t-0123456789abcdef0

# Delete a trust relationship
aws ds delete-trust \
    --trust-id t-0123456789abcdef0

# Update trust password
aws ds update-trust \
    --trust-id t-0123456789abcdef0 \
    --selective-auth Enabled
```

### Conditional Forwarders

#### Create Conditional Forwarder
```bash
# Create conditional forwarder for specific domain
aws ds create-conditional-forwarder \
    --directory-id d-1234567890 \
    --remote-domain-name partner.example.com \
    --dns-ip-addrs 10.0.0.100 10.0.0.101

# Create multiple conditional forwarders
aws ds create-conditional-forwarder \
    --directory-id d-1234567890 \
    --remote-domain-name vendor.example.com \
    --dns-ip-addrs 192.168.1.10 192.168.1.11
```

#### Manage Conditional Forwarders
```bash
# Describe conditional forwarders
aws ds describe-conditional-forwarders \
    --directory-id d-1234567890

# Describe specific conditional forwarder
aws ds describe-conditional-forwarders \
    --directory-id d-1234567890 \
    --remote-domain-names partner.example.com

# Update conditional forwarder DNS IPs
aws ds update-conditional-forwarder \
    --directory-id d-1234567890 \
    --remote-domain-name partner.example.com \
    --dns-ip-addrs 10.0.0.102 10.0.0.103

# Delete conditional forwarder
aws ds delete-conditional-forwarder \
    --directory-id d-1234567890 \
    --remote-domain-name partner.example.com
```

### Shared Directories

#### Share Directory
```bash
# Share directory with another AWS account
aws ds share-directory \
    --directory-id d-1234567890 \
    --share-target Id=123456789012,Type=ACCOUNT \
    --share-method HANDSHAKE \
    --share-notes "Sharing for cross-account EC2 domain join"

# Share directory with organization
aws ds share-directory \
    --directory-id d-1234567890 \
    --share-target Id=o-exampleorgid,Type=ORGANIZATION \
    --share-method ORGANIZATIONS
```

#### Manage Shared Directories
```bash
# Describe shared directories
aws ds describe-shared-directories \
    --owner-directory-id d-1234567890

# Accept shared directory invitation
aws ds accept-shared-directory \
    --shared-directory-id d-1234567890

# Reject shared directory invitation
aws ds reject-shared-directory \
    --shared-directory-id d-1234567890

# Unshare directory
aws ds unshare-directory \
    --directory-id d-1234567890 \
    --unshare-target Id=123456789012,Type=ACCOUNT
```

### MFA Configuration

#### Enable and Configure MFA
```bash
# Enable RADIUS-based MFA
aws ds enable-radius \
    --directory-id d-1234567890 \
    --radius-settings DisplayLabel="Company MFA",RadiusServers=192.168.1.50,RadiusPort=1812,RadiusTimeout=5,RadiusRetries=3,SharedSecret=MyRadiusSecret123!,AuthenticationProtocol=PAP,UseSameUsername=true

# Update RADIUS settings
aws ds update-radius \
    --directory-id d-1234567890 \
    --radius-settings DisplayLabel="Updated MFA",RadiusServers=192.168.1.51,RadiusPort=1812,RadiusTimeout=10,RadiusRetries=3,SharedSecret=NewSecret123!,AuthenticationProtocol=CHAP,UseSameUsername=true

# Disable RADIUS/MFA
aws ds disable-radius \
    --directory-id d-1234567890
```

### Snapshots Management

#### Create and Manage Snapshots
```bash
# Create manual snapshot
aws ds create-snapshot \
    --directory-id d-1234567890 \
    --name "pre-upgrade-snapshot-2026-02-08"

# List all snapshots for a directory
aws ds describe-snapshots \
    --directory-id d-1234567890

# List snapshots with specific details
aws ds describe-snapshots \
    --directory-id d-1234567890 \
    --query 'Snapshots[*].[SnapshotId,Name,Status,StartTime]' \
    --output table

# Delete a snapshot
aws ds delete-snapshot \
    --snapshot-id s-0123456789abcdef0

# Restore from snapshot (requires creating new directory)
aws ds restore-from-snapshot \
    --snapshot-id s-0123456789abcdef0
```

### Domain Controllers

#### Manage Domain Controllers
```bash
# Add domain controller to directory
aws ds add-region \
    --directory-id d-1234567890 \
    --region-name eu-west-1 \
    --vpc-settings VpcId=vpc-eu123456,SubnetIds=subnet-eu1,subnet-eu2

# Describe domain controllers
aws ds describe-domain-controllers \
    --directory-id d-1234567890

# Describe domain controllers in specific region
aws ds describe-domain-controllers \
    --directory-id d-1234567890 \
    --region us-east-1

# List regions where directory is deployed
aws ds list-log-subscriptions \
    --directory-id d-1234567890
```

### Schema Extensions

#### Manage Schema Extensions
```bash
# Start schema extension
aws ds start-schema-extension \
    --directory-id d-1234567890 \
    --create-snapshot-before-schema-extension \
    --ldif-content "$(cat schema-extension.ldif)" \
    --description "Adding custom attributes for HR system"

# Describe schema extensions
aws ds describe-schema-extensions \
    --directory-id d-1234567890

# Cancel schema extension
aws ds cancel-schema-extension \
    --directory-id d-1234567890 \
    --schema-extension-id extn-0123456789abcdef0
```

### Tags Management

#### Add and Manage Tags
```bash
# Add tags to directory
aws ds add-tags-to-resource \
    --resource-id d-1234567890 \
    --tags Key=Environment,Value=Production Key=CostCenter,Value=IT-001 Key=Owner,Value=admin@example.com

# List tags for a directory
aws ds list-tags-for-resource \
    --resource-id d-1234567890

# Remove tags from directory
aws ds remove-tags-from-resource \
    --resource-id d-1234567890 \
    --tag-keys Environment CostCenter
```

### Directory Settings

#### Update Directory Settings
```bash
# Update directory settings
aws ds update-settings \
    --directory-id d-1234567890 \
    --settings Name=SSO,Value=true

# Enable/Disable LDAPS
aws ds enable-ldaps \
    --directory-id d-1234567890 \
    --type Client

aws ds disable-ldaps \
    --directory-id d-1234567890 \
    --type Client

# Describe LDAPS settings
aws ds describe-ldaps-settings \
    --directory-id d-1234567890
```

### IP Routes (for AD Connector and Managed AD)

#### Manage IP Routes
```bash
# Add IP route for peered VPC
aws ds add-ip-routes \
    --directory-id d-1234567890 \
    --ip-routes CidrIp=10.1.0.0/16,Description="Route to peered VPC"

# List IP routes
aws ds list-ip-routes \
    --directory-id d-1234567890

# Remove IP route
aws ds remove-ip-routes \
    --directory-id d-1234567890 \
    --cidr-ips 10.1.0.0/16
```

### CloudWatch Log Integration

#### Configure CloudWatch Logs
```bash
# Create log subscription
aws ds create-log-subscription \
    --directory-id d-1234567890 \
    --log-group-name /aws/directoryservice/d-1234567890

# List log subscriptions
aws ds list-log-subscriptions \
    --directory-id d-1234567890

# Delete log subscription
aws ds delete-log-subscription \
    --directory-id d-1234567890
```

### Computer Objects

#### Manage Computer Objects
```bash
# Create computer object for pre-staging
aws ds create-computer \
    --directory-id d-1234567890 \
    --computer-name WEB-SERVER-01 \
    --password ComputerP@ssw0rd! \
    --organizational-unit-distinguished-name "OU=Servers,DC=corp,DC=example,DC=com" \
    --computer-attributes Name=description,Value="Web Server in DMZ"
```

### Certificate Management

#### Manage Certificates for LDAPS
```bash
# Register certificate for LDAPS
aws ds register-certificate \
    --directory-id d-1234567890 \
    --certificate-data file://certificate.pem \
    --type ClientCertAuth

# List certificates
aws ds list-certificates \
    --directory-id d-1234567890

# Describe certificate
aws ds describe-certificate \
    --directory-id d-1234567890 \
    --certificate-id cert-0123456789abcdef0

# Deregister certificate
aws ds deregister-certificate \
    --directory-id d-1234567890 \
    --certificate-id cert-0123456789abcdef0
```

### Event Subscriptions

#### Manage Event Subscriptions
```bash
# Register event topic
aws ds register-event-topic \
    --directory-id d-1234567890 \
    --topic-name arn:aws:sns:us-east-1:123456789012:DirectoryServiceEvents

# Describe event topics
aws ds describe-event-topics \
    --directory-id d-1234567890

# Deregister event topic
aws ds deregister-event-topic \
    --directory-id d-1234567890 \
    --topic-name arn:aws:sns:us-east-1:123456789012:DirectoryServiceEvents
```

### Client Authentication

#### Configure Client Authentication
```bash
# Enable client authentication
aws ds enable-client-authentication \
    --directory-id d-1234567890 \
    --type SmartCard

# Describe client authentication settings
aws ds describe-client-authentication-settings \
    --directory-id d-1234567890

# Disable client authentication
aws ds disable-client-authentication \
    --directory-id d-1234567890 \
    --type SmartCard
```

### Useful Query Commands

#### Advanced Queries
```bash
# Get all directories with their types and stages
aws ds describe-directories \
    --query 'DirectoryDescriptions[*].{ID:DirectoryId,Name:Name,Type:Type,Stage:Stage,Size:Size}' \
    --output table

# Find directories in specific VPC
aws ds describe-directories \
    --query 'DirectoryDescriptions[?VpcSettings.VpcId==`vpc-0123456789abcdef0`].[DirectoryId,Name]' \
    --output table

# Get directory DNS IPs
aws ds describe-directories \
    --directory-ids d-1234567890 \
    --query 'DirectoryDescriptions[0].DnsIpAddrs' \
    --output table

# Check directory status across all regions
for region in us-east-1 us-west-2 eu-west-1; do
  echo "Region: $region"
  aws ds describe-directories --region $region --query 'DirectoryDescriptions[*].[DirectoryId,Name,Stage]' --output table
done
```

---

## Hands-On Labs

### Lab 1: Setting up AWS Managed Microsoft AD

#### Prerequisites:
- AWS account with appropriate permissions
- VPC with at least 2 subnets in different AZs

#### Steps:
1. **Create Managed AD**:
```bash
aws ds create-microsoft-ad \
    --name lab.example.com \
    --password LabPassword123! \
    --description "Lab Managed AD" \
    --vpc-settings VpcId=vpc-12345678,SubnetIds=subnet-12345678,subnet-87654321 \
    --edition Standard
```

2. **Verify Directory Status**:
```bash
aws ds describe-directories --directory-ids d-123456789a
```

3. **Configure Security Groups**:
```bash
# Allow AD traffic
aws ec2 authorize-security-group-ingress \
    --group-id sg-12345678 \
    --protocol tcp \
    --port 389 \
    --source-group sg-87654321
```

### Lab 2: EC2 Domain Join

#### Launch Windows EC2 Instance:
```bash
aws ec2 run-instances \
    --image-id ami-12345678 \
    --count 1 \
    --instance-type t3.medium \
    --key-name my-key-pair \
    --security-group-ids sg-12345678 \
    --subnet-id subnet-12345678 \
    --iam-instance-profile Name=EC2DomainJoinRole
```

#### Domain Join Script:
```powershell
# PowerShell script for domain join
$domain = "lab.example.com"
$username = "Admin"
$password = "LabPassword123!" | ConvertTo-SecureString -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($username, $password)

Add-Computer -DomainName $domain -Credential $credential -Restart
```

### Lab 3: Cognito User Pool Setup

#### Create User Pool:
```bash
aws cognito-idp create-user-pool \
    --pool-name LabUserPool \
    --policies PasswordPolicy='{MinimumLength=8,RequireUppercase=true,RequireLowercase=true,RequireNumbers=true,RequireSymbols=false}'
```

#### Create User Pool Client:
```bash
aws cognito-idp create-user-pool-client \
    --user-pool-id us-east-1_ABC123DEF \
    --client-name LabWebApp \
    --generate-secret
```

---

## Conclusion

AWS Directory Services provides flexible options for identity and access management in the cloud. Understanding when to use each service is crucial for the SAA-C03 exam:

- **AWS Managed Microsoft AD**: Full AD features, enterprise requirements
- **AD Connector**: Existing on-premises AD, hybrid scenarios  
- **Simple AD**: Basic needs, cost-sensitive environments
- **Amazon Cognito**: Web/mobile apps, modern authentication

Key exam focus areas:
- Service selection based on requirements
- Integration patterns with AWS services
- Security and networking considerations
- Cost optimization strategies
- Troubleshooting common issues

Remember to practice hands-on labs and understand real-world scenarios for exam success.