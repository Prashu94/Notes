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
12. [Hands-On Labs](#hands-on-labs)

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